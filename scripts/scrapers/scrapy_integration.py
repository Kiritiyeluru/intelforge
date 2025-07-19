"""
Scrapy Integration Module - Bridge between Scrapy and Semantic Crawler
Provides function to run scrapy spider programmatically
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from .semantic_spider import SCRAPY_SETTINGS, SemanticSpider


def run_scrapy_crawler(
    urls: List[str],
    output_format="json",
    save_raw: bool = False,
    proxy_rotate: bool = False,
    max_retries: int = 3,
    ignore_robots: bool = False,
    output_dir: str = None,
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
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for url in urls:
            f.write(f"{url}\n")
        urls_file = f.name

    try:
        # Configure scrapy settings
        settings = get_project_settings()
        settings.setdict(SCRAPY_SETTINGS)

        # Phase 4 Production CLI Settings
        if ignore_robots:
            settings.set("ROBOTSTXT_OBEY", False)
        else:
            settings.set("ROBOTSTXT_OBEY", True)

        # Set retry settings
        settings.set("RETRY_TIMES", max_retries)
        settings.set("RETRY_HTTP_CODES", [500, 502, 503, 504, 522, 524, 408, 429])

        # Configure proxy rotation if enabled
        if proxy_rotate:
            settings.set("ROTATING_PROXY_LIST_PATH", "config/proxy_pools.txt")
            # Get existing middlewares and add proxy middlewares
            existing_middlewares = settings.get("DOWNLOADER_MIDDLEWARES")
            proxy_middlewares = {
                "rotating_proxies.middlewares.RotatingProxyMiddleware": 360,
                "rotating_proxies.middlewares.BanDetectionMiddleware": 370,
            }
            # Merge middlewares
            combined_middlewares = {**existing_middlewares, **proxy_middlewares}
            settings.set("DOWNLOADER_MIDDLEWARES", combined_middlewares)

        # Configure output directory and file
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file_path = output_path / "scraped_data.jsonl"
        else:
            # Fallback to temporary file
            output_file = tempfile.NamedTemporaryFile(
                mode="w", suffix=".jsonl", delete=False
            )
            output_file.close()
            output_file_path = output_file.name

        # Configure feeds for output (use JSONL for better streaming)
        settings.set("FEEDS", {str(output_file_path): {"format": "jsonlines", "overwrite": True}})

        # Create and run crawler
        process = CrawlerProcess(settings)
        process.crawl(SemanticSpider, urls_file=urls_file, save_raw=save_raw)
        process.start()

        # Read results from JSONL file
        results = []
        try:
            with open(output_file_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        results.append(json.loads(line))
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not read results from {output_file_path}: {e}")
            results = []

        # Cleanup temporary files (keep output if output_dir specified)
        Path(urls_file).unlink(missing_ok=True)
        if not output_dir:
            Path(output_file_path).unlink(missing_ok=True)

        return results

    except Exception as e:
        # Cleanup on error
        Path(urls_file).unlink(missing_ok=True)
        raise e


def convert_scrapy_to_semantic_format(
    scrapy_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
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
            "url": item.get("url", ""),
            "title": item.get("title", ""),
            "content": item.get("content", ""),
            "content_length": item.get("content_length", 0),
            "extracted_at": item.get(
                "scraped_at", ""
            ),  # Map scraped_at to extracted_at
            "author": item.get("author", "Unknown"),
            "site": item.get("site", ""),
            "extraction_method": item.get("extraction_method", "trafilatura"),
            "content_hash": item.get("content_hash", ""),
        }

        converted.append(semantic_item)

    return converted
