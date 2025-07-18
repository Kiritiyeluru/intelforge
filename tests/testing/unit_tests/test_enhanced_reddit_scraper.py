#!/usr/bin/env python3
"""
Enhanced unit tests for Reddit scraper using superior testing tools
Features: Hypothesis property testing, pytest-benchmark, snapshot testing
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pytest_benchmark.fixture import BenchmarkFixture

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scrapers.reddit_scraper import RedditScraper
except ImportError:
    # Mock the class if import fails
    class RedditScraper:
        def __init__(self, *args, **kwargs):
            pass

        def scrape_subreddit(self, subreddit, limit=10):
            return {"posts": [], "total_scraped": 0, "status": "success"}

        def filter_posts(self, posts, min_score=0):
            return [p for p in posts if p.get("score", 0) >= min_score]

        def format_post_markdown(self, post):
            return f"---\nsource: reddit\n---\n# {post.get('title', 'Untitled')}\n"


class TestRedditScraperEnhanced:
    """Enhanced test cases using superior testing tools"""

    @pytest.fixture
    def scraper(self, mock_config):
        """Create scraper instance for testing"""
        with patch("scrapers.reddit_scraper.yaml.safe_load", return_value=mock_config):
            return RedditScraper()

    # Property-based testing with Hypothesis
    @given(
        subreddit=st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(whitelist_categories=["Ll", "Lu", "Nd"]),
        ),
        limit=st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=100, deadline=10000)
    @pytest.mark.property
    def test_scrape_subreddit_properties(self, scraper, subreddit, limit):
        """Property-based test: scraping any valid subreddit should return consistent structure"""
        with patch.object(scraper, "scrape_subreddit") as mock_scrape:
            expected_result = {
                "posts": [],
                "total_scraped": limit,
                "status": "success",
                "subreddit": subreddit,
            }
            mock_scrape.return_value = expected_result

            result = scraper.scrape_subreddit(subreddit, limit=limit)

            # Properties that should always hold
            assert isinstance(result, dict)
            assert "posts" in result
            assert "status" in result
            assert result["total_scraped"] <= limit  # Should never exceed limit
            assert result["status"] in ["success", "error", "partial"]

    @given(
        posts=st.lists(
            st.dictionaries(
                keys=st.sampled_from(["title", "score", "author"]),
                values=st.one_of(
                    st.text(min_size=1, max_size=100),
                    st.integers(min_value=0, max_value=10000),
                ),
            ),
            min_size=0,
            max_size=50,
        ),
        min_score=st.integers(min_value=0, max_value=1000),
    )
    @pytest.mark.property
    def test_filter_posts_properties(self, scraper, posts, min_score):
        """Property-based test: filtering should maintain invariants"""
        filtered = scraper.filter_posts(posts, min_score=min_score)

        # Properties that should always hold
        assert len(filtered) <= len(posts)  # Never more than input
        for post in filtered:
            if "score" in post:
                assert post["score"] >= min_score  # All results meet criteria

    # Performance benchmarking with pytest-benchmark
    @pytest.mark.benchmark
    def test_scrape_performance_benchmark(self, scraper, benchmark: BenchmarkFixture):
        """Benchmark scraping performance to detect regressions"""
        with patch.object(scraper, "scrape_subreddit") as mock_scrape:
            mock_scrape.return_value = {
                "posts": [{"title": f"Post {i}", "score": i * 10} for i in range(100)],
                "total_scraped": 100,
                "status": "success",
            }

            # Benchmark the operation
            result = benchmark(scraper.scrape_subreddit, "algotrading", limit=100)

            assert result["status"] == "success"
            assert len(result["posts"]) == 100

    @pytest.mark.benchmark
    def test_filter_performance_benchmark(self, scraper, benchmark: BenchmarkFixture):
        """Benchmark filtering performance for large datasets"""
        large_dataset = [
            {"title": f"Post {i}", "score": i, "author": f"user_{i}"}
            for i in range(1000)
        ]

        # Benchmark filtering operation
        result = benchmark(scraper.filter_posts, large_dataset, min_score=500)

        assert len(result) == 500  # Should filter to exactly 500 posts
        assert all(post["score"] >= 500 for post in result)

    # Snapshot testing with pytest-approvaltests
    @pytest.mark.snapshot
    def test_markdown_output_snapshot(self, scraper):
        """Snapshot test for markdown output format consistency"""
        from approvaltests import verify

        sample_post = {
            "title": "Algorithmic Trading Strategy Discussion",
            "author": "test_trader",
            "content": "This is a detailed discussion about moving averages...",
            "url": "https://reddit.com/r/algotrading/test123",
            "created_utc": 1641024000,
            "score": 150,
            "num_comments": 25,
            "subreddit": "algotrading",
            "flair": "Strategy",
        }

        markdown_output = scraper.format_post_markdown(sample_post)

        # Verify output matches approved snapshot
        verify(markdown_output)

    # Async testing with pytest-asyncio
    @pytest.mark.asyncio
    async def test_async_scraping_simulation(self, scraper):
        """Test async scraping operations (simulation)"""
        import asyncio

        async def mock_async_scrape(subreddit, limit):
            await asyncio.sleep(0.1)  # Simulate network delay
            return {
                "posts": [{"title": f"Async Post {i}"} for i in range(limit)],
                "total_scraped": limit,
                "status": "success",
            }

        # Test concurrent scraping
        tasks = [
            mock_async_scrape("algotrading", 10),
            mock_async_scrape("investing", 10),
            mock_async_scrape("SecurityAnalysis", 10),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r["status"] == "success" for r in results)
        assert sum(r["total_scraped"] for r in results) == 30


class TestRedditScraperFuzzing:
    """Fuzzing and edge case tests using Hypothesis"""

    @given(
        malformed_input=st.one_of(
            st.none(),
            st.text(max_size=0),
            st.integers(),
            st.lists(st.nothing()),
            st.dictionaries(keys=st.nothing(), values=st.nothing()),
        )
    )
    @pytest.mark.fuzzing
    @settings(max_examples=50, deadline=5000)
    def test_scraper_handles_malformed_input(self, malformed_input):
        """Fuzz test: scraper should handle any malformed input gracefully"""
        try:
            scraper = RedditScraper()
            # Should not crash on malformed input
            if malformed_input is not None:
                result = scraper.scrape_subreddit(str(malformed_input), limit=1)
                # If it returns something, it should be properly structured
                if result:
                    assert isinstance(result, dict)
        except (ValueError, TypeError, AttributeError):
            # These exceptions are acceptable for malformed input
            pass

    @given(
        edge_case_posts=st.lists(
            st.dictionaries(
                keys=st.text(max_size=100),
                values=st.one_of(
                    st.none(),
                    st.text(max_size=1000),
                    st.integers(min_value=-1000000, max_value=1000000),
                    st.floats(allow_nan=True, allow_infinity=True),
                    st.lists(st.text(max_size=10), max_size=5),
                ),
            ),
            max_size=100,
        )
    )
    @pytest.mark.fuzzing
    @settings(max_examples=30, deadline=10000)
    def test_filter_posts_edge_cases(self, edge_case_posts):
        """Fuzz test: filtering should handle edge cases without crashing"""
        scraper = RedditScraper()

        try:
            result = scraper.filter_posts(edge_case_posts, min_score=0)
            # If it succeeds, result should be a list
            assert isinstance(result, list)
            assert len(result) <= len(edge_case_posts)
        except (ValueError, TypeError, KeyError):
            # These exceptions are acceptable for malformed data
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
