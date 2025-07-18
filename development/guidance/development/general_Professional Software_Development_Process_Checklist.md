General Professional Software Development Process Checklist
Tailored for: Solo developer • No coding background • AI-assisted builds • Long-term personal use

Thanks! Based on your workflow — solo development, AI-generated code, long-term unstructured builds, and no prior coding experience — here’s an updated, **modular and reusable software development checklist** that works for **any kind of project**, not just algo trading.

---

# ✅ **Professional Software Development Process Checklist**

**Tailored for: Solo developer • No coding background • AI-assisted builds • Long-term personal use**

---

### 🧱 **0. Project Initialization (Once per project)**

| Task                                | Purpose                                        | Notes                                                                       |
| ----------------------------------- | ---------------------------------------------- | --------------------------------------------------------------------------- |
| ☐ Define project goal in 2-3 lines  | AI will generate better code if goal is clear  | e.g., “Build a bot to extract and summarize trading strategies from GitHub” |
| ☐ Create private Git repo           | Store versions safely                          | Name it clearly (e.g., `intel-forge`)                                       |
| ☐ Add basic folder structure        | Keeps things tidy even if code is AI-generated | e.g., `/src`, `/tests`, `/logs`, `/vault`, `/docs`, `/config`               |
| ☐ Create config file (YAML or JSON) | Makes your code reusable and easier to update  | Store API keys, paths, flags like `dry_run` here                            |
| ☐ Create README.md                  | Summarize purpose, setup, and structure        | Helps AI and future-you understand the project                              |

---

### 🧠 **1. Planning Before Every Module**

| Task                                  | Purpose                                   | Notes                                                          |
| ------------------------------------- | ----------------------------------------- | -------------------------------------------------------------- |
| ☐ Write prompt plan in `docs/plan.md` | Guides AI and tracks your thought process | Use checklists, pseudocode, sample output formats              |
| ☐ Define inputs/outputs               | Helps AI design clean, modular code       | e.g., input = GitHub query, output = Markdown notes            |
| ☐ Define failure behaviors            | Makes your code reliable                  | e.g., “On API error, retry once, then log and skip”            |
| ☐ Request logging and docstrings      | Reduces debugging, improves reusability   | Ask AI to include `# Logging starts`, `"""This function..."""` |

---

### 🧪 **2. Development (Each Module or Phase)**

| Task                              | Purpose                                 | Notes                                                      |
| --------------------------------- | --------------------------------------- | ---------------------------------------------------------- |
| ☐ Use focused AI prompt           | One phase per prompt = clean code       | Include desired filename, dry-run option, and config usage |
| ☐ Request clear logs and comments | Avoids confusion later                  | e.g., log to `logs/pipeline.log`, comment steps clearly    |
| ☐ Test with mock or dry-run mode  | Avoid damaging or spamming real systems | Use test data or a `--dry-run` flag                        |
| ☐ Save AI prompt and response     | Archive for debugging or reuse          | Store in `/docs/history/module_X.md`                       |

---

### 🧪 **3. Testing and Validation**

| Task                                    | Purpose                                  | Notes                                          |
| --------------------------------------- | ---------------------------------------- | ---------------------------------------------- |
| ☐ Run manual tests (real + mock)        | Spot logic or formatting bugs early      | Use sample data if available                   |
| ☐ Add a validation script               | Ensures everything works before full run | e.g., `"health_check.py"` for API + file paths |
| ☐ Test logging and error-handling paths | See how it behaves on fail cases         | Manually trigger errors if needed              |

---

### ♻️ **4. Iteration & Debugging**

| Task                                             | Purpose                          | Notes                                                           |
| ------------------------------------------------ | -------------------------------- | --------------------------------------------------------------- |
| ☐ Identify what's broken (input? logic? output?) | Helps frame clean AI fix prompts | Summarize in one line                                           |
| ☐ Regenerate only the broken part                | Keeps rest stable                | “Fix just the loop that parses GitHub repo data”                |
| ☐ Save fixed version with comments               | Track what changed               | Add `# Fixed on 2025-06-07` etc.                                |
| ☐ Commit each working version                    | Never lose working states        | Use commit messages like: `working github_fetcher with retries` |

---

### 🧹 **5. Maintenance & Hygiene**

| Task                                   | Purpose                            | Notes                                        |
| -------------------------------------- | ---------------------------------- | -------------------------------------------- |
| ☐ Clean up old logs, test files        | Avoid clutter                      | Add `scripts/reset_vault.py`                 |
| ☐ Archive successful prompts + outputs | Build your personal prompt library | Use folders like `docs/prompts/github.md`    |
| ☐ Periodically test all modules        | Avoid silent breakage              | Run every 1–2 weeks if active project        |
| ☐ Backup project                       | Prevent data loss                  | Use GitHub, GDrive, or encrypted disk folder |

---

### 🛠️ **6. Long-Term Modularity Practices**

| Task                               | Purpose                            | Notes                                               |
| ---------------------------------- | ---------------------------------- | --------------------------------------------------- |
| ☐ Use functions instead of scripts | Easier to reuse and test           | Ask AI to use `"def"` format                        |
| ☐ Isolate configs                  | Avoid hardcoded values             | Use `config.yaml` or `.env`                         |
| ☐ Standardize output formats       | Makes future stages easier         | JSON, Markdown, CSV — pick one per phase            |
| ☐ Write usage notes in each script | Helps you remember how to run them | e.g., `# Usage: python github_fetcher.py --dry-run` |

---

### 🧠 Pro Tip: Prompt Template for AI-Coding

Use this pattern every time you ask AI to write a module:

```text
Write a Python script that:
- Does XYZ clearly and modularly
- Loads settings from config.yaml
- Logs to logs/pipeline.log with timestamps
- Includes clear docstrings and comments
- Handles errors without crashing
- Supports a --dry-run flag
```

---
