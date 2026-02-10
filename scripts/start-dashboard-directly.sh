#!/bin/bash
# Start OpenAlgo Dashboard Directly (Bypass Caddy)
# This bypasses Caddy issues temporarily to get dashboard accessible

echo "🚀 Starting OpenAlgo Dashboard Directly..."

# Activate virtual environment
source /var/python/openalgo-flask/algo.bhakta.us/venv/bin/activate

# Set working directory
cd /var/python/openalgo-flask/algo.bhakta.us

# Try multiple startup methods
if [ -f "app.py" ]; then
    echo "Running Flask app with app.py..."
    python3 app.py
elif [ -f "run.py" ]; then
    echo "Running Flask app with run.py..."
    python3 run.py
elif [ -f "main.py" ]; then
    echo "Running Flask app with main.py..."
    python3 main.py
elif [ -f "openalgo.py" ]; then
    echo "Running Flask app with openalgo.py..."
    python3 openalgo.py
elif [ -f "server.py" ]; then
    echo "Running Flask app with server.py..."
    python3 server.py
else
    # Try importing and running
    echo "Attempting to start Flask app via Python import..."
    python3 -c "from app import create_app; create_app().run(host='0.0.0.0', port=5000, debug=True)"
fi
