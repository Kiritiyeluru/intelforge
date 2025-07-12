# 🧠 Find vs Build Checklist

_A reusable decision-making guide for every new module in IntelForge._

## 🧩 Purpose
Before building anything new, this checklist helps you evaluate:
- Is this problem already solved elsewhere?
- Can I reuse or wrap existing tools?
- Will building this from scratch waste time or increase fragility?

---

## ✅ 1. Core Discovery Questions

| Question | If YES → |
|----------|----------|
| 🔍 Has someone already built a tool or script for this? | ✅ Reuse it or wrap it |
| 🧪 Is this available on PyPI, GitHub, or via an API? | ✅ Try it before rebuilding |
| 🧠 Could AI help me search better before coding? | ✅ Use `/prompts/find_tools_template.md` |

---

## ⚙️ 2. Reuse Filters

| Criteria | Recommendation |
|----------|----------------|
| 🌟 Tool has >100 stars and recent updates | ✅ High-confidence reuse |
| 🧰 Well-documented and pip-installable | ✅ Easy to integrate |
| ⚙️ Simple to wrap in a function | ✅ Favor wrapping over reimplementation |
| 📦 Handles edge cases I’d have to debug myself | ✅ Use it instead of guessing |

---

## 🚫 3. Anti-Patterns (Rebuild Red Flags)

| If you find yourself... | Stop and ask why |
|------------------------|------------------|
| Rewriting a basic HTTP scraper | Use `requests`, `feedparser`, or `praw` |
| Parsing RSS manually | Use `feedparser` |
| Looping over a repo manually to find README | Use `PyGitHub` |
| Implementing your own vector store | Use `FAISS`, `Chroma`, or `sqlite-vss` |
| Writing a search engine | Use `SerpAPI`, `Tavily`, or GitHub API search |

---

## 🧭 4. Build-Only When...

- The tool doesn’t exist or is badly broken
- Your use case is very specific or private
- You’ve already failed with 2+ existing options
- You understand the domain logic better than what’s available

---

## 🧠 Reminder

> The smartest systems are not built from scratch.  
> They are **assembled** from the best of what already works.

Save time. Reuse. Wrap. Move forward.

