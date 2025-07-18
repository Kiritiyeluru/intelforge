#!/bin/bash
# IntelForge Analytics Dashboard Startup Script

set -e

echo "🚀 Starting IntelForge Analytics Dashboard..."

# Check if we're in the right directory
if [ ! -f "dashboard/app.py" ]; then
    echo "❌ Error: Please run this script from the IntelForge root directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "dashboard/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv dashboard/venv
fi

# Activate virtual environment
source dashboard/venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r dashboard/requirements.txt

# Create necessary directories
mkdir -p logs
mkdir -p reports
mkdir -p dashboard/templates

# Set environment variables
export FLASK_APP=dashboard/app.py
export FLASK_ENV=development

# Check if monitoring system is configured
if [ ! -f "logs/crawler_metrics.json" ]; then
    echo "⚠️  Warning: No crawler metrics found. Dashboard will show limited data."
    echo "   Run the crawler first to generate metrics."
fi

# Start the dashboard
echo "🖥️  Starting dashboard on http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo ""

python dashboard/app.py
