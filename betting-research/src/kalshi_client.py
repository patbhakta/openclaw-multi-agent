"""
Kalshi API Client
"""

import os
from typing import Dict, List, Any, Optional
import requests


class KalshiClient:
    """Client for interacting with Kalshi API"""

    def __init__(self, api_key: str = None, api_secret: str = None, environment: str = 'demo'):
        """
        Initialize Kalshi client

        Args:
            api_key: Kalshi API key
            api_secret: Kalshi API secret
            environment: 'demo' or 'production'
        """
        self.api_key = api_key or os.getenv('KALSHI_API_KEY')
        self.api_secret = api_secret or os.getenv('KALSHI_API_SECRET')
        self.environment = environment

        # API endpoints
        if environment == 'production':
            self.base_url = 'https://trading-api.kalshi.com/v1'
        else:
            self.base_url = 'https://demo-api.kalshi.co/v1'

        self.session = requests.Session()
        self.token = None

    def authenticate(self) -> bool:
        """
        Authenticate with Kalshi API

        Returns:
            Success status
        """
        if not self.api_key or not self.api_secret:
            print("API key or secret not provided")
            return False

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

            print(f"Authentication failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def get_markets(self, status: str = 'open', limit: int = 100) -> List[Dict]:
        """
        Get list of markets

        Args:
            status: Market status filter
            limit: Maximum number of markets to return

        Returns:
            List of market data
        """
        if not self.token:
            if not self.authenticate():
                return []

        try:
            response = self.session.get(
                f"{self.base_url}/markets",
                params={
                    'status': status,
                    'limit': limit
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('markets', [])

            print(f"Failed to get markets: {response.status_code} - {response.text}")
            return []
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []

    def get_market(self, market_id: str) -> Optional[Dict]:
        """
        Get details for a specific market

        Args:
            market_id: Market ticker or ID

        Returns:
            Market data dictionary or None
        """
        if not self.token:
            if not self.authenticate():
                return None

        try:
            response = self.session.get(f"{self.base_url}/markets/{market_id}")

            if response.status_code == 200:
                return response.json()

            print(f"Failed to get market {market_id}: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"Error fetching market {market_id}: {e}")
            return None

    def get_orderbook(self, market_id: str) -> Optional[Dict]:
        """
        Get orderbook for a market

        Args:
            market_id: Market ticker or ID

        Returns:
            Orderbook data or None
        """
        if not self.token:
            if not self.authenticate():
                return None

        try:
            response = self.session.get(f"{self.base_url}/markets/{market_id}/orderbook")

            if response.status_code == 200:
                return response.json()

            print(f"Failed to get orderbook for {market_id}: {response.status_code}")
            return None
        except Exception as e:
            print(f"Error fetching orderbook: {e}")
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
        if not self.token:
            if not self.authenticate():
                return None

        try:
            response = self.session.post(
                f"{self.base_url}/orders",
                json={
                    'market_id': market_id,
                    'side': side,
                    'quantity': quantity,
                    'price': price,
                    'order_type': order_type
                }
            )

            if response.status_code in [200, 201]:
                return response.json()

            print(f"Failed to place order: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            print(f"Error placing order: {e}")
            return None

    def get_positions(self) -> List[Dict]:
        """
        Get current positions

        Returns:
            List of positions
        """
        if not self.token:
            if not self.authenticate():
                return []

        try:
            response = self.session.get(f"{self.base_url}/portfolio/positions")

            if response.status_code == 200:
                data = response.json()
                return data.get('positions', [])

            print(f"Failed to get positions: {response.status_code}")
            return []
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []
