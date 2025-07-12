# Architecture Decision Record - Knowledge Management

## Decision 1: Local-First Vector Database
**Date:** 2025-07-02  
**Status:** Accepted

### Context
Need to make 25+ articles searchable and AI-ready without recurring costs.

### Decision
Use FAISS for local vector storage with Ollama embeddings.

### Rationale
- Zero recurring costs
- Privacy-focused (no data sent to cloud)
- Mature, battle-tested tools
- Fits IntelForge "reuse over rebuild" philosophy

### Alternatives Considered
- Pinecone (rejected: paid service)
- OpenAI embeddings (rejected: recurring costs)
- Custom search (rejected: reinventing wheel)

## Decision 2: Hierarchical + AI Hybrid Approach
**Date:** 2025-07-02  
**Status:** Accepted

### Context
Need immediate organization improvement while building AI system.

### Decision
Implement folder-based organization first, then add AI search layer.

### Rationale
- Immediate benefit from folder organization
- Progressive enhancement approach
- Allows testing/refinement of categories
- Fallback if AI system has issues

## Decision 3: Integration with Existing Phases
**Date:** 2025-07-02  
**Status:** Accepted

### Context
Knowledge management should enhance existing trading research workflow.

### Decision
Build phase_07_article_processor.py that integrates with phases 1-6.

### Rationale
- Consistent with existing architecture
- Reuses existing config/logging systems
- Enables cross-referencing between scraped content and saved articles
- Maintains simplicity principle