# Field map (TED Search API v3 -> our model)

Source: probe runs on 2026-10-21, 148 Spanish notices, last 90 days
(`data/sample/probe_report.md`, `data/sample/fill_by_type.md`).

Status: **V** checked with real data · **A** assumption, still to confirm · **X** not used

## Notice types

| form-type | What it is | Used for |
|---|---|---|
| competition | Open tender: buyers ask for offers | Open lots, deadline, estimated value, duration |
| result | Award: who won and for how much | Winner, awarded value, tenders received |
| cont-modif | Change to a signed contract | Stored only (left out of awarded value to avoid double counting) |
| planning | Early notice of a future purchase | Stored only (no procedure id) |

## Fields

| Question | Our column | TED field | Notice type | Fill | Status | Notes |
|---|---|---|---|---|---|---|
| Key | notice_id | publication-number | all | 100% | V | |
| Key | procedure_id | procedure-identifier | all except planning | 100% | V | Links competition and result notices of the same tender |
| Key | lot_id | identifier-lot | all | 100% (planning 73%) | V | |
| All | form_type | form-type | all | 100% | V | |
| All | notice_type | notice-type | all | 100% | V | |
| All | publication_date | publication-date | all | 100% | V | |
| All | cpv_code | classification-cpv | all | 100% | V | Parent code search includes children |
| All | title | notice-title | all | 100% | V | |
| Q1 Open lots | deadline | deadline-receipt-tender-date-lot | competition | 98% | V | |
| Q1, Q4 | estimated_value_lot | estimated-value-lot | competition | 45% | V | |
| Q1, Q4 | estimated_value_proc | estimated-value-proc | competition | 73% | A | Fallback when lot value is missing; only safe for single-lot tenders |
| Q2 Buyers | buyer_name | buyer-name | all | 100% | V | Organisation only, no staff contact data |
| Q2 Buyers | buyer_city | buyer-city | all | 100% | V | Region comes from a seed table |
| Q3 Supplier share | supplier_name | winner-name | result | 96% | V | Cleaned with an alias table in step 3 |
| Q3, Q4 | awarded_value | tender-value | result | 94% | A | Looks like the award amount; confirm currency and VAT (O10) |
| Q3, Q4 | awarded_currency | tender-value-cur | result | 94% | V | |
| Q4 Competition | tenders_received | received-submissions-type-val | result | 100% | V | |
| Q5 Re-tenders | duration_value | duration-period-value-lot | competition | 89% | V | Taken from the competition notice of the same procedure |
| Q5 Re-tenders | duration_unit | duration-period-unit-lot | competition | 89% | V | |
| - | - | result-value-lot | result | 11% | X | Too sparse; tender-value used instead |
| - | - | organisation-name-tenderer | result | 96% | X | All bidders, not only winners |