# broker/kalshi/api/auth_api.py

import os
from kalshi_python_sync import ApiClient, Configuration
from kalshi_python_sync.api import auth_api
from utils.logging import get_logger

logger = get_logger(__name__)

def authenticate_broker(credentials):
    """
    Authenticate with Kalshi API.
    
    Args:
        credentials: Dictionary containing Kalshi credentials
            - email: User's Kalshi email
            - password: User's Kalshi password
            - environment: 'demo' or 'production' (optional, defaults to demo)
    
    Returns:
        tuple: (auth_token, broker_name)
    """
    email = credentials.get("email")
    password = credentials.get("password")
    environment = credentials.get("environment", "demo").lower()
    
    if not email or not password:
        logger.error("Kalshi authentication failed: Missing email or password")
        return None, "kalshi"

    host = "https://demo-api.kalshi.co/trade-api/v2" if environment == "demo" else "https://api.kalshi.com/trade-api/v2"
    
    configuration = Configuration(host=host)
    api_client = ApiClient(configuration)
    auth_inst = auth_api.AuthApi(api_client)
    
    try:
        # Login to get session token
        login_request = {
            "email": email,
            "password": password
        }
        login_response = auth_inst.login(login_request)
        
        # Kalshi SDK might return the token in different ways depending on version
        # Usually it's in the response object or session header
        # For simplicity in this integration, we'll return the configuration/client object or a token string
        # OpenAlgo usually expects a string token if the broker module handles the rest
        
        token = login_response.token
        logger.info(f"Kalshi authenticated successfully in {environment} mode")
        return token, "kalshi"
        
    except Exception as e:
        logger.error(f"Kalshi authentication error: {e}")
        return None, "kalshi"
