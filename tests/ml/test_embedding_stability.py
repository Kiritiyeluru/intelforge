#!/usr/bin/env python3
"""
Embedding Stability and Vector Store Consistency Validation
Tests for embedding consistency, dimensional stability, and vector store reliability.
"""

import hashlib
import json
import os
import shutil
import statistics
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pytest

# Test if ML dependencies are available
try:
    from sentence_transformers import SentenceTransformer

    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import chromadb

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False


@dataclass
class EmbeddingStabilityResult:
    """Result of embedding stability test."""

    test_name: str
    input_text: str
    embedding_hash: str
    dimension: int
    magnitude: float
    consistency_score: float
    passed: bool
    details: Dict[str, Any]


class EmbeddingStabilityValidator:
    """Comprehensive embedding stability validation."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize embedding stability validator."""
        self.model_name = model_name
        self.project_root = Path(__file__).parent.parent.parent
        self.temp_dirs: List[str] = []
        self.stability_results: List[EmbeddingStabilityResult] = []

        # Load model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.expected_dimension = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                print(f"Warning: Could not load model {model_name}: {e}")
                self.model = None
                self.expected_dimension = 384  # Default
        else:
            self.model = None
            self.expected_dimension = 384

    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def _compute_embedding_hash(self, embedding: np.ndarray) -> str:
        """Compute deterministic hash of embedding for comparison."""
        # Round to handle floating point precision issues
        rounded = np.round(embedding, decimals=6)
        return hashlib.sha256(rounded.tobytes()).hexdigest()[:16]

    def _compute_embedding_magnitude(self, embedding: np.ndarray) -> float:
        """Compute L2 magnitude of embedding."""
        return float(np.linalg.norm(embedding))

    def test_dimensional_consistency(self) -> bool:
        """Test that embeddings maintain consistent dimensions."""
        if not self.model:
            return False

        test_texts = [
            "Short text.",
            "This is a medium length text that contains several words and should produce a consistent embedding dimension.",
            "This is a very long text that goes on and on with lots of different words and phrases to test whether the embedding dimension remains stable regardless of input length and complexity, including various punctuation marks, numbers like 12345, and other linguistic elements that might affect the embedding generation process.",
            "",  # Empty string
            "🚀 Unicode and emojis test 中文 العربية ñoël",
            "123 456 789 000",  # Numbers only
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",  # Special characters
        ]

        try:
            embeddings = self.model.encode(test_texts)

            # Check dimensions
            dimensions = [emb.shape[0] for emb in embeddings]
            unique_dimensions = set(dimensions)

            consistency_passed = (
                len(unique_dimensions) == 1
                and list(unique_dimensions)[0] == self.expected_dimension
            )

            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="dimensional_consistency",
                    input_text=f"{len(test_texts)} test texts",
                    embedding_hash="multiple",
                    dimension=list(unique_dimensions)[0] if unique_dimensions else 0,
                    magnitude=0.0,  # Not applicable for batch test
                    consistency_score=1.0 if consistency_passed else 0.0,
                    passed=consistency_passed,
                    details={
                        "test_texts_count": len(test_texts),
                        "dimensions_found": list(unique_dimensions),
                        "expected_dimension": self.expected_dimension,
                    },
                )
            )

            return consistency_passed

        except Exception as e:
            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="dimensional_consistency",
                    input_text="error",
                    embedding_hash="",
                    dimension=0,
                    magnitude=0.0,
                    consistency_score=0.0,
                    passed=False,
                    details={"error": str(e)},
                )
            )
            return False

    def test_reproducibility(self, num_runs: int = 5) -> bool:
        """Test that identical inputs produce identical embeddings."""
        if not self.model:
            return False

        test_text = (
            "This is a test for embedding reproducibility and deterministic behavior."
        )

        try:
            embeddings = []
            embedding_hashes = []

            for run in range(num_runs):
                embedding = self.model.encode([test_text])[0]
                embeddings.append(embedding)
                embedding_hashes.append(self._compute_embedding_hash(embedding))

            # Check if all embeddings are identical
            unique_hashes = set(embedding_hashes)
            reproducibility_passed = len(unique_hashes) == 1

            # Compute pairwise similarities for additional verification
            similarities = []
            base_embedding = embeddings[0]

            for embedding in embeddings[1:]:
                similarity = np.dot(base_embedding, embedding) / (
                    np.linalg.norm(base_embedding) * np.linalg.norm(embedding)
                )
                similarities.append(similarity)

            min_similarity = min(similarities) if similarities else 1.0
            consistency_score = float(min_similarity)

            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="reproducibility",
                    input_text=test_text,
                    embedding_hash=embedding_hashes[0],
                    dimension=len(embeddings[0]),
                    magnitude=self._compute_embedding_magnitude(embeddings[0]),
                    consistency_score=consistency_score,
                    passed=reproducibility_passed and min_similarity > 0.999,
                    details={
                        "num_runs": num_runs,
                        "unique_hashes": len(unique_hashes),
                        "min_similarity": min_similarity,
                        "all_similarities": similarities,
                    },
                )
            )

            return reproducibility_passed and min_similarity > 0.999

        except Exception as e:
            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="reproducibility",
                    input_text=test_text,
                    embedding_hash="",
                    dimension=0,
                    magnitude=0.0,
                    consistency_score=0.0,
                    passed=False,
                    details={"error": str(e)},
                )
            )
            return False

    def test_magnitude_stability(self) -> bool:
        """Test that similar texts have similar embedding magnitudes."""
        if not self.model:
            return False

        # Test texts with similar semantic content but different lengths
        test_groups = [
            [
                "Machine learning is powerful.",
                "Machine learning algorithms are very powerful tools.",
                "Machine learning and artificial intelligence are powerful technologies.",
            ],
            [
                "The weather is nice today.",
                "Today we have really nice weather conditions.",
                "The weather conditions today are particularly nice and pleasant.",
            ],
        ]

        try:
            magnitude_ratios = []

            for group in test_groups:
                embeddings = self.model.encode(group)
                magnitudes = [
                    self._compute_embedding_magnitude(emb) for emb in embeddings
                ]

                # Compute magnitude ratios
                for i in range(len(magnitudes)):
                    for j in range(i + 1, len(magnitudes)):
                        ratio = max(magnitudes[i], magnitudes[j]) / min(
                            magnitudes[i], magnitudes[j]
                        )
                        magnitude_ratios.append(ratio)

            # Magnitude ratios should be reasonable (not too different)
            max_ratio = max(magnitude_ratios)
            mean_ratio = statistics.mean(magnitude_ratios)

            # Accept ratios up to 2.0 as reasonable
            stability_passed = max_ratio < 2.0 and mean_ratio < 1.5

            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="magnitude_stability",
                    input_text=f"{len(test_groups)} groups tested",
                    embedding_hash="multiple",
                    dimension=self.expected_dimension,
                    magnitude=mean_ratio,
                    consistency_score=1.0 / max_ratio,  # Inverse of max ratio
                    passed=stability_passed,
                    details={
                        "max_magnitude_ratio": max_ratio,
                        "mean_magnitude_ratio": mean_ratio,
                        "all_ratios": magnitude_ratios,
                        "groups_tested": len(test_groups),
                    },
                )
            )

            return stability_passed

        except Exception as e:
            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="magnitude_stability",
                    input_text="error",
                    embedding_hash="",
                    dimension=0,
                    magnitude=0.0,
                    consistency_score=0.0,
                    passed=False,
                    details={"error": str(e)},
                )
            )
            return False

    def test_semantic_stability(self) -> bool:
        """Test that semantically similar texts have similar embeddings."""
        if not self.model:
            return False

        # Pairs of semantically similar texts
        similar_pairs = [
            ("The cat is sleeping.", "A cat is taking a nap."),
            ("I love programming.", "I enjoy coding."),
            ("The weather is cold.", "It's chilly outside."),
            ("She is reading a book.", "She's studying from a novel."),
        ]

        # Pairs of semantically different texts
        different_pairs = [
            ("The cat is sleeping.", "Quantum physics is complex."),
            ("I love programming.", "The ocean is blue."),
            ("The weather is cold.", "Mathematics is challenging."),
            ("She is reading a book.", "Cars need gasoline."),
        ]

        try:
            similar_similarities = []
            different_similarities = []

            # Test similar pairs
            for text1, text2 in similar_pairs:
                embeddings = self.model.encode([text1, text2])
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                similar_similarities.append(similarity)

            # Test different pairs
            for text1, text2 in different_pairs:
                embeddings = self.model.encode([text1, text2])
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                different_similarities.append(similarity)

            # Similar texts should have higher similarity than different texts
            min_similar = min(similar_similarities)
            max_different = max(different_similarities)
            mean_similar = statistics.mean(similar_similarities)
            mean_different = statistics.mean(different_similarities)

            # Semantic stability requires clear separation
            semantic_separation = min_similar > max_different
            reasonable_similarity = mean_similar > 0.7 and mean_different < 0.5

            semantic_stability_passed = semantic_separation and reasonable_similarity

            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="semantic_stability",
                    input_text=f"{len(similar_pairs)} similar + {len(different_pairs)} different pairs",
                    embedding_hash="multiple",
                    dimension=self.expected_dimension,
                    magnitude=mean_similar - mean_different,  # Separation measure
                    consistency_score=(
                        min_similar / max_different if max_different > 0 else 0.0
                    ),
                    passed=semantic_stability_passed,
                    details={
                        "min_similar_similarity": min_similar,
                        "max_different_similarity": max_different,
                        "mean_similar_similarity": mean_similar,
                        "mean_different_similarity": mean_different,
                        "semantic_separation": semantic_separation,
                        "reasonable_similarity": reasonable_similarity,
                    },
                )
            )

            return semantic_stability_passed

        except Exception as e:
            self.stability_results.append(
                EmbeddingStabilityResult(
                    test_name="semantic_stability",
                    input_text="error",
                    embedding_hash="",
                    dimension=0,
                    magnitude=0.0,
                    consistency_score=0.0,
                    passed=False,
                    details={"error": str(e)},
                )
            )
            return False

    def run_all_stability_tests(self) -> Dict[str, bool]:
        """Run all embedding stability tests."""
        print("🧠 Running Embedding Stability Tests")
        print("=" * 40)

        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            print("❌ sentence-transformers not available")
            return {}

        if not self.model:
            print("❌ Model not loaded")
            return {}

        test_results = {}

        print("📏 Testing dimensional consistency...")
        test_results["dimensional_consistency"] = self.test_dimensional_consistency()

        print("🔄 Testing reproducibility...")
        test_results["reproducibility"] = self.test_reproducibility()

        print("📊 Testing magnitude stability...")
        test_results["magnitude_stability"] = self.test_magnitude_stability()

        print("🎯 Testing semantic stability...")
        test_results["semantic_stability"] = self.test_semantic_stability()

        return test_results

    def _convert_to_json_serializable(self, obj):
        """Convert numpy types and other non-serializable objects to JSON-serializable types."""
        if isinstance(obj, dict):
            return {k: self._convert_to_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif hasattr(obj, "item"):  # numpy scalar
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, int)):
            return int(obj)
        elif isinstance(obj, (np.floating, float)):
            return float(obj)
        else:
            return obj

    def generate_stability_report(self, output_dir: str = "logs/ml_testing") -> str:
        """Generate embedding stability report."""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            output_dir, f"embedding_stability_report_{timestamp}.json"
        )

        # Calculate summary statistics
        total_tests = len(self.stability_results)
        passed_tests = sum(1 for r in self.stability_results if r.passed)

        report_data = {
            "embedding_stability_report": {
                "timestamp": datetime.now().isoformat(),
                "model_name": self.model_name,
                "model_available": self.model is not None,
                "expected_dimension": self.expected_dimension,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "success_rate": (
                        passed_tests / total_tests if total_tests > 0 else 0.0
                    ),
                },
                "test_results": [
                    {
                        "test_name": r.test_name,
                        "input_text": r.input_text,
                        "embedding_hash": r.embedding_hash,
                        "dimension": int(r.dimension),
                        "magnitude": float(r.magnitude),
                        "consistency_score": float(r.consistency_score),
                        "passed": bool(r.passed),
                        "details": self._convert_to_json_serializable(r.details),
                    }
                    for r in self.stability_results
                ],
            }
        }

        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"📊 Embedding stability report saved to: {report_file}")
        return report_file


@pytest.mark.skipif(
    not SENTENCE_TRANSFORMERS_AVAILABLE, reason="sentence-transformers not available"
)
class TestEmbeddingStability:
    """Test embedding stability using pytest."""

    def setup_method(self):
        """Set up test method."""
        self.validator = EmbeddingStabilityValidator()

    def teardown_method(self):
        """Clean up after test method."""
        self.validator.cleanup()

    def test_dimensional_consistency(self):
        """Test embedding dimensional consistency."""
        result = self.validator.test_dimensional_consistency()
        assert result, "Dimensional consistency test failed"

    def test_reproducibility(self):
        """Test embedding reproducibility."""
        result = self.validator.test_reproducibility()
        assert result, "Reproducibility test failed"

    def test_magnitude_stability(self):
        """Test embedding magnitude stability."""
        result = self.validator.test_magnitude_stability()
        assert result, "Magnitude stability test failed"

    def test_semantic_stability(self):
        """Test semantic stability."""
        result = self.validator.test_semantic_stability()
        assert result, "Semantic stability test failed"


@pytest.mark.skipif(
    not (SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE),
    reason="Both sentence-transformers and chromadb required",
)
class TestVectorStoreConsistency:
    """Test vector store consistency and reliability."""

    def setup_method(self):
        """Set up test method."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up after test method."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_chromadb_persistence_consistency(self):
        """Test ChromaDB persistence and data consistency."""
        import chromadb
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Test data
        documents = [
            "First document for persistence testing.",
            "Second document with different content.",
            "Third document for comprehensive testing.",
        ]

        embeddings = model.encode(documents).tolist()
        ids = ["doc1", "doc2", "doc3"]

        # Test with persistent client
        client = chromadb.PersistentClient(path=self.temp_dir)
        collection = client.create_collection("persistence_test")

        # Add documents
        collection.add(documents=documents, embeddings=embeddings, ids=ids)

        # Query and verify
        query_embedding = model.encode(["Test query document"]).tolist()
        initial_results = collection.query(
            query_embeddings=query_embedding, n_results=3
        )

        # Create new client instance (simulating restart)
        client2 = chromadb.PersistentClient(path=self.temp_dir)
        collection2 = client2.get_collection("persistence_test")

        # Query again with new client
        persistent_results = collection2.query(
            query_embeddings=query_embedding, n_results=3
        )

        # Results should be identical
        assert initial_results["ids"] == persistent_results["ids"]
        assert initial_results["documents"] == persistent_results["documents"]

        # Distances should be nearly identical (allowing for floating point precision)
        for i in range(len(initial_results["distances"][0])):
            initial_dist = initial_results["distances"][0][i]
            persistent_dist = persistent_results["distances"][0][i]
            assert abs(initial_dist - persistent_dist) < 1e-6

    def test_chromadb_concurrent_operations(self):
        """Test ChromaDB consistency under concurrent operations."""
        import chromadb
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.Client()
        collection = client.create_collection("concurrent_test")

        # Add initial documents
        initial_docs = ["Base document for concurrent testing."]
        initial_embeddings = model.encode(initial_docs).tolist()
        collection.add(
            documents=initial_docs, embeddings=initial_embeddings, ids=["base_doc"]
        )

        # Simulate concurrent operations
        operations_count = 10

        for i in range(operations_count):
            # Add document
            doc = f"Concurrent document number {i}."
            embedding = model.encode([doc]).tolist()
            doc_id = f"concurrent_doc_{i}"

            collection.add(documents=[doc], embeddings=embedding, ids=[doc_id])

            # Verify document was added
            retrieved = collection.get(ids=[doc_id])
            assert len(retrieved["ids"]) == 1
            assert retrieved["documents"][0] == doc

            # Verify total count
            expected_count = 1 + i + 1  # base + current additions
            actual_count = collection.count()
            assert actual_count == expected_count

    def test_embedding_consistency_across_storage(self):
        """Test that embeddings remain consistent when stored and retrieved."""
        import chromadb
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.Client()
        collection = client.create_collection("consistency_test")

        # Test document
        test_doc = (
            "This document tests embedding consistency across storage operations."
        )
        original_embedding = model.encode([test_doc])[0]

        # Store with custom embedding
        collection.add(
            documents=[test_doc],
            embeddings=[original_embedding.tolist()],
            ids=["consistency_doc"],
        )

        # Retrieve and compare
        query_results = collection.query(
            query_embeddings=[original_embedding.tolist()],
            n_results=1,
            include=["documents", "distances", "embeddings"],
        )

        # Should find exact match with near-zero distance
        assert len(query_results["ids"][0]) == 1
        assert query_results["ids"][0][0] == "consistency_doc"
        assert query_results["documents"][0][0] == test_doc
        assert query_results["distances"][0][0] < 1e-6  # Should be nearly zero

        # Retrieved embedding should match original
        retrieved_embedding = np.array(query_results["embeddings"][0][0])
        embedding_difference = np.max(np.abs(original_embedding - retrieved_embedding))
        assert embedding_difference < 1e-6


def main():
    """Main entry point for embedding stability testing."""
    print("🧠 IntelForge Embedding Stability Validation")
    print("=" * 50)

    # Check component availability
    print(
        f"📦 sentence-transformers: {'✅' if SENTENCE_TRANSFORMERS_AVAILABLE else '❌'}"
    )
    print(f"📦 chromadb: {'✅' if CHROMADB_AVAILABLE else '❌'}")

    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("❌ Cannot run tests without sentence-transformers")
        return

    # Run stability tests
    validator = EmbeddingStabilityValidator()
    test_results = validator.run_all_stability_tests()

    # Print results
    print("\n📊 Test Results:")
    print("-" * 30)
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    # Generate report
    report_file = validator.generate_stability_report()

    # Overall result
    all_passed = all(test_results.values())
    print(
        f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
    )

    if not all_passed:
        exit(1)


if __name__ == "__main__":
    main()
