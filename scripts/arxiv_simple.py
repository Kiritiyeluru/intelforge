#!/usr/bin/env python3
"""
ArXiv Research Script - Direct API Usage
Uses lukasschwab/arxiv.py (1.3k stars, official API wrapper)
Simple wrapper for academic paper extraction from ArXiv
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Direct arxiv.py usage (official API wrapper)
import arxiv
import yaml


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
    """
    Search ArXiv papers using official API.
    Direct usage of arxiv.py library.
    """
    papers = []

    # Create arxiv client and search
    client = arxiv.Client()
    search = arxiv.Search(
        query=query, max_results=limit, sort_by=arxiv.SortCriterion.Relevance
    )

    print(f"Searching ArXiv for: '{query}' (limit: {limit})")

    try:
        for result in client.results(search):
            paper = {
                "id": result.entry_id,
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "abstract": result.summary,
                "published": result.published.strftime("%Y-%m-%d"),
                "updated": (
                    result.updated.strftime("%Y-%m-%d") if result.updated else ""
                ),
                "url": result.entry_id,
                "pdf_url": result.pdf_url,
                "categories": result.categories,
                "primary_category": result.primary_category,
                "comment": result.comment or "",
                "journal_ref": result.journal_ref or "",
                "doi": result.doi or "",
            }
            papers.append(paper)

        print(f"Retrieved {len(papers)} papers from ArXiv")
        return papers

    except Exception as e:
        print(f"Error searching ArXiv: {e}")
        return []


def format_paper_markdown(paper: Dict) -> str:
    """Format paper into Obsidian-compatible markdown."""
    authors_str = ", ".join(paper.get("authors", []))
    categories_str = ", ".join(paper.get("categories", []))

    content = f"""---
source: arxiv
type: academic_paper
date: {paper.get("published", "")}
updated: {paper.get("updated", "")}
title: "{paper.get("title", "")}"
authors: "{authors_str}"
categories: [{categories_str}]
primary_category: {paper.get("primary_category", "")}
arxiv_id: {paper.get("id", "").split("/")[-1]}
url: {paper.get("url", "")}
pdf_url: {paper.get("pdf_url", "")}
doi: {paper.get("doi", "")}
journal_ref: "{paper.get("journal_ref", "")}"
content_hash: {generate_content_hash(paper.get("abstract", ""))}
---

# {paper.get("title", "Untitled")}

**Authors:** {authors_str}
**Published:** {paper.get("published", "Unknown")}
**Updated:** {paper.get("updated", "N/A")}
**Primary Category:** {paper.get("primary_category", "")}
**ArXiv ID:** {paper.get("id", "").split("/")[-1]}

**Links:**
- [ArXiv Abstract]({paper.get("url", "")})
- [PDF Download]({paper.get("pdf_url", "")})
{f"- [DOI]({paper.get('doi', '')})" if paper.get("doi") else ""}

## Abstract

{paper.get("abstract", "No abstract available")}

## Categories

{categories_str}

{f"## Journal Reference\n\n{paper.get('journal_ref', '')}\n" if paper.get("journal_ref") else ""}

{f"## Comment\n\n{paper.get('comment', '')}\n" if paper.get("comment") else ""}

## Keywords

#arxiv #academic_paper #research #{paper.get("primary_category", "").replace(".", "_")}

---
*Retrieved from ArXiv on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} using arxiv.py*
"""
    return content


def save_papers(papers: List[Dict], query: str, config: Dict) -> int:
    """Save papers to vault directory."""
    if not papers:
        print("No papers to save")
        return 0

    # Get vault directory from config
    vault_dir = Path(config.get("vault_directory", "vault"))
    academic_dir = vault_dir / "notes" / "academic" / "arxiv"
    academic_dir.mkdir(parents=True, exist_ok=True)

    saved_count = 0

    for paper in papers:
        # Generate filename
        title_slug = slugify(paper.get("title", "untitled"))
        arxiv_id = paper.get("id", "").split("/")[-1].replace(".", "_")
        filename = (
            f"{title_slug}_{arxiv_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
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
        description="ArXiv Research Script - Direct API Usage"
    )
    parser.add_argument(
        "--query", type=str, required=True, help="Search query for ArXiv papers"
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

    print("ArXiv Research Script")
    print(f"Query: {args.query}")
    print(f"Limit: {args.limit}")
    print("-" * 50)

    try:
        # Search papers using direct arxiv.py API
        papers = search_arxiv_papers(args.query, args.limit)

        if papers:
            if not args.dry_run:
                # Save papers
                saved_count = save_papers(papers, args.query, config)
                print(f"\nSuccessfully retrieved and saved {saved_count} ArXiv papers!")
            else:
                print(f"\nDry-run: Would save {len(papers)} papers")

            # Summary
            print("\nSummary:")
            print(f"- Query: {args.query}")
            print(f"- Papers found: {len(papers)}")
            print("- Source: ArXiv (official API)")
            print("- Tool: arxiv.py (1.3k stars)")

            # Show first paper as example
            if papers:
                first_paper = papers[0]
                print("\nExample paper:")
                print(f"- Title: {first_paper.get('title', '')[:80]}...")
                print(f"- Authors: {', '.join(first_paper.get('authors', [])[:3])}")
                print(f"- Published: {first_paper.get('published', '')}")
                print(
                    f"- Categories: {', '.join(first_paper.get('categories', [])[:3])}"
                )
        else:
            print("No papers found for the specified query.")

    except KeyboardInterrupt:
        print("\nSearch interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
