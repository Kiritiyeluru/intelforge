#!/usr/bin/env python3
"""
Budget Overrun Auto-Notifier for IntelForge
Tracks development time and budget across testing phases.
Part of Part 3B System Hardening implementation.
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BudgetStatus(Enum):
    """Budget status indicators."""

    UNDER_BUDGET = "under_budget"
    ON_TRACK = "on_track"
    WARNING = "warning"
    OVER_BUDGET = "over_budget"
    CRITICAL = "critical"


@dataclass
class BudgetEntry:
    """Individual budget tracking entry."""

    timestamp: str
    phase: str
    task: str
    hours_spent: float
    hours_remaining: float
    description: str
    status: str = "in_progress"


@dataclass
class PhaseBudget:
    """Budget allocation for a testing phase."""

    name: str
    allocated_hours: float
    spent_hours: float
    remaining_hours: float
    tasks: List[str]
    status: BudgetStatus
    completion_percentage: float
    estimated_completion: Optional[str] = None


class BudgetTracker:
    """Track development budget and provide overrun notifications."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.budget_file = project_root / "tests" / "BUDGET_TRACKER.json"
        self.budget_md_file = project_root / "tests" / "BUDGET_TRACKER.md"

        # Initialize phase budgets based on CURRENT_IMPLEMENTATION_PLAN.md
        self.phase_budgets = {
            "Part_1_1_Outcome_Verification": {
                "allocated": 10.0,
                "description": "Silent failure detection, Claude integrity, vector health, system health contract",
                "tasks": [
                    "fail_fast_validator",
                    "claude_integrity_validator",
                    "vector_health_validator",
                    "health_contract",
                ],
                "priority": "critical",
                "status": "completed",
            },
            "Part_1_2_Security_Baseline": {
                "allocated": 6.0,
                "description": "Lightweight security testing, graceful shutdown, output sanitization",
                "tasks": ["security_baseline", "graceful_shutdown", "output_sanitizer"],
                "priority": "critical",
                "status": "completed",
            },
            "Part_1_3_CLI_Core_Testing": {
                "allocated": 8.0,
                "description": "CLI regression testing, end-to-end workflows, error handling",
                "tasks": ["cli_regression", "workflow_tests", "error_handling"],
                "priority": "critical",
                "status": "completed",
            },
            "Part_1_4_Observability": {
                "allocated": 4.0,
                "description": "Structured logging, TTR tracker, performance monitoring",
                "tasks": ["structured_logger", "ttr_tracker", "performance_monitor"],
                "priority": "critical",
                "status": "completed",
            },
            "Part_2_1_Snapshot_Drift": {
                "allocated": 10.0,
                "description": "Tolerance configuration, snapshot drift validator, enhanced reports",
                "tasks": [
                    "tolerance_config",
                    "snapshot_drift_validator",
                    "drift_reports",
                ],
                "priority": "high",
                "status": "completed",
            },
            "Part_2_2_Performance_Benchmarking": {
                "allocated": 6.0,
                "description": "CLI performance, baseline configuration, regression framework",
                "tasks": [
                    "cli_performance",
                    "performance_baseline",
                    "regression_framework",
                ],
                "priority": "high",
                "status": "completed",
            },
            "Part_2_3_Enhanced_Module_Testing": {
                "allocated": 4.0,
                "description": "ML component validation, embedding stability, academic tools",
                "tasks": [
                    "ml_validation",
                    "embedding_stability",
                    "academic_integration",
                ],
                "priority": "high",
                "status": "completed",
            },
            "Part_3A_Persona_Functionality": {
                "allocated": 8.0,
                "description": "Researcher, trader, developer scenarios, E2E workflows",
                "tasks": [
                    "researcher_persona",
                    "trader_persona",
                    "developer_persona",
                    "e2e_workflows",
                ],
                "priority": "high",
                "status": "completed",
            },
            "Part_3B_System_Hardening": {
                "allocated": 6.0,
                "description": "k6 load testing, test tagging, coverage analysis, budget tracking",
                "tasks": [
                    "k6_load_testing",
                    "test_tagging",
                    "coverage_analysis",
                    "budget_tracking",
                ],
                "priority": "medium",
                "status": "in_progress",
            },
            "Part_3C_CI_Production_Polish": {
                "allocated": 4.0,
                "description": "GitHub Actions matrix, CI pipeline automation",
                "tasks": ["github_actions", "ci_automation"],
                "priority": "low",
                "status": "pending",
            },
        }

        # Load existing budget data
        self.budget_data = self.load_budget_data()

    def load_budget_data(self) -> Dict:
        """Load existing budget tracking data."""
        if self.budget_file.exists():
            try:
                with open(self.budget_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        # Initialize with default structure
        return {
            "project_start": datetime.now().isoformat(),
            "total_allocated_hours": sum(
                phase["allocated"] for phase in self.phase_budgets.values()
            ),
            "total_spent_hours": 0.0,
            "phases": {},
            "entries": [],
            "alerts": [],
            "last_updated": datetime.now().isoformat(),
        }

    def save_budget_data(self):
        """Save budget data to JSON file."""
        self.budget_data["last_updated"] = datetime.now().isoformat()

        with open(self.budget_file, "w") as f:
            json.dump(self.budget_data, f, indent=2)

    def add_time_entry(self, phase: str, task: str, hours: float, description: str):
        """Add a time tracking entry."""
        entry = BudgetEntry(
            timestamp=datetime.now().isoformat(),
            phase=phase,
            task=task,
            hours_spent=hours,
            hours_remaining=self.get_remaining_hours(phase) - hours,
            description=description,
        )

        self.budget_data["entries"].append(asdict(entry))
        self.budget_data["total_spent_hours"] += hours

        # Update phase tracking
        if phase not in self.budget_data["phases"]:
            self.budget_data["phases"][phase] = {
                "spent_hours": 0.0,
                "tasks_completed": [],
                "status": "in_progress",
            }

        self.budget_data["phases"][phase]["spent_hours"] += hours
        if task not in self.budget_data["phases"][phase]["tasks_completed"]:
            self.budget_data["phases"][phase]["tasks_completed"].append(task)

        # Check for budget alerts
        self.check_budget_alerts(phase)
        self.save_budget_data()

    def get_remaining_hours(self, phase: str) -> float:
        """Get remaining hours for a phase."""
        allocated = self.phase_budgets.get(phase, {}).get("allocated", 0.0)
        spent = self.budget_data["phases"].get(phase, {}).get("spent_hours", 0.0)
        return max(0.0, allocated - spent)

    def get_phase_status(self, phase: str) -> BudgetStatus:
        """Determine budget status for a phase."""
        if phase not in self.phase_budgets:
            return BudgetStatus.CRITICAL

        allocated = self.phase_budgets[phase]["allocated"]
        spent = self.budget_data["phases"].get(phase, {}).get("spent_hours", 0.0)

        if spent == 0:
            return BudgetStatus.UNDER_BUDGET

        utilization = spent / allocated

        if utilization <= 0.8:
            return BudgetStatus.UNDER_BUDGET
        elif utilization <= 0.95:
            return BudgetStatus.ON_TRACK
        elif utilization <= 1.05:
            return BudgetStatus.WARNING
        elif utilization <= 1.2:
            return BudgetStatus.OVER_BUDGET
        else:
            return BudgetStatus.CRITICAL

    def check_budget_alerts(self, phase: str):
        """Check for budget overrun alerts."""
        status = self.get_phase_status(phase)
        allocated = self.phase_budgets.get(phase, {}).get("allocated", 0.0)
        spent = self.budget_data["phases"].get(phase, {}).get("spent_hours", 0.0)

        alert_conditions = [
            (BudgetStatus.WARNING, 0.95, "approaching budget limit"),
            (BudgetStatus.OVER_BUDGET, 1.0, "exceeded allocated budget"),
            (BudgetStatus.CRITICAL, 1.2, "critical budget overrun"),
        ]

        for alert_status, threshold, message in alert_conditions:
            if status == alert_status and spent >= allocated * threshold:
                alert = {
                    "timestamp": datetime.now().isoformat(),
                    "phase": phase,
                    "status": status.value,
                    "message": message,
                    "allocated_hours": allocated,
                    "spent_hours": spent,
                    "overrun_hours": max(0.0, spent - allocated),
                    "utilization_percent": (
                        (spent / allocated * 100) if allocated > 0 else 0
                    ),
                }

                # Only add if not already alerted for this condition
                existing_alerts = [
                    a
                    for a in self.budget_data["alerts"]
                    if a["phase"] == phase and a["status"] == status.value
                ]
                if not existing_alerts:
                    self.budget_data["alerts"].append(alert)
                    print(f"🚨 BUDGET ALERT: {phase} - {message}")
                    print(
                        f"   Spent: {spent:.1f}h / Allocated: {allocated:.1f}h ({spent/allocated*100:.1f}%)"
                    )

    def get_overall_budget_status(self) -> Tuple[BudgetStatus, Dict]:
        """Get overall project budget status."""
        total_allocated = self.budget_data["total_allocated_hours"]
        total_spent = self.budget_data["total_spent_hours"]

        if total_spent == 0:
            utilization = 0.0
            status = BudgetStatus.UNDER_BUDGET
        else:
            utilization = total_spent / total_allocated

            if utilization <= 0.8:
                status = BudgetStatus.UNDER_BUDGET
            elif utilization <= 0.95:
                status = BudgetStatus.ON_TRACK
            elif utilization <= 1.05:
                status = BudgetStatus.WARNING
            elif utilization <= 1.2:
                status = BudgetStatus.OVER_BUDGET
            else:
                status = BudgetStatus.CRITICAL

        summary = {
            "status": status,
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "remaining": max(0.0, total_allocated - total_spent),
            "utilization_percent": utilization * 100,
            "phases_completed": len(
                [
                    p
                    for p in self.phase_budgets.values()
                    if p.get("status") == "completed"
                ]
            ),
            "phases_total": len(self.phase_budgets),
            "alerts_count": len(self.budget_data["alerts"]),
        }

        return status, summary

    def generate_budget_report(self) -> str:
        """Generate comprehensive budget report."""
        status, summary = self.get_overall_budget_status()

        # Status indicators
        status_indicators = {
            BudgetStatus.UNDER_BUDGET: "🟢",
            BudgetStatus.ON_TRACK: "🟡",
            BudgetStatus.WARNING: "🟠",
            BudgetStatus.OVER_BUDGET: "🔴",
            BudgetStatus.CRITICAL: "💥",
        }

        report = []
        report.append("💰 IntelForge Budget Tracking Report")
        report.append("=====================================")
        report.append(
            f"Overall Status: {status.value.title()} {status_indicators[status]}"
        )
        report.append(f"Total Budget: {summary['total_allocated']:.1f} hours")
        report.append(
            f"Spent: {summary['total_spent']:.1f} hours ({summary['utilization_percent']:.1f}%)"
        )
        report.append(f"Remaining: {summary['remaining']:.1f} hours")
        report.append(
            f"Phases Completed: {summary['phases_completed']}/{summary['phases_total']}"
        )

        if summary["alerts_count"] > 0:
            report.append(f"🚨 Active Alerts: {summary['alerts_count']}")

        report.append("")

        # Phase breakdown
        report.append("📋 Phase Budget Breakdown")
        report.append("-------------------------")

        for phase_key, phase_config in self.phase_budgets.items():
            phase_data = self.budget_data["phases"].get(phase_key, {})
            allocated = phase_config["allocated"]
            spent = phase_data.get("spent_hours", 0.0)
            status = self.get_phase_status(phase_key)
            status_icon = status_indicators.get(status, "❓")

            utilization = (spent / allocated * 100) if allocated > 0 else 0
            remaining = max(0.0, allocated - spent)

            report.append(
                f"{phase_key:>30}: {spent:>5.1f}h / {allocated:>5.1f}h "
                f"({utilization:>5.1f}%) {status_icon}"
            )

            if status in [
                BudgetStatus.WARNING,
                BudgetStatus.OVER_BUDGET,
                BudgetStatus.CRITICAL,
            ]:
                overrun = max(0.0, spent - allocated)
                if overrun > 0:
                    report.append(f"{'':>30}  ⚠️  Overrun: {overrun:.1f}h")

        report.append("")

        # Recent alerts
        if self.budget_data["alerts"]:
            report.append("🚨 Recent Budget Alerts")
            report.append("-----------------------")
            recent_alerts = sorted(
                self.budget_data["alerts"], key=lambda x: x["timestamp"], reverse=True
            )[:5]

            for alert in recent_alerts:
                timestamp = datetime.fromisoformat(alert["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M"
                )
                report.append(f"{timestamp} - {alert['phase']}: {alert['message']}")
                report.append(
                    f"{'':>20} Utilization: {alert['utilization_percent']:.1f}%"
                )

        report.append("")

        # Budget recommendations
        report.append("💡 Budget Recommendations")
        report.append("-------------------------")

        if status == BudgetStatus.CRITICAL:
            report.append("🔴 CRITICAL: Immediate budget review required")
            report.append("   - Consider scope reduction or timeline extension")
            report.append("   - Prioritize critical path items only")
        elif status == BudgetStatus.OVER_BUDGET:
            report.append("🟠 WARNING: Budget exceeded, monitor closely")
            report.append("   - Focus on high-priority remaining tasks")
            report.append("   - Consider deferring optional features")
        elif status == BudgetStatus.ON_TRACK:
            report.append("🟡 ON TRACK: Continue current pace")
            report.append("   - Monitor phase completion rates")
            report.append("   - Maintain current velocity")
        else:
            report.append("🟢 UNDER BUDGET: Opportunity for additional features")
            report.append("   - Consider advancing optional Phase 3C tasks")
            report.append("   - Maintain quality standards")

        report.append("")
        report.append(
            f"📊 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        return "\n".join(report)

    def budget_check(self, warn_threshold: float = 95.0) -> bool:
        """Check if budget is approaching or exceeding threshold."""
        _, summary = self.get_overall_budget_status()

        if summary["utilization_percent"] >= warn_threshold:
            print(
                f"⚠️  Budget warning: {summary['utilization_percent']:.1f}% of budget used"
            )
            print(
                f"   Spent: {summary['total_spent']:.1f}h / Allocated: {summary['total_allocated']:.1f}h"
            )

            # Show phases over budget
            over_budget_phases = []
            for phase_key in self.phase_budgets:
                status = self.get_phase_status(phase_key)
                if status in [
                    BudgetStatus.WARNING,
                    BudgetStatus.OVER_BUDGET,
                    BudgetStatus.CRITICAL,
                ]:
                    over_budget_phases.append(phase_key)

            if over_budget_phases:
                print(f"   Phases over budget: {', '.join(over_budget_phases)}")

            return False  # Budget warning triggered

        return True  # Budget OK

    def generate_markdown_report(self):
        """Generate markdown budget report file."""
        report = self.generate_budget_report()

        # Convert to markdown format
        md_report = (
            report.replace("=", "-")
            .replace("💰", "##")
            .replace("📋", "###")
            .replace("🚨", "###")
            .replace("💡", "###")
        )

        with open(self.budget_md_file, "w") as f:
            f.write(md_report)

        print(f"📄 Markdown report saved: {self.budget_md_file}")


def main():
    """Main entry point for budget tracking."""
    import argparse

    parser = argparse.ArgumentParser(description="IntelForge Budget Tracker")
    parser.add_argument(
        "--add-time",
        nargs=4,
        metavar=("PHASE", "TASK", "HOURS", "DESCRIPTION"),
        help="Add time entry: phase task hours description",
    )
    parser.add_argument("--report", action="store_true", help="Generate budget report")
    parser.add_argument("--check", action="store_true", help="Check budget status")
    parser.add_argument(
        "--warn-if-over",
        type=float,
        default=95.0,
        help="Warn if budget utilization exceeds percentage (default: 95)",
    )
    parser.add_argument(
        "--markdown", action="store_true", help="Generate markdown report"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    tracker = BudgetTracker(project_root)

    if args.add_time:
        phase, task, hours_str, description = args.add_time
        try:
            hours = float(hours_str)
            tracker.add_time_entry(phase, task, hours, description)
            print(f"✅ Added {hours}h to {phase}/{task}")
        except ValueError:
            print(f"❌ Invalid hours value: {hours_str}")
            return 1

    if args.check:
        budget_ok = tracker.budget_check(args.warn_if_over)
        return 0 if budget_ok else 1

    if args.report:
        report = tracker.generate_budget_report()
        print(report)

    if args.markdown:
        tracker.generate_markdown_report()

    if not any([args.add_time, args.report, args.check, args.markdown]):
        # Default: show brief status
        _, summary = tracker.get_overall_budget_status()
        print(
            f"Budget Status: {summary['utilization_percent']:.1f}% "
            f"({summary['total_spent']:.1f}h / {summary['total_allocated']:.1f}h)"
        )

    return 0


if __name__ == "__main__":
    exit(main())
