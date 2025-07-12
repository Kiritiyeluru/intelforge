#!/usr/bin/env python3
"""
Simple Stealth Scraper - HTTP-based Anti-Detection
Uses httpx + stealth-requests for maximum stealth with financial sites
Simpler alternative to browser automation for HTTP-only scraping
"""

import argparse
import os
import sys
import yaml
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# HTTP libraries with stealth features
try:
    import httpx
    from selectolax.parser import HTMLParser
    # Try to import stealth-requests for enhanced anti-detection
    try:
        from stealth_requests import StealthSession
        STEALTH_AVAILABLE = True
    except ImportError:
        STEALTH_AVAILABLE = False
        print("📝 Note: stealth-requests not available, using basic httpx")
except ImportError:
    print("Error: Required packages not installed. Run: uv add httpx selectolax")
    sys.exit(1)

def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')

def generate_content_hash(content: str) -> str:
    """Generate SHA256 hash for content."""
    import hashlib
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def get_stealth_headers() -> Dict[str, str]:
    """Generate realistic browser headers for stealth."""
    user_agents = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]
    
    accept_languages = [
        "en-US,en;q=0.9",
        "en-US,en;q=0.8,es;q=0.6",
        "en-GB,en;q=0.9,en-US;q=0.8"
    ]
    
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": random.choice(accept_languages),
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-CH-UA": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Linux"',
    }

def create_stealth_session() -> httpx.Client:
    """Create an HTTP session with stealth capabilities."""
    if STEALTH_AVAILABLE:
        # Use stealth-requests for maximum anti-detection
        session = StealthSession()
        return session
    else:
        # Use httpx with stealth headers
        headers = get_stealth_headers()
        client = httpx.Client(
            headers=headers,
            timeout=30.0,
            follow_redirects=True,
            verify=True
        )
        return client

def extract_content_with_selectolax(html: str, url: str) -> Dict[str, str]:
    """Extract content using selectolax parser."""
    tree = HTMLParser(html)
    
    # Extract title
    title_element = tree.css_first('title')
    title = title_element.text() if title_element else ''
    
    # Extract meta description
    meta_desc = tree.css_first('meta[name="description"]')
    meta_description = meta_desc.attributes.get('content', '') if meta_desc else ''
    
    # Extract meta keywords
    meta_kw = tree.css_first('meta[name="keywords"]')
    meta_keywords = meta_kw.attributes.get('content', '') if meta_kw else ''
    
    # Try to find main content using common selectors
    main_content_selectors = [
        'main',
        'article',
        '.content',
        '.main-content',
        '#content',
        '.post-content',
        '.entry-content',
        '[role="main"]'
    ]
    
    main_content = ''
    for selector in main_content_selectors:
        elements = tree.css(selector)
        if elements:
            main_content = '\n\n'.join([elem.text() for elem in elements])
            break
    
    # If no main content found, get body text
    if not main_content:
        body = tree.css_first('body')
        if body:
            main_content = body.text()
        else:
            main_content = tree.text()
    
    # Remove script and style content
    for element in tree.css('script, style'):
        element.decompose()
    
    # Clean up whitespace
    main_content = ' '.join(main_content.split())
    
    return {
        'title': title.strip(),
        'meta_description': meta_description.strip(),
        'meta_keywords': meta_keywords.strip(),
        'main_content': main_content.strip(),
        'full_text': tree.text().strip()
    }

def stealth_scrape_url(url: str, session: httpx.Client, delay: int = 3) -> Dict:
    """Scrape a single URL with stealth capabilities."""
    print(f"🕵️  Scraping: {url}")
    
    try:
        # Add random delay to simulate human browsing
        if delay > 0:
            sleep_time = delay + random.uniform(0, 2)
            time.sleep(sleep_time)
        
        # Make request with stealth session
        response = session.get(url)
        response.raise_for_status()
        
        # Check for common bot detection patterns
        html_content = response.text
        html_lower = html_content.lower()
        
        bot_indicators = [
            "access denied",
            "blocked", 
            "robot",
            "bot detected",
            "cloudflare",
            "security check",
            "captcha",
            "rate limit",
            "forbidden"
        ]
        
        bot_detected = any(indicator in html_lower for indicator in bot_indicators)
        
        # Extract content
        extracted = extract_content_with_selectolax(html_content, url)
        
        result = {
            'url': url,
            'final_url': str(response.url),
            'status_code': response.status_code,
            'title': extracted['title'],
            'meta_description': extracted['meta_description'],
            'meta_keywords': extracted['meta_keywords'],
            'main_content': extracted['main_content'],
            'full_text': extracted['full_text'],
            'content_length': len(extracted['main_content']),
            'html_length': len(html_content),
            'bot_detected': bot_detected,
            'status': 'success' if not bot_detected else 'detection_warning',
            'timestamp': datetime.now().isoformat(),
            'headers': dict(response.headers),
            'stealth_method': 'stealth-requests' if STEALTH_AVAILABLE else 'httpx+headers'
        }
        
        if bot_detected:
            print(f"   ⚠️  Possible bot detection")
        else:
            print(f"   ✅ Stealth successful - {len(extracted['main_content']):,} chars")
            
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            'url': url,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'stealth_method': 'stealth-requests' if STEALTH_AVAILABLE else 'httpx+headers'
        }

def format_result_markdown(result: Dict) -> str:
    """Format scraping result into Obsidian-compatible markdown."""
    status = result.get('status', 'unknown')
    bot_detected = result.get('bot_detected', False)
    
    content = f"""---
source: web_stealth_http
type: stealth_scraping
date: {datetime.now().strftime('%Y-%m-%d')}
url: {result.get('url', '')}
final_url: {result.get('final_url', '')}
title: "{result.get('title', '')}"
status: {status}
status_code: {result.get('status_code', '')}
bot_detected: {bot_detected}
content_length: {result.get('content_length', 0)}
html_length: {result.get('html_length', 0)}
stealth_method: {result.get('stealth_method', '')}
content_hash: {generate_content_hash(result.get('main_content', ''))}
timestamp: {result.get('timestamp', '')}
---

# {result.get('title', 'Untitled Page')}

**URL:** {result.get('url', '')}  
**Final URL:** {result.get('final_url', '')}  
**Status:** {status} (HTTP {result.get('status_code', 'N/A')})  
**Bot Detection:** {'⚠️ WARNING' if bot_detected else '✅ Clear'}  
**Content Length:** {result.get('content_length', 0):,} characters  
**Stealth Method:** {result.get('stealth_method', '')}  
**Scraped:** {result.get('timestamp', '')}  

## Main Content

{result.get('main_content', 'No content extracted')}

{f"## Meta Description\n\n{result.get('meta_description', '')}\n" if result.get('meta_description') else ""}

{f"## Meta Keywords\n\n{result.get('meta_keywords', '')}\n" if result.get('meta_keywords') else ""}

{f"## Error Details\n\n```\n{result.get('error', '')}\n```\n" if result.get('error') else ""}

## Response Headers

```json
{yaml.dump(result.get('headers', {}), default_flow_style=False) if result.get('headers') else 'No headers available'}
```

## Tags

#web_scraping #stealth #http_only {"#bot_detected" if bot_detected else "#stealth_success"} #{result.get('stealth_method', 'unknown').replace('-', '_')}

---
*Scraped via HTTP stealth framework on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    return content

def save_result(result: Dict, config: Dict) -> bool:
    """Save scraping result to vault directory."""
    if result.get('status') == 'error' and not result.get('main_content'):
        print("   📝 Skipping save for failed scrape with no content")
        return False
    
    # Get vault directory from config
    vault_dir = Path(config.get('vault_directory', 'vault'))
    stealth_dir = vault_dir / "notes" / "stealth_http"
    stealth_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    url_slug = slugify(result.get('final_url', result.get('url', 'unknown')))[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"stealth_http_{url_slug}_{timestamp}.md"
    
    # Format content
    content = format_result_markdown(result)
    
    # Save file
    file_path = stealth_dir / filename
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   💾 Saved: {filename}")
        return True
        
    except Exception as e:
        print(f"   ❌ Save failed: {e}")
        return False

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Simple Stealth Scraper - HTTP Anti-Detection")
    parser.add_argument('--url', type=str, help="Single URL to scrape")
    parser.add_argument('--urls', type=str, nargs='+', help="Multiple URLs to scrape")
    parser.add_argument('--file', type=str, help="File containing URLs (one per line)")
    parser.add_argument('--config', type=str, default="config/config.yaml", help="Path to config file")
    parser.add_argument('--dry-run', action='store_true', help="Run in dry-run mode")
    parser.add_argument('--delay', type=int, default=3, help="Delay between requests (seconds)")
    
    args = parser.parse_args()
    
    # Collect URLs to scrape
    urls = []
    if args.url:
        urls.append(args.url)
    if args.urls:
        urls.extend(args.urls)
    if args.file:
        try:
            with open(args.file, 'r') as f:
                file_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                urls.extend(file_urls)
        except FileNotFoundError:
            print(f"❌ Error: URL file '{args.file}' not found")
            sys.exit(1)
    
    if not urls:
        print("❌ Error: No URLs provided. Use --url, --urls, or --file")
        sys.exit(1)
    
    # Set dry-run mode if specified
    if args.dry_run:
        os.environ['INTELFORGE_DRY_RUN'] = 'true'
        print("🔍 Running in dry-run mode")
    
    # Load configuration
    config = load_config(args.config)
    
    print(f"🕵️  Simple Stealth Scraper - HTTP Anti-Detection")
    print(f"📄 URLs to scrape: {len(urls)}")
    print(f"⏱️  Delay between requests: {args.delay}s")
    print(f"🛡️  Stealth method: {'stealth-requests' if STEALTH_AVAILABLE else 'httpx + realistic headers'}")
    print("-" * 60)
    
    try:
        # Create stealth session
        session = create_stealth_session()
        
        results = []
        successful_saves = 0
        total_content_length = 0
        bot_detections = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Processing: {url}")
            
            result = stealth_scrape_url(url, session, args.delay)
            results.append(result)
            
            if result.get('bot_detected'):
                bot_detections += 1
            
            total_content_length += result.get('content_length', 0)
            
            if not args.dry_run:
                if save_result(result, config):
                    successful_saves += 1
            else:
                print(f"   🔍 Dry-run: Would save result")
                successful_saves += 1
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 HTTP Stealth Scraping Summary:")
        print(f"   URLs processed: {len(results)}")
        print(f"   Successfully saved: {successful_saves}")
        print(f"   Total content: {total_content_length:,} characters")
        print(f"   Bot detections: {bot_detections}/{len(results)}")
        print(f"   Success rate: {(len(results)-bot_detections)/len(results)*100:.1f}%")
        print(f"   Stealth method: {'stealth-requests' if STEALTH_AVAILABLE else 'httpx + realistic headers'}")
        
        if not args.dry_run and successful_saves > 0:
            print(f"\n✅ Content saved to vault/notes/stealth_http/")
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Close session
        if hasattr(session, 'close'):
            session.close()

if __name__ == "__main__":
    main()