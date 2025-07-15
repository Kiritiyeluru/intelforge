# 📁 IntelForge Doc Tools

## ✅ Validation Script: `validate_naming.sh`

```bash
#!/bin/bash
# Checks filenames for IntelForge naming convention compliance
# Format: [CATEGORY]_[PRIORITY]_[DESCRIPTOR]_[YYYYMMDD]_v[VERSION]_[AUTHOR].md

REGEX='^(STS|IMP|ARC|TSK|CFG|TST|RPT|REF|LOG)_[ABCD]_[A-Z0-9_]+_[0-9]{8}_v[0-9]+_[A-Z]{2}\.md$'

FAILED=0

for file in "$@"
do
  filename=$(basename "$file")
  if [[ ! $filename =~ $REGEX ]]; then
    echo "❌ Invalid file: $filename"
    FAILED=1
  else
    echo "✅ Valid file: $filename"
  fi
done

exit $FAILED
```

## 🧩 YAML Metadata Template (in each .md file)

```markdown
---
project: INTELFORGE
category: IMP
priority: A
date: 2025-07-14
version: 1
author: CL
tags:
  - canary-validator
  - bugfix
  - critical
status: active
estimated_time: 30min
---
```

## 🛠️ Automation Script: `create_doc.sh`

```bash
#!/bin/bash
# Usage: ./create_doc.sh IMP A "CRAWLER_REFACTOR_PLAN" 20250714 1 CL
CATEGORY=$1
PRIORITY=$2
DESC=$3
DATE=$4
VERSION=$5
AUTHOR=$6

FILENAME="${CATEGORY}_${PRIORITY}_${DESC}_${DATE}_v${VERSION}_${AUTHOR}.md"

cat <<EOF > $FILENAME
---
project: INTELFORGE
category: $CATEGORY
priority: $PRIORITY
date: ${DATE:0:4}-${DATE:4:2}-${DATE:6:2}
version: $VERSION
author: $AUTHOR
tags: []
status: active
estimated_time: 
---

# ${DESC//_/ }

> Created on $(date +%Y-%m-%d)
EOF

echo "✅ Created $FILENAME"
```

## 📁 Folder Structure (Standard)

```
/session_docs/
  /STS/    # Status documents
  /IMP/    # Implementation guides
  /ARC/    # Archives & historical
  /TSK/    # Task lists
  /PLAN/   # Planning documents
  /RPT/    # Reports & analysis
  /archive/
    /2025-07-14/
    /2025-07-15/
```

## 🔍 Example Filenames

```
IMP_A_CRAWLER_REFACTOR_PLAN_20250714_v1_CL.md
STS_A_PROJECT_CURRENT_STATE_20250714_v1_CL.md
ARC_D_PHASE1_CLOSURE_SUMMARY_20250701_v1_KY.md
```

## ✅ Implementation Steps

**Phase 1: Rename Critical Files**
```
CURRENT_STATE.md → STS/STS_A_PROJECT_CURRENT_STATE_20250714_v1_CL.md
IMPLEMENTATION_GUIDE.md → IMP/IMP_A_IMPLEMENTATION_GUIDE_20250714_v1_CL.md
TECHNICAL_ARCHIVE.md → ARC/ARC_B_TECHNICAL_ARCHIVE_20250714_v1_CL.md
```

**Phase 2: Standardize Metadata & Templates**
- Add YAML metadata to all new and key existing files

**Phase 3: Enable Git Hooks** (optional)
- Add `validate_naming.sh` to a pre-commit hook
- Run on `docs/` or `session_docs/` folder

```bash
# .git/hooks/pre-commit
scripts/validate_naming.sh $(git diff --cached --name-only | grep '\.md$')
```

**Phase 4: Integrate Templates**
- Use `create_doc.sh` for all new documentation entries
- Add editor aliases or `.bash_aliases` helpers

---

Let me know if you'd like me to also add a metadata extractor or GitHub README template for this system.
