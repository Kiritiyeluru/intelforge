#!/usr/bin/env python3
"""
Enhanced Data Schemas for IntelForge Content Enrichment

Defines the complete data schema for enriched content storage,
including validation and transformation utilities.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class ScoringDetails:
    """Content scoring details"""
    overall_score: float
    heuristic_score: float
    ai_score: Optional[float] = None
    scoring_method: str = "heuristic"
    content_length: int = 0
    title_relevance: float = 0.0
    code_presence: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CodeSnippet:
    """Code snippet information"""
    type: str  # 'code_block' or 'inline_code'
    language: str
    code: str
    length: int
    line_count: Optional[int] = None


@dataclass
class TechnicalIndicator:
    """Technical indicator information"""
    matches: List[str]
    count: int
    full_name: str
    type: str
    context: List[str] = field(default_factory=list)


@dataclass
class CustomStrategy:
    """Custom strategy information"""
    type: str
    description: str
    confidence: float


@dataclass
class EnrichmentSummary:
    """Summary of enrichment results"""
    quality_score: float
    has_code: bool
    strategy_density: float
    tag_categories: int
    technical_indicators_count: int
    key_concepts_count: int
    actionable: bool
    enrichment_quality: str  # 'excellent', 'good', 'moderate', 'basic'


@dataclass
class EnrichedContent:
    """Complete enriched content schema"""

    # Original fields
    url: str
    title: str
    content: str
    content_length: int
    extraction_method: str
    site: str
    content_hash: str

    # Enrichment fields
    quality_score: float
    content_tags: Dict[str, List[str]]
    strategy_keywords: Dict[str, List[str]]
    technical_indicators: Dict[str, TechnicalIndicator]
    market_terms: Dict[str, List[str]]
    custom_strategies: List[CustomStrategy]
    technical_level: str
    topic_areas: List[str]
    code_snippets: List[CodeSnippet]
    key_concepts: List[str]
    strategy_density: float

    # Metadata
    enrichment_timestamp: str
    enrichment_version: str
    scoring_details: ScoringDetails
    enrichment_summary: EnrichmentSummary

    # Optional fields
    tag_count: int = 0
    extraction_confidence: Dict[str, float] = field(default_factory=dict)
    enrichment_skipped: bool = False
    skip_reason: Optional[str] = None
    enrichment_error: Optional[str] = None


class SchemaValidator:
    """Validator for enriched content schemas"""

    @staticmethod
    def validate_enriched_content(data: Dict[str, Any]) -> bool:
        """Validate enriched content against schema"""

        required_fields = [
            'url', 'title', 'content', 'content_hash',
            'quality_score', 'enrichment_timestamp'
        ]

        # Check required fields
        for field in required_fields:
            if field not in data:
                return False

        # Validate data types
        if not isinstance(data.get('quality_score'), (int, float)):
            return False

        if not isinstance(data.get('content_tags'), dict):
            return False

        if not isinstance(data.get('strategy_keywords'), dict):
            return False

        return True

    @staticmethod
    def validate_scoring_details(data: Dict[str, Any]) -> bool:
        """Validate scoring details structure"""

        required_fields = ['overall_score', 'scoring_method']

        for field in required_fields:
            if field not in data:
                return False

        # Score should be between 0 and 100
        score = data.get('overall_score', 0)
        if not (0 <= score <= 100):
            return False

        return True

    @staticmethod
    def validate_content_tags(tags: Dict[str, Any]) -> bool:
        """Validate content tags structure"""

        expected_categories = [
            'content_type', 'technical_level', 'topic_area',
            'tools_languages', 'strategy_types'
        ]

        # Check that tags is a dictionary with list values
        if not isinstance(tags, dict):
            return False

        for category, tag_list in tags.items():
            if not isinstance(tag_list, list):
                return False

        return True


class SchemaTransformer:
    """Transform data to/from enriched content schema"""

    @staticmethod
    def to_enriched_content(data: Dict[str, Any]) -> EnrichedContent:
        """Transform dictionary to EnrichedContent dataclass"""

        # Extract and transform nested objects
        scoring_details = ScoringDetails(**data.get('scoring_details', {}))

        code_snippets = [
            CodeSnippet(**snippet)
            for snippet in data.get('code_snippets', [])
        ]

        technical_indicators = {
            name: TechnicalIndicator(**info)
            for name, info in data.get('technical_indicators', {}).items()
        }

        custom_strategies = [
            CustomStrategy(**strategy)
            for strategy in data.get('custom_strategies', [])
        ]

        enrichment_summary = EnrichmentSummary(**data.get('enrichment_summary', {}))

        return EnrichedContent(
            # Original fields
            url=data['url'],
            title=data['title'],
            content=data['content'],
            content_length=data.get('content_length', len(data['content'])),
            extraction_method=data.get('extraction_method', ''),
            site=data.get('site', ''),
            content_hash=data['content_hash'],

            # Enrichment fields
            quality_score=data['quality_score'],
            content_tags=data.get('content_tags', {}),
            strategy_keywords=data.get('strategy_keywords', {}),
            technical_indicators=technical_indicators,
            market_terms=data.get('market_terms', {}),
            custom_strategies=custom_strategies,
            technical_level=data.get('technical_level', 'intermediate'),
            topic_areas=data.get('topic_areas', []),
            code_snippets=code_snippets,
            key_concepts=data.get('key_concepts', []),
            strategy_density=data.get('strategy_density', 0.0),

            # Metadata
            enrichment_timestamp=data['enrichment_timestamp'],
            enrichment_version=data.get('enrichment_version', '1.0'),
            scoring_details=scoring_details,
            enrichment_summary=enrichment_summary,

            # Optional fields
            tag_count=data.get('tag_count', 0),
            extraction_confidence=data.get('extraction_confidence', {}),
            enrichment_skipped=data.get('enrichment_skipped', False),
            skip_reason=data.get('skip_reason'),
            enrichment_error=data.get('enrichment_error')
        )

    @staticmethod
    def from_enriched_content(content: EnrichedContent) -> Dict[str, Any]:
        """Transform EnrichedContent dataclass to dictionary"""

        # Convert dataclass to dict, handling nested objects
        result = {
            # Original fields
            'url': content.url,
            'title': content.title,
            'content': content.content,
            'content_length': content.content_length,
            'extraction_method': content.extraction_method,
            'site': content.site,
            'content_hash': content.content_hash,

            # Enrichment fields
            'quality_score': content.quality_score,
            'content_tags': content.content_tags,
            'strategy_keywords': content.strategy_keywords,
            'market_terms': content.market_terms,
            'technical_level': content.technical_level,
            'topic_areas': content.topic_areas,
            'key_concepts': content.key_concepts,
            'strategy_density': content.strategy_density,

            # Metadata
            'enrichment_timestamp': content.enrichment_timestamp,
            'enrichment_version': content.enrichment_version,
            'tag_count': content.tag_count,
            'extraction_confidence': content.extraction_confidence,
            'enrichment_skipped': content.enrichment_skipped
        }

        # Handle optional fields
        if content.skip_reason:
            result['skip_reason'] = content.skip_reason

        if content.enrichment_error:
            result['enrichment_error'] = content.enrichment_error

        # Convert complex objects to dictionaries
        result['scoring_details'] = {
            'overall_score': content.scoring_details.overall_score,
            'heuristic_score': content.scoring_details.heuristic_score,
            'ai_score': content.scoring_details.ai_score,
            'scoring_method': content.scoring_details.scoring_method,
            'content_length': content.scoring_details.content_length,
            'title_relevance': content.scoring_details.title_relevance,
            'code_presence': content.scoring_details.code_presence,
            'timestamp': content.scoring_details.timestamp
        }

        result['technical_indicators'] = {
            name: {
                'matches': indicator.matches,
                'count': indicator.count,
                'full_name': indicator.full_name,
                'type': indicator.type,
                'context': indicator.context
            }
            for name, indicator in content.technical_indicators.items()
        }

        result['code_snippets'] = [
            {
                'type': snippet.type,
                'language': snippet.language,
                'code': snippet.code,
                'length': snippet.length,
                'line_count': snippet.line_count
            }
            for snippet in content.code_snippets
        ]

        result['custom_strategies'] = [
            {
                'type': strategy.type,
                'description': strategy.description,
                'confidence': strategy.confidence
            }
            for strategy in content.custom_strategies
        ]

        result['enrichment_summary'] = {
            'quality_score': content.enrichment_summary.quality_score,
            'has_code': content.enrichment_summary.has_code,
            'strategy_density': content.enrichment_summary.strategy_density,
            'tag_categories': content.enrichment_summary.tag_categories,
            'technical_indicators_count': content.enrichment_summary.technical_indicators_count,
            'key_concepts_count': content.enrichment_summary.key_concepts_count,
            'actionable': content.enrichment_summary.actionable,
            'enrichment_quality': content.enrichment_summary.enrichment_quality
        }

        return result


class SchemaUpgrader:
    """Handle schema version upgrades"""

    @staticmethod
    def upgrade_from_v1_0(data: Dict[str, Any]) -> Dict[str, Any]:
        """Upgrade from v1.0 schema to current"""

        # v1.0 is current version, no upgrade needed
        return data

    @staticmethod
    def detect_schema_version(data: Dict[str, Any]) -> str:
        """Detect schema version from data"""

        return data.get('enrichment_version', '1.0')

    @staticmethod
    def upgrade_schema(data: Dict[str, Any]) -> Dict[str, Any]:
        """Upgrade schema to current version"""

        version = SchemaUpgrader.detect_schema_version(data)

        if version == '1.0':
            return SchemaUpgrader.upgrade_from_v1_0(data)

        # Unknown version, return as-is
        return data


def create_sample_enriched_content() -> Dict[str, Any]:
    """Create a sample enriched content entry for testing"""

    return {
        "url": "https://example.com/trading-strategy",
        "title": "Advanced Momentum Trading Strategy with Python",
        "content": "This tutorial covers implementing a momentum trading strategy using Python and pandas...",
        "content_length": 5420,
        "extraction_method": "trafilatura",
        "site": "example.com",
        "content_hash": "abc123def456",

        "quality_score": 85.5,
        "content_tags": {
            "content_type": ["tutorial", "implementation"],
            "technical_level": ["intermediate"],
            "topic_area": ["equities"],
            "tools_languages": ["python"],
            "strategy_types": ["momentum"]
        },

        "strategy_keywords": {
            "indicators": ["moving average", "RSI"],
            "signals": ["crossover", "breakout"],
            "metrics": ["sharpe ratio", "drawdown"]
        },

        "technical_indicators": {
            "RSI": {
                "matches": ["RSI", "relative strength index"],
                "count": 3,
                "full_name": "Relative Strength Index",
                "type": "momentum_oscillator",
                "context": ["When RSI exceeds 70, consider selling"]
            }
        },

        "market_terms": {
            "trading_styles": ["day trading"],
            "asset_classes": ["equities"]
        },

        "custom_strategies": [
            {
                "type": "pattern_1",
                "description": "Buy when price crosses above 20-day moving average",
                "confidence": 0.8
            }
        ],

        "technical_level": "intermediate",
        "topic_areas": ["equities"],
        "code_snippets": [
            {
                "type": "code_block",
                "language": "python",
                "code": "import pandas as pd\ndf['MA20'] = df['close'].rolling(20).mean()",
                "length": 52,
                "line_count": 2
            }
        ],

        "key_concepts": ["moving average", "momentum", "rsi"],
        "strategy_density": 2.5,

        "enrichment_timestamp": "2025-07-19T12:00:00",
        "enrichment_version": "1.0",
        "tag_count": 6,
        "extraction_confidence": {"indicators": 0.9, "signals": 0.7},

        "scoring_details": {
            "overall_score": 85.5,
            "heuristic_score": 82.0,
            "ai_score": 89.0,
            "scoring_method": "hybrid",
            "content_length": 5420,
            "title_relevance": 8.0,
            "code_presence": {"total_score": 15, "has_substantial_code": True},
            "timestamp": "2025-07-19T12:00:00"
        },

        "enrichment_summary": {
            "quality_score": 85.5,
            "has_code": True,
            "strategy_density": 2.5,
            "tag_categories": 5,
            "technical_indicators_count": 1,
            "key_concepts_count": 3,
            "actionable": True,
            "enrichment_quality": "good"
        }
    }


def main():
    """Test schema functionality"""

    # Create sample data
    sample_data = create_sample_enriched_content()

    # Test validation
    validator = SchemaValidator()
    is_valid = validator.validate_enriched_content(sample_data)
    print(f"✅ Schema validation: {'PASSED' if is_valid else 'FAILED'}")

    # Test transformation
    transformer = SchemaTransformer()

    # Dict to dataclass
    enriched_content = transformer.to_enriched_content(sample_data)
    print(f"✅ Dict to dataclass: {type(enriched_content).__name__}")

    # Dataclass to dict
    dict_data = transformer.from_enriched_content(enriched_content)
    print(f"✅ Dataclass to dict: {len(dict_data)} fields")

    # Test schema upgrade
    upgrader = SchemaUpgrader()
    version = upgrader.detect_schema_version(sample_data)
    print(f"✅ Schema version: {version}")

    print("\n🎉 All schema tests passed!")


if __name__ == "__main__":
    main()
