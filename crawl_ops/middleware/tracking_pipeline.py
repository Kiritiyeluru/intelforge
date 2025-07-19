"""
Scrapy pipeline for recording crawled URLs and content tracking.
Integrates with URLTracker to maintain crawl history.
"""

from scrapy.exceptions import DropItem
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from ..tracking.url_tracker import URLTracker
from ..tracking.content_detector import ContentChangeDetector

logger = logging.getLogger(__name__)


class URLRecordingPipeline:
    """
    Scrapy item pipeline for recording successful crawls in URL tracker.
    """
    
    def __init__(self,
                 tracker_db_path: str = "crawl_ops/tracking/url_tracker.db",
                 enabled: bool = True,
                 quality_scoring: bool = True,
                 content_change_detection: bool = True):
        """
        Initialize URL recording pipeline.
        
        Args:
            tracker_db_path: Path to URL tracker database
            enabled: Whether pipeline is enabled
            quality_scoring: Whether to calculate quality scores
            content_change_detection: Whether to detect content changes
        """
        self.enabled = enabled
        self.tracker_db_path = tracker_db_path
        self.quality_scoring = quality_scoring
        self.content_change_detection = content_change_detection
        
        # Initialize components
        self.url_tracker = None
        self.content_detector = None
        
        # Statistics
        self.stats = {
            'items_processed': 0,
            'urls_recorded': 0,
            'urls_updated': 0,
            'content_changes_detected': 0,
            'quality_scores_calculated': 0,
            'recording_errors': 0
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler."""
        settings = crawler.settings
        url_tracking_config = settings.get('URL_TRACKING', {})
        
        return cls(
            tracker_db_path=url_tracking_config.get(
                'database_path',
                "crawl_ops/tracking/url_tracker.db"
            ),
            enabled=url_tracking_config.get('enabled', True),
            quality_scoring=url_tracking_config.get('quality_scoring', True),
            content_change_detection=url_tracking_config.get(
                'content_change_detection', True
            )
        )
    
    def open_spider(self, spider):
        """Initialize when spider opens."""
        if not self.enabled:
            spider.logger.info("URL recording pipeline disabled")
            return
        
        try:
            self.url_tracker = URLTracker(self.tracker_db_path)
            self.content_detector = ContentChangeDetector()
            spider.logger.info(f"URL recording pipeline initialized with database: {self.tracker_db_path}")
            
        except Exception as e:
            spider.logger.error(f"Failed to initialize URL recording pipeline: {e}")
            self.enabled = False
    
    def close_spider(self, spider):
        """Cleanup when spider closes."""
        if self.url_tracker:
            # Log statistics
            spider.logger.info("URL recording statistics:")
            for key, value in self.stats.items():
                spider.logger.info(f"  - {key}: {value}")
            
            # Close tracker
            self.url_tracker.close()
            self.url_tracker = None
    
    def process_item(self, item, spider):
        """
        Process crawled item and record in URL tracker.
        
        Args:
            item: Scraped item
            spider: Spider instance
            
        Returns:
            Processed item or raises DropItem
        """
        if not self.enabled or not self.url_tracker:
            return item
        
        self.stats['items_processed'] += 1
        
        try:
            # Extract required fields from item
            url = self._get_item_field(item, ['url', 'link', 'source_url'])
            content = self._get_item_field(item, ['content', 'text', 'body', 'description'])
            
            if not url:
                spider.logger.warning("Item missing URL field, skipping tracking")
                return item
            
            if not content:
                spider.logger.warning(f"Item {url} missing content field, skipping tracking")
                return item
            
            # Generate content hash
            content_hash = self.content_detector.generate_content_hash(content)
            
            # Calculate quality score if enabled
            quality_score = None
            if self.quality_scoring:
                quality_score = self.content_detector.estimate_content_quality(content)
                self.stats['quality_scores_calculated'] += 1
            
            # Detect content changes if enabled
            content_changed = False
            if self.content_change_detection:
                existing_record = self.url_tracker.get_url_record(url)
                if existing_record:
                    old_hash = existing_record.get('content_hash', '')
                    content_changed = self.content_detector.detect_content_change(url, content_hash)
                    if content_changed:
                        self.stats['content_changes_detected'] += 1
            
            # Extract additional metadata
            site = self._extract_site(url)
            extraction_method = self._get_item_field(item, ['extraction_method', 'extractor'])
            content_length = len(content) if content else 0
            
            # Get HTTP headers if available from request metadata
            response = getattr(item, 'response', None) if hasattr(item, 'response') else None
            etag = None
            last_modified = None
            response_code = 200
            
            if response:
                etag = response.headers.get('ETag', '').decode('utf-8') if response.headers.get('ETag') else None
                last_modified = response.headers.get('Last-Modified', '').decode('utf-8') if response.headers.get('Last-Modified') else None
                response_code = response.status
            
            # Extract tags if available
            tags = self._get_item_field(item, ['tags', 'categories', 'topics'])
            if isinstance(tags, str):
                tags = [tags]
            elif not isinstance(tags, list):
                tags = None
            
            # Record the crawl
            success = self.url_tracker.record_crawl(
                url=url,
                content_hash=content_hash,
                content_length=content_length,
                site=site,
                extraction_method=extraction_method or 'unknown',
                status='success',
                quality_score=quality_score,
                tags=tags,
                etag=etag,
                last_modified=last_modified,
                response_code=response_code
            )
            
            if success:
                # Check if this was a new URL or update
                existing_record = self.url_tracker.get_url_record(url)
                if existing_record and existing_record.get('scrape_count', 0) > 1:
                    self.stats['urls_updated'] += 1
                else:
                    self.stats['urls_recorded'] += 1
                
                # Add tracking metadata to item
                item['url_tracking'] = {
                    'content_hash': content_hash,
                    'quality_score': quality_score,
                    'content_changed': content_changed,
                    'site': site,
                    'tracked': True
                }
                
                spider.logger.debug(f"Recorded URL {url} in tracker (quality: {quality_score})")
            else:
                self.stats['recording_errors'] += 1
                spider.logger.warning(f"Failed to record URL {url} in tracker")
        
        except Exception as e:
            self.stats['recording_errors'] += 1
            spider.logger.error(f"Error recording URL in tracker: {e}")
            # Don't drop item on tracking error
        
        return item
    
    def _get_item_field(self, item, field_names: list) -> Optional[str]:
        """
        Get field value from item, trying multiple possible field names.
        
        Args:
            item: Scraped item
            field_names: List of possible field names to try
            
        Returns:
            Field value or None if not found
        """
        for field_name in field_names:
            if hasattr(item, 'get'):
                # Dictionary-like item
                value = item.get(field_name)
            else:
                # Object-like item
                value = getattr(item, field_name, None)
            
            if value:
                return str(value).strip()
        
        return None
    
    def _extract_site(self, url: str) -> str:
        """Extract site domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "unknown"


class ContentValidationPipeline:
    """
    Pipeline for validating content quality and filtering low-quality items.
    """
    
    def __init__(self,
                 min_content_length: int = 100,
                 min_quality_score: int = 20,
                 drop_duplicates: bool = True,
                 validate_encoding: bool = True):
        """
        Initialize content validation pipeline.
        
        Args:
            min_content_length: Minimum content length to accept
            min_quality_score: Minimum quality score to accept
            drop_duplicates: Whether to drop duplicate content
            validate_encoding: Whether to validate text encoding
        """
        self.min_content_length = min_content_length
        self.min_quality_score = min_quality_score
        self.drop_duplicates = drop_duplicates
        self.validate_encoding = validate_encoding
        
        # Track seen content hashes for duplicate detection
        self.seen_hashes = set()
        
        # Statistics
        self.stats = {
            'items_validated': 0,
            'items_dropped_length': 0,
            'items_dropped_quality': 0,
            'items_dropped_duplicates': 0,
            'items_dropped_encoding': 0,
            'items_passed': 0
        }
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create pipeline instance from crawler."""
        settings = crawler.settings
        url_tracking_config = settings.get('URL_TRACKING', {})
        validation_config = url_tracking_config.get('validation', {})
        
        return cls(
            min_content_length=validation_config.get('min_content_length', 100),
            min_quality_score=validation_config.get('min_quality_score', 20),
            drop_duplicates=validation_config.get('drop_duplicates', True),
            validate_encoding=validation_config.get('validate_encoding', True)
        )
    
    def close_spider(self, spider):
        """Log statistics when spider closes."""
        spider.logger.info("Content validation statistics:")
        for key, value in self.stats.items():
            spider.logger.info(f"  - {key}: {value}")
        
        # Calculate validation rates
        total_validated = self.stats['items_validated']
        if total_validated > 0:
            pass_rate = (self.stats['items_passed'] / total_validated) * 100
            spider.logger.info(f"  - Pass rate: {pass_rate:.1f}%")
    
    def process_item(self, item, spider):
        """
        Validate item content quality.
        
        Args:
            item: Scraped item
            spider: Spider instance
            
        Returns:
            Processed item or raises DropItem
        """
        self.stats['items_validated'] += 1
        
        # Get content for validation
        content = self._get_item_field(item, ['content', 'text', 'body', 'description'])
        
        if not content:
            # Allow items without content to pass (might be metadata-only)
            self.stats['items_passed'] += 1
            return item
        
        # Validate content length
        if len(content) < self.min_content_length:
            self.stats['items_dropped_length'] += 1
            raise DropItem(f"Content too short: {len(content)} < {self.min_content_length}")
        
        # Validate quality score if available
        url_tracking = getattr(item, 'url_tracking', None) or item.get('url_tracking', {})
        quality_score = url_tracking.get('quality_score')
        
        if quality_score is not None and quality_score < self.min_quality_score:
            self.stats['items_dropped_quality'] += 1
            raise DropItem(f"Quality score too low: {quality_score} < {self.min_quality_score}")
        
        # Check for duplicates
        if self.drop_duplicates:
            content_hash = url_tracking.get('content_hash')
            if content_hash:
                if content_hash in self.seen_hashes:
                    self.stats['items_dropped_duplicates'] += 1
                    raise DropItem(f"Duplicate content hash: {content_hash}")
                else:
                    self.seen_hashes.add(content_hash)
        
        # Validate encoding
        if self.validate_encoding:
            try:
                content.encode('utf-8')
            except UnicodeEncodeError:
                self.stats['items_dropped_encoding'] += 1
                raise DropItem("Invalid text encoding")
        
        self.stats['items_passed'] += 1
        return item
    
    def _get_item_field(self, item, field_names: list) -> Optional[str]:
        """Get field value from item, trying multiple possible field names."""
        for field_name in field_names:
            if hasattr(item, 'get'):
                value = item.get(field_name)
            else:
                value = getattr(item, field_name, None)
            
            if value:
                return str(value).strip()
        
        return None