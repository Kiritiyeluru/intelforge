"""
Scrapy middleware for URL deduplication and pre-crawl checking.
Integrates with URLTracker to prevent redundant crawling.
"""

from scrapy import signals
from scrapy.exceptions import IgnoreRequest
from scrapy.http import Request
from scrapy.utils.misc import load_object
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from ..tracking.url_tracker import URLTracker
from ..tracking.content_detector import ContentChangeDetector

logger = logging.getLogger(__name__)


class URLTrackingMiddleware:
    """
    Scrapy downloader middleware for URL tracking and deduplication.
    Checks URLs before downloading to prevent redundant crawls.
    """
    
    def __init__(self, 
                 tracker_db_path: str = "crawl_ops/tracking/url_tracker.db",
                 enabled: bool = True,
                 default_refresh_days: int = 30,
                 site_policies: Optional[Dict[str, int]] = None,
                 check_http_headers: bool = False):
        """
        Initialize URL tracking middleware.
        
        Args:
            tracker_db_path: Path to URL tracker database
            enabled: Whether middleware is enabled
            default_refresh_days: Default refresh interval in days
            site_policies: Site-specific refresh policies
            check_http_headers: Whether to check HTTP headers for changes
        """
        self.enabled = enabled
        self.tracker_db_path = tracker_db_path
        self.default_refresh_days = default_refresh_days
        self.site_policies = site_policies or {}
        self.check_http_headers = check_http_headers
        
        # Initialize components
        self.url_tracker = None
        self.content_detector = None
        
        # Statistics
        self.stats = {
            'urls_checked': 0,
            'urls_skipped': 0,
            'urls_allowed': 0,
            'new_urls': 0,
            'refresh_due': 0,
            'recently_scraped': 0,
            'retry_failed': 0,
            'http_header_checks': 0,
            'content_changes_detected': 0
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler."""
        settings = crawler.settings
        
        # Extract configuration from settings
        url_tracking_config = settings.get('URL_TRACKING', {})
        
        instance = cls(
            tracker_db_path=url_tracking_config.get(
                'database_path', 
                "crawl_ops/tracking/url_tracker.db"
            ),
            enabled=url_tracking_config.get('enabled', True),
            default_refresh_days=url_tracking_config.get('default_refresh_days', 30),
            site_policies=url_tracking_config.get('site_policies', {}),
            check_http_headers=url_tracking_config.get(
                'check_http_headers', False
            )
        )
        
        # Connect to spider signals
        crawler.signals.connect(
            instance.spider_opened, signal=signals.spider_opened
        )
        crawler.signals.connect(
            instance.spider_closed, signal=signals.spider_closed
        )
        
        return instance
    
    def spider_opened(self, spider):
        """Initialize when spider opens."""
        if not self.enabled:
            logger.info("URL tracking middleware disabled")
            return
        
        try:
            self.url_tracker = URLTracker(self.tracker_db_path)
            self.content_detector = ContentChangeDetector()
            logger.info(f"URL tracking middleware initialized with database: {self.tracker_db_path}")
            
            # Log configuration
            spider.logger.info(f"URL tracking configuration:")
            spider.logger.info(f"  - Default refresh days: {self.default_refresh_days}")
            spider.logger.info(f"  - Site policies: {self.site_policies}")
            spider.logger.info(f"  - HTTP header checking: {self.check_http_headers}")
            
        except Exception as e:
            logger.error(f"Failed to initialize URL tracking middleware: {e}")
            self.enabled = False
    
    def spider_closed(self, spider):
        """Cleanup when spider closes."""
        if self.url_tracker:
            # Log statistics
            spider.logger.info("URL tracking statistics:")
            for key, value in self.stats.items():
                spider.logger.info(f"  - {key}: {value}")
            
            # Calculate efficiency
            total_checked = self.stats['urls_checked']
            if total_checked > 0:
                skip_rate = (self.stats['urls_skipped'] / total_checked) * 100
                spider.logger.info(f"  - Skip rate: {skip_rate:.1f}%")
            
            # Close tracker
            self.url_tracker.close()
            self.url_tracker = None
    
    def process_request(self, request: Request, spider):
        """
        Process request before downloading.
        
        Args:
            request: Scrapy request object
            spider: Spider instance
            
        Returns:
            None to continue processing, or IgnoreRequest to skip
        """
        if not self.enabled or not self.url_tracker:
            return None
        
        url = request.url
        self.stats['urls_checked'] += 1
        
        try:
            # Check if URL should be crawled
            should_crawl, reason = self.url_tracker.should_crawl(
                url=url,
                force_refresh_days=self.default_refresh_days,
                site_specific_policies=self.site_policies
            )
            
            # Update statistics
            self.stats[reason] = self.stats.get(reason, 0) + 1
            
            if not should_crawl:
                self.stats['urls_skipped'] += 1
                spider.logger.debug(f"Skipping URL {url}: {reason}")
                raise IgnoreRequest(f"URL tracking: {reason}")
            else:
                self.stats['urls_allowed'] += 1
                
                # Add tracking metadata to request
                request.meta['crawl_reason'] = reason
                request.meta['url_tracking_enabled'] = True
                
                # Check HTTP headers if enabled and appropriate
                if (self.check_http_headers and reason == 'refresh_due'):
                    self._check_http_headers(request, spider)
                
                spider.logger.debug(f"Allowing URL {url}: {reason}")
        
        except IgnoreRequest:
            raise
        except Exception as e:
            spider.logger.error(f"Error in URL tracking middleware for {url}: {e}")
            # Allow crawl on error to be safe
            self.stats['urls_allowed'] += 1
            request.meta['url_tracking_error'] = str(e)
        
        return None
    
    def _check_http_headers(self, request: Request, spider):
        """
        Check HTTP headers for content changes.
        
        Args:
            request: Scrapy request object
            spider: Spider instance
        """
        try:
            url = request.url
            headers_info = self.content_detector.check_http_headers(url)
            
            if headers_info:
                self.stats['http_header_checks'] += 1
                
                # Get previous record for comparison
                url_record = self.url_tracker.get_url_record(url)
                
                if url_record:
                    # Compare with previous headers
                    old_etag = url_record.get('etag')
                    old_last_modified = url_record.get('last_modified')
                    
                    new_etag = headers_info.get('etag')
                    new_last_modified = headers_info.get('last_modified')
                    
                    # If headers indicate no change, could potentially skip
                    if (old_etag and new_etag and old_etag == new_etag) or \
                       (old_last_modified and new_last_modified and 
                        old_last_modified == new_last_modified):
                        spider.logger.debug(f"HTTP headers indicate no change for {url}")
                        request.meta['http_headers_unchanged'] = True
                    else:
                        spider.logger.debug(f"HTTP headers indicate change for {url}")
                        request.meta['http_headers_changed'] = True
                        self.stats['content_changes_detected'] += 1
                
                # Store header info for pipeline use
                request.meta['http_headers_info'] = headers_info
        
        except Exception as e:
            spider.logger.warning(f"Error checking HTTP headers for {request.url}: {e}")
    
    def process_exception(self, request: Request, exception, spider):
        """Handle exceptions during request processing."""
        if hasattr(request, 'meta') and request.meta.get('url_tracking_enabled'):
            spider.logger.debug(f"Exception in tracked URL {request.url}: {exception}")
        return None


class URLFilterMiddleware:
    """
    Additional middleware for URL filtering based on tracking history.
    """
    
    def __init__(self, 
                 min_quality_score: int = 0,
                 max_failed_attempts: int = 3,
                 blacklist_patterns: Optional[list] = None):
        """
        Initialize URL filter middleware.
        
        Args:
            min_quality_score: Minimum quality score to allow crawling
            max_failed_attempts: Maximum failed attempts before blacklisting
            blacklist_patterns: URL patterns to blacklist
        """
        self.min_quality_score = min_quality_score
        self.max_failed_attempts = max_failed_attempts
        self.blacklist_patterns = blacklist_patterns or []
        
        # Compile regex patterns
        import re
        self.compiled_patterns = [re.compile(pattern) for pattern in self.blacklist_patterns]
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance from crawler."""
        settings = crawler.settings
        url_tracking_config = settings.get('URL_TRACKING', {})
        filter_config = url_tracking_config.get('filtering', {})
        
        return cls(
            min_quality_score=filter_config.get('min_quality_score', 0),
            max_failed_attempts=filter_config.get('max_failed_attempts', 3),
            blacklist_patterns=filter_config.get('blacklist_patterns', [])
        )
    
    def process_request(self, request: Request, spider):
        """Filter requests based on URL tracking history."""
        url = request.url
        
        # Check blacklist patterns
        for pattern in self.compiled_patterns:
            if pattern.search(url):
                spider.logger.debug(f"URL {url} matches blacklist pattern")
                raise IgnoreRequest("URL matches blacklist pattern")
        
        # Additional filtering logic could be added here
        return None