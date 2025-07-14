# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.http import HtmlResponse
import logging
import stealth_requests

# useful for handling different item types with a single interface


class IntelforgeScrapingSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class StealthDownloaderMiddleware:
    """
    Stealth-Requests middleware for advanced anti-detection capabilities.
    Integrates stealth_requests with Scrapy for enhanced bot detection evasion.
    """

    def __init__(self, stealth_enabled=True):
        self.stealth_enabled = stealth_enabled
        self.logger = logging.getLogger(__name__)

        # Initialize stealth session
        self.session = stealth_requests.StealthSession()

        # Configure advanced stealth options
        self.session.verify = True
        self.session.timeout = 30

        self.logger.info("StealthDownloaderMiddleware initialized")

    @classmethod
    def from_crawler(cls, crawler):
        # Extract settings
        stealth_enabled = crawler.settings.getbool("STEALTH_ENABLED", True)

        # Return the middleware instance
        return cls(stealth_enabled=stealth_enabled)

    def process_request(self, request, spider):
        """
        Process requests using stealth_requests for anti-detection.
        """
        if not self.stealth_enabled:
            return None

        try:
            # Use stealth_requests to make the request
            response = self.session.get(
                request.url,
                headers=request.headers.to_unicode_dict(),
                timeout=30,
                allow_redirects=True,
            )

            # Create Scrapy response from stealth_requests response
            scrapy_response = HtmlResponse(
                url=response.url,
                body=response.content,
                encoding="utf-8",
                request=request,
                status=response.status_code,
                headers=response.headers,
            )

            spider.logger.info(
                f"Stealth request successful: {request.url} (Status: {response.status_code})"
            )
            return scrapy_response

        except Exception as e:
            spider.logger.error(f"Stealth request failed for {request.url}: {e}")
            # Return None to let Scrapy handle with default downloader
            return None

    def process_response(self, request, response, spider):
        """Process response - additional stealth logic can be added here."""
        return response

    def process_exception(self, request, exception, spider):
        """Handle exceptions in stealth requests."""
        spider.logger.error(
            f"Stealth middleware exception for {request.url}: {exception}"
        )
        return None


class NoDriverMiddleware:
    """
    NoDriver middleware for undetectable browser automation.
    Integrates with Scrapy for JavaScript-heavy sites requiring browser automation.
    """

    def __init__(self, nodriver_enabled=False):
        self.nodriver_enabled = nodriver_enabled
        self.logger = logging.getLogger(__name__)
        self.browser = None

        if self.nodriver_enabled:
            try:
                import nodriver as uc

                self.uc = uc
                self.logger.info("NoDriver middleware initialized")
            except ImportError:
                self.logger.warning(
                    "NoDriver not available - install with: pip install nodriver"
                )
                self.nodriver_enabled = False

    @classmethod
    def from_crawler(cls, crawler):
        # Extract settings
        nodriver_enabled = crawler.settings.getbool("NODRIVER_ENABLED", False)
        return cls(nodriver_enabled=nodriver_enabled)

    async def process_request(self, request, spider):
        """
        Process requests using NoDriver for undetectable browser automation.
        """
        if not self.nodriver_enabled:
            return None

        try:
            # Initialize browser if not already done
            if not self.browser:
                self.browser = await self.uc.start()

            # Navigate to the URL
            page = await self.browser.get(request.url)

            # Wait for page to load
            await page.wait_for_load_state("networkidle")

            # Get page content
            content = await page.content()

            # Create Scrapy response
            scrapy_response = HtmlResponse(
                url=request.url,
                body=content.encode("utf-8"),
                encoding="utf-8",
                request=request,
                status=200,
            )

            spider.logger.info(f"NoDriver request successful: {request.url}")
            return scrapy_response

        except Exception as e:
            spider.logger.error(f"NoDriver request failed for {request.url}: {e}")
            return None

    def process_response(self, request, response, spider):
        """Process response - additional NoDriver logic can be added here."""
        return response

    def process_exception(self, request, exception, spider):
        """Handle exceptions in NoDriver requests."""
        spider.logger.error(
            f"NoDriver middleware exception for {request.url}: {exception}"
        )
        return None

    def spider_closed(self, spider):
        """Clean up browser when spider closes."""
        if self.browser:
            try:
                import asyncio

                asyncio.create_task(self.browser.stop())
                self.logger.info("NoDriver browser closed")
            except Exception as e:
                self.logger.error(f"Error closing NoDriver browser: {e}")


class IntelforgeScrapingDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
