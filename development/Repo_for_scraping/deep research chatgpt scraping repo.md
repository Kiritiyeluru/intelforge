Got it. I’ll look for actively maintained GitHub repositories offering prebuilt or easily extensible web scraping codebases for news, blogs, academic papers, and general websites. I’ll prioritize Python-based projects but will include others that can integrate well with a Python stack. I’ll also consider both open-source and high-value restrictive licenses if they're relevant, with a bias toward production-ready or well-documented academic projects.

I’ll get back to you with a detailed evaluation of the top repositories across your target areas.


# Prebuilt Scraping Codebases on GitHub

* **news-please** (Python, 2.3k★) – A mature, Scrapy-based news crawler and extractor. It “extracts structured information from almost any news website” by crawling links or RSS feeds.  Out of the box it parses article fields (headline, author, date, body, etc.) and supports CLI or library mode.  Outputs can be written to JSON, PostgreSQL, Redis, or Elasticsearch via configurable pipelines.  This makes it highly modular: you feed it a site or URL list and it returns clean article JSON.

  * **Prebuilt (5):** Includes ready-made extraction of headlines, authors, text, images, date, etc..
  * **Code Quality (4):** Well-documented and actively developed (2.3k stars, frequent commits).
  * **Dynamic (2):** Primarily designed for static pages (uses Newspaper3k, readability); no built-in JS engine (though one could plug in Splash).
  * **Maintenance (4):** Actively maintained by research team, regularly updated (2024).
  * **Adaptability (4):** Offers both CLI and library interfaces; pipelines for various outputs; easy to integrate into Python projects.

* **RISJbot** (Python, 73★) – A Scrapy framework for news sites, built for academic research. It “extracts text and metadata of articles from news websites” and includes many site-specific spiders (Guardian, BBC, CNN, NYT, etc.). It even has a generic fallback extractor using readability.  The project uses `scrapy-splash`, `newspaper`, and other libs to handle pages (including some JS).  Output is sent as JSON lines (e.g. to S3); it was developed for ongoing scraping of news feeds. However, RISJbot is research-grade (not production-hardened).

  * **Prebuilt (4):** Many pre-written spiders for major news sites; fallback parser covers generic pages.
  * **Code Quality (3):** Reasonably structured code, but less polished (minimal CI/tests).
  * **Dynamic (3):** Includes `scrapy-splash` for JS.
  * **Maintenance (3):** Moderately active (last updates by author; 73 stars).
  * **Adaptability (3):** Can be extended with new spiders; JSON output; but focused on news sites.

* **Mechanical News** (Python, 8★) – An application framework (Scrapy + Flask) for news crawling and research. It “scrapes and saves the full text of online news articles to a database” and exposes a REST API for analysts. It is designed for continuous crawling of news frontpages and URLs, storing headlines, body text and rich metadata (authors, date, tags, paywall flags, etc.). In practice you run its `run.py` to crawl sites and then query the local API. This is aimed at social-science research rather than commercial use.

  * **Prebuilt (4):** Has infrastructure for crawling and storing articles, and defines many metadata fields (headline, lead, body, authors, date, tags, etc.).
  * **Code Quality (3):** Clear architecture (Scrapy + Flask), but niche and somewhat academic.
  * **Dynamic (2):** Focuses on static HTML; no explicit JS support mentioned.
  * **Maintenance (2):** Low activity (8 stars, few commits); last updates unclear.
  * **Adaptability (3):** Good for Python-based workflows (database + API), but GPL-licensed and tailored for news.

* **binsarjr/news-scraper** (Python, 6★) – A Scrapy project targeting Indonesian news outlets. It “scrapes news articles from multiple prominent sources in Indonesia” (Kompas, CNN Indonesia, Detik, etc.). It supports keyword queries and date ranges via CLI or Python script, and outputs results to CSV/JSON. This is a country-specific example but illustrates how to chain Scrapy spiders and pipelines.

  * **Prebuilt (4):** Has spiders for 10+ major sites and can query by keyword/date.
  * **Code Quality (3):** Modular with Poetry setup; decent but fairly specialized.
  * **Dynamic (2):** Assumes static pages (Indonesian news sites are mostly static).
  * **Maintenance (3):** Some recent commits (2023 examples) but only 6 stars.
  * **Adaptability (2):** Good as a template, but tuned to Indonesian sources; limited broader use.

* **MahdiSadjadi/arXivScraper** (Python, 304★) – A utility to pull records from arXiv.org. It “scrape\[s] arXiv.org for a date range and category”.  You specify a category (e.g. `physics:cond-mat`) and date range, and it returns papers’ metadata (id, title, authors, abstract, DOI, dates). It can also filter on keywords in title/abstract. Output is a list or Pandas dataframe. This is stand-alone (pip-installable) but not a full framework – more of a convenience tool.

  * **Prebuilt (3):** Fetches metadata of arXiv entries; no generic crawling needed (uses arXiv’s HTML/list pages).
  * **Code Quality (3):** Simple API, MIT-licensed, moderate docs.
  * **Dynamic (1):** arXiv is static HTML; no JS.
  * **Maintenance (3):** 304 stars suggests use, but last update was some years back; still works.
  * **Adaptability (4):** Pure Python with filters; can be integrated or extended easily.

* **karthiktadepalli1/ssrn-scraper** (Python, 10★) – A small scraper for the Social Science Research Network (SSRN). It “crawls SSRN for working papers” using `requests` and BeautifulSoup. In practice it automates login or search to retrieve paper listings and details. This project is quite basic (10 stars, 7 forks) and aimed at one’s own crawling needs.

  * **Prebuilt (2):** Provides core logic for SSRN listing pages, but no general pipeline or many export options.
  * **Code Quality (2):** Minimal code (one main script), MIT license, no tests.
  * **Dynamic (1):** SSRN pages are static (no headless browser).
  * **Maintenance (2):** Low (few commits; 10 stars).
  * **Adaptability (2):** Very custom to SSRN; could be forked for similar academic sites.

* **JohnGiorgi/biorxiv-scraper** (Python, 11★) – A scraper for bioRxiv preprints. It provides a `bioRxivScraper` class that can fetch articles by year and subject area. For example `scraper.by_year(2019, subject_areas="Animal Behavior")` returns a dict of DOIs to metadata. It handles pagination and compiles titles, authors, etc. This is a notebook-based project, not a polished pipeline.

  * **Prebuilt (3):** Methods for common queries (by year/subject), returns structured dict of papers.
  * **Code Quality (2):** Lightly organized (Jupyter/NBdev style), Apache-2.0 license, minimal interface.
  * **Dynamic (1):** bioRxiv is static.
  * **Maintenance (2):** 11 stars; limited contributors.
  * **Adaptability (3):** Can be used as a library (pip installable); code can be reused for similar sites.

* **codelucas/newspaper** (Python, 14.5k★) – *Library* for article extraction. Newspaper3k “is a news, full-text, and article metadata extraction in Python 3”. It isn’t a full crawler, but given a URL it downloads the page, extracts the clean text, title, authors, publish date, etc. It also offers a “source crawling” mode (given a site, collect top stories). This library is widely used (14.5k stars) in many scraping projects as a building block.

  * **Prebuilt (5):** Instant extraction of content+metadata from any news URL.
  * **Code Quality (4):** Popular and mature (multi-licensed, active Git).
  * **Dynamic (1):** No headless browser; works on static HTML only.
  * **Maintenance (5):** Very active community use (14k stars); last releases in recent years.
  * **Adaptability (5):** Pure Python, pip-installable, integrates easily into any scraper.

* **Trafilatura** (Python) – A powerful text extraction library/CLI for *any* web page. It “gathers text on the Web and simplifies the process of turning raw HTML into structured data”. Trafilatura can crawl sitemaps and RSS, filter URLs, and then extract the main article text, metadata (title, author, date, tags), images, comments, etc.. It outputs in JSON/CSV/HTML/Markdown/etc. It is actively maintained (GitHub shows \~1.6k commits) and benchmarked as state-of-the-art.

  * **Prebuilt (5):** Full suite: crawling (sitemaps/feeds), smart URL filtering, and robust extraction (uses jusText, readability, etc.).
  * **Code Quality (5):** Highly polished (thousands of commits, used by major projects; Apache 2.0).
  * **Dynamic (2):** Focuses on HTML analysis; requires pre-downloaded HTML (no built-in browser).
  * **Maintenance (5):** Very active (updates and docs by maintainer Adrian Barbu; used by HuggingFace, IBM, etc.).
  * **Adaptability (5):** Flexible API/CLI; works on files or live URLs; outputs multiple formats; extensible modules.

Each of the above tools can serve as a plug-in component for a larger framework. **news-please** and **Mechanical News** offer the most end-to-end pipelines for news sites. **RISJbot** and the Indonesian news scraper provide reusable Scrapy templates. **ArXivScraper**, **SSRN-scraper**, and **bioRxiv-scraper** show examples of field-specific scrapers for academic content. And libraries like **Newspaper3k** and **Trafilatura** can be embedded into any Python scraper to extract article text and metadata with minimal code.

**Sources:** Project READMEs on GitHub.
