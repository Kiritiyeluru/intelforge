"""
Site-specific refresh policies and content-type based refresh scheduling.
Manages intelligent refresh intervals based on content patterns.
"""

import orjson as json
import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class RefreshPolicyManager:
    """
    Manages site-specific and content-type based refresh policies.
    """

    # Default site-specific refresh policies (days)
    DEFAULT_SITE_POLICIES = {
        'quantstart.com': 90,           # Educational content changes rarely
        'investopedia.com': 30,         # Financial education updates monthly
        'blog.quantinsti.com': 7,       # Blog posts update weekly
        'quantinsti.com': 14,           # Main site updates bi-weekly
        'reddit.com': 1,                # Social content updates daily
        'news.ycombinator.com': 1,      # News updates daily
        'stackoverflow.com': 30,        # Q&A content relatively stable
        'github.com': 7,                # Code repositories update weekly
        'arxiv.org': 180,               # Academic papers rarely change
        'wikipedia.org': 30,            # Encyclopedia updates monthly
        'medium.com': 14,               # Articles update bi-weekly
        'towards-data-science': 14,     # Technical articles bi-weekly
        'default': 30                   # Default refresh interval
    }

    # Content-type based refresh policies (days)
    DEFAULT_CONTENT_TYPE_POLICIES = {
        'tutorial': 90,         # Tutorials rarely change
        'documentation': 60,    # Documentation updates bi-monthly
        'guide': 60,           # Guides update bi-monthly
        'reference': 180,      # Reference materials very stable
        'news': 1,             # News updates daily
        'blog': 7,             # Blogs update weekly
        'article': 14,         # Articles update bi-weekly
        'paper': 180,          # Academic papers rarely change
        'discussion': 3,       # Discussions update frequently
        'forum': 3,            # Forum posts update frequently
        'code': 14,            # Code examples update bi-weekly
        'api': 30,             # API docs update monthly
        'changelog': 7,        # Changelogs update weekly
        'release': 30,         # Release notes update monthly
        'unknown': 30          # Default for unknown content types
    }

    def __init__(self,
                 config_path: Optional[str] = None,
                 site_policies: Optional[Dict[str, int]] = None,
                 content_type_policies: Optional[Dict[str, int]] = None):
        """
        Initialize refresh policy manager.

        Args:
            config_path: Path to configuration file
            site_policies: Custom site policies
            content_type_policies: Custom content type policies
        """
        self.config_path = Path(config_path) if config_path else None

        # Initialize policies with defaults
        self.site_policies = self.DEFAULT_SITE_POLICIES.copy()
        self.content_type_policies = self.DEFAULT_CONTENT_TYPE_POLICIES.copy()

        # Update with custom policies
        if site_policies:
            self.site_policies.update(site_policies)
        if content_type_policies:
            self.content_type_policies.update(content_type_policies)

        # Load from config file if specified
        if self.config_path and self.config_path.exists():
            self.load_config()

        # Track policy usage for optimization
        self.policy_usage = {}
        self.content_analysis = {}

    def get_refresh_interval(self,
                           url: str,
                           content_type: Optional[str] = None,
                           quality_score: Optional[int] = None,
                           change_frequency: Optional[float] = None) -> Tuple[int, str]:
        """
        Get refresh interval for a URL based on multiple factors.

        Args:
            url: URL to get refresh interval for
            content_type: Detected content type
            quality_score: Content quality score (0-100)
            change_frequency: Historical change frequency (changes per day)

        Returns:
            Tuple of (refresh_days, reason)
        """
        try:
            site = self._extract_site(url)

            # Start with site-specific policy
            site_interval = self.site_policies.get(site, self.site_policies['default'])
            reasons = [f"site_policy:{site_interval}"]

            # Apply content type policy
            content_interval = site_interval
            if content_type and content_type in self.content_type_policies:
                content_interval = self.content_type_policies[content_type]
                reasons.append(f"content_type:{content_type}:{content_interval}")

            # Choose the more conservative (shorter) interval
            base_interval = min(site_interval, content_interval)

            # Apply quality-based adjustments
            quality_adjusted = self._apply_quality_adjustment(base_interval, quality_score)
            if quality_adjusted != base_interval:
                reasons.append(f"quality_adjustment:{quality_score}:{quality_adjusted}")

            # Apply change frequency adjustments
            frequency_adjusted = self._apply_frequency_adjustment(quality_adjusted, change_frequency)
            if frequency_adjusted != quality_adjusted:
                reasons.append(f"frequency_adjustment:{change_frequency}:{frequency_adjusted}")

            final_interval = max(1, frequency_adjusted)  # Minimum 1 day

            # Track policy usage
            self._track_policy_usage(site, content_type, final_interval)

            return final_interval, " | ".join(reasons)

        except Exception as e:
            logger.error(f"Error calculating refresh interval for {url}: {e}")
            return self.site_policies['default'], "error_default"

    def _apply_quality_adjustment(self, base_interval: int, quality_score: Optional[int]) -> int:
        """
        Adjust refresh interval based on content quality.
        Higher quality content gets more frequent updates.

        Args:
            base_interval: Base refresh interval
            quality_score: Content quality score (0-100)

        Returns:
            Adjusted interval
        """
        if quality_score is None:
            return base_interval

        try:
            if quality_score >= 80:
                # High quality: 20% more frequent
                return max(1, int(base_interval * 0.8))
            elif quality_score >= 60:
                # Good quality: 10% more frequent
                return max(1, int(base_interval * 0.9))
            elif quality_score <= 20:
                # Low quality: 50% less frequent
                return int(base_interval * 1.5)
            elif quality_score <= 40:
                # Poor quality: 25% less frequent
                return int(base_interval * 1.25)
            else:
                # Medium quality: no change
                return base_interval

        except Exception as e:
            logger.warning(f"Error applying quality adjustment: {e}")
            return base_interval

    def _apply_frequency_adjustment(self, base_interval: int, change_frequency: Optional[float]) -> int:
        """
        Adjust refresh interval based on historical change frequency.

        Args:
            base_interval: Base refresh interval
            change_frequency: Changes per day

        Returns:
            Adjusted interval
        """
        if change_frequency is None:
            return base_interval

        try:
            if change_frequency > 1.0:
                # Changes more than once per day: check daily
                return 1
            elif change_frequency > 0.5:
                # Changes every 2 days: check every 2 days
                return 2
            elif change_frequency > 0.2:
                # Changes every 5 days: check every 5 days
                return 5
            elif change_frequency > 0.1:
                # Changes every 10 days: check every 10 days
                return 10
            elif change_frequency > 0.03:
                # Changes every 30 days: check every 30 days
                return 30
            else:
                # Rarely changes: extend interval by 50%
                return int(base_interval * 1.5)

        except Exception as e:
            logger.warning(f"Error applying frequency adjustment: {e}")
            return base_interval

    def detect_content_type(self,
                          url: str,
                          title: Optional[str] = None,
                          content: Optional[str] = None,
                          metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Detect content type from URL, title, and content.

        Args:
            url: URL to analyze
            title: Page title
            content: Page content
            metadata: Additional metadata

        Returns:
            Detected content type or None
        """
        try:
            url_lower = url.lower()
            title_lower = title.lower() if title else ""
            content_lower = content[:1000].lower() if content else ""  # First 1000 chars

            # URL pattern matching
            if any(pattern in url_lower for pattern in ['/blog/', '/news/', '/articles/']):
                if 'tutorial' in title_lower or 'guide' in title_lower:
                    return 'tutorial'
                elif 'news' in title_lower or '/news/' in url_lower:
                    return 'news'
                else:
                    return 'blog'

            if any(pattern in url_lower for pattern in ['/docs/', '/documentation/', '/api/']):
                return 'documentation'

            if any(pattern in url_lower for pattern in ['/forum/', '/discussion/', '/reddit']):
                return 'discussion'

            if any(pattern in url_lower for pattern in ['/releases/', '/changelog/', '/changes/']):
                return 'changelog'

            if 'github.com' in url_lower or 'gitlab.com' in url_lower:
                if '/releases/' in url_lower:
                    return 'release'
                else:
                    return 'code'

            if 'arxiv.org' in url_lower or 'paper' in title_lower:
                return 'paper'

            # Title-based detection
            if title_lower:
                if any(word in title_lower for word in ['tutorial', 'guide', 'how to', 'step by step']):
                    return 'tutorial'
                elif any(word in title_lower for word in ['news', 'breaking', 'update', 'announcement']):
                    return 'news'
                elif any(word in title_lower for word in ['reference', 'api', 'documentation']):
                    return 'reference'
                elif any(word in title_lower for word in ['discussion', 'forum', 'comment']):
                    return 'discussion'

            # Content-based detection
            if content_lower:
                tutorial_indicators = content_lower.count('step') + content_lower.count('tutorial') + content_lower.count('example')
                news_indicators = content_lower.count('today') + content_lower.count('yesterday') + content_lower.count('breaking')
                reference_indicators = content_lower.count('api') + content_lower.count('reference') + content_lower.count('documentation')

                max_indicators = max(tutorial_indicators, news_indicators, reference_indicators)

                if max_indicators > 0:
                    if tutorial_indicators == max_indicators:
                        return 'tutorial'
                    elif news_indicators == max_indicators:
                        return 'news'
                    elif reference_indicators == max_indicators:
                        return 'reference'

            # Check metadata
            if metadata:
                article_type = metadata.get('article_type') or metadata.get('content_type')
                if article_type:
                    return article_type.lower()

            # Default to article for most content
            return 'article'

        except Exception as e:
            logger.warning(f"Error detecting content type for {url}: {e}")
            return 'unknown'

    def update_policy(self,
                     site: Optional[str] = None,
                     content_type: Optional[str] = None,
                     interval: int = 30):
        """
        Update refresh policy for site or content type.

        Args:
            site: Site domain to update
            content_type: Content type to update
            interval: New refresh interval in days
        """
        try:
            if site:
                old_interval = self.site_policies.get(site, 'not_set')
                self.site_policies[site] = interval
                logger.info(f"Updated site policy for {site}: {old_interval} -> {interval} days")

            if content_type:
                old_interval = self.content_type_policies.get(content_type, 'not_set')
                self.content_type_policies[content_type] = interval
                logger.info(f"Updated content type policy for {content_type}: {old_interval} -> {interval} days")

            # Save to config file if path is set
            if self.config_path:
                self.save_config()

        except Exception as e:
            logger.error(f"Error updating policy: {e}")

    def get_policy_recommendations(self, url_tracker) -> Dict[str, Any]:
        """
        Analyze crawl history and recommend policy adjustments.

        Args:
            url_tracker: URLTracker instance

        Returns:
            Dictionary with recommendations
        """
        try:
            recommendations = {
                'site_adjustments': {},
                'content_type_adjustments': {},
                'frequently_changing': [],
                'rarely_changing': [],
                'analysis_date': datetime.now().isoformat()
            }

            # Get frequently changing URLs
            frequent_changes = url_tracker.get_frequently_changing_urls(limit=50)

            for url_data in frequent_changes:
                site = self._extract_site(url_data['url'])
                days_per_change = url_data.get('days_per_change', 30)

                current_policy = self.site_policies.get(site, self.site_policies['default'])

                # If content changes more frequently than policy, recommend shorter interval
                if days_per_change < current_policy * 0.5:
                    recommended_interval = max(1, int(days_per_change * 1.5))
                    recommendations['site_adjustments'][site] = {
                        'current': current_policy,
                        'recommended': recommended_interval,
                        'reason': f'changes_every_{days_per_change:.1f}_days'
                    }

            # Get site statistics for analysis
            site_stats = url_tracker.get_site_stats()
            if 'sites' in site_stats:
                for site_data in site_stats['sites']:
                    site = site_data['site']
                    efficiency_ratio = site_data.get('efficiency_ratio', 1.0)

                    # If efficiency is very high (few re-crawls), might extend interval
                    if efficiency_ratio > 0.9:  # 90% of crawls are unique
                        current_policy = self.site_policies.get(site, self.site_policies['default'])
                        recommended_interval = min(90, int(current_policy * 1.5))

                        if recommended_interval > current_policy:
                            recommendations['rarely_changing'].append({
                                'site': site,
                                'current_policy': current_policy,
                                'recommended_policy': recommended_interval,
                                'efficiency_ratio': efficiency_ratio
                            })

            return recommendations

        except Exception as e:
            logger.error(f"Error generating policy recommendations: {e}")
            return {'error': str(e)}

    def _track_policy_usage(self, site: str, content_type: Optional[str], interval: int):
        """Track policy usage for optimization."""
        try:
            key = f"{site}:{content_type or 'unknown'}"
            if key not in self.policy_usage:
                self.policy_usage[key] = []

            self.policy_usage[key].append({
                'interval': interval,
                'timestamp': datetime.now().isoformat()
            })

            # Keep only recent usage (last 1000 entries)
            if len(self.policy_usage[key]) > 1000:
                self.policy_usage[key] = self.policy_usage[key][-1000:]

        except Exception as e:
            logger.warning(f"Error tracking policy usage: {e}")

    def _extract_site(self, url: str) -> str:
        """Extract site domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()

            # Handle common subdomain patterns
            if domain.startswith('www.'):
                domain = domain[4:]
            elif domain.startswith('blog.'):
                return domain  # Keep blog subdomain
            elif domain.startswith('news.'):
                return domain  # Keep news subdomain
            elif domain.startswith('docs.'):
                return domain  # Keep docs subdomain

            return domain
        except:
            return "unknown"

    def save_config(self):
        """Save current policies to configuration file."""
        if not self.config_path:
            return

        try:
            config = {
                'site_policies': self.site_policies,
                'content_type_policies': self.content_type_policies,
                'last_updated': datetime.now().isoformat(),
                'policy_usage_summary': self._summarize_policy_usage()
            }

            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"Saved refresh policies to {self.config_path}")

        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def load_config(self):
        """Load policies from configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            if 'site_policies' in config:
                self.site_policies.update(config['site_policies'])

            if 'content_type_policies' in config:
                self.content_type_policies.update(config['content_type_policies'])

            logger.info(f"Loaded refresh policies from {self.config_path}")

        except Exception as e:
            logger.warning(f"Error loading config: {e}")

    def _summarize_policy_usage(self) -> Dict[str, Any]:
        """Summarize policy usage statistics."""
        try:
            summary = {
                'total_sites': len(self.policy_usage),
                'most_used_intervals': {},
                'average_interval': 0
            }

            all_intervals = []
            for site_data in self.policy_usage.values():
                for usage in site_data[-100:]:  # Last 100 uses
                    interval = usage['interval']
                    all_intervals.append(interval)

                    if interval not in summary['most_used_intervals']:
                        summary['most_used_intervals'][interval] = 0
                    summary['most_used_intervals'][interval] += 1

            if all_intervals:
                summary['average_interval'] = sum(all_intervals) / len(all_intervals)

            return summary

        except Exception as e:
            logger.warning(f"Error summarizing policy usage: {e}")
            return {}
