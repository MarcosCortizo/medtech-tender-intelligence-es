# Medtech Public Tender Intelligence (Spain)

Spanish public tenders for medical imaging and radiotherapy equipment, collected from the EU TED API, stored in Azure SQL and shown in Power BI for a medtech sales / tender team.

```
TED API -> raw JSON -> CSV -> Azure SQL (staging -> core) -> Power BI
```

**Status:** step 3, building the core model in SQL. Staging has Oct 2024 to Oct 2026 (524 notices, 1,429 lots).

## How to run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Azure SQL details. Run `sql/01_staging/01_create_staging.sql` once. Then, for a date window:

```powershell
python src/extract/extract.py 2026-09-01 2026-09-30
python src/transform/flatten.py data/raw/ted_2026-09-01_2026-09-30.json
python src/load/load_staging.py ted_2026-09-01_2026-09-30
```

Running the same window twice adds no duplicates.

## Folders

- `src/extract` – TED API download (`ted_probe.py` and `fill_by_type.py` were the first data checks)
- `src/transform` – JSON to CSV
- `src/load` – CSV to Azure SQL
- `sql` – table scripts
- `seeds` – CPV codes in scope
- `docs` – field map

## Limits

- Only above-threshold tenders published on TED.
- Awarded value is not revenue.
- No personal contact data is stored.
