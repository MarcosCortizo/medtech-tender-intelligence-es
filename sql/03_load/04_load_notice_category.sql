INSERT INTO notice_category (publication_number, category)
SELECT DISTINCT n.publication_number, k.category
FROM stg_notice n
CROSS APPLY STRING_SPLIT(n.cpv_codes, ',') s
JOIN cpv_category k
    ON TRIM(s.value) LIKE TRIM(TRAILING '0' FROM k.cpv_code) + '%'
WHERE NOT EXISTS (
    SELECT 1 FROM notice_category x
    WHERE x.publication_number = n.publication_number
      AND x.category = k.category
);