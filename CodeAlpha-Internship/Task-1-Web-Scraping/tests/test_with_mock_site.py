"""
Offline test: starts a tiny LOCAL web server that imitates the HTML structure of
books.toscrape.com, runs scrape_books.py against it, and checks the result.

IMPORTANT: the books here are FAKE test data made up by this script.
They are NOT from any real website. Output goes to tests/mock_output/.
Run:  python tests/test_with_mock_site.py
"""
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
WORDS = ["One", "Two", "Three", "Four", "Five"]
CATS = ["Poetry", "Travel", "Mystery"]
PER_PAGE, PAGES = 5, 3
flaky = {"hit": False}


def card(i):
    return f'''<article class="product_pod"><p class="star-rating {WORDS[i % 5]}"></p>
<h3><a href="book_{i}/index.html" title="Mock Book {i}">Mock Boo...</a></h3>
<div class="product_price"><p class="price_color">\u00a3{10 + i}.50</p>
<p class="instock availability"> In stock </p></div></article>'''


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        p = self.path
        if p == "/robots.txt":
            return self.send(404, "")
        if p.startswith("/catalogue/page-"):
            n = int(p.split("page-")[1].split(".")[0])
            if n > PAGES:
                return self.send(404, "")
            if n == 2 and not flaky["hit"]:  # simulate one temporary server error
                flaky["hit"] = True
                return self.send(500, "error")
            start = (n - 1) * PER_PAGE
            cards = "".join(card(i) for i in range(start, start + PER_PAGE))
            return self.send(200, "<html><body>" + cards + "</body></html>")
        if "/book_" in p:
            i = int(p.split("book_")[1].split("/")[0])
            return self.send(200, f'''<html><body><ul class="breadcrumb"><li>Home</li><li>Books</li><li>{CATS[i % 3]}</li></ul>
<table class="table table-striped"><tr><th>UPC</th><td>upc{i:04d}</td></tr>
<tr><th>Availability</th><td>In stock (7 available)</td></tr></table></body></html>''')
        self.send(404, "")

    def send(self, code, body):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


server = HTTPServer(("127.0.0.1", 8765), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()

out = ROOT / "tests" / "mock_output" / "MOCK_TEST_ONLY_books.csv"
result = subprocess.run(
    [sys.executable, str(ROOT / "scrape_books.py"), "--base-url", "http://127.0.0.1:8765/",
     "--max-pages", "10", "--delay", "0.05", "--output", str(out)],
    capture_output=True, text=True)
print(result.stdout, result.stderr)
server.shutdown()

df = pd.read_csv(out)
assert len(df) == PER_PAGE * PAGES, f"expected {PER_PAGE * PAGES} rows, got {len(df)}"
assert df["category"].notna().all() and df["upc"].notna().all()
assert df["rating"].between(1, 5).all()
print("ALL MOCK TESTS PASSED (retry after HTTP 500, pagination stop on 404, parsing, validation)")
