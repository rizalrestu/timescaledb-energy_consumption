import os
import time
import glob
import pandas as pd
from sqlalchemy import create_engine

DB_URI = "postgresql://postgres:postgres@localhost:54321/energy_db"
engine = create_engine(DB_URI)
TABLE_NAME = "energy_actual"

def clean_and_parse_data(row):
    dt_str = f"{row['Date']} {row['Hour']}"
    dt = pd.to_datetime(dt_str, format="%d.%m.%Y %H:%M")
    
    consumption = float(str(row['Consumption (MWh)']).replace(',', ''))
    return dt, consumption

def get_last_timestamp():
    try:
        query = f"SELECT MAX(time) as last_time FROM {TABLE_NAME}"
        df = pd.read_sql(query, engine)
        
        last_time = df.iloc[0]['last_time']
        if pd.notnull(last_time):
            return pd.to_datetime(last_time).tz_localize(None)
    except Exception:
        pass
        
    return None

def run_ingestion():
    csv_files = glob.glob("../data/*.csv")
    
    if not csv_files:
        print("Error: No CSV files found in ../data/")
        return

    last_timestamp = get_last_timestamp()
    if last_timestamp:
        print(f"Resuming ingestion after: {last_timestamp}")
    else:
        print("Database is empty. Starting initial ingestion...")

    print("Press Ctrl+C to stop the stream.\n")
    
    for file_path in csv_files:
        print(f"\nReading {file_path}...")
        try:
            df = pd.read_csv(file_path)
            
            # Filter out already ingested data
            if last_timestamp:
                temp_time = pd.to_datetime(df['Date'] + " " + df['Hour'], format="%d.%m.%Y %H:%M")
                df = df[temp_time > last_timestamp]
                
                if df.empty:
                    print("All rows in this file are already ingested. Skipping.")
                    continue
            
            print(f"Found {len(df)} new rows. Starting stream...\n")
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            continue
        
        for index, row in df.iterrows():
            try:
                dt, consumption = clean_and_parse_data(row)
                
                data_to_insert = pd.DataFrame([{'time': dt, 'consumption': consumption}])
                data_to_insert.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
                
                print(f"[{dt}] Inserted: {consumption} MWh")
                time.sleep(0.05) 
                
            except KeyboardInterrupt:
                print("\nSimulation stopped.")
                return 
            except Exception as e:
                print(f"Error on row {index}: {e}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_ingestion()
