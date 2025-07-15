Here’s how you can **turbo‑charge your IntelForge naming convention**—keeping it clean, scalable, and in line with industry best practices—all without bloating:

---

## 📚 1. Add **YAML Frontmatter Metadata**

Embed metadata inside each file for clarity, searchability, and automation.

**Example at top of `IMP_A_CANARY_VALIDATOR_FIX_20250714_v1.md`:**

```yaml
---
project: INTELFORGE
category: IMP
priority: A
date: 2025-07-14
version: 1
author: KR
tags:
  - validator
  - bugfix
---
```

**Benefits:**

* Makes files self-descriptive and machine-readable
* Enables tooling: automatic TOCs, metadata export, or scripts&#x20;

---

## 🗂️ 2. Combine Naming with Folder Hierarchy

Use both filenames and folder structure to reduce redundancy.

```
/docs
  /STS/
    STS_A_PROJECT_CURRENT_STATE_20250714_v1.md
  /IMP/
    IMP_A_CANARY_VALIDATOR_FIX_20250714_v1.md
  /ARC/
```

**Why?**
Folders indicate broad categories; filenames handle specifics. Less noise, easier navigation .

---

## 🔧 3. Add **Name Validation with Pre-commit Hooks**

Use a simple shell/Python script to enforce your naming rules.

Grab before commit:

```bash
scripts/validate_naming.sh READMES ARCHIVE IMP STS ARC
```

Fail on mismatches. Helps you catch typos and inconsistencies early ([datamanagement.hms.harvard.edu][1]).

---

## 🧾 4. Use **File Templates / Snippets**

For VS Code, add a snippet to auto-create new doc:

```json
"IntelForge Doc": {
  "prefix": "intel-doc",
  "body": [
    "---",
    "project: INTELFORGE",
    "category: $1",
    "priority: $2",
    "date: ${CURRENT_YEAR}-${CURRENT_MONTH}-${CURRENT_DAY}",
    "version: 1",
    "author: KR",
    "tags: []",
    "---",
    "",
    "# $3"
  ]
}
```

Streamlines new doc creation and keeps formats consistent.

---

## ⏳ 5. Use **ISO Date Ordering and Zero-Padding**

Stick to `YYYYMMDD` or `YYYY-MM-DD`.
Use versioning like `v01`, `v02` for future-proofing and easy alphabetical sorting ([Canto][2], [Luca Pallotta][3], [GitHub][4]).

---

## 🧹 6. Normalize Case and Remove Special Characters

Use uppercase for category codes, snake\_case for descriptors.
Avoid spaces, slashes, or unusual punctuation ([hivo.co][5]).

---

## 💾 7. Archive Structure with Date Subfolders

Instead of dumping into one archive folder, use:

```
archive/2025-07-14/...
```

Keeps old files cleanly separated and easy to retrieve. Suggested here .

---

## ⚙️ 8. Integrate with Your Editor and CI/CD

* **VS Code**: Metadata hover panels, tasks to enforce naming
* **CI/CD**: Lint names on pull requests, disallow bad filenames
* **Scripts**: Export metadata for project dashboards or tracking

---

### 🔁 Recap: Full Best-Practice System

1. **Folders** by category (`STS/`, `IMP/`, `ARC/`)
2. **Filename**: `CATEGORY_PRIORITY_DESCRIPTOR_YYYYMMDD_v01_[AUTH].md`
3. **Top Metadata block** using YAML frontmatter
4. **Pre-commit hook** to validate naming rules
5. **Snippets/templates** for consistent creation
6. **Zero special characters**, ISO dates, padded versions
7. **Archive date subfolders**
8. **CI/editor integration** for automated sanity checks

---

### 🏁 Outcome:

* ✅ Human- and machine-readable docs
* ✅ No guesswork — category, priority, date, version obvious
* ✅ Tools can automate metadata extraction, summaries, dashboards
* ✅ Team-wide consistency with minimal manual effort

---

Here's your metadata + validation bundle for IntelForge documentation:
## 📁 File: scripts/validate_naming.sh

#!/bin/bash

# IntelForge Naming Convention Validator
# Usage: ./scripts/validate_naming.sh path/to/docs/

dir="$1"
regex='^(STS|IMP|ARC|TSK|CFG|TST|RPT|REF|LOG)_[A-D]_[A-Z0-9_]+_[0-9]{8}_v[0-9]+\.md$'

fail=0

for file in "$dir"/*.md; do
  base=$(basename "$file")
  if [[ ! $base =~ $regex ]]; then
    echo "❌ Invalid filename: $base"
    fail=1
  else
    echo "✅ Valid filename: $base"
  fi
done

exit $fail
---
Here's your metadata + validation bundle for IntelForge documentation:

---

## ✅ Validation Script

A Bash script named `validate_naming.sh` (now saved in your project under `scripts/`) that checks whether your documentation filenames conform to your naming convention:

**Accepted format:**

```
[CATEGORY]_[PRIORITY]_[DESCRIPTOR]_[YYYYMMDD]_v[VERSION].md
```

Example:

```
IMP_A_CRAWLER_REFACTOR_PLAN_20250714_v1.md
```

---

## 🧩 Suggested Metadata Inclusion (inside each doc)

At the top of every `.md` file, embed this header block:

```markdown
<!--
DOC_META:
  Category: IMP (Implementation)
  Priority: A
  Descriptor: CRAWLER_REFACTOR_PLAN
  Date: 2025-07-14
  Version: v1
-->
```

You can later parse this block with scripts (e.g., YAML/regex) if needed for dashboards, changelogs, or documentation indices.

---

## 🚀 Automation (Optional Enhancements)

### Create Docs Script (Optional)

```bash
#!/bin/bash
# Usage: ./create_doc.sh IMP A "CRAWLER_REFACTOR_PLAN" 20250714 1

CATEGORY=$1
PRIORITY=$2
DESC=$3
DATE=$4
VERSION=$5

FILENAME="${CATEGORY}_${PRIORITY}_${DESC}_${DATE}_v${VERSION}.md"

cat <<EOF > $FILENAME
<!--
DOC_META:
  Category: $CATEGORY
  Priority: $PRIORITY
  Descriptor: $DESC
  Date: $DATE
  Version: v$VERSION
-->

# ${DESC//_/ }

> Created on $(date +%Y-%m-%d)

EOF

echo "✅ Created $FILENAME"
```

Let me know if you want this script added too, or integrated with your git pre-commit hooks.
