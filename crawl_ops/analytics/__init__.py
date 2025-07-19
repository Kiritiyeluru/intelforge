"""
Analytics Dashboard for IntelForge Content Enrichment

Provides comprehensive analytics and insights on enriched content:
- Quality distribution analysis
- Topic coverage mapping
- Strategy mining and pattern recognition
- Source performance metrics
- Trend analysis and visualizations

Main Components:
- ContentAnalytics: Comprehensive analytics engine

Usage:
    from crawl_ops.analytics import ContentAnalytics

    analytics = ContentAnalytics()
    dashboard = analytics.generate_comprehensive_dashboard(data)
"""

from .content_analytics import ContentAnalytics

__version__ = "1.0.0"
__author__ = "IntelForge Development Team"

__all__ = [
    'ContentAnalytics'
]
