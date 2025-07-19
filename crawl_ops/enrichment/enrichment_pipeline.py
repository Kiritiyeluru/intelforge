#!/usr/bin/env python3
"""
IntelForge Content Enrichment Pipeline Orchestrator

Main orchestrator that combines all enrichment components:
1. Content Scoring System
2. Auto-Tagging Pipeline
3. Strategy Keyword Extraction
4. Enhanced Storage Integration

Implements the complete Phase 1 enrichment pipeline from the data enrichment plan.
"""

import orjson as json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import enrichment components
from crawl_ops.enrichment.content_scorer import ContentScorer
from crawl_ops.enrichment.auto_tagger import AutoTagger
from crawl_ops.enrichment.strategy_extractor import StrategyExtractor


class EnrichmentPipeline:
    """Complete content enrichment pipeline orchestrator"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Initialize enrichment components
        print("🔧 Initializing enrichment components...")
        self.content_scorer = ContentScorer()
        self.auto_tagger = AutoTagger()
        self.strategy_extractor = StrategyExtractor()

        # Pipeline configuration
        self.quality_threshold = self.config.get('quality_threshold', 70.0)
        self.enable_ai_scoring = self.config.get('enable_ai_scoring', True)
        self.parallel_processing = self.config.get('parallel_processing', False)

        print("✅ Enrichment pipeline initialized")

    def enrich_single_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single content entry with all enrichment components"""

        # Extract basic content
        content = entry.get('content', '')
        title = entry.get('title', '')
        url = entry.get('url', '')

        if not content:
            print(f"⚠️ Skipping entry with no content: {url}")
            return entry

        enriched_entry = entry.copy()

        try:
            # 1. Content Scoring
            print(f"📊 Scoring content: {title[:50]}...")
            score_data = self.content_scorer.calculate_content_score(content, title, url)

            enriched_entry.update({
                'quality_score': score_data['overall_score'],
                'scoring_details': score_data,
                'enrichment_timestamp': self._get_timestamp(),
                'enrichment_version': '1.0'
            })

            # Skip low quality content if below threshold
            if score_data['overall_score'] < self.quality_threshold:
                print(f"⚠️ Content below quality threshold: {score_data['overall_score']}")
                enriched_entry['enrichment_skipped'] = True
                enriched_entry['skip_reason'] = 'below_quality_threshold'
                return enriched_entry

            # 2. Auto-Tagging
            print(f"🏷️ Tagging content...")
            tags = self.auto_tagger.tag_content(content, title, url)

            enriched_entry.update({
                'content_tags': tags,
                'tag_count': sum(len(tag_list) for tag_list in tags.values()),
                'technical_level': self._extract_technical_level(tags),
                'topic_areas': self._extract_topic_areas(tags)
            })

            # 3. Strategy Keyword Extraction
            print(f"🔍 Extracting strategy keywords...")
            strategy_data = self.strategy_extractor.extract_strategy_keywords(content, title)

            enriched_entry.update({
                'strategy_keywords': strategy_data['strategy_patterns'],
                'technical_indicators': strategy_data['technical_indicators'],
                'market_terms': strategy_data['market_terms'],
                'custom_strategies': strategy_data['custom_strategies'],
                'strategy_density': strategy_data['extraction_metadata']['strategy_density'],
                'key_concepts': self._extract_key_concepts(strategy_data)
            })

            # 4. Code Snippet Detection
            code_snippets = self._extract_code_snippets(content)
            if code_snippets:
                enriched_entry['code_snippets'] = code_snippets

            # 5. Enrichment Summary
            enriched_entry['enrichment_summary'] = self._generate_enrichment_summary(enriched_entry)

            print(f"✅ Successfully enriched: {title[:50]}")

        except Exception as e:
            print(f"❌ Error enriching entry: {e}")
            enriched_entry['enrichment_error'] = str(e)
            enriched_entry['enrichment_skipped'] = True
            enriched_entry['skip_reason'] = 'processing_error'

        return enriched_entry

    def enrich_scraped_data(self, input_file: Path,
                           output_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Enrich all entries in a scraped data JSONL file"""

        print(f"🚀 Starting enrichment pipeline for: {input_file}")
        enriched_entries = []

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            print(f"📝 Processing {len(lines)} entries...")

            for line_num, line in enumerate(lines, 1):
                try:
                    entry = json.loads(line.strip())

                    print(f"\n🔄 Processing entry {line_num}/{len(lines)}")
                    enriched_entry = self.enrich_single_entry(entry)
                    enriched_entries.append(enriched_entry)

                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing line {line_num}: {e}")
                    continue

            # Generate pipeline statistics
            stats = self._generate_pipeline_statistics(enriched_entries)
            print(f"\n📊 Pipeline Statistics:")
            self._print_statistics(stats)

            # Save enriched data
            if output_file:
                self._save_enriched_data(enriched_entries, output_file)
                print(f"💾 Saved enriched data to: {output_file}")

            return enriched_entries

        except FileNotFoundError:
            print(f"❌ Input file not found: {input_file}")
            return []
        except Exception as e:
            print(f"❌ Pipeline error: {e}")
            return []

    def _extract_technical_level(self, tags: Dict[str, List[str]]) -> str:
        """Extract primary technical level from tags"""
        tech_levels = tags.get('technical_level', [])

        if not tech_levels:
            return 'intermediate'  # Default

        # Priority order: expert > advanced > intermediate > beginner
        priority_order = ['expert', 'advanced', 'intermediate', 'beginner']

        for level in priority_order:
            if level in tech_levels:
                return level

        return tech_levels[0]  # Fallback to first found

    def _extract_topic_areas(self, tags: Dict[str, List[str]]) -> List[str]:
        """Extract topic areas from tags"""
        return tags.get('topic_area', [])

    def _extract_key_concepts(self, strategy_data: Dict[str, Any]) -> List[str]:
        """Extract key concepts from strategy extraction results"""
        key_concepts = []

        # Add unique indicators
        indicators = strategy_data.get('technical_indicators', {})
        key_concepts.extend(indicators.keys())

        # Add strategy types
        strategy_patterns = strategy_data.get('strategy_patterns', {})
        strategy_types = strategy_patterns.get('strategy_types', [])
        key_concepts.extend(strategy_types)

        # Add significant metrics
        metrics = strategy_patterns.get('metrics', [])
        key_concepts.extend(metrics[:3])  # Top 3 metrics

        # Remove duplicates and clean up
        return list(set([concept.lower().replace('_', ' ') for concept in key_concepts]))

    def _extract_code_snippets(self, content: str) -> List[Dict[str, Any]]:
        """Extract and analyze code snippets from content"""
        import re

        code_snippets = []

        # Extract code blocks
        code_block_pattern = r'```(\w*)\n(.*?)\n```'
        code_blocks = re.findall(code_block_pattern, content, re.DOTALL)

        for language, code in code_blocks:
            if len(code.strip()) > 10:  # Minimum code length
                code_snippets.append({
                    'type': 'code_block',
                    'language': language or 'unknown',
                    'code': code.strip(),
                    'length': len(code.strip()),
                    'line_count': len(code.strip().split('\n'))
                })

        # Extract inline code
        inline_code_pattern = r'`([^`]+)`'
        inline_codes = re.findall(inline_code_pattern, content)

        for code in inline_codes:
            if len(code.strip()) > 5 and any(char in code for char in ['(', '=', '.']):
                code_snippets.append({
                    'type': 'inline_code',
                    'language': 'unknown',
                    'code': code.strip(),
                    'length': len(code.strip())
                })

        return code_snippets[:10]  # Limit to 10 snippets

    def _generate_enrichment_summary(self, enriched_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of enrichment results"""
        summary = {
            'quality_score': enriched_entry.get('quality_score', 0),
            'has_code': len(enriched_entry.get('code_snippets', [])) > 0,
            'strategy_density': enriched_entry.get('strategy_density', 0),
            'tag_categories': len(enriched_entry.get('content_tags', {})),
            'technical_indicators_count': len(enriched_entry.get('technical_indicators', {})),
            'key_concepts_count': len(enriched_entry.get('key_concepts', [])),
            'actionable': self._assess_actionability(enriched_entry)
        }

        # Add enrichment quality assessment
        summary['enrichment_quality'] = self._assess_enrichment_quality(enriched_entry)

        return summary

    def _assess_actionability(self, enriched_entry: Dict[str, Any]) -> bool:
        """Assess if content is actionable for trading strategy development"""

        # Criteria for actionability
        has_high_quality = enriched_entry.get('quality_score', 0) >= 80
        has_implementation = len(enriched_entry.get('code_snippets', [])) > 0
        has_strategy_content = enriched_entry.get('strategy_density', 0) > 1.0
        has_indicators = len(enriched_entry.get('technical_indicators', {})) > 0

        # Content types that are typically actionable
        content_tags = enriched_entry.get('content_tags', {})
        content_types = content_tags.get('content_type', [])
        actionable_types = ['implementation', 'strategy', 'tutorial']
        has_actionable_type = any(ct in actionable_types for ct in content_types)

        # Score-based decision
        actionability_score = sum([
            has_high_quality,
            has_implementation,
            has_strategy_content,
            has_indicators,
            has_actionable_type
        ])

        return actionability_score >= 3

    def _assess_enrichment_quality(self, enriched_entry: Dict[str, Any]) -> str:
        """Assess overall enrichment quality"""

        quality_score = enriched_entry.get('quality_score', 0)
        tag_count = enriched_entry.get('tag_count', 0)
        strategy_density = enriched_entry.get('strategy_density', 0)

        if quality_score >= 90 and tag_count >= 8 and strategy_density > 2.0:
            return 'excellent'
        elif quality_score >= 75 and tag_count >= 5 and strategy_density > 1.0:
            return 'good'
        elif quality_score >= 60 and tag_count >= 3:
            return 'moderate'
        else:
            return 'basic'

    def _generate_pipeline_statistics(self, enriched_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive pipeline statistics"""

        if not enriched_entries:
            return {}

        total_entries = len(enriched_entries)
        successful_entries = [e for e in enriched_entries if not e.get('enrichment_skipped', False)]

        quality_scores = [e.get('quality_score', 0) for e in successful_entries]
        strategy_densities = [e.get('strategy_density', 0) for e in successful_entries]

        stats = {
            'total_entries': total_entries,
            'successful_enrichments': len(successful_entries),
            'skipped_entries': total_entries - len(successful_entries),
            'success_rate': (len(successful_entries) / total_entries) * 100,

            'quality_statistics': {
                'average_score': sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                'max_score': max(quality_scores) if quality_scores else 0,
                'min_score': min(quality_scores) if quality_scores else 0,
                'high_quality_entries': len([s for s in quality_scores if s >= 80])
            },

            'strategy_statistics': {
                'average_density': sum(strategy_densities) / len(strategy_densities) if strategy_densities else 0,
                'max_density': max(strategy_densities) if strategy_densities else 0,
                'strategy_rich_entries': len([d for d in strategy_densities if d > 2.0])
            },

            'actionability': {
                'actionable_entries': len([e for e in successful_entries if e.get('enrichment_summary', {}).get('actionable', False)]),
                'code_containing_entries': len([e for e in successful_entries if e.get('enrichment_summary', {}).get('has_code', False)])
            }
        }

        return stats

    def _print_statistics(self, stats: Dict[str, Any]):
        """Print formatted pipeline statistics"""

        print(f"  Total entries processed: {stats['total_entries']}")
        print(f"  Successful enrichments: {stats['successful_enrichments']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")

        quality_stats = stats['quality_statistics']
        print(f"\n📊 Quality Statistics:")
        print(f"  Average quality score: {quality_stats['average_score']:.1f}")
        print(f"  High quality entries (80+): {quality_stats['high_quality_entries']}")

        strategy_stats = stats['strategy_statistics']
        print(f"\n🎯 Strategy Statistics:")
        print(f"  Average strategy density: {strategy_stats['average_density']:.2f}%")
        print(f"  Strategy-rich entries (2%+): {strategy_stats['strategy_rich_entries']}")

        actionability = stats['actionability']
        print(f"\n⚡ Actionability:")
        print(f"  Actionable entries: {actionability['actionable_entries']}")
        print(f"  Code-containing entries: {actionability['code_containing_entries']}")

    def _save_enriched_data(self, enriched_entries: List[Dict[str, Any]], output_file: Path):
        """Save enriched data to JSONL file"""

        with open(output_file, 'w', encoding='utf-8') as f:
            for entry in enriched_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()


def main():
    """CLI interface for enrichment pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description='IntelForge Content Enrichment Pipeline')
    parser.add_argument('--input', '-i', required=True, help='Input JSONL file')
    parser.add_argument('--output', '-o', help='Output JSONL file')
    parser.add_argument('--quality-threshold', '-t', type=float, default=70.0,
                       help='Quality threshold for processing')
    parser.add_argument('--config', '-c', help='Configuration file')
    parser.add_argument('--stats-only', action='store_true',
                       help='Only show statistics, do not save output')

    args = parser.parse_args()

    # Load configuration if provided
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
        except Exception as e:
            print(f"❌ Error loading config: {e}")

    config['quality_threshold'] = args.quality_threshold

    # Initialize and run pipeline
    pipeline = EnrichmentPipeline(config)

    output_file = None if args.stats_only else Path(args.output) if args.output else None

    enriched_entries = pipeline.enrich_scraped_data(Path(args.input), output_file)

    print(f"\n🎉 Enrichment pipeline completed!")
    print(f"Processed {len(enriched_entries)} entries")


if __name__ == "__main__":
    main()
