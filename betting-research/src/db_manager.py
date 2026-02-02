"""
Database Manager - Handles PostgreSQL operations for market data
Provides interface to store/retrieve Kalshi market data
"""

import os
from typing import List, Dict, Optional
from datetime import datetime, timezone
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manager for PostgreSQL database operations"""

    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize database connection

        Args:
            database_url: PostgreSQL connection URL
                         (reads from DATABASE_URL env var if not provided)
        """
        self.database_url = database_url or os.getenv('DATABASE_URL')

        if not self.database_url:
            logger.warning("DATABASE_URL not set. Using default localhost connection.")
            self.database_url = "postgresql://postgres:postgres@localhost:5432/betting_markets"

        self.connection = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = psycopg2.connect(self.database_url, cursor_factory=RealDictCursor)
            logger.info("✅ Database connection established")
        except psycopg2.Error as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """
        Execute a SELECT query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            self.connection.commit()
            return [dict(row) for row in results]

    def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an INSERT/UPDATE/DELETE query

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Number of rows affected
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            affected_rows = cursor.rowcount
            self.connection.commit()
            return affected_rows

    def insert_market(self,
                      kalshi_market_id: str,
                      title: str,
                      subtitle: Optional[str] = None,
                      category: Optional[str] = None,
                      status: str = 'open',
                      close_time: Optional[datetime] = None,
                      ticker: Optional[str] = None) -> int:
        """
        Insert or update a market

        Args:
            kalshi_market_id: Kalshi market identifier
            title: Market title
            subtitle: Market subtitle
            category: Market category
            status: Market status
            close_time: Market closing time
            ticker: Market ticker

        Returns:
            Database market ID
        """
        query = """
            INSERT INTO markets (kalshi_market_id, title, subtitle, category, status, close_time, ticker)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (kalshi_market_id)
            DO UPDATE SET
                title = EXCLUDED.title,
                subtitle = EXCLUDED.subtitle,
                category = EXCLUDED.category,
                status = EXCLUDED.status,
                close_time = EXCLUDED.close_time,
                ticker = EXCLUDED.ticker,
                updated_at = NOW()
            RETURNING id
        """

        result = self.execute_query(
            query,
            (kalshi_market_id, title, subtitle, category, status, close_time, ticker)
        )

        if result:
            market_id = result[0]['id']
            logger.info(f"Market inserted/updated: {kalshi_market_id} (id={market_id})")
            return market_id
        return None

    def insert_market_price(self,
                           market_id: int,
                           yes_price: Optional[float] = None,
                           no_price: Optional[float] = None,
                           yes_volume: Optional[float] = None,
                           no_volume: Optional[float] = None) -> int:
        """
        Insert market price snapshot

        Args:
            market_id: Database market ID
            yes_price: Current YES price
            no_price: Current NO price
            yes_volume: YES volume
            no_volume: NO volume

        Returns:
            Number of rows inserted
        """
        query = """
            INSERT INTO market_prices (market_id, yes_price, no_price, yes_volume, no_volume)
            VALUES (%s, %s, %s, %s, %s)
        """

        affected = self.execute_update(
            query,
            (market_id, yes_price, no_price, yes_volume, no_volume)
        )

        if affected > 0:
            logger.debug(f"Price inserted for market_id={market_id}")
        return affected

    def get_market_by_kalshi_id(self, kalshi_market_id: str) -> Optional[Dict]:
        """
        Get market by Kalshi market ID

        Args:
            kalshi_market_id: Kalshi market identifier

        Returns:
            Market data or None
        """
        query = "SELECT * FROM markets WHERE kalshi_market_id = %s"
        results = self.execute_query(query, (kalshi_market_id,))
        return results[0] if results else None

    def get_open_markets(self) -> List[Dict]:
        """
        Get all open markets

        Returns:
            List of open markets
        """
        query = "SELECT * FROM markets WHERE status = 'open' ORDER BY close_time"
        return self.execute_query(query)

    def get_latest_prices(self, market_id: int, limit: int = 100) -> List[Dict]:
        """
        Get latest price history for a market

        Args:
            market_id: Database market ID
            limit: Number of price points to return

        Returns:
            List of price snapshots
        """
        query = """
            SELECT * FROM market_prices
            WHERE market_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        return self.execute_query(query, (market_id, limit))

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful
        """
        try:
            self.execute_query("SELECT 1")
            logger.info("✅ Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize database manager
    db = DatabaseManager()

    # Test connection
    if db.test_connection():
        # Get open markets
        markets = db.get_open_markets()
        print(f"Found {len(markets)} open markets in database")

        # Example: Insert a test market
        # market_id = db.insert_market(
        #     kalshi_market_id="test-market-001",
        #     title="Test Market",
        #     category="test",
        #     status="open"
        # )
        # print(f"Created market with ID: {market_id}")

    db.disconnect()
