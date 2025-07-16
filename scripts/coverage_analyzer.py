#!/usr/bin/env python3
"""
Coverage Analysis Tool for IntelForge
Provides comprehensive coverage analysis with meaningful thresholds.
Part of Part 3B System Hardening implementation.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class CoverageThreshold:
    """Coverage threshold configuration."""

    minimum: float = 70.0
    warning: float = 80.0
    good: float = 90.0
    excellent: float = 95.0


@dataclass
class ModuleCoverage:
    """Coverage data for a single module."""

    name: str
    lines_total: int
    lines_covered: int
    branches_total: int
    branches_covered: int
    coverage_percent: float
    missing_lines: List[int]


class CoverageAnalyzer:
    """Analyze test coverage with comprehensive reporting."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.reports_dir = project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

        # Coverage thresholds by module type
        self.thresholds = {
            "critical": CoverageThreshold(85.0, 90.0, 95.0, 98.0),
            "core": CoverageThreshold(80.0, 85.0, 90.0, 95.0),
            "utils": CoverageThreshold(75.0, 80.0, 85.0, 90.0),
            "scrapers": CoverageThreshold(70.0, 75.0, 80.0, 85.0),
            "default": CoverageThreshold(70.0, 80.0, 90.0, 95.0),
        }

        # Module categorization
        self.module_categories = {
            "critical": ["cli.py", "health", "validation", "security"],
            "core": ["semantic_crawler", "canary_validation", "structured_logger"],
            "utils": ["output_sanitizer", "graceful_shutdown", "performance_monitor"],
            "scrapers": ["reddit_scraper", "enhanced_reddit", "scrapy_integration"],
        }

    def get_module_category(self, module_name: str) -> str:
        """Determine the category of a module for threshold application."""
        for category, keywords in self.module_categories.items():
            if any(keyword in module_name.lower() for keyword in keywords):
                return category
        return "default"

    def run_coverage_analysis(
        self, test_markers: List[str] = None, exclude_markers: List[str] = None
    ) -> Dict:
        """Run comprehensive coverage analysis."""

        print("📊 Running coverage analysis...")

        # Build pytest command with coverage
        cmd = [
            "python",
            "-m",
            "pytest",
            "--cov=scripts",
            "--cov=scrapers",
            "--cov-report=term-missing",
            "--cov-report=html:reports/coverage_html",
            "--cov-report=xml:reports/coverage.xml",
            "--cov-report=json:reports/coverage.json",
            "--cov-branch",
            "--cov-fail-under=1",
            "tests/",
            "-v",
            "--tb=short",
        ]

        # Add marker selection if specified
        if test_markers:
            marker_expr = " or ".join(test_markers)
            if exclude_markers:
                exclude_expr = " and not " + " and not ".join(exclude_markers)
                marker_expr = f"({marker_expr}){exclude_expr}"
            cmd.extend(["-m", marker_expr])

        # Exclude slow tests for faster coverage analysis
        if not test_markers:
            cmd.extend(["-m", "not slow and not load"])

        print(f"   Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
            )

            success = result.returncode == 0

            # Parse coverage results
            coverage_data = self.parse_coverage_json()
            analysis = self.analyze_coverage_data(coverage_data)

            return {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "coverage_data": coverage_data,
                "analysis": analysis,
                "command": " ".join(cmd),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": 124,
                "stdout": "",
                "stderr": "Coverage analysis timed out after 600s",
                "coverage_data": None,
                "analysis": None,
                "command": " ".join(cmd),
            }

        except Exception as e:
            return {
                "success": False,
                "returncode": 1,
                "stdout": "",
                "stderr": str(e),
                "coverage_data": None,
                "analysis": None,
                "command": " ".join(cmd),
            }

    def parse_coverage_json(self) -> Optional[Dict]:
        """Parse JSON coverage report."""
        json_file = self.reports_dir / "coverage.json"

        if not json_file.exists():
            print(f"   ⚠️  Coverage JSON not found: {json_file}")
            return None

        try:
            with open(json_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"   ❌ Error parsing coverage JSON: {e}")
            return None

    def analyze_coverage_data(self, coverage_data: Optional[Dict]) -> Optional[Dict]:
        """Analyze coverage data and generate insights."""
        if not coverage_data:
            return None

        files = coverage_data.get("files", {})
        totals = coverage_data.get("totals", {})

        # Overall metrics
        overall_percent = totals.get("percent_covered", 0.0)
        lines_total = totals.get("num_statements", 0)
        lines_covered = totals.get("covered_lines", 0)
        branches_total = totals.get("num_branches", 0)
        branches_covered = totals.get("covered_branches", 0)

        # Module analysis
        modules = []
        for file_path, file_data in files.items():
            module = ModuleCoverage(
                name=file_path,
                lines_total=file_data.get("summary", {}).get("num_statements", 0),
                lines_covered=file_data.get("summary", {}).get("covered_lines", 0),
                branches_total=file_data.get("summary", {}).get("num_branches", 0),
                branches_covered=file_data.get("summary", {}).get(
                    "covered_branches", 0
                ),
                coverage_percent=file_data.get("summary", {}).get(
                    "percent_covered", 0.0
                ),
                missing_lines=file_data.get("missing_lines", []),
            )
            modules.append(module)

        # Sort by coverage percentage
        modules.sort(key=lambda m: m.coverage_percent)

        # Categorize modules
        category_analysis = {}
        for module in modules:
            category = self.get_module_category(module.name)
            if category not in category_analysis:
                category_analysis[category] = {
                    "modules": [],
                    "avg_coverage": 0.0,
                    "threshold": self.thresholds[category],
                    "status": "unknown",
                }
            category_analysis[category]["modules"].append(module)

        # Calculate category averages and status
        for category, data in category_analysis.items():
            if data["modules"]:
                avg_coverage = sum(m.coverage_percent for m in data["modules"]) / len(
                    data["modules"]
                )
                data["avg_coverage"] = avg_coverage

                threshold = data["threshold"]
                if avg_coverage >= threshold.excellent:
                    data["status"] = "excellent"
                elif avg_coverage >= threshold.good:
                    data["status"] = "good"
                elif avg_coverage >= threshold.warning:
                    data["status"] = "warning"
                elif avg_coverage >= threshold.minimum:
                    data["status"] = "acceptable"
                else:
                    data["status"] = "critical"

        return {
            "overall": {
                "percent": overall_percent,
                "lines_total": lines_total,
                "lines_covered": lines_covered,
                "branches_total": branches_total,
                "branches_covered": branches_covered,
                "status": self.get_overall_status(overall_percent),
            },
            "modules": modules,
            "categories": category_analysis,
            "low_coverage_modules": [m for m in modules if m.coverage_percent < 70],
            "high_coverage_modules": [m for m in modules if m.coverage_percent >= 90],
        }

    def get_overall_status(self, coverage_percent: float) -> str:
        """Determine overall coverage status."""
        default_threshold = self.thresholds["default"]

        if coverage_percent >= default_threshold.excellent:
            return "excellent"
        elif coverage_percent >= default_threshold.good:
            return "good"
        elif coverage_percent >= default_threshold.warning:
            return "warning"
        elif coverage_percent >= default_threshold.minimum:
            return "acceptable"
        else:
            return "critical"

    def generate_coverage_report(self, analysis_result: Dict) -> str:
        """Generate comprehensive coverage report."""
        if not analysis_result["success"] or not analysis_result["analysis"]:
            return "❌ Coverage analysis failed or no data available"

        analysis = analysis_result["analysis"]
        overall = analysis["overall"]

        # Status indicators
        status_indicators = {
            "excellent": "🟢",
            "good": "🟡",
            "warning": "🟠",
            "acceptable": "🔵",
            "critical": "🔴",
        }

        report = []
        report.append("📊 Coverage Analysis Report")
        report.append("==========================")
        report.append(
            f"Overall Coverage: {overall['percent']:.1f}% {status_indicators.get(overall['status'], '❓')}"
        )
        report.append(f"Lines: {overall['lines_covered']}/{overall['lines_total']}")
        report.append(
            f"Branches: {overall['branches_covered']}/{overall['branches_total']}"
        )
        report.append("")

        # Category breakdown
        report.append("📋 Coverage by Category")
        report.append("-----------------------")
        for category, data in analysis["categories"].items():
            status_icon = status_indicators.get(data["status"], "❓")
            threshold = data["threshold"]
            module_count = len(data["modules"])

            report.append(
                f"{category.title():>10}: {data['avg_coverage']:>5.1f}% {status_icon} "
                f"({module_count} modules, target: {threshold.minimum:.0f}%+)"
            )

        report.append("")

        # Low coverage modules (need attention)
        if analysis["low_coverage_modules"]:
            report.append("🔴 Low Coverage Modules (< 70%)")
            report.append("-------------------------------")
            for module in analysis["low_coverage_modules"][:10]:  # Top 10
                missing_count = len(module.missing_lines)
                report.append(
                    f"{module.name:>30}: {module.coverage_percent:>5.1f}% "
                    f"({missing_count} missing lines)"
                )

        # High coverage modules (good examples)
        if analysis["high_coverage_modules"]:
            report.append("")
            report.append("🟢 High Coverage Modules (≥ 90%)")
            report.append("--------------------------------")
            for module in analysis["high_coverage_modules"][-5:]:  # Top 5
                report.append(f"{module.name:>30}: {module.coverage_percent:>5.1f}%")

        report.append("")
        report.append("📁 Detailed Reports")
        report.append("-------------------")
        report.append(f"HTML Report: {self.reports_dir}/coverage_html/index.html")
        report.append(f"JSON Report: {self.reports_dir}/coverage.json")
        report.append(f"XML Report:  {self.reports_dir}/coverage.xml")

        return "\n".join(report)

    def quick_coverage_check(self) -> Dict:
        """Run quick coverage check with fast tests only."""
        print("⚡ Running quick coverage check...")
        return self.run_coverage_analysis(
            test_markers=["quick", "regression"],
            exclude_markers=["slow", "load", "persona"],
        )

    def full_coverage_analysis(self) -> Dict:
        """Run comprehensive coverage analysis."""
        print("🎯 Running full coverage analysis...")
        return self.run_coverage_analysis(
            exclude_markers=["load"]  # Exclude only load tests
        )


def main():
    """Main entry point for coverage analysis."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze test coverage for IntelForge")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick coverage check with fast tests only",
    )
    parser.add_argument("--markers", nargs="+", help="Test markers to include")
    parser.add_argument("--exclude", nargs="+", help="Test markers to exclude")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Generate report from existing coverage data",
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    analyzer = CoverageAnalyzer(project_root)

    if args.report_only:
        # Generate report from existing data
        coverage_data = analyzer.parse_coverage_json()
        if not coverage_data:
            print("❌ No existing coverage data found")
            return 1

        analysis = analyzer.analyze_coverage_data(coverage_data)
        result = {
            "success": True,
            "analysis": analysis,
            "coverage_data": coverage_data,
        }
    elif args.quick:
        result = analyzer.quick_coverage_check()
    elif args.markers or args.exclude:
        result = analyzer.run_coverage_analysis(
            test_markers=args.markers, exclude_markers=args.exclude
        )
    else:
        result = analyzer.full_coverage_analysis()

    # Generate and print report
    report = analyzer.generate_coverage_report(result)
    print(report)

    # Return appropriate exit code
    if result["success"] and result.get("analysis"):
        overall_status = result["analysis"]["overall"]["status"]
        return 0 if overall_status in ["excellent", "good", "acceptable"] else 1
    else:
        return 1


if __name__ == "__main__":
    exit(main())
