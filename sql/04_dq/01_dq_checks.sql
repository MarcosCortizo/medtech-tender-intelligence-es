INSERT INTO dq_check_result (check_name, bad_rows)
SELECT 'notices lost between staging and core', COUNT(*)
FROM stg_notice s
WHERE NOT EXISTS (SELECT 1 FROM notice n WHERE n.publication_number = s.publication_number)
UNION ALL
SELECT 'lots lost between staging and core', COUNT(*)
FROM stg_lot s
WHERE NOT EXISTS (SELECT 1 FROM lot l WHERE l.publication_number = s.publication_number AND l.lot_id = s.lot_id)
UNION ALL
SELECT 'deadline before publication', COUNT(*)
FROM v_lot_latest v
JOIN notice n ON n.publication_number = v.competition_notice
WHERE v.deadline_date < n.publication_date
UNION ALL
SELECT 'award outside 0.3-1.5 x estimate', COUNT(*)
FROM v_lot_latest
WHERE awarded_value IS NOT NULL AND estimated_value > 0
  AND (awarded_value / estimated_value < 0.3 OR awarded_value / estimated_value > 1.5);
