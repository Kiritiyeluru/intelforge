# 🤖 AI Prompt Template: Find vs Build (Tool Discovery Assistant)

## 🎯 Purpose
Use this template to prompt Claude, ChatGPT, or any AI assistant to **search for prebuilt libraries, repos, or APIs** before you build a new module.

---

## 🔁 Prompt Template

> I am building a system that needs to perform the following function:
> 
> ```
> [Describe function in one sentence. e.g., "Scrape Reddit posts from r/algotrading and extract posts with backtest code."]
> ```
> 
> Please:
> 1. Search for **prebuilt libraries, GitHub repos, APIs, or tools** that already solve this problem.
> 2. Prioritize options that:
>    - Are well-maintained (recent commits, stars > 100)
>    - Have Python bindings or CLI tools
>    - Are modular or easily wrappable
>    - Avoid brittle scraping (prefer API/RSS when possible)
> 3. Summarize:
>    - 🔗 Link to the tool/repo
>    - 📄 Description of what it does
>    - ✅ Why it might replace a custom build
>    - 🛠️ What I’d still need to add/wrap
> 4. Add a quick recommendation: **Reuse**, **Wrap**, or **Build custom**

---

## ✅ Example Use Case

> I want to extract GitHub repositories for “bollinger band strategy” and save the data (stars, description, README) to markdown. Are there any tools or libraries that already help with GitHub scraping or summarization?

---

## 📌 Notes

- Save this prompt in `/prompts/` for reuse across all modules.
- Use it **before** each new phase.
- Pair with `/docs/find_vs_build.md` as a discipline.

