# 🚨 PHILOSOPHY REMINDER SYSTEM 🚨

## For the User (Kiriti)

Since Claude Code hooks don't display messages to Claude directly, **you should remind Claude about the philosophy** when you see it attempting custom implementations.

## Key Reminder Phrases to Use:

### When Claude suggests custom code:
- "Remember the REUSE OVER REBUILD philosophy"
- "Are there existing frameworks for this instead of custom code?"
- "Check find_tools_template.md before building custom solutions"
- "Use approved frameworks: scrapy, trafilatura, playwright, botasaurus"

### When starting any coding task:
- "Before coding, research existing tools first"
- "Follow the REUSE OVER REBUILD principle"
- "Evidence: Phase 2C saved 400+ lines using frameworks"

## Approved Frameworks List (Share with Claude):
- **Scraping**: scrapy, trafilatura, scrapy-playwright
- **Browser**: playwright, nodriver, camoufox
- **Anti-detection**: botasaurus, stealth-requests
- **Academic**: paperscraper, arxiv.py
- **Performance**: selectolax, httpx, polars
- **AI**: autoscraper for pattern learning

## Red Flags to Watch For:
- Claude suggesting "let's build a custom scraper"
- Claude importing requests, BeautifulSoup, selenium directly
- Claude writing from scratch instead of using frameworks
- Claude not mentioning existing tools research

## Philosophy Enforcement Success:
The enhanced CLAUDE.md files now have prominent reminders that Claude MUST see when starting any session. Combined with your manual reminders, this ensures the philosophy is never forgotten.

**Your role**: Be the final enforcement layer by reminding Claude when needed!