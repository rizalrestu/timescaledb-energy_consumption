# TimescaleDB Energy Forecasting

A complete end-to-end data pipeline demonstrating how to ingest, store, and forecast time-series data using TimescaleDB, Python, XGBoost, and Grafana.

## Features
- **Data Ingestion**: Streaming simulation of historical energy consumption data into a TimescaleDB hypertable (`src/ingest.py`). Includes auto-resume checkpointing.
- **Continuous Aggregates**: Automated daily aggregations handled natively by TimescaleDB in the background.
- **Machine Learning**: Time-series forecasting using XGBoost, featuring advanced Lag Features and cyclical encoding to predict the next 24 hours (`src/forecast.py`).
- **Visualization**: Grafana dashboard configuration for comparing actual vs predicted consumption.

## Prerequisites
- Docker & Docker Compose
- Python 3.9+

## Quick Start
1. **Start the Infrastructure**
   ```bash
   docker-compose up -d
   ```
   *This automatically sets up TimescaleDB, Grafana, and initializes the SQL schemas (`sql/`).*

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure numpy version compatibility if you encounter SciPy errors).*

3. **Run Data Ingestion**
   Place your time-series CSV datasets in the `data/` folder, then run:
   ```bash
   python src/ingest.py
   ```

4. **Run Forecasting Model**
   Generate predictions for the next 24 hours:
   ```bash
   python src/forecast.py
   ```

5. **View Dashboard**
   Open Grafana at `http://localhost:3000` (User: `admin` / Pass: `admin`), connect the PostgreSQL data source to `timescaledb:5432` (or `localhost:54321` if accessed outside docker network), and query the `energy_actual` and `energy_forecast` tables.
