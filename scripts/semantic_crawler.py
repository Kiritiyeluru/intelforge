#!/usr/bin/env python3
"""
Semantic Crawler with AI-Filtered Capture
Purpose: Intelligent content curation using embeddings and cosine similarity
Usage: python semantic_crawler.py --url-file urls.txt [--threshold 0.75] [--dry-run]
"""

import asyncio

# Import httpx and asyncio for fallback
import httpx

# Scrapy integration for web crawling
try:
    from scripts.scrapers.scrapy_integration import (
        convert_scrapy_to_semantic_format, run_scrapy_crawler)

    SCRAPY_AVAILABLE = True
    print("✅ Scrapy integration available")
except ImportError:
    SCRAPY_AVAILABLE = False
    print("⚠️ Scrapy integration not available, falling back to httpx")
import argparse
import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from selectolax.parser import HTMLParser
from sentence_transformers import SentenceTransformer
# Core extraction and AI libraries
from trafilatura import extract

# Vector storage - ChromaDB with Qdrant fallback
try:
    from scripts.vector_storage_migration import (ChromaVectorStorage,
                                                  migrate_qdrant_to_chroma)

    CHROMA_AVAILABLE = True
    print("✅ ChromaDB integration available")
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB not available, falling back to Qdrant")
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, PointStruct, VectorParams

# Enhanced semantic analysis modules
try:
    import sys

    sys.path.append("./scripts/semantic_crawler/scripts")
    from adaptive_thresholding import IntelligentAdaptiveThresholder
    from enhanced_research_detector import EnhancedResearchGapDetector
    from intelligent_knowledge_graph import IntelligentKnowledgeGraph

    ENHANCED_MODULES_AVAILABLE = True
    print("✅ Enhanced semantic analysis modules loaded successfully")
except ImportError as e:
    ENHANCED_MODULES_AVAILABLE = False
    print(f"⚠️ Enhanced modules not found, using basic semantic analysis: {e}")

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

# Initialize vector storage (ChromaDB or Qdrant)
if CHROMA_AVAILABLE:
    print("🗃️ Using ChromaDB for vector storage")
    vector_storage = ChromaVectorStorage("./chroma_storage", COLLECTION_NAME)

    # Try to migrate from Qdrant if it exists
    if Path("./qdrant_storage").exists():
        print("📦 Migrating existing Qdrant data to ChromaDB...")
        migrate_qdrant_to_chroma()

    # Create a compatibility layer for Qdrant-style interface
    class VectorStorageAdapter:
        def __init__(self, storage):
            self.storage = storage

        def upsert(self, collection_name, points):
            return self.storage.upsert(collection_name, points)

        def query(self, vector, top_k=10):
            return self.storage.query(vector, top_k)

    qdrant_client = VectorStorageAdapter(vector_storage)

else:
    print("🗃️ Using Qdrant for vector storage")
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
    """Extract structured content from HTML with enhanced language detection"""
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

        # Language detection for content filtering
        detected_language = "unknown"
        language_confidence = 0.0

        if (
            main_content and len(main_content) > 50
        ):  # Minimum text for reliable detection
            try:
                from langdetect import detect, detect_langs

                detected_language = detect(main_content)
                # Get confidence score
                lang_probs = detect_langs(main_content)
                language_confidence = max(lang.prob for lang in lang_probs)
            except Exception as lang_e:
                print(f"⚠️ Language detection failed for {url}: {lang_e}")

        return {
            "url": url,
            "title": title_text.strip(),
            "content": main_content.strip() if main_content else "",
            "content_length": len(main_content) if main_content else 0,
            "extracted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "language": detected_language,
            "language_confidence": language_confidence,
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
            "language": "unknown",
            "language_confidence": 0.0,
        }


# ─────────────────────────────────────────────────────────────────
# 🧠 AI-Based Relevance Filtering


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Calculate cosine similarity between two vectors using sklearn"""
    from sklearn.metrics.pairwise import \
        cosine_similarity as sklearn_cosine_similarity

    return float(
        sklearn_cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0][0]
    )


def is_content_relevant(
    content: str,
    threshold: float = DEFAULT_THRESHOLD,
    language: str = "unknown",
    language_confidence: float = 0.0,
) -> tuple[bool, float]:
    """Determine if content is relevant using enhanced semantic analysis with language filtering"""

    # Basic content quality checks
    if not content or len(content) < MIN_CONTENT_LENGTH:
        return False, 0.0

    # Language filtering - only accept English content with high confidence
    if language != "en" and language_confidence > 0.8:
        print(
            f"⚠️ Filtering out non-English content: {language} (confidence: {language_confidence:.2f})"
        )
        return False, 0.0

    # Use enhanced modules if available
    if ENHANCED_MODULES_AVAILABLE:
        try:
            # Initialize enhanced components with basic config
            enhanced_config = {
                "threshold": threshold,
                "method": "cleanlab",
                "min_confidence": 0.7,
            }
            adaptive_thresholder = IntelligentAdaptiveThresholder(enhanced_config)
            research_detector = EnhancedResearchGapDetector()

            # Use adaptive thresholding for better accuracy
            is_relevant, enhanced_score = adaptive_thresholder.evaluate_content(content)

            # Additional research gap detection
            research_score = research_detector.detect_research_gaps([content])

            # Combine scores for final decision
            final_score = (enhanced_score + research_score) / 2
            is_relevant = final_score >= threshold

            return is_relevant, final_score

        except Exception as e:
            print(f"⚠️ Enhanced analysis failed, falling back to basic: {e}")
            # Fall back to basic analysis
            pass

    # Basic analysis fallback
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
    """Embed content into Qdrant vector database with enhanced knowledge graph integration"""
    try:
        # Generate embedding for storage
        content_vector = model.encode(data["content"]).tolist()

        # Enhanced knowledge graph integration with new frameworks
        if ENHANCED_MODULES_AVAILABLE:
            try:
                # Initialize enhanced modules
                knowledge_graph = IntelligentKnowledgeGraph()
                research_detector = EnhancedResearchGapDetector()

                # Analyze content with enhanced modules
                graph_analysis = knowledge_graph.analyze_content(data["content"])
                research_gaps = research_detector.detect_gaps(data["content"])

                # Log successful integration
                print(
                    f"🔬 Enhanced analysis completed: {len(graph_analysis)} graph nodes, {len(research_gaps)} research gaps"
                )

                # Add enhanced insights to payload
                enhanced_payload = {
                    "source_file": markdown_file,
                    "metadata_file": metadata_file,
                    "url": data["url"],
                    "title": data["title"],
                    "similarity_score": similarity_score,
                    "content_length": data["content_length"],
                    "extracted_at": data["extracted_at"],
                    "content_preview": (
                        data["content"][:300] + "..."
                        if len(data["content"]) > 300
                        else data["content"]
                    ),
                    "knowledge_graph": graph_analysis,
                    "research_gaps": research_gaps,
                    "enhanced_processing": True,
                    "extraction_method": (
                        "scrapy-trafilatura"
                        if SCRAPY_AVAILABLE
                        else "httpx-trafilatura"
                    ),
                    "vector_storage": "ChromaDB" if CHROMA_AVAILABLE else "Qdrant",
                }
                payload = enhanced_payload
            except Exception as kg_error:
                print(f"⚠️ Enhanced analysis failed: {kg_error}")
                # Fall back to basic payload
                payload = {
                    "source_file": markdown_file,
                    "metadata_file": metadata_file,
                    "url": data["url"],
                    "title": data["title"],
                    "similarity_score": similarity_score,
                    "content_length": data["content_length"],
                    "extracted_at": data["extracted_at"],
                    "content_preview": (
                        data["content"][:300] + "..."
                        if len(data["content"]) > 300
                        else data["content"]
                    ),
                    "enhanced_processing": False,
                    "extraction_method": (
                        "scrapy-trafilatura"
                        if SCRAPY_AVAILABLE
                        else "httpx-trafilatura"
                    ),
                    "vector_storage": "ChromaDB" if CHROMA_AVAILABLE else "Qdrant",
                }
        else:
            # Basic payload
            payload = {
                "source_file": markdown_file,
                "metadata_file": metadata_file,
                "url": data["url"],
                "title": data["title"],
                "similarity_score": similarity_score,
                "content_length": data["content_length"],
                "extracted_at": data["extracted_at"],
                "content_preview": (
                    data["content"][:300] + "..."
                    if len(data["content"]) > 300
                    else data["content"]
                ),
                "enhanced_processing": False,
                "extraction_method": (
                    "scrapy-trafilatura" if SCRAPY_AVAILABLE else "httpx-trafilatura"
                ),
                "vector_storage": "ChromaDB" if CHROMA_AVAILABLE else "Qdrant",
            }

        # Generate unique ID
        unique_id = uuid.uuid4().int >> 64

        # Store in vector database (ChromaDB or Qdrant)
        if CHROMA_AVAILABLE:
            # ChromaDB format
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    {"id": unique_id, "vector": content_vector, "payload": payload}
                ],
            )
            storage_type = "ChromaDB"
        else:
            # Qdrant format
            qdrant_client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(id=unique_id, vector=content_vector, payload=payload)
                ],
            )
            storage_type = "Qdrant"

        # Update metadata to reflect embedding status
        try:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
            metadata["vector_embedded"] = True
            metadata["vector_id"] = unique_id
            metadata["vector_storage"] = storage_type
            metadata["enhanced_processing"] = payload.get("enhanced_processing", False)
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
        except Exception as meta_error:
            print(f"⚠️ Failed to update metadata: {meta_error}")

        processing_type = (
            "Enhanced" if payload.get("enhanced_processing", False) else "Basic"
        )
        print(
            f"🔍 {processing_type} embedding to {storage_type}: {data['title'][:50]}..."
        )

    except Exception as e:
        print(f"❌ Vector storage embedding error: {e}")


# ─────────────────────────────────────────────────────────────────
# 🚀 Main Semantic Crawler


def run_semantic_crawler(
    urls: List[str],
    threshold: float = DEFAULT_THRESHOLD,
    dry_run: bool = False,
    limit_domains: Optional[str] = None,
    save_raw: bool = False,
    proxy_rotate: bool = False,
    max_retries: int = 3,
    ignore_robots: bool = False,
):
    """Main crawler function with AI filtering"""

    print("🧠 Starting Semantic Crawler")
    print(f"📊 URLs to process: {len(urls)}")
    print(f"🎯 Similarity threshold: {threshold}")
    print(f"🧪 Dry run mode: {dry_run}")

    # Phase 4 Production Configuration
    if limit_domains:
        allowed_domains = [d.strip() for d in limit_domains.split(",")]
        print(f"🔒 Domain filtering: {allowed_domains}")
    else:
        allowed_domains = None

    if save_raw:
        print("💾 Raw HTML saving: enabled")
        raw_html_dir = Path("./raw_html_debug")
        raw_html_dir.mkdir(exist_ok=True)

    if proxy_rotate:
        print("🔄 Proxy rotation: enabled")

    print(f"🔁 Max retries: {max_retries}")
    print(f"🤖 Robots.txt respect: {not ignore_robots}")

    print("-" * 60)

    # Phase 4: Domain filtering
    if allowed_domains:
        from urllib.parse import urlparse

        filtered_urls = []
        for url in urls:
            domain = urlparse(url).netloc
            if any(allowed_domain in domain for allowed_domain in allowed_domains):
                filtered_urls.append(url)
            else:
                print(f"⚠️ Skipping {url} - domain not in allowed list")
        urls = filtered_urls
        print(f"🔒 Domain filtering applied: {len(urls)} URLs remaining")

    # Use scrapy if available, otherwise fallback to httpx
    if SCRAPY_AVAILABLE:
        print("🕷️ Using Scrapy + Trafilatura for content extraction")
        try:
            scrapy_results = run_scrapy_crawler(
                urls,
                save_raw=save_raw,
                proxy_rotate=proxy_rotate,
                max_retries=max_retries,
                ignore_robots=ignore_robots,
            )
            results = convert_scrapy_to_semantic_format(scrapy_results)

            # Convert to format expected by rest of function
            formatted_results = []
            for item in results:
                formatted_results.append((item, item["url"]))

            print(f"✅ Scrapy extracted content from {len(formatted_results)} URLs")
        except Exception as e:
            print(f"⚠️ Scrapy extraction failed: {e}")
            print("📱 Falling back to httpx")
            results = asyncio.run(fetch_all_urls(urls))
            formatted_results = [
                (parse_content(html, url), url) for html, url in results if html
            ]
    else:
        # Fallback to httpx
        print("📱 Using httpx for content extraction")
        results = asyncio.run(fetch_all_urls(urls))
        formatted_results = [
            (parse_content(html, url), url) for html, url in results if html
        ]

    # Process each result
    processed_count = 0
    relevant_count = 0
    similarity_scores = []

    for parsed_data, url in formatted_results:
        if not parsed_data or not parsed_data.get("content"):
            continue

        processed_count += 1
        print(f"\n📄 Processing {processed_count}/{len(formatted_results)}: {url}")

        if not parsed_data["content"]:
            print("  ❌ No content extracted")
            continue

        # Check relevance with AI including language filtering
        is_relevant, similarity_score = is_content_relevant(
            parsed_data["content"],
            threshold,
            parsed_data.get("language", "unknown"),
            parsed_data.get("language_confidence", 0.0),
        )
        similarity_scores.append(similarity_score)

        print(f"  🧠 Similarity score: {similarity_score:.3f}")
        print(f"  📏 Content length: {parsed_data['content_length']} chars")
        print(
            f"  🌐 Language: {parsed_data.get('language', 'unknown')} (confidence: {parsed_data.get('language_confidence', 0.0):.2f})"
        )

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

    # Phase 4 Production CLI Flags
    parser.add_argument(
        "--limit-domains",
        help="Comma-separated list of allowed domains to prevent crawl explosions",
    )

    parser.add_argument(
        "--save-raw",
        action="store_true",
        help="Save raw HTML content for debugging before parsing",
    )

    parser.add_argument(
        "--proxy-rotate",
        action="store_true",
        help="Enable proxy rotation for stealth crawling",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries for failed requests (default: 3)",
    )

    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Ignore robots.txt files (default: respect robots.txt)",
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
    run_semantic_crawler(
        urls,
        args.threshold,
        args.dry_run,
        args.limit_domains,
        args.save_raw,
        args.proxy_rotate,
        args.max_retries,
        args.ignore_robots,
    )


if __name__ == "__main__":
    main()
