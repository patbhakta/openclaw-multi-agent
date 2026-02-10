#!/bin/bash
# Start OpenAlgo Dashboard Directly (Bypass Caddy)
# This bypasses Caddy temporarily to test if dashboard app is working

echo "🚀 Starting OpenAlgo Dashboard Directly..."

# Activate virtual environment
source /var/python/openalgo-flask/algo.bhakta.us/venv/bin/activate

# Start Flask application
python3 -m app
