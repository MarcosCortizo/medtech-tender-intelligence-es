# Medtech Public Tender Intelligence (Spain)

Spanish public tenders for medical imaging and radiotherapy equipment, collected from the EU TED API, stored in Azure SQL and shown in Power BI for a medtech sales / tender team.

```
TED API -> raw JSON -> CSV -> Azure SQL (staging -> core) -> Power BI
```

**Status:** step 3, building the core model in SQL. Staging has Oct 2024 to Oct 2026 (524 notices, 1,429 lots).

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Azure SQL details.

Create the database objects once, in this order:

1. `sql/01_staging/01_create_staging.sql`
2. the files in `sql/02_core`, in number order
3. `python src/load/load_seed.py`

## Load data

For a date window:

```powershell
python src/extract/extract.py 2026-09-01 2026-09-30
python src/transform/flatten.py data/raw/ted_2026-09-01_2026-09-30.json
python src/load/load_staging.py ted_2026-09-01_2026-09-30
```

Then run the files in `sql/03_load`, in number order. Running the same window twice adds no duplicates.

## Name cleaning

TED has the same company written in many ways (GE Healthcare has 11 spellings). `dbo.clean_name` turns each name into one key: capitals, no accents, no punctuation and no legal form at the end (S.A., S.L.U., GmbH...).

```
General Electric Healthcare España, S.A.U.  ->  GENERAL ELECTRIC HEALTHCARE ESPANA
GENERAL ELECTRIC HEALTHCARE ESPAÑA SAU      ->  GENERAL ELECTRIC HEALTHCARE ESPANA
```

It uses `REGEXP_REPLACE`, so it needs Azure SQL or SQL Server 2025.

## Folders

- `src/extract` – TED API download (`ted_probe.py` and `fill_by_type.py` were the first data checks)
- `src/transform` – JSON to CSV
- `src/load` – CSV to Azure SQL
- `sql/01_staging` – landing tables, same columns as the CSVs
- `sql/02_core` – clean tables and the `clean_name` function
- `sql/03_load` – fill the core tables from staging
- `seeds` – CPV codes in scope
- `docs` – field map

## Limits

- Only above-threshold tenders published on TED.
- Awarded value is not revenue.
- No personal contact data is stored.
