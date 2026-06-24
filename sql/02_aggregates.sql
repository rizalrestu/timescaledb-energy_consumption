-- Membuat continuous aggregate untuk summary harian
CREATE MATERIALIZED VIEW IF NOT EXISTS energy_daily_summary
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 day', time) AS bucket,
       AVG(consumption) AS avg_consumption,
       SUM(consumption) AS total_consumption
FROM energy_actual
GROUP BY bucket;

-- Policy agar update otomatis
SELECT add_continuous_aggregate_policy('energy_daily_summary',
    start_offset => INTERVAL '30 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
