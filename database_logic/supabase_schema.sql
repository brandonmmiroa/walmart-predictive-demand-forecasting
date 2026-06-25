-- =========================================================
-- 🛢️ SUPABASE DATA WAREHOUSE SCHEMA DEFINITION
-- =========================================================
DROP TABLE IF EXISTS store_daily_features;

CREATE TABLE store_daily_features (
    id SERIAL PRIMARY KEY,
    date_only DATE NOT NULL UNIQUE,
    total_quantity INT NOT NULL,
    masked_revenue NUMERIC(12, 2) NOT NULL,
    is_holiday INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_features_date ON store_daily_features(date_only);
