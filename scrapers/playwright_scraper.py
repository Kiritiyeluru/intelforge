#!/usr/bin/env python3
"""
Playwright Scraper for IntelForge

A high-performance browser scraper using Playwright + base framework.
Designed for JavaScript-heavy financial sites that require browser automation.

Usage:
    python playwright_scraper.py [--dry-run] [--url URL] [--headless] [--limit N]

Example:
    python playwright_scraper.py --dry-run --url "https://finviz.com" --headless
"""

import argparse
import asyncio
import os
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright, Browser, Page
from dotenv import load_dotenv

from scripts.scraping_base import BaseScraper


class PlaywrightScraper(BaseScraper):
    """High-performance browser scraper using Playwright + base framework."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Playwright scraper."""
        super().__init__(config_path, scraper_name="playwright")
        
        # Load environment variables
        load_dotenv()
        
        # Playwright configuration
        self.browser = None
        self.context = None
        self.headless = True
        self.timeout = 30000  # 30 seconds
        
        # Site-specific configurations for financial sites
        self.site_configs = {
            'finviz.com': {
                'selectors': {
                    'title': 'title',
                    'content': '.screener-table tr, .quote-header, .fullview-title',
                    'data_table': '.screener-table'
                },
                'wait_for': '.screener-table',
                'scroll_behavior': 'lazy_load'
            },
            'yahoo.com': {
                'selectors': {
                    'title': 'h1',
                    'content': '[data-module] p, [data-module] span, .quote-summary',
                    'price_data': '[data-symbol] span'
                },
                'wait_for': '[data-symbol]',
                'scroll_behavior': 'infinite_scroll'
            },
            'seeking alpha.com': {
                'selectors': {
                    'title': 'h1[data-test-id="post-title"]',
                    'content': '[data-test-id="content-container"] p',
                    'author': '[data-test-id="author-name"]'
                },
                'wait_for': '[data-test-id="content-container"]',
                'scroll_behavior': 'static'
            }
        }
    
    async def _initialize_browser(self, headless: bool = True):
        """Initialize Playwright browser with optimized settings."""
        try:
            self.playwright = await async_playwright().start()
            
            # Use Chromium with stealth settings
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu'
                ]
            )
            
            # Create context with realistic browser settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                accept_downloads=False,
                java_script_enabled=True
            )
            
            # Set reasonable timeouts
            self.context.set_default_timeout(self.timeout)
            
            self.logger.info("Playwright browser initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Playwright browser: {e}")
            raise
    
    async def _create_page(self) -> Page:
        """Create a new page with anti-detection measures."""
        if not self.context:
            await self._initialize_browser()
        
        page = await self.context.new_page()
        
        # Add basic anti-detection
        await page.add_init_script("""
            // Override webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)
        
        return page
    
    def _get_site_config(self, url: str) -> Dict:
        """Get site-specific configuration."""
        domain = urlparse(url).netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Check for exact match or partial match
        for site_domain, config in self.site_configs.items():
            if site_domain in domain:
                return config
        
        # Default configuration
        return {
            'selectors': {
                'title': 'h1, title',
                'content': 'p, article p, .content p, .post-content p, div[data-test] p',
                'data_table': 'table, .table, [role="table"]'
            },
            'wait_for': 'body',
            'scroll_behavior': 'static'
        }
    
    async def _wait_for_content(self, page: Page, config: Dict):
        """Wait for site-specific content to load."""
        try:
            wait_selector = config.get('wait_for', 'body')
            await page.wait_for_selector(wait_selector, timeout=self.timeout)
            
            # Additional wait for dynamic content
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            self.logger.warning(f"Content wait timeout: {e}")
    
    async def _handle_scroll_behavior(self, page: Page, config: Dict):
        """Handle different scroll behaviors for dynamic content."""
        scroll_behavior = config.get('scroll_behavior', 'static')
        
        if scroll_behavior == 'lazy_load':
            # Scroll to trigger lazy loading
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
        elif scroll_behavior == 'infinite_scroll':
            # Simulate infinite scroll
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)
                
        # Static: no additional scrolling needed
    
    async def _extract_content_from_page(self, page: Page, url: str) -> Optional[Dict]:
        """Extract content from a single page."""
        try:
            config = self._get_site_config(url)
            
            # Wait for content to load
            await self._wait_for_content(page, config)
            
            # Handle scroll behavior
            await self._handle_scroll_behavior(page, config)
            
            # Extract title
            title_selector = config['selectors']['title']
            title_element = await page.query_selector(title_selector)
            if title_element:
                title = await title_element.inner_text()
                title = title.strip()
            else:
                title = await page.title()
            
            # Extract main content
            content_selector = config['selectors']['content']
            content_elements = await page.query_selector_all(content_selector)
            
            content_texts = []
            for element in content_elements:
                try:
                    text = await element.inner_text()
                    if text and len(text.strip()) > 20:  # Skip very short texts
                        content_texts.append(text.strip())
                except:
                    continue
            
            content = '\n\n'.join(content_texts)
            
            # Check if content is relevant
            if not self._is_relevant_content(title, content):
                self.logger.debug(f"Content not relevant: {url}")
                return None
            
            # Extract metadata
            metadata = {
                'site': urlparse(url).netloc,
                'extraction_method': 'playwright',
                'content_length': len(content),
                'page_title': await page.title(),
                'final_url': page.url,  # In case of redirects
                'viewport': await page.viewport_size(),
                'user_agent': await page.evaluate('navigator.userAgent')
            }
            
            # Try to extract data tables if present
            if 'data_table' in config['selectors']:
                try:
                    table_selector = config['selectors']['data_table']
                    table_elements = await page.query_selector_all(table_selector)
                    if table_elements:
                        metadata['has_data_tables'] = len(table_elements)
                except:
                    pass
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _is_relevant_content(self, title: str, content: str) -> bool:
        """Check if content is relevant based on keywords."""
        # Use the same relevance check as web scraper
        text_to_check = f"{title} {content}".lower()
        
        # Financial/trading keywords
        keywords = [
            'trading', 'algorithm', 'strategy', 'finance', 'stock',
            'portfolio', 'investment', 'market', 'quant', 'backtest',
            'indicator', 'analysis', 'price', 'chart', 'data'
        ]
        
        # Must contain at least one keyword
        return any(keyword in text_to_check for keyword in keywords)
    
    async def scrape_url(self, url: str, headless: bool = True) -> Optional[Dict]:
        """Scrape a single URL using Playwright."""
        if not self._check_robots_txt(url):
            return None
        
        try:
            if not self.browser:
                await self._initialize_browser(headless)
            
            page = await self._create_page()
            
            try:
                # Navigate to URL
                self.logger.info(f"Navigating to: {url}")
                response = await page.goto(url, wait_until='domcontentloaded')
                
                if not response or response.status >= 400:
                    self.logger.warning(f"HTTP {response.status if response else 'No response'} for {url}")
                    return None
                
                # Extract content
                result = await self._extract_content_from_page(page, url)
                return result
                
            finally:
                await page.close()
                
        except Exception as e:
            self.logger.error(f"Error scraping {url}: {e}")
            return None
    
    async def scrape_urls(self, urls: List[str], headless: bool = True):
        """Scrape multiple URLs with Playwright."""
        self.logger.info(f"Starting to scrape {len(urls)} URLs with Playwright...")
        
        try:
            await self._initialize_browser(headless)
            
            for i, url in enumerate(urls):
                try:
                    result = await self.scrape_url(url, headless)
                    if result:
                        self.save_content(
                            result['url'],
                            result['title'],
                            result['content'],
                            result['metadata']
                        )
                    
                    # Add delay between requests
                    if i < len(urls) - 1:
                        self._random_delay(3, 5)  # Longer delays for browser automation
                        
                except Exception as e:
                    self.logger.error(f"Error processing URL {url}: {e}")
                    continue
            
        finally:
            await self._cleanup()
        
        self.logger.info(f"Finished scraping {len(urls)} URLs")
    
    async def _cleanup(self):
        """Clean up Playwright resources."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
    
    def close(self):
        """Clean up resources synchronously."""
        try:
            # Run cleanup in event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, schedule cleanup
                loop.create_task(self._cleanup())
            else:
                # Run cleanup directly
                loop.run_until_complete(self._cleanup())
        except Exception as e:
            self.logger.warning(f"Error during sync cleanup: {e}")
        
        # Call parent cleanup
        super().close()


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Playwright Scraper for IntelForge")
    parser.add_argument('--dry-run', action='store_true', help="Run in dry-run mode")
    parser.add_argument('--url', type=str, help="Specific URL to scrape")
    parser.add_argument('--urls-file', type=str, help="File containing URLs to scrape (one per line)")
    parser.add_argument('--headless', action='store_true', default=True, help="Run in headless mode")
    parser.add_argument('--show-browser', action='store_true', help="Show browser (non-headless mode)")
    parser.add_argument('--config', type=str, default="config/config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    # Set dry-run mode if specified
    if args.dry_run:
        os.environ['INTELFORGE_DRY_RUN'] = 'true'
    
    # Determine headless mode
    headless = args.headless and not args.show_browser
    
    async def run_scraper():
        scraper = PlaywrightScraper(config_path=args.config)
        
        try:
            if args.url:
                # Scrape specific URL
                result = await scraper.scrape_url(args.url, headless)
                if result:
                    scraper.save_content(
                        result['url'],
                        result['title'],
                        result['content'],
                        result['metadata']
                    )
                    print(f"Scraped: {result['title']}")
                else:
                    print("No relevant content found or error occurred")
                    
            elif args.urls_file:
                # Scrape URLs from file
                try:
                    with open(args.urls_file, 'r') as f:
                        urls = [line.strip() for line in f if line.strip()]
                    await scraper.scrape_urls(urls, headless)
                except FileNotFoundError:
                    print(f"File not found: {args.urls_file}")
                    return
                    
            else:
                # Example usage
                example_urls = [
                    "https://finviz.com/screener.ashx?v=111&f=cap_mega",
                    "https://finance.yahoo.com/quote/SPY"
                ]
                print("No URL specified. Running example scraping...")
                await scraper.scrape_urls(example_urls, headless)
                
        finally:
            scraper.close()
    
    try:
        asyncio.run(run_scraper())
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()