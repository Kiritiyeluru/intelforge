#!/usr/bin/env python3
"""
RSS Feed Discovery for IntelForge
Enhanced RSS parsing using feedparser for robust content discovery.
"""

import feedparser
import requests
from typing import List, Dict, Optional
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time
from tqdm import tqdm


class RSSDiscovery:
    """Enhanced RSS feed discovery using feedparser for robust parsing."""
    
    def __init__(self, timeout: int = 30):
        """Initialize with request timeout."""
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'IntelForge-Discovery/1.0 (Educational Research)'
        })
        
        # Configure session timeouts and retries
        adapter = requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=2,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, feedparser.FeedParserDict))
    )
    def discover_from_feeds(self, feed_urls: List[str], max_entries_per_feed: int = 20) -> List[Dict]:
        """Discover URLs from RSS/Atom feeds with robust parsing."""
        all_discoveries = []
        
        for feed_url in tqdm(feed_urls, desc="Processing RSS feeds", unit="feed"):
            try:
                entries = self._parse_feed(feed_url, max_entries_per_feed)
                all_discoveries.extend(entries)
                
                # Rate limiting between feeds
                time.sleep(2)
                
            except Exception as e:
                print(f"⚠️  Error processing feed {feed_url}: {e}")
                continue
        
        # Deduplicate and sort by publication date
        unique_discoveries = self._deduplicate_and_sort(all_discoveries)
        
        print(f"📡 RSS Discovery: {len(unique_discoveries)} articles discovered from {len(feed_urls)} feeds")
        return unique_discoveries
    
    def _parse_feed(self, feed_url: str, max_entries: int) -> List[Dict]:
        """Parse a single RSS/Atom feed using feedparser."""
        # Use feedparser's built-in HTTP handling with custom User-Agent
        feedparser.USER_AGENT = self.session.headers['User-Agent']
        
        # Parse the feed - feedparser handles various formats gracefully
        feed = feedparser.parse(feed_url)
        
        if feed.bozo and feed.bozo_exception:
            print(f"⚠️  Feed parsing warning for {feed_url}: {feed.bozo_exception}")
        
        # Extract feed metadata
        feed_title = getattr(feed.feed, 'title', 'Unknown Feed')
        feed_description = getattr(feed.feed, 'description', '')
        
        discoveries = []
        
        for entry in tqdm(feed.entries[:max_entries], desc=f"Processing {feed_title[:20]}...", unit="entry", leave=False):
            try:
                discovery = self._extract_entry_data(entry, feed_url, feed_title)
                if discovery:
                    discoveries.append(discovery)
            except Exception as e:
                print(f"⚠️  Error processing entry: {e}")
                continue
        
        print(f"📰 Feed '{feed_title}': {len(discoveries)} articles extracted")
        return discoveries
    
    def _extract_entry_data(self, entry, feed_url: str, feed_title: str) -> Optional[Dict]:
        """Extract data from a single RSS entry."""
        # Get entry URL
        entry_url = getattr(entry, 'link', None)
        if not entry_url:
            return None
        
        # Get entry title
        title = getattr(entry, 'title', 'Untitled')
        
        # Get entry description/summary
        description = getattr(entry, 'description', '') or getattr(entry, 'summary', '')
        
        # Get publication date
        published_date = None
        for date_field in ['published_parsed', 'updated_parsed']:
            date_tuple = getattr(entry, date_field, None)
            if date_tuple:
                try:
                    published_date = datetime(*date_tuple[:6], tzinfo=timezone.utc).isoformat()
                    break
                except:
                    continue
        
        # Get author information
        author = getattr(entry, 'author', '')
        
        # Get tags/categories
        tags = []
        if hasattr(entry, 'tags'):
            tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
        
        # Calculate quality score and category
        quality_score = self._calculate_content_quality(title, description, tags, feed_url)
        category = self._infer_category_from_content(title, description, tags)
        priority = self._calculate_priority_from_feed(feed_url, quality_score)
        
        return {
            'url': entry_url,
            'source': 'rss_discovery',
            'category': category,
            'priority': priority,
            'quality_estimate': quality_score,
            'metadata': {
                'title': title,
                'description': description[:500],  # Truncate long descriptions
                'author': author,
                'published_date': published_date,
                'feed_url': feed_url,
                'feed_title': feed_title,
                'tags': tags,
                'discovery_date': datetime.now().isoformat()
            }
        }
    
    def _calculate_content_quality(self, title: str, description: str, tags: List[str], feed_url: str) -> float:
        """Calculate quality score based on content signals."""
        base_quality = 0.6  # Default for RSS content
        
        # Feed source quality bonus
        feed_domain = urlparse(feed_url).netloc.lower()
        quality_feeds = {
            'quantstart.com': 0.3,
            'blog.quantinsti.com': 0.25,
            'investopedia.com': 0.2,
            'arxiv.org': 0.3,
            'papers.ssrn.com': 0.25,
            'seekingalpha.com': 0.15,
            'bloomberg.com': 0.2,
            'reuters.com': 0.15
        }
        
        feed_bonus = 0
        for domain, bonus in quality_feeds.items():
            if domain in feed_domain:
                feed_bonus = bonus
                break
        
        # Content quality signals
        content = (title + " " + description).lower()
        quality_keywords = {
            'python': 0.1,
            'algorithm': 0.1,
            'strategy': 0.15,
            'backtest': 0.15,
            'trading': 0.1,
            'analysis': 0.1,
            'research': 0.1,
            'quantitative': 0.15,
            'machine learning': 0.1,
            'tutorial': 0.05
        }
        
        keyword_bonus = sum(
            bonus for keyword, bonus in quality_keywords.items()
            if keyword in content
        )
        
        # Tag-based quality boost
        tag_bonus = 0
        if tags:
            relevant_tags = ['finance', 'trading', 'python', 'quant', 'algorithm', 'strategy']
            tag_bonus = sum(0.05 for tag in tags if any(rt in tag.lower() for rt in relevant_tags))
        
        return min(base_quality + feed_bonus + keyword_bonus + tag_bonus, 1.0)
    
    def _infer_category_from_content(self, title: str, description: str, tags: List[str]) -> str:
        """Infer content category from title, description, and tags."""
        content = (title + " " + description + " " + " ".join(tags)).lower()
        
        # Category keyword mapping with priorities
        category_keywords = {
            'strategy': ['strategy', 'trading strategy', 'backtest', 'algorithm', 'model'],
            'tutorial': ['tutorial', 'guide', 'how to', 'step by step', 'learn', 'course'],
            'research': ['research', 'study', 'analysis', 'paper', 'findings', 'empirical'],
            'news': ['news', 'update', 'announcement', 'breaking', 'market news'],
            'blog': ['blog', 'post', 'article', 'opinion', 'thoughts', 'commentary'],
            'code': ['code', 'python', 'github', 'implementation', 'library', 'package']
        }
        
        # Find the category with the most matches
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'general'
    
    def _calculate_priority_from_feed(self, feed_url: str, quality_score: float) -> int:
        """Calculate crawling priority based on feed source and quality."""
        # Base priority from feed reputation
        feed_domain = urlparse(feed_url).netloc.lower()
        priority_feeds = {
            'quantstart.com': 2,
            'blog.quantinsti.com': 2,
            'arxiv.org': 2,
            'papers.ssrn.com': 3,
            'investopedia.com': 3,
            'seekingalpha.com': 4,
            'bloomberg.com': 3,
            'reuters.com': 4
        }
        
        base_priority = 5  # Default
        for domain, priority in priority_feeds.items():
            if domain in feed_domain:
                base_priority = priority
                break
        
        # Adjust based on quality score
        if quality_score >= 0.8:
            base_priority = max(base_priority - 1, 1)
        elif quality_score >= 0.6:
            base_priority = base_priority
        else:
            base_priority = min(base_priority + 1, 6)
        
        return int(base_priority)
    
    def _deduplicate_and_sort(self, discoveries: List[Dict]) -> List[Dict]:
        """Remove duplicates and sort by publication date (newest first)."""
        # Deduplicate by URL
        seen_urls = set()
        unique_discoveries = []
        
        for discovery in discoveries:
            url = discovery['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_discoveries.append(discovery)
        
        # Sort by publication date (newest first), fallback to discovery date
        def get_sort_date(discovery):
            pub_date = discovery['metadata'].get('published_date')
            if pub_date:
                try:
                    return datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                except:
                    pass
            # Fallback to discovery date
            return datetime.fromisoformat(discovery['metadata']['discovery_date'])
        
        unique_discoveries.sort(key=get_sort_date, reverse=True)
        
        return unique_discoveries
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def discover_feed_urls_from_domain(self, domain: str) -> List[str]:
        """Discover RSS/Atom feed URLs from a domain."""
        potential_feeds = []
        
        # Common RSS feed locations
        common_paths = [
            '/rss', '/rss.xml', '/feed', '/feed.xml', '/feeds/all.atom.xml',
            '/blog/rss', '/blog/feed', '/index.xml', '/atom.xml',
            '/news/rss', '/articles/rss'
        ]
        
        for path in common_paths:
            feed_url = f"https://{domain}{path}"
            try:
                response = self.session.head(feed_url, timeout=10)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '').lower()
                    if any(feed_type in content_type for feed_type in ['xml', 'rss', 'atom']):
                        potential_feeds.append(feed_url)
            except:
                continue
        
        # Also check robots.txt for feed declarations
        try:
            robots_url = f"https://{domain}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if 'feed' in line.lower() or 'rss' in line.lower():
                        # Extract URL from robots.txt line
                        parts = line.split()
                        for part in parts:
                            if part.startswith('http') and ('feed' in part or 'rss' in part):
                                potential_feeds.append(part)
        except:
            pass
        
        return list(set(potential_feeds))  # Remove duplicates


# Predefined high-quality RSS feeds for trading/finance
DEFAULT_FEEDS = [
    'https://www.quantstart.com/feeds/all.atom.xml',
    'https://blog.quantinsti.com/feed/',
    'https://seekingalpha.com/feed.xml',
    'https://feeds.reuters.com/reuters/businessNews',
    'https://feeds.bloomberg.com/markets/news.rss',
    'https://rss.cnn.com/rss/money_markets.rss'
]


if __name__ == "__main__":
    # Test RSS discovery
    discovery = RSSDiscovery()
    
    # Test with a subset of feeds
    test_feeds = DEFAULT_FEEDS[:2]  # Test with first 2 feeds
    discoveries = discovery.discover_from_feeds(test_feeds, max_entries_per_feed=5)
    
    print(f"\nDiscovered {len(discoveries)} articles:")
    for discovery in discoveries[:3]:  # Show first 3
        print(f"  {discovery['url']}")
        print(f"    Title: {discovery['metadata']['title']}")
        print(f"    Category: {discovery['category']}, Quality: {discovery['quality_estimate']:.2f}")
        print()