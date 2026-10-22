WITH cleaned AS (
    SELECT n.*, dbo.clean_name(n.buyer_name) AS clean_key
    FROM stg_notice n
),
k AS (
    SELECT c.*, COALESCE(a.official_key, c.clean_key) AS buyer_key
    FROM cleaned c
    LEFT JOIN name_alias a
        ON a.entity = 'buyer'
       AND a.variant_key = c.clean_key
)
INSERT INTO notice (publication_number, procedure_id, notice_type, form_type,
                    publication_date, buyer_id, buyer_city, title,
                    estimated_value_proc, notice_url)
SELECT k.publication_number, k.procedure_id, k.notice_type, k.form_type,
       k.publication_date, b.buyer_id, k.buyer_city, k.title,
       k.estimated_value_proc, k.notice_url
FROM k
JOIN buyer b ON b.buyer_key = k.buyer_key
WHERE NOT EXISTS (SELECT 1 FROM notice x WHERE x.publication_number = k.publication_number);