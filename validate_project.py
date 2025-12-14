#!/usr/bin/env python3
"""
Simple validation script to check if project is ready without requiring all dependencies
"""

import os
import sys
import json
from pathlib import Path


def check_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")

    required_files = [
        "bot/telegram_bot.py",
        "bot/nlp_processor.py",
        "database/schema.sql",
        "database/connection.py",
        "config/settings.py",
        "scripts/migrate.py",
        "scripts/import_data.py",
        "main.py",
        "requirements.txt",
        "docker-compose.yml",
        "Dockerfile",
        "README.md",
        "data/videos.json"
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print(f"❌ Missing files: {missing}")
        return False

    print(f"✅ All {len(required_files)} required files present")
    return True


def check_json_structure():
    """Check if JSON data structure is correct"""
    print("🔍 Checking JSON data structure...")

    try:
        with open("data/videos.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        videos = data.get("videos", [])
        if not videos:
            print("❌ No videos found in JSON")
            return False

        # Check first video structure
        video = videos[0]
        required_video_fields = [
            "id", "creator_id", "video_created_at", "views_count",
            "likes_count", "comments_count", "reports_count",
            "created_at", "updated_at", "snapshots"
        ]

        for field in required_video_fields:
            if field not in video:
                print(f"❌ Missing field '{field}' in video structure")
                return False

        # Check snapshots structure
        snapshots = video.get("snapshots", [])
        if snapshots:
            snapshot = snapshots[0]
            required_snapshot_fields = [
                "id", "video_id", "views_count", "likes_count",
                "comments_count", "reports_count", "delta_views_count",
                "delta_likes_count", "delta_comments_count", "delta_reports_count",
                "created_at", "updated_at"
            ]

            for field in required_snapshot_fields:
                if field not in snapshot:
                    print(f"❌ Missing field '{field}' in snapshot structure")
                    return False

        print(f"✅ JSON structure valid - {len(videos)} videos, {len(snapshots)} snapshots per video")
        return True

    except Exception as e:
        print(f"❌ JSON validation failed: {e}")
        return False


def check_sql_schema():
    """Check if SQL schema is valid"""
    print("🔍 Checking SQL schema...")

    try:
        with open("database/schema.sql", "r", encoding="utf-8") as f:
            sql = f.read()

        # Basic checks
        if "CREATE TABLE" not in sql:
            print("❌ No CREATE TABLE statements found")
            return False

        if "videos" not in sql or "video_snapshots" not in sql:
            print("❌ Required tables not found in schema")
            return False

        if "PRIMARY KEY" not in sql:
            print("❌ No primary keys defined")
            return False

        if "REFERENCES" not in sql:
            print("❌ No foreign key relationships defined")
            return False

        print("✅ SQL schema structure looks valid")
        return True

    except Exception as e:
        print(f"❌ SQL schema validation failed: {e}")
        return False


def check_docker_config():
    """Check Docker configuration"""
    print("🔍 Checking Docker configuration...")

    try:
        with open("docker-compose.yml", "r", encoding="utf-8") as f:
            compose_content = f.read()

        with open("Dockerfile", "r", encoding="utf-8") as f:
            dockerfile_content = f.read()

        # Check docker-compose
        required_services = ["postgres", "bot"]
        for service in required_services:
            if f"{service}:" not in compose_content:
                print(f"❌ Service '{service}' not found in docker-compose.yml")
                return False

        if "TELEGRAM_BOT_TOKEN" not in compose_content:
            print("❌ TELEGRAM_BOT_TOKEN not configured in docker-compose")
            return False

        # Check Dockerfile
        if "FROM python" not in dockerfile_content:
            print("❌ Dockerfile doesn't use Python base image")
            return False

        print("✅ Docker configuration looks valid")
        return True

    except Exception as e:
        print(f"❌ Docker validation failed: {e}")
        return False


def calculate_expected_results():
    """Calculate expected results for TZ queries"""
    print("🔍 Calculating expected query results...")

    try:
        with open("data/videos.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        videos = data["videos"]

        # Query 1: Total videos
        total_videos = len(videos)

        # Query 2: Videos with >100k views
        videos_over_100k = len([v for v in videos if v["views_count"] > 100000])

        # Collect all snapshots
        all_snapshots = []
        for video in videos:
            all_snapshots.extend(video.get("snapshots", []))

        # Query 3: Total view growth on Nov 28, 2025
        nov28_snapshots = [s for s in all_snapshots if s["created_at"].startswith("2025-11-28")]
        total_growth_nov28 = sum(s["delta_views_count"] for s in nov28_snapshots)

        # Query 4: Videos with new views on Nov 27, 2025
        nov27_snapshots = [s for s in all_snapshots if s["created_at"].startswith("2025-11-27")]
        videos_with_new_views_nov27 = len(set(s["video_id"] for s in nov27_snapshots if s["delta_views_count"] > 0))

        print("📊 Expected results:")
        print(f"   - Total videos: {total_videos}")
        print(f"   - Videos >100k views: {videos_over_100k}")
        print(f"   - View growth Nov 28: {total_growth_nov28}")
        print(f"   - Videos with new views Nov 27: {videos_with_new_views_nov27}")

        return True

    except Exception as e:
        print(f"❌ Result calculation failed: {e}")
        return False


def main():
    """Main validation function"""
    print("🚀 PROJECT VALIDATION CHECK")
    print("=" * 50)

    checks = [
        check_files,
        check_json_structure,
        check_sql_schema,
        check_docker_config,
        calculate_expected_results
    ]

    passed = 0
    total = len(checks)

    for check in checks:
        try:
            if check():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Check {check.__name__} crashed: {e}")
            print()

    print("=" * 50)
    print(f"📊 VALIDATION RESULTS: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 PROJECT IS READY!")
        print("\n📋 Next steps:")
        print("1. Create .env file with your API tokens")
        print("2. Run: docker-compose up --build")
        print("3. Test bot with the example queries")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

