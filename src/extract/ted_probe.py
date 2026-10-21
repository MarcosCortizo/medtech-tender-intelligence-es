"""
ted_probe.py - Week 1 discovery script (run once, by hand).

What it does (no database needed, no API key needed):
  1. Counts Spanish notices for our CPV seed list in the last DAYS_BACK days.
  2. Tests the CPV hierarchy (open check O3): does searching a parent code
     also return notices tagged only with a child code?
  3. Tests every candidate field name one by one (open check O1/O2):
     the API rejects unknown field names, so we learn which names are valid.
  4. Downloads up to SAMPLE_SIZE notices with all valid fields and measures
     the fill rate (% of notices where the field has a value).
  5. Saves evidence: data/sample/ted_probe_sample.json and
     data/sample/probe_report.md

Run from the repo root:
    python src/extract/ted_probe.py
"""

from __future__ import annotations

import csv
import json
import time
from datetime import date, timedelta
from pathlib import Path

import requests

# ---------------------------------------------------------------- settings
API_URL = "https://api.ted.europa.eu/v3/notices/search"
ROOT = Path(__file__).resolve().parents[2]          # repo root
SEED_FILE = ROOT / "seeds" / "cpv_category.csv"
OUT_DIR = ROOT / "data" / "sample"

DAYS_BACK = 90          # look-back window for the probe
SAMPLE_SIZE = 100       # notices downloaded for the fill-rate test (max 250)
PAUSE_S = 1.5           # pause between calls: rate limits are undocumented
TIMEOUT_S = 60

# Candidate field names. Some are Verified in the project brief, the rest are
# GUESSES we want the API to confirm or reject. Do not trust them until the
# probe marks them VALID.
CANDIDATE_FIELDS = [
    # identifiers
    "publication-number", "publication-date", "notice-type", "form-type",
    "notice-identifier", "procedure-identifier", "identifier-lot",
    # buyer
    "buyer-name", "buyer-city", "buyer-country",
    # what / when
    "classification-cpv", "notice-title", "dispatch-date",
    "deadline-receipt-tender-date-lot",
    # values
    "estimated-value-lot", "estimated-value-cur-lot",
    "estimated-value-proc", "estimated-value-cur-proc",
    "tender-value", "tender-value-cur", "result-value-lot",
    # award / competition
    "winner-name", "organisation-name-tenderer", "winner-country",
    "received-submissions-type-val", "received-submissions-type-code",
    # contract duration (re-tender KPI)
    "duration-period-value-lot", "duration-period-unit-lot",
    # link to the notice page
    "links",
]

# CPV hierarchy test (O3): parent and one child code
PARENT_CPV = "33110000"   # imaging equipment
CHILD_CPV = "33111000"    # X-ray devices (child of 33110000)


# ---------------------------------------------------------------- helpers
def post(body: dict) -> requests.Response:
    """POST to the TED search API, retrying once on HTTP 429 (too many requests)."""
    for attempt in (1, 2):
        resp = requests.post(API_URL, json=body, timeout=TIMEOUT_S,
                             headers={"Accept": "application/json"})
        if resp.status_code == 429 and attempt == 1:
            print("  HTTP 429 (rate limit) - waiting 30 s and retrying once")
            time.sleep(30)
            continue
        time.sleep(PAUSE_S)
        return resp
    return resp


def count(query: str) -> int | None:
    """Return the number of notices matching an expert query (None on error)."""
    body = {"query": query, "fields": ["publication-number"], "limit": 1,
            "scope": "ALL", "paginationMode": "PAGE_NUMBER"}
    resp = post(body)
    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code}: {resp.text[:300]}")
        return None
    return resp.json().get("totalNoticeCount")


def is_empty(value) -> bool:
    """True when a field value carries no information (None, '', [], {} ...)."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return all(is_empty(v) for v in value)
    if isinstance(value, dict):
        return all(is_empty(v) for v in value.values())
    return False


def load_cpv_seed() -> list[str]:
    with SEED_FILE.open(encoding="utf-8") as f:
        return [row["cpv_code"] for row in csv.DictReader(f)
                if row.get("include_flag", "1").strip() == "1"]


# ---------------------------------------------------------------- main
def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    since = (date.today() - timedelta(days=DAYS_BACK)).strftime("%Y%m%d")
    cpvs = load_cpv_seed()
    base = f"buyer-country=ESP AND publication-date>={since}"
    seed_query = f"{base} AND classification-cpv IN ({' '.join(cpvs)})"
    report: list[str] = [f"# TED probe report ({date.today()})", "",
                         f"Window: last {DAYS_BACK} days (publication-date >= {since})",
                         f"CPV seed ({len(cpvs)} codes): {', '.join(cpvs)}", ""]

    # 1. connectivity + volume
    print("1) Counting notices for the CPV seed ...")
    total = count(seed_query)
    print(f"   {total} notices")
    report += ["## 1. Volume", f"- Query: `{seed_query}`", f"- Notices: **{total}**", ""]
    if total is None:
        print("Stopping: the base query failed. Copy the error above to Claude.")
        return

    # 2. CPV hierarchy (O3)
    print("2) Testing CPV hierarchy ...")
    n_parent = count(f"{base} AND classification-cpv={PARENT_CPV}")
    n_child = count(f"{base} AND classification-cpv={CHILD_CPV}")
    n_union = count(f"{base} AND classification-cpv IN ({PARENT_CPV} {CHILD_CPV})")
    if None in (n_parent, n_child, n_union):
        verdict = "UNKNOWN (a query failed, see console)"
    elif n_child == 0:
        verdict = "UNKNOWN (child code has 0 notices; pick another child code)"
    elif n_union == n_parent:
        verdict = "Parent search INCLUDES child codes -> seed parent codes only"
    else:
        verdict = "Parent search is EXACT -> seed must list child codes too"
    print(f"   parent={n_parent} child={n_child} parent+child={n_union} -> {verdict}")
    report += ["## 2. CPV hierarchy (O3)",
               f"- {PARENT_CPV}: {n_parent} · {CHILD_CPV}: {n_child} · both: {n_union}",
               f"- Verdict: **{verdict}**", ""]

    # 3. field-name validation (O1/O2)
    print(f"3) Validating {len(CANDIDATE_FIELDS)} candidate field names ...")
    valid, invalid = [], {}
    for field in CANDIDATE_FIELDS:
        resp = post({"query": seed_query, "fields": [field], "limit": 1, "scope": "ALL"})
        if resp.status_code == 200:
            valid.append(field)
            print(f"   VALID    {field}")
        else:
            invalid[field] = resp.text[:150].replace("\n", " ")
            print(f"   INVALID  {field}  ({resp.status_code})")

    # 4. sample + fill rate
    print(f"4) Downloading {SAMPLE_SIZE} notices with {len(valid)} valid fields ...")
    resp = post({"query": seed_query, "fields": valid, "limit": SAMPLE_SIZE,
                 "scope": "ALL", "paginationMode": "PAGE_NUMBER"})
    notices = resp.json().get("notices", []) if resp.status_code == 200 else []
    if resp.status_code != 200:
        print(f"   ERROR {resp.status_code}: {resp.text[:300]}")
    n = len(notices) or 1
    report += ["## 3. Fields (O1, O2)", "",
               f"Sample: {len(notices)} notices", "",
               "| Field | Status | Fill rate |", "|---|---|---|"]
    for field in valid:
        filled = sum(not is_empty(nt.get(field)) for nt in notices)
        report.append(f"| `{field}` | VALID | {filled / n:.0%} |")
    for field, msg in invalid.items():
        report.append(f"| `{field}` | INVALID | - |")
    report.append("")

    # 5. evidence files
    sample_path = OUT_DIR / "ted_probe_sample.json"
    sample_path.write_text(json.dumps(notices[:20], ensure_ascii=False, indent=2),
                           encoding="utf-8")
    report_path = OUT_DIR / "probe_report.md"
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(f"\nDone. Evidence saved:\n  {sample_path}\n  {report_path}")


if __name__ == "__main__":
    main()
