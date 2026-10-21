

from collections import Counter, defaultdict
from datetime import date, timedelta

from ted_probe import CANDIDATE_FIELDS, DAYS_BACK, OUT_DIR, is_empty, load_cpv_seed, post


def first(value):
    """TED often returns lists. For grouping we only need the first item."""
    if isinstance(value, list):
        return value[0] if value else None
    return value


def main() -> None:
    since = (date.today() - timedelta(days=DAYS_BACK)).strftime("%Y%m%d")
    query = (f"buyer-country=ESP AND publication-date>={since} "
             f"AND classification-cpv IN ({' '.join(load_cpv_seed())})")

    print("Downloading notices ...")
    resp = post({"query": query, "fields": CANDIDATE_FIELDS, "limit": 250,
                 "scope": "ALL", "paginationMode": "PAGE_NUMBER"})
    if resp.status_code != 200:
        print(f"ERROR {resp.status_code}: {resp.text[:300]}")
        return
    data = resp.json()
    notices = data.get("notices", [])
    print(f"Got {len(notices)} of {data.get('totalNoticeCount')} notices")

    # group notices by form type
    groups = defaultdict(list)
    for nt in notices:
        groups[str(first(nt.get("form-type")))].append(nt)
    types = sorted(groups, key=lambda t: -len(groups[t]))

    # which notice types sit inside each form type
    mix = Counter((str(first(nt.get("form-type"))), str(first(nt.get("notice-type"))))
                  for nt in notices)

    lines = [f"# Fill rate by form type ({date.today()})", "",
             f"Notices: {len(notices)} (last {DAYS_BACK} days)", "",
             "## Form type -> notice type", "",
             "| form-type | notice-type | notices |", "|---|---|---|"]
    lines += [f"| {f} | {n} | {c} |" for (f, n), c in mix.most_common()]

    lines += ["", "## Fill rate per field", "",
              "| Field | " + " | ".join(f"{t} (n={len(groups[t])})" for t in types) + " |",
              "|---|" + "---|" * len(types)]
    for field in CANDIDATE_FIELDS:
        cells = []
        for t in types:
            filled = sum(not is_empty(nt.get(field)) for nt in groups[t])
            cells.append(f"{filled / len(groups[t]):.0%}")
        lines.append(f"| `{field}` | " + " | ".join(cells) + " |")

    report = "\n".join(lines)
    path = OUT_DIR / "fill_by_type.md"
    path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nSaved: {path}")


if __name__ == "__main__":
    main()