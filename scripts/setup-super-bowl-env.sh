#!/bin/bash
# Super Bowl System Environment Setup
# Date: February 6, 2026

set -e

echo "🔧 Configuring Environment Variables..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Database Configuration
export DB_HOST=localhost
export DB_PORT=5433
export DB_NAME=betting_markets
export DB_USER=betting_user
export DB_PASSWORD=betting_password
export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

# OpenAlgo Dashboard Configuration
export PUBLIC_URL=https://algo.bhakta.us
export DASHBOARD_URL=https://algo.bhakta.us/dashboard
export API_URL=https://algo.bhakta.us/api
export WS_URL=wss://algo.bhakta.us/ws

# Super Bowl Bot Configuration
export KALSHI_API_URL=https://api.kalshi.com/trade-api/v2
export KALSHI_DEMO_API_URL=https://demo-api.kalshi.co/trade-api/v2
export KALSHI_ENVIRONMENT=demo
export TZ=America/Chicago
export LOG_LEVEL=INFO

echo ""
echo "✅ Environment Variables Set:"
echo "   Database: postgresql://$DB_USER:****@$DB_HOST:$DB_PORT/$DB_NAME"
echo "   Dashboard: https://algo.bhakta.us/dashboard"
echo "   API: https://algo.bhakta.us/api"
echo "   WebSocket: wss://algo.bhakta.us/ws"
echo "   Kalshi: $KALSHI_ENVIRONMENT mode ($KALSHI_DEMO_API_URL)"
echo "   Timezone: $TZ"
echo ""
echo "🎯 Next Step: Test Database Connection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
