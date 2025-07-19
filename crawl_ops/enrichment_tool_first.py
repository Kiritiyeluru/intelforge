#!/usr/bin/env python3
"""
Tool-First Content Enrichment Pipeline for IntelForge
Replaces 2,620 lines of custom code with 150 lines using proven libraries.
Philosophy: REUSE OVER REBUILD
"""

from pathlib import Path
import orjson as json
from typing import List, Optional
from flashtext import KeywordProcessor
import yake
from pydantic import BaseModel, Field
import spacy
import textstat

# Load spaCy and YAKE
nlp = spacy.load("en_core_web_sm")
kw_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.7, top=5)

# FlashText for strategy keyword extraction
keyword_processor = KeywordProcessor()
strategy_terms = ["RSI", "MACD", "bollinger bands", "moving average", "sharpe ratio", "drawdown"]
for term in strategy_terms:
    keyword_processor.add_keyword(term)

# -----------------------------
# Schema using Pydantic
# -----------------------------
class EnrichedContent(BaseModel):
    url: str
    title: str
    content: str
    content_length: int = Field(..., ge=0)
    quality_score: float = Field(..., ge=0, le=100)
    keywords: List[str]
    strategy_keywords: List[str]
    readability_score: float
    tags: List[str] = []

# -----------------------------
# Utility Functions
# -----------------------------
def calculate_quality_score(content: str) -> float:
    length_score = min(len(content) / 10000, 1.0) * 50
    readability_score = max(0, min(100 - textstat.flesch_kincaid_grade(content) * 5, 50))
    return round(length_score + readability_score, 2)

def extract_keywords(content: str, top_n: int = 5) -> List[str]:
    keywords = kw_extractor.extract_keywords(content)
    return [kw[0] for kw in keywords[:top_n]]

def extract_tags(doc) -> List[str]:
    tags = set()
    if any(token.pos_ == "VERB" for token in doc):
        tags.add("tutorial")
    if any(tok.lower_ in ("trading", "strategy") for tok in doc):
        tags.add("strategy")
    if any(tok.lower_ in ("python", "code") for tok in doc):
        tags.add("implementation")
    return list(tags)

def process_entry(entry: dict) -> Optional[EnrichedContent]:
    content = entry.get("content", "")
    if len(content) < 200:
        return None

    doc = nlp(content[:1000])
    quality_score = calculate_quality_score(content)
    keywords = extract_keywords(content)
    strategy_keywords = keyword_processor.extract_keywords(content)
    readability_score = textstat.flesch_reading_ease(content)
    tags = extract_tags(doc)

    return EnrichedContent(
        url=entry.get("url", ""),
        title=entry.get("title", ""),
        content=content,
        content_length=len(content),
        quality_score=quality_score,
        keywords=keywords,
        strategy_keywords=strategy_keywords,
        readability_score=readability_score,
        tags=tags,
    )

# -----------------------------
# Main pipeline function
# -----------------------------
def enrich_jsonl(input_path: Path, output_path: Path):
    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            try:
                entry = json.loads(line)
                enriched = process_entry(entry)
                if enriched:
                    fout.write(enriched.json() + "\n")
            except Exception as e:
                print(f"Error processing entry: {e}")

# -----------------------------
# CLI Runner Example
# -----------------------------
if __name__ == "__main__":
    input_file = Path("/home/kiriti/alpha_projects/intelforge/crawl_ops/data_runs/20250719/scraped_data.jsonl")
    output_file = Path("/home/kiriti/alpha_projects/intelforge/crawl_ops/data_runs/20250719/enriched_data.jsonl")
    enrich_jsonl(input_file, output_file)
