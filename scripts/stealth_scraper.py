#!/usr/bin/env python3
"""
Stealth Scraper - Advanced Anti-Detection Web Scraping
Uses Botasaurus framework for undetectable browser automation
Designed for protected financial sites (Finviz, Yahoo Finance, etc.)
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml

# Botasaurus for stealth browser automation
try:
    from botasaurus.browser import browser
except ImportError:
    print("Error: botasaurus not installed. Run: uv add botasaurus")
    sys.exit(1)


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re

    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def generate_content_hash(content: str) -> str:
    """Generate SHA256 hash for content."""
    import hashlib

    return hashlib.sha256(content.encode()).hexdigest()[:16]


@browser(
    # Basic stealth configuration
    headless=True,
    profile="stealth-profile",
    # Block resources for speed and stealth
    block_images_and_css=True,
    # Language settings
    lang="en-US",
    # Wait for complete page load
    wait_for_complete_page_load=True,
)
def stealth_scrape_page(driver, url: str):
    """
    Scrape a single page with maximum stealth capabilities.

    Args:
        driver: Botasaurus driver instance
        url: URL to scrape

    Returns:
        Dict with extracted content and metadata
    """
    try:
        print(f"Navigating to: {url}")

        # Navigate with human-like behavior
        driver.get(url)

        # Wait for page to load completely using Botasaurus sleep
        driver.sleep(3)

        # Check for bot detection using correct API methods
        page_title = driver.title
        page_text = driver.page_text

        # Common bot detection indicators
        bot_indicators = [
            "access denied",
            "blocked",
            "robot",
            "bot detected",
            "cloudflare",
            "security check",
            "captcha",
        ]

        detected = any(indicator in page_text.lower() for indicator in bot_indicators)

        if detected:
            print(f"⚠️  Possible bot detection on {url}")
            print(f"Page title: {page_title}")

        # Extract content
        result = {
            "url": url,
            "title": page_title,
            "text_content": page_text,
            "html_content": driver.page_html,
            "final_url": driver.current_url,
            "status": "success" if not detected else "detection_warning",
            "bot_detected": detected,
            "timestamp": datetime.now().isoformat(),
            "content_length": len(page_text),
            "html_length": len(driver.page_html),
        }

        # Try to extract main content using common selectors
        main_content_selectors = [
            "main",
            "article",
            ".content",
            ".main-content",
            "#content",
            ".post-content",
            ".entry-content",
        ]

        for selector in main_content_selectors:
            try:
                # Use Botasaurus methods for element selection
                if driver.is_element_present(selector):
                    main_text = driver.get_text(selector)
                    if main_text:
                        result["main_content"] = main_text
                        break
            except:
                continue

        # Extract meta information using Botasaurus methods
        try:
            # Try to get meta description
            if driver.is_element_present('meta[name="description"]'):
                result["meta_description"] = driver.get_attribute(
                    'meta[name="description"]', "content"
                )

            # Try to get meta keywords
            if driver.is_element_present('meta[name="keywords"]'):
                result["meta_keywords"] = driver.get_attribute(
                    'meta[name="keywords"]', "content"
                )
        except:
            pass

        return result

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            "url": url,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def format_result_markdown(result: Dict) -> str:
    """Format scraping result into Obsidian-compatible markdown."""
    status = result.get("status", "unknown")
    bot_detected = result.get("bot_detected", False)

    content = f"""---
source: web_stealth
type: stealth_scraping
date: {datetime.now().strftime("%Y-%m-%d")}
url: {result.get("url", "")}
final_url: {result.get("final_url", "")}
title: "{result.get("title", "")}"
status: {status}
bot_detected: {bot_detected}
content_length: {result.get("content_length", 0)}
html_length: {result.get("html_length", 0)}
content_hash: {generate_content_hash(result.get("text_content", ""))}
timestamp: {result.get("timestamp", "")}
---

# {result.get("title", "Untitled Page")}

**URL:** {result.get("url", "")}
**Final URL:** {result.get("final_url", "")}
**Status:** {status}
**Bot Detection:** {"⚠️ WARNING" if bot_detected else "✅ Clear"}
**Content Length:** {result.get("content_length", 0):,} characters
**Scraped:** {result.get("timestamp", "")}

## Main Content

{result.get("main_content", result.get("text_content", "No content extracted"))}

{f"## Meta Description\n\n{result.get('meta_description', '')}\n" if result.get("meta_description") else ""}

{f"## Meta Keywords\n\n{result.get('meta_keywords', '')}\n" if result.get("meta_keywords") else ""}

{f"## Error Details\n\n```\n{result.get('error', '')}\n```\n" if result.get("error") else ""}

## Tags

#web_scraping #stealth #anti_detection {"#bot_detected" if bot_detected else "#stealth_success"}

---
*Scraped via Botasaurus stealth framework on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    return content


def save_result(result: Dict, config: Dict) -> bool:
    """Save scraping result to vault directory."""
    if result.get("status") == "error" and not result.get("text_content"):
        print("Skipping save for failed scrape with no content")
        return False

    # Get vault directory from config
    vault_dir = Path(config.get("vault_directory", "vault"))
    stealth_dir = vault_dir / "notes" / "stealth_scraping"
    stealth_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    url_slug = slugify(result.get("final_url", result.get("url", "unknown")))[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stealth_{url_slug}_{timestamp}.md"

    # Format content
    content = format_result_markdown(result)

    # Save file
    file_path = stealth_dir / filename
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Saved: {filename}")
        return True

    except Exception as e:
        print(f"❌ Failed to save {filename}: {e}")
        return False


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Stealth Scraper - Advanced Anti-Detection Web Scraping"
    )
    parser.add_argument("--url", type=str, help="Single URL to scrape")
    parser.add_argument("--urls", type=str, nargs="+", help="Multiple URLs to scrape")
    parser.add_argument("--file", type=str, help="File containing URLs (one per line)")
    parser.add_argument(
        "--config", type=str, default="config/config.yaml", help="Path to config file"
    )
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument(
        "--delay", type=int, default=3, help="Delay between requests (seconds)"
    )

    args = parser.parse_args()

    # Collect URLs to scrape
    urls = []
    if args.url:
        urls.append(args.url)
    if args.urls:
        urls.extend(args.urls)
    if args.file:
        try:
            with open(args.file, "r") as f:
                file_urls = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
                urls.extend(file_urls)
        except FileNotFoundError:
            print(f"Error: URL file '{args.file}' not found")
            sys.exit(1)

    if not urls:
        print("Error: No URLs provided. Use --url, --urls, or --file")
        sys.exit(1)

    # Set dry-run mode if specified
    if args.dry_run:
        os.environ["INTELFORGE_DRY_RUN"] = "true"
        print("Running in dry-run mode")

    # Load configuration
    config = load_config(args.config)

    print("Stealth Scraper - Botasaurus Framework")
    print(f"URLs to scrape: {len(urls)}")
    print(f"Delay between requests: {args.delay}s")
    print("-" * 50)

    try:
        # Scrape URLs using Botasaurus
        results = stealth_scrape_page(urls)

        successful_saves = 0
        total_content_length = 0
        bot_detections = 0

        for result in results:
            print(f"\n📄 Processing: {result.get('url', 'Unknown URL')}")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Content: {result.get('content_length', 0):,} characters")

            if result.get("bot_detected"):
                bot_detections += 1
                print("   ⚠️  Bot detection warning")
            else:
                print("   ✅ Stealth successful")

            total_content_length += result.get("content_length", 0)

            if not args.dry_run:
                if save_result(result, config):
                    successful_saves += 1
            else:
                print("   🔍 Dry-run: Would save result")
                successful_saves += 1

        # Summary
        print(f"\n{'=' * 50}")
        print("📊 Stealth Scraping Summary:")
        print(f"   URLs processed: {len(results)}")
        print(f"   Successfully saved: {successful_saves}")
        print(f"   Total content: {total_content_length:,} characters")
        print(f"   Bot detections: {bot_detections}/{len(results)}")
        print(
            f"   Success rate: {(len(results) - bot_detections) / len(results) * 100:.1f}%"
        )
        print("   Framework: Botasaurus (undetectable)")

        if not args.dry_run and successful_saves > 0:
            print("\n✅ Content saved to vault/notes/stealth_scraping/")

    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
