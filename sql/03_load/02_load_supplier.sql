WITH cleaned AS (
    SELECT dbo.clean_name(winner_name) AS clean_key, winner_name
    FROM stg_lot
),
k AS (
    SELECT COALESCE(a.official_key, c.clean_key) AS supplier_key, c.winner_name
    FROM cleaned c
    LEFT JOIN name_alias a
        ON a.entity = 'supplier'
       AND a.variant_key = c.clean_key
)
INSERT INTO supplier (supplier_key, supplier_name)
SELECT k.supplier_key, MIN(k.winner_name)
FROM k
WHERE k.supplier_key IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM supplier s WHERE s.supplier_key = k.supplier_key)
GROUP BY k.supplier_key;