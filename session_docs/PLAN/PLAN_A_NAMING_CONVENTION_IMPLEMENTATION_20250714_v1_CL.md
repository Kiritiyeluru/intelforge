---
project: INTELFORGE
category: PLAN
priority: A
date: 2025-07-14
version: 1
author: CL
tags:
  - naming-convention
  - documentation-standards
  - implementation-plan
  - best-practices
status: active
estimated_time: 4-6 hours
---

# IntelForge Naming Convention Implementation Plan

**Created:** 2025-07-14  
**Category:** PLAN (Planning)  
**Priority:** A (Critical/Urgent)  
**Author:** CL  
**Estimated Time:** 4-6 hours total implementation

## Overview

This document outlines the complete implementation plan for the IntelForge documentation naming convention system. The plan synthesizes industry best practices from multiple sources and provides a structured rollout approach to eliminate documentation chaos and establish enterprise-grade organization standards.

## 🎯 **Strategic Objectives**

1. **Eliminate Documentation Confusion**: Replace current 35+ files across 6 directories with organized, searchable structure
2. **Establish Industry Standards**: Implement proven naming conventions aligned with software development best practices
3. **Enable Automation**: Create tooling for validation, creation, and maintenance
4. **Future-Proof Scalability**: Design system that grows with project complexity
5. **Team Productivity**: Reduce time spent searching for documents by 50%+

## 📋 **Final Naming Convention System**

### **Template Structure**
```
[CATEGORY]_[PRIORITY]_[DESCRIPTOR]_[YYYYMMDD]_v[VERSION]_[AUTHOR].md
```

### **Category Codes (Optimized Set)**
| Code | Name | Purpose | Examples |
|------|------|---------|----------|
| `STS` | Status | Current project state and progress | Project status, current tasks |
| `IMP` | Implementation | Implementation guides and action plans | Bug fixes, feature implementations |
| `ARC` | Archive | Historical records and technical decisions | Completed phases, legacy docs |
| `TSK` | Tasks | Task lists and todos | Sprint tasks, action items |
| `CFG` | Configuration | Configuration and setup documentation | System configs, environment setup |
| `TST` | Testing | Testing plans and validation results | Test strategies, validation reports |
| `RPT` | Reports | Analysis reports and findings | Performance reports, assessments |
| `REF` | Reference | Reference materials and guides | Standards, guidelines, documentation |
| `LOG` | Logs | Session logs and handovers | Session summaries, handover docs |

### **Priority System**
- `A` - Critical/Urgent (blockers, current active work)
- `B` - High Priority (next sprint items, important features)
- `C` - Medium Priority (planned items, enhancements)
- `D` - Low Priority (future items, reference materials)

### **Author Codes**
- `CL` - Claude (AI assistant)
- `KR` - Kiriti (project owner)
- `SYS` - System generated

## 🗂️ **Folder Structure Design**

```
/session_docs/
  /STS/           # Status documents
  /IMP/           # Implementation guides
  /ARC/           # Archives & historical
  /TSK/           # Task lists
  /CFG/           # Configuration
  /TST/           # Testing documentation
  /RPT/           # Reports & analysis
  /REF/           # Reference materials
  /LOG/           # Session logs
  /templates/     # Document templates
  /archive/       # Date-based archives
    /2025-07-14/
    /2025-07-15/
```

## 📝 **YAML Frontmatter Standard**

Every document must include:

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

## 🚀 **Implementation Phases**

### **Phase 1: Core Infrastructure Setup (1-2 hours)**

#### **1.1 Create Folder Structure**
```bash
mkdir -p session_docs/{STS,IMP,ARC,TSK,CFG,TST,RPT,REF,LOG,templates,archive}
```

#### **1.2 Install Automation Scripts**
- [x] `validate_naming.sh` - Naming convention validator
- [x] `create_doc.sh` - Document creator with templates
- [x] `setup_git_hooks.sh` - Git hooks installer

#### **1.3 Setup Git Hooks**
```bash
./scripts/setup_git_hooks.sh
```

#### **1.4 Create Reference Documentation**
- [x] Naming convention guide
- [x] Implementation plan (this document)

### **Phase 2: Critical Files Migration (1 hour)**

#### **2.1 Rename Core Files**
```bash
# Current → New Structure
CURRENT_STATE.md → STS/STS_A_PROJECT_CURRENT_STATE_20250714_v1_CL.md
IMPLEMENTATION_GUIDE.md → IMP/IMP_A_IMPLEMENTATION_GUIDE_20250714_v1_CL.md
TECHNICAL_ARCHIVE.md → ARC/ARC_B_TECHNICAL_ARCHIVE_20250714_v1_CL.md
```

#### **2.2 Add YAML Frontmatter**
- Update all renamed files with metadata headers
- Ensure consistency across all core documents

#### **2.3 Update Navigation**
- Update INDEX.md with new file locations
- Update README.md references
- Update any internal cross-references

### **Phase 3: Archive Organization (1-2 hours)**

#### **3.1 Process Current Archive**
```bash
# Move existing archive to date-based structure
mv session_docs/archive_2025_07_14/* session_docs/archive/2025-07-14/
rmdir session_docs/archive_2025_07_14
```

#### **3.2 Apply Naming Convention to Archives**
- Rename archived files following convention
- Add metadata headers to important historical documents
- Create archive index for easy reference

#### **3.3 Validate Archive Structure**
```bash
./scripts/validate_naming.sh session_docs/archive/
```

### **Phase 4: Templates and Automation (1 hour)**

#### **4.1 Create Document Templates**
- Status report template
- Implementation plan template
- Task list template
- Testing report template

#### **4.2 VS Code Integration**
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

#### **4.3 Bash Aliases for Quick Access**
```bash
alias ifg-create='./scripts/create_doc.sh'
alias ifg-validate='./scripts/validate_naming.sh session_docs/'
alias ifg-status='find session_docs/STS -name "*.md" | sort'
```

### **Phase 5: Validation and Testing (30 minutes)**

#### **5.1 Run Complete Validation**
```bash
./scripts/validate_naming.sh session_docs/
```

#### **5.2 Test Document Creation**
```bash
./scripts/create_doc.sh TST A "NAMING_CONVENTION_TEST" CL
```

#### **5.3 Test Git Hooks**
```bash
git add session_docs/
git commit -m "Test naming convention validation"
```

## 🔧 **Automation Tools**

### **Available Scripts**
1. **validate_naming.sh** - Validates filename compliance
2. **create_doc.sh** - Creates properly named documents with templates
3. **setup_git_hooks.sh** - Installs pre-commit validation hooks

### **Usage Examples**
```bash
# Create new implementation document
./scripts/create_doc.sh IMP A "CANARY_VALIDATOR_FIX" CL "bugfix,critical"

# Validate all documents
./scripts/validate_naming.sh session_docs/

# Setup git validation
./scripts/setup_git_hooks.sh
```

## ✅ **Success Criteria**

### **Technical Criteria**
- [ ] All files follow naming convention (100% compliance)
- [ ] YAML frontmatter present in all documents
- [ ] Git hooks validate on commit
- [ ] No broken internal references
- [ ] Archive structure organized by date

### **Usability Criteria**
- [ ] Documents findable in under 10 seconds
- [ ] Clear file purpose from filename alone
- [ ] Chronological sorting works correctly
- [ ] Team can create compliant documents easily

### **Business Criteria**
- [ ] 50%+ reduction in documentation search time
- [ ] Zero confusion about current project status
- [ ] Immediate identification of priorities
- [ ] Scalable system for future growth

## 🔄 **Maintenance Plan**

### **Weekly Tasks**
- Run naming validation on all documents
- Review and update priority levels
- Archive completed documents

### **Monthly Tasks**
- Clean up archive folders
- Update templates based on usage patterns
- Review category effectiveness

### **Quarterly Tasks**
- Assess system effectiveness
- Update naming guide based on lessons learned
- Consider new categories if needed

## 📊 **Expected Benefits**

### **Immediate Benefits (Week 1)**
- **Elimination of Confusion**: Clear project status and priorities
- **Faster Navigation**: Direct access to needed documents
- **Professional Appearance**: Industry-standard organization

### **Short-term Benefits (Month 1)**
- **Reduced Search Time**: 50%+ improvement in document discovery
- **Better Collaboration**: Clear communication through organized docs
- **Automated Quality**: Git hooks prevent naming violations

### **Long-term Benefits (Quarter 1)**
- **Scalability**: System grows with project complexity
- **Team Efficiency**: New developers onboard faster
- **Knowledge Management**: Historical information easily accessible
- **Process Automation**: Scripts handle routine documentation tasks

## 🚨 **Risk Mitigation**

### **Potential Risks**
1. **Team Adoption**: Resistance to new naming system
2. **Migration Errors**: Breaking existing references during rename
3. **Tool Complexity**: Scripts too complex for team to maintain

### **Mitigation Strategies**
1. **Gradual Rollout**: Phase-based implementation with validation
2. **Reference Validation**: Check all links before and after migration
3. **Simple Tools**: Keep scripts minimal and well-documented

## 🎯 **Next Steps**

### **Immediate Actions (Today)**
1. Execute Phase 1: Create folder structure and install scripts
2. Execute Phase 2: Rename and update critical files
3. Update CLAUDE.md with naming convention reference

### **This Week**
1. Complete Phases 3-5: Archive organization and validation
2. Train team on new system
3. Document lessons learned

### **This Month**
1. Monitor system effectiveness
2. Refine templates based on usage
3. Consider additional automation opportunities

---

## 📚 **References**

### **Source Documents**
- `/external tips/naming conventions and metadata standards for documents.md`
- `/external tips/turbo‑charge your IntelForge naming convention.md`
- `/external tips/naming convention system.md`

### **Industry Standards Referenced**
- ISO 8601 date formatting
- YAML frontmatter specification
- Git hooks best practices
- Software documentation standards

### **Implementation Files**
- `scripts/validate_naming.sh`
- `scripts/create_doc.sh`
- `scripts/setup_git_hooks.sh`
- `session_docs/IFG_NAMING_GUIDE_20250714_v1_CL.md`

---

*This implementation plan ensures IntelForge documentation becomes a strategic asset rather than a maintenance burden, following industry best practices and enabling long-term scalability.*