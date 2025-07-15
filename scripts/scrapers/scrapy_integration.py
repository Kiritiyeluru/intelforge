"""
Scrapy Integration Module - Bridge between Scrapy and Semantic Crawler
Provides function to run scrapy spider programmatically
"""

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .semantic_spider import SemanticSpider, SCRAPY_SETTINGS
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any


def run_scrapy_crawler(
    urls: List[str], 
    output_format='json',
    save_raw: bool = False,
    proxy_rotate: bool = False,
    max_retries: int = 3,
    ignore_robots: bool = False
) -> List[Dict[str, Any]]:
    """
    Run scrapy spider with trafilatura integration
    
    Args:
        urls: List of URLs to crawl
        output_format: Output format ('json', 'dict')
        save_raw: Save raw HTML content for debugging
        proxy_rotate: Enable proxy rotation for stealth crawling
        max_retries: Maximum number of retries for failed requests
        ignore_robots: Ignore robots.txt files
    
    Returns:
        List of extracted items
    """
    
    # Create temporary file for URLs
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        urls_file = f.name
    
    try:
        # Configure scrapy settings
        settings = get_project_settings()
        settings.setdict(SCRAPY_SETTINGS)
        
        # Phase 4 Production CLI Settings
        if ignore_robots:
            settings.set('ROBOTSTXT_OBEY', False)
        else:
            settings.set('ROBOTSTXT_OBEY', True)
        
        # Set retry settings
        settings.set('RETRY_TIMES', max_retries)
        settings.set('RETRY_HTTP_CODES', [500, 502, 503, 504, 522, 524, 408, 429])
        
        # Configure proxy rotation if enabled
        if proxy_rotate:
            settings.set('ROTATING_PROXY_LIST_PATH', 'config/proxy_pools.txt')
            settings.set('DOWNLOADER_MIDDLEWARES', {
                'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
                'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
            })
        
        # Create output file
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        output_file.close()
        
        # Configure feeds for output
        settings.set('FEEDS', {
            output_file.name: {
                'format': 'json',
                'overwrite': True
            }
        })
        
        # Create and run crawler
        process = CrawlerProcess(settings)
        process.crawl(SemanticSpider, urls_file=urls_file, save_raw=save_raw)
        process.start()
        
        # Read results
        results = []
        try:
            with open(output_file.name, 'r') as f:
                content = f.read().strip()
                if content:
                    # Handle both single objects and arrays
                    if content.startswith('['):
                        results = json.loads(content)
                    else:
                        # Line-delimited JSON
                        results = []
                        for line in content.split('\n'):
                            if line.strip():
                                results.append(json.loads(line))
        except (json.JSONDecodeError, FileNotFoundError):
            results = []
        
        # Cleanup
        Path(urls_file).unlink(missing_ok=True)
        Path(output_file.name).unlink(missing_ok=True)
        
        return results
        
    except Exception as e:
        # Cleanup on error
        Path(urls_file).unlink(missing_ok=True)
        raise e


def convert_scrapy_to_semantic_format(scrapy_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert scrapy items to semantic crawler format
    
    Args:
        scrapy_items: Items from scrapy spider
    
    Returns:
        Items in semantic crawler format
    """
    
    converted = []
    
    for item in scrapy_items:
        # Map scrapy fields to semantic crawler format
        semantic_item = {
            'url': item.get('url', ''),
            'title': item.get('title', ''),
            'content': item.get('content', ''),
            'content_length': item.get('content_length', 0),
            'extracted_at': item.get('scraped_at', ''),  # Map scraped_at to extracted_at
            'author': item.get('author', 'Unknown'),
            'site': item.get('site', ''),
            'extraction_method': item.get('extraction_method', 'trafilatura'),
            'content_hash': item.get('content_hash', '')
        }
        
        converted.append(semantic_item)
    
    return converted