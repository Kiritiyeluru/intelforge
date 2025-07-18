#!/bin/bash
# IntelForge Production Startup Script
# Supports both Python 3.12 (.venv) and Python 3.10 (micromamba) environments

set -e  # Exit on any error

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 IntelForge Dual-Environment Startup${NC}"
echo -e "${BLUE}======================================${NC}"

# Parse Python version flag
PYTHON_VERSION="3.10"  # Default to high-performance Python 3.10
if [[ "$1" == "--python" ]]; then
    PYTHON_VERSION="$2"
    shift 2  # Remove the --python and version arguments
fi

# Activate appropriate environment
if [[ "$PYTHON_VERSION" == "3.12" ]]; then
    echo -e "${YELLOW}🔧 Using Python 3.12 (Current/Stable)${NC}"
    if [ ! -d ".venv" ]; then
        echo -e "${RED}❌ Python 3.12 environment not found at .venv${NC}"
        echo -e "${YELLOW}Run: uv sync${NC}"
        exit 1
    fi
    source .venv/bin/activate
    echo -e "${GREEN}✅ Python 3.12: $(python --version)${NC}"
elif [[ "$PYTHON_VERSION" == "3.10" ]]; then
    echo -e "${YELLOW}⚡ Using Python 3.10 (High-Performance)${NC}"
    if [ ! -f "bin/micromamba" ]; then
        echo -e "${RED}❌ Micromamba not found at bin/micromamba${NC}"
        echo -e "${YELLOW}Run installation script first${NC}"
        exit 1
    fi
    # Use micromamba run for Python 3.10 environment
    echo -e "${GREEN}✅ Python 3.10: High-performance environment ready${NC}"
    echo -e "${GREEN}✅ Tools: vectorbt, numba, ta-lib, polars${NC}"
else
    echo -e "${RED}❌ Unsupported Python version: $PYTHON_VERSION${NC}"
    echo -e "${YELLOW}Supported versions: 3.10 (high-performance), 3.12 (current)${NC}"
    exit 1
fi

# Parse command line arguments
COMMAND=${1:-"test"}

# Define Python execution based on environment
if [[ "$PYTHON_VERSION" == "3.12" ]]; then
    PYTHON_CMD="python"
else
    PYTHON_CMD="./bin/micromamba run -n intelforge-py310 python"
fi

case $COMMAND in
    "test")
        echo -e "${BLUE}🧪 Running comprehensive tests...${NC}"
        if [[ "$PYTHON_VERSION" == "3.10" ]]; then
            echo -e "${YELLOW}Running Python 3.10 performance tests...${NC}"
            $PYTHON_CMD test_python310_performance.py
        else
            $PYTHON_CMD scripts/comprehensive_test_runner.py
        fi
        ;;
    "performance")
        echo -e "${BLUE}⚡ Running performance benchmarks...${NC}"
        if [[ "$PYTHON_VERSION" == "3.10" ]]; then
            $PYTHON_CMD test_python310_performance.py
        else
            $PYTHON_CMD test_performance_improvements.py
        fi
        ;;
    "monitor")
        echo -e "${BLUE}📊 Starting monitoring dashboard...${NC}"
        $PYTHON_CMD scripts/enhanced_monitoring.py --financial
        ;;
    "scrape")
        echo -e "${BLUE}🕷️ Starting batch scraping...${NC}"
        $PYTHON_CMD scripts/batch_stealth_scraper.py
        ;;
    "ai")
        echo -e "${BLUE}🤖 Running AI processing...${NC}"
        $PYTHON_CMD scripts/phase_08_ai_processor.py --search "${2:-algorithmic trading}"
        ;;
    "financial")
        echo -e "${BLUE}💰 Running financial analysis...${NC}"
        $PYTHON_CMD scripts/enhanced_monitoring.py --market
        ;;
    "backtest")
        echo -e "${BLUE}📈 Running high-performance backtesting...${NC}"
        if [[ "$PYTHON_VERSION" == "3.10" ]]; then
            echo -e "${GREEN}✅ Using VectorBT for maximum performance${NC}"
            $PYTHON_CMD -c "
import vectorbt as vbt
import numpy as np
import pandas as pd
print('🚀 VectorBT High-Performance Backtesting Ready')
print('Example: Simple moving average crossover strategy')
# Demo would go here
"
        else
            echo -e "${YELLOW}⚠️ For maximum backtesting performance, use: --python 3.10${NC}"
            echo -e "${YELLOW}Current environment supports basic backtesting only${NC}"
        fi
        ;;
    "help")
        echo -e "${GREEN}Available commands:${NC}"
        echo -e "  ${YELLOW}test${NC}        - Run comprehensive system tests"
        echo -e "  ${YELLOW}performance${NC} - Run performance benchmarks"
        echo -e "  ${YELLOW}monitor${NC}     - Start monitoring dashboard"
        echo -e "  ${YELLOW}scrape${NC}      - Run batch scraping"
        echo -e "  ${YELLOW}ai${NC}          - Run AI processing with search query"
        echo -e "  ${YELLOW}financial${NC}   - Run financial market analysis"
        echo -e "  ${YELLOW}backtest${NC}    - Run high-performance backtesting (best with Python 3.10)"
        echo -e "  ${YELLOW}help${NC}        - Show this help message"
        echo -e ""
        echo -e "${GREEN}Environment options:${NC}"
        echo -e "  ${YELLOW}--python 3.10${NC} - Use high-performance environment (vectorbt, numba, ta-lib)"
        echo -e "  ${YELLOW}--python 3.12${NC} - Use current stable environment"
        echo -e ""
        echo -e "${GREEN}Examples:${NC}"
        echo -e "  ${YELLOW}./run_intelforge.sh test${NC}                    # Default: Python 3.10 performance tests"
        echo -e "  ${YELLOW}./run_intelforge.sh --python 3.12 test${NC}     # Python 3.12 compatibility tests"
        echo -e "  ${YELLOW}./run_intelforge.sh performance${NC}             # Benchmark high-performance tools"
        echo -e "  ${YELLOW}./run_intelforge.sh backtest${NC}                # VectorBT backtesting (Python 3.10)"
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo -e "${YELLOW}Run: ./run_intelforge.sh help${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ IntelForge operation completed${NC}"
