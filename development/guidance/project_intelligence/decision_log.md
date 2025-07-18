# Decision Log - IntelForge

## Purpose
Track architectural and implementation decisions with rationale to prevent repeated discussions and maintain context across sessions.

---

## 2025-01-06: GitHub Projects Automation Setup

**Decision:** Three-file handover system (current_task.md, next_task.md, session_summary.md)
**Alternatives Considered:** Single status file, Git commit messages only, Complex project management tools
**Rationale:** User has burned repos due to documentation decay; need lightweight but comprehensive context preservation
**Impact:** Prevents information loss between sessions, supports solo+AI development
**Status:** Implemented

**Decision:** Phase-based commit message format (phase_XX: description)
**Alternatives Considered:** Conventional Commits, free-form messages
**Rationale:** Aligns with IntelForge's phase_XX module naming convention
**Impact:** Consistent tracking of work across development phases
**Status:** Implemented

**Decision:** GitHub issue templates over freeform issues
**Alternatives Considered:** Simple issue creation, external task management
**Rationale:** Standardizes information capture, prevents incomplete task descriptions
**Impact:** More structured development workflow
**Status:** Implemented

---

---

## 2025-01-06: Tool Reuse Strategy for Content Extraction

**Decision:** Use specialized existing libraries for each content type vs. building custom scrapers
**Alternatives Considered:**
- Build everything from scratch using requests/BeautifulSoup
- Use single general-purpose scraping framework
- Mix of specialized tools (chosen approach)

**Rationale:**
- Marker for PDFs provides superior quality vs. custom PDF parsing
- PRAW for Reddit is official API wrapper with built-in rate limiting
- PaperScraper for ArXiv handles academic paper extraction professionally
- Specialized tools handle edge cases and API changes automatically

**Impact:**
- ~80% reduction in development time
- More robust error handling and edge case coverage
- Reduced long-term maintenance burden
- Higher quality extraction results

**Implementation Plan:**
- Phase 1: PRAW + Reddit2Text for Reddit extraction
- Phase 2: PyGitHub for repository mining
- Phase 4: Marker for PDF processing
- Phase 4: PaperScraper for ArXiv papers
- Custom wrapper for Obsidian formatting and metadata

**Status:** Approved - will implement in phases
**Follow-up Required:** Update each phase roadmap with specific tool integration

**2025 Research Update:** Perplexity MCP search confirmed PRAW remains the best choice:
- Still the most mature and reliable Reddit API wrapper in 2025
- Automatic rate limit management (critical with Reddit's stricter policies)
- Abstracts API complexities effectively
- Alternative tools (URS, Apify) are either CLI-only or require paid services
- Reddit API has become more restrictive, making official API wrapper essential

---

## Template for Future Decisions

**Decision:** [Brief description]
**Date:** YYYY-MM-DD
**Alternatives Considered:** [List other options evaluated]
**Rationale:** [Why this choice was made]
**Impact:** [How this affects the project]
**Status:** [Proposed/Implemented/Deprecated]
**Related Issues:** [Link to GitHub issues if applicable]
**Follow-up Required:** [Any monitoring or future decisions needed]
