CREATE OR ALTER VIEW v_lot_latest AS
WITH ranked AS (
    SELECT n.procedure_id, l.lot_id, n.form_type, n.publication_number, n.buyer_id,
           l.estimated_value, l.deadline_date, l.duration_value, l.duration_unit,
           l.supplier_id, l.tender_value, l.tenders_received, l.contract_date,
           ROW_NUMBER() OVER (
               PARTITION BY n.procedure_id, l.lot_id, n.form_type
               ORDER BY n.publication_date DESC, n.publication_number DESC
           ) AS rn
    FROM lot l
    JOIN notice n ON n.publication_number = l.publication_number
    WHERE n.procedure_id IS NOT NULL
      AND n.form_type IN ('competition', 'result')
)
SELECT procedure_id,
       lot_id,
       MAX(buyer_id) AS buyer_id,
       MAX(CASE WHEN form_type = 'competition' THEN publication_number END) AS competition_notice,
       MAX(CASE WHEN form_type = 'result' THEN publication_number END) AS result_notice,
       CASE
           WHEN MAX(CASE WHEN form_type = 'result' THEN 1 END) = 1 THEN 'result'
           WHEN MAX(deadline_date) >= CAST(GETDATE() AS DATE) THEN 'open'
           ELSE 'closed, no result yet'
       END AS status,
       COALESCE(MAX(CASE WHEN form_type = 'competition' THEN estimated_value END),
                MAX(CASE WHEN form_type = 'result' THEN estimated_value END)) AS estimated_value,
       MAX(CASE WHEN form_type = 'competition' THEN deadline_date END) AS deadline_date,
       MAX(CASE WHEN form_type = 'competition' THEN duration_value END) AS duration_value,
       MAX(CASE WHEN form_type = 'competition' THEN duration_unit END) AS duration_unit,
       MAX(CASE WHEN form_type = 'result' THEN supplier_id END) AS supplier_id,
       MAX(CASE WHEN form_type = 'result' THEN tender_value END) AS awarded_value,
       MAX(CASE WHEN form_type = 'result' THEN tenders_received END) AS tenders_received,
       MAX(CASE WHEN form_type = 'result' THEN contract_date END) AS contract_date
FROM ranked
WHERE rn = 1
GROUP BY procedure_id, lot_id;