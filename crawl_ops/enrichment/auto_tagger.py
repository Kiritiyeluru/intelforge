#!/usr/bin/env python3
"""
Auto-Tagging Pipeline for IntelForge Data Enrichment

Automatically tags content with relevant categories:
- Content Type: tutorial, strategy, theory, implementation, news
- Technical Level: beginner, intermediate, advanced, expert  
- Topic Area: options, futures, equities, forex, crypto
- Tools/Languages: python, cpp, r, matlab, api
- Strategy Types: momentum, mean_reversion, arbitrage, ml, hft
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any
from urllib.parse import urlparse

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class AutoTagger:
    """Automated content tagging system"""
    
    def __init__(self):
        self.tag_patterns = self._initialize_tag_patterns()
        self.domain_tags = self._initialize_domain_tags()
    
    def _initialize_tag_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize keyword patterns for different tag categories"""
        return {
            "content_type": {
                "tutorial": [
                    "tutorial", "guide", "how to", "step by step", "walkthrough",
                    "introduction to", "beginner", "getting started", "learn"
                ],
                "strategy": [
                    "strategy", "approach", "method", "technique", "system",
                    "trading strategy", "algorithm", "model"
                ],
                "theory": [
                    "theory", "concept", "principle", "mathematics", "statistical",
                    "theoretical", "academic", "research", "analysis"
                ],
                "implementation": [
                    "implementation", "code", "python", "c++", "programming",
                    "example", "demo", "script", "function", "class"
                ],
                "news": [
                    "news", "announcement", "update", "market", "breaking",
                    "latest", "today", "report", "press release"
                ]
            },
            
            "technical_level": {
                "beginner": [
                    "beginner", "basic", "introduction", "fundamentals", "simple",
                    "getting started", "101", "basics", "elementary"
                ],
                "intermediate": [
                    "intermediate", "moderate", "standard", "typical", "common",
                    "practical", "applied", "real-world"
                ],
                "advanced": [
                    "advanced", "complex", "sophisticated", "detailed", "in-depth",
                    "professional", "expert level", "comprehensive"
                ],
                "expert": [
                    "expert", "cutting-edge", "research", "novel", "innovative",
                    "PhD", "academic", "theoretical", "mathematical proof"
                ]
            },
            
            "topic_area": {
                "options": [
                    "options", "option trading", "calls", "puts", "strike price",
                    "expiration", "volatility", "greeks", "black-scholes"
                ],
                "futures": [
                    "futures", "commodities", "contracts", "margin", "leverage",
                    "delivery", "settlement", "contango", "backwardation"
                ],
                "equities": [
                    "stocks", "equities", "shares", "dividends", "earnings",
                    "market cap", "P/E ratio", "fundamentals", "valuation"
                ],
                "forex": [
                    "forex", "currency", "exchange rate", "FX", "pairs",
                    "pip", "spread", "carry trade", "central bank"
                ],
                "crypto": [
                    "crypto", "cryptocurrency", "bitcoin", "ethereum", "blockchain",
                    "digital asset", "defi", "web3", "altcoin"
                ]
            },
            
            "tools_languages": {
                "python": [
                    "python", "pandas", "numpy", "matplotlib", "sklearn",
                    "jupyter", "anaconda", "pip", "import pandas"
                ],
                "cpp": [
                    "c++", "cpp", "#include", "std::", "boost",
                    "quantlib", "compiled", "performance"
                ],
                "r": [
                    "r language", "r programming", "rstudio", "cran",
                    "tidyverse", "ggplot", "library(", "data.frame"
                ],
                "matlab": [
                    "matlab", "simulink", "financial toolbox", ".m file",
                    "matrix", "vectorized", "mathworks"
                ],
                "api": [
                    "api", "rest", "json", "http", "endpoint",
                    "authentication", "rate limit", "webhook"
                ]
            },
            
            "strategy_types": {
                "momentum": [
                    "momentum", "trend following", "breakout", "moving average",
                    "price momentum", "technical momentum", "relative strength"
                ],
                "mean_reversion": [
                    "mean reversion", "reversion", "bollinger bands", "rsi",
                    "oversold", "overbought", "oscillator", "pairs trading"
                ],
                "arbitrage": [
                    "arbitrage", "spread", "pairs", "statistical arbitrage",
                    "market neutral", "hedge", "long short", "cointegration"
                ],
                "ml": [
                    "machine learning", "neural network", "deep learning", "AI",
                    "regression", "classification", "clustering", "feature"
                ],
                "hft": [
                    "high frequency", "hft", "latency", "microseconds",
                    "market making", "tick data", "order book", "co-location"
                ]
            }
        }
    
    def _initialize_domain_tags(self) -> Dict[str, List[str]]:
        """Initialize domain-based tag mappings"""
        return {
            "quantstart.com": ["tutorial", "python", "theory"],
            "quantopian.com": ["tutorial", "python", "backtesting"],
            "investopedia.com": ["beginner", "theory", "fundamentals"],
            "github.com": ["implementation", "code", "open-source"],
            "arxiv.org": ["research", "academic", "theory", "expert"],
            "bloomberg.com": ["news", "market", "professional"],
            "reuters.com": ["news", "market", "updates"],
            "sec.gov": ["regulation", "compliance", "official"],
            "stackexchange.com": ["qa", "community", "problem-solving"],
            "reddit.com": ["community", "discussion", "informal"]
        }
    
    def tag_content(self, content: str, title: str = "", url: str = "") -> Dict[str, List[str]]:
        """
        Tag content based on multiple analysis methods
        
        Returns dictionary with tag categories and their assigned tags
        """
        tags = {}
        combined_text = f"{title} {content}".lower()
        
        # Rule-based tagging using keyword patterns
        for category, patterns in self.tag_patterns.items():
            category_tags = []
            
            for tag, keywords in patterns.items():
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in combined_text)
                
                # Tag threshold: at least 1 match for most categories, 2+ for technical level
                threshold = 2 if category == "technical_level" else 1
                
                if matches >= threshold:
                    category_tags.append(tag)
            
            # Apply category-specific logic
            if category == "technical_level" and not category_tags:
                # Default to intermediate if no clear level detected
                category_tags.append("intermediate")
            elif category == "content_type" and not category_tags:
                # Infer content type from other signals
                if any(lang in combined_text for lang in ["python", "code", "function", "class"]):
                    category_tags.append("implementation")
                else:
                    category_tags.append("theory")
            
            tags[category] = category_tags
        
        # URL-based tagging
        if url:
            domain_tags = self._get_domain_tags(url)
            if domain_tags:
                tags["source_type"] = domain_tags
        
        # Pattern-based tagging
        pattern_tags = self._get_pattern_tags(content)
        if pattern_tags:
            tags["patterns"] = pattern_tags
        
        # Technical complexity assessment
        complexity_tags = self._assess_technical_complexity(content)
        if complexity_tags:
            tags["complexity"] = complexity_tags
        
        return tags
    
    def _get_domain_tags(self, url: str) -> List[str]:
        """Extract tags based on URL domain"""
        try:
            domain = urlparse(url).netloc.lower()
            # Remove www. prefix
            domain = domain.replace("www.", "")
            
            return self.domain_tags.get(domain, [])
        except:
            return []
    
    def _get_pattern_tags(self, content: str) -> List[str]:
        """Detect specific patterns in content"""
        tags = []
        
        # Code patterns
        if re.search(r'def \w+\(.*\):|class \w+.*:', content):
            tags.append("code_definitions")
        
        if re.search(r'```[\w]*\n.*?```', content, re.DOTALL):
            tags.append("code_blocks")
        
        # Mathematical patterns
        if re.search(r'\$.*?\$|\\[a-zA-Z]+{|\\begin{', content):
            tags.append("mathematical_formulas")
        
        # Data patterns
        if re.search(r'\.csv|\.json|\.xlsx|data frame|dataset', content, re.IGNORECASE):
            tags.append("data_analysis")
        
        # Backtesting patterns
        if re.search(r'backtest|sharpe ratio|drawdown|returns?.*analysis', content, re.IGNORECASE):
            tags.append("backtesting")
        
        # Strategy patterns
        if re.search(r'entry.*signal|exit.*signal|buy.*sell|long.*short', content, re.IGNORECASE):
            tags.append("trading_signals")
        
        return tags
    
    def _assess_technical_complexity(self, content: str) -> List[str]:
        """Assess technical complexity based on content analysis"""
        complexity_tags = []
        
        # Count technical indicators
        indicators = [
            "standard deviation", "correlation", "regression", "optimization",
            "monte carlo", "stochastic", "volatility modeling", "risk metrics",
            "portfolio theory", "efficient frontier", "var", "expected shortfall"
        ]
        
        technical_count = sum(1 for indicator in indicators if indicator in content.lower())
        
        if technical_count >= 5:
            complexity_tags.append("highly_technical")
        elif technical_count >= 2:
            complexity_tags.append("moderately_technical")
        
        # Code complexity
        code_patterns = [
            r'class \w+', r'def \w+\(', r'import \w+', r'for \w+ in',
            r'if __name__', r'try:', r'except:', r'with open'
        ]
        
        code_count = sum(1 for pattern in code_patterns 
                        if re.search(pattern, content))
        
        if code_count >= 5:
            complexity_tags.append("code_heavy")
        elif code_count >= 2:
            complexity_tags.append("includes_code")
        
        return complexity_tags
    
    def tag_scraped_data(self, jsonl_file: Path) -> List[Dict[str, Any]]:
        """Tag all entries in a scraped data JSONL file"""
        tagged_entries = []
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.strip())
                        
                        # Extract content for tagging
                        content = entry.get('content', '')
                        title = entry.get('title', '')
                        url = entry.get('url', '')
                        
                        # Generate tags
                        tags = self.tag_content(content, title, url)
                        
                        # Add tags to entry
                        entry['content_tags'] = tags
                        entry['tag_count'] = sum(len(tag_list) for tag_list in tags.values())
                        entry['tagging_timestamp'] = self._get_timestamp()
                        
                        tagged_entries.append(entry)
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"File not found: {jsonl_file}")
            return []
        
        return tagged_entries
    
    def get_tag_statistics(self, tagged_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about tag distribution"""
        stats = {
            "total_entries": len(tagged_entries),
            "tag_distribution": {},
            "category_coverage": {},
            "most_common_tags": {}
        }
        
        # Count tags by category
        for entry in tagged_entries:
            tags = entry.get('content_tags', {})
            
            for category, tag_list in tags.items():
                if category not in stats["tag_distribution"]:
                    stats["tag_distribution"][category] = {}
                
                for tag in tag_list:
                    if tag not in stats["tag_distribution"][category]:
                        stats["tag_distribution"][category][tag] = 0
                    stats["tag_distribution"][category][tag] += 1
        
        # Calculate coverage percentages
        for category, tag_counts in stats["tag_distribution"].items():
            total_tagged = sum(tag_counts.values())
            stats["category_coverage"][category] = (total_tagged / len(tagged_entries)) * 100
            
            # Find most common tags in category
            most_common = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            stats["most_common_tags"][category] = most_common
        
        return stats
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """CLI interface for auto-tagging"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Tagging Pipeline')
    parser.add_argument('--file', '-f', required=True, help='JSONL file to tag')
    parser.add_argument('--output', '-o', help='Output file for tagged data')
    parser.add_argument('--stats', action='store_true', help='Show tagging statistics')
    parser.add_argument('--category', '-c', help='Filter by specific tag category')
    
    args = parser.parse_args()
    
    tagger = AutoTagger()
    
    # Tag the data
    print(f"🏷️ Tagging content in: {args.file}")
    tagged_entries = tagger.tag_scraped_data(Path(args.file))
    
    if not tagged_entries:
        print("❌ No entries to tag")
        return
    
    # Show statistics
    if args.stats:
        stats = tagger.get_tag_statistics(tagged_entries)
        
        print(f"\n📊 Tagging Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"\n🏷️ Category Coverage:")
        
        for category, coverage in stats['category_coverage'].items():
            print(f"  {category}: {coverage:.1f}%")
            
            # Show most common tags
            if category in stats['most_common_tags']:
                common_tags = stats['most_common_tags'][category]
                tag_info = ", ".join([f"{tag}({count})" for tag, count in common_tags])
                print(f"    Most common: {tag_info}")
    
    # Filter by category if specified
    if args.category:
        filtered_entries = []
        for entry in tagged_entries:
            tags = entry.get('content_tags', {})
            if args.category in tags and tags[args.category]:
                filtered_entries.append(entry)
        
        print(f"🔍 Filtered to {len(filtered_entries)} entries with '{args.category}' tags")
        tagged_entries = filtered_entries
    
    # Save output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in tagged_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"💾 Saved {len(tagged_entries)} tagged entries to: {output_path}")
    else:
        print(f"✅ Tagged {len(tagged_entries)} entries")


if __name__ == "__main__":
    main()