---
project: INTELFORGE
category: REF
priority: A
date: 2025-07-14
version: 1
author: CL
tags:
  - naming-convention
  - documentation-standards
  - best-practices
status: active
estimated_time: ""
---

# IntelForge Documentation Naming Convention Guide

**Created:** 2025-07-14  
**Category:** REF (Reference)  
**Priority:** A (Critical/Urgent)  
**Author:** CL  

## Overview

This document establishes the comprehensive naming convention system for IntelForge documentation, based on industry standards and best practices. The system ensures consistency, searchability, and scalability across all project documentation.

## 🎯 **Core Naming Template**

```
[CATEGORY]_[PRIORITY]_[DESCRIPTOR]_[YYYYMMDD]_v[VERSION]_[AUTHOR].md
```

### **Example**
```
IMP_A_CANARY_VALIDATOR_FIX_20250714_v1_CL.md
```

## 📋 **Component Definitions**

### **Categories (3-4 letters)**
| Code | Name | Purpose |
|------|------|---------|
| `STS` | Status | Current project state and progress |
| `IMP` | Implementation | Implementation guides and action plans |
| `ARC` | Archive | Historical records and technical decisions |
| `TSK` | Tasks | Task lists and todos |
| `PLAN` | Planning | Planning documents and roadmaps |
| `RPT` | Reports | Analysis reports and findings |
| `CFG` | Configuration | Configuration and setup documentation |
| `TEST` | Testing | Testing plans and validation results |
| `LOG` | Logs | Session logs and handovers |

### **Priority Levels (1 letter)**
| Code | Name | Description |
|------|------|-------------|
| `A` | Critical/Urgent | Blockers, current active work |
| `B` | High Priority | Next sprint items, important features |
| `C` | Medium Priority | Planned items, enhancements |
| `D` | Low Priority | Future items, reference materials |

### **Descriptors**
- Use UPPERCASE with underscores
- Be descriptive but concise (max 25 characters)
- Use clear, searchable keywords
- Examples: `PROJECT_STATUS`, `CANARY_VALIDATOR_FIX`, `SEMANTIC_CRAWLER_PLAN`

### **Date Format**
- Use ISO 8601: `YYYYMMDD`
- Ensures chronological sorting
- Example: `20250714` for July 14, 2025

### **Version**
- Start with `v1`, increment as `v2`, `v3`, etc.
- Use `v1_DRAFT` for work in progress
- Use `v1_FINAL` for approved versions

### **Author Codes**
| Code | Author |
|------|--------|
| `KR` | Kiriti (project owner) |
| `CL` | Claude (AI assistant) |
| `SYS` | System generated |

## 🗂️ **Folder Structure**

### **Hierarchical Organization**
```
/session_docs/
  /STS/           # Status documents
  /IMP/           # Implementation guides
  /ARC/           # Archives & historical
  /TSK/           # Task lists
  /PLAN/          # Planning documents
  /RPT/           # Reports & analysis
  /CFG/           # Configuration
  /TEST/          # Testing documentation
  /LOG/           # Session logs
  /archive/       # Date-based archives
    /2025-07-14/
    /2025-07-15/
  /templates/     # Document templates
```

### **Archive Strategy**
- Move completed/outdated files to `/archive/YYYY-MM-DD/`
- Maintain original folder structure within archives
- Keep current working files in category folders

## 📝 **YAML Frontmatter Standard**

Every document must include metadata header:

```yaml
---
project: INTELFORGE
category: [CATEGORY]
priority: [PRIORITY]
date: YYYY-MM-DD
version: [NUMBER]
author: [AUTHOR_CODE]
tags:
  - [tag1]
  - [tag2]
status: [draft|active|completed|archived]
estimated_time: "[time estimate]"
---
```

### **Metadata Fields**
- `project`: Always "INTELFORGE"
- `category`: Document category (STS, IMP, etc.)
- `priority`: Priority level (A, B, C, D)
- `date`: Creation/last update date
- `version`: Version number
- `author`: Author code
- `tags`: Searchable keywords
- `status`: Current document status
- `estimated_time`: Time estimate for implementation

## 🔧 **Automation Tools**

### **Document Creator**
```bash
./scripts/create_doc.sh IMP A "CANARY_VALIDATOR_FIX" CL "bugfix,critical"
```

### **Naming Validator**
```bash
./scripts/validate_naming.sh session_docs/
```

### **VS Code Snippet**
Add to `.vscode/snippets.json`:
```json
{
  "IntelForge Doc": {
    "prefix": "ifg-doc",
    "body": [
      "---",
      "project: INTELFORGE",
      "category: $1",
      "priority: $2",
      "date: ${CURRENT_YEAR}-${CURRENT_MONTH}-${CURRENT_DAY}",
      "version: 1",
      "author: $3",
      "tags: []",
      "status: draft",
      "estimated_time: \"\"",
      "---",
      "",
      "# $4"
    ]
  }
}
```

## ✅ **Validation Checklist**

Before creating/committing any document:

- [ ] Filename follows exact template format
- [ ] Category code is valid (STS, IMP, ARC, etc.)
- [ ] Priority is appropriate (A, B, C, D)
- [ ] Date is in YYYYMMDD format
- [ ] Version starts with v1
- [ ] Author code is correct
- [ ] YAML frontmatter is complete
- [ ] File is in correct category folder
- [ ] No spaces or special characters in filename
- [ ] Descriptor is clear and searchable

## 🎯 **Benefits**

### **Immediate Benefits**
- **Zero Confusion**: Purpose, priority, and date clear from filename
- **Automatic Sorting**: Files sort chronologically and by priority
- **Easy Search**: Structured naming enables powerful search
- **Version Control**: Built-in versioning prevents conflicts

### **Long-term Benefits**
- **Scalability**: System grows with project complexity
- **Team Onboarding**: New developers understand structure immediately
- **Automation**: Scripts can process files by naming patterns
- **Professional Standards**: Aligns with industry best practices

## 📊 **Examples**

### **Current Implementation (Renamed)**
```
STS/STS_A_PROJECT_CURRENT_STATE_20250714_v1_CL.md
IMP/IMP_A_IMPLEMENTATION_GUIDE_20250714_v1_CL.md
ARC/ARC_B_TECHNICAL_ARCHIVE_20250714_v1_CL.md
```

### **Future Documents**
```
TSK/TSK_A_CANARY_VALIDATOR_TASKS_20250714_v1_KR.md
PLAN/PLAN_B_SEMANTIC_CRAWLER_ROADMAP_20250714_v1_CL.md
RPT/RPT_C_PERFORMANCE_ANALYSIS_20250714_v1_SYS.md
TEST/TEST_A_VALIDATION_FRAMEWORK_20250714_v1_CL.md
```

## 🚀 **Implementation Timeline**

### **Phase 1: Core Setup (Immediate)**
- [x] Create naming guide document
- [x] Create automation scripts
- [ ] Rename 3 critical files
- [ ] Create category folders
- [ ] Update navigation references

### **Phase 2: Migration (Week 1)**
- [ ] Apply naming convention to all current documents
- [ ] Set up archive structure
- [ ] Create document templates
- [ ] Add VS Code snippets

### **Phase 3: Enforcement (Week 2)**
- [ ] Add pre-commit hooks
- [ ] Create validation CI checks
- [ ] Train team on new system
- [ ] Document migration procedures

## 🔄 **Maintenance**

### **Regular Tasks**
- Run validation script weekly
- Archive completed documents monthly
- Update naming guide as needed
- Review and optimize folder structure quarterly

### **Version Updates**
- Update guide version when making changes
- Maintain backward compatibility
- Document all changes in git history
- Notify team of updates

---

*This naming convention system ensures IntelForge documentation remains organized, searchable, and scalable as the project grows.*