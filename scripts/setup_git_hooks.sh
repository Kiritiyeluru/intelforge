#!/bin/bash

# IntelForge Git Hooks Setup Script

echo "🔧 Setting up IntelForge git hooks..."

# Create pre-commit hook for naming convention validation
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

# IntelForge Pre-commit Hook - Naming Convention Validation
# Validates markdown files follow naming convention before commit

echo "🔍 IntelForge: Validating naming convention..."

# Get staged markdown files in session_docs
staged_files=$(git diff --cached --name-only | grep '\.md$' | grep -E '^session_docs/')

if [ -z "$staged_files" ]; then
    echo "✅ No markdown files in session_docs to validate"
    exit 0
fi

# Run validation on staged files
./scripts/validate_naming.sh session_docs/

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Naming convention validation failed!"
    echo "Please rename files to follow IntelForge naming convention:"
    echo "[CATEGORY]_[PRIORITY]_[DESCRIPTOR]_[YYYYMMDD]_v[VERSION]_[AUTHOR].md"
    echo ""
    echo "Use: ./scripts/create_doc.sh to create properly named documents"
    echo "See: session_docs/IFG_NAMING_GUIDE_20250714_v1_CL.md for details"
    exit 1
fi

echo "✅ All files follow naming convention"
exit 0
EOF

# Make hook executable
chmod +x .git/hooks/pre-commit

echo "✅ Pre-commit hook installed successfully"
echo "📋 Hook will validate naming convention on markdown files in session_docs/"