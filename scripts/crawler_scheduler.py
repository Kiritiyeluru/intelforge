#!/usr/bin/env python3
"""
IntelForge Crawler Scheduler - Phase 5.1 Implementation
Priority-based scheduling system for intelligent semantic crawling automation.

This module implements automated scheduling based on source priorities defined in
the source registry YAML configuration.
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Priority(Enum):
    """Priority levels for source scheduling"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ScheduledSource:
    """Represents a scheduled crawling source"""

    name: str
    url: str
    priority: Priority
    threshold: float
    category: str
    quality: str
    complexity: str
    content_requirements: Dict
    tags: List[str]
    last_crawled: Optional[datetime] = None
    next_crawl: Optional[datetime] = None
    crawl_count: int = 0
    success_rate: float = 1.0

    def is_due(self) -> bool:
        """Check if this source is due for crawling"""
        if self.next_crawl is None:
            return True
        return datetime.now() >= self.next_crawl

    def calculate_next_crawl(self) -> datetime:
        """Calculate next crawl time based on priority"""
        now = datetime.now()

        if self.priority == Priority.DAILY:
            return now + timedelta(days=1)
        elif self.priority == Priority.WEEKLY:
            return now + timedelta(weeks=1)
        elif self.priority == Priority.MONTHLY:
            return now + timedelta(days=30)
        else:
            return now + timedelta(days=1)  # Default to daily

    def update_after_crawl(self, success: bool):
        """Update source metrics after crawling"""
        self.last_crawled = datetime.now()
        self.next_crawl = self.calculate_next_crawl()
        self.crawl_count += 1

        # Update success rate with exponential moving average
        if self.crawl_count == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            # 70% weight to historical, 30% to current
            self.success_rate = 0.7 * self.success_rate + 0.3 * (
                1.0 if success else 0.0
            )


class CrawlerScheduler:
    """Main scheduler for managing crawling tasks"""

    def __init__(self, registry_path: str = "config/source_registry.yaml"):
        self.registry_path = Path(registry_path)
        self.schedule_file = Path("metadata/crawler_schedule.json")
        self.sources: List[ScheduledSource] = []
        self.global_settings = {}

        # Create metadata directory if it doesn't exist
        self.schedule_file.parent.mkdir(exist_ok=True)

        self.load_registry()
        self.load_schedule()

    def load_registry(self):
        """Load source registry from YAML file"""
        try:
            with open(self.registry_path, "r") as f:
                registry = yaml.safe_load(f)

            self.global_settings = registry.get("global_settings", {})

            # Load sources from all categories
            for category, category_sources in registry.items():
                if category in ["global_settings", "content_types"]:
                    continue

                for source_config in category_sources:
                    source = ScheduledSource(
                        name=source_config["name"],
                        url=source_config["url"],
                        priority=Priority(source_config["priority"]),
                        threshold=source_config.get("threshold", 0.75),
                        category=category,
                        quality=source_config.get("quality", "good"),
                        complexity=source_config.get("complexity", "medium"),
                        content_requirements=source_config.get(
                            "content_requirements", {}
                        ),
                        tags=source_config.get("tags", []),
                    )

                    # Set initial next crawl time
                    source.next_crawl = source.calculate_next_crawl()

                    self.sources.append(source)

            logger.info(f"Loaded {len(self.sources)} sources from registry")

        except Exception as e:
            logger.error(f"Error loading registry: {e}")
            raise

    def load_schedule(self):
        """Load existing schedule data"""
        if self.schedule_file.exists():
            try:
                with open(self.schedule_file, "r") as f:
                    schedule_data = json.load(f)

                # Update sources with saved schedule data
                for source in self.sources:
                    if source.name in schedule_data:
                        saved_data = schedule_data[source.name]
                        if "last_crawled" in saved_data and saved_data["last_crawled"]:
                            source.last_crawled = datetime.fromisoformat(
                                saved_data["last_crawled"]
                            )
                        if "next_crawl" in saved_data and saved_data["next_crawl"]:
                            source.next_crawl = datetime.fromisoformat(
                                saved_data["next_crawl"]
                            )
                        source.crawl_count = saved_data.get("crawl_count", 0)
                        source.success_rate = saved_data.get("success_rate", 1.0)

                logger.info("Loaded existing schedule data")

            except Exception as e:
                logger.warning(f"Error loading schedule: {e}")

    def save_schedule(self):
        """Save current schedule state to file"""
        try:
            schedule_data = {}
            for source in self.sources:
                schedule_data[source.name] = {
                    "last_crawled": (
                        source.last_crawled.isoformat() if source.last_crawled else None
                    ),
                    "next_crawl": (
                        source.next_crawl.isoformat() if source.next_crawl else None
                    ),
                    "crawl_count": source.crawl_count,
                    "success_rate": source.success_rate,
                }

            with open(self.schedule_file, "w") as f:
                json.dump(schedule_data, f, indent=2)

            logger.info("Saved schedule data")

        except Exception as e:
            logger.error(f"Error saving schedule: {e}")

    def get_due_sources(
        self, priority: Optional[Priority] = None
    ) -> List[ScheduledSource]:
        """Get sources that are due for crawling"""
        due_sources = [s for s in self.sources if s.is_due()]

        if priority:
            due_sources = [s for s in due_sources if s.priority == priority]

        # Sort by priority (daily first, then weekly, then monthly)
        # Within same priority, sort by success rate and threshold
        def sort_key(source: ScheduledSource) -> Tuple[int, float, float]:
            priority_order = {
                Priority.DAILY: 0,
                Priority.WEEKLY: 1,
                Priority.MONTHLY: 2,
            }
            return (
                priority_order[source.priority],
                -source.success_rate,
                -source.threshold,
            )

        due_sources.sort(key=sort_key)
        return due_sources

    def execute_crawl(self, source: ScheduledSource, dry_run: bool = False) -> bool:
        """Execute crawling for a specific source"""
        try:
            # Determine URL file based on source category
            url_file_map = {
                "rss_feeds": "urls_tier1_premium.txt",
                "technical_blogs": "urls_technical_blogs.txt",
                "github_sources": "urls_github_strategies.txt",
                "academic_sources": "urls_academic_research.txt",
            }

            url_file = url_file_map.get(source.category)
            if not url_file:
                logger.error(f"No URL file mapping for category: {source.category}")
                source.update_after_crawl(False)
                return False

            # Build command for semantic crawler
            cmd_parts = [
                "python",
                "scripts/semantic_crawler.py",
                "--url-file",
                url_file,
                "--threshold",
                str(source.threshold),
                "--metadata-output",
                f'metadata/crawl_{source.name.lower().replace(" ", "_")}.json',
            ]

            # Add rate limiting from global settings
            if "default_rate_limit" in self.global_settings:
                cmd_parts.extend(
                    ["--rate-limit", str(self.global_settings["default_rate_limit"])]
                )

            # Add content requirements validation
            if source.content_requirements:
                cmd_parts.append("--validate-content-requirements")

            # Add dry run flag if specified
            if dry_run:
                cmd_parts.append("--dry-run")

            cmd = " ".join(cmd_parts)

            logger.info(f"Executing crawl for {source.name}: {cmd}")

            if not dry_run:
                # Execute the command
                import subprocess

                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

                # Check if crawl was successful
                success = result.returncode == 0

                if success:
                    logger.info(f"Successfully crawled {source.name}")
                else:
                    logger.error(f"Failed to crawl {source.name}: {result.stderr}")

                # Update source metrics
                source.update_after_crawl(success)

                return success
            else:
                logger.info(f"Dry run - would execute: {cmd}")
                return True

        except Exception as e:
            logger.error(f"Error executing crawl for {source.name}: {e}")
            source.update_after_crawl(False)
            return False

    def run_scheduled_crawls(
        self,
        priority: Optional[Priority] = None,
        max_sources: int = 10,
        dry_run: bool = False,
    ) -> Dict:
        """Run scheduled crawls for due sources"""
        due_sources = self.get_due_sources(priority)

        if not due_sources:
            logger.info("No sources due for crawling")
            return {"executed": 0, "successful": 0, "failed": 0}

        # Limit number of sources to process
        sources_to_process = due_sources[:max_sources]

        logger.info(f"Processing {len(sources_to_process)} sources")

        results = {"executed": 0, "successful": 0, "failed": 0}

        for source in sources_to_process:
            results["executed"] += 1

            if self.execute_crawl(source, dry_run):
                results["successful"] += 1
            else:
                results["failed"] += 1

        # Save schedule after processing
        if not dry_run:
            self.save_schedule()

        return results

    def show_schedule(self):
        """Display current schedule status"""
        print("\n📅 IntelForge Crawler Schedule Status")
        print("=" * 50)

        # Group sources by priority
        priority_groups = {}
        for source in self.sources:
            if source.priority not in priority_groups:
                priority_groups[source.priority] = []
            priority_groups[source.priority].append(source)

        for priority in [Priority.DAILY, Priority.WEEKLY, Priority.MONTHLY]:
            if priority in priority_groups:
                sources = priority_groups[priority]
                print(f"\n🔄 {priority.value.upper()} Sources ({len(sources)} total)")
                print("-" * 40)

                for source in sources:
                    due_status = "🟢 DUE" if source.is_due() else "⏳ SCHEDULED"
                    next_crawl = (
                        source.next_crawl.strftime("%Y-%m-%d %H:%M")
                        if source.next_crawl
                        else "Not set"
                    )
                    success_rate = (
                        f"{source.success_rate:.1%}"
                        if source.crawl_count > 0
                        else "N/A"
                    )

                    print(f"  {due_status} {source.name}")
                    print(f"    Next: {next_crawl}")
                    print(f"    Success: {success_rate} ({source.crawl_count} crawls)")
                    print(
                        f"    Quality: {source.quality} | Threshold: {source.threshold}"
                    )
                    print()

        # Summary statistics
        total_sources = len(self.sources)
        due_sources = len([s for s in self.sources if s.is_due()])

        print(f"📊 Summary: {due_sources}/{total_sources} sources due for crawling")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="IntelForge Crawler Scheduler")
    parser.add_argument(
        "--registry-file",
        default="config/source_registry.yaml",
        help="Path to source registry YAML file",
    )
    parser.add_argument(
        "--priority",
        choices=["daily", "weekly", "monthly"],
        help="Filter by priority level",
    )
    parser.add_argument(
        "--max-sources",
        type=int,
        default=10,
        help="Maximum number of sources to process",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running",
    )
    parser.add_argument(
        "--show-schedule", action="store_true", help="Display current schedule status"
    )

    args = parser.parse_args()

    try:
        scheduler = CrawlerScheduler(args.registry_file)

        if args.show_schedule:
            scheduler.show_schedule()
        else:
            priority = Priority(args.priority) if args.priority else None
            results = scheduler.run_scheduled_crawls(
                priority=priority, max_sources=args.max_sources, dry_run=args.dry_run
            )

            print("\n📊 Crawling Results:")
            print(f"  Executed: {results['executed']}")
            print(f"  Successful: {results['successful']}")
            print(f"  Failed: {results['failed']}")

            if results["executed"] > 0:
                success_rate = results["successful"] / results["executed"] * 100
                print(f"  Success Rate: {success_rate:.1f}%")

    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
