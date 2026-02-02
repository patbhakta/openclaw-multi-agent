"""
Unit tests for Database Manager
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from db_manager import DatabaseManager


@pytest.fixture
def mock_connection():
    """Mock database connection"""
    with patch('db_manager.psycopg2.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = Mock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = Mock(return_value=False)
        mock_connect.return_value = mock_conn
        yield mock_conn, mock_cursor


class TestDatabaseManager:
    """Test DatabaseManager class"""

    def test_init_with_url(self):
        """Test initialization with database URL"""
        db = DatabaseManager(database_url="postgresql://user:pass@localhost/db")
        assert db.database_url == "postgresql://user:pass@localhost/db"

    def test_init_without_url(self):
        """Test initialization without database URL (uses env var)"""
        with patch.dict(os.environ, {'DATABASE_URL': 'test-url'}):
            db = DatabaseManager()
            assert db.database_url == 'test-url'

    @patch('db_manager.psycopg2.connect')
    def test_connect_success(self, mock_connect):
        """Test successful database connection"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        db = DatabaseManager()
        db.connect()

        mock_connect.assert_called_once()
        assert db.connection == mock_conn

    @patch('db_manager.psycopg2.connect')
    def test_connect_failure(self, mock_connect):
        """Test failed database connection"""
        import psycopg2
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        with pytest.raises(psycopg2.Error):
            db = DatabaseManager()
            db.connect()

    def test_disconnect(self, mock_connection):
        """Test disconnecting from database"""
        mock_conn, _ = mock_connection

        db = DatabaseManager()
        db.connection = mock_conn
        db.disconnect()

        mock_conn.close.assert_called_once()

    def test_execute_query(self, mock_connection):
        """Test executing SELECT query"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'test'}]

        db = DatabaseManager()
        db.connection = mock_conn

        results = db.execute_query("SELECT * FROM test")

        assert len(results) == 1
        assert results[0]['id'] == 1
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_execute_update(self, mock_connection):
        """Test executing INSERT/UPDATE/DELETE query"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.rowcount = 5

        db = DatabaseManager()
        db.connection = mock_conn

        affected = db.execute_update("UPDATE test SET name = 'new'")

        assert affected == 5
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_insert_market(self, mock_connection):
        """Test inserting a market"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.fetchall.return_value = [{'id': 1}]

        db = DatabaseManager()
        db.connection = mock_conn

        market_id = db.insert_market(
            kalshi_market_id="TEST-001",
            title="Test Market",
            category="test"
        )

        assert market_id == 1
        mock_cursor.execute.assert_called_once()

    def test_get_market_by_kalshi_id(self, mock_connection):
        """Test getting market by Kalshi ID"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'kalshi_market_id': 'TEST-001', 'title': 'Test Market'}
        ]

        db = DatabaseManager()
        db.connection = mock_conn

        market = db.get_market_by_kalshi_id("TEST-001")

        assert market is not None
        assert market['kalshi_market_id'] == 'TEST-001'

    def test_get_open_markets(self, mock_connection):
        """Test getting all open markets"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'status': 'open'},
            {'id': 2, 'status': 'open'}
        ]

        db = DatabaseManager()
        db.connection = mock_conn

        markets = db.get_open_markets()

        assert len(markets) == 2

    def test_get_latest_prices(self, mock_connection):
        """Test getting latest price history"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'yes_price': 0.50},
            {'id': 2, 'yes_price': 0.52}
        ]

        db = DatabaseManager()
        db.connection = mock_conn

        prices = db.get_latest_prices(market_id=1, limit=10)

        assert len(prices) == 2
        assert prices[0]['yes_price'] == 0.50

    def test_test_connection_success(self, mock_connection):
        """Test successful connection test"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.fetchall.return_value = [{'?column?': 1}]

        db = DatabaseManager()
        db.connection = mock_conn

        result = db.test_connection()

        assert result is True

    def test_test_connection_failure(self, mock_connection):
        """Test failed connection test"""
        mock_conn, mock_cursor = mock_connection
        mock_cursor.execute.side_effect = Exception("Error")

        db = DatabaseManager()
        db.connection = mock_conn

        result = db.test_connection()

        assert result is False
