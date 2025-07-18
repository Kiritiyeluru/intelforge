# Scrapy settings for intelforge_scraping project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "intelforge_scraping"

SPIDER_MODULES = ["intelforge_scraping.spiders"]
NEWSPIDER_MODULE = "intelforge_scraping.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "IntelForge/2.0 (Algorithmic Trading Research Bot)"  # Disabled for fake-useragent

# Fake User-Agent settings
RANDOM_UA_PER_PROXY = True
RANDOM_UA_TYPE = "desktop"  # Options: 'desktop', 'mobile', 'tablet'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings (production-ready)
CONCURRENT_REQUESTS = 2  # Reduced for respectful crawling
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 5  # Increased for politeness
RANDOMIZE_DOWNLOAD_DELAY = 0.5  # 50% random delay variation
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 0.8
AUTOTHROTTLE_DEBUG = False

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "intelforge_scraping.middlewares.IntelforgeScrapingSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # Anti-detection middleware (ordered by priority)
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 350,
    "rotating_proxies.middlewares.RotatingProxyMiddleware": 360,
    "rotating_proxies.middlewares.BanDetectionMiddleware": 370,
    "intelforge_scraping.middlewares.StealthDownloaderMiddleware": 400,
    "intelforge_scraping.middlewares.NoDriverMiddleware": 401,
    "intelforge_scraping.middlewares.RateLimitingMiddleware": 420,  # Phase 4 rate limiting
    "intelforge_scraping.middlewares.IntelforgeScrapingDownloaderMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "intelforge_scraping.pipelines.ObsidianMarkdownPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

# Stealth and Anti-Detection Settings
STEALTH_ENABLED = True
NODRIVER_ENABLED = False  # Enable only for JavaScript-heavy sites

# Rotating Proxies Settings
ROTATING_PROXY_LIST_PATH = (
    "config/proxy_pools.txt"  # Path to proxy list file (optional)
)
ROTATING_PROXY_LOGSTATS_INTERVAL = 30  # Log stats every N seconds
ROTATING_PROXY_CLOSE_SPIDER_ON_BAN = False  # Don't close spider on ban
ROTATING_PROXY_PAGE_RETRY_TIMES = 5  # Retry times for banned proxies
ROTATING_PROXY_BACKOFF_BASE = 300  # Base backoff time in seconds
ROTATING_PROXY_BACKOFF_CAP = 3600  # Maximum backoff time in seconds

# Ban Detection Settings
BAN_CODE_RANGES = [
    (400, 499),  # Client errors
    (500, 599),  # Server errors
]

# Advanced headers for stealth
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}

# Production compliance and safety settings
DEPTH_LIMIT = 3  # Limit crawl depth to prevent infinite loops
CLOSESPIDER_TIMEOUT = 3600  # Close spider after 1 hour
CLOSESPIDER_ITEMCOUNT = 1000  # Close spider after 1000 items
CLOSESPIDER_PAGECOUNT = 5000  # Close spider after 5000 pages
CLOSESPIDER_ERRORCOUNT = 50  # Close spider after 50 errors

# Request timeout settings
DOWNLOAD_TIMEOUT = 30  # Request timeout in seconds
DOWNLOAD_MAXSIZE = 1048576  # Max download size: 1MB
DOWNLOAD_WARNSIZE = 33554432  # Warn at 32MB

# Retry settings
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Phase 4 Rate Limiting Enhancements
# Content-type filtering to block large files
ALLOWED_CONTENT_TYPES = [
    "text/html",
    "text/plain",
    "application/xhtml+xml",
    "application/xml",
    "text/xml",
]

# Max links per page limit to prevent crawl explosions
MAX_LINKS_PER_PAGE = 50

# Circuit breaker settings for failed domains
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5  # Failures before breaking circuit
CIRCUIT_BREAKER_TIMEOUT = 300  # Seconds to wait before retrying domain
CIRCUIT_BREAKER_SUCCESS_THRESHOLD = 3  # Successes needed to close circuit

# Global timeouts and limits
CONCURRENT_REQUESTS_PER_IP = 1  # Additional IP-based limiting
DOWNLOAD_FAIL_ON_DATALOSS = True  # Fail on incomplete downloads
RETRY_PRIORITY_ADJUST = -1

# Memory usage protection
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "logs/scrapy.log"
