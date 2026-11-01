"""
Task 1: Web Scraping - Books to Scrape
CodeAlpha Data Analytics Internship | Student ID: CA/DF1/317087

Scrapes https://books.toscrape.com (a website built for scraping practice).
For every book it collects: title, price, rating, stock, category, UPC, URL.

Usage (PowerShell):
    python scrape_books.py                  # all 50 pages + detail pages (~15-20 min)
    python scrape_books.py --max-pages 3    # quick run, first 3 pages
    python scrape_books.py --no-details     # faster, skips category/UPC
"""

import argparse
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "CodeAlpha-Internship-Learning-Scraper/1.0 (educational use)"}
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "output"


def check_robots(base_url):
    """Politely check robots.txt. If it can't be read, we still scrape slowly."""
    rp = RobotFileParser()
    try:
        rp.set_url(urljoin(base_url, "robots.txt"))
        rp.read()
        return rp.can_fetch(HEADERS["User-Agent"], base_url)
    except Exception:
        print("Note: robots.txt could not be read; continuing with polite delays.")
        return True


def fetch_page(session, url, delay, retries=3):
    """Download a page with retries. Returns BeautifulSoup or None on failure."""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 404:
                return None  # page does not exist (used to detect the last page)
            response.raise_for_status()
            response.encoding = "utf-8"  # avoids broken pound-sign characters
            time.sleep(delay)  # be polite to the server
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as error:
            print(f"  Attempt {attempt}/{retries} failed for {url}: {error}")
            time.sleep(delay * attempt)
    print(f"  Giving up on {url}")
    return None


def parse_price(text):
    """'£51.77' -> 51.77 ; returns None if there is no number."""
    match = re.search(r"\d+(?:\.\d+)?", text or "")
    return float(match.group()) if match else None


def parse_listing(soup, page_url):
    """Extract basic info for every book on one listing page."""
    books = []
    for card in soup.select("article.product_pod"):
        try:
            link = card.h3.a
            rating_class = card.select_one("p.star-rating")["class"]
            rating = next((RATING_WORDS[c] for c in rating_class if c in RATING_WORDS), None)
            books.append({
                "title": link["title"].strip(),
                "price_gbp": parse_price(card.select_one("p.price_color").text),
                "rating": rating,
                "in_stock": "in stock" in card.select_one("p.availability").text.lower(),
                "url": urljoin(page_url, link["href"]),
            })
        except (AttributeError, KeyError, TypeError) as error:
            print(f"  Skipping one malformed book card: {error}")
    return books


def parse_detail(soup):
    """Extract category, UPC and stock count from a book detail page."""
    details = {"category": None, "upc": None, "stock_count": None}
    crumbs = soup.select("ul.breadcrumb li")
    if len(crumbs) >= 3:
        details["category"] = crumbs[2].text.strip()
    table = {row.th.text.strip(): row.td.text.strip() for row in soup.select("table.table-striped tr")}
    details["upc"] = table.get("UPC")
    match = re.search(r"(\d+)\s+available", table.get("Availability", ""))
    details["stock_count"] = int(match.group(1)) if match else None
    return details


def listing_url(base_url, page):
    return urljoin(base_url, f"catalogue/page-{page}.html")


def scrape(base_url, max_pages, delay, with_details):
    if not check_robots(base_url):
        sys.exit("robots.txt does not allow scraping. Stopping.")
    session = requests.Session()
    all_books = []

    for page in range(1, max_pages + 1):
        url = listing_url(base_url, page)
        print(f"Scraping listing page {page}: {url}")
        soup = fetch_page(session, url, delay)
        if soup is None:
            print("No more pages (or page failed). Stopping pagination.")
            break
        all_books.extend(parse_listing(soup, url))

    if with_details:
        print(f"Fetching detail pages for {len(all_books)} books...")
        for i, book in enumerate(all_books, start=1):
            soup = fetch_page(session, book["url"], delay)
            if soup is not None:
                book.update(parse_detail(soup))
            if i % 50 == 0:
                print(f"  {i}/{len(all_books)} detail pages done")
    return all_books


def validate(df):
    """Basic data validation. Returns (clean_df, report_lines)."""
    report = [f"Rows scraped: {len(df)}"]
    before = len(df)
    df = df.drop_duplicates(subset="url")
    report.append(f"Duplicate rows removed: {before - len(df)}")
    bad_price = df["price_gbp"].isna() | (df["price_gbp"] <= 0)
    report.append(f"Rows with missing/invalid price removed: {int(bad_price.sum())}")
    df = df[~bad_price]
    bad_rating = ~df["rating"].isin([1, 2, 3, 4, 5])
    report.append(f"Rows with invalid rating removed: {int(bad_rating.sum())}")
    df = df[~bad_rating]
    report.append(f"Final rows: {len(df)}")
    report.append("Missing values per column:")
    report.extend(f"  {col}: {n}" for col, n in df.isna().sum().items())
    return df.reset_index(drop=True), report


def main():
    parser = argparse.ArgumentParser(description="Books to Scrape web scraper")
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between requests")
    parser.add_argument("--no-details", action="store_true")
    parser.add_argument("--output", default=str(DATA_DIR / "books_dataset.csv"))
    args = parser.parse_args()

    base = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    books = scrape(base, args.max_pages, args.delay, not args.no_details)
    if not books:
        sys.exit("No books were scraped. Check your internet connection.")

    df, report = validate(pd.DataFrame(books))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    # Report goes to output/ for normal runs, or next to a custom --output file (used by tests)
    report_dir = OUTPUT_DIR if out_path.parent == DATA_DIR else out_path.parent
    report_dir.mkdir(exist_ok=True)
    (report_dir / "validation_report.txt").write_text("\n".join(report), encoding="utf-8")
    print("\n".join(report))
    print(f"\nSaved dataset to: {out_path}")


if __name__ == "__main__":
    main()
