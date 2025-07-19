#!/usr/bin/env python3
"""
Strategy Keyword Extraction for IntelForge Data Enrichment

Extracts trading strategy-specific keywords and patterns:
- Strategy Names: moving average, bollinger bands, rsi, macd
- Entry/Exit Rules: buy when, sell when, stop loss, take profit
- Technical Indicators: pattern matching for indicator definitions
- Backtesting Terms: sharpe ratio, drawdown, win rate
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from collections import defaultdict

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class StrategyExtractor:
    """Strategy keyword and pattern extraction system"""

    def __init__(self):
        self.strategy_patterns = self._initialize_strategy_patterns()
        self.technical_indicators = self._initialize_technical_indicators()
        self.market_terms = self._initialize_market_terms()

    def _initialize_strategy_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for strategy extraction"""
        return {
            "indicators": [
                r"moving average|MA\s|SMA|EMA|WMA",
                r"RSI|relative strength index",
                r"MACD|moving average convergence divergence",
                r"bollinger bands?|BB",
                r"stochastic oscillator|stochastic",
                r"fibonacci retracement|fib levels",
                r"support and resistance|S&R",
                r"volume weighted average price|VWAP",
                r"average true range|ATR",
                r"commodity channel index|CCI"
            ],

            "signals": [
                r"buy signal|purchase signal|long signal|entry signal",
                r"sell signal|short signal|exit signal",
                r"crossover|cross above|cross below",
                r"breakout|breakdown|break above|break below",
                r"golden cross|death cross",
                r"bullish divergence|bearish divergence",
                r"oversold|overbought",
                r"trend reversal|trend continuation"
            ],

            "metrics": [
                r"sharpe ratio|sharpe",
                r"drawdown|maximum drawdown|max DD",
                r"volatility|vol|standard deviation",
                r"correlation|corr",
                r"beta coefficient|beta",
                r"alpha|excess return",
                r"win rate|success rate|hit ratio",
                r"profit factor|PF",
                r"calmar ratio|sterling ratio",
                r"sortino ratio|treynor ratio"
            ],

            "timeframes": [
                r"daily|1D|day trading",
                r"hourly|1H|hour",
                r"minute|1M|5M|15M|30M",
                r"weekly|1W|week",
                r"monthly|1M|month",
                r"intraday|scalping",
                r"swing trading|position trading",
                r"long term|long-term"
            ],

            "strategy_types": [
                r"momentum strategy|momentum trading",
                r"mean reversion|reverting|reversion strategy",
                r"arbitrage|statistical arbitrage|pairs trading",
                r"trend following|trend trader",
                r"breakout strategy|breakout trading",
                r"grid trading|martingale",
                r"scalping strategy|scalp",
                r"carry trade|interest rate differential",
                r"calendar spread|time spread",
                r"iron condor|butterfly spread|straddle|strangle"
            ],

            "risk_management": [
                r"stop loss|SL|stop order",
                r"take profit|TP|profit target",
                r"position sizing|position size",
                r"risk per trade|risk management",
                r"money management|capital allocation",
                r"maximum risk|risk limit",
                r"trailing stop|dynamic stop",
                r"diversification|portfolio allocation"
            ]
        }

    def _initialize_technical_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize technical indicator definitions and patterns"""
        return {
            "RSI": {
                "full_name": "Relative Strength Index",
                "type": "momentum_oscillator",
                "range": "0-100",
                "signals": ["overbought (>70)", "oversold (<30)", "divergence"],
                "pattern": r"RSI|relative strength index"
            },

            "MACD": {
                "full_name": "Moving Average Convergence Divergence",
                "type": "trend_momentum",
                "signals": ["signal line crossover", "zero line crossover", "divergence"],
                "pattern": r"MACD|moving average convergence divergence"
            },

            "Bollinger_Bands": {
                "full_name": "Bollinger Bands",
                "type": "volatility",
                "signals": ["band squeeze", "band expansion", "price touching bands"],
                "pattern": r"bollinger bands?|BB"
            },

            "Moving_Average": {
                "full_name": "Moving Average",
                "type": "trend",
                "variants": ["SMA", "EMA", "WMA"],
                "signals": ["price crossover", "MA crossover", "slope analysis"],
                "pattern": r"moving average|MA\s|SMA|EMA|WMA"
            },

            "Stochastic": {
                "full_name": "Stochastic Oscillator",
                "type": "momentum",
                "range": "0-100",
                "signals": ["overbought (>80)", "oversold (<20)", "%K %D crossover"],
                "pattern": r"stochastic oscillator|stochastic"
            }
        }

    def _initialize_market_terms(self) -> Dict[str, List[str]]:
        """Initialize market-specific terminology"""
        return {
            "order_types": [
                "market order", "limit order", "stop order", "stop limit",
                "trailing stop", "bracket order", "OCO order", "good till cancelled"
            ],

            "market_conditions": [
                "bull market", "bear market", "sideways market", "ranging market",
                "trending market", "volatile market", "low volatility", "high volatility"
            ],

            "trading_styles": [
                "day trading", "swing trading", "position trading", "scalping",
                "algorithmic trading", "quantitative trading", "systematic trading"
            ],

            "asset_classes": [
                "equities", "stocks", "bonds", "commodities", "currencies", "forex",
                "futures", "options", "derivatives", "ETFs", "mutual funds", "crypto"
            ]
        }

    def extract_strategy_keywords(self, content: str, title: str = "") -> Dict[str, Any]:
        """
        Extract strategy-related keywords and patterns from content

        Returns detailed extraction results with confidence scores
        """
        combined_text = f"{title} {content}"
        extraction_results = {
            "strategy_patterns": {},
            "technical_indicators": {},
            "market_terms": {},
            "custom_strategies": [],
            "confidence_scores": {},
            "extraction_metadata": {}
        }

        # Extract patterns using regex
        for category, patterns in self.strategy_patterns.items():
            matches = []
            for pattern in patterns:
                found_matches = re.findall(pattern, combined_text, re.IGNORECASE)
                matches.extend(found_matches)

            # Remove duplicates and clean matches
            clean_matches = list(set([match.strip() for match in matches if match.strip()]))

            if clean_matches:
                extraction_results["strategy_patterns"][category] = clean_matches
                # Confidence based on number of matches and pattern quality
                extraction_results["confidence_scores"][category] = min(1.0, len(clean_matches) * 0.2)

        # Extract technical indicators with detailed analysis
        for indicator, info in self.technical_indicators.items():
            pattern = info["pattern"]
            matches = re.findall(pattern, combined_text, re.IGNORECASE)

            if matches:
                extraction_results["technical_indicators"][indicator] = {
                    "matches": list(set(matches)),
                    "count": len(matches),
                    "full_name": info["full_name"],
                    "type": info["type"],
                    "context": self._extract_context(combined_text, pattern)
                }

        # Extract market terms
        for category, terms in self.market_terms.items():
            found_terms = []
            for term in terms:
                if term.lower() in combined_text.lower():
                    found_terms.append(term)

            if found_terms:
                extraction_results["market_terms"][category] = found_terms

        # Extract custom strategy descriptions
        custom_strategies = self._extract_custom_strategies(combined_text)
        if custom_strategies:
            extraction_results["custom_strategies"] = custom_strategies

        # Calculate counts for metadata
        total_patterns_found = sum(len(v) if isinstance(v, list) else len(v.keys())
                                 for v in extraction_results["strategy_patterns"].values())
        total_indicators_found = len(extraction_results["technical_indicators"])
        total_market_terms_found = sum(len(v) for v in extraction_results["market_terms"].values())

        # Add metadata
        extraction_results["extraction_metadata"] = {
            "total_patterns_found": total_patterns_found,
            "total_indicators_found": total_indicators_found,
            "total_market_terms_found": total_market_terms_found,
            "content_length": len(content),
            "strategy_density": self._calculate_strategy_density_direct(content, total_patterns_found, total_indicators_found, total_market_terms_found),
            "extraction_timestamp": self._get_timestamp()
        }

        return extraction_results

    def _extract_context(self, text: str, pattern: str, window: int = 50) -> List[str]:
        """Extract context around pattern matches"""
        contexts = []

        for match in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            context = text[start:end].strip()
            contexts.append(context)

        return contexts[:3]  # Limit to first 3 contexts

    def _extract_custom_strategies(self, text: str) -> List[Dict[str, Any]]:
        """Extract custom strategy descriptions and rules"""
        custom_strategies = []

        # Pattern for strategy definitions
        strategy_patterns = [
            r"(?:strategy|approach|method|system)\s+(?:is|involves|uses|consists of)\s+([^.!?]*[.!?])",
            r"(?:buy|sell|enter|exit)\s+when\s+([^.!?]*[.!?])",
            r"(?:if|when)\s+([^,]*),?\s+(?:then\s+)?(?:buy|sell|enter|exit|close)",
            r"(?:rule|condition|signal):\s*([^.!?]*[.!?])"
        ]

        for i, pattern in enumerate(strategy_patterns):
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)

            for match in matches[:5]:  # Limit to 5 matches per pattern
                custom_strategies.append({
                    "type": f"pattern_{i+1}",
                    "description": match.strip(),
                    "confidence": 0.7 if len(match.split()) > 5 else 0.5
                })

        return custom_strategies

    def _calculate_strategy_density_direct(self, content: str, total_patterns: int, total_indicators: int, total_market_terms: int) -> float:
        """Calculate strategy keyword density in content"""
        if not content:
            return 0.0

        total_keywords = total_patterns + total_indicators + total_market_terms
        word_count = len(content.split())
        return (total_keywords / word_count) * 100 if word_count > 0 else 0.0

    def extract_from_scraped_data(self, jsonl_file: Path) -> List[Dict[str, Any]]:
        """Extract strategy keywords from all entries in a scraped data JSONL file"""
        extracted_entries = []

        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.strip())

                        # Extract content for processing
                        content = entry.get('content', '')
                        title = entry.get('title', '')

                        # Extract strategy keywords
                        strategy_data = self.extract_strategy_keywords(content, title)

                        # Add extraction results to entry
                        entry['strategy_keywords'] = strategy_data["strategy_patterns"]
                        entry['technical_indicators'] = strategy_data["technical_indicators"]
                        entry['market_terms'] = strategy_data["market_terms"]
                        entry['custom_strategies'] = strategy_data["custom_strategies"]
                        entry['strategy_density'] = strategy_data["extraction_metadata"]["strategy_density"]
                        entry['extraction_confidence'] = strategy_data["confidence_scores"]

                        extracted_entries.append(entry)

                    except json.JSONDecodeError as e:
                        print(f"Error parsing line {line_num}: {e}")
                        continue

        except FileNotFoundError:
            print(f"File not found: {jsonl_file}")
            return []

        return extracted_entries

    def get_extraction_statistics(self, extracted_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about strategy keyword extraction"""
        stats = {
            "total_entries": len(extracted_entries),
            "strategy_coverage": {},
            "indicator_frequency": defaultdict(int),
            "strategy_type_distribution": defaultdict(int),
            "average_density": 0.0,
            "high_density_entries": 0
        }

        total_density = 0

        for entry in extracted_entries:
            # Strategy density analysis
            density = entry.get('strategy_density', 0)
            total_density += density

            if density > 2.0:  # High density threshold
                stats["high_density_entries"] += 1

            # Count strategy patterns
            strategy_keywords = entry.get('strategy_keywords', {})
            for category, keywords in strategy_keywords.items():
                if category not in stats["strategy_coverage"]:
                    stats["strategy_coverage"][category] = 0
                if keywords:
                    stats["strategy_coverage"][category] += 1

            # Count indicators
            indicators = entry.get('technical_indicators', {})
            for indicator in indicators.keys():
                stats["indicator_frequency"][indicator] += 1

        # Calculate averages
        if len(extracted_entries) > 0:
            stats["average_density"] = total_density / len(extracted_entries)

        # Convert defaultdicts to regular dicts for JSON serialization
        stats["indicator_frequency"] = dict(stats["indicator_frequency"])
        stats["strategy_type_distribution"] = dict(stats["strategy_type_distribution"])

        return stats

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()


def main():
    """CLI interface for strategy keyword extraction"""
    import argparse

    parser = argparse.ArgumentParser(description='Strategy Keyword Extraction')
    parser.add_argument('--file', '-f', required=True, help='JSONL file to process')
    parser.add_argument('--output', '-o', help='Output file for processed data')
    parser.add_argument('--stats', action='store_true', help='Show extraction statistics')
    parser.add_argument('--density-threshold', '-t', type=float, default=1.0,
                       help='Minimum strategy density threshold')
    parser.add_argument('--export-keywords', action='store_true',
                       help='Export unique keywords to separate file')

    args = parser.parse_args()

    extractor = StrategyExtractor()

    # Extract strategy keywords
    print(f"🔍 Extracting strategy keywords from: {args.file}")
    extracted_entries = extractor.extract_from_scraped_data(Path(args.file))

    if not extracted_entries:
        print("❌ No entries to process")
        return

    # Filter by density threshold
    high_density_entries = [
        entry for entry in extracted_entries
        if entry.get('strategy_density', 0) >= args.density_threshold
    ]

    # Show statistics
    if args.stats:
        stats = extractor.get_extraction_statistics(extracted_entries)

        print(f"\n📊 Extraction Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Average strategy density: {stats['average_density']:.2f}%")
        print(f"  High density entries (>{args.density_threshold}%): {len(high_density_entries)}")

        print(f"\n🏷️ Strategy Coverage:")
        for category, count in stats['strategy_coverage'].items():
            coverage = (count / stats['total_entries']) * 100
            print(f"  {category}: {count} entries ({coverage:.1f}%)")

        print(f"\n📈 Most Common Indicators:")
        sorted_indicators = sorted(stats['indicator_frequency'].items(),
                                 key=lambda x: x[1], reverse=True)
        for indicator, count in sorted_indicators[:5]:
            print(f"  {indicator}: {count} mentions")

    # Export unique keywords
    if args.export_keywords:
        keywords_file = Path(args.file).parent / "extracted_keywords.json"
        all_keywords = set()

        for entry in extracted_entries:
            strategy_keywords = entry.get('strategy_keywords', {})
            for keywords in strategy_keywords.values():
                if isinstance(keywords, list):
                    all_keywords.update(keywords)

        with open(keywords_file, 'w') as f:
            json.dump(sorted(list(all_keywords)), f, indent=2)
        print(f"📝 Exported {len(all_keywords)} unique keywords to: {keywords_file}")

    # Save output
    output_entries = high_density_entries if args.density_threshold > 0 else extracted_entries

    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in output_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        print(f"💾 Saved {len(output_entries)} entries to: {output_path}")
    else:
        print(f"✅ Processed {len(extracted_entries)} entries, {len(high_density_entries)} above density threshold")


if __name__ == "__main__":
    main()
