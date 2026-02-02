"""
Data collection script for betting markets
Collects market data from Kalshi and stores in database
"""

import os
import time
from datetime import datetime

from dotenv import load_dotenv

from .db import DatabaseManager
from .kalshi_client import KalshiClient

# Load environment variables
load_dotenv()


class DataCollector:
    """Collects and stores market data"""

    def __init__(self):
        """Initialize data collector"""
        self.db = DatabaseManager()
        self.kalshi = KalshiClient(
            environment=os.getenv('KALSHI_ENVIRONMENT', 'demo')
        )

        # Track last collection time
        self.last_collection = None

    def test_connections(self) -> bool:
        """Test database and API connections"""
        db_ok = self.db.test_connection()
        api_ok = self.kalshi.authenticate()

        print(f"Database connection: {'✓' if db_ok else '✗'}")
        print(f"Kalshi API connection: {'✓' if api_ok else '✗'}")

        return db_ok and api_ok

    def collect_markets(self, status: str = 'open', limit: int = 100) -> int:
        """
        Collect markets from Kalshi and store in database

        Args:
            status: Market status to collect
            limit: Maximum markets to collect

        Returns:
            Number of markets collected
        """
        print(f"\nCollecting markets (status={status}, limit={limit})...")

        markets = self.kalshi.get_markets(status=status, limit=limit)

        if not markets:
            print("No markets found")
            return 0

        stored_count = 0
        for market in markets:
            # Transform Kalshi market data to our schema
            market_data = {
                'id': market.get('ticker', market.get('market_id', '')),
                'title': market.get('title', ''),
                'subtitle': market.get('subtitle', ''),
                'category': market.get('category', ''),
                'status': market.get('status', 'unknown'),
                'open_time': market.get('open_time'),
                'close_time': market.get('close_time'),
                'ticker': market.get('ticker', ''),
                'min_price': market.get('min_price', 1),
                'max_price': market.get('max_price', 99),
                'volume': market.get('volume', 0),
                'metadata': {
                    'category': market.get('category', ''),
                    'subtitle': market.get('subtitle', ''),
                    'group_id': market.get('group_id', ''),
                    'event_ticker': market.get('event_ticker', '')
                }
            }

            if self.db.insert_market(market_data):
                stored_count += 1

        print(f"Stored {stored_count} markets")
        return stored_count

    def collect_market_history(self, market_ids: list = None) -> int:
        """
        Collect price history for specific markets

        Args:
            market_ids: List of market IDs (None = all open markets)

        Returns:
            Number of history records collected
        """
        print("\nCollecting market history...")

        if market_ids is None:
            # Get all open markets from database
            markets = self.db.get_markets(status='open')
            market_ids = [m['id'] for m in markets]

        if not market_ids:
            print("No markets to collect history for")
            return 0

        records_collected = 0

        for market_id in market_ids:
            # Get orderbook for current prices
            orderbook = self.kalshi.get_orderbook(market_id)

            if orderbook:
                # Extract yes and no prices from orderbook
                yes_bid = orderbook.get('bids', {}).get('yes', [{}])[0].get('price') if orderbook.get('bids', {}).get('yes') else None
                yes_ask = orderbook.get('asks', {}).get('yes', [{}])[0].get('price') if orderbook.get('asks', {}).get('yes') else None
                no_bid = orderbook.get('bids', {}).get('no', [{}])[0].get('price') if orderbook.get('bids', {}).get('no') else None
                no_ask = orderbook.get('asks', {}).get('no', [{}])[0].get('price') if orderbook.get('asks', {}).get('no') else None

                # Use mid price if both available
                yes_price = (yes_bid + yes_ask) / 2 if yes_bid and yes_ask else yes_bid or yes_ask
                no_price = (no_bid + no_ask) / 2 if no_bid and no_ask else no_bid or no_ask

                # Get market for volume
                market = self.kalshi.get_market(market_id)
                volume = market.get('volume', 0) if market else 0

                if self.db.record_market_history(market_id, yes_price, no_price, volume):
                    records_collected += 1

                print(f"  Recorded history for {market_id}: yes={yes_price}, no={no_price}, vol={volume}")

        print(f"Collected {records_collected} history records")
        return records_collected

    def run_collection_cycle(self) -> dict:
        """
        Run a full collection cycle

        Returns:
            Dictionary with collection stats
        """
        print(f"\n{'='*60}")
        print(f"Starting collection cycle at {datetime.utcnow().isoformat()}")
        print(f"{'='*60}")

        if not self.test_connections():
            return {
                'success': False,
                'error': 'Connection test failed'
            }

        stats = {
            'timestamp': datetime.utcnow().isoformat(),
            'markets_collected': 0,
            'open_markets': 0,
            'history_records': 0,
            'success': True
        }

        # Collect open markets
        stats['open_markets'] = self.collect_markets(status='open', limit=100)
        stats['markets_collected'] += stats['open_markets']

        # Collect closed markets (smaller set)
        stats['markets_collected'] += self.collect_markets(status='closed', limit=50)

        # Collect price history for open markets
        stats['history_records'] = self.collect_market_history()

        self.last_collection = datetime.utcnow()

        print(f"\nCollection complete!")
        print(f"  Total markets: {stats['markets_collected']}")
        print(f"  Open markets: {stats['open_markets']}")
        print(f"  History records: {stats['history_records']}")
        print(f"{'='*60}\n")

        return stats


def main():
    """Main entry point"""
    print("Betting Market Data Collector")
    print("=" * 40)

    collector = DataCollector()

    # Run one collection cycle
    stats = collector.run_collection_cycle()

    if stats['success']:
        print("\n✓ Collection successful")
    else:
        print(f"\n✗ Collection failed: {stats.get('error', 'Unknown error')}")
        return 1

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
