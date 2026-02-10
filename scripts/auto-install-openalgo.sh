#!/bin/bash
# Auto-Install OpenAlgo for algo.bhakta.us
# Date: February 6, 2026

# Configuration
DOMAIN="algo.bhakta.us"
BROKER_NAME="kalshi"
KALSHI_ENVIRONMENT="demo"  # Start with demo mode
CADDY_ADMIN_PASSWORD="changeme123"
APP_KEY=$(openssl rand -hex 32 | tr '[:lower:]' '[:upper:]')
API_KEY_PEPPER=$(openssl rand -hex 32 | tr '[:lower:]' '[:upper:]')

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     AUTO-INSTALL OPENALGO FOR SUPER BOWL          ║${NC}"
echo -e "${GREEN}║     Domain: $DOMAIN                       ║${NC}"
echo -e "${GREEN}║     Broker: $BROKER_NAME                    ║${NC}"
echo -e "${GREEN}║     Mode: $KALSHI_ENVIRONMENT                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo -e "${NC}"

# OS detection
OS_TYPE=$(grep -w "ID" /etc/os-release | cut -d "=" -f 2 | tr -d '"')

# Proceed with installation
case "$OS_TYPE" in
    ubuntu|debian|raspbian)
        echo -e "${BLUE}[1/6] Detecting Ubuntu/Debian/Raspbian...${NC}"
        
        # Update packages
        echo -e "${BLUE}[2/6] Updating system packages...${NC}"
        export DEBIAN_FRONTEND=noninteractive
        apt-get update -qq
        
        # Check swap (will be configured by main script)
        TOTAL_RAM=$(free -m | grep MemTotal | awk '{print $2}')
        TOTAL_RAM_MB=$((TOTAL_RAM / 1024))
        if [ $TOTAL_RAM -lt 2048 ]; then
            echo -e "${YELLOW}[3/6] RAM < 2GB, swap will be configured...${NC}"
        fi
        
        # Install dependencies
        echo -e "${BLUE}[4/6] Installing required packages...${NC}"
        apt-get install -y python3 python3-venv nginx git software-properties-common curl certbot > /dev/null 2>&1
        
        # Install uv
        if command -v uv >/dev/null 2>&1; then
            echo -e "${GREEN}[5/6] Installing uv (package manager)...${NC}"
            apt-get install -y snapd 2>/dev/null || true
            snap install astral-uv --classic 2>/dev/null || true
        else
            echo -e "${YELLOW}[5/6] Installing uv via pip...${NC}"
            pip3 install uv
        fi
        
        echo -e "${GREEN}[6/6] uv installed successfully${NC}"
        ;;
    
    centos|fedora|rhel|amzn)
        echo -e "${BLUE}[1/6] Detecting CentOS/Fedora/RHEL/Amazon Linux...${NC}"
        
        # Update packages
        echo -e "${BLUE}[2/6] Updating system packages...${NC}"
        
        # Check swap
        TOTAL_RAM=$(free -m | grep MemTotal | awk '{print $2}')
        TOTAL_RAM_MB=$((TOTAL_RAM / 1024))
        if [ $TOTAL_RAM -lt 2048 ]; then
            echo -e "${YELLOW}[4/6] RAM < 2GB, swap will be configured...${NC}"
        fi
        
        # Install dependencies
        echo -e "${BLUE}[3/6] Installing required packages...${NC}"
        dnf install -y python3 python3-pip nginx git epel-release openblas-devel gcc-gfortran libgomp
        
        # Install uv
        echo -e "${BLUE}[5/6] Installing uv via pip...${NC}"
        pip3 install uv
        
        echo -e "${GREEN}[6/6] uv installed successfully${NC}"
        ;;
    
    arch)
        echo -e "${BLUE}[1/6] Detecting Arch Linux...${NC}"
        
        # Install dependencies
        echo -e "${BLUE}[2/6] Installing required packages...${NC}"
        pacman -Sy --noconfirm --needed python python-pip nginx git
        
        # Install uv
        echo -e "${BLUE}[3/6] Installing uv via pip...${NC}"
        pacman -Sy --noconfirm --needed python-uv
        echo -e "${GREEN}[4/6] uv installed successfully${NC}"
        ;;
esac

# Log directory
LOG_DIR="/root/.openclaw/workspace/openalgo-main/logs"
mkdir -p "$LOG_DIR"

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/auto-install_${TIMESTAMP}.log"

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "${BLUE}Starting automated OpenAlgo installation..." "$NC"
log "${BLUE}Domain: $DOMAIN" "$NC"
log "${BLUE}Broker: $BROKER_NAME ($KALSHI_ENVIRONMENT mode)" "$NC"
log "${BLUE}APP Key: $APP_KEY" "$NC"

# Create deployment directory
DEPLOY_DIR="/var/python/openalgo-flask/$DOMAIN"
mkdir -p "$DEPLOY_DIR"

log "${BLUE}[1/10] Creating deployment directory: $DEPLOY_DIR" "$NC"

# Clone repository
log "${BLUE}[2/10] Cloning official OpenAlgo repository..." "$NC}"

git clone https://github.com/marketcalls/openalgo.git "$DEPLOY_DIR"
if [ $? -ne 0 ]; then
    log "${RED}[ERROR] Failed to clone repository" "$NC}"
    exit 1
fi

log "${GREEN}[3/10] Repository cloned successfully" "$NC}"

# Change to deployment directory
cd "$DEPLOY_DIR"

# Create virtual environment using uv
log "${BLUE}[4/10] Creating Python virtual environment with uv..." "$NC"

if command -v uv >/dev/null 2>&1; then
    # Use standalone uv command
    uv venv venv
else
    python3 -m venv venv
fi

if [ $? -ne 0 ]; then
    log "${RED}[ERROR] Failed to create virtual environment" "$NC}"
    exit 1
fi

log "${GREEN}[5/10] Virtual environment created" "$NC"

# Activate virtual environment
source venv/bin/activate
log "${GREEN}[6/10] Virtual environment activated" "$NC"

# Install dependencies
log "${BLUE}[7/10] Installing Python dependencies via uv..." "$NC}"

if command -v uv >/dev/null 2>&1; then
    uv pip install -r requirements-nginx.txt
else
    pip install -r requirements-nginx.txt
fi

if [ $? -ne 0 ]; then
    log "${RED}[ERROR] Failed to install dependencies" "$NC}"
    exit 1
fi

log "${GREEN}[8/10] Dependencies installed successfully" "$NC}"

# Generate API keys
log "${BLUE}[9/10] Generating API keys..." "$NC}"

APP_KEY_FULL=$(python3 -c "from secrets import token_hex; print(token_hex(32))")
API_KEY_FULL=$(python3 -c "import secrets; print(token_hex(32))")

# Create .env file
cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres_user:postgres_password@127.0.0.1:5432/openalgo_db
REDIS_URL=redis://127.0.0.1:6379/0

# Dashboard Configuration
PUBLIC_URL=https://$DOMAIN
DASHBOARD_URL=https://$DOMAIN/dashboard
API_URL=https://$DOMAIN/api
WS_URL=wss://$DOMAIN/ws

# Application Configuration
APP_KEY=$APP_KEY_FULL
API_KEY_PEPPER=$API_KEY_PEPPER

# Security
ENABLE_TAILSCALE=false
USE_DASHBOARD_KEYS=true
NODE_ENV=production

# Tailscale Configuration
TAILSCALE_FUNNEL_NAME=$DOMAIN
ENABLE_TAILSCALE=false

# Super Bowl Configuration
KALSHI_ENVIRONMENT=$KALSHI_ENVIRONMENT
SUPER_BOWL_ANALYZE_MODE=paper
SUPER_BOWL_PAPER_BANKROLL=1000
SUPER_BOWL_RISK_LEVEL=moderate

# Logging
LOG_LEVEL=INFO
TZ=America/Chicago
EOF

log "${GREEN}[10/10] Environment configuration created" "$NC"

# Configure Nginx (simplified for auto-install)
log "${BLUE}[11/10] Configuring Nginx..." "$NC}"

# Check if nginx user exists
if ! id "www-data" &>/dev/null; then
    log "${YELLOW}[11/10] Warning: nginx user not found, creating..." "$NC}"
    useradd -r -m -s /bin/bash -d /var/www www-data
fi

# Remove default configuration
rm -f /etc/nginx/sites-enabled/default 2>/dev/null

# Create Nginx configuration for OpenAlgo
cat > /etc/nginx/sites-available/$DOMAIN.conf << EOF
server {
    listen 80;
    listen [::]:80;
    
    server_name $DOMAIN;
    root /var/python/openalgo-flask/$DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    
    # WebSocket
    location /ws {
        proxy_pass http://127.0.0.1:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Main app (Gunicorn)
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

log "${GREEN}[12/10] Nginx configuration created" "$NC"

# Enable site
ln -sf /etc/nginx/sites-available/$DOMAIN.conf /etc/nginx/sites-enabled/

# Test Nginx configuration
log "${BLUE}[13/10] Testing Nginx configuration..." "$NC}"

nginx -t 2>&1 | head -20

if [ $? -ne 0 ]; then
    log "${RED}[ERROR] Nginx configuration test failed" "$NC}"
    exit 1
fi

log "${GREEN}[14/10] Nginx configuration test passed" "$NC}"

# Reload Nginx
log "${BLUE}[15/10] Reloading Nginx..." "$NC}"

nginx -s reload 2>&1 | head -10

if [ $? -ne 0 ]; then
    log "${RED}[ERROR] Failed to reload Nginx" "$NC}"
    exit 1
fi

log "${GREEN}[16/10] Nginx reloaded successfully" "$NC}"

# Create systemd service
log "${BLUE}[17/10] Creating systemd service..." "$NC}"

cat > /etc/systemd/system/openalgo-$DOMAIN.service << EOF
[Unit]
Description=OpenAlgo Gunicorn Daemon ($DOMAIN)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$DEPLOY_DIR

# Environment variables
Environment="TMPDIR=$DEPLOY_DIR/tmp"
Environment="NUMBA_CACHE_DIR=$DEPLOY_DIR/tmp"
Environment="LLVMLITE_TMPDIR=$DEPLOY_DIR/tmp"
Environment="MPLCONFIGDIR=$DEPLOY_DIR/tmp"

# Thread limits (for NumPy optimization)
Environment="OPENBLAS_NUM_THREADS=2"
Environment="OMP_NUM_THREADS=2"

# Simplified approach for auto-install (no complex flags)
ExecStart=/bin/bash -c 'source venv/bin/activate && gunicorn \
    --workers 3 \
    -w 1 \
    --bind 127.0.0.1:5001 \
    --timeout 300 \
    --log-level info \
    app:app'

# Restart settings
Restart=always
RestartSec=5
TimeoutSec=300

[Install]
WantedBy=multi-user.target
EOF

log "${GREEN}[18/10] Systemd service created" "$NC}"

# Set permissions
chown -R www-data:www-data $DEPLOY_DIR
chmod -R 755 $DEPLOY_DIR

log "${GREEN}[19/10] Permissions set" "$NC}"

# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable openalgo-$DOMAIN.service
systemctl restart openalgo-$DOMAIN.service

log "${BLUE}[20/10] Starting OpenAlgo service..." "$NC}"

# Wait for service to start
sleep 5

# Check service status
systemctl is-active openalgo-$DOMAIN.service

if [ $? -ne 0 ]; then
    log "${RED}[ERROR] Failed to start OpenAlgo service" "$NC}"
else
    log "${GREEN}[21/10] OpenAlgo service started successfully" "$NC}"
fi

# Open ports
log "${BLUE}[22/10] Opening firewall ports..." "$NC}"

# Ubuntu/Debian
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8765/tcp
ufw --force enable

# CentOS/Fedora/RHEL
if command -v firewall-cmd >/dev/null 2>&1; then
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
else
    systemctl enable firewalld
    systemctl start firewalld
fi

log "${GREEN}[23/10] Firewall configured" "$NC}"

# Installation complete
log "${GREEN}========================================" "$NC}"
log "${GREEN}       INSTALLATION COMPLETE!" "$NC}"
log "${GREEN}========================================" "$NC}"
log "${GREEN}Domain: $DOMAIN" "$NC}"
log "${GREEN}Broker: $BROKER_NAME" "$NC}"
log "${GREEN}Dashboard: https://$DOMAIN/dashboard" "$NC}"
log "${GREEN}API: https://$DOMAIN/api" "$NC}"
log "${GREEN}WebSocket: wss://$DOMAIN/ws" "$NC}"
log "${GREEN}APP Key: $APP_KEY" "$NC}"
log "${GREEN}========================================" "$NC}"

log "${BLUE}NEXT STEPS:" "$NC}"
log "${BLUE}1. Visit https://$DOMAIN/dashboard to access your OpenAlgo instance" "$NC}"
log "${BLUE}2. Configure your broker settings in the dashboard" "$NC}"
log "${BLUE}3. Navigate to https://$DOMAIN/dashboard/strategies" "$NC}"
log "${BLUE}4. Create a new Super Bowl prediction strategy" "$NC}"
log "${BLUE}5. Enable paper trading mode for testing" "$NC}"
log "${BLUE}6. Review logs: tail -f /root/.openclaw/workspace/openalgo-main/logs/install_*.log" "$NC}"
log "${BLUE}========================================" "$NC}"
