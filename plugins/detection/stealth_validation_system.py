#!/usr/bin/env python3
"""
Phase 3 Stealth Validation System
Automated CreepJS and Pixelscan validation for anti-detection effectiveness
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path

import undetected_chromedriver as uc
from botasaurus_driver import Driver
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StealthValidator:
    """Automated stealth validation system"""

    def __init__(self):
        self.results_dir = Path("reports/stealth_validation")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def test_creepjs_score(self, driver_type: str, driver_instance=None):
        """Test CreepJS fingerprinting score"""
        logger.info(f"Testing CreepJS score for {driver_type}")

        try:
            if driver_type == "playwright":
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=False)
                    context = await browser.new_context()
                    page = await context.new_page()

                    await page.goto("https://abrahamjuliot.github.io/creepjs/")
                    await page.wait_for_timeout(10000)  # Wait for analysis

                    # Extract score from page
                    score_element = await page.query_selector("[data-score]")
                    score = (
                        await score_element.get_attribute("data-score")
                        if score_element
                        else "N/A"
                    )

                    await browser.close()

            elif driver_type == "undetected_chrome":
                # Use provided driver or create new one
                if driver_instance:
                    driver = driver_instance
                    close_after = False
                else:
                    driver = uc.Chrome(headless=False)
                    close_after = True

                try:
                    driver.get("https://abrahamjuliot.github.io/creepjs/")
                    time.sleep(10)  # Wait for analysis

                    # Extract score
                    score_element = driver.find_element("css selector", "[data-score]")
                    score = (
                        score_element.get_attribute("data-score")
                        if score_element
                        else "N/A"
                    )

                finally:
                    if close_after:
                        driver.quit()

            elif driver_type == "botasaurus":
                if driver_instance:
                    driver = driver_instance
                    close_after = False
                else:
                    driver = Driver()
                    close_after = True

                try:
                    driver.get("https://abrahamjuliot.github.io/creepjs/")
                    time.sleep(10)  # Wait for analysis

                    # Extract score
                    score_element = driver.find_element_by_css_selector("[data-score]")
                    score = (
                        score_element.get_attribute("data-score")
                        if score_element
                        else "N/A"
                    )

                finally:
                    if close_after:
                        driver.quit()

            return {
                "driver_type": driver_type,
                "score": score,
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "url": "https://abrahamjuliot.github.io/creepjs/",
            }

        except Exception as e:
            logger.error(f"CreepJS test failed for {driver_type}: {e}")
            return {
                "driver_type": driver_type,
                "score": "ERROR",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
            }

    def test_pixelscan_detection(self, driver_type: str):
        """Test Pixelscan fingerprint detection"""
        logger.info(f"Testing Pixelscan detection for {driver_type}")

        try:
            # Pixelscan API endpoint (if available) or web interface
            # This is a placeholder - actual implementation would depend on Pixelscan API
            result = {
                "driver_type": driver_type,
                "fingerprint_detected": "PLACEHOLDER",
                "timestamp": datetime.now().isoformat(),
                "status": "pending_implementation",
                "note": "Pixelscan integration requires API access or manual testing",
            }

            return result

        except Exception as e:
            logger.error(f"Pixelscan test failed for {driver_type}: {e}")
            return {
                "driver_type": driver_type,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "status": "failed",
            }

    def test_basic_detection_sites(self, driver_type: str):
        """Test against basic bot detection sites"""
        test_sites = [
            "https://bot.sannysoft.com/",
            "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html",
            "https://arh.antoinevastel.com/bots/areyouheadless",
        ]

        results = []

        for site in test_sites:
            try:
                logger.info(f"Testing {driver_type} against {site}")

                if driver_type == "undetected_chrome":
                    driver = uc.Chrome(headless=True)
                    driver.get(site)
                    time.sleep(3)

                    # Take screenshot for manual review
                    screenshot_path = (
                        self.results_dir
                        / f"{driver_type}_{site.replace('/', '_').replace(':', '')}.png"
                    )
                    driver.save_screenshot(str(screenshot_path))

                    page_source = driver.page_source
                    driver.quit()

                    # Simple detection checks
                    detected = any(
                        keyword in page_source.lower()
                        for keyword in [
                            "bot",
                            "automated",
                            "webdriver",
                            "selenium",
                            "headless",
                        ]
                    )

                elif driver_type == "botasaurus":
                    driver = Driver(headless=True)
                    driver.get(site)
                    time.sleep(3)

                    page_source = driver.page_source
                    driver.quit()

                    detected = any(
                        keyword in page_source.lower()
                        for keyword in [
                            "bot",
                            "automated",
                            "webdriver",
                            "selenium",
                            "headless",
                        ]
                    )

                results.append(
                    {
                        "site": site,
                        "driver_type": driver_type,
                        "detected": detected,
                        "timestamp": datetime.now().isoformat(),
                        "status": "success",
                    }
                )

            except Exception as e:
                logger.error(f"Detection test failed for {driver_type} on {site}: {e}")
                results.append(
                    {
                        "site": site,
                        "driver_type": driver_type,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                        "status": "failed",
                    }
                )

        return results

    async def run_comprehensive_validation(self):
        """Run comprehensive stealth validation across all frameworks"""
        logger.info("Starting comprehensive stealth validation")

        results = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "frameworks_tested": ["playwright", "undetected_chrome", "botasaurus"],
            "tests": {
                "creepjs_scores": [],
                "pixelscan_results": [],
                "detection_site_results": [],
            },
            "summary": {},
        }

        # Test CreepJS scores
        for framework in ["playwright", "undetected_chrome", "botasaurus"]:
            try:
                creepjs_result = await self.test_creepjs_score(framework)
                results["tests"]["creepjs_scores"].append(creepjs_result)
            except Exception as e:
                logger.error(f"CreepJS test failed for {framework}: {e}")

        # Test Pixelscan (placeholder)
        for framework in ["undetected_chrome", "botasaurus"]:
            pixelscan_result = self.test_pixelscan_detection(framework)
            results["tests"]["pixelscan_results"].append(pixelscan_result)

        # Test basic detection sites
        for framework in ["undetected_chrome", "botasaurus"]:
            detection_results = self.test_basic_detection_sites(framework)
            results["tests"]["detection_site_results"].extend(detection_results)

        # Generate summary
        results["summary"] = self.generate_summary(results)

        # Save results
        results_file = self.results_dir / f"stealth_validation_{self.session_id}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(
            f"Comprehensive validation complete. Results saved to {results_file}"
        )
        return results

    def generate_summary(self, results):
        """Generate validation summary"""
        summary = {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "framework_scores": {},
            "recommendations": [],
        }

        # Count tests
        for test_category in results["tests"].values():
            if isinstance(test_category, list):
                summary["total_tests"] += len(test_category)
                summary["successful_tests"] += len(
                    [t for t in test_category if t.get("status") == "success"]
                )
                summary["failed_tests"] += len(
                    [t for t in test_category if t.get("status") == "failed"]
                )

        # Analyze CreepJS scores
        for creepjs_result in results["tests"]["creepjs_scores"]:
            framework = creepjs_result["driver_type"]
            score = creepjs_result.get("score", "N/A")

            if score != "N/A" and score != "ERROR":
                try:
                    numeric_score = float(score.replace("%", ""))
                    summary["framework_scores"][framework] = {
                        "creepjs_score": numeric_score,
                        "grade": (
                            "EXCELLENT"
                            if numeric_score >= 70
                            else "GOOD" if numeric_score >= 50 else "NEEDS_IMPROVEMENT"
                        ),
                    }
                except:
                    summary["framework_scores"][framework] = {
                        "creepjs_score": "INVALID",
                        "grade": "UNKNOWN",
                    }

        # Generate recommendations
        if summary["framework_scores"]:
            best_framework = max(
                summary["framework_scores"].items(),
                key=lambda x: (
                    x[1].get("creepjs_score", 0)
                    if isinstance(x[1].get("creepjs_score"), (int, float))
                    else 0
                ),
            )
            summary["recommendations"].append(
                f"Best performing framework: {best_framework[0]} with score {best_framework[1].get('creepjs_score', 'N/A')}"
            )

        if summary["failed_tests"] > 0:
            summary["recommendations"].append(
                f"Review {summary['failed_tests']} failed tests for potential improvements"
            )

        return summary

    def generate_health_check_script(self):
        """Generate automated health check script"""
        script_content = """#!/usr/bin/env python3
# Automated Stealth Health Check
# Run this script regularly to monitor stealth effectiveness

import sys
import asyncio
from stealth_validation_system import StealthValidator

async def main():
    validator = StealthValidator()
    results = await validator.run_comprehensive_validation()

    # Check if any framework scores below 70%
    alert_threshold = 70.0
    alerts = []

    for framework, data in results["summary"]["framework_scores"].items():
        score = data.get("creepjs_score", 0)
        if isinstance(score, (int, float)) and score < alert_threshold:
            alerts.append(f"⚠️ {framework}: {score}% (below {alert_threshold}% threshold)")

    if alerts:
        print("🚨 STEALTH ALERTS:")
        for alert in alerts:
            print(f"  {alert}")
        sys.exit(1)
    else:
        print("✅ All frameworks above stealth threshold")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
"""

        health_check_file = Path("scripts/stealth_health_check.py")
        health_check_file.parent.mkdir(parents=True, exist_ok=True)

        with open(health_check_file, "w") as f:
            f.write(script_content)

        # Make executable
        health_check_file.chmod(0o755)

        logger.info(f"Health check script created: {health_check_file}")
        return health_check_file


async def main():
    """Main execution function"""
    validator = StealthValidator()

    print("🔍 Starting Phase 3 Stealth Validation System")
    print("=" * 50)

    # Run comprehensive validation
    results = await validator.run_comprehensive_validation()

    # Generate health check script
    health_check_script = validator.generate_health_check_script()

    # Display results
    print("\n📊 Validation Results:")
    print(f"   Session ID: {results['session_id']}")
    print(f"   Total Tests: {results['summary']['total_tests']}")
    print(f"   Successful: {results['summary']['successful_tests']}")
    print(f"   Failed: {results['summary']['failed_tests']}")

    print("\n🎯 Framework Scores:")
    for framework, data in results["summary"]["framework_scores"].items():
        score = data.get("creepjs_score", "N/A")
        grade = data.get("grade", "UNKNOWN")
        print(f"   {framework}: {score}% ({grade})")

    print("\n💡 Recommendations:")
    for rec in results["summary"]["recommendations"]:
        print(f"   • {rec}")

    print(f"\n📋 Health check script: {health_check_script}")
    print("   Run 'python scripts/stealth_health_check.py' for regular monitoring")

    print("\n✅ Stealth Validation System - OPERATIONAL")


if __name__ == "__main__":
    asyncio.run(main())
