#!/bin/bash
# Setup AI processing for knowledge management

echo "🧠 Setting up AI processing for IntelForge Knowledge Management..."
echo ""

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

if (( $(echo "$python_version >= 3.8" | bc -l) )); then
    echo "✅ Python version compatible"
else
    echo "❌ Python 3.8+ required"
    exit 1
fi

# Install required packages
echo ""
echo "📦 Installing required packages..."
pip install sentence-transformers faiss-cpu numpy

echo ""
echo "🧪 Testing installation..."
python3 -c "
import sentence_transformers
import faiss
import numpy as np
print('✅ All packages installed successfully')
print('Model will be downloaded on first use (~90MB)')
"

echo ""
echo "🚀 Setup complete!"
echo ""
echo "Usage:"
echo "  # Build embeddings (one-time setup)"
echo "  python phase_08_ai_processor.py --build"
echo ""
echo "  # Test with dry run first"
echo "  python phase_08_ai_processor.py --build --dry-run"
echo ""
echo "  # Search articles"
echo "  python phase_08_ai_processor.py --search 'MCP servers'"
echo "  python phase_08_ai_processor.py --search 'web scraping tools'"
echo ""
echo "📝 First build will download ~90MB embedding model"
echo "🔍 Vector database will be stored in knowledge_management/vector_db/"
