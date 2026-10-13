USE veerseva;

CREATE INDEX idx_applications_user
ON applications(user_id);

CREATE INDEX idx_applications_scheme
ON applications(scheme_id);

CREATE INDEX idx_applications_status
ON applications(current_status);

CREATE INDEX idx_documents_application
ON documents(application_id);

CREATE INDEX idx_notifications_user_read
ON notifications(user_id, is_read);
