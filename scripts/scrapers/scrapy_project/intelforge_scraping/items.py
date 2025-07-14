# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArticleItem(scrapy.Item):
    """Item for storing scraped article data."""

    # Article content
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()

    # Metadata
    site = scrapy.Field()
    keywords = scrapy.Field()
    content_length = scrapy.Field()
    scraped_at = scrapy.Field()
    content_hash = scrapy.Field()

    # Processing flags
    is_relevant = scrapy.Field()
    extraction_method = scrapy.Field()
