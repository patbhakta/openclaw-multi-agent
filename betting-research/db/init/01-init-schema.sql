-- Betting Markets Database Schema

-- Markets table (Kalshi market data)
CREATE TABLE IF NOT EXISTS markets (
    id VARCHAR(255) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    subtitle VARCHAR(500),
    category VARCHAR(100),
    status VARCHAR(50) NOT NULL, -- 'open', 'closed', 'settled'
    open_time TIMESTAMP WITH TIME ZONE,
    close_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ticker VARCHAR(50),
    min_price FLOAT,
    max_price FLOAT,
    volume FLOAT DEFAULT 0,
    metadata JSONB
);

-- Create index on status for filtering
CREATE INDEX idx_markets_status ON markets(status);
CREATE INDEX idx_markets_category ON markets(category);
CREATE INDEX idx_markets_close_time ON markets(close_time);

-- Orders table (Trade history)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(255) NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    side VARCHAR(10) NOT NULL, -- 'yes' or 'no'
    quantity FLOAT NOT NULL,
    price FLOAT NOT NULL,
    order_type VARCHAR(50), -- 'limit', 'market'
    status VARCHAR(50) NOT NULL, -- 'open', 'filled', 'cancelled', 'expired'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    filled_at TIMESTAMP WITH TIME ZONE,
    kalshi_order_id VARCHAR(255),
    metadata JSONB
);

-- Create index on orders for querying
CREATE INDEX idx_orders_market_id ON orders(market_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);

-- Positions table (Current holdings)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(255) NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    side VARCHAR(10) NOT NULL, -- 'yes' or 'no'
    quantity FLOAT NOT NULL,
    avg_price FLOAT NOT NULL,
    current_price FLOAT,
    unrealized_pnl FLOAT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on positions
CREATE INDEX idx_positions_market_id ON positions(market_id);

-- Market history (for tracking price movements)
CREATE TABLE IF NOT EXISTS market_history (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(255) NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
    yes_price FLOAT,
    no_price FLOAT,
    volume FLOAT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on market history
CREATE INDEX idx_market_history_market_id ON market_history(market_id);
CREATE INDEX idx_market_history_recorded_at ON market_history(recorded_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_markets_updated_at BEFORE UPDATE ON markets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data (for testing)
INSERT INTO markets (id, title, subtitle, category, status, ticker, min_price, max_price, metadata)
VALUES
    ('test-market-1', 'Test Market 1', 'A test market for development', 'test', 'open', 'TEST/YESNO', 1, 99, '{"test": true}'),
    ('test-market-2', 'Test Market 2', 'Another test market', 'test', 'closed', 'TEST2/YESNO', 1, 99, '{"test": true}')
ON CONFLICT (id) DO NOTHING;
