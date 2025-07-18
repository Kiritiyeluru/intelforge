# AKM (Automated Knowledge Miner) Insights - Distilled for IntelForge Integration

## Meta Information
- **Source**: Discussion summary from `/docs/Automated Knowledge Miner (AKM).md`
- **Date Extracted**: 2025-01-06
- **Purpose**: AI-friendly documentation for future IntelForge enhancements
- **Integration Status**: Ready for implementation in future phases

---

## Core Insight Summary

### Central Vision
Transform IntelForge from a simple Reddit scraper into a **comprehensive automated knowledge mining system** that turns the web into a personalized, continuous research feed—coded, filtered, and saved in your language and structure.

### Key Quote
> *"If I can build a proper legal scraper system (using APIs), I can automate discovery, filtering, formatting, and organizing knowledge for every module I plan to build."*

---

## System Architecture Components

### 1. Proposed AKM Pipeline (8 Layers)

| Layer | Function | IntelForge Integration Priority |
|-------|----------|--------------------------------|
| **Query Builder** | Auto-generate searches per topic/module | 🟡 Medium - Phase 3+ |
| **Source Access** | APIs (Reddit, arXiv, Medium, GitHub, Dev.to) | 🟢 High - Phase 1-2 exist |
| **Content Extractor** | Pull structured data from sources | 🟢 High - Enhanced Phase 2+ |
| **Relevance Filter** | AI/ML scoring of content quality | 🟡 Medium - Phase 3+ |
| **Markdown Generator** | Obsidian-friendly note creation | ✅ Implemented - Phase 1 |
| **Vault Organizer** | Auto-categorization and linking | 🟡 Medium - Phase 4+ |
| **Digest Generator** | AI-powered daily/weekly summaries | 🔴 Low - Phase 5+ |
| **Feedback Loop** | Learn from user preferences | 🔴 Low - Phase 6+ |

### 2. Source Access Analysis

| Platform | API Status | Cost | Legal | IntelForge Status |
|----------|------------|------|-------|-------------------|
| **Reddit** | ✅ Official API | 💰 Paid (2023+) | ✅ Legal | ✅ Implemented |
| **GitHub** | ✅ REST API | 🆓 Free (limits) | ✅ Legal | 🔄 Phase 2 target |
| **Dev.to** | ✅ Open API | 🆓 Free | ✅ Legal | 🔄 Future phase |
| **arXiv** | ✅ Official API | 🆓 Free | ✅ Legal | 🔄 Phase 4 target |
| **Medium** | ❌ No API | 🚫 Risky | ⚠️ RSS only | 🔄 Low priority |
| **Google Search** | ❌ No API | 🚫 Risky | ❌ Avoid | ❌ Not planned |

---

## Key Improvements for IntelForge

### Immediate (Phase 2-3) Enhancements

#### A. Smart Content Filtering
- **Current**: Basic keyword + score filtering in Reddit scraper
- **Enhancement**: Multi-layered filtering system
  ```python
  # Rule-based pre-filter
  if stars > 100 or upvotes > 50 and published_after:2024-01-01:
      # Then apply ML-based relevance scoring
      relevance_score = tfidf_classifier.predict(content)
  ```

#### B. Unified Data Schema
- **Current**: Reddit-specific output format
- **Enhancement**: Standardized JSON schema for all sources
  ```json
  {
    "title": "Strategy Name",
    "url": "source_url",
    "summary": "AI-generated summary",
    "tags": ["bollinger-band", "python"],
    "source": "GitHub|Reddit|arXiv",
    "score": 83,
    "freshness": "2024-06-01",
    "content_hash": "sha256_hash"
  }
  ```

#### C. Enhanced Vault Organization
- **Current**: Flat file structure in `vault/notes/reddit/`
- **Enhancement**: Dynamic tag-based organization
  - Use Obsidian Dataview queries: `from #bollinger-band and #python`
  - Metadata-driven linking: `related: [[momentum-strategy]]`
  - Auto-generated connection notes between related findings

### Medium-term (Phase 3-4) Enhancements

#### A. Content Deduplication
- **Method**: Embedding-based similarity detection
- **Implementation**: `sentence-transformers` + FAISS for local vector search
- **Benefit**: Avoid saving duplicate strategies across sources

#### B. Research Thread Tracking
- **Concept**: Track evolution of ideas across sources
- **Example**: `Strategy > Backtest > Performance > Commentary`
- **Implementation**: Automatic backlinking via metadata

#### C. Gap Detection
- **Function**: Identify research areas lacking content
- **Implementation**: Script checks tagged topics without sufficient coverage
- **Example**: "Found 'momentum' strategies but no backtests"

### Long-term (Phase 5+) Enhancements

#### A. Personal Knowledge Graph
- **Alternative to**: Static markdown files
- **Tools**: Roam Research, LogSeq, or enhanced Obsidian
- **Benefit**: More queryable, semantic connections

#### B. LLM Research Assistant
- **Function**: Real-time synthesis instead of data dumping
- **Implementation**: Local LLM (Ollama) + vector store
- **Query Examples**:
  - "What strategies do I have for range-bound markets?"
  - "Where have I collected momentum indicators without backtests?"

---

## AI-Friendly Development Guidelines

### 1. Code Structure Requirements

#### Docstring Standards
```python
def fetch_repos(query: str) -> List[Dict]:
    """
    Fetch repositories from GitHub based on search query.

    Args:
        query (str): Search string (e.g., "bollinger band language:python")

    Returns:
        List[Dict]: Parsed repositories with metadata

    AI_HINT: This function is part of the Extractor module. Keep reusable and source-agnostic.
    """
```

#### Error Handling Instructions
```python
# If the API fails, retry 3 times then log and continue with next query
try:
    response = api_call()
except RateLimitError:
    logger.error("Rate limit hit, waiting 60 seconds...")
    time.sleep(60)
```

#### Configuration-Driven Design
```yaml
# config.yaml with AI descriptions
github:
  api_key: YOUR_KEY
  query: "bollinger band language:python"
  ai_description: "Search GitHub for Python implementations of Bollinger Band strategies"
```

### 2. AI Helper Scripts (Future Development)

#### System Health Check
- **Purpose**: Validate all APIs before pipeline runs
- **Features**: Test connectivity, log status to `vault/logs/health_check.md`

#### Sample Data Generator
- **Purpose**: Mock data for offline testing
- **Features**: Generate realistic fake data matching real API schemas

#### Reset/Cleanup Script
- **Purpose**: Clean vault for fresh starts
- **Features**: Safe deletion with user confirmation

### 3. AI Prompt Templates

#### Module Generation Template
```
Create a script that:
- [Task]: Fetch GitHub repos matching 'bollinger band'
- [Output]: Save to vault/notes/github-YYYY-MM-DD.md
- [Logging]: Log to vault/logs/pipeline.log
- [Error Handling]: Retry with exponential backoff
- [Features]: Include docstrings, comments, --dry-run flag
- [Schema]: Return JSON with {title, url, stars, description, tags}
```

---

## Implementation Roadmap for IntelForge

### Phase 2: GitHub Integration (Current)
- ✅ Basic GitHub API integration (existing)
- 🔄 Add unified schema output
- 🔄 Implement content filtering
- 🔄 Add deduplication logic

### Phase 3: Multi-Source Pipeline
- 🔄 Add Dev.to API integration
- 🔄 Implement relevance scoring (TF-IDF + rules)
- 🔄 Create query builder for automated searches
- 🔄 Enhanced vault organization

### Phase 4: Intelligence Layer
- 🔄 Add arXiv paper mining
- 🔄 Implement semantic clustering
- 🔄 Research thread tracking
- 🔄 Gap detection system

### Phase 5: AI Assistant
- 🔄 Local LLM integration (Ollama)
- 🔄 Vector store for semantic search
- 🔄 Automated digest generation
- 🔄 Personal research assistant queries

### Phase 6: Advanced Features
- 🔄 Feedback learning system
- 🔄 Knowledge graph visualization
- 🔄 Automated strategy backtesting integration
- 🔄 Community integration (Discord/Slack bots)

---

## Integration with Current IntelForge

### Existing Assets to Leverage
- ✅ **Reddit scraper** (Phase 1) - Foundation for multi-source system
- ✅ **MCP servers** - Enhanced research capabilities already installed
- ✅ **Obsidian output format** - Perfect for AKM markdown generation
- ✅ **Configuration system** - Ready for multi-source config expansion
- ✅ **Virtual environment** - Prepared for additional dependencies

### Recommended Next Steps
1. **Enhance Phase 1** with unified schema output
2. **Begin Phase 2** GitHub integration using AKM principles
3. **Implement basic filtering** with TF-IDF + rule-based scoring
4. **Add content deduplication** to prevent duplicate strategies
5. **Create query builder** for automated content discovery

---

## Competitive Advantages

### What This Gives You
- **Scalable learning memory** - Continuous knowledge accumulation
- **Reusable code discovery engine** - Find and organize implementations
- **AI-understandable system** - Semantic search and synthesis
- **Personal research lab** - Automated curation of trading knowledge

### Differentiation from Manual Browsing
- **Automated**: Runs continuously without manual intervention
- **Filtered**: Only high-quality, relevant content makes it through
- **Organized**: Structured for easy retrieval and connection-making
- **Synthesized**: AI-powered summaries and insights generation

---

## Files for Future Reference

### Documentation to Create
- `docs/akm_implementation_guide.md` - Step-by-step build instructions
- `prompts/akm_module_templates.md` - AI generation templates
- `config/akm_sources.yaml` - Multi-source configuration schema

### Scripts to Develop
- `tools/system_health.py` - API validation and health checks
- `tools/generate_fake_data.py` - Test data generation
- `tools/reset_pipeline.py` - Clean slate functionality
- `akm/query_builder.py` - Automated search generation
- `akm/relevance_filter.py` - Content quality scoring
- `akm/deduplicator.py` - Embedding-based duplicate detection

This distilled documentation provides a clear roadmap for evolving IntelForge from a single-source Reddit scraper into a comprehensive automated knowledge mining system, while maintaining the simplicity-first philosophy and AI-friendly development approach.
