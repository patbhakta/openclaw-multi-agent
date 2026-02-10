"""
Dashboard API Client for Openalgo Integration

Handles authentication, key fetching, and API calls to the Openalgo Dashboard API.
Based on openalgo's Dashboard API pattern.

Features:
- JWT authentication
- API key fetch (hash-only storage)
- API Analyzer Mode integration
- Error handling and retry logic
"""

import os
import json
import time
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class APIKeyInfo:
    """API key information"""
    service: str
    key_hash: str
    expires_at: Optional[datetime]
    permissions: List[str]
    dashboard_managed: bool


class DashboardAPIClient:
    """
    Client for interacting with Openalgo Dashboard API.

    Handles authentication, key management, and API proxy calls.
    """

    def __init__(
        self,
        dashboard_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Dashboard API client.

        Args:
            dashboard_url: Dashboard API base URL
            username: Dashboard username (or None to use env vars)
            password: Dashboard password (or None to use env vars)
        """
        self.dashboard_url = dashboard_url or os.getenv('DASHBOARD_API_URL', 'http://localhost:5000')
        self.username = username or os.getenv('DASHBOARD_USERNAME')
        self.password = password or os.getenv('DASHBOARD_PASSWORD')
        self.jwt_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        self.session = requests.Session()

    def login(self) -> bool:
        """
        Authenticate with Dashboard API and obtain JWT token.

        Returns:
            True if login successful, False otherwise
        """
        try:
            response = self.session.post(
                f"{self.dashboard_url}/api/auth/login",
                json={
                    'username': self.username,
                    'password': self.password
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.jwt_token = data.get('token')

                # Calculate token expiration (default 24 hours)
                expires_in = data.get('expires_in', 86400)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)

                print(f"✅ Logged into Dashboard API successfully")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def _ensure_authenticated(self) -> bool:
        """
        Ensure JWT token is valid and not expired.

        Returns:
            True if authenticated, False otherwise
        """
        if not self.jwt_token or not self.token_expires_at:
            return self.login()

        if datetime.now() >= self.token_expires_at:
            return self.login()

        return True

    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with JWT token.

        Returns:
            Headers dictionary with Authorization header
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'

        return headers

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make GET request to Dashboard API.

        Args:
            endpoint: API endpoint (e.g., '/api/accounts')
            params: Query parameters

        Returns:
            Response dictionary with 'success' and 'data'/'error' keys
        """
        if not self._ensure_authenticated():
            return {'success': False, 'error': 'Not authenticated'}

        try:
            response = self.session.get(
                f"{self.dashboard_url}{endpoint}",
                headers=self._get_headers(),
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            elif response.status_code == 401:
                # Token expired, try re-authentication
                if self.login():
                    return self.get(endpoint, params)
                else:
                    return {'success': False, 'error': 'Authentication failed'}
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make POST request to Dashboard API.

        Args:
            endpoint: API endpoint (e.g., '/api/accounts')
            data: Request body

        Returns:
            Response dictionary with 'success' and 'data'/'error' keys
        """
        if not self._ensure_authenticated():
            return {'success': False, 'error': 'Not authenticated'}

        try:
            response = self.session.post(
                f"{self.dashboard_url}{endpoint}",
                headers=self._get_headers(),
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            elif response.status_code == 401:
                # Token expired, try re-authentication
                if self.login():
                    return self.post(endpoint, data)
                else:
                    return {'success': False, 'error': 'Authentication failed'}
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def list_keys(self) -> List[APIKeyInfo]:
        """
        List all API keys managed by Dashboard.

        Returns:
            List of API key information objects
        """
        response = self.get('/api/keys')

        if not response['success']:
            print(f"❌ Failed to list keys: {response.get('error')}")
            return []

        keys = []
        for key_data in response['data'].get('keys', []):
            keys.append(APIKeyInfo(
                service=key_data.get('service'),
                key_hash=key_data.get('key_hash'),
                expires_at=datetime.fromisoformat(key_data['expires_at']) if key_data.get('expires_at') else None,
                permissions=key_data.get('permissions', []),
                dashboard_managed=key_data.get('dashboard_managed', True)
            ))

        return keys

    def fetch_key(self, service: str) -> Optional[str]:
        """
        Fetch decrypted API key for a service.

        This method retrieves the actual API key from Dashboard (not the hash).
        The key is decrypted server-side and returned securely.

        Args:
            service: Service name (e.g., 'kalshi')

        Returns:
            Decrypted API key or None if not found
        """
        response = self.get(f'/api/keys/{service}')

        if not response['success']:
            print(f"❌ Failed to fetch key for {service}: {response.get('error')}")
            return None

        return response['data'].get('key')

    def enable_analyzer_mode(self, reason: Optional[str] = None) -> bool:
        """
        Enable API Analyzer Mode for paper trading.

        In Analyzer Mode, all API calls are simulated (no real money).

        Args:
            reason: Reason for enabling analyzer mode

        Returns:
            True if successful, False otherwise
        """
        data = {'reason': reason or 'Paper trading mode'}

        response = self.post('/api/analyzer/enable', data)

        if response['success']:
            print("✅ API Analyzer Mode enabled")
            return True
        else:
            print(f"❌ Failed to enable Analyzer Mode: {response.get('error')}")
            return False

    def disable_analyzer_mode(self, reason: Optional[str] = None) -> bool:
        """
        Disable API Analyzer Mode.

        Args:
            reason: Reason for disabling analyzer mode

        Returns:
            True if successful, False otherwise
        """
        data = {'reason': reason or 'Exiting paper trading mode'}

        response = self.post('/api/analyzer/disable', data)

        if response['success']:
            print("✅ API Analyzer Mode disabled")
            return True
        else:
            print(f"❌ Failed to disable Analyzer Mode: {response.get('error')}")
            return False

    def get_analyzer_mode_status(self) -> bool:
        """
        Check if API Analyzer Mode is enabled.

        Returns:
            True if enabled, False otherwise
        """
        response = self.get('/api/analyzer/status')

        if response['success']:
            return response['data'].get('enabled', False)
        else:
            print(f"❌ Failed to get Analyzer Mode status: {response.get('error')}")
            return False

    def proxy_api_call(
        self,
        service: str,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict] = None,
        analyzer_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Proxy API call through Dashboard.

        The Dashboard authenticates with the broker service and forwards the request.
        This keeps the actual API keys secure on the Dashboard server.

        Args:
            service: Service name (e.g., 'kalshi')
            endpoint: API endpoint to call
            method: HTTP method (GET, POST, etc.)
            data: Request body
            analyzer_mode: Enable API Analyzer Mode for this call

        Returns:
            Response dictionary with 'success' and 'data'/'error' keys
        """
        request_data = {
            'service': service,
            'endpoint': endpoint,
            'method': method,
            'analyzer_mode': analyzer_mode
        }

        if data:
            request_data['data'] = data

        response = self.post('/api/proxy', request_data)

        if response['success']:
            return response['data']
        else:
            return {'success': False, 'error': response.get('error')}

    def get_analyzer_portfolio(self) -> Dict[str, Any]:
        """
        Get paper trading portfolio from API Analyzer Mode.

        Returns:
            Portfolio dictionary with 'total_pnl', 'win_rate', 'total_trades'
        """
        response = self.get('/api/analyzer/portfolio')

        if response['success']:
            return response['data']
        else:
            print(f"❌ Failed to get analyzer portfolio: {response.get('error')}")
            return {
                'total_pnl': 0.0,
                'win_rate': 0.0,
                'total_trades': 0
            }

    def get_analyzer_trades(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get paper trading history from API Analyzer Mode.

        Args:
            limit: Maximum number of trades to return

        Returns:
            List of trade dictionaries
        """
        response = self.get(f'/api/analyzer/trades?limit={limit}')

        if response['success']:
            return response['data'].get('trades', [])
        else:
            print(f"❌ Failed to get analyzer trades: {response.get('error')}")
            return []

    def submit_analyzer_trade(
        self,
        prop_id: str,
        action: str,
        amount: float,
        market_type: str = 'nfl_superbowl'
    ) -> Dict[str, Any]:
        """
        Submit paper trade through API Analyzer Mode.

        Args:
            prop_id: Property/market ID
            action: Action (BUY/SELL)
            amount: Trade amount
            market_type: Market type

        Returns:
            Response dictionary with 'success' and 'trade_id'/'error'
        """
        data = {
            'analyzer_mode': True,
            'prop_id': prop_id,
            'action': action,
            'amount': amount,
            'market_type': market_type
        }

        response = self.post('/api/analyzer/trade', data)

        if response['success']:
            print(f"✅ Paper trade submitted: {response['data'].get('trade_id')}")
            return response['data']
        else:
            print(f"❌ Failed to submit paper trade: {response.get('error')}")
            return {'success': False, 'error': response.get('error')}

    def health_check(self) -> bool:
        """
        Check if Dashboard API is accessible.

        Returns:
            True if accessible, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.dashboard_url}/api/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False


# Convenience functions for common operations

def get_dashboard_client() -> Optional[DashboardAPIClient]:
    """
    Get authenticated Dashboard API client.

    Returns:
        Authenticated client or None if configuration is missing
    """
    dashboard_url = os.getenv('DASHBOARD_API_URL')
    username = os.getenv('DASHBOARD_USERNAME')
    password = os.getenv('DASHBOARD_PASSWORD')

    if not all([dashboard_url, username, password]):
        print("⚠️  Dashboard API configuration missing")
        return None

    client = DashboardAPIClient(dashboard_url, username, password)

    if not client.login():
        print("❌ Failed to authenticate with Dashboard API")
        return None

    return client


def fetch_service_key(service: str) -> Optional[str]:
    """
    Fetch API key for a service from Dashboard.

    Args:
        service: Service name (e.g., 'kalshi')

    Returns:
        API key or None if not found
    """
    client = get_dashboard_client()

    if not client:
        return None

    return client.fetch_key(service)


def is_analyzer_mode_enabled() -> bool:
    """
    Check if API Analyzer Mode is enabled.

    Returns:
        True if enabled, False otherwise
    """
    client = get_dashboard_client()

    if not client:
        return False

    return client.get_analyzer_mode_status()
