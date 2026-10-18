USE veerseva;

-- View documents submitted for each application
SELECT
    a.application_id,
    u.full_name AS beneficiary_name,
    s.scheme_name,
    d.document_name,
    d.document_type,
    d.uploaded_at
FROM applications a
JOIN users u
    ON a.user_id = u.user_id
JOIN schemes s
    ON a.scheme_id = s.scheme_id
LEFT JOIN documents d
    ON a.application_id = d.application_id
ORDER BY a.application_id, d.uploaded_at;
SELECT
    a.application_id,
    u.full_name AS beneficiary_name,
    s.scheme_name,
    a.current_status
FROM applications a
JOIN users u
    ON a.user_id = u.user_id
JOIN schemes s
    ON a.scheme_id = s.scheme_id
LEFT JOIN documents d
    ON a.application_id = d.application_id
WHERE d.document_id IS NULL;
