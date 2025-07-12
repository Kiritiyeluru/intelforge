#!/bin/bash
# Setup file watcher for automatic article organization

echo "Setting up article auto-organizer..."

# Install required Python packages
echo "Installing PyYAML if needed..."
pip install pyyaml

# Make scripts executable
chmod +x ../phase_07_article_organizer.py

echo "Setup complete!"
echo ""
echo "Usage:"
echo "  # Test organization (safe)"
echo "  python ../phase_07_article_organizer.py --dry-run"
echo ""
echo "  # Organize articles once"
echo "  python ../phase_07_article_organizer.py"
echo ""  
echo "  # Watch for new files continuously"
echo "  python ../phase_07_article_organizer.py --watch"
echo ""
echo "Drop new .md files in knowledge_management/intake/ folder"