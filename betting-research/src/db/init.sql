-- Betting Prediction Market Database Schema
-- Initialize tables for market data storage

-- Markets table: Stores Kalshi market information
CREATE TABLE IF NOT EXISTS markets (
    id SERIAL PRIMARY KEY,
    kalshi_market_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(1000) NOT NULL,
    subtitle VARCHAR(1000),
    category VARCHAR(100),
    status VARCHAR(50) NOT NULL, -- open, closed, settled
    close_time TIMESTAMP WITH TIME ZONE,
    ticker VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Market prices history: Stores price/volume data over time
CREATE TABLE IF NOT EXISTS market_prices (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES markets(id) ON DELETE CASCADE,
    yes_price NUMERIC(10, 4), -- Price for YES contract
    no_price NUMERIC(10, 4),  -- Price for NO contract
    yes_volume NUMERIC(20, 2),
    no_volume NUMERIC(20, 2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(market_id, timestamp)
);

-- Orders table: Stores trade orders placed by the bot
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    kalshi_order_id VARCHAR(255) UNIQUE,
    market_id INTEGER REFERENCES markets(id) ON DELETE SET NULL,
    side VARCHAR(10) NOT NULL, -- yes, no
    quantity INTEGER NOT NULL,
    price NUMERIC(10, 4) NOT NULL,
    total_cost NUMERIC(20, 2) NOT NULL,
    status VARCHAR(50) NOT NULL, -- pending, filled, cancelled, expired
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    filled_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE
);

-- Positions table: Stores current holdings
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES markets(id) ON DELETE CASCADE,
    side VARCHAR(10) NOT NULL, -- yes, no
    quantity INTEGER NOT NULL,
    avg_price NUMERIC(10, 4) NOT NULL,
    current_price NUMERIC(10, 4),
    unrealized_pnl NUMERIC(20, 2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trade history: Completed trades
CREATE TABLE IF NOT EXISTS trade_history (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE SET NULL,
    market_id INTEGER REFERENCES markets(id) ON DELETE SET NULL,
    side VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price NUMERIC(10, 4) NOT NULL,
    exit_price NUMERIC(10, 4),
    pnl NUMERIC(20, 2),
    closed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Signals table: Stores trading signals generated
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES markets(id) ON DELETE CASCADE,
    signal_type VARCHAR(50) NOT NULL, -- buy_yes, buy_no, sell_yes, sell_no
    confidence NUMERIC(5, 4) NOT NULL, -- 0.0 to 1.0
    reason TEXT,
    acted_upon BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance (
    id SERIAL PRIMARY KEY,
    metric_date DATE UNIQUE NOT NULL,
    total_pnl NUMERIC(20, 2) DEFAULT 0,
    open_positions INTEGER DEFAULT 0,
    total_trades INTEGER DEFAULT 0,
    win_rate NUMERIC(5, 4), -- 0.0 to 1.0
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_markets_kalshi_id ON markets(kalshi_market_id);
CREATE INDEX IF NOT EXISTS idx_markets_status ON markets(status);
CREATE INDEX IF NOT EXISTS idx_market_prices_market_id ON market_prices(market_id);
CREATE INDEX IF NOT EXISTS idx_market_prices_timestamp ON market_prices(timestamp);
CREATE INDEX IF NOT EXISTS idx_orders_market_id ON orders(market_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_positions_market_id ON positions(market_id);
CREATE INDEX IF NOT EXISTS idx_trade_history_market_id ON trade_history(market_id);
CREATE INDEX IF NOT EXISTS idx_signals_market_id ON signals(market_id);

-- Grant permissions (adjust user as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
