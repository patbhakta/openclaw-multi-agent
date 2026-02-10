#!/usr/bin/env python3
"""
Migration script to add 'environment' column to auth table for Kalshi integration.

This migration adds support for storing Kalshi environment (demo/production) in the auth table.
Run this script to update existing databases.
"""

import os
import sys

# Add OpenAlgo to path
sys.path.insert(0, '/root/.openclaw/workspace/openalgo')

from sqlalchemy import text
from database.auth_db import engine, logger


def migrate():
    """Add environment column to auth table if it doesn't exist"""
    try:
        # Check if column already exists
        check_sql = text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'auth' AND column_name = 'environment'
        """)

        with engine.connect() as conn:
            result = conn.execute(check_sql).fetchone()

            if result:
                logger.info("✅ 'environment' column already exists in auth table")
                return True

        # Add the column
        alter_sql = text("""
            ALTER TABLE auth
            ADD COLUMN environment VARCHAR(20) DEFAULT 'demo'
        """)

        with engine.connect() as conn:
            conn.execute(alter_sql)
            conn.commit()

        logger.info("✅ Successfully added 'environment' column to auth table")
        logger.info("   Default value: 'demo'")
        logger.info("   Allowed values: 'demo', 'production'")

        return True

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Kalshi Integration Migration")
    print("=" * 60)
    print()

    if migrate():
        print()
        print("✅ Migration completed successfully")
        sys.exit(0)
    else:
        print()
        print("❌ Migration failed")
        sys.exit(1)
