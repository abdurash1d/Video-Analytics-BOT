#!/usr/bin/env python3
"""Script to import video data from JSON file into PostgreSQL"""

import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db_cursor


def load_json_data(file_path: str) -> Dict[str, Any]:
    """Load JSON data from file"""
    print(f"Loading data from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def insert_videos(cursor, videos: List[Dict[str, Any]]) -> None:
    """Insert videos into database"""
    print(f"Inserting {len(videos)} videos...")

    video_query = """
    INSERT INTO videos (id, creator_id, video_created_at, views_count, likes_count,
                       comments_count, reports_count, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING
    """

    for video in videos:
        cursor.execute(video_query, (
            video['id'],
            video['creator_id'],
            video['video_created_at'],
            video['views_count'],
            video['likes_count'],
            video['comments_count'],
            video['reports_count'],
            video['created_at'],
            video['updated_at']
        ))


def insert_snapshots(cursor, video_id: str, snapshots: List[Dict[str, Any]]) -> None:
    """Insert snapshots for a specific video"""
    if not snapshots:
        return

    snapshot_query = """
    INSERT INTO video_snapshots (id, video_id, views_count, likes_count, comments_count,
                                reports_count, delta_views_count, delta_likes_count,
                                delta_comments_count, delta_reports_count, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING
    """

    for snapshot in snapshots:
        cursor.execute(snapshot_query, (
            snapshot['id'],
            video_id,
            snapshot['views_count'],
            snapshot['likes_count'],
            snapshot['comments_count'],
            snapshot['reports_count'],
            snapshot['delta_views_count'],
            snapshot['delta_likes_count'],
            snapshot['delta_comments_count'],
            snapshot['delta_reports_count'],
            snapshot['created_at'],
            snapshot['updated_at']
        ))


def import_data(json_file_path: str) -> None:
    """Main import function"""
    try:
        # Load JSON data
        data = load_json_data(json_file_path)
        videos = data.get('videos', [])

        if not videos:
            print("❌ No videos found in JSON file")
            return

        print(f"Found {len(videos)} videos to import")

        # Import data
        with get_db_cursor() as cursor:
            # Insert videos
            insert_videos(cursor, videos)

            # Insert snapshots for each video
            total_snapshots = 0
            for video in videos:
                snapshots = video.get('snapshots', [])
                insert_snapshots(cursor, video['id'], snapshots)
                total_snapshots += len(snapshots)

            print(f"✅ Successfully imported {len(videos)} videos and {total_snapshots} snapshots")

    except Exception as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python import_data.py <json_file_path>")
        sys.exit(1)

    json_file_path = sys.argv[1]
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        sys.exit(1)

    import_data(json_file_path)

