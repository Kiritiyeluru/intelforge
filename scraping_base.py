#!/usr/bin/env python3
"""
Simple Base Scraping Framework for IntelForge

A minimalist scraping framework for personal algo trading research.
Focuses on simplicity, reliability, and ease of maintenance.

Usage:
    from scraping_base import BaseScraper
    
    class MyCustomScraper(BaseScraper):
        def scrape_content(self):
            # Your scraping logic here
            pass
"""

import hashlib
import logging
import os
import random
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse

import httpx
import yaml
from retrying import retry


class BaseScraper:
    """Simple base class for all scrapers with essential functionality."""
    
    # Basic user agents - real browser strings
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0",
    ]
    
    def __init__(self, config_path: str = "config/config.yaml", scraper_name: str = "base"):
        """Initialize the base scraper with configuration."""
        self.scraper_name = scraper_name
        self.config = self._load_config(config_path)
        self.session = httpx.Client(timeout=30.0)
        
        # Set up logging
        self._setup_logging()
        
        # Initialize storage
        self._setup_storage()
        
        self.logger.info(f"Initialized {scraper_name} scraper")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file with environment overrides."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Environment overrides
            if os.getenv('INTELFORGE_DRY_RUN'):
                config['options']['dry_run'] = True
            if os.getenv('INTELFORGE_VERBOSE'):
                config['options']['verbose_logging'] = True
                
            return config
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Invalid YAML in config: {e}")
            raise
    
    def _setup_logging(self):
        """Set up simple file-based logging."""
        log_dir = Path(self.config['paths']['log_file'])
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"{self.scraper_name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.DEBUG if self.config['options']['verbose_logging'] else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(f"intelforge.{self.scraper_name}")
    
    def _setup_storage(self):
        """Set up SQLite database for structured data."""
        db_path = Path(self.config['paths']['output_dir']) / "scraped_data.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with basic schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraped_content (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE,
                    title TEXT,
                    content TEXT,
                    source TEXT,
                    content_hash TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            conn.commit()
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent string."""
        return random.choice(self.USER_AGENTS)
    
    def _random_delay(self, min_delay: int = 2, max_delay: int = 5):
        """Add random delay between requests."""
        delay = random.uniform(min_delay, max_delay)
        self.logger.debug(f"Waiting {delay:.2f} seconds...")
        time.sleep(delay)
    
    def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            # Use a generic user agent for robots.txt checking
            allowed = rp.can_fetch("*", url)
            
            if not allowed:
                self.logger.warning(f"URL blocked by robots.txt: {url}")
            
            return allowed
        except Exception as e:
            self.logger.warning(f"Could not check robots.txt for {url}: {e}")
            return True  # Default to allowed if can't check
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content for deduplication."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def _is_duplicate(self, url: str, content_hash: str) -> bool:
        """Check if content already exists in database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM scraped_content WHERE url = ? OR content_hash = ?",
                (url, content_hash)
            )
            return cursor.fetchone()[0] > 0
    
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def _make_request(self, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic."""
        headers = kwargs.get('headers', {})
        headers.update({
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        kwargs['headers'] = headers
        
        self.logger.debug(f"Making request to: {url}")
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        
        return response
    
    def save_content(self, url: str, title: str, content: str, metadata: Dict = None):
        """Save scraped content to database and markdown file."""
        if not content.strip():
            self.logger.warning(f"Empty content for {url}, skipping...")
            return
        
        content_hash = self._calculate_content_hash(content)
        
        # Check for duplicates
        if self._is_duplicate(url, content_hash):
            self.logger.info(f"Duplicate content found for {url}, skipping...")
            return
        
        if self.config['options']['dry_run']:
            self.logger.info(f"DRY RUN: Would save content from {url}")
            return
        
        # Save to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO scraped_content 
                (url, title, content, source, content_hash, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (url, title, content, self.scraper_name, content_hash, 
                  yaml.dump(metadata) if metadata else None))
            conn.commit()
        
        # Save to markdown file
        self._save_markdown(url, title, content, metadata)
        
        self.logger.info(f"Saved content: {title} ({len(content)} chars)")
    
    def _save_markdown(self, url: str, title: str, content: str, metadata: Dict = None):
        """Save content as Obsidian-compatible markdown file."""
        # Create filename from title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]  # Limit filename length
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{safe_title}_{timestamp}.md"
        
        output_dir = Path(self.config['paths']['output_dir']) / self.scraper_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = output_dir / filename
        
        # Create markdown with frontmatter
        frontmatter = {
            'source': self.scraper_name,
            'url': url,
            'title': title,
            'date': datetime.now().isoformat(),
            'content_hash': self._calculate_content_hash(content),
            'tags': ['algo-trading', 'research', self.scraper_name]
        }
        
        if metadata:
            frontmatter.update(metadata)
        
        markdown_content = "---\n"
        markdown_content += yaml.dump(frontmatter, default_flow_style=False)
        markdown_content += "---\n\n"
        markdown_content += f"# {title}\n\n"
        markdown_content += content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        self.logger.debug(f"Saved markdown: {filepath}")
    
    def scrape_url(self, url: str) -> Optional[Dict]:
        """
        Scrape a single URL. Override this method in subclasses.
        
        Returns:
            Dict with keys: url, title, content, metadata
        """
        if not self._check_robots_txt(url):
            return None
        
        try:
            response = self._make_request(url)
            
            # Basic content extraction - override in subclasses
            title = "Scraped Content"
            content = response.text
            metadata = {'status_code': response.status_code}
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata
            }
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
    
    def scrape_urls(self, urls: List[str]):
        """Scrape multiple URLs with delays."""
        self.logger.info(f"Starting to scrape {len(urls)} URLs...")
        
        for i, url in enumerate(urls):
            try:
                result = self.scrape_url(url)
                if result:
                    self.save_content(
                        result['url'],
                        result['title'],
                        result['content'],
                        result['metadata']
                    )
                
                # Add delay between requests (except for last URL)
                if i < len(urls) - 1:
                    self._random_delay()
                    
            except Exception as e:
                self.logger.error(f"Error processing URL {url}: {e}")
                continue
        
        self.logger.info(f"Finished scraping {len(urls)} URLs")
    
    def close(self):
        """Clean up resources."""
        if hasattr(self, 'session'):
            self.session.close()
        self.logger.info(f"Closed {self.scraper_name} scraper")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Simple test
    with BaseScraper(scraper_name="test") as scraper:
        test_urls = ["https://httpbin.org/html"]
        scraper.scrape_urls(test_urls)