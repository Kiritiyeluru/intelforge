#!/usr/bin/env python3
"""
Content Analytics Dashboard for IntelForge

Provides comprehensive analytics and insights on enriched content:
- Quality Distribution Analysis
- Topic Coverage Mapping
- Strategy Type Distribution
- Source Performance Metrics
- Trend Analysis Over Time
"""

import orjson as json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️ Matplotlib/Seaborn not available, plotting disabled")

from crawl_ops.enhanced_storage.enriched_storage import EnrichedContentStorage


class ContentAnalytics:
    """Content analytics engine for enriched data"""

    def __init__(self):
        self.storage = EnrichedContentStorage()

        # Analytics configuration
        self.quality_thresholds = {
            "excellent": 90,
            "good": 75,
            "moderate": 60,
            "basic": 40
        }

        self.strategy_density_thresholds = {
            "very_high": 3.0,
            "high": 2.0,
            "moderate": 1.0,
            "low": 0.5
        }

        print("📊 Content analytics engine initialized")

    def generate_quality_distribution_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate quality distribution analysis"""

        if not data:
            return {"error": "No data available for analysis"}

        quality_scores = [entry.get('quality_score', 0) for entry in data]

        # Calculate distribution
        quality_distribution = {
            "excellent": len([s for s in quality_scores if s >= self.quality_thresholds["excellent"]]),
            "good": len([s for s in quality_scores if self.quality_thresholds["good"] <= s < self.quality_thresholds["excellent"]]),
            "moderate": len([s for s in quality_scores if self.quality_thresholds["moderate"] <= s < self.quality_thresholds["good"]]),
            "basic": len([s for s in quality_scores if self.quality_thresholds["basic"] <= s < self.quality_thresholds["moderate"]]),
            "poor": len([s for s in quality_scores if s < self.quality_thresholds["basic"]])
        }

        # Calculate statistics
        quality_stats = {
            "mean": statistics.mean(quality_scores),
            "median": statistics.median(quality_scores),
            "std_dev": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0,
            "min": min(quality_scores),
            "max": max(quality_scores),
            "total_entries": len(quality_scores)
        }

        # Quality by source analysis
        source_quality = defaultdict(list)
        for entry in data:
            site = entry.get('site', 'unknown')
            quality = entry.get('quality_score', 0)
            source_quality[site].append(quality)

        source_analysis = {}
        for site, scores in source_quality.items():
            source_analysis[site] = {
                "count": len(scores),
                "avg_quality": statistics.mean(scores),
                "max_quality": max(scores),
                "min_quality": min(scores)
            }

        return {
            "distribution": quality_distribution,
            "statistics": quality_stats,
            "source_analysis": source_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def generate_topic_coverage_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate topic coverage analysis"""

        if not data:
            return {"error": "No data available for analysis"}

        # Collect all tags and topics
        content_types = Counter()
        topic_areas = Counter()
        tools_languages = Counter()
        strategy_types = Counter()
        technical_levels = Counter()

        for entry in data:
            content_tags = entry.get('content_tags', {})

            # Count content types
            for content_type in content_tags.get('content_type', []):
                content_types[content_type] += 1

            # Count topic areas
            for topic in entry.get('topic_areas', []):
                topic_areas[topic] += 1

            # Count tools and languages
            for tool in content_tags.get('tools_languages', []):
                tools_languages[tool] += 1

            # Count strategy types
            for strategy in content_tags.get('strategy_types', []):
                strategy_types[strategy] += 1

            # Count technical levels
            level = entry.get('technical_level', 'unknown')
            technical_levels[level] += 1

        # Calculate coverage percentages
        total_entries = len(data)

        coverage_analysis = {
            "content_types": {
                "distribution": dict(content_types),
                "coverage": {ct: (count/total_entries)*100 for ct, count in content_types.items()},
                "most_common": content_types.most_common(5)
            },
            "topic_areas": {
                "distribution": dict(topic_areas),
                "coverage": {ta: (count/total_entries)*100 for ta, count in topic_areas.items()},
                "most_common": topic_areas.most_common(5)
            },
            "tools_languages": {
                "distribution": dict(tools_languages),
                "coverage": {tl: (count/total_entries)*100 for tl, count in tools_languages.items()},
                "most_common": tools_languages.most_common(5)
            },
            "strategy_types": {
                "distribution": dict(strategy_types),
                "coverage": {st: (count/total_entries)*100 for st, count in strategy_types.items()},
                "most_common": strategy_types.most_common(5)
            },
            "technical_levels": {
                "distribution": dict(technical_levels),
                "coverage": {tl: (count/total_entries)*100 for tl, count in technical_levels.items()}
            }
        }

        # Identify gaps and recommendations
        gaps_analysis = self._identify_content_gaps(coverage_analysis)

        return {
            "coverage_analysis": coverage_analysis,
            "gaps_analysis": gaps_analysis,
            "total_entries": total_entries,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def generate_strategy_mining_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate strategy mining and pattern analysis"""

        if not data:
            return {"error": "No data available for analysis"}

        # Collect strategy-related data
        strategy_densities = [entry.get('strategy_density', 0) for entry in data]
        technical_indicators = Counter()
        key_concepts = Counter()

        # Strategy density distribution
        density_distribution = {
            "very_high": len([d for d in strategy_densities if d >= self.strategy_density_thresholds["very_high"]]),
            "high": len([d for d in strategy_densities if self.strategy_density_thresholds["high"] <= d < self.strategy_density_thresholds["very_high"]]),
            "moderate": len([d for d in strategy_densities if self.strategy_density_thresholds["moderate"] <= d < self.strategy_density_thresholds["high"]]),
            "low": len([d for d in strategy_densities if self.strategy_density_thresholds["low"] <= d < self.strategy_density_thresholds["moderate"]]),
            "very_low": len([d for d in strategy_densities if d < self.strategy_density_thresholds["low"]])
        }

        # Collect indicators and concepts
        for entry in data:
            # Count technical indicators
            indicators = entry.get('technical_indicators', {})
            for indicator in indicators.keys():
                technical_indicators[indicator] += 1

            # Count key concepts
            concepts = entry.get('key_concepts', [])
            for concept in concepts:
                key_concepts[concept] += 1

        # Strategy patterns analysis
        strategy_patterns = self._analyze_strategy_patterns(data)

        # Implementation analysis
        implementation_analysis = self._analyze_implementation_patterns(data)

        return {
            "strategy_density": {
                "distribution": density_distribution,
                "statistics": {
                    "mean": statistics.mean(strategy_densities),
                    "median": statistics.median(strategy_densities),
                    "max": max(strategy_densities) if strategy_densities else 0
                }
            },
            "technical_indicators": {
                "most_common": technical_indicators.most_common(10),
                "total_unique": len(technical_indicators),
                "distribution": dict(technical_indicators)
            },
            "key_concepts": {
                "most_common": key_concepts.most_common(15),
                "total_unique": len(key_concepts),
                "distribution": dict(key_concepts)
            },
            "strategy_patterns": strategy_patterns,
            "implementation_analysis": implementation_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def generate_source_performance_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate source performance analysis"""

        if not data:
            return {"error": "No data available for analysis"}

        # Group by source
        source_metrics = defaultdict(lambda: {
            "entries": [],
            "quality_scores": [],
            "strategy_densities": [],
            "actionable_count": 0,
            "has_code_count": 0
        })

        for entry in data:
            site = entry.get('site', 'unknown')
            metrics = source_metrics[site]

            metrics["entries"].append(entry)
            metrics["quality_scores"].append(entry.get('quality_score', 0))
            metrics["strategy_densities"].append(entry.get('strategy_density', 0))

            enrichment_summary = entry.get('enrichment_summary', {})
            if enrichment_summary.get('actionable', False):
                metrics["actionable_count"] += 1
            if enrichment_summary.get('has_code', False):
                metrics["has_code_count"] += 1

        # Calculate performance metrics for each source
        source_performance = {}

        for site, metrics in source_metrics.items():
            entry_count = len(metrics["entries"])
            quality_scores = metrics["quality_scores"]
            strategy_densities = metrics["strategy_densities"]

            source_performance[site] = {
                "total_entries": entry_count,
                "avg_quality": statistics.mean(quality_scores),
                "max_quality": max(quality_scores),
                "min_quality": min(quality_scores),
                "avg_strategy_density": statistics.mean(strategy_densities),
                "actionable_percentage": (metrics["actionable_count"] / entry_count) * 100,
                "code_percentage": (metrics["has_code_count"] / entry_count) * 100,
                "quality_consistency": statistics.stdev(quality_scores) if len(quality_scores) > 1 else 0
            }

        # Rank sources by performance
        ranked_sources = sorted(
            source_performance.items(),
            key=lambda x: (x[1]["avg_quality"], x[1]["actionable_percentage"]),
            reverse=True
        )

        return {
            "source_performance": source_performance,
            "ranked_sources": ranked_sources,
            "top_performers": ranked_sources[:5],
            "performance_summary": {
                "total_sources": len(source_performance),
                "best_avg_quality": max(sp["avg_quality"] for sp in source_performance.values()),
                "best_actionable_rate": max(sp["actionable_percentage"] for sp in source_performance.values())
            },
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _identify_content_gaps(self, coverage_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Identify content gaps and provide recommendations"""

        gaps = {
            "missing_content_types": [],
            "underrepresented_topics": [],
            "missing_tools": [],
            "strategy_gaps": [],
            "recommendations": []
        }

        # Expected content types for trading education
        expected_content_types = ["tutorial", "strategy", "implementation", "theory", "news"]
        current_content_types = set(coverage_analysis["content_types"]["distribution"].keys())

        gaps["missing_content_types"] = list(set(expected_content_types) - current_content_types)

        # Underrepresented topics (less than 10% coverage)
        topic_coverage = coverage_analysis["topic_areas"]["coverage"]
        gaps["underrepresented_topics"] = [
            topic for topic, coverage in topic_coverage.items() if coverage < 10
        ]

        # Missing important tools
        expected_tools = ["python", "r", "matlab", "cpp"]
        current_tools = set(coverage_analysis["tools_languages"]["distribution"].keys())
        gaps["missing_tools"] = list(set(expected_tools) - current_tools)

        # Strategy type gaps
        expected_strategies = ["momentum", "mean_reversion", "arbitrage", "ml"]
        current_strategies = set(coverage_analysis["strategy_types"]["distribution"].keys())
        gaps["strategy_gaps"] = list(set(expected_strategies) - current_strategies)

        # Generate recommendations
        if gaps["missing_content_types"]:
            gaps["recommendations"].append(f"Add more {', '.join(gaps['missing_content_types'])} content")

        if gaps["underrepresented_topics"]:
            gaps["recommendations"].append(f"Increase coverage of {', '.join(gaps['underrepresented_topics'])}")

        if gaps["missing_tools"]:
            gaps["recommendations"].append(f"Add content covering {', '.join(gaps['missing_tools'])}")

        return gaps

    def _analyze_strategy_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze common strategy patterns"""

        # Extract strategy keywords
        indicator_patterns = Counter()
        signal_patterns = Counter()
        metric_patterns = Counter()

        for entry in data:
            strategy_keywords = entry.get('strategy_keywords', {})

            for indicator in strategy_keywords.get('indicators', []):
                indicator_patterns[indicator.lower()] += 1

            for signal in strategy_keywords.get('signals', []):
                signal_patterns[signal.lower()] += 1

            for metric in strategy_keywords.get('metrics', []):
                metric_patterns[metric.lower()] += 1

        return {
            "common_indicators": indicator_patterns.most_common(10),
            "common_signals": signal_patterns.most_common(10),
            "common_metrics": metric_patterns.most_common(10),
            "pattern_diversity": {
                "indicator_types": len(indicator_patterns),
                "signal_types": len(signal_patterns),
                "metric_types": len(metric_patterns)
            }
        }

    def _analyze_implementation_patterns(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze implementation and code patterns"""

        code_analysis = {
            "total_with_code": 0,
            "languages": Counter(),
            "code_types": Counter(),
            "average_code_snippets": 0
        }

        code_snippet_counts = []

        for entry in data:
            code_snippets = entry.get('code_snippets', [])

            if code_snippets:
                code_analysis["total_with_code"] += 1
                code_snippet_counts.append(len(code_snippets))

                for snippet in code_snippets:
                    language = snippet.get('language', 'unknown')
                    code_type = snippet.get('type', 'unknown')

                    code_analysis["languages"][language] += 1
                    code_analysis["code_types"][code_type] += 1

        if code_snippet_counts:
            code_analysis["average_code_snippets"] = statistics.mean(code_snippet_counts)

        return {
            "code_coverage": (code_analysis["total_with_code"] / len(data)) * 100 if data else 0,
            "most_common_languages": code_analysis["languages"].most_common(5),
            "code_type_distribution": dict(code_analysis["code_types"]),
            "average_snippets_per_entry": code_analysis["average_code_snippets"]
        }

    def generate_comprehensive_dashboard(self, data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate comprehensive analytics dashboard"""

        if data is None:
            # Try to get data from storage
            print("📥 Fetching data from storage...")
            # This would need to be implemented based on storage capabilities
            data = []  # Placeholder

        if not data:
            return {"error": "No data available for analysis"}

        print(f"📊 Generating analytics for {len(data)} entries...")

        dashboard = {
            "summary": {
                "total_entries": len(data),
                "analysis_timestamp": datetime.now().isoformat(),
                "quality_overview": {
                    "avg_quality": statistics.mean([e.get('quality_score', 0) for e in data]),
                    "actionable_count": len([e for e in data if e.get('enrichment_summary', {}).get('actionable', False)])
                }
            },
            "quality_analysis": self.generate_quality_distribution_report(data),
            "topic_coverage": self.generate_topic_coverage_report(data),
            "strategy_mining": self.generate_strategy_mining_report(data),
            "source_performance": self.generate_source_performance_report(data)
        }

        return dashboard

    def save_dashboard(self, dashboard: Dict[str, Any], output_file: Path):
        """Save dashboard to file"""

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)

        print(f"📁 Dashboard saved to: {output_file}")

    def create_visualizations(self, dashboard: Dict[str, Any], output_dir: Path):
        """Create visualization plots (if matplotlib available)"""

        if not PLOTTING_AVAILABLE:
            print("⚠️ Plotting libraries not available, skipping visualizations")
            return

        output_dir.mkdir(parents=True, exist_ok=True)

        # Quality distribution plot
        self._plot_quality_distribution(dashboard["quality_analysis"], output_dir)

        # Topic coverage plot
        self._plot_topic_coverage(dashboard["topic_coverage"], output_dir)

        # Strategy indicators plot
        self._plot_strategy_indicators(dashboard["strategy_mining"], output_dir)

        print(f"📊 Visualizations saved to: {output_dir}")

    def _plot_quality_distribution(self, quality_data: Dict[str, Any], output_dir: Path):
        """Create quality distribution plot"""

        if not PLOTTING_AVAILABLE:
            return

        try:
            distribution = quality_data["distribution"]

            plt.figure(figsize=(10, 6))
            categories = list(distribution.keys())
            values = list(distribution.values())

            colors = ['#2E8B57', '#32CD32', '#FFD700', '#FFA500', '#FF6347']

            plt.bar(categories, values, color=colors)
            plt.title('Content Quality Distribution')
            plt.xlabel('Quality Category')
            plt.ylabel('Number of Entries')
            plt.xticks(rotation=45)

            for i, v in enumerate(values):
                plt.text(i, v + 0.1, str(v), ha='center', va='bottom')

            plt.tight_layout()
            plt.savefig(output_dir / 'quality_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()

        except Exception as e:
            print(f"❌ Failed to create quality plot: {e}")

    def _plot_topic_coverage(self, topic_data: Dict[str, Any], output_dir: Path):
        """Create topic coverage plot"""

        if not PLOTTING_AVAILABLE:
            return

        try:
            content_types = topic_data["coverage_analysis"]["content_types"]["distribution"]

            plt.figure(figsize=(12, 8))

            # Create pie chart for content types
            if content_types:
                labels = list(content_types.keys())
                sizes = list(content_types.values())

                plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
                plt.title('Content Type Distribution')
                plt.axis('equal')

                plt.savefig(output_dir / 'topic_coverage.png', dpi=300, bbox_inches='tight')

            plt.close()

        except Exception as e:
            print(f"❌ Failed to create topic plot: {e}")

    def _plot_strategy_indicators(self, strategy_data: Dict[str, Any], output_dir: Path):
        """Create strategy indicators plot"""

        if not PLOTTING_AVAILABLE:
            return

        try:
            indicators = strategy_data["technical_indicators"]["most_common"]

            if indicators:
                plt.figure(figsize=(12, 6))

                names = [item[0] for item in indicators[:10]]
                counts = [item[1] for item in indicators[:10]]

                plt.barh(names, counts)
                plt.title('Most Common Technical Indicators')
                plt.xlabel('Frequency')
                plt.gca().invert_yaxis()

                plt.tight_layout()
                plt.savefig(output_dir / 'strategy_indicators.png', dpi=300, bbox_inches='tight')

            plt.close()

        except Exception as e:
            print(f"❌ Failed to create strategy plot: {e}")


def main():
    """CLI interface for content analytics"""
    import argparse

    parser = argparse.ArgumentParser(description='Content Analytics Dashboard')
    parser.add_argument('--input-file', help='JSONL file with enriched data')
    parser.add_argument('--output-dir', help='Output directory for dashboard')
    parser.add_argument('--visualizations', action='store_true', help='Create visualizations')
    parser.add_argument('--report-type', choices=['quality', 'topics', 'strategy', 'sources', 'all'],
                       default='all', help='Type of report to generate')

    args = parser.parse_args()

    analytics = ContentAnalytics()

    # Load data
    data = []
    if args.input_file:
        input_path = Path(args.input_file)
        if input_path.exists():
            with open(input_path, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
            print(f"📊 Loaded {len(data)} entries from {input_path}")
        else:
            print(f"❌ Input file not found: {input_path}")
            return

    if not data:
        print("❌ No data available for analysis")
        return

    # Generate reports
    if args.report_type == 'all':
        dashboard = analytics.generate_comprehensive_dashboard(data)
        report_name = "comprehensive_dashboard"
    elif args.report_type == 'quality':
        dashboard = analytics.generate_quality_distribution_report(data)
        report_name = "quality_report"
    elif args.report_type == 'topics':
        dashboard = analytics.generate_topic_coverage_report(data)
        report_name = "topic_coverage_report"
    elif args.report_type == 'strategy':
        dashboard = analytics.generate_strategy_mining_report(data)
        report_name = "strategy_mining_report"
    elif args.report_type == 'sources':
        dashboard = analytics.generate_source_performance_report(data)
        report_name = "source_performance_report"

    # Save results
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save dashboard JSON
        dashboard_file = output_dir / f"{report_name}.json"
        analytics.save_dashboard(dashboard, dashboard_file)

        # Create visualizations if requested
        if args.visualizations and args.report_type == 'all':
            viz_dir = output_dir / "visualizations"
            analytics.create_visualizations(dashboard, viz_dir)

    # Print summary
    print(f"\n📈 Analytics Summary:")
    if isinstance(dashboard, dict) and "summary" in dashboard:
        summary = dashboard["summary"]
        print(f"  Total entries: {summary['total_entries']}")
        print(f"  Average quality: {summary['quality_overview']['avg_quality']:.1f}")
        print(f"  Actionable entries: {summary['quality_overview']['actionable_count']}")


if __name__ == "__main__":
    main()
