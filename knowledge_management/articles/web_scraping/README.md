# Article Intake Folder

Drop new articles (.md files) here for automatic organization.

## How It Works

1. **Save articles** as `.md` files in this folder
2. **Run organizer**: `python phase_07_article_organizer.py`
3. **Articles auto-moved** to appropriate category folders

## Commands

```bash
# Test what would happen (safe)
python phase_07_article_organizer.py --dry-run

# Process articles once
python phase_07_article_organizer.py

# Watch for new files continuously
python phase_07_article_organizer.py --watch
```

## Categorization Rules

Articles are categorized by title/content keywords:
- **claude_mcp**: Claude, MCP, Anthropic, Claude Code
- **web_scraping**: scraping, crawling, scraperr, pydoll
- **ai_workflows**: AI agent, LangGraph, workflow, prompt
- **productivity**: productivity, tools, Ubuntu, CLI, tips
- **archived**: Everything else

## Workflow

1. Save articles here from browser/downloads
2. Run `python phase_07_article_organizer.py --dry-run` to preview
3. Run `python phase_07_article_organizer.py` to organize
4. Check logs at `knowledge_management/logs/organizer.log`