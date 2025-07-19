#!/usr/bin/env python3
"""
GitHub Repository Discovery for IntelForge
Leverages GitHub API for targeted repository discovery in trading/finance domains.
"""

import requests
from typing import List, Dict, Optional
import orjson as json
import os
from datetime import datetime
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm import tqdm


class GitHubDiscovery:
    """GitHub API-based repository discovery for trading/quant content."""

    def __init__(self, token: Optional[str] = None):
        """Initialize with optional GitHub token for higher rate limits."""
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'IntelForge-Discovery/1.0'
        }
        if self.token:
            self.headers['Authorization'] = f'token {self.token}'

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.exceptions.RequestException, requests.exceptions.Timeout))
    )
    def search_repositories(self, keywords: List[str], max_results: int = 50) -> List[Dict]:
        """Search GitHub for trading/quant repositories with quality filtering."""
        query = " ".join(keywords) + " language:python"

        params = {
            'q': query,
            'sort': 'stars',
            'order': 'desc',
            'per_page': min(max_results, 100)
        }

        try:
            response = requests.get(
                f"{self.base_url}/search/repositories",
                params=params,
                headers=self.headers,
                timeout=30
            )

            # Handle rate limiting
            if response.status_code == 403:
                rate_limit_reset = response.headers.get('X-RateLimit-Reset')
                if rate_limit_reset:
                    reset_time = datetime.fromtimestamp(int(rate_limit_reset))
                    print(f"⚠️  Rate limited. Reset at: {reset_time}")
                return []

            if response.status_code == 200:
                data = response.json()
                repositories = []

                for repo in tqdm(data.get('items', []), desc="Processing repositories", unit="repo"):
                    # Quality filtering
                    if self._is_quality_repo(repo):
                        repositories.append({
                            'url': repo['html_url'],
                            'source': 'github_api',
                            'category': 'code',
                            'priority': self._calculate_priority(repo),
                            'quality_estimate': self._calculate_quality_score(repo),
                            'metadata': {
                                'stars': repo['stargazers_count'],
                                'forks': repo['forks_count'],
                                'language': repo['language'],
                                'description': repo['description'],
                                'updated_at': repo['updated_at'],
                                'search_keywords': keywords,
                                'discovery_date': datetime.now().isoformat()
                            }
                        })

                print(f"🔍 GitHub API: Found {len(repositories)} quality repositories")
                return repositories

            else:
                print(f"❌ GitHub API error: {response.status_code}")
                return []

        except requests.exceptions.RequestException as e:
            print(f"❌ GitHub API request failed: {e}")
            return []

    def _is_quality_repo(self, repo: Dict) -> bool:
        """Filter repositories based on quality indicators."""
        # Minimum quality thresholds
        min_stars = 10
        min_activity_days = 365  # Updated within last year

        stars = repo.get('stargazers_count', 0)
        updated_at = repo.get('updated_at', '')

        # Check if recently updated
        if updated_at:
            try:
                last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                days_since_update = (datetime.now().astimezone() - last_update).days
                recently_active = days_since_update < min_activity_days
            except:
                recently_active = False
        else:
            recently_active = False

        # Quality checks
        description = repo.get('description') or ''
        has_description = bool(description.strip())
        sufficient_stars = stars >= min_stars
        not_archived = not repo.get('archived', False)

        return has_description and sufficient_stars and recently_active and not_archived

    def _calculate_priority(self, repo: Dict) -> int:
        """Calculate priority based on repository characteristics."""
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)

        # Higher priority for more popular repos
        if stars > 1000:
            return 2  # High priority
        elif stars > 100:
            return 3  # Medium-high priority
        elif stars > 50:
            return 4  # Medium priority
        else:
            return 5  # Lower priority

    def _calculate_quality_score(self, repo: Dict) -> float:
        """Calculate quality score based on repository metrics."""
        stars = repo.get('stargazers_count', 0)
        forks = repo.get('forks_count', 0)

        # Base score from stars (logarithmic scale)
        import math
        star_score = min(math.log10(max(stars, 1)) / 4, 0.8)  # Max 0.8 from stars

        # Fork ratio contribution
        fork_ratio = forks / max(stars, 1)
        fork_score = min(fork_ratio * 0.2, 0.2)  # Max 0.2 from fork ratio

        return min(star_score + fork_score, 1.0)

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=5),
        retry=retry_if_exception_type(requests.exceptions.RequestException)
    )
    def get_rate_limit_status(self) -> Dict:
        """Check GitHub API rate limit status."""
        try:
            response = requests.get(
                f"{self.base_url}/rate_limit",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {}


if __name__ == "__main__":
    # Test the GitHub discovery
    discovery = GitHubDiscovery()

    # Test with trading keywords
    repos = discovery.search_repositories(['backtest', 'trading'], max_results=5)
    print(f"Found {len(repos)} repositories")

    for repo in repos:
        print(f"  {repo['url']} (stars: {repo['metadata']['stars']}, quality: {repo['quality_estimate']:.2f})")
