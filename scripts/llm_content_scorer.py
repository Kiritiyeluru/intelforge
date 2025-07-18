#!/usr/bin/env python3
"""
LLM Content Scorer - AI-powered content relevance scoring
Evaluates content quality and relevance for trading strategy research

Usage:
    python scripts/llm_content_scorer.py --file content.md --criteria trading_strategy
    python scripts/llm_content_scorer.py --text "momentum trading strategy" --criteria backtesting
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import openai
import yaml
from anthropic import Anthropic

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


class LLMContentScorer:
    """AI-powered content relevance scoring system"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.openai_client = None
        self.anthropic_client = None

        # Initialize AI clients
        self._initialize_ai_clients()

    def _initialize_ai_clients(self):
        """Initialize OpenAI and Anthropic clients"""
        try:
            # Try to get API keys from config or environment
            openai_key = self.config.get("ai", {}).get("openai", {}).get(
                "api_key"
            ) or os.getenv("OPENAI_API_KEY")

            claude_key = self.config.get("ai", {}).get("claude", {}).get(
                "api_key"
            ) or os.getenv("ANTHROPIC_API_KEY")

            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
                print("✅ OpenAI client initialized")

            if claude_key:
                self.anthropic_client = Anthropic(api_key=claude_key)
                print("✅ Anthropic client initialized")

        except Exception as e:
            print(f"⚠️ Error initializing AI clients: {e}")

    def score_content(self, content: str, criteria: List[str]) -> Dict[str, Any]:
        """Score content based on specified criteria"""

        # Try Claude first, then OpenAI
        if self.anthropic_client:
            return self._score_with_claude(content, criteria)
        elif self.openai_client:
            return self._score_with_openai(content, criteria)
        else:
            return self._score_with_local_heuristics(content, criteria)

    def _score_with_claude(self, content: str, criteria: List[str]) -> Dict[str, Any]:
        """Score content using Claude API"""
        try:
            prompt = self._build_scoring_prompt(content, criteria)

            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            return self._parse_scoring_response(response.content[0].text)

        except Exception as e:
            print(f"❌ Claude scoring error: {e}")
            return self._score_with_local_heuristics(content, criteria)

    def _score_with_openai(self, content: str, criteria: List[str]) -> Dict[str, Any]:
        """Score content using OpenAI API"""
        try:
            prompt = self._build_scoring_prompt(content, criteria)

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
            )

            return self._parse_scoring_response(response.choices[0].message.content)

        except Exception as e:
            print(f"❌ OpenAI scoring error: {e}")
            return self._score_with_local_heuristics(content, criteria)

    def _build_scoring_prompt(self, content: str, criteria: List[str]) -> str:
        """Build prompt for content scoring"""
        criteria_descriptions = {
            "trading_strategy": "Contains concrete trading strategy with clear entry/exit rules",
            "technical_analysis": "Discusses technical indicators, chart patterns, or market analysis",
            "backtesting": "Includes backtesting methodology, results, or performance metrics",
            "algorithmic_trading": "Covers automated trading systems, algorithms, or quantitative methods",
            "risk_management": "Addresses risk management techniques, position sizing, or portfolio protection",
            "quantitative_finance": "Uses mathematical models, statistical analysis, or quantitative research",
            "code_implementation": "Provides actual code, libraries, or implementation details",
            "market_insights": "Offers valuable market observations, trends, or analysis",
        }

        criteria_text = "\n".join(
            [
                f"- {criterion}: {criteria_descriptions.get(criterion, 'General relevance to this topic')}"
                for criterion in criteria
            ]
        )

        prompt = f"""
Analyze the following content and score it for relevance to algorithmic trading research.

CONTENT TO ANALYZE:
{content[:2000]}...

SCORING CRITERIA:
{criteria_text}

Please provide scores from 1-5 for each criterion where:
- 1 = Not relevant at all
- 2 = Slightly relevant
- 3 = Moderately relevant
- 4 = Highly relevant
- 5 = Extremely relevant and valuable

Also provide:
- An overall score (1-5)
- Brief reasoning for the scores
- Key insights or valuable information identified

Format your response as JSON:
{{
    "overall_score": <number>,
    "criteria_scores": {{
        "criterion_name": <score>,
        ...
    }},
    "reasoning": "<brief explanation>",
    "key_insights": ["<insight1>", "<insight2>", ...],
    "content_type": "<article/code/research_paper/blog_post/etc>",
    "actionable": <true/false>
}}
"""
        return prompt

    def _parse_scoring_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured scoring data"""
        try:
            # Try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # Fallback parsing
        return {
            "overall_score": 3.0,
            "criteria_scores": {},
            "reasoning": "Unable to parse LLM response",
            "key_insights": [],
            "content_type": "unknown",
            "actionable": False,
        }

    def _score_with_local_heuristics(
        self, content: str, criteria: List[str]
    ) -> Dict[str, Any]:
        """Fallback scoring using local heuristics"""
        content_lower = content.lower()

        # Keyword-based scoring
        keyword_weights = {
            "trading_strategy": ["strategy", "entry", "exit", "signal", "rule"],
            "technical_analysis": [
                "indicator",
                "rsi",
                "macd",
                "bollinger",
                "moving average",
            ],
            "backtesting": ["backtest", "performance", "sharpe", "drawdown", "return"],
            "algorithmic_trading": ["algorithm", "automated", "bot", "quantitative"],
            "risk_management": ["risk", "position size", "stop loss", "portfolio"],
            "code_implementation": ["python", "import", "def", "class", "function"],
            "market_insights": [
                "market",
                "trend",
                "analysis",
                "insight",
                "observation",
            ],
        }

        scores = {}
        total_score = 0

        for criterion in criteria:
            if criterion in keyword_weights:
                keywords = keyword_weights[criterion]
                keyword_count = sum(
                    1 for keyword in keywords if keyword in content_lower
                )
                score = min(5, max(1, keyword_count * 0.8 + 2))
                scores[criterion] = score
                total_score += score

        overall_score = total_score / len(criteria) if criteria else 3.0

        return {
            "overall_score": round(overall_score, 1),
            "criteria_scores": scores,
            "reasoning": "Local heuristic-based scoring using keyword matching",
            "key_insights": ["Local analysis - limited insights available"],
            "content_type": "text",
            "actionable": overall_score >= 3.5,
        }

    def score_file(self, file_path: Path, criteria: List[str]) -> Dict[str, Any]:
        """Score content from a file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            result = self.score_content(content, criteria)
            result["source_file"] = str(file_path)
            result["file_size"] = file_path.stat().st_size

            return result

        except Exception as e:
            return {
                "error": f"Failed to score file {file_path}: {e}",
                "overall_score": 0,
                "criteria_scores": {},
                "reasoning": "File reading error",
            }

    def batch_score_directory(
        self, directory: Path, criteria: List[str], file_pattern: str = "*.md"
    ) -> List[Dict[str, Any]]:
        """Score all files in a directory"""
        results = []

        for file_path in directory.glob(file_pattern):
            if file_path.is_file():
                print(f"📊 Scoring: {file_path.name}")
                result = self.score_file(file_path, criteria)
                results.append(result)

        return results


def main():
    parser = argparse.ArgumentParser(description="LLM Content Scorer")
    parser.add_argument("--file", "-f", help="File to score")
    parser.add_argument("--text", "-t", help="Text content to score")
    parser.add_argument("--directory", "-d", help="Directory to batch score")
    parser.add_argument(
        "--criteria",
        "-c",
        nargs="+",
        default=["trading_strategy", "technical_analysis", "backtesting"],
        help="Scoring criteria",
    )
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument(
        "--threshold",
        default=3.5,
        type=float,
        help="Minimum score threshold for filtering",
    )

    args = parser.parse_args()

    if not args.file and not args.text and not args.directory:
        print("❌ Must provide --file, --text, or --directory")
        sys.exit(1)

    # Load configuration
    config = load_config()

    # Initialize scorer
    scorer = LLMContentScorer(config)

    results = []

    if args.file:
        # Score single file
        file_path = Path(args.file)
        result = scorer.score_file(file_path, args.criteria)
        results.append(result)

    elif args.text:
        # Score text content
        result = scorer.score_content(args.text, args.criteria)
        results.append(result)

    elif args.directory:
        # Batch score directory
        directory = Path(args.directory)
        results = scorer.batch_score_directory(directory, args.criteria)

    # Filter by threshold
    filtered_results = [
        r for r in results if r.get("overall_score", 0) >= args.threshold
    ]

    # Display results
    print(f"\n📈 Scoring Results (threshold: {args.threshold}):")
    print("=" * 60)

    for result in filtered_results:
        print(f"\n📊 Overall Score: {result.get('overall_score', 'N/A')}/5")

        if "source_file" in result:
            print(f"📁 File: {result['source_file']}")

        criteria_scores = result.get("criteria_scores", {})
        if criteria_scores:
            print("📋 Criteria Scores:")
            for criterion, score in criteria_scores.items():
                print(f"  {criterion}: {score}/5")

        if result.get("reasoning"):
            print(f"💭 Reasoning: {result['reasoning']}")

        if result.get("key_insights"):
            print(f"🔍 Key Insights: {', '.join(result['key_insights'])}")

        if result.get("actionable"):
            print("✅ Actionable: Yes")

        print("-" * 40)

    print(f"\n📊 Summary: {len(filtered_results)} items above threshold")

    # Save results if output specified
    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(filtered_results, f, indent=2)
        print(f"💾 Results saved to: {output_path}")


if __name__ == "__main__":
    main()
