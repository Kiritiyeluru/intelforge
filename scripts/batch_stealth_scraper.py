#!/usr/bin/env python3
"""
Batch Stealth Scraper - High-Performance Concurrent Web Scraping

Optimized for high-volume scraping operations with:
- Concurrent processing for maximum throughput
- Intelligent rate limiting and retry logic
- Memory-efficient batch operations
- Progress tracking and failure recovery
- Support for both HTTP and browser-based stealth methods
"""

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class BatchStealthScraper:
    """High-performance batch scraper with concurrent processing."""

    def __init__(
        self,
        max_workers: int = 5,
        delay_range: tuple = (2, 5),
        retry_attempts: int = 3,
        use_browser: bool = False,
    ):
        """
        Initialize batch scraper.

        Args:
            max_workers: Maximum concurrent workers
            delay_range: Random delay range between requests (min, max) seconds
            retry_attempts: Number of retry attempts for failed requests
            use_browser: Use browser-based scraping (slower but more capable)
        """
        self.max_workers = max_workers
        self.delay_range = delay_range
        self.retry_attempts = retry_attempts
        self.use_browser = use_browser
        self.results = []
        self.failed_urls = []

    def scrape_single_url(self, url: str, attempt: int = 1) -> Dict[str, Any]:
        """
        Scrape a single URL with error handling and retries.

        Args:
            url: URL to scrape
            attempt: Current attempt number

        Returns:
            Dict with scraping results and metadata
        """
        start_time = time.time()

        try:
            # Choose scraping method
            if self.use_browser:
                # Use Botasaurus for JavaScript-heavy sites
                result = subprocess.run(
                    [sys.executable, "scripts/stealth_scraper.py", "--url", url],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=120,
                )
            else:
                # Use HTTP stealth scraper for speed
                result = subprocess.run(
                    [sys.executable, "scripts/stealth_scraper_simple.py", "--url", url],
                    capture_output=True,
                    text=True,
                    cwd=project_root,
                    timeout=60,
                )

            execution_time = time.time() - start_time

            # Parse success/failure
            success = result.returncode == 0

            # Extract content length from output if available
            content_length = 0
            if "Content Length:" in result.stdout:
                try:
                    line = [
                        l for l in result.stdout.split("\n") if "Content Length:" in l
                    ][0]
                    content_length = int(
                        line.split(":")[1].strip().replace(",", "").split()[0]
                    )
                except:
                    pass

            return {
                "url": url,
                "success": success,
                "attempt": attempt,
                "execution_time": execution_time,
                "content_length": content_length,
                "method": "browser" if self.use_browser else "http",
                "timestamp": datetime.now().isoformat(),
                "output": result.stdout if success else None,
                "error": result.stderr if not success else None,
            }

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return {
                "url": url,
                "success": False,
                "attempt": attempt,
                "execution_time": execution_time,
                "content_length": 0,
                "method": "browser" if self.use_browser else "http",
                "timestamp": datetime.now().isoformat(),
                "output": None,
                "error": f"Timeout after {execution_time:.1f}s",
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "url": url,
                "success": False,
                "attempt": attempt,
                "execution_time": execution_time,
                "content_length": 0,
                "method": "browser" if self.use_browser else "http",
                "timestamp": datetime.now().isoformat(),
                "output": None,
                "error": str(e),
            }

    def scrape_with_retry(self, url: str) -> Dict[str, Any]:
        """
        Scrape URL with automatic retries for failed requests.

        Args:
            url: URL to scrape

        Returns:
            Final scraping result after all retry attempts
        """
        import random

        for attempt in range(1, self.retry_attempts + 1):
            # Add random delay to avoid rate limiting
            if attempt > 1:
                delay = random.uniform(*self.delay_range)
                time.sleep(delay)

            result = self.scrape_single_url(url, attempt)

            if result["success"]:
                return result

            # If this was the last attempt, return the failed result
            if attempt == self.retry_attempts:
                self.failed_urls.append(url)
                return result

        # Should never reach here, but return failure just in case
        return {"url": url, "success": False, "error": "Unexpected retry logic error"}

    def scrape_batch(
        self, urls: List[str], progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Scrape multiple URLs concurrently with progress tracking.

        Args:
            urls: List of URLs to scrape
            progress_callback: Optional callback function for progress updates

        Returns:
            Dict with batch results and performance metrics
        """
        start_time = time.time()
        results = []

        print(f"🚀 Starting batch scraping of {len(urls)} URLs")
        print(
            f"⚙️  Configuration: {self.max_workers} workers, {'browser' if self.use_browser else 'HTTP'} method"
        )
        print("-" * 60)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_url = {
                executor.submit(self.scrape_with_retry, url): url for url in urls
            }

            # Process completed jobs
            completed = 0
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                result = future.result()
                results.append(result)
                completed += 1

                # Progress reporting
                progress = (completed / len(urls)) * 100
                status = "✅" if result["success"] else "❌"
                print(
                    f"{status} [{completed:3d}/{len(urls):3d}] {progress:5.1f}% | {url:<50} | {result['execution_time']:5.2f}s"
                )

                # Optional progress callback
                if progress_callback:
                    progress_callback(completed, len(urls), result)

        total_time = time.time() - start_time

        # Calculate performance metrics
        successful_results = [r for r in results if r["success"]]
        failed_results = [r for r in results if not r["success"]]

        total_content = sum(r.get("content_length", 0) for r in successful_results)
        avg_time = (
            sum(r["execution_time"] for r in successful_results)
            / len(successful_results)
            if successful_results
            else 0
        )

        metrics = {
            "total_urls": len(urls),
            "successful": len(successful_results),
            "failed": len(failed_results),
            "success_rate": len(successful_results) / len(urls) * 100,
            "total_time": total_time,
            "avg_time_per_url": avg_time,
            "total_content_length": total_content,
            "throughput_urls_per_second": len(urls) / total_time,
            "method": "browser" if self.use_browser else "http",
            "workers": self.max_workers,
        }

        self.results = results
        return {"results": results, "metrics": metrics, "failed_urls": self.failed_urls}


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from text file (one per line)."""
    try:
        with open(file_path, "r") as f:
            urls = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
        return urls
    except FileNotFoundError:
        print(f"❌ Error: URL file '{file_path}' not found")
        return []


def save_results(batch_result: Dict[str, Any], output_file: str):
    """Save batch results to JSON file."""
    try:
        with open(output_file, "w") as f:
            json.dump(batch_result, f, indent=2)
        print(f"💾 Results saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save results: {e}")


def print_summary_report(batch_result: Dict[str, Any]):
    """Print detailed summary report of batch scraping results."""
    metrics = batch_result["metrics"]

    print("\n" + "=" * 80)
    print("📊 BATCH SCRAPING SUMMARY REPORT")
    print("=" * 80)

    print("🎯 **Overall Performance:**")
    print(f"   Total URLs: {metrics['total_urls']}")
    print(f"   Successful: {metrics['successful']} ({metrics['success_rate']:.1f}%)")
    print(f"   Failed: {metrics['failed']}")
    print(f"   Total Time: {metrics['total_time']:.2f}s")
    print(f"   Throughput: {metrics['throughput_urls_per_second']:.2f} URLs/second")

    print("\n⚡ **Performance Metrics:**")
    print(f"   Average Time per URL: {metrics['avg_time_per_url']:.2f}s")
    print(f"   Total Content Extracted: {metrics['total_content_length']:,} characters")
    print(f"   Method: {metrics['method'].upper()}")
    print(f"   Concurrent Workers: {metrics['workers']}")

    # Performance rating
    if metrics["success_rate"] >= 95 and metrics["throughput_urls_per_second"] >= 0.5:
        rating = "🏆 EXCELLENT"
    elif metrics["success_rate"] >= 85 and metrics["throughput_urls_per_second"] >= 0.3:
        rating = "✅ GOOD"
    elif metrics["success_rate"] >= 70:
        rating = "⚠️  FAIR"
    else:
        rating = "❌ POOR"

    print(f"\n🎖️  **Performance Rating:** {rating}")

    # Failed URLs summary
    if batch_result["failed_urls"]:
        print(f"\n❌ **Failed URLs ({len(batch_result['failed_urls'])}):**")
        for url in batch_result["failed_urls"][:5]:  # Show first 5
            print(f"   - {url}")
        if len(batch_result["failed_urls"]) > 5:
            print(f"   ... and {len(batch_result['failed_urls']) - 5} more")


def main():
    """Main batch scraping function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Batch Stealth Scraper - High-Performance Concurrent Web Scraping"
    )
    parser.add_argument("--urls", type=str, nargs="+", help="URLs to scrape")
    parser.add_argument("--file", type=str, help="File containing URLs (one per line)")
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of concurrent workers (default: 5)",
    )
    parser.add_argument(
        "--delay-min",
        type=int,
        default=2,
        help="Minimum delay between requests (default: 2s)",
    )
    parser.add_argument(
        "--delay-max",
        type=int,
        default=5,
        help="Maximum delay between requests (default: 5s)",
    )
    parser.add_argument(
        "--retries", type=int, default=3, help="Number of retry attempts (default: 3)"
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Use browser-based scraping (slower but more capable)",
    )
    parser.add_argument(
        "--output", type=str, help="Output file for results (JSON format)"
    )

    args = parser.parse_args()

    # Collect URLs
    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.file:
        file_urls = load_urls_from_file(args.file)
        urls.extend(file_urls)

    if not urls:
        print("❌ Error: No URLs provided. Use --urls or --file")
        sys.exit(1)

    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    print("🎯 Batch Stealth Scraper - High-Performance Mode")
    print(
        f"📋 URLs to process: {len(unique_urls)} (duplicates removed: {len(urls) - len(unique_urls)})"
    )
    print(
        f"⚙️  Workers: {args.workers} | Retries: {args.retries} | Method: {'Browser' if args.browser else 'HTTP'}"
    )

    # Initialize batch scraper
    scraper = BatchStealthScraper(
        max_workers=args.workers,
        delay_range=(args.delay_min, args.delay_max),
        retry_attempts=args.retries,
        use_browser=args.browser,
    )

    # Run batch scraping
    try:
        batch_result = scraper.scrape_batch(unique_urls)

        # Print summary report
        print_summary_report(batch_result)

        # Save results if output file specified
        if args.output:
            save_results(batch_result, args.output)
        else:
            # Default output file
            timestamp = int(time.time())
            default_output = f"output/batch_scraping_{timestamp}.json"
            save_results(batch_result, default_output)

        # Return success/failure based on results
        success_rate = batch_result["metrics"]["success_rate"]
        if success_rate >= 70:
            print("\n🎉 Batch scraping completed successfully!")
            sys.exit(0)
        else:
            print(
                f"\n⚠️  Batch scraping completed with {success_rate:.1f}% success rate"
            )
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Batch scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Batch scraping failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
