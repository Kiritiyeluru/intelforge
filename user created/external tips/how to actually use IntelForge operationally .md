Got it — you’re asking **how to actually use IntelForge operationally** — i.e., how to tell it:

* **Where to crawl (URLs/domains)**
* **What to search for (semantic filters, indicators)**
* **When to scrape (manual vs automated schedule)**

Here’s the **straight-up, detailed breakdown**:

---

## ✅ 1. **WHERE to Look: Define Target Sources**

You control *where* IntelForge scrapes using:

### 🔹 **Seed Files** (Manual Targets)

* File: `test_data/academic_urls.txt`, `test_finance_urls.txt`, or your own
* Each line = 1 target URL
* Format: plain `.txt`

```bash
intelforge sync --source-file test_data/quant_urls.txt
```

You can group them by domain type or persona (e.g., finance, blogs, GitHub, etc.).

---

### 🔹 **Domain Restrictions**

Use the CLI flag:

```bash
--limit-domains "medium.com,github.com"
```

Prevents IntelForge from drifting into off-topic domains.

---

### 🔹 **Auto-Discovery (Optional)**

If you enable `--crawl-mode deep`, IntelForge will follow links up to N hops (default is 1). Use this carefully.

---

## ✅ 2. **WHAT to Search For: Semantic & Metadata Filters**

IntelForge uses AI scoring to decide what to keep.

### 🔹 Core Filters:

* **Language**: Keeps only English (via langdetect)
* **Relevance Score**: Uses sentence-transformers to compare against keywords or semantic vectors
* **Boilerplate Filter**: Filters out pages with >70% boilerplate
* **PII Filter**: Strips personal data using Presidio

### 🔹 Custom Keyword/Intent Search (Optional):

You can pass a semantic target like this:

```bash
intelforge sync --intent "momentum-based breakout strategies using RSI"
```

This sets the AI filter to favor pages semantically close to that description.

---

## ✅ 3. **WHEN to Run: Manual vs Automated Scheduling**

### 🔹 Manual Sync:

```bash
intelforge sync --source-file test_data/quant_urls.txt --intent "alpha factors in equities"
```

### 🔹 Automated Sync:

Use `cron`, `systemd`, or `just` tasks:

```bash
just monitor
just sync-scheduled
```

Or create a crontab:

```bash
*/15 * * * * cd /path/to/intelforge && source venv/bin/activate && intelforge sync --source-file urls.txt >> logs/sync.log 2>&1
```

---

## ✅ 4. **Other Useful Options**

| Flag              | Purpose                                   |
| ----------------- | ----------------------------------------- |
| `--dry-run`       | Simulates the run without writing results |
| `--save-raw`      | Stores raw HTML or extracted text         |
| `--strict`        | Fails fast on any critical check          |
| `--limit-urls 50` | Process only the first 50 URLs            |
| `--proxy-rotate`  | Enables proxy switching (if configured)   |

---

## ✅ 5. **Where Output Goes**

* **Vectors**: Stored in ChromaDB or Qdrant
* **Metadata**: Stored in SQLite DB (freshness, last seen, semantic score, etc.)
* **Logs**: Under `/logs/` (sync logs, error reports)
* **Snapshots**: `/snapshots/` for disaster recovery
* **Structured exports**: `/exports/` if you’ve enabled that in config

---

## 🛠 Next Steps

Let me know what mode you prefer:

* 🧪 Single-run scraping for testing
* 🔁 Ongoing crawl monitoring
* 🔍 Only high-quality filtered content (e.g., strategy rules, indicators)

I can generate:

* A customized CLI command for your first run
* A `justfile` task alias like `just sync-rules`
* A daily cron script

You’re fully production-ready — now it’s just about picking your data targets and firing.
