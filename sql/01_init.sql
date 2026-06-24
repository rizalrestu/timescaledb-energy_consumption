CREATE TABLE IF NOT EXISTS energy_actual (
    time TIMESTAMPTZ NOT NULL,
    consumption FLOAT NOT NULL
);

-- Mengubah tabel biasa menjadi hypertable TimescaleDB
SELECT create_hypertable('energy_actual', by_range('time'), if_not_exists => TRUE);

-- Membuat tabel untuk menampung hasil prediksi
CREATE TABLE IF NOT EXISTS energy_forecast (
    time TIMESTAMPTZ NOT NULL,
    predicted_value FLOAT NOT NULL
);

-- Menjadikan tabel prediksi sebagai hypertable
SELECT create_hypertable('energy_forecast', by_range('time'), if_not_exists => TRUE);
