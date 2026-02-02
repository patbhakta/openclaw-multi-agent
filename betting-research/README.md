# Betting Research - Prediction Market Infrastructure

Docker-based environment for betting prediction market research with Jupyter, PostgreSQL, and Kalshi API integration.

## Features

- **Jupyter Notebooks**: Research environment with scipy stack
- **PostgreSQL Database**: Market data storage with optimized schema
- **Kalshi API Integration**: Real-time market data collection
- **Docker Compose**: Easy one-command setup

## Quick Start

### 1. Install Docker and Docker Compose

Make sure Docker and Docker Compose are installed on your system.

### 2. Set Up Environment Variables

Copy the example environment file and add your Kalshi API credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your Kalshi API key and secret:
```env
POSTGRES_PASSWORD=your_secure_password
KALSHI_API_KEY=your_email
KALSHI_API_SECRET=your_password
KALSHI_ENVIRONMENT=demo
```

Get your Kalshi API credentials from https://kalshi.com/dashboard

### 3. Start the Services

```bash
docker-compose up -d
```

This starts:
- PostgreSQL database (port 5432)
- Jupyter notebook (port 8888)
- Kalshi bot service

### 4. Access Services

**Jupyter Notebooks**: Open http://localhost:8888 in your browser

**PostgreSQL**:
```bash
docker exec -it betting-db psql -U betting_user -d betting_markets
```

### 5. Collect Data

Run data collection:
```bash
docker-compose run --rm kalshi-bot python -m src.collect_data
```

## Project Structure

```
betting-research/
├── data/              # Raw market data
├── models/            # ML models
├── notebooks/         # Jupyter notebooks
├── src/               # Python source code
│   ├── db.py          # Database operations
│   ├── kalshi_client.py  # Kalshi API client
│   ├── collect_data.py   # Data collection script
│   └── main.py        # Entry point
├── tests/             # Unit tests
├── db/
│   └── init/          # Database initialization scripts
├── docker-compose.yml # Docker services
├── Dockerfile         # Kalshi bot container
└── requirements.txt    # Python dependencies
```

## Database Schema

### Tables

**markets**: Kalshi market data
- id, title, subtitle, category, status
- open_time, close_time, ticker
- min_price, max_price, volume
- metadata (JSONB)

**orders**: Trade history
- id, market_id, side, quantity, price
- order_type, status, timestamps
- kalshi_order_id, metadata

**positions**: Current holdings
- id, market_id, side, quantity, avg_price
- current_price, unrealized_pnl

**market_history**: Price movements over time
- id, market_id, yes_price, no_price, volume
- recorded_at timestamp

## API Usage

### Database Manager

```python
from src.db import DatabaseManager

db = DatabaseManager()

# Get markets
markets = db.get_markets(status='open')

# Insert market
db.insert_market({
    'id': 'market-123',
    'title': 'Test Market',
    'status': 'open',
    'ticker': 'TEST/YESNO',
    # ... other fields
})

# Record price history
db.record_market_history('market-123', yes_price=50, no_price=50, volume=100)
```

### Kalshi Client

```python
from src.kalshi_client import KalshiClient

client = KalshiClient()
client.authenticate()

# Get markets
markets = client.get_markets(status='open')

# Get market details
market = client.get_market('TEST/YESNO')

# Get orderbook
orderbook = client.get_orderbook('TEST/YESNO')

# Place order
order = client.place_order('TEST/YESNO', side='yes',
                           quantity=10, price=50)
```

## Running Tests

```bash
docker-compose run --rm kalshi-bot pytest tests/ -v
```

## Stopping Services

```bash
docker-compose down
```

To remove volumes (deletes data):
```bash
docker-compose down -v
```

## Development Notes

- The Kalshi API uses demo environment by default
- Change `KALSHI_ENVIRONMENT=production` for live trading
- Jupyter runs without password authentication (adjust in docker-compose.yml for production)
- Database schema is initialized automatically on first run

## Next Steps

1. Set up Kalshi API credentials
2. Run initial data collection
3. Create Jupyter notebooks for analysis
4. Develop ML models in `models/` directory
5. Implement trading strategies in `src/`

## Resources

- [Kalshi API Documentation](https://docs.kalshi.co/)
- [Jupyter Documentation](https://jupyter.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
