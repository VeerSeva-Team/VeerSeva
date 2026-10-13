USE veerseva;

DELIMITER //

CREATE PROCEDURE CheckEligibility(
    IN p_scheme_id INT,
    IN p_age INT,
    IN p_income DECIMAL(12,2),
    IN p_service_category VARCHAR(100)
)
BEGIN
    SELECT
        s.scheme_id,
        s.scheme_name,
        CASE
            WHEN (er.min_age IS NULL OR p_age >= er.min_age)
             AND (er.max_age IS NULL OR p_age <= er.max_age)
             AND (er.income_limit IS NULL OR p_income <= er.income_limit)
             AND (er.service_category IS NULL
                  OR er.service_category = p_service_category)
            THEN 'ELIGIBLE'
            ELSE 'NOT ELIGIBLE'
        END AS eligibility_status
    FROM schemes s
    JOIN eligibility_rules er
        ON s.scheme_id = er.scheme_id
    WHERE s.scheme_id = p_scheme_id
      AND s.status = 'ACTIVE';
END //

DELIMITER ;
