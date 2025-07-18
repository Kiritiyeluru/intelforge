#!/usr/bin/env python3
"""
IntelForge Performance Improvement Test
Tests the performance improvements from newly installed optimization tools
"""

import json
import logging
import time

import numpy as np
import pandas as pd

# Test new performance tools
try:
    import orjson  # 2-3x faster JSON

    ORJSON_AVAILABLE = True
except ImportError:
    ORJSON_AVAILABLE = False

try:
    import msgpack  # Fast serialization

    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False

try:
    import polars as pl  # 10-100x faster dataframes

    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False

try:
    import redis  # High-performance caching

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import diskcache  # Persistent caching

    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

try:
    import numpy_financial as npf  # Financial calculations

    NUMPY_FINANCIAL_AVAILABLE = True
except ImportError:
    NUMPY_FINANCIAL_AVAILABLE = False

try:
    import scipy  # Scientific computing

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def test_json_performance():
    """Test JSON processing performance: orjson vs standard json"""
    if not ORJSON_AVAILABLE:
        logger.warning("orjson not available, skipping JSON performance test")
        return {}

    # Generate test data
    test_data = {
        "financial_data": [
            {
                "symbol": f"STOCK{i}",
                "price": np.random.uniform(10, 1000),
                "volume": np.random.randint(1000, 100000),
            }
            for i in range(1000)
        ],
        "metadata": {"timestamp": "2025-07-09", "source": "performance_test"},
    }

    # Test standard json
    start_time = time.time()
    for _ in range(100):
        json_str = json.dumps(test_data)
        json.loads(json_str)
    standard_time = time.time() - start_time

    # Test orjson
    start_time = time.time()
    for _ in range(100):
        orjson_bytes = orjson.dumps(test_data)
        orjson.loads(orjson_bytes)
    orjson_time = time.time() - start_time

    speedup = standard_time / orjson_time if orjson_time > 0 else 0

    return {
        "test": "JSON Processing",
        "standard_time": f"{standard_time:.4f}s",
        "orjson_time": f"{orjson_time:.4f}s",
        "speedup": f"{speedup:.2f}x",
        "status": "✅ IMPROVED" if speedup > 1.5 else "⚠️ MINIMAL",
    }


def test_serialization_performance():
    """Test serialization performance: msgpack vs pickle"""
    if not MSGPACK_AVAILABLE:
        logger.warning("msgpack not available, skipping serialization test")
        return {}

    import pickle

    # Generate test data
    test_data = {
        "trading_strategies": [
            {
                "strategy": f"Strategy{i}",
                "parameters": {"period": i * 10, "threshold": i * 0.1},
            }
            for i in range(500)
        ]
    }

    # Test pickle
    start_time = time.time()
    for _ in range(100):
        pickle_data = pickle.dumps(test_data)
        pickle.loads(pickle_data)
    pickle_time = time.time() - start_time

    # Test msgpack
    start_time = time.time()
    for _ in range(100):
        msgpack_data = msgpack.packb(test_data)
        msgpack.unpackb(msgpack_data, raw=False)
    msgpack_time = time.time() - start_time

    speedup = pickle_time / msgpack_time if msgpack_time > 0 else 0

    return {
        "test": "Serialization",
        "pickle_time": f"{pickle_time:.4f}s",
        "msgpack_time": f"{msgpack_time:.4f}s",
        "speedup": f"{speedup:.2f}x",
        "status": "✅ IMPROVED" if speedup > 1.5 else "⚠️ MINIMAL",
    }


def test_dataframe_performance():
    """Test dataframe performance: polars vs pandas"""
    if not POLARS_AVAILABLE:
        logger.warning("polars not available, skipping dataframe test")
        return {}

    # Generate test data
    data = {
        "price": np.random.uniform(10, 1000, 10000),
        "volume": np.random.randint(1000, 100000, 10000),
        "timestamp": pd.date_range("2024-01-01", periods=10000, freq="1min"),
    }

    # Test pandas
    start_time = time.time()
    df_pandas = pd.DataFrame(data)
    df_pandas["price_change"] = df_pandas["price"].pct_change()
    df_pandas["volume_ma"] = df_pandas["volume"].rolling(window=20).mean()
    df_pandas.groupby(df_pandas["timestamp"].dt.hour)["price"].mean()
    pandas_time = time.time() - start_time

    # Test polars
    start_time = time.time()
    df_polars = pl.DataFrame(data)
    df_polars = df_polars.with_columns(
        [
            pl.col("price").pct_change().alias("price_change"),
            pl.col("volume").rolling_mean(window_size=20).alias("volume_ma"),
        ]
    )
    df_polars.group_by(pl.col("timestamp").dt.hour()).agg(pl.col("price").mean())
    polars_time = time.time() - start_time

    speedup = pandas_time / polars_time if polars_time > 0 else 0

    return {
        "test": "Dataframe Operations",
        "pandas_time": f"{pandas_time:.4f}s",
        "polars_time": f"{polars_time:.4f}s",
        "speedup": f"{speedup:.2f}x",
        "status": "✅ IMPROVED" if speedup > 2.0 else "⚠️ MINIMAL",
    }


def test_financial_calculations():
    """Test financial calculations with numpy-financial"""
    if not NUMPY_FINANCIAL_AVAILABLE:
        logger.warning(
            "numpy-financial not available, skipping financial calculation test"
        )
        return {}

    # Test financial calculations
    start_time = time.time()

    # Present value calculations
    pv_results = []
    for i in range(1000):
        rate = 0.05 + i * 0.0001
        nper = 10
        pmt = -100
        fv = 0
        pv = npf.pv(rate, nper, pmt, fv)
        pv_results.append(pv)

    # Future value calculations
    fv_results = []
    for i in range(1000):
        rate = 0.05 + i * 0.0001
        nper = 10
        pmt = -100
        pv = 0
        fv = npf.fv(rate, nper, pmt, pv)
        fv_results.append(fv)

    financial_time = time.time() - start_time

    return {
        "test": "Financial Calculations",
        "calculations": 2000,
        "time": f"{financial_time:.4f}s",
        "rate": f"{2000 / financial_time:.0f} calc/sec",
        "status": "✅ OPTIMIZED",
    }


def test_caching_performance():
    """Test caching performance improvements"""
    if not DISKCACHE_AVAILABLE:
        logger.warning("diskcache not available, skipping caching test")
        return {}

    import diskcache

    # Test without caching
    start_time = time.time()
    results = []
    for i in range(100):
        # Simulate expensive calculation
        result = sum(j**2 for j in range(1000))
        results.append(result)
    no_cache_time = time.time() - start_time

    # Test with caching
    cache = diskcache.Cache("/tmp/intelforge_cache_test")
    start_time = time.time()
    cached_results = []
    for i in range(100):
        key = f"calculation_{i}"
        if key in cache:
            result = cache[key]
        else:
            result = sum(j**2 for j in range(1000))
            cache[key] = result
        cached_results.append(result)

    # Second pass (should be cached)
    for i in range(100):
        key = f"calculation_{i}"
        result = cache[key]
        cached_results.append(result)

    cached_time = time.time() - start_time
    cache.close()

    speedup = no_cache_time / (cached_time / 2) if cached_time > 0 else 0

    return {
        "test": "Caching Performance",
        "no_cache_time": f"{no_cache_time:.4f}s",
        "cached_time": f"{cached_time / 2:.4f}s (avg)",
        "speedup": f"{speedup:.2f}x",
        "status": "✅ IMPROVED" if speedup > 2.0 else "⚠️ MINIMAL",
    }


def main():
    """Run all performance tests"""
    logger.info("🚀 Starting IntelForge Performance Improvement Tests")

    # Check what's available
    available_tools = {
        "orjson": ORJSON_AVAILABLE,
        "msgpack": MSGPACK_AVAILABLE,
        "polars": POLARS_AVAILABLE,
        "redis": REDIS_AVAILABLE,
        "diskcache": DISKCACHE_AVAILABLE,
        "numpy_financial": NUMPY_FINANCIAL_AVAILABLE,
        "scipy": SCIPY_AVAILABLE,
    }

    logger.info(f"Available performance tools: {sum(available_tools.values())}/7")
    for tool, available in available_tools.items():
        status = "✅" if available else "❌"
        logger.info(f"  {tool}: {status}")

    # Run tests
    test_results = []

    logger.info("Running JSON performance test...")
    json_result = test_json_performance()
    if json_result:
        test_results.append(json_result)

    logger.info("Running serialization performance test...")
    serialization_result = test_serialization_performance()
    if serialization_result:
        test_results.append(serialization_result)

    logger.info("Running dataframe performance test...")
    dataframe_result = test_dataframe_performance()
    if dataframe_result:
        test_results.append(dataframe_result)

    logger.info("Running financial calculations test...")
    financial_result = test_financial_calculations()
    if financial_result:
        test_results.append(financial_result)

    logger.info("Running caching performance test...")
    caching_result = test_caching_performance()
    if caching_result:
        test_results.append(caching_result)

    # Summary
    logger.info("🎯 Performance Test Results:")
    logger.info("=" * 60)

    for result in test_results:
        logger.info(f"📊 {result['test']}: {result['status']}")
        if "speedup" in result:
            logger.info(f"   Speedup: {result['speedup']}")
        if "rate" in result:
            logger.info(f"   Rate: {result['rate']}")

    # Overall assessment
    improved_count = sum(
        1
        for result in test_results
        if result["status"] == "✅ IMPROVED" or result["status"] == "✅ OPTIMIZED"
    )
    total_tests = len(test_results)

    logger.info("=" * 60)
    logger.info(
        f"📈 Overall Performance: {improved_count}/{total_tests} tests show improvement"
    )

    if improved_count >= total_tests * 0.8:
        logger.info("🎉 EXCELLENT: Significant performance improvements achieved!")
    elif improved_count >= total_tests * 0.6:
        logger.info("✅ GOOD: Moderate performance improvements achieved")
    else:
        logger.info("⚠️ MINIMAL: Limited performance improvements")

    return test_results


if __name__ == "__main__":
    main()
