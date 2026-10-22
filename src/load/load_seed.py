from pathlib import Path

from db import connect
from load_staging import count, insert_new, read_csv

ROOT = Path(__file__).resolve().parents[2]
CPV_FILE = ROOT / "seeds" / "cpv_category.csv"
ALIAS_FILE = ROOT / "seeds" / "name_alias.csv"


def load_cpv():
    df = read_csv(CPV_FILE)
    df = df[df["include_flag"] == "1"]
    df = df.rename(columns={"cpv_label_en": "cpv_label"})
    df = df[["cpv_code", "cpv_label", "category"]]
    with connect() as conn:
        cursor = conn.cursor()
        insert_new(cursor, "cpv_category", ["cpv_code"], df)
        conn.commit()
        print(f"cpv_category: {count(cursor, 'cpv_category')} rows")


def load_alias():
    df = read_csv(ALIAS_FILE)
    df = df[["entity", "variant_key", "official_key", "reason"]]
    with connect() as conn:
        cursor = conn.cursor()
        insert_new(cursor, "name_alias", ["entity", "variant_key"], df)
        conn.commit()
        print(f"name_alias: {count(cursor, 'name_alias')} rows")


if __name__ == "__main__":
    load_cpv()
    load_alias()