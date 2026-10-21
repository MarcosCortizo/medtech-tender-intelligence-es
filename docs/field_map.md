# Field map (TED Search API v3 -> our model)

Fill this in after running `src/extract/ted_probe.py`. Copy status and fill rate from `data/sample/probe_report.md`.
Status: **V** valid and filled · **W** workaround written · **X** not available (KPI documented as not computable)

| Business question | Our column | TED field | Status | Fill rate | Notes / workaround |
|---|---|---|---|---|---|
| Key | notice_id | publication-number | | | |
| Key | procedure_id | procedure-identifier | | | |
| Key | lot_id | identifier-lot | | | |
| Q1 Open lots | notice_type | notice-type / form-type | | | competition vs result |
| Q1 Open lots | deadline | deadline-receipt-tender-date-lot | | | |
| Q1 Open lots | estimated_value | estimated-value-lot | | | currency? VAT? (O10) |
| Q2 Buyers | buyer_name | buyer-name | | | |
| Q2 Buyers | buyer_city | buyer-city | | | region via seed |
| Q3 Supplier share | supplier_name | winner-name | | | alias map in step 3 |
| Q3/Q4 Awards | awarded_value | tender-value / result-value-lot | | | lot or procedure level? |
| Q4 Competition | tenders_received | received-submissions-type-val | | | |
| Q5 Re-tenders | duration | duration-period-value-lot + unit | | | O2 |
| All | cpv | classification-cpv | | | |
| All | publication_date | publication-date | | | |
