Here is the updated `README.md` for **IntelForge**, now with your **Simplicity Philosophy** seamlessly baked in. This version clearly communicates your purpose, prevents future over-engineering, and sets expectations for anyone (including AI) who reads or contributes to the code.

---

```markdown
# 🧠 IntelForge

_A personal AI-powered knowledge extraction system for web scraping and intelligence gathering._

---

## 🚀 Overview

**IntelForge** is a solo-developed, AI-assisted project designed to help me build a long-term, modular agent that scrapes and organizes valuable knowledge from public online sources — especially in the fields of **algorithmic trading**, **technical strategy mining**, and **financial research**.

Rather than reinventing common tools, this system wraps reliable scraping methods with minimal logic and intelligent automation — all built using AI tools like Claude or ChatGPT.

> ⚠️ This project is for **personal, non-commercial use only** and respects site TOS and robots.txt wherever applicable.

---

## 🎯 Core Objectives

### ✅ What I'm Building

- A **simple, AI-cooperative pipeline** that can:
  - Scrape content from target sources (GitHub, Reddit, Medium, PDFs, etc.)
  - Extract and summarize relevant ideas (e.g. strategies, indicators, backtests)
  - Store those insights as markdown notes for long-term use

### 💡 Why I'm Building It

- I build **alone**, from scratch, with **no formal coding background**
- I rely on **AI** to help me write, fix, and evolve the code
- I need a system that is:
  - 🧠 *Understandable by a non-CS user*
  - 🧱 *Modular and AI-regenerable*
  - 🧹 *Simple enough to maintain over years*

---

## 🧘‍♂️ Simplicity-First Development Philosophy

> “We are building a lab notebook, not a SaaS platform.”
| ❌ Don’t Use                | ✅ Use Instead                                      |
| -------------------------- | -------------------------------------------------- |
| Rebuild tools from scratch | 📦 Use trusted libraries or wrap open-source tools |

### 🧠 See Also:
- [♻️ Find vs Build Checklist](docs/find_vs_build.md)
- [🤖 AI Prompt Template – Tool Discovery](prompts/find_tools_template.md)


## ♻️ Reuse Over Rebuild

> “If someone smarter has already built it — I’ll use it.”

IntelForge is grounded in the principle of **reusing existing libraries, tools, and open-source implementations** wherever possible. The purpose of this system is not to reinvent common scraping, summarization, or backtesting logic — it is to:
- Identify and **wrap** trusted tools
- Use AI to glue them together intelligently
- Avoid building brittle code for problems that are already solved

### ✅ Reuse Checklist for Every Phase:
- [ ] Did I search GitHub / PyPI / Reddit / arXiv before writing any custom logic?
- [ ] Is this already available as a library or CLI tool?
- [ ] Can I wrap this in a function instead of building from scratch?
- [ ] Would future AI agents benefit more from a known tool than new code?

When in doubt: **Search, evaluate, wrap — don’t rebuild.**

### ❌ Avoiding Unnecessary Complexity

| ❌ Don’t Use | ✅ Use Instead |
|-------------|----------------|
| `src/`, `lib/`, abstract modules | Flat script layout (1 file per phase) |
| Custom classes for everything | Named functions in a script |
| Over-abstracted configs | One `config.py` or `config.yaml` |
| Full test frameworks | Manual tests + `--dry-run` mode |
| Framework-based structure | Readable, small AI-friendly scripts |

### 🧭 Design Check Before Adding Anything:
- Would I understand this in 3 months?
- Can this live in one file instead of three?
- Would this make AI-generated fixes harder?
- Is it adding value or just structure?

If the answer is no — **keep it simple**.

---

## 📦 Planned Architecture (Phased)

| Phase | Description |
|-------|-------------|
| `phase_01_github.py` | Scrape GitHub repos (e.g., for strategy code) |
| `phase_02_reddit.py` | Extract Reddit threads/posts (e.g., r/algotrading) |
| `phase_03_blogs.py` | Scrape blog posts from Dev.to, Medium, etc. |
| `phase_04_pdfs.py` | Extract and summarize research papers and PDFs |
| `phase_05_summarizer.py` | Use GPT to auto-clean, tag, and summarize |
| `phase_06_curator.py` | Organize all outputs into markdown vault |

---

## 📁 Folder Structure

```

intelforge/
├── phase\_01\_github.py       # Modular scraper (self-contained)
├── config.py                # Simple settings and API keys
├── vault/
│   ├── notes/               # Saved markdown outputs
│   └── logs/                # Log files and error traces
├── prompts/
│   └── github\_scraper.md    # Claude/GPT prompt used for generation
├── docs/
│   └── development\_checklist.md  # Reusable checklist for building each module
├── README.md

````

---

## 🛠️ Tooling Principles

| Principle | What It Means |
|----------|----------------|
| 🔹 Flat, simple structure | Avoids overmodularization |
| 🔹 Clear prompt history | Everything AI-generated is saved |
| 🔹 Config-first design | Change behavior without editing code |
| 🔹 Test-friendly by design | Includes dry-run mode and test data |
| 🔹 Logging by default | Logs to markdown or plaintext logs |

---

## 🧪 Getting Started

1. Clone the repo privately.
2. Add your API keys and settings to `config.py` or `config.yaml`.
3. Run the health check:
   ```bash
   python scripts/health_check.py
````

4. Start the GitHub fetcher in dry-run mode:

   ```bash
   python phase_01_github.py --dry-run
   ```
5. Output will be saved to:

   * ✅ Notes: `vault/notes/`
   * ✅ Logs: `vault/logs/`

---

## 🔍 Success Criteria

| ✅ What Success Looks Like                                     |
| ------------------------------------------------------------- |
| Everything lives in 1–2 files per phase                       |
| Total repo is understandable in under 5 mins                  |
| Can be fully managed by solo user with AI help                |
| Doesn’t look or feel like a commercial codebase               |
| System builds toward a personal research brain, not a product |

---

## 🧠 Development Process

* All code is written using AI (Claude or GPT), based on saved prompts in `/prompts`
* Every script includes a docstring, inline comments, and fallback logic
* I follow a **10-point development checklist** in `/docs/development_checklist.md`
* I use versioned prompt files to track how each module was built or fixed

---

## 🔒 Ethics & Legal Use

* No scraping behind paywalls or logins
* Only uses official APIs or public RSS where possible
* Designed for personal research and educational purposes only

---

## ✨ Future Ideas

* Local summarization using LLMs (Ollama, LM Studio)
* Obsidian plugin for summarizing vault content
* Periodic scraping jobs + auto-digests (cron + markdown)
* GPT-based chat agent for asking:

  > “What strategies have I collected that use Z-Score + SMA?”

---

## 🤝 Collaborators & Credits

This project is personal and private, but credits go to:

* Claude + GPT (AI pair-programmers)
* The open-source community that shares knowledge publicly
* Tools like Obsidian, PRAW, and PyGitHub

## 📚 Internal Docs & Reusable Tools

| File | Purpose |
|------|---------|
| [`docs/find_vs_build.md`](docs/find_vs_build.md) | Helps decide whether to build from scratch or wrap existing tools |
| [`prompts/find_tools_template.md`](prompts/find_tools_template.md) | Reusable prompt template for Claude/GPT to search for prebuilt tools before coding |
| [`docs/development_checklist.md`](docs/development_checklist.md) | End-to-end checklist for building each module with AI help |

```
