INSERT INTO buyer (buyer_name, buyer_city)
SELECT MIN(s.buyer_name), MAX(s.buyer_city)
FROM stg_notice s
WHERE s.buyer_name IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM buyer b
      WHERE b.buyer_name = s.buyer_name
  )
GROUP BY s.buyer_name;
