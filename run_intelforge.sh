#!/bin/bash
# IntelForge Production Startup Script
# Automatically activates correct virtual environment and runs commands

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

echo -e "${BLUE}🚀 IntelForge Production Startup${NC}"
echo -e "${BLUE}=================================${NC}"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Virtual environment not found at .venv${NC}"
    echo -e "${YELLOW}Run: uv sync${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}✅ Activating virtual environment...${NC}"
source .venv/bin/activate

# Verify Python environment
echo -e "${GREEN}✅ Python: $(python --version)${NC}"
echo -e "${GREEN}✅ Environment: $(which python)${NC}"

# Parse command line arguments
COMMAND=${1:-"test"}

case $COMMAND in
    "test")
        echo -e "${BLUE}🧪 Running comprehensive tests...${NC}"
        python scripts/comprehensive_test_runner.py
        ;;
    "monitor")
        echo -e "${BLUE}📊 Starting monitoring dashboard...${NC}"
        python scripts/enhanced_monitoring.py --financial
        ;;
    "scrape")
        echo -e "${BLUE}🕷️ Starting batch scraping...${NC}"
        python scripts/batch_stealth_scraper.py
        ;;
    "ai")
        echo -e "${BLUE}🤖 Running AI processing...${NC}"
        python scripts/phase_08_ai_processor.py --search "${2:-algorithmic trading}"
        ;;
    "financial")
        echo -e "${BLUE}💰 Running financial analysis...${NC}"
        python scripts/enhanced_monitoring.py --market
        ;;
    "help")
        echo -e "${GREEN}Available commands:${NC}"
        echo -e "  ${YELLOW}test${NC}      - Run comprehensive system tests"
        echo -e "  ${YELLOW}monitor${NC}    - Start monitoring dashboard"
        echo -e "  ${YELLOW}scrape${NC}     - Run batch scraping"
        echo -e "  ${YELLOW}ai${NC}         - Run AI processing with search query"
        echo -e "  ${YELLOW}financial${NC}  - Run financial market analysis"
        echo -e "  ${YELLOW}help${NC}       - Show this help message"
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo -e "${YELLOW}Run: ./run_intelforge.sh help${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ IntelForge operation completed${NC}"