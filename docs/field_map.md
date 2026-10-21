# Field map (TED API -> our tables)

Based on the step 1 checks on 2026-10-21: 148 Spanish notices from the last 90 days (`data/sample/probe_report.md`, `data/sample/fill_by_type.md`).

Status: **V** checked with real data, **A** assumption, **X** not used.

## Notice types

| form-type | What it is | Used for |
|---|---|---|
| competition | Open tender: buyers ask for offers | Open lots, deadline, estimated value, duration |
| result | Award: who won and for how much | Winner, awarded value, tenders received |
| cont-modif | Change to a signed contract | Stored only (left out of awarded value to avoid double counting) |
| planning | Early notice of a future purchase | Stored only (no procedure id) |

## stg_notice

| Column | TED field | Fill | Status | Notes |
|---|---|---|---|---|
| publication_number | publication-number | 100% | V | Key |
| notice_id | notice-identifier | 100% | V | |
| procedure_id | procedure-identifier | 100% (planning 0%) | V | Links competition and result notices of the same tender |
| notice_type | notice-type | 100% | V | |
| form_type | form-type | 100% | V | |
| publication_date | publication-date | 100% | V | |
| dispatch_date | dispatch-date | 100% | V | |
| buyer_name | buyer-name | 100% | V | Organisation only, no staff contact data |
| buyer_city | buyer-city | Most notices, some empty (e.g. Hospital Clínic) | V | Region comes from a seed table |
| title | notice-title | 100% | V | Spanish text, prefix removed |
| cpv_codes | classification-cpv | 100% | V | All codes, comma separated. Parent code search includes children |
| estimated_value_proc | estimated-value-proc | 73% (competition) | A | Fallback when the lot value is missing; only safe for single-lot tenders |
| notice_url | built from publication-number | 100% | V | |

## stg_lot

| Column | TED field | Fill | Status | Notes |
|---|---|---|---|---|
| publication_number + lot_id | publication-number + identifier-lot | 100% (planning 73%) | V | Key |
| estimated_value | estimated-value-lot | 45% (competition) | V | |
| tender_value | tender-value | 94% (result) | V | Awarded value, checked on notice 523461-2026; assumed without VAT |
| currency | tender-value-cur, else estimated-value-cur-lot | 94% (result) | V | |
| winner_name | winner-name | 96% (result) | V | Name variants cleaned with an alias table in step 3 |
| tenders_received | received-submissions-type-val | 100% (result) | V | Only the value where type-code = "tenders" |
| deadline_date | deadline-receipt-tender-date-lot | 98% (competition) | V | |
| duration_value | duration-period-value-lot | 89% (competition) | V | For the re-tender estimate |
| duration_unit | duration-period-unit-lot | 89% (competition) | V | |
| contract_date | contract-conclusion-date | 96% (result) | V | Start date for the re-tender estimate |

## Not used

| TED field | Fill | Why |
|---|---|---|
| result-value-lot | 11% (result) | Too sparse; tender-value used instead |
| organisation-name-tenderer | 96% (result) | All bidders, not only winners |
