# IntelForge Guidance Hub

**📍 Essential project guidance documents organized for easy access and maximum impact**

This directory contains all crucial guidance documents reorganized from `/docs/` into logical categories based on usage patterns and development workflow needs.

---

## 🏛️ **Core Essentials** - Daily Development Reference

**Location:** `guidance/core_essentials/`
**Usage:** Consult these before/during development for immediate guidance

### 🔧 [find_vs_build.md](core_essentials/find_vs_build.md)
**Purpose:** Decision framework for build vs. reuse choices
**When to use:** Before implementing any new functionality
**Key sections:** Reuse checklist, build criteria, decision matrix

### 🚨 [troubleshooting_guide.md](core_essentials/troubleshooting_guide.md)
**Purpose:** Quick problem resolution reference
**When to use:** When encountering issues or errors
**Key sections:** Common problems, MCP issues, git workflow, quick fixes

### ⚡ [scraping_tools_recommendations.md](core_essentials/scraping_tools_recommendations.md)
**Purpose:** Comprehensive technical implementation guide
**When to use:** For tool selection, performance optimization, architecture decisions
**Key sections:** Performance benchmarks, Phase 2 roadmap, tool comparisons

---

## 📊 **Project Intelligence** - Knowledge Capture & Analysis

**Location:** `guidance/project_intelligence/`
**Usage:** Document insights, track decisions, monitor technical status

### 🎯 [decision_log.md](project_intelligence/decision_log.md)
**Purpose:** Architectural decisions with detailed rationale
**When to update:** After making any significant technical or architectural choice
**Key sections:** Tool selections, architecture patterns, trade-off analysis

### 🧠 [learning_log.md](project_intelligence/learning_log.md)
**Purpose:** Capture insights, discoveries, and lessons learned
**When to update:** After significant discoveries or completing development sessions
**Key sections:** Technical insights, process improvements, gotchas and solutions

### 📈 [dependency_report.md](project_intelligence/dependency_report.md)
**Purpose:** Auto-generated dependency analysis and warnings
**When to review:** After adding new dependencies or during health checks
**Key sections:** Package analysis, import warnings, security considerations

---

## ⚙️ **Operations** - Configuration & Automation Management

**Location:** `guidance/operations/`
**Usage:** Configuration management and long-term automation strategy

### 📝 [config_changelog.md](operations/config_changelog.md)
**Purpose:** Track configuration changes to prevent breaking changes
**When to update:** Every time configuration files are modified
**Key sections:** Change log template, impact analysis, rollback procedures

### 🤖 [claude_code_hooks_maintenance_plan.md](operations/claude_code_hooks_maintenance_plan.md)
**Purpose:** Comprehensive automation strategy with 9 intelligent hooks
**When to reference:** Planning automation improvements or implementing new hooks
**Key sections:** Hook implementation phases, dependency intelligence, code pattern enforcement

---

## 🚀 **Strategic Vision** - Future Planning & Roadmaps

**Location:** `guidance/strategic_vision/`
**Usage:** Long-term planning and architectural evolution

### 🔮 [Automated Knowledge Miner (AKM).md](strategic_vision/Automated%20Knowledge%20Miner%20(AKM).md)
**Purpose:** Comprehensive future development roadmap for intelligent knowledge extraction
**When to reference:** Planning major features or architectural evolution
**Key sections:** AKM system design, intelligence capabilities, integration roadmap

---

## 🛠️ **Development** - Methodology & Best Practices

**Location:** `guidance/development/`
**Usage:** Core development processes and methodologies for consistent AI-assisted development

### 📋 [Reusable_Development_Checklist_for_Each_Module.md](development/Reusable_Development_Checklist_for_Each_Module.md)
**Purpose:** 10-point checklist for every module development
**When to use:** Before implementing any new functionality
**Key sections:** Reuse over rebuild, AI-friendliness, modularity, testability

### 🏗️ [SOFTWARE_DEVELOPMENT_PROCESS.md](development/SOFTWARE_DEVELOPMENT_PROCESS.md)
**Purpose:** Professional software development process for solo developers with AI assistance
**When to use:** Planning development phases and maintaining quality standards
**Key sections:** Project initialization, development workflow, testing strategy

### ⚠️ [crucial_issues_to_address_proactively.md](development/crucial_issues_to_address_proactively.md)
**Purpose:** Proactive issue identification and prevention
**When to use:** Regular review sessions and before major changes
**Key sections:** Common pitfalls, prevention strategies, quality gates

### 📚 [general_Professional Software_Development_Process_Checklist.md](development/general_Professional%20Software_Development_Process_Checklist.md)
**Purpose:** Comprehensive development checklist
**When to use:** Project reviews and process improvement
**Key sections:** Planning, implementation, testing, deployment phases

---

## 🤖 **Automation** - GitHub Projects & Workflow Enhancement

**Location:** `guidance/automation/`
**Usage:** Automation strategies and GitHub integration for enhanced development workflow

### 🐙 [github-projects/README.md](automation/github-projects/README.md)
**Purpose:** GitHub Projects automation setup and usage
**When to reference:** Setting up project management automation
**Key sections:** Project board configuration, automation rules, workflow integration

### 📋 [github-projects/plan.md](automation/github-projects/plan.md)
**Purpose:** Detailed automation implementation plan
**When to reference:** Planning GitHub integration features
**Key sections:** Phase-based automation, issue templates, project management

---

## 🎯 **Quick Navigation Guide**

### **Starting a Development Session?**
1. **Check current status:** `session_docs/CURRENT_PROJECT_PLAN.md`
2. **Review active tasks:** Current project plan priorities
3. **Before coding:** `guidance/core_essentials/find_vs_build.md`

### **Encountering Issues?**
1. **First stop:** `guidance/core_essentials/troubleshooting_guide.md`
2. **Need context:** `guidance/project_intelligence/learning_log.md`
3. **Check decisions:** `guidance/project_intelligence/decision_log.md`

### **Making Technical Decisions?**
1. **Tool selection:** `guidance/core_essentials/scraping_tools_recommendations.md`
2. **Architecture choices:** `guidance/project_intelligence/decision_log.md`
3. **Document rationale:** Update decision_log.md with your choice

### **Planning Future Development?**
1. **Automation strategy:** `guidance/operations/claude_code_hooks_maintenance_plan.md`
2. **Long-term vision:** `guidance/strategic_vision/Automated Knowledge Miner (AKM).md`
3. **Performance roadmap:** `guidance/core_essentials/scraping_tools_recommendations.md`

### **End of Session?**
1. **Update learnings:** `guidance/project_intelligence/learning_log.md`
2. **Log decisions:** `guidance/project_intelligence/decision_log.md`
3. **Track config changes:** `guidance/operations/config_changelog.md`

---

## 📋 **Document Update Schedule**

### **Per Development Session:**
- Update `learning_log.md` with insights
- Add significant decisions to `decision_log.md`
- Track config changes in `config_changelog.md`

### **Per Phase/Week:**
- Review `troubleshooting_guide.md` for new patterns
- Update `scraping_tools_recommendations.md` based on experience
- Review `dependency_report.md` for security/updates

### **Per Month/Quarter:**
- Review strategic vision alignment with `Automated Knowledge Miner (AKM).md`
- Plan automation improvements with `claude_code_hooks_maintenance_plan.md`
- Consolidate and organize captured knowledge

---

## 🔗 **Cross-References**

### **Related Documentation:**
- **Project Memory:** `/CLAUDE.md` - Core development philosophy
- **Current Status:** `/session_docs/CURRENT_PROJECT_PLAN.md` - Active work and priorities
- **Development Process:** `/knowledge_docs/Reusable_Development_Checklist_for_Each_Module.md`

### **Configuration Files:**
- **Main Config:** `/config/config.yaml`
- **Claude Settings:** `/.claude/settings.json`
- **Tech Stack:** `/.claude/tech_stack.json`

### **Active Systems:**
- **Knowledge Management:** `/knowledge_management/` - Auto-organization system
- **Scraped Content:** `/vault/notes/` - Operational output
- **Logs:** `/vault/logs/` - System operation logs

---

## 🚨 **Critical Success Factors**

### **For Daily Development:**
1. **Always check `troubleshooting_guide.md` first** when encountering issues
2. **Consult `find_vs_build.md`** before implementing new functionality
3. **Document decisions immediately** in `decision_log.md`

### **For Knowledge Preservation:**
1. **Update `learning_log.md` during development**, not after
2. **Cross-reference related documents** to prevent information silos
3. **Keep `config_changelog.md` current** to prevent breaking changes

### **For Long-term Success:**
1. **Regular review of strategic documents** maintains project direction
2. **Consistent documentation updates** prevents knowledge loss
3. **Automation implementation** from `claude_code_hooks_maintenance_plan.md` ensures maintainability

---

*This reorganization creates purpose-driven accessibility while maintaining comprehensive knowledge capture that prevents project abandonment and ensures sustainable solo development with AI assistance.*
