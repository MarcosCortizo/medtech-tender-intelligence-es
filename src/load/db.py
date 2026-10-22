import os
import time

import pyodbc
from dotenv import load_dotenv

load_dotenv()


def connect():
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER=tcp:{os.environ['SQL_SERVER']},1433;"
        f"DATABASE={os.environ['SQL_DB']};"
        f"UID={os.environ['SQL_USER']};"
        f"PWD={os.environ['SQL_PASSWORD']};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60;"
    )
    for attempt in range(1, 4):
        try:
            return pyodbc.connect(conn_str)
        except pyodbc.OperationalError as err:
            if attempt == 3:
                raise
            print(f"connection attempt {attempt} failed, database may be waking up: {err}")
            time.sleep(30)


if __name__ == "__main__":
    with connect() as conn:
        print(conn.execute("SELECT DB_NAME()").fetchone()[0])
