"""
extract.py - step 2.1
Downloads TED notices (Spain + our CPV list) for a date window
and saves the raw answer as one JSON file in data/raw/.

Run from the repo root:
    python src/extract/extract.py                          # last 7 days
    python src/extract/extract.py 2026-09-01 2026-09-30    # chosen window
"""
import csv
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

import requests

API_URL = "https://api.ted.europa.eu/v3/notices/search"
ROOT = Path(__file__).resolve().parents[2]
SEED_FILE = ROOT / "seeds" / "cpv_category.csv"
RAW_DIR = ROOT / "data" / "raw"

PAGE_SIZE = 250  # the most TED gives per page

FIELDS = [
    "publication-number", "publication-date", "notice-type", "form-type",
    "notice-identifier", "procedure-identifier", "identifier-lot",
    "buyer-name", "buyer-city", "buyer-country",
    "classification-cpv", "notice-title", "dispatch-date",
    "deadline-receipt-tender-date-lot",
    "estimated-value-lot", "estimated-value-cur-lot",
    "estimated-value-proc", "estimated-value-cur-proc",
    "tender-value", "tender-value-cur",
    "winner-name", "organisation-name-tenderer", "winner-country",
    "received-submissions-type-val", "received-submissions-type-code",
    "duration-period-value-lot", "duration-period-unit-lot",
    "winner-decision-date", "contract-conclusion-date",
    "links",
]


def load_cpv_codes():
    with SEED_FILE.open(encoding="utf-8") as f:
        return [row["cpv_code"] for row in csv.DictReader(f)
                if row.get("include_flag", "1").strip() == "1"]


def get_page(query, page):
    """Ask TED for one page. Try up to 3 times before giving up."""
    body = {"query": query, "fields": FIELDS, "limit": PAGE_SIZE, "page": page,
            "scope": "ALL", "paginationMode": "PAGE_NUMBER"}
    for attempt in range(1, 4):
        try:
            resp = requests.post(API_URL, json=body, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            print(f"  attempt {attempt}: HTTP {resp.status_code} {resp.text[:200]}")
        except requests.RequestException as err:  # no internet, timeout...
            print(f"  attempt {attempt}: {err}")
        time.sleep(10 * attempt)  # wait 10 s, then 20 s, then 30 s
    raise RuntimeError("TED API failed 3 times, stopping")


def extract(start, end):
    cpvs = load_cpv_codes()
    query = (f"buyer-country=ESP"
             f" AND publication-date>={start:%Y%m%d}"
             f" AND publication-date<={end:%Y%m%d}"
             f" AND classification-cpv IN ({' '.join(cpvs)})")

    notices = []
    page = 1
    while True:
        data = get_page(query, page)
        batch = data.get("notices", [])
        notices.extend(batch)
        print(f"  page {page}: {len(batch)} notices")
        if len(batch) < PAGE_SIZE:  # a page that isn't full is the last one
            break
        page += 1
        time.sleep(1.5)  # be polite to the API

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RAW_DIR / f"ted_{start}_{end}.json"
    out_file.write_text(json.dumps(notices, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"Saved {len(notices)} notices "
          f"(TED says {data.get('totalNoticeCount')}) -> {out_file}")
    return out_file


if __name__ == "__main__":
    if len(sys.argv) == 3:
        start = date.fromisoformat(sys.argv[1])
        end = date.fromisoformat(sys.argv[2])
    else:
        end = date.today()
        start = end - timedelta(days=7)
    extract(start, end)