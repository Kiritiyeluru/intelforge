#!/usr/bin/env python3
"""
Semantic Crawler with AI-Filtered Capture
Purpose: Intelligent content curation using embeddings and cosine similarity
Usage: python semantic_crawler.py --url-file urls.txt [--threshold 0.75] [--dry-run]
"""

import asyncio
import random

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
import orjson as json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

# Phase 4 YAML registry support
try:
    import yaml
    YAML_AVAILABLE = True
    print("✅ PyYAML available for registry support")
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️ PyYAML not available, registry functionality disabled")

# Core dependencies with graceful fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy not available, using Python statistics for calculations")

try:
    from selectolax.parser import HTMLParser
    SELECTOLAX_AVAILABLE = True
except ImportError:
    SELECTOLAX_AVAILABLE = False
    print("⚠️ Selectolax not available, using basic HTML parsing")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ SentenceTransformers not available, semantic analysis disabled")

try:
    from trafilatura import extract
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    print("⚠️ Trafilatura not available, using basic text extraction")

# Vector storage - ChromaDB with Qdrant fallback
try:
    from scripts.vector_storage_migration import (ChromaVectorStorage,
                                                  migrate_qdrant_to_chroma)

    CHROMA_AVAILABLE = True
    print("✅ ChromaDB integration available")
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠️ ChromaDB not available, falling back to Qdrant")

# Try to import Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, PointStruct, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("⚠️ Qdrant not available, vector storage disabled")

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
# 📊 Fallback Similarity Functions

def calculate_keyword_similarity(content: str) -> float:
    """Fallback similarity calculation based on trading keywords"""
    trading_keywords = [
        'strategy', 'trading', 'backtest', 'signal', 'indicator', 'rsi', 'ema', 'sma',
        'macd', 'bollinger', 'momentum', 'profit', 'loss', 'portfolio', 'risk',
        'hedge', 'arbitrage', 'algorithm', 'quant', 'finance', 'market', 'stock',
        'forex', 'crypto', 'bitcoin', 'analysis', 'technical', 'fundamental',
        'price', 'volume', 'trend', 'support', 'resistance', 'breakout', 'reversal'
    ]

    content_lower = content.lower()
    keyword_count = sum(1 for keyword in trading_keywords if keyword in content_lower)

    # Score based on keyword density
    content_length = len(content.split())
    if content_length == 0:
        return 0.0

    # Normalize score between 0 and 1
    score = min(keyword_count / 10.0, 1.0)  # Max score when 10+ keywords found
    return score

# ─────────────────────────────────────────────────────────────────
# 🧠 AI Models & Storage Initialization

if SENTENCE_TRANSFORMERS_AVAILABLE:
    print("🧠 Loading AI models...")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ Loaded embedding model: {EMBEDDING_MODEL}")
    except Exception as e:
        print(f"⚠️ Failed to load embedding model: {e}")
        SENTENCE_TRANSFORMERS_AVAILABLE = False
        model = None
else:
    print("⚠️ SentenceTransformers not available, semantic analysis disabled")
    model = None

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

elif QDRANT_AVAILABLE:
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
else:
    print("⚠️ No vector storage available, content will be saved to files only")
    qdrant_client = None

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


async def fetch_url_with_retry(
    client: httpx.AsyncClient,
    url: str,
    max_retries: int = 3,
    timeout: int = 20,
    backoff_factor: float = 2.0,
    rate_limit: Optional[float] = None
) -> tuple[Optional[str], str]:
    """Fetch content from a single URL with enhanced error recovery

    Args:
        client: httpx AsyncClient instance
        url: URL to fetch
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        backoff_factor: Exponential backoff multiplier
        rate_limit: Optional rate limit in requests per second

    Returns:
        Tuple of (content, url) or (None, url) if failed
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            # Rate limiting - delay between requests
            if rate_limit and rate_limit > 0:
                delay = 1.0 / rate_limit
                # Add small random jitter to prevent thundering herd
                jitter = random.uniform(0.8, 1.2)
                await asyncio.sleep(delay * jitter)

            # Make request with configurable timeout
            response = await client.get(url, timeout=timeout)
            response.raise_for_status()

            # Success - return content
            if attempt > 0:
                print(f"✅ Retry {attempt} succeeded for {url}")
            return response.text, url

        except httpx.TimeoutException as e:
            last_error = f"Timeout after {timeout}s"
            error_type = "timeout"
        except httpx.HTTPStatusError as e:
            last_error = f"HTTP {e.response.status_code}"
            error_type = "http_error"
        except httpx.RequestError as e:
            last_error = f"Request error: {e}"
            error_type = "request_error"
        except Exception as e:
            last_error = f"Unexpected error: {e}"
            error_type = "unknown"

        # Don't retry on certain HTTP errors
        if error_type == "http_error" and "4" in str(last_error):
            print(f"❌ {url}: {last_error} (not retrying client errors)")
            break

        # Calculate exponential backoff delay
        if attempt < max_retries:
            delay = backoff_factor ** attempt
            # Add jitter to prevent thundering herd
            jitter = random.uniform(0.5, 1.5)
            backoff_delay = delay * jitter

            print(f"⚠️ {url}: {last_error} (retry {attempt + 1}/{max_retries} in {backoff_delay:.1f}s)")
            await asyncio.sleep(backoff_delay)

    # All retries exhausted
    print(f"❌ Failed to fetch {url} after {max_retries} retries: {last_error}")
    return None, url


async def fetch_url(client: httpx.AsyncClient, url: str) -> tuple[Optional[str], str]:
    """Legacy fetch function for backward compatibility"""
    return await fetch_url_with_retry(client, url, max_retries=3, timeout=20)


async def fetch_all_urls(
    urls: List[str],
    max_retries: int = 3,
    timeout: int = 20,
    backoff_factor: float = 2.0,
    rate_limit: Optional[float] = None
) -> List[tuple[Optional[str], str]]:
    """Fetch content from multiple URLs with enhanced error recovery

    Args:
        urls: List of URLs to fetch
        max_retries: Maximum number of retry attempts per URL
        timeout: Request timeout in seconds
        backoff_factor: Exponential backoff multiplier
        rate_limit: Optional rate limit in requests per second

    Returns:
        List of (content, url) tuples
    """
    print(f"🌐 Fetching {len(urls)} URLs with enhanced error recovery...")

    if rate_limit:
        print(f"⏱️ Rate limit: {rate_limit} requests/second")
    print(f"🔁 Max retries: {max_retries}")
    print(f"⏰ Timeout: {timeout}s")
    print(f"📈 Backoff factor: {backoff_factor}")

    async with httpx.AsyncClient(headers=HEADERS, http2=True) as client:
        tasks = [
            fetch_url_with_retry(
                client, url, max_retries, timeout, backoff_factor, rate_limit
            ) for url in urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions and return valid results
    valid_results = []
    exception_count = 0

    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Request failed with exception: {result}")
            exception_count += 1
        else:
            valid_results.append(result)

    success_count = len([r for r in valid_results if r[0] is not None])
    failure_count = len([r for r in valid_results if r[0] is None])

    print(f"✅ Successfully fetched {success_count} pages")
    print(f"⚠️ Failed to fetch {failure_count} pages")
    if exception_count > 0:
        print(f"❌ {exception_count} requests failed with exceptions")

    return valid_results


# ─────────────────────────────────────────────────────────────────
# ✂️ Content Extraction


def parse_content(html: str, url: str) -> Dict[str, Any]:
    """Extract structured content from HTML with enhanced language detection"""
    try:
        # Parse with selectolax for metadata if available
        if SELECTOLAX_AVAILABLE:
            dom = HTMLParser(html)
            title = dom.css_first("title")
            title_text = title.text() if title else "Untitled"
        else:
            # Fallback title extraction
            import re
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title_text = title_match.group(1).strip() if title_match else "Untitled"

        # Extract main content with trafilatura if available
        if TRAFILATURA_AVAILABLE:
            main_content = extract(html)
        else:
            main_content = None

        if not main_content:
            # Fallback extraction
            if SELECTOLAX_AVAILABLE:
                body = dom.css_first("body")
                main_content = body.text() if body else ""
            else:
                # Basic text extraction fallback
                import re
                # Remove script and style tags
                clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.IGNORECASE | re.DOTALL)
                clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.IGNORECASE | re.DOTALL)
                # Extract text content
                main_content = re.sub(r'<[^>]+>', '', clean_html)
                main_content = re.sub(r'\s+', ' ', main_content).strip()

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
# 🔍 Enhanced Content Filtering


def filter_content_by_keywords(
    content: str,
    title: str = "",
    include_keywords: Optional[List[str]] = None,
    exclude_keywords: Optional[List[str]] = None,
) -> tuple[bool, Dict[str, Any]]:
    """Filter content based on keyword inclusion/exclusion rules

    Args:
        content: Main content text
        title: Article title (optional)
        include_keywords: List of keywords that must be present
        exclude_keywords: List of keywords to exclude

    Returns:
        Tuple of (passes_filter, filter_details)
    """
    filter_details = {
        "include_matches": [],
        "exclude_matches": [],
        "include_satisfied": True,
        "exclude_satisfied": True,
    }

    # Combine content and title for comprehensive keyword matching
    search_text = f"{title} {content}".lower()

    # Check include keywords (must have at least one match for each keyword)
    if include_keywords:
        for keyword in include_keywords:
            if keyword.lower() in search_text:
                filter_details["include_matches"].append(keyword)

        # If include keywords specified, at least one must match
        if not filter_details["include_matches"]:
            filter_details["include_satisfied"] = False

    # Check exclude keywords (must have no matches)
    if exclude_keywords:
        for keyword in exclude_keywords:
            if keyword.lower() in search_text:
                filter_details["exclude_matches"].append(keyword)

        # If any exclude keyword matches, filter fails
        if filter_details["exclude_matches"]:
            filter_details["exclude_satisfied"] = False

    # Content passes if both include and exclude criteria are satisfied
    passes_filter = filter_details["include_satisfied"] and filter_details["exclude_satisfied"]

    return passes_filter, filter_details


def filter_content_by_word_count(
    content: str, min_word_count: int = 200, max_word_count: int = 10000
) -> tuple[bool, Dict[str, Any]]:
    """Filter content based on word count limits

    Args:
        content: Main content text
        min_word_count: Minimum required word count
        max_word_count: Maximum allowed word count

    Returns:
        Tuple of (passes_filter, word_count_details)
    """
    if not content:
        return False, {"word_count": 0, "reason": "empty_content"}

    # Count words using simple whitespace splitting
    word_count = len(content.split())

    word_count_details = {
        "word_count": word_count,
        "min_required": min_word_count,
        "max_allowed": max_word_count,
        "passes_min": word_count >= min_word_count,
        "passes_max": word_count <= max_word_count,
    }

    if word_count < min_word_count:
        word_count_details["reason"] = f"below_minimum_{min_word_count}"
        return False, word_count_details
    elif word_count > max_word_count:
        word_count_details["reason"] = f"above_maximum_{max_word_count}"
        return False, word_count_details

    word_count_details["reason"] = "within_range"
    return True, word_count_details


def detect_content_type(content: str, title: str = "") -> str:
    """Detect content type based on text analysis

    Args:
        content: Main content text
        title: Article title (optional)

    Returns:
        Content type: 'article', 'codeblock', 'tutorial', 'research', or 'unknown'
    """
    if not content:
        return "unknown"

    # Combine title and content for analysis
    text = f"{title} {content}".lower()

    # Code indicators
    code_indicators = [
        "def ", "class ", "import ", "from ", "function", "var ", "let ", "const ",
        "```", "```python", "```javascript", "```java", "```cpp", "```r",
        "github.com/", "gitlab.com/", "bitbucket.org/", "stackoverflow.com/",
        "algorithm", "implementation", "code", "script", "function", "method",
        "programming", "developer", "software", "library", "package", "module"
    ]

    # Tutorial indicators
    tutorial_indicators = [
        "tutorial", "guide", "how to", "step by step", "walkthrough", "example",
        "getting started", "beginner", "introduction", "learn", "course",
        "lesson", "chapter", "part 1", "part 2", "series", "follow along"
    ]

    # Research indicators
    research_indicators = [
        "research", "study", "paper", "journal", "arxiv", "doi:", "abstract",
        "methodology", "experiment", "analysis", "findings", "results",
        "conclusion", "references", "bibliography", "peer review", "published"
    ]

    # Article indicators (general content)
    article_indicators = [
        "article", "blog", "post", "news", "opinion", "review", "analysis",
        "discussion", "insights", "thoughts", "perspective", "commentary"
    ]

    # Count indicators for each type
    code_count = sum(1 for indicator in code_indicators if indicator in text)
    tutorial_count = sum(1 for indicator in tutorial_indicators if indicator in text)
    research_count = sum(1 for indicator in research_indicators if indicator in text)
    article_count = sum(1 for indicator in article_indicators if indicator in text)

    # Determine content type based on highest count
    counts = {
        'codeblock': code_count,
        'tutorial': tutorial_count,
        'research': research_count,
        'article': article_count
    }

    # Return the type with the highest count, or 'article' as default if all counts are equal
    max_count = max(counts.values())
    if max_count == 0:
        return "article"  # Default to article if no specific indicators found

    # Find the type with the highest count
    for content_type, count in counts.items():
        if count == max_count:
            return content_type

    return "article"


def filter_content_by_type(
    content: str,
    title: str = "",
    allowed_types: Optional[List[str]] = None
) -> tuple[bool, Dict[str, Any]]:
    """Filter content based on content type

    Args:
        content: Main content text
        title: Article title (optional)
        allowed_types: List of allowed content types

    Returns:
        Tuple of (passes_filter, type_details)
    """
    if not allowed_types:
        # If no filter specified, allow all content
        detected_type = detect_content_type(content, title)
        return True, {"detected_type": detected_type, "allowed_types": [], "passes_filter": True}

    detected_type = detect_content_type(content, title)
    passes_filter = detected_type in allowed_types

    type_details = {
        "detected_type": detected_type,
        "allowed_types": allowed_types,
        "passes_filter": passes_filter,
    }

    return passes_filter, type_details


# ─────────────────────────────────────────────────────────────────
# 🔍 Phase 2: Content Validation Layer (Overlooked Areas Integration)

def validate_strategy_content(content: str, title: str = "") -> Dict[str, Any]:
    """Validate extracted content for strategy requirements

    Based on 'Overlooked Areas' recommendation for Raw-to-Parsed Validation Layer

    Args:
        content: Main content text
        title: Article title (optional)

    Returns:
        Dict containing validation results and quality metrics
    """
    text = f"{title} {content}".lower()

    # Strategy structure validation
    has_entry_rules = any(term in text for term in [
        "entry", "buy signal", "long signal", "enter", "open position",
        "trigger", "signal", "condition", "rule", "when to buy", "entry point"
    ])

    has_exit_rules = any(term in text for term in [
        "exit", "sell signal", "short signal", "close position", "stop loss",
        "take profit", "exit point", "when to sell", "profit target"
    ])

    has_parameters = any(term in text for term in [
        "parameter", "setting", "value", "threshold", "period", "window",
        "lookback", "days", "minutes", "hours", "alpha", "beta", "gamma"
    ])

    # Validate parameter values are numeric and reasonable
    parameters_valid = True
    if has_parameters:
        # Look for numeric values in reasonable ranges
        import re
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        if numbers:
            try:
                numeric_values = [float(n) for n in numbers]
                # Check if values are within reasonable ranges for trading parameters
                parameters_valid = all(0 <= val <= 1000 for val in numeric_values if val < 100000)
            except ValueError:
                parameters_valid = False

    # Backtest validation
    contains_backtest = any(term in text for term in [
        "backtest", "back test", "historical", "simulation", "performance",
        "returns", "sharpe", "drawdown", "profit", "loss", "win rate"
    ])

    # Content quality indicators
    has_specific_indicators = any(term in text for term in [
        "rsi", "macd", "ema", "sma", "bollinger", "stochastic", "atr",
        "momentum", "volume", "moving average", "oscillator"
    ])

    has_risk_management = any(term in text for term in [
        "risk", "stop loss", "position size", "drawdown", "volatility",
        "money management", "risk management", "portfolio"
    ])

    # Calculate quality score
    quality_components = [
        has_entry_rules, has_exit_rules, has_parameters, parameters_valid,
        contains_backtest, has_specific_indicators, has_risk_management
    ]
    quality_score = sum(quality_components) / len(quality_components)

    return {
        "has_entry_rules": has_entry_rules,
        "has_exit_rules": has_exit_rules,
        "has_parameters": has_parameters,
        "parameters_valid": parameters_valid,
        "contains_backtest": contains_backtest,
        "has_specific_indicators": has_specific_indicators,
        "has_risk_management": has_risk_management,
        "quality_score": round(quality_score, 2)
    }


def run_health_check() -> bool:
    """Run CLI health check to verify system functionality

    Based on 'Overlooked Areas' recommendation for CLI Health Contracts

    Returns:
        True if all checks pass, False otherwise
    """
    print("🔍 Checking system dependencies...")

    # Check required imports
    try:
        import sentence_transformers
        print("  ✅ sentence_transformers")
    except ImportError:
        print("  ❌ sentence_transformers not available")
        return False

    try:
        import trafilatura
        print("  ✅ trafilatura")
    except ImportError:
        print("  ❌ trafilatura not available")
        return False

    try:
        import numpy
        print("  ✅ numpy")
    except ImportError:
        print("  ❌ numpy not available")
        return False

    # Check model loading
    try:
        print("🧠 Testing model loading...")
        test_model = SentenceTransformer(EMBEDDING_MODEL)
        print("  ✅ Embedding model loaded successfully")
    except Exception as e:
        print(f"  ❌ Embedding model loading failed: {e}")
        return False

    # Check vector storage
    try:
        print("🗃️ Testing vector storage...")
        if CHROMA_AVAILABLE:
            print("  ✅ ChromaDB available")
        else:
            print("  ✅ Qdrant fallback available")
    except Exception as e:
        print(f"  ❌ Vector storage failed: {e}")
        return False

    # Check directory structure
    required_dirs = ["./exports", "./logs"]
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"  ⚠️ Creating missing directory: {dir_path}")
            Path(dir_path).mkdir(exist_ok=True)
        print(f"  ✅ Directory exists: {dir_path}")

    print("🎯 Health check completed successfully")
    return True


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
        reference_vector_np = np.array(reference_vector)
        similarity_score = cosine_similarity(content_vector, reference_vector_np)

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

        # Store in vector database (ChromaDB or Qdrant) if available
        if content_vector is not None:
            if CHROMA_AVAILABLE and qdrant_client is not None:
                # ChromaDB format
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[
                        {"id": unique_id, "vector": content_vector, "payload": payload}
                    ],
                )
                storage_type = "ChromaDB"
            elif QDRANT_AVAILABLE and qdrant_client is not None:
                # Qdrant format
                qdrant_client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=[
                        PointStruct(id=unique_id, vector=content_vector, payload=payload)
                    ],
                )
                storage_type = "Qdrant"
            else:
                print("⚠️ No vector storage available, skipping vector embedding")
                storage_type = "None"
        else:
            print("⚠️ No content vector available, skipping vector embedding")
            storage_type = "None"

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
    include_keywords: Optional[str] = None,
    exclude_keywords: Optional[str] = None,
    min_word_count: int = 200,
    max_word_count: int = 10000,
    content_type_filter: Optional[str] = None,
    metadata_output: Optional[str] = None,
    validate_content: bool = False,
    rate_limit: Optional[float] = None,
    timeout: int = 20,
    backoff_factor: float = 2.0,
    registry: Optional[Dict[str, Any]] = None,
    registry_settings: Optional[Dict[str, Any]] = None,
    validate_content_requirements: bool = False,
):
    """Main crawler function with AI filtering"""

    print("🧠 Starting Semantic Crawler")
    print(f"📊 URLs to process: {len(urls)}")
    print(f"🎯 Similarity threshold: {threshold}")
    print(f"🧪 Dry run mode: {dry_run}")

    # Display keyword filtering configuration
    if include_keywords:
        print(f"🔍 Include keywords: {include_keywords}")
    if exclude_keywords:
        print(f"🚫 Exclude keywords: {exclude_keywords}")

    # Display word count filtering configuration
    print(f"📏 Word count range: {min_word_count} - {max_word_count} words")

    # Display content type filtering configuration
    if content_type_filter:
        print(f"📝 Content type filter: {content_type_filter}")

    # Phase 2: Display metadata and validation configuration
    if metadata_output:
        print(f"📁 Metadata output: {metadata_output}")
    if validate_content:
        print(f"🔍 Content validation: enabled")

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

    # Phase 3: Display rate limiting and reliability configuration
    if rate_limit:
        print(f"⏱️ Rate limit: {rate_limit} requests/second")
    print(f"⏰ Timeout: {timeout}s")
    print(f"📈 Backoff factor: {backoff_factor}")

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
            # Get output directory from environment (set by nightly crawler)
            output_dir = os.getenv('INTELFORGE_OUTPUT_DIR')
            if output_dir:
                print(f"📁 Using output directory: {output_dir}")
            
            scrapy_results = run_scrapy_crawler(
                urls,
                save_raw=save_raw,
                proxy_rotate=proxy_rotate,
                max_retries=max_retries,
                output_dir=output_dir,
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
            results = asyncio.run(fetch_all_urls(
                urls, max_retries, timeout, backoff_factor, rate_limit
            ))
            formatted_results = [
                (parse_content(html, url), url) for html, url in results if html
            ]
    else:
        # Fallback to httpx
        print("📱 Using httpx for content extraction")
        results = asyncio.run(fetch_all_urls(
            urls, max_retries, timeout, backoff_factor, rate_limit
        ))
        formatted_results = [
            (parse_content(html, url), url) for html, url in results if html
        ]

    # Process each result
    processed_count = 0
    relevant_count = 0
    similarity_scores = []
    metadata_records = []  # Phase 2: Collect metadata for all processed URLs

    for parsed_data, url in formatted_results:
        if not parsed_data or not parsed_data.get("content"):
            continue

        processed_count += 1
        print(f"\n📄 Processing {processed_count}/{len(formatted_results)}: {url}")

        if not parsed_data["content"]:
            print("  ❌ No content extracted")
            continue

        # Parse keyword arguments
        include_keywords_list = None
        exclude_keywords_list = None
        if include_keywords:
            include_keywords_list = [kw.strip() for kw in include_keywords.split(',')]
        if exclude_keywords:
            exclude_keywords_list = [kw.strip() for kw in exclude_keywords.split(',')]

        # Apply keyword filtering
        passes_keyword_filter, filter_details = filter_content_by_keywords(
            parsed_data["content"],
            parsed_data.get("title", ""),
            include_keywords_list,
            exclude_keywords_list,
        )

        # Display keyword filtering results
        if include_keywords_list:
            print(f"  🔍 Include keywords: {include_keywords_list}")
            print(f"  ✅ Matches found: {filter_details['include_matches']}")
        if exclude_keywords_list:
            print(f"  🚫 Exclude keywords: {exclude_keywords_list}")
            if filter_details['exclude_matches']:
                print(f"  ❌ Excluded matches: {filter_details['exclude_matches']}")

        if not passes_keyword_filter:
            print("  ❌ FILTERED OUT - Failed keyword filtering")
            continue

        # Apply word count filtering
        passes_word_count_filter, word_count_details = filter_content_by_word_count(
            parsed_data["content"], min_word_count, max_word_count
        )

        # Display word count filtering results
        print(f"  📏 Word count: {word_count_details['word_count']} words")
        print(f"  📊 Range: {word_count_details['min_required']}-{word_count_details['max_allowed']}")

        if not passes_word_count_filter:
            print(f"  ❌ FILTERED OUT - {word_count_details['reason']}")
            continue

        # Parse content type filter
        allowed_content_types = None
        if content_type_filter:
            allowed_content_types = [ct.strip() for ct in content_type_filter.split(',')]

        # Apply content type filtering
        passes_content_type_filter, type_details = filter_content_by_type(
            parsed_data["content"],
            parsed_data.get("title", ""),
            allowed_content_types,
        )

        # Display content type filtering results
        print(f"  📝 Content type: {type_details['detected_type']}")
        if allowed_content_types:
            print(f"  🎯 Allowed types: {allowed_content_types}")
            if not passes_content_type_filter:
                print(f"  ❌ FILTERED OUT - Content type '{type_details['detected_type']}' not in allowed types")
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

        # Phase 2: Content validation and metadata collection
        validation_status = {}
        if validate_content:
            validation_status = validate_strategy_content(
                parsed_data["content"],
                parsed_data.get("title", "")
            )
            print(f"  🔍 Content validation: {validation_status['quality_score']:.2f}")
            print(f"  📋 Entry rules: {'✅' if validation_status['has_entry_rules'] else '❌'}")
            print(f"  🚪 Exit rules: {'✅' if validation_status['has_exit_rules'] else '❌'}")
            print(f"  📊 Backtest: {'✅' if validation_status['contains_backtest'] else '❌'}")

        # Phase 4: Content requirements validation from registry
        requirements_validation = {}
        if validate_content_requirements and registry:
            # Find requirements for this URL's source
            url_requirements = None
            for category in registry:
                if isinstance(registry[category], list):
                    for source in registry[category]:
                        if isinstance(source, dict) and source.get('url') == url:
                            url_requirements = source.get('content_requirements', {})
                            break
                    if url_requirements:
                        break

            if url_requirements:
                requirements_validation = validate_content_requirements(
                    parsed_data["content"],
                    url_requirements
                )
                print(f"  🎯 Requirements validation: {requirements_validation['score']:.2f}")
                print(f"  ✅ Valid: {requirements_validation['valid']}")
                if requirements_validation['missing']:
                    print(f"  ❌ Missing: {', '.join(requirements_validation['missing'])}")
                if requirements_validation['optional_found']:
                    print(f"  ➕ Optional found: {', '.join(requirements_validation['optional_found'])}")

        # Collect metadata for all processed URLs
        metadata_record = {
            "url": url,
            "title": parsed_data.get("title", ""),
            "score": round(similarity_score, 3),
            "extracted": is_relevant,
            "parameters": [],  # Will be populated if content is relevant
            "backtest_result": validation_status.get('contains_backtest', False),
            "word_count": word_count_details['word_count'],
            "content_type": type_details['detected_type'],
            "crawl_timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            "language": parsed_data.get('language', 'unknown'),
            "language_confidence": parsed_data.get('language_confidence', 0.0),
            "filter_results": {
                "keyword_filter": passes_keyword_filter,
                "word_count_filter": passes_word_count_filter,
                "content_type_filter": passes_content_type_filter,
                "similarity_threshold": is_relevant,
            }
        }

        # Add validation status if content validation is enabled
        if validate_content:
            metadata_record["validation_status"] = validation_status

        # Add requirements validation if enabled
        if validate_content_requirements and requirements_validation:
            metadata_record["requirements_validation"] = requirements_validation

        metadata_records.append(metadata_record)

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
        if NUMPY_AVAILABLE:
            print(f"Average similarity: {np.mean(similarity_scores):.3f}")
            print(
                f"Similarity range: {np.min(similarity_scores):.3f} - {np.max(similarity_scores):.3f}"
            )
        else:
            # Fallback statistics without numpy
            avg_score = sum(similarity_scores) / len(similarity_scores)
            min_score = min(similarity_scores)
            max_score = max(similarity_scores)
            print(f"Average similarity: {avg_score:.3f}")
            print(f"Similarity range: {min_score:.3f} - {max_score:.3f}")

    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60)

    # Phase 2: Save metadata output if specified
    if metadata_output and metadata_records:
        print(f"\n📁 Saving metadata to: {metadata_output}")

        # Ensure metadata directory exists
        metadata_dir = Path(metadata_output).parent
        metadata_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata as JSON
        try:
            with open(metadata_output, 'w', encoding='utf-8') as f:
                json.dump(metadata_records, f, indent=2, ensure_ascii=False)
            print(f"✅ Metadata saved: {len(metadata_records)} records")

            # Summary statistics for metadata
            extracted_count = sum(1 for record in metadata_records if record['extracted'])
            avg_score = np.mean([record['score'] for record in metadata_records])

            print(f"📊 Metadata summary:")
            print(f"  Total records: {len(metadata_records)}")
            print(f"  Extracted: {extracted_count}")
            print(f"  Average score: {avg_score:.3f}")

            if validate_content:
                validated_records = [r for r in metadata_records if 'validation_status' in r]
                if validated_records:
                    quality_scores = [r['validation_status']['quality_score'] for r in validated_records]
                    if NUMPY_AVAILABLE:
                        avg_quality = np.mean(quality_scores)
                    else:
                        avg_quality = sum(quality_scores) / len(quality_scores)
                    print(f"  Average quality score: {avg_quality:.2f}")

        except Exception as e:
            print(f"❌ Error saving metadata: {e}")
    elif metadata_output:
        print(f"⚠️ No metadata records to save")

    # Display metadata and validation configuration
    if metadata_output:
        print(f"📁 Metadata output: {metadata_output}")
    if validate_content:
        print(f"🔍 Content validation: enabled")


# ─────────────────────────────────────────────────────────────────
# 🗂️ Phase 4: Source Registry System


def load_registry(registry_file: str) -> Dict[str, Any]:
    """Load and parse YAML source registry file"""
    if not YAML_AVAILABLE:
        print("❌ PyYAML not available, cannot load registry")
        return {}

    try:
        with open(registry_file, 'r', encoding='utf-8') as f:
            registry = yaml.safe_load(f)

        print(f"✅ Loaded registry: {registry_file}")
        return registry

    except FileNotFoundError:
        print(f"❌ Registry file not found: {registry_file}")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return {}
    except Exception as e:
        print(f"❌ Error loading registry: {e}")
        return {}


def extract_urls_from_registry(registry: Dict[str, Any], category: str = None) -> List[str]:
    """Extract URLs from registry based on category"""
    if not registry:
        return []

    urls = []
    categories_to_process = [category] if category else registry.keys()

    for cat in categories_to_process:
        if cat in registry and isinstance(registry[cat], list):
            for source in registry[cat]:
                if isinstance(source, dict) and 'url' in source:
                    urls.append(source['url'])
                    print(f"📌 Added from {cat}: {source.get('name', 'Unknown')} - {source['url']}")

    print(f"✅ Extracted {len(urls)} URLs from registry")
    return urls


def apply_registry_settings(registry: Dict[str, Any], category: str = None) -> Dict[str, Any]:
    """Apply registry-based settings and defaults"""
    settings = {}

    # Apply global settings
    if 'global_settings' in registry:
        global_settings = registry['global_settings']
        settings.update({
            'threshold': global_settings.get('default_threshold', 0.75),
            'rate_limit': global_settings.get('default_rate_limit', 3),
            'timeout': global_settings.get('default_timeout', 10),
            'max_retries': global_settings.get('default_max_retries', 2),
            'backoff_factor': global_settings.get('default_backoff_factor', 2),
        })

        # Apply content filtering defaults
        if 'content_filtering' in global_settings:
            cf = global_settings['content_filtering']
            settings.update({
                'enable_keyword_filtering': cf.get('enable_keyword_filtering', True),
                'enable_word_count_filtering': cf.get('enable_word_count_filtering', True),
                'enable_content_type_filtering': cf.get('enable_content_type_filtering', True),
            })

        # Apply default keywords
        if 'default_keywords' in global_settings:
            dk = global_settings['default_keywords']
            settings.update({
                'default_include_keywords': dk.get('include', []),
                'default_exclude_keywords': dk.get('exclude', []),
            })

    # Apply category-specific settings
    if category and category in registry:
        category_sources = registry[category]
        if category_sources and isinstance(category_sources, list):
            # Use settings from first source as defaults for the category
            first_source = category_sources[0]
            if isinstance(first_source, dict):
                settings.update({
                    'category_threshold': first_source.get('threshold', settings.get('threshold', 0.75)),
                    'category_priority': first_source.get('priority', 'weekly'),
                    'category_quality': first_source.get('quality', 'good'),
                })

    return settings


def validate_content_requirements(content: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content against requirements from registry"""
    if not requirements:
        return {"valid": True, "score": 1.0, "missing": [], "optional_found": []}

    content_lower = content.lower()
    validation_result = {
        "valid": True,
        "score": 1.0,
        "missing": [],
        "optional_found": [],
        "must_have_found": []
    }

    # Check must-have requirements
    must_have = requirements.get('must_have', [])
    must_have_score = 0
    for requirement in must_have:
        if requirement.lower() in content_lower:
            validation_result["must_have_found"].append(requirement)
            must_have_score += 1
        else:
            validation_result["missing"].append(requirement)

    # Check optional requirements
    optional = requirements.get('optional', [])
    optional_score = 0
    for requirement in optional:
        if requirement.lower() in content_lower:
            validation_result["optional_found"].append(requirement)
            optional_score += 1

    # Calculate overall score
    must_have_weight = 0.8
    optional_weight = 0.2

    must_have_ratio = must_have_score / len(must_have) if must_have else 1.0
    optional_ratio = optional_score / len(optional) if optional else 1.0

    validation_result["score"] = (must_have_weight * must_have_ratio) + (optional_weight * optional_ratio)
    validation_result["valid"] = len(validation_result["missing"]) == 0

    return validation_result


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
  python semantic_crawler.py --url-file urls.txt --include-keywords "backtest,strategy,RSI,EMA"
  python semantic_crawler.py --url-file urls.txt --exclude-keywords "opinion,news" --threshold 0.8
  python semantic_crawler.py --url-file urls.txt --min-word-count 200 --max-word-count 8000
  python semantic_crawler.py --url-file urls.txt --content-type-filter "article,tutorial"
  python semantic_crawler.py --url-file urls.txt --rate-limit 3 --timeout 10 --backoff-factor 2
  python semantic_crawler.py --url-file urls.txt --metadata-output metadata/results.json --validate-content
        """,
    )

    parser.add_argument(
        "--url-file",
        "-f",
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


    # Phase 1 Enhanced Content Filtering
    parser.add_argument(
        "--include-keywords",
        help="Comma-separated list of keywords that must be present in content",
    )

    parser.add_argument(
        "--exclude-keywords",
        help="Comma-separated list of keywords to exclude from content",
    )

    parser.add_argument(
        "--min-word-count",
        type=int,
        default=200,
        help="Minimum word count for content quality control (default: 200)",
    )

    parser.add_argument(
        "--max-word-count",
        type=int,
        default=10000,
        help="Maximum word count for content quality control (default: 10000)",
    )

    parser.add_argument(
        "--content-type-filter",
        help="Comma-separated list of content types to include (article, codeblock, tutorial, research)",
    )

    # Phase 2 Enhanced Metadata Output System
    parser.add_argument(
        "--metadata-output",
        help="Path to save consolidated metadata output as JSON file",
    )

    parser.add_argument(
        "--validate-content",
        action="store_true",
        help="Enable content validation layer for quality assurance",
    )

    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run CLI health check to verify system functionality",
    )

    # Phase 3 Rate Limiting & Reliability
    parser.add_argument(
        "--rate-limit",
        type=float,
        help="Rate limit in requests per second (default: no limit)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Request timeout in seconds (default: 20)",
    )

    parser.add_argument(
        "--backoff-factor",
        type=float,
        default=2.0,
        help="Exponential backoff multiplier for retries (default: 2.0)",
    )

    # Phase 4 Source Registry System
    parser.add_argument(
        "--registry-file",
        help="Path to YAML source registry file for configuration-based crawling",
    )

    parser.add_argument(
        "--category",
        help="Category from registry to crawl (rss_feeds, technical_blogs, github_sources, academic_sources)",
    )

    parser.add_argument(
        "--validate-content-requirements",
        action="store_true",
        help="Enable content requirements validation from registry",
    )

    args = parser.parse_args()

    # Health check functionality
    if args.health_check:
        print("🏥 Running CLI Health Check...")
        health_status = run_health_check()
        if health_status:
            print("✅ Health check passed")
            return
        else:
            print("❌ Health check failed")
            sys.exit(1)

    # Regenerate reference embeddings if requested
    if args.regenerate_reference:
        print("🔄 Regenerating reference embeddings...")
        create_reference_embeddings()
        print("✅ Reference embeddings updated")
        return

    # Phase 4: Registry-based crawling or traditional file-based crawling
    registry = {}
    registry_settings = {}

    if args.registry_file:
        # Load from registry
        registry = load_registry(args.registry_file)
        if not registry:
            print("❌ Failed to load registry, exiting")
            return

        # Apply registry settings
        registry_settings = apply_registry_settings(registry, args.category)

        # Extract URLs from registry
        urls = extract_urls_from_registry(registry, args.category)
        if not urls:
            print(f"❌ No URLs found in registry for category: {args.category or 'all'}")
            return

        print(f"🗂️ Using registry-based crawling")
        print(f"📂 Registry: {args.registry_file}")
        print(f"📁 Category: {args.category or 'all'}")

    elif args.url_file:
        # Load from traditional file
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

        print(f"📄 Using file-based crawling: {args.url_file}")

    else:
        print("❌ Either --url-file or --registry-file is required for crawling operations")
        print("Use --url-file/-f to specify a file containing URLs to crawl")
        print("Use --registry-file to specify a YAML registry configuration")
        return

    # Apply registry settings to arguments if available
    if registry_settings:
        # Use registry settings as defaults, CLI args override
        if args.threshold == DEFAULT_THRESHOLD and 'threshold' in registry_settings:
            args.threshold = registry_settings['threshold']
        if not args.rate_limit and 'rate_limit' in registry_settings:
            args.rate_limit = registry_settings['rate_limit']
        if args.timeout == 20 and 'timeout' in registry_settings:
            args.timeout = registry_settings['timeout']
        if args.max_retries == 3 and 'max_retries' in registry_settings:
            args.max_retries = registry_settings['max_retries']
        if args.backoff_factor == 2.0 and 'backoff_factor' in registry_settings:
            args.backoff_factor = registry_settings['backoff_factor']

        # Apply default keywords if not provided
        if not args.include_keywords and 'default_include_keywords' in registry_settings:
            args.include_keywords = ','.join(registry_settings['default_include_keywords'])
        if not args.exclude_keywords and 'default_exclude_keywords' in registry_settings:
            args.exclude_keywords = ','.join(registry_settings['default_exclude_keywords'])

    # Run semantic crawler
    run_semantic_crawler(
        urls,
        args.threshold,
        args.dry_run,
        args.limit_domains,
        args.save_raw,
        args.proxy_rotate,
        args.max_retries,
        args.include_keywords,
        args.exclude_keywords,
        args.min_word_count,
        args.max_word_count,
        args.content_type_filter,
        args.metadata_output,
        args.validate_content,
        args.rate_limit,
        args.timeout,
        args.backoff_factor,
        registry,
        registry_settings,
        args.validate_content_requirements,
    )


if __name__ == "__main__":
    main()
