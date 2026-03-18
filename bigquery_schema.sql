-- Esquema para BigQuery
CREATE SCHEMA IF NOT EXISTS betting_ai;

-- Tabla de partidos
CREATE TABLE IF NOT EXISTS betting_ai.matches (
    match_id STRING,
    league STRING,
    home_team STRING,
    away_team STRING,
    match_date DATE,
    odds_home DECIMAL,
    odds_draw DECIMAL,
    odds_away DECIMAL,
    result_home INT64,
    result_away INT64,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Tabla de predicciones
CREATE TABLE IF NOT EXISTS betting_ai.predictions (
    prediction_id STRING,
    match_id STRING,
    predicted_winner STRING,
    confidence DECIMAL,
    actual_winner STRING,
    was_correct BOOLEAN,
    model_version STRING,
    created_at TIMESTAMP
);

-- Tabla de parlays
CREATE TABLE IF NOT EXISTS betting_ai.parlays (
    parlay_id STRING,
    picks ARRAY<STRUCT<
        match_id STRING,
        pick STRING,
        odds DECIMAL
    >>,
    total_odds DECIMAL,
    stake DECIMAL,
    result STRING,
    profit DECIMAL,
    created_at TIMESTAMP
);
