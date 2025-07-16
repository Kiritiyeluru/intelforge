#!/usr/bin/env python3
"""
Simple GitHub Scraper for IntelForge

A minimal GitHub scraper using PyGitHub + base framework.
Extracts algorithmic trading repositories and documentation.

Usage:
    python github_scraper.py [--dry-run] [--query "SEARCH_QUERY"] [--limit N]

Example:
    python github_scraper.py --dry-run --query "algorithmic trading python" --limit 5
"""

import argparse
import os
from typing import Dict, List

from dotenv import load_dotenv
from github import Github

from scripts.scraping_base import BaseScraper


class GitHubScraper(BaseScraper):
    """Simple GitHub scraper using PyGitHub + base framework."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize GitHub scraper."""
        super().__init__(config_path, scraper_name="github")

        # Load environment variables for GitHub API
        load_dotenv()

        # Initialize GitHub API
        self._initialize_github()

    def _initialize_github(self):
        """Initialize GitHub API client."""
        try:
            # Get token from environment or config
            access_token = (
                os.getenv("GITHUB_TOKEN")
                or os.getenv("GITHUB_ACCESS_TOKEN")
                or self.config["github"]["access_token"]
                or self.config["api_keys"]["github_token"]
            )

            if not access_token or access_token == "your_github_token_here":
                self.logger.warning(
                    "GitHub access token not found. Using unauthenticated API (lower rate limits)"
                )
                self.github = Github()
            else:
                self.github = Github(access_token)

            # Test the connection
            rate_limit = self.github.get_rate_limit()
            self.logger.info(
                f"GitHub API initialized. Rate limit: {rate_limit.core.remaining}/{rate_limit.core.limit}"
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize GitHub API: {e}")
            self.github = None

    def _clean_text(self, text: str) -> str:
        """Clean and format text content."""
        if not text:
            return ""

        # Basic text cleaning
        text = text.replace("\r\n", "\n")  # Normalize line endings
        text = text.strip()

        return text

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        keywords = self.config["github"]["search_queries"]
        found_keywords = []

        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return found_keywords

    def _is_relevant_repo(self, repo) -> bool:
        """Check if repository is relevant based on filters."""
        try:
            # Skip forks and archived repositories
            if repo.fork or repo.archived:
                return False

            # Check if it has minimum activity (stars, recent commits)
            if repo.stargazers_count < 5:  # Minimum 5 stars
                return False

            # Check for relevant keywords in name and description
            text_to_check = f"{repo.name} {repo.description or ''}".lower()
            keywords = self.config["github"]["search_queries"]

            return any(keyword.lower() in text_to_check for keyword in keywords)

        except Exception as e:
            self.logger.warning(f"Error checking repository relevance: {e}")
            return False

    def _extract_readme_content(self, repo) -> str:
        """Extract README content from repository."""
        try:
            readme = repo.get_readme()
            content = readme.decoded_content.decode("utf-8")
            return self._clean_text(content)
        except Exception as e:
            self.logger.debug(f"Could not get README for {repo.name}: {e}")
            return ""

    def search_repositories(self, query: str, limit: int = None) -> List[Dict]:
        """Search GitHub repositories for a specific query."""
        if not self.github:
            self.logger.error("GitHub API not initialized")
            return []

        if limit is None:
            limit = self.config["github"]["max_results"]

        self.logger.info(f"Searching repositories for: '{query}' (limit: {limit})")

        scraped_repos = []

        try:
            # Search repositories
            search_query = f"{query} language:python"
            repositories = self.github.search_repositories(
                query=search_query, sort="stars", order="desc"
            )

            processed = 0
            for repo in repositories:
                try:
                    if processed >= limit * 2:  # Limit API calls
                        break

                    processed += 1

                    if not self._is_relevant_repo(repo):
                        continue

                    # Extract repository information
                    title = f"{repo.owner.login}/{repo.name}"
                    description = repo.description or "No description available"

                    # Get README content
                    readme_content = self._extract_readme_content(repo)

                    # Build full content
                    content = f"**Repository:** {title}\n\n"
                    content += f"**Description:** {description}\n\n"
                    content += f"**Stars:** {repo.stargazers_count} | **Forks:** {repo.forks_count}\n\n"

                    if readme_content:
                        content += f"**README:**\n{readme_content[:2000]}..."  # Limit README length
                    else:
                        content += "**README:** Not available\n"

                    # Create metadata
                    metadata = {
                        "repository_name": repo.name,
                        "owner": repo.owner.login,
                        "stars": repo.stargazers_count,
                        "forks": repo.forks_count,
                        "language": repo.language,
                        "created_at": (
                            repo.created_at.isoformat() if repo.created_at else None
                        ),
                        "updated_at": (
                            repo.updated_at.isoformat() if repo.updated_at else None
                        ),
                        "topics": list(repo.get_topics()),
                        "license": repo.license.name if repo.license else None,
                        "clone_url": repo.clone_url,
                        "keywords": self._extract_keywords(f"{title} {description}"),
                    }

                    scraped_repo = {
                        "url": repo.html_url,
                        "title": title,
                        "content": content,
                        "metadata": metadata,
                    }

                    scraped_repos.append(scraped_repo)

                    if len(scraped_repos) >= limit:
                        break

                    # Add delay to respect rate limits
                    self._random_delay(
                        self.config["github"]["rate_limit_delay"],
                        self.config["github"]["rate_limit_delay"] + 1,
                    )

                except Exception as e:
                    self.logger.error(f"Error processing repository {repo.name}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error searching repositories for '{query}': {e}")

        self.logger.info(
            f"Found {len(scraped_repos)} relevant repositories for '{query}'"
        )
        return scraped_repos

    def scrape_all_queries(self, limit_per_query: int = None):
        """Scrape repositories for all configured search queries."""
        queries = self.config["github"]["search_queries"]

        self.logger.info(f"Starting to scrape {len(queries)} search queries...")

        all_repos = []

        for query in queries:
            try:
                repos = self.search_repositories(query, limit_per_query)

                # Save each repository
                for repo in repos:
                    self.save_content(
                        repo["url"], repo["title"], repo["content"], repo["metadata"]
                    )

                all_repos.extend(repos)

                # Add delay between queries
                if query != queries[-1]:  # Not the last query
                    self._random_delay(
                        self.config["github"]["rate_limit_delay"] * 2,
                        self.config["github"]["rate_limit_delay"] * 3,
                    )

            except Exception as e:
                self.logger.error(f"Error scraping query '{query}': {e}")
                continue

        self.logger.info(f"Finished scraping. Total repositories: {len(all_repos)}")
        return all_repos

    def get_rate_limit_status(self) -> Dict:
        """Get current GitHub API rate limit status."""
        if not self.github:
            return {"error": "GitHub API not initialized"}

        try:
            rate_limit = self.github.get_rate_limit()
            return {
                "core": {
                    "remaining": rate_limit.core.remaining,
                    "limit": rate_limit.core.limit,
                    "reset": rate_limit.core.reset.isoformat(),
                },
                "search": {
                    "remaining": rate_limit.search.remaining,
                    "limit": rate_limit.search.limit,
                    "reset": rate_limit.search.reset.isoformat(),
                },
            }
        except Exception as e:
            return {"error": str(e)}


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="GitHub Scraper for IntelForge")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--query", type=str, help="Specific search query")
    parser.add_argument(
        "--limit", type=int, help="Limit number of repositories per query"
    )
    parser.add_argument(
        "--config", type=str, default="config/config.yaml", help="Path to config file"
    )
    parser.add_argument(
        "--rate-limit", action="store_true", help="Show rate limit status and exit"
    )

    args = parser.parse_args()

    # Set dry-run mode if specified
    if args.dry_run:
        os.environ["INTELFORGE_DRY_RUN"] = "true"

    try:
        with GitHubScraper(config_path=args.config) as scraper:
            if args.rate_limit:
                # Show rate limit status
                status = scraper.get_rate_limit_status()
                print("GitHub API Rate Limit Status:")
                if "error" in status:
                    print(f"Error: {status['error']}")
                else:
                    print(
                        f"Core API: {status['core']['remaining']}/{status['core']['limit']}"
                    )
                    print(
                        f"Search API: {status['search']['remaining']}/{status['search']['limit']}"
                    )
                return

            if args.query:
                # Scrape specific query
                repos = scraper.search_repositories(args.query, args.limit)
                for repo in repos:
                    scraper.save_content(
                        repo["url"], repo["title"], repo["content"], repo["metadata"]
                    )
            else:
                # Scrape all configured queries
                scraper.scrape_all_queries(args.limit)

    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
