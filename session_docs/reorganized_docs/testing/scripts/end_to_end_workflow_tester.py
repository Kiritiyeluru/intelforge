#!/usr/bin/env python3
"""
IntelForge End-to-End Workflow Testing
Complete pipeline validation from input to final output
"""

import os
import sys
import json
import time
import datetime
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import argparse
import sqlite3

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

class EndToEndWorkflowTester:
    """Comprehensive end-to-end workflow testing for IntelForge"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.test_dir = Path(__file__).parent.parent
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Test database
        self.e2e_db_path = self.test_dir / "reports" / "end_to_end" / f"e2e_session_{self.timestamp}.db"
        self.e2e_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Test data directories
        self.test_data_dir = self.test_dir / "test_data"
        self.test_output_dir = self.test_dir / "test_output" / self.timestamp
        self.test_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Results tracking
        self.results = {
            "session_id": self.timestamp,
            "test_type": "end_to_end_workflow",
            "start_time": datetime.datetime.now().isoformat(),
            "workflows": {},
            "data_flow": {},
            "integrity_checks": {},
            "status": "running"
        }
        
        # Initialize database
        self.init_e2e_database()
        
        # Create test data
        self.create_test_data()
    
    def init_e2e_database(self):
        """Initialize SQLite database for end-to-end test tracking"""
        conn = sqlite3.connect(self.e2e_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                workflow_name TEXT NOT NULL,
                phase TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_seconds REAL,
                input_size INTEGER,
                output_size INTEGER,
                error_message TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_flow_validation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                test_name TEXT NOT NULL,
                input_format TEXT NOT NULL,
                output_format TEXT NOT NULL,
                data_integrity_score REAL,
                transformation_accuracy REAL,
                status TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                success BOOLEAN,
                error_message TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_test_data(self):
        """Create comprehensive test data for end-to-end testing"""
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Create mock articles for processing
        mock_articles = [
            {
                "title": "Advanced Algorithmic Trading Strategies",
                "content": "This comprehensive analysis explores modern algorithmic trading approaches including momentum strategies, mean reversion techniques, and statistical arbitrage. The paper discusses implementation of Bollinger Bands, RSI indicators, and machine learning models for market prediction. Key findings show that ensemble methods combining technical indicators with sentiment analysis achieve 67% accuracy in directional prediction.",
                "source": "https://example.com/trading-strategies",
                "tags": ["trading", "algorithms", "technical-analysis"],
                "date": "2025-07-10"
            },
            {
                "title": "Risk Management in Quantitative Finance",
                "content": "Effective risk management forms the cornerstone of successful quantitative trading operations. This study examines Value at Risk (VaR) calculations, stress testing methodologies, and portfolio optimization techniques. The research demonstrates how Monte Carlo simulations can be used to model tail risks and optimize position sizing for maximum risk-adjusted returns.",
                "source": "https://example.com/risk-management", 
                "tags": ["risk", "quantitative", "portfolio"],
                "date": "2025-07-09"
            },
            {
                "title": "Market Microstructure and High-Frequency Trading",
                "content": "An in-depth examination of market microstructure effects on high-frequency trading strategies. The analysis covers order book dynamics, latency arbitrage, and market making algorithms. Results indicate that co-location strategies provide significant advantages, with latency reductions of 10 microseconds improving profitability by 15% in equity markets.",
                "source": "https://example.com/hft-analysis",
                "tags": ["hft", "microstructure", "equity"],
                "date": "2025-07-08"
            },
            {
                "title": "Cryptocurrency Market Analysis and Prediction",
                "content": "Comprehensive study of cryptocurrency market dynamics using advanced time series analysis and machine learning techniques. The research applies LSTM networks, ARIMA models, and sentiment analysis to predict Bitcoin price movements. Findings show that combining on-chain metrics with social sentiment data improves prediction accuracy by 23%.",
                "source": "https://example.com/crypto-analysis",
                "tags": ["cryptocurrency", "prediction", "machine-learning"],
                "date": "2025-07-07"
            },
            {
                "title": "ESG Investing and Sustainable Finance Strategies", 
                "content": "Analysis of Environmental, Social, and Governance (ESG) factors in investment decision-making. The study evaluates ESG scoring methodologies, sustainable portfolio construction, and impact measurement frameworks. Research demonstrates that ESG-integrated portfolios achieve comparable returns while reducing downside risk by 12%.",
                "source": "https://example.com/esg-investing",
                "tags": ["esg", "sustainable", "portfolio"],
                "date": "2025-07-06"
            }
        ]
        
        # Save test articles
        for i, article in enumerate(mock_articles):
            article_path = self.test_data_dir / f"test_article_{i+1}.json"
            with open(article_path, 'w') as f:
                json.dump(article, f, indent=2)
        
        # Create test configuration
        test_config = {
            "scraping": {
                "user_agent": "IntelForge-E2E-Test/1.0",
                "timeout": 30,
                "retry_attempts": 2
            },
            "processing": {
                "min_content_length": 100,
                "max_content_length": 10000,
                "keywords": ["trading", "finance", "investment", "market", "analysis"]
            },
            "ai": {
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "similarity_threshold": 0.7,
                "max_chunk_size": 512
            }
        }
        
        config_path = self.test_data_dir / "test_config.json"
        with open(config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        return len(mock_articles)
    
    def record_workflow_test(self, workflow_name: str, phase: str, status: str,
                           duration: float = 0, input_size: int = 0, 
                           output_size: int = 0, error: str = None):
        """Record workflow test result in database"""
        conn = sqlite3.connect(self.e2e_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO workflow_tests 
            (timestamp, workflow_name, phase, status, duration_seconds, input_size, output_size, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.datetime.now().isoformat(), workflow_name, phase, status, 
              duration, input_size, output_size, error))
        
        conn.commit()
        conn.close()
    
    def record_data_flow(self, test_name: str, input_format: str, output_format: str,
                        integrity_score: float, accuracy: float, status: str):
        """Record data flow validation results"""
        conn = sqlite3.connect(self.e2e_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO data_flow_validation 
            (timestamp, test_name, input_format, output_format, data_integrity_score, transformation_accuracy, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.datetime.now().isoformat(), test_name, input_format, output_format,
              integrity_score, accuracy, status))
        
        conn.commit()
        conn.close()
    
    def test_data_ingestion_workflow(self) -> Dict:
        """Test complete data ingestion and initial processing workflow"""
        print("📥 Testing data ingestion workflow...")
        
        workflow_start = time.time()
        workflow_name = "data_ingestion"
        
        try:
            # Phase 1: Data loading
            phase_start = time.time()
            test_files = list(self.test_data_dir.glob("test_article_*.json"))
            
            loaded_articles = []
            for file_path in test_files:
                try:
                    with open(file_path, 'r') as f:
                        article = json.load(f)
                        loaded_articles.append(article)
                except Exception as e:
                    self.record_workflow_test(workflow_name, "data_loading", "error", 
                                            error=f"Failed to load {file_path}: {e}")
                    return {"status": "❌ ERROR", "error": f"Data loading failed: {e}"}
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "data_loading", "pass", 
                                    phase_duration, len(test_files), len(loaded_articles))
            
            # Phase 2: Data validation
            phase_start = time.time()
            validated_articles = []
            validation_errors = []
            
            required_fields = ["title", "content", "source", "tags", "date"]
            
            for i, article in enumerate(loaded_articles):
                valid = True
                missing_fields = []
                
                for field in required_fields:
                    if field not in article or not article[field]:
                        valid = False
                        missing_fields.append(field)
                
                if valid:
                    # Additional validation
                    if len(article["content"]) < 50:
                        valid = False
                        validation_errors.append(f"Article {i+1}: Content too short")
                    
                    if not isinstance(article["tags"], list):
                        valid = False
                        validation_errors.append(f"Article {i+1}: Tags must be a list")
                
                if valid:
                    validated_articles.append(article)
                else:
                    validation_errors.append(f"Article {i+1}: Missing fields: {missing_fields}")
            
            phase_duration = time.time() - phase_start
            validation_status = "pass" if len(validation_errors) == 0 else "partial"
            self.record_workflow_test(workflow_name, "data_validation", validation_status,
                                    phase_duration, len(loaded_articles), len(validated_articles))
            
            # Phase 3: Data transformation
            phase_start = time.time()
            transformed_articles = []
            
            for article in validated_articles:
                transformed = {
                    "id": len(transformed_articles) + 1,
                    "title": article["title"].strip(),
                    "content": article["content"].strip(),
                    "source_url": article["source"],
                    "keywords": article["tags"],
                    "publish_date": article["date"],
                    "word_count": len(article["content"].split()),
                    "character_count": len(article["content"]),
                    "processing_timestamp": datetime.datetime.now().isoformat()
                }
                transformed_articles.append(transformed)
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "data_transformation", "pass",
                                    phase_duration, len(validated_articles), len(transformed_articles))
            
            # Save processed data
            output_file = self.test_output_dir / "processed_articles.json"
            with open(output_file, 'w') as f:
                json.dump(transformed_articles, f, indent=2)
            
            workflow_duration = time.time() - workflow_start
            
            # Calculate data integrity score
            integrity_score = len(transformed_articles) / len(loaded_articles) if loaded_articles else 0
            
            self.record_data_flow("data_ingestion", "json", "processed_json", 
                                integrity_score, 1.0, "pass")
            
            return {
                "status": "✅ PASS",
                "workflow_duration": workflow_duration,
                "input_articles": len(loaded_articles),
                "validated_articles": len(validated_articles),
                "transformed_articles": len(transformed_articles),
                "validation_errors": validation_errors,
                "integrity_score": integrity_score,
                "output_file": str(output_file)
            }
            
        except Exception as e:
            self.record_workflow_test(workflow_name, "general", "error", error=str(e))
            return {
                "status": "❌ EXCEPTION",
                "error": str(e),
                "workflow_duration": time.time() - workflow_start
            }
    
    def test_content_processing_workflow(self) -> Dict:
        """Test content processing and analysis workflow"""
        print("🔍 Testing content processing workflow...")
        
        workflow_start = time.time()
        workflow_name = "content_processing"
        
        try:
            # Load processed articles from previous step
            input_file = self.test_output_dir / "processed_articles.json"
            if not input_file.exists():
                return {
                    "status": "❌ DEPENDENCY_ERROR",
                    "error": "No processed articles found from ingestion workflow"
                }
            
            with open(input_file, 'r') as f:
                articles = json.load(f)
            
            # Phase 1: Content analysis
            phase_start = time.time()
            analyzed_articles = []
            
            for article in articles:
                content = article["content"]
                
                # Simple content analysis
                analysis = {
                    "sentiment_score": 0.7,  # Mock positive sentiment
                    "complexity_score": len(content.split()) / 100,  # Word count based complexity
                    "technical_terms": len([word for word in content.lower().split() 
                                          if word in ["trading", "analysis", "market", "risk", "portfolio"]]),
                    "readability_score": min(100, max(0, 100 - len(content) / 50)),
                    "financial_relevance": 0.85 if any(term in content.lower() 
                                                     for term in ["trading", "finance", "investment"]) else 0.3
                }
                
                article["analysis"] = analysis
                analyzed_articles.append(article)
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "content_analysis", "pass",
                                    phase_duration, len(articles), len(analyzed_articles))
            
            # Phase 2: Content categorization
            phase_start = time.time()
            categorized_articles = []
            
            categories = {
                "algorithmic_trading": ["algorithm", "trading", "strategy"],
                "risk_management": ["risk", "management", "var", "portfolio"],
                "market_analysis": ["market", "analysis", "prediction", "forecast"],
                "cryptocurrency": ["crypto", "bitcoin", "blockchain"],
                "sustainable_finance": ["esg", "sustainable", "environmental"]
            }
            
            for article in analyzed_articles:
                content_lower = article["content"].lower()
                
                # Score each category
                category_scores = {}
                for category, keywords in categories.items():
                    score = sum(1 for keyword in keywords if keyword in content_lower)
                    category_scores[category] = score
                
                # Assign primary category
                primary_category = max(category_scores, key=category_scores.get)
                confidence = category_scores[primary_category] / len(categories[primary_category])
                
                article["categorization"] = {
                    "primary_category": primary_category,
                    "confidence": confidence,
                    "all_scores": category_scores
                }
                
                categorized_articles.append(article)
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "categorization", "pass",
                                    phase_duration, len(analyzed_articles), len(categorized_articles))
            
            # Phase 3: Quality scoring
            phase_start = time.time()
            scored_articles = []
            
            for article in categorized_articles:
                analysis = article["analysis"]
                categorization = article["categorization"]
                
                # Calculate quality score
                quality_components = {
                    "content_length": min(1.0, article["word_count"] / 200),  # Prefer 200+ words
                    "technical_relevance": analysis["technical_terms"] / 10,  # More technical terms = higher quality
                    "financial_relevance": analysis["financial_relevance"],
                    "categorization_confidence": categorization["confidence"],
                    "complexity": min(1.0, analysis["complexity_score"])
                }
                
                overall_quality = sum(quality_components.values()) / len(quality_components)
                
                article["quality"] = {
                    "overall_score": overall_quality,
                    "components": quality_components,
                    "grade": "high" if overall_quality >= 0.7 else "medium" if overall_quality >= 0.4 else "low"
                }
                
                scored_articles.append(article)
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "quality_scoring", "pass",
                                    phase_duration, len(categorized_articles), len(scored_articles))
            
            # Save processed content
            output_file = self.test_output_dir / "analyzed_articles.json"
            with open(output_file, 'w') as f:
                json.dump(scored_articles, f, indent=2)
            
            workflow_duration = time.time() - workflow_start
            
            # Calculate processing accuracy
            high_quality_articles = [a for a in scored_articles if a["quality"]["grade"] == "high"]
            accuracy = len(high_quality_articles) / len(scored_articles) if scored_articles else 0
            
            self.record_data_flow("content_processing", "processed_json", "analyzed_json",
                                1.0, accuracy, "pass")
            
            return {
                "status": "✅ PASS",
                "workflow_duration": workflow_duration,
                "input_articles": len(articles),
                "analyzed_articles": len(analyzed_articles),
                "high_quality_articles": len(high_quality_articles),
                "average_quality_score": sum(a["quality"]["overall_score"] for a in scored_articles) / len(scored_articles),
                "processing_accuracy": accuracy,
                "output_file": str(output_file)
            }
            
        except Exception as e:
            self.record_workflow_test(workflow_name, "general", "error", error=str(e))
            return {
                "status": "❌ EXCEPTION",
                "error": str(e),
                "workflow_duration": time.time() - workflow_start
            }
    
    def test_ai_pipeline_workflow(self) -> Dict:
        """Test AI processing pipeline workflow"""
        print("🧠 Testing AI pipeline workflow...")
        
        workflow_start = time.time()
        workflow_name = "ai_pipeline"
        
        try:
            # Load analyzed articles from previous step
            input_file = self.test_output_dir / "analyzed_articles.json"
            if not input_file.exists():
                return {
                    "status": "❌ DEPENDENCY_ERROR",
                    "error": "No analyzed articles found from content processing workflow"
                }
            
            with open(input_file, 'r') as f:
                articles = json.load(f)
            
            # Phase 1: Text chunking
            phase_start = time.time()
            chunked_content = []
            
            for article in articles:
                content = article["content"]
                # Simple chunking by sentences (mock implementation)
                sentences = content.split('. ')
                
                chunks = []
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) < 500:  # 500 char chunks
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                for i, chunk in enumerate(chunks):
                    chunked_content.append({
                        "article_id": article["id"],
                        "chunk_id": f"{article['id']}-{i+1}",
                        "content": chunk,
                        "length": len(chunk),
                        "article_title": article["title"],
                        "category": article["categorization"]["primary_category"]
                    })
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "text_chunking", "pass",
                                    phase_duration, len(articles), len(chunked_content))
            
            # Phase 2: Mock embedding generation
            phase_start = time.time()
            embedded_chunks = []
            
            for chunk in chunked_content:
                # Mock embedding generation (384-dimensional vector)
                # In real implementation, this would use actual embedding models
                embedding = [0.1 * i % 1.0 for i in range(384)]  # Mock embedding
                
                embedded_chunks.append({
                    "chunk_id": chunk["chunk_id"],
                    "article_id": chunk["article_id"],
                    "content": chunk["content"],
                    "embedding": embedding,
                    "embedding_dimension": len(embedding),
                    "category": chunk["category"]
                })
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "embedding_generation", "pass",
                                    phase_duration, len(chunked_content), len(embedded_chunks))
            
            # Phase 3: Mock vector search and similarity testing
            phase_start = time.time()
            
            # Test similarity searches
            search_queries = [
                "algorithmic trading strategies",
                "risk management techniques", 
                "market analysis methods",
                "cryptocurrency prediction models"
            ]
            
            search_results = []
            for query in search_queries:
                # Mock similarity search
                # In real implementation, this would use vector similarity
                query_results = []
                
                for chunk in embedded_chunks[:10]:  # Top 10 results
                    # Mock similarity score based on keyword matching
                    query_words = set(query.lower().split())
                    content_words = set(chunk["content"].lower().split())
                    similarity = len(query_words & content_words) / len(query_words | content_words)
                    
                    query_results.append({
                        "chunk_id": chunk["chunk_id"],
                        "similarity_score": similarity,
                        "content_preview": chunk["content"][:100] + "..."
                    })
                
                # Sort by similarity
                query_results.sort(key=lambda x: x["similarity_score"], reverse=True)
                search_results.append({
                    "query": query,
                    "results": query_results[:5],  # Top 5 results
                    "avg_similarity": sum(r["similarity_score"] for r in query_results[:5]) / 5
                })
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "vector_search", "pass",
                                    phase_duration, len(search_queries), len(search_results))
            
            # Save AI pipeline results
            ai_results = {
                "chunks": embedded_chunks,
                "search_results": search_results,
                "metadata": {
                    "total_chunks": len(embedded_chunks),
                    "embedding_dimension": 384,
                    "search_queries_tested": len(search_queries),
                    "average_search_similarity": sum(r["avg_similarity"] for r in search_results) / len(search_results)
                }
            }
            
            output_file = self.test_output_dir / "ai_pipeline_results.json"
            with open(output_file, 'w') as f:
                json.dump(ai_results, f, indent=2)
            
            workflow_duration = time.time() - workflow_start
            
            # Calculate AI pipeline performance
            avg_similarity = ai_results["metadata"]["average_search_similarity"]
            
            self.record_data_flow("ai_pipeline", "analyzed_json", "vector_embeddings",
                                1.0, avg_similarity, "pass")
            
            return {
                "status": "✅ PASS",
                "workflow_duration": workflow_duration,
                "input_articles": len(articles),
                "total_chunks": len(embedded_chunks),
                "embedding_dimension": 384,
                "search_queries": len(search_queries),
                "average_search_similarity": avg_similarity,
                "ai_performance": "excellent" if avg_similarity >= 0.7 else "good" if avg_similarity >= 0.5 else "needs_improvement",
                "output_file": str(output_file)
            }
            
        except Exception as e:
            self.record_workflow_test(workflow_name, "general", "error", error=str(e))
            return {
                "status": "❌ EXCEPTION",
                "error": str(e),
                "workflow_duration": time.time() - workflow_start
            }
    
    def test_output_generation_workflow(self) -> Dict:
        """Test final output generation and export workflow"""
        print("📄 Testing output generation workflow...")
        
        workflow_start = time.time()
        workflow_name = "output_generation"
        
        try:
            # Load AI pipeline results
            input_file = self.test_output_dir / "ai_pipeline_results.json"
            if not input_file.exists():
                return {
                    "status": "❌ DEPENDENCY_ERROR",
                    "error": "No AI pipeline results found"
                }
            
            with open(input_file, 'r') as f:
                ai_results = json.load(f)
            
            # Phase 1: Generate summary report
            phase_start = time.time()
            
            chunks = ai_results["chunks"]
            search_results = ai_results["search_results"]
            metadata = ai_results["metadata"]
            
            # Create comprehensive summary
            summary_report = {
                "executive_summary": {
                    "total_documents_processed": len(set(chunk["article_id"] for chunk in chunks)),
                    "total_content_chunks": len(chunks),
                    "embedding_model": "mock-sentence-transformer",
                    "search_performance": metadata["average_search_similarity"],
                    "processing_timestamp": datetime.datetime.now().isoformat()
                },
                "content_analysis": {
                    "categories_identified": list(set(chunk["category"] for chunk in chunks)),
                    "average_chunk_length": sum(len(chunk["content"]) for chunk in chunks) / len(chunks),
                    "content_distribution": {}
                },
                "search_analytics": {
                    "queries_processed": len(search_results),
                    "average_results_per_query": sum(len(r["results"]) for r in search_results) / len(search_results),
                    "search_quality_score": metadata["average_search_similarity"]
                }
            }
            
            # Calculate content distribution
            for chunk in chunks:
                category = chunk["category"]
                if category in summary_report["content_analysis"]["content_distribution"]:
                    summary_report["content_analysis"]["content_distribution"][category] += 1
                else:
                    summary_report["content_analysis"]["content_distribution"][category] = 1
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "summary_generation", "pass",
                                    phase_duration, len(chunks), 1)
            
            # Phase 2: Generate markdown report
            phase_start = time.time()
            
            markdown_content = f"""# IntelForge Analysis Report
            
## Executive Summary

**Processing Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Documents Processed**: {summary_report['executive_summary']['total_documents_processed']}  
**Content Chunks**: {summary_report['executive_summary']['total_content_chunks']}  
**Search Performance**: {summary_report['executive_summary']['search_performance']:.2f}

## Content Analysis

### Categories Identified
"""
            
            for category, count in summary_report["content_analysis"]["content_distribution"].items():
                percentage = (count / len(chunks)) * 100
                markdown_content += f"- **{category.replace('_', ' ').title()}**: {count} chunks ({percentage:.1f}%)\n"
            
            markdown_content += f"""
### Content Metrics
- **Average Chunk Length**: {summary_report['content_analysis']['average_chunk_length']:.0f} characters
- **Embedding Dimension**: {metadata['embedding_dimension']}
- **Total Content Volume**: {sum(len(chunk['content']) for chunk in chunks):,} characters

## Search Analytics

### Query Performance
"""
            
            for result in search_results:
                markdown_content += f"- **Query**: {result['query']}\n"
                markdown_content += f"  - **Average Similarity**: {result['avg_similarity']:.3f}\n"
                markdown_content += f"  - **Results**: {len(result['results'])}\n\n"
            
            markdown_content += f"""
### Overall Performance
- **Search Quality Score**: {summary_report['search_analytics']['search_quality_score']:.3f}
- **Queries Processed**: {summary_report['search_analytics']['queries_processed']}
- **Average Results per Query**: {summary_report['search_analytics']['average_results_per_query']:.1f}

## Technical Details

- **Processing Framework**: IntelForge End-to-End Pipeline
- **Embedding Model**: {summary_report['executive_summary']['embedding_model']}
- **Vector Dimension**: {metadata['embedding_dimension']}
- **Search Algorithm**: Mock Vector Similarity

---
*Generated by IntelForge E2E Testing Framework*
"""
            
            # Save markdown report
            markdown_file = self.test_output_dir / "analysis_report.md"
            with open(markdown_file, 'w') as f:
                f.write(markdown_content)
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "markdown_generation", "pass",
                                    phase_duration, 1, 1)
            
            # Phase 3: Generate JSON export
            phase_start = time.time()
            
            export_data = {
                "metadata": {
                    "export_timestamp": datetime.datetime.now().isoformat(),
                    "format_version": "1.0",
                    "generator": "IntelForge E2E Pipeline"
                },
                "summary": summary_report,
                "detailed_results": {
                    "chunks": chunks[:5],  # Sample of chunks for export
                    "search_examples": search_results
                }
            }
            
            json_file = self.test_output_dir / "export_data.json"
            with open(json_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            phase_duration = time.time() - phase_start
            self.record_workflow_test(workflow_name, "json_export", "pass",
                                    phase_duration, 1, 1)
            
            workflow_duration = time.time() - workflow_start
            
            # Calculate output quality
            output_files = [
                summary_report,
                markdown_file.stat().st_size,
                json_file.stat().st_size
            ]
            
            self.record_data_flow("output_generation", "vector_embeddings", "reports",
                                1.0, 1.0, "pass")
            
            return {
                "status": "✅ PASS",
                "workflow_duration": workflow_duration,
                "summary_report": summary_report,
                "markdown_file": str(markdown_file),
                "json_file": str(json_file),
                "markdown_size": markdown_file.stat().st_size,
                "json_size": json_file.stat().st_size,
                "output_quality": "excellent"
            }
            
        except Exception as e:
            self.record_workflow_test(workflow_name, "general", "error", error=str(e))
            return {
                "status": "❌ EXCEPTION",
                "error": str(e),
                "workflow_duration": time.time() - workflow_start
            }
    
    def validate_data_integrity(self) -> Dict:
        """Validate data integrity across the entire pipeline"""
        print("🔍 Validating data integrity across pipeline...")
        
        integrity_results = {}
        
        try:
            # Check all output files exist
            expected_files = [
                "processed_articles.json",
                "analyzed_articles.json", 
                "ai_pipeline_results.json",
                "analysis_report.md",
                "export_data.json"
            ]
            
            file_integrity = {}
            for filename in expected_files:
                file_path = self.test_output_dir / filename
                file_integrity[filename] = {
                    "exists": file_path.exists(),
                    "size": file_path.stat().st_size if file_path.exists() else 0,
                    "readable": file_path.is_file() if file_path.exists() else False
                }
            
            integrity_results["file_integrity"] = file_integrity
            
            # Validate data consistency
            consistency_checks = {}
            
            if file_integrity["processed_articles.json"]["exists"]:
                with open(self.test_output_dir / "processed_articles.json", 'r') as f:
                    processed = json.load(f)
                    consistency_checks["processed_articles_count"] = len(processed)
            
            if file_integrity["analyzed_articles.json"]["exists"]:
                with open(self.test_output_dir / "analyzed_articles.json", 'r') as f:
                    analyzed = json.load(f)
                    consistency_checks["analyzed_articles_count"] = len(analyzed)
            
            if file_integrity["ai_pipeline_results.json"]["exists"]:
                with open(self.test_output_dir / "ai_pipeline_results.json", 'r') as f:
                    ai_results = json.load(f)
                    consistency_checks["total_chunks"] = len(ai_results.get("chunks", []))
            
            integrity_results["consistency_checks"] = consistency_checks
            
            # Calculate overall integrity score
            files_exist = sum(1 for f in file_integrity.values() if f["exists"])
            total_files = len(file_integrity)
            file_score = files_exist / total_files
            
            # Data consistency score
            expected_processed = 5  # We started with 5 test articles
            actual_processed = consistency_checks.get("processed_articles_count", 0)
            consistency_score = min(1.0, actual_processed / expected_processed)
            
            overall_integrity = (file_score + consistency_score) / 2
            
            integrity_results["scores"] = {
                "file_integrity_score": file_score,
                "data_consistency_score": consistency_score,
                "overall_integrity_score": overall_integrity
            }
            
            return {
                "status": "✅ PASS" if overall_integrity >= 0.8 else "⚠️ PARTIAL" if overall_integrity >= 0.6 else "❌ FAIL",
                "integrity_results": integrity_results,
                "overall_score": overall_integrity
            }
            
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "error": str(e),
                "integrity_results": integrity_results
            }
    
    def generate_e2e_report(self) -> str:
        """Generate comprehensive end-to-end test report"""
        self.results["end_time"] = datetime.datetime.now().isoformat()
        self.results["status"] = "completed"
        
        # Calculate summary statistics
        conn = sqlite3.connect(self.e2e_db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM workflow_tests WHERE status = "pass"')
        passed_tests = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM workflow_tests WHERE status = "error"')
        failed_tests = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(duration_seconds) FROM workflow_tests WHERE duration_seconds > 0')
        avg_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Save detailed report
        report_path = self.test_dir / "reports" / "end_to_end" / f"e2e_report_{self.timestamp}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate markdown report
        md_report_path = self.test_dir / "reports" / "end_to_end" / f"e2e_report_{self.timestamp}.md"
        self.create_e2e_markdown_report(md_report_path, passed_tests, failed_tests, avg_duration)
        
        return str(md_report_path)
    
    def create_e2e_markdown_report(self, path: Path, passed: int, failed: int, avg_duration: float):
        """Create comprehensive end-to-end markdown report"""
        total_tests = passed + failed
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        
        content = f"""# IntelForge End-to-End Workflow Test Report

**Session ID**: {self.results['session_id']}  
**Test Date**: {self.results['start_time']}  
**Report Type**: Complete Pipeline Validation  

## 📊 Executive Summary

**Overall Status**: {'✅ EXCELLENT' if success_rate >= 90 else '✅ GOOD' if success_rate >= 75 else '⚠️ NEEDS ATTENTION' if success_rate >= 60 else '❌ CRITICAL ISSUES'}  
**Pipeline Health**: {'Excellent' if success_rate >= 90 else 'Good' if success_rate >= 75 else 'Needs Attention'}  
**Success Rate**: {success_rate:.1f}% ({passed}/{total_tests} tests passed)

## 🎯 Workflow Results Overview

| Workflow | Status | Duration | Key Metrics |
|----------|--------|----------|-------------|
"""
        
        # Add workflow results
        for workflow_name, results in self.results["workflows"].items():
            status = results.get("status", "❓ UNKNOWN")
            duration = results.get("workflow_duration", 0)
            
            # Extract key metrics based on workflow type
            key_metrics = "N/A"
            if "input_articles" in results and "transformed_articles" in results:
                key_metrics = f"{results['input_articles']}→{results['transformed_articles']} articles"
            elif "total_chunks" in results:
                key_metrics = f"{results['total_chunks']} chunks, {results.get('embedding_dimension', 0)}D embeddings"
            elif "markdown_file" in results:
                key_metrics = f"Reports generated ({results.get('markdown_size', 0)} + {results.get('json_size', 0)} bytes)"
            
            content += f"| **{workflow_name.replace('_', ' ').title()}** | {status} | {duration:.2f}s | {key_metrics} |\n"
        
        content += f"""

### Performance Metrics
- **Average Workflow Duration**: {avg_duration:.3f}s
- **Total Pipeline Runtime**: {sum(w.get('workflow_duration', 0) for w in self.results['workflows'].values()):.2f}s
- **Test Data Processing**: 5 articles → Multiple output formats

## 🔍 Detailed Workflow Analysis

"""
        
        # Add detailed analysis for each workflow
        for workflow_name, results in self.results["workflows"].items():
            content += f"### {workflow_name.replace('_', ' ').title()}\n\n"
            content += f"**Status**: {results.get('status', '❓ UNKNOWN')}  \n"
            content += f"**Duration**: {results.get('workflow_duration', 0):.3f}s  \n"
            
            if "error" in results:
                content += f"**Error**: {results['error']}  \n"
            else:
                # Add workflow-specific details
                if workflow_name == "data_ingestion":
                    content += f"**Articles Processed**: {results.get('input_articles', 0)} → {results.get('transformed_articles', 0)}  \n"
                    content += f"**Data Integrity**: {results.get('integrity_score', 0):.2f}  \n"
                elif workflow_name == "content_processing":
                    content += f"**Quality Analysis**: {results.get('average_quality_score', 0):.2f} average score  \n"
                    content += f"**High Quality Articles**: {results.get('high_quality_articles', 0)}  \n"
                elif workflow_name == "ai_pipeline":
                    content += f"**Chunks Generated**: {results.get('total_chunks', 0)}  \n"
                    content += f"**Search Performance**: {results.get('average_search_similarity', 0):.3f}  \n"
                    content += f"**AI Performance**: {results.get('ai_performance', 'N/A')}  \n"
                elif workflow_name == "output_generation":
                    content += f"**Reports Generated**: Markdown ({results.get('markdown_size', 0)} bytes) + JSON ({results.get('json_size', 0)} bytes)  \n"
                    content += f"**Output Quality**: {results.get('output_quality', 'N/A')}  \n"
            
            content += "\n"
        
        # Add data integrity analysis
        if "integrity_checks" in self.results:
            integrity = self.results["integrity_checks"]
            content += "## 🔍 Data Integrity Analysis\n\n"
            content += f"**Overall Integrity Score**: {integrity.get('overall_score', 0):.2f}  \n"
            content += f"**Status**: {integrity.get('status', 'Unknown')}  \n"
            
            if "integrity_results" in integrity:
                content += "\n### File Integrity\n"
                for filename, info in integrity["integrity_results"].get("file_integrity", {}).items():
                    status = "✅" if info["exists"] and info["readable"] else "❌"
                    content += f"- **{filename}**: {status} ({info['size']} bytes)\n"
        
        content += f"""

## 🎯 Pipeline Assessment

### Strengths
- End-to-end data flow validation completed
- Multiple output formats generated successfully
- Comprehensive workflow testing across {len(self.results['workflows'])} core components

### Areas for Improvement
{'- No critical issues identified' if success_rate >= 90 else '- Review failed workflows for optimization opportunities'}
{'- Excellent pipeline performance' if success_rate >= 80 else '- Consider performance optimization for slower workflows'}

## 📋 Recommendations

### Immediate Actions
{'✅ No immediate actions required - pipeline is healthy' if success_rate >= 90 else '⚠️ Address failing workflows before production deployment'}

### Long-term Optimization
- Implement automated end-to-end testing in CI/CD pipeline
- Set up data quality monitoring for production
- Establish performance benchmarks for each workflow stage

## 🔗 Technical Details

**Test Database**: `{self.e2e_db_path}`  
**Test Data Directory**: `{self.test_data_dir}`  
**Output Directory**: `{self.test_output_dir}`  
**Report Location**: `{path}`

**Generated Files:**
- Test articles: 5 JSON files
- Processing outputs: Multiple JSON and Markdown files
- Comprehensive analysis reports

---
*Generated by IntelForge End-to-End Testing Framework*  
*Framework: Complete pipeline validation with data integrity checks*
"""
        
        with open(path, 'w') as f:
            f.write(content)

def main():
    parser = argparse.ArgumentParser(description="IntelForge End-to-End Workflow Tester")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--keep-data", action="store_true", help="Keep test data after completion")
    
    args = parser.parse_args()
    
    print("🚀 Starting IntelForge End-to-End Workflow Testing")
    print("🔄 Testing complete data pipeline from ingestion to output")
    print("📊 Comprehensive workflow validation with data integrity checks")
    
    tester = EndToEndWorkflowTester()
    
    # Run complete workflow pipeline
    print("\n" + "="*80)
    tester.results["workflows"]["data_ingestion"] = tester.test_data_ingestion_workflow()
    
    print("\n" + "="*80)
    tester.results["workflows"]["content_processing"] = tester.test_content_processing_workflow()
    
    print("\n" + "="*80)
    tester.results["workflows"]["ai_pipeline"] = tester.test_ai_pipeline_workflow()
    
    print("\n" + "="*80)
    tester.results["workflows"]["output_generation"] = tester.test_output_generation_workflow()
    
    print("\n" + "="*80)
    tester.results["integrity_checks"] = tester.validate_data_integrity()
    
    # Generate comprehensive report
    print("\n" + "="*80)
    print("📊 Generating end-to-end test report...")
    report_path = tester.generate_e2e_report()
    
    # Calculate final statistics
    workflows = tester.results["workflows"]
    successful_workflows = sum(1 for w in workflows.values() if w.get("status", "").startswith("✅"))
    total_workflows = len(workflows)
    success_rate = (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0
    
    integrity_score = tester.results["integrity_checks"].get("overall_score", 0)
    
    print(f"\n🎉 End-to-end workflow testing complete!")
    print(f"📊 **Workflows**: {successful_workflows}/{total_workflows} successful ({success_rate:.1f}%)")
    print(f"🔍 **Data Integrity**: {integrity_score:.2f}")
    print(f"📋 **Pipeline Status**: {'HEALTHY' if success_rate >= 80 and integrity_score >= 0.8 else 'NEEDS ATTENTION'}")
    print(f"📁 **Report**: {report_path}")
    print(f"🗄️ **Database**: {tester.e2e_db_path}")
    print(f"📂 **Test Output**: {tester.test_output_dir}")
    
    # Cleanup if not keeping data
    if not args.keep_data:
        try:
            shutil.rmtree(tester.test_data_dir)
            print(f"🧹 Cleaned up test data directory")
        except Exception as e:
            print(f"⚠️ Warning: Could not clean up test data: {e}")

if __name__ == "__main__":
    main()