"""
Tests for database module
"""

import pytest
import os
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db import DatabaseManager


@pytest.fixture
def test_db():
    """Create test database connection"""
    # Use test database URL if available, otherwise use default
    test_url = os.getenv('TEST_DATABASE_URL', os.getenv('DATABASE_URL'))
    db = DatabaseManager(test_url)
    yield db
    # Cleanup could be added here


class TestDatabaseManager:
    """Test DatabaseManager class"""

    def test_connection(self, test_db):
        """Test database connection"""
        assert test_db.test_connection() is True

    def test_get_markets(self, test_db):
        """Test getting markets"""
        markets = test_db.get_markets(status='test')
        assert isinstance(markets, list)
        # Check if test data exists
        if markets:
            assert 'id' in markets[0]
            assert 'title' in markets[0]

    def test_insert_market(self, test_db):
        """Test inserting a market"""
        test_market = {
            'id': f'test-{datetime.utcnow().timestamp()}',
            'title': 'Test Market',
            'subtitle': 'Test subtitle',
            'category': 'test',
            'status': 'open',
            'open_time': None,
            'close_time': None,
            'ticker': 'TEST/YESNO',
            'min_price': 1.0,
            'max_price': 99.0,
            'volume': 0.0,
            'metadata': {'test': True}
        }

        result = test_db.insert_market(test_market)
        assert result is True

        # Verify it was inserted
        markets = test_db.get_markets()
        found = any(m['id'] == test_market['id'] for m in markets)
        assert found is True

    def test_get_market_history(self, test_db):
        """Test getting market history"""
        # Get history for a test market
        df = test_db.get_market_history('test-market-1', limit=10)
        assert isinstance(df, type(df))  # Check if it's a DataFrame

    def test_record_market_history(self, test_db):
        """Test recording market history"""
        result = test_db.record_market_history(
            'test-market-1',
            yes_price=50.0,
            no_price=50.0,
            volume=100.0
        )
        assert result is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
