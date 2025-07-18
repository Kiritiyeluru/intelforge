#!/usr/bin/env python3
"""
TTR (Time-to-Recovery) Tracking Test Script
Demonstrates the TTR tracking system with target <60s recovery time
"""

import json
import time

from intel_bot_driver import IntelBotDriver, TTRTracker


def test_ttr_tracking():
    """Test TTR tracking system with various scenarios"""
    print("🕒 Testing TTR (Time-to-Recovery) Tracking System")
    print("=" * 60)

    # Test URLs with different expected behaviors
    test_scenarios = [
        {
            "name": "Fast Success",
            "url": "https://httpbin.org/user-agent",
            "expected_ttr": "<5s",
        },
        {"name": "Medium Load", "url": "https://example.com", "expected_ttr": "<10s"},
        {
            "name": "Potential Challenge",
            "url": "https://bot.sannysoft.com/",
            "expected_ttr": "<30s",
        },
        {
            "name": "Invalid URL (Failure Test)",
            "url": "https://this-definitely-does-not-exist-12345.com",
            "expected_ttr": "N/A (Expected Failure)",
        },
    ]

    results = []

    with IntelBotDriver(headless=True, enable_ttr_tracking=True) as driver:
        for scenario in test_scenarios:
            print(f"\n📊 Testing: {scenario['name']}")
            print(f"   URL: {scenario['url']}")
            print(f"   Expected TTR: {scenario['expected_ttr']}")

            time.time()
            result = driver.get(scenario["url"])

            if result["success"]:
                ttr = result.get("ttr_seconds", 0)
                status = "✅ SUCCESS"

                # Check if TTR meets target
                if ttr < 60:
                    ttr_status = "✅ UNDER TARGET"
                else:
                    ttr_status = "⚠️ OVER TARGET"

                print(f"   Result: {status}")
                print(f"   TTR: {ttr:.2f}s {ttr_status}")
                print(f"   Attempts: {result['attempt']}")

                # Get page info for additional validation
                try:
                    page_info = driver.get_page_info()
                    print(f"   Title: {page_info['title'][:50]}...")
                except:
                    print("   Title: Unable to retrieve")

            else:
                print("   Result: ❌ FAILED")
                print(f"   Error: {result['error']}")
                print(f"   Attempts: {result.get('attempts', 'Unknown')}")

            results.append(
                {
                    "scenario": scenario["name"],
                    "url": scenario["url"],
                    "success": result["success"],
                    "ttr_seconds": result.get("ttr_seconds"),
                    "attempts": result.get("attempt", result.get("attempts")),
                    "error": result.get("error"),
                }
            )

    # Analyze TTR performance
    print("\n📈 TTR Performance Analysis")
    print("=" * 40)

    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]

    if successful_tests:
        ttrs = [r["ttr_seconds"] for r in successful_tests]
        avg_ttr = sum(ttrs) / len(ttrs)
        max_ttr = max(ttrs)
        min_ttr = min(ttrs)

        print(f"Successful Operations: {len(successful_tests)}")
        print(f"Average TTR: {avg_ttr:.2f}s")
        print(f"Min TTR: {min_ttr:.2f}s")
        print(f"Max TTR: {max_ttr:.2f}s")

        # Check target compliance
        under_target = len([t for t in ttrs if t < 60])
        print(
            f"Under 60s Target: {under_target}/{len(ttrs)} ({(under_target / len(ttrs) * 100):.1f}%)"
        )

        if avg_ttr < 60:
            print("✅ AVERAGE TTR MEETS TARGET (<60s)")
        else:
            print("⚠️ AVERAGE TTR EXCEEDS TARGET")

    if failed_tests:
        print(f"\nFailed Operations: {len(failed_tests)}")
        for test in failed_tests:
            print(f"  - {test['scenario']}: {test['error']}")

    # Check TTR session data
    ttr_tracker = TTRTracker()
    if ttr_tracker.session_file.exists():
        print("\n📊 TTR Session Data Saved:")
        print(f"   Location: {ttr_tracker.session_file}")

        with open(ttr_tracker.session_file, "r") as f:
            session_data = json.load(f)

        print(f"   Total Sessions: {len(session_data)}")
        print(
            f"   Latest Session: {session_data[-1]['start_timestamp'] if session_data else 'None'}"
        )

    print("\n✅ TTR Tracking Test Complete")
    return results


def analyze_historical_ttr():
    """Analyze historical TTR data if available"""
    ttr_tracker = TTRTracker()

    if not ttr_tracker.session_file.exists():
        print("No historical TTR data available")
        return

    with open(ttr_tracker.session_file, "r") as f:
        sessions = json.load(f)

    if not sessions:
        print("No TTR sessions found")
        return

    print("\n📊 Historical TTR Analysis")
    print("=" * 40)

    successful_sessions = [s for s in sessions if s.get("success")]
    failed_sessions = [s for s in sessions if not s.get("success")]

    print(f"Total Sessions: {len(sessions)}")
    print(f"Successful: {len(successful_sessions)}")
    print(f"Failed: {len(failed_sessions)}")
    print(f"Success Rate: {(len(successful_sessions) / len(sessions) * 100):.1f}%")

    if successful_sessions:
        ttrs = [s["ttr_seconds"] for s in successful_sessions]
        print("\nTTR Statistics:")
        print(f"  Average: {sum(ttrs) / len(ttrs):.2f}s")
        print(f"  Min: {min(ttrs):.2f}s")
        print(f"  Max: {max(ttrs):.2f}s")

        # Categorize TTR performance
        excellent = len([t for t in ttrs if t < 5])
        good = len([t for t in ttrs if 5 <= t < 15])
        acceptable = len([t for t in ttrs if 15 <= t < 60])
        poor = len([t for t in ttrs if t >= 60])

        print("\nTTR Distribution:")
        print(f"  Excellent (<5s): {excellent} ({excellent / len(ttrs) * 100:.1f}%)")
        print(f"  Good (5-15s): {good} ({good / len(ttrs) * 100:.1f}%)")
        print(
            f"  Acceptable (15-60s): {acceptable} ({acceptable / len(ttrs) * 100:.1f}%)"
        )
        print(f"  Poor (>60s): {poor} ({poor / len(ttrs) * 100:.1f}%)")


if __name__ == "__main__":
    # Run TTR tracking test
    test_results = test_ttr_tracking()

    # Analyze historical data
    analyze_historical_ttr()
