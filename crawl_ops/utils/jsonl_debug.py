#!/usr/bin/env python3
"""
JSONL Debugging and Analysis Utility for IntelForge

Interactive tool for exploring and filtering crawl data.
Better than cat + grep for JSONL analysis.
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import orjson

try:
    import jq
    JQ_AVAILABLE = True
except ImportError:
    JQ_AVAILABLE = False


class JSONLDebugger:
    """Interactive JSONL exploration and filtering tool."""
    
    def __init__(self, file_path: str):
        """
        Initialize JSONL debugger.
        
        Args:
            file_path: Path to JSONL file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSONL file not found: {file_path}")
        
        self.data = self._load_data()
        print(f"📄 Loaded {len(self.data)} entries from {file_path}")
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Load JSONL data from file."""
        data = []
        with open(self.file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = orjson.loads(line.strip())
                    data.append(entry)
                except json.JSONDecodeError as e:
                    print(f"Warning: Invalid JSON on line {line_num}: {e}")
                    continue
        return data
    
    def summary(self):
        """Show summary statistics of the JSONL data."""
        if not self.data:
            print("No data to analyze")
            return
        
        print(f"\n📊 JSONL Summary")
        print("=" * 40)
        print(f"Total entries: {len(self.data)}")
        
        # Field analysis
        all_fields = set()
        for entry in self.data:
            all_fields.update(entry.keys())
        
        print(f"Unique fields: {len(all_fields)}")
        print(f"Fields: {', '.join(sorted(all_fields))}")
        
        # Common field statistics
        if 'url' in all_fields:
            unique_urls = len(set(entry.get('url', '') for entry in self.data))
            print(f"Unique URLs: {unique_urls}")
        
        if 'site' in all_fields:
            sites = [entry.get('site', '') for entry in self.data]
            site_counts = {}
            for site in sites:
                site_counts[site] = site_counts.get(site, 0) + 1
            print(f"Sites: {dict(list(site_counts.items())[:5])}")
        
        if 'content_length' in all_fields:
            lengths = [entry.get('content_length', 0) for entry in self.data if entry.get('content_length')]
            if lengths:
                avg_length = sum(lengths) / len(lengths)
                print(f"Avg content length: {avg_length:.0f} chars")
        
        if 'quality_score' in all_fields:
            scores = [entry.get('quality_score', 0) for entry in self.data if entry.get('quality_score')]
            if scores:
                avg_score = sum(scores) / len(scores)
                print(f"Avg quality score: {avg_score:.1f}")
    
    def filter_by_field(self, field: str, value: Any = None, show_values: bool = False):
        """Filter entries by field value or show unique values."""
        if show_values:
            # Show unique values for the field
            values = set()
            for entry in self.data:
                if field in entry:
                    values.add(str(entry[field]))
            
            print(f"\n🔍 Unique values for '{field}':")
            for val in sorted(values)[:20]:  # Show first 20
                print(f"  {val}")
            if len(values) > 20:
                print(f"  ... and {len(values) - 20} more")
            return
        
        # Filter by value
        if value is None:
            print(f"Please specify a value to filter by for field '{field}'")
            return
        
        filtered = [entry for entry in self.data if entry.get(field) == value]
        print(f"\n🎯 Filtered {len(filtered)} entries where {field} = {value}")
        
        for i, entry in enumerate(filtered[:5]):  # Show first 5
            print(f"\n{i+1}. {entry.get('url', 'No URL')}")
            if 'title' in entry:
                print(f"   Title: {entry['title'][:80]}...")
            if 'content_length' in entry:
                print(f"   Length: {entry['content_length']} chars")
        
        if len(filtered) > 5:
            print(f"\n... and {len(filtered) - 5} more entries")
    
    def search_content(self, keyword: str, case_sensitive: bool = False):
        """Search for keyword in content fields."""
        results = []
        search_fields = ['content', 'title', 'url']
        
        for entry in self.data:
            for field in search_fields:
                if field in entry:
                    text = str(entry[field])
                    if not case_sensitive:
                        text = text.lower()
                        keyword = keyword.lower()
                    
                    if keyword in text:
                        results.append((entry, field))
                        break
        
        print(f"\n🔍 Found {len(results)} entries containing '{keyword}'")
        
        for i, (entry, field) in enumerate(results[:5]):
            print(f"\n{i+1}. {entry.get('url', 'No URL')} (found in {field})")
            if 'title' in entry:
                print(f"   Title: {entry['title'][:80]}...")
            
            # Show context around keyword
            if field in entry:
                text = str(entry[field])
                if not case_sensitive:
                    text_lower = text.lower()
                    keyword_lower = keyword.lower()
                    idx = text_lower.find(keyword_lower)
                else:
                    idx = text.find(keyword)
                
                if idx != -1:
                    start = max(0, idx - 50)
                    end = min(len(text), idx + len(keyword) + 50)
                    context = text[start:end]
                    print(f"   Context: ...{context}...")
        
        if len(results) > 5:
            print(f"\n... and {len(results) - 5} more entries")
    
    def quality_analysis(self):
        """Analyze content quality scores and metrics."""
        quality_entries = [e for e in self.data if 'quality_score' in e]
        
        if not quality_entries:
            print("No quality score data found")
            return
        
        scores = [e['quality_score'] for e in quality_entries]
        
        print(f"\n📈 Quality Analysis")
        print("=" * 30)
        print(f"Entries with quality scores: {len(quality_entries)}")
        print(f"Average score: {sum(scores) / len(scores):.1f}")
        print(f"Min score: {min(scores):.1f}")
        print(f"Max score: {max(scores):.1f}")
        
        # Score distribution
        score_ranges = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for score in scores:
            if score <= 20:
                score_ranges["0-20"] += 1
            elif score <= 40:
                score_ranges["21-40"] += 1
            elif score <= 60:
                score_ranges["41-60"] += 1
            elif score <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        
        print(f"\nScore distribution:")
        for range_name, count in score_ranges.items():
            print(f"  {range_name}: {count} entries")
        
        # Top quality entries
        top_entries = sorted(quality_entries, key=lambda x: x['quality_score'], reverse=True)[:3]
        print(f"\nTop quality entries:")
        for i, entry in enumerate(top_entries, 1):
            print(f"  {i}. Score {entry['quality_score']:.1f}: {entry.get('url', 'No URL')}")
    
    def export_filtered(self, output_file: str, filter_func=None):
        """Export filtered data to new JSONL file."""
        if filter_func is None:
            filtered_data = self.data
        else:
            filtered_data = [entry for entry in self.data if filter_func(entry)]
        
        output_path = Path(output_file)
        with open(output_path, 'wb') as f:
            for entry in filtered_data:
                f.write(orjson.dumps(entry) + b'\n')
        
        print(f"📤 Exported {len(filtered_data)} entries to {output_file}")
    
    def jq_query(self, query: str):
        """Run jq query on the data if jq is available."""
        if not JQ_AVAILABLE:
            print("jq package not available. Install with: pip install jq")
            return
        
        try:
            # Convert data to JSON string and apply jq query
            json_data = orjson.dumps(self.data)
            result = jq.compile(query).input(json.loads(json_data)).all()
            
            print(f"\n🔍 jq query: {query}")
            print("Results:")
            for item in result[:10]:  # Show first 10 results
                print(f"  {item}")
            
            if len(result) > 10:
                print(f"  ... and {len(result) - 10} more results")
                
        except Exception as e:
            print(f"Error running jq query: {e}")


def main():
    parser = argparse.ArgumentParser(description="JSONL Debugging Tool for IntelForge")
    parser.add_argument("file", help="JSONL file to analyze")
    parser.add_argument("--summary", action="store_true", help="Show summary statistics")
    parser.add_argument("--filter-field", help="Field to filter by")
    parser.add_argument("--filter-value", help="Value to filter by")
    parser.add_argument("--show-values", help="Show unique values for field")
    parser.add_argument("--search", help="Search for keyword in content")
    parser.add_argument("--quality", action="store_true", help="Analyze quality scores")
    parser.add_argument("--export", help="Export filtered results to file")
    parser.add_argument("--jq", help="Run jq query on data")
    
    args = parser.parse_args()
    
    try:
        debugger = JSONLDebugger(args.file)
        
        if args.summary:
            debugger.summary()
        
        if args.show_values:
            debugger.filter_by_field(args.show_values, show_values=True)
        
        if args.filter_field:
            debugger.filter_by_field(args.filter_field, args.filter_value)
        
        if args.search:
            debugger.search_content(args.search)
        
        if args.quality:
            debugger.quality_analysis()
        
        if args.jq:
            debugger.jq_query(args.jq)
        
        if args.export:
            debugger.export_filtered(args.export)
        
        # Interactive mode if no specific command
        if not any([args.summary, args.filter_field, args.search, args.quality, args.jq, args.export, args.show_values]):
            debugger.summary()
            print(f"\n💡 Try: python {sys.argv[0]} {args.file} --summary")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()