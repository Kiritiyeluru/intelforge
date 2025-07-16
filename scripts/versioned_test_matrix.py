#!/usr/bin/env python3
"""
Versioned Test Matrix with Optional Sacred Integration
Tracks anti-detection regression across browser and framework versions with optional
experiment tracking via Sacred for advanced analytics.
"""

import csv
import importlib.util
import logging
import platform
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VersionedTestMatrix:
    """
    Test matrix tracking for anti-detection regression with optional Sacred integration.

    Maintains CSV-based tracking (lightweight, git-trackable) with optional Sacred
    experiment logging for rich analytics and visualization.
    """

    def __init__(
        self,
        use_sacred: bool = False,
        sacred_experiment_name: str = "stealth_regression",
    ):
        self.csv_file = Path("reports/anti_detection_matrix.csv")
        self.csv_file.parent.mkdir(parents=True, exist_ok=True)
        self.use_sacred = use_sacred
        self.sacred_experiment = None

        # Initialize Sacred if requested and available
        if self.use_sacred:
            try:
                sacred_spec = importlib.util.find_spec("sacred")
                if sacred_spec is not None:
                    from sacred import Experiment

                    self.sacred_experiment = Experiment(sacred_experiment_name)
                    logger.info(
                        f"Sacred experiment '{sacred_experiment_name}' initialized"
                    )
                else:
                    logger.warning(
                        "Sacred not installed, falling back to CSV-only tracking"
                    )
                    self.use_sacred = False
            except Exception as e:
                logger.warning(f"Failed to initialize Sacred: {e}, using CSV-only")
                self.use_sacred = False

        # Initialize CSV file if it doesn't exist
        self._initialize_csv()

    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist"""
        if not self.csv_file.exists():
            headers = [
                "Date",
                "Time",
                "Chrome_Version",
                "Botasaurus_Version",
                "Target",
                "Stealth_Pass_Percent",
                "Avg_TTR",
                "Budget_Exceeded_Count",
                "Success_Rate",
                "Detection_Rate",
                "Notes",
            ]
            with open(self.csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
            logger.info(f"Initialized test matrix CSV: {self.csv_file}")

    def _get_chrome_version(self) -> str:
        """Detect Chrome version from system"""
        try:
            if platform.system() == "Linux":
                result = subprocess.run(
                    ["google-chrome", "--version"], capture_output=True, text=True
                )
                if result.returncode == 0:
                    return result.stdout.strip().split()[-1]
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    [
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                        "--version",
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    return result.stdout.strip().split()[-1]
            elif platform.system() == "Windows":
                # Windows Chrome version detection
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon"
                )
                version, _ = winreg.QueryValueEx(key, "version")
                return version
        except Exception as e:
            logger.warning(f"Could not detect Chrome version: {e}")

        return "unknown"

    def _get_botasaurus_version(self) -> str:
        """Detect Botasaurus version from installed package"""
        try:
            import botasaurus

            return getattr(botasaurus, "__version__", "unknown")
        except ImportError:
            logger.warning("Botasaurus not installed")
            return "not_installed"
        except Exception as e:
            logger.warning(f"Could not detect Botasaurus version: {e}")
            return "unknown"

    def log_test_result(
        self,
        target: str,
        stealth_pass_percent: float,
        avg_ttr: float,
        budget_exceeded_count: int,
        success_rate: float = 0.0,
        detection_rate: float = 0.0,
        notes: str = "",
        chrome_version: Optional[str] = None,
        botasaurus_version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log test result to CSV and optionally to Sacred experiment

        Args:
            target: Site or service being tested
            stealth_pass_percent: Percentage of stealth checks passed
            avg_ttr: Average time-to-recovery in seconds
            budget_exceeded_count: Number of retry budget violations
            success_rate: Overall success rate (0.0-1.0)
            detection_rate: Bot detection rate (0.0-1.0)
            notes: Additional notes about the test
            chrome_version: Override auto-detected Chrome version
            botasaurus_version: Override auto-detected Botasaurus version

        Returns:
            Dict containing logged data
        """

        # Collect version info
        chrome_ver = chrome_version or self._get_chrome_version()
        botasaurus_ver = botasaurus_version or self._get_botasaurus_version()

        # Prepare data
        now = datetime.now()
        data = {
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
            "Chrome_Version": chrome_ver,
            "Botasaurus_Version": botasaurus_ver,
            "Target": target,
            "Stealth_Pass_Percent": f"{stealth_pass_percent:.1f}%",
            "Avg_TTR": f"{avg_ttr:.1f}",
            "Budget_Exceeded_Count": str(budget_exceeded_count),
            "Success_Rate": f"{success_rate:.1%}",
            "Detection_Rate": f"{detection_rate:.1%}",
            "Notes": notes,
        }

        # Log to CSV (always)
        self._log_to_csv(data)

        # Log to Sacred (optional)
        if self.use_sacred and self.sacred_experiment:
            self._log_to_sacred(
                data,
                stealth_pass_percent,
                avg_ttr,
                budget_exceeded_count,
                success_rate,
                detection_rate,
            )

        logger.info(
            f"Logged test result: {target} - {stealth_pass_percent:.1f}% stealth, "
            f"{avg_ttr:.1f}s TTR, {budget_exceeded_count} budget exceeded"
        )

        return data

    def _log_to_csv(self, data: Dict[str, Any]) -> None:
        """Log data to CSV file"""
        with open(self.csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    data["Date"],
                    data["Time"],
                    data["Chrome_Version"],
                    data["Botasaurus_Version"],
                    data["Target"],
                    data["Stealth_Pass_Percent"],
                    data["Avg_TTR"],
                    data["Budget_Exceeded_Count"],
                    data["Success_Rate"],
                    data["Detection_Rate"],
                    data["Notes"],
                ]
            )

    def _log_to_sacred(
        self,
        data: Dict[str, Any],
        stealth_pass_percent: float,
        avg_ttr: float,
        budget_exceeded_count: int,
        success_rate: float,
        detection_rate: float,
    ) -> None:
        """Log data to Sacred experiment"""
        try:
            with self.sacred_experiment.run() as run:
                # Log configuration
                run.config.update(
                    {
                        "chrome_version": data["Chrome_Version"],
                        "botasaurus_version": data["Botasaurus_Version"],
                        "target": data["Target"],
                        "notes": data["Notes"],
                    }
                )

                # Log metrics
                run.log_scalar("stealth_pass_percent", stealth_pass_percent)
                run.log_scalar("avg_ttr_seconds", avg_ttr)
                run.log_scalar("budget_exceeded_count", budget_exceeded_count)
                run.log_scalar("success_rate", success_rate)
                run.log_scalar("detection_rate", detection_rate)

                # Log derived metrics
                run.log_scalar("stealth_score", stealth_pass_percent / 100.0)
                run.log_scalar(
                    "performance_score", max(0, 1 - (avg_ttr / 60.0))
                )  # Normalize TTR
                run.log_scalar("reliability_score", success_rate)

                logger.info(f"Sacred experiment logged: run_id={run._id}")

        except Exception as e:
            logger.error(f"Failed to log to Sacred: {e}")

    def get_regression_analysis(
        self, target: Optional[str] = None, days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze regression trends from CSV data

        Args:
            target: Specific target to analyze (None for all)
            days_back: Number of days of history to analyze

        Returns:
            Regression analysis results
        """

        if not self.csv_file.exists():
            return {"error": "No test data available"}

        # Read CSV data
        results = []
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date - timedelta(days=days_back)

        with open(self.csv_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row_date = datetime.strptime(
                        f"{row['Date']} {row['Time']}", "%Y-%m-%d %H:%M:%S"
                    )
                    if row_date >= cutoff_date:
                        if target is None or row["Target"] == target:
                            results.append(row)
                except ValueError:
                    continue  # Skip malformed dates

        if not results:
            return {"error": "No recent data found"}

        # Analyze trends
        analysis = {
            "total_tests": len(results),
            "date_range": f"{cutoff_date.date()} to {datetime.now().date()}",
            "targets_tested": list(set(r["Target"] for r in results)),
            "avg_stealth_score": self._calculate_avg_metric(
                results, "Stealth_Pass_Percent"
            ),
            "avg_ttr": self._calculate_avg_metric(results, "Avg_TTR"),
            "total_budget_exceeded": sum(
                int(r.get("Budget_Exceeded_Count", 0)) for r in results
            ),
            "version_changes": self._detect_version_changes(results),
            "trend_analysis": self._calculate_trends(results),
        }

        return analysis

    def _calculate_avg_metric(self, results: List[Dict], metric_key: str) -> float:
        """Calculate average of a metric, handling percentage strings"""
        values = []
        for result in results:
            try:
                value_str = result.get(metric_key, "0")
                # Handle percentage strings
                if "%" in value_str:
                    value = float(value_str.replace("%", ""))
                else:
                    value = float(value_str)
                values.append(value)
            except (ValueError, TypeError):
                continue

        return sum(values) / len(values) if values else 0.0

    def _detect_version_changes(self, results: List[Dict]) -> Dict[str, Any]:
        """Detect version changes in the dataset"""
        chrome_versions = set(r["Chrome_Version"] for r in results)
        botasaurus_versions = set(r["Botasaurus_Version"] for r in results)

        return {
            "chrome_versions": list(chrome_versions),
            "botasaurus_versions": list(botasaurus_versions),
            "version_stability": {
                "chrome_stable": len(chrome_versions) == 1,
                "botasaurus_stable": len(botasaurus_versions) == 1,
            },
        }

    def _calculate_trends(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate performance trends over time"""
        if len(results) < 2:
            return {"insufficient_data": True}

        # Sort by date
        sorted_results = sorted(results, key=lambda x: f"{x['Date']} {x['Time']}")

        # Calculate first half vs second half metrics
        mid_point = len(sorted_results) // 2
        first_half = sorted_results[:mid_point] if mid_point > 0 else sorted_results
        second_half = sorted_results[mid_point:] if mid_point > 0 else sorted_results

        first_stealth = self._calculate_avg_metric(first_half, "Stealth_Pass_Percent")
        second_stealth = self._calculate_avg_metric(second_half, "Stealth_Pass_Percent")

        first_ttr = self._calculate_avg_metric(first_half, "Avg_TTR")
        second_ttr = self._calculate_avg_metric(second_half, "Avg_TTR")

        return {
            "stealth_trend": (
                "improving" if second_stealth > first_stealth else "declining"
            ),
            "stealth_change": round(second_stealth - first_stealth, 1),
            "ttr_trend": "improving" if second_ttr < first_ttr else "declining",
            "ttr_change": round(second_ttr - first_ttr, 1),
            "overall_assessment": self._assess_overall_trend(
                second_stealth, first_stealth, second_ttr, first_ttr
            ),
        }

    def _assess_overall_trend(
        self, new_stealth: float, old_stealth: float, new_ttr: float, old_ttr: float
    ) -> str:
        """Assess overall performance trend"""
        stealth_improving = new_stealth > old_stealth
        ttr_improving = new_ttr < old_ttr

        if stealth_improving and ttr_improving:
            return "excellent"
        elif stealth_improving or ttr_improving:
            return "good"
        elif abs(new_stealth - old_stealth) < 5 and abs(new_ttr - old_ttr) < 5:
            return "stable"
        else:
            return "concerning"

    def export_analysis_report(
        self, target: Optional[str] = None, output_file: Optional[str] = None
    ) -> str:
        """Export comprehensive analysis report"""
        analysis = self.get_regression_analysis(target=target)

        if "error" in analysis:
            return f"Analysis failed: {analysis['error']}"

        # Generate report
        report_lines = [
            "# Anti-Detection Test Matrix Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- Total Tests: {analysis['total_tests']}",
            f"- Date Range: {analysis['date_range']}",
            f"- Targets: {', '.join(analysis['targets_tested'])}",
            "",
            "## Performance Metrics",
            f"- Average Stealth Score: {analysis['avg_stealth_score']:.1f}%",
            f"- Average TTR: {analysis['avg_ttr']:.1f}s",
            f"- Total Budget Exceeded: {analysis['total_budget_exceeded']}",
            "",
            "## Version Stability",
        ]

        version_changes = analysis["version_changes"]
        report_lines.extend(
            [
                f"- Chrome Versions: {', '.join(version_changes['chrome_versions'])}",
                f"- Botasaurus Versions: {', '.join(version_changes['botasaurus_versions'])}",
                f"- Chrome Stable: {version_changes['version_stability']['chrome_stable']}",
                f"- Botasaurus Stable: {version_changes['version_stability']['botasaurus_stable']}",
                "",
            ]
        )

        if "insufficient_data" not in analysis["trend_analysis"]:
            trends = analysis["trend_analysis"]
            report_lines.extend(
                [
                    "## Trend Analysis",
                    f"- Stealth Trend: {trends['stealth_trend']} ({trends['stealth_change']:+.1f}%)",
                    f"- TTR Trend: {trends['ttr_trend']} ({trends['ttr_change']:+.1f}s)",
                    f"- Overall Assessment: {trends['overall_assessment'].upper()}",
                    "",
                ]
            )

        report_content = "\n".join(report_lines)

        # Save to file if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as f:
                f.write(report_content)
            logger.info(f"Analysis report saved to: {output_path}")

        return report_content


def main():
    """CLI interface for test matrix logging and analysis"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Versioned Test Matrix with Sacred Integration"
    )
    parser.add_argument("--log", action="store_true", help="Log a test result")
    parser.add_argument(
        "--analyze", action="store_true", help="Run regression analysis"
    )
    parser.add_argument("--target", type=str, help="Target site/service")
    parser.add_argument("--stealth-score", type=float, help="Stealth pass percentage")
    parser.add_argument("--ttr", type=float, help="Average TTR in seconds")
    parser.add_argument(
        "--budget-exceeded", type=int, default=0, help="Budget exceeded count"
    )
    parser.add_argument(
        "--success-rate", type=float, default=0.0, help="Success rate (0.0-1.0)"
    )
    parser.add_argument(
        "--detection-rate", type=float, default=0.0, help="Detection rate (0.0-1.0)"
    )
    parser.add_argument("--notes", type=str, default="", help="Additional notes")
    parser.add_argument(
        "--use-sacred", action="store_true", help="Enable Sacred experiment tracking"
    )
    parser.add_argument("--report", type=str, help="Export analysis report to file")

    args = parser.parse_args()

    # Initialize matrix
    matrix = VersionedTestMatrix(use_sacred=args.use_sacred)

    if args.log:
        if not args.target or args.stealth_score is None or args.ttr is None:
            print(
                "Error: --target, --stealth-score, and --ttr are required for logging"
            )
            return

        result = matrix.log_test_result(
            target=args.target,
            stealth_pass_percent=args.stealth_score,
            avg_ttr=args.ttr,
            budget_exceeded_count=args.budget_exceeded,
            success_rate=args.success_rate,
            detection_rate=args.detection_rate,
            notes=args.notes,
        )

        print("✅ Test result logged:")
        print(f"   Target: {result['Target']}")
        print(f"   Stealth: {result['Stealth_Pass_Percent']}")
        print(f"   TTR: {result['Avg_TTR']}s")
        print(f"   Budget Exceeded: {result['Budget_Exceeded_Count']}")

    elif args.analyze:
        analysis = matrix.get_regression_analysis(target=args.target)

        if "error" in analysis:
            print(f"❌ Analysis failed: {analysis['error']}")
            return

        print("\n📊 Regression Analysis Results:")
        print(f"   Tests: {analysis['total_tests']} over {analysis['date_range']}")
        print(f"   Avg Stealth: {analysis['avg_stealth_score']:.1f}%")
        print(f"   Avg TTR: {analysis['avg_ttr']:.1f}s")
        print(f"   Budget Exceeded: {analysis['total_budget_exceeded']}")

        if "insufficient_data" not in analysis["trend_analysis"]:
            trends = analysis["trend_analysis"]
            print(f"   Trend: {trends['overall_assessment'].upper()}")

        # Export report if requested
        if args.report:
            matrix.export_analysis_report(target=args.target, output_file=args.report)
            print(f"   Report exported to: {args.report}")

    else:
        print("Use --log to log test results or --analyze to run analysis")
        print(
            "Example: python versioned_test_matrix.py --log --target finviz --stealth-score 85.5 --ttr 12.3"
        )


if __name__ == "__main__":
    main()
