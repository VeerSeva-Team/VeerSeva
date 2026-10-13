USE veerseva;

-- Trigger 1: Record the initial status when an application is created
DELIMITER //

CREATE TRIGGER after_application_insert_status
AFTER INSERT ON applications
FOR EACH ROW
BEGIN
    INSERT INTO application_status (
        application_id,
        status,
        remarks
    )
    VALUES (
        NEW.application_id,
        NEW.current_status,
        'Initial application status'
    );
END //

-- Trigger 2: Record status changes in the history table
CREATE TRIGGER after_application_status_update
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    IF NOT (OLD.current_status <=> NEW.current_status) THEN
        INSERT INTO application_status (
            application_id,
            status,
            remarks
        )
        VALUES (
            NEW.application_id,
            NEW.current_status,
            CONCAT(
                'Status changed from ',
                COALESCE(OLD.current_status, 'NULL'),
                ' to ',
                COALESCE(NEW.current_status, 'NULL')
            )
        );
    END IF;
END //

DELIMITER ;
