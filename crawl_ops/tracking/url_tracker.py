"""
Core URL tracking system for IntelForge crawling operations.
Prevents redundant crawling and tracks content changes.
"""

import sqlite3
import hashlib
import orjson as json
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class URLTracker:
    """
    SQLite-based URL tracking system for preventing redundant crawls
    and detecting content changes.
    """

    def __init__(self, db_path: str = "crawl_ops/tracking/url_tracker.db"):
        """
        Initialize URL tracker with SQLite database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self._create_tables()

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

    def _create_tables(self):
        """Create database tables with proper schema."""
        conn = self._get_connection()

        # Main tracking table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scraped_urls (
                url TEXT PRIMARY KEY,
                content_hash TEXT NOT NULL,
                content_length INTEGER,
                last_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                first_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scrape_count INTEGER DEFAULT 1,
                site TEXT,
                extraction_method TEXT,
                status TEXT DEFAULT 'success',
                quality_score INTEGER,
                tags TEXT,
                etag TEXT,
                last_modified TEXT,
                response_code INTEGER DEFAULT 200
            )
        """)

        # Indexes for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_site ON scraped_urls(site)",
            "CREATE INDEX IF NOT EXISTS idx_last_scraped ON scraped_urls(last_scraped)",
            "CREATE INDEX IF NOT EXISTS idx_content_hash ON scraped_urls(content_hash)",
            "CREATE INDEX IF NOT EXISTS idx_status ON scraped_urls(status)",
            "CREATE INDEX IF NOT EXISTS idx_scrape_count ON scraped_urls(scrape_count)"
        ]

        for index_sql in indexes:
            conn.execute(index_sql)

        conn.commit()

    def should_crawl(self,
                    url: str,
                    force_refresh_days: int = 30,
                    site_specific_policies: Dict[str, int] = None) -> Tuple[bool, str]:
        """
        Determine if URL should be crawled based on tracking history.

        Args:
            url: URL to check
            force_refresh_days: Default days before forcing refresh
            site_specific_policies: Site-specific refresh policies

        Returns:
            Tuple of (should_crawl: bool, reason: str)
        """
        try:
            record = self.get_url_record(url)

            if not record:
                return True, "new_url"

            # Extract site from URL for policy lookup
            site = self._extract_site(url)
            refresh_days = force_refresh_days

            if site_specific_policies and site in site_specific_policies:
                refresh_days = site_specific_policies[site]

            # Check if content should be refreshed
            last_scraped = datetime.fromisoformat(record['last_scraped'])
            days_since = (datetime.now() - last_scraped).days

            if days_since >= refresh_days:
                return True, "refresh_due"

            # Check if previous crawl failed
            if record['status'] == 'failed':
                # Exponential backoff for failed URLs
                failed_attempts = record['scrape_count'] if record['scrape_count'] > 1 else 1
                backoff_days = min(failed_attempts ** 2, 7)  # Max 7 days

                if days_since >= backoff_days:
                    return True, "retry_failed"

            return False, "recently_scraped"

        except Exception as e:
            logger.error(f"Error checking URL {url}: {e}")
            return True, "error_default_crawl"

    def record_crawl(self,
                    url: str,
                    content_hash: str,
                    content_length: int,
                    site: str,
                    extraction_method: str,
                    status: str = 'success',
                    quality_score: Optional[int] = None,
                    tags: Optional[list] = None,
                    etag: Optional[str] = None,
                    last_modified: Optional[str] = None,
                    response_code: int = 200) -> bool:
        """
        Record successful or failed crawl attempt.

        Args:
            url: Crawled URL
            content_hash: SHA-256 hash of content
            content_length: Content length in bytes
            site: Source site domain
            extraction_method: Method used for extraction
            status: Crawl status ('success', 'failed', 'partial')
            quality_score: Content quality score (0-100)
            tags: List of content tags
            etag: HTTP ETag header
            last_modified: HTTP Last-Modified header
            response_code: HTTP response code

        Returns:
            True if recorded successfully
        """
        try:
            conn = self._get_connection()
            now = datetime.now().isoformat()

            # Check if URL already exists
            existing = self.get_url_record(url)

            if existing:
                # Update existing record
                conn.execute("""
                    UPDATE scraped_urls SET
                        content_hash = ?,
                        content_length = ?,
                        last_scraped = ?,
                        scrape_count = scrape_count + 1,
                        site = ?,
                        extraction_method = ?,
                        status = ?,
                        quality_score = ?,
                        tags = ?,
                        etag = ?,
                        last_modified = ?,
                        response_code = ?
                    WHERE url = ?
                """, (
                    content_hash, content_length, now, site, extraction_method,
                    status, quality_score, json.dumps(tags) if tags else None,
                    etag, last_modified, response_code, url
                ))
            else:
                # Insert new record
                conn.execute("""
                    INSERT INTO scraped_urls (
                        url, content_hash, content_length, last_scraped,
                        first_scraped, scrape_count, site, extraction_method,
                        status, quality_score, tags, etag, last_modified,
                        response_code
                    ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    url, content_hash, content_length, now, now, site,
                    extraction_method, status, quality_score,
                    json.dumps(tags) if tags else None, etag, last_modified,
                    response_code
                ))

            conn.commit()
            return True

        except Exception as e:
            logger.error(f"Error recording crawl for {url}: {e}")
            return False

    def detect_content_change(self, url: str, new_content_hash: str) -> bool:
        """
        Detect if content has changed since last crawl.

        Args:
            url: URL to check
            new_content_hash: New content hash to compare

        Returns:
            True if content has changed
        """
        try:
            record = self.get_url_record(url)

            if not record:
                return True  # New URL, content is "changed"

            return record['content_hash'] != new_content_hash

        except Exception as e:
            logger.error(f"Error detecting content change for {url}: {e}")
            return True  # Default to changed on error

    def get_url_record(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get tracking record for a URL.

        Args:
            url: URL to lookup

        Returns:
            Dictionary with URL record or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.execute(
                "SELECT * FROM scraped_urls WHERE url = ?", (url,)
            )
            row = cursor.fetchone()

            if row:
                record = dict(row)
                # Parse JSON fields
                if record['tags']:
                    record['tags'] = json.loads(record['tags'])
                return record

            return None

        except Exception as e:
            logger.error(f"Error getting URL record for {url}: {e}")
            return None

    def get_site_stats(self, site: str = None) -> Dict[str, Any]:
        """
        Get statistics for a specific site or all sites.

        Args:
            site: Site domain to get stats for, or None for all sites

        Returns:
            Dictionary with statistics
        """
        try:
            conn = self._get_connection()

            if site:
                cursor = conn.execute("""
                    SELECT
                        site,
                        COUNT(*) as total_urls,
                        SUM(scrape_count) as total_crawls,
                        AVG(scrape_count) as avg_crawls_per_url,
                        COUNT(*) * 1.0 / SUM(scrape_count) as efficiency_ratio,
                        MAX(last_scraped) as last_activity,
                        AVG(quality_score) as avg_quality,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
                    FROM scraped_urls
                    WHERE site = ?
                    GROUP BY site
                """, (site,))
            else:
                cursor = conn.execute("""
                    SELECT
                        site,
                        COUNT(*) as total_urls,
                        SUM(scrape_count) as total_crawls,
                        AVG(scrape_count) as avg_crawls_per_url,
                        COUNT(*) * 1.0 / SUM(scrape_count) as efficiency_ratio,
                        MAX(last_scraped) as last_activity,
                        AVG(quality_score) as avg_quality,
                        COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
                    FROM scraped_urls
                    GROUP BY site
                    ORDER BY total_urls DESC
                """)

            results = [dict(row) for row in cursor.fetchall()]

            if site and results:
                return results[0]
            elif site:
                return {}
            else:
                return {'sites': results}

        except Exception as e:
            logger.error(f"Error getting site stats: {e}")
            return {}

    def get_frequently_changing_urls(self, limit: int = 20) -> list:
        """
        Get URLs that change frequently.

        Args:
            limit: Maximum number of URLs to return

        Returns:
            List of URL records sorted by change frequency
        """
        try:
            conn = self._get_connection()
            cursor = conn.execute("""
                SELECT
                    url,
                    site,
                    scrape_count,
                    (julianday('now') - julianday(first_scraped)) / scrape_count as days_per_change,
                    last_scraped,
                    quality_score
                FROM scraped_urls
                WHERE scrape_count > 1
                ORDER BY days_per_change ASC
                LIMIT ?
            """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error getting frequently changing URLs: {e}")
            return []

    def cleanup_old_records(self, days_old: int = 365) -> int:
        """
        Remove old URL records to prevent database bloat.

        Args:
            days_old: Remove records older than this many days

        Returns:
            Number of records removed
        """
        try:
            conn = self._get_connection()
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()

            cursor = conn.execute("""
                DELETE FROM scraped_urls
                WHERE last_scraped < ? AND status = 'failed'
            """, (cutoff_date,))

            removed_count = cursor.rowcount
            conn.commit()

            logger.info(f"Cleaned up {removed_count} old URL records")
            return removed_count

        except Exception as e:
            logger.error(f"Error cleaning up old records: {e}")
            return 0

    def _extract_site(self, url: str) -> str:
        """Extract site domain from URL."""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "unknown"

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
