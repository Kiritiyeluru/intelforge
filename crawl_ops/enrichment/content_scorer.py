#!/usr/bin/env python3
"""
Content Scoring System for IntelForge Data Enrichment Pipeline

Implements the quality scoring algorithm described in the data enrichment plan.
Integrates with existing llm_content_scorer.py for AI-powered scoring.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.llm_content_scorer import LLMContentScorer, load_config


class ContentScorer:
    """Content scoring system with both heuristic and AI-powered scoring"""
    
    def __init__(self):
        self.config = load_config()
        self.llm_scorer = LLMContentScorer(self.config)
        
        # Trading keywords for heuristic scoring
        self.trading_keywords = [
            "strategy", "backtest", "algorithm", "trading", 
            "portfolio", "risk", "volatility", "signal",
            "momentum", "mean reversion", "arbitrage"
        ]
        
        self.tech_keywords = [
            "python", "c++", "numpy", "pandas", "API",
            "quantlib", "zipline", "backtesting"
        ]
        
        self.math_keywords = [
            "regression", "statistics", "monte carlo", "optimization",
            "sharpe", "drawdown", "correlation", "variance"
        ]
    
    def calculate_content_score(self, content: str, title: str = "", url: str = "") -> Dict[str, Any]:
        """
        Calculate comprehensive content score using multiple scoring methods
        
        Returns score from 0-100 based on:
        - Content length (0-30 points)
        - Keyword presence (0-40 points) 
        - Implementation indicators (0-30 points)
        """
        
        # Start with heuristic scoring
        heuristic_score = self._calculate_heuristic_score(content, title, url)
        
        # Try to get AI score if available
        ai_score = self._get_ai_score(content)
        
        # Combine scores (weighted average)
        if ai_score is not None:
            # 70% AI score, 30% heuristic score
            final_score = (ai_score * 0.7) + (heuristic_score * 0.3)
            scoring_method = "hybrid"
        else:
            final_score = heuristic_score
            scoring_method = "heuristic"
        
        return {
            "overall_score": round(final_score, 1),
            "heuristic_score": heuristic_score,
            "ai_score": ai_score,
            "scoring_method": scoring_method,
            "content_length": len(content),
            "title_relevance": self._score_title_relevance(title),
            "code_presence": self._detect_code_presence(content),
            "timestamp": self._get_timestamp()
        }
    
    def _calculate_heuristic_score(self, content: str, title: str, url: str) -> float:
        """Calculate heuristic score based on content analysis"""
        score = 0
        content_lower = content.lower()
        title_lower = title.lower()
        
        # Length scoring (0-30 points)
        content_length = len(content)
        if content_length > 10000:
            score += 30
        elif content_length > 5000:
            score += 20
        elif content_length > 1000:
            score += 10
        elif content_length > 500:
            score += 5
        
        # Keyword presence scoring (0-40 points)
        trading_matches = sum(1 for keyword in self.trading_keywords 
                            if keyword in content_lower or keyword in title_lower)
        tech_matches = sum(1 for keyword in self.tech_keywords 
                         if keyword in content_lower or keyword in title_lower)
        math_matches = sum(1 for keyword in self.math_keywords 
                         if keyword in content_lower or keyword in title_lower)
        
        # Weight different types of keywords
        keyword_score = min(40, (trading_matches * 3) + (tech_matches * 2) + (math_matches * 2))
        score += keyword_score
        
        # Implementation indicators (0-30 points)
        impl_score = 0
        if "class " in content or "def " in content:
            impl_score += 15
        if "import " in content:
            impl_score += 10
        if "```" in content or "```python" in content:
            impl_score += 5
        
        score += min(30, impl_score)
        
        return min(100, score)
    
    def _get_ai_score(self, content: str) -> float:
        """Get AI-powered score if available"""
        try:
            criteria = ["trading_strategy", "technical_analysis", "backtesting", "algorithmic_trading"]
            result = self.llm_scorer.score_content(content, criteria)
            
            if result and "overall_score" in result:
                # Convert 1-5 scale to 0-100 scale
                return (result["overall_score"] - 1) * 25
        except Exception as e:
            print(f"AI scoring failed: {e}")
        
        return None
    
    def _score_title_relevance(self, title: str) -> float:
        """Score title relevance (0-10 scale)"""
        if not title:
            return 0
        
        title_lower = title.lower()
        relevance_score = 0
        
        # Check for trading-related terms in title
        title_keywords = ["trading", "strategy", "algorithm", "backtest", "quant", "portfolio"]
        for keyword in title_keywords:
            if keyword in title_lower:
                relevance_score += 2
        
        return min(10, relevance_score)
    
    def _detect_code_presence(self, content: str) -> Dict[str, Any]:
        """Detect and analyze code presence in content"""
        code_indicators = {
            "python_imports": len(re.findall(r'import \w+|from \w+ import', content)),
            "function_definitions": len(re.findall(r'def \w+\(', content)),
            "class_definitions": len(re.findall(r'class \w+', content)),
            "code_blocks": len(re.findall(r'```[\w]*\n', content)),
            "inline_code": len(re.findall(r'`[^`]+`', content))
        }
        
        total_code_score = sum(code_indicators.values())
        
        return {
            "indicators": code_indicators,
            "total_score": total_code_score,
            "has_substantial_code": total_code_score >= 5
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def score_scraped_data(self, jsonl_file: Path) -> List[Dict[str, Any]]:
        """Score all entries in a scraped data JSONL file"""
        scored_entries = []
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.strip())
                        
                        # Extract content for scoring
                        content = entry.get('content', '')
                        title = entry.get('title', '')
                        url = entry.get('url', '')
                        
                        # Calculate score
                        score_data = self.calculate_content_score(content, title, url)
                        
                        # Add scoring data to entry
                        entry['quality_score'] = score_data['overall_score']
                        entry['scoring_details'] = score_data
                        entry['enrichment_version'] = "1.0"
                        
                        scored_entries.append(entry)
                        
                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            print(f"File not found: {jsonl_file}")
            return []
        
        return scored_entries
    
    def filter_by_quality(self, scored_entries: List[Dict[str, Any]], 
                         threshold: float = 70.0) -> List[Dict[str, Any]]:
        """Filter entries by quality score threshold"""
        return [entry for entry in scored_entries 
                if entry.get('quality_score', 0) >= threshold]


def main():
    """CLI interface for content scoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Content Scoring System')
    parser.add_argument('--file', '-f', required=True, help='JSONL file to score')
    parser.add_argument('--output', '-o', help='Output file for scored data')
    parser.add_argument('--threshold', '-t', type=float, default=70.0, 
                       help='Quality threshold for filtering')
    parser.add_argument('--stats', action='store_true', 
                       help='Show scoring statistics')
    
    args = parser.parse_args()
    
    scorer = ContentScorer()
    
    # Score the data
    print(f"🔍 Scoring content in: {args.file}")
    scored_entries = scorer.score_scraped_data(Path(args.file))
    
    if not scored_entries:
        print("❌ No entries to score")
        return
    
    # Filter by quality threshold
    high_quality_entries = scorer.filter_by_quality(scored_entries, args.threshold)
    
    # Show statistics
    if args.stats:
        scores = [entry.get('quality_score', 0) for entry in scored_entries]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        print(f"\n📊 Scoring Statistics:")
        print(f"  Total entries: {len(scored_entries)}")
        print(f"  Average score: {avg_score:.1f}")
        print(f"  Max score: {max_score:.1f}")
        print(f"  Min score: {min_score:.1f}")
        print(f"  Above threshold ({args.threshold}): {len(high_quality_entries)}")
    
    # Save output
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in high_quality_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"💾 Saved {len(high_quality_entries)} high-quality entries to: {output_path}")
    else:
        print(f"✅ Scored {len(scored_entries)} entries, {len(high_quality_entries)} above threshold")


if __name__ == "__main__":
    main()