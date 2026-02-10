# Super Bowl Paper Trading Dashboard

Simple Streamlit dashboard for monitoring Super Bowl paper trading.

## Features

### Pages

1. **Portfolio Overview (Home)**
   - Paper P&L metric
   - Win rate percentage
   - Total trades count
   - Analyzer mode status
   - Dashboard API connection status
   - Bot status (ACTIVE/IDLE)
   - API keys loaded count

2. **Paper Trades**
   - Table of recent paper trades
   - Columns: trade_id, prop_id, action, amount, status, created_at
   - Filter by status (PENDING, EXECUTED, FAILED)
   - Sort by timestamp
   - Trade statistics

3. **Signals**
   - List of active betting signals
   - Columns: prop_id, market_type, action, confidence, edge, market_price, suggested_price, reasoning, timestamp
   - Filter by action (BET/PASS)
   - Sort by edge or confidence
   - Signal statistics

4. **Bot Controls**
   - Start/Stop bot buttons
   - API Analyzer Mode toggle
   - Bot status display
   - System logs viewer

### Key Features

- **Real-time updates** (auto-refresh every 30 seconds)
- **Mobile-friendly** responsive design
- **Clean, simple UI** (inspired by openalgo)
- **Dashboard API client** (authentication, key fetch)
- **API Analyzer Mode** integration for paper trading
- **PostgreSQL database** integration

## Requirements

- Python 3.10+
- PostgreSQL database
- Openalgo Dashboard API (optional, for key management)

## Installation

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Set environment variables:**

Create a `.env` file in the dashboard directory:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=betting_db
DB_USER=postgres
DB_PASSWORD=postgres

# Dashboard API (optional, for key management)
DASHBOARD_API_URL=http://localhost:5000
DASHBOARD_USERNAME=your_username
DASHBOARD_PASSWORD=your_password

# Encryption
TOKEN_ENCRYPTION_KEY=your_32_byte_key_here
```

3. **Run the dashboard:**

```bash
streamlit run app.py --server.port 8888
```

Access the dashboard at: **http://localhost:8888**

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `betting_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DASHBOARD_API_URL` | Dashboard API base URL | `http://localhost:5000` |
| `DASHBOARD_USERNAME` | Dashboard username | - |
| `DASHBOARD_PASSWORD` | Dashboard password | - |
| `TOKEN_ENCRYPTION_KEY` | Token encryption key | - |

### Docker Deployment

The dashboard can be run in Docker using the existing `docker-compose.yml`:

```bash
docker-compose up -d
```

Then access at: **http://localhost:8888**

## API Analyzer Mode

The dashboard integrates with Openalgo's **API Analyzer Mode** for paper trading:

- **No real money risk** - All trades are simulated
- **Full P&L tracking** - See how your strategy performs
- **Complete order history** - All paper trades logged
- **Real-time updates** - Auto-refresh every 30 seconds

### Enabling API Analyzer Mode

1. Use the **Bot Controls** page
2. Click **Toggle Analyzer Mode**
3. Verify "Analyzer Mode: ENABLED" status

All subsequent trades will be paper trades (simulated).

## Database Schema

The dashboard uses the following database tables:

### paper_trades
- `trade_id` (UUID, primary key)
- `prop_id` (VARCHAR)
- `action` (VARCHAR) - BUY/SELL
- `amount` (DECIMAL)
- `status` (VARCHAR) - PENDING/EXECUTED/FAILED
- `pnl` (DECIMAL) - Profit/loss
- `analyzer_mode` (BOOLEAN)
- `created_at` (TIMESTAMP)

### api_keys
- `service` (VARCHAR)
- `key_hash` (VARCHAR)
- `expires_at` (TIMESTAMP)
- `permissions` (JSON)
- `dashboard_managed` (BOOLEAN)

### security_events
- `id` (SERIAL, primary key)
- `severity` (VARCHAR) - INFO/WARNING/ERROR
- `event_type` (VARCHAR)
- `user_id` (INTEGER)
- `details` (JSON)
- `ip_address` (VARCHAR)
- `created_at` (TIMESTAMP)

## Security

The dashboard uses production-grade security:

- **Argon2-CFFI** password hashing (PHC winner)
- **Fernet** token encryption
- **SQLAlchemy** ORM (SQL injection prevention)
- **Row-level security** (account_id on all tables)
- **Rate limiting** (per user/IP)
- **Comprehensive audit trail**

## Troubleshooting

### Database Connection Failed

Check your database credentials in `.env`:

```bash
# Verify PostgreSQL is running
docker-compose ps db

# Check database logs
docker-compose logs db
```

### Dashboard API Not Connected

Verify Dashboard API is accessible:

```bash
# Check if Dashboard API is running
curl http://localhost:5000/api/health

# Verify credentials in .env
cat .env | grep DASHBOARD
```

### No Paper Trades Showing

1. Check if bot is running (Bot Controls page)
2. Verify API Analyzer Mode is enabled
3. Check system logs for errors

## Development

### Project Structure

```
dashboard/
├── app.py              # Main Streamlit application
├── dashboard_api.py    # Dashboard API client
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Running in Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run app.py --server.port 8888 --server.runOnSave true
```

## Support

For issues or questions:
- Check system logs in the **Bot Controls** page
- Review database connection status
- Verify Dashboard API connectivity
- Check environment variables

## License

MIT License - See parent project license file.

---

**Super Bowl Paper Trading Dashboard** v1.0.0  
Built for OpenClaw Super Bowl Betting System  
February 6, 2026
