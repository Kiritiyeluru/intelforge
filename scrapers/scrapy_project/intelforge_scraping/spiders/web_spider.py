"""
Web Spider for IntelForge - Scrapy Implementation

Migrated from web_scraper.py to use Scrapy framework with trafilatura integration.
Extracts algorithmic trading articles from blogs and news sites.
"""

import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse, urljoin

import scrapy
import yaml
import trafilatura
from trafilatura import extract, extract_metadata

from ..items import ArticleItem


class WebSpider(scrapy.Spider):
    name = 'web'
    allowed_domains = []
    start_urls = []
    
    # Site-specific configurations
    site_configs = {
        'medium.com': {
            'search_urls': [
                'https://medium.com/search?q=algorithmic%20trading',
                'https://medium.com/search?q=quantitative%20finance',
                'https://medium.com/search?q=trading%20strategy'
            ],
            'link_selectors': ['h2 a', 'h3 a', '.article-title a']
        },
        'dev.to': {
            'search_urls': [
                'https://dev.to/search?q=algorithmic%20trading',
                'https://dev.to/search?q=quantitative%20finance'
            ],
            'link_selectors': ['h2 a', 'h3 a', '.crayons-story__title a']
        },
        'towardsdatascience.com': {
            'search_urls': [
                'https://towardsdatascience.com/search?q=algorithmic%20trading',
                'https://towardsdatascience.com/search?q=quantitative%20finance'
            ],
            'link_selectors': ['h2 a', 'h3 a', '.article-title a']
        },
        'quantstart.com': {
            'search_urls': [
                'https://www.quantstart.com/articles/'
            ],
            'link_selectors': ['h2 a', 'h3 a', '.article-title a', '.post-title a']
        }
    }
    
    def __init__(self, config_path='config/config.yaml', *args, **kwargs):
        super(WebSpider, self).__init__(*args, **kwargs)
        
        # Load configuration
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            self.config = {'web': {'keywords': [], 'target_sites': []}}
        
        # Set up domains and start URLs
        self.target_sites = self.config.get('web', {}).get('target_sites', [])
        self.keywords = self.config.get('web', {}).get('keywords', [])
        
        # Configure allowed domains
        for site in self.target_sites:
            domain = site.replace('www.', '')
            if domain not in self.allowed_domains:
                self.allowed_domains.append(domain)
        
        # Generate start URLs from site configurations
        for site in self.target_sites:
            site_key = site.replace('www.', '')
            if site_key in self.site_configs:
                self.start_urls.extend(self.site_configs[site_key]['search_urls'])
    
    def start_requests(self):
        """Generate initial requests for search pages."""
        # For testing: Add a direct article URL to test extraction
        test_article_url = "https://www.quantstart.com/articles/Backtesting-a-Moving-Average-Crossover-in-Python-with-pandas/"
        yield scrapy.Request(
            url=test_article_url,
            callback=self.parse_article,
            meta={'site': 'quantstart.com'}
        )
        
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_search_page,
                meta={'site': self._get_site_from_url(url)}
            )
    
    def parse_search_page(self, response):
        """Parse search/listing pages to find article links."""
        site = response.meta.get('site')
        site_config = self.site_configs.get(site, {})
        
        # Extract article links using site-specific selectors
        article_links = set()
        
        # Try site-specific selectors first
        if 'link_selectors' in site_config:
            for selector in site_config['link_selectors']:
                links = response.css(f'{selector}::attr(href)').getall()
                for link in links:
                    full_url = response.urljoin(link)
                    if self._is_article_url(full_url):
                        article_links.add(full_url)
        
        # Fallback to generic article link patterns
        if not article_links:
            generic_selectors = [
                'a[href*="/article/"]::attr(href)',
                'a[href*="/post/"]::attr(href)',
                'a[href*="/story/"]::attr(href)',
                'a[href*="/blog/"]::attr(href)',
                'h2 a::attr(href)',
                'h3 a::attr(href)'
            ]
            
            for selector in generic_selectors:
                links = response.css(selector).getall()
                for link in links:
                    full_url = response.urljoin(link)
                    if self._is_article_url(full_url):
                        article_links.add(full_url)
        
        # Limit number of articles per search page
        max_articles = 20
        for article_url in list(article_links)[:max_articles]:
            yield scrapy.Request(
                url=article_url,
                callback=self.parse_article,
                meta={'site': site}
            )
    
    def parse_article(self, response):
        """Parse individual article pages."""
        # Use trafilatura for content extraction
        try:
            # Extract content using trafilatura
            content = trafilatura.extract(
                response.text,
                include_comments=False,
                include_tables=True,
                include_formatting=True
            )
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(response.text)
            
            if not content:
                self.logger.debug(f"No content extracted from {response.url}")
                return
            
            # Clean and process content
            content = self._clean_text(content)
            title = metadata.title if metadata and metadata.title else self._extract_title_fallback(response)
            author = metadata.author if metadata and metadata.author else "Unknown Author"
            
            # Check relevance
            if not self._is_relevant_content(title, content):
                self.logger.debug(f"Content not relevant: {response.url}")
                return
            
            # Extract keywords
            keywords = self._extract_keywords(f"{title} {content}")
            
            # Create article item
            item = ArticleItem()
            item['url'] = response.url
            item['title'] = self._clean_text(title)
            item['content'] = content
            item['author'] = self._clean_text(author)
            item['site'] = response.meta.get('site', self._get_site_from_url(response.url))
            item['keywords'] = keywords
            item['content_length'] = len(content)
            item['scraped_at'] = datetime.now().isoformat()
            item['content_hash'] = hashlib.sha256(content.encode()).hexdigest()
            item['is_relevant'] = True
            item['extraction_method'] = 'trafilatura'
            
            yield item
            
        except Exception as e:
            self.logger.error(f"Error parsing article {response.url}: {e}")
    
    def _get_site_from_url(self, url: str) -> str:
        """Extract site domain from URL."""
        domain = urlparse(url).netloc
        return domain.replace('www.', '')
    
    def _is_article_url(self, url: str) -> bool:
        """Check if URL looks like an article."""
        url_lower = url.lower()
        article_patterns = [
            '/article/', '/post/', '/story/', '/blog/',
            '/articles/', '/posts/', '/stories/', '/blogs/'
        ]
        
        # Must contain an article pattern
        has_pattern = any(pattern in url_lower for pattern in article_patterns)
        
        # Exclude non-article URLs
        exclude_patterns = [
            '/search', '/tag/', '/category/', '/author/',
            '/login', '/register', '/about', '/contact'
        ]
        has_exclude = any(pattern in url_lower for pattern in exclude_patterns)
        
        return has_pattern and not has_exclude
    
    def _extract_title_fallback(self, response) -> str:
        """Fallback title extraction if trafilatura fails."""
        title_selectors = [
            'h1::text',
            'title::text',
            '.article-title::text',
            '.post-title::text'
        ]
        
        for selector in title_selectors:
            title = response.css(selector).get()
            if title and title.strip():
                return title.strip()
        
        return "Untitled Article"
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove common unwanted phrases
        unwanted_phrases = [
            'Sign up for free',
            'Follow us on',
            'Subscribe to',
            'Click here',
            'Read more'
        ]
        
        for phrase in unwanted_phrases:
            text = text.replace(phrase, '')
        
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in self.keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _is_relevant_content(self, title: str, content: str) -> bool:
        """Check if content is relevant based on keywords."""
        text_to_check = f"{title} {content}".lower()
        
        # Must contain at least one keyword
        return any(keyword.lower() in text_to_check for keyword in self.keywords)