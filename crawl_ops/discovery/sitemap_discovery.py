#!/usr/bin/env python3
"""
Sitemap Discovery for IntelForge
Extracts URLs from website sitemaps for systematic content discovery.
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
from datetime import datetime
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm


class SitemapDiscovery:
    """Sitemap-based URL discovery for systematic website crawling."""
    
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
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
    )
    def extract_urls_from_sitemap(self, domain: str) -> List[Dict]:
        """Extract URLs from domain sitemap with quality assessment."""
        sitemap_urls = [
            f"https://{domain}/sitemap.xml",
            f"https://{domain}/sitemap_index.xml",
            f"https://{domain}/robots.txt"  # Check robots.txt for sitemap location
        ]
        
        all_urls = []
        
        # First check robots.txt for sitemap location
        robots_sitemaps = self._extract_sitemaps_from_robots(domain)
        if robots_sitemaps:
            sitemap_urls = robots_sitemaps + sitemap_urls
        
        for sitemap_url in sitemap_urls:
            try:
                urls = self._process_sitemap_url(sitemap_url, domain)
                all_urls.extend(urls)
                
                if urls:  # If we found URLs, we're done
                    break
                    
            except Exception as e:
                print(f"⚠️  Error processing {sitemap_url}: {e}")
                continue
        
        # Remove duplicates and apply quality filtering
        unique_urls = self._deduplicate_and_filter(all_urls)
        
        print(f"🗺️  Sitemap discovery for {domain}: {len(unique_urls)} quality URLs found")
        return unique_urls
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def _extract_sitemaps_from_robots(self, domain: str) -> List[str]:
        """Extract sitemap URLs from robots.txt."""
        try:
            robots_url = f"https://{domain}/robots.txt"
            response = self.session.get(robots_url, timeout=self.timeout)
            
            if response.status_code == 200:
                sitemaps = []
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemaps.append(sitemap_url)
                return sitemaps
        except:
            pass
        return []
    
    def _process_sitemap_url(self, sitemap_url: str, domain: str) -> List[Dict]:
        """Process a single sitemap URL and extract content URLs."""
        response = self.session.get(sitemap_url, timeout=self.timeout)
        
        if response.status_code != 200:
            return []
        
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            return []
        
        urls = []
        
        # Handle sitemap index (contains references to other sitemaps)
        sitemaps = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
        if sitemaps:
            for sitemap in sitemaps[:10]:  # Limit to 10 sitemaps to avoid recursion issues
                loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    nested_urls = self._process_sitemap_url(loc.text, domain)
                    urls.extend(nested_urls)
        
        # Handle URL entries
        url_entries = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        for url_entry in tqdm(url_entries, desc="Processing sitemap URLs", unit="URL", leave=False):
            loc = url_entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            lastmod = url_entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            priority = url_entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
            changefreq = url_entry.find('{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
            
            if loc is not None:
                url_data = {
                    'url': loc.text,
                    'source': 'sitemap',
                    'category': self._infer_category_from_url(loc.text),
                    'priority': self._calculate_priority_from_sitemap(priority, changefreq),
                    'quality_estimate': self._calculate_quality_from_url(loc.text, domain),
                    'metadata': {
                        'domain': domain,
                        'lastmod': lastmod.text if lastmod is not None else None,
                        'sitemap_priority': priority.text if priority is not None else None,
                        'changefreq': changefreq.text if changefreq is not None else None,
                        'discovery_date': datetime.now().isoformat()
                    }
                }
                urls.append(url_data)
        
        return urls
    
    def _infer_category_from_url(self, url: str) -> str:
        """Infer content category from URL path patterns."""
        path = urlparse(url).path.lower()
        
        # Category mapping based on URL patterns
        if any(term in path for term in ['blog', 'article', 'post', 'news']):
            return 'blog'
        elif any(term in path for term in ['tutorial', 'guide', 'learn', 'course', 'education']):
            return 'tutorial' 
        elif any(term in path for term in ['research', 'paper', 'study', 'analysis']):
            return 'research'
        elif any(term in path for term in ['documentation', 'docs', 'api', 'reference']):
            return 'documentation'
        elif any(term in path for term in ['strategy', 'trading', 'backtest', 'algorithm']):
            return 'strategy'
        else:
            return 'general'
    
    def _calculate_priority_from_sitemap(self, priority_elem, changefreq_elem) -> int:
        """Calculate crawling priority from sitemap metadata."""
        base_priority = 5  # Default medium priority
        
        # Adjust based on sitemap priority
        if priority_elem is not None:
            try:
                sitemap_priority = float(priority_elem.text)
                if sitemap_priority >= 0.8:
                    base_priority = 2
                elif sitemap_priority >= 0.6:
                    base_priority = 3
                elif sitemap_priority >= 0.4:
                    base_priority = 4
            except:
                pass
        
        # Adjust based on change frequency
        if changefreq_elem is not None:
            changefreq = changefreq_elem.text.lower()
            if changefreq in ['daily', 'hourly']:
                base_priority = max(base_priority - 1, 1)
            elif changefreq in ['weekly']:
                base_priority = max(base_priority - 0.5, 1)
        
        return int(base_priority)
    
    def _calculate_quality_from_url(self, url: str, domain: str) -> float:
        """Calculate quality estimate from URL characteristics."""
        base_quality = 0.6  # Default for sitemap URLs
        
        # Domain-specific quality bonuses
        quality_domains = {
            'quantstart.com': 0.3,
            'blog.quantinsti.com': 0.25,
            'investopedia.com': 0.2,
            'arxiv.org': 0.3,
            'papers.ssrn.com': 0.25
        }
        
        domain_bonus = quality_domains.get(domain, 0)
        
        # Path-based quality signals
        path = urlparse(url).path.lower()
        quality_keywords = {
            'tutorial': 0.1,
            'guide': 0.1,
            'strategy': 0.15,
            'backtest': 0.15,
            'research': 0.1,
            'analysis': 0.1,
            'python': 0.05,
            'algorithm': 0.1
        }
        
        keyword_bonus = sum(
            bonus for keyword, bonus in quality_keywords.items()
            if keyword in path
        )
        
        return min(base_quality + domain_bonus + keyword_bonus, 1.0)
    
    def _deduplicate_and_filter(self, urls: List[Dict]) -> List[Dict]:
        """Remove duplicates and apply quality filters."""
        seen_urls = set()
        filtered_urls = []
        
        for url_data in urls:
            url = url_data['url']
            
            # Skip duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Apply quality filters
            if self._passes_quality_filter(url_data):
                filtered_urls.append(url_data)
        
        return filtered_urls
    
    def _passes_quality_filter(self, url_data: Dict) -> bool:
        """Apply quality filters to determine if URL should be included."""
        url = url_data['url']
        
        # Skip common low-value pages
        skip_patterns = [
            '/tag/', '/tags/', '/category/', '/categories/',
            '/search/', '/archive/', '/sitemap',
            '.pdf', '.zip', '.exe', '.dmg',
            '/contact', '/about/contact', '/privacy', '/terms'
        ]
        
        path = urlparse(url).path.lower()
        if any(pattern in path for pattern in skip_patterns):
            return False
        
        # Require minimum quality score
        if url_data['quality_estimate'] < 0.3:
            return False
        
        return True


if __name__ == "__main__":
    # Test sitemap discovery
    discovery = SitemapDiscovery()
    
    test_domains = ['quantstart.com', 'blog.quantinsti.com']
    for domain in test_domains:
        urls = discovery.extract_urls_from_sitemap(domain)
        print(f"\n{domain}: {len(urls)} URLs found")
        for url in urls[:3]:  # Show first 3
            print(f"  {url['url']} ({url['category']}, quality: {url['quality_estimate']:.2f})")