from pathlib import Path

from db import connect
from load_staging import count, insert_new, read_csv

ROOT = Path(__file__).resolve().parents[2]
SEED_FILE = ROOT / "seeds" / "cpv_category.csv"


def load_cpv():
    df = read_csv(SEED_FILE)
    df = df[df["include_flag"] == "1"]
    df = df.rename(columns={"cpv_label_en": "cpv_label"})
    df = df[["cpv_code", "cpv_label", "category"]]
    with connect() as conn:
        cursor = conn.cursor()
        insert_new(cursor, "cpv_category", ["cpv_code"], df)
        conn.commit()
        print(f"cpv_category: {count(cursor, 'cpv_category')} rows")


if __name__ == "__main__":
    load_cpv()