# Kalshi API Integration with OpenAlgo Dashboard Key Management

This document explains how to use the Kalshi API client with OpenAlgo's secure credential storage system.

## Overview

The Kalshi integration uses OpenAlgo's production-grade key management system:
- **Credentials encrypted** with Fernet (AES-128 CBC mode)
- **Credentials hashed** with Argon2-CFFI (PHC winner)
- **Automatic token refresh** on 401 errors
- **Demo/Production environments** supported
- **Zero real money risk** (demo environment for paper trading)

## Quick Start

### 1. Store Kalshi Credentials

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/openalgo')
from database.auth_db import upsert_kalshi_credentials

# Store credentials (demo environment)
upsert_kalshi_credentials(
    email="your_email@example.com",
    password="your_password",
    environment="demo"  # Use 'production' for live trading
)
```

### 2. Use Kalshi Client

```python
from kalshi_client import KalshiClient

# Initialize with OpenAlgo integration
client = KalshiClient(email="your_email@example.com", use_openalgo=True)

# Get markets
markets = client.get_markets(status='open', limit=10)
print(f"Found {len(markets)} markets")

# Place an order (paper trading)
order = client.place_order(
    market_id='HIGH-EWGS-2026-02-09',
    side='yes',
    quantity=10,
    price=50
)
print(f"Order ID: {order.get('order_id')}")

# Get positions
positions = client.get_positions()
print(f"Current positions: {len(positions)}")
```

## API Reference

### KalshiClient

Initialize Kalshi client with OpenAlgo credentials.

**Parameters:**
- `email` (str): Kalshi account email (required for OpenAlgo mode)
- `use_openalgo` (bool): Use OpenAlgo credential storage (default: True)

**Example:**
```python
client = KalshiClient(email="user@example.com", use_openalgo=True)
```

### authenticate()

Authenticate with Kalshi API.

**Returns:**
- `bool`: True if successful, False otherwise

**Example:**
```python
if client.authenticate():
    print("✅ Authenticated successfully")
else:
    print("❌ Authentication failed")
```

### get_markets(status='open', limit=100)

Get list of markets.

**Parameters:**
- `status` (str): Market status filter ('open', 'closed', 'settled')
- `limit` (int): Maximum number of markets to return

**Returns:**
- `list`: List of market dictionaries

**Example:**
```python
markets = client.get_markets(status='open', limit=50)
for market in markets:
    print(f"{market['ticker']}: {market['title']}")
```

### get_market(market_id)

Get details for a specific market.

**Parameters:**
- `market_id` (str): Market ticker or ID

**Returns:**
- `dict`: Market data or None

**Example:**
```python
market = client.get_market('HIGH-EWGS-2026-02-09')
print(market['title'])
print(market['subtitle'])
```

### get_orderbook(market_id)

Get orderbook for a market.

**Parameters:**
- `market_id` (str): Market ticker or ID

**Returns:**
- `dict`: Orderbook data or None

**Example:**
```python
orderbook = client.get_orderbook('HIGH-EWGS-2026-02-09')
print(f"Yes orders: {len(orderbook['yes'])}")
print(f"No orders: {len(orderbook['no'])}")
```

### place_order(market_id, side, quantity, price, order_type='limit')

Place an order.

**Parameters:**
- `market_id` (str): Market ticker or ID
- `side` (str): 'yes' or 'no'
- `quantity` (int): Number of contracts
- `price` (int): Price in cents (1-99)
- `order_type` (str): 'limit' or 'market'

**Returns:**
- `dict`: Order response or None

**Example:**
```python
order = client.place_order(
    market_id='HIGH-EWGS-2026-02-09',
    side='yes',
    quantity=10,
    price=50,
    order_type='limit'
)
print(f"Order ID: {order.get('order_id')}")
print(f"Order status: {order.get('status')}")
```

### get_positions()

Get current positions.

**Returns:**
- `list`: List of positions

**Example:**
```python
positions = client.get_positions()
total_pnl = sum(p['pnl'] for p in positions)
print(f"Total P&L: ${total_pnl}")
```

## OpenAlgo Auth Functions

### upsert_kalshi_credentials(email, password, environment='demo')

Store or update Kalshi credentials using OpenAlgo's secure storage.

**Parameters:**
- `email` (str): Kalshi account email
- `password` (str): Kalshi account password
- `environment` (str): 'demo' or 'production' (default: 'demo')

**Returns:**
- `int`: Auth object ID or None on failure

**Example:**
```python
from database.auth_db import upsert_kalshi_credentials

upsert_kalshi_credentials(
    email="user@example.com",
    password="secure_password",
    environment="demo"
)
```

### authenticate_kalshi(email, bypass_cache=False)

Authenticate with Kalshi API and cache session token.

**Parameters:**
- `email` (str): Kalshi account email
- `bypass_cache` (bool): Skip cache and query DB directly (for token refresh)

**Returns:**
- `str`: Session token or None

**Example:**
```python
from database.auth_db import authenticate_kalshi

token = authenticate_kalshi("user@example.com")
if token:
    print(f"✅ Authenticated with token: {token[:10]}...")
```

### get_kalshi_credentials(email)

Get Kalshi credentials (email, password, environment) for direct use.

**Parameters:**
- `email` (str): Kalshi account email

**Returns:**
- `dict`: Credentials dictionary or None

**Example:**
```python
from database.auth_db import get_kalshi_credentials

creds = get_kalshi_credentials("user@example.com")
if creds:
    print(f"Environment: {creds['environment']}")
    print(f"Email: {creds['email']}")
    # Note: Password is decrypted for use with Kalshi API
```

### get_kalshi_environment(email)

Get Kalshi environment for an email.

**Parameters:**
- `email` (str): Kalshi account email

**Returns:**
- `str`: 'demo' or 'production'

**Example:**
```python
from database.auth_db import get_kalshi_environment

env = get_kalshi_environment("user@example.com")
if env == 'demo':
    print("Using demo environment (paper trading)")
else:
    print("Using production environment (real money)")
```

## Environment Configuration

### Demo Environment (Recommended for Paper Trading)

**URL:** `https://demo-api.kalshi.co/trade-api/v2`

**Benefits:**
- No real money risk
- Full API functionality
- Same behavior as production

**Use case:** Testing, development, paper trading

### Production Environment (Real Money Trading)

**URL:** `https://api.kalshi.com/trade-api/v2`

**WARNING:** Real money risk

**Use case:** Live trading

## Token Refresh

The Kalshi client automatically handles token expiration:

1. **Initial authentication:** Client authenticates and caches session token
2. **API request:** Client uses cached token
3. **401 error:** Token expired, client:
   - Bypasses cache
   - Refreshes token from Kalshi API
   - Retries request with fresh token

This is transparent to the user - just call methods normally.

## Security Features

### Credential Storage

- **Password:** Encrypted with Fernet (AES-128 CBC mode)
- **Password Hash:** Hashed with Argon2-CFFI (PHC winner)
- **Salt:** Generated per password
- **Pepper:** Adds security layer (32+ hex chars from API_KEY_PEPPER)

### Cache Management

- **Valid tokens:** Cached for session expiry time (default: 3 AM IST)
- **Invalid tokens:** Cached for 5 minutes (prevents brute force)
- **Cache invalidation:** Automatic on credential changes

### Revocation

Set `is_revoked=True` to immediately invalidate credentials:

```python
from database.auth_db import Auth, db_session

auth_obj = Auth.query.filter_by(name="user@example.com").first()
auth_obj.is_revoked = True
db_session.commit()
```

## Testing

### Unit Tests

Run unit tests for Kalshi client:

```bash
cd /root/.openclaw/workspace/betting-research
pytest tests/test_kalshi_openalgo.py -v
```

### Integration Tests

Test with Kalshi demo API:

```python
from kalshi_client import KalshiClient

# Initialize with demo credentials
client = KalshiClient(email="your_email@example.com", use_openalgo=True)

# Test authentication
if client.authenticate():
    print("✅ Authentication successful")

    # Test market retrieval
    markets = client.get_markets(limit=5)
    print(f"✅ Retrieved {len(markets)} markets")

    # Test order placement (small amount)
    order = client.place_order(
        market_id=markets[0]['ticker'],
        side='yes',
        quantity=1,
        price=50
    )
    print(f"✅ Order placed: {order.get('order_id')}")
else:
    print("❌ Authentication failed")
```

## Troubleshooting

### Authentication Failed

**Symptom:** `authenticate()` returns False

**Solutions:**
1. Check credentials are stored:
   ```python
   from database.auth_db import get_kalshi_credentials
   creds = get_kalshi_credentials("your_email@example.com")
   print(creds)
   ```

2. Check environment is correct ('demo' vs 'production')

3. Check Kalshi account is active

### 401 Unauthorized Errors

**Symptom:** Frequent 401 errors

**Cause:** Token expiration (typical: 1 hour)

**Solution:** Token refresh is automatic. If issues persist:
   ```python
   # Force fresh token
   from database.auth_db import authenticate_kalshi
   token = authenticate_kalshi(email="user@example.com", bypass_cache=True)
   ```

### Connection Errors

**Symptom:** `Connection refused` or timeout

**Solutions:**
1. Check network connectivity
2. Check API endpoint URL (demo vs production)
3. Check firewall rules

## Migration

If upgrading from legacy mode (KALSHI_API_KEY/KALSHI_API_SECRET environment variables):

1. Store credentials in OpenAlgo:
   ```python
   from database.auth_db import upsert_kalshi_credentials

   upsert_kalshi_credentials(
       email=os.getenv('KALSHI_API_KEY'),
       password=os.getenv('KALSHI_API_SECRET'),
       environment=os.getenv('KALSHI_ENVIRONMENT', 'demo')
   )
   ```

2. Update code to use OpenAlgo:
   ```python
   # Old
   client = KalshiClient(use_openalgo=False)

   # New
   client = KalshiClient(email="user@example.com", use_openalgo=True)
   ```

## References

- [OpenAlgo Dashboard Integration Recommendations](/root/.openclaw/workspace/shared/documents/openalgo-integration-recommendations.md)
- [Kalshi Integration Research](/root/.openclaw/workspace/shared/documents/kalshi-integration-research.md)
- [OpenAlgo Auth DB](/root/.openclaw/workspace/openalgo/database/auth_db.py)
- [Kalshi API Docs](https://docs.kalshi.com/)
