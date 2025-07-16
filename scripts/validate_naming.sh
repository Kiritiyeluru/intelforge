#!/bin/bash

# IntelForge Naming Convention Validator
# Usage: ./scripts/validate_naming.sh path/to/docs/

dir="$1"
if [ -z "$dir" ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

# Updated regex pattern for IntelForge naming convention (simplified from external source)
regex='^(STS|IMP|ARC|TSK|CFG|TST|RPT|REF|LOG)_[ABCD]_[A-Z0-9_]+_[0-9]{8}_v[0-9]+_[A-Z]{2}\.md$'

fail=0
total=0
valid=0

echo "🔍 Validating IntelForge naming convention in: $dir"
echo "Expected format: [CATEGORY]_[PRIORITY]_[DESCRIPTOR]_[YYYYMMDD]_v[VERSION]_[AUTHOR].md"
echo ""

for file in "$dir"/*.md "$dir"/*/*.md; do
    if [ -f "$file" ]; then
        base=$(basename "$file")
        total=$((total + 1))

        if [[ $base =~ $regex ]]; then
            echo "✅ Valid: $base"
            valid=$((valid + 1))
        else
            echo "❌ Invalid: $base"
            fail=1
        fi
    fi
done

echo ""
echo "📊 Summary: $valid/$total files follow naming convention"

if [ $fail -eq 1 ]; then
    echo "❌ Some files need to be renamed"
    exit 1
else
    echo "✅ All files follow naming convention"
    exit 0
fi
