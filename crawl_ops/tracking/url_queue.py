#!/usr/bin/env python3
"""
URL Queue System for IntelForge - Systematic Content Discovery and Processing

Extends existing URL tracking infrastructure to support:
- Priority-based URL queue management
- Systematic content discovery from multiple sources
- Smart scheduling and processing optimization

Based on implementation plan in IMP_A_PERFORMANCE_OPTIMIZATION_PLAN_20250719_v1_CL.md
"""

import sqlite3
import orjson as json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Iterator
from pathlib import Path
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class URLQueue:
    """
    Priority-based URL queue system for systematic content discovery.
    
    Extends existing URLTracker infrastructure with queue management
    capabilities for scalable content processing.
    """
    
    def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
        """
        Initialize URL queue using existing URLTracker database.
        
        Args:
            db_path: Path to SQLite database file (shared with URLTracker)
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._create_queue_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper configuration."""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self.connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrent access
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA synchronous=NORMAL")
            self.connection.execute("PRAGMA cache_size=10000")
        return self.connection
    
    def _create_queue_tables(self):
        """Create URL queue tables extending existing schema."""
        conn = self._get_connection()
        
        # URL queue table for discovered URLs
        conn.execute("""
            CREATE TABLE IF NOT EXISTS url_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,  -- 'github', 'rss', 'manual', 'targeted'
                category TEXT DEFAULT 'general',
                priority INTEGER DEFAULT 5,  -- 1-10 scale (1=highest)
                discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_date TIMESTAMP,
                status TEXT DEFAULT 'queued',  -- 'queued', 'processing', 'completed', 'failed', 'skipped'
                quality_estimate REAL DEFAULT 0.0,
                metadata TEXT,  -- JSON metadata about discovery context
                retry_count INTEGER DEFAULT 0,
                last_retry TIMESTAMP,
                failure_reason TEXT
            )
        """)
        
        # Discovery sources configuration
        conn.execute("""
            CREATE TABLE IF NOT EXISTS discovery_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,  -- 'github_search', 'rss_feed', 'sitemap'
                source_url TEXT NOT NULL,
                source_config TEXT,  -- JSON configuration
                enabled BOOLEAN DEFAULT 1,
                last_check TIMESTAMP,
                total_discovered INTEGER DEFAULT 0,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Queue performance analytics
        conn.execute("""
            CREATE TABLE IF NOT EXISTS queue_analytics (
                date DATE PRIMARY KEY,
                urls_discovered INTEGER DEFAULT 0,
                urls_processed INTEGER DEFAULT 0,
                urls_skipped INTEGER DEFAULT 0,
                avg_quality_score REAL DEFAULT 0.0,
                processing_time_avg REAL DEFAULT 0.0,
                source_breakdown TEXT  -- JSON breakdown by source
            )
        """)
        
        # Indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_queue_status ON url_queue(status)",
            "CREATE INDEX IF NOT EXISTS idx_queue_priority ON url_queue(priority)",
            "CREATE INDEX IF NOT EXISTS idx_queue_source ON url_queue(source)",
            "CREATE INDEX IF NOT EXISTS idx_queue_category ON url_queue(category)",
            "CREATE INDEX IF NOT EXISTS idx_queue_discovered ON url_queue(discovered_date)",
            "CREATE INDEX IF NOT EXISTS idx_queue_scheduled ON url_queue(scheduled_date)",
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_queue_url ON url_queue(url)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
        
        conn.commit()
    
    def add_discovered_urls(self, urls: List[Dict[str, Any]]) -> int:
        """
        Add URLs from discovery sources with metadata.
        
        Args:
            urls: List of URL dictionaries with discovery metadata
                  Format: {
                      'url': str,
                      'source': str,
                      'category': str (optional),
                      'priority': int (optional, 1-10),
                      'quality_estimate': float (optional),
                      'metadata': dict (optional)
                  }
        
        Returns:
            Number of URLs successfully added to queue
        """
        conn = self._get_connection()
        added_count = 0
        
        for url_data in urls:
            try:
                # Parse domain for categorization
                parsed = urlparse(url_data['url'])
                domain = parsed.netloc.lower()
                
                # Prepare data with defaults
                queue_data = {
                    'url': url_data['url'],
                    'source': url_data['source'],
                    'category': url_data.get('category', self._infer_category(domain)),
                    'priority': url_data.get('priority', self._infer_priority(domain, url_data['source'])),
                    'quality_estimate': url_data.get('quality_estimate', 0.0),
                    'metadata': json.dumps(url_data.get('metadata', {})).decode('utf-8'),
                    'discovered_date': datetime.now().isoformat()
                }
                
                # Insert with conflict resolution (ignore duplicates)
                conn.execute("""
                    INSERT OR IGNORE INTO url_queue 
                    (url, source, category, priority, quality_estimate, metadata, discovered_date)
                    VALUES (?, ?,?, ?, ?, ?, ?)
                """, (
                    queue_data['url'],
                    queue_data['source'],
                    queue_data['category'],
                    queue_data['priority'],
                    queue_data['quality_estimate'],
                    queue_data['metadata'],
                    queue_data['discovered_date']
                ))
                
                if conn.total_changes > 0:
                    added_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to add URL {url_data.get('url', 'unknown')}: {e}")
                continue
        
        conn.commit()
        logger.info(f"Added {added_count} URLs to queue from {len(urls)} discovered")
        return added_count
    
    def get_next_urls(self, batch_size: int = 10, categories: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get next URLs for processing, priority-ordered.
        
        Args:
            batch_size: Number of URLs to return
            categories: Optional category filter
            
        Returns:
            List of URL dictionaries ready for processing
        """
        conn = self._get_connection()
        
        # Build query with optional category filter
        where_clause = "WHERE status = 'queued'"
        params = []
        
        if categories:
            placeholders = ','.join(['?' for _ in categories])
            where_clause += f" AND category IN ({placeholders})"
            params.extend(categories)
        
        query = f"""
            SELECT * FROM url_queue 
            {where_clause}
            ORDER BY priority ASC, quality_estimate DESC, discovered_date ASC
            LIMIT ?
        """
        params.append(batch_size)
        
        cursor = conn.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            url_data = dict(row)
            # Parse metadata JSON
            try:
                url_data['metadata'] = json.loads(url_data['metadata'] or '{}')
            except:
                url_data['metadata'] = {}
            results.append(url_data)
        
        # Mark selected URLs as processing
        if results:
            url_ids = [r['id'] for r in results]
            placeholders = ','.join(['?' for _ in url_ids])
            conn.execute(f"""
                UPDATE url_queue 
                SET status = 'processing', scheduled_date = ?
                WHERE id IN ({placeholders})
            """, [datetime.now().isoformat()] + url_ids)
            conn.commit()
        
        return results
    
    def mark_url_completed(self, url: str, success: bool = True, quality_score: float = None, 
                          failure_reason: str = None):
        """
        Mark URL as completed or failed in the queue.
        
        Args:
            url: URL that was processed
            success: Whether processing was successful
            quality_score: Optional quality score from processing
            failure_reason: Reason for failure if success=False
        """
        conn = self._get_connection()
        
        if success:
            update_data = {
                'status': 'completed',
                'quality_estimate': quality_score or 0.0
            }
            conn.execute("""
                UPDATE url_queue 
                SET status = ?, quality_estimate = ?
                WHERE url = ?
            """, ('completed', quality_score or 0.0, url))
        else:
            conn.execute("""
                UPDATE url_queue 
                SET status = 'failed', failure_reason = ?, retry_count = retry_count + 1,
                    last_retry = ?
                WHERE url = ?
            """, ('failed', failure_reason, datetime.now().isoformat(), url))
        
        conn.commit()
    
    def get_queue_statistics(self) -> Dict[str, Any]:
        """Get comprehensive queue statistics for monitoring."""
        conn = self._get_connection()
        
        # Basic counts by status
        cursor = conn.execute("""
            SELECT status, COUNT(*) as count 
            FROM url_queue 
            GROUP BY status
        """)
        status_counts = dict(cursor.fetchall())
        
        # Source breakdown
        cursor = conn.execute("""
            SELECT source, COUNT(*) as count, AVG(quality_estimate) as avg_quality
            FROM url_queue 
            GROUP BY source
        """)
        source_breakdown = {row[0]: {'count': row[1], 'avg_quality': row[2] or 0.0} 
                           for row in cursor.fetchall()}
        
        # Category breakdown
        cursor = conn.execute("""
            SELECT category, COUNT(*) as count, AVG(priority) as avg_priority
            FROM url_queue 
            GROUP BY category
        """)
        category_breakdown = {row[0]: {'count': row[1], 'avg_priority': row[2] or 5.0} 
                             for row in cursor.fetchall()}
        
        # Processing efficiency
        cursor = conn.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing,
                COUNT(*) as total
            FROM url_queue
        """)
        row = cursor.fetchone()
        efficiency = {
            'total_urls': row[3] or 0,
            'completed': row[0] or 0,
            'failed': row[1] or 0,
            'processing': row[2] or 0,
            'success_rate': (row[0] / max(row[3], 1)) * 100
        }
        
        return {
            'status_counts': status_counts,
            'source_breakdown': source_breakdown,
            'category_breakdown': category_breakdown,
            'efficiency': efficiency,
            'queue_size': status_counts.get('queued', 0),
            'last_updated': datetime.now().isoformat()
        }
    
    def _infer_category(self, domain: str) -> str:
        """Infer content category from domain."""
        domain_categories = {
            'quantstart.com': 'tutorial',
            'quantinsti.com': 'education', 
            'investopedia.com': 'reference',
            'github.com': 'code',
            'arxiv.org': 'research',
            'medium.com': 'blog',
            'towards': 'blog'  # covers towardsdatascience.com etc
        }
        
        for domain_pattern, category in domain_categories.items():
            if domain_pattern in domain:
                return category
        
        return 'general'
    
    def _infer_priority(self, domain: str, source: str) -> int:
        """Infer processing priority (1=highest, 10=lowest)."""
        # High-quality educational sources get priority
        high_priority_domains = [
            'quantstart.com', 'quantinsti.com', 'mit.edu', 
            'stanford.edu', 'arxiv.org'
        ]
        
        # Manual additions get higher priority
        if source == 'manual':
            return 2
        
        # High-quality domains get priority
        for domain in high_priority_domains:
            if domain in domain:
                return 3
        
        # GitHub repositories get medium priority
        if 'github.com' in domain:
            return 4
        
        # RSS feeds and automated discovery get lower priority
        if source in ['rss', 'automated']:
            return 6
        
        return 5  # Default priority
    
    def cleanup_old_entries(self, days_old: int = 90):
        """Remove old completed/failed entries to manage database size."""
        conn = self._get_connection()
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        cursor = conn.execute("""
            DELETE FROM url_queue 
            WHERE status IN ('completed', 'failed') 
            AND discovered_date < ?
        """, (cutoff_date.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        logger.info(f"Cleaned up {deleted_count} old queue entries")
        return deleted_count


# Integration helper functions for existing pipeline
def integrate_with_url_tracker():
    """
    Integration helper to work with existing URLTracker.
    
    This allows seamless integration where URLTracker handles
    deduplication and URLQueue handles discovery and scheduling.
    """
    from .url_tracker import URLTracker
    
    class IntegratedURLManager:
        def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
            self.tracker = URLTracker(db_path)
            self.queue = URLQueue(db_path)
        
        def process_discovery_batch(self, batch_size: int = 10) -> List[str]:
            """
            Get next batch of URLs, check against tracker, return new URLs.
            
            Returns:
                List of URLs ready for crawling (not in tracker or due for refresh)
            """
            queued_urls = self.queue.get_next_urls(batch_size)
            crawl_ready_urls = []
            
            for url_data in queued_urls:
                url = url_data['url']
                should_crawl, reason = self.tracker.should_crawl(url)
                
                if should_crawl:
                    crawl_ready_urls.append(url)
                else:
                    # Mark as skipped in queue
                    self.queue.mark_url_completed(url, success=True, failure_reason=f"Skipped: {reason}")
            
            return crawl_ready_urls
    
    return IntegratedURLManager


if __name__ == "__main__":
    # Test the URL queue system
    queue = URLQueue()
    
    # Add some test URLs
    test_urls = [
        {
            'url': 'https://quantstart.com/articles/new-strategy',
            'source': 'manual',
            'category': 'tutorial',
            'priority': 2,
            'quality_estimate': 0.85
        },
        {
            'url': 'https://github.com/quantitative-research/algo-trading',
            'source': 'github',
            'category': 'code',
            'metadata': {'stars': 150, 'language': 'python'}
        }
    ]
    
    added = queue.add_discovered_urls(test_urls)
    print(f"Added {added} URLs to queue")
    
    # Get statistics
    stats = queue.get_queue_statistics()
    print(f"Queue statistics: {json.dumps(stats, indent=2).decode('utf-8')}")
    
    # Get next URLs for processing
    next_batch = queue.get_next_urls(5)
    print(f"Next {len(next_batch)} URLs ready for processing")