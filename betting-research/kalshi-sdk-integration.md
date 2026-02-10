# Kalshi SDK Integration - Super Bowl Prediction System

**Date:** February 6, 2026
**Version:** 1.0
**Status:** Active Development

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Components

```
┌───────────────────────────────────────────────────────────┐
│  Your Dashboard API                         │
│  (Key Management - Hashes Only)              │
│         │                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │  Super Bowl Prediction Bot              │      │
│  │  (Kalshi SDK Client)                     │      │
│  │  - Authentication via dashboard            │      │
│  │  - Market Data via Kalshi API           │      │
│  │  - Signal Generation                     │      │
│  │  - Paper Trading (API Analyzer Mode)    │      │
│  └──────────────────────────────────────────────┘      │
│         │                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │  Simple Streamlit Dashboard              │      │
│  │  - Paper P&L Tracking                │      │
│  │  - Markets Display                     │      │
│  │  - Signals Log                        │      │
│  │  - System Status                       │      │
│  └──────────────────────────────────────────────┘      │
│         │                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │  Your Dashboard API                      │      │
│  │  (Provides API Keys to System)            │      │
│  │  - Stores Actual Kalshi API Keys        │      │
│  │  - Manages Key Rotation                 │      │
│  │  - Provides Dashboard UI (Optional)        │      │
│  └──────────────────────────────────────────────┘      │
└───────────────────────────────────────────────────────────┘
```

---

## 📋 PHASE 1: SDK INTEGRATION (Week 1: Feb 6-9)

### Tasks

#### Task 1.1: Kalshi SDK Installation
- [ ] Install `kalshi-python-sync` SDK
- [ ] Verify installation
- [ ] Test basic connectivity with demo account
- [ ] Document SDK usage

#### Task 1.2: Dashboard API Client
- [ ] Implement authentication (JWT tokens)
- [ ] Implement key fetching (hash-only storage)
- [ ] Implement API proxy calls (for paper trading)
- [ ] Add comprehensive audit logging

#### Task 1.3: Super Bowl Research Module
- [ ] Create research framework
- [ ] Implement team matchup analysis
- [ ] Implement player prop analysis (QB, RB, WR)
- [ ] Implement historical data fetching
- [ ] Create probability estimation models

#### Task 1.4: Paper Trading Module
- [ ] Implement order placement via SDK
- [ ] Implement position sizing (Kelly criterion)
- [ ] Implement P&L tracking
- [ ] Add stop-loss/take-profit logic
- [ ] Enable API Analyzer Mode

#### Task 1.5: Database Integration
- [ ] Update database schema for SDK integration
- [ ] Add tables for signals, paper trades, research data
- [ ] Implement row-level security (account_id)

#### Task 1.6: Security Hardening
- [ ] Implement Argon2-CFFI password hashing
- [ ] Implement Fernet token encryption
- [ ] Add rate limiting (per user, per API key)
- [ ] Create comprehensive audit trail system

---

## 💻 CODE STRUCTURE

### Directory Layout

```
/root/.openclaw/workspace/
├── betting-research/
│   └── kalshi-sdk/              ← SDK Code (copied from forked openalgo)
│       ├── auth_api.py          ← Authentication
│       ├── order_api.py          ← Order Management
│       └── funds.py             ← Portfolio Management
├── shared/
│   ├── documents/
│   │   └── super-bowl-research.md
├── agents/
│   ├── dev-team/
│   │   ├── codex/              ← Will build SDK integration
│   │   ├── sage/               ← Will build Super Bowl research module
│   │   └── pipeline/            ← Will build simple dashboard
│   └── va-team/
│       └── atlas/               ← Will coordinate the effort
└── scripts/
    ├── shared-state.sh           ← Task management
    ├── run-bot.py               ← Will create execution script
    ├── dashboard.py              ← Will create Streamlit dashboard
    └── paper-trading.py           ← Will create paper trading logic
```

---

## 🔐 SECURITY ARCHITECTURE (Production-Grade)

### Key Management (Your Dashboard API)

```python
class DashboardKeyManager:
    def __init__(self, dashboard_url, username, password):
        self.dashboard_url = dashboard_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.jwt_token = None
        self.api_keys_cache = {}  # Cache API keys
    
    def login(self):
        """Authenticate with your dashboard"""
        response = self.session.post(
            f"{self.dashboard_url}/api/auth/login",
            json={"username": self.username, "password": self.password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.jwt_token = data['token']
            return {"success": True, "token": self.jwt_token}
        else:
            return {"success": False, "error": response.text}
    
    def fetch_key(self, service):
        """
        Fetch API key from dashboard
        
        CRITICAL: Your dashboard manages ACTUAL API keys
        We store ONLY SHA-256 hashes (never plaintext)
        """
        if not self.jwt_token:
            self.login()
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        response = self.session.get(
            f"{self.dashboard_url}/api/keys/{service}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            key_hash = data['key_hash']
            expires_at = data['expires_at']
            permissions = data.get('permissions', [])
            
            # Cache key hash
            self.api_keys_cache[service] = key_hash
            
            # Store ONLY hash in database (never plaintext)
            self._store_key_hash(service, key_hash, expires_at, permissions, key_type='dashboard')
            
            return {
                "success": True,
                "key_hash": key_hash,
                "expires_at": expires_at,
                "permissions": permissions,
                "dashboard_managed": True
            }
        else:
            return {"success": False, "error": response.text}
    
    def proxy_api_call(self, service, endpoint, method='GET', data=None, params=None):
        """
        Make API call through your dashboard
        
        Your dashboard acts as proxy:
        1. Validates key hash
        2. Uses stored API key to make actual call
        3. Returns results to us
        
        This pattern: API keys never leave your dashboard
        """
        if not self.jwt_token:
            self.login()
        
        headers = {"Authorization": f"Bearer {self.jwt_token}"}
        api_url = f"{self.dashboard_url}/api/proxy/{service}/{endpoint}"
        
        if method == 'GET':
            if data:
                response = self.session.get(api_url, headers=headers, params=data)
            else:
                response = self.session.get(api_url, headers=headers)
        elif method == 'POST':
            response = self.session.post(api_url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response.json()
    
    def _store_key_hash(self, service, key_hash, expires_at, permissions, key_type):
        """
        Store ONLY hash in database
        NEVER store plaintext key
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if service has existing active key
            cursor.execute("""
                SELECT id FROM api_keys
                WHERE service = %s AND is_active = TRUE
                ORDER BY created_at DESC LIMIT 1
                FOR UPDATE OF api_keys
            """, (service,))
            
            result = cursor.fetchone()
            
            if result:
                existing_id = result[0]
                
                # Deactivate old key
                cursor.execute("""
                    UPDATE api_keys
                    SET is_active = FALSE,
                        last_access_at = NOW()
                    WHERE id = %s
                    """, (existing_id,))
            
            # Insert new key hash
            cursor.execute("""
                INSERT INTO api_keys
                (account_id, service, key_hash, key_type, permissions, expires_at, created_at, is_active)
                VALUES (1, %s, %s, %s, %s, %s, TRUE, NOW())
                """, (service, key_hash, json.dumps(permissions), expires_at, key_type))
            
            conn.commit()
            self._log_key_fetch(service, key_hash, 'dashboard', 'api_call')
```

### Super Bowl Prediction Bot

```python
class SuperBowlPredictor:
    def __init__(self, db_connection, dashboard_api):
        self.db = db_connection
        self.dashboard = dashboard_api
        self.api_keys = {}
    
    def initialize(self):
        """Initialize Super Bowl prediction system"""
        # Fetch Kalshi API key via dashboard
        kalshi_key = self.dashboard.fetch_key("kalshi_api")
        
        if not kalshi_key.get("success"):
            raise ValueError("Failed to fetch Kalshi API key from dashboard")
        
        # Store key hash
        self.api_keys["kalshi"] = kalshi_key["key_hash']
        
        # Initialize Kalshi SDK client
        from kalshi_python_sync import ApiClient, Configuration
        from utils.constants import EXCHANGE_KALSHI
        
        host = "https://demo-api.kalshi.co/trade-api/v2"
        configuration = Configuration(host=host)
        configuration.api_key['KSA-SESSION-KEY'] = kalshi_key["key_hash']  # Use key hash
        
        self.kalshi_client = ApiClient(configuration)
        
        # Login to get session token
        auth_inst = self.kalshi_client.auth()
        login_request = {
            "email": "demo@kalshi.co",
            "password": "demo"  # For demo account
        }
        
        login_response = auth_inst.login(login_request)
        
        if login_response.status_code != 200:
            raise ValueError("Failed to authenticate with Kalshi")
        
        self.kalshi_session_token = login_response.token
        
        print("✅ Initialized Super Bowl prediction system")
        return True
    
    def get_super_bowl_markets(self):
        """Get Super Bowl markets from Kalshi"""
        from kalshi_python_sync.api import market_api
        
        try:
            # Get markets with exchange type and event ticker
            markets = self.kalshi_client.markets.get_markets(
                exchange=EXCHANGE_KALSHI,
                series_ticker="NFL"  # NFL league
                event_ticker="SB-LX-2026"  # Super Bowl LX
                event_type="markets"
            )
            return markets
        except Exception as e:
            print(f"❌ Error fetching Super Bowl markets: {e}")
            return None
    
    def analyze_prop(self, prop_type, prop_value):
        """
        Analyze prop for edge calculation
        """
        # Calculate true probability
        true_prob = self._calculate_probability(prop_type, prop_value)
        
        # Get market price
        market_price = self._get_market_price(prop_type, prop_value)
        
        # Calculate edge
        edge = true_prob - market_price
        
        # Determine bet action
        if edge > 0.05:  # 5% edge threshold
            return {
                "action": "BET",
                "confidence": "HIGH",
                "edge": f"{edge:.1%}",
                "reasoning": f"Market mispriced by {edge:.1%}"
            }
        elif edge > 0.02:  # 2% edge threshold
            return {
                "action": "BET",
                "confidence": "MEDIUM",
                "edge": f"{edge:.1%}",
                "reasoning": f"Slight market inefficiency ({edge:.1%})"
            }
        else:
            return {
                "action": "PASS",
                "confidence": "LOW",
                "edge": f"{edge:.1%}",
                "reasoning": "No significant edge"
            }
    
    def _calculate_probability(self, prop_type, prop_value):
        """
        Calculate true probability using multiple methods
        """
        # Method 1: Historical performance
        historical_prob = self._get_historical_probability(prop_type, prop_value)
        
        # Method 2: Market analysis
        market_prob = self._get_market_probability(prop_type, prop_value)
        
        # Method 3: Machine learning prediction
        ml_prob = self._get_ml_probability(prop_type, prop_value)
        
        # Weighted average of methods
        weights = [0.4, 0.3, 0.3]  # Historical, market, ML
        
        true_prob = (historical_prob * weights[0] +
                     market_prob * weights[1] +
                     ml_prob * weights[2])
        
        return true_prob
    
    def _get_market_price(self, prop_type, prop_value):
        """
        Get current market price for prop type and value
        """
        # In real implementation, this would query Kalshi API
        # For now, return fixed prices for simulation
        market_prices = {
            "passing_yards": 249.5,
            "passing_tds": 2.5,
            "rushing_yards": 89.5,
            "receiving_yards": 64.5,
            "touchdowns": 1.5,
            "total_points": 47.5
        }
        
        return market_prices.get(prop_type, 100)  # Default value if not found
```

### Paper Trading Module (API Analyzer Mode)

```python
class PaperTradingBot:
    def __init__(self, db_connection, dashboard_api):
        self.db = db_connection
        self.dashboard = dashboard_api
        self.paper_bankroll = 1000  # $1,000 paper
        self.risk_level = "moderate"  # 2-5% per bet
        self.positions = []
        self.trades = []
    
    def place_paper_trade(self, prop_id, action, amount):
        """
        Execute paper trade via dashboard API proxy
        
        In API Analyzer Mode:
        - No real money risk
        - All trades are simulated
        - P&L is tracked but not real
        """
        # Validate risk
        if amount > self.paper_bankroll * 0.05:  # Max 5% risk
            return {"success": False, "error": "Amount exceeds max risk (5% of bankroll)"}
        
        # Execute via dashboard API proxy
        response = self.dashboard.proxy_api_call(
            service="kalshi",
            endpoint="place_order",
            method="POST",
            data={
                "analyzer_mode": True,  # Key parameter for paper trading
                "prop_id": prop_id,
                "action": action,  # "BUY" or "SELL"
                "amount": amount,
                "market_type": "nfl_superbowl"
                "paper_account_id": 1  # Your account ID
            }
        )
        
        if response.get("success"):
            trade_id = response.get("trade_id")
            
            # Log paper trade
            self._log_paper_trade(prop_id, action, amount, trade_id, "PENDING")
            
            # Update position
            self.positions.append({
                "prop_id": prop_id,
                "action": action,
                "amount": amount,
                "status": "PENDING",
                "trade_id": trade_id
            })
            
            return {
                "success": True,
                "trade_id": trade_id,
                "paper_trade": True,
                "analyzer_mode": True,
                "message": "Paper trade executed (simulated)"
            }
        else:
            return {
                "success": False,
                "error": response.get("error")
            }
    
    def get_paper_portfolio(self):
        """
        Get paper trading portfolio status
        
        In API Analyzer Mode:
        - Simulated P&L (not real money)
        - Win rate calculation
        - Open positions tracking
        """
        total_pnl = sum(trade["amount"] for trade in self.trades if trade["action"] == "SELL")
        
        win_rate = 0
        if len(self.trades) > 0:
            win_rate = (sum(1 for trade in self.trades if trade["result"] == "WIN") / len(self.trades)) * 100
        
        return {
            "paper_bankroll": self.paper_bankroll,
            "total_pnl": total_pnl,
            "win_rate": f"{win_rate:.1f}%",
            "open_positions": len(self.positions),
            "total_trades": len(self.trades),
            "analyzer_mode": True  # Indicates paper trading
        }
    
    def _log_paper_trade(self, prop_id, action, amount, trade_id, status):
        """Log paper trade for audit trail"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO paper_trades
                (prop_id, action, amount, status, trade_id, created_at, analyzer_mode)
                VALUES (%s, %s, %s, %s, %s, NOW(), TRUE)
                """, (prop_id, action, amount, trade_id, status))
            conn.commit()
```

---

## 🔒 SECURITY MEASURES

### Authentication
- ✅ JWT tokens (24-hour expiry)
- ✅ Dashboard API integration (your dashboard manages keys)
- ✅ Hash-only storage (never plaintext keys)

### Authorization
- ✅ Row-level security (account_id for multi-user)
- ✅ Role-based access control
- ✅ API Analyzer Mode for paper trading

### Encryption
- ✅ Fernet token encryption (for API keys)
- ✅ Argon2-CFFI password hashing (PHC winner)
- ✅ SHA-256 key hashing

### Protection
- ✅ Rate limiting (per user, per API key)
- ✅ Comprehensive audit trail
- ✅ IP blocking for suspicious activity

---

## 📋 PHASE 2: DASHBOARD DEVELOPMENT (Week 3: Feb 13-19)

### Streamlit Dashboard Pages

#### Page 1: Main Dashboard
- Paper portfolio overview
- P&L metrics
- Win rate calculation
- System status (bot health, API connectivity)
- Bot controls (start/stop/refresh)

#### Page 2: Markets
- Live Super Bowl prop markets
- Line history and movements
- Market depth (if available)
- Real-time updates

#### Page 3: Signals
- All betting signals with reasoning
- Filter by confidence level
- Filter by bet type
- Signal history

#### Page 4: Settings
- Dashboard API configuration
- API key status
- Bot configuration
- Risk level adjustment

---

## 📊 TESTING STRATEGY

### Phase 1: Unit Testing (Feb 8-9)
- [ ] Test authentication flows
- [ ] Test key fetching (dashboard proxy)
- [ ] Test order placement (API Analyzer Mode)
- [ ] Test signal generation
- [ ] Validate edge calculations

### Phase 2: Integration Testing (Feb 10-14)
- [ ] End-to-end dashboard testing
- [ ] Mock market data simulation
- [ ] Paper trading simulation
- [ ] Validate P&L calculations

### Phase 3: Backtesting (Feb 17-21)
- [ ] Backtest strategies with historical Super Bowl data
- [ ] Validate win rate > 55%
- [ ] Optimize confidence thresholds

### Phase 4: Super Bowl Saturday Test (Feb 8)
- [ ] Enable API Analyzer Mode in dashboard
- [ ] Load final strategy
- [ ] Start paper trading bot
- [ ] Monitor all activity
- [ ] Generate real-time signals

---

## 🎯 SUCCESS CRITERIA

### Paper Trading System
- ✅ Zero plaintext keys in bot
- ✅ Your dashboard manages actual API keys
- ✅ Hash-based key storage (SHA-256)
- ✅ Comprehensive audit trail
- ✅ API Analyzer Mode for safe testing
- ✅ Real-time P&L tracking

### Super Bowl Prediction
- ✅ Production-grade Kalshi SDK integration
- ✅ Real-time market data access
- ✅ Multi-method probability estimation
- ✅ Machine learning predictions
- ✅ Edge calculation and risk management

### Dashboard
- ✅ Streamlit simple dashboard (4 pages)
- ✅ Real-time updates
- ✅ Bot controls
- ✅ System health monitoring

---

## 📅 NEXT STEPS

### Immediate (This Week)
1. [ ] Install Kalshi SDK
2. [ ] Copy API code from forked repository
3. [ ] Create dashboard API client
4. [ ] Implement Super Bowl prediction engine
5. [ ] Implement paper trading module
6. [ ] Create Streamlit dashboard
7. [ ] Implement security hardening
8. [ ] Create database schema updates

### Timeline to Super Bowl (Feb 9)
- **Week 1 (Feb 6-9):** SDK Integration + Dashboard API Client
- **Week 2 (Feb 10-14):** Super Bowl Strategy + Simple Dashboard
- **Week 3 (Feb 17-21):** Testing + Backtesting
- **Feb 8 (Saturday):** Test Day (Paper Trading)
- **Feb 9 (Sunday):** Super Bowl Game Day (Live Paper Trading)

---

## 📊 SYSTEM ARCHITECTURE

```
┌───────────────────────────────────────────────────────────┐
│  Your Dashboard                              │
│         │                             │
│  ┌──────────────────────────────────────┐     │
│  │  API Key Management          │     │
│  │  (Stores Actual Keys)          │     │
│  └──────────────────────────────────────┘     │
│         │                             │
│  ▼                             │
│  ┌──────────────────────────────────────────────┐     │
│  │  Super Bowl Prediction Bot         │     │
│  │  - Kalshi SDK Client           │     │
│  │  - Auth via Dashboard          │     │
│  │  - Market Data via Kalshi       │     │
│  │  - Signal Generation            │     │
│  └──────────────────────────────────────────────┘     │
│         │                             │
│  ▼                             │
│  ┌──────────────────────────────────────────────┐     │
│  │  Simple Streamlit Dashboard         │     │
│  │  - Paper P&L Tracking          │     │
│  │  - Markets Display              │     │
│  │  - Signals Log                  │     │
│  └──────────────────────────────────────────────┘     │
│         │                             │
│  ▼                             │
│  ┌──────────────────────────────────────────────┐     │
│  │  Betting Research Database         │     │
│  │  - User Data                   │     │
│  │  - API Keys (Hashes)          │     │
│  │  - Paper Trades                │     │
│  │  - Signals                     │     │
│  │  - Research Data               │     │
│  └──────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────┘
```

---

**Document Created:** `/root/.openclaw/workspace/betting-research/kalshi-sdk-integration.md`

**Status:** Ready to start implementation

**Next Step:** Install Kalshi SDK and begin Phase 1 tasks
