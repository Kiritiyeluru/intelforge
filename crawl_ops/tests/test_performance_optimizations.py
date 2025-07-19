#!/usr/bin/env python3
"""
Test suite for IntelForge performance optimizations.
Tests orjson, rapidfuzz, and zstandard integrations.
"""

import pytest
import tempfile
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_orjson_import():
    """Test that orjson can be imported and used as json replacement."""
    try:
        import orjson as json

        # Test basic functionality
        test_data = {"test": "data", "number": 42, "list": [1, 2, 3]}

        # Test encoding
        encoded = json.dumps(test_data)
        assert isinstance(encoded, bytes)

        # Test decoding
        decoded = json.loads(encoded)
        assert decoded == test_data

    except ImportError:
        pytest.skip("orjson not available")


def test_rapidfuzz_content_similarity():
    """Test rapidfuzz integration for content similarity."""
    try:
        from rapidfuzz import fuzz

        # Test identical content
        content1 = "This is a test content for similarity matching."
        content2 = "This is a test content for similarity matching."
        similarity = fuzz.ratio(content1, content2)
        assert similarity == 100.0

        # Test similar content
        content3 = "This is a test content for similarity checking."
        similarity2 = fuzz.ratio(content1, content3)
        assert 80.0 <= similarity2 <= 95.0  # Should be high similarity

        # Test different content
        content4 = "Completely different text with no relation."
        similarity3 = fuzz.ratio(content1, content4)
        assert similarity3 < 50.0  # Should be low similarity

    except ImportError:
        pytest.skip("rapidfuzz not available")


def test_zstandard_compressed_io():
    """Test zstandard compressed JSONL utilities."""
    try:
        from crawl_ops.utils.compressed_io import write_jsonl_zst, read_jsonl_zst

        # Test data
        test_data = [
            {"id": 1, "content": "First item", "metadata": {"type": "test"}},
            {"id": 2, "content": "Second item", "metadata": {"type": "test"}},
            {"id": 3, "content": "Third item", "metadata": {"type": "test"}}
        ]

        with tempfile.NamedTemporaryFile(suffix='.jsonl.zst', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Test write
            write_jsonl_zst(tmp_path, test_data)
            assert tmp_path.exists()
            assert tmp_path.stat().st_size > 0

            # Test read
            loaded_data = list(read_jsonl_zst(tmp_path))
            assert len(loaded_data) == len(test_data)
            assert loaded_data == test_data

        finally:
            # Cleanup
            if tmp_path.exists():
                tmp_path.unlink()

    except ImportError:
        pytest.skip("zstandard or compressed_io not available")


def test_content_detector_rapidfuzz_integration():
    """Test content detector with rapidfuzz integration."""
    try:
        from crawl_ops.tracking.content_detector import ContentChangeDetector

        detector = ContentChangeDetector()

        # Test enhanced similarity method
        content1 = "This is original content about trading strategies."
        content2 = "This is original content about trading strategies."  # Identical
        content3 = "This is modified content about trading algorithms."   # Similar
        content4 = "Completely unrelated text about cooking recipes."    # Different

        # Test identical content
        similarity1 = detector.enhanced_content_similarity(content1, content2)
        assert similarity1 == 100.0

        # Test similar content
        similarity2 = detector.enhanced_content_similarity(content1, content3)
        assert 50.0 <= similarity2 <= 90.0

        # Test different content
        similarity3 = detector.enhanced_content_similarity(content1, content4)
        assert similarity3 < 40.0

    except ImportError:
        pytest.skip("rapidfuzz or content_detector not available")


def test_performance_package_availability():
    """Test that all performance optimization packages are available."""
    packages = {
        'orjson': 'orjson',
        'rapidfuzz': 'rapidfuzz',
        'zstandard': 'zstandard',
        'selectolax': 'selectolax',
        'pytest-cov': 'pytest_cov'
    }

    available_packages = []
    missing_packages = []

    for name, import_name in packages.items():
        try:
            __import__(import_name)
            available_packages.append(name)
        except ImportError:
            missing_packages.append(name)

    # Should have at least the core performance packages
    assert 'orjson' in available_packages, "orjson required for JSON performance"
    assert 'rapidfuzz' in available_packages, "rapidfuzz required for similarity performance"
    assert 'zstandard' in available_packages, "zstandard required for compression"

    print(f"Available packages: {available_packages}")
    if missing_packages:
        print(f"Missing packages: {missing_packages}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
