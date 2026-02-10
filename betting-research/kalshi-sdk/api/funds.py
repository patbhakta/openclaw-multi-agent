# broker/kalshi/api/funds.py

from kalshi_python_sync import ApiClient, Configuration
from kalshi_python_sync.api import portfolio_api
from utils.logging import get_logger

logger = get_logger(__name__)

def get_client(auth_token, environment="demo"):
    """Helper to initialize Kalshi client with token."""
    host = "https://demo-api.kalshi.co/trade-api/v2" if environment == "demo" else "https://api.kalshi.com/trade-api/v2"
    configuration = Configuration(host=host)
    configuration.api_key['KSA-SESSION-KEY'] = auth_token
    return ApiClient(configuration)

def get_funds_api(auth_token, environment="demo"):
    """
    Get available funds from Kalshi.
    
    Args:
        auth_token: Kalshi session token
        environment: 'demo' or 'production'
        
    Returns:
        dict: Fund details
    """
    client = get_client(auth_token, environment)
    port_api = portfolio_api.PortfolioApi(client)
    
    try:
        response = port_api.get_balance()
        return {
            "status": "success",
            "balance": float(response.balance) / 100.0, # Convert cents to dollars
            "available_balance": float(response.balance) / 100.0
        }
    except Exception as e:
        logger.error(f"Kalshi funds retrieval error: {e}")
        return {"status": "error", "message": str(e)}
