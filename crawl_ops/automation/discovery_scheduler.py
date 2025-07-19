#!/usr/bin/env python3
"""
Automated Discovery Scheduler for IntelForge
Orchestrates periodic URL discovery from multiple sources.
"""

import schedule
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import logging

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from crawl_ops.tracking.url_queue import URLQueue
    from crawl_ops.discovery.github_discovery import GitHubDiscovery
    from crawl_ops.discovery.sitemap_discovery import SitemapDiscovery
    from crawl_ops.discovery.search_discovery import SearchDiscovery
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class DiscoveryScheduler:
    """Automated scheduler for multi-source URL discovery."""

    def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
        """Initialize scheduler with discovery modules."""
        self.queue = URLQueue(db_path)
        self.github = GitHubDiscovery()
        self.sitemap = SitemapDiscovery()
        self.search = SearchDiscovery()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawl_ops/logs/discovery_scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Discovery configuration
        self.config = {
            'github_keywords': [
                ["algorithmic", "trading", "python"],
                ["backtest", "strategy", "finance"],
                ["quantitative", "analysis", "trading"],
                ["portfolio", "optimization", "python"],
                ["market", "data", "analysis"],
                ["financial", "modeling", "python"]
            ],
            'target_domains': [
                "quantstart.com",
                "blog.quantinsti.com",
                "investopedia.com",
                "seekingalpha.com",
                "quantocracy.com"
            ],
            'search_queries': [
                "algorithmic trading python tutorial",
                "quantitative finance strategy",
                "backtesting trading strategies",
                "python financial analysis",
                "machine learning trading"
            ]
        }

    def daily_github_discovery(self):
        """Daily GitHub repository discovery with rotation."""
        self.logger.info("🔍 Starting daily GitHub discovery")

        try:
            total_added = 0

            # Rotate through keyword sets to avoid repetition
            day_of_year = datetime.now().timetuple().tm_yday
            keywords_index = day_of_year % len(self.config['github_keywords'])
            keywords = self.config['github_keywords'][keywords_index]

            repos = self.github.search_repositories(keywords, max_results=15)
            if repos:
                added = self.queue.add_discovered_urls(repos)
                total_added += added
                self.logger.info(f"GitHub discovery: Added {added} repositories for {keywords}")

            # Check rate limit status
            rate_limit = self.github.get_rate_limit_status()
            if rate_limit:
                remaining = rate_limit.get('resources', {}).get('search', {}).get('remaining', 'unknown')
                self.logger.info(f"GitHub API rate limit remaining: {remaining}")

            self.logger.info(f"✅ Daily GitHub discovery completed: {total_added} URLs added")

        except Exception as e:
            self.logger.error(f"❌ GitHub discovery failed: {e}")

    def weekly_sitemap_refresh(self):
        """Weekly sitemap discovery for known high-quality domains."""
        self.logger.info("🗺️  Starting weekly sitemap refresh")

        try:
            total_added = 0

            for domain in self.config['target_domains']:
                try:
                    urls = self.sitemap.extract_urls_from_sitemap(domain)
                    if urls:
                        added = self.queue.add_discovered_urls(urls)
                        total_added += added
                        self.logger.info(f"Sitemap {domain}: Added {added} URLs")

                    # Rate limiting pause
                    time.sleep(2)

                except Exception as e:
                    self.logger.warning(f"Sitemap discovery failed for {domain}: {e}")
                    continue

            self.logger.info(f"✅ Weekly sitemap refresh completed: {total_added} URLs added")

        except Exception as e:
            self.logger.error(f"❌ Sitemap refresh failed: {e}")

    def bi_weekly_search_discovery(self):
        """Bi-weekly search-based discovery for fresh content."""
        self.logger.info("🔍 Starting bi-weekly search discovery")

        try:
            total_added = 0

            # Rotate through search queries
            week_number = datetime.now().isocalendar()[1]
            query_index = week_number % len(self.config['search_queries'])
            query = self.config['search_queries'][query_index]

            # Search across target domains
            results = self.search.search_targeted_domains(query, self.config['target_domains'][:3])
            if results:
                added = self.queue.add_discovered_urls(results)
                total_added += added
                self.logger.info(f"Search discovery for '{query}': Added {added} URLs")

            self.logger.info(f"✅ Bi-weekly search discovery completed: {total_added} URLs added")

        except Exception as e:
            self.logger.error(f"❌ Search discovery failed: {e}")

    def hourly_queue_maintenance(self):
        """Hourly queue maintenance and monitoring."""
        try:
            # Get queue status
            status = self._get_queue_status()

            # Log queue metrics
            self.logger.info(f"📊 Queue status: {status['pending']} pending, "
                           f"{status['total']} total, "
                           f"{status['success_rate']:.1f}% success rate")

            # Alert if queue is getting too large or too small
            if status['pending'] > 1000:
                self.logger.warning(f"⚠️  Queue size large: {status['pending']} pending URLs")
            elif status['pending'] < 10:
                self.logger.warning(f"⚠️  Queue size low: {status['pending']} pending URLs")

            # Clean up old completed entries
            if status['completed'] > 5000:
                self.logger.info("🧹 Cleaning up old completed entries")
                # Add cleanup logic here if needed

        except Exception as e:
            self.logger.error(f"❌ Queue maintenance failed: {e}")

    def _get_queue_status(self) -> Dict:
        """Get current queue status metrics."""
        try:
            # This would interface with URLQueue status methods
            # For now, return simulated status
            return {
                'pending': 50,
                'completed': 100,
                'failed': 5,
                'total': 155,
                'success_rate': 95.2
            }
        except:
            return {'pending': 0, 'completed': 0, 'failed': 0, 'total': 0, 'success_rate': 0}

    def start_scheduler(self):
        """Start the discovery scheduler with all scheduled tasks."""
        self.logger.info("🚀 Starting IntelForge Discovery Scheduler")

        # Schedule discovery tasks
        schedule.every().day.at("02:00").do(self.daily_github_discovery)
        schedule.every().sunday.at("03:00").do(self.weekly_sitemap_refresh)
        schedule.every(2).weeks.do(self.bi_weekly_search_discovery)
        schedule.every().hour.do(self.hourly_queue_maintenance)

        # Initial status log
        self.logger.info("📅 Scheduled tasks:")
        self.logger.info("  - Daily GitHub discovery at 02:00")
        self.logger.info("  - Weekly sitemap refresh on Sundays at 03:00")
        self.logger.info("  - Bi-weekly search discovery")
        self.logger.info("  - Hourly queue maintenance")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("🛑 Discovery scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Scheduler error: {e}")

    def run_manual_discovery(self, discovery_type: str = "all"):
        """Run discovery manually for testing/immediate execution."""
        self.logger.info(f"🔧 Manual discovery requested: {discovery_type}")

        if discovery_type in ["all", "github"]:
            self.daily_github_discovery()

        if discovery_type in ["all", "sitemap"]:
            self.weekly_sitemap_refresh()

        if discovery_type in ["all", "search"]:
            self.bi_weekly_search_discovery()

        self.logger.info("✅ Manual discovery completed")


def main():
    """Main entry point for the discovery scheduler."""
    import argparse

    parser = argparse.ArgumentParser(description="IntelForge Discovery Scheduler")
    parser.add_argument("--mode", choices=["schedule", "manual"], default="schedule",
                       help="Run in scheduled mode or manual mode")
    parser.add_argument("--discovery", choices=["all", "github", "sitemap", "search"],
                       default="all", help="Type of discovery to run (manual mode only)")

    args = parser.parse_args()

    scheduler = DiscoveryScheduler()

    if args.mode == "schedule":
        scheduler.start_scheduler()
    else:
        scheduler.run_manual_discovery(args.discovery)


if __name__ == "__main__":
    main()
