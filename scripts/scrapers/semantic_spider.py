"""
Semantic Spider - Simplified Scrapy Spider with Trafilatura Integration
Replaces custom httpx/asyncio implementation with scrapy+trafilatura
"""

from pathlib import Path

import scrapy
import trafilatura
from scrapy.http import HtmlResponse


class SemanticSpider(scrapy.Spider):
    name = "semantic_crawler"

    def __init__(self, urls_file=None, save_raw=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.urls_file = urls_file or "urls.txt"
        self.save_raw = save_raw

        if self.save_raw:
            self.raw_html_dir = Path("./raw_html_debug")
            self.raw_html_dir.mkdir(exist_ok=True)

    def start_requests(self):
        """Generate requests from URL file"""
        urls_path = Path(self.urls_file)

        if not urls_path.exists():
            self.logger.error(f"URLs file not found: {self.urls_file}")
            return

        with open(urls_path, "r") as f:
            urls = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        self.logger.info(f"Processing {len(urls)} URLs from {self.urls_file}")

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        """Parse response - extract content directly using trafilatura"""

        # Save raw HTML if enabled
        if self.save_raw:
            import hashlib

            url_hash = hashlib.md5(response.url.encode()).hexdigest()
            raw_file = self.raw_html_dir / f"{url_hash}.html"
            with open(raw_file, "w", encoding="utf-8") as f:
                f.write(response.text)
            self.logger.info(f"Saved raw HTML to {raw_file}")

        # Only process HTML responses
        if not isinstance(response, HtmlResponse):
            self.logger.warning(f"Non-HTML response from {response.url}")
            return

        # Extract content directly using trafilatura
        self.logger.debug(f"Extracting content from {response.url}")

        # Get settings for trafilatura
        settings = self.crawler.settings
        content = trafilatura.extract(
            response.text,
            include_comments=settings.getbool("TRAFILATURA_INCLUDE_COMMENTS", False),
            include_tables=settings.getbool("TRAFILATURA_INCLUDE_TABLES", True),
            include_formatting=settings.getbool("TRAFILATURA_INCLUDE_FORMATTING", True),
            url=response.url,
        )

        self.logger.debug(f"Extracted content length: {len(content) if content else 0}")

        # Extract metadata if enabled
        metadata = None
        if settings.getbool("TRAFILATURA_EXTRACT_METADATA", True):
            metadata = trafilatura.extract_metadata(response.text)
            self.logger.debug(f"Extracted metadata: {metadata.title if metadata and metadata.title else 'No title'}")

        # Check content length requirement
        min_content_length = settings.getint("TRAFILATURA_MIN_CONTENT_LENGTH", 100)

        if content and len(content.strip()) >= min_content_length:
            # Create and yield the item
            item = {
                "url": response.url,
                "title": metadata.title if metadata and metadata.title else "Untitled",
                "content": content,
                "author": metadata.author if metadata and metadata.author else "Unknown",
                "date": metadata.date if metadata and metadata.date else None,
                "content_length": len(content),
                "extraction_method": "trafilatura",
                "site": response.url.split("/")[2],
            }

            self.logger.info(f"Yielding item from {response.url}: {item['title'][:50]}... ({len(content)} chars)")
            yield item
        else:
            content_length = len(content) if content else 0
            self.logger.warning(f"Content too short or empty from {response.url}: {content_length} chars (min: {min_content_length})")


# Scrapy settings for semantic spider
SCRAPY_SETTINGS = {
    "ITEM_PIPELINES": {
        "scripts.scrapers.trafilatura_middleware.TrafilaturaPipeline": 300,
    },
    "DOWNLOADER_MIDDLEWARES": {
        # Anti-detection middleware (ordered by priority)
        "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 350,
        # Proxy middleware will be added conditionally in scrapy_integration.py
        # TrafilaturaMiddleware removed - extraction now done in spider parse() method
    },
    "TRAFILATURA_INCLUDE_COMMENTS": False,
    "TRAFILATURA_INCLUDE_TABLES": True,
    "TRAFILATURA_INCLUDE_FORMATTING": True,
    "TRAFILATURA_EXTRACT_METADATA": True,
    "TRAFILATURA_MIN_CONTENT_LENGTH": 100,
    "ROBOTSTXT_OBEY": True,
    "CONCURRENT_REQUESTS": 2,  # Reduced for respectful crawling
    "DOWNLOAD_DELAY": 5,  # Increased for politeness
    "RANDOMIZE_DOWNLOAD_DELAY": 0.5,
    "AUTOTHROTTLE_ENABLED": True,
    "AUTOTHROTTLE_START_DELAY": 1,
    "AUTOTHROTTLE_MAX_DELAY": 10,
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 0.8,
    "AUTOTHROTTLE_DEBUG": False,
    # 'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'  # Disabled for fake-useragent
    # Fake User-Agent settings
    "RANDOM_UA_PER_PROXY": True,
    "RANDOM_UA_TYPE": "desktop",
    # Rotating Proxies Settings
    "ROTATING_PROXY_LIST_PATH": "config/proxy_pools.txt",
    "ROTATING_PROXY_LOGSTATS_INTERVAL": 30,
    "ROTATING_PROXY_CLOSE_SPIDER_ON_BAN": False,
    "ROTATING_PROXY_PAGE_RETRY_TIMES": 5,
    "ROTATING_PROXY_BACKOFF_BASE": 300,
    "ROTATING_PROXY_BACKOFF_CAP": 3600,
    # Ban Detection Settings
    "BAN_CODE_RANGES": [
        (400, 499),  # Client errors
        (500, 599),  # Server errors
    ],
    # Advanced headers for stealth
    "DEFAULT_REQUEST_HEADERS": {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    },
    # Production compliance and safety settings
    "DEPTH_LIMIT": 3,
    "CLOSESPIDER_TIMEOUT": 3600,
    "CLOSESPIDER_ITEMCOUNT": 1000,
    "CLOSESPIDER_PAGECOUNT": 5000,
    "CLOSESPIDER_ERRORCOUNT": 50,
    "DOWNLOAD_TIMEOUT": 30,
    "DOWNLOAD_MAXSIZE": 1048576,
    "DOWNLOAD_WARNSIZE": 33554432,
    "RETRY_TIMES": 3,
    "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429],
    "RETRY_PRIORITY_ADJUST": -1,
    "MEMUSAGE_ENABLED": True,
    "MEMUSAGE_LIMIT_MB": 2048,
    "MEMUSAGE_WARNING_MB": 1024,
    "LOG_LEVEL": "INFO",
    "LOG_FILE": "crawl_ops/logs/semantic_spider.log",
}
