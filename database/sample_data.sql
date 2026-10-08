-- ============================================
-- VeerSeva - Defence Welfare Management System
-- Phase 2 Database Schema
-- ============================================

CREATE DATABASE IF NOT EXISTS veerseva;

USE veerseva;


-- ============================================
-- 1. USERS TABLE
-- ============================================

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    user_type VARCHAR(30) DEFAULT 'BENEFICIARY',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 2. WELFARE SCHEMES TABLE
-- ============================================

CREATE TABLE schemes (
    scheme_id INT PRIMARY KEY AUTO_INCREMENT,
    scheme_name VARCHAR(150) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    benefit VARCHAR(255),
    required_documents TEXT,
    deadline DATE,
    status VARCHAR(30) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================
-- 3. ELIGIBILITY RULES TABLE
-- ============================================

CREATE TABLE eligibility_rules (
    rule_id INT PRIMARY KEY AUTO_INCREMENT,
    scheme_id INT NOT NULL,
    min_age INT,
    max_age INT,
    service_category VARCHAR(100),
    income_limit DECIMAL(12,2),
    description TEXT,

    FOREIGN KEY (scheme_id)
        REFERENCES schemes(scheme_id)
        ON DELETE CASCADE
);


-- ============================================
-- 4. APPLICATIONS TABLE
-- ============================================

CREATE TABLE applications (
    application_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    scheme_id INT NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_status VARCHAR(30) DEFAULT 'SUBMITTED',

    FOREIGN KEY (user_id)
        REFERENCES users(user_id),

    FOREIGN KEY (scheme_id)
        REFERENCES schemes(scheme_id)
);


-- ============================================
-- 5. DOCUMENTS TABLE
-- ============================================

CREATE TABLE documents (
    document_id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    document_name VARCHAR(150) NOT NULL,
    document_type VARCHAR(50),
    document_path VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id)
        REFERENCES applications(application_id)
        ON DELETE CASCADE
);


-- ============================================
-- 6. APPLICATION STATUS HISTORY
-- ============================================

CREATE TABLE application_status (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    status VARCHAR(30) NOT NULL,
    remarks VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (application_id)
        REFERENCES applications(application_id)
        ON DELETE CASCADE
);


-- ============================================
-- 7. NOTIFICATIONS TABLE
-- ============================================

CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- ============================================
-- 8. AUDIT LOGS TABLE
-- ============================================

CREATE TABLE audit_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INT,
    action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);