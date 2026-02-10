#!/bin/bash
# Install Caddy web server for Super Bowl SaaS platform
# Date: February 6, 2026

set -e

echo "🚀 Installing Caddy Web Server for Super Bowl SaaS..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if Caddy is already installed
if command -v caddy &> /dev/null; then
    echo "✅ Caddy already installed"
    CADDY_VERSION=$(caddy version)
    echo "   Version: $CADDY_VERSION"
else
    echo "📦 Installing Caddy..."
    
    # Update package lists
    apt update
    
    # Install Caddy
    apt install -y caddy
    
    CADDY_VERSION=$(caddy version)
    echo "✅ Caddy installed: $CADDY_VERSION"
fi

echo ""
echo "✅ Step 1 Complete: Caddy installed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
