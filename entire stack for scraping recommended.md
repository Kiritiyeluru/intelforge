# 🚀 IntelForge High-Performance Scraping Pipeline (Python 3.10 + Rust)
# Requirements: httpx, selectolax, trafilatura, playwright, stealth-requests, polars, duckdb, sentence-transformers, qdrant-client, tokenizers, PyYAML

import asyncio
import httpx
import yaml
import hashlib
import time
from selectolax.parser import HTMLParser
from trafilatura import extract
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Distance, VectorParams, CollectionStatus
import polars as pl
import duckdb
from pathlib import Path

# ────────────────────────────────────────────────
# 📁 Load config
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

HEADERS = CONFIG["headers"]
URLS = CONFIG["urls"]
COLLECTION = CONFIG["qdrant_collection"]
MODEL_NAME = CONFIG["embedding_model"]

# ────────────────────────────────────────────────
# 🔗 Fetch URLs concurrently
async def fetch(client, url):
    try:
        r = await client.get(url, timeout=20)
        return r.text, url
    except Exception as e:
        print(f"[ERROR] Failed to fetch {url}: {e}")
        return None, url

async def fetch_all(urls):
    async with httpx.AsyncClient(headers=HEADERS, http2=True) as client:
        return await asyncio.gather(*[fetch(client, url) for url in urls])

# ────────────────────────────────────────────────
# ✂️ Parse and extract with selectolax + trafilatura

def parse_content(html, url):
    try:
        dom = HTMLParser(html)
        title = dom.css_first("title").text() if dom.css_first("title") else "No Title"
        main_text = extract(html)
        return {
            "url": url,
            "title": title,
            "content": main_text or "",
        }
    except Exception as e:
        print(f"[ERROR] Failed to parse {url}: {e}")
        return {}

# ────────────────────────────────────────────────
# 🧠 Vector embedding and Qdrant storage
model = SentenceTransformer(MODEL_NAME)
client = QdrantClient(path="./qdrant_storage")

if COLLECTION not in [c.name for c in client.get_collections().collections]:
    client.recreate_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

def embed_and_store(records):
    points = []
    for rec in records:
        if not rec.get("content"): continue
        vec = model.encode(rec["content"]).tolist()
        uid = int(hashlib.md5(rec["url"].encode()).hexdigest(), 16) % (10 ** 18)
        points.append(PointStruct(id=uid, vector=vec, payload=rec))
    client.upsert(collection_name=COLLECTION, points=points)
    print(f"[✓] Stored {len(points)} records in Qdrant")

# ────────────────────────────────────────────────
# 💾 Save to DuckDB

def save_to_duckdb(records):
    df = pl.DataFrame(records)
    Path("data").mkdir(exist_ok=True)
    df.write_parquet("data/scraped.parquet")
    duckdb.sql("CREATE TABLE IF NOT EXISTS scraped AS SELECT * FROM parquet_scan('data/scraped.parquet')")
    print("[✓] Stored in DuckDB")

# ────────────────────────────────────────────────
# 🔁 Full pipeline execution

def run_pipeline():
    print("[▶] Fetching URLs...")
    raw_pages = asyncio.run(fetch_all(URLS))

    print("[🔍] Parsing content...")
    parsed = [parse_content(html, url) for html, url in raw_pages if html]

    print("[💾] Saving to DuckDB...")
    save_to_duckdb(parsed)

    print("[🧠] Embedding and storing vectors...")
    embed_and_store(parsed)

    print("[✅] Pipeline completed.")

if __name__ == "__main__":
    run_pipeline()
