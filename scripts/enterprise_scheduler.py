#!/usr/bin/env python3
"""
Enterprise Scheduling System
Advanced orchestration for regular financial data collection with:
- Intelligent retry and backoff strategies
- Priority-based job queuing
- Configuration management for different scraping profiles
- Automated scheduling with cron-like functionality
"""

import argparse
import json
import logging
import random
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import our monitoring system
from scripts.monitoring_dashboard import ScrapingEvent, ScrapingLogger


class JobPriority(Enum):
    """Job priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class JobStatus(Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


@dataclass
class ScrapingJob:
    """Represents a scheduled scraping job."""

    id: str
    name: str
    job_type: str  # 'financial_batch', 'academic_research', 'single_url'
    priority: JobPriority
    schedule_expression: str  # cron-like or interval
    config: Dict[str, Any]
    retry_policy: Dict[str, Any]
    created_at: str
    next_run: str
    last_run: Optional[str] = None
    status: JobStatus = JobStatus.PENDING
    retry_count: int = 0
    metadata: Optional[Dict] = None


class RetryPolicy:
    """Implements intelligent retry and backoff strategies."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 300.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given retry attempt."""
        delay = self.initial_delay * (self.backoff_factor**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add ±25% jitter to prevent thundering herd
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0, delay)

    def should_retry(self, attempt: int, error_type: str = None) -> bool:
        """Determine if job should be retried."""
        if attempt >= self.max_retries:
            return False

        # Don't retry certain types of errors
        permanent_errors = ["auth_failure", "invalid_url", "permission_denied"]
        if error_type in permanent_errors:
            return False

        return True


class JobQueue:
    """Priority-based job queue with persistence."""

    def __init__(self, db_path: str = "vault/logs/job_queue.db"):
        self.db_path = Path(project_root) / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        self.logger = ScrapingLogger()

    def init_database(self):
        """Initialize SQLite database for job persistence."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    job_type TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    schedule_expression TEXT NOT NULL,
                    config TEXT NOT NULL,
                    retry_policy TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    next_run TEXT NOT NULL,
                    last_run TEXT,
                    status TEXT NOT NULL,
                    retry_count INTEGER DEFAULT 0,
                    metadata TEXT
                )
            """
            )

            conn.execute("CREATE INDEX IF NOT EXISTS idx_priority ON jobs(priority)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_next_run ON jobs(next_run)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON jobs(status)")

    def add_job(self, job: ScrapingJob):
        """Add a job to the queue."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO jobs
                (id, name, job_type, priority, schedule_expression, config,
                 retry_policy, created_at, next_run, last_run, status, retry_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    job.id,
                    job.name,
                    job.job_type,
                    job.priority.value,
                    job.schedule_expression,
                    json.dumps(job.config),
                    json.dumps(job.retry_policy),
                    job.created_at,
                    job.next_run,
                    job.last_run,
                    job.status.value,
                    job.retry_count,
                    json.dumps(job.metadata) if job.metadata else None,
                ),
            )

    def get_ready_jobs(self) -> List[ScrapingJob]:
        """Get jobs ready for execution, ordered by priority."""
        current_time = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT * FROM jobs
                WHERE next_run <= ? AND status IN ('pending', 'retrying')
                ORDER BY priority DESC, next_run ASC
            """,
                (current_time,),
            )

            jobs = []
            for row in cursor.fetchall():
                job_data = dict(row)
                job = ScrapingJob(
                    id=job_data["id"],
                    name=job_data["name"],
                    job_type=job_data["job_type"],
                    priority=JobPriority(job_data["priority"]),
                    schedule_expression=job_data["schedule_expression"],
                    config=json.loads(job_data["config"]),
                    retry_policy=json.loads(job_data["retry_policy"]),
                    created_at=job_data["created_at"],
                    next_run=job_data["next_run"],
                    last_run=job_data["last_run"],
                    status=JobStatus(job_data["status"]),
                    retry_count=job_data["retry_count"],
                    metadata=(
                        json.loads(job_data["metadata"])
                        if job_data["metadata"]
                        else None
                    ),
                )
                jobs.append(job)

            return jobs

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        next_run: str = None,
        retry_count: int = None,
    ):
        """Update job status and schedule."""
        with sqlite3.connect(self.db_path) as conn:
            updates = ["status = ?", "last_run = ?"]
            params = [status.value, datetime.now().isoformat()]

            if next_run:
                updates.append("next_run = ?")
                params.append(next_run)

            if retry_count is not None:
                updates.append("retry_count = ?")
                params.append(retry_count)

            params.append(job_id)

            conn.execute(
                f"""
                UPDATE jobs
                SET {", ".join(updates)}
                WHERE id = ?
            """,
                params,
            )


class ScrapingProfileManager:
    """Manages different scraping profiles and configurations."""

    def __init__(self, config_path: str = "config/scraping_profiles.json"):
        self.config_path = Path(project_root) / config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.profiles = self.load_profiles()

    def load_profiles(self) -> Dict[str, Any]:
        """Load scraping profiles from configuration file."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        else:
            # Create default profiles
            default_profiles = {
                "financial_fast": {
                    "description": "Fast financial data collection",
                    "method": "http",
                    "workers": 5,
                    "delay_range": [1, 3],
                    "retries": 2,
                    "timeout": 30,
                    "max_retry_attempts": 3,
                    "retry_backoff_factor": 2.0,
                },
                "financial_stealth": {
                    "description": "Stealth financial data collection",
                    "method": "http",
                    "workers": 3,
                    "delay_range": [3, 8],
                    "retries": 3,
                    "timeout": 60,
                    "max_retry_attempts": 5,
                    "retry_backoff_factor": 1.5,
                },
                "academic_bulk": {
                    "description": "Bulk academic research collection",
                    "method": "api",
                    "concurrent_requests": 10,
                    "rate_limit": 0.5,
                    "max_retry_attempts": 3,
                    "retry_backoff_factor": 2.0,
                },
            }
            self.save_profiles(default_profiles)
            return default_profiles

    def save_profiles(self, profiles: Dict[str, Any]):
        """Save profiles to configuration file."""
        with open(self.config_path, "w") as f:
            json.dump(profiles, f, indent=2)
        self.profiles = profiles

    def get_profile(self, profile_name: str) -> Dict[str, Any]:
        """Get configuration for a specific profile."""
        return self.profiles.get(profile_name, self.profiles.get("financial_fast"))


class EnterpriseScheduler:
    """Main enterprise scheduling system."""

    def __init__(self):
        self.job_queue = JobQueue()
        self.profile_manager = ScrapingProfileManager()
        self.logger = ScrapingLogger()
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(project_root / "vault/logs/scheduler.log"),
                logging.StreamHandler(),
            ],
        )
        self.log = logging.getLogger(__name__)

    def create_job(
        self,
        name: str,
        job_type: str,
        priority: JobPriority,
        schedule_expression: str,
        config: Dict[str, Any],
        retry_policy: Dict[str, Any] = None,
    ) -> str:
        """Create a new scheduled job."""
        job_id = f"{job_type}_{int(time.time())}"

        if retry_policy is None:
            retry_policy = {
                "max_retries": 3,
                "initial_delay": 1.0,
                "max_delay": 300.0,
                "backoff_factor": 2.0,
            }

        # Calculate next run time based on schedule expression
        next_run = self.calculate_next_run(schedule_expression)

        job = ScrapingJob(
            id=job_id,
            name=name,
            job_type=job_type,
            priority=priority,
            schedule_expression=schedule_expression,
            config=config,
            retry_policy=retry_policy,
            created_at=datetime.now().isoformat(),
            next_run=next_run,
        )

        self.job_queue.add_job(job)
        self.log.info(f"Created job: {job_id} - {name}")
        return job_id

    def calculate_next_run(self, schedule_expression: str) -> str:
        """Calculate next run time from schedule expression."""
        now = datetime.now()

        if schedule_expression.startswith("every_"):
            # Simple interval scheduling: every_30m, every_1h, every_6h, every_1d
            interval_str = schedule_expression[6:]
            if interval_str.endswith("m"):
                minutes = int(interval_str[:-1])
                next_run = now + timedelta(minutes=minutes)
            elif interval_str.endswith("h"):
                hours = int(interval_str[:-1])
                next_run = now + timedelta(hours=hours)
            elif interval_str.endswith("d"):
                days = int(interval_str[:-1])
                next_run = now + timedelta(days=days)
            else:
                # Default to 1 hour
                next_run = now + timedelta(hours=1)
        else:
            # Default to 1 hour for unrecognized expressions
            next_run = now + timedelta(hours=1)

        return next_run.isoformat()

    def execute_job(self, job: ScrapingJob) -> bool:
        """Execute a single job."""
        self.log.info(f"Executing job: {job.id} - {job.name}")

        # Update job status to running
        self.job_queue.update_job_status(job.id, JobStatus.RUNNING)

        # Log start event
        self.logger.log_event(
            ScrapingEvent(
                timestamp=datetime.now().isoformat(),
                event_type="start",
                scraper_type=job.job_type,
                url=(
                    job.config.get("urls", ["scheduled_job"])[0]
                    if job.config.get("urls")
                    else "scheduled_job"
                ),
                metadata={"job_id": job.id, "job_name": job.name},
            )
        )

        start_time = time.time()
        success = False
        error_message = None

        try:
            if job.job_type == "financial_batch":
                success = self.execute_financial_batch(job)
            elif job.job_type == "academic_research":
                success = self.execute_academic_research(job)
            elif job.job_type == "single_url":
                success = self.execute_single_url(job)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")

        except Exception as e:
            self.log.error(f"Job {job.id} failed: {e}")
            error_message = str(e)
            success = False

        execution_time = time.time() - start_time

        # Log completion event
        self.logger.log_event(
            ScrapingEvent(
                timestamp=datetime.now().isoformat(),
                event_type="success" if success else "failure",
                scraper_type=job.job_type,
                url=(
                    job.config.get("urls", ["scheduled_job"])[0]
                    if job.config.get("urls")
                    else "scheduled_job"
                ),
                execution_time=execution_time,
                error_message=error_message,
                metadata={"job_id": job.id, "job_name": job.name},
            )
        )

        # Update job status and schedule next run
        if success:
            next_run = self.calculate_next_run(job.schedule_expression)
            self.job_queue.update_job_status(job.id, JobStatus.PENDING, next_run, 0)
            self.log.info(f"Job {job.id} completed successfully. Next run: {next_run}")
        else:
            self.handle_job_failure(job, error_message)

        return success

    def handle_job_failure(self, job: ScrapingJob, error_message: str):
        """Handle job failure with retry logic."""
        retry_policy = RetryPolicy(**job.retry_policy)

        if retry_policy.should_retry(job.retry_count):
            # Schedule retry
            delay = retry_policy.calculate_delay(job.retry_count)
            next_run = (datetime.now() + timedelta(seconds=delay)).isoformat()

            self.job_queue.update_job_status(
                job.id, JobStatus.RETRYING, next_run, job.retry_count + 1
            )

            self.log.info(
                f"Job {job.id} will retry in {delay:.1f}s (attempt {job.retry_count + 1})"
            )
        else:
            # Mark as failed
            self.job_queue.update_job_status(job.id, JobStatus.FAILED)
            self.log.error(
                f"Job {job.id} failed permanently after {job.retry_count} retries"
            )

    def execute_financial_batch(self, job: ScrapingJob) -> bool:
        """Execute financial batch scraping job."""
        config = job.config
        profile = self.profile_manager.get_profile(
            config.get("profile", "financial_fast")
        )

        # Build command
        cmd = [
            sys.executable,
            "scripts/batch_stealth_scraper.py",
            "--workers",
            str(profile.get("workers", 3)),
            "--retries",
            str(profile.get("retries", 2)),
            "--delay-min",
            str(profile.get("delay_range", [2, 5])[0]),
            "--delay-max",
            str(profile.get("delay_range", [2, 5])[1]),
        ]

        if config.get("urls"):
            cmd.extend(["--urls"] + config["urls"])
        elif config.get("url_file"):
            cmd.extend(["--file", config["url_file"]])

        if config.get("output_file"):
            cmd.extend(["--output", config["output_file"]])

        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=profile.get("timeout", 300),
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def execute_academic_research(self, job: ScrapingJob) -> bool:
        """Execute academic research job."""
        config = job.config

        cmd = [sys.executable, "scripts/academic_research.py"]

        if config.get("queries"):
            cmd.extend(["--queries"] + config["queries"])
        if config.get("max_results"):
            cmd.extend(["--max-results", str(config["max_results"])])

        try:
            result = subprocess.run(
                cmd, cwd=project_root, capture_output=True, text=True, timeout=300
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def execute_single_url(self, job: ScrapingJob) -> bool:
        """Execute single URL scraping job."""
        config = job.config

        cmd = [sys.executable, "scripts/stealth_scraper_simple.py"]
        cmd.extend(["--url", config["url"]])

        try:
            result = subprocess.run(
                cmd, cwd=project_root, capture_output=True, text=True, timeout=120
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def start_scheduler(self):
        """Start the main scheduler loop."""
        self.running = True
        self.log.info("Enterprise Scheduler started")

        try:
            while self.running:
                # Get ready jobs
                ready_jobs = self.job_queue.get_ready_jobs()

                if ready_jobs:
                    self.log.info(f"Processing {len(ready_jobs)} ready job(s)")

                    # Execute jobs in priority order
                    for job in ready_jobs:
                        if not self.running:
                            break

                        # Submit job to thread pool
                        self.executor.submit(self.execute_job, job)

                # Sleep for 30 seconds before next check
                time.sleep(30)

        except KeyboardInterrupt:
            self.log.info("Scheduler interrupted by user")
        finally:
            self.running = False
            self.executor.shutdown(wait=True)
            self.log.info("Enterprise Scheduler stopped")

    def stop_scheduler(self):
        """Stop the scheduler."""
        self.running = False


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Enterprise Scheduling System")
    parser.add_argument("--start", action="store_true", help="Start the scheduler")
    parser.add_argument("--create-job", action="store_true", help="Create a new job")
    parser.add_argument("--list-jobs", action="store_true", help="List all jobs")
    parser.add_argument(
        "--create-defaults", action="store_true", help="Create default scheduled jobs"
    )

    # Job creation parameters
    parser.add_argument("--name", type=str, help="Job name")
    parser.add_argument(
        "--type",
        type=str,
        choices=["financial_batch", "academic_research", "single_url"],
        help="Job type",
    )
    parser.add_argument(
        "--priority",
        type=str,
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Job priority",
    )
    parser.add_argument(
        "--schedule",
        type=str,
        default="every_1h",
        help="Schedule expression (e.g., every_30m, every_6h)",
    )
    parser.add_argument("--urls", nargs="+", help="URLs to scrape")
    parser.add_argument(
        "--profile", type=str, default="financial_fast", help="Scraping profile"
    )

    args = parser.parse_args()

    scheduler = EnterpriseScheduler()

    if args.start:
        scheduler.start_scheduler()

    elif args.create_job:
        if not args.name or not args.type:
            print("Error: --name and --type are required for job creation")
            return

        priority_map = {
            "low": JobPriority.LOW,
            "medium": JobPriority.MEDIUM,
            "high": JobPriority.HIGH,
            "critical": JobPriority.CRITICAL,
        }

        config = {"profile": args.profile}

        if args.urls:
            config["urls"] = args.urls
        elif args.type == "financial_batch":
            config["url_file"] = "financial_test_urls.txt"

        job_id = scheduler.create_job(
            name=args.name,
            job_type=args.type,
            priority=priority_map[args.priority],
            schedule_expression=args.schedule,
            config=config,
        )

        print(f"Created job: {job_id}")

    elif args.create_defaults:
        # Create default scheduled jobs
        jobs_created = []

        # Daily financial data collection
        jobs_created.append(
            scheduler.create_job(
                name="Daily Financial Data Collection",
                job_type="financial_batch",
                priority=JobPriority.HIGH,
                schedule_expression="every_6h",
                config={
                    "profile": "financial_stealth",
                    "url_file": "financial_test_urls.txt",
                    "output_file": "output/daily_financial_data.json",
                },
            )
        )

        # Weekly academic research update
        jobs_created.append(
            scheduler.create_job(
                name="Weekly Academic Research Update",
                job_type="academic_research",
                priority=JobPriority.MEDIUM,
                schedule_expression="every_1d",
                config={
                    "queries": [
                        "algorithmic trading",
                        "quantitative finance",
                        "financial risk management",
                    ],
                    "max_results": 10,
                },
            )
        )

        print(f"Created {len(jobs_created)} default jobs:")
        for job_id in jobs_created:
            print(f"  - {job_id}")

    elif args.list_jobs:
        jobs = scheduler.job_queue.get_ready_jobs()
        if jobs:
            print(f"Found {len(jobs)} ready jobs:")
            for job in jobs:
                print(
                    f"  - {job.id}: {job.name} ({job.priority.name}) - {job.status.value}"
                )
        else:
            print("No ready jobs found")

    else:
        print(
            "Use --start to run scheduler, --create-job to add jobs, or --create-defaults"
        )


if __name__ == "__main__":
    main()
