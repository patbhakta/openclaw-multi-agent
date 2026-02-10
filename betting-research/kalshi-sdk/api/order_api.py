# broker/kalshi/api/order_api.py

import os
from kalshi_python_sync import ApiClient, Configuration
from kalshi_python_sync.api import market_api, order_api
from utils.logging import get_logger

logger = get_logger(__name__)

def get_client(auth_token, environment="demo"):
    """Helper to initialize Kalshi client with token."""
    host = "https://demo-api.kalshi.co/trade-api/v2" if environment == "demo" else "https://api.kalshi.com/trade-api/v2"
    configuration = Configuration(host=host)
    configuration.api_key['KSA-SESSION-KEY'] = auth_token
    return ApiClient(configuration)

def place_order_api(order_data, auth_token):
    """
    Place an order on Kalshi.
    
    Args:
        order_data: Dictionary containing order details
        auth_token: Kalshi session token
        
    Returns:
        tuple: (Response semantic object, response_data, order_id)
    """
    client = get_client(auth_token, order_data.get("environment", "demo"))
    trading_api = order_api.OrderApi(client)
    
    # Map OpenAlgo order to Kalshi order
    # Kalshi uses 'ticker' instead of 'symbol'
    # 'action' is 'buy' or 'sell'
    # 'type' is 'limit' or 'market'
    
    kalshi_order = {
        "ticker": order_data["symbol"],
        "action": order_data["action"].lower(),
        "type": order_data.get("pricetype", "limit").lower(),
        "count": int(order_data["quantity"]),
        "client_order_id": order_data.get("strategy", "openalgo") + "_" + os.urandom(4).hex()
    }
    
    if kalshi_order["type"] == "limit":
        kalshi_order["price"] = int(float(order_data.get("price", 0)) * 100) # Kalshi uses cents
        
    try:
        response = trading_api.create_order(kalshi_order)
        
        class ResponseStub:
            def __init__(self, status):
                self.status = status
        
        # OpenAlgo expects a response object with .status and then data and order_id
        return ResponseStub(200), response.to_dict(), response.order_id
        
    except Exception as e:
        logger.error(f"Kalshi order placement error: {e}")
        class ResponseStub:
            def __init__(self, status):
                self.status = status
        return ResponseStub(400), {"message": str(e)}, None

def cancel_order_api(order_id, auth_token, environment="demo"):
    """Cancel an order on Kalshi."""
    client = get_client(auth_token, environment)
    trading_api = order_api.OrderApi(client)
    
    try:
        response = trading_api.cancel_order(order_id)
        class ResponseStub:
            def __init__(self, status):
                self.status = status
        return ResponseStub(200), response.to_dict()
    except Exception as e:
        logger.error(f"Kalshi order cancellation error: {e}")
        class ResponseStub:
            def __init__(self, status):
                self.status = status
        return ResponseStub(400), {"message": str(e)}
