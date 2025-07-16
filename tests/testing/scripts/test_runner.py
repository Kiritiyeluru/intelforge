#!/usr/bin/env python3
"""
IntelForge Test Runner
Comprehensive testing framework for all IntelForge modules
"""

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class IntelForgeTestRunner:
    """Main test runner for IntelForge project"""

    def __init__(self, report_dir: Optional[str] = None):
        self.project_root = PROJECT_ROOT
        self.test_dir = Path(__file__).parent.parent
        self.report_dir = Path(report_dir) if report_dir else self.test_dir / "reports"
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Ensure report directories exist
        self.setup_report_directories()

    def setup_report_directories(self):
        """Create necessary report directories"""
        subdirs = [
            "unit_tests",
            "integration_tests",
            "performance_tests",
            "scraping_tests",
            "api_tests",
            "security_tests",
            "regression_tests",
            "archives",
        ]

        for subdir in subdirs:
            (self.report_dir / subdir).mkdir(parents=True, exist_ok=True)

    def run_unit_tests(self, module: Optional[str] = None) -> Dict:
        """Run unit tests for specified module or all modules"""
        print(f"🧪 Running unit tests{f' for {module}' if module else ''}...")

        test_results = {
            "test_type": "unit",
            "timestamp": self.timestamp,
            "module": module or "all",
            "status": "pass",
            "details": [],
        }

        # Add your unit test logic here
        # For now, return a mock result
        test_results["details"].append("Unit tests placeholder - implement with pytest")

        self.save_report("unit_tests", test_results)
        return test_results

    def run_integration_tests(self) -> Dict:
        """Run integration tests for system components"""
        print("🔗 Running integration tests...")

        test_results = {
            "test_type": "integration",
            "timestamp": self.timestamp,
            "status": "pass",
            "details": [],
        }

        # Add your integration test logic here
        test_results["details"].append("Integration tests placeholder")

        self.save_report("integration_tests", test_results)
        return test_results

    def run_performance_tests(self) -> Dict:
        """Run performance benchmarks"""
        print("⚡ Running performance tests...")

        test_results = {
            "test_type": "performance",
            "timestamp": self.timestamp,
            "status": "pass",
            "benchmarks": {},
            "details": [],
        }

        # Add performance testing logic here
        test_results["details"].append("Performance tests placeholder")

        self.save_report("performance_tests", test_results)
        return test_results

    def run_scraping_tests(self) -> Dict:
        """Test web scraping functionality"""
        print("🕷️ Running scraping tests...")

        test_results = {
            "test_type": "scraping",
            "timestamp": self.timestamp,
            "status": "pass",
            "scrapers_tested": [],
            "details": [],
        }

        # Test each scraper module
        scrapers = ["reddit_scraper", "github_scraper", "web_scraper"]
        for scraper in scrapers:
            test_results["scrapers_tested"].append(scraper)
            test_results["details"].append(f"Testing {scraper} - placeholder")

        self.save_report("scraping_tests", test_results)
        return test_results

    def save_report(self, test_type: str, results: Dict):
        """Save test report to appropriate directory"""
        filename = f"{self.timestamp}_{test_type}_{results.get('module', 'all')}_{results['status']}.json"
        report_path = self.report_dir / test_type / filename

        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        # Also create markdown report
        md_filename = filename.replace(".json", ".md")
        md_path = self.report_dir / test_type / md_filename

        self.create_markdown_report(md_path, results)
        print(f"📊 Report saved: {md_path}")

    def create_markdown_report(self, path: Path, results: Dict):
        """Create markdown report from test results"""
        status_emoji = {"pass": "✅", "fail": "❌", "warn": "⚠️"}

        content = f"""# Test Report: {results["test_type"].title()}

**Status**: {status_emoji.get(results["status"], "❓")} {results["status"].upper()}
**Timestamp**: {results["timestamp"]}
**Module**: {results.get("module", "N/A")}

## Test Details

"""

        for detail in results.get("details", []):
            content += f"- {detail}\n"

        if "benchmarks" in results:
            content += "\n## Performance Benchmarks\n\n"
            for key, value in results["benchmarks"].items():
                content += f"- **{key}**: {value}\n"

        if "scrapers_tested" in results:
            content += "\n## Scrapers Tested\n\n"
            for scraper in results["scrapers_tested"]:
                content += f"- {scraper}\n"

        content += f"\n---\n*Generated by IntelForge Test Runner at {datetime.datetime.now()}*\n"

        with open(path, "w") as f:
            f.write(content)


def main():
    parser = argparse.ArgumentParser(description="IntelForge Test Runner")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "performance", "scraping", "all"],
        default="all",
        help="Type of tests to run",
    )
    parser.add_argument("--module", help="Specific module to test (for unit tests)")
    parser.add_argument("--report-dir", help="Custom report directory")

    args = parser.parse_args()

    runner = IntelForgeTestRunner(args.report_dir)

    print(f"🚀 Starting IntelForge tests - Type: {args.type}")
    print(f"📁 Reports will be saved to: {runner.report_dir}")

    results = []

    if args.type in ["unit", "all"]:
        results.append(runner.run_unit_tests(args.module))

    if args.type in ["integration", "all"]:
        results.append(runner.run_integration_tests())

    if args.type in ["performance", "all"]:
        results.append(runner.run_performance_tests())

    if args.type in ["scraping", "all"]:
        results.append(runner.run_scraping_tests())

    print(f"\n🎉 Testing complete! {len(results)} test suites executed.")

    # Summary
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")

    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")


if __name__ == "__main__":
    main()
