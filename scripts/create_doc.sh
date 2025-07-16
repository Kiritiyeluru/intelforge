#!/bin/bash

# IntelForge Document Creator
# Usage: ./create_doc.sh CATEGORY PRIORITY "DESCRIPTOR" AUTHOR [TAGS]

CATEGORY=$1
PRIORITY=$2
DESC=$3
AUTHOR=$4
TAGS=${5:-""}

if [ -z "$CATEGORY" ] || [ -z "$PRIORITY" ] || [ -z "$DESC" ] || [ -z "$AUTHOR" ]; then
    echo "Usage: $0 CATEGORY PRIORITY \"DESCRIPTOR\" AUTHOR [TAGS]"
    echo "Example: $0 IMP A \"CANARY_VALIDATOR_FIX\" CL \"bugfix,critical\""
    echo ""
    echo "Categories: STS, IMP, ARC, TSK, PLAN, RPT, CFG, TEST, LOG"
    echo "Priorities: A (Critical), B (High), C (Medium), D (Low)"
    exit 1
fi

DATE=$(date +%Y%m%d)
FILENAME="${CATEGORY}_${PRIORITY}_${DESC}_${DATE}_v1_${AUTHOR}.md"

# Create category directory if it doesn't exist
mkdir -p "session_docs/${CATEGORY}"

# Convert tags to YAML array format
if [ -n "$TAGS" ]; then
    TAG_ARRAY=$(echo "$TAGS" | sed 's/,/\n  - /g' | sed 's/^/  - /')
else
    TAG_ARRAY="  []"
fi

# Create file with metadata template
cat <<EOF > "session_docs/${CATEGORY}/${FILENAME}"
---
project: INTELFORGE
category: ${CATEGORY}
priority: ${PRIORITY}
date: ${DATE:0:4}-${DATE:4:2}-${DATE:6:2}
version: 1
author: ${AUTHOR}
tags:
${TAG_ARRAY}
status: draft
estimated_time: ""
---

# ${DESC//_/ }

**Created:** $(date +%Y-%m-%d)
**Category:** ${CATEGORY} ($(get_category_name $CATEGORY))
**Priority:** ${PRIORITY} ($(get_priority_name $PRIORITY))
**Author:** ${AUTHOR}

## Overview

[Brief description of document purpose]

## Contents

[Document content goes here]

---

*Generated with IntelForge document creator*
EOF

echo "✅ Created: session_docs/${CATEGORY}/${FILENAME}"
echo "📁 Location: $(pwd)/session_docs/${CATEGORY}/${FILENAME}"

# Helper functions for display names
get_category_name() {
    case $1 in
        STS) echo "Status" ;;
        IMP) echo "Implementation" ;;
        ARC) echo "Archive" ;;
        TSK) echo "Tasks" ;;
        PLAN) echo "Planning" ;;
        RPT) echo "Reports" ;;
        CFG) echo "Configuration" ;;
        TEST) echo "Testing" ;;
        LOG) echo "Logs" ;;
        *) echo "Unknown" ;;
    esac
}

get_priority_name() {
    case $1 in
        A) echo "Critical/Urgent" ;;
        B) echo "High Priority" ;;
        C) echo "Medium Priority" ;;
        D) echo "Low Priority" ;;
        *) echo "Unknown" ;;
    esac
}
