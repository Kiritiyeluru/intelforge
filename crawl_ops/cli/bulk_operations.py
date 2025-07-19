#!/usr/bin/env python3
"""
Bulk Operations CLI for IntelForge
Enhanced bulk processing with tqdm progress bars for long operations.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from tqdm import tqdm
import time
import sys
from pathlib import Path
from typing import List

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from crawl_ops.tracking.url_queue import URLQueue
    from crawl_ops.prioritization.queue_prioritizer import QueuePrioritizer
    from crawl_ops.discovery.github_discovery import GitHubDiscovery
    from crawl_ops.discovery.rss_discovery import RSSDiscovery, DEFAULT_FEEDS
    from crawl_ops.discovery.search_discovery import SearchDiscovery
    from crawl_ops.discovery.sitemap_discovery import SitemapDiscovery
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

console = Console()


@click.group()
@click.option('--db-path', default='crawl_ops/tracking/url_tracker.db',
              help='Path to SQLite database')
@click.pass_context
def bulk(ctx, db_path):
    """Bulk operations with enhanced progress tracking."""
    ctx.ensure_object(dict)
    ctx.obj['db_path'] = db_path
    ctx.obj['queue'] = URLQueue(db_path)
    ctx.obj['prioritizer'] = QueuePrioritizer(db_path)


@bulk.command()
@click.option('--keywords', multiple=True, required=True, help='Search keywords')
@click.option('--max-repos', type=int, default=50, help='Maximum repositories per keyword set')
@click.option('--batch-size', type=int, default=10, help='Batch size for API calls')
@click.pass_context
def github_bulk(ctx, keywords, max_repos, batch_size):
    """Bulk GitHub repository discovery with progress tracking."""
    github = GitHubDiscovery()
    queue = ctx.obj['queue']

    console.print(f"[bold blue]🔍 Bulk GitHub Discovery[/bold blue]")
    console.print(f"Keywords: {', '.join(keywords)}")
    console.print(f"Max repos per search: {max_repos}")

    # Check rate limit first
    rate_status = github.get_rate_limit_status()
    if rate_status and 'resources' in rate_status:
        remaining = rate_status['resources'].get('search', {}).get('remaining', 0)
        console.print(f"GitHub API requests remaining: {remaining}")

        if remaining < len(keywords):
            console.print("[red]⚠️ Insufficient API requests remaining[/red]")
            return

    all_repos = []

    # Process keywords with progress bar
    for keyword_set in tqdm(list(keywords), desc="Processing keyword sets", unit="keywords"):
        repos = github.search_repositories([keyword_set], max_results=max_repos)
        all_repos.extend(repos)

        # Rate limiting between searches
        if len(keywords) > 1:
            time.sleep(2)

    # Add to queue in batches with progress
    if all_repos:
        console.print(f"\n[green]Found {len(all_repos)} total repositories[/green]")

        # Batch add with progress
        for i in tqdm(range(0, len(all_repos), batch_size), desc="Adding to queue", unit="batch"):
            batch = all_repos[i:i + batch_size]
            queue.add_discovered_urls(batch)
            time.sleep(0.1)  # Small delay for visibility

        console.print(f"[green]✅ Added {len(all_repos)} repositories to queue[/green]")
    else:
        console.print("[yellow]No repositories found[/yellow]")


@bulk.command()
@click.option('--feed-file', type=click.Path(exists=True), help='File with RSS feed URLs (one per line)')
@click.option('--max-entries', type=int, default=10, help='Max entries per feed')
@click.option('--batch-size', type=int, default=5, help='Batch size for processing')
@click.pass_context
def rss_bulk(ctx, feed_file, max_entries, batch_size):
    """Bulk RSS feed processing with progress tracking."""
    rss = RSSDiscovery()
    queue = ctx.obj['queue']

    # Get feed URLs
    if feed_file:
        with open(feed_file, 'r') as f:
            feed_urls = [line.strip() for line in f if line.strip()]
    else:
        feed_urls = DEFAULT_FEEDS

    console.print(f"[bold green]📡 Bulk RSS Discovery[/bold green]")
    console.print(f"Processing {len(feed_urls)} feeds")
    console.print(f"Max entries per feed: {max_entries}")

    all_discoveries = []

    # Process feeds in batches
    for i in tqdm(range(0, len(feed_urls), batch_size), desc="Processing feed batches", unit="batch"):
        batch_feeds = feed_urls[i:i + batch_size]
        discoveries = rss.discover_from_feeds(batch_feeds, max_entries_per_feed=max_entries)
        all_discoveries.extend(discoveries)

        # Rate limiting between batches
        time.sleep(1)

    # Add to queue
    if all_discoveries:
        console.print(f"\n[green]Found {len(all_discoveries)} total articles[/green]")

        added = queue.add_discovered_urls(all_discoveries)
        console.print(f"[green]✅ Added {added} articles to queue[/green]")
    else:
        console.print("[yellow]No articles found[/yellow]")


@bulk.command()
@click.option('--domains', multiple=True, required=True, help='Domains to process')
@click.option('--batch-size', type=int, default=3, help='Batch size for sitemap processing')
@click.pass_context
def sitemap_bulk(ctx, domains, batch_size):
    """Bulk sitemap discovery with progress tracking."""
    sitemap = SitemapDiscovery()
    queue = ctx.obj['queue']

    console.print(f"[bold cyan]🗺️ Bulk Sitemap Discovery[/bold cyan]")
    console.print(f"Processing {len(domains)} domains")

    all_urls = []

    # Process domains in batches
    for i in tqdm(range(0, len(domains), batch_size), desc="Processing domain batches", unit="batch"):
        batch_domains = domains[i:i + batch_size]

        for domain in batch_domains:
            urls = sitemap.extract_urls_from_sitemap(domain)
            all_urls.extend(urls)
            time.sleep(1)  # Rate limiting

    # Add to queue
    if all_urls:
        console.print(f"\n[green]Found {len(all_urls)} total URLs[/green]")

        added = queue.add_discovered_urls(all_urls)
        console.print(f"[green]✅ Added {added} URLs to queue[/green]")
    else:
        console.print("[yellow]No URLs found[/yellow]")


@bulk.command()
@click.option('--batch-size', type=int, default=1000, help='Batch size for priority calculation')
@click.option('--update-all', is_flag=True, help='Update all URLs regardless of batch size')
@click.pass_context
def recalculate_all_priorities(ctx, batch_size, update_all):
    """Recalculate priorities for all queued URLs with progress tracking."""
    prioritizer = ctx.obj['prioritizer']

    console.print(f"[bold magenta]🎯 Bulk Priority Recalculation[/bold magenta]")

    if update_all:
        # Get total count first
        import sqlite3
        with sqlite3.connect(ctx.obj['db_path']) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM url_queue WHERE status = 'queued'")
            total_urls = cursor.fetchone()[0]

        console.print(f"Updating priorities for {total_urls} URLs")

        # Process in batches with progress
        updated_total = 0
        for batch_start in tqdm(range(0, total_urls, batch_size), desc="Updating priorities", unit="batch"):
            updated = prioritizer.calculate_priority_scores(batch_size)
            updated_total += updated

            if updated == 0:  # No more URLs to process
                break

        console.print(f"[green]✅ Updated {updated_total} URLs total[/green]")
    else:
        updated = prioritizer.calculate_priority_scores(batch_size)
        console.print(f"[green]✅ Updated {updated} URLs in single batch[/green]")


@bulk.command()
@click.option('--source', help='Filter by source')
@click.option('--category', help='Filter by category')
@click.option('--min-quality', type=float, default=0.0, help='Minimum quality threshold')
@click.option('--output-file', help='Output file for export')
@click.pass_context
def export_filtered(ctx, source, category, min_quality, output_file):
    """Export filtered URLs with progress tracking."""
    import sqlite3
    import orjson
    from datetime import datetime

    console.print(f"[bold cyan]📄 Bulk Export[/bold cyan]")

    # Build filter conditions
    conditions = ["status = 'queued'"]
    params = []

    if source:
        conditions.append("source = ?")
        params.append(source)

    if category:
        conditions.append("category = ?")
        params.append(category)

    if min_quality > 0:
        conditions.append("quality_estimate >= ?")
        params.append(min_quality)

    where_clause = " AND ".join(conditions)

    # Execute query with progress
    with sqlite3.connect(ctx.obj['db_path']) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM url_queue WHERE {where_clause}", params)
        total_count = cursor.fetchone()[0]

        console.print(f"Exporting {total_count} filtered URLs")

        # Fetch and process with progress
        cursor.execute(f"SELECT * FROM url_queue WHERE {where_clause}", params)

        export_data = []
        for row in tqdm(cursor.fetchall(), desc="Processing URLs", unit="URL"):
            export_data.append(dict(row))

    # Write to file
    if not output_file:
        output_file = f"bulk_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    export_result = {
        'export_date': datetime.now().isoformat(),
        'filters': {
            'source': source,
            'category': category,
            'min_quality': min_quality
        },
        'total_count': len(export_data),
        'urls': export_data
    }

    with open(output_file, 'wb') as f:
        f.write(orjson.dumps(export_result, option=orjson.OPT_INDENT_2))

    console.print(f"[green]✅ Exported {len(export_data)} URLs to {output_file}[/green]")


def main():
    """Entry point for bulk operations CLI."""
    bulk()


if __name__ == "__main__":
    main()
