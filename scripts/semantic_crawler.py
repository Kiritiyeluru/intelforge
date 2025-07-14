#!/usr/bin/env python3
"""
Semantic Crawler with AI-Filtered Capture
Purpose: Intelligent content curation using embeddings and cosine similarity
Usage: python semantic_crawler.py --url-file urls.txt [--threshold 0.75] [--dry-run]
"""

import httpx
import asyncio
import json
import time
import hashlib
import uuid
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

# Core extraction and AI libraries
from trafilatura import extract
from selectolax.parser import HTMLParser
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams

# ─────────────────────────────────────────────────────────────────
# 🔧 Configuration

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "semantic_capture"
REFERENCE_VECTOR_PATH = "scripts/reference_embeddings.json"
DEFAULT_THRESHOLD = 0.75
MIN_CONTENT_LENGTH = 300

# ─────────────────────────────────────────────────────────────────
# 🧠 AI Models & Storage Initialization

print("🧠 Loading AI models...")
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"✅ Loaded embedding model: {EMBEDDING_MODEL}")

# Initialize Qdrant client
qdrant_client = QdrantClient(path="./qdrant_storage")

# Ensure collection exists
try:
    collections = [c.name for c in qdrant_client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        print(f"✅ Created Qdrant collection: {COLLECTION_NAME}")
    else:
        print(f"✅ Using existing Qdrant collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"⚠️ Qdrant initialization warning: {e}")

# ─────────────────────────────────────────────────────────────────
# 📚 Reference Vector Management


def create_reference_embeddings():
    """Create reference embeddings for training the semantic filter"""

    # High-quality training examples for momentum trading strategies
    training_content = [
        "momentum trading strategy using moving averages and RSI indicators for algorithmic backtesting",
        "quantitative finance research with statistical analysis of momentum factors in equity markets",
        "Python implementation of vectorbt backtesting framework for trading strategy validation",
        "technical analysis indicators including MACD, Bollinger Bands, and stochastic oscillators",
        "algorithmic trading system design with risk management and position sizing algorithms",
        "machine learning applications in quantitative finance for alpha generation and strategy optimization",
    ]

    print("🔬 Generating reference embeddings from training content...")
    embeddings = []

    for content in training_content:
        embedding = model.encode(content)
        embeddings.append(embedding)
        print(f"  ✅ Encoded: {content[:50]}...")

    # Average the embeddings to create a reference vector
    reference_vector = np.mean(embeddings, axis=0).tolist()

    # Save reference vector
    Path("scripts").mkdir(exist_ok=True)
    with open(REFERENCE_VECTOR_PATH, "w") as f:
        json.dump(
            {
                "embedding": reference_vector,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "model": EMBEDDING_MODEL,
                "training_samples": len(training_content),
            },
            f,
            indent=2,
        )

    print(f"✅ Reference embeddings saved to: {REFERENCE_VECTOR_PATH}")
    return reference_vector


def load_reference_vector():
    """Load reference vector for semantic comparison"""
    if not Path(REFERENCE_VECTOR_PATH).exists():
        print("📚 Reference embeddings not found, creating new ones...")
        return create_reference_embeddings()

    try:
        with open(REFERENCE_VECTOR_PATH, "r") as f:
            data = json.load(f)
        print(
            f"✅ Loaded reference embeddings (created: {data.get('created_at', 'unknown')})"
        )
        return data["embedding"]
    except Exception as e:
        print(f"❌ Error loading reference embeddings: {e}")
        print("📚 Creating new reference embeddings...")
        return create_reference_embeddings()


# Load reference vector
reference_vector = load_reference_vector()

# ─────────────────────────────────────────────────────────────────
# 🌐 Async Content Fetching


async def fetch_url(client: httpx.AsyncClient, url: str) -> tuple[Optional[str], str]:
    """Fetch content from a single URL with error handling"""
    try:
        response = await client.get(url, timeout=20)
        response.raise_for_status()
        return response.text, url
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None, url


async def fetch_all_urls(urls: List[str]) -> List[tuple[Optional[str], str]]:
    """Fetch content from multiple URLs concurrently"""
    print(f"🌐 Fetching {len(urls)} URLs concurrently...")

    async with httpx.AsyncClient(headers=HEADERS, http2=True) as client:
        tasks = [fetch_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and return valid results
    valid_results = []
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Request failed: {result}")
        else:
            valid_results.append(result)

    print(f"✅ Successfully fetched {len(valid_results)} pages")
    return valid_results


# ─────────────────────────────────────────────────────────────────
# ✂️ Content Extraction


def parse_content(html: str, url: str) -> Dict[str, Any]:
    """Extract structured content from HTML"""
    try:
        # Parse with selectolax for metadata
        dom = HTMLParser(html)
        title = dom.css_first("title")
        title_text = title.text() if title else "Untitled"

        # Extract main content with trafilatura
        main_content = extract(html)

        if not main_content:
            # Fallback extraction
            body = dom.css_first("body")
            main_content = body.text() if body else ""

        return {
            "url": url,
            "title": title_text.strip(),
            "content": main_content.strip() if main_content else "",
            "content_length": len(main_content) if main_content else 0,
            "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    except Exception as e:
        print(f"❌ Parse error for {url}: {e}")
        return {
            "url": url,
            "title": "Parse Error",
            "content": "",
            "content_length": 0,
            "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────
# 🧠 AI-Based Relevance Filtering


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors"""
    # Ensure vectors are numpy arrays
    v1, v2 = np.array(vec1), np.array(vec2)

    # Calculate cosine similarity
    dot_product = np.dot(v1, v2)
    norm_product = np.linalg.norm(v1) * np.linalg.norm(v2)

    if norm_product == 0:
        return 0.0

    return float(dot_product / norm_product)


def is_content_relevant(
    content: str, threshold: float = DEFAULT_THRESHOLD
) -> tuple[bool, float]:
    """Determine if content is relevant using semantic similarity"""

    # Basic content quality checks
    if not content or len(content) < MIN_CONTENT_LENGTH:
        return False, 0.0

    # Generate embedding for the content
    try:
        content_vector = model.encode(content)
        similarity_score = cosine_similarity(content_vector, reference_vector)

        is_relevant = similarity_score >= threshold
        return is_relevant, similarity_score

    except Exception as e:
        print(f"❌ Embedding error: {e}")
        return False, 0.0


# ─────────────────────────────────────────────────────────────────
# 💾 Storage Functions


def save_to_markdown(data: Dict[str, Any], similarity_score: float) -> tuple[str, str]:
    """Save content to Obsidian-compatible markdown with metadata"""

    # Create output directory
    output_dir = Path("vault/notes/semantic_capture")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    timestamp = str(int(time.time()))
    url_hash = hashlib.md5(data["url"].encode()).hexdigest()[:8]
    filename = f"semantic_{timestamp}_{url_hash}"
    md_filepath = output_dir / f"{filename}.md"
    metadata_filepath = output_dir / f"{filename}.metadata.json"

    # Generate content hash
    content_hash = hashlib.sha256(data["content"].encode()).hexdigest()[:16]

    # Extract basic tags from content
    content_lower = data["content"].lower()
    extracted_tags = []

    # Financial strategy tags
    strategy_keywords = {
        "momentum": ["momentum", "moving average", "trend following"],
        "mean_reversion": ["mean reversion", "reversal", "overbought", "oversold"],
        "technical_analysis": ["rsi", "macd", "bollinger", "stochastic", "indicator"],
        "backtesting": ["backtest", "historical", "simulation", "performance"],
        "python": ["python", "pandas", "numpy", "matplotlib"],
        "quantitative": ["quantitative", "statistical", "mathematical", "algorithm"],
    }

    for tag, keywords in strategy_keywords.items():
        if any(keyword in content_lower for keyword in keywords):
            extracted_tags.append(tag)

    # Create metadata
    metadata = {
        "title": data["title"],
        "url": data["url"],
        "score": round(similarity_score, 3),
        "filter_method": "cosine_similarity",
        "tags": extracted_tags,
        "captured_at": data["extracted_at"],
        "content_hash": content_hash,
        "content_length": data["content_length"],
        "source": "semantic_crawler",
        "qdrant_embedded": False,  # Will be updated when embedded
    }

    # Create markdown content with YAML frontmatter
    markdown_content = f"""---
title: "{data["title"]}"
url: "{data["url"]}"
date: "{time.strftime("%Y-%m-%d")}"
extracted_at: "{data["extracted_at"]}"
similarity_score: {similarity_score:.3f}
content_length: {data["content_length"]}
source: "semantic_crawler"
tags: {extracted_tags}
content_hash: "{content_hash}"
---

# {data["title"]}

**URL**: {data["url"]}  
**Similarity Score**: {similarity_score:.3f}  
**Tags**: {", ".join(extracted_tags) if extracted_tags else "None detected"}  
**Extracted**: {data["extracted_at"]}

---

{data["content"]}
"""

    # Write markdown file
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    # Write metadata file
    with open(metadata_filepath, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"💾 Saved: {md_filepath}")
    print(f"📋 Metadata: {metadata_filepath}")
    return str(md_filepath), str(metadata_filepath)


def embed_to_qdrant(
    markdown_file: str,
    metadata_file: str,
    data: Dict[str, Any],
    similarity_score: float,
):
    """Embed content into Qdrant vector database and update metadata"""
    try:
        # Generate embedding for storage
        content_vector = model.encode(data["content"]).tolist()

        # Create payload with metadata
        payload = {
            "source_file": markdown_file,
            "metadata_file": metadata_file,
            "url": data["url"],
            "title": data["title"],
            "similarity_score": similarity_score,
            "content_length": data["content_length"],
            "extracted_at": data["extracted_at"],
            "content_preview": data["content"][:300] + "..."
            if len(data["content"]) > 300
            else data["content"],
        }

        # Generate unique ID
        unique_id = uuid.uuid4().int >> 64

        # Store in Qdrant
        qdrant_client.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(id=unique_id, vector=content_vector, payload=payload)],
        )

        # Update metadata to reflect embedding status
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            metadata["qdrant_embedded"] = True
            metadata["qdrant_id"] = unique_id
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as meta_error:
            print(f"⚠️ Failed to update metadata: {meta_error}")

        print(f"🔍 Embedded to Qdrant: {data['title'][:50]}...")

    except Exception as e:
        print(f"❌ Qdrant embedding error: {e}")


# ─────────────────────────────────────────────────────────────────
# 🚀 Main Semantic Crawler


def run_semantic_crawler(
    urls: List[str], threshold: float = DEFAULT_THRESHOLD, dry_run: bool = False
):
    """Main crawler function with AI filtering"""

    print("🧠 Starting Semantic Crawler")
    print(f"📊 URLs to process: {len(urls)}")
    print(f"🎯 Similarity threshold: {threshold}")
    print(f"🧪 Dry run mode: {dry_run}")
    print("-" * 60)

    # Fetch all URLs
    results = asyncio.run(fetch_all_urls(urls))

    # Process each result
    processed_count = 0
    relevant_count = 0
    similarity_scores = []

    for html, url in results:
        if not html:
            continue

        processed_count += 1
        print(f"\n📄 Processing {processed_count}/{len(results)}: {url}")

        # Extract content
        parsed_data = parse_content(html, url)

        if not parsed_data["content"]:
            print("  ❌ No content extracted")
            continue

        # Check relevance with AI
        is_relevant, similarity_score = is_content_relevant(
            parsed_data["content"], threshold
        )
        similarity_scores.append(similarity_score)

        print(f"  🧠 Similarity score: {similarity_score:.3f}")
        print(f"  📏 Content length: {parsed_data['content_length']} chars")

        if is_relevant:
            relevant_count += 1
            print("  ✅ RELEVANT - Capturing content")

            if not dry_run:
                # Save to markdown with metadata
                markdown_file, metadata_file = save_to_markdown(
                    parsed_data, similarity_score
                )

                # Embed to Qdrant
                embed_to_qdrant(
                    markdown_file, metadata_file, parsed_data, similarity_score
                )
            else:
                print(f"  🧪 DRY RUN - Would save: {parsed_data['title']}")
        else:
            print(f"  ❌ Not relevant (threshold: {threshold})")

    # Summary statistics
    print("\n" + "=" * 60)
    print("📊 SEMANTIC CRAWLER SUMMARY")
    print("=" * 60)
    print(f"URLs processed: {processed_count}")
    print(f"Content captured: {relevant_count}")
    print(
        f"Capture rate: {(relevant_count / processed_count * 100):.1f}%"
        if processed_count > 0
        else "N/A"
    )

    if similarity_scores:
        print(f"Average similarity: {np.mean(similarity_scores):.3f}")
        print(
            f"Similarity range: {np.min(similarity_scores):.3f} - {np.max(similarity_scores):.3f}"
        )

    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60)


# ─────────────────────────────────────────────────────────────────
# 🔧 CLI Interface


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Semantic Crawler with AI-Filtered Capture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python semantic_crawler.py --url-file urls.txt
  python semantic_crawler.py --url-file test_urls.txt --threshold 0.8 --dry-run
  python semantic_crawler.py --url-file discover_results.txt --threshold 0.7
        """,
    )

    parser.add_argument(
        "--url-file",
        "-f",
        required=True,
        help="Text file containing URLs to crawl (one per line)",
    )

    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=f"Similarity threshold for content relevance (default: {DEFAULT_THRESHOLD})",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mode - analyze content but don't save anything",
    )

    parser.add_argument(
        "--regenerate-reference",
        action="store_true",
        help="Regenerate reference embeddings from training data",
    )

    args = parser.parse_args()

    # Regenerate reference embeddings if requested
    if args.regenerate_reference:
        print("🔄 Regenerating reference embeddings...")
        create_reference_embeddings()
        print("✅ Reference embeddings updated")
        return

    # Load URLs from file
    try:
        with open(args.url_file, "r") as f:
            urls = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        if not urls:
            print(f"❌ No URLs found in {args.url_file}")
            return

    except FileNotFoundError:
        print(f"❌ URL file not found: {args.url_file}")
        return
    except Exception as e:
        print(f"❌ Error reading URL file: {e}")
        return

    # Run semantic crawler
    run_semantic_crawler(urls, args.threshold, args.dry_run)


if __name__ == "__main__":
    main()
