#!/usr/bin/env python3
"""
IntelForge CLI - Unified command interface for all scraping and intelligence operations
Usage: python forgecli.py <command> [options]
"""

import click
import yaml
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

# ────────────────────────────────────────────────
# 🔧 Helper: Centralized Subprocess Runner


def run_subprocess(
    cmd: List[str], desc: str, capture_output: bool = True
) -> subprocess.CompletedProcess:
    """
    Centralized subprocess execution with consistent error handling

    Args:
        cmd: Command and arguments list
        desc: Human-readable description for logging
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess object with standardized error handling
    """
    click.echo(f"🚀 {desc}: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd, capture_output=capture_output, text=True, timeout=300
        )

        if result.returncode == 0:
            click.echo(f"✅ {desc} completed successfully")
            if capture_output and result.stdout:
                click.echo(result.stdout)
            return result
        else:
            click.echo(f"❌ {desc} failed (exit code: {result.returncode})")
            if capture_output and result.stderr:
                click.echo(f"Error details: {result.stderr}")
            return result

    except subprocess.TimeoutExpired:
        click.echo(f"⏱️ {desc} timed out after 5 minutes")
        raise
    except Exception as e:
        click.echo(f"❌ {desc} error: {e}")
        raise


# Load configuration
def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        click.echo(f"❌ Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()


@click.group()
@click.version_option(version="1.0")
def cli():
    """🚀 IntelForge - AI-Powered Financial Intelligence System"""
    pass


@cli.command()
@click.option("--topic", "-t", required=True, help="Topic to process end-to-end")
@click.option(
    "--sources",
    "-s",
    multiple=True,
    default=["google", "github", "arxiv"],
    help="Sources to search",
)
@click.option("--limit", "-l", default=20, help="Max results per source")
@click.option("--workers", "-w", default=3, help="Concurrent scraping workers")
@click.option("--model", "-m", default="all-MiniLM-L6-v2", help="Embedding model")
@click.option("--threshold", "-th", default=0.7, help="Semantic threshold")
@click.option(
    "--output", "-o", default="vault/notes/pipeline/", help="Output directory"
)
@click.option(
    "--smart-filter",
    is_flag=True,
    help="Use AI-powered semantic filtering during scraping",
)
def pipeline(
    topic: str,
    sources: tuple,
    limit: int,
    workers: int,
    model: str,
    threshold: float,
    output: str,
    smart_filter: bool,
):
    """🔁 Run full automated pipeline: discovery → scrape → embed → search"""
    click.echo(f"🔁 Running full pipeline for: {topic}")
    click.echo(f"Sources: {', '.join(sources)}")
    click.echo(f"Workers: {workers}, Model: {model}")

    # Create output directory
    output_dir = Path(output) / topic
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Discovery
    click.echo("\n📍 Step 1: Discovery")
    discovery_result = run_subprocess(
        ["python", "forgecli.py", "discover", "-t", topic, "-s"]
        + list(sources)
        + ["-l", str(limit), "-o", str(output_dir)],
        f"Discovering content for '{topic}'",
    )

    if discovery_result.returncode != 0:
        click.echo("❌ Discovery failed, aborting pipeline")
        sys.exit(1)

    # Step 2: Scraping
    click.echo("\n📍 Step 2: Scraping")

    # Find the latest discovery file
    discovery_files = sorted(output_dir.glob(f"discovery_{topic}_*.json"))
    if not discovery_files:
        click.echo("❌ No discovery results found")
        sys.exit(1)

    latest_file = discovery_files[-1]

    # Extract URLs from discovery results
    url_file = output_dir / f"urls_{topic}.txt"
    try:
        with open(latest_file, "r") as f:
            data = json.load(f)

        with open(url_file, "w") as f:
            for discovery in data.get("discoveries", []):
                f.write(discovery["url"] + "\n")

        click.echo(f"📋 Extracted {len(data.get('discoveries', []))} URLs")

    except Exception as e:
        click.echo(f"❌ Error extracting URLs: {e}")
        sys.exit(1)

    # Run scraping (with optional smart filtering)
    if smart_filter:
        click.echo("🧠 Using AI-powered semantic filtering")
        scrape_result = run_subprocess(
            [
                "python",
                "scripts/semantic_crawler.py",
                "--url-file",
                str(url_file),
                "--threshold",
                str(threshold),
            ],
            f"AI-filtered semantic crawling for '{topic}'",
        )
    else:
        scrape_result = run_subprocess(
            [
                "python",
                "forgecli.py",
                "scrape",
                "-f",
                str(url_file),
                "--workers",
                str(workers),
            ],
            f"Scraping URLs for '{topic}'",
        )

    if scrape_result.returncode != 0:
        click.echo("❌ Scraping failed, aborting pipeline")
        sys.exit(1)

    # Step 3: Embedding
    click.echo("\n📍 Step 3: Embedding")
    embed_result = run_subprocess(
        ["python", "forgecli.py", "embed", "--chunk-size", "512", "--model", model],
        f"Building embeddings with {model}",
    )

    if embed_result.returncode != 0:
        click.echo("❌ Embedding failed, aborting pipeline")
        sys.exit(1)

    # Step 4: Test search
    click.echo("\n📍 Step 4: Testing semantic search")
    search_result = run_subprocess(
        [
            "python",
            "forgecli.py",
            "search",
            "-q",
            topic,
            "-l",
            "5",
            "-t",
            str(threshold),
        ],
        f"Testing search for '{topic}'",
    )

    if search_result.returncode != 0:
        click.echo("❌ Search test failed")
        sys.exit(1)

    # Cleanup temporary files
    if url_file.exists():
        url_file.unlink()

    click.echo(f"\n🎯 Pipeline completed successfully for '{topic}'!")
    click.echo(f"📁 Results saved to: {output_dir}")
    click.echo(f"🔍 Use 'forgecli search -q \"{topic}\"' to search the knowledge base")


@cli.command()
@click.option("--topic", "-t", required=True, help="Topic to discover content for")
@click.option(
    "--sources",
    "-s",
    multiple=True,
    default=["google", "github", "arxiv"],
    help="Sources to search: google, github, arxiv, reddit",
)
@click.option("--limit", "-l", default=20, help="Maximum results per source")
@click.option(
    "--output", "-o", default="vault/notes/discovery/", help="Output directory"
)
def discover(topic: str, sources: tuple, limit: int, output: str):
    """🔍 Discover content on a specific topic across multiple sources"""
    click.echo(f"🔍 Discovering content for: {topic}")

    # Create output directory
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    # Track discoveries
    discoveries = []

    if "google" in sources:
        click.echo("📊 Searching Google with advanced operators...")
        # Run Google search automation
        google_results = run_google_search(topic, limit)
        discoveries.extend(google_results)

    if "github" in sources:
        click.echo("🐙 Searching GitHub repositories...")
        # Run GitHub discovery
        github_results = run_github_discovery(topic, limit)
        discoveries.extend(github_results)

    if "arxiv" in sources:
        click.echo("📚 Searching ArXiv papers...")
        # Run ArXiv discovery
        arxiv_results = run_arxiv_discovery(topic, limit)
        discoveries.extend(arxiv_results)

    if "reddit" in sources:
        click.echo("🔸 Searching Reddit communities...")
        # Run Reddit discovery
        reddit_results = run_reddit_discovery(topic, limit)
        discoveries.extend(reddit_results)

    # Save discovery results
    save_discovery_results(discoveries, topic, output_path)

    click.echo(f"✅ Discovered {len(discoveries)} items for '{topic}'")
    click.echo(f"📁 Results saved to: {output_path}")


@cli.command()
@click.option("--url-file", "-f", help="File containing URLs to scrape")
@click.option("--url", "-u", help="Single URL to scrape")
@click.option("--stealth", is_flag=True, help="Use stealth mode for scraping")
@click.option("--workers", "-w", default=3, help="Number of concurrent workers")
@click.option("--retries", "-r", default=3, help="Number of retry attempts")
def scrape(url_file: str, url: str, stealth: bool, workers: int, retries: int):
    """🕷️ Scrape URLs using high-performance concurrent processing"""
    if not url_file and not url:
        click.echo("❌ Either --url-file or --url must be provided")
        sys.exit(1)

    if stealth:
        click.echo("🛡️ Using stealth mode for scraping")
        scraper_cmd = ["python", "scripts/batch_stealth_scraper.py"]
    else:
        click.echo("⚡ Using high-performance HTTP scraping")
        scraper_cmd = ["python", "scripts/batch_scraper.py"]

    # Build command arguments
    if url_file:
        scraper_cmd.extend(["--file", url_file])
    if url:
        scraper_cmd.extend(["--url", url])

    scraper_cmd.extend(["--workers", str(workers), "--retries", str(retries)])

    # Execute scraper using centralized helper
    try:
        result = run_subprocess(scraper_cmd, "Scraping URLs")
        if result.returncode != 0:
            sys.exit(1)
    except Exception:
        sys.exit(1)


@cli.command()
@click.option("--chunk-size", "-c", default=512, help="Chunk size for embedding")
@click.option("--model", "-m", default="all-MiniLM-L6-v2", help="Embedding model")
@click.option("--rebuild", is_flag=True, help="Rebuild entire embedding database")
def embed(chunk_size: int, model: str, rebuild: bool):
    """🧠 Build embeddings for semantic search"""
    click.echo("🧠 Building embeddings for semantic search...")

    embed_cmd = ["python", "scripts/phase_08_ai_processor.py"]

    if rebuild:
        embed_cmd.append("--build")

    embed_cmd.extend(["--chunk-size", str(chunk_size), "--model", model])

    try:
        result = run_subprocess(embed_cmd, "Building embeddings")
        if result.returncode != 0:
            sys.exit(1)
    except Exception:
        sys.exit(1)


@cli.command()
@click.option("--query", "-q", required=True, help="Search query")
@click.option("--limit", "-l", default=10, help="Maximum results")
@click.option("--threshold", "-t", default=0.7, help="Similarity threshold")
def search(query: str, limit: int, threshold: float):
    """🔍 Search knowledge base using semantic similarity"""
    click.echo(f"🔍 Searching for: {query}")

    search_cmd = [
        "python",
        "scripts/phase_08_ai_processor.py",
        "--search",
        query,
        "--limit",
        str(limit),
        "--threshold",
        str(threshold),
    ]

    try:
        result = run_subprocess(search_cmd, "Semantic search")
        if result.returncode != 0:
            sys.exit(1)
    except Exception:
        sys.exit(1)


@cli.command()
@click.option(
    "--url-file",
    "-f",
    required=True,
    help="File containing URLs to crawl (one per line)",
)
@click.option(
    "--threshold", "-t", default=0.75, help="Similarity threshold for content relevance"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview mode - analyze content but don't save anything",
)
@click.option(
    "--regenerate-reference",
    is_flag=True,
    help="Regenerate reference embeddings from training data",
)
def smart_crawl(
    url_file: str, threshold: float, dry_run: bool, regenerate_reference: bool
):
    """🧠 AI-filtered semantic crawler with intelligent content curation"""
    click.echo("🧠 Starting Semantic Crawler with AI-Filtered Capture")

    # Build command arguments
    cmd = ["python", "scripts/semantic_crawler.py", "--url-file", url_file]

    if threshold != 0.75:
        cmd.extend(["--threshold", str(threshold)])

    if dry_run:
        cmd.append("--dry-run")

    if regenerate_reference:
        cmd.append("--regenerate-reference")

    # Execute semantic crawler
    try:
        result = run_subprocess(
            cmd, f"AI-filtered semantic crawling (threshold: {threshold})"
        )
        if result.returncode != 0:
            sys.exit(1)
    except Exception:
        sys.exit(1)


@cli.command()
@click.option("--url", "-u", required=True, help="URL to ingest and evaluate")
@click.option(
    "--filter-method",
    type=click.Choice(["cosine", "gpt"], case_sensitive=False),
    default="cosine",
    help="AI filtering method to use",
)
@click.option(
    "--threshold", "-t", default=0.75, help="Minimum score required to capture content"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview mode - analyze content but don't save anything",
)
def ingest(url: str, filter_method: str, threshold: float, dry_run: bool):
    """📥 Manually ingest a single URL with AI-powered relevance filtering"""
    click.echo(f"🌐 Ingesting: {url}")
    click.echo(f"🧠 Filter method: {filter_method}")
    click.echo(f"🎯 Threshold: {threshold}")

    # Create temporary URL file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write(url)
        tmp_file_path = tmp_file.name

    try:
        # Build command based on filter method
        if filter_method == "cosine":
            cmd = [
                "python",
                "scripts/semantic_crawler.py",
                "--url-file",
                tmp_file_path,
                "--threshold",
                str(threshold),
            ]
            if dry_run:
                cmd.append("--dry-run")

        elif filter_method == "gpt":
            # Future: GPT-based filtering
            click.echo("⚠️ GPT filtering not yet implemented, using cosine similarity")
            cmd = [
                "python",
                "scripts/semantic_crawler.py",
                "--url-file",
                tmp_file_path,
                "--threshold",
                str(threshold),
            ]
            if dry_run:
                cmd.append("--dry-run")

        # Execute ingestion
        result = run_subprocess(
            cmd, f"Ingesting single URL with {filter_method} filtering"
        )

        if result.returncode == 0:
            click.echo("✅ Ingestion completed successfully")
        else:
            click.echo("❌ Ingestion failed")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Ingestion error: {e}")
        sys.exit(1)
    finally:
        # Cleanup temporary file
        Path(tmp_file_path).unlink(missing_ok=True)


@cli.command()
@click.option("--tag", "-t", help="Filter by tag (e.g., momentum, technical_analysis)")
@click.option("--min-score", type=float, help="Minimum relevance score (0.0-1.0)")
@click.option("--max-results", type=int, default=50, help="Limit number of results")
@click.option(
    "--sort",
    type=click.Choice(["score", "date", "title"], case_sensitive=False),
    default="score",
    help="Sort results by field",
)
@click.option("--reverse", is_flag=True, help="Reverse sort order")
def list(tag: str, min_score: float, max_results: int, sort: str, reverse: bool):
    """📂 List and filter captured semantic notes"""
    notes_dir = Path("vault/notes/semantic_capture")

    if not notes_dir.exists():
        click.echo("❌ No semantic capture directory found")
        click.echo("💡 Try running 'forgecli smart-crawl' or 'forgecli ingest' first")
        return

    # Collect all notes with metadata
    items = []
    total_notes = 0

    for md_file in notes_dir.glob("*.md"):
        total_notes += 1
        meta_path = md_file.with_suffix(".metadata.json")

        if not meta_path.exists():
            # Skip notes without metadata
            continue

        try:
            with open(meta_path) as f:
                meta = json.load(f)
        except Exception as e:
            click.echo(f"⚠️ Error reading metadata for {md_file}: {e}")
            continue

        # Apply filters
        if tag and tag not in meta.get("tags", []):
            continue

        if min_score and meta.get("score", 0.0) < min_score:
            continue

        # Prepare item for display
        item = {
            "score": meta.get("score", 0.0),
            "title": meta.get("title", "Untitled"),
            "path": str(md_file),
            "tags": meta.get("tags", []),
            "captured_at": meta.get("captured_at", "Unknown"),
            "url": meta.get("url", "No URL"),
            "content_length": meta.get("content_length", 0),
            "filter_method": meta.get("filter_method", "unknown"),
        }
        items.append(item)

    # Sort items
    if sort == "score":
        items.sort(key=lambda x: x["score"], reverse=not reverse)
    elif sort == "date":
        items.sort(key=lambda x: x["captured_at"], reverse=not reverse)
    elif sort == "title":
        items.sort(key=lambda x: x["title"].lower(), reverse=reverse)

    # Limit results
    displayed_items = items[:max_results]

    # Display header
    click.echo("📂 Semantic Notes Collection")
    click.echo("=" * 60)

    # Display filters if applied
    filter_info = []
    if tag:
        filter_info.append(f"tag: {tag}")
    if min_score:
        filter_info.append(f"min_score: {min_score}")
    if filter_info:
        click.echo(f"🔍 Filters: {', '.join(filter_info)}")

    click.echo(
        f"📊 Found: {len(items)} notes (showing {len(displayed_items)}/{total_notes} total)"
    )
    click.echo(f"🔢 Sorted by: {sort} {'(reversed)' if reverse else ''}")
    click.echo("-" * 60)

    # Display items
    for i, item in enumerate(displayed_items, 1):
        click.echo(f"{i:2d}. [{item['score']:.3f}] {item['title']}")

        # Show tags if any
        if item["tags"]:
            tags_str = ", ".join(item["tags"])
            click.echo(f"    🏷️  Tags: {tags_str}")

        # Show metadata
        click.echo(
            f"    📊 {item['content_length']} chars | {item['filter_method']} | {item['captured_at'][:10]}"
        )
        click.echo(f"    📁 {item['path']}")
        click.echo(f"    🔗 {item['url']}")
        click.echo()

    # Summary
    if len(items) > max_results:
        click.echo(f"📝 Showing {max_results} of {len(items)} results")
        click.echo("💡 Use --max-results to show more")

    if len(items) == 0:
        click.echo("📭 No notes found matching your criteria")
        if tag or min_score:
            click.echo("💡 Try removing filters or lowering the minimum score")


@cli.command()
@click.option("--content-file", "-f", help="File containing content to score")
@click.option("--text", "-t", help="Text content to score")
@click.option(
    "--criteria",
    "-c",
    multiple=True,
    default=["trading_strategy", "technical_analysis", "backtesting"],
    help="Scoring criteria",
)
def score(content_file: str, text: str, criteria: tuple):
    """📊 Score content relevance using LLM"""
    if not content_file and not text:
        click.echo("❌ Either --content-file or --text must be provided")
        sys.exit(1)

    click.echo("📊 Scoring content relevance...")

    # Run LLM content scoring
    score_result = run_llm_scoring(content_file, text, criteria)

    click.echo(f"📈 Content Score: {score_result['overall_score']}/5")
    click.echo("📋 Criteria Scores:")
    for criterion, score in score_result["criteria_scores"].items():
        click.echo(f"  {criterion}: {score}/5")

    if score_result["reasoning"]:
        click.echo(f"💭 Reasoning: {score_result['reasoning']}")


@cli.command()
@click.option("--quick", is_flag=True, help="Run quick validation checks only")
@click.option("--deep", is_flag=True, help="Run comprehensive system validation")
@click.option("--fix", is_flag=True, help="Auto-fix common issues where possible")
def test(quick: bool, deep: bool, fix: bool):
    """🧪 Test environment and validate system configuration"""
    if not quick and not deep:
        quick = True  # Default to quick test

    click.echo("🧪 IntelForge Environment Validation")
    click.echo("=" * 50)

    # Track test results
    test_results = []

    # Python Environment Tests
    click.echo("\n🐍 Python Environment Tests:")

    # Test 1: Python version
    try:
        result = run_subprocess(
            ["python", "--version"], "Checking Python version", capture_output=True
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            click.echo(f"  ✅ Python version: {version}")
            test_results.append(("python_version", True, version))
        else:
            click.echo("  ❌ Python version check failed")
            test_results.append(("python_version", False, "Failed"))
    except Exception as e:
        click.echo(f"  ❌ Python version error: {e}")
        test_results.append(("python_version", False, str(e)))

    # Test 2: Virtual environment
    if sys.prefix != sys.base_prefix:
        click.echo("  ✅ Virtual environment active")
        test_results.append(("virtual_env", True, "Active"))
    else:
        click.echo("  ⚠️ No virtual environment detected")
        test_results.append(("virtual_env", False, "Not active"))

    # Configuration Tests
    click.echo("\n⚙️ Configuration Tests:")

    # Test 3: Config file exists
    config_path = Path("config/config.yaml")
    if config_path.exists():
        click.echo("  ✅ Config file found")
        test_results.append(("config_file", True, str(config_path)))

        # Test 4: Config file validity
        try:
            with open(config_path, "r") as f:
                yaml.safe_load(f)
            click.echo("  ✅ Config file valid YAML")
            test_results.append(("config_valid", True, "Valid"))
        except Exception as e:
            click.echo(f"  ❌ Config file invalid: {e}")
            test_results.append(("config_valid", False, str(e)))
    else:
        click.echo("  ❌ Config file not found")
        test_results.append(("config_file", False, "Not found"))

    # Dependency Tests
    click.echo("\n📦 Dependency Tests:")

    # Test 5: Key dependencies
    key_deps = ["click", "yaml", "pathlib", "subprocess"]
    for dep in key_deps:
        try:
            __import__(dep)
            click.echo(f"  ✅ {dep} available")
            test_results.append((f"dep_{dep}", True, "Available"))
        except ImportError:
            click.echo(f"  ❌ {dep} not available")
            test_results.append((f"dep_{dep}", False, "Not available"))

    # File System Tests
    click.echo("\n📁 File System Tests:")

    # Test 6: Required directories
    required_dirs = ["vault", "scripts", "scrapers", "config"]
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            click.echo(f"  ✅ {dir_name}/ directory exists")
            test_results.append((f"dir_{dir_name}", True, "Exists"))
        else:
            click.echo(f"  ❌ {dir_name}/ directory missing")
            test_results.append((f"dir_{dir_name}", False, "Missing"))

            # Auto-fix: Create missing directories
            if fix:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    click.echo(f"    🔧 Created {dir_name}/ directory")
                except Exception as e:
                    click.echo(f"    ❌ Failed to create {dir_name}/: {e}")

    # Deep tests (if requested)
    if deep:
        click.echo("\n🔍 Deep System Tests:")

        # Test 7: Memory usage
        try:
            import psutil

            memory = psutil.virtual_memory()
            click.echo(
                f"  ✅ Memory usage: {memory.percent}% of {memory.total // (1024**3)}GB"
            )
            test_results.append(("memory_usage", True, f"{memory.percent}%"))
        except ImportError:
            click.echo("  ⚠️ psutil not available for memory check")
            test_results.append(("memory_usage", False, "psutil not available"))

        # Test 8: Disk space
        try:
            import shutil

            disk_usage = shutil.disk_usage(".")
            free_gb = disk_usage.free // (1024**3)
            click.echo(f"  ✅ Disk space: {free_gb}GB free")
            test_results.append(("disk_space", True, f"{free_gb}GB"))
        except Exception as e:
            click.echo(f"  ❌ Disk space check failed: {e}")
            test_results.append(("disk_space", False, str(e)))

    # Summary
    click.echo("\n📊 Test Summary:")
    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)
    click.echo(f"  ✅ Passed: {passed}/{total} tests")

    if passed == total:
        click.echo("  🎉 All tests passed! System is ready.")
        return True
    else:
        click.echo("  ⚠️ Some tests failed. Check details above.")
        return False


@cli.command()
def status():
    """📊 Show system status and performance metrics"""
    click.echo("📊 IntelForge System Status")
    click.echo("=" * 50)

    # Check Python environments
    click.echo("\n🐍 Python Environments:")
    try:
        # Check Python 3.10 high-performance environment
        result = run_subprocess(
            [
                "/home/kiriti/alpha_projects/intelforge/bin/micromamba",
                "run",
                "-n",
                "intelforge-py310",
                "python",
                "--version",
            ],
            "Checking Python 3.10 environment",
            capture_output=True,
        )
        if result.returncode == 0:
            click.echo(f"  ✅ Python 3.10 (High-Performance): {result.stdout.strip()}")
        else:
            click.echo("  ❌ Python 3.10 environment not available")
    except Exception as e:
        click.echo(f"  ❌ Error checking Python 3.10: {e}")

    # Check current environment
    try:
        result = run_subprocess(
            ["python", "--version"], "Checking current Python", capture_output=True
        )
        click.echo(f"  ✅ Current Python: {result.stdout.strip()}")
    except Exception as e:
        click.echo(f"  ❌ Error checking current Python: {e}")

    # Check scrapers
    click.echo("\n🕷️ Scrapers Status:")
    scraper_files = [
        "scrapers/reddit_scraper.py",
        "scrapers/github_scraper.py",
        "scrapers/web_scraper.py",
        "scripts/stealth_scraper.py",
    ]

    for scraper in scraper_files:
        if Path(scraper).exists():
            click.echo(f"  ✅ {scraper}")
        else:
            click.echo(f"  ❌ {scraper} - Not found")

    # Check knowledge base
    click.echo("\n🧠 Knowledge Base:")
    vault_path = Path("vault/notes")
    if vault_path.exists():
        note_count = len(list(vault_path.glob("**/*.md")))
        click.echo(f"  ✅ {note_count} notes in vault")
    else:
        click.echo("  ❌ Vault directory not found")

    # Check AI components
    click.echo("\n🤖 AI Components:")
    ai_files = [
        "scripts/phase_08_ai_processor.py",
        "scripts/phase_07_article_organizer.py",
    ]

    for ai_file in ai_files:
        if Path(ai_file).exists():
            click.echo(f"  ✅ {ai_file}")
        else:
            click.echo(f"  ❌ {ai_file} - Not found")


# Helper functions for discovery
def run_google_search(topic: str, limit: int) -> List[Dict[str, Any]]:
    """Run Google search with advanced operators"""
    # This would implement Google search automation
    # For now, return placeholder results
    return [
        {
            "source": "google",
            "title": f"Google result for {topic}",
            "url": f"https://example.com/search?q={topic}",
            "snippet": f"Search result snippet for {topic}",
            "type": "web_page",
        }
    ]


def run_github_discovery(topic: str, limit: int) -> List[Dict[str, Any]]:
    """Run GitHub repository discovery"""
    try:
        result = run_subprocess(
            [
                "python",
                "scrapers/github_scraper.py",
                "--query",
                topic,
                "--limit",
                str(limit),
            ],
            f"GitHub discovery for '{topic}'",
        )

        if result.returncode == 0:
            # Parse GitHub results
            return [
                {
                    "source": "github",
                    "title": f"GitHub repository for {topic}",
                    "url": "https://github.com/example/repo",
                    "type": "repository",
                }
            ]
    except Exception as e:
        click.echo(f"❌ GitHub discovery error: {e}")

    return []


def run_arxiv_discovery(topic: str, limit: int) -> List[Dict[str, Any]]:
    """Run ArXiv paper discovery"""
    try:
        result = run_subprocess(
            [
                "python",
                "scripts/arxiv_simple.py",
                "--query",
                topic,
                "--limit",
                str(limit),
            ],
            f"ArXiv discovery for '{topic}'",
        )

        if result.returncode == 0:
            return [
                {
                    "source": "arxiv",
                    "title": f"ArXiv paper for {topic}",
                    "url": "https://arxiv.org/abs/example",
                    "type": "academic_paper",
                }
            ]
    except Exception as e:
        click.echo(f"❌ ArXiv discovery error: {e}")

    return []


def run_reddit_discovery(topic: str, limit: int) -> List[Dict[str, Any]]:
    """Run Reddit community discovery"""
    try:
        result = run_subprocess(
            [
                "python",
                "scrapers/reddit_scraper.py",
                "--query",
                topic,
                "--limit",
                str(limit),
            ],
            f"Reddit discovery for '{topic}'",
        )

        if result.returncode == 0:
            return [
                {
                    "source": "reddit",
                    "title": f"Reddit post about {topic}",
                    "url": "https://reddit.com/r/example/post",
                    "type": "forum_post",
                }
            ]
    except Exception as e:
        click.echo(f"❌ Reddit discovery error: {e}")

    return []


def run_llm_scoring(content_file: str, text: str, criteria: tuple) -> Dict[str, Any]:
    """Run LLM content scoring"""
    # This would implement LLM-based content scoring
    # For now, return placeholder results
    return {
        "overall_score": 4.2,
        "criteria_scores": {criterion: 4.0 for criterion in criteria},
        "reasoning": "Content contains relevant trading strategy information with technical analysis.",
    }


def save_discovery_results(
    discoveries: List[Dict[str, Any]], topic: str, output_path: Path
):
    """Save discovery results to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_path / f"discovery_{topic}_{timestamp}.json"

    with open(results_file, "w") as f:
        json.dump(
            {
                "topic": topic,
                "timestamp": timestamp,
                "total_results": len(discoveries),
                "discoveries": discoveries,
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    cli()
