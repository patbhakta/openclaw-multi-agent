#!/usr/bin/env python3
"""
Simple migration script to add 'environment' column to auth table.
Uses betting-research database connection.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Get database connection from environment"""
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        # Fallback to localhost
        database_url = "postgresql://betting_user:betting_password@postgres:5432/betting_markets"

    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)


def migrate():
    """Add environment column to auth table if it doesn't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if column exists
        check_sql = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'auth' AND column_name = 'environment'
        """
        cursor.execute(check_sql)
        result = cursor.fetchone()

        if result:
            print("✅ 'environment' column already exists in auth table")
            cursor.close()
            conn.close()
            return True

        # Add the column
        alter_sql = """
            ALTER TABLE auth
            ADD COLUMN environment VARCHAR(20) DEFAULT 'demo'
        """
        cursor.execute(alter_sql)
        conn.commit()

        print("✅ Successfully added 'environment' column to auth table")
        print("   Default value: 'demo'")
        print("   Allowed values: 'demo', 'production'")

        cursor.close()
        conn.close()
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
