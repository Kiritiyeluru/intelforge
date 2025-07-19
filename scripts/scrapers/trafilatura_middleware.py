"""
Trafilatura Middleware for Scrapy - Enhanced Content Extraction
Integrates trafilatura content extraction with Scrapy's processing pipeline
"""

import trafilatura
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse


class TrafilaturaMiddleware:
    """Middleware that uses trafilatura for content extraction"""

    def __init__(self, settings=None):
        if not settings:
            raise NotConfigured("TrafilaturaMiddleware requires settings")

        self.include_comments = settings.getbool("TRAFILATURA_INCLUDE_COMMENTS", False)
        self.include_tables = settings.getbool("TRAFILATURA_INCLUDE_TABLES", True)
        self.include_formatting = settings.getbool(
            "TRAFILATURA_INCLUDE_FORMATTING", True
        )
        self.extract_metadata = settings.getbool("TRAFILATURA_EXTRACT_METADATA", True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):
        """Process response with trafilatura extraction"""
        spider.logger.debug(f"TrafilaturaMiddleware processing: {response.url}")

        spider.logger.debug(f"Response type: {type(response)}, has request: {hasattr(response, 'request')}")
        spider.logger.debug(f"Is HtmlResponse: {isinstance(response, HtmlResponse)}")
        spider.logger.debug(f"Request is not None: {response.request is not None if hasattr(response, 'request') else False}")

        if isinstance(response, HtmlResponse):
            spider.logger.debug(f"HTML response detected, extracting content from {response.url}")

            # Check if response has meta (some responses like robots.txt don't)
            try:
                # Extract content using trafilatura
                content = trafilatura.extract(
                    response.text,
                    include_comments=self.include_comments,
                    include_tables=self.include_tables,
                    include_formatting=self.include_formatting,
                    url=response.url,
                )

                spider.logger.debug(f"Extracted content length: {len(content) if content else 0}")
                spider.logger.debug(f"Content is truthy: {bool(content)}")
                spider.logger.debug(f"Content type: {type(content)}")

                # Extract metadata if enabled
                metadata = None
                if self.extract_metadata:
                    metadata = trafilatura.extract_metadata(response.text)
                    spider.logger.debug(f"Extracted metadata: {metadata.title if metadata and metadata.title else 'No title'}")

                # Check if we can access response.meta
                try:
                    # Test meta access
                    _ = response.meta
                    meta_available = True
                except AttributeError:
                    meta_available = False
                    spider.logger.debug(f"Response.meta not available for {response.url}")

                if meta_available:
                    # Add extracted content to response meta
                    response.meta["trafilatura_content"] = content
                    response.meta["trafilatura_metadata"] = metadata

                    # Create a structured item for the pipeline
                    spider.logger.debug(f"About to check content condition: content={content is not None}, stripped_len={len(content.strip()) if content else 0}")
                    if content and len(content.strip()) > 0:
                        spider.logger.info(f"Creating trafilatura_item for {response.url} with {len(content)} chars")
                        response.meta["trafilatura_item"] = {
                            "url": response.url,
                            "title": (
                                metadata.title if metadata and metadata.title else "Untitled"
                            ),
                            "content": content,
                            "author": (
                                metadata.author if metadata and metadata.author else "Unknown"
                            ),
                            "date": metadata.date if metadata and metadata.date else None,
                            "content_length": len(content),
                            "extraction_method": "trafilatura",
                            "site": response.url.split("/")[2],
                        }
                    else:
                        spider.logger.warning(f"No content extracted by trafilatura from {response.url}")
                else:
                    spider.logger.debug(f"Skipping item creation for {response.url} - no meta access")

            except Exception as e:
                spider.logger.error(f"Error processing response {response.url}: {e}")
                spider.logger.error(f"Exception type: {type(e)}")
                import traceback
                spider.logger.error(f"Traceback: {traceback.format_exc()}")
                # Skip responses that cause errors

        return response


class TrafilaturaPipeline:
    """Pipeline for processing trafilatura-extracted content"""

    def __init__(self, settings=None):
        self.min_content_length = (
            settings.getint("TRAFILATURA_MIN_CONTENT_LENGTH", 300) if settings else 300
        )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_item(self, item, spider):
        """Process items extracted by trafilatura"""
        spider.logger.debug(f"TrafilaturaPipeline processing item: {item.get('url', 'unknown')}")
        spider.logger.debug(f"Item content length: {item.get('content_length', 0)}, min required: {self.min_content_length}")

        # Validate content length
        if item.get("content_length", 0) < self.min_content_length:
            spider.logger.warning(f"Content too short ({item.get('content_length', 0)} < {self.min_content_length}): {item.get('url', 'unknown')}")
            return item

        # Clean and validate content
        content = item.get("content", "")
        if content:
            # Basic content cleaning
            content = content.strip()
            item["content"] = content
            item["content_hash"] = self._generate_hash(content)
            spider.logger.info(f"Item processed successfully: {item.get('url', 'unknown')}")

        return item

    def _generate_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content"""
        import hashlib

        return hashlib.sha256(content.encode("utf-8")).hexdigest()
