#!/usr/bin/env python3
"""
Simple Web Scraper for IntelForge

A minimal web scraper using httpx + selectolax + base framework.
Extracts algorithmic trading articles from blogs and news sites.

Usage:
    python web_scraper.py [--dry-run] [--site SITE] [--limit N]

Example:
    python web_scraper.py --dry-run --site medium.com --limit 5
"""

import argparse
import os
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import selectolax.parser as sp
from dotenv import load_dotenv

from scripts.scraping_base import BaseScraper


class WebScraper(BaseScraper):
    """Simple web scraper using httpx + selectolax + base framework."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize web scraper."""
        super().__init__(config_path, scraper_name="web")
        
        # Load environment variables
        load_dotenv()
        
        # Site-specific selectors for content extraction
        self.site_selectors = {
            'medium.com': {
                'title': 'h1',
                'content': 'article div p, article div h1, article div h2, article div h3',
                'author': '[data-testid="authorName"]',
                'search_urls': [
                    'https://medium.com/search?q=algorithmic%20trading',
                    'https://medium.com/search?q=quantitative%20finance',
                    'https://medium.com/search?q=trading%20strategy'
                ]
            },
            'dev.to': {
                'title': 'h1.crayons-title',
                'content': 'div#article-body p, div#article-body h1, div#article-body h2, div#article-body h3',
                'author': '.crayons-article__header__meta a',
                'search_urls': [
                    'https://dev.to/search?q=algorithmic%20trading',
                    'https://dev.to/search?q=quantitative%20finance'
                ]
            },
            'towardsdatascience.com': {
                'title': 'h1',
                'content': 'article div p, article div h1, article div h2, article div h3',
                'author': '[data-testid="authorName"]',
                'search_urls': [
                    'https://towardsdatascience.com/search?q=algorithmic%20trading',
                    'https://towardsdatascience.com/search?q=quantitative%20finance'
                ]
            },
            'quantstart.com': {
                'title': 'h1.entry-title',
                'content': '.entry-content p, .entry-content h1, .entry-content h2, .entry-content h3',
                'author': '.author-name',
                'search_urls': [
                    'https://www.quantstart.com/articles/'
                ]
            }
        }
    
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
        keywords = self.config['web']['keywords']
        found_keywords = []
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _is_relevant_content(self, title: str, content: str) -> bool:
        """Check if content is relevant based on keywords."""
        text_to_check = f"{title} {content}".lower()
        keywords = self.config['web']['keywords']
        
        # Must contain at least one keyword
        return any(keyword.lower() in text_to_check for keyword in keywords)
    
    def _get_site_selector(self, url: str) -> Optional[Dict]:
        """Get selector configuration for a site."""
        domain = urlparse(url).netloc
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return self.site_selectors.get(domain)
    
    def _extract_article_content(self, url: str) -> Optional[Dict]:
        """Extract content from a single article URL."""
        try:
            if not self._check_robots_txt(url):
                return None
            
            response = self._make_request(url)
            tree = sp.HTMLParser(response.text)
            
            # Get site-specific selectors
            selectors = self._get_site_selector(url)
            if not selectors:
                # Use generic selectors as fallback
                selectors = {
                    'title': 'h1, title',
                    'content': 'p, article p, .content p, .post-content p',
                    'author': '.author, .byline, [rel="author"]'
                }
            
            # Extract title
            title_elem = tree.css_first(selectors['title'])
            title = title_elem.text() if title_elem else "Untitled Article"
            title = self._clean_text(title)
            
            # Extract content
            content_elements = tree.css(selectors['content'])
            content_texts = []
            
            for elem in content_elements:
                text = elem.text()
                if text and len(text.strip()) > 20:  # Skip very short texts
                    content_texts.append(self._clean_text(text))
            
            content = '\n\n'.join(content_texts)
            
            # Extract author
            author_elem = tree.css_first(selectors['author'])
            author = author_elem.text() if author_elem else "Unknown Author"
            author = self._clean_text(author)
            
            # Check relevance
            if not self._is_relevant_content(title, content):
                self.logger.debug(f"Content not relevant: {url}")
                return None
            
            # Extract metadata
            metadata = {
                'site': urlparse(url).netloc,
                'author': author,
                'content_length': len(content),
                'keywords': self._extract_keywords(f"{title} {content}")
            }
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def _find_article_links(self, search_url: str) -> List[str]:
        """Find article links from a search or listing page."""
        try:
            response = self._make_request(search_url)
            tree = sp.HTMLParser(response.text)
            
            # Common patterns for article links
            link_selectors = [
                'a[href*="/article/"]',
                'a[href*="/post/"]',
                'a[href*="/story/"]',
                'a[href*="/blog/"]',
                'h2 a',
                'h3 a',
                '.article-title a',
                '.post-title a'
            ]
            
            article_links = []
            base_url = f"{urlparse(search_url).scheme}://{urlparse(search_url).netloc}"
            
            for selector in link_selectors:
                elements = tree.css(selector)
                for elem in elements:
                    href = elem.attrs.get('href')
                    if href:
                        # Convert relative URLs to absolute
                        if href.startswith('/'):
                            href = urljoin(base_url, href)
                        elif not href.startswith('http'):
                            continue
                        
                        # Filter out non-article URLs
                        if any(pattern in href.lower() for pattern in ['article', 'post', 'story', 'blog']):
                            article_links.append(href)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_links = []
            for link in article_links:
                if link not in seen:
                    seen.add(link)
                    unique_links.append(link)
            
            self.logger.info(f"Found {len(unique_links)} article links from {search_url}")
            return unique_links[:20]  # Limit to first 20 links
            
        except Exception as e:
            self.logger.error(f"Error finding article links from {search_url}: {e}")
            return []
    
    def scrape_site(self, site: str, limit: int = None) -> List[Dict]:
        """Scrape articles from a specific site."""
        if limit is None:
            limit = self.config['web']['max_pages_per_site']
        
        self.logger.info(f"Scraping {site} (limit: {limit})")
        
        selectors = self.site_selectors.get(site)
        if not selectors:
            self.logger.error(f"No selectors configured for {site}")
            return []
        
        scraped_articles = []
        
        # Get article links from search URLs
        all_article_links = []
        for search_url in selectors.get('search_urls', []):
            try:
                links = self._find_article_links(search_url)
                all_article_links.extend(links)
                
                # Add delay between search requests
                self._random_delay(
                    self.config['web']['rate_limit_delay'],
                    self.config['web']['rate_limit_delay'] + 2
                )
                
            except Exception as e:
                self.logger.error(f"Error searching {search_url}: {e}")
                continue
        
        # Remove duplicates
        unique_links = list(dict.fromkeys(all_article_links))
        
        # Process articles
        for i, article_url in enumerate(unique_links[:limit]):
            try:
                article = self._extract_article_content(article_url)
                if article:
                    scraped_articles.append(article)
                
                # Add delay between article requests
                if i < len(unique_links[:limit]) - 1:
                    self._random_delay(
                        self.config['web']['rate_limit_delay'],
                        self.config['web']['rate_limit_delay'] + 1
                    )
                
            except Exception as e:
                self.logger.error(f"Error processing article {article_url}: {e}")
                continue
        
        self.logger.info(f"Scraped {len(scraped_articles)} articles from {site}")
        return scraped_articles
    
    def scrape_all_sites(self, limit_per_site: int = None):
        """Scrape all configured sites."""
        sites = self.config['web']['target_sites']
        
        self.logger.info(f"Starting to scrape {len(sites)} sites...")
        
        all_articles = []
        
        for site in sites:
            try:
                articles = self.scrape_site(site, limit_per_site)
                
                # Save each article
                for article in articles:
                    self.save_content(
                        article['url'],
                        article['title'],
                        article['content'],
                        article['metadata']
                    )
                
                all_articles.extend(articles)
                
                # Add delay between sites
                if site != sites[-1]:  # Not the last site
                    self._random_delay(
                        self.config['web']['rate_limit_delay'] * 2,
                        self.config['web']['rate_limit_delay'] * 3
                    )
                    
            except Exception as e:
                self.logger.error(f"Error scraping {site}: {e}")
                continue
        
        self.logger.info(f"Finished scraping. Total articles: {len(all_articles)}")
        return all_articles


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Web Scraper for IntelForge")
    parser.add_argument('--dry-run', action='store_true', help="Run in dry-run mode")
    parser.add_argument('--site', type=str, help="Specific site to scrape")
    parser.add_argument('--url', type=str, help="Specific article URL to scrape")
    parser.add_argument('--limit', type=int, help="Limit number of articles per site")
    parser.add_argument('--config', type=str, default="config/config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    # Set dry-run mode if specified
    if args.dry_run:
        os.environ['INTELFORGE_DRY_RUN'] = 'true'
    
    try:
        with WebScraper(config_path=args.config) as scraper:
            if args.url:
                # Scrape specific URL
                article = scraper._extract_article_content(args.url)
                if article:
                    scraper.save_content(
                        article['url'],
                        article['title'],
                        article['content'],
                        article['metadata']
                    )
                    print(f"Scraped: {article['title']}")
                else:
                    print("No relevant content found or error occurred")
                    
            elif args.site:
                # Scrape specific site
                articles = scraper.scrape_site(args.site, args.limit)
                for article in articles:
                    scraper.save_content(
                        article['url'],
                        article['title'],
                        article['content'],
                        article['metadata']
                    )
            else:
                # Scrape all configured sites
                scraper.scrape_all_sites(args.limit)
                
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()