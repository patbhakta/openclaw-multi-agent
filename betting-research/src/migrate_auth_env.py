#!/usr/bin/env python3
"""
Simple migration script to add 'environment' column to auth table.
Run this from the betting-research/src directory.
"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/openalgo')

from sqlalchemy import text
from database.auth_db import engine


def migrate():
    """Add environment column to auth table if it doesn't exist"""
    try:
        with engine.connect() as conn:
            # Check if column exists
            check_sql = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'auth' AND column_name = 'environment'
            """)
            result = conn.execute(check_sql).fetchone()

            if result:
                print("✅ 'environment' column already exists in auth table")
                return True

            # Add the column
            alter_sql = text("""
                ALTER TABLE auth
                ADD COLUMN environment VARCHAR(20) DEFAULT 'demo'
            """)
            conn.execute(alter_sql)
            conn.commit()

            print("✅ Successfully added 'environment' column to auth table")
            print("   Default value: 'demo'")
            print("   Allowed values: 'demo', 'production'")
            return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Kalshi Integration Migration")
    print("=" * 60)
    print()

    if migrate():
        print()
        print("✅ Migration completed successfully")
    else:
        print()
        print("❌ Migration failed")
