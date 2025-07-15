#!/usr/bin/env python3
"""
Phase 1: Reddit Scraping Module for IntelForge

Extract algorithmic trading strategies and discussions from Reddit.
Outputs Obsidian-compatible markdown with metadata.

Usage:
    python phase_01_reddit.py [--dry-run] [--subreddit SUBREDDIT] [--limit N]

Example:
    python phase_01_reddit.py --dry-run --subreddit algotrading --limit 10
"""

import argparse
import hashlib
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import praw
import yaml
from dotenv import load_dotenv


class IntelForgeRedditScraper:
    """Reddit content extractor for algorithmic trading research."""

    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Reddit scraper with configuration."""
        # Load environment variables
        load_dotenv()

        self.config = self._load_config(config_path)
        self.reddit = None
        self.dry_run = self.config["options"]["dry_run"]

        # Set up logging
        self._setup_logging()

        # Initialize Reddit API
        if not self.dry_run:
            self._initialize_reddit()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)
                self.logger = self._setup_basic_logging()
                self.logger.info(f"Configuration loaded from {config_path}")
                return config
        except FileNotFoundError:
            print(f"ERROR: Configuration file {config_path} not found")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"ERROR: Invalid YAML configuration: {e}")
            sys.exit(1)

    def _setup_basic_logging(self) -> logging.Logger:
        """Set up basic logging before full configuration is loaded."""
        logger = logging.getLogger("intelforge.reddit")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _setup_logging(self):
        """Set up comprehensive logging to file and console."""
        # Create logs directory if it doesn't exist
        logs_dir = Path(self.config["paths"]["log_file"])
        logs_dir.mkdir(parents=True, exist_ok=True)

        # Set up file logging
        log_file = (
            logs_dir / f"reddit_scraper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        self.logger = logging.getLogger("intelforge.reddit")
        self.logger.setLevel(
            logging.DEBUG if self.config["options"]["verbose_logging"] else logging.INFO
        )

        # Clear any existing handlers
        self.logger.handlers.clear()

        # File handler
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        self.logger.info(f"Logging initialized. Log file: {log_file}")

    def _initialize_reddit(self):
        """Initialize Reddit API connection."""
        reddit_config = self.config["reddit"]

        # Get credentials from environment variables
        client_id = os.getenv("reddit_api_client_id")
        client_secret = os.getenv("reddit_api_client_secret")

        if not client_id or not client_secret:
            self.logger.error("Reddit API credentials not found in .env file")
            self.logger.error(
                "Please add reddit_api_client_id and reddit_api_client_secret to .env"
            )
            self.logger.error("Get credentials at: https://www.reddit.com/prefs/apps")
            sys.exit(1)

        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=reddit_config["user_agent"],
                ratelimit_seconds=reddit_config["rate_limit_delay"],
            )

            # Test connection (this will fail if credentials are invalid)
            self.logger.info("Testing Reddit API connection...")
            # For script-type apps, we can't call user.me(), so just test basic access
            test_subreddit = self.reddit.subreddit("test")
            # Try to access the subreddit (this will validate credentials)
            _ = test_subreddit.display_name

            self.logger.info("Reddit API connection established successfully")

        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit API: {e}")
            self.logger.error("Please check your Reddit API credentials in .env file")
            sys.exit(1)

    def _generate_content_hash(self, content: str) -> str:
        """Generate SHA256 hash for content deduplication."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant trading keywords from text."""
        keywords = self.config["reddit"]["keywords"]
        found_keywords = []

        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)

        return found_keywords

    def _create_obsidian_markdown(self, post_data: Dict) -> str:
        """Create Obsidian-compatible markdown with frontmatter."""
        # YAML frontmatter
        frontmatter = {
            "source": "reddit",
            "subreddit": post_data["subreddit"],
            "date": post_data["created_utc"],
            "tags": post_data["keywords"],
            "content_hash": post_data["content_hash"],
            "author": post_data["author"],
            "score": post_data["score"],
            "url": post_data["url"],
            "post_id": post_data["id"],
        }

        markdown_content = "---\n"
        for key, value in frontmatter.items():
            if isinstance(value, list):
                markdown_content += f"{key}: {value}\n"
            elif isinstance(value, str) and " " in value:
                markdown_content += f'{key}: "{value}"\n'
            else:
                markdown_content += f"{key}: {value}\n"
        markdown_content += "---\n\n"

        # Content
        markdown_content += f"# {post_data['title']}\n\n"

        if post_data["selftext"]:
            markdown_content += f"{post_data['selftext']}\n\n"

        # Comments section
        if post_data["comments"]:
            markdown_content += "## Comments\n\n"
            for i, comment in enumerate(post_data["comments"], 1):
                markdown_content += f"### Comment {i} (Score: {comment['score']})\n\n"
                markdown_content += f"**Author:** u/{comment['author']}\n\n"
                markdown_content += f"{comment['body']}\n\n"

        # Links and references
        markdown_content += "## Source\n\n"
        markdown_content += (
            f"- **Reddit Post:** [{post_data['title']}]({post_data['url']})\n"
        )
        markdown_content += f"- **Subreddit:** r/{post_data['subreddit']}\n"
        markdown_content += f"- **Author:** u/{post_data['author']}\n"
        markdown_content += f"- **Score:** {post_data['score']} upvotes\n"

        return markdown_content

    def _save_to_file(self, content: str, filename: str) -> bool:
        """Save content to markdown file."""
        if self.dry_run:
            self.logger.info(f"DRY RUN: Would save to {filename}")
            return True

        try:
            # Create output directory if it doesn't exist
            output_dir = Path(self.config["paths"]["reddit_notes"])
            output_dir.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path = output_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.logger.info(f"Content saved to {file_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save file {filename}: {e}")
            return False

    def _extract_post_data(self, submission) -> Optional[Dict]:
        """Extract and structure data from a Reddit submission."""
        try:
            # Get post content
            title = submission.title
            selftext = submission.selftext or ""
            combined_text = f"{title} {selftext}"

            # Filter by keywords
            keywords = self._extract_keywords(combined_text)
            if not keywords:
                self.logger.debug(
                    f"Skipping post '{title[:50]}...' - no relevant keywords"
                )
                return None

            # Filter by score
            min_score = self.config["reddit"]["min_post_score"]
            if submission.score < min_score:
                self.logger.debug(
                    f"Skipping post '{title[:50]}...' - score {submission.score} < {min_score}"
                )
                return None

            # Extract comments
            comments = []
            max_comments = self.config["reddit"]["max_comments_per_post"]
            min_comment_score = self.config["reddit"]["min_comment_score"]

            submission.comments.replace_more(limit=0)  # Remove "load more comments"
            for comment in submission.comments.list()[:max_comments]:
                if hasattr(comment, "body") and comment.score >= min_comment_score:
                    comments.append(
                        {
                            "author": str(comment.author)
                            if comment.author
                            else "[deleted]",
                            "body": comment.body,
                            "score": comment.score,
                            "created_utc": datetime.fromtimestamp(
                                comment.created_utc
                            ).isoformat(),
                        }
                    )

            # Structure post data
            post_data = {
                "id": submission.id,
                "title": title,
                "selftext": selftext,
                "author": str(submission.author) if submission.author else "[deleted]",
                "score": submission.score,
                "url": f"https://reddit.com{submission.permalink}",
                "subreddit": submission.subreddit.display_name,
                "created_utc": datetime.fromtimestamp(
                    submission.created_utc
                ).isoformat(),
                "keywords": keywords,
                "comments": comments,
                "content_hash": self._generate_content_hash(combined_text),
            }

            return post_data

        except Exception as e:
            self.logger.error(f"Error extracting post data: {e}")
            return None

    def scrape_subreddit(self, subreddit_name: str, limit: Optional[int] = None) -> int:
        """Scrape posts from a specific subreddit."""
        if limit is None:
            limit = self.config["reddit"]["max_posts_per_subreddit"]

        self.logger.info(f"Scraping r/{subreddit_name} (limit: {limit})")

        if self.dry_run:
            self.logger.info("DRY RUN MODE: No actual API calls or file writes")
            return 0

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts_saved = 0

            # Get hot posts from subreddit
            for submission in subreddit.hot(limit=limit):
                post_data = self._extract_post_data(submission)

                if post_data:
                    # Create markdown content
                    markdown_content = self._create_obsidian_markdown(post_data)

                    # Generate filename
                    safe_title = "".join(
                        c
                        for c in post_data["title"][:50]
                        if c.isalnum() or c in (" ", "-", "_")
                    ).rstrip()
                    filename = f"{post_data['created_utc'][:10]}_{post_data['id']}_{safe_title}.md"

                    # Save to file
                    if self._save_to_file(markdown_content, filename):
                        posts_saved += 1
                        self.logger.info(f"Saved: {post_data['title'][:60]}...")

            self.logger.info(
                f"Scraping r/{subreddit_name} complete. Saved {posts_saved} posts."
            )
            return posts_saved

        except Exception as e:
            self.logger.error(f"Error scraping r/{subreddit_name}: {e}")
            return 0

    def scrape_all_subreddits(self) -> Dict[str, int]:
        """Scrape all configured subreddits."""
        results = {}
        subreddits = self.config["reddit"]["subreddits"]

        self.logger.info(f"Starting scrape of {len(subreddits)} subreddits")

        for subreddit_name in subreddits:
            try:
                count = self.scrape_subreddit(subreddit_name)
                results[subreddit_name] = count
            except Exception as e:
                self.logger.error(f"Failed to scrape r/{subreddit_name}: {e}")
                results[subreddit_name] = 0

        total_posts = sum(results.values())
        self.logger.info(f"Scraping complete. Total posts saved: {total_posts}")

        return results


def main():
    """Main entry point for the Reddit scraper."""
    parser = argparse.ArgumentParser(
        description="IntelForge Reddit Scraper for Algorithmic Trading Research"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making API calls or saving files",
    )
    parser.add_argument("--subreddit", type=str, help="Scrape specific subreddit only")
    parser.add_argument("--limit", type=int, help="Limit number of posts to scrape")
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file",
    )

    args = parser.parse_args()

    # Initialize scraper
    scraper = IntelForgeRedditScraper(args.config)

    # Override dry-run if specified
    if args.dry_run:
        scraper.dry_run = True

    # Scrape specific subreddit or all configured subreddits
    if args.subreddit:
        scraper.scrape_subreddit(args.subreddit, args.limit)
    else:
        scraper.scrape_all_subreddits()


if __name__ == "__main__":
    main()
