#!/usr/bin/env python3
"""
Enhanced URL Quality Scoring for IntelForge
Integrates with existing tool-first content scoring pipeline for comprehensive quality assessment.
"""

from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from crawl_ops.enrichment.tool_first_content_scorer import ToolFirstContentScorer
    CONTENT_SCORER_AVAILABLE = True
except ImportError:
    CONTENT_SCORER_AVAILABLE = False
    print("Warning: Content scorer not available, using basic scoring")


class EnhancedQualityScorer:
    """Enhanced URL quality scoring with domain intelligence and content signals."""

    def __init__(self):
        """Initialize quality scorer with domain and keyword mappings."""
        self.content_scorer = ToolFirstContentScorer() if CONTENT_SCORER_AVAILABLE else None

        # Domain quality mapping based on authority and content quality
        self.quality_domains = {
            # High authority educational sources
            'quantstart.com': 0.9,
            'blog.quantinsti.com': 0.85,
            'arxiv.org': 0.9,
            'papers.ssrn.com': 0.85,

            # Established financial media
            'investopedia.com': 0.8,
            'seekingalpha.com': 0.75,
            'morningstar.com': 0.8,
            'bloomberg.com': 0.85,

            # Technical/code repositories
            'github.com': 0.7,
            'kaggle.com': 0.75,
            'pypi.org': 0.7,

            # Financial data providers
            'yahoo.com': 0.6,
            'marketwatch.com': 0.65,
            'cnbc.com': 0.7,

            # Academic institutions
            'edu': 0.85,  # Any .edu domain
            'ac.uk': 0.85,  # UK academic
            'mit.edu': 0.9,
            'stanford.edu': 0.9
        }

        # Path keyword quality signals
        self.path_keywords = {
            # High-value content types
            'tutorial': 0.15,
            'guide': 0.15,
            'strategy': 0.2,
            'backtest': 0.2,
            'algorithm': 0.18,

            # Research and analysis
            'research': 0.15,
            'analysis': 0.12,
            'paper': 0.15,
            'study': 0.12,

            # Technical content
            'python': 0.1,
            'code': 0.08,
            'implementation': 0.12,
            'model': 0.1,

            # Educational content
            'course': 0.1,
            'lesson': 0.08,
            'learn': 0.08,
            'education': 0.08,

            # Trading/finance specific
            'trading': 0.12,
            'finance': 0.1,
            'investment': 0.1,
            'portfolio': 0.12,
            'quantitative': 0.15,
            'quant': 0.15
        }

        # Content quality modifiers
        self.negative_signals = {
            'advertisement': -0.3,
            'ads': -0.2,
            'sponsored': -0.2,
            'affiliate': -0.15,
            'promo': -0.1,
            'discount': -0.1,
            'sale': -0.1
        }

        # File type quality mapping
        self.file_type_quality = {
            '.pdf': 0.15,  # PDFs often contain research papers
            '.ipynb': 0.2,  # Jupyter notebooks are high-value
            '.py': 0.12,   # Python code files
            '.md': 0.08,   # Documentation
            '.html': 0.0,  # Neutral
            '.htm': 0.0,   # Neutral
        }

    def enhance_url_quality_scoring(self, urls: List[Dict]) -> List[Dict]:
        """Enhance URL quality estimates based on comprehensive scoring."""
        enhanced_urls = []

        for url_data in urls:
            enhanced_url = url_data.copy()
            enhanced_url['quality_estimate'] = self._calculate_comprehensive_quality(url_data)
            enhanced_url['quality_breakdown'] = self._get_quality_breakdown(url_data)
            enhanced_urls.append(enhanced_url)

        return enhanced_urls

    def _calculate_comprehensive_quality(self, url_data: Dict) -> float:
        """Calculate comprehensive quality score from multiple signals."""
        url = url_data['url']
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        # Start with base quality
        base_quality = url_data.get('quality_estimate', 0.5)

        # Domain authority boost
        domain_quality = self._get_domain_quality(domain)

        # Path keyword signals
        keyword_boost = self._calculate_keyword_boost(path)

        # File type bonus
        file_type_bonus = self._get_file_type_bonus(path)

        # Negative signal penalties
        penalty = self._calculate_penalties(url, path)

        # Source-specific adjustments
        source_adjustment = self._get_source_adjustment(url_data.get('source', ''))

        # Combine all factors
        final_quality = (
            base_quality * 0.3 +          # 30% base quality
            domain_quality * 0.4 +        # 40% domain authority
            keyword_boost * 0.2 +         # 20% keyword signals
            file_type_bonus * 0.05 +      # 5% file type
            source_adjustment * 0.05      # 5% source quality
        ) + penalty  # Subtract penalties

        return max(0.0, min(final_quality, 1.0))  # Clamp to [0, 1]

    def _get_domain_quality(self, domain: str) -> float:
        """Get quality score based on domain authority."""
        # Check exact domain matches
        if domain in self.quality_domains:
            return self.quality_domains[domain]

        # Check domain suffixes for academic institutions
        if domain.endswith('.edu'):
            return self.quality_domains['edu']
        elif domain.endswith('.ac.uk'):
            return self.quality_domains['ac.uk']

        # Check for subdomain patterns
        for quality_domain, score in self.quality_domains.items():
            if domain.endswith(f'.{quality_domain}'):
                return score * 0.9  # Slightly lower for subdomains

        # Default quality for unknown domains
        return 0.5

    def _calculate_keyword_boost(self, path: str) -> float:
        """Calculate quality boost from path keywords."""
        total_boost = 0.0

        for keyword, boost in self.path_keywords.items():
            if keyword in path:
                total_boost += boost

        # Cap maximum boost to prevent over-inflation
        return min(total_boost, 0.4)

    def _get_file_type_bonus(self, path: str) -> float:
        """Get quality bonus based on file type."""
        for file_ext, bonus in self.file_type_quality.items():
            if path.endswith(file_ext):
                return bonus
        return 0.0

    def _calculate_penalties(self, url: str, path: str) -> float:
        """Calculate quality penalties for negative signals."""
        penalty = 0.0
        content = (url + " " + path).lower()

        for negative_term, penalty_value in self.negative_signals.items():
            if negative_term in content:
                penalty += penalty_value

        # Cap maximum penalty
        return max(penalty, -0.5)

    def _get_source_adjustment(self, source: str) -> float:
        """Get quality adjustment based on discovery source."""
        source_quality = {
            'manual': 0.8,           # Manually curated URLs are high quality
            'github_api': 0.7,       # GitHub repos have decent quality
            'sitemap': 0.6,          # Sitemap URLs are structured
            'rss': 0.65,            # RSS feeds are curated content
            'google_search': 0.5,    # Search results are mixed quality
            'bing_search': 0.45,     # Bing results might be lower quality
            'github_discovery': 0.6  # Simulated GitHub discovery
        }

        return source_quality.get(source, 0.5)

    def _get_quality_breakdown(self, url_data: Dict) -> Dict[str, float]:
        """Get detailed breakdown of quality scoring factors."""
        url = url_data['url']
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        return {
            'base_quality': url_data.get('quality_estimate', 0.5),
            'domain_quality': self._get_domain_quality(domain),
            'keyword_boost': self._calculate_keyword_boost(path),
            'file_type_bonus': self._get_file_type_bonus(path),
            'penalties': self._calculate_penalties(url, path),
            'source_adjustment': self._get_source_adjustment(url_data.get('source', ''))
        }

    def score_content_quality(self, content: str, url: str) -> Dict[str, Any]:
        """Score content quality using tool-first content scorer if available."""
        if not self.content_scorer:
            return {'content_score': 0.5, 'method': 'fallback'}

        try:
            # Use existing tool-first content scorer
            scores = self.content_scorer.score_content(content)
            return {
                'content_score': scores.get('overall_score', 0.5),
                'readability_score': scores.get('readability_score', 0.5),
                'keyword_density': scores.get('keyword_density', 0.0),
                'method': 'tool_first_scorer'
            }
        except Exception as e:
            print(f"Content scoring failed for {url}: {e}")
            return {'content_score': 0.5, 'method': 'error_fallback'}

    def get_quality_insights(self, url_data: Dict) -> Dict[str, Any]:
        """Get human-readable quality insights for a URL."""
        quality_score = url_data.get('quality_estimate', 0.5)
        breakdown = url_data.get('quality_breakdown', {})

        # Quality tier classification
        if quality_score >= 0.8:
            tier = "Premium"
        elif quality_score >= 0.65:
            tier = "High"
        elif quality_score >= 0.5:
            tier = "Medium"
        elif quality_score >= 0.35:
            tier = "Low"
        else:
            tier = "Poor"

        # Key quality factors
        factors = []
        if breakdown.get('domain_quality', 0) > 0.7:
            factors.append("Authoritative domain")
        if breakdown.get('keyword_boost', 0) > 0.1:
            factors.append("Relevant keywords")
        if breakdown.get('file_type_bonus', 0) > 0:
            factors.append("Valuable file type")
        if breakdown.get('penalties', 0) < -0.1:
            factors.append("Commercial content detected")

        return {
            'quality_tier': tier,
            'quality_score': quality_score,
            'key_factors': factors,
            'recommendation': self._get_crawling_recommendation(quality_score)
        }

    def _get_crawling_recommendation(self, quality_score: float) -> str:
        """Get crawling priority recommendation based on quality score."""
        if quality_score >= 0.8:
            return "High priority - crawl immediately"
        elif quality_score >= 0.65:
            return "Medium priority - crawl within 24 hours"
        elif quality_score >= 0.5:
            return "Standard priority - crawl within week"
        elif quality_score >= 0.35:
            return "Low priority - crawl when resources available"
        else:
            return "Consider skipping - poor quality signals"


if __name__ == "__main__":
    # Test the enhanced quality scorer
    scorer = EnhancedQualityScorer()

    test_urls = [
        {
            'url': 'https://quantstart.com/articles/algorithmic-trading-python-tutorial',
            'source': 'manual',
            'quality_estimate': 0.6
        },
        {
            'url': 'https://github.com/quantopian/zipline/blob/master/backtest.py',
            'source': 'github_api',
            'quality_estimate': 0.7
        },
        {
            'url': 'https://arxiv.org/pdf/2103.12345.pdf',
            'source': 'manual',
            'quality_estimate': 0.5
        }
    ]

    enhanced_urls = scorer.enhance_url_quality_scoring(test_urls)

    for url_data in enhanced_urls:
        insights = scorer.get_quality_insights(url_data)
        print(f"\n{url_data['url']}")
        print(f"Quality: {insights['quality_score']:.3f} ({insights['quality_tier']})")
        print(f"Recommendation: {insights['recommendation']}")
        print(f"Factors: {', '.join(insights['key_factors']) if insights['key_factors'] else 'None'}")
