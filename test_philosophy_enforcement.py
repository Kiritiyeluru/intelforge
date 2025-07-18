# Test file to verify philosophy enforcement system
# This should trigger philosophy reminders for code tools

import scrapy  # Approved framework - should be allowed
from trafilatura import extract  # Another approved framework


def test_approved_approach():
    """Using approved frameworks as per REUSE OVER REBUILD philosophy"""
    spider = scrapy.Spider()
    content = extract("test content")
    return {"spider": spider, "content": content}
