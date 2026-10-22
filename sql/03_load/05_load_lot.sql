WITH cleaned AS (
    SELECT l.*, dbo.clean_name(l.winner_name) AS clean_key
    FROM stg_lot l
),
k AS (
    SELECT c.*, COALESCE(a.official_key, c.clean_key) AS supplier_key
    FROM cleaned c
    LEFT JOIN name_alias a
        ON a.entity = 'supplier'
       AND a.variant_key = c.clean_key
)
INSERT INTO lot (publication_number, lot_id, supplier_id, estimated_value,
                 tender_value, currency, tenders_received, deadline_date,
                 duration_value, duration_unit, contract_date)
SELECT k.publication_number, k.lot_id, s.supplier_id, k.estimated_value,
       k.tender_value, k.currency, k.tenders_received, k.deadline_date,
       k.duration_value, k.duration_unit, k.contract_date
FROM k
LEFT JOIN supplier s ON s.supplier_key = k.supplier_key
WHERE NOT EXISTS (
    SELECT 1 FROM lot x
    WHERE x.publication_number = k.publication_number
      AND x.lot_id = k.lot_id
);