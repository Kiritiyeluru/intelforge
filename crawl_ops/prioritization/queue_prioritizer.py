#!/usr/bin/env python3
"""
Queue Prioritization Engine for IntelForge
Uses existing infrastructure (SQLite + enrichment metadata) for intelligent URL prioritization.
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import orjson as json
import math
from tqdm import tqdm


class QueuePrioritizer:
    """
    Intelligent queue prioritization using existing enrichment metadata.
    No custom logic - just smart SQL queries and existing quality scores.
    """
    
    def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
        """Initialize with existing database path."""
        self.db_path = db_path
        self._ensure_priority_schema()
    
    def _ensure_priority_schema(self):
        """Add priority_score column if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if priority_score column exists
            cursor.execute("PRAGMA table_info(url_queue)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'priority_score' not in columns:
                cursor.execute("""
                    ALTER TABLE url_queue 
                    ADD COLUMN priority_score REAL DEFAULT 0.5
                """)
                
                # Create index for fast priority-based queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_queue_priority 
                    ON url_queue(priority_score DESC, discovered_date ASC)
                """)
                
                conn.commit()
                print("✅ Added priority_score column and index to url_queue")
    
    def calculate_priority_scores(self, batch_size: int = 1000) -> int:
        """
        Calculate priority scores for all pending URLs using existing metadata.
        Returns number of URLs updated.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if url_tracker table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='url_tracker'
            """)
            has_tracker_table = cursor.fetchone() is not None
            
            # Get pending URLs with optional enrichment data
            if has_tracker_table:
                cursor.execute("""
                    SELECT 
                        uq.id,
                        uq.url,
                        uq.quality_estimate,
                        uq.priority,
                        uq.source,
                        uq.category,
                        uq.discovered_date,
                        uq.metadata,
                        ut.content_hash,
                        ut.last_crawled,
                        ut.crawl_count,
                        ut.last_status
                    FROM url_queue uq
                    LEFT JOIN url_tracker ut ON uq.url = ut.url
                    WHERE uq.status = 'queued'
                    ORDER BY uq.id
                    LIMIT ?
                """, (batch_size,))
            else:
                cursor.execute("""
                    SELECT 
                        uq.id,
                        uq.url,
                        uq.quality_estimate,
                        uq.priority,
                        uq.source,
                        uq.category,
                        uq.discovered_date,
                        uq.metadata,
                        NULL as content_hash,
                        NULL as last_crawled,
                        NULL as crawl_count,
                        NULL as last_status
                    FROM url_queue uq
                    WHERE uq.status = 'queued'
                    ORDER BY uq.id
                    LIMIT ?
                """, (batch_size,))
            
            urls_data = cursor.fetchall()
            updates = []
            
            for row in tqdm(urls_data, desc="Calculating priority scores", unit="URL"):
                (queue_id, url, quality_estimate, priority, source, category, 
                 discovered_date, metadata_json, content_hash, last_crawled, 
                 crawl_count, last_status) = row
                
                # Parse metadata
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except:
                    metadata = {}
                
                # Calculate priority score using existing data
                priority_score = self._calculate_url_priority_score(
                    debug=False,
                    url=url,
                    quality_estimate=quality_estimate or 0.0,
                    priority=priority or 5,
                    source=source,
                    category=category,
                    discovered_date=discovered_date,
                    metadata=metadata,
                    content_hash=content_hash,
                    last_crawled=last_crawled,
                    crawl_count=crawl_count or 0,
                    last_status=last_status
                )
                
                updates.append((priority_score, queue_id))
            
            # Batch update priority scores
            if updates:
                cursor.executemany("""
                    UPDATE url_queue 
                    SET priority_score = ?
                    WHERE id = ?
                """, updates)
                
                conn.commit()
            
            return len(updates)
    
    def _calculate_url_priority_score(self, debug: bool = False, **kwargs) -> float:
        """
        Calculate priority score using existing enrichment metadata.
        Higher score = higher priority.
        
        Args:
            debug: If True, return dict with score breakdown instead of float
        """
        url = kwargs.get('url', '')
        quality_estimate = kwargs.get('quality_estimate', 0.0)
        priority = kwargs.get('priority', 5)
        source = kwargs.get('source', '')
        category = kwargs.get('category', '')
        discovered_date = kwargs.get('discovered_date', '')
        metadata = kwargs.get('metadata', {})
        content_hash = kwargs.get('content_hash')
        last_crawled = kwargs.get('last_crawled')
        crawl_count = kwargs.get('crawl_count', 0)
        last_status = kwargs.get('last_status')
        
        # Base score from quality estimate (0.0 - 1.0)
        base_score = float(quality_estimate)
        
        # Source quality bonus (using existing source reputation)
        source_bonuses = {
            'manual': 0.3,           # Manually curated = high value
            'github_api': 0.2,       # GitHub repos = good quality
            'rss_discovery': 0.15,   # RSS feeds = medium quality
            'sitemap': 0.1,          # Sitemap = systematic discovery
            'google_search': 0.05,   # Search results = lower confidence
            'bing_search': 0.05
        }
        source_bonus = source_bonuses.get(source, 0.0)
        
        # Category priority boost
        category_bonuses = {
            'strategy': 0.25,        # Trading strategies = highest value
            'research': 0.2,         # Research papers = high value
            'tutorial': 0.15,        # Educational content = good value
            'code': 0.1,             # Code repositories = useful
            'blog': 0.05,            # Blog posts = some value
            'news': 0.02             # News = timely but lower priority
        }
        category_bonus = category_bonuses.get(category, 0.0)
        
        # Recency bonus (newer discoveries get priority boost)
        recency_bonus = 0.0
        if discovered_date:
            try:
                discovered_dt = datetime.fromisoformat(discovered_date.replace('Z', '+00:00'))
                days_old = (datetime.now() - discovered_dt.replace(tzinfo=None)).days
                
                if days_old <= 1:
                    recency_bonus = 0.2      # Very recent
                elif days_old <= 7:
                    recency_bonus = 0.1      # Recent
                elif days_old <= 30:
                    recency_bonus = 0.05     # Moderately recent
                # No bonus for older content
            except:
                pass
        
        # Domain authority bonus (extract from URL)
        domain_bonus = 0.0
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.lower()
            
            authority_domains = {
                'quantstart.com': 0.3,
                'blog.quantinsti.com': 0.25,
                'arxiv.org': 0.3,
                'papers.ssrn.com': 0.25,
                'github.com': 0.2,
                'investopedia.com': 0.2,
                'bloomberg.com': 0.15,
                'reuters.com': 0.15
            }
            
            for auth_domain, bonus in authority_domains.items():
                if auth_domain in domain:
                    domain_bonus = bonus
                    break
        except:
            pass
        
        # Crawl history penalty/bonus
        crawl_bonus = 0.0
        if last_status:
            if last_status == 'success':
                crawl_bonus = 0.1        # Previously successful = likely good
            elif last_status == 'failed':
                crawl_bonus = -0.2       # Previously failed = lower priority
        
        # Avoid re-crawling too frequently
        freshness_penalty = 0.0
        if last_crawled:
            try:
                last_crawled_dt = datetime.fromisoformat(last_crawled.replace('Z', '+00:00'))
                days_since_crawl = (datetime.now() - last_crawled_dt.replace(tzinfo=None)).days
                
                if days_since_crawl < 7:
                    freshness_penalty = -0.3    # Recently crawled = lower priority
                elif days_since_crawl < 30:
                    freshness_penalty = -0.1    # Somewhat recent = small penalty
            except:
                pass
        
        # Content metadata bonuses (from existing enrichment)
        content_bonus = 0.0
        if metadata:
            # Strategy density bonus (if available from enrichment)
            strategy_density = metadata.get('strategy_density', 0)
            if strategy_density:
                content_bonus += min(strategy_density * 0.2, 0.2)
            
            # Keyword bonuses
            title = metadata.get('title', '').lower()
            description = metadata.get('description', '').lower()
            content_text = f"{title} {description}"
            
            high_value_keywords = [
                'backtest', 'algorithm', 'strategy', 'quantitative', 
                'machine learning', 'python', 'trading', 'portfolio'
            ]
            
            keyword_matches = sum(1 for keyword in high_value_keywords if keyword in content_text)
            content_bonus += min(keyword_matches * 0.05, 0.25)
        
        # Priority inversion (lower priority number = higher importance)
        priority_score = max(0, 10 - priority) * 0.05  # Convert 1-10 to 0.45-0.0
        
        # Combine all factors
        final_score = (
            base_score +
            source_bonus +
            category_bonus +
            recency_bonus +
            domain_bonus +
            crawl_bonus +
            freshness_penalty +
            content_bonus +
            priority_score
        )
        
        # Clamp to reasonable range
        clamped_score = max(0.0, min(final_score, 2.0))
        
        if debug:
            return {
                "final_score": clamped_score,
                "components": {
                    "base_score": base_score,
                    "source_bonus": source_bonus,
                    "category_bonus": category_bonus,
                    "recency_bonus": recency_bonus,
                    "domain_bonus": domain_bonus,
                    "crawl_bonus": crawl_bonus,
                    "freshness_penalty": freshness_penalty,
                    "content_bonus": content_bonus,
                    "priority_score": priority_score
                },
                "metadata": {
                    "url": url,
                    "source": source,
                    "category": category
                }
            }
        
        return clamped_score
    
    def get_next_batch_prioritized(self, batch_size: int = 50, 
                                 categories: Optional[List[str]] = None,
                                 min_quality: float = 0.0) -> List[Dict]:
        """
        Get next batch of URLs ordered by priority score.
        Uses pure SQL for maximum performance.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            # Build category filter
            category_filter = ""
            params = [min_quality, batch_size]
            
            if categories:
                placeholders = ','.join(['?' for _ in categories])
                category_filter = f"AND category IN ({placeholders})"
                params = [min_quality] + categories + [batch_size]
            
            query = f"""
                SELECT 
                    url, source, category, priority, quality_estimate,
                    priority_score, discovered_date, metadata,
                    (priority_score * 100) as score_pct
                FROM url_queue
                WHERE status = 'queued' 
                  AND quality_estimate >= ?
                  {category_filter}
                ORDER BY priority_score DESC, discovered_date ASC
                LIMIT ?
            """
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_priority_for_source(self, source: str, score_multiplier: float = 1.0):
        """Update priority scores for all URLs from a specific source."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE url_queue 
                SET priority_score = priority_score * ?
                WHERE source = ? AND status = 'pending'
            """, (score_multiplier, source))
            
            updated = cursor.rowcount
            conn.commit()
            
            return updated
    
    def get_priority_statistics(self) -> Dict:
        """Get priority distribution statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_pending,
                    AVG(priority_score) as avg_score,
                    MIN(priority_score) as min_score,
                    MAX(priority_score) as max_score,
                    COUNT(CASE WHEN priority_score > 1.0 THEN 1 END) as high_priority,
                    COUNT(CASE WHEN priority_score BETWEEN 0.5 AND 1.0 THEN 1 END) as medium_priority,
                    COUNT(CASE WHEN priority_score < 0.5 THEN 1 END) as low_priority
                FROM url_queue
                WHERE status = 'queued'
            """)
            
            row = cursor.fetchone()
            if row:
                stats = dict(zip([col[0] for col in cursor.description], row))
            else:
                stats = {
                    'total_pending': 0, 'avg_score': 0.0, 'min_score': 0.0, 
                    'max_score': 0.0, 'high_priority': 0, 'medium_priority': 0, 
                    'low_priority': 0
                }
            
            # Get top sources by priority
            cursor.execute("""
                SELECT source, AVG(priority_score) as avg_score, COUNT(*) as count
                FROM url_queue
                WHERE status = 'queued'
                GROUP BY source
                ORDER BY avg_score DESC
            """)
            
            rows = cursor.fetchall()
            if rows:
                cols = [col[0] for col in cursor.description]
                stats['source_rankings'] = [dict(zip(cols, row)) for row in rows]
            else:
                stats['source_rankings'] = []
            
            return stats
    
    def debug_priority_calculation(self, url: str) -> Dict:
        """Get detailed priority score breakdown for a specific URL."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if url_tracker table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='url_tracker'
            """)
            has_tracker_table = cursor.fetchone() is not None
            
            if has_tracker_table:
                cursor.execute("""
                    SELECT 
                        uq.url,
                        uq.quality_estimate,
                        uq.priority,
                        uq.source,
                        uq.category,
                        uq.discovered_date,
                        uq.metadata,
                        ut.content_hash,
                        ut.last_crawled,
                        ut.crawl_count,
                        ut.last_status
                    FROM url_queue uq
                    LEFT JOIN url_tracker ut ON uq.url = ut.url
                    WHERE uq.url = ?
                    LIMIT 1
                """, (url,))
            else:
                cursor.execute("""
                    SELECT 
                        uq.url,
                        uq.quality_estimate,
                        uq.priority,
                        uq.source,
                        uq.category,
                        uq.discovered_date,
                        uq.metadata,
                        NULL as content_hash,
                        NULL as last_crawled,
                        NULL as crawl_count,
                        NULL as last_status
                    FROM url_queue uq
                    WHERE uq.url = ?
                    LIMIT 1
                """, (url,))
            
            row = cursor.fetchone()
            if not row:
                return {"error": f"URL not found in queue: {url}"}
            
            (url_found, quality_estimate, priority, source, category, 
             discovered_date, metadata_json, content_hash, last_crawled, 
             crawl_count, last_status) = row
            
            # Parse metadata
            try:
                metadata = json.loads(metadata_json) if metadata_json else {}
            except:
                metadata = {}
            
            # Get debug breakdown
            return self._calculate_url_priority_score(
                debug=True,
                url=url_found,
                quality_estimate=quality_estimate or 0.0,
                priority=priority or 5,
                source=source,
                category=category,
                discovered_date=discovered_date,
                metadata=metadata,
                content_hash=content_hash,
                last_crawled=last_crawled,
                crawl_count=crawl_count or 0,
                last_status=last_status
            )


if __name__ == "__main__":
    # Test the prioritization engine
    prioritizer = QueuePrioritizer()
    
    print("🎯 Testing Queue Prioritization Engine")
    print("=" * 50)
    
    # Calculate priority scores
    updated = prioritizer.calculate_priority_scores(batch_size=100)
    print(f"✅ Updated priority scores for {updated} URLs")
    
    # Get statistics
    stats = prioritizer.get_priority_statistics()
    print(f"\n📊 Priority Statistics:")
    print(f"  Total pending: {stats['total_pending']}")
    avg_score = stats['avg_score'] or 0.0
    print(f"  Average score: {avg_score:.3f}")
    print(f"  High priority (>1.0): {stats['high_priority']}")
    print(f"  Medium priority (0.5-1.0): {stats['medium_priority']}")
    print(f"  Low priority (<0.5): {stats['low_priority']}")
    
    # Show top prioritized URLs
    next_batch = prioritizer.get_next_batch_prioritized(batch_size=5)
    print(f"\n🔥 Top 5 Prioritized URLs:")
    for i, url_data in enumerate(next_batch, 1):
        print(f"  {i}. {url_data['url'][:60]}...")
        print(f"     Score: {url_data['priority_score']:.3f} | Source: {url_data['source']} | Category: {url_data['category']}")