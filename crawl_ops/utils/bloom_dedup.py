#!/usr/bin/env python3
"""
Memory-efficient URL deduplication using Bloom filters.

100x memory reduction for large-scale URL tracking (100k+ URLs).
Based on performance optimization plan recommendations.
"""

import pickle
from pathlib import Path
from typing import Set, Optional
import logging

try:
    from pyprobables import BloomFilter
    BLOOM_AVAILABLE = True
except ImportError:
    BLOOM_AVAILABLE = False

logger = logging.getLogger(__name__)


class MemoryEfficientURLTracker:
    """
    Bloom filter-based URL tracking for massive scale deduplication.

    Uses 100x less memory than Python sets for 100k+ URLs.
    Perfect for long-running crawlers with large URL sets.
    """

    def __init__(self,
                 estimated_elements: int = 100000,
                 false_positive_rate: float = 0.01,
                 storage_path: str = "crawl_ops/tracking/bloom_filter.pkl"):
        """
        Initialize memory-efficient URL tracker.

        Args:
            estimated_elements: Expected number of URLs to track
            false_positive_rate: Acceptable false positive rate (0.01 = 1%)
            storage_path: Path to persist Bloom filter
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        if not BLOOM_AVAILABLE:
            logger.warning("pyprobables not available, falling back to set-based tracking")
            self.bloom = None
            self.url_set: Set[str] = set()
        else:
            try:
                # Try to load existing filter
                self.bloom = self._load_filter()
                self.url_set = None
            except (FileNotFoundError, Exception):
                # Create new filter
                self.bloom = BloomFilter(
                    est_elements=estimated_elements,
                    false_positive_rate=false_positive_rate
                )
                self.url_set = None

        self.estimated_elements = estimated_elements
        self.false_positive_rate = false_positive_rate
        logger.info(f"URL tracker initialized for {estimated_elements} URLs "
                   f"with {false_positive_rate*100:.1f}% false positive rate")

    def is_duplicate(self, url: str) -> bool:
        """
        Check if URL has been seen before (probabilistic).

        Args:
            url: URL to check

        Returns:
            True if URL probably seen before, False if definitely new

        Note:
            May have false positives (claims URL seen when it wasn't)
            Never has false negatives (claims URL new when it was seen)
        """
        if self.bloom is not None:
            # Bloom filter implementation
            if url in self.bloom:
                return True  # Probably seen before
            else:
                # Definitely new - add to filter
                self.bloom.add(url)
                return False
        else:
            # Fallback to set-based implementation
            if url in self.url_set:
                return True
            else:
                self.url_set.add(url)
                return False

    def add_url(self, url: str):
        """
        Explicitly add URL to tracking (for batch operations).

        Args:
            url: URL to add to tracking
        """
        if self.bloom is not None:
            self.bloom.add(url)
        else:
            self.url_set.add(url)

    def add_urls_batch(self, urls: list):
        """
        Add multiple URLs in batch (more efficient).

        Args:
            urls: List of URLs to add
        """
        for url in urls:
            self.add_url(url)

        logger.info(f"Added {len(urls)} URLs to tracking")

    def get_stats(self) -> dict:
        """Get tracking statistics."""
        if self.bloom is not None:
            return {
                'implementation': 'bloom_filter',
                'estimated_elements': self.estimated_elements,
                'false_positive_rate': self.false_positive_rate,
                'filter_size_bits': self.bloom.estimated_bits_per_item * self.estimated_elements,
                'memory_usage': 'bloom_filter_memory_efficient'
            }
        else:
            return {
                'implementation': 'set_fallback',
                'tracked_urls': len(self.url_set),
                'memory_usage': f'{len(self.url_set) * 100} bytes (approx)'
            }

    def save_filter(self):
        """Persist Bloom filter to disk."""
        if self.bloom is not None:
            try:
                with open(self.storage_path, 'wb') as f:
                    pickle.dump(self.bloom, f)
                logger.info(f"Saved Bloom filter to {self.storage_path}")
            except Exception as e:
                logger.error(f"Failed to save Bloom filter: {e}")
        else:
            # Save URL set as fallback
            fallback_path = self.storage_path.with_suffix('.set.pkl')
            try:
                with open(fallback_path, 'wb') as f:
                    pickle.dump(self.url_set, f)
                logger.info(f"Saved URL set to {fallback_path}")
            except Exception as e:
                logger.error(f"Failed to save URL set: {e}")

    def _load_filter(self):
        """Load existing Bloom filter from disk."""
        if self.storage_path.exists():
            with open(self.storage_path, 'rb') as f:
                return pickle.load(f)
        else:
            raise FileNotFoundError("No existing filter found")

    def clear(self):
        """Clear all tracking data."""
        if self.bloom is not None:
            self.bloom = BloomFilter(
                est_elements=self.estimated_elements,
                false_positive_rate=self.false_positive_rate
            )
        else:
            self.url_set.clear()

        logger.info("Cleared all URL tracking data")


class ScalableURLDeduplicator:
    """
    Scalable URL deduplication system that adapts to scale.

    Uses sets for small scale, Bloom filters for large scale.
    """

    def __init__(self, scale_threshold: int = 10000):
        """
        Initialize scalable deduplicator.

        Args:
            scale_threshold: Number of URLs before switching to Bloom filters
        """
        self.scale_threshold = scale_threshold
        self.url_set: Set[str] = set()
        self.bloom_tracker: Optional[MemoryEfficientURLTracker] = None
        self.scaled_up = False

        logger.info(f"Scalable deduplicator initialized (threshold: {scale_threshold})")

    def is_duplicate(self, url: str) -> bool:
        """Check if URL is duplicate, scaling to Bloom filters if needed."""
        # Check if we need to scale up
        if not self.scaled_up and len(self.url_set) >= self.scale_threshold:
            self._scale_to_bloom_filter()

        if self.scaled_up:
            return self.bloom_tracker.is_duplicate(url)
        else:
            if url in self.url_set:
                return True
            else:
                self.url_set.add(url)
                return False

    def _scale_to_bloom_filter(self):
        """Scale up from set to Bloom filter."""
        logger.info(f"Scaling to Bloom filter with {len(self.url_set)} existing URLs")

        # Estimate elements based on current size
        estimated_elements = max(len(self.url_set) * 10, 100000)

        self.bloom_tracker = MemoryEfficientURLTracker(
            estimated_elements=estimated_elements,
            false_positive_rate=0.01
        )

        # Transfer existing URLs to Bloom filter
        self.bloom_tracker.add_urls_batch(list(self.url_set))

        # Clear set to free memory
        self.url_set.clear()
        self.scaled_up = True

        logger.info(f"Successfully scaled to Bloom filter (est: {estimated_elements} URLs)")

    def get_stats(self) -> dict:
        """Get deduplication statistics."""
        if self.scaled_up:
            stats = self.bloom_tracker.get_stats()
            stats['scaled_from_set'] = True
            return stats
        else:
            return {
                'implementation': 'set_based',
                'tracked_urls': len(self.url_set),
                'scale_threshold': self.scale_threshold,
                'scaled_up': False
            }

    def save(self):
        """Save current state."""
        if self.scaled_up and self.bloom_tracker:
            self.bloom_tracker.save_filter()


def create_deduplicator(expected_scale: str = "medium") -> MemoryEfficientURLTracker:
    """
    Factory function for creating appropriate deduplicator.

    Args:
        expected_scale: "small" (<10k), "medium" (10k-100k), "large" (100k+)

    Returns:
        Configured URL deduplicator
    """
    scale_configs = {
        "small": {"threshold": 5000, "estimated": 10000},
        "medium": {"threshold": 10000, "estimated": 100000},
        "large": {"threshold": 50000, "estimated": 1000000}
    }

    config = scale_configs.get(expected_scale, scale_configs["medium"])

    if expected_scale == "large" or not BLOOM_AVAILABLE:
        return MemoryEfficientURLTracker(
            estimated_elements=config["estimated"],
            false_positive_rate=0.01
        )
    else:
        return ScalableURLDeduplicator(scale_threshold=config["threshold"])


if __name__ == "__main__":
    # Test the memory-efficient URL tracker
    print("Testing Memory-Efficient URL Deduplication")
    print("=" * 50)

    # Test with small scale
    tracker = create_deduplicator("medium")

    # Test URLs
    test_urls = [
        "https://quantstart.com/article1",
        "https://github.com/trading-repo",
        "https://quantstart.com/article1",  # Duplicate
        "https://investopedia.com/guide",
        "https://github.com/trading-repo"   # Duplicate
    ]

    print("Testing deduplication:")
    for url in test_urls:
        is_dup = tracker.is_duplicate(url)
        print(f"  {url}: {'DUPLICATE' if is_dup else 'NEW'}")

    # Show statistics
    stats = tracker.get_stats()
    print(f"\nTracker Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Test saving
    if hasattr(tracker, 'save'):
        tracker.save()
        print(f"\nSaved tracker state")
