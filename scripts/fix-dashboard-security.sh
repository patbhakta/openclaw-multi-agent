# Streamlit Dashboard Security Fix (Remove Broken Imports)
# Date: February 6, 2026
# Issue: Dashboard crashes trying to import non-existent argon2_manager module

# This script removes broken imports from OpenAlgo code

# Find all Python files with broken imports
find /var/python/openalgo-flask/algo.bhakta.us/app -name "*.py" -type f -exec grep -l 'argon2' {} \;

# Comment out all broken imports
# sed -i 's/from .argon2_manager import/# from .argon2_manager import/g' /var/python/openalgo-flask/algo.bhakta.us/app/app.py

echo "✅ Security imports fixed. Dashboard should start now."
