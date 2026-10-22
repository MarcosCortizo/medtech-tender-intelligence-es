WITH cleaned AS (
    SELECT dbo.clean_name(buyer_name) AS clean_key, buyer_name, buyer_city
    FROM stg_notice
),
k AS (
    SELECT COALESCE(a.official_key, c.clean_key) AS buyer_key, c.buyer_name, c.buyer_city
    FROM cleaned c
    LEFT JOIN name_alias a
        ON a.entity = 'buyer'
       AND a.variant_key = c.clean_key
)
INSERT INTO buyer (buyer_key, buyer_name, buyer_city)
SELECT k.buyer_key, MIN(k.buyer_name), MAX(k.buyer_city)
FROM k
WHERE k.buyer_key IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM buyer b WHERE b.buyer_key = k.buyer_key)
GROUP BY k.buyer_key;
