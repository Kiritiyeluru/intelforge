"""
Content change detection algorithms for URL tracking system.
Supports hash-based, HTTP header, and semantic change detection.
"""

import hashlib
import requests
from typing import Optional, Dict, Any, Tuple
import logging
from datetime import datetime

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentChangeDetector:
    """
    Multi-method content change detection system.
    """
    
    def __init__(self, primary_method: str = "hash"):
        """
        Initialize content change detector.
        
        Args:
            primary_method: Primary detection method ('hash', 'http_headers', 'semantic')
        """
        self.primary_method = primary_method
        self.timeout = 10
    
    def generate_content_hash(self, content: str, method: str = "sha256") -> str:
        """
        Generate hash of content for change detection.
        
        Args:
            content: Text content to hash
            method: Hash algorithm ('sha256', 'md5')
            
        Returns:
            Hexadecimal hash string
        """
        try:
            # Clean content before hashing (remove whitespace variations)
            cleaned_content = self._clean_content_for_hashing(content)
            
            if method == "sha256":
                return hashlib.sha256(cleaned_content.encode('utf-8')).hexdigest()
            elif method == "md5":
                return hashlib.md5(cleaned_content.encode('utf-8')).hexdigest()
            else:
                raise ValueError(f"Unsupported hash method: {method}")
                
        except Exception as e:
            logger.error(f"Error generating content hash: {e}")
            return ""
    
    def check_http_headers(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Check HTTP headers for change indicators.
        
        Args:
            url: URL to check
            
        Returns:
            Dictionary with header information or None if failed
        """
        try:
            response = requests.head(
                url, 
                timeout=self.timeout,
                allow_redirects=True,
                headers={'User-Agent': 'IntelForge-URLTracker/1.0'}
            )
            
            return {
                'etag': response.headers.get('ETag'),
                'last_modified': response.headers.get('Last-Modified'),
                'content_length': response.headers.get('Content-Length'),
                'cache_control': response.headers.get('Cache-Control'),
                'expires': response.headers.get('Expires'),
                'status_code': response.status_code,
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"Error checking HTTP headers for {url}: {e}")
            return None
    
    def has_content_changed(self, 
                          old_hash: str, 
                          new_hash: str,
                          old_headers: Optional[Dict] = None,
                          new_headers: Optional[Dict] = None,
                          similarity_threshold: float = 0.1) -> Tuple[bool, str]:
        """
        Determine if content has changed using multiple methods.
        
        Args:
            old_hash: Previous content hash
            new_hash: New content hash
            old_headers: Previous HTTP headers
            new_headers: New HTTP headers
            similarity_threshold: Threshold for semantic similarity
            
        Returns:
            Tuple of (has_changed: bool, reason: str)
        """
        try:
            # Primary method: Hash comparison
            if self.primary_method == "hash":
                if old_hash != new_hash:
                    return True, "content_hash_changed"
                return False, "content_hash_unchanged"
            
            # Secondary method: HTTP headers
            elif self.primary_method == "http_headers":
                if old_headers and new_headers:
                    # Check ETag
                    if (old_headers.get('etag') and new_headers.get('etag') and
                        old_headers['etag'] != new_headers['etag']):
                        return True, "etag_changed"
                    
                    # Check Last-Modified
                    if (old_headers.get('last_modified') and new_headers.get('last_modified') and
                        old_headers['last_modified'] != new_headers['last_modified']):
                        return True, "last_modified_changed"
                    
                    # Check Content-Length
                    if (old_headers.get('content_length') and new_headers.get('content_length') and
                        old_headers['content_length'] != new_headers['content_length']):
                        return True, "content_length_changed"
                
                # Fallback to hash if headers inconclusive
                if old_hash != new_hash:
                    return True, "content_hash_changed_fallback"
                
                return False, "no_header_changes_detected"
            
            # Default: Hash comparison
            else:
                if old_hash != new_hash:
                    return True, "content_hash_changed"
                return False, "content_hash_unchanged"
                
        except Exception as e:
            logger.error(f"Error detecting content change: {e}")
            return True, "error_assume_changed"
    
    def detect_semantic_change(self, 
                             old_content: str, 
                             new_content: str, 
                             threshold: float = 0.1) -> Tuple[bool, str]:
        """
        Detect significant semantic changes using rapidfuzz for 10-20x faster similarity.
        
        Args:
            old_content: Previous content
            new_content: New content
            threshold: Change threshold (0.0-1.0)
            
        Returns:
            Tuple of (has_changed: bool, reason: str)
        """
        try:
            # Basic length-based change detection
            old_len = len(old_content)
            new_len = len(new_content)
            
            if old_len == 0:
                return True, "new_content"
            
            # Calculate relative length change
            length_change = abs(old_len - new_len) / old_len
            
            if length_change > threshold:
                return True, f"significant_length_change_{length_change:.3f}"
            
            # Enhanced content similarity with rapidfuzz (10-20x faster than difflib)
            if RAPIDFUZZ_AVAILABLE:
                # Quick hash check first (performance optimization)
                if old_content == new_content:
                    return False, "content_identical"
                
                # Use rapidfuzz for semantic similarity on truncated content (performance)
                old_sample = old_content[:1000] if len(old_content) > 1000 else old_content
                new_sample = new_content[:1000] if len(new_content) > 1000 else new_content
                
                # rapidfuzz ratio: 0-100 scale, higher = more similar
                similarity_score = fuzz.ratio(old_sample, new_sample) / 100.0
                
                # Convert threshold (0.1 = 10% change) to similarity threshold (90% similar)
                similarity_threshold = 1.0 - threshold
                
                if similarity_score < similarity_threshold:
                    return True, f"semantic_change_rapidfuzz_{similarity_score:.3f}"
                
                return False, f"no_significant_change_rapidfuzz_{similarity_score:.3f}"
            
            else:
                # Fallback to word-based Jaccard similarity if rapidfuzz not available
                old_words = set(old_content.lower().split())
                new_words = set(new_content.lower().split())
                
                if len(old_words) == 0:
                    return True, "new_content_words"
                
                # Calculate Jaccard similarity for words
                intersection = len(old_words.intersection(new_words))
                union = len(old_words.union(new_words))
                
                if union == 0:
                    return False, "no_words_detected"
                
                jaccard_similarity = intersection / union
                
                if jaccard_similarity < (1 - threshold):
                    return True, f"semantic_change_jaccard_{jaccard_similarity:.3f}"
                
                return False, "no_significant_semantic_change"
            
        except Exception as e:
            logger.error(f"Error detecting semantic change: {e}")
            return True, "error_assume_changed"
    
    def enhanced_content_similarity(self, content1: str, content2: str) -> float:
        """
        Enhanced content similarity with rapidfuzz (10-20x faster than difflib).
        
        Args:
            content1: First content to compare
            content2: Second content to compare
            
        Returns:
            Similarity score from 0.0 to 100.0 (higher = more similar)
        """
        try:
            # Quick hash check first (performance optimization)
            if content1 == content2:
                return 100.0
            
            if RAPIDFUZZ_AVAILABLE:
                # Use rapidfuzz for fast similarity scoring
                # Limit to first 1000 chars for performance on large content
                sample1 = content1[:1000] if len(content1) > 1000 else content1
                sample2 = content2[:1000] if len(content2) > 1000 else content2
                
                return fuzz.ratio(sample1, sample2)
            else:
                # Fallback to basic Jaccard similarity if rapidfuzz not available
                words1 = set(content1.lower().split())
                words2 = set(content2.lower().split())
                
                if len(words1) == 0 and len(words2) == 0:
                    return 100.0
                if len(words1) == 0 or len(words2) == 0:
                    return 0.0
                
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                
                if union == 0:
                    return 0.0
                
                # Convert Jaccard similarity to 0-100 scale
                return (intersection / union) * 100.0
                
        except Exception as e:
            logger.error(f"Error calculating content similarity: {e}")
            return 0.0
    
    def _clean_content_for_hashing(self, content: str) -> str:
        """
        Clean content for consistent hashing.
        
        Args:
            content: Raw content
            
        Returns:
            Cleaned content
        """
        try:
            # Remove extra whitespace and normalize line endings
            cleaned = ' '.join(content.split())
            
            # Remove common dynamic elements that don't affect content meaning
            import re
            
            # Remove timestamps (common patterns)
            cleaned = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', '', cleaned)
            cleaned = re.sub(r'\d{1,2}/\d{1,2}/\d{4}', '', cleaned)
            
            # Remove common dynamic IDs
            cleaned = re.sub(r'id="[^"]*"', '', cleaned)
            cleaned = re.sub(r'data-\w+="[^"]*"', '', cleaned)
            
            # Normalize whitespace again after removals
            cleaned = ' '.join(cleaned.split())
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Error cleaning content: {e}")
            return content
    
    def estimate_content_quality(self, content: str) -> int:
        """
        Estimate content quality score (0-100).
        
        Args:
            content: Content to evaluate
            
        Returns:
            Quality score from 0-100
        """
        try:
            if not content or len(content.strip()) == 0:
                return 0
            
            score = 50  # Base score
            
            # Length factor (prefer substantial content)
            if len(content) > 1000:
                score += 20
            elif len(content) > 500:
                score += 10
            elif len(content) < 100:
                score -= 20
            
            # Word count factor
            words = content.split()
            if len(words) > 200:
                score += 15
            elif len(words) > 100:
                score += 10
            elif len(words) < 20:
                score -= 15
            
            # Sentence structure (rough indicator)
            sentences = content.split('.')
            if len(sentences) > 5:
                score += 10
            elif len(sentences) < 2:
                score -= 10
            
            # Check for common quality indicators
            quality_indicators = [
                'analysis', 'research', 'study', 'conclusion', 'methodology',
                'algorithm', 'strategy', 'implementation', 'framework'
            ]
            
            content_lower = content.lower()
            quality_matches = sum(1 for indicator in quality_indicators 
                                if indicator in content_lower)
            score += min(quality_matches * 5, 15)
            
            # Penalize very repetitive content
            unique_words = set(content.lower().split())
            if len(words) > 0:
                repetition_ratio = len(unique_words) / len(words)
                if repetition_ratio < 0.3:
                    score -= 20
                elif repetition_ratio > 0.7:
                    score += 10
            
            # Ensure score is within bounds
            return max(0, min(100, score))
            
        except Exception as e:
            logger.error(f"Error estimating content quality: {e}")
            return 50  # Default middle score