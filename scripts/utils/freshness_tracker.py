#!/usr/bin/env python3
"""
Freshness Tracker for IntelForge using sqlite-utils
Replaces CSV-based freshness tracking with sqlite-utils for better analytics
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import sqlite_utils
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()


class FreshnessStatus(Enum):
    """Freshness status levels"""

    FRESH = "fresh"
    STALE = "stale"
    EXPIRED = "expired"
    UNKNOWN = "unknown"


@dataclass
class CrawlRecord:
    """Data class for crawl freshness tracking"""

    domain: str
    url: str
    last_crawled: datetime
    content_hash: str
    status: FreshnessStatus
    response_time_ms: int
    content_size_bytes: int
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FreshnessMetrics:
    """Data class for freshness metrics"""

    domain: str
    total_urls: int
    fresh_count: int
    stale_count: int
    expired_count: int
    avg_age_hours: float
    last_updated: datetime
    success_rate: float


class FreshnessTracker:
    """SQLite-based freshness tracker using sqlite-utils"""

    def __init__(self, db_path: str = "./logs/freshness.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite_utils.Database(self.db_path)
        self._initialize_tables()

    def _initialize_tables(self):
        """Initialize database tables"""
        # Crawl records table
        self.db["crawl_records"].create(
            {
                "id": int,
                "domain": str,
                "url": str,
                "last_crawled": str,
                "content_hash": str,
                "status": str,
                "response_time_ms": int,
                "content_size_bytes": int,
                "error_message": str,
                "metadata": str,
            },
            pk="id",
            if_not_exists=True,
        )

        # Freshness metrics table
        self.db["freshness_metrics"].create(
            {
                "id": int,
                "domain": str,
                "total_urls": int,
                "fresh_count": int,
                "stale_count": int,
                "expired_count": int,
                "avg_age_hours": float,
                "last_updated": str,
                "success_rate": float,
            },
            pk="id",
            if_not_exists=True,
        )

        # Create indexes for better performance
        self.db["crawl_records"].create_index(["domain"], if_not_exists=True)
        self.db["crawl_records"].create_index(["last_crawled"], if_not_exists=True)
        self.db["crawl_records"].create_index(["status"], if_not_exists=True)
        self.db["freshness_metrics"].create_index(["domain"], if_not_exists=True)

    def record_crawl(self, record: CrawlRecord) -> int:
        """Record a crawl event"""
        data = {
            "domain": record.domain,
            "url": record.url,
            "last_crawled": record.last_crawled.isoformat(),
            "content_hash": record.content_hash,
            "status": record.status.value,
            "response_time_ms": record.response_time_ms,
            "content_size_bytes": record.content_size_bytes,
            "error_message": record.error_message,
            "metadata": json.dumps(record.metadata) if record.metadata else None,
        }

        return self.db["crawl_records"].insert(data).last_pk

    def update_domain_metrics(self, domain: str) -> FreshnessMetrics:
        """Update and calculate freshness metrics for a domain"""
        # Get all records for domain
        records = list(
            self.db.execute(
                "SELECT * FROM crawl_records WHERE domain = ? ORDER BY last_crawled DESC",
                [domain],
            )
        )

        if not records:
            return None

        # Calculate metrics
        total_urls = len(records)
        fresh_count = sum(
            1 for r in records if r["status"] == FreshnessStatus.FRESH.value
        )
        stale_count = sum(
            1 for r in records if r["status"] == FreshnessStatus.STALE.value
        )
        expired_count = sum(
            1 for r in records if r["status"] == FreshnessStatus.EXPIRED.value
        )

        # Calculate average age
        now = datetime.now()
        total_age_hours = 0
        for record in records:
            crawl_time = datetime.fromisoformat(record["last_crawled"])
            age_hours = (now - crawl_time).total_seconds() / 3600
            total_age_hours += age_hours

        avg_age_hours = total_age_hours / total_urls if total_urls > 0 else 0

        # Calculate success rate (non-error records)
        success_count = sum(1 for r in records if not r["error_message"])
        success_rate = (success_count / total_urls) * 100 if total_urls > 0 else 0

        metrics = FreshnessMetrics(
            domain=domain,
            total_urls=total_urls,
            fresh_count=fresh_count,
            stale_count=stale_count,
            expired_count=expired_count,
            avg_age_hours=avg_age_hours,
            last_updated=now,
            success_rate=success_rate,
        )

        # Store metrics
        metrics_data = {
            "domain": domain,
            "total_urls": total_urls,
            "fresh_count": fresh_count,
            "stale_count": stale_count,
            "expired_count": expired_count,
            "avg_age_hours": avg_age_hours,
            "last_updated": now.isoformat(),
            "success_rate": success_rate,
        }

        self.db["freshness_metrics"].insert(metrics_data, replace=True)
        return metrics

    def get_domain_metrics(self, domain: str) -> Optional[FreshnessMetrics]:
        """Get freshness metrics for a domain"""
        try:
            row = self.db.execute(
                "SELECT * FROM freshness_metrics WHERE domain = ? ORDER BY last_updated DESC LIMIT 1",
                [domain],
            ).fetchone()

            if row:
                return FreshnessMetrics(
                    domain=row["domain"],
                    total_urls=row["total_urls"],
                    fresh_count=row["fresh_count"],
                    stale_count=row["stale_count"],
                    expired_count=row["expired_count"],
                    avg_age_hours=row["avg_age_hours"],
                    last_updated=datetime.fromisoformat(row["last_updated"]),
                    success_rate=row["success_rate"],
                )
        except Exception as e:
            logger.error(f"Error getting domain metrics: {e}")
        return None

    def get_overall_metrics(self) -> Dict[str, Any]:
        """Get overall freshness metrics across all domains"""
        try:
            # Get totals across all domains
            totals = self.db.execute(
                """
                SELECT
                    COUNT(DISTINCT domain) as total_domains,
                    COUNT(*) as total_urls,
                    SUM(CASE WHEN status = 'fresh' THEN 1 ELSE 0 END) as fresh_count,
                    SUM(CASE WHEN status = 'stale' THEN 1 ELSE 0 END) as stale_count,
                    SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) as expired_count,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(CASE WHEN error_message IS NULL THEN 1 ELSE 0 END) as success_count
                FROM crawl_records
            """
            ).fetchone()

            # Calculate overall success rate
            success_rate = (
                (totals["success_count"] / totals["total_urls"]) * 100
                if totals["total_urls"] > 0
                else 0
            )

            # Get domain-specific metrics
            domain_metrics = list(
                self.db.execute(
                    """
                SELECT domain, avg_age_hours, success_rate
                FROM freshness_metrics
                ORDER BY last_updated DESC
            """
                )
            )

            return {
                "timestamp": datetime.now().isoformat(),
                "total_domains": totals["total_domains"],
                "total_urls": totals["total_urls"],
                "fresh_count": totals["fresh_count"],
                "stale_count": totals["stale_count"],
                "expired_count": totals["expired_count"],
                "overall_success_rate": success_rate,
                "avg_response_time_ms": totals["avg_response_time"] or 0,
                "domain_breakdown": domain_metrics,
            }
        except Exception as e:
            logger.error(f"Error getting overall metrics: {e}")
            return {}

    def get_stale_urls(self, hours_threshold: int = 24) -> List[Dict[str, Any]]:
        """Get URLs that are stale (older than threshold)"""
        threshold_time = datetime.now() - timedelta(hours=hours_threshold)

        return list(
            self.db.execute(
                """
            SELECT domain, url, last_crawled, status, error_message
            FROM crawl_records
            WHERE last_crawled < ?
            ORDER BY last_crawled ASC
        """,
                [threshold_time.isoformat()],
            )
        )

    def generate_freshness_report(
        self, format_type: str = "table", days: int = 7
    ) -> str:
        """Generate freshness report in specified format"""
        # Get data for the last N days
        since_date = datetime.now() - timedelta(days=days)

        # Get domain metrics
        domain_metrics = list(
            self.db.execute(
                """
            SELECT * FROM freshness_metrics
            WHERE last_updated >= ?
            ORDER BY avg_age_hours DESC
        """,
                [since_date.isoformat()],
            )
        )

        if format_type == "json":
            return json.dumps(
                {
                    "report_date": datetime.now().isoformat(),
                    "days_covered": days,
                    "domains": domain_metrics,
                    "overall_metrics": self.get_overall_metrics(),
                },
                indent=2,
            )

        elif format_type == "table":
            if not domain_metrics:
                return "No freshness data available for the specified period."

            table = Table(title=f"Freshness Report - Last {days} Days")
            table.add_column("Domain", style="cyan")
            table.add_column("URLs", justify="right")
            table.add_column("Fresh", justify="right", style="green")
            table.add_column("Stale", justify="right", style="yellow")
            table.add_column("Expired", justify="right", style="red")
            table.add_column("Avg Age (hrs)", justify="right")
            table.add_column("Success Rate", justify="right")

            for metrics in domain_metrics:
                table.add_row(
                    metrics["domain"],
                    str(metrics["total_urls"]),
                    str(metrics["fresh_count"]),
                    str(metrics["stale_count"]),
                    str(metrics["expired_count"]),
                    f"{metrics['avg_age_hours']:.1f}",
                    f"{metrics['success_rate']:.1f}%",
                )

            # Capture table as string
            with console.capture() as capture:
                console.print(table)
            return capture.get()

        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def cleanup_old_records(self, days_to_keep: int = 30) -> int:
        """Clean up old records to manage database size"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        # Delete old crawl records
        result = self.db.execute(
            """
            DELETE FROM crawl_records
            WHERE last_crawled < ?
        """,
            [cutoff_date.isoformat()],
        )

        deleted_count = result.rowcount

        # Clean up orphaned metrics
        self.db.execute(
            """
            DELETE FROM freshness_metrics
            WHERE last_updated < ?
        """,
            [cutoff_date.isoformat()],
        )

        return deleted_count

    def export_to_csv(self, output_path: str, table_name: str = "crawl_records") -> str:
        """Export data to CSV for compatibility"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Export using sqlite-utils
        with open(output_file, "w", newline="") as f:
            for row in self.db[table_name].rows:
                if not hasattr(export_to_csv, "header_written"):
                    # Write header
                    writer = csv.DictWriter(f, fieldnames=row.keys())
                    writer.writeheader()
                    export_to_csv.header_written = True

                writer.writerow(row)

        return str(output_file)


# CLI Integration Functions
def determine_freshness_status(
    last_crawled: datetime,
    fresh_threshold_hours: int = 6,
    stale_threshold_hours: int = 24,
) -> FreshnessStatus:
    """Determine freshness status based on age"""
    now = datetime.now()
    age_hours = (now - last_crawled).total_seconds() / 3600

    if age_hours <= fresh_threshold_hours:
        return FreshnessStatus.FRESH
    elif age_hours <= stale_threshold_hours:
        return FreshnessStatus.STALE
    else:
        return FreshnessStatus.EXPIRED


def create_sample_data(tracker: FreshnessTracker):
    """Create sample data for testing"""
    import hashlib
    import random

    domains = ["example.com", "test.org", "sample.net"]
    now = datetime.now()

    for domain in domains:
        for i in range(random.randint(5, 15)):
            # Random crawl time in last 48 hours
            crawl_time = now - timedelta(hours=random.randint(0, 48))

            # Determine status based on age
            status = determine_freshness_status(crawl_time)

            record = CrawlRecord(
                domain=domain,
                url=f"https://{domain}/page{i}",
                last_crawled=crawl_time,
                content_hash=hashlib.md5(f"{domain}{i}".encode()).hexdigest(),
                status=status,
                response_time_ms=random.randint(100, 2000),
                content_size_bytes=random.randint(1000, 50000),
                error_message=None if random.random() > 0.1 else "Connection timeout",
                metadata={
                    "user_agent": "IntelForge/1.0",
                    "retry_count": random.randint(0, 2),
                },
            )

            tracker.record_crawl(record)

        # Update metrics for domain
        tracker.update_domain_metrics(domain)


if __name__ == "__main__":
    # Test the tracker
    tracker = FreshnessTracker()

    # Create sample data
    create_sample_data(tracker)

    # Generate report
    print("=== Freshness Report ===")
    print(tracker.generate_freshness_report(format_type="table", days=7))

    # Show overall metrics
    print("\n=== Overall Metrics ===")
    overall = tracker.get_overall_metrics()
    print(json.dumps(overall, indent=2))
