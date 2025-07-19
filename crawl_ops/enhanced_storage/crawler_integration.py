#!/usr/bin/env python3
"""
Crawler Integration for IntelForge Content Enrichment

Integrates the enrichment pipeline with the existing semantic crawler
to automatically enrich content during the crawling process.
"""

import orjson as json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from crawl_ops.enrichment import EnrichmentPipeline
from crawl_ops.enhanced_storage.enriched_storage import EnrichedContentStorage


class CrawlerEnrichmentIntegration:
    """Integration layer between semantic crawler and enrichment pipeline"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Initialize components
        self.enrichment_pipeline = EnrichmentPipeline(self.config)
        self.enhanced_storage = EnrichedContentStorage()

        # Integration settings
        self.auto_enrich = self.config.get('auto_enrich', True)
        self.store_enriched = self.config.get('store_enriched', True)
        self.quality_threshold = self.config.get('quality_threshold', 70.0)

        print("🔗 Crawler enrichment integration initialized")

    def process_scrapy_output(self, scrapy_jsonl_file: Path,
                             output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Process Scrapy JSONL output through enrichment pipeline

        Args:
            scrapy_jsonl_file: Path to Scrapy output JSONL file
            output_dir: Optional output directory for enriched data

        Returns:
            Processing results and statistics
        """

        if not scrapy_jsonl_file.exists():
            return {"error": f"Scrapy output file not found: {scrapy_jsonl_file}"}

        print(f"🔄 Processing Scrapy output: {scrapy_jsonl_file}")

        # Setup output paths
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            enriched_file = output_dir / "enriched_data.jsonl"
        else:
            # Use same directory as input
            enriched_file = scrapy_jsonl_file.parent / "enriched_data.jsonl"

        # Run enrichment pipeline
        enriched_entries = self.enrichment_pipeline.enrich_scraped_data(
            scrapy_jsonl_file,
            enriched_file if self.auto_enrich else None
        )

        # Store in enhanced storage if enabled
        storage_results = {"stored_count": 0, "storage_errors": []}

        if self.store_enriched and enriched_entries:
            storage_results = self._store_enriched_data(enriched_entries)

        # Generate processing summary
        processing_results = {
            "input_file": str(scrapy_jsonl_file),
            "output_file": str(enriched_file) if self.auto_enrich else None,
            "total_entries": len(enriched_entries),
            "enriched_entries": len([e for e in enriched_entries if not e.get('enrichment_skipped', False)]),
            "high_quality_entries": len([e for e in enriched_entries if e.get('quality_score', 0) >= self.quality_threshold]),
            "actionable_entries": len([e for e in enriched_entries if e.get('enrichment_summary', {}).get('actionable', False)]),
            "storage_results": storage_results,
            "processing_timestamp": self.enrichment_pipeline._get_timestamp()
        }

        return processing_results

    def _store_enriched_data(self, enriched_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Store enriched data in enhanced storage"""

        stored_count = 0
        storage_errors = []

        for entry in enriched_entries:
            # Skip entries that failed enrichment
            if entry.get('enrichment_skipped', False):
                continue

            try:
                # Generate vector embedding if possible (placeholder for now)
                vector = None  # TODO: Integrate with sentence-transformers

                success = self.enhanced_storage.store_enriched_content(entry, vector)
                if success:
                    stored_count += 1
                else:
                    storage_errors.append(f"Failed to store: {entry.get('url', 'unknown')}")

            except Exception as e:
                storage_errors.append(f"Storage error for {entry.get('url', 'unknown')}: {e}")

        return {
            "stored_count": stored_count,
            "storage_errors": storage_errors,
            "success_rate": (stored_count / len(enriched_entries)) * 100 if enriched_entries else 0
        }

    def create_enrichment_hook(self) -> callable:
        """
        Create a hook function that can be integrated into the semantic crawler

        Returns:
            Hook function that processes captured content
        """

        def enrichment_hook(captured_data: Dict[str, Any]) -> Dict[str, Any]:
            """
            Hook function for real-time enrichment during crawling

            Args:
                captured_data: Data captured by semantic crawler

            Returns:
                Enhanced data with enrichment results
            """

            try:
                # Convert captured data to enrichment format
                temp_file = self._create_temp_jsonl([captured_data])

                # Run enrichment pipeline
                enriched_entries = self.enrichment_pipeline.enrich_scraped_data(temp_file)

                # Clean up temp file
                temp_file.unlink()

                if enriched_entries:
                    enriched_data = enriched_entries[0]

                    # Store in enhanced storage if enabled
                    if self.store_enriched:
                        vector = None  # TODO: Use actual vector from crawler
                        self.enhanced_storage.store_enriched_content(enriched_data, vector)

                    return enriched_data
                else:
                    return captured_data

            except Exception as e:
                print(f"❌ Enrichment hook error: {e}")
                return captured_data

        return enrichment_hook

    def _create_temp_jsonl(self, data_entries: List[Dict[str, Any]]) -> Path:
        """Create temporary JSONL file for processing"""

        temp_file = Path(tempfile.mktemp(suffix='.jsonl'))

        with open(temp_file, 'w', encoding='utf-8') as f:
            for entry in data_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')

        return temp_file

    def integrate_with_semantic_crawler(self, crawler_script_path: Path) -> bool:
        """
        Integrate enrichment pipeline with semantic crawler script

        Args:
            crawler_script_path: Path to semantic_crawler.py

        Returns:
            True if integration successful
        """

        if not crawler_script_path.exists():
            print(f"❌ Crawler script not found: {crawler_script_path}")
            return False

        try:
            # Read current crawler script
            with open(crawler_script_path, 'r', encoding='utf-8') as f:
                crawler_content = f.read()

            # Check if already integrated
            if "EnrichmentPipeline" in crawler_content:
                print("✅ Enrichment pipeline already integrated")
                return True

            # Find integration points
            integration_point = self._find_integration_point(crawler_content)

            if not integration_point:
                print("❌ Could not find suitable integration point in crawler")
                return False

            # Add enrichment integration
            modified_content = self._add_enrichment_integration(crawler_content, integration_point)

            # Create backup
            backup_path = crawler_script_path.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(crawler_content)

            # Write modified content
            with open(crawler_script_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)

            print(f"✅ Enrichment integration added to {crawler_script_path}")
            print(f"📁 Backup saved to {backup_path}")

            return True

        except Exception as e:
            print(f"❌ Integration failed: {e}")
            return False

    def _find_integration_point(self, content: str) -> Optional[str]:
        """Find suitable integration point in crawler script"""

        # Look for the main processing loop or save functions
        integration_markers = [
            "save_to_markdown",
            "embed_to_qdrant",
            "metadata_records.append",
            "def main("
        ]

        for marker in integration_markers:
            if marker in content:
                return marker

        return None

    def _add_enrichment_integration(self, content: str, integration_point: str) -> str:
        """Add enrichment integration code to crawler script"""

        # Add import at the top
        import_line = "from crawl_ops.enhanced_storage.crawler_integration import CrawlerEnrichmentIntegration\n"

        # Find imports section
        lines = content.split('\n')
        import_index = -1

        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_index = i

        if import_index >= 0:
            lines.insert(import_index + 1, import_line)

        # Add initialization in main function
        init_code = """
    # Initialize enrichment integration
    enrichment_config = {'auto_enrich': True, 'store_enriched': True}
    enrichment_integration = CrawlerEnrichmentIntegration(enrichment_config)
    enrichment_hook = enrichment_integration.create_enrichment_hook()
"""

        # Find main function and add initialization
        for i, line in enumerate(lines):
            if 'def main(' in line:
                # Find the first non-comment line in main
                j = i + 1
                while j < len(lines) and (lines[j].strip().startswith('#') or not lines[j].strip()):
                    j += 1

                # Insert initialization code
                for init_line in init_code.strip().split('\n'):
                    lines.insert(j, init_line)
                    j += 1
                break

        # Add enrichment hook call at processing point
        hook_code = "        # Apply enrichment hook\n        captured_data = enrichment_hook(captured_data)"

        for i, line in enumerate(lines):
            if integration_point in line and "captured_data" in line:
                lines.insert(i + 1, hook_code)
                break

        return '\n'.join(lines)


def main():
    """CLI interface for crawler integration"""
    import argparse

    parser = argparse.ArgumentParser(description='Crawler Enrichment Integration')
    parser.add_argument('--process-scrapy', help='Process Scrapy JSONL output file')
    parser.add_argument('--output-dir', help='Output directory for enriched data')
    parser.add_argument('--integrate-crawler', help='Integrate with semantic crawler script')
    parser.add_argument('--test-hook', action='store_true', help='Test enrichment hook')

    args = parser.parse_args()

    integration = CrawlerEnrichmentIntegration()

    if args.process_scrapy:
        scrapy_file = Path(args.process_scrapy)
        output_dir = Path(args.output_dir) if args.output_dir else None

        results = integration.process_scrapy_output(scrapy_file, output_dir)

        print("\n📊 Processing Results:")
        print(json.dumps(results, indent=2))

    elif args.integrate_crawler:
        crawler_path = Path(args.integrate_crawler)
        success = integration.integrate_with_semantic_crawler(crawler_path)

        if success:
            print("✅ Integration completed successfully")
        else:
            print("❌ Integration failed")

    elif args.test_hook:
        # Test the enrichment hook with sample data
        sample_data = {
            "url": "https://example.com/test",
            "title": "Test Trading Strategy",
            "content": "This is a test article about momentum trading using moving averages.",
            "content_length": 100,
            "extraction_method": "test",
            "site": "example.com",
            "content_hash": "test123"
        }

        hook = integration.create_enrichment_hook()
        enriched_data = hook(sample_data)

        print("🧪 Hook Test Results:")
        print(f"Quality Score: {enriched_data.get('quality_score', 'N/A')}")
        print(f"Tags: {len(enriched_data.get('content_tags', {}))}")
        print(f"Enriched: {'✅' if 'enrichment_timestamp' in enriched_data else '❌'}")


if __name__ == "__main__":
    main()
