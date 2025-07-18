#!/usr/bin/env python3
"""
Pytest configuration file for IntelForge testing
Shared fixtures and configuration for all tests
"""

import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(scope="session")
def project_root():
    """Provide project root path"""
    return PROJECT_ROOT


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_config():
    """Standard mock configuration for all tests"""
    return {
        "reddit": {
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "user_agent": "IntelForge-Test/1.0",
        },
        "github": {"token": "test_github_token"},
        "scraping": {"delay": 1, "max_retries": 3, "timeout": 30},
        "output": {
            "format": "markdown",
            "directory": "vault/notes",
            "database": "vault/database.db",
        },
        "ai": {
            "openai_api_key": "test_openai_key",
            "model": "gpt-3.5-turbo",
            "max_tokens": 1000,
        },
    }


@pytest.fixture
def mock_reddit_post():
    """Mock Reddit post data"""
    return {
        "id": "test123",
        "title": "Sample Trading Strategy Discussion",
        "author": "test_trader",
        "content": "This is a sample post about algorithmic trading strategies.",
        "url": "https://reddit.com/r/algotrading/test123",
        "created_utc": 1641024000,
        "score": 150,
        "num_comments": 25,
        "subreddit": "algotrading",
        "flair": "Strategy",
    }


@pytest.fixture
def mock_github_repo():
    """Mock GitHub repository data"""
    return {
        "name": "trading-bot",
        "full_name": "user/trading-bot",
        "description": "A sample algorithmic trading bot",
        "url": "https://github.com/user/trading-bot",
        "stars": 1250,
        "forks": 300,
        "language": "Python",
        "topics": ["trading", "algorithms", "finance"],
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2024-12-01T00:00:00Z",
    }


@pytest.fixture
def mock_web_content():
    """Mock web page content"""
    return {
        "url": "https://example.com/trading-article",
        "title": "Advanced Trading Strategies",
        "content": "This is sample content about trading strategies...",
        "author": "Expert Trader",
        "published_date": "2024-01-15",
        "tags": ["trading", "strategies", "finance"],
    }


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing"""
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def mock_file_system(temp_dir):
    """Mock file system operations"""
    vault_dir = temp_dir / "vault"
    notes_dir = vault_dir / "notes"
    logs_dir = vault_dir / "logs"

    vault_dir.mkdir()
    notes_dir.mkdir()
    logs_dir.mkdir()

    return {"vault": vault_dir, "notes": notes_dir, "logs": logs_dir}


@pytest.fixture
def mock_api_responses():
    """Mock API responses for various services"""
    return {
        "reddit_success": {
            "status_code": 200,
            "json": lambda: {"data": {"children": []}},
        },
        "github_success": {"status_code": 200, "json": lambda: {"items": []}},
        "web_success": {
            "status_code": 200,
            "text": "<html><body>Sample content</body></html>",
        },
    }


@pytest.fixture(autouse=True)
def mock_config_file(mock_config, temp_dir):
    """Automatically mock config file for all tests"""
    config_path = temp_dir / "config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(mock_config, f)

    with patch(
        "builtins.open",
        side_effect=lambda path, *args, **kwargs: (
            open(config_path, *args, **kwargs)
            if "config.yaml" in str(path)
            else open(path, *args, **kwargs)
        ),
    ):
        yield config_path


# Pytest markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "performance: mark test as performance test")
    config.addinivalue_line("markers", "scraping: mark test as scraping test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


# Skip integration tests by default unless specifically requested
def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle markers"""
    if config.getoption("-m") is None:
        # Skip integration tests by default
        skip_integration = pytest.mark.skip(
            reason="Integration tests skipped by default"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
