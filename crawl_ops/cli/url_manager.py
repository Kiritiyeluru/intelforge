#!/usr/bin/env python3
"""
CLI tool for managing IntelForge URL tracking database.
Provides commands for statistics, cleanup, and policy management.
"""

import argparse
import sys
import orjson as json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
import sqlite3

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crawl_ops.tracking.url_tracker import URLTracker
from crawl_ops.tracking.refresh_policies import RefreshPolicyManager
from crawl_ops.tracking.content_detector import ContentChangeDetector


class URLManagerCLI:
    """Command-line interface for URL tracking management."""
    
    def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
        """
        Initialize CLI with database path.
        
        Args:
            db_path: Path to URL tracker database
        """
        self.db_path = db_path
        self.tracker = None
        self.policy_manager = None
        self.content_detector = None
    
    def _init_components(self):
        """Initialize tracking components."""
        if not self.tracker:
            self.tracker = URLTracker(self.db_path)
            self.policy_manager = RefreshPolicyManager()
            self.content_detector = ContentChangeDetector()
    
    def _cleanup_components(self):
        """Cleanup tracking components."""
        if self.tracker:
            self.tracker.close()
            self.tracker = None
    
    def show_statistics(self, site: Optional[str] = None, detailed: bool = False):
        """
        Show URL tracking statistics.
        
        Args:
            site: Specific site to show stats for
            detailed: Show detailed statistics
        """
        try:
            self._init_components()
            
            if site:
                stats = self.tracker.get_site_stats(site)
                if not stats:
                    print(f"No statistics found for site: {site}")
                    return
                
                print(f"\n📊 Statistics for {site}:")
                print(f"  Total URLs: {stats.get('total_urls', 0)}")
                print(f"  Total crawls: {stats.get('total_crawls', 0)}")
                print(f"  Average crawls per URL: {stats.get('avg_crawls_per_url', 0):.2f}")
                print(f"  Efficiency ratio: {stats.get('efficiency_ratio', 0):.3f}")
                print(f"  Success rate: {stats.get('success_count', 0)} / {stats.get('total_urls', 0)}")
                print(f"  Failed URLs: {stats.get('failed_count', 0)}")
                if stats.get('avg_quality'):
                    print(f"  Average quality score: {stats.get('avg_quality'):.1f}")
                print(f"  Last activity: {stats.get('last_activity', 'Unknown')}")
            else:
                stats = self.tracker.get_site_stats()
                sites = stats.get('sites', [])
                
                if not sites:
                    print("No tracking data found.")
                    return
                
                print(f"\n📊 URL Tracking Statistics ({len(sites)} sites)")
                print("=" * 80)
                
                total_urls = sum(site['total_urls'] for site in sites)
                total_crawls = sum(site['total_crawls'] for site in sites)
                
                print(f"Overall totals:")
                print(f"  Total URLs tracked: {total_urls}")
                print(f"  Total crawl attempts: {total_crawls}")
                if total_urls > 0:
                    print(f"  Average crawls per URL: {total_crawls / total_urls:.2f}")
                    efficiency = total_urls / total_crawls if total_crawls > 0 else 0
                    print(f"  Overall efficiency: {efficiency:.3f}")
                
                print(f"\nPer-site breakdown:")
                print(f"{'Site':<30} {'URLs':<8} {'Crawls':<8} {'Efficiency':<12} {'Quality':<8}")
                print("-" * 80)
                
                for site_data in sorted(sites, key=lambda x: x['total_urls'], reverse=True):
                    site_name = site_data['site'][:29]
                    urls = site_data['total_urls']
                    crawls = site_data['total_crawls']
                    efficiency = site_data.get('efficiency_ratio', 0)
                    quality = site_data.get('avg_quality', 0)
                    
                    print(f"{site_name:<30} {urls:<8} {crawls:<8} {efficiency:<12.3f} {quality:<8.1f}")
                
                if detailed:
                    self._show_detailed_statistics()
        
        except Exception as e:
            print(f"Error showing statistics: {e}")
        finally:
            self._cleanup_components()
    
    def _show_detailed_statistics(self):
        """Show detailed tracking statistics."""
        try:
            # Show frequently changing URLs
            frequent_changes = self.tracker.get_frequently_changing_urls(limit=10)
            
            if frequent_changes:
                print(f"\n🔄 Most Frequently Changing URLs (Top 10):")
                print(f"{'URL':<50} {'Changes':<8} {'Days/Change':<12} {'Quality':<8}")
                print("-" * 80)
                
                for url_data in frequent_changes:
                    url = url_data['url'][:49]
                    changes = url_data['scrape_count']
                    days_per_change = url_data.get('days_per_change', 0)
                    quality = url_data.get('quality_score', 0) or 0
                    
                    print(f"{url:<50} {changes:<8} {days_per_change:<12.1f} {quality:<8}")
            
            # Show recent activity
            self._show_recent_activity()
            
        except Exception as e:
            print(f"Error showing detailed statistics: {e}")
    
    def _show_recent_activity(self):
        """Show recent crawling activity."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Get recent crawls (last 24 hours)
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            
            cursor = conn.execute("""
                SELECT site, COUNT(*) as recent_crawls
                FROM scraped_urls 
                WHERE last_scraped > ?
                GROUP BY site
                ORDER BY recent_crawls DESC
                LIMIT 10
            """, (yesterday,))
            
            recent_activity = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if recent_activity:
                print(f"\n🕒 Recent Activity (Last 24 Hours):")
                print(f"{'Site':<30} {'Crawls':<8}")
                print("-" * 40)
                
                for activity in recent_activity:
                    site_name = activity['site'][:29]
                    crawls = activity['recent_crawls']
                    print(f"{site_name:<30} {crawls:<8}")
            
        except Exception as e:
            print(f"Error showing recent activity: {e}")
    
    def check_duplicates(self, threshold: int = 2):
        """
        Check for potential duplicate URLs.
        
        Args:
            threshold: Minimum number of URLs with same content hash to report
        """
        try:
            self._init_components()
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT content_hash, COUNT(*) as url_count, 
                       GROUP_CONCAT(url, '; ') as urls
                FROM scraped_urls 
                WHERE content_hash != ''
                GROUP BY content_hash
                HAVING COUNT(*) >= ?
                ORDER BY url_count DESC
                LIMIT 20
            """, (threshold,))
            
            duplicates = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            if not duplicates:
                print(f"✅ No duplicate content found (threshold: {threshold})")
                return
            
            print(f"\n🔍 Potential Duplicate Content (threshold: {threshold}):")
            print("=" * 80)
            
            for dup in duplicates:
                url_count = dup['url_count']
                content_hash = dup['content_hash'][:16]
                urls = dup['urls'].split('; ')
                
                print(f"\nContent Hash: {content_hash}... ({url_count} URLs)")
                for i, url in enumerate(urls[:5]):  # Show first 5 URLs
                    print(f"  {i+1}. {url}")
                if len(urls) > 5:
                    print(f"  ... and {len(urls) - 5} more")
        
        except Exception as e:
            print(f"Error checking duplicates: {e}")
        finally:
            self._cleanup_components()
    
    def cleanup_old_records(self, days_old: int = 365, dry_run: bool = True):
        """
        Clean up old URL records.
        
        Args:
            days_old: Remove records older than this many days
            dry_run: Show what would be removed without actually removing
        """
        try:
            self._init_components()
            
            if dry_run:
                # Count what would be removed
                conn = sqlite3.connect(self.db_path)
                cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
                
                cursor = conn.execute("""
                    SELECT COUNT(*) as count FROM scraped_urls 
                    WHERE last_scraped < ? AND status = 'failed'
                """, (cutoff_date,))
                
                count = cursor.fetchone()[0]
                conn.close()
                
                print(f"🗑️  Cleanup Preview (dry run):")
                print(f"  Records older than {days_old} days: {count}")
                print(f"  Cutoff date: {cutoff_date}")
                print(f"\nRun with --execute to perform actual cleanup")
            else:
                removed_count = self.tracker.cleanup_old_records(days_old)
                print(f"✅ Cleanup completed: {removed_count} old records removed")
        
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            self._cleanup_components()
    
    def update_policy(self, site: Optional[str] = None, 
                     content_type: Optional[str] = None,
                     days: int = 30):
        """
        Update refresh policy for site or content type.
        
        Args:
            site: Site domain to update
            content_type: Content type to update
            days: New refresh interval in days
        """
        try:
            self._init_components()
            
            if not site and not content_type:
                print("Error: Must specify either --site or --content-type")
                return
            
            self.policy_manager.update_policy(
                site=site,
                content_type=content_type,
                interval=days
            )
            
            if site:
                print(f"✅ Updated refresh policy for site '{site}' to {days} days")
            if content_type:
                print(f"✅ Updated refresh policy for content type '{content_type}' to {days} days")
        
        except Exception as e:
            print(f"Error updating policy: {e}")
        finally:
            self._cleanup_components()
    
    def show_policies(self):
        """Show current refresh policies."""
        try:
            self._init_components()
            
            print("\n📋 Current Refresh Policies:")
            print("=" * 60)
            
            print("\nSite-specific policies:")
            for site, days in sorted(self.policy_manager.site_policies.items()):
                print(f"  {site:<30} {days:>3} days")
            
            print(f"\nContent-type policies:")
            for content_type, days in sorted(self.policy_manager.content_type_policies.items()):
                print(f"  {content_type:<20} {days:>3} days")
        
        except Exception as e:
            print(f"Error showing policies: {e}")
        finally:
            self._cleanup_components()
    
    def analyze_patterns(self):
        """Analyze crawling patterns and provide recommendations."""
        try:
            self._init_components()
            
            print("\n🔍 Analyzing Crawling Patterns...")
            
            recommendations = self.policy_manager.get_policy_recommendations(self.tracker)
            
            if 'error' in recommendations:
                print(f"Error generating recommendations: {recommendations['error']}")
                return
            
            print(f"\n📈 Policy Recommendations:")
            print("=" * 60)
            
            # Site adjustments
            site_adjustments = recommendations.get('site_adjustments', {})
            if site_adjustments:
                print(f"\nSuggested site policy adjustments:")
                for site, adjustment in site_adjustments.items():
                    current = adjustment['current']
                    recommended = adjustment['recommended']
                    reason = adjustment['reason']
                    print(f"  {site:<25} {current:>3} → {recommended:>3} days ({reason})")
            else:
                print(f"\n✅ No site policy adjustments recommended")
            
            # Rarely changing content
            rarely_changing = recommendations.get('rarely_changing', [])
            if rarely_changing:
                print(f"\nSites with high efficiency (rarely changing content):")
                for item in rarely_changing[:10]:
                    site = item['site']
                    efficiency = item['efficiency_ratio']
                    current_policy = item['current_policy']
                    recommended_policy = item['recommended_policy']
                    print(f"  {site:<25} Efficiency: {efficiency:.3f} | {current_policy} → {recommended_policy} days")
            
            print(f"\nAnalysis completed at: {recommendations.get('analysis_date', 'Unknown')}")
        
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
        finally:
            self._cleanup_components()
    
    def force_refresh_url(self, url: str):
        """
        Force refresh a specific URL by removing it from tracking.
        
        Args:
            url: URL to force refresh
        """
        try:
            self._init_components()
            
            # Check if URL exists
            record = self.tracker.get_url_record(url)
            if not record:
                print(f"❌ URL not found in tracking database: {url}")
                return
            
            # Remove the record to force re-crawl
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("DELETE FROM scraped_urls WHERE url = ?", (url,))
            removed_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if removed_count > 0:
                print(f"✅ Removed URL from tracking: {url}")
                print(f"   Next crawl will treat this as a new URL")
            else:
                print(f"❌ Failed to remove URL: {url}")
        
        except Exception as e:
            print(f"Error forcing refresh: {e}")
        finally:
            self._cleanup_components()
    
    def export_data(self, output_file: str, format_type: str = "json"):
        """
        Export tracking data to file.
        
        Args:
            output_file: Output file path
            format_type: Export format ('json' or 'csv')
        """
        try:
            self._init_components()
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("SELECT * FROM scraped_urls ORDER BY last_scraped DESC")
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type.lower() == "json":
                with open(output_path, 'w') as f:
                    json.dump(records, f, indent=2, default=str)
            elif format_type.lower() == "csv":
                import csv
                
                if records:
                    with open(output_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=records[0].keys())
                        writer.writeheader()
                        writer.writerows(records)
            else:
                print(f"Unsupported format: {format_type}")
                return
            
            print(f"✅ Exported {len(records)} records to {output_path}")
        
        except Exception as e:
            print(f"Error exporting data: {e}")
        finally:
            self._cleanup_components()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="IntelForge URL Tracking Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s stats                           # Show overall statistics
  %(prog)s stats --site quantstart.com    # Show stats for specific site
  %(prog)s duplicates                      # Check for duplicate content
  %(prog)s cleanup --days 180 --execute   # Remove records older than 180 days
  %(prog)s policy --site example.com --days 60  # Update site policy
  %(prog)s analyze                         # Analyze patterns and get recommendations
  %(prog)s refresh --url https://example.com/page  # Force refresh specific URL
  %(prog)s export tracking_data.json       # Export data to JSON
        """
    )
    
    parser.add_argument(
        '--db-path',
        default="crawl_ops/tracking/url_tracker.db",
        help="Path to URL tracking database"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Statistics command
    stats_parser = subparsers.add_parser('stats', help='Show tracking statistics')
    stats_parser.add_argument('--site', help='Show stats for specific site')
    stats_parser.add_argument('--detailed', action='store_true', help='Show detailed statistics')
    
    # Duplicates command
    dup_parser = subparsers.add_parser('duplicates', help='Check for duplicate content')
    dup_parser.add_argument('--threshold', type=int, default=2, 
                           help='Minimum URLs per content hash to report')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old records')
    cleanup_parser.add_argument('--days', type=int, default=365,
                               help='Remove records older than N days')
    cleanup_parser.add_argument('--execute', action='store_true',
                               help='Actually perform cleanup (default is dry run)')
    
    # Policy command
    policy_parser = subparsers.add_parser('policy', help='Manage refresh policies')
    policy_parser.add_argument('--site', help='Site domain to update')
    policy_parser.add_argument('--content-type', help='Content type to update')
    policy_parser.add_argument('--days', type=int, default=30,
                              help='Refresh interval in days')
    policy_parser.add_argument('--show', action='store_true',
                              help='Show current policies')
    
    # Analysis command
    subparsers.add_parser('analyze', help='Analyze patterns and get recommendations')
    
    # Refresh command
    refresh_parser = subparsers.add_parser('refresh', help='Force refresh specific URL')
    refresh_parser.add_argument('--url', required=True, help='URL to force refresh')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export tracking data')
    export_parser.add_argument('output_file', help='Output file path')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json',
                              help='Export format')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = URLManagerCLI(args.db_path)
    
    try:
        if args.command == 'stats':
            cli.show_statistics(args.site, args.detailed)
        elif args.command == 'duplicates':
            cli.check_duplicates(args.threshold)
        elif args.command == 'cleanup':
            cli.cleanup_old_records(args.days, not args.execute)
        elif args.command == 'policy':
            if args.show:
                cli.show_policies()
            else:
                cli.update_policy(args.site, args.content_type, args.days)
        elif args.command == 'analyze':
            cli.analyze_patterns()
        elif args.command == 'refresh':
            cli.force_refresh_url(args.url)
        elif args.command == 'export':
            cli.export_data(args.output_file, args.format)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()