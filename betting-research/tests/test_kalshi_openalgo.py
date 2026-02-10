"""
Unit tests for Kalshi Client with OpenAlgo Integration
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock, call

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from kalshi_client import KalshiClient


class TestKalshiClientOpenAlgo:
    """Test KalshiClient with OpenAlgo integration"""

    def test_init_openalgo_mode(self):
        """Test initialization with OpenAlgo mode"""
        client = KalshiClient(email="test@example.com", use_openalgo=True)

        assert client.email == "test@example.com"
        assert client.use_openalgo is True
        assert client.token is None
        assert client.environment == 'demo'

    def test_init_legacy_mode(self):
        """Test initialization in legacy mode"""
        with patch.dict(os.environ, {
            'KALSHI_API_KEY': 'test-key',
            'KALSHI_API_SECRET': 'test-secret',
            'KALSHI_ENVIRONMENT': 'production'
        }):
            client = KalshiClient(use_openalgo=False)

            assert client.email is None
            assert client.use_openalgo is False
            assert client.api_key == 'test-key'
            assert client.api_secret == 'test-secret'
            assert client.environment == 'production'

    def test_set_base_url_demo(self):
        """Test base URL for demo environment"""
        client = KalshiClient(email="test@example.com")
        client.environment = 'demo'
        client._set_base_url()

        assert client.base_url == 'https://demo-api.kalshi.co/trade-api/v2'

    def test_set_base_url_production(self):
        """Test base URL for production environment"""
        client = KalshiClient(email="test@example.com")
        client.environment = 'production'
        client._set_base_url()

        assert client.base_url == 'https://api.kalshi.com/trade-api/v2'

    @patch('kalshi_client.KalshiClient._authenticate_openalgo')
    def test_authenticate_openalgo(self, mock_auth_openalgo):
        """Test authenticate using OpenAlgo mode"""
        mock_auth_openalgo.return_value = True

        client = KalshiClient(email="test@example.com", use_openalgo=True)
        result = client.authenticate()

        assert result is True
        mock_auth_openalgo.assert_called_once()

    @patch('kalshi_client.KalshiClient._authenticate_legacy')
    def test_authenticate_legacy(self, mock_auth_legacy):
        """Test authenticate using legacy mode"""
        mock_auth_legacy.return_value = True

        client = KalshiClient(use_openalgo=False)
        result = client.authenticate()

        assert result is True
        mock_auth_legacy.assert_called_once()

    def test_authenticate_openalgo_success(self):
        """Test successful OpenAlgo authentication"""
        # Create mock database module (package with __path__ and __spec__)
        mock_database = MagicMock()
        mock_database.__path__ = []
        mock_database.__spec__ = MagicMock()  # Make it look like a proper package

        # Create mock auth_db module
        mock_auth_db = MagicMock()
        mock_auth_db.__spec__ = MagicMock()
        mock_auth_db.get_kalshi_credentials.return_value = {
            'email': 'test@example.com',
            'password': 'test-password',
            'environment': 'demo'
        }
        mock_auth_db.authenticate_kalshi.return_value = 'test-token'

        # Add auth_db to both sys.modules and as a submodule
        with patch.dict(sys.modules, {'database': mock_database, 'database.auth_db': mock_auth_db}):
            client = KalshiClient(email="test@example.com", use_openalgo=True)
            result = client._authenticate_openalgo()

            assert result is True
            assert client.token == 'test-token'
            assert client.environment == 'demo'
            mock_auth_db.get_kalshi_credentials.assert_called_once_with('test@example.com')
            mock_auth_db.authenticate_kalshi.assert_called_once_with('test@example.com')

    def test_authenticate_openalgo_no_credentials(self):
        """Test OpenAlgo authentication with no credentials"""
        # Create mock database module (package with __path__ and __spec__)
        mock_database = MagicMock()
        mock_database.__path__ = []
        mock_database.__spec__ = MagicMock()

        # Create mock auth_db module
        mock_auth_db = MagicMock()
        mock_auth_db.__spec__ = MagicMock()
        mock_auth_db.get_kalshi_credentials.return_value = None

        # Add both modules to sys.modules
        with patch.dict(sys.modules, {'database': mock_database, 'database.auth_db': mock_auth_db}):
            client = KalshiClient(email="test@example.com", use_openalgo=True)
            result = client._authenticate_openalgo()

            assert result is False
            assert client.token is None

    @patch('requests.Session.post')
    def test_authenticate_legacy_success(self, mock_post):
        """Test successful legacy authentication"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'token': 'test-token'}
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'KALSHI_API_KEY': 'test@example.com',
            'KALSHI_API_SECRET': 'test-password',
            'KALSHI_ENVIRONMENT': 'demo'
        }):
            client = KalshiClient(use_openalgo=False)
            result = client._authenticate_legacy()

            assert result is True
            assert client.token == 'test-token'

    @patch('requests.Session.post')
    def test_authenticate_legacy_failure(self, mock_post):
        """Test failed legacy authentication"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = 'Invalid credentials'
        mock_post.return_value = mock_response

        with patch.dict(os.environ, {
            'KALSHI_API_KEY': 'test@example.com',
            'KALSHI_API_SECRET': 'wrong-password',
            'KALSHI_ENVIRONMENT': 'demo'
        }):
            client = KalshiClient(use_openalgo=False)
            result = client._authenticate_legacy()

            assert result is False

    @patch('kalshi_client.KalshiClient._make_request')
    def test_get_markets(self, mock_make_request):
        """Test getting markets"""
        mock_make_request.return_value = {
            'markets': [
                {'ticker': 'M1', 'title': 'Market 1'},
                {'ticker': 'M2', 'title': 'Market 2'}
            ]
        }

        client = KalshiClient(email="test@example.com")
        client.token = 'test-token'
        result = client.get_markets(status='open', limit=10)

        assert len(result) == 2
        assert result[0]['ticker'] == 'M1'
        mock_make_request.assert_called_once_with(
            'GET',
            '/markets',
            params={'status': 'open', 'limit': 10}
        )

    @patch('kalshi_client.KalshiClient._make_request')
    def test_get_market(self, mock_make_request):
        """Test getting a specific market"""
        mock_make_request.return_value = {
            'ticker': 'M1',
            'title': 'Market 1'
        }

        client = KalshiClient(email="test@example.com")
        client.token = 'test-token'
        result = client.get_market('M1')

        assert result['ticker'] == 'M1'
        mock_make_request.assert_called_once_with('GET', '/markets/M1')

    @patch('kalshi_client.KalshiClient._make_request')
    def test_place_order(self, mock_make_request):
        """Test placing an order"""
        mock_make_request.return_value = {
            'order_id': 'O1',
            'status': 'pending'
        }

        client = KalshiClient(email="test@example.com")
        client.token = 'test-token'
        result = client.place_order('M1', side='yes', quantity=10, price=50)

        assert result['order_id'] == 'O1'
        mock_make_request.assert_called_once_with(
            'POST',
            '/orders',
            data={
                'market_id': 'M1',
                'side': 'yes',
                'quantity': 10,
                'price': 50,
                'order_type': 'limit'
            }
        )

    @patch('kalshi_client.KalshiClient._make_request')
    def test_get_positions(self, mock_make_request):
        """Test getting positions"""
        mock_make_request.return_value = {
            'positions': [
                {'ticker': 'M1', 'quantity': 10, 'side': 'yes'}
            ]
        }

        client = KalshiClient(email="test@example.com")
        client.token = 'test-token'
        result = client.get_positions()

        assert len(result) == 1
        assert result[0]['ticker'] == 'M1'
        mock_make_request.assert_called_once_with('GET', '/portfolio/positions')


class TestKalshiClientTokenRefresh:
    """Test automatic token refresh on 401 errors"""

    def test_make_request_token_refresh_openalgo(self):
        """Test automatic token refresh with OpenAlgo"""
        # First call returns 401
        mock_response_401 = Mock()
        mock_response_401.status_code = 401

        # Second call succeeds
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'success': True}

        # Create mock database module (package with __path__ and __spec__)
        mock_database = MagicMock()
        mock_database.__path__ = []
        mock_database.__spec__ = MagicMock()

        # Create mock auth_db module
        mock_auth_db = MagicMock()
        mock_auth_db.__spec__ = MagicMock()
        mock_auth_db.authenticate_kalshi.return_value = 'new-token'

        # Add modules to sys.modules
        with patch.dict(sys.modules, {
            'database': mock_database,
            'database.auth_db': mock_auth_db
        }):
            # Patch requests.Session to use our mock session
            with patch('kalshi_client.requests.Session') as MockSession:
                mock_session = Mock()
                mock_session.get.return_value = mock_response_401
                mock_session.get.side_effect = [mock_response_401, mock_response_200]
                MockSession.return_value = mock_session

                client = KalshiClient(email="test@example.com", use_openalgo=True)
                client.token = 'old-token'
                result = client._make_request('GET', '/test', retry_on_401=True)

                # Should have authenticated (refreshed token)
                assert client.token == 'new-token'
                mock_auth_db.authenticate_kalshi.assert_called_once_with('test@example.com', bypass_cache=True)

    @patch('kalshi_client.KalshiClient._authenticate_legacy')
    def test_make_request_token_refresh_legacy(self, mock_auth_legacy):
        """Test automatic token refresh in legacy mode"""
        # First call returns 401
        mock_response_401 = Mock()
        mock_response_401.status_code = 401

        # Second call succeeds
        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {'success': True}

        mock_session = Mock()
        mock_session.request.side_effect = [mock_response_401, mock_response_200]
        mock_session.headers = {}

        mock_auth_legacy.return_value = True

        with patch.dict(os.environ, {
            'KALSHI_API_KEY': 'test@example.com',
            'KALSHI_API_SECRET': 'test-password'
        }):
            client = KalshiClient(use_openalgo=False)
            client._authenticate_legacy()  # Set initial token
            result = client._make_request('GET', '/test', retry_on_401=True)

            # Should have re-authenticated
            mock_auth_legacy.assert_called()

    def test_make_request_no_retry_on_401(self):
        """Test that 401 doesn't retry when retry_on_401 is False"""
        mock_response_401 = Mock()
        mock_response_401.status_code = 401

        mock_session = Mock()
        mock_session.request.return_value = mock_response_401

        with patch.dict(sys.modules, {
            'requests': MagicMock(Session=Mock(return_value=mock_session))
        }):
            client = KalshiClient(email="test@example.com", use_openalgo=True)
            client.token = 'test-token'
            result = client._make_request('GET', '/test', retry_on_401=False)

            # Should return None without retrying
            assert result is None

    def test_make_request_not_authenticated(self):
        """Test making request when not authenticated"""
        mock_session = Mock()
        mock_session.headers = {}

        with patch.dict(sys.modules, {
            'database': MagicMock(),
            'requests': MagicMock(Session=Mock(return_value=mock_session))
        }):
            with patch('kalshi_client.KalshiClient.authenticate', return_value=False):
                client = KalshiClient(email="test@example.com", use_openalgo=True)
                result = client._make_request('GET', '/test')

                # Should return None without authenticating
                assert result is None
