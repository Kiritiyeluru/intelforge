"""
IntelForge Content Enrichment Pipeline

This module provides comprehensive content enrichment capabilities for scraped data:

1. Content Scoring - Quality assessment using heuristic and AI methods
2. Auto-Tagging - Automated categorization and tagging
3. Strategy Extraction - Trading strategy keyword and pattern extraction  
4. Enhanced Storage - Structured data schemas and validation

Main Components:
- EnrichmentPipeline: Main orchestrator for all enrichment processes
- ContentScorer: Content quality scoring system
- AutoTagger: Automated content tagging
- StrategyExtractor: Strategy keyword extraction
- SchemaValidator: Data validation and transformation

Usage:
    from crawl_ops.enrichment import EnrichmentPipeline
    
    pipeline = EnrichmentPipeline()
    enriched_data = pipeline.enrich_scraped_data('input.jsonl', 'output.jsonl')
"""

from .enrichment_pipeline import EnrichmentPipeline
from .content_scorer import ContentScorer
from .auto_tagger import AutoTagger
from .strategy_extractor import StrategyExtractor
from .schemas import (
    EnrichedContent, 
    SchemaValidator, 
    SchemaTransformer,
    SchemaUpgrader,
    create_sample_enriched_content
)

__version__ = "1.0.0"
__author__ = "IntelForge Development Team"

__all__ = [
    'EnrichmentPipeline',
    'ContentScorer', 
    'AutoTagger',
    'StrategyExtractor',
    'EnrichedContent',
    'SchemaValidator',
    'SchemaTransformer', 
    'SchemaUpgrader',
    'create_sample_enriched_content'
]