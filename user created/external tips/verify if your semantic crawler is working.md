Here’s how to **verify if your semantic crawler is working correctly**, along with a shortlist of **simple, safe websites** you can scrape right now.

---

## ✅ How to Check if Semantic Crawler is Working Properly

### 🔍 1. **Dry-Run Mode Test**

```bash
source venv/bin/activate
python scripts/semantic_crawler.py \
  --url https://www.quantstart.com/articles/ \
  --threshold 0.8 \
  --dry-run
```

✅ You should see:

* Logs showing “Found X candidate links”
* Semantic scores printed (e.g., `0.86` for each)
* No actual files written

If **nothing is found**, lower the threshold:

```bash
--threshold 0.6
```

---

### 🔬 2. **Live Crawl + Output Check**

```bash
python scripts/semantic_crawler.py \
  --url https://robotwealth.com/articles/ \
  --threshold 0.75 \
  --save-raw
```

Then check:

```bash
ls exports/
cat exports/*.json | less
```

✅ Expect: JSON files with `title`, `url`, `score`, `text`, maybe tags like `strategy`, `backtest`.

---

### 📊 3. **ChromaDB / Qdrant Indexing Check**

You should see new embeddings in your vector DB logs.

**Qdrant (default fallback)**:

```bash
curl http://localhost:6333/collections
```

✅ You should see collections like:

```json
"intelforge_articles"
```

---

### ✅ 4. **CLI Health Test**

```bash
python scripts/semantic_crawler.py --help
```

Check that:

* Flags like `--url`, `--threshold`, `--url-file`, `--save-raw` are recognized.
* No `ModuleNotFoundError` (especially for spaCy, transformers, or httpx).

---

### 🧠 5. **Manual Semantics Comparison**

1. Choose a known article on a strategy:

   * e.g., [https://www.quantstart.com/articles/Backtesting-A-Moving-Average-Crossover-in-Python/](https://www.quantstart.com/articles/Backtesting-A-Moving-Average-Crossover-in-Python/)

2. Run it with:

```bash
python scripts/semantic_crawler.py \
  --url https://www.quantstart.com/articles/Backtesting-A-Moving-Average-Crossover-in-Python/ \
  --threshold 0.6 \
  --save-raw
```

3. Check if:

   * It extracted the strategy logic
   * The semantic score is >0.6
   * It contains key phrases like "moving average", "buy signal", "sell signal"

---

## 🌐 Simple, Safe Sites to Test Semantic Crawler On

These are **non-authenticated**, non-JS-heavy, crawler-friendly sources:

### 📰 Articles / Blogs

| Site        | URL                                                                                                    |
| ----------- | ------------------------------------------------------------------------------------------------------ |
| QuantStart  | [https://www.quantstart.com/articles/](https://www.quantstart.com/articles/)                           |
| RobotWealth | [https://robotwealth.com/articles/](https://robotwealth.com/articles/)                                 |
| QuantInsti  | [https://blog.quantinsti.com/tag/trading-strategy/](https://blog.quantinsti.com/tag/trading-strategy/) |
| Quantpedia  | [https://quantpedia.com/strategies/](https://quantpedia.com/strategies/)                               |
| PyQuantNews | [https://www.pyquantnews.com/](https://www.pyquantnews.com/)                                           |

### 📚 Academic

| Site  | URL                                                                                                                                                                              |
| ----- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| arXiv | [https://arxiv.org/rss/q-fin](https://arxiv.org/rss/q-fin)                                                                                                                       |
| SSRN  | [https://papers.ssrn.com/sol3/DisplayAbstractSearch.cfm?txtCriteria=algorithmic+trading](https://papers.ssrn.com/sol3/DisplayAbstractSearch.cfm?txtCriteria=algorithmic+trading) |

### 📂 GitHub (good for dry runs, not full scraping)

| Repo           | URL                                                                                                                          |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Backtrader     | [https://github.com/mementum/backtrader/tree/master/samples](https://github.com/mementum/backtrader/tree/master/samples)     |
| Freqtrade      | [https://github.com/freqtrade/freqtrade-strategies](https://github.com/freqtrade/freqtrade-strategies)                       |
| Backtesting.py | [https://github.com/kernc/backtesting.py/tree/master/examples](https://github.com/kernc/backtesting.py/tree/master/examples) |

---

## 🧪 Final Diagnostic Combo (Full Check)

```bash
python scripts/semantic_crawler.py \
  --url https://quantpedia.com/strategies/ \
  --threshold 0.75 \
  --save-raw \
  --limit-domains "quantpedia.com"
```

Then:

```bash
ls exports/
cat exports/*.json | jq '.score, .title, .url'
```

If you see real content with high semantic scores and proper URLs, **IntelForge is crawling and filtering correctly**.

Want a `test_crawler.sh` that automates this validation? I can generate one too.
