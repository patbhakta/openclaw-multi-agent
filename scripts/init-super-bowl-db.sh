#!/bin/bash
# Super Bowl Database Initialization Script
# Uses PostgreSQL directly via psql (bypassing sqlalchemy dependency issues)

set -e

# Database connection parameters
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5433}
DB_NAME=${DB_NAME:-betting_markets}
DB_USER=${DB_USER:-betting_user}
DB_PASSWORD=${DB_PASSWORD:-betting_password}

echo "🗄️ Initializing Super Bowl Database..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# SQL to create all tables
SQL="
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(64) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Super Bowl Props table (V2 API)
CREATE TABLE IF NOT EXISTS super_bowl_props (
    id SERIAL PRIMARY KEY,
    kalshi_ticker VARCHAR(50) NOT NULL,
    market_type VARCHAR(20) NOT NULL,
    submarket_type VARCHAR(50),
    prop_type VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    value VARCHAR(100),
    side VARCHAR(10),
    price NUMERIC(10,2),
    volume NUMERIC(10,2),
    status VARCHAR(20),
    is_live BOOLEAN DEFAULT FALSE,
    closing_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Signals table
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    prop_id INTEGER REFERENCES super_bowl_props(id),
    signal_type VARCHAR(20) NOT NULL,
    action VARCHAR(10),
    confidence VARCHAR(10),
    edge NUMERIC(10,4),
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Paper Trades table
CREATE TABLE IF NOT EXISTS paper_trades (
    id SERIAL PRIMARY KEY,
    prop_id INTEGER REFERENCES super_bowl_props(id),
    account_id INTEGER REFERENCES users(id),
    action VARCHAR(10),
    amount NUMERIC(10,2),
    status VARCHAR(20),
    is_analyzer_mode BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Settings table (for dashboard keys, analyze mode, etc.)
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    analyze_mode BOOLEAN DEFAULT FALSE,
    demo_mode BOOLEAN DEFAULT TRUE,
    paper_bankroll NUMERIC(10,2) DEFAULT 1000.00,
    risk_level VARCHAR(20) DEFAULT 'moderate',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"

# Execute SQL
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "$SQL"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database initialized successfully!"
    echo ""
    echo "📊 Tables created:"
    echo "   - users (user authentication)"
    echo "   - super_bowl_props (Kalshi V2 markets)"
    echo "   - signals (betting signals)"
    echo "   - paper_trades (paper trading history)"
    echo "   - settings (system configuration)"
    echo ""
    echo "🎯 Database connection:"
    echo "   Host: $DB_HOST"
    echo "   Port: $DB_PORT"
    echo "   Database: $DB_NAME"
    echo "   User: $DB_USER"
    echo ""
    echo "🎯 Next Steps:"
    echo "   1. Load Super Bowl markets via OpenAlgo Dashboard API"
    echo "   2. Generate betting signals using prediction engine"
    echo "   3. Execute paper trades via OpenAlgo Dashboard API"
    echo "   4. Track portfolio and P&L"
    echo "   5. Start Streamlit dashboard for monitoring"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo ""
    echo "❌ Database initialization failed"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   1. Check database container is running: docker ps | grep betting-db"
    echo "   2. Check environment variables are set correctly"
    echo "   3. Verify database credentials are correct"
    echo "   4. Check container logs: docker logs betting-db"
    echo ""
    exit 1
fi
