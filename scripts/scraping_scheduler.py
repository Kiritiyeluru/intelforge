#!/usr/bin/env python3
"""
Simple Scraping Scheduler for IntelForge

A minimal scheduler using Python schedule library for automated scraping.
Runs configured scrapers on a schedule with basic error handling.

Usage:
    python scraping_scheduler.py [--config CONFIG] [--once] [--daemon]

Example:
    python scraping_scheduler.py --daemon  # Run continuously
    python scraping_scheduler.py --once    # Run all jobs once and exit
"""

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import schedule
import yaml
from dotenv import load_dotenv

# Import our scrapers
from reddit_scraper import RedditScraper
from github_scraper import GitHubScraper
from web_scraper import WebScraper


class ScrapingScheduler:
    """Simple scheduler for automated scraping."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the scheduler."""
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_logging()
        
        # Schedule configuration
        self.schedule_config = {
            'reddit': {
                'interval': 'daily',
                'time': '09:00',  # 9 AM
                'enabled': True
            },
            'github': {
                'interval': 'weekly',
                'day': 'monday',
                'time': '10:00',  # 10 AM on Mondays
                'enabled': True
            },
            'web': {
                'interval': 'daily',
                'time': '14:00',  # 2 PM
                'enabled': True
            }
        }
        
        self.logger.info("Scraping scheduler initialized")
    
    def _load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def _setup_logging(self):
        """Set up logging for the scheduler."""
        log_dir = Path(self.config['paths']['log_file'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("intelforge.scheduler")
    
    def run_reddit_scraper(self):
        """Run the Reddit scraper."""
        self.logger.info("Starting Reddit scraping job...")
        try:
            with RedditScraper(self.config_path) as scraper:
                scraper.scrape_all_subreddits()
            self.logger.info("Reddit scraping job completed successfully")
        except Exception as e:
            self.logger.error(f"Reddit scraping job failed: {e}")
    
    def run_github_scraper(self):
        """Run the GitHub scraper."""
        self.logger.info("Starting GitHub scraping job...")
        try:
            with GitHubScraper(self.config_path) as scraper:
                scraper.scrape_all_queries()
            self.logger.info("GitHub scraping job completed successfully")
        except Exception as e:
            self.logger.error(f"GitHub scraping job failed: {e}")
    
    def run_web_scraper(self):
        """Run the web scraper."""
        self.logger.info("Starting web scraping job...")
        try:
            with WebScraper(self.config_path) as scraper:
                scraper.scrape_all_sites()
            self.logger.info("Web scraping job completed successfully")
        except Exception as e:
            self.logger.error(f"Web scraping job failed: {e}")
    
    def setup_schedules(self):
        """Set up the scraping schedules."""
        self.logger.info("Setting up scraping schedules...")
        
        # Reddit scraper - daily at 9 AM
        if self.schedule_config['reddit']['enabled']:
            schedule.every().day.at(self.schedule_config['reddit']['time']).do(self.run_reddit_scraper)
            self.logger.info(f"Reddit scraper scheduled daily at {self.schedule_config['reddit']['time']}")
        
        # GitHub scraper - weekly on Monday at 10 AM
        if self.schedule_config['github']['enabled']:
            schedule.every().monday.at(self.schedule_config['github']['time']).do(self.run_github_scraper)
            self.logger.info(f"GitHub scraper scheduled weekly on Monday at {self.schedule_config['github']['time']}")
        
        # Web scraper - daily at 2 PM
        if self.schedule_config['web']['enabled']:
            schedule.every().day.at(self.schedule_config['web']['time']).do(self.run_web_scraper)
            self.logger.info(f"Web scraper scheduled daily at {self.schedule_config['web']['time']}")
        
        # Show next scheduled jobs
        self._show_next_jobs()
    
    def _show_next_jobs(self):
        """Show information about next scheduled jobs."""
        jobs = schedule.get_jobs()
        if jobs:
            self.logger.info("Scheduled jobs:")
            for job in jobs:
                self.logger.info(f"  - {job.job_func.__name__}: next run at {job.next_run}")
        else:
            self.logger.warning("No jobs scheduled")
    
    def run_all_once(self):
        """Run all scrapers once and exit."""
        self.logger.info("Running all scrapers once...")
        
        if self.schedule_config['reddit']['enabled']:
            self.run_reddit_scraper()
        
        if self.schedule_config['github']['enabled']:
            self.run_github_scraper()
        
        if self.schedule_config['web']['enabled']:
            self.run_web_scraper()
        
        self.logger.info("All scraping jobs completed")
    
    def run_daemon(self):
        """Run the scheduler as a daemon."""
        self.setup_schedules()
        
        self.logger.info("Starting scheduler daemon... Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}")
    
    def generate_crontab(self):
        """Generate crontab entries for system cron scheduling."""
        python_path = sys.executable
        script_dir = Path(__file__).parent.absolute()
        
        cron_entries = []
        
        if self.schedule_config['reddit']['enabled']:
            time_parts = self.schedule_config['reddit']['time'].split(':')
            cron_entries.append(
                f"{time_parts[1]} {time_parts[0]} * * * cd {script_dir} && {python_path} reddit_scraper.py"
            )
        
        if self.schedule_config['github']['enabled']:
            time_parts = self.schedule_config['github']['time'].split(':')
            cron_entries.append(
                f"{time_parts[1]} {time_parts[0]} * * 1 cd {script_dir} && {python_path} github_scraper.py"
            )
        
        if self.schedule_config['web']['enabled']:
            time_parts = self.schedule_config['web']['time'].split(':')
            cron_entries.append(
                f"{time_parts[1]} {time_parts[0]} * * * cd {script_dir} && {python_path} web_scraper.py"
            )
        
        return cron_entries


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Scraping Scheduler for IntelForge")
    parser.add_argument('--config', type=str, default="config/config.yaml", help="Path to config file")
    parser.add_argument('--once', action='store_true', help="Run all jobs once and exit")
    parser.add_argument('--daemon', action='store_true', help="Run as daemon (default)")
    parser.add_argument('--crontab', action='store_true', help="Generate crontab entries and exit")
    parser.add_argument('--test', action='store_true', help="Test run with dry-run mode")
    
    args = parser.parse_args()
    
    # Set dry-run mode for testing
    if args.test:
        os.environ['INTELFORGE_DRY_RUN'] = 'true'
        print("Running in test mode (dry-run)")
    
    # Load environment variables
    load_dotenv()
    
    try:
        scheduler = ScrapingScheduler(config_path=args.config)
        
        if args.crontab:
            # Generate crontab entries
            entries = scheduler.generate_crontab()
            print("Add these entries to your crontab (crontab -e):")
            print()
            for entry in entries:
                print(entry)
            print()
            print("Note: Make sure to set up the full environment (PATH, etc.) in your crontab")
            
        elif args.once:
            # Run all jobs once
            scheduler.run_all_once()
            
        else:
            # Run as daemon (default)
            scheduler.run_daemon()
            
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()