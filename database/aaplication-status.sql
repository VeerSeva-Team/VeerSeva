-- =============================================================================
-- VeerSeva - Defence Welfare Management System
-- Phase-III: Application Status Tracking, Constraints & State Transitions
-- Course: OS(PCS-502) & DBMS(PCS-503) | Team 210
-- =============================================================================

USE veerseva;

-- Ensure application status log table has proper indexes and cascade foreign keys
DROP TABLE IF EXISTS application_status_history;

CREATE TABLE IF NOT EXISTS application_status_history (
    history_id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    action_by VARCHAR(100) DEFAULT 'SYSTEM_SCHEDULER',
    remarks TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id)
        REFERENCES applications(application_id)
        ON DELETE CASCADE
);

-- Trigger: Automatically records application status transitions and logs to audit_logs
DELIMITER //

DROP TRIGGER IF EXISTS trg_after_application_status_update //

CREATE TRIGGER trg_after_application_status_update
AFTER UPDATE ON applications
FOR EACH ROW
BEGIN
    IF OLD.current_status <> NEW.current_status THEN
        -- Insert transition record into history
        INSERT INTO application_status_history (
            application_id,
            old_status,
            new_status,
            action_by,
            remarks
        ) VALUES (
            NEW.application_id,
            OLD.current_status,
            NEW.current_status,
            'OFFICER_REVIEW_PROCESS',
            CONCAT('Status updated from ', OLD.current_status, ' to ', NEW.current_status)
        );

        -- Also record in central audit_logs table (OSDBMS ACID Compliance)
        INSERT INTO audit_logs (
            user_id,
            action,
            table_name,
            record_id,
            action_time
        ) VALUES (
            NEW.user_id,
            CONCAT('STATUS_CHANGE_', NEW.current_status),
            'applications',
            NEW.application_id,
            CURRENT_TIMESTAMP
        );
    END IF;
END //

-- Stored Procedure: Update application state with validation
DROP PROCEDURE IF EXISTS AdvanceApplicationStatus //

CREATE PROCEDURE AdvanceApplicationStatus(
    IN p_application_id INT,
    IN p_new_status VARCHAR(30),
    IN p_remarks VARCHAR(255)
)
BEGIN
    DECLARE v_valid_status INT DEFAULT 0;
    
    -- Check if target status is in approved state lifecycle
    IF p_new_status IN ('SUBMITTED', 'DOC_VERIFIED', 'ELIGIBILITY_CHECK', 'APPROVED', 'DISBURSED', 'REJECTED') THEN
        SET v_valid_status = 1;
    END IF;

    IF v_valid_status = 1 THEN
        UPDATE applications 
        SET current_status = p_new_status 
        WHERE application_id = p_application_id;
        
        INSERT INTO application_status (application_id, status, remarks, updated_at)
        VALUES (p_application_id, p_new_status, p_remarks, CURRENT_TIMESTAMP);
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid Application Status transition provided.';
    END IF;
END //

DELIMITER ;
