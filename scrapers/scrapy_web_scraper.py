#!/usr/bin/env python3
"""
Scrapy Web Scraper Wrapper for IntelForge

A wrapper script to run the Scrapy web spider with proper configuration.
Replaces the original web_scraper.py with enterprise-grade Scrapy framework.

Usage:
    python scrapy_web_scraper.py [--dry-run] [--limit N] [--site SITE]

Example:
    python scrapy_web_scraper.py --limit 5 --site medium.com
"""

import argparse
import os
import sys
from pathlib import Path

# Add the Scrapy project to Python path
scrapy_project_path = Path(__file__).parent / "scrapy_project"
sys.path.insert(0, str(scrapy_project_path))

# Change to Scrapy project directory for proper config resolution
os.chdir(scrapy_project_path)

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from intelforge_scraping.spiders.web_spider import WebSpider


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Scrapy Web Scraper for IntelForge")
    parser.add_argument('--dry-run', action='store_true', help="Run in dry-run mode")
    parser.add_argument('--site', type=str, help="Specific site to scrape")
    parser.add_argument('--limit', type=int, default=10, help="Limit number of articles")
    parser.add_argument('--config', type=str, default="../../config/config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    # Set dry-run mode if specified
    if args.dry_run:
        os.environ['INTELFORGE_DRY_RUN'] = 'true'
        print("Running in dry-run mode")
    
    try:
        # Get Scrapy settings
        settings = get_project_settings()
        
        # Override settings based on arguments
        if args.limit:
            settings.set('CLOSESPIDER_ITEMCOUNT', args.limit)
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Configure spider with custom settings
        spider_kwargs = {
            'config_path': args.config
        }
        
        if args.site:
            # Filter to specific site
            spider_kwargs['target_sites'] = [args.site]
        
        # Start crawling
        print(f"Starting Scrapy web scraper...")
        print(f"Config: {args.config}")
        print(f"Limit: {args.limit}")
        if args.site:
            print(f"Site: {args.site}")
        
        process.crawl(WebSpider, **spider_kwargs)
        process.start()
        
        print("Scraping completed successfully!")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()