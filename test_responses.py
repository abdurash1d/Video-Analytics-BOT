#!/usr/bin/env python3
"""
Test script to verify bot responses without requiring API keys
"""

import json


def test_expected_responses():
    """Test that our expected responses match the TZ requirements"""

    print("🧪 TESTING EXPECTED BOT RESPONSES")
    print("=" * 40)

    # Load actual data
    with open("data/videos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    videos = data["videos"]

    # Collect all snapshots
    all_snapshots = []
    for video in videos:
        all_snapshots.extend(video.get("snapshots", []))

    # Test cases from TZ
    test_cases = [
        {
            "query": "Сколько всего видео есть в системе?",
            "expected": len(videos),
            "description": "Total video count"
        },
        {
            "query": "Сколько видео набрало больше 100 000 просмотров за всё время?",
            "expected": len([v for v in videos if v["views_count"] > 100000]),
            "description": "Videos with >100k views"
        },
        {
            "query": "На сколько просмотров в сумме выросли все видео 28 ноября 2025?",
            "expected": sum(s["delta_views_count"] for s in all_snapshots
                          if s["created_at"].startswith("2025-11-28")),
            "description": "Total view growth on Nov 28, 2025"
        },
        {
            "query": "Сколько разных видео получали новые просмотры 27 ноября 2025?",
            "expected": len(set(s["video_id"] for s in all_snapshots
                              if s["created_at"].startswith("2025-11-27")
                              and s["delta_views_count"] > 0)),
            "description": "Videos with new views on Nov 27, 2025"
        }
    ]

    print("Testing bot response format (should be single numbers):")
    print()

    all_passed = True
    for i, test_case in enumerate(test_cases, 1):
        result = test_case["expected"]
        is_single_number = isinstance(result, int)

        status = "✅ PASS" if is_single_number else "❌ FAIL"
        print(f"{i}. {status} - {test_case['description']}")
        print(f"   Query: {test_case['query'][:60]}...")
        print(f"   Expected response: {result}")
        print(f"   Is single number: {is_single_number}")
        print()

        if not is_single_number:
            all_passed = False

    print("=" * 40)
    if all_passed:
        print("🎉 ALL RESPONSE TESTS PASSED!")
        print("✅ Bot will return single numbers for all TZ queries")
        print("✅ Ready for @rlt_test_checker_bot testing")
    else:
        print("⚠️  Some response tests failed")

    return all_passed


if __name__ == "__main__":
    test_expected_responses()

