#!/usr/bin/env python3
"""
Simple Performance Test for IntelForge

Quick performance validation without heavy dependencies.
Tests core performance improvements: selectolax vs BeautifulSoup, httpx vs requests.

Usage:
    python scripts/simple_performance_test.py
"""

import json
import time
from datetime import datetime

# Performance libraries (should be available)
import httpx
import selectolax.parser as sp

# Comparison libraries (optional)
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


def time_function(func, *args, **kwargs):
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


def generate_test_html():
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
    """ * 500  # Repeat to make it larger for meaningful timing


def test_selectolax_parsing(html_content):
    """Test selectolax HTML parsing performance."""
    def parse_with_selectolax():
        tree = sp.HTMLParser(html_content)
        
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
    
    return time_function(parse_with_selectolax)


def test_beautifulsoup_parsing(html_content):
    """Test BeautifulSoup HTML parsing performance."""
    if not BS4_AVAILABLE:
        return {
            'time': 0,
            'success': False,
            'result': None,
            'error': 'BeautifulSoup not available'
        }
    
    def parse_with_bs4():
        soup = BeautifulSoup(html_content, 'html.parser')
        
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
    
    return time_function(parse_with_bs4)


def test_httpx_requests():
    """Test httpx HTTP request performance."""
    test_urls = [
        'https://httpbin.org/json',
        'https://httpbin.org/html'
    ]
    
    def make_requests_with_httpx():
        results = []
        with httpx.Client(timeout=10.0) as client:
            for url in test_urls:
                try:
                    response = client.get(url)
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
    
    return time_function(make_requests_with_httpx)


def test_requests_requests():
    """Test requests library HTTP request performance."""
    if not REQUESTS_AVAILABLE:
        return {
            'time': 0,
            'success': False,
            'result': None,
            'error': 'requests library not available'
        }
    
    test_urls = [
        'https://httpbin.org/json',
        'https://httpbin.org/html'
    ]
    
    def make_requests_with_requests():
        results = []
        for url in test_urls:
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
    
    return time_function(make_requests_with_requests)


def main():
    """Run simple performance tests."""
    print("🚀 IntelForge Simple Performance Test")
    print("=====================================")
    
    # Generate test HTML
    print("📝 Generating test HTML content...")
    html_content = generate_test_html()
    print(f"   Generated {len(html_content):,} characters of HTML")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'html_parsing': {},
        'http_requests': {}
    }
    
    # Test HTML parsing
    print("\n🔬 Testing HTML Parsing Performance...")
    
    print("  📊 Testing selectolax...")
    selectolax_result = test_selectolax_parsing(html_content)
    results['html_parsing']['selectolax'] = selectolax_result
    
    if selectolax_result['success']:
        print(f"    ✅ selectolax: {selectolax_result['time']:.4f} seconds")
    else:
        print(f"    ❌ selectolax failed: {selectolax_result['error']}")
    
    print("  📊 Testing BeautifulSoup...")
    bs4_result = test_beautifulsoup_parsing(html_content)
    results['html_parsing']['bs4'] = bs4_result
    
    if bs4_result['success']:
        print(f"    ✅ BeautifulSoup: {bs4_result['time']:.4f} seconds")
        
        # Calculate performance improvement
        if selectolax_result['success']:
            improvement = bs4_result['time'] / selectolax_result['time']
            print(f"    🚀 selectolax is {improvement:.1f}x faster than BeautifulSoup")
    else:
        print(f"    ❌ BeautifulSoup: {bs4_result['error']}")
    
    # Test HTTP requests
    print("\n🌐 Testing HTTP Request Performance...")
    
    print("  📊 Testing httpx...")
    httpx_result = test_httpx_requests()
    results['http_requests']['httpx'] = httpx_result
    
    if httpx_result['success']:
        print(f"    ✅ httpx: {httpx_result['time']:.4f} seconds")
    else:
        print(f"    ❌ httpx failed: {httpx_result['error']}")
    
    print("  📊 Testing requests...")
    requests_result = test_requests_requests()
    results['http_requests']['requests'] = requests_result
    
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
    
    # Summary
    print("\n" + "="*50)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("="*50)
    
    if selectolax_result['success'] and bs4_result['success']:
        improvement = bs4_result['time'] / selectolax_result['time']
        print(f"⚡ HTML Parsing: selectolax is {improvement:.1f}x faster than BeautifulSoup")
    
    if httpx_result['success'] and requests_result['success']:
        ratio = requests_result['time'] / httpx_result['time']
        if ratio > 1:
            print(f"🌐 HTTP Requests: httpx is {ratio:.1f}x faster than requests")
        else:
            print(f"🌐 HTTP Requests: Similar performance (requests {1/ratio:.1f}x faster)")
    
    print(f"\n📅 Test completed: {results['timestamp']}")
    print("✅ IntelForge is using optimized performance libraries!")
    
    # Save results
    try:
        with open('vault/logs/simple_performance_test.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to: vault/logs/simple_performance_test.json")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")


if __name__ == "__main__":
    main()