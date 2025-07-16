#!/usr/bin/env python3
"""
Failure Mode Tracker for IntelForge Phase 3
Operational intelligence system for stealth scraping reliability
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

try:
    import polars as pl

    POLARS_AVAILABLE = True
except ImportError:
    import pandas as pd

    POLARS_AVAILABLE = False


class FailureModeTracker:
    """Tracks and analyzes failure patterns in stealth scraping operations"""

    def __init__(self, reports_dir: Path = None):
        self.reports_dir = reports_dir or Path("reports/failure_tracking")
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.tracker_file = self.reports_dir / "failure_mode_tracker.csv"
        self.daily_summary_file = self.reports_dir / "daily_failure_summary.json"
        self.mitigation_effectiveness_file = (
            self.reports_dir / "mitigation_effectiveness.json"
        )

        # Initialize CSV if it doesn't exist
        if not self.tracker_file.exists():
            self._initialize_tracker_csv()

    def _initialize_tracker_csv(self):
        """Initialize the failure tracking CSV with headers"""
        headers = [
            "Date",
            "Time",
            "Site",
            "Failure_Mode",
            "Frequency",
            "Total_Attempts",
            "Mitigation_Applied",
            "Success_After_Mitigation",
            "Recovery_Time_Seconds",
            "Notes",
            "Stealth_Score",
            "Performance_Impact",
        ]

        with open(self.tracker_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def log_failure(
        self,
        site: str,
        failure_mode: str,
        frequency: int,
        total_attempts: int,
        mitigation_applied: str = None,
        success_after_mitigation: int = 0,
        recovery_time_seconds: float = 0,
        notes: str = "",
        stealth_score: Optional[float] = None,
        performance_impact: str = "Unknown",
    ):
        """Log a failure incident to the tracking system"""

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")

        row = [
            date_str,
            time_str,
            site,
            failure_mode,
            frequency,
            total_attempts,
            mitigation_applied or "None",
            success_after_mitigation,
            recovery_time_seconds,
            notes,
            stealth_score or "N/A",
            performance_impact,
        ]

        with open(self.tracker_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        logging.info(
            f"Logged failure: {failure_mode} on {site} ({frequency}/{total_attempts})"
        )

    def generate_daily_summary(self) -> Dict:
        """Generate daily failure summary statistics"""
        if not self.tracker_file.exists():
            return {"error": "No tracking data available"}

        if POLARS_AVAILABLE:
            # Use polars for 30x faster data processing
            df = pl.read_csv(self.tracker_file)
            today = datetime.now().strftime("%Y-%m-%d")
            today_data = df.filter(pl.col("Date") == today)

            if today_data.is_empty():
                is_empty = True
            else:
                is_empty = False
        else:
            # Fallback to pandas
            df = pd.read_csv(self.tracker_file)
            today = datetime.now().strftime("%Y-%m-%d")
            today_data = df[df["Date"] == today]
            is_empty = today_data.empty

        if is_empty:
            summary = {
                "date": today,
                "total_incidents": 0,
                "sites_affected": 0,
                "overall_success_rate": 100.0,
                "top_failure_modes": [],
                "mitigation_effectiveness": {},
            }
        else:
            # Calculate summary statistics
            total_incidents = len(today_data)
            sites_affected = today_data["Site"].nunique()

            # Calculate overall success rate
            total_attempts = today_data["Total_Attempts"].sum()
            total_failures = today_data["Frequency"].sum()
            overall_success_rate = (
                ((total_attempts - total_failures) / total_attempts * 100)
                if total_attempts > 0
                else 100.0
            )

            # Top failure modes
            failure_mode_counts = today_data["Failure_Mode"].value_counts().head(5)
            top_failure_modes = [
                {"mode": mode, "count": count}
                for mode, count in failure_mode_counts.items()
            ]

            # Mitigation effectiveness
            mitigation_data = today_data.groupby("Mitigation_Applied").agg(
                {"Success_After_Mitigation": "sum", "Frequency": "sum"}
            )

            mitigation_effectiveness = {}
            for mitigation, data in mitigation_data.iterrows():
                if mitigation != "None" and data["Frequency"] > 0:
                    effectiveness = (
                        data["Success_After_Mitigation"] / data["Frequency"]
                    ) * 100
                    mitigation_effectiveness[mitigation] = round(effectiveness, 1)

            summary = {
                "date": today,
                "total_incidents": total_incidents,
                "sites_affected": sites_affected,
                "overall_success_rate": round(overall_success_rate, 1),
                "top_failure_modes": top_failure_modes,
                "mitigation_effectiveness": mitigation_effectiveness,
            }

        # Save to file
        with open(self.daily_summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return summary

    def analyze_mitigation_effectiveness(self) -> Dict:
        """Analyze effectiveness of different mitigation strategies"""
        if not self.tracker_file.exists():
            return {"error": "No tracking data available"}

        df = pd.read_csv(self.tracker_file)

        # Group by mitigation strategy
        mitigation_analysis = (
            df.groupby("Mitigation_Applied")
            .agg(
                {
                    "Frequency": "sum",
                    "Success_After_Mitigation": "sum",
                    "Recovery_Time_Seconds": "mean",
                }
            )
            .round(2)
        )

        effectiveness = {}
        for mitigation, data in mitigation_analysis.iterrows():
            if mitigation != "None" and data["Frequency"] > 0:
                success_rate = (
                    data["Success_After_Mitigation"] / data["Frequency"]
                ) * 100
                effectiveness[mitigation] = {
                    "success_rate": round(success_rate, 1),
                    "avg_recovery_time": data["Recovery_Time_Seconds"],
                    "total_applications": int(data["Frequency"]),
                }

        # Save to file
        with open(self.mitigation_effectiveness_file, "w") as f:
            json.dump(effectiveness, f, indent=2)

        return effectiveness

    def get_failure_patterns(self, days: int = 7) -> Dict:
        """Identify patterns in failure modes over specified days"""
        if not self.tracker_file.exists():
            return {"error": "No tracking data available"}

        df = pd.read_csv(self.tracker_file)

        # Filter to recent days
        df["Date"] = pd.to_datetime(df["Date"])
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        recent_data = df[df["Date"] >= cutoff_date]

        patterns = {
            "site_reliability": {},
            "failure_mode_trends": {},
            "time_patterns": {},
            "stealth_score_correlation": {},
        }

        # Site reliability analysis
        site_stats = recent_data.groupby("Site").agg(
            {"Frequency": "sum", "Total_Attempts": "sum"}
        )

        for site, stats in site_stats.iterrows():
            if stats["Total_Attempts"] > 0:
                failure_rate = (stats["Frequency"] / stats["Total_Attempts"]) * 100
                patterns["site_reliability"][site] = round(failure_rate, 1)

        # Failure mode trends
        failure_trends = (
            recent_data.groupby("Failure_Mode")["Frequency"]
            .sum()
            .sort_values(ascending=False)
        )
        patterns["failure_mode_trends"] = failure_trends.to_dict()

        # Time pattern analysis (by hour)
        recent_data["Hour"] = pd.to_datetime(recent_data["Time"]).dt.hour
        time_patterns = recent_data.groupby("Hour")["Frequency"].sum()
        patterns["time_patterns"] = time_patterns.to_dict()

        return patterns

    def export_dashboard_data(self) -> str:
        """Export data for HTML dashboard generation"""
        daily_summary = self.generate_daily_summary()
        mitigation_effectiveness = self.analyze_mitigation_effectiveness()
        failure_patterns = self.get_failure_patterns()

        dashboard_data = {
            "generated_at": datetime.now().isoformat(),
            "daily_summary": daily_summary,
            "mitigation_effectiveness": mitigation_effectiveness,
            "failure_patterns": failure_patterns,
        }

        dashboard_file = self.reports_dir / "dashboard_data.json"
        with open(dashboard_file, "w") as f:
            json.dump(dashboard_data, f, indent=2)

        return str(dashboard_file)


# Usage example and CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IntelForge Failure Mode Tracker")
    parser.add_argument("--log", action="store_true", help="Log a failure incident")
    parser.add_argument("--site", help="Site where failure occurred")
    parser.add_argument("--failure-mode", help="Type of failure")
    parser.add_argument("--frequency", type=int, help="Number of failures")
    parser.add_argument("--total-attempts", type=int, help="Total attempts")
    parser.add_argument("--mitigation", help="Mitigation strategy applied")
    parser.add_argument(
        "--success-after", type=int, default=0, help="Successes after mitigation"
    )
    parser.add_argument("--notes", default="", help="Additional notes")

    parser.add_argument("--summary", action="store_true", help="Generate daily summary")
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze mitigation effectiveness"
    )
    parser.add_argument("--patterns", action="store_true", help="Show failure patterns")
    parser.add_argument(
        "--dashboard", action="store_true", help="Export dashboard data"
    )

    args = parser.parse_args()

    tracker = FailureModeTracker()

    if args.log:
        if not all([args.site, args.failure_mode, args.frequency, args.total_attempts]):
            print(
                "Error: --site, --failure-mode, --frequency, and --total-attempts are required for logging"
            )
            exit(1)

        tracker.log_failure(
            site=args.site,
            failure_mode=args.failure_mode,
            frequency=args.frequency,
            total_attempts=args.total_attempts,
            mitigation_applied=args.mitigation,
            success_after_mitigation=args.success_after,
            notes=args.notes,
        )
        print(f"Logged failure: {args.failure_mode} on {args.site}")

    elif args.summary:
        summary = tracker.generate_daily_summary()
        print(json.dumps(summary, indent=2))

    elif args.analyze:
        effectiveness = tracker.analyze_mitigation_effectiveness()
        print(json.dumps(effectiveness, indent=2))

    elif args.patterns:
        patterns = tracker.get_failure_patterns()
        print(json.dumps(patterns, indent=2))

    elif args.dashboard:
        dashboard_file = tracker.export_dashboard_data()
        print(f"Dashboard data exported to: {dashboard_file}")

    else:
        print("Use --help for usage information")
        print("\nExample usage:")
        print(
            "  python failure_mode_tracker.py --log --site Finviz --failure-mode Botasaurus_Load_Hang --frequency 3 --total-attempts 10 --mitigation Driver_Restart_Logic --success-after 7"
        )
        print("  python failure_mode_tracker.py --summary")
        print("  python failure_mode_tracker.py --dashboard")
