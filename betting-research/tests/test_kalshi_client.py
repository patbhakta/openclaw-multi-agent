"""
Unit tests for Kalshi Client
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from kalshi_client import KalshiClient


@pytest.fixture
def mock_session():
    """Mock requests session"""
    with patch('kalshi_client.requests.Session') as mock_session_class:
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        yield mock_session


class TestKalshiClient:
    """Test KalshiClient class"""

    def test_init_with_credentials(self):
        """Test initialization with API credentials"""
        client = KalshiClient(api_key="test-key", api_secret="test-secret")

        assert client.api_key == "test-key"
        assert client.api_secret == "test-secret"
        assert client.authenticated is True

    def test_init_from_env(self):
        """Test initialization from environment variables"""
        with patch.dict(os.environ, {
            'KALSHI_API_KEY': 'env-key',
            'KALSHI_API_SECRET': 'env-secret'
        }):
            client = KalshiClient()

            assert client.api_key == 'env-key'
            assert client.api_secret == 'env-secret'

    def test_init_without_credentials(self):
        """Test initialization without credentials"""
        with patch.dict(os.environ, {}, clear=True):
            client = KalshiClient()

            assert client.api_key is None
            assert client.api_secret is None
            assert client.authenticated is False

    @patch('kalshi_client.requests.Session')
    def test_make_request_authenticated(self, mock_session_class, mock_session):
        """Test making authenticated request"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'success': True}
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        client._make_request('GET', '/test')

        mock_session.request.assert_called_once()
        assert 'Authorization' in client.session.headers

    def test_make_request_not_authenticated(self):
        """Test making request when not authenticated"""
        client = KalshiClient()

        with pytest.raises(ValueError, match="not authenticated"):
            client._make_request('GET', '/test')

    @patch('kalshi_client.requests.Session')
    def test_get_markets(self, mock_session_class, mock_session):
        """Test getting markets"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'markets': [
                {'id': 'M1', 'title': 'Market 1'},
                {'id': 'M2', 'title': 'Market 2'}
            ]
        }
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.get_markets(status='open', limit=10)

        assert 'markets' in result
        assert len(result['markets']) == 2

    @patch('kalshi_client.requests.Session')
    def test_get_market(self, mock_session_class, mock_session):
        """Test getting a specific market"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'market': {'id': 'M1', 'title': 'Market 1'}
        }
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.get_market('M1')

        assert 'market' in result
        assert result['market']['id'] == 'M1'

    @patch('kalshi_client.requests.Session')
    def test_place_order(self, mock_session_class, mock_session):
        """Test placing an order"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'order': {'id': 'O1', 'status': 'pending'}
        }
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.place_order('M1', side='yes', quantity=10, price=50)

        assert 'order' in result

    def test_place_order_invalid_side(self):
        """Test placing order with invalid side"""
        client = KalshiClient(api_key="test-key")

        with pytest.raises(ValueError, match="Side must be"):
            client.place_order('M1', side='invalid', quantity=10, price=50)

    def test_place_order_invalid_price(self):
        """Test placing order with invalid price"""
        client = KalshiClient(api_key="test-key")

        with pytest.raises(ValueError, match="Price must be"):
            client.place_order('M1', side='yes', quantity=10, price=150)

    @patch('kalshi_client.requests.Session')
    def test_cancel_order(self, mock_session_class, mock_session):
        """Test cancelling an order"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {'cancelled': True}
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.cancel_order('O1')

        assert result.get('cancelled') is True

    @patch('kalshi_client.requests.Session')
    def test_get_orders(self, mock_session_class, mock_session):
        """Test getting orders"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'orders': [
                {'id': 'O1', 'status': 'filled'},
                {'id': 'O2', 'status': 'pending'}
            ]
        }
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.get_orders(status='pending')

        assert 'orders' in result

    @patch('kalshi_client.requests.Session')
    def test_get_portfolio(self, mock_session_class, mock_session):
        """Test getting portfolio"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'portfolio': {
                'balance': 1000.00,
                'positions': []
            }
        }
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.get_portfolio()

        assert 'portfolio' in result

    @patch('kalshi_client.requests.Session')
    def test_test_connection_success(self, mock_session_class, mock_session):
        """Test successful connection test"""
        mock_response = MagicMock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            'markets': [{'id': 'M1'}]
        }
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.test_connection()

        assert result is True

    @patch('kalshi_client.requests.Session')
    def test_test_connection_failure(self, mock_session_class, mock_session):
        """Test failed connection test"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("Connection failed")
        mock_session.request.return_value = mock_response

        client = KalshiClient(api_key="test-key")
        result = client.test_connection()

        assert result is False
