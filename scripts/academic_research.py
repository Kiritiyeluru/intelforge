#!/usr/bin/env python3
"""
Academic Research Script - Multi-Database Search
Uses jannisborn/paperscraper (381 stars, 5 databases)
Simple wrapper for comprehensive academic research
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import yaml

# Direct paperscraper usage (multi-database research tool)
try:
    import paperscraper.get_dumps as get_dumps
    from paperscraper import QUERY_FN_DICT
except ImportError:
    print("Error: paperscraper not installed. Run: pip install paperscraper")
    sys.exit(1)


def load_config(config_path: str = "config/config.yaml") -> Dict:
    """Load configuration from YAML file."""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    import re

    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


def generate_content_hash(content: str) -> str:
    """Generate SHA256 hash for content."""
    import hashlib

    return hashlib.sha256(content.encode()).hexdigest()[:16]


def search_arxiv_papers(query: str, limit: int = 20) -> List[Dict]:
    """Search ArXiv papers using paperscraper."""
    papers = []
    temp_dir = Path("temp_arxiv_search")
    temp_dir.mkdir(exist_ok=True)

    try:
        print(f"Searching ArXiv via paperscraper: '{query}' (limit: {limit})")

        # Use paperscraper's QUERY_FN_DICT for ArXiv
        arxiv_fn = QUERY_FN_DICT.get("arxiv")
        if not arxiv_fn:
            print("ArXiv search function not available in paperscraper")
            return []

        output_file = temp_dir / "arxiv_results.jsonl"

        # Search using paperscraper - ArXiv expects keywords as list
        keywords = [query]  # Simple query as list
        arxiv_fn(keywords, output_filepath=str(output_file))

        # Read results
        if output_file.exists():
            import json

            with open(output_file, "r") as f:
                for line in f:
                    if line.strip():
                        result = json.loads(line)
                        paper = {
                            "id": result.get("arxiv_id", ""),
                            "title": result.get("title", ""),
                            "authors": result.get("authors", []),
                            "abstract": result.get("abstract", ""),
                            "published": result.get("date", ""),
                            "url": f"https://arxiv.org/abs/{result.get('arxiv_id', '')}",
                            "pdf_url": f"https://arxiv.org/pdf/{result.get('arxiv_id', '')}.pdf",
                            "categories": result.get("categories", []),
                            "database": "arxiv",
                        }
                        papers.append(paper)

                        # Limit results manually since ArXiv doesn't support limit parameter
                        if len(papers) >= limit:
                            break

        print(f"Retrieved {len(papers)} papers from ArXiv via paperscraper")

    except Exception as e:
        print(f"Error searching ArXiv: {e}")
    finally:
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    return papers


def search_pubmed_papers(query: str, limit: int = 20) -> List[Dict]:
    """Search PubMed papers using paperscraper."""
    papers = []
    temp_dir = Path("temp_pubmed_search")
    temp_dir.mkdir(exist_ok=True)

    try:
        print(f"Searching PubMed via paperscraper: '{query}' (limit: {limit})")

        # Use paperscraper's QUERY_FN_DICT for PubMed
        pubmed_fn = QUERY_FN_DICT.get("pubmed")
        if not pubmed_fn:
            print("PubMed search function not available in paperscraper")
            return []

        output_file = temp_dir / "pubmed_results.jsonl"

        # Search using paperscraper - PubMed expects keywords as list
        keywords = [query]  # Simple query as list
        pubmed_fn(keywords, output_filepath=str(output_file))

        # Read results
        if output_file.exists():
            import json

            with open(output_file, "r") as f:
                for line in f:
                    if line.strip():
                        result = json.loads(line)
                        paper = {
                            "id": result.get("pmid", result.get("id", "")),
                            "title": result.get("title", ""),
                            "authors": result.get("authors", []),
                            "abstract": result.get("abstract", ""),
                            "published": result.get("date", ""),
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{result.get('pmid', result.get('id', ''))}",
                            "pdf_url": result.get("pdf_url", ""),
                            "keywords": result.get("keywords", []),
                            "journal": result.get("journal", ""),
                            "doi": result.get("doi", ""),
                            "database": "pubmed",
                        }
                        papers.append(paper)

                        # Limit results manually since PubMed doesn't support limit parameter
                        if len(papers) >= limit:
                            break

        print(f"Retrieved {len(papers)} papers from PubMed via paperscraper")

    except Exception as e:
        print(f"Error searching PubMed: {e}")
    finally:
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    return papers


def search_papers(query: str, database: str = "arxiv", limit: int = 20) -> List[Dict]:
    """Search papers from specified database using paperscraper."""
    supported_databases = ["arxiv", "pubmed"]

    if database not in supported_databases:
        print(f"Database '{database}' not supported. Available: {supported_databases}")
        return []

    if database == "arxiv":
        return search_arxiv_papers(query, limit)
    elif database == "pubmed":
        return search_pubmed_papers(query, limit)
    else:
        print(f"Database '{database}' not yet implemented")
        return []


def format_paper_markdown(paper: Dict) -> str:
    """Format paper into Obsidian-compatible markdown."""
    authors_str = ", ".join(paper.get("authors", []))
    categories_str = ", ".join(paper.get("categories", []))
    keywords_str = ", ".join(paper.get("keywords", []))

    content = f"""---
source: {paper.get("database", "academic")}
type: academic_paper
date: {paper.get("published", "")}
title: "{paper.get("title", "")}"
authors: "{authors_str}"
categories: [{categories_str}]
keywords: [{keywords_str}]
database: {paper.get("database", "")}
paper_id: {paper.get("id", "")}
url: {paper.get("url", "")}
pdf_url: {paper.get("pdf_url", "")}
content_hash: {generate_content_hash(paper.get("abstract", ""))}
---

# {paper.get("title", "Untitled")}

**Authors:** {authors_str}
**Published:** {paper.get("published", "Unknown")}
**Database:** {paper.get("database", "").upper()}
**Paper ID:** {paper.get("id", "")}

**Links:**
- [Abstract]({paper.get("url", "")})
{f"- [PDF]({paper.get('pdf_url', '')})" if paper.get("pdf_url") else ""}

## Abstract

{paper.get("abstract", "No abstract available")}

{f"## Categories\n\n{categories_str}\n" if categories_str else ""}

{f"## Keywords\n\n{keywords_str}\n" if keywords_str else ""}

## Tags

#{paper.get("database", "academic")} #academic_paper #research

---
*Retrieved via paperscraper on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    return content


def save_papers(papers: List[Dict], query: str, database: str, config: Dict) -> int:
    """Save papers to vault directory."""
    if not papers:
        print("No papers to save")
        return 0

    # Get vault directory from config
    vault_dir = Path(config.get("vault_directory", "vault"))
    academic_dir = vault_dir / "notes" / "academic" / database
    academic_dir.mkdir(parents=True, exist_ok=True)

    saved_count = 0

    for paper in papers:
        # Generate filename
        title_slug = slugify(paper.get("title", "untitled"))
        paper_id = slugify(str(paper.get("id", "unknown")))
        filename = (
            f"{title_slug}_{paper_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )

        # Format content
        content = format_paper_markdown(paper)

        # Save file
        file_path = academic_dir / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            saved_count += 1
            print(f"Saved: {filename}")

        except Exception as e:
            print(f"Failed to save {filename}: {e}")

    print(f"Saved {saved_count} papers to {academic_dir}")
    return saved_count


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Academic Research Script - Multi-Database Search"
    )
    parser.add_argument(
        "--query", type=str, required=True, help="Search query for academic papers"
    )
    parser.add_argument(
        "--database",
        type=str,
        default="arxiv",
        choices=["arxiv", "pubmed"],
        help="Academic database to search",
    )
    parser.add_argument(
        "--limit", type=int, default=20, help="Maximum number of papers to retrieve"
    )
    parser.add_argument(
        "--config", type=str, default="config/config.yaml", help="Path to config file"
    )
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")

    args = parser.parse_args()

    # Set dry-run mode if specified
    if args.dry_run:
        os.environ["INTELFORGE_DRY_RUN"] = "true"
        print("Running in dry-run mode")

    # Load configuration
    config = load_config(args.config)

    print("Academic Research Script - Multi-Database Search")
    print(f"Query: {args.query}")
    print(f"Database: {args.database}")
    print(f"Limit: {args.limit}")
    print("-" * 50)

    try:
        # Search papers using direct paperscraper API
        papers = search_papers(args.query, args.database, args.limit)

        if papers:
            if not args.dry_run:
                # Save papers
                saved_count = save_papers(papers, args.query, args.database, config)
                print(
                    f"\nSuccessfully retrieved and saved {saved_count} academic papers!"
                )
            else:
                print(f"\nDry-run: Would save {len(papers)} papers")

            # Summary
            print("\nSummary:")
            print(f"- Query: {args.query}")
            print(f"- Database: {args.database}")
            print(f"- Papers found: {len(papers)}")
            print("- Tool: paperscraper (381 stars, 5 databases)")

            # Show first paper as example
            if papers:
                first_paper = papers[0]
                print("\nExample paper:")
                print(f"- Title: {first_paper.get('title', '')[:80]}...")
                print(f"- Authors: {', '.join(first_paper.get('authors', [])[:3])}")
                print(f"- Published: {first_paper.get('published', '')}")
                print(f"- Database: {first_paper.get('database', '').upper()}")
        else:
            print(f"No papers found in {args.database} for the specified query.")

    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
