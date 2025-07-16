

Sure — here are **three excellent and safe websites** you can practice scraping with IntelForge:

---

## 📙 1. **books.toscrape.com**
A static, sandbox bookstore built for learning scraping.
- No login or JavaScript needed.
- Ideal for practicing pagination, parsing titles, prices, stock statuses, and ratings.
- **“Warning! This is a demo website for web scraping purposes”** — free to scrape freely citeturn0search1turn0search3.

---

## 💬 2. **quotes.toscrape.com**
Part of the same sandbox domain, this site features:
- Multiple endpoints (quotes, authors, tags)
- JavaScript and AJAX examples in some endpoints
Perfect for testing `intelforge` in regex vs JS parsing mode citeturn0search3.

---

## 🎯 3. **ScrapePark.org**
A dedicated public scraping sandbox by freeCodeCamp.
- Built specifically for heavy scraping practice
- Contains interactive elements (forms, tables, images, dropdowns)
- Designed to be scraped at scale — IntelForge can operate here at full speed citeturn0search0.

---

## ⚙️ Example: Scraping `books.toscrape.com` with IntelForge

Assuming IntelForge supports standard sync and filters:

```bash
intelforge sync \
  --source-url https://books.toscrape.com \
  --limit-domains "books.toscrape.com" \
  --intent "book title price availability rating" \
  --limit-urls 50 \
  --save-raw \
  --strict
```

This tells IntelForge to:
- Crawl up to 50 book pages from this domain
- Filter by relevance to "book title price availability rating"
- Save raw HTML and enforce strict health checks

---

## 🔁 Example: scraping quotes

```bash
intelforge sync \
  --source-url https://quotes.toscrape.com \
  --limit-domains "quotes.toscrape.com" \
  --crawl-mode deep \
  --intent "author quote tag" \
  --save-raw \
  --strict
```

Going “deep” follows all internal links (authors, tags), pulling structured content.

---

## ⚡ Example: ScrapePark.org as a stress test

```bash
intelforge sync \
  --source-url https://scrapepark.org \
  --limit-domains "scrapepark.org" \
  --crawl-mode full \
  --intent "table list dropdown iframe" \
  --proxy-rotate \
  --save-raw
```

This exercises parts of the scraper like tables, iframes, and drop-down forms under load.

---

## ✅ TL;DR: Steps to try

1. Choose a sandbox site (start with `books.toscrape.com`).
2. Plug it into IntelForge with proper flags.
3. Inspect `/logs/`, DB and raw HTML to confirm what got scraped.

Let me know once you try it — I can help debug filters, intents, or flag usage based on actual IntelForge logs!
