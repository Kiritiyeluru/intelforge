"""
Trafilatura Middleware for Scrapy - Enhanced Content Extraction
Integrates trafilatura content extraction with Scrapy's processing pipeline
"""

import trafilatura
from scrapy.http import HtmlResponse
from scrapy.exceptions import NotConfigured
from scrapy.utils.python import to_bytes
from urllib.parse import urljoin


class TrafilaturaMiddleware:
    """Middleware that uses trafilatura for content extraction"""
    
    def __init__(self, settings=None):
        if not settings:
            raise NotConfigured('TrafilaturaMiddleware requires settings')
        
        self.include_comments = settings.getbool('TRAFILATURA_INCLUDE_COMMENTS', False)
        self.include_tables = settings.getbool('TRAFILATURA_INCLUDE_TABLES', True)
        self.include_formatting = settings.getbool('TRAFILATURA_INCLUDE_FORMATTING', True)
        self.extract_metadata = settings.getbool('TRAFILATURA_EXTRACT_METADATA', True)
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def process_response(self, request, response, spider):
        """Process response with trafilatura extraction"""
        if isinstance(response, HtmlResponse):
            # Extract content using trafilatura
            content = trafilatura.extract(
                response.text,
                include_comments=self.include_comments,
                include_tables=self.include_tables,
                include_formatting=self.include_formatting,
                url=response.url
            )
            
            # Extract metadata if enabled
            metadata = None
            if self.extract_metadata:
                metadata = trafilatura.extract_metadata(response.text)
            
            # Add extracted content to response meta
            response.meta['trafilatura_content'] = content
            response.meta['trafilatura_metadata'] = metadata
            
            # Create a structured item for the pipeline
            if content:
                response.meta['trafilatura_item'] = {
                    'url': response.url,
                    'title': metadata.title if metadata and metadata.title else 'Untitled',
                    'content': content,
                    'author': metadata.author if metadata and metadata.author else 'Unknown',
                    'date': metadata.date if metadata and metadata.date else None,
                    'content_length': len(content),
                    'extraction_method': 'trafilatura',
                    'site': response.url.split('/')[2]
                }
        
        return response


class TrafilaturaPipeline:
    """Pipeline for processing trafilatura-extracted content"""
    
    def __init__(self, settings=None):
        self.min_content_length = settings.getint('TRAFILATURA_MIN_CONTENT_LENGTH', 300) if settings else 300
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
    
    def process_item(self, item, spider):
        """Process items extracted by trafilatura"""
        
        # Validate content length
        if item.get('content_length', 0) < self.min_content_length:
            spider.logger.debug(f"Content too short: {item.get('url', 'unknown')}")
            return item
            
        # Clean and validate content
        content = item.get('content', '')
        if content:
            # Basic content cleaning
            content = content.strip()
            item['content'] = content
            item['content_hash'] = self._generate_hash(content)
            
        return item
    
    def _generate_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()