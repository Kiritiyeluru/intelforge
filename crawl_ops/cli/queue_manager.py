#!/usr/bin/env python3
"""
URL Queue Management CLI for IntelForge

Command-line interface for managing the URL discovery and processing queue.
Extends existing url_manager.py with queue-specific operations.
"""

import click
import sys
from pathlib import Path
from datetime import datetime, timedelta
import orjson as json
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from crawl_ops.tracking.url_queue import URLQueue, integrate_with_url_tracker
    from crawl_ops.tracking.url_tracker import URLTracker
    from crawl_ops.prioritization.queue_prioritizer import QueuePrioritizer
except ImportError as e:
    print(f"Error importing tracking modules: {e}")
    print("Ensure you're running from the project root directory")
    sys.exit(1)


class QueueManagerCLI:
    """Command-line interface for URL queue management."""
    
    def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
        self.queue = URLQueue(db_path)
        self.tracker = URLTracker(db_path)
        self.integrated_manager = integrate_with_url_tracker()(db_path)
        self.prioritizer = QueuePrioritizer(db_path)
    
    def add_urls(self, urls: List[str], source: str = "manual", 
                category: str = "general", priority: int = 5):
        """Add URLs to the discovery queue."""
        url_data = []
        for url in track(urls, description="Processing URLs..."):
            url_data.append({
                'url': url.strip(),
                'source': source,
                'category': category,
                'priority': priority,
                'quality_estimate': 0.0,
                'metadata': {'added_via': 'cli', 'added_date': datetime.now().isoformat()}
            })
            time.sleep(0.1)  # Small delay for progress bar visibility
        
        added_count = self.queue.add_discovered_urls(url_data)
        return added_count
    
    def show_queue_status(self):
        """Display comprehensive queue status - deprecated, use CLI status command."""
        # This method is kept for backwards compatibility
        # The rich CLI version is preferred
        pass
    
    def show_next_batch(self, batch_size: int = 10, categories: List[str] = None):
        """Show next URLs that would be processed."""
        next_urls = self.queue.get_next_urls(batch_size, categories)
        
        print(f"\n🔄 Next {len(next_urls)} URLs for Processing")
        print("=" * 60)
        
        if not next_urls:
            print("No URLs ready for processing.")
            return
        
        for i, url_data in enumerate(next_urls, 1):
            print(f"\n{i}. {url_data['url']}")
            print(f"   Source: {url_data['source']} | Category: {url_data['category']}")
            print(f"   Priority: {url_data['priority']} | Quality Est: {url_data['quality_estimate']:.2f}")
            print(f"   Discovered: {url_data['discovered_date']}")
    
    def process_batch(self, batch_size: int = 5, dry_run: bool = True):
        """Process a batch of URLs (with dry-run option)."""
        ready_urls = self.integrated_manager.process_discovery_batch(batch_size)
        
        print(f"\n⚡ Processing Batch (Dry Run: {dry_run})")
        print("=" * 50)
        print(f"📦 {len(ready_urls)} URLs ready for crawling:")
        
        for i, url in enumerate(ready_urls, 1):
            print(f"  {i}. {url}")
        
        if not dry_run and ready_urls:
            print(f"\n🚀 Would trigger crawling for {len(ready_urls)} URLs")
            print("Integration with semantic_crawler.py would happen here")
        elif dry_run:
            print(f"\n💡 Run with --no-dry-run to actually process these URLs")
    
    def add_github_discovery(self, keywords: List[str], max_repos: int = 10):
        """Add GitHub repository discovery for trading/strategy keywords."""
        print(f"🔍 GitHub Discovery: {', '.join(keywords)} (max {max_repos} repos)")
        
        # This would integrate with GitHub API
        # For now, simulate some common repos
        simulated_repos = [
            "https://github.com/quantopian/zipline",
            "https://github.com/stefan-jansen/machine-learning-for-trading", 
            "https://github.com/kernc/backtesting.py",
            "https://github.com/ranaroussi/yfinance",
            "https://github.com/polakowo/vectorbt"
        ]
        
        github_urls = []
        for repo in simulated_repos[:max_repos]:
            github_urls.append({
                'url': repo,
                'source': 'github_discovery',
                'category': 'code',
                'priority': 4,
                'quality_estimate': 0.7,
                'metadata': {
                    'discovery_keywords': keywords,
                    'discovery_date': datetime.now().isoformat()
                }
            })
        
        added = self.queue.add_discovered_urls(github_urls)
        print(f"✅ Added {added} GitHub repositories to queue")
    
    def add_rss_discovery(self, rss_feeds: List[str]):
        """Add RSS feed discovery sources."""
        print(f"📰 RSS Discovery: {len(rss_feeds)} feeds")
        
        # Common trading/finance RSS feeds
        default_feeds = [
            "https://www.quantstart.com/feed/",
            "https://blog.quantinsti.com/feed/", 
            "https://www.investopedia.com/feed/",
            "https://feeds.feedburner.com/oreilly/radar"
        ]
        
        all_feeds = list(set(rss_feeds + default_feeds))
        
        # Simulate RSS discovery (would parse feeds in real implementation)
        rss_urls = []
        for feed in all_feeds:
            # Simulate 2-3 recent articles per feed
            for i in range(2):
                article_url = feed.replace('/feed/', f'/article-{i+1}/')
                rss_urls.append({
                    'url': article_url,
                    'source': 'rss_discovery',
                    'category': 'blog',
                    'priority': 6,
                    'quality_estimate': 0.6,
                    'metadata': {
                        'rss_source': feed,
                        'discovery_date': datetime.now().isoformat()
                    }
                })
        
        added = self.queue.add_discovered_urls(rss_urls)
        print(f"✅ Added {added} articles from RSS feeds to queue")
    
    def cleanup_queue(self, days_old: int = 30):
        """Clean up old completed/failed entries."""
        deleted = self.queue.cleanup_old_entries(days_old)
        print(f"🧹 Cleaned up {deleted} entries older than {days_old} days")
    
    def export_queue(self, output_file: str = None):
        """Export queue to JSON file."""
        if not output_file:
            output_file = f"queue_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        stats = self.queue.get_queue_statistics()
        next_batch = self.queue.get_next_urls(100)  # Get larger sample
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'statistics': stats,
            'sample_urls': next_batch,
            'total_exported': len(next_batch)
        }
        
        with open(output_file, 'wb') as f:
            f.write(orjson.dumps(export_data, option=orjson.OPT_INDENT_2))
        
        print(f"📄 Exported queue data to {output_file}")


# Initialize Rich console
console = Console()


@click.group()
@click.option('--db-path', default='crawl_ops/tracking/url_tracker.db', 
              help='Path to SQLite database')
@click.pass_context
def cli(ctx, db_path):
    """IntelForge URL Queue Manager - Enhanced CLI with rich output."""
    ctx.ensure_object(dict)
    try:
        ctx.obj['manager'] = QueueManagerCLI(db_path)
    except Exception as e:
        console.print(f"[red]Error initializing queue manager: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_context
def status(ctx):
    """Show comprehensive queue status with rich formatting."""
    manager = ctx.obj['manager']
    stats = manager.queue.get_queue_statistics()
    
    # Main status table
    table = Table(title="🎯 URL Queue Status", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    table.add_column("Details", style="yellow")
    
    efficiency = stats['efficiency']
    table.add_row("📊 Queue Size", str(stats['queue_size']), "pending URLs")
    table.add_row("📈 Total URLs", str(efficiency['total_urls']), "all time")
    table.add_row("✅ Completed", str(efficiency['completed']), f"{efficiency['success_rate']:.1f}% success rate")
    table.add_row("❌ Failed", str(efficiency['failed']), "")
    table.add_row("⚡ Processing", str(efficiency['processing']), "")
    
    console.print(table)
    
    # Source breakdown table
    if stats['source_breakdown']:
        source_table = Table(title="📂 Sources Breakdown", show_header=True)
        source_table.add_column("Source", style="cyan")
        source_table.add_column("Count", style="green")
        source_table.add_column("Avg Quality", style="yellow")
        
        for source, data in stats['source_breakdown'].items():
            source_table.add_row(source, str(data['count']), f"{data['avg_quality']:.2f}")
        
        console.print("\n")
        console.print(source_table)
    
    # Category breakdown table
    if stats['category_breakdown']:
        category_table = Table(title="🏷️ Categories Breakdown", show_header=True)
        category_table.add_column("Category", style="cyan")
        category_table.add_column("Count", style="green")
        category_table.add_column("Avg Priority", style="yellow")
        
        for category, data in stats['category_breakdown'].items():
            category_table.add_row(category, str(data['count']), f"{data['avg_priority']:.1f}")
        
        console.print("\n")
        console.print(category_table)
    
    console.print(f"\n🕐 [bold]Last Updated:[/bold] {stats['last_updated']}")


@cli.command()
@click.argument('urls', nargs=-1, required=True)
@click.option('--source', default='manual', help='Discovery source')
@click.option('--category', default='general', help='Content category')
@click.option('--priority', type=int, default=5, help='Priority (1-10)')
@click.pass_context
def add(ctx, urls, source, category, priority):
    """Add URLs to the discovery queue."""
    manager = ctx.obj['manager']
    
    with console.status(f"[bold green]Adding {len(urls)} URLs..."):
        added_count = manager.add_urls(list(urls), source, category, priority)
    
    console.print(f"[green]✅ Added {added_count} URLs to queue[/green]")
    console.print(f"[dim]Source: {source} | Category: {category} | Priority: {priority}[/dim]")


@cli.command()
@click.option('--batch-size', type=int, default=10, help='Number of URLs to show')
@click.option('--categories', multiple=True, help='Filter by categories')
@click.pass_context
def next(ctx, batch_size, categories):
    """Show next URLs that would be processed."""
    manager = ctx.obj['manager']
    next_urls = manager.queue.get_next_urls(batch_size, list(categories) if categories else None)
    
    if not next_urls:
        console.print("[yellow]No URLs ready for processing.[/yellow]")
        return
    
    table = Table(title=f"🔄 Next {len(next_urls)} URLs for Processing", show_header=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("URL", style="blue", max_width=50)
    table.add_column("Source", style="cyan")
    table.add_column("Category", style="green")
    table.add_column("Priority", style="yellow")
    table.add_column("Quality", style="magenta")
    
    for i, url_data in enumerate(next_urls, 1):
        table.add_row(
            str(i),
            url_data['url'],
            url_data['source'],
            url_data['category'],
            str(url_data['priority']),
            f"{url_data['quality_estimate']:.2f}"
        )
    
    console.print(table)


@cli.command()
@click.option('--batch-size', type=int, default=5, help='Batch size to process')
@click.option('--no-dry-run', is_flag=True, help='Actually process (not just simulate)')
@click.pass_context
def process(ctx, batch_size, no_dry_run):
    """Process a batch of URLs with optional dry-run."""
    manager = ctx.obj['manager']
    
    with console.status("[bold yellow]Processing batch..."):
        ready_urls = manager.integrated_manager.process_discovery_batch(batch_size)
    
    table = Table(title=f"⚡ Processing Batch (Dry Run: {not no_dry_run})", show_header=True)
    table.add_column("#", style="dim", width=3)
    table.add_column("URL", style="blue")
    
    for i, url in enumerate(ready_urls, 1):
        table.add_row(str(i), url)
    
    console.print(table)
    
    if no_dry_run and ready_urls:
        console.print(f"\n[green]🚀 Would trigger crawling for {len(ready_urls)} URLs[/green]")
        console.print("[dim]Integration with semantic_crawler.py would happen here[/dim]")
    elif not no_dry_run:
        console.print(f"\n[yellow]💡 Use --no-dry-run to actually process these URLs[/yellow]")


@cli.command()
@click.argument('keywords', nargs=-1, required=True)
@click.option('--max-repos', type=int, default=10, help='Maximum repositories to discover')
@click.pass_context
def github(ctx, keywords, max_repos):
    """Add GitHub repository discovery for trading/strategy keywords."""
    manager = ctx.obj['manager']
    
    with console.status(f"[bold blue]Discovering GitHub repositories for: {', '.join(keywords)}..."):
        # Use real GitHub discovery if available
        try:
            from crawl_ops.discovery.github_discovery import GitHubDiscovery
            github_discovery = GitHubDiscovery()
            
            # Check rate limit first
            rate_status = github_discovery.get_rate_limit_status()
            if rate_status and 'resources' in rate_status:
                remaining = rate_status['resources'].get('search', {}).get('remaining', 0)
                if remaining < 5:
                    console.print(f"[red]⚠️ GitHub API rate limit low: {remaining} requests remaining[/red]")
                    return
            
            repos = github_discovery.search_repositories(list(keywords), max_repos)
            if repos:
                added = manager.queue.add_discovered_urls(repos)
                console.print(f"[green]✅ Added {added} GitHub repositories to queue[/green]")
                
                # Show discovered repos in a table
                if repos:
                    table = Table(title="🔍 Discovered Repositories", show_header=True)
                    table.add_column("Repository", style="blue")
                    table.add_column("Stars", style="yellow")
                    table.add_column("Quality", style="green")
                    
                    for repo in repos[:5]:  # Show first 5
                        stars = repo['metadata'].get('stars', 0)
                        table.add_row(
                            repo['url'].split('/')[-1],
                            str(stars),
                            f"{repo['quality_estimate']:.2f}"
                        )
                    
                    console.print(table)
            else:
                console.print(f"[yellow]No repositories found for keywords: {', '.join(keywords)}[/yellow]")
        
        except ImportError:
            # Fallback to simulated discovery
            manager.add_github_discovery(list(keywords), max_repos)


@cli.command()
@click.argument('feeds', nargs=-1)
@click.pass_context
def rss(ctx, feeds):
    """Add RSS feed discovery with enhanced feedparser."""
    manager = ctx.obj['manager']
    
    # Use enhanced RSS discovery if available
    try:
        from crawl_ops.discovery.rss_discovery import RSSDiscovery, DEFAULT_FEEDS
        rss_discovery = RSSDiscovery()
        
        # Use provided feeds or defaults
        feed_urls = list(feeds) if feeds else DEFAULT_FEEDS[:3]  # Use first 3 defaults
        
        with console.status(f"[bold green]Discovering content from {len(feed_urls)} RSS feeds..."):
            discoveries = rss_discovery.discover_from_feeds(feed_urls, max_entries_per_feed=10)
        
        if discoveries:
            added = manager.queue.add_discovered_urls(discoveries)
            console.print(f"[green]✅ Added {added} articles from RSS feeds to queue[/green]")
            
            # Show discovered articles in a table
            table = Table(title="📰 Recent Discoveries", show_header=True)
            table.add_column("Title", style="blue", max_width=40)
            table.add_column("Category", style="green")
            table.add_column("Quality", style="yellow")
            table.add_column("Feed", style="dim")
            
            for discovery in discoveries[:5]:  # Show first 5
                title = discovery['metadata'].get('title', 'Untitled')[:40]
                feed_title = discovery['metadata'].get('feed_title', 'Unknown')[:15]
                table.add_row(
                    title,
                    discovery['category'],
                    f"{discovery['quality_estimate']:.2f}",
                    feed_title
                )
            
            console.print(table)
        else:
            console.print("[yellow]No content discovered from RSS feeds[/yellow]")
    
    except ImportError:
        # Fallback to simulated discovery
        with console.status("[bold green]Using simulated RSS discovery..."):
            manager.add_rss_discovery(list(feeds) if feeds else [])


@cli.command()
@click.option('--days', type=int, default=30, help='Days old to clean up')
@click.pass_context
def cleanup(ctx, days):
    """Clean up old completed/failed entries."""
    manager = ctx.obj['manager']
    
    with console.status(f"[bold red]Cleaning up entries older than {days} days..."):
        deleted = manager.queue.cleanup_old_entries(days)
    
    console.print(f"[green]🧹 Cleaned up {deleted} entries older than {days} days[/green]")


@cli.command()
@click.option('--output', help='Output file path')
@click.pass_context
def export(ctx, output):
    """Export queue data to JSON file."""
    manager = ctx.obj['manager']
    
    if not output:
        output = f"queue_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with console.status("[bold cyan]Exporting queue data..."):
        stats = manager.queue.get_queue_statistics()
        next_batch = manager.queue.get_next_urls(100)  # Get larger sample
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'statistics': stats,
            'sample_urls': next_batch,
            'total_exported': len(next_batch)
        }
        
        with open(output, 'wb') as f:
            f.write(orjson.dumps(export_data, option=orjson.OPT_INDENT_2))
    
    console.print(f"[green]📄 Exported queue data to {output}[/green]")


@cli.command()
@click.option('--batch-size', type=int, default=500, help='Batch size for priority calculation')
@click.pass_context
def reprioritize(ctx, batch_size):
    """Recalculate priority scores for pending URLs."""
    manager = ctx.obj['manager']
    
    with console.status(f"[bold magenta]Recalculating priority scores for up to {batch_size} URLs..."):
        updated = manager.prioritizer.calculate_priority_scores(batch_size)
    
    console.print(f"[green]🎯 Updated priority scores for {updated} URLs[/green]")
    
    # Show updated statistics
    stats = manager.prioritizer.get_priority_statistics()
    avg_score = stats['avg_score'] or 0.0
    console.print(f"[dim]New average score: {avg_score:.3f}[/dim]")
    console.print(f"[dim]High priority URLs: {stats['high_priority']}[/dim]")


@cli.command()
@click.option('--count', type=int, default=10, help='Number of top URLs to show')
@click.option('--categories', multiple=True, help='Filter by categories')
@click.option('--min-quality', type=float, default=0.0, help='Minimum quality threshold')
@click.pass_context
def priority_next(ctx, count, categories, min_quality):
    """Show next URLs using priority-based ordering."""
    manager = ctx.obj['manager']
    
    with console.status(f"[bold blue]Finding top {count} priority URLs..."):
        priority_urls = manager.prioritizer.get_next_batch_prioritized(
            batch_size=count,
            categories=list(categories) if categories else None,
            min_quality=min_quality
        )
    
    if not priority_urls:
        console.print("[yellow]No URLs match the criteria.[/yellow]")
        return
    
    table = Table(title=f"🔥 Top {len(priority_urls)} Priority URLs", show_header=True)
    table.add_column("Rank", style="yellow", width=4)
    table.add_column("URL", style="blue", max_width=50)
    table.add_column("Score", style="green")
    table.add_column("Quality", style="cyan")
    table.add_column("Source", style="magenta")
    table.add_column("Category", style="white")
    
    for i, url_data in enumerate(priority_urls, 1):
        table.add_row(
            str(i),
            url_data['url'],
            f"{url_data['priority_score']:.3f}",
            f"{url_data['quality_estimate']:.2f}",
            url_data['source'],
            url_data['category']
        )
    
    console.print(table)


@cli.command()
@click.argument('url')
@click.pass_context
def debug_score(ctx, url):
    """Show detailed priority score breakdown for a specific URL."""
    manager = ctx.obj['manager']
    
    with console.status(f"[bold cyan]Analyzing priority score for {url[:60]}..."):
        debug_info = manager.prioritizer.debug_priority_calculation(url)
    
    if 'error' in debug_info:
        console.print(f"[red]❌ {debug_info['error']}[/red]")
        return
    
    # Main score info
    final_score = debug_info['final_score']
    metadata = debug_info['metadata']
    
    console.print(Panel(
        f"[bold green]Final Score: {final_score:.3f}[/bold green]\n"
        f"Source: {metadata['source']} | Category: {metadata['category']}",
        title=f"🎯 Priority Score for {url[:50]}...",
        border_style="green"
    ))
    
    # Component breakdown table
    components = debug_info['components']
    breakdown_table = Table(title="📊 Score Component Breakdown", show_header=True)
    breakdown_table.add_column("Component", style="cyan")
    breakdown_table.add_column("Value", style="green")
    breakdown_table.add_column("Impact", style="yellow")
    
    for component, value in components.items():
        impact = "" 
        if value > 0.1:
            impact = "🔥 High"
        elif value > 0.05:
            impact = "📈 Medium"
        elif value > 0:
            impact = "📊 Low"
        elif value < -0.1:
            impact = "❄️ High Penalty"
        elif value < 0:
            impact = "📉 Penalty"
        else:
            impact = "➖ None"
        
        breakdown_table.add_row(
            component.replace('_', ' ').title(),
            f"{value:+.3f}",
            impact
        )
    
    console.print("\n")
    console.print(breakdown_table)


def main():
    """Entry point for the CLI."""
    cli()


# Add a separate priority management group
@click.group()
@click.option('--db-path', default='crawl_ops/tracking/url_tracker.db', 
              help='Path to SQLite database')
@click.pass_context
def priority(ctx, db_path):
    """Priority queue management commands."""
    ctx.ensure_object(dict)
    try:
        from crawl_ops.prioritization.queue_prioritizer import QueuePrioritizer
        ctx.obj['prioritizer'] = QueuePrioritizer(db_path)
    except Exception as e:
        console.print(f"[red]Error initializing prioritizer: {e}[/red]")
        sys.exit(1)


@priority.command()
@click.option('--batch-size', type=int, default=1000, help='Batch size for calculation')
@click.pass_context
def calculate(ctx, batch_size):
    """Calculate priority scores for pending URLs."""
    prioritizer = ctx.obj['prioritizer']
    
    with console.status(f"[bold magenta]Calculating priority scores..."):
        updated = prioritizer.calculate_priority_scores(batch_size)
    
    console.print(f"[green]✅ Updated {updated} URLs[/green]")


@priority.command()
@click.pass_context
def stats(ctx):
    """Show priority queue statistics."""
    prioritizer = ctx.obj['prioritizer']
    
    stats = prioritizer.get_priority_statistics()
    
    # Stats table
    stats_table = Table(title="🎯 Priority Statistics", show_header=True)
    stats_table.add_column("Metric", style="cyan")
    stats_table.add_column("Value", style="green")
    
    stats_table.add_row("Total Pending", str(stats['total_pending']))
    stats_table.add_row("Average Score", f"{stats['avg_score']:.3f}")
    stats_table.add_row("Score Range", f"{stats['min_score']:.3f} - {stats['max_score']:.3f}")
    stats_table.add_row("High Priority (>1.0)", str(stats['high_priority']))
    stats_table.add_row("Medium Priority (0.5-1.0)", str(stats['medium_priority']))
    stats_table.add_row("Low Priority (<0.5)", str(stats['low_priority']))
    
    console.print(stats_table)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "priority":
        # Route to priority subcommand
        sys.argv.pop(1)
        priority()
    else:
        main()


# This is handled by the new main logic above