#!/usr/bin/env python3
"""Database migration script"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_cursor


def run_migrations():
    """Run database migrations"""
    print("Running database migrations...")

    # Read schema file
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    try:
        with get_db_cursor() as cursor:
            cursor.execute(schema_sql)
        print("✅ Database schema created successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()

