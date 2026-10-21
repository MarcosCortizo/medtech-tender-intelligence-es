import os
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
    return pyodbc.connect(conn_str)


if __name__ == "__main__":
    with connect() as conn:
        print(conn.execute("SELECT DB_NAME()").fetchone()[0])