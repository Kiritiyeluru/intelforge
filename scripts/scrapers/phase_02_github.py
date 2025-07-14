#!/usr/bin/env python3
"""
Phase 02: GitHub Repository Mining
🔍 Fetches GitHub repositories for strategy keywords and saves them as Markdown notes.

Follows:
- Simplicity-first structure (single script, flat output)
- Reuse-over-build (uses PyGitHub)
- Config-driven (uses config.yaml)

Usage: python phase_02_github.py [--dry-run]
"""

import os
import yaml
import logging
import argparse


def load_config(config_path="config/config.yaml"):
    """Load configuration with error handling"""
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML in config: {e}")
        exit(1)


def setup_logging(log_file):
    """Initialize logging to file and console"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


def fetch_github_repos(config, dry_run=False):
    """
    Core GitHub scraping logic
    TODO: Implement using PyGitHub when ready for Phase 2
    """
    try:
        # Import PyGitHub when implementing
        # from github import Github

        github_config = config["github"]
        query = github_config["query"]
        max_results = github_config["max_results"]

        logging.info(
            f"Starting GitHub fetch: query='{query}', max_results={max_results}"
        )

        if dry_run:
            logging.info("🧪 DRY RUN MODE - No files will be written")
            return

        # TODO: Implement actual GitHub API calls here
        logging.info("⚠️  GitHub scraping not yet implemented - this is phase 02")
        logging.info("💡 Phase 01 (Reddit) should be implemented first")

    except Exception as e:
        logging.error(f"GitHub fetch failed: {e}")
        raise


def main():
    """Main execution with CLI argument handling"""
    parser = argparse.ArgumentParser(
        description="GitHub repository mining for IntelForge"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Run without writing files"
    )
    parser.add_argument(
        "--config", default="config/config.yaml", help="Config file path"
    )
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Setup logging
    log_file = config["paths"]["log_file"].replace(
        "github_fetch.log", "phase_02_github.log"
    )
    setup_logging(log_file)

    # Determine dry-run mode
    dry_run = args.dry_run or config["options"]["dry_run"]

    try:
        logging.info("=== Phase 02: GitHub Repository Mining Started ===")
        fetch_github_repos(config, dry_run)
        logging.info("✅ Phase 02 completed successfully")

    except Exception as e:
        logging.error(f"❌ Phase 02 failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()
