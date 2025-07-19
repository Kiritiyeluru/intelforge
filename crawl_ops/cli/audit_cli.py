#!/usr/bin/env python3
"""
Audit CLI for IntelForge URL Queue System
Provides operational visibility and system health monitoring.
"""

import click
import sqlite3
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.progress import track
from pathlib import Path
import sys
from typing import Dict, List
from tqdm import tqdm

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from crawl_ops.prioritization.queue_prioritizer import QueuePrioritizer
    from crawl_ops.tracking.url_queue import URLQueue
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

console = Console()


class AuditCLI:
    """Operational audit and monitoring for URL queue system."""

    def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
        self.db_path = db_path
        self.queue = URLQueue(db_path)
        self.prioritizer = QueuePrioritizer(db_path)

    def get_system_health(self) -> Dict:
        """Get comprehensive system health metrics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Queue health metrics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_urls,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    AVG(CASE WHEN status = 'pending' THEN priority_score END) as avg_priority,
                    AVG(CASE WHEN status = 'pending' THEN quality_estimate END) as avg_quality
                FROM url_queue
            """)

            queue_health = dict(cursor.fetchone())

            # Processing rates (last 24h, 7d, 30d)
            time_periods = [
                ('24h', 1),
                ('7d', 7),
                ('30d', 30)
            ]

            processing_rates = {}
            for period_name, days in time_periods:
                since_date = (datetime.now() - timedelta(days=days)).isoformat()

                cursor.execute("""
                    SELECT
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                    FROM url_queue
                    WHERE discovered_date >= ?
                """, (since_date,))

                rates = dict(cursor.fetchone())
                processing_rates[period_name] = rates

            # Source health
            cursor.execute("""
                SELECT
                    source,
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    AVG(priority_score) as avg_priority,
                    AVG(quality_estimate) as avg_quality
                FROM url_queue
                GROUP BY source
                ORDER BY total DESC
            """)

            source_health = [dict(row) for row in cursor.fetchall()]

            # Category distribution
            cursor.execute("""
                SELECT
                    category,
                    COUNT(*) as count,
                    AVG(priority_score) as avg_priority,
                    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending
                FROM url_queue
                WHERE status != 'failed'
                GROUP BY category
                ORDER BY count DESC
            """)

            category_distribution = [dict(row) for row in cursor.fetchall()]

            # Queue staleness (oldest pending URLs)
            cursor.execute("""
                SELECT
                    url,
                    source,
                    category,
                    discovered_date,
                    priority_score
                FROM url_queue
                WHERE status = 'pending'
                ORDER BY discovered_date ASC
                LIMIT 5
            """)

            stale_urls = [dict(row) for row in cursor.fetchall()]

            return {
                'queue_health': queue_health,
                'processing_rates': processing_rates,
                'source_health': source_health,
                'category_distribution': category_distribution,
                'stale_urls': stale_urls,
                'audit_timestamp': datetime.now().isoformat()
            }

    def get_discovery_performance(self) -> Dict:
        """Analyze discovery source performance and efficiency."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Discovery efficiency by source
            cursor.execute("""
                SELECT
                    source,
                    COUNT(*) as discovered,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as processed,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    AVG(quality_estimate) as avg_quality,
                    CASE
                        WHEN COUNT(*) > 0
                        THEN (COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*))
                        ELSE 0
                    END as success_rate
                FROM url_queue
                GROUP BY source
                ORDER BY discovered DESC
            """)

            source_performance = [dict(row) for row in cursor.fetchall()]

            # Recent discovery trends (last 7 days)
            cursor.execute("""
                SELECT
                    DATE(discovered_date) as discovery_date,
                    source,
                    COUNT(*) as count
                FROM url_queue
                WHERE discovered_date >= date('now', '-7 days')
                GROUP BY DATE(discovered_date), source
                ORDER BY discovery_date DESC, count DESC
            """)

            recent_trends = [dict(row) for row in cursor.fetchall()]

            # Quality score distribution
            cursor.execute("""
                SELECT
                    CASE
                        WHEN quality_estimate >= 0.8 THEN 'Excellent (0.8+)'
                        WHEN quality_estimate >= 0.6 THEN 'Good (0.6-0.8)'
                        WHEN quality_estimate >= 0.4 THEN 'Fair (0.4-0.6)'
                        WHEN quality_estimate >= 0.2 THEN 'Poor (0.2-0.4)'
                        ELSE 'Very Poor (<0.2)'
                    END as quality_tier,
                    COUNT(*) as count,
                    AVG(priority_score) as avg_priority
                FROM url_queue
                WHERE status = 'pending'
                GROUP BY quality_tier
                ORDER BY AVG(quality_estimate) DESC
            """)

            quality_distribution = [dict(row) for row in cursor.fetchall()]

            return {
                'source_performance': source_performance,
                'recent_trends': recent_trends,
                'quality_distribution': quality_distribution
            }

    def get_bottlenecks_and_issues(self) -> Dict:
        """Identify system bottlenecks and potential issues."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            issues = []

            # Check for stalled processing
            cursor.execute("""
                SELECT COUNT(*) as stalled_count
                FROM url_queue
                WHERE status = 'processing'
                  AND last_updated < datetime('now', '-2 hours')
            """)

            stalled = dict(cursor.fetchone())
            if stalled['stalled_count'] > 0:
                issues.append({
                    'type': 'stalled_processing',
                    'severity': 'high',
                    'count': stalled['stalled_count'],
                    'description': f"{stalled['stalled_count']} URLs stuck in processing state"
                })

            # Check for high failure rate
            cursor.execute("""
                SELECT
                    source,
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    (COUNT(CASE WHEN status = 'failed' THEN 1 END) * 100.0 / COUNT(*)) as failure_rate
                FROM url_queue
                WHERE last_updated >= datetime('now', '-7 days')
                GROUP BY source
                HAVING failure_rate > 50 AND total > 5
            """)

            high_failure_sources = [dict(row) for row in cursor.fetchall()]
            for source in high_failure_sources:
                issues.append({
                    'type': 'high_failure_rate',
                    'severity': 'medium',
                    'source': source['source'],
                    'failure_rate': source['failure_rate'],
                    'description': f"Source '{source['source']}' has {source['failure_rate']:.1f}% failure rate"
                })

            # Check for queue backlog
            cursor.execute("""
                SELECT COUNT(*) as backlog_count
                FROM url_queue
                WHERE status = 'pending'
                  AND discovered_date < datetime('now', '-30 days')
            """)

            backlog = dict(cursor.fetchone())
            if backlog['backlog_count'] > 100:
                issues.append({
                    'type': 'large_backlog',
                    'severity': 'medium',
                    'count': backlog['backlog_count'],
                    'description': f"{backlog['backlog_count']} URLs pending for >30 days"
                })

            # Check for low-quality accumulation
            cursor.execute("""
                SELECT COUNT(*) as low_quality_count
                FROM url_queue
                WHERE status = 'pending'
                  AND quality_estimate < 0.3
            """)

            low_quality = dict(cursor.fetchone())
            if low_quality['low_quality_count'] > 50:
                issues.append({
                    'type': 'low_quality_accumulation',
                    'severity': 'low',
                    'count': low_quality['low_quality_count'],
                    'description': f"{low_quality['low_quality_count']} low-quality URLs in queue"
                })

            return {
                'issues': issues,
                'total_issues': len(issues),
                'severity_breakdown': {
                    'high': len([i for i in issues if i['severity'] == 'high']),
                    'medium': len([i for i in issues if i['severity'] == 'medium']),
                    'low': len([i for i in issues if i['severity'] == 'low'])
                }
            }


@click.group()
@click.option('--db-path', default='crawl_ops/tracking/url_tracker.db',
              help='Path to SQLite database')
@click.pass_context
def audit(ctx, db_path):
    """IntelForge URL Queue Audit and Monitoring CLI."""
    ctx.ensure_object(dict)
    ctx.obj['audit'] = AuditCLI(db_path)


@audit.command()
@click.pass_context
def health(ctx):
    """Show comprehensive system health dashboard."""
    audit_cli = ctx.obj['audit']

    with console.status("[bold green]Gathering system health metrics..."):
        health_data = audit_cli.get_system_health()

    # Queue health overview
    queue_health = health_data['queue_health']

    health_table = Table(title="🏥 System Health Overview", show_header=True)
    health_table.add_column("Metric", style="cyan", no_wrap=True)
    health_table.add_column("Value", style="green")
    health_table.add_column("Status", style="yellow")

    total_urls = queue_health['total_urls']
    pending_pct = (queue_health['pending'] / total_urls * 100) if total_urls > 0 else 0

    health_table.add_row("Total URLs", str(total_urls), "📊")
    health_table.add_row("Pending", f"{queue_health['pending']} ({pending_pct:.1f}%)", "⏳")
    health_table.add_row("Processing", str(queue_health['processing']), "⚡")
    health_table.add_row("Completed", str(queue_health['completed']), "✅")
    health_table.add_row("Failed", str(queue_health['failed']), "❌")
    health_table.add_row("Avg Priority", f"{queue_health['avg_priority']:.3f}" if queue_health['avg_priority'] else "N/A", "🎯")
    health_table.add_row("Avg Quality", f"{queue_health['avg_quality']:.3f}" if queue_health['avg_quality'] else "N/A", "⭐")

    console.print(health_table)

    # Processing rates
    console.print(f"\n📈 [bold]Processing Rates[/bold]")
    for period, rates in health_data['processing_rates'].items():
        completed = rates['completed']
        failed = rates['failed']
        total = completed + failed
        success_rate = (completed / total * 100) if total > 0 else 0
        console.print(f"  {period}: {completed} completed, {failed} failed ({success_rate:.1f}% success)")

    # Source health table
    if health_data['source_health']:
        source_table = Table(title="📂 Source Health", show_header=True)
        source_table.add_column("Source", style="cyan")
        source_table.add_column("Total", style="green")
        source_table.add_column("Pending", style="yellow")
        source_table.add_column("Success Rate", style="blue")
        source_table.add_column("Avg Priority", style="magenta")

        for source in health_data['source_health']:
            total = source['total']
            completed = source['completed']
            success_rate = (completed / total * 100) if total > 0 else 0

            source_table.add_row(
                source['source'],
                str(total),
                str(source['pending']),
                f"{success_rate:.1f}%",
                f"{source['avg_priority']:.2f}" if source['avg_priority'] else "N/A"
            )

        console.print(f"\n")
        console.print(source_table)


@audit.command()
@click.pass_context
def performance(ctx):
    """Show discovery source performance analysis."""
    audit_cli = ctx.obj['audit']

    with console.status("[bold blue]Analyzing discovery performance..."):
        perf_data = audit_cli.get_discovery_performance()

    # Source performance table
    perf_table = Table(title="🔍 Discovery Source Performance", show_header=True)
    perf_table.add_column("Source", style="cyan")
    perf_table.add_column("Discovered", style="green")
    perf_table.add_column("Processed", style="blue")
    perf_table.add_column("Success Rate", style="yellow")
    perf_table.add_column("Avg Quality", style="magenta")

    for source in perf_data['source_performance']:
        perf_table.add_row(
            source['source'],
            str(source['discovered']),
            str(source['processed']),
            f"{source['success_rate']:.1f}%",
            f"{source['avg_quality']:.2f}" if source['avg_quality'] else "N/A"
        )

    console.print(perf_table)

    # Quality distribution
    if perf_data['quality_distribution']:
        quality_table = Table(title="⭐ Quality Score Distribution", show_header=True)
        quality_table.add_column("Quality Tier", style="cyan")
        quality_table.add_column("Count", style="green")
        quality_table.add_column("Avg Priority", style="yellow")

        for tier in perf_data['quality_distribution']:
            quality_table.add_row(
                tier['quality_tier'],
                str(tier['count']),
                f"{tier['avg_priority']:.2f}" if tier['avg_priority'] else "N/A"
            )

        console.print(f"\n")
        console.print(quality_table)


@audit.command()
@click.pass_context
def issues(ctx):
    """Identify and report system bottlenecks and issues."""
    audit_cli = ctx.obj['audit']

    with console.status("[bold red]Scanning for system issues..."):
        issues_data = audit_cli.get_bottlenecks_and_issues()

    if issues_data['total_issues'] == 0:
        console.print(Panel(
            "[green]✅ No issues detected! System is running smoothly.[/green]",
            title="🏥 System Health Check",
            border_style="green"
        ))
        return

    # Issues summary
    severity = issues_data['severity_breakdown']
    summary = f"Found {issues_data['total_issues']} issues: "
    summary += f"{severity['high']} high, {severity['medium']} medium, {severity['low']} low severity"

    console.print(Panel(
        f"[yellow]⚠️ {summary}[/yellow]",
        title="🚨 Issues Detected",
        border_style="yellow"
    ))

    # Issues table
    issues_table = Table(title="🔧 System Issues", show_header=True)
    issues_table.add_column("Severity", style="red")
    issues_table.add_column("Type", style="cyan")
    issues_table.add_column("Description", style="white")

    severity_colors = {'high': 'red', 'medium': 'yellow', 'low': 'blue'}
    severity_icons = {'high': '🔥', 'medium': '⚠️', 'low': 'ℹ️'}

    for issue in issues_data['issues']:
        color = severity_colors[issue['severity']]
        icon = severity_icons[issue['severity']]

        issues_table.add_row(
            f"[{color}]{icon} {issue['severity'].upper()}[/{color}]",
            issue['type'],
            issue['description']
        )

    console.print(f"\n")
    console.print(issues_table)


@audit.command()
@click.option('--update-scores', is_flag=True, help='Update priority scores before showing report')
@click.pass_context
def priority(ctx, update_scores):
    """Show priority queue statistics and distribution."""
    audit_cli = ctx.obj['audit']

    if update_scores:
        with console.status("[bold cyan]Updating priority scores..."):
            updated = audit_cli.prioritizer.calculate_priority_scores(batch_size=1000)
        console.print(f"[green]✅ Updated priority scores for {updated} URLs[/green]\n")

    with console.status("[bold magenta]Gathering priority statistics..."):
        stats = audit_cli.prioritizer.get_priority_statistics()

    # Priority overview
    priority_table = Table(title="🎯 Priority Queue Statistics", show_header=True)
    priority_table.add_column("Metric", style="cyan")
    priority_table.add_column("Value", style="green")

    priority_table.add_row("Total Pending", str(stats['total_pending']))
    priority_table.add_row("Average Score", f"{stats['avg_score']:.3f}")
    priority_table.add_row("Score Range", f"{stats['min_score']:.3f} - {stats['max_score']:.3f}")
    priority_table.add_row("High Priority (>1.0)", str(stats['high_priority']))
    priority_table.add_row("Medium Priority (0.5-1.0)", str(stats['medium_priority']))
    priority_table.add_row("Low Priority (<0.5)", str(stats['low_priority']))

    console.print(priority_table)

    # Source rankings
    if stats['source_rankings']:
        ranking_table = Table(title="📊 Source Priority Rankings", show_header=True)
        ranking_table.add_column("Rank", style="yellow")
        ranking_table.add_column("Source", style="cyan")
        ranking_table.add_column("Avg Score", style="green")
        ranking_table.add_column("Count", style="blue")

        for i, source in enumerate(stats['source_rankings'], 1):
            ranking_table.add_row(
                str(i),
                source['source'],
                f"{source['avg_score']:.3f}",
                str(source['count'])
            )

        console.print(f"\n")
        console.print(ranking_table)


@audit.command()
@click.option('--count', type=int, default=10, help='Number of top URLs to show')
@click.pass_context
def top(ctx, count):
    """Show top-priority URLs ready for processing."""
    audit_cli = ctx.obj['audit']

    with console.status(f"[bold blue]Finding top {count} priority URLs..."):
        top_urls = audit_cli.prioritizer.get_next_batch_prioritized(batch_size=count)

    if not top_urls:
        console.print("[yellow]No URLs ready for processing.[/yellow]")
        return

    top_table = Table(title=f"🔥 Top {len(top_urls)} Priority URLs", show_header=True)
    top_table.add_column("Rank", style="yellow", width=4)
    top_table.add_column("URL", style="blue", max_width=50)
    top_table.add_column("Score", style="green")
    top_table.add_column("Source", style="cyan")
    top_table.add_column("Category", style="magenta")

    for i, url_data in enumerate(top_urls, 1):
        top_table.add_row(
            str(i),
            url_data['url'],
            f"{url_data['priority_score']:.3f}",
            url_data['source'],
            url_data['category']
        )

    console.print(top_table)


def main():
    """Entry point for the audit CLI."""
    audit()


if __name__ == "__main__":
    main()
