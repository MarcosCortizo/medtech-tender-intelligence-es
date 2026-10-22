import sys
from datetime import date, datetime, timedelta
from pathlib import Path

SRC = Path(__file__).resolve().parent
ROOT = SRC.parent
for folder in ["extract", "transform", "load"]:
    sys.path.append(str(SRC / folder))

from db import connect
from extract import extract
from flatten import flatten
from load_staging import count, load

LOAD_SQL = ROOT / "sql" / "03_load"
DQ_SQL = ROOT / "sql" / "04_dq" / "01_dq_checks.sql"
WINDOW_DAYS = 14


def run_sql_files():
    with connect() as conn:
        cursor = conn.cursor()
        for path in sorted(LOAD_SQL.glob("*.sql")):
            cursor.execute(path.read_text(encoding="utf-8-sig"))
            print(f"{path.name}: {cursor.rowcount} new rows")
        cursor.execute(DQ_SQL.read_text(encoding="utf-8-sig"))
        print("dq checks saved")
        conn.commit()


def table_counts():
    with connect() as conn:
        cursor = conn.cursor()
        return count(cursor, "stg_notice"), count(cursor, "stg_lot")


def write_log(started, status, new_notices, new_lots, error):
    with connect() as conn:
        conn.execute(
            "INSERT INTO etl_run_log (started_at, finished_at, status, new_notices, new_lots, error_message) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            started, datetime.now(), status, new_notices, new_lots, error,
        )
        conn.commit()


def main():
    started = datetime.now()
    end = date.today()
    start = end - timedelta(days=WINDOW_DAYS)
    notices_before, lots_before = table_counts()
    status, error = "OK", None

    try:
        raw_file = extract(start, end)
        notices, lots = flatten(raw_file)
        if notices:
            load(raw_file.stem)
        run_sql_files()
    except Exception as err:
        status, error = "FAIL", str(err)[:1000]
        print(f"Pipeline failed: {error}")

    notices_after, lots_after = table_counts()
    write_log(started, status, notices_after - notices_before, lots_after - lots_before, error)
    print(f"Run {status}: {notices_after - notices_before} new notices, {lots_after - lots_before} new lots")

    if status == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()