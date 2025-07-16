#!/usr/bin/env python3
"""
Time-to-Recovery (TTR) tracker for IntelForge
Implements recovery time logging with CSV/Markdown export and incident tracking
"""

import csv
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class IncidentSeverity(Enum):
    """Incident severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status states"""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    RESOLVING = "resolving"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class Incident:
    """Data class for incident tracking"""

    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    component: str
    detection_time: datetime
    resolution_time: Optional[datetime] = None
    status: IncidentStatus = IncidentStatus.DETECTED
    recovery_actions: List[str] = None
    root_cause: Optional[str] = None
    prevention_measures: List[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.recovery_actions is None:
            self.recovery_actions = []
        if self.prevention_measures is None:
            self.prevention_measures = []
        if self.tags is None:
            self.tags = []

    @property
    def ttr_seconds(self) -> Optional[float]:
        """Calculate time-to-recovery in seconds"""
        if self.resolution_time and self.detection_time:
            return (self.resolution_time - self.detection_time).total_seconds()
        return None

    @property
    def ttr_minutes(self) -> Optional[float]:
        """Calculate time-to-recovery in minutes"""
        ttr = self.ttr_seconds
        return ttr / 60 if ttr is not None else None

    @property
    def is_resolved(self) -> bool:
        """Check if incident is resolved"""
        return self.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]


class TTRTracker:
    """
    Comprehensive Time-to-Recovery tracking system
    Manages incident lifecycle, recovery metrics, and reporting
    """

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path(__file__).parent.parent.parent / "logs" / "ttr"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.incidents_file = self.data_dir / "incidents.json"
        self.metrics_file = self.data_dir / "ttr_metrics.csv"
        self.logger = logging.getLogger(__name__)

        # In-memory incident storage
        self.active_incidents: Dict[str, Incident] = {}
        self.incident_history: List[Incident] = []

        # Load existing data
        self._load_incidents()

        # TTR targets by severity (in minutes)
        self.ttr_targets = {
            IncidentSeverity.CRITICAL: 15,  # 15 minutes
            IncidentSeverity.HIGH: 60,  # 1 hour
            IncidentSeverity.MEDIUM: 240,  # 4 hours
            IncidentSeverity.LOW: 1440,  # 24 hours
        }

    def create_incident(
        self,
        title: str,
        description: str,
        severity: Union[IncidentSeverity, str],
        component: str,
        tags: List[str] = None,
    ) -> str:
        """
        Create a new incident and start tracking

        Args:
            title: Incident title
            description: Detailed description
            severity: Incident severity level
            component: Affected component/system
            tags: Optional tags for categorization

        Returns:
            str: Generated incident ID
        """
        if isinstance(severity, str):
            severity = IncidentSeverity(severity.lower())

        incident_id = f"INC-{int(time.time())}-{component[:3].upper()}"

        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            component=component,
            detection_time=datetime.now(),
            tags=tags or [],
        )

        self.active_incidents[incident_id] = incident
        self._save_incidents()

        self.logger.info(
            f"Created incident {incident_id}: {title}",
            extra={
                "incident_id": incident_id,
                "severity": severity.value,
                "component": component,
            },
        )

        return incident_id

    def update_incident_status(
        self, incident_id: str, status: Union[IncidentStatus, str], notes: str = None
    ) -> bool:
        """
        Update incident status with optional notes

        Args:
            incident_id: Incident identifier
            status: New status
            notes: Optional status change notes

        Returns:
            bool: Success status
        """
        if isinstance(status, str):
            status = IncidentStatus(status.lower())

        incident = self.active_incidents.get(incident_id)
        if not incident:
            self.logger.error(f"Incident {incident_id} not found")
            return False

        old_status = incident.status
        incident.status = status

        # Auto-set resolution time when resolved
        if status == IncidentStatus.RESOLVED and not incident.resolution_time:
            incident.resolution_time = datetime.now()

        self._save_incidents()

        self.logger.info(
            f"Updated incident {incident_id} status: {old_status.value} -> {status.value}",
            extra={
                "incident_id": incident_id,
                "old_status": old_status.value,
                "new_status": status.value,
                "notes": notes,
            },
        )

        return True

    def add_recovery_action(
        self, incident_id: str, action: str, timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Add a recovery action to an incident

        Args:
            incident_id: Incident identifier
            action: Description of recovery action taken
            timestamp: Optional timestamp (defaults to now)

        Returns:
            bool: Success status
        """
        incident = self.active_incidents.get(incident_id)
        if not incident:
            self.logger.error(f"Incident {incident_id} not found")
            return False

        timestamp = timestamp or datetime.now()
        timestamped_action = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {action}"

        incident.recovery_actions.append(timestamped_action)
        self._save_incidents()

        self.logger.info(
            f"Added recovery action to {incident_id}: {action}",
            extra={"incident_id": incident_id, "action": action},
        )

        return True

    def resolve_incident(
        self,
        incident_id: str,
        root_cause: str = None,
        prevention_measures: List[str] = None,
    ) -> bool:
        """
        Resolve an incident with root cause and prevention measures

        Args:
            incident_id: Incident identifier
            root_cause: Root cause analysis
            prevention_measures: List of prevention measures

        Returns:
            bool: Success status
        """
        incident = self.active_incidents.get(incident_id)
        if not incident:
            self.logger.error(f"Incident {incident_id} not found")
            return False

        incident.status = IncidentStatus.RESOLVED
        incident.resolution_time = datetime.now()

        if root_cause:
            incident.root_cause = root_cause

        if prevention_measures:
            incident.prevention_measures.extend(prevention_measures)

        # Move to history
        self.incident_history.append(incident)
        del self.active_incidents[incident_id]

        self._save_incidents()
        self._save_ttr_metrics(incident)

        ttr = incident.ttr_minutes
        target = self.ttr_targets.get(incident.severity, 0)
        sla_met = ttr <= target if ttr else False

        self.logger.info(
            f"Resolved incident {incident_id} in {ttr:.1f} minutes (SLA: {sla_met})",
            extra={
                "incident_id": incident_id,
                "ttr_minutes": ttr,
                "sla_target_minutes": target,
                "sla_met": sla_met,
                "root_cause": root_cause,
            },
        )

        return True

    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident details by ID"""
        # Check active incidents first
        if incident_id in self.active_incidents:
            return self.active_incidents[incident_id]

        # Check history
        for incident in self.incident_history:
            if incident.incident_id == incident_id:
                return incident

        return None

    def get_active_incidents(self) -> List[Incident]:
        """Get all active incidents"""
        return list(self.active_incidents.values())

    def get_metrics_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Get TTR metrics summary for the specified period

        Args:
            days: Number of days to analyze

        Returns:
            dict: Metrics summary
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_incidents = [
            inc
            for inc in self.incident_history
            if inc.detection_time >= cutoff_date and inc.is_resolved
        ]

        if not recent_incidents:
            return {
                "period_days": days,
                "total_incidents": 0,
                "avg_ttr_minutes": 0,
                "sla_compliance_rate": 0,
                "by_severity": {},
                "by_component": {},
            }

        # Calculate overall metrics
        total_incidents = len(recent_incidents)
        avg_ttr = sum(inc.ttr_minutes for inc in recent_incidents) / total_incidents

        # SLA compliance
        sla_met_count = sum(
            1
            for inc in recent_incidents
            if inc.ttr_minutes <= self.ttr_targets.get(inc.severity, float("inf"))
        )
        sla_compliance_rate = (sla_met_count / total_incidents) * 100

        # By severity
        by_severity = {}
        for severity in IncidentSeverity:
            severity_incidents = [
                inc for inc in recent_incidents if inc.severity == severity
            ]
            if severity_incidents:
                by_severity[severity.value] = {
                    "count": len(severity_incidents),
                    "avg_ttr_minutes": sum(
                        inc.ttr_minutes for inc in severity_incidents
                    )
                    / len(severity_incidents),
                    "target_minutes": self.ttr_targets.get(severity, 0),
                    "sla_compliance_rate": (
                        sum(
                            1
                            for inc in severity_incidents
                            if inc.ttr_minutes
                            <= self.ttr_targets.get(severity, float("inf"))
                        )
                        / len(severity_incidents)
                    )
                    * 100,
                }

        # By component
        by_component = {}
        components = set(inc.component for inc in recent_incidents)
        for component in components:
            component_incidents = [
                inc for inc in recent_incidents if inc.component == component
            ]
            by_component[component] = {
                "count": len(component_incidents),
                "avg_ttr_minutes": sum(inc.ttr_minutes for inc in component_incidents)
                / len(component_incidents),
            }

        return {
            "period_days": days,
            "total_incidents": total_incidents,
            "avg_ttr_minutes": round(avg_ttr, 2),
            "sla_compliance_rate": round(sla_compliance_rate, 2),
            "by_severity": by_severity,
            "by_component": by_component,
        }

    def export_to_csv(self, filename: Optional[str] = None) -> Path:
        """
        Export incident data to CSV format

        Args:
            filename: Optional custom filename

        Returns:
            Path: Path to exported CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ttr_export_{timestamp}.csv"

        export_path = self.data_dir / filename

        all_incidents = list(self.active_incidents.values()) + self.incident_history

        with open(export_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "incident_id",
                "title",
                "description",
                "severity",
                "component",
                "detection_time",
                "resolution_time",
                "status",
                "ttr_minutes",
                "sla_target_minutes",
                "sla_met",
                "root_cause",
                "tags",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for incident in all_incidents:
                target = self.ttr_targets.get(incident.severity, 0)
                sla_met = (
                    (incident.ttr_minutes <= target) if incident.ttr_minutes else None
                )

                writer.writerow(
                    {
                        "incident_id": incident.incident_id,
                        "title": incident.title,
                        "description": incident.description,
                        "severity": incident.severity.value,
                        "component": incident.component,
                        "detection_time": incident.detection_time.isoformat(),
                        "resolution_time": (
                            incident.resolution_time.isoformat()
                            if incident.resolution_time
                            else ""
                        ),
                        "status": incident.status.value,
                        "ttr_minutes": incident.ttr_minutes,
                        "sla_target_minutes": target,
                        "sla_met": sla_met,
                        "root_cause": incident.root_cause or "",
                        "tags": ";".join(incident.tags),
                    }
                )

        self.logger.info(f"Exported {len(all_incidents)} incidents to {export_path}")
        return export_path

    def export_to_markdown(
        self, filename: Optional[str] = None, days: int = 30
    ) -> Path:
        """
        Export TTR report to Markdown format

        Args:
            filename: Optional custom filename
            days: Number of days to include in report

        Returns:
            Path: Path to exported Markdown file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ttr_report_{timestamp}.md"

        export_path = self.data_dir / filename

        metrics = self.get_metrics_summary(days)
        active_incidents = self.get_active_incidents()

        with open(export_path, "w", encoding="utf-8") as f:
            f.write("# Time-to-Recovery Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Period:** Last {days} days\n\n")

            # Summary metrics
            f.write("## Summary Metrics\n\n")
            f.write(f"- **Total Incidents:** {metrics['total_incidents']}\n")
            f.write(f"- **Average TTR:** {metrics['avg_ttr_minutes']:.1f} minutes\n")
            f.write(f"- **SLA Compliance:** {metrics['sla_compliance_rate']:.1f}%\n\n")

            # By severity
            if metrics["by_severity"]:
                f.write("## Metrics by Severity\n\n")
                f.write(
                    "| Severity | Count | Avg TTR (min) | Target (min) | SLA Compliance |\n"
                )
                f.write(
                    "|----------|-------|---------------|--------------|----------------|\n"
                )
                for severity, data in metrics["by_severity"].items():
                    f.write(
                        f"| {severity.title()} | {data['count']} | {data['avg_ttr_minutes']:.1f} | {data['target_minutes']} | {data['sla_compliance_rate']:.1f}% |\n"
                    )
                f.write("\n")

            # By component
            if metrics["by_component"]:
                f.write("## Metrics by Component\n\n")
                f.write("| Component | Count | Avg TTR (min) |\n")
                f.write("|-----------|-------|---------------|\n")
                for component, data in metrics["by_component"].items():
                    f.write(
                        f"| {component} | {data['count']} | {data['avg_ttr_minutes']:.1f} |\n"
                    )
                f.write("\n")

            # Active incidents
            if active_incidents:
                f.write("## Active Incidents\n\n")
                for incident in active_incidents:
                    f.write(f"### {incident.incident_id}: {incident.title}\n\n")
                    f.write(f"- **Severity:** {incident.severity.value.title()}\n")
                    f.write(f"- **Component:** {incident.component}\n")
                    f.write(f"- **Status:** {incident.status.value.title()}\n")
                    f.write(
                        f"- **Detection Time:** {incident.detection_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
                    if incident.recovery_actions:
                        f.write("- **Recovery Actions:**\n")
                        for action in incident.recovery_actions:
                            f.write(f"  - {action}\n")
                    f.write("\n")

        self.logger.info(f"Exported TTR report to {export_path}")
        return export_path

    def _load_incidents(self):
        """Load incidents from persistent storage"""
        if self.incidents_file.exists():
            try:
                with open(self.incidents_file, "r") as f:
                    data = json.load(f)

                # Load active incidents
                for incident_data in data.get("active", []):
                    incident = self._dict_to_incident(incident_data)
                    self.active_incidents[incident.incident_id] = incident

                # Load incident history
                for incident_data in data.get("history", []):
                    incident = self._dict_to_incident(incident_data)
                    self.incident_history.append(incident)

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"Failed to load incidents: {e}")

    def _save_incidents(self):
        """Save incidents to persistent storage"""
        data = {
            "active": [
                self._incident_to_dict(inc) for inc in self.active_incidents.values()
            ],
            "history": [self._incident_to_dict(inc) for inc in self.incident_history],
        }

        with open(self.incidents_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def _incident_to_dict(self, incident: Incident) -> Dict[str, Any]:
        """Convert incident to dictionary for JSON serialization"""
        data = asdict(incident)
        data["severity"] = incident.severity.value
        data["status"] = incident.status.value
        return data

    def _dict_to_incident(self, data: Dict[str, Any]) -> Incident:
        """Convert dictionary to incident object"""
        data["severity"] = IncidentSeverity(data["severity"])
        data["status"] = IncidentStatus(data["status"])
        data["detection_time"] = datetime.fromisoformat(data["detection_time"])
        if data["resolution_time"]:
            data["resolution_time"] = datetime.fromisoformat(data["resolution_time"])

        return Incident(**data)

    def _save_ttr_metrics(self, incident: Incident):
        """Save TTR metrics to CSV file"""
        file_exists = self.metrics_file.exists()

        with open(self.metrics_file, "a", newline="") as csvfile:
            fieldnames = [
                "timestamp",
                "incident_id",
                "severity",
                "component",
                "ttr_minutes",
                "sla_target_minutes",
                "sla_met",
            ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            target = self.ttr_targets.get(incident.severity, 0)
            sla_met = incident.ttr_minutes <= target if incident.ttr_minutes else False

            writer.writerow(
                {
                    "timestamp": datetime.now().isoformat(),
                    "incident_id": incident.incident_id,
                    "severity": incident.severity.value,
                    "component": incident.component,
                    "ttr_minutes": incident.ttr_minutes,
                    "sla_target_minutes": target,
                    "sla_met": sla_met,
                }
            )


# Global instance management
_global_ttr_tracker: Optional[TTRTracker] = None


def get_ttr_tracker() -> TTRTracker:
    """Get or create the global TTR tracker instance"""
    global _global_ttr_tracker

    if _global_ttr_tracker is None:
        _global_ttr_tracker = TTRTracker()

    return _global_ttr_tracker


# Convenience functions
def create_incident(
    title: str, description: str, severity: str, component: str, tags: List[str] = None
) -> str:
    """Convenience function to create an incident"""
    tracker = get_ttr_tracker()
    return tracker.create_incident(title, description, severity, component, tags)


def resolve_incident(
    incident_id: str, root_cause: str = None, prevention_measures: List[str] = None
) -> bool:
    """Convenience function to resolve an incident"""
    tracker = get_ttr_tracker()
    return tracker.resolve_incident(incident_id, root_cause, prevention_measures)


# CLI integration helpers
def cli_incident_handler(component: str = "cli"):
    """Context manager for CLI operations with automatic incident creation on failure"""
    from contextlib import contextmanager

    @contextmanager
    def handler():
        tracker = get_ttr_tracker()
        incident_id = None

        try:
            yield
        except Exception as e:
            # Auto-create incident for CLI failures
            incident_id = tracker.create_incident(
                title=f"CLI operation failed: {type(e).__name__}",
                description=str(e),
                severity=IncidentSeverity.MEDIUM,
                component=component,
                tags=["cli", "auto-created"],
            )

            # Add basic recovery action
            tracker.add_recovery_action(incident_id, f"Exception occurred: {str(e)}")

            # Re-raise the exception
            raise
        finally:
            if incident_id:
                # Auto-resolve if no further action needed
                tracker.resolve_incident(
                    incident_id,
                    root_cause="CLI operation exception",
                    prevention_measures=[
                        "Add better error handling",
                        "Improve input validation",
                    ],
                )

    return handler()


# Example usage and testing
if __name__ == "__main__":
    # Example usage
    tracker = TTRTracker()

    # Create a test incident
    incident_id = tracker.create_incident(
        title="Database connection failure",
        description="Unable to connect to primary database",
        severity=IncidentSeverity.HIGH,
        component="database",
        tags=["database", "connectivity"],
    )

    print(f"Created incident: {incident_id}")

    # Add recovery actions
    tracker.add_recovery_action(incident_id, "Checked database service status")
    tracker.add_recovery_action(incident_id, "Restarted database service")
    tracker.add_recovery_action(incident_id, "Verified connectivity restored")

    # Resolve incident
    time.sleep(1)  # Simulate resolution time
    tracker.resolve_incident(
        incident_id,
        root_cause="Database service crashed due to memory exhaustion",
        prevention_measures=[
            "Implement database monitoring",
            "Set up memory alerts",
            "Configure automatic restart",
        ],
    )

    # Get metrics
    metrics = tracker.get_metrics_summary(days=1)
    print(f"Metrics: {json.dumps(metrics, indent=2)}")

    # Export reports
    csv_path = tracker.export_to_csv()
    md_path = tracker.export_to_markdown()

    print(f"Exported CSV: {csv_path}")
    print(f"Exported Markdown: {md_path}")
