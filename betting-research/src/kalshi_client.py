"""
Kalshi API Client with OpenAlgo Dashboard Key Management Integration

This client uses OpenAlgo's secure credential storage system (hash + encrypted storage)
for Kalshi API authentication. Credentials are stored encrypted with Fernet and
hashed with Argon2-CFFI for production-grade security.
"""

import os
from typing import Dict, List, Any, Optional
import requests


class KalshiClient:
    """Client for interacting with Kalshi API with OpenAlgo integration"""

    def __init__(self, email: str = None, use_openalgo: bool = True):
        """
        Initialize Kalshi client

        Args:
            email: Kalshi account email (required for OpenAlgo mode)
            use_openalgo: Use OpenAlgo's credential storage (default: True)
                           Set to False to use legacy KALSHI_API_KEY/SECRET env vars
        """
        self.email = email
        self.use_openalgo = use_openalgo
        self.environment = 'demo'  # Will be set during authentication
        self.base_url = 'https://demo-api.kalshi.co/trade-api/v2'  # Default to demo
        self.session = requests.Session()
        self.token = None

        # Legacy mode: use environment variables (for backward compatibility)
        if not use_openalgo:
            self.api_key = os.getenv('KALSHI_API_KEY')
            self.api_secret = os.getenv('KALSHI_API_SECRET')
            self.environment = os.getenv('KALSHI_ENVIRONMENT', 'demo')

            # Set correct API base URL based on environment
            self._set_base_url()

    def _set_base_url(self):
        """Set API base URL based on environment"""
        if self.environment == 'production':
            self.base_url = 'https://api.kalshi.com/trade-api/v2'
        else:
            self.base_url = 'https://demo-api.kalshi.co/trade-api/v2'

    def authenticate(self) -> bool:
        """
        Authenticate with Kalshi API

        Returns:
            Success status
        """
        if self.use_openalgo:
            return self._authenticate_openalgo()
        else:
            return self._authenticate_legacy()

    def _authenticate_openalgo(self) -> bool:
        """
        Authenticate using OpenAlgo's credential storage system.

        Returns:
            Success status
        """
        if not self.email:
            print("Email is required for OpenAlgo mode")
            return False

        try:
            # Import OpenAlgo auth functions
            import sys
            import os
            openalgo_path = os.environ.get('OPENALGO_PATH', '/app/openalgo')
            if openalgo_path not in sys.path:
                sys.path.insert(0, openalgo_path)
            from database.auth_db import authenticate_kalshi, get_kalshi_credentials

            # Get credentials (including environment)
            creds = get_kalshi_credentials(self.email)

            if not creds:
                print(f"Failed to get Kalshi credentials for {self.email}")
                return False

            self.environment = creds.get('environment', 'demo')
            self._set_base_url()

            # Authenticate with Kalshi API using OpenAlgo's cached token
            token = authenticate_kalshi(self.email)

            if token:
                self.token = token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}'
                })
                print(f"✅ Authenticated with Kalshi ({self.environment}) using OpenAlgo")
                return True
            else:
                print(f"❌ Authentication failed for {self.email}")
                return False

        except Exception as e:
            print(f"❌ OpenAlgo authentication error: {e}")
            return False

    def _authenticate_legacy(self) -> bool:
        """
        Authenticate using legacy environment variables (for backward compatibility).

        Returns:
            Success status
        """
        if not self.api_key or not self.api_secret:
            print("API key or secret not provided (set KALSHI_API_KEY and KALSHI_API_SECRET)")
            return False

        self._set_base_url()

        try:
            response = self.session.post(
                f"{self.base_url}/login",
                json={
                    'email': self.api_key,
                    'password': self.api_secret
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                if self.token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })
                    return True

            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False

    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, retry_on_401: bool = True) -> Optional[Dict]:
        """
        Make API request with automatic token refresh on 401 errors.

        Args:
            method: HTTP method ('GET', 'POST', etc.)
            endpoint: API endpoint
            data: Request body data
            params: URL parameters
            retry_on_401: Retry request on 401 errors (default: True)

        Returns:
            Response data or None
        """
        # Ensure authenticated
        if not self.token and not self.authenticate():
            return None

        url = f"{self.base_url}{endpoint}"

        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            else:
                print(f"Unsupported HTTP method: {method}")
                return None

            # Handle 401 Unauthorized - token expired
            if response.status_code == 401 and retry_on_401:
                print("⚠️ Token expired, refreshing...")

                # Refresh token (bypass cache for fresh token)
                if self.use_openalgo:
                    import sys
                    import os
                    openalgo_path = os.environ.get('OPENALGO_PATH', '/app/openalgo')
                    if openalgo_path not in sys.path:
                        sys.path.insert(0, openalgo_path)
                    from database.auth_db import authenticate_kalshi
                    new_token = authenticate_kalshi(self.email, bypass_cache=True)
                else:
                    # Legacy mode: re-authenticate
                    self.token = None
                    if not self._authenticate_legacy():
                        return None
                    new_token = self.token

                if new_token:
                    self.token = new_token
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.token}'
                    })

                    # Retry request with new token
                    print("🔄 Retrying request with fresh token...")
                    return self._make_request(method, endpoint, data, params, retry_on_401=False)
                else:
                    print("❌ Token refresh failed")
                    return None

            # Check response status
            if response.status_code in [200, 201]:
                return response.json()
            else:
                print(f"❌ API request failed: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"❌ API request error: {e}")
            return None

    def get_markets(self, status: str = 'open', limit: int = 100) -> List[Dict]:
        """
        Get list of markets

        Args:
            status: Market status filter
            limit: Maximum number of markets to return

        Returns:
            List of market data
        """
        response = self._make_request(
            'GET',
            '/markets',
            params={'status': status, 'limit': limit}
        )

        if response:
            return response.get('markets', [])
        return []

    def get_market(self, market_id: str) -> Optional[Dict]:
        """
        Get details for a specific market

        Args:
            market_id: Market ticker or ID

        Returns:
            Market data dictionary or None
        """
        response = self._make_request('GET', f'/markets/{market_id}')

        if response:
            return response
        return None

    def get_orderbook(self, market_id: str) -> Optional[Dict]:
        """
        Get orderbook for a market

        Args:
            market_id: Market ticker or ID

        Returns:
            Orderbook data or None
        """
        response = self._make_request('GET', f'/markets/{market_id}/orderbook')

        if response:
            return response
        return None

    def place_order(self, market_id: str, side: str, quantity: int,
                    price: int, order_type: str = 'limit') -> Optional[Dict]:
        """
        Place an order

        Args:
            market_id: Market ticker or ID
            side: 'yes' or 'no'
            quantity: Number of contracts
            price: Price in cents (1-99)
            order_type: 'limit' or 'market'

        Returns:
            Order response or None
        """
        data = {
            'market_id': market_id,
            'side': side,
            'quantity': quantity,
            'price': price,
            'order_type': order_type
        }

        response = self._make_request('POST', '/orders', data=data)

        if response:
            return response
        return None

    def get_positions(self) -> List[Dict]:
        """
        Get current positions

        Returns:
            List of positions
        """
        response = self._make_request('GET', '/portfolio/positions')

        if response:
            return response.get('positions', [])
        return []
