"""
Database module for betting markets
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


class DatabaseManager:
    """Manager for database operations"""

    def __init__(self, database_url: str = None):
        """
        Initialize database manager

        Args:
            database_url: PostgreSQL connection URL
        """
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'postgresql://betting_user:betting_password@localhost:5432/betting_markets'
            )

        self.engine: Engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def insert_market(self, market_data: Dict[str, Any]) -> bool:
        """
        Insert or update market data

        Args:
            market_data: Market data dictionary

        Returns:
            Success status
        """
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO markets (
                        id, title, subtitle, category, status,
                        open_time, close_time, ticker, min_price,
                        max_price, volume, metadata
                    ) VALUES (
                        :id, :title, :subtitle, :category, :status,
                        :open_time, :close_time, :ticker, :min_price,
                        :max_price, :volume, :metadata
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        subtitle = EXCLUDED.subtitle,
                        category = EXCLUDED.category,
                        status = EXCLUDED.status,
                        open_time = EXCLUDED.open_time,
                        close_time = EXCLUDED.close_time,
                        ticker = EXCLUDED.ticker,
                        min_price = EXCLUDED.min_price,
                        max_price = EXCLUDED.max_price,
                        volume = EXCLUDED.volume,
                        metadata = EXCLUDED.metadata,
                        updated_at = CURRENT_TIMESTAMP
                """)
                conn.execute(query, market_data)
                conn.commit()
            return True
        except Exception as e:
            print(f"Failed to insert market: {e}")
            return False

    def get_markets(self, status: str = None, category: str = None) -> List[Dict]:
        """
        Get markets with optional filters

        Args:
            status: Filter by status
            category: Filter by category

        Returns:
            List of market dictionaries
        """
        try:
            with self.engine.connect() as conn:
                query = "SELECT * FROM markets WHERE 1=1"
                params = {}

                if status:
                    query += " AND status = :status"
                    params['status'] = status

                if category:
                    query += " AND category = :category"
                    params['category'] = category

                query += " ORDER BY close_time DESC"

                result = conn.execute(text(query), params)
                columns = result.keys()
                return [dict(zip(columns, row)) for row in result.fetchall()]
        except Exception as e:
            print(f"Failed to get markets: {e}")
            return []

    def record_market_history(self, market_id: str, yes_price: float,
                              no_price: float, volume: float) -> bool:
        """
        Record market price history

        Args:
            market_id: Market ID
            yes_price: Yes contract price
            no_price: No contract price
            volume: Trading volume

        Returns:
            Success status
        """
        try:
            with self.engine.connect() as conn:
                query = text("""
                    INSERT INTO market_history (market_id, yes_price, no_price, volume)
                    VALUES (:market_id, :yes_price, :no_price, :volume)
                """)
                conn.execute(query, {
                    'market_id': market_id,
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'volume': volume
                })
                conn.commit()
            return True
        except Exception as e:
            print(f"Failed to record market history: {e}")
            return False

    def get_market_history(self, market_id: str, limit: int = 100) -> pd.DataFrame:
        """
        Get market price history

        Args:
            market_id: Market ID
            limit: Maximum records to return

        Returns:
            DataFrame with market history
        """
        try:
            query = """
                SELECT * FROM market_history
                WHERE market_id = :market_id
                ORDER BY recorded_at DESC
                LIMIT :limit
            """
            df = pd.read_sql_query(
                query,
                self.engine,
                params={'market_id': market_id, 'limit': limit}
            )
            return df
        except Exception as e:
            print(f"Failed to get market history: {e}")
            return pd.DataFrame()
