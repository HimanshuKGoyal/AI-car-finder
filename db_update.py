# scraper.py
import csv
import os
import sys
import time
import logging
from datetime import datetime
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

# === Configuration ===
BASE_URL = "https://example.com"
LIST_PATH = "/items"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "items.csv")
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "checkpoint.txt")

# Respectful scraping: identify yourself; adjust as appropriate
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; DataScraper/1.0; +https://yourdomain.example/scraper-info)"
}
REQUEST_TIMEOUT = 15  # seconds
RATE_LIMIT_SECONDS = 1.0  # pause between requests

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def make_session() -> requests.Session:
    """Create a requests session with retry/backoff."""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.8,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "HEAD"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(DEFAULT_HEADERS)
    return session

def ensure_output_paths():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "price", "url", "scraped_at"])

def load_checkpoint() -> set:
    """Track processed IDs to be idempotent across runs."""
    processed = set()
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                processed.add(line.strip())
    return processed

def save_checkpoint(processed: set):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        for pid in sorted(processed):
            f.write(pid + "\n")

def fetch(session: requests.Session, url: str) -> requests.Response:
    time.sleep(RATE_LIMIT_SECONDS)
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp

def parse_list_page(html: str) -> list[dict]:
    """Parse list page into item dicts with minimally required fields."""
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for card in soup.select(".item-card"):
        item_id = card.get("data-id") or card.select_one(".id").text.strip()
        title = (card.select_one(".title").text or "").strip()
        price = (card.select_one(".price").text or "").strip()
        href_el = card.select_one("a.details")
        url = urljoin(BASE_URL, href_el.get("href")) if href_el else BASE_URL
        items.append({"id": item_id, "title": title, "price": price, "url": url})
    return items

def append_rows(rows: list[dict]):
    now = datetime.utcnow().isoformat()
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r in rows:
            writer.writerow([r["id"], r["title"], r["price"], r["url"], now])

def main():
    # Prevent overlapping runs via a simple lock file
    lock_path = os.path.join(OUTPUT_DIR, ".lock")
    if os.path.exists(lock_path):
        logging.warning("Lock file exists; another run may be in progress. Exiting.")
        sys.exit(0)
    open(lock_path, "w").close()

    try:
        ensure_output_paths()
        processed = load_checkpoint()
        session = make_session()

        list_url = urljoin(BASE_URL, LIST_PATH)
        logging.info(f"Fetching list page: {list_url}")
        try:
            resp = fetch(session, list_url)
        except requests.HTTPError as e:
            # If 429 Too Many Requests, exit non-zero so scheduler can alert
            logging.error(f"HTTP error: {e}")
            sys.exit(2)

        items = parse_list_page(resp.text)
        logging.info(f"Found {len(items)} items.")

        new_items = [it for it in items if it["id"] not in processed]
        if not new_items:
            logging.info("No new items to process.")
            sys.exit(0)

        logging.info(f"Processing {len(new_items)} new items.")
        append_rows(new_items)
        processed.update(it["id"] for it in new_items)
        save_checkpoint(processed)
        logging.info("Scrape complete.")

    except Exception as e:
        logging.exception(f"Fatal error: {e}")
        # Non-zero exit so cron can notify
        sys.exit(1)
    finally:
        try:
            os.remove(lock_path)
        except Exception:
            pass

if __name__ == "__main__":
    main()
