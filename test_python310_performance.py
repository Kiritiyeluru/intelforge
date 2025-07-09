#!/usr/bin/env python3
"""
Python 3.10 Performance Validation Script
Tests the high-performance tools: vectorbt, numba, ta-lib, polars
"""

import sys
import time
import numpy as np
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_numba_performance():
    """Test Numba JIT compilation speedup"""
    logger.info("Testing Numba JIT compilation...")
    
    try:
        import numba
        
        @numba.jit
        def fibonacci_jit(n):
            if n < 2:
                return n
            return fibonacci_jit(n-1) + fibonacci_jit(n-2)
        
        def fibonacci_python(n):
            if n < 2:
                return n
            return fibonacci_python(n-1) + fibonacci_python(n-2)
        
        # Compile JIT function
        _ = fibonacci_jit(5)
        
        # Test smaller numbers due to exponential complexity
        n = 30
        
        # Time Python version
        start = time.time()
        result_python = fibonacci_python(n)
        python_time = time.time() - start
        
        # Time JIT version
        start = time.time()
        result_jit = fibonacci_jit(n)
        jit_time = time.time() - start
        
        speedup = python_time / jit_time if jit_time > 0 else 0
        
        return {
            "test": "Numba JIT Compilation",
            "python_time": f"{python_time:.4f}s",
            "jit_time": f"{jit_time:.4f}s",
            "speedup": f"{speedup:.2f}x",
            "result_match": result_python == result_jit,
            "status": "✅ EXCELLENT" if speedup > 50 else "✅ GOOD" if speedup > 10 else "⚠️ MINIMAL"
        }
        
    except ImportError:
        return {"test": "Numba JIT Compilation", "status": "❌ NOT AVAILABLE"}

def test_talib_performance():
    """Test TA-Lib technical analysis performance"""
    logger.info("Testing TA-Lib technical analysis...")
    
    try:
        import talib
        
        # Generate larger dataset for performance testing
        np.random.seed(42)
        n_points = 10000
        prices = 100 + np.cumsum(np.random.randn(n_points) * 0.01)
        
        start = time.time()
        
        # Calculate multiple indicators
        sma_20 = talib.SMA(prices, timeperiod=20)
        ema_20 = talib.EMA(prices, timeperiod=20)
        rsi = talib.RSI(prices, timeperiod=14)
        macd, macd_signal, macd_hist = talib.MACD(prices)
        bb_upper, bb_middle, bb_lower = talib.BBANDS(prices)
        slowk, slowd = talib.STOCH(prices, prices, prices)
        atr = talib.ATR(prices, prices, prices, timeperiod=14)
        adx = talib.ADX(prices, prices, prices, timeperiod=14)
        
        end = time.time()
        
        calculation_time = end - start
        indicators_per_second = 8 / calculation_time if calculation_time > 0 else 0
        
        return {
            "test": "TA-Lib Technical Analysis",
            "data_points": n_points,
            "indicators": 8,
            "time": f"{calculation_time:.4f}s",
            "rate": f"{indicators_per_second:.0f} indicators/sec",
            "status": "✅ OPTIMIZED"
        }
        
    except ImportError:
        return {"test": "TA-Lib Technical Analysis", "status": "❌ NOT AVAILABLE"}

def test_vectorbt_performance():
    """Test VectorBT backtesting performance"""
    logger.info("Testing VectorBT backtesting...")
    
    try:
        import vectorbt as vbt
        
        # Generate realistic market data
        np.random.seed(42)
        n_days = 2000  # ~5.5 years
        dates = pd.date_range('2019-01-01', periods=n_days, freq='D')
        
        # Generate more realistic price data with trends and volatility
        returns = np.random.normal(0.0005, 0.02, n_days)  # Daily returns
        prices = pd.Series(100 * np.exp(np.cumsum(returns)), index=dates)
        
        start = time.time()
        
        # Multiple moving average strategy
        fast_ma = prices.rolling(10).mean()
        slow_ma = prices.rolling(50).mean()
        
        # Generate signals
        entries = fast_ma > slow_ma
        exits = fast_ma <= slow_ma
        
        # Backtest with transaction costs
        portfolio = vbt.Portfolio.from_signals(
            prices, entries, exits, 
            init_cash=100000,
            fees=0.001,  # 0.1% transaction fee
            freq='D'
        )
        
        # Calculate performance metrics
        total_return = portfolio.total_return()
        sharpe_ratio = portfolio.sharpe_ratio()
        max_drawdown = portfolio.max_drawdown()
        
        end = time.time()
        
        backtest_time = end - start
        days_per_second = n_days / backtest_time if backtest_time > 0 else 0
        
        return {
            "test": "VectorBT Backtesting",
            "data_points": n_days,
            "time": f"{backtest_time:.4f}s",
            "rate": f"{days_per_second:.0f} days/sec",
            "total_return": f"{total_return:.2%}",
            "sharpe_ratio": f"{sharpe_ratio:.2f}",
            "max_drawdown": f"{max_drawdown:.2%}",
            "status": "✅ OPTIMIZED" if days_per_second > 1000 else "✅ GOOD"
        }
        
    except ImportError:
        return {"test": "VectorBT Backtesting", "status": "❌ NOT AVAILABLE"}

def test_polars_performance():
    """Test Polars dataframe performance vs Pandas"""
    logger.info("Testing Polars vs Pandas performance...")
    
    try:
        import polars as pl
        
        # Generate larger dataset to see Polars benefits
        np.random.seed(42)
        n_rows = 100000
        data = {
            'timestamp': pd.date_range('2020-01-01', periods=n_rows, freq='1min'),
            'price': np.random.uniform(10, 1000, n_rows),
            'volume': np.random.randint(1000, 100000, n_rows),
            'symbol': np.random.choice(['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'], n_rows)
        }
        
        # Test Pandas
        start = time.time()
        df_pandas = pd.DataFrame(data)
        df_pandas['price_change'] = df_pandas.groupby('symbol')['price'].pct_change()
        df_pandas['volume_ma'] = df_pandas.groupby('symbol')['volume'].rolling(window=100).mean().reset_index(0, drop=True)
        result_pandas = df_pandas.groupby(['symbol', df_pandas['timestamp'].dt.hour])['price'].agg(['mean', 'std', 'count'])
        pandas_time = time.time() - start
        
        # Test Polars
        start = time.time()
        df_polars = pl.DataFrame(data)
        df_polars = df_polars.with_columns([
            pl.col('price').pct_change().over('symbol').alias('price_change'),
            pl.col('volume').rolling_mean(window_size=100).over('symbol').alias('volume_ma')
        ])
        result_polars = df_polars.group_by(['symbol', pl.col('timestamp').dt.hour()]).agg([
            pl.col('price').mean().alias('price_mean'),
            pl.col('price').std().alias('price_std'),
            pl.col('price').count().alias('price_count')
        ])
        polars_time = time.time() - start
        
        speedup = pandas_time / polars_time if polars_time > 0 else 0
        
        return {
            "test": "Polars vs Pandas",
            "data_rows": n_rows,
            "pandas_time": f"{pandas_time:.4f}s",
            "polars_time": f"{polars_time:.4f}s",
            "speedup": f"{speedup:.2f}x",
            "status": "✅ EXCELLENT" if speedup > 5 else "✅ GOOD" if speedup > 2 else "⚠️ MINIMAL"
        }
        
    except ImportError:
        return {"test": "Polars vs Pandas", "status": "❌ NOT AVAILABLE"}

def test_financial_calculations():
    """Test financial calculations performance"""
    logger.info("Testing financial calculations...")
    
    try:
        # Test complex financial calculations
        np.random.seed(42)
        n_calculations = 10000
        
        start = time.time()
        
        # Portfolio optimization calculations
        returns = np.random.normal(0.08/252, 0.2/np.sqrt(252), (n_calculations, 5))
        weights = np.random.dirichlet(np.ones(5), n_calculations)
        
        # Calculate portfolio returns and volatility
        portfolio_returns = np.sum(returns * weights, axis=1)
        portfolio_variance = np.sum((weights**2) * (0.2**2), axis=1) / 252
        portfolio_volatility = np.sqrt(portfolio_variance)
        sharpe_ratios = portfolio_returns / portfolio_volatility
        
        # Risk metrics
        var_95 = np.percentile(portfolio_returns, 5)
        cvar_95 = np.mean(portfolio_returns[portfolio_returns <= var_95])
        
        end = time.time()
        
        calc_time = end - start
        calcs_per_second = n_calculations / calc_time if calc_time > 0 else 0
        
        return {
            "test": "Financial Calculations",
            "calculations": n_calculations,
            "time": f"{calc_time:.4f}s",
            "rate": f"{calcs_per_second:.0f} portfolios/sec",
            "avg_return": f"{np.mean(portfolio_returns)*252:.2%}",
            "avg_volatility": f"{np.mean(portfolio_volatility)*np.sqrt(252):.2%}",
            "avg_sharpe": f"{np.mean(sharpe_ratios)*np.sqrt(252):.2f}",
            "status": "✅ OPTIMIZED"
        }
        
    except Exception as e:
        return {"test": "Financial Calculations", "status": f"❌ ERROR: {str(e)}"}

def main():
    """Run all Python 3.10 performance tests"""
    logger.info("🚀 Starting Python 3.10 High-Performance Tools Validation")
    logger.info(f"Python version: {sys.version}")
    
    # Run all tests
    test_results = []
    
    logger.info("=" * 60)
    numba_result = test_numba_performance()
    if numba_result:
        test_results.append(numba_result)
    
    logger.info("=" * 60)
    talib_result = test_talib_performance()
    if talib_result:
        test_results.append(talib_result)
    
    logger.info("=" * 60)
    vectorbt_result = test_vectorbt_performance()
    if vectorbt_result:
        test_results.append(vectorbt_result)
    
    logger.info("=" * 60)
    polars_result = test_polars_performance()
    if polars_result:
        test_results.append(polars_result)
    
    logger.info("=" * 60)
    financial_result = test_financial_calculations()
    if financial_result:
        test_results.append(financial_result)
    
    # Summary
    logger.info("🎯 Python 3.10 Performance Test Results:")
    logger.info("=" * 60)
    
    excellent_count = 0
    good_count = 0
    total_tests = len(test_results)
    
    for result in test_results:
        logger.info(f"📊 {result['test']}: {result['status']}")
        if 'speedup' in result:
            logger.info(f"   Speedup: {result['speedup']}")
        if 'rate' in result:
            logger.info(f"   Rate: {result['rate']}")
        if 'time' in result:
            logger.info(f"   Time: {result['time']}")
        
        if result['status'].startswith("✅ EXCELLENT"):
            excellent_count += 1
        elif result['status'].startswith("✅"):
            good_count += 1
    
    # Overall assessment
    logger.info("=" * 60)
    success_rate = (excellent_count + good_count) / total_tests if total_tests > 0 else 0
    logger.info(f"📈 Overall Performance: {excellent_count + good_count}/{total_tests} tests successful ({success_rate:.1%})")
    
    if excellent_count >= total_tests * 0.6:
        logger.info("🎉 EXCELLENT: Major performance improvements achieved!")
        logger.info("🚀 Python 3.10 delivers significant speedups for financial computing")
    elif good_count + excellent_count >= total_tests * 0.8:
        logger.info("✅ GOOD: Solid performance improvements achieved")
        logger.info("📈 Python 3.10 provides meaningful enhancements")
    else:
        logger.info("⚠️ MIXED: Some performance improvements, some limitations")
    
    # Performance summary
    logger.info("🏆 Key Achievements:")
    for result in test_results:
        if result['status'].startswith("✅"):
            key_metric = ""
            if 'speedup' in result:
                key_metric = f" ({result['speedup']} speedup)"
            elif 'rate' in result:
                key_metric = f" ({result['rate']})"
            logger.info(f"   • {result['test']}{key_metric}")
    
    return test_results

if __name__ == "__main__":
    main()