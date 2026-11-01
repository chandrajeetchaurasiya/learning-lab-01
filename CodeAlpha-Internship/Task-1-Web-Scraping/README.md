# Task 1: Web Scraping – Books to Scrape

**CodeAlpha Data Analytics Internship** | Student: Chandrajeet Chaurasiya | ID: CA/DF1/317087

## Project objective
Build a Python scraper that collects book data from a public practice website and saves it as a clean CSV dataset.

## Problem statement
Websites show data as HTML, not as tables. This project converts the HTML pages of *Books to Scrape* (https://books.toscrape.com, a site built for scraping practice) into a structured dataset ready for analysis.

## Tools and technologies
Python 3.12/3.13, Requests (download pages), BeautifulSoup4 (read HTML), Pandas (validate and save CSV).

## Dataset description (columns produced)
| Column | Meaning |
|---|---|
| title | Book title |
| price_gbp | Price in British pounds |
| rating | Star rating 1–5 |
| in_stock | True/False |
| url | Book page link |
| category | Genre (from the book's detail page) |
| upc | Product code |
| stock_count | Copies available |

## Methodology
1. Check `robots.txt` politely.
2. Visit listing pages `catalogue/page-1.html`, `page-2.html`, … until a page returns 404 (website navigation / pagination).
3. Parse each `article.product_pod` card for title, price, rating, stock, link.
4. Open every book's detail page for category, UPC and stock count.
5. Validate: remove duplicates, remove invalid prices/ratings, report missing values.
6. Save to `data/books_dataset.csv` and `output/validation_report.txt`.

**Error handling:** 15-second timeouts, 3 retries with growing waits, 1-second delay between requests, malformed cards skipped with a message, graceful stop on 404, clear exit message if nothing was scraped.

## Project structure
```
Task_1_Web_Scraping/
├── scrape_books.py          # the scraper
├── requirements.txt
├── README.md
├── data/                    # books_dataset.csv appears here after you run it
├── output/                  # validation_report.txt appears here after you run it
└── tests/
    └── test_with_mock_site.py   # offline test using FAKE local data
```

## How to run (VS Code terminal, Windows PowerShell)
```powershell
cd Task_1_Web_Scraping
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python scrape_books.py --max-pages 3     # quick trial (60 books, ~2 minutes)
python scrape_books.py                   # full run: 50 pages, ~1000 books, ~17 minutes
python scrape_books.py --no-details      # faster, but no category/UPC
```
If PowerShell blocks activation, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Results
The real `data/books_dataset.csv` is created **when you run the scraper on your own computer**. It was **not** included here because the environment where this project was built had no access to books.toscrape.com, and generated data must never be passed off as scraped data.

## Testing status (honest summary)
- ✅ `scrape_books.py` passes a Python syntax check.
- ✅ `tests/test_with_mock_site.py` passed. It runs the scraper against a **local fake website with made-up books** that copies the real site's HTML structure. It verified parsing, pagination stop, retry after a simulated HTTP 500, validation and CSV writing. The output (`tests/mock_output/MOCK_TEST_ONLY_books.csv`) is **fake test data, not real books**.
- ❌ **Not yet run against the live site.** The selectors follow the documented structure of Books to Scrape, but please run the quick trial first (`--max-pages 3`) and check the CSV.
- Built and tested on Python 3.12; the code uses nothing version-specific, so it should work on 3.13.

## Key findings
Not applicable: this task delivers a dataset. After your real run, `validation_report.txt` lists exact row counts. Analysing the scraped books would be a follow-up EDA.

## Conclusion
The project demonstrates HTML parsing, pagination, polite scraping, error handling and data validation, producing a CSV ready for analysis.
