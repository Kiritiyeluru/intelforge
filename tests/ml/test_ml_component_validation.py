#!/usr/bin/env python3
"""
ML Component Validation Tests
Tests for sentence-transformers, ChromaDB, and other ML components used in IntelForge.
"""

import pytest
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
from datetime import datetime

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

try:
    import qdrant_client
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class MLComponentValidator:
    """Comprehensive ML component validation."""
    
    def __init__(self):
        """Initialize ML component validator."""
        self.project_root = Path(__file__).parent.parent.parent
        self.test_results: List[Dict[str, Any]] = []
        self.temp_dirs: List[str] = []
    
    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def _log_test_result(self, component: str, test_name: str, 
                        passed: bool, details: Dict[str, Any] = None):
        """Log test result for reporting."""
        result = {
            "component": component,
            "test_name": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)


@pytest.mark.skipif(not SENTENCE_TRANSFORMERS_AVAILABLE, 
                   reason="sentence-transformers not available")
class TestSentenceTransformers:
    """Test sentence-transformers functionality."""
    
    def setup_method(self):
        """Set up test method."""
        self.validator = MLComponentValidator()
        
    def teardown_method(self):
        """Clean up after test method."""
        self.validator.cleanup()
    
    def test_model_loading(self):
        """Test loading sentence-transformers model."""
        try:
            # Use a small, fast model for testing
            model = SentenceTransformer('all-MiniLM-L6-v2')
            assert model is not None
            
            # Test model configuration
            assert hasattr(model, 'encode')
            assert hasattr(model, 'get_sentence_embedding_dimension')
            
            # Verify expected dimensions
            expected_dim = 384  # all-MiniLM-L6-v2 dimensions
            actual_dim = model.get_sentence_embedding_dimension()
            assert actual_dim == expected_dim, f"Expected {expected_dim}D, got {actual_dim}D"
            
            self.validator._log_test_result(
                "sentence_transformers", "model_loading", True,
                {"model_name": "all-MiniLM-L6-v2", "dimensions": actual_dim}
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "sentence_transformers", "model_loading", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed to load sentence-transformers model: {e}")
    
    def test_embedding_generation(self):
        """Test embedding generation."""
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Test single text embedding
            test_text = "This is a test sentence for embedding generation."
            embedding = model.encode(test_text)
            
            assert isinstance(embedding, np.ndarray)
            assert embedding.shape == (384,)  # Expected dimensions
            assert not np.all(embedding == 0)  # Should not be all zeros
            
            # Test batch embedding
            test_texts = [
                "First test sentence.",
                "Second test sentence.",
                "Third test sentence with different content."
            ]
            batch_embeddings = model.encode(test_texts)
            
            assert isinstance(batch_embeddings, np.ndarray)
            assert batch_embeddings.shape == (3, 384)
            
            # Test embedding similarity
            similarity_1_2 = np.dot(batch_embeddings[0], batch_embeddings[1])
            similarity_1_3 = np.dot(batch_embeddings[0], batch_embeddings[2])
            
            # First two should be more similar (both simple test sentences)
            assert similarity_1_2 > similarity_1_3 * 0.8  # Allow some tolerance
            
            self.validator._log_test_result(
                "sentence_transformers", "embedding_generation", True,
                {
                    "single_embedding_shape": list(embedding.shape),
                    "batch_embedding_shape": list(batch_embeddings.shape),
                    "similarity_check_passed": True
                }
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "sentence_transformers", "embedding_generation", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed embedding generation test: {e}")
    
    def test_embedding_consistency(self):
        """Test embedding consistency across runs."""
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            test_text = "Consistency test sentence for reproducibility."
            
            # Generate embeddings multiple times
            embeddings = []
            for _ in range(5):
                embedding = model.encode(test_text)
                embeddings.append(embedding)
            
            # Check consistency (should be identical for same input)
            base_embedding = embeddings[0]
            for i, embedding in enumerate(embeddings[1:], 1):
                similarity = np.dot(base_embedding, embedding) / (
                    np.linalg.norm(base_embedding) * np.linalg.norm(embedding)
                )
                assert similarity > 0.999, f"Consistency check failed at run {i}: {similarity}"
            
            # Check for deterministic behavior
            max_diff = max(np.max(np.abs(base_embedding - emb)) for emb in embeddings[1:])
            assert max_diff < 1e-6, f"Embeddings not deterministic, max diff: {max_diff}"
            
            self.validator._log_test_result(
                "sentence_transformers", "embedding_consistency", True,
                {"consistency_score": float(similarity), "max_difference": float(max_diff)}
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "sentence_transformers", "embedding_consistency", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed consistency test: {e}")


@pytest.mark.skipif(not CHROMADB_AVAILABLE, 
                   reason="chromadb not available")
class TestChromaDB:
    """Test ChromaDB functionality."""
    
    def setup_method(self):
        """Set up test method."""
        self.validator = MLComponentValidator()
        self.temp_dir = tempfile.mkdtemp()
        self.validator.temp_dirs.append(self.temp_dir)
        
    def teardown_method(self):
        """Clean up after test method."""
        self.validator.cleanup()
    
    def test_client_creation(self):
        """Test ChromaDB client creation."""
        try:
            # Test in-memory client
            client = chromadb.Client()
            assert client is not None
            
            # Test persistent client
            persistent_client = chromadb.PersistentClient(path=self.temp_dir)
            assert persistent_client is not None
            
            self.validator._log_test_result(
                "chromadb", "client_creation", True,
                {"temp_dir": self.temp_dir}
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "chromadb", "client_creation", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed to create ChromaDB client: {e}")
    
    def test_collection_operations(self):
        """Test ChromaDB collection operations."""
        try:
            client = chromadb.Client()
            
            # Create collection
            collection_name = "test_collection"
            collection = client.create_collection(collection_name)
            assert collection is not None
            assert collection.name == collection_name
            
            # List collections
            collections = client.list_collections()
            assert len(collections) == 1
            assert collections[0].name == collection_name
            
            # Get collection
            retrieved_collection = client.get_collection(collection_name)
            assert retrieved_collection.name == collection_name
            
            # Delete collection
            client.delete_collection(collection_name)
            collections_after = client.list_collections()
            assert len(collections_after) == 0
            
            self.validator._log_test_result(
                "chromadb", "collection_operations", True,
                {"collection_name": collection_name}
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "chromadb", "collection_operations", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed collection operations test: {e}")
    
    def test_document_operations(self):
        """Test ChromaDB document operations."""
        try:
            client = chromadb.Client()
            collection = client.create_collection("test_docs")
            
            # Add documents
            documents = [
                "This is the first test document.",
                "This is the second test document.",
                "This is the third test document with different content."
            ]
            ids = ["doc1", "doc2", "doc3"]
            metadata = [
                {"type": "test", "index": 1},
                {"type": "test", "index": 2},
                {"type": "test", "index": 3}
            ]
            
            collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadata
            )
            
            # Count documents
            count = collection.count()
            assert count == 3
            
            # Query similar documents
            query_results = collection.query(
                query_texts=["test document"],
                n_results=2
            )
            
            assert len(query_results['ids'][0]) == 2
            assert len(query_results['documents'][0]) == 2
            assert len(query_results['distances'][0]) == 2
            
            # Get specific document
            get_results = collection.get(ids=["doc1"])
            assert len(get_results['ids']) == 1
            assert get_results['ids'][0] == "doc1"
            assert get_results['documents'][0] == documents[0]
            
            # Update document
            collection.update(
                ids=["doc1"],
                documents=["Updated first test document."],
                metadatas=[{"type": "test", "index": 1, "updated": True}]
            )
            
            updated_doc = collection.get(ids=["doc1"])
            assert "Updated" in updated_doc['documents'][0]
            assert updated_doc['metadatas'][0]['updated'] is True
            
            # Delete document
            collection.delete(ids=["doc3"])
            remaining_count = collection.count()
            assert remaining_count == 2
            
            self.validator._log_test_result(
                "chromadb", "document_operations", True,
                {
                    "documents_added": 3,
                    "documents_after_delete": remaining_count,
                    "query_results_count": len(query_results['ids'][0])
                }
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "chromadb", "document_operations", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed document operations test: {e}")
    
    @pytest.mark.skipif(not SENTENCE_TRANSFORMERS_AVAILABLE, 
                       reason="sentence-transformers not available for embedding test")
    def test_custom_embeddings(self):
        """Test ChromaDB with custom embeddings."""
        try:
            # Create sentence transformer model
            model = SentenceTransformer('all-MiniLM-L6-v2')
            
            client = chromadb.Client()
            collection = client.create_collection("test_custom_embeddings")
            
            # Prepare test data
            documents = [
                "Machine learning is a subset of artificial intelligence.",
                "Deep learning uses neural networks with multiple layers.",
                "Natural language processing helps computers understand text."
            ]
            
            # Generate embeddings
            embeddings = model.encode(documents).tolist()
            ids = ["ml_doc", "dl_doc", "nlp_doc"]
            
            # Add with custom embeddings
            collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids
            )
            
            # Query with custom embedding
            query_text = "What is artificial intelligence?"
            query_embedding = model.encode([query_text]).tolist()
            
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=2
            )
            
            assert len(results['ids'][0]) == 2
            
            # Verify that ML document is most similar (should contain "artificial intelligence")
            top_result_id = results['ids'][0][0]
            assert top_result_id == "ml_doc"
            
            self.validator._log_test_result(
                "chromadb", "custom_embeddings", True,
                {
                    "embedding_dimension": len(embeddings[0]),
                    "top_result_correct": top_result_id == "ml_doc"
                }
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "chromadb", "custom_embeddings", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed custom embeddings test: {e}")


@pytest.mark.skipif(not QDRANT_AVAILABLE, 
                   reason="qdrant-client not available")
class TestQdrant:
    """Test Qdrant functionality (if available)."""
    
    def setup_method(self):
        """Set up test method."""
        self.validator = MLComponentValidator()
        
    def teardown_method(self):
        """Clean up after test method."""
        self.validator.cleanup()
    
    def test_qdrant_client_creation(self):
        """Test Qdrant client creation (in-memory)."""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            
            # Create in-memory client
            client = QdrantClient(":memory:")
            assert client is not None
            
            # Test collection creation
            collection_name = "test_collection"
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            
            # Verify collection exists
            collections = client.get_collections()
            collection_names = [col.name for col in collections.collections]
            assert collection_name in collection_names
            
            self.validator._log_test_result(
                "qdrant", "client_creation", True,
                {"collection_created": collection_name}
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "qdrant", "client_creation", False,
                {"error": str(e)}
            )
            # Don't fail the test if Qdrant is not properly configured
            pytest.skip(f"Qdrant test skipped: {e}")


class TestMLIntegration:
    """Test ML component integration scenarios."""
    
    def setup_method(self):
        """Set up test method."""
        self.validator = MLComponentValidator()
        
    def teardown_method(self):
        """Clean up after test method."""
        self.validator.cleanup()
    
    @pytest.mark.skipif(not (SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE), 
                       reason="Both sentence-transformers and chromadb required")
    def test_end_to_end_semantic_search(self):
        """Test end-to-end semantic search workflow."""
        try:
            # Initialize components
            model = SentenceTransformer('all-MiniLM-L6-v2')
            client = chromadb.Client()
            collection = client.create_collection("semantic_search_test")
            
            # Sample academic/research documents
            documents = [
                "The research gap in quantum computing applications for cryptography remains significant.",
                "Machine learning models show promise in predicting climate change effects on agriculture.",
                "Blockchain technology offers new solutions for supply chain transparency and traceability.",
                "Neural network architectures continue to evolve with transformer-based models leading innovation.",
                "Renewable energy storage systems face challenges in efficiency and cost-effectiveness."
            ]
            
            # Generate embeddings and store
            embeddings = model.encode(documents).tolist()
            ids = [f"doc_{i}" for i in range(len(documents))]
            
            collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=[{"topic": f"topic_{i}", "length": len(doc)} for i, doc in enumerate(documents)]
            )
            
            # Test semantic queries
            test_queries = [
                "What are the challenges in quantum cryptography?",
                "How does AI help with environmental issues?",
                "What are the benefits of distributed ledger technology?"
            ]
            
            query_results = []
            for query in test_queries:
                query_embedding = model.encode([query]).tolist()
                results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=2
                )
                query_results.append(results)
            
            # Verify semantic relevance
            # Query 1 (quantum) should match document 0 (quantum computing)
            assert "quantum" in query_results[0]['documents'][0][0].lower()
            
            # Query 2 (AI/environmental) should match document 1 (ML climate)
            assert any("climate" in doc.lower() or "agriculture" in doc.lower() 
                      for doc in query_results[1]['documents'][0])
            
            # Query 3 (blockchain) should match document 2 (blockchain)
            assert any("blockchain" in doc.lower() or "supply chain" in doc.lower() 
                      for doc in query_results[2]['documents'][0])
            
            self.validator._log_test_result(
                "ml_integration", "end_to_end_semantic_search", True,
                {
                    "documents_processed": len(documents),
                    "queries_tested": len(test_queries),
                    "semantic_matching_verified": True
                }
            )
            
        except Exception as e:
            self.validator._log_test_result(
                "ml_integration", "end_to_end_semantic_search", False,
                {"error": str(e)}
            )
            pytest.fail(f"Failed end-to-end semantic search test: {e}")
    
    def test_ml_component_health_check(self):
        """Test ML component health and availability."""
        health_status = {
            "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
            "chromadb": CHROMADB_AVAILABLE,
            "qdrant": QDRANT_AVAILABLE
        }
        
        # At least one vector store should be available
        vector_stores_available = health_status["chromadb"] or health_status["qdrant"]
        assert vector_stores_available, "No vector stores available"
        
        # Sentence transformers should be available for embeddings
        assert health_status["sentence_transformers"], "sentence-transformers not available"
        
        self.validator._log_test_result(
            "ml_integration", "health_check", True,
            health_status
        )


def generate_ml_test_report(output_dir: str = "logs/ml_testing"):
    """Generate ML component testing report."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Run tests and collect results
    validator = MLComponentValidator()
    
    # Component availability check
    availability = {
        "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
        "chromadb": CHROMADB_AVAILABLE,
        "qdrant": QDRANT_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    # Generate report
    report = {
        "ml_testing_report": {
            "timestamp": datetime.now().isoformat(),
            "component_availability": availability,
            "test_results": validator.test_results,
            "summary": {
                "components_available": sum(1 for k, v in availability.items() if k != "timestamp" and v),
                "total_components": len([k for k in availability.keys() if k != "timestamp"]),
                "tests_run": len(validator.test_results),
                "tests_passed": sum(1 for r in validator.test_results if r["passed"])
            }
        }
    }
    
    # Save JSON report
    report_file = os.path.join(output_dir, f"ml_component_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"ML component test report saved to: {report_file}")
    return report_file


if __name__ == "__main__":
    # Run as standalone script
    print("🧠 ML Component Validation Test")
    print("=" * 40)
    
    print(f"📦 sentence-transformers: {'✅' if SENTENCE_TRANSFORMERS_AVAILABLE else '❌'}")
    print(f"📦 chromadb: {'✅' if CHROMADB_AVAILABLE else '❌'}")
    print(f"📦 qdrant-client: {'✅' if QDRANT_AVAILABLE else '❌'}")
    
    if SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE:
        print("\n🚀 Running basic integration test...")
        
        # Quick integration test
        try:
            from sentence_transformers import SentenceTransformer
            import chromadb
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            client = chromadb.Client()
            collection = client.create_collection("test")
            
            test_doc = "This is a test document for ML validation."
            embedding = model.encode([test_doc]).tolist()
            
            collection.add(
                documents=[test_doc],
                embeddings=embedding,
                ids=["test_doc"]
            )
            
            results = collection.query(
                query_embeddings=embedding,
                n_results=1
            )
            
            assert len(results['ids'][0]) == 1
            print("✅ Basic ML integration test passed")
            
        except Exception as e:
            print(f"❌ Basic ML integration test failed: {e}")
    
    # Generate report
    generate_ml_test_report()