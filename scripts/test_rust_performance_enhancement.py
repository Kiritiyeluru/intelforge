#!/usr/bin/env python3
"""
Rust Performance Enhancement Test Suite
Tests performance improvements from Rust-backed libraries
"""

import time
import polars as pl
import pandas as pd
from transformers import AutoTokenizer
import numpy as np
from typing import Dict, Any
from pathlib import Path


class RustPerformanceEnhancementTest:
    """Test suite for Rust-backed performance improvements"""

    def __init__(self):
        self.results = {}
        self.test_data = self._generate_test_data()

    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate test data for performance comparisons"""
        return {
            "text_samples": [
                "The quick brown fox jumps over the lazy dog. " * 100,
                "Financial markets are experiencing significant volatility. " * 100,
                "Algorithmic trading strategies require efficient data processing. "
                * 100,
                "Real-time market analysis demands high-performance computing. " * 100,
                "Vector databases enable fast similarity searches. " * 100,
            ]
            * 200,  # 1000 total samples
            "dataframe_data": {
                "timestamp": pd.date_range("2024-01-01", periods=10000, freq="1min"),
                "price": np.random.normal(100, 5, 10000),
                "volume": np.random.randint(1000, 10000, 10000),
                "symbol": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"] * 2000,
            },
        }

    def test_tokenizers_performance(self) -> Dict[str, float]:
        """Test tokenizers (Rust) vs transformers tokenizers performance"""
        print("Testing tokenizers performance...")

        # Test with transformers tokenizer (Python-based)
        start_time = time.time()
        try:
            transformers_tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
            for text in self.test_data["text_samples"]:
                transformers_tokenizer.tokenize(text)
            transformers_time = time.time() - start_time
        except Exception as e:
            print(f"Transformers tokenizer test failed: {e}")
            transformers_time = float("inf")

        # Test with tokenizers library (Rust-backed)
        start_time = time.time()
        try:
            # Use a simple whitespace tokenizer for fair comparison
            from tokenizers import Tokenizer, models, pre_tokenizers

            rust_tokenizer = Tokenizer(models.BPE())
            rust_tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()

            for text in self.test_data["text_samples"]:
                rust_tokenizer.encode(text)
            rust_time = time.time() - start_time
        except Exception as e:
            print(f"Rust tokenizer test failed: {e}")
            rust_time = float("inf")

        speedup = transformers_time / rust_time if rust_time > 0 else 0

        result = {
            "transformers_time": transformers_time,
            "rust_tokenizers_time": rust_time,
            "speedup": speedup,
        }

        print(f"  Transformers tokenizer: {transformers_time:.4f}s")
        print(f"  Rust tokenizers: {rust_time:.4f}s")
        print(f"  Speedup: {speedup:.2f}x")

        return result

    def test_polars_performance(self) -> Dict[str, float]:
        """Test polars (Rust) vs pandas performance"""
        print("Testing polars vs pandas performance...")

        # Generate larger dataset for better performance testing
        large_data = {
            "timestamp": pd.date_range("2024-01-01", periods=100000, freq="1min"),
            "price": np.random.normal(100, 5, 100000),
            "volume": np.random.randint(1000, 10000, 100000),
            "symbol": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"] * 20000,
        }

        # Test pandas
        start_time = time.time()
        df_pandas = pd.DataFrame(large_data)
        # Complex operations
        (
            df_pandas.groupby("symbol")
            .agg({"price": ["mean", "std", "min", "max"], "volume": "sum"})
            .reset_index()
        )
        pandas_time = time.time() - start_time

        # Test polars
        start_time = time.time()
        df_polars = pl.DataFrame(large_data)
        # Complex operations
        (
            df_polars.group_by("symbol").agg(
                [
                    pl.col("price").mean().alias("price_mean"),
                    pl.col("price").std().alias("price_std"),
                    pl.col("price").min().alias("price_min"),
                    pl.col("price").max().alias("price_max"),
                    pl.col("volume").sum().alias("volume_sum"),
                ]
            )
        )
        polars_time = time.time() - start_time

        speedup = pandas_time / polars_time if polars_time > 0 else 0

        result = {
            "pandas_time": pandas_time,
            "polars_time": polars_time,
            "speedup": speedup,
        }

        print(f"  Pandas: {pandas_time:.4f}s")
        print(f"  Polars: {polars_time:.4f}s")
        print(f"  Speedup: {speedup:.2f}x")

        return result

    def test_qdrant_client_setup(self) -> Dict[str, Any]:
        """Test qdrant-client setup and basic operations"""
        print("Testing qdrant-client setup...")

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct

            # Test in-memory client
            start_time = time.time()
            client = QdrantClient(":memory:")

            # Create collection
            collection_name = "test_collection"
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

            # Test vector operations
            vectors = np.random.random((100, 384)).astype(np.float32)
            points = [
                PointStruct(
                    id=i, vector=vectors[i].tolist(), payload={"text": f"Sample {i}"}
                )
                for i in range(100)
            ]

            # Insert vectors
            client.upsert(collection_name=collection_name, points=points)

            # Test search
            search_vector = np.random.random(384).astype(np.float32)
            results = client.search(
                collection_name=collection_name,
                query_vector=search_vector.tolist(),
                limit=10,
            )

            setup_time = time.time() - start_time

            result = {
                "setup_successful": True,
                "setup_time": setup_time,
                "vectors_inserted": len(points),
                "search_results": len(results),
            }

            print(f"  Setup successful: {setup_time:.4f}s")
            print(f"  Vectors inserted: {len(points)}")
            print(f"  Search results: {len(results)}")

        except Exception as e:
            result = {"setup_successful": False, "error": str(e)}
            print(f"  Setup failed: {e}")

        return result

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all performance tests"""
        print("=" * 60)
        print("RUST PERFORMANCE ENHANCEMENT TEST SUITE")
        print("=" * 60)

        results = {}

        # Test 1: Tokenizers Performance
        results["tokenizers"] = self.test_tokenizers_performance()
        print()

        # Test 2: Polars Performance
        results["polars"] = self.test_polars_performance()
        print()

        # Test 3: Qdrant Client Setup
        results["qdrant"] = self.test_qdrant_client_setup()
        print()

        # Summary
        print("=" * 60)
        print("PERFORMANCE ENHANCEMENT SUMMARY")
        print("=" * 60)

        if results["tokenizers"]["speedup"] > 1:
            print(f"✅ Tokenizers: {results['tokenizers']['speedup']:.2f}x speedup")
        else:
            print("❌ Tokenizers: No significant speedup")

        if results["polars"]["speedup"] > 1:
            print(f"✅ Polars: {results['polars']['speedup']:.2f}x speedup")
        else:
            print("❌ Polars: No significant speedup")

        if results["qdrant"]["setup_successful"]:
            print("✅ Qdrant: Vector operations ready")
        else:
            print("❌ Qdrant: Setup failed")

        # Calculate total performance improvement
        total_improvement = (
            results["tokenizers"]["speedup"] + results["polars"]["speedup"]
        ) / 2

        print(f"\n🚀 Average Performance Improvement: {total_improvement:.2f}x")

        return results


def main():
    """Run the performance test suite"""
    tester = RustPerformanceEnhancementTest()
    results = tester.run_comprehensive_test()

    # Save results
    output_file = Path("vault/logs/rust_performance_enhancement_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    import json

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📊 Results saved to: {output_file}")


if __name__ == "__main__":
    main()
