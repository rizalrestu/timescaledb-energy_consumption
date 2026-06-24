import warnings
import pandas as pd
import numpy as np
import xgboost as xgb
from sqlalchemy import create_engine

warnings.filterwarnings("ignore")

DB_URI = "postgresql://postgres:postgres@localhost:54321/energy_db"
engine = create_engine(DB_URI)

def create_features(df):
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    df['is_weekend'] = (df.index.dayofweek >= 5).astype(int)
    
    # Lag features
    df['lag_24'] = df['consumption'].shift(24)
    df['lag_168'] = df['consumption'].shift(168)
    
    return df

def run_forecast():
    print("Fetching historical data from TimescaleDB...")
    query = "SELECT time, consumption FROM energy_actual ORDER BY time ASC"
    df = pd.read_sql(query, engine)
    
    if df.empty:
        print("Data is empty.")
        return
        
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    
    df = create_features(df)
    df.dropna(inplace=True)
    
    FEATURES = ['hour', 'dayofweek', 'month', 'year', 'dayofyear', 
                'is_weekend', 'lag_24', 'lag_168']
    TARGET = 'consumption'
    
    print("\n--- PHASE 1: MODEL EVALUATION ---")
    split_index = int(len(df) * 0.8)
    
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]
    
    X_train, y_train = train_df[FEATURES], train_df[TARGET]
    X_test, y_test = test_df[FEATURES], test_df[TARGET]
    
    eval_model = xgb.XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=6)
    eval_model.fit(X_train, y_train, verbose=False)
    
    test_predictions = eval_model.predict(X_test)
    
    mae = np.mean(np.abs(y_test - test_predictions))
    rmse = np.sqrt(np.mean((y_test - test_predictions)**2))
    
    print(f"Evaluation Results:")
    print(f"  > MAE : {mae:.2f} MWh")
    print(f"  > RMSE: {rmse:.2f} MWh")
    
    print("\n--- PHASE 2: FUTURE FORECASTING (24H) ---")
    
    # Retrain on full dataset
    X, y = df[FEATURES], df[TARGET]
    final_model = xgb.XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=6)
    final_model.fit(X, y, verbose=False)
    
    # Generate future dates
    last_time = df.index.max()
    future_dates = pd.date_range(start=last_time + pd.Timedelta(hours=1), periods=24, freq='h')
    future_df = pd.DataFrame(index=future_dates, columns=['consumption'])
    future_df.index.name = 'time'
    
    # Concatenate to compute lag features for the future period
    combined_df = pd.concat([df[['consumption']], future_df])
    combined_df = create_features(combined_df)
    
    # Extract future features
    future_features = combined_df.iloc[-24:]
    future_predictions = final_model.predict(future_features[FEATURES])
    
    forecast_results = pd.DataFrame({
        'time': future_dates,
        'predicted_value': future_predictions
    })
    
    print("Saving predictions to 'energy_forecast' table...")
    forecast_results.to_sql('energy_forecast', engine, if_exists='append', index=False)
    
    print("Done.")

if __name__ == "__main__":
    run_forecast()
