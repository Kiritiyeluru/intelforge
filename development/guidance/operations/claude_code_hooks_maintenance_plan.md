# Claude Code Hooks: Long-term Maintenance Strategy for IntelForge

## 🎯 Overview

This document outlines a comprehensive Claude Code hooks strategy designed specifically for **solo developers with AI assistance** who need to maintain and evolve their codebase over time without deep software engineering knowledge.

## 🚨 The Problem We're Solving

**For Non-Technical Solo Developers:**
- **Dependency Hell**: Forgetting which libraries are used where
- **Inconsistent Patterns**: New modules don't follow established conventions
- **Documentation Drift**: Code changes but docs fall behind
- **Refactoring Fear**: Scared to change base code due to unknown impacts
- **Context Loss**: Forgetting project structure between sessions

**For AI-Assisted Development:**
- **Stale Context**: AI doesn't know current dependencies/patterns
- **Inconsistent Generation**: AI recreates patterns differently each time
- **Manual Overhead**: Constantly updating documentation and tracking files

## 💡 Hook-Based Solution Strategy

### Core Principle: **"Automate the Boring, Error-Prone Stuff"**

Instead of remembering to manually:
- Update requirements.txt when adding imports
- Check if new modules follow patterns
- Update documentation after changes
- Track which files depend on what

**→ Hooks do it automatically every time you code**

## 🎯 Priority 1: Critical Maintenance Hooks

### 1. **Dependency Intelligence Hook** ⭐⭐⭐
**What it does**: Automatically tracks and manages Python imports
**Triggers**: PostToolUse when creating/editing .py files
**Files it creates/updates**:
- `.claude/dependencies.json` - Live dependency map
- `requirements_auto.txt` - Auto-generated requirements
- `docs/dependency_report.md` - Human-readable dependency analysis

**Hook Configuration**:
```json
{
  "name": "dependency_intelligence",
  "type": "PostToolUse",
  "matchers": [
    {"tool": "Write", "path": "**/*.py"},
    {"tool": "Edit", "path": "**/*.py"},
    {"tool": "MultiEdit", "path": "**/*.py"}
  ],
  "command": "python scripts/hooks/dependency_intelligence.py \"$CLAUDE_FILE_PATHS\""
}
```

**Supporting Script**: `scripts/hooks/dependency_intelligence.py`
- Scans all imports in modified files
- Updates dependency database with usage info
- Generates warnings for deprecated/problematic libraries
- Suggests alternatives for heavy dependencies
- Auto-updates requirements files

### 2. **Module Structure Guardian** ⭐⭐⭐
**What it does**: Ensures all new Python modules follow IntelForge patterns
**Triggers**: PostToolUse when creating new .py files
**Checks for**:
- Proper docstring format
- CLI argument patterns (--dry-run, --config)
- BaseScraper inheritance for scrapers
- Error handling and logging setup
- File naming conventions

**Hook Configuration**:
```json
{
  "name": "module_structure_guardian",
  "type": "PostToolUse",
  "matchers": [{"tool": "Write", "path": "**/*.py"}],
  "command": "python scripts/hooks/module_structure_guardian.py \"$CLAUDE_FILE_PATHS\""
}
```

**Supporting Script**: `scripts/hooks/module_structure_guardian.py`
- Validates module structure against IntelForge patterns
- Suggests fixes for non-compliant modules
- Updates `.claude/module_patterns.json` with examples
- Generates pattern compliance report

## 🎯 Priority 2: Documentation Automation Hooks

### 3. **Documentation Sync Engine** ⭐⭐
**What it does**: Keeps documentation automatically in sync with code
**Triggers**: PostToolUse when key files are modified
**Updates**:
- README.md folder structure when files are moved
- Tech stack documentation when dependencies change
- Module listings when new scrapers are added

**Hook Configuration**:
```json
{
  "name": "documentation_sync_engine",
  "type": "PostToolUse",
  "matchers": [
    {"tool": "Write", "path": "scrapers/*.py"},
    {"tool": "Write", "path": "scripts/*.py"},
    {"tool": "Edit", "path": "config/config.yaml"},
    {"tool": "Edit", "path": "requirements*.txt"}
  ],
  "command": "python scripts/hooks/documentation_sync_engine.py \"$CLAUDE_FILE_PATHS\""
}
```

### 4. **Session Context Maintainer** ⭐⭐
**What it does**: Automatically updates session tracking files
**Triggers**: PostToolUse after significant changes
**Updates**:
- `session_docs/current_task.md` with progress
- `.claude/project_context.json` with current status
- `session_docs/session_summary.md` with recent changes

**Hook Configuration**:
```json
{
  "name": "session_context_maintainer",
  "type": "PostToolUse",
  "matchers": [
    {"tool": "Write", "path": "{scrapers,scripts}/*.py"},
    {"tool": "Edit", "path": "session_docs/*.md"}
  ],
  "command": "python scripts/hooks/session_context_maintainer.py"
}
```

## 🎯 Priority 3: Refactoring Safety Hooks

### 5. **Refactoring Impact Analyzer** ⭐
**What it does**: Warns about potential breaking changes when modifying core files
**Triggers**: PostToolUse when editing base framework files
**Analyzes**:
- Which modules import from modified files
- What functions/classes are being changed
- Potential downstream impacts

**Hook Configuration**:
```json
{
  "name": "refactoring_impact_analyzer",
  "type": "PostToolUse",
  "matchers": [
    {"tool": "Edit", "path": "scripts/scraping_base.py"},
    {"tool": "Edit", "path": "config/config.yaml"}
  ],
  "command": "python scripts/hooks/refactoring_impact_analyzer.py \"$CLAUDE_FILE_PATHS\""
}
```

### 6. **Code Quality Watchdog** ⭐
**What it does**: Runs basic quality checks on new/modified code
**Triggers**: PostToolUse when editing Python files
**Checks**:
- Basic syntax validation
- Import organization
- Common anti-patterns
- Security issues (hardcoded credentials, etc.)

## 🚀 IntelForge-Specific Additional Hooks

### 7. **Scraping Session Logger** ⭐⭐⭐ **HIGHEST PRIORITY**
**What it does**: Automatically tracks all scraping activities and performance
**Why critical for IntelForge**: You run scrapers frequently and need to track what was scraped when without manual logs

**Triggers**: PostToolUse when running any scraper
**Hook Configuration**:
```json
{
  "name": "scraping_session_logger",
  "type": "PostToolUse",
  "matchers": [
    {"tool": "Bash", "command": "python scrapers/*"},
    {"tool": "Bash", "command": "python phase_*"},
    {"tool": "Bash", "command": "python scripts/phase_*"}
  ],
  "command": "python scripts/hooks/scraping_session_logger.py \"$CLAUDE_TOOL_INPUT\" \"$CLAUDE_TOOL_OUTPUT\""
}
```

**Supporting Script**: `scripts/hooks/scraping_session_logger.py`
- Tracks which scraper was run with what parameters
- Records number of items scraped, errors encountered, rate limit hits
- Performance metrics (execution time, success rate, data volume)
- Updates `.claude/scraping_history.json` with timestamped session data
- Generates daily/weekly scraping summary reports
- **Immediate value**: No more manual tracking of scraping sessions

### 8. **Config Change Propagator** ⭐⭐ **HIGH PRIORITY**
**What it does**: Automatically propagates config.yaml changes to related files
**Why needed for IntelForge**: Config changes (new APIs, scraper targets) need updates across multiple files

**Triggers**: PostToolUse when config.yaml is modified
**Hook Configuration**:
```json
{
  "name": "config_change_propagator",
  "type": "PostToolUse",
  "matchers": [{"tool": "Edit", "path": "config/config.yaml"}],
  "command": "python scripts/hooks/config_change_propagator.py \"$CLAUDE_FILE_PATHS\""
}
```

**Supporting Script**: `scripts/hooks/config_change_propagator.py`
- Updates `.env.example` when new API keys are added to config
- Regenerates `requirements.txt` if new dependencies are implied by config
- Updates scraper documentation when new targets/sources are added
- Validates config syntax and suggests fixes for common errors
- Updates `.claude/config_history.json` with change tracking
- **Prevents**: Config-related breakage and inconsistency

### 9. **Knowledge Base Optimizer** ⭐⭐ **MEDIUM PRIORITY**
**What it does**: Automatically organizes and optimizes the growing vault content
**Why useful for IntelForge**: Your vault grows quickly from scraping and needs automatic organization

**Triggers**: PostToolUse when vault content is modified
**Hook Configuration**:
```json
{
  "name": "knowledge_base_optimizer",
  "type": "PostToolUse",
  "matchers": [
    {"tool": "Write", "path": "vault/notes/**/*.md"},
    {"tool": "Edit", "path": "vault/notes/**/*.md"}
  ],
  "command": "python scripts/hooks/knowledge_base_optimizer.py \"$CLAUDE_FILE_PATHS\""
}
```

**Supporting Script**: `scripts/hooks/knowledge_base_optimizer.py`
- Detects duplicate or near-duplicate content and suggests merging
- Auto-generates cross-references between related articles using content analysis
- Updates tag consistency across similar topics (e.g., #trading-strategy vs #trading_strategy)
- Triggers re-indexing for semantic search when significant content changes
- Optimizes file organization and suggests better categorization
- **Keeps growing knowledge base organized without manual intervention**

## 📁 Supporting File Structure

```
scripts/hooks/                           # Hook implementation scripts
├── dependency_intelligence.py           # Tracks imports and dependencies
├── module_structure_guardian.py         # Validates module patterns
├── documentation_sync_engine.py         # Keeps docs in sync
├── session_context_maintainer.py        # Updates session tracking
├── refactoring_impact_analyzer.py       # Analyzes change impacts
├── code_quality_watchdog.py            # Basic quality checks
├── scraping_session_logger.py          # Tracks scraping activities (IntelForge-specific)
├── config_change_propagator.py         # Propagates config changes (IntelForge-specific)
└── knowledge_base_optimizer.py         # Optimizes vault content (IntelForge-specific)

.claude/                                 # Hook-generated context files
├── dependencies.json                   # Live dependency map
├── module_patterns.json               # IntelForge code patterns
├── refactoring_alerts.json            # Impact analysis results
├── quality_reports.json               # Code quality summaries
├── scraping_history.json              # Scraping session tracking (IntelForge-specific)
└── config_history.json                # Config change tracking (IntelForge-specific)

docs/                                   # Auto-generated documentation
├── dependency_report.md               # Human-readable dependency info
├── module_compliance_report.md        # Pattern compliance status
├── refactoring_safety_guide.md        # Change impact summaries
└── scraping_activity_reports.md       # Scraping performance and activity summaries (IntelForge-specific)
```

## 🔧 Implementation Phases

### Phase 1: Critical Infrastructure (Week 1)
1. **Scraping Session Logger** - Immediate value for daily scraping workflow ⭐ **START HERE**
2. **Dependency Intelligence Hook** - Start tracking imports immediately
3. **Module Structure Guardian** - Enforce patterns on new files
4. Create supporting scripts and test with existing codebase

### Phase 2: IntelForge-Specific Automation (Week 2)
1. **Config Change Propagator** - Prevent config-related breakage
2. **Documentation Sync Engine** - Automate README/docs updates
3. **Session Context Maintainer** - Keep session files current
4. Test automation with real config and scraping changes

### Phase 3: Advanced Features (Week 3)
1. **Knowledge Base Optimizer** - Organize growing vault content
2. **Refactoring Impact Analyzer** - Add change safety nets
3. **Code Quality Watchdog** - Basic quality enforcement
4. Full integration testing and refinement

### 🎯 **Recommended Start Order for IntelForge**:
1. **Scraping Session Logger** (immediate daily value)
2. **Dependency Intelligence** (foundational)
3. **Config Change Propagator** (prevents breakage)
4. **Module Structure Guardian** (maintains consistency)
5. **Knowledge Base Optimizer** (as vault grows)
6. **Advanced safety features** (refactoring, quality)

## ✅ Success Metrics

**For Solo Developer:**
- **Zero manual dependency tracking** - All imports automatically catalogued
- **Consistent code patterns** - New modules automatically follow established conventions
- **Always-current documentation** - README and docs stay in sync without manual effort
- **Fearless refactoring** - Confident changes with impact analysis
- **Session continuity** - Context preserved between development sessions

**For AI Assistance:**
- **Rich context awareness** - AI always knows current dependencies and patterns
- **Consistent code generation** - AI follows established patterns automatically
- **Accurate problem diagnosis** - AI has current project state for troubleshooting

## 🚀 Long-term Benefits

1. **Maintainability**: Project stays organized as it grows
2. **Reliability**: Fewer bugs from inconsistent patterns or forgotten dependencies
3. **Scalability**: Easy to add new modules following established patterns
4. **Knowledge Preservation**: Project knowledge captured in machine-readable form
5. **AI Effectiveness**: Better AI assistance with rich, current context

## 🎯 Next Steps

1. **Review and approve** this plan
2. **Implement Priority 1 hooks** (dependency tracking and module validation)
3. **Test with existing codebase** to validate approach
4. **Gradually add** documentation and refactoring hooks
5. **Iterate based on real usage** and refine as needed

---

*This plan transforms IntelForge from manual maintenance to automated intelligence, ensuring long-term success for solo AI-assisted development.*
