USE veerseva;

DELIMITER //

CREATE PROCEDURE LogAuditAction(
    IN p_user_id INT,
    IN p_action VARCHAR(100),
    IN p_table_name VARCHAR(100),
    IN p_record_id INT
)
BEGIN
    INSERT INTO audit_logs (
        user_id,
        action,
        table_name,
        record_id,
        action_time
    )
    VALUES (
        p_user_id,
        p_action,
        p_table_name,
        p_record_id,
        CURRENT_TIMESTAMP
    );
END //

DELIMITER ;
