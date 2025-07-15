Excellent breakdown — you're operating with strong architectural discipline already. Let's now focus on **replacing the remaining 10% (optimization targets)** with mature, battle-tested tools, **without overengineering** or rebuilding what’s already solved.

---

## ✅ Optimization Targets + Best Prebuilt Replacements

---

### 🔁 **1. Cosine Similarity (Replace Custom)**

**Replace with:**

* [`sklearn.metrics.pairwise.cosine_similarity`](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html)
* Or: [`faiss`](https://github.com/facebookresearch/faiss) for larger-scale dense vector matching

**Why:**

* Scikit-learn is fast, proven, and well-tested
* Handles batching, sparse vectors, GPU (with FAISS)
* Avoids reimplementing similarity logic

---

### 📁 **2. Custom File I/O → Jinja2 Templates**

**Replace with:**

* [`Jinja2`](https://jinja.palletsprojects.com/) for dynamic Markdown + YAML generation

**Use Case:**

* Replace hardcoded string formatting for `.md` or `.yaml` output

**Why:**

* Cleaner template logic
* Better separation of content and formatting
* Easy to reuse/parameterize across doc types (e.g. session logs, reports)

---

### 🧪 **3. Custom Data Validation → Pydantic**

**Replace with:**

* [`Pydantic`](https://docs.pydantic.dev/latest/) (or `attrs`, if you want even lighter)

**Use Case:**

* Validating scraped records
* Normalizing `DocMeta`, vector embedding schema, TTR records

**Why:**

* Built-in type checking, regex validation, default handling
* Easily converted to `dict`, JSON, etc.
* Future-proof if you later add FastAPI or microservices

---

### 🌐 **4. Custom HTTP Client → Scrapy Framework**

**Replace with:**

* [`Scrapy`](https://scrapy.org/) + optional `scrapy-playwright` or `browsertrix`

**Why:**

* Native retry, backoff, throttling, proxy rotation, pipeline hooks
* Clean separation of spider logic and output processing
* Easier to scale, debug, and test than manual `httpx` pipelines

---

## 🧩 Bonus (Not Requested, But High Leverage)

### 📊 **Add Prometheus Metrics**

* Tool: [`prometheus_client`](https://github.com/prometheus/client_python)
* Use for: Tracking run counts, failures, TTR breakdowns, latency per domain
* **Why:** Immediate observability into pipeline health and crawl behavior

---

### 📦 **Optional Packaging/Orchestration Tools**

| Feature                | Tool                                | Why Use It                                             |
| ---------------------- | ----------------------------------- | ------------------------------------------------------ |
| Reproducible pipelines | `taskfile.yml` (Task) or `Makefile` | Declarative, versionable pipeline runner               |
| Workflow orchestration | `n8n`, `Airflow`, or `Prefect`      | Optional if your flows get complex                     |
| Lightweight UI/Logs    | `Textual`, `rich`, or `typer`       | For TUI dashboards or logs that aren’t just `print()`s |

---

## 🧠 Final Mapping of What to Replace

| Current Component           | Replace With                | Effort | Benefit                        |
| --------------------------- | --------------------------- | ------ | ------------------------------ |
| Manual cosine function      | `sklearn` or `faiss`        | \~1 hr | ✅ Speed, batching, clarity     |
| YAML/Markdown by string     | `Jinja2`                    | \~2–3h | ✅ Maintainability, reuse       |
| Ad hoc data validation      | `Pydantic`                  | \~2–3h | ✅ Fewer bugs, easier testing   |
| `httpx` + retry logic       | `Scrapy`                    | \~4h   | ✅ Industrial strength scraping |
| Manual metrics/debug prints | `prometheus_client`, `rich` | \~1–2h | ✅ Monitoring, observability    |

---

## 🎯 Final Recommendation Summary

| Priority  | Task                           | Prebuilt Tool               |
| --------- | ------------------------------ | --------------------------- |
| 🟢 High   | Replace cosine sim logic       | `sklearn`                   |
| 🟢 High   | Migrate to Scrapy              | `Scrapy`                    |
| 🟡 Medium | Add data schema enforcement    | `Pydantic`                  |
| 🟡 Medium | Use Jinja2 for template output | `Jinja2`                    |
| 🔵 Low    | Add metrics/logging            | `prometheus_client`, `rich` |

---

Would you like me to:

* Auto-refactor one of your existing scripts using Jinja2 + Pydantic?
* Generate a Scrapy spider starter that plugs into your semantic pipeline?

Just tell me which module to optimize first.
