#!/usr/bin/env python3
"""
Discovery Engine - Phase D1 Implementation
Intelligent content discovery across multiple sources with advanced search operators

Sources:
- Google Search (advanced operators)
- GitHub Repositories (PyGithub API)
- ArXiv Papers (official API)
- Reddit Communities (PRAW)

Usage:
    python scripts/discovery_engine.py --topic "momentum trading strategy" --sources google github arxiv
    python scripts/discovery_engine.py --topic "algorithmic trading" --limit 50 --output discovery_results/
"""

import argparse
import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import requests
from urllib.parse import quote_plus
import sys
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    config_path = Path("config/config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

class DiscoveryEngine:
    """Intelligent content discovery system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        
        # Set up user agent
        self.session.headers.update({
            'User-Agent': 'IntelForge Discovery Engine 1.0'
        })
        
        # Initialize API clients
        self.github_client = None
        self.reddit_client = None
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize API clients"""
        try:
            # GitHub API
            github_token = (
                self.config.get('github', {}).get('access_token') or
                os.getenv('GITHUB_TOKEN')
            )
            
            if github_token:
                from github import Github
                self.github_client = Github(github_token)
                print("✅ GitHub API initialized")
            
            # Reddit API
            reddit_config = self.config.get('reddit', {})
            reddit_id = reddit_config.get('client_id') or os.getenv('REDDIT_CLIENT_ID')
            reddit_secret = reddit_config.get('client_secret') or os.getenv('REDDIT_CLIENT_SECRET')
            
            if reddit_id and reddit_secret:
                import praw
                self.reddit_client = praw.Reddit(
                    client_id=reddit_id,
                    client_secret=reddit_secret,
                    user_agent=reddit_config.get('user_agent', 'IntelForge Discovery Engine')
                )
                print("✅ Reddit API initialized")
                
        except Exception as e:
            print(f"⚠️ Error initializing API clients: {e}")
    
    def discover_google_content(self, topic: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Discover content using Google search with advanced operators"""
        print(f"🔍 Discovering Google content for: {topic}")
        
        # Advanced search operators for financial/trading content
        search_queries = [
            f'"{topic}" site:medium.com',
            f'"{topic}" site:substack.com',
            f'"{topic}" site:dev.to',
            f'"{topic}" site:quantstart.com',
            f'"{topic}" site:towardsdatascience.com',
            f'"{topic}" filetype:pdf',
            f'"{topic}" intitle:strategy inurl:blog',
            f'"{topic}" intext:backtest',
            f'"{topic}" intext:algorithm',
            f'"{topic}" intext:python OR intext:code'
        ]
        
        discoveries = []
        
        for query in search_queries[:5]:  # Limit to top 5 queries
            try:
                results = self._search_google(query, limit // 5)
                discoveries.extend(results)
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Google search error for '{query}': {e}")
        
        return discoveries[:limit]
    
    def _search_google(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Perform Google search using googlesearch-python library"""
        try:
            from googlesearch import search
            
            results = []
            search_results = search(query, num=limit, stop=limit, pause=2)
            
            for i, url in enumerate(search_results):
                if i >= limit:
                    break
                    
                results.append({
                    "source": "google",
                    "title": f"Google result {i+1} for: {query}",
                    "url": url,
                    "query": query,
                    "type": "web_page",
                    "discovered_at": datetime.now().isoformat(),
                    "relevance_score": 1.0 - (i * 0.1)  # Decrease by position
                })
            
            return results
            
        except ImportError:
            print("⚠️ googlesearch-python not installed. Using fallback method.")
            return self._search_google_fallback(query, limit)
        except Exception as e:
            print(f"❌ Google search error: {e}")
            return []
    
    def _search_google_fallback(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback Google search method"""
        # Simple fallback - in production, implement SerpAPI or custom scraping
        return [
            {
                "source": "google",
                "title": f"Fallback result for: {query}",
                "url": f"https://www.google.com/search?q={quote_plus(query)}",
                "query": query,
                "type": "search_query",
                "discovered_at": datetime.now().isoformat(),
                "relevance_score": 0.5
            }
        ]
    
    def discover_github_content(self, topic: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Discover GitHub repositories using PyGithub"""
        print(f"🐙 Discovering GitHub content for: {topic}")
        
        if not self.github_client:
            print("❌ GitHub API not initialized")
            return []
        
        discoveries = []
        
        # Search queries for algorithmic trading
        search_queries = [
            f"{topic} language:python",
            f"{topic} stars:>10",
            f"{topic} algorithm trading",
            f"{topic} backtest",
            f"{topic} strategy",
            f'"{topic}" in:readme',
            f'topic:algorithmic-trading {topic}',
            f'topic:quantitative-finance {topic}'
        ]
        
        try:
            for query in search_queries[:4]:  # Limit to top 4 queries
                try:
                    repos = self.github_client.search_repositories(
                        query=query,
                        sort='stars',
                        order='desc'
                    )
                    
                    count = 0
                    for repo in repos:
                        if count >= limit // 4:
                            break
                        
                        discoveries.append({
                            "source": "github",
                            "title": repo.name,
                            "url": repo.html_url,
                            "description": repo.description or "No description",
                            "stars": repo.stargazers_count,
                            "language": repo.language,
                            "query": query,
                            "type": "repository",
                            "discovered_at": datetime.now().isoformat(),
                            "relevance_score": min(1.0, repo.stargazers_count / 100)
                        })
                        
                        count += 1
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ GitHub search error for '{query}': {e}")
                    continue
        
        except Exception as e:
            print(f"❌ GitHub discovery error: {e}")
        
        return discoveries[:limit]
    
    def discover_arxiv_content(self, topic: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Discover ArXiv papers using official API"""
        print(f"📚 Discovering ArXiv content for: {topic}")
        
        try:
            import arxiv
            
            # Search ArXiv
            search = arxiv.Search(
                query=topic,
                max_results=limit,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            discoveries = []
            
            for paper in search.results():
                discoveries.append({
                    "source": "arxiv",
                    "title": paper.title,
                    "url": paper.entry_id,
                    "pdf_url": paper.pdf_url,
                    "abstract": paper.summary[:500] + "..." if len(paper.summary) > 500 else paper.summary,
                    "authors": [author.name for author in paper.authors],
                    "published": paper.published.isoformat(),
                    "categories": paper.categories,
                    "type": "academic_paper",
                    "discovered_at": datetime.now().isoformat(),
                    "relevance_score": 0.8  # Academic papers generally high relevance
                })
            
            return discoveries
            
        except ImportError:
            print("⚠️ arxiv library not installed. Using fallback method.")
            return self._discover_arxiv_fallback(topic, limit)
        except Exception as e:
            print(f"❌ ArXiv discovery error: {e}")
            return []
    
    def _discover_arxiv_fallback(self, topic: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback ArXiv discovery method"""
        # Call existing arxiv_simple.py script
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "scripts/arxiv_simple.py",
                "--query", topic,
                "--limit", str(limit)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return [
                    {
                        "source": "arxiv",
                        "title": f"ArXiv paper for: {topic}",
                        "url": "https://arxiv.org/search",
                        "type": "academic_paper",
                        "discovered_at": datetime.now().isoformat(),
                        "relevance_score": 0.7
                    }
                ]
        except Exception as e:
            print(f"❌ ArXiv fallback error: {e}")
        
        return []
    
    def discover_reddit_content(self, topic: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Discover Reddit content using PRAW"""
        print(f"🔸 Discovering Reddit content for: {topic}")
        
        if not self.reddit_client:
            print("❌ Reddit API not initialized")
            return []
        
        discoveries = []
        
        # Target subreddits
        subreddits = [
            "algotrading",
            "quantfinance", 
            "SecurityAnalysis",
            "investing",
            "Python",
            "MachineLearning"
        ]
        
        try:
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit_client.subreddit(subreddit_name)
                    
                    # Search within subreddit
                    search_results = subreddit.search(
                        topic,
                        limit=limit // len(subreddits),
                        sort='relevance'
                    )
                    
                    for post in search_results:
                        discoveries.append({
                            "source": "reddit",
                            "title": post.title,
                            "url": f"https://reddit.com{post.permalink}",
                            "subreddit": subreddit_name,
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "author": str(post.author),
                            "created": datetime.fromtimestamp(post.created_utc).isoformat(),
                            "type": "forum_post",
                            "discovered_at": datetime.now().isoformat(),
                            "relevance_score": min(1.0, post.score / 100)
                        })
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Reddit search error for r/{subreddit_name}: {e}")
                    continue
        
        except Exception as e:
            print(f"❌ Reddit discovery error: {e}")
        
        return discoveries[:limit]
    
    def discover_all_sources(self, topic: str, sources: List[str], limit_per_source: int = 20) -> List[Dict[str, Any]]:
        """Discover content from all specified sources"""
        print(f"🚀 Starting discovery for: {topic}")
        print(f"📊 Sources: {', '.join(sources)}")
        
        all_discoveries = []
        
        if 'google' in sources:
            google_results = self.discover_google_content(topic, limit_per_source)
            all_discoveries.extend(google_results)
        
        if 'github' in sources:
            github_results = self.discover_github_content(topic, limit_per_source)
            all_discoveries.extend(github_results)
        
        if 'arxiv' in sources:
            arxiv_results = self.discover_arxiv_content(topic, limit_per_source)
            all_discoveries.extend(arxiv_results)
        
        if 'reddit' in sources:
            reddit_results = self.discover_reddit_content(topic, limit_per_source)
            all_discoveries.extend(reddit_results)
        
        # Sort by relevance score
        all_discoveries.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return all_discoveries
    
    def save_discovery_results(self, discoveries: List[Dict[str, Any]], topic: str, output_dir: Path):
        """Save discovery results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = output_dir / f"discovery_{topic.replace(' ', '_')}_{timestamp}.json"
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare results
        results = {
            "topic": topic,
            "timestamp": timestamp,
            "total_results": len(discoveries),
            "sources": list(set(d.get('source') for d in discoveries)),
            "discoveries": discoveries
        }
        
        # Save to JSON
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"💾 Discovery results saved to: {results_file}")
        
        # Also save URLs for easy scraping
        urls_file = output_dir / f"urls_{topic.replace(' ', '_')}_{timestamp}.txt"
        with open(urls_file, 'w') as f:
            for discovery in discoveries:
                if discovery.get('url'):
                    f.write(f"{discovery['url']}\n")
        
        print(f"📄 URLs saved to: {urls_file}")
        
        return results_file, urls_file

def main():
    parser = argparse.ArgumentParser(description="IntelForge Discovery Engine")
    parser.add_argument("--topic", "-t", required=True, help="Topic to discover content for")
    parser.add_argument("--sources", "-s", nargs="+", 
                       default=['google', 'github', 'arxiv', 'reddit'],
                       help="Sources to search: google, github, arxiv, reddit")
    parser.add_argument("--limit", "-l", type=int, default=20, 
                       help="Maximum results per source")
    parser.add_argument("--output", "-o", default="vault/discovery/",
                       help="Output directory for results")
    parser.add_argument("--min-score", type=float, default=0.3,
                       help="Minimum relevance score filter")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Initialize discovery engine
    engine = DiscoveryEngine(config)
    
    # Discover content
    discoveries = engine.discover_all_sources(args.topic, args.sources, args.limit)
    
    # Filter by minimum score
    filtered_discoveries = [
        d for d in discoveries 
        if d.get('relevance_score', 0) >= args.min_score
    ]
    
    # Save results
    output_dir = Path(args.output)
    results_file, urls_file = engine.save_discovery_results(
        filtered_discoveries, args.topic, output_dir
    )
    
    # Display summary
    print(f"\n📊 Discovery Summary:")
    print(f"🎯 Topic: {args.topic}")
    print(f"📈 Total Results: {len(filtered_discoveries)}")
    print(f"🔍 Sources: {', '.join(args.sources)}")
    print(f"📊 Results by Source:")
    
    source_counts = {}
    for discovery in filtered_discoveries:
        source = discovery.get('source', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    for source, count in source_counts.items():
        print(f"  {source}: {count} results")
    
    print(f"\n📁 Files Created:")
    print(f"  Results: {results_file}")
    print(f"  URLs: {urls_file}")
    
    print(f"\n🚀 Next Steps:")
    print(f"  Scrape discovered URLs: python forgecli.py scrape --url-file {urls_file}")
    print(f"  Score content: python scripts/llm_content_scorer.py --directory vault/notes/")

if __name__ == "__main__":
    main()