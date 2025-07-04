#!/usr/bin/env python3
"""
Simple Reddit Scraper for IntelForge

A minimal Reddit scraper using PRAW + base framework.
Extracts algorithmic trading content from target subreddits.

Usage:
    python reddit_scraper.py [--dry-run] [--subreddit SUBREDDIT] [--limit N]

Example:
    python reddit_scraper.py --dry-run --subreddit algotrading --limit 10
"""

import argparse
import os
from typing import Dict, List, Optional

import praw
from dotenv import load_dotenv

from scraping_base import BaseScraper


class RedditScraper(BaseScraper):
    """Simple Reddit scraper using PRAW + base framework."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize Reddit scraper."""
        super().__init__(config_path, scraper_name="reddit")
        
        # Load environment variables for Reddit API
        load_dotenv()
        
        # Initialize Reddit API
        self._initialize_reddit()
    
    def _initialize_reddit(self):
        """Initialize Reddit API client."""
        try:
            # Get credentials from config or environment
            client_id = (
                os.getenv('REDDIT_CLIENT_ID') or 
                self.config['reddit']['client_id'] or
                self.config['api_keys']['reddit_client_id']
            )
            client_secret = (
                os.getenv('REDDIT_CLIENT_SECRET') or 
                self.config['reddit']['client_secret'] or
                self.config['api_keys']['reddit_client_secret']
            )
            user_agent = self.config['reddit']['user_agent']
            
            if not client_id or not client_secret:
                self.logger.warning("Reddit API credentials not found. Some features may not work.")
                self.reddit = None
                return
            
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
            # Test the connection
            self.reddit.user.me()
            self.logger.info("Reddit API initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit API: {e}")
            self.reddit = None
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text content."""
        if not text:
            return ""
        
        # Basic text cleaning
        text = text.replace('\n\n', '\n')  # Reduce multiple newlines
        text = text.strip()
        
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text."""
        keywords = self.config['reddit']['keywords']
        found_keywords = []
        
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _is_relevant_post(self, post) -> bool:
        """Check if post is relevant based on filters."""
        config = self.config['reddit']
        
        # Check minimum score
        if post.score < config['min_post_score']:
            return False
        
        # Check for relevant keywords
        text_to_check = f"{post.title} {post.selftext}".lower()
        keywords = config['keywords']
        
        return any(keyword.lower() in text_to_check for keyword in keywords)
    
    def scrape_subreddit(self, subreddit_name: str, limit: int = None) -> List[Dict]:
        """Scrape posts from a specific subreddit."""
        if not self.reddit:
            self.logger.error("Reddit API not initialized")
            return []
        
        if limit is None:
            limit = self.config['reddit']['max_posts_per_subreddit']
        
        self.logger.info(f"Scraping r/{subreddit_name} (limit: {limit})")
        
        scraped_posts = []
        
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts from subreddit
            for post in subreddit.hot(limit=limit * 2):  # Get extra to account for filtering
                try:
                    if not self._is_relevant_post(post):
                        continue
                    
                    # Extract post content
                    title = post.title
                    content = self._clean_text(post.selftext) if post.selftext else ""
                    
                    # Add post URL and metadata
                    post_url = f"https://reddit.com{post.permalink}"
                    
                    # Extract comments if enabled
                    comments = []
                    if self.config['reddit']['max_comments_per_post'] > 0:
                        comments = self._extract_comments(post)
                    
                    # Build full content
                    full_content = f"**Original Post:**\n{content}\n\n"
                    if comments:
                        full_content += "**Top Comments:**\n" + "\n".join(comments)
                    
                    # Create metadata
                    metadata = {
                        'subreddit': subreddit_name,
                        'author': str(post.author) if post.author else '[deleted]',
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'post_url': post_url,
                        'keywords': self._extract_keywords(f"{title} {content}")
                    }
                    
                    scraped_post = {
                        'url': post_url,
                        'title': title,
                        'content': full_content,
                        'metadata': metadata
                    }
                    
                    scraped_posts.append(scraped_post)
                    
                    if len(scraped_posts) >= limit:
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error processing post {post.id}: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error scraping r/{subreddit_name}: {e}")
        
        self.logger.info(f"Scraped {len(scraped_posts)} posts from r/{subreddit_name}")
        return scraped_posts
    
    def _extract_comments(self, post) -> List[str]:
        """Extract top comments from a post."""
        config = self.config['reddit']
        max_comments = config['max_comments_per_post']
        min_score = config['min_comment_score']
        
        comments = []
        
        try:
            # Get top-level comments
            post.comments.replace_more(limit=0)  # Don't load "more comments"
            
            for comment in post.comments[:max_comments]:
                if hasattr(comment, 'score') and comment.score >= min_score:
                    author = str(comment.author) if comment.author else '[deleted]'
                    comment_text = self._clean_text(comment.body)
                    
                    if comment_text:
                        formatted_comment = f"**{author}** (score: {comment.score}):\n{comment_text}\n"
                        comments.append(formatted_comment)
        
        except Exception as e:
            self.logger.error(f"Error extracting comments: {e}")
        
        return comments
    
    def scrape_all_subreddits(self, limit_per_subreddit: int = None):
        """Scrape all configured subreddits."""
        subreddits = self.config['reddit']['subreddits']
        
        self.logger.info(f"Starting to scrape {len(subreddits)} subreddits...")
        
        all_posts = []
        
        for subreddit_name in subreddits:
            try:
                posts = self.scrape_subreddit(subreddit_name, limit_per_subreddit)
                
                # Save each post
                for post in posts:
                    self.save_content(
                        post['url'],
                        post['title'],
                        post['content'],
                        post['metadata']
                    )
                
                all_posts.extend(posts)
                
                # Add delay between subreddits
                if subreddit_name != subreddits[-1]:  # Not the last subreddit
                    self._random_delay(
                        self.config['reddit']['rate_limit_delay'],
                        self.config['reddit']['rate_limit_delay'] + 2
                    )
                    
            except Exception as e:
                self.logger.error(f"Error scraping r/{subreddit_name}: {e}")
                continue
        
        self.logger.info(f"Finished scraping. Total posts: {len(all_posts)}")
        return all_posts


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Reddit Scraper for IntelForge")
    parser.add_argument('--dry-run', action='store_true', help="Run in dry-run mode")
    parser.add_argument('--subreddit', type=str, help="Specific subreddit to scrape")
    parser.add_argument('--limit', type=int, help="Limit number of posts per subreddit")
    parser.add_argument('--config', type=str, default="config/config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    # Set dry-run mode if specified
    if args.dry_run:
        os.environ['INTELFORGE_DRY_RUN'] = 'true'
    
    try:
        with RedditScraper(config_path=args.config) as scraper:
            if args.subreddit:
                # Scrape specific subreddit
                posts = scraper.scrape_subreddit(args.subreddit, args.limit)
                for post in posts:
                    scraper.save_content(
                        post['url'],
                        post['title'],
                        post['content'],
                        post['metadata']
                    )
            else:
                # Scrape all configured subreddits
                scraper.scrape_all_subreddits(args.limit)
                
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()