#!/usr/bin/env python3
"""
Test script for Video Analytics Bot functionality
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import get_db_cursor
from bot.nlp_processor import NLPProcessor


def test_database_connection():
    """Test database connection and basic queries"""
    print("🧪 Testing database connection...")

    try:
        with get_db_cursor() as cursor:
            # Test basic connection
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            assert result['test'] == 1
            print("✅ Database connection works")

            # Check if tables exist
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('videos', 'video_snapshots')
            """)
            tables = cursor.fetchall()
            table_names = [row['table_name'] for row in tables]

            assert 'videos' in table_names
            assert 'video_snapshots' in table_names
            print("✅ Database tables exist")

            # Check data counts
            cursor.execute("SELECT COUNT(*) as video_count FROM videos")
            video_count = cursor.fetchone()['video_count']
            print(f"📊 Videos in database: {video_count}")

            cursor.execute("SELECT COUNT(*) as snapshot_count FROM video_snapshots")
            snapshot_count = cursor.fetchone()['snapshot_count']
            print(f"📊 Snapshots in database: {snapshot_count}")

            return True

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_nlp_processor():
    """Test NLP processor with sample queries"""
    print("\n🧪 Testing NLP processor...")

    processor = NLPProcessor()

    # Test queries from TZ
    test_queries = [
        "Сколько всего видео есть в системе?",
        "Сколько видео набрало больше 1000 просмотров за всё время?",
        "На сколько просмотров в сумме выросли все видео 28 ноября 2025?",
        "Сколько разных видео получали новые просмотры 27 ноября 2025?"
    ]

    success_count = 0

    for query in test_queries:
        print(f"\n  Testing: {query}")
        try:
            # Generate SQL
            sql = processor.generate_sql_query(query)
            if sql:
                print(f"  ✅ Generated SQL: {sql[:100]}...")

                # Execute query
                result = processor.execute_query_and_get_result(sql)
                if result is not None:
                    print(f"  ✅ Result: {result}")
                    success_count += 1
                else:
                    print("  ❌ Failed to execute query")
            else:
                print("  ❌ Failed to generate SQL")

        except Exception as e:
            print(f"  ❌ Error: {e}")

    print(f"\n✅ NLP tests passed: {success_count}/{len(test_queries)}")
    return success_count > 0


def test_data_integrity():
    """Test data integrity"""
    print("\n🧪 Testing data integrity...")

    try:
        with get_db_cursor() as cursor:
            # Check for orphaned snapshots
            cursor.execute("""
                SELECT COUNT(*) as orphaned_count
                FROM video_snapshots vs
                LEFT JOIN videos v ON vs.video_id = v.id
                WHERE v.id IS NULL
            """)
            orphaned = cursor.fetchone()['orphaned_count']
            assert orphaned == 0, f"Found {orphaned} orphaned snapshots"
            print("✅ No orphaned snapshots")

            # Check date ranges
            cursor.execute("SELECT MIN(video_created_at), MAX(video_created_at) FROM videos")
            date_range = cursor.fetchone()
            print(f"📅 Video dates range: {date_range['min']} to {date_range['max']}")

            # Check snapshot dates
            cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM video_snapshots")
            snap_range = cursor.fetchone()
            print(f"📅 Snapshot dates range: {snap_range['min']} to {snap_range['max']}")

            return True

    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Running Video Analytics Bot Tests")
    print("=" * 50)

    tests = [
        test_database_connection,
        test_data_integrity,
        test_nlp_processor
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Bot is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

