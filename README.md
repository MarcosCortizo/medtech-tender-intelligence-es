# Medtech Public Tender Intelligence (Spain)

Automated BI pipeline: EU TED Search API -> raw JSON -> Azure SQL (ELT, lot grain) -> Power BI, for a medtech commercial / tender team.

> Status: **Step 1 – discovery**. Work in progress.

## Scope and limits
- Source: TED (above-threshold EU tenders only). Buyer country: Spain.
- Awarded value is not revenue.
- No personal contact data is stored.

## How to run (step 1)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/extract/ted_probe.py
```
Output: `data/sample/probe_report.md` and `data/sample/ted_probe_sample.json`.
