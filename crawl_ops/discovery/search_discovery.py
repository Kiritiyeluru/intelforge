#!/usr/bin/env python3
"""
Search-based Discovery for IntelForge
Uses search APIs for targeted content discovery in trading/finance domains.
"""

import requests
from typing import List, Dict, Optional
from datetime import datetime
import os
import time
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm


class SearchDiscovery:
    """Search API-based content discovery for targeted domain research."""
    
    def __init__(self, google_api_key: Optional[str] = None, bing_api_key: Optional[str] = None):
        """Initialize with optional API keys for enhanced discovery."""
        self.google_api_key = google_api_key or os.environ.get('GOOGLE_SEARCH_API_KEY')
        self.bing_api_key = bing_api_key or os.environ.get('BING_SEARCH_API_KEY')
        
        # Google Custom Search Engine ID for finance/trading content
        self.google_cse_id = os.environ.get('GOOGLE_CSE_ID', '017576662512468239146:omuauf_lfve')
        
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
    def search_google_custom(self, query: str, site_filter: Optional[str] = None, 
                           max_results: int = 10) -> List[Dict]:
        """Use Google Custom Search API for targeted content discovery."""
        if not self.google_api_key:
            print("⚠️  Google API key not available, skipping Google search")
            return []
        
        search_query = query
        if site_filter:
            search_query = f"site:{site_filter} {query}"
        
        params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': search_query,
            'num': min(max_results, 10),  # Google CSE limit is 10 per request
            'safe': 'off',
            'fields': 'items(title,link,snippet,displayLink)'
        }
        
        try:
            response = self.session.get(
                'https://www.googleapis.com/customsearch/v1',
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('items', []):
                    result = {
                        'url': item['link'],
                        'source': 'google_search',
                        'category': self._infer_category_from_content(
                            item.get('title', ''), 
                            item.get('snippet', '')
                        ),
                        'priority': self._calculate_search_priority(item),
                        'quality_estimate': self._calculate_search_quality(item),
                        'metadata': {
                            'title': item.get('title'),
                            'snippet': item.get('snippet'),
                            'display_link': item.get('displayLink'),
                            'search_query': query,
                            'site_filter': site_filter,
                            'discovery_date': datetime.now().isoformat()
                        }
                    }
                    results.append(result)
                
                print(f"🔍 Google Search: Found {len(results)} results for '{query}'")
                return results
            
            elif response.status_code == 429:
                print("⚠️  Google Search API rate limited")
                return []
            else:
                print(f"❌ Google Search API error: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Google Search request failed: {e}")
            return []
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
    )
    def search_bing(self, query: str, site_filter: Optional[str] = None,
                   max_results: int = 20) -> List[Dict]:
        """Use Bing Web Search API for content discovery."""
        if not self.bing_api_key:
            print("⚠️  Bing API key not available, skipping Bing search")
            return []
        
        search_query = query
        if site_filter:
            search_query = f"site:{site_filter} {query}"
        
        headers = {
            'Ocp-Apim-Subscription-Key': self.bing_api_key
        }
        
        params = {
            'q': search_query,
            'count': min(max_results, 50),  # Bing allows up to 50
            'responseFilter': 'Webpages',
            'safeSearch': 'Off',
            'textFormat': 'HTML'
        }
        
        try:
            response = self.session.get(
                'https://api.bing.microsoft.com/v7.0/search',
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for item in data.get('webPages', {}).get('value', []):
                    result = {
                        'url': item['url'],
                        'source': 'bing_search',
                        'category': self._infer_category_from_content(
                            item.get('name', ''), 
                            item.get('snippet', '')
                        ),
                        'priority': self._calculate_search_priority(item),
                        'quality_estimate': self._calculate_search_quality(item),
                        'metadata': {
                            'title': item.get('name'),
                            'snippet': item.get('snippet'),
                            'display_url': item.get('displayUrl'),
                            'search_query': query,
                            'site_filter': site_filter,
                            'discovery_date': datetime.now().isoformat()
                        }
                    }
                    results.append(result)
                
                print(f"🔍 Bing Search: Found {len(results)} results for '{query}'")
                return results
            
            elif response.status_code == 429:
                print("⚠️  Bing Search API rate limited")
                return []
            else:
                print(f"❌ Bing Search API error: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Bing Search request failed: {e}")
            return []
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def search_targeted_domains(self, query: str, target_domains: List[str]) -> List[Dict]:
        """Search specific domains for targeted content discovery."""
        all_results = []
        
        for domain in tqdm(target_domains, desc="Searching domains", unit="domain"):
            # Try Google first
            google_results = self.search_google_custom(query, site_filter=domain, max_results=5)
            all_results.extend(google_results)
            
            # Add Bing results if available
            bing_results = self.search_bing(query, site_filter=domain, max_results=5)
            all_results.extend(bing_results)
            
            # Rate limiting pause
            time.sleep(2)
        
        # Deduplicate results
        return self._deduplicate_search_results(all_results)
    
    def _infer_category_from_content(self, title: str, snippet: str) -> str:
        """Infer content category from title and snippet text."""
        content = (title + " " + snippet).lower()
        
        # Category keyword mapping
        category_keywords = {
            'tutorial': ['tutorial', 'guide', 'how to', 'step by step', 'learn'],
            'research': ['research', 'study', 'analysis', 'paper', 'findings'],
            'strategy': ['strategy', 'trading', 'backtest', 'algorithm', 'model'],
            'news': ['news', 'update', 'announcement', 'breaking'],
            'documentation': ['documentation', 'docs', 'api', 'reference', 'manual'],
            'blog': ['blog', 'post', 'article', 'opinion', 'thoughts']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in content for keyword in keywords):
                return category
        
        return 'general'
    
    def _calculate_search_priority(self, item: Dict) -> int:
        """Calculate priority based on search result characteristics."""
        # Higher priority for results from known quality domains
        url = item.get('url', '') if 'url' in item else item.get('link', '')
        domain = urlparse(url).netloc.lower()
        
        priority_domains = {
            'quantstart.com': 2,
            'blog.quantinsti.com': 2,
            'arxiv.org': 2,
            'papers.ssrn.com': 3,
            'github.com': 4,
            'investopedia.com': 3
        }
        
        return priority_domains.get(domain, 5)  # Default to lower priority
    
    def _calculate_search_quality(self, item: Dict) -> float:
        """Calculate quality estimate from search result metadata."""
        base_quality = 0.5  # Default for search results
        
        # Domain-based quality boost
        url = item.get('url', '') if 'url' in item else item.get('link', '')
        domain = urlparse(url).netloc.lower()
        
        quality_domains = {
            'quantstart.com': 0.3,
            'blog.quantinsti.com': 0.25,
            'arxiv.org': 0.3,
            'papers.ssrn.com': 0.25,
            'investopedia.com': 0.2
        }
        
        domain_bonus = quality_domains.get(domain, 0)
        
        # Content quality signals from title/snippet
        title = item.get('title', '') if 'title' in item else item.get('name', '')
        snippet = item.get('snippet', '')
        content = (title + " " + snippet).lower()
        
        quality_signals = [
            'python', 'algorithm', 'strategy', 'backtest', 
            'tutorial', 'guide', 'analysis', 'research'
        ]
        
        signal_bonus = sum(0.05 for signal in quality_signals if signal in content)
        
        return min(base_quality + domain_bonus + signal_bonus, 1.0)
    
    def _deduplicate_search_results(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate URLs from search results."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results


if __name__ == "__main__":
    # Test search discovery
    discovery = SearchDiscovery()
    
    # Test targeted domain search
    target_domains = ['quantstart.com', 'blog.quantinsti.com']
    results = discovery.search_targeted_domains('algorithmic trading python', target_domains)
    
    print(f"Found {len(results)} unique search results")
    for result in results[:3]:  # Show first 3
        print(f"  {result['url']} ({result['source']}, quality: {result['quality_estimate']:.2f})")