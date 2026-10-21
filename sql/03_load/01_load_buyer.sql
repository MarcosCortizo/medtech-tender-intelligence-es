INSERT INTO buyer (buyer_key, buyer_name, buyer_city)
SELECT k.buyer_key, MIN(k.buyer_name), MAX(k.buyer_city)
FROM (
    SELECT dbo.clean_name(buyer_name) AS buyer_key, buyer_name, buyer_city
    FROM stg_notice
) AS k
WHERE k.buyer_key IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM buyer b
      WHERE b.buyer_key = k.buyer_key
  )
GROUP BY k.buyer_key;
