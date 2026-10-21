import csv
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
FLAT_DIR = ROOT / "data" / "flat"
NOTICE_URL = "https://ted.europa.eu/es/notice/-/detail/{}"


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def first(value):
    items = as_list(value)
    return items[0] if items else None


def pick_list(value):
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    texts = value.get("spa") or next(iter(value.values()))
    return as_list(texts)


def pick_text(value):
    texts = [t for t in pick_list(value) if t not in ("", "No consta")]
    return texts[0] if texts else None


def clean_title(value):
    title = pick_text(value)
    return title.split(" – ", 2)[-1] if title else None


def clean_date(text):
    return date.fromisoformat(text[:10]) if text else None


def clean_amount(text):
    if text is None:
        return None
    amount = Decimal(text)
    return amount if amount > 0 else None


def clean_int(text):
    return int(Decimal(text)) if text is not None else None


def per_lot(values, n_lots, repeat=True):
    values = as_list(values)
    if len(values) == n_lots:
        return values
    if repeat and len(set(values)) == 1:
        return [values[0]] * n_lots
    return [None] * n_lots


def tenders_received(codes, vals):
    return [v for c, v in zip(as_list(codes), as_list(vals)) if c == "tenders"]


def notice_row(n):
    pub = n.get("publication-number")
    return {
        "publication_number": pub,
        "notice_id": n.get("notice-identifier"),
        "procedure_id": n.get("procedure-identifier"),
        "notice_type": n.get("notice-type"),
        "form_type": n.get("form-type"),
        "publication_date": clean_date(n.get("publication-date")),
        "dispatch_date": clean_date(n.get("dispatch-date")),
        "buyer_name": pick_text(n.get("buyer-name")),
        "buyer_city": pick_text(n.get("buyer-city")),
        "title": clean_title(n.get("notice-title")),
        "cpv_codes": ",".join(sorted(set(as_list(n.get("classification-cpv"))))),
        "estimated_value_proc": clean_amount(first(n.get("estimated-value-proc"))),
        "notice_url": NOTICE_URL.format(pub),
    }


def lot_rows(n):
    lot_ids = as_list(n.get("identifier-lot"))
    k = len(lot_ids)
    estimated = per_lot(n.get("estimated-value-lot"), k, repeat=False)
    awarded = per_lot(n.get("tender-value"), k, repeat=False)
    winners = per_lot(pick_list(n.get("winner-name")), k, repeat=False)
    bids = per_lot(tenders_received(n.get("received-submissions-type-code"),
                                    n.get("received-submissions-type-val")), k, repeat=False)
    deadlines = per_lot(n.get("deadline-receipt-tender-date-lot"), k)
    durations = per_lot(n.get("duration-period-value-lot"), k)
    units = per_lot(n.get("duration-period-unit-lot"), k)
    contracts = per_lot(n.get("contract-conclusion-date"), k)
    currency = first(n.get("tender-value-cur")) or first(n.get("estimated-value-cur-lot"))

    rows = []
    for i, lot_id in enumerate(lot_ids):
        rows.append({
            "publication_number": n.get("publication-number"),
            "lot_id": lot_id,
            "estimated_value": clean_amount(estimated[i]),
            "tender_value": clean_amount(awarded[i]),
            "currency": currency,
            "winner_name": winners[i],
            "tenders_received": clean_int(bids[i]),
            "deadline_date": clean_date(deadlines[i]),
            "duration_value": clean_int(durations[i]),
            "duration_unit": units[i],
            "contract_date": clean_date(contracts[i]),
        })
    return rows


def save_csv(rows, path):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def flatten(raw_file):
    notices = json.loads(raw_file.read_text(encoding="utf-8"))
    notice_table = [notice_row(n) for n in notices]
    lot_table = [row for n in notices for row in lot_rows(n)]

    FLAT_DIR.mkdir(parents=True, exist_ok=True)
    save_csv(notice_table, FLAT_DIR / f"{raw_file.stem}_notice.csv")
    save_csv(lot_table, FLAT_DIR / f"{raw_file.stem}_lot.csv")
    print(f"{len(notice_table)} notices, {len(lot_table)} lots -> {FLAT_DIR}")
    return notice_table, lot_table


if __name__ == "__main__":
    if len(sys.argv) == 2:
        raw_file = Path(sys.argv[1])
    else:
        raw_file = max(RAW_DIR.glob("ted_*.json"), key=lambda p: p.stat().st_mtime)
    flatten(raw_file)