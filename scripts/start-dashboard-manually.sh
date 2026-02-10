#!/bin/bash
# Manual Start: OpenAlgo Dashboard (Bypass Caddy Issues)
# Date: February 6, 2026
# Status: Emergency fix to get Super Bowl development running NOW

echo "🚀 STARTING OPENALGO DASHBOARD MANUALLY..."

# Navigate to application directory
cd /var/python/openalgo-flask/algo.bhakta.us

# Activate virtual environment
source venv/bin/activate

# Set environment variables (production)
export DATABASE_URL=postgresql://postgres_user:postgres_password@127.0.0.1:5432/openalgo_db
export REDIS_URL=redis://127.0.0.1:6379/1
export PUBLIC_URL=https://algo.bhakta.us
export DASHBOARD_URL=https://algo.bhakta.us/dashboard
export API_URL=https://algo.bhakta.us/api
export WS_URL=wss://algo.bhakta.us/ws
export NODE_ENV=production
export TZ=America/Chicago
export LOG_LEVEL=INFO

# Super Bowl Configuration
export ENABLE_TAILSCALE=true
export USE_DASHBOARD_KEYS=true
export KALSHI_API_URL=https://demo-api.kalshi.co/trade-api/v2
export KALSHI_ENVIRONMENT=demo
export SUPER_BOWL_ANALYZE_MODE=paper
export SUPER_BOWL_PAPER_BANKROLL=1000
export SUPER_BOWL_RISK_LEVEL=moderate

echo "✅ Environment variables set"
echo ""
echo "🚀 Starting OpenAlgo Dashboard (Gunicorn)..."
echo "   Port: 5000"
echo "   Bind: 127.0.0.1"
echo "   Workers: 3"
echo "   Mode: Production"
echo ""

# Start Gunicorn
gunicorn --workers 3 --bind 127.0.0.1:5000 --timeout 300 --log-level info app:app

echo ""
echo "✅ OpenAlgo Dashboard Started!"
echo ""
echo "🎯 ACCESS DASHBOARD NOW:"
echo "   HTTP:  http://localhost:5000"
echo "   HTTPS: https://algo.bhakta.us (once Caddy is fixed)"
echo "   API:   https://algo.bhakta.us/api"
echo "   WebSocket: wss://algo.bhakta.us/ws"
echo ""
echo "📋 NEXT STEPS:"
echo "   1. Test dashboard at http://localhost:5000"
echo "   2. Once confirmed working, fix Caddy to reverse proxy"
echo "   3. Verify HTTPS at https://algo.bhakta.us"
echo ""
echo "⏱ SUPER BOWL DEVELOPMENT CAN BEGIN NOW!"
echo ""
