"""
Enhanced Storage Layer for IntelForge Content Enrichment

Provides advanced storage and retrieval capabilities for enriched content:
- Qdrant vector database integration
- Metadata-based filtering and search
- Crawler integration for automatic enrichment
- Backup and recovery systems

Main Components:
- EnrichedContentStorage: Vector storage with metadata filtering
- CrawlerEnrichmentIntegration: Seamless crawler integration

Usage:
    from crawl_ops.enhanced_storage import EnrichedContentStorage, CrawlerEnrichmentIntegration

    storage = EnrichedContentStorage()
    integration = CrawlerEnrichmentIntegration()
"""

from .enriched_storage import EnrichedContentStorage
from .crawler_integration import CrawlerEnrichmentIntegration

__version__ = "1.0.0"
__author__ = "IntelForge Development Team"

__all__ = [
    'EnrichedContentStorage',
    'CrawlerEnrichmentIntegration'
]
