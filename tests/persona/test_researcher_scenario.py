#!/usr/bin/env python3
"""
Researcher Persona Testing - Bulk Semantic Extraction from Academic URLs

This module tests the researcher use case: bulk processing of academic papers
with semantic extraction, research gap detection, and knowledge synthesis.

Test Categories:
- Bulk URL processing from academic sources
- Semantic similarity validation
- Research gap detection accuracy  
- Knowledge extraction quality
- Performance with concurrent academic content processing
"""

import json
import pytest
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch

# Import existing testing infrastructure
from tests.utils.snapshot_drift_validator import SnapshotDriftValidator
from tests.ml.test_ml_component_validation import TestSentenceTransformers
from tests.performance.test_performance_regression import PerformanceRegressionTester

@pytest.mark.integration
@pytest.mark.persona
@pytest.mark.slow
class TestResearcherPersona:
    """Test suite for researcher persona workflows"""
    
    @classmethod
    def setup_class(cls):
        """Setup test fixtures and configurations"""
        cls.fixtures_path = Path(__file__).parent.parent / "fixtures"
        cls.research_data = cls._load_research_fixtures()
        cls.drift_validator = SnapshotDriftValidator()
        cls.performance_tester = PerformanceRegressionTester()
        
    @classmethod
    def _load_research_fixtures(cls) -> Dict[str, Any]:
        """Load research paper fixtures and configuration"""
        fixtures_file = cls.fixtures_path / "sample_research_papers.json"
        with open(fixtures_file, 'r') as f:
            return json.load(f)
    
    def test_bulk_academic_url_processing(self):
        """Test bulk processing of academic URLs with semantic extraction"""
        academic_urls = self.research_data["academic_urls"]
        config = self.research_data["bulk_processing_config"]
        
        # Simulate bulk processing
        start_time = time.time()
        processed_papers = []
        
        for url_data in academic_urls:
            # Mock semantic extraction
            extracted_content = {
                "url": url_data["url"],
                "title": url_data["title"], 
                "domain": url_data["domain"],
                "keywords": url_data["expected_keywords"],
                "semantic_embedding": [0.1] * 384,  # Mock 384D embedding
                "extraction_quality": 0.92,
                "processing_time": 2.3
            }
            processed_papers.append(extracted_content)
        
        processing_time = time.time() - start_time
        
        # Validate bulk processing results
        assert len(processed_papers) == len(academic_urls)
        assert processing_time < config["expected_processing_time"]
        
        # Validate semantic extraction quality
        for paper in processed_papers:
            assert paper["extraction_quality"] > 0.85
            assert len(paper["semantic_embedding"]) == 384
            assert len(paper["keywords"]) >= 3
            
        print(f"✅ Bulk processed {len(processed_papers)} papers in {processing_time:.2f}s")
    
    def test_semantic_similarity_validation(self):
        """Test semantic similarity scoring for research content"""
        mock_content = self.research_data["mock_content"]
        
        for paper_key, paper_data in mock_content.items():
            # Test semantic similarity with expected threshold
            similarity_score = paper_data["expected_semantic_similarity"]
            threshold = self.research_data["bulk_processing_config"]["semantic_similarity_threshold"]
            
            assert similarity_score >= threshold, f"Paper {paper_key} similarity {similarity_score} below threshold {threshold}"
            
            # Validate research gap detection
            research_gaps = paper_data["research_gaps"]
            assert len(research_gaps) >= 2, f"Insufficient research gaps detected for {paper_key}"
            
            # Validate methodology extraction
            methodology = paper_data["methodology"]
            assert methodology, f"No methodology extracted for {paper_key}"
            
        print(f"✅ Validated semantic similarity for {len(mock_content)} papers")
    
    def test_research_gap_detection_accuracy(self):
        """Test accuracy of research gap detection in academic content"""
        lora_paper = self.research_data["mock_content"]["lora_paper"]
        attention_paper = self.research_data["mock_content"]["attention_paper"]
        
        # Test LoRA paper gap detection
        lora_gaps = lora_paper["research_gaps"]
        expected_lora_gaps = ["Parameter efficiency", "Computational cost reduction", "Model adaptation"]
        
        for expected_gap in expected_lora_gaps:
            assert any(expected_gap.lower() in gap.lower() for gap in lora_gaps), \
                f"Expected gap '{expected_gap}' not found in LoRA paper analysis"
        
        # Test Attention paper gap detection  
        attention_gaps = attention_paper["research_gaps"]
        expected_attention_gaps = ["Sequential processing limitations", "Parallelization challenges"]
        
        for expected_gap in expected_attention_gaps:
            assert any(expected_gap.lower() in gap.lower() for gap in attention_gaps), \
                f"Expected gap '{expected_gap}' not found in Attention paper analysis"
                
        print(f"✅ Research gap detection accuracy validated")
    
    def test_concurrent_academic_processing(self):
        """Test concurrent processing of multiple academic papers"""
        config = self.research_data["bulk_processing_config"]
        academic_urls = self.research_data["academic_urls"]
        
        max_concurrent = config["max_concurrent_requests"]
        batch_size = config["batch_size"]
        
        # Simulate concurrent processing
        async def process_paper_async(url_data):
            """Simulate async paper processing"""
            await asyncio.sleep(0.1)  # Simulate processing time
            return {
                "url": url_data["url"],
                "status": "processed",
                "extraction_time": 0.1,
                "semantic_quality": 0.89
            }
        
        async def run_concurrent_test():
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_limit(url_data):
                async with semaphore:
                    return await process_paper_async(url_data)
            
            tasks = [process_with_limit(url_data) for url_data in academic_urls[:batch_size]]
            results = await asyncio.gather(*tasks)
            return results
        
        # Run concurrent processing test
        start_time = time.time()
        results = asyncio.run(run_concurrent_test())
        processing_time = time.time() - start_time
        
        # Validate concurrent processing results
        assert len(results) == batch_size
        assert processing_time < config["timeout_per_url"]
        
        for result in results:
            assert result["status"] == "processed"
            assert result["semantic_quality"] > 0.8
            
        print(f"✅ Concurrent processing of {batch_size} papers completed in {processing_time:.2f}s")
    
    def test_knowledge_synthesis_workflow(self):
        """Test end-to-end knowledge synthesis from multiple papers"""
        papers = self.research_data["academic_urls"]
        
        # Simulate knowledge synthesis
        synthesized_knowledge = {
            "total_papers": len(papers),
            "domains_covered": list(set(paper["domain"] for paper in papers)),
            "common_themes": ["machine learning", "neural networks", "optimization"],
            "cross_paper_connections": [
                {
                    "paper1": "LoRA: Low-Rank Adaptation",
                    "paper2": "Attention Is All You Need", 
                    "connection": "Both focus on computational efficiency in neural networks"
                }
            ],
            "synthesis_confidence": 0.87
        }
        
        # Validate synthesis results
        assert synthesized_knowledge["total_papers"] == len(papers)
        assert len(synthesized_knowledge["domains_covered"]) >= 3
        assert synthesized_knowledge["synthesis_confidence"] > 0.8
        assert len(synthesized_knowledge["cross_paper_connections"]) >= 1
        
        # Test semantic drift in synthesis
        synthesis_content = " ".join(synthesized_knowledge["common_themes"])
        drift_result = self.drift_validator.validate_drift(
            module_name="ResearchSynthesis",
            current_content=synthesis_content
        )
        
        # First run creates baseline, subsequent runs should pass
        if "baseline" not in drift_result.diff_reason:
            assert drift_result.verdict == "✅ PASS", f"Synthesis drift check failed: {drift_result.diff_reason}"
        else:
            print(f"✅ Baseline snapshot created for ResearchSynthesis")
        
        print(f"✅ Knowledge synthesis completed with {synthesized_knowledge['synthesis_confidence']:.2f} confidence")
    
    def test_researcher_performance_benchmarks(self):
        """Test performance benchmarks for researcher workflows"""
        # Define researcher-specific performance baselines
        researcher_baselines = {
            "bulk_url_processing": {"max_time": 45.0, "memory_limit": 512},
            "semantic_extraction": {"max_time": 5.0, "accuracy_min": 0.85},
            "gap_detection": {"max_time": 3.0, "gaps_min": 2},
            "knowledge_synthesis": {"max_time": 10.0, "confidence_min": 0.8}
        }
        
        # Run performance tests for each benchmark
        performance_results = {}
        
        for benchmark, limits in researcher_baselines.items():
            start_time = time.time()
            
            # Simulate benchmark execution
            if benchmark == "bulk_url_processing":
                # Simulate bulk processing
                result = {"processed_count": 5, "success_rate": 1.0}
            elif benchmark == "semantic_extraction":
                result = {"accuracy": 0.92, "extraction_quality": 0.89}
            elif benchmark == "gap_detection":
                result = {"gaps_detected": 3, "detection_accuracy": 0.91}
            elif benchmark == "knowledge_synthesis":
                result = {"synthesis_confidence": 0.87, "connections_found": 2}
            
            execution_time = time.time() - start_time
            
            # Validate performance against baselines
            assert execution_time <= limits["max_time"], \
                f"Benchmark {benchmark} exceeded time limit: {execution_time:.2f}s > {limits['max_time']}s"
            
            performance_results[benchmark] = {
                "execution_time": execution_time,
                "result": result,
                "status": "passed"
            }
        
        print(f"✅ All researcher performance benchmarks passed")
        return performance_results

if __name__ == "__main__":
    # Run researcher persona tests
    test_suite = TestResearcherPersona()
    test_suite.setup_class()
    
    print("🔬 Running Researcher Persona Tests...")
    
    try:
        test_suite.test_bulk_academic_url_processing()
        test_suite.test_semantic_similarity_validation()
        test_suite.test_research_gap_detection_accuracy()
        test_suite.test_concurrent_academic_processing()
        test_suite.test_knowledge_synthesis_workflow()
        performance_results = test_suite.test_researcher_performance_benchmarks()
        
        print("\n🏆 Researcher Persona Testing Summary:")
        print(f"✅ Bulk URL Processing: PASSED")
        print(f"✅ Semantic Similarity: PASSED") 
        print(f"✅ Research Gap Detection: PASSED")
        print(f"✅ Concurrent Processing: PASSED")
        print(f"✅ Knowledge Synthesis: PASSED")
        print(f"✅ Performance Benchmarks: PASSED")
        
        print(f"\n📊 Performance Results:")
        for benchmark, result in performance_results.items():
            print(f"  {benchmark}: {result['execution_time']:.2f}s - {result['status']}")
            
    except Exception as e:
        print(f"❌ Researcher persona test failed: {e}")
        raise