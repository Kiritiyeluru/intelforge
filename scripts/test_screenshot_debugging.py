#!/usr/bin/env python3
"""
Screenshot-on-Detection Debugging Test
Tests the automatic screenshot capture functionality when detection or failures occur.
"""

import os
import time
from pathlib import Path

from intel_bot_driver import IntelBotDriver


def test_screenshot_debugging():
    """Test screenshot debugging functionality"""
    print("📸 Testing Screenshot-on-Detection Debugging")
    print("=" * 50)

    # Test scenarios that may trigger screenshots
    test_scenarios = [
        {
            "name": "Valid URL (Should succeed, no screenshot)",
            "url": "https://httpbin.org/user-agent",
            "expected_outcome": "success",
        },
        {
            "name": "Invalid URL (Should fail, trigger screenshot)",
            "url": "https://definitely-does-not-exist-12345.invalid",
            "expected_outcome": "failure_with_screenshot",
        },
        {
            "name": "Slow URL (May timeout, trigger screenshot)",
            "url": "https://httpbin.org/delay/30",  # Very slow response
            "expected_outcome": "possible_timeout",
        },
        {
            "name": "Detection Test Site (May trigger anti-bot, screenshot)",
            "url": "https://bot.sannysoft.com/",
            "expected_outcome": "possible_detection",
        },
    ]

    screenshots_dir = Path("reports/screenshots")
    initial_screenshot_count = (
        len(list(screenshots_dir.glob("*.png"))) if screenshots_dir.exists() else 0
    )

    print(f"Initial screenshot count: {initial_screenshot_count}")

    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Test {i}: {scenario['name']}")
        print(f"   URL: {scenario['url']}")
        print(f"   Expected: {scenario['expected_outcome']}")

        start_time = time.time()

        try:
            with IntelBotDriver(headless=True, enable_ttr_tracking=True) as driver:
                result = driver.get(
                    scenario["url"], max_retries=1
                )  # Limited retries for testing

                duration = time.time() - start_time

                # Check for new screenshots
                current_screenshot_count = (
                    len(list(screenshots_dir.glob("*.png")))
                    if screenshots_dir.exists()
                    else 0
                )
                new_screenshots = current_screenshot_count - initial_screenshot_count

                if result["success"]:
                    print(f"   Result: ✅ SUCCESS ({duration:.1f}s)")
                    if scenario["expected_outcome"] == "success":
                        print("   Expected: ✅ Matches expectation")
                    else:
                        print("   Expected: ⚠️ Unexpected success")
                else:
                    print(f"   Result: ❌ FAILED ({duration:.1f}s)")
                    print(f"   Error: {result['error'][:100]}...")

                    if new_screenshots > 0:
                        print(f"   Screenshot: ✅ Captured ({new_screenshots} new)")

                        # Find the most recent screenshot
                        if screenshots_dir.exists():
                            screenshots = sorted(
                                screenshots_dir.glob("*.png"),
                                key=os.path.getmtime,
                                reverse=True,
                            )
                            if screenshots:
                                latest_screenshot = screenshots[0]
                                print(f"   Latest: {latest_screenshot.name}")
                    else:
                        print("   Screenshot: ❌ Not captured")

                results.append(
                    {
                        "scenario": scenario["name"],
                        "url": scenario["url"],
                        "success": result["success"],
                        "duration": duration,
                        "error": result.get("error"),
                        "screenshots_captured": new_screenshots > 0,
                        "operation_id": result.get("operation_id"),
                    }
                )

                # Update screenshot count for next iteration
                initial_screenshot_count = current_screenshot_count

        except Exception as e:
            print(f"   Exception: ❌ {str(e)}")
            results.append(
                {
                    "scenario": scenario["name"],
                    "url": scenario["url"],
                    "success": False,
                    "error": str(e),
                    "exception": True,
                }
            )

    return results


def analyze_screenshot_system():
    """Analyze the screenshot debugging system"""
    print("\n📊 Screenshot System Analysis")
    print("=" * 40)

    screenshots_dir = Path("reports/screenshots")

    if not screenshots_dir.exists():
        print("No screenshots directory found")
        return

    # Analyze screenshot files
    screenshots = list(screenshots_dir.glob("*.png"))
    html_files = list(screenshots_dir.glob("*.html"))

    print(f"Total Screenshots: {len(screenshots)}")
    print(f"Total HTML Files: {len(html_files)}")

    if screenshots:
        # Show recent screenshots
        recent_screenshots = sorted(screenshots, key=os.path.getmtime, reverse=True)[:5]

        print("\nRecent Screenshots:")
        for screenshot in recent_screenshots:
            mtime = time.ctime(os.path.getmtime(screenshot))
            size_kb = os.path.getsize(screenshot) / 1024
            print(f"  - {screenshot.name} ({size_kb:.1f}KB, {mtime})")

        # Analyze file naming patterns
        failure_screenshots = [s for s in screenshots if "failure_" in s.name]
        print(f"\nFailure Screenshots: {len(failure_screenshots)}")

        # Check for accompanying HTML files
        screenshots_with_html = 0
        for screenshot in screenshots:
            html_file = screenshot.with_suffix(".html")
            if html_file.exists():
                screenshots_with_html += 1

        print(f"Screenshots with HTML: {screenshots_with_html}/{len(screenshots)}")

    # Disk usage analysis
    if screenshots_dir.exists():
        total_size = sum(
            f.stat().st_size for f in screenshots_dir.glob("*") if f.is_file()
        )
        print(f"\nTotal Storage Used: {total_size / (1024 * 1024):.1f} MB")

        if total_size > 100 * 1024 * 1024:  # 100MB
            print("⚠️ Storage usage high - consider cleanup")


def test_screenshot_quality():
    """Test screenshot quality and content capture"""
    print("\n🎯 Testing Screenshot Quality")
    print("=" * 40)

    test_url = "https://example.com"  # Simple, reliable test site

    try:
        with IntelBotDriver(
            headless=False
        ) as driver:  # Use headed mode for quality test
            print(f"Loading test page: {test_url}")

            result = driver.get(test_url)

            if result["success"]:
                # Manually trigger a screenshot for quality testing
                screenshots_dir = Path("reports/screenshots")
                test_screenshot = screenshots_dir / "quality_test.png"

                try:
                    driver.driver.save_screenshot(str(test_screenshot))

                    if test_screenshot.exists():
                        size_kb = os.path.getsize(test_screenshot) / 1024
                        print(f"✅ Quality test screenshot saved: {size_kb:.1f}KB")

                        # Basic quality checks
                        if size_kb > 50:  # Reasonable size for a screenshot
                            print("✅ Screenshot size adequate")
                        else:
                            print("⚠️ Screenshot size may be too small")

                    else:
                        print("❌ Screenshot file not created")

                except Exception as e:
                    print(f"❌ Screenshot capture failed: {e}")
            else:
                print(f"❌ Test page load failed: {result['error']}")

    except Exception as e:
        print(f"❌ Quality test failed: {e}")


def main():
    """Main test function"""
    print("🧪 Screenshot-on-Detection Debugging Test Suite")
    print("=" * 60)

    # Test 1: Screenshot debugging functionality
    test_results = test_screenshot_debugging()

    # Test 2: Analyze screenshot system
    analyze_screenshot_system()

    # Test 3: Test screenshot quality
    test_screenshot_quality()

    # Summary
    print("\n✅ Screenshot Debugging Test Complete")
    print("=" * 60)

    successful_tests = len([r for r in test_results if r.get("success")])
    failed_tests = len([r for r in test_results if not r.get("success")])
    screenshots_captured = len(
        [r for r in test_results if r.get("screenshots_captured")]
    )

    print("Test Results:")
    print(f"  Successful Operations: {successful_tests}")
    print(f"  Failed Operations: {failed_tests}")
    print(f"  Screenshots Captured: {screenshots_captured}")

    # Validate screenshot debugging functionality
    if failed_tests > 0 and screenshots_captured > 0:
        print("✅ Screenshot debugging working correctly")
    elif failed_tests > 0 and screenshots_captured == 0:
        print("⚠️ Screenshot debugging may not be working")
    else:
        print("ℹ️ No failures occurred to test screenshot debugging")

    print("\n💡 Screenshot System Features:")
    print("  - Automatic capture on page load failures")
    print("  - Automatic capture on detection events")
    print("  - HTML source code saved alongside screenshots")
    print("  - Unique filenames with operation IDs")
    print("  - Configurable storage location")


if __name__ == "__main__":
    main()
