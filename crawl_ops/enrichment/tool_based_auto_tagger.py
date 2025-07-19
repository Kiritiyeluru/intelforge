#!/usr/bin/env python3
"""
Tool-First Auto-Tagging Component (50 LOC vs 490 LOC custom)
Using spaCy + rapidfuzz instead of custom rule engine
"""

import spacy
from spacy.matcher import Matcher
from rapidfuzz import fuzz, process
from typing import List, Set
import json
from pathlib import Path
from datetime import datetime

class ToolBasedAutoTagger:
    """Auto-tagger using spaCy + rapidfuzz instead of custom rules"""

    def __init__(self):
        """Initialize spaCy and define patterns"""
        self.nlp = spacy.load("en_core_web_sm")
        self.matcher = Matcher(self.nlp.vocab)

        # Define trading patterns using spaCy's pattern syntax
        trading_patterns = [
            [{"LOWER": {"IN": ["strategy", "algorithm", "trading", "backtest"]}}],
            [{"LOWER": {"IN": ["python", "numpy", "pandas", "scipy"]}}],
            [{"LOWER": {"IN": ["momentum", "mean", "reversion", "arbitrage"]}}],
            [{"LOWER": {"IN": ["options", "futures", "equities", "forex"]}}],
            [{"LOWER": {"IN": ["rsi", "macd", "bollinger", "stochastic"]}}],
            [{"LOWER": {"IN": ["risk", "portfolio", "optimization"]}}]
        ]

        self.matcher.add("TRADING_TERMS", trading_patterns)

        # Known tags for fuzzy matching (rapidfuzz)
        self.known_tags = {
            "tutorial", "strategy", "theory", "implementation", "news",
            "beginner", "intermediate", "advanced", "options", "futures",
            "equities", "python", "cpp", "momentum", "mean_reversion",
            "arbitrage", "risk_management", "portfolio", "backtest",
            "technical_analysis", "fundamental_analysis", "quant"
        }

    def auto_tag_content(self, content: str, title: str, url: str) -> List[str]:
        """Extract tags using spaCy + rapidfuzz (50 LOC vs 490 LOC custom)"""

        # Process content with spaCy
        doc = self.nlp(content)

        # Extract matches using spaCy matcher
        matches = self.matcher(doc)
        spacy_tags = [doc[start:end].text.lower().replace(" ", "_")
                     for match_id, start, end in matches]

        # Use rapidfuzz for fuzzy tag matching (10-20x faster than difflib)
        fuzzy_tags = []
        content_lower = content.lower()

        for tag in self.known_tags:
            # Check if tag appears in content with fuzzy matching
            if fuzz.partial_ratio(tag.replace("_", " "), content_lower) > 80:
                fuzzy_tags.append(tag)

        # URL-based tagging
        url_tags = []
        if "tutorial" in url.lower():
            url_tags.append("tutorial")
        if "strategy" in url.lower():
            url_tags.append("strategy")
        if "python" in url.lower():
            url_tags.append("python")

        # Title-based tagging
        title_tags = []
        title_lower = title.lower()
        if any(word in title_lower for word in ["beginner", "introduction", "basics"]):
            title_tags.append("beginner")
        if any(word in title_lower for word in ["advanced", "expert", "professional"]):
            title_tags.append("advanced")

        # Combine and deduplicate
        all_tags = set(spacy_tags + fuzzy_tags + url_tags + title_tags)

        # Filter out single characters and very short tags
        filtered_tags = [tag for tag in all_tags if len(tag) > 2]

        return sorted(list(set(filtered_tags)))

    def tag_scraped_data(self, jsonl_file: Path) -> List[dict]:
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

                        # Generate tags using tool-first approach
                        tags = self.auto_tag_content(content, title, url)

                        # Add tags to entry
                        entry['content_tags'] = tags
                        entry['tag_count'] = len(tags)
                        entry['tagging_timestamp'] = datetime.now().isoformat()

                        tagged_entries.append(entry)

                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue

        except FileNotFoundError:
            print(f"File not found: {jsonl_file}")
            return []

        return tagged_entries

def main():
    """Test the tool-based auto-tagger"""
    tagger = ToolBasedAutoTagger()

    test_content = """
    This tutorial covers momentum trading strategies using Python.
    We'll implement RSI and MACD indicators for algorithmic trading.
    The strategy focuses on mean reversion in equity markets.
    """

    tags = tagger.auto_tag_content(
        content=test_content,
        title="Python Momentum Trading Tutorial",
        url="https://example.com/python-tutorial-momentum"
    )

    print("Extracted tags:", tags)

if __name__ == "__main__":
    main()
