"""
Main entry point for betting research services
"""

import sys


def main():
    """Main entry point"""
    print("Betting Research Service")
    print("=" * 40)
    print("\nAvailable services:")
    print("  - Data collection (use: python -m src.collect_data)")
    print("  - Jupyter notebooks (access via port 8888)")
    print("  - PostgreSQL database (access via port 5432)")
    print("\nTo start the full stack:")
    print("  docker-compose up -d")
    print("\nTo collect data:")
    print("  docker-compose run --rm kalshi-bot python -m src.collect_data")
    print("\nTo start Jupyter:")
    print("  docker-compose up -d jupyter")

    return 0


if __name__ == '__main__':
    sys.exit(main())
