import sys
from pathlib import Path

import pandas as pd

from db import connect

ROOT = Path(__file__).resolve().parents[2]
FLAT_DIR = ROOT / "data" / "flat"

TABLES = [
    ("notice", "stg_notice", ["publication_number"]),
    ("lot", "stg_lot", ["publication_number", "lot_id"]),
]


def read_csv(path):
    df = pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    return df.astype(object).where(df.notna(), None)


def insert_new(cursor, table, keys, df):
    cols = list(df.columns)
    match = " AND ".join(f"{k} = ?" for k in keys)
    marks = ", ".join("?" for _ in cols)
    sql = (
        f"IF NOT EXISTS (SELECT 1 FROM {table} WHERE {match}) "
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({marks})"
    )
    for row in df.to_dict("records"):
        params = [row[k] for k in keys] + [row[c] for c in cols]
        cursor.execute(sql, params)


def count(cursor, table):
    return cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def load(stem):
    with connect() as conn:
        cursor = conn.cursor()
        for part, table, keys in TABLES:
            df = read_csv(FLAT_DIR / f"{stem}_{part}.csv")
            before = count(cursor, table)
            insert_new(cursor, table, keys, df)
            after = count(cursor, table)
            print(f"{table}: {len(df)} rows in file, {after - before} new, {after} in table")
        conn.commit()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        stem = sys.argv[1]
    else:
        latest = max(FLAT_DIR.glob("ted_*_notice.csv"), key=lambda p: p.stat().st_mtime)
        stem = latest.name.removesuffix("_notice.csv")
    load(stem)