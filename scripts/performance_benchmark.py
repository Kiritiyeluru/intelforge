#!/usr/bin/env python3
"""
Performance Benchmark Suite for IntelForge

Comprehensive performance testing to validate optimization improvements.
Tests HTML parsing, HTTP requests, and overall scraping performance.

Usage:
    python scripts/performance_benchmark.py [--detailed] [--save-results]

Example:
    python scripts/performance_benchmark.py --detailed --save-results
"""

import argparse
import asyncio
import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Performance libraries
import httpx
import selectolax.parser as sp

# Comparison libraries (if available)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

# IntelForge modules
from scrapers.web_scraper import WebScraper
from scrapers.github_scraper import GitHubScraper


class PerformanceBenchmark:
    """Comprehensive performance benchmark suite."""
    
    def __init__(self):
        """Initialize benchmark suite."""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'html_parsing': {},
            'http_requests': {},
            'full_scraping': {},
            'summary': {}
        }
        
        # Test HTML content for parsing
        self.test_html = self._generate_test_html()
        self.test_urls = [
            'https://httpbin.org/html',
            'https://httpbin.org/json',
            'https://jsonplaceholder.typicode.com/posts/1'
        ]
    
    def _generate_test_html(self) -> str:
        """Generate HTML content for parsing tests."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Test Page</title>
        </head>
        <body>
            <h1>Main Title</h1>
            <div class="content">
                <p>This is test paragraph 1 with trading content.</p>
                <p>This is test paragraph 2 about algorithmic strategies.</p>
                <p>This is test paragraph 3 discussing market analysis.</p>
            </div>
            <div class="sidebar">
                <h2>Sidebar Title</h2>
                <ul>
                    <li><a href="/link1">Trading Link 1</a></li>
                    <li><a href="/link2">Strategy Link 2</a></li>
                    <li><a href="/link3">Analysis Link 3</a></li>
                </ul>
            </div>
            <table class="data-table">
                <tr><th>Symbol</th><th>Price</th><th>Change</th></tr>
                <tr><td>AAPL</td><td>150.00</td><td>+2.5%</td></tr>
                <tr><td>GOOGL</td><td>2800.00</td><td>-1.2%</td></tr>
                <tr><td>MSFT</td><td>350.00</td><td>+0.8%</td></tr>
            </table>
        </body>
        </html>
        """ * 100  # Repeat to make it larger
    
    def _time_function(self, func, *args, **kwargs):
        """Time a function execution."""
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            return {
                'time': end_time - start_time,
                'success': True,
                'result': result,
                'error': None
            }
        except Exception as e:
            end_time = time.perf_counter()
            return {
                'time': end_time - start_time,
                'success': False,
                'result': None,
                'error': str(e)
            }
    
    def test_html_parsing_selectolax(self) -> Dict:
        """Test selectolax HTML parsing performance."""
        def parse_with_selectolax():
            tree = sp.HTMLParser(self.test_html)
            
            # Extract various elements
            title = tree.css_first('title')
            title_text = title.text() if title else ''
            
            paragraphs = tree.css('p')
            paragraph_texts = [p.text() for p in paragraphs]
            
            links = tree.css('a')
            link_texts = [link.text() for link in links]
            
            table_rows = tree.css('tr')
            table_data = [row.text() for row in table_rows]
            
            return {
                'title': title_text,
                'paragraphs': len(paragraph_texts),
                'links': len(link_texts),
                'table_rows': len(table_data)
            }
        
        return self._time_function(parse_with_selectolax)
    
    def test_html_parsing_bs4(self) -> Dict:
        """Test BeautifulSoup HTML parsing performance."""
        if not BS4_AVAILABLE:
            return {
                'time': 0,
                'success': False,
                'result': None,
                'error': 'BeautifulSoup not available'
            }
        
        def parse_with_bs4():
            soup = BeautifulSoup(self.test_html, 'html.parser')
            
            # Extract various elements
            title = soup.find('title')
            title_text = title.get_text() if title else ''
            
            paragraphs = soup.find_all('p')
            paragraph_texts = [p.get_text() for p in paragraphs]
            
            links = soup.find_all('a')
            link_texts = [link.get_text() for link in links]
            
            table_rows = soup.find_all('tr')
            table_data = [row.get_text() for row in table_rows]
            
            return {
                'title': title_text,
                'paragraphs': len(paragraph_texts),
                'links': len(link_texts),
                'table_rows': len(table_data)
            }
        
        return self._time_function(parse_with_bs4)
    
    def test_http_requests_httpx(self) -> Dict:
        """Test httpx HTTP request performance."""
        def make_requests_with_httpx():
            results = []
            with httpx.Client() as client:
                for url in self.test_urls:
                    try:
                        response = client.get(url, timeout=10.0)
                        results.append({
                            'url': url,
                            'status': response.status_code,
                            'size': len(response.content)
                        })
                    except Exception as e:
                        results.append({
                            'url': url,
                            'status': 'error',
                            'error': str(e)
                        })
            return results
        
        return self._time_function(make_requests_with_httpx)
    
    def test_http_requests_requests(self) -> Dict:
        """Test requests library HTTP request performance."""
        if not REQUESTS_AVAILABLE:
            return {
                'time': 0,
                'success': False,
                'result': None,
                'error': 'requests library not available'
            }
        
        def make_requests_with_requests():
            results = []
            for url in self.test_urls:
                try:
                    response = requests.get(url, timeout=10.0)
                    results.append({
                        'url': url,
                        'status': response.status_code,
                        'size': len(response.content)
                    })
                except Exception as e:
                    results.append({
                        'url': url,
                        'status': 'error',
                        'error': str(e)
                    })
            return results
        
        return self._time_function(make_requests_with_requests)
    
    def test_full_scraping_web(self) -> Dict:
        """Test full web scraping performance."""
        def run_web_scraper():
            scraper = WebScraper()
            # Test extraction on a single URL
            test_url = "https://httpbin.org/html"
            result = scraper._extract_article_content(test_url)
            scraper.close()
            return result
        
        return self._time_function(run_web_scraper)
    
    def test_full_scraping_github(self) -> Dict:
        """Test full GitHub scraping performance."""
        def run_github_scraper():
            scraper = GitHubScraper()
            # Test a small search
            results = scraper.search_repositories("python testing", limit=2)
            scraper.close()
            return results
        
        return self._time_function(run_github_scraper)
    
    def run_html_parsing_benchmarks(self):
        """Run HTML parsing benchmarks."""
        print("🔬 Testing HTML Parsing Performance...")
        
        # Test selectolax
        print("  📊 Testing selectolax...")
        selectolax_result = self.test_html_parsing_selectolax()
        self.results['html_parsing']['selectolax'] = selectolax_result
        
        if selectolax_result['success']:
            print(f"    ✅ selectolax: {selectolax_result['time']:.4f} seconds")
        else:
            print(f"    ❌ selectolax failed: {selectolax_result['error']}")
        
        # Test BeautifulSoup
        print("  📊 Testing BeautifulSoup...")
        bs4_result = self.test_html_parsing_bs4()
        self.results['html_parsing']['bs4'] = bs4_result
        
        if bs4_result['success']:
            print(f"    ✅ BeautifulSoup: {bs4_result['time']:.4f} seconds")
            
            # Calculate performance improvement
            if selectolax_result['success']:
                improvement = bs4_result['time'] / selectolax_result['time']
                print(f"    🚀 selectolax is {improvement:.1f}x faster than BeautifulSoup")
        else:
            print(f"    ❌ BeautifulSoup: {bs4_result['error']}")
    
    def run_http_benchmarks(self):
        """Run HTTP request benchmarks."""
        print("\n🌐 Testing HTTP Request Performance...")
        
        # Test httpx
        print("  📊 Testing httpx...")
        httpx_result = self.test_http_requests_httpx()
        self.results['http_requests']['httpx'] = httpx_result
        
        if httpx_result['success']:
            print(f"    ✅ httpx: {httpx_result['time']:.4f} seconds")
        else:
            print(f"    ❌ httpx failed: {httpx_result['error']}")
        
        # Test requests
        print("  📊 Testing requests...")
        requests_result = self.test_http_requests_requests()
        self.results['http_requests']['requests'] = requests_result
        
        if requests_result['success']:
            print(f"    ✅ requests: {requests_result['time']:.4f} seconds")
            
            # Calculate performance comparison
            if httpx_result['success']:
                ratio = requests_result['time'] / httpx_result['time']
                if ratio > 1:
                    print(f"    🚀 httpx is {ratio:.1f}x faster than requests")
                else:
                    print(f"    📊 requests is {1/ratio:.1f}x faster than httpx")
        else:
            print(f"    ❌ requests: {requests_result['error']}")
    
    def run_full_scraping_benchmarks(self):
        """Run full scraping benchmarks."""
        print("\n🕷️ Testing Full Scraping Performance...")
        
        # Test web scraper
        print("  📊 Testing web scraper...")
        web_result = self.test_full_scraping_web()
        self.results['full_scraping']['web'] = web_result
        
        if web_result['success']:
            print(f"    ✅ Web scraper: {web_result['time']:.4f} seconds")
        else:
            print(f"    ❌ Web scraper failed: {web_result['error']}")
        
        # Test GitHub scraper
        print("  📊 Testing GitHub scraper...")
        github_result = self.test_full_scraping_github()
        self.results['full_scraping']['github'] = github_result
        
        if github_result['success']:
            print(f"    ✅ GitHub scraper: {github_result['time']:.4f} seconds")
        else:
            print(f"    ❌ GitHub scraper failed: {github_result['error']}")
    
    def generate_summary(self):
        """Generate performance summary."""
        summary = {
            'html_parsing_improvement': None,
            'http_requests_comparison': None,
            'total_tests': 0,
            'successful_tests': 0,
            'performance_gains': []
        }
        
        # HTML parsing improvement
        selectolax = self.results['html_parsing'].get('selectolax', {})
        bs4 = self.results['html_parsing'].get('bs4', {})
        
        if selectolax.get('success') and bs4.get('success'):
            improvement = bs4['time'] / selectolax['time']
            summary['html_parsing_improvement'] = improvement
            summary['performance_gains'].append({
                'category': 'HTML Parsing',
                'improvement': f"{improvement:.1f}x faster",
                'technology': 'selectolax vs BeautifulSoup'
            })
        
        # HTTP requests comparison
        httpx_req = self.results['http_requests'].get('httpx', {})
        requests_req = self.results['http_requests'].get('requests', {})
        
        if httpx_req.get('success') and requests_req.get('success'):
            ratio = requests_req['time'] / httpx_req['time']
            summary['http_requests_comparison'] = ratio
            if ratio > 1:
                summary['performance_gains'].append({
                    'category': 'HTTP Requests',
                    'improvement': f"{ratio:.1f}x faster",
                    'technology': 'httpx vs requests'
                })
        
        # Count test results
        all_results = []
        for category in self.results.values():
            if isinstance(category, dict):
                for test_result in category.values():
                    if isinstance(test_result, dict) and 'success' in test_result:
                        all_results.append(test_result)
        
        summary['total_tests'] = len(all_results)
        summary['successful_tests'] = sum(1 for r in all_results if r['success'])
        
        self.results['summary'] = summary
    
    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE BENCHMARK SUMMARY")
        print("="*60)
        
        summary = self.results['summary']
        
        print(f"🧪 Tests Run: {summary['successful_tests']}/{summary['total_tests']}")
        
        if summary['performance_gains']:
            print(f"\n🚀 Performance Improvements:")
            for gain in summary['performance_gains']:
                print(f"  • {gain['category']}: {gain['improvement']} ({gain['technology']})")
        
        if summary['html_parsing_improvement']:
            print(f"\n⚡ HTML Parsing: selectolax is {summary['html_parsing_improvement']:.1f}x faster than BeautifulSoup")
        
        if summary['http_requests_comparison']:
            if summary['http_requests_comparison'] > 1:
                print(f"🌐 HTTP Requests: httpx is {summary['http_requests_comparison']:.1f}x faster than requests")
            else:
                print(f"🌐 HTTP Requests: Similar performance between httpx and requests")
        
        print(f"\n📅 Benchmark completed: {self.results['timestamp']}")
        print("="*60)
    
    def save_results(self, output_file: str = None):
        """Save benchmark results to file."""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"vault/logs/performance_benchmark_{timestamp}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {output_path}")
    
    def run_all_benchmarks(self, detailed: bool = False):
        """Run all performance benchmarks."""
        print("🚀 IntelForge Performance Benchmark Suite")
        print("==========================================")
        
        try:
            self.run_html_parsing_benchmarks()
            self.run_http_benchmarks()
            
            if detailed:
                self.run_full_scraping_benchmarks()
            
            self.generate_summary()
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ Benchmark failed: {e}")
            if detailed:
                traceback.print_exc()


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Performance Benchmark Suite for IntelForge")
    parser.add_argument('--detailed', action='store_true', help="Run detailed benchmarks including full scrapers")
    parser.add_argument('--save-results', action='store_true', help="Save results to file")
    parser.add_argument('--output', type=str, help="Output file path for results")
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks(detailed=args.detailed)
    
    if args.save_results:
        benchmark.save_results(args.output)


if __name__ == "__main__":
    main()