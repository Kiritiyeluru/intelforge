#!/usr/bin/env python3
"""
Academic Research Tools Integration Testing
Tests for academic research functionality, query processing, and research gap detection.
"""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

# Check for IntelForge components
try:
    from scripts.semantic_crawler import SemanticCrawler

    SEMANTIC_CRAWLER_AVAILABLE = True
except ImportError:
    SEMANTIC_CRAWLER_AVAILABLE = False

try:
    from scripts.enhanced_research_gap_detector import \
        EnhancedResearchGapDetector

    RESEARCH_GAP_DETECTOR_AVAILABLE = True
except ImportError:
    RESEARCH_GAP_DETECTOR_AVAILABLE = False

# Check for ML dependencies
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


class AcademicToolsIntegrationTester:
    """Academic tools integration testing framework."""

    def __init__(self):
        """Initialize academic tools integration tester."""
        self.project_root = Path(__file__).parent.parent.parent
        self.temp_dirs: List[str] = []
        self.test_results: List[Dict[str, Any]] = []

        # Academic test queries
        self.test_queries = [
            {
                "query": "machine learning applications in healthcare",
                "expected_domains": ["healthcare", "machine learning", "AI"],
                "min_results": 3,
            },
            {
                "query": "climate change impact on agriculture",
                "expected_domains": ["climate", "agriculture", "environment"],
                "min_results": 2,
            },
            {
                "query": "quantum computing cryptography research",
                "expected_domains": ["quantum", "cryptography", "security"],
                "min_results": 2,
            },
        ]

        # Mock academic URLs for testing
        self.mock_academic_urls = [
            "https://arxiv.org/abs/2301.00001",
            "https://pubmed.ncbi.nlm.nih.gov/12345678",
            "https://ieeexplore.ieee.org/document/9876543",
            "https://www.nature.com/articles/s41586-023-12345-6",
            "https://scholar.google.com/citations?view_op=view_citation&hl=en&user=test",
        ]

        # Mock academic content
        self.mock_academic_content = {
            "https://arxiv.org/abs/2301.00001": {
                "title": "Advanced Machine Learning Techniques for Healthcare Diagnostics",
                "abstract": "This paper presents novel machine learning approaches for improving healthcare diagnostic accuracy through deep learning and neural networks.",
                "content": "Machine learning has shown significant promise in healthcare applications, particularly in diagnostic imaging and predictive analytics. Our research demonstrates improved accuracy in medical diagnosis through advanced neural network architectures.",
            },
            "https://pubmed.ncbi.nlm.nih.gov/12345678": {
                "title": "Climate Change Effects on Agricultural Productivity",
                "abstract": "Study of climate change impacts on global agricultural systems and crop yields.",
                "content": "Climate change poses significant challenges to agricultural productivity worldwide. Rising temperatures and changing precipitation patterns affect crop yields and food security.",
            },
            "https://ieeexplore.ieee.org/document/9876543": {
                "title": "Quantum Cryptography: Security in the Quantum Era",
                "abstract": "Analysis of quantum computing implications for cryptographic security and new quantum-resistant algorithms.",
                "content": "Quantum computing presents both opportunities and challenges for cryptographic security. This research explores quantum-resistant cryptographic protocols.",
            },
        }

    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def _log_test_result(
        self,
        component: str,
        test_name: str,
        passed: bool,
        details: Dict[str, Any] = None,
    ):
        """Log test result for reporting."""
        result = {
            "component": component,
            "test_name": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }
        self.test_results.append(result)


@pytest.mark.skipif(
    not SEMANTIC_CRAWLER_AVAILABLE, reason="SemanticCrawler not available"
)
class TestSemanticCrawlerIntegration:
    """Test SemanticCrawler integration."""

    def setup_method(self):
        """Set up test method."""
        self.tester = AcademicToolsIntegrationTester()
        self.temp_dir = tempfile.mkdtemp()
        self.tester.temp_dirs.append(self.temp_dir)

    def teardown_method(self):
        """Clean up after test method."""
        self.tester.cleanup()

    def test_semantic_crawler_initialization(self):
        """Test SemanticCrawler initialization."""
        try:
            # Mock the storage paths to use temp directory
            with patch.dict(
                os.environ,
                {
                    "CHROMA_STORAGE_PATH": os.path.join(self.temp_dir, "chroma"),
                    "QDRANT_STORAGE_PATH": os.path.join(self.temp_dir, "qdrant"),
                },
            ):
                crawler = SemanticCrawler()
                assert crawler is not None

                # Check if required attributes exist
                required_attrs = ["config", "vector_store"]
                for attr in required_attrs:
                    assert hasattr(crawler, attr), f"Missing attribute: {attr}"

                self.tester._log_test_result(
                    "semantic_crawler",
                    "initialization",
                    True,
                    {"attributes_checked": required_attrs},
                )

        except Exception as e:
            self.tester._log_test_result(
                "semantic_crawler", "initialization", False, {"error": str(e)}
            )
            pytest.fail(f"SemanticCrawler initialization failed: {e}")

    def test_semantic_crawler_url_validation(self):
        """Test SemanticCrawler URL validation."""
        try:
            with patch.dict(
                os.environ,
                {
                    "CHROMA_STORAGE_PATH": os.path.join(self.temp_dir, "chroma"),
                    "QDRANT_STORAGE_PATH": os.path.join(self.temp_dir, "qdrant"),
                },
            ):
                crawler = SemanticCrawler()

                # Test valid academic URLs
                valid_urls = self.tester.mock_academic_urls
                for url in valid_urls:
                    # Assume crawler has a method to validate URLs
                    if hasattr(crawler, "is_valid_url"):
                        is_valid = crawler.is_valid_url(url)
                        assert is_valid, f"URL should be valid: {url}"

                # Test invalid URLs
                invalid_urls = ["not_a_url", "http://", "https://", "ftp://invalid.com"]

                for url in invalid_urls:
                    if hasattr(crawler, "is_valid_url"):
                        is_valid = crawler.is_valid_url(url)
                        assert not is_valid, f"URL should be invalid: {url}"

                self.tester._log_test_result(
                    "semantic_crawler",
                    "url_validation",
                    True,
                    {
                        "valid_urls_tested": len(valid_urls),
                        "invalid_urls_tested": len(invalid_urls),
                    },
                )

        except Exception as e:
            self.tester._log_test_result(
                "semantic_crawler", "url_validation", False, {"error": str(e)}
            )
            pytest.fail(f"URL validation test failed: {e}")

    @patch("requests.get")
    def test_semantic_crawler_content_extraction(self, mock_get):
        """Test SemanticCrawler content extraction with mocked responses."""
        try:
            # Mock HTTP responses
            def mock_response(url):
                mock_resp = Mock()
                if url in self.tester.mock_academic_content:
                    content_data = self.tester.mock_academic_content[url]
                    mock_resp.status_code = 200
                    mock_resp.text = f"""
                    <html>
                        <head><title>{content_data['title']}</title></head>
                        <body>
                            <h1>{content_data['title']}</h1>
                            <div class="abstract">{content_data['abstract']}</div>
                            <div class="content">{content_data['content']}</div>
                        </body>
                    </html>
                    """
                    mock_resp.headers = {"content-type": "text/html"}
                else:
                    mock_resp.status_code = 404
                    mock_resp.text = "Not Found"
                return mock_resp

            mock_get.side_effect = lambda url, **kwargs: mock_response(url)

            with patch.dict(
                os.environ,
                {
                    "CHROMA_STORAGE_PATH": os.path.join(self.temp_dir, "chroma"),
                    "QDRANT_STORAGE_PATH": os.path.join(self.temp_dir, "qdrant"),
                },
            ):
                crawler = SemanticCrawler()

                # Test content extraction for each mock URL
                extracted_contents = []
                for url in self.tester.mock_academic_urls[:3]:  # Test first 3
                    if hasattr(crawler, "extract_content"):
                        content = crawler.extract_content(url)
                        if content:
                            extracted_contents.append(content)

                            # Verify content quality
                            expected_content = self.tester.mock_academic_content[url]
                            assert expected_content["title"].lower() in content.lower()

                self.tester._log_test_result(
                    "semantic_crawler",
                    "content_extraction",
                    True,
                    {
                        "urls_tested": 3,
                        "successful_extractions": len(extracted_contents),
                    },
                )

        except Exception as e:
            self.tester._log_test_result(
                "semantic_crawler", "content_extraction", False, {"error": str(e)}
            )
            pytest.fail(f"Content extraction test failed: {e}")


@pytest.mark.skipif(
    not RESEARCH_GAP_DETECTOR_AVAILABLE,
    reason="EnhancedResearchGapDetector not available",
)
class TestResearchGapDetectorIntegration:
    """Test EnhancedResearchGapDetector integration."""

    def setup_method(self):
        """Set up test method."""
        self.tester = AcademicToolsIntegrationTester()

    def teardown_method(self):
        """Clean up after test method."""
        self.tester.cleanup()

    def test_research_gap_detector_initialization(self):
        """Test EnhancedResearchGapDetector initialization."""
        try:
            detector = EnhancedResearchGapDetector()
            assert detector is not None

            # Check if required methods exist
            required_methods = ["detect_gaps", "analyze_research_trends"]
            for method in required_methods:
                assert hasattr(detector, method), f"Missing method: {method}"

            self.tester._log_test_result(
                "research_gap_detector",
                "initialization",
                True,
                {"methods_checked": required_methods},
            )

        except Exception as e:
            self.tester._log_test_result(
                "research_gap_detector", "initialization", False, {"error": str(e)}
            )
            pytest.fail(f"EnhancedResearchGapDetector initialization failed: {e}")

    def test_research_gap_detection(self):
        """Test research gap detection functionality."""
        try:
            detector = EnhancedResearchGapDetector()

            # Test with academic content
            test_documents = [
                {
                    "title": "Machine Learning in Healthcare: Current Applications",
                    "content": "Current machine learning applications in healthcare focus on diagnostic imaging and patient monitoring. However, there are limited studies on preventive care applications.",
                },
                {
                    "title": "Deep Learning for Medical Diagnosis",
                    "content": "Deep learning shows promise for medical diagnosis, particularly in radiology. Further research is needed in rare disease detection and personalized treatment plans.",
                },
                {
                    "title": "AI Ethics in Healthcare",
                    "content": "AI ethics in healthcare requires attention to bias, privacy, and transparency. More research is needed on algorithmic fairness in medical AI systems.",
                },
            ]

            # Test gap detection
            if hasattr(detector, "detect_gaps"):
                gaps = detector.detect_gaps(test_documents)

                # Verify gaps were detected
                assert isinstance(
                    gaps, (list, dict)
                ), "Gaps should be returned as list or dict"

                if isinstance(gaps, list):
                    assert len(gaps) > 0, "Should detect some research gaps"
                elif isinstance(gaps, dict):
                    assert len(gaps.keys()) > 0, "Should detect some research areas"

                self.tester._log_test_result(
                    "research_gap_detector",
                    "gap_detection",
                    True,
                    {
                        "documents_analyzed": len(test_documents),
                        "gaps_detected": (
                            len(gaps) if isinstance(gaps, list) else len(gaps.keys())
                        ),
                    },
                )
            else:
                # Skip if method doesn't exist
                self.tester._log_test_result(
                    "research_gap_detector",
                    "gap_detection",
                    True,
                    {"note": "detect_gaps method not available, test skipped"},
                )

        except Exception as e:
            self.tester._log_test_result(
                "research_gap_detector", "gap_detection", False, {"error": str(e)}
            )
            pytest.fail(f"Research gap detection test failed: {e}")


@pytest.mark.skipif(
    not (SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE),
    reason="Both sentence-transformers and chromadb required",
)
class TestAcademicWorkflowIntegration:
    """Test complete academic research workflow integration."""

    def setup_method(self):
        """Set up test method."""
        self.tester = AcademicToolsIntegrationTester()
        self.temp_dir = tempfile.mkdtemp()
        self.tester.temp_dirs.append(self.temp_dir)

    def teardown_method(self):
        """Clean up after test method."""
        self.tester.cleanup()

    def test_academic_query_processing_workflow(self):
        """Test complete academic query processing workflow."""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            # Initialize components
            model = SentenceTransformer("all-MiniLM-L6-v2")
            client = chromadb.Client()
            collection = client.create_collection("academic_test")

            # Simulate academic document processing
            academic_documents = [
                "Machine learning applications in healthcare diagnostics show promising results for early disease detection and personalized treatment plans.",
                "Climate change research indicates significant impacts on agricultural productivity, requiring adaptive farming techniques and crop development.",
                "Quantum computing advances in cryptography present both opportunities for enhanced security and challenges for current encryption methods.",
                "Natural language processing techniques are being applied to academic literature analysis for research gap identification and trend analysis.",
                "Renewable energy storage solutions face technical and economic challenges that require interdisciplinary research approaches.",
            ]

            # Process documents (simulate academic content processing)
            embeddings = model.encode(academic_documents).tolist()
            ids = [f"academic_doc_{i}" for i in range(len(academic_documents))]

            # Store in vector database
            collection.add(
                documents=academic_documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=[
                    {"domain": "healthcare", "type": "research"},
                    {"domain": "climate", "type": "research"},
                    {"domain": "quantum", "type": "research"},
                    {"domain": "nlp", "type": "research"},
                    {"domain": "energy", "type": "research"},
                ],
            )

            # Test academic queries
            successful_queries = 0
            for test_query in self.tester.test_queries:
                query_text = test_query["query"]
                expected_domains = test_query["expected_domains"]
                min_results = test_query["min_results"]

                # Generate query embedding
                query_embedding = model.encode([query_text]).tolist()

                # Search for relevant documents
                results = collection.query(
                    query_embeddings=query_embedding,
                    n_results=min_results,
                    include=["documents", "metadatas", "distances"],
                )

                # Verify results
                if len(results["ids"][0]) >= min_results:
                    # Check if any expected domain appears in results
                    found_domains = [meta["domain"] for meta in results["metadatas"][0]]
                    domain_match = any(
                        domain in " ".join(found_domains) for domain in expected_domains
                    )

                    if domain_match:
                        successful_queries += 1

            # Test should pass if most queries return relevant results
            success_rate = successful_queries / len(self.tester.test_queries)
            workflow_success = success_rate >= 0.6  # At least 60% success rate

            self.tester._log_test_result(
                "academic_workflow",
                "query_processing",
                workflow_success,
                {
                    "total_queries": len(self.tester.test_queries),
                    "successful_queries": successful_queries,
                    "success_rate": success_rate,
                    "documents_processed": len(academic_documents),
                },
            )

            assert (
                workflow_success
            ), f"Academic workflow success rate too low: {success_rate:.2f}"

        except Exception as e:
            self.tester._log_test_result(
                "academic_workflow", "query_processing", False, {"error": str(e)}
            )
            pytest.fail(f"Academic workflow integration test failed: {e}")

    def test_research_domain_classification(self):
        """Test research domain classification accuracy."""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("all-MiniLM-L6-v2")
            client = chromadb.Client()
            collection = client.create_collection("domain_classification_test")

            # Documents with clear domain labels
            domain_documents = {
                "healthcare": [
                    "Medical AI systems for patient diagnosis and treatment recommendations.",
                    "Healthcare data analytics for epidemic prediction and prevention.",
                ],
                "climate": [
                    "Climate modeling for predicting environmental changes and impacts.",
                    "Sustainable development strategies for climate change mitigation.",
                ],
                "technology": [
                    "Artificial intelligence advances in computer vision and robotics.",
                    "Cybersecurity protocols for protecting digital infrastructure.",
                ],
            }

            # Add documents to collection
            all_docs = []
            all_embeddings = []
            all_ids = []
            all_metadata = []

            for domain, docs in domain_documents.items():
                for i, doc in enumerate(docs):
                    all_docs.append(doc)
                    all_ids.append(f"{domain}_doc_{i}")
                    all_metadata.append({"domain": domain})

            all_embeddings = model.encode(all_docs).tolist()

            collection.add(
                documents=all_docs,
                embeddings=all_embeddings,
                ids=all_ids,
                metadatas=all_metadata,
            )

            # Test domain-specific queries
            domain_queries = {
                "healthcare": "What are the latest developments in medical AI?",
                "climate": "How can we address environmental sustainability?",
                "technology": "What are the advances in artificial intelligence?",
            }

            correct_classifications = 0
            total_classifications = 0

            for expected_domain, query in domain_queries.items():
                query_embedding = model.encode([query]).tolist()

                results = collection.query(
                    query_embeddings=query_embedding, n_results=1, include=["metadatas"]
                )

                if results["metadatas"] and len(results["metadatas"][0]) > 0:
                    predicted_domain = results["metadatas"][0][0]["domain"]
                    if predicted_domain == expected_domain:
                        correct_classifications += 1
                    total_classifications += 1

            classification_accuracy = (
                correct_classifications / total_classifications
                if total_classifications > 0
                else 0
            )

            self.tester._log_test_result(
                "academic_workflow",
                "domain_classification",
                True,
                {
                    "total_classifications": total_classifications,
                    "correct_classifications": correct_classifications,
                    "accuracy": classification_accuracy,
                },
            )

            # Expect reasonable classification accuracy
            assert (
                classification_accuracy >= 0.5
            ), f"Classification accuracy too low: {classification_accuracy:.2f}"

        except Exception as e:
            self.tester._log_test_result(
                "academic_workflow", "domain_classification", False, {"error": str(e)}
            )
            pytest.fail(f"Domain classification test failed: {e}")


class TestAcademicToolsHealthCheck:
    """Health check for academic tools availability and integration."""

    def setup_method(self):
        """Set up test method."""
        self.tester = AcademicToolsIntegrationTester()

    def teardown_method(self):
        """Clean up after test method."""
        self.tester.cleanup()

    def test_academic_components_availability(self):
        """Test availability of academic research components."""
        components_status = {
            "semantic_crawler": SEMANTIC_CRAWLER_AVAILABLE,
            "research_gap_detector": RESEARCH_GAP_DETECTOR_AVAILABLE,
            "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
            "chromadb": CHROMADB_AVAILABLE,
        }

        # Count available components
        available_count = sum(components_status.values())
        total_count = len(components_status)

        # At least core ML components should be available
        core_available = (
            components_status["sentence_transformers"] and components_status["chromadb"]
        )

        self.tester._log_test_result(
            "academic_tools",
            "health_check",
            core_available,
            {
                "components_status": components_status,
                "available_count": available_count,
                "total_count": total_count,
                "availability_rate": available_count / total_count,
            },
        )

        assert (
            core_available
        ), "Core ML components (sentence-transformers + chromadb) must be available"


def generate_academic_integration_report(output_dir: str = "logs/academic_testing"):
    """Generate academic tools integration testing report."""
    os.makedirs(output_dir, exist_ok=True)

    tester = AcademicToolsIntegrationTester()

    # Component availability
    availability = {
        "semantic_crawler": SEMANTIC_CRAWLER_AVAILABLE,
        "research_gap_detector": RESEARCH_GAP_DETECTOR_AVAILABLE,
        "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
        "chromadb": CHROMADB_AVAILABLE,
        "timestamp": datetime.now().isoformat(),
    }

    # Generate report
    report = {
        "academic_integration_report": {
            "timestamp": datetime.now().isoformat(),
            "component_availability": availability,
            "test_queries": tester.test_queries,
            "mock_urls": tester.mock_academic_urls,
            "test_results": tester.test_results,
            "summary": {
                "components_available": sum(
                    1 for k, v in availability.items() if k != "timestamp" and v
                ),
                "total_components": len(
                    [k for k in availability.keys() if k != "timestamp"]
                ),
                "tests_run": len(tester.test_results),
                "tests_passed": sum(1 for r in tester.test_results if r["passed"]),
            },
        }
    }

    # Save JSON report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(
        output_dir, f"academic_integration_report_{timestamp}.json"
    )
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Academic integration test report saved to: {report_file}")
    return report_file


if __name__ == "__main__":
    # Run as standalone script
    print("🎓 Academic Tools Integration Testing")
    print("=" * 50)

    print("📦 Component Availability:")
    print(f"   SemanticCrawler: {'✅' if SEMANTIC_CRAWLER_AVAILABLE else '❌'}")
    print(
        f"   ResearchGapDetector: {'✅' if RESEARCH_GAP_DETECTOR_AVAILABLE else '❌'}"
    )
    print(
        f"   sentence-transformers: {'✅' if SENTENCE_TRANSFORMERS_AVAILABLE else '❌'}"
    )
    print(f"   chromadb: {'✅' if CHROMADB_AVAILABLE else '❌'}")

    # Generate report
    report_file = generate_academic_integration_report()

    # Basic integration test if core components available
    if SENTENCE_TRANSFORMERS_AVAILABLE and CHROMADB_AVAILABLE:
        print("\n🚀 Running basic academic integration test...")

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("all-MiniLM-L6-v2")
            client = chromadb.Client()
            collection = client.create_collection("basic_academic_test")

            # Test academic query processing
            academic_doc = "Machine learning applications in healthcare show promising results for diagnostic accuracy."
            embedding = model.encode([academic_doc]).tolist()

            collection.add(
                documents=[academic_doc],
                embeddings=embedding,
                ids=["test_academic_doc"],
                metadatas=[{"domain": "healthcare"}],
            )

            # Test query
            query = "What are AI applications in medical diagnosis?"
            query_embedding = model.encode([query]).tolist()

            results = collection.query(query_embeddings=query_embedding, n_results=1)

            assert len(results["ids"][0]) == 1
            print("✅ Basic academic integration test passed")

        except Exception as e:
            print(f"❌ Basic academic integration test failed: {e}")
    else:
        print("⚠️  Core components not available for integration test")
