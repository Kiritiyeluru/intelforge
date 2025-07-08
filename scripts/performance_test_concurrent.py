#!/usr/bin/env python3
"""
Phase 4: Performance Optimization & Concurrent Processing Test

This script tests concurrent processing capabilities for:
1. Academic research queries across multiple databases
2. Batch web scraping operations
3. Performance benchmarking and optimization

Designed to validate scalability before production deployment.
"""

import asyncio
import time
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Dict, Any
import subprocess

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_academic_query(query: str, database: str = "arxiv", limit: int = 5) -> Dict[str, Any]:
    """Run single academic research query."""
    start_time = time.time()
    
    try:
        if database == "arxiv":
            # Use arxiv_simple.py
            result = subprocess.run([
                sys.executable, "scripts/arxiv_simple.py",
                "--query", query,
                "--limit", str(limit)
            ], capture_output=True, text=True, cwd=project_root)
        else:
            # Use academic_research.py
            result = subprocess.run([
                sys.executable, "scripts/academic_research.py", 
                "--query", query,
                "--database", database,
                "--limit", str(limit)
            ], capture_output=True, text=True, cwd=project_root)
        
        execution_time = time.time() - start_time
        
        return {
            "query": query,
            "database": database,
            "limit": limit,
            "success": result.returncode == 0,
            "execution_time": execution_time,
            "output_length": len(result.stdout) if result.stdout else 0,
            "error": result.stderr if result.stderr else None
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "query": query,
            "database": database,
            "limit": limit,
            "success": False,
            "execution_time": execution_time,
            "output_length": 0,
            "error": str(e)
        }

def run_stealth_scrape(url: str) -> Dict[str, Any]:
    """Run single stealth scraping operation."""
    start_time = time.time()
    
    try:
        # Use stealth_scraper_simple.py (HTTP-based for speed)
        result = subprocess.run([
            sys.executable, "scripts/stealth_scraper_simple.py",
            "--url", url
        ], capture_output=True, text=True, cwd=project_root)
        
        execution_time = time.time() - start_time
        
        return {
            "url": url,
            "success": result.returncode == 0,
            "execution_time": execution_time,
            "output_length": len(result.stdout) if result.stdout else 0,
            "error": result.stderr if result.stderr else None
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        return {
            "url": url,
            "success": False,
            "execution_time": execution_time,
            "output_length": 0,
            "error": str(e)
        }

def test_concurrent_academic_research():
    """Test concurrent academic research processing."""
    print("🔬 Testing Concurrent Academic Research Processing")
    print("=" * 60)
    
    # Define test queries
    academic_queries = [
        ("algorithmic trading", "arxiv", 5),
        ("machine learning finance", "arxiv", 5), 
        ("quantitative analysis", "arxiv", 5),
        ("neural networks trading", "arxiv", 5),
        ("risk management algorithms", "arxiv", 5)
    ]
    
    # Sequential processing benchmark
    print("📊 Sequential Processing Benchmark:")
    sequential_start = time.time()
    sequential_results = []
    
    for query, database, limit in academic_queries:
        result = run_academic_query(query, database, limit)
        sequential_results.append(result)
        print(f"  ✅ {query[:30]:<30} | {result['execution_time']:.2f}s | {'SUCCESS' if result['success'] else 'FAILED'}")
    
    sequential_time = time.time() - sequential_start
    print(f"\n📈 Sequential Total Time: {sequential_time:.2f}s")
    
    # Concurrent processing test
    print("\n🚀 Concurrent Processing Test:")
    concurrent_start = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for query, database, limit in academic_queries:
            future = executor.submit(run_academic_query, query, database, limit)
            futures.append(future)
        
        concurrent_results = []
        for future in futures:
            result = future.result()
            concurrent_results.append(result)
            print(f"  ✅ {result['query'][:30]:<30} | {result['execution_time']:.2f}s | {'SUCCESS' if result['success'] else 'FAILED'}")
    
    concurrent_time = time.time() - concurrent_start
    
    # Performance analysis
    speedup = sequential_time / concurrent_time if concurrent_time > 0 else 0
    print(f"\n📈 Concurrent Total Time: {concurrent_time:.2f}s")
    print(f"🚀 Performance Speedup: {speedup:.2f}x")
    print(f"⚡ Efficiency Gain: {((speedup - 1) * 100):.1f}%")
    
    return {
        "sequential_time": sequential_time,
        "concurrent_time": concurrent_time,
        "speedup": speedup,
        "sequential_results": sequential_results,
        "concurrent_results": concurrent_results
    }

def test_concurrent_web_scraping():
    """Test concurrent web scraping operations."""
    print("\n🌐 Testing Concurrent Web Scraping")
    print("=" * 60)
    
    # Define test URLs (using safe, fast sites for testing)
    test_urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/html", 
        "https://httpbin.org/robots.txt",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers"
    ]
    
    # Sequential processing benchmark
    print("📊 Sequential Scraping Benchmark:")
    sequential_start = time.time()
    sequential_results = []
    
    for url in test_urls:
        result = run_stealth_scrape(url)
        sequential_results.append(result)
        print(f"  ✅ {url:<35} | {result['execution_time']:.2f}s | {'SUCCESS' if result['success'] else 'FAILED'}")
    
    sequential_time = time.time() - sequential_start
    print(f"\n📈 Sequential Total Time: {sequential_time:.2f}s")
    
    # Concurrent processing test
    print("\n🚀 Concurrent Scraping Test:")
    concurrent_start = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for url in test_urls:
            future = executor.submit(run_stealth_scrape, url)
            futures.append(future)
        
        concurrent_results = []
        for future in futures:
            result = future.result()
            concurrent_results.append(result)
            print(f"  ✅ {result['url']:<35} | {result['execution_time']:.2f}s | {'SUCCESS' if result['success'] else 'FAILED'}")
    
    concurrent_time = time.time() - concurrent_start
    
    # Performance analysis
    speedup = sequential_time / concurrent_time if concurrent_time > 0 else 0
    print(f"\n📈 Concurrent Total Time: {concurrent_time:.2f}s")
    print(f"🚀 Performance Speedup: {speedup:.2f}x")
    print(f"⚡ Efficiency Gain: {((speedup - 1) * 100):.1f}%")
    
    return {
        "sequential_time": sequential_time,
        "concurrent_time": concurrent_time,
        "speedup": speedup,
        "sequential_results": sequential_results,
        "concurrent_results": concurrent_results
    }

def test_memory_usage():
    """Test memory usage during concurrent operations."""
    print("\n💾 Memory Usage Analysis")
    print("=" * 60)
    
    try:
        import psutil
        process = psutil.Process()
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        print(f"📊 Baseline Memory: {baseline_memory:.1f} MB")
        
        # Memory during concurrent academic research
        print("🔬 Testing memory during concurrent academic research...")
        academic_results = test_concurrent_academic_research()
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory
        print(f"📈 Peak Memory: {peak_memory:.1f} MB (+{memory_increase:.1f} MB)")
        
        return {
            "baseline_memory_mb": baseline_memory,
            "peak_memory_mb": peak_memory,
            "memory_increase_mb": memory_increase,
            "academic_results": academic_results
        }
        
    except ImportError:
        print("⚠️  psutil not available - skipping memory analysis")
        return {"academic_results": test_concurrent_academic_research()}

def main():
    """Main performance testing function."""
    print("🚀 IntelForge Phase 4: Performance Optimization & Concurrent Processing")
    print("=" * 80)
    
    # Test concurrent academic research
    academic_results = test_concurrent_academic_research()
    
    # Test concurrent web scraping
    web_results = test_concurrent_web_scraping()
    
    # Summary report
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE SUMMARY REPORT")
    print("=" * 80)
    
    print(f"🔬 Academic Research:")
    print(f"   Sequential: {academic_results['sequential_time']:.2f}s")
    print(f"   Concurrent: {academic_results['concurrent_time']:.2f}s")
    print(f"   Speedup: {academic_results['speedup']:.2f}x")
    
    print(f"\n🌐 Web Scraping:")
    print(f"   Sequential: {web_results['sequential_time']:.2f}s")
    print(f"   Concurrent: {web_results['concurrent_time']:.2f}s")
    print(f"   Speedup: {web_results['speedup']:.2f}x")
    
    # Overall assessment
    avg_speedup = (academic_results['speedup'] + web_results['speedup']) / 2
    print(f"\n🎯 Overall Performance:")
    print(f"   Average Speedup: {avg_speedup:.2f}x")
    print(f"   Efficiency Rating: {'EXCELLENT' if avg_speedup > 2.5 else 'GOOD' if avg_speedup > 1.5 else 'MODERATE'}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if avg_speedup > 2.0:
        print("   ✅ Concurrent processing provides significant performance benefits")
        print("   🚀 Ready for production concurrent operations")
    else:
        print("   ⚠️  Limited concurrent benefits - consider I/O optimization")
        print("   🔧 Focus on single-threaded performance improvements")
    
    return {
        "academic_results": academic_results,
        "web_results": web_results,
        "average_speedup": avg_speedup
    }

if __name__ == "__main__":
    results = main()
    
    # Save results for analysis
    import json
    output_file = project_root / "output" / f"performance_test_{int(time.time())}.json"
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")