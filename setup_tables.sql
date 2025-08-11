-- Account Task Management System - Database Setup
-- This script creates the necessary tables and objects for the Streamlit application
-- Run this script in your Snowflake environment before deploying the application

-- Create database and schema (adjust names as needed for your environment)
CREATE DATABASE IF NOT EXISTS ACCOUNT_TASK_MGMT;
USE DATABASE ACCOUNT_TASK_MGMT;

CREATE SCHEMA IF NOT EXISTS TASK_MANAGEMENT;
USE SCHEMA TASK_MANAGEMENT;

-- Create sequence for generating unique IDs
CREATE SEQUENCE IF NOT EXISTS SEQ_TASK_ID
    START = 1
    INCREMENT = 1
    COMMENT = 'Sequence for generating unique task IDs';

-- =====================================================
-- ACCOUNTS TABLE
-- =====================================================
CREATE OR REPLACE TABLE TBL_ACCOUNTS (
    ACCOUNT_ID VARCHAR(50) PRIMARY KEY,
    ACCOUNT_NAME VARCHAR(200) NOT NULL,
    ACCOUNT_STAGE VARCHAR(50) NOT NULL,
    ACCOUNT_PHASE VARCHAR(50) NOT NULL,
    TECH_STACK ARRAY,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    UPDATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
)
COMMENT = 'Master table for managing client accounts with their stages, phases, and technology stacks';

-- =====================================================
-- TASKS TABLE
-- =====================================================
CREATE OR REPLACE TABLE TBL_TASKS (
    TASK_ID VARCHAR(50) PRIMARY KEY,
    ACCOUNT_ID VARCHAR(50) NOT NULL,
    TASK_TITLE VARCHAR(500) NOT NULL,
    TASK_DESCRIPTION TEXT,
    ESTIMATED_HOURS NUMBER(10,2) NOT NULL DEFAULT 1,
    DEADLINE_DATE DATE NOT NULL,
    TASK_STATUS VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    PRIORITY_SCORE NUMBER(10,2),
    PRIORITY_LABEL VARCHAR(20),
    ACTUAL_HOURS NUMBER(10,2),
    COMPLETION_DATE TIMESTAMP_NTZ,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CREATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    UPDATED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    IS_ACTIVE BOOLEAN DEFAULT TRUE,
    
    -- Foreign key constraint
    CONSTRAINT FK_TASKS_ACCOUNT FOREIGN KEY (ACCOUNT_ID) REFERENCES TBL_ACCOUNTS(ACCOUNT_ID)
)
COMMENT = 'Main table for managing tasks associated with accounts, including priority calculation and tracking';

-- =====================================================
-- TASK HISTORY TABLE (for audit trail)
-- =====================================================
CREATE OR REPLACE TABLE TBL_TASK_HISTORY (
    HISTORY_ID VARCHAR(50) PRIMARY KEY DEFAULT UUID_STRING(),
    TASK_ID VARCHAR(50) NOT NULL,
    CHANGE_TYPE VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    OLD_VALUES VARIANT,
    NEW_VALUES VARIANT,
    CHANGED_BY VARCHAR(100) DEFAULT CURRENT_USER(),
    CHANGED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    
    CONSTRAINT FK_TASK_HISTORY FOREIGN KEY (TASK_ID) REFERENCES TBL_TASKS(TASK_ID)
)
COMMENT = 'Audit trail table to track all changes made to tasks';

-- =====================================================
-- LOOKUP TABLES
-- =====================================================

-- Account Stages Lookup
CREATE OR REPLACE TABLE LKP_ACCOUNT_STAGES (
    STAGE_CODE VARCHAR(20) PRIMARY KEY,
    STAGE_NAME VARCHAR(100) NOT NULL,
    STAGE_DESCRIPTION VARCHAR(500),
    SORT_ORDER NUMBER(3),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
)
COMMENT = 'Lookup table for valid account stages';

-- Account Phases Lookup  
CREATE OR REPLACE TABLE LKP_ACCOUNT_PHASES (
    PHASE_CODE VARCHAR(20) PRIMARY KEY,
    PHASE_NAME VARCHAR(100) NOT NULL,
    PHASE_DESCRIPTION VARCHAR(500),
    SORT_ORDER NUMBER(3),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
)
COMMENT = 'Lookup table for valid account phases';

-- Technology Stack Lookup
CREATE OR REPLACE TABLE LKP_TECH_STACK (
    TECH_CODE VARCHAR(50) PRIMARY KEY,
    TECH_NAME VARCHAR(100) NOT NULL,
    TECH_CATEGORY VARCHAR(50), -- Frontend, Backend, Database, Cloud, etc.
    TECH_DESCRIPTION VARCHAR(500),
    IS_ACTIVE BOOLEAN DEFAULT TRUE
)
COMMENT = 'Lookup table for available technology stack options';

-- =====================================================
-- INSERT REFERENCE DATA
-- =====================================================

-- Insert Account Stages
INSERT INTO LKP_ACCOUNT_STAGES (STAGE_CODE, STAGE_NAME, STAGE_DESCRIPTION, SORT_ORDER) VALUES
('LEAD', 'Lead', 'Initial contact or inquiry from potential client', 1),
('PROSPECT', 'Prospect', 'Qualified lead with identified opportunity', 2),
('CUSTOMER', 'Customer', 'Active paying client with ongoing relationship', 3),
('PARTNER', 'Partner', 'Strategic partnership or alliance', 4);

-- Insert Account Phases
INSERT INTO LKP_ACCOUNT_PHASES (PHASE_CODE, PHASE_NAME, PHASE_DESCRIPTION, SORT_ORDER) VALUES
('DISCOVERY', 'Discovery', 'Initial discovery and needs assessment phase', 1),
('QUALIFICATION', 'Qualification', 'Qualifying opportunity and solution fit', 2),
('JOURNEY', 'Journey', 'Active engagement and solution development', 3),
('IMPLEMENTATION', 'Implementation', 'Solution implementation and deployment', 4),
('SUPPORT', 'Support', 'Ongoing support and maintenance phase', 5);

-- Insert Technology Stack Options
INSERT INTO LKP_TECH_STACK (TECH_CODE, TECH_NAME, TECH_CATEGORY) VALUES
('PYTHON', 'Python', 'Backend'),
('STREAMLIT', 'Streamlit', 'Frontend'),
('REACT', 'React', 'Frontend'),
('NODEJS', 'Node.js', 'Backend'),
('REDIS', 'Redis', 'Database'),
('DOCKER', 'Docker', 'DevOps'),
('POSTGRESQL', 'PostgreSQL', 'Database'),
('MONGODB', 'MongoDB', 'Database'),
('AWS', 'Amazon Web Services', 'Cloud'),
('AZURE', 'Microsoft Azure', 'Cloud'),
('SNOWFLAKE', 'Snowflake', 'Data Platform'),
('JAVASCRIPT', 'JavaScript', 'Frontend'),
('TYPESCRIPT', 'TypeScript', 'Frontend'),
('FASTAPI', 'FastAPI', 'Backend'),
('DJANGO', 'Django', 'Backend');

-- Insert Sample Accounts
INSERT INTO TBL_ACCOUNTS (ACCOUNT_ID, ACCOUNT_NAME, ACCOUNT_STAGE, ACCOUNT_PHASE, TECH_STACK) 
SELECT 'VID4A', 'VID4A', 'CUSTOMER', 'JOURNEY', ARRAY_CONSTRUCT('PYTHON', 'STREAMLIT')
UNION ALL
SELECT 'REDIS', 'REDIS', 'PROSPECT', 'DISCOVERY', ARRAY_CONSTRUCT('REDIS', 'DOCKER')
UNION ALL
SELECT 'FINONEX', 'FINONEX', 'LEAD', 'QUALIFICATION', ARRAY_CONSTRUCT('REACT', 'NODEJS');

-- Insert Sample Tasks
INSERT INTO TBL_TASKS (TASK_ID, ACCOUNT_ID, TASK_TITLE, TASK_DESCRIPTION, ESTIMATED_HOURS, DEADLINE_DATE, TASK_STATUS)
SELECT UUID_STRING(), 'VID4A', 'Customer check-in task', 'Need to check-in with customer, not scheduled', 2, CURRENT_DATE() + 7, 'PENDING'
UNION ALL
SELECT UUID_STRING(), 'REDIS', 'Project implementation', 'Project in 2 months, scheduled', 80, CURRENT_DATE() + 60, 'IN_PROGRESS'
UNION ALL
SELECT UUID_STRING(), 'FINONEX', 'Initial discovery call', 'Schedule and conduct initial discovery session', 4, CURRENT_DATE() + 3, 'PENDING';

-- =====================================================
-- VIEWS FOR APPLICATION
-- =====================================================

-- View for Tasks with Account Information
CREATE OR REPLACE VIEW VW_TASKS_WITH_ACCOUNTS AS
SELECT 
    t.TASK_ID,
    t.ACCOUNT_ID,
    a.ACCOUNT_NAME,
    a.ACCOUNT_STAGE,
    a.ACCOUNT_PHASE,
    a.TECH_STACK,
    t.TASK_TITLE,
    t.TASK_DESCRIPTION,
    t.ESTIMATED_HOURS,
    t.DEADLINE_DATE,
    t.TASK_STATUS,
    t.PRIORITY_SCORE,
    t.PRIORITY_LABEL,
    t.ACTUAL_HOURS,
    t.COMPLETION_DATE,
    t.CREATED_AT,
    t.UPDATED_AT,
    DATEDIFF('day', CURRENT_DATE(), t.DEADLINE_DATE) AS DAYS_UNTIL_DEADLINE,
    CASE 
        WHEN t.DEADLINE_DATE < CURRENT_DATE() THEN 'OVERDUE'
        WHEN DATEDIFF('day', CURRENT_DATE(), t.DEADLINE_DATE) <= 3 THEN 'URGENT'
        WHEN DATEDIFF('day', CURRENT_DATE(), t.DEADLINE_DATE) <= 7 THEN 'HIGH'
        WHEN DATEDIFF('day', CURRENT_DATE(), t.DEADLINE_DATE) <= 30 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS URGENCY_CATEGORY
FROM TBL_TASKS t
INNER JOIN TBL_ACCOUNTS a ON t.ACCOUNT_ID = a.ACCOUNT_ID
WHERE t.IS_ACTIVE = TRUE AND a.IS_ACTIVE = TRUE;

-- View for Dashboard Statistics
CREATE OR REPLACE VIEW VW_DASHBOARD_STATS AS
SELECT 
    COUNT(DISTINCT a.ACCOUNT_ID) AS TOTAL_ACCOUNTS,
    COUNT(DISTINCT CASE WHEN a.ACCOUNT_STAGE = 'CUSTOMER' THEN a.ACCOUNT_ID END) AS ACTIVE_CUSTOMERS,
    COUNT(t.TASK_ID) AS TOTAL_TASKS,
    COUNT(CASE WHEN t.TASK_STATUS = 'PENDING' THEN 1 END) AS PENDING_TASKS,
    COUNT(CASE WHEN t.TASK_STATUS = 'IN_PROGRESS' THEN 1 END) AS IN_PROGRESS_TASKS,
    COUNT(CASE WHEN t.TASK_STATUS = 'COMPLETED' THEN 1 END) AS COMPLETED_TASKS,
    COUNT(CASE WHEN t.DEADLINE_DATE < CURRENT_DATE() AND t.TASK_STATUS NOT IN ('COMPLETED', 'CANCELLED') THEN 1 END) AS OVERDUE_TASKS,
    AVG(t.ESTIMATED_HOURS) AS AVG_TASK_HOURS,
    SUM(CASE WHEN t.TASK_STATUS = 'PENDING' THEN t.ESTIMATED_HOURS ELSE 0 END) AS PENDING_HOURS,
    SUM(CASE WHEN t.TASK_STATUS = 'IN_PROGRESS' THEN t.ESTIMATED_HOURS ELSE 0 END) AS IN_PROGRESS_HOURS
FROM TBL_ACCOUNTS a
LEFT JOIN TBL_TASKS t ON a.ACCOUNT_ID = t.ACCOUNT_ID AND t.IS_ACTIVE = TRUE
WHERE a.IS_ACTIVE = TRUE;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

-- Procedure to calculate and update task priorities
CREATE OR REPLACE PROCEDURE SP_UPDATE_TASK_PRIORITIES()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    UPDATE TBL_TASKS 
    SET 
        PRIORITY_SCORE = CASE 
            WHEN DEADLINE_DATE < CURRENT_DATE() THEN 1000 + ESTIMATED_HOURS
            WHEN DATEDIFF('day', CURRENT_DATE(), DEADLINE_DATE) <= 3 THEN 900 - ESTIMATED_HOURS
            WHEN DATEDIFF('day', CURRENT_DATE(), DEADLINE_DATE) <= 7 THEN 800 - ESTIMATED_HOURS
            WHEN DATEDIFF('day', CURRENT_DATE(), DEADLINE_DATE) <= 30 THEN 600 - ESTIMATED_HOURS
            ELSE 400 - ESTIMATED_HOURS
        END,
        PRIORITY_LABEL = CASE 
            WHEN DEADLINE_DATE < CURRENT_DATE() THEN 'CRITICAL'
            WHEN DATEDIFF('day', CURRENT_DATE(), DEADLINE_DATE) <= 3 THEN 'URGENT'
            WHEN DATEDIFF('day', CURRENT_DATE(), DEADLINE_DATE) <= 7 THEN 'HIGH'
            WHEN DATEDIFF('day', CURRENT_DATE(), DEADLINE_DATE) <= 30 THEN 'MEDIUM'
            ELSE 'LOW'
        END,
        UPDATED_AT = CURRENT_TIMESTAMP()
    WHERE IS_ACTIVE = TRUE;
    
    RETURN 'Task priorities updated successfully';
END;
$$;

-- =====================================================
-- GRANTS (adjust as needed for your security model)
-- =====================================================

-- Grant usage on database and schema
GRANT USAGE ON DATABASE ACCOUNT_TASK_MGMT TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA TASK_MANAGEMENT TO ROLE SYSADMIN;

-- Grant permissions on tables
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA TASK_MANAGEMENT TO ROLE SYSADMIN;
GRANT SELECT ON ALL VIEWS IN SCHEMA TASK_MANAGEMENT TO ROLE SYSADMIN;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA TASK_MANAGEMENT TO ROLE SYSADMIN;

-- Grant execute on stored procedures
GRANT USAGE ON PROCEDURE SP_UPDATE_TASK_PRIORITIES() TO ROLE SYSADMIN;

-- =====================================================
-- INITIAL SETUP COMPLETE
-- =====================================================

-- Call the priority update procedure to set initial priorities
CALL SP_UPDATE_TASK_PRIORITIES();

-- Verify setup
SELECT 'Setup completed successfully. Tables created:' AS MESSAGE;
SHOW TABLES IN SCHEMA TASK_MANAGEMENT;

SELECT 'Sample data verification:' AS MESSAGE;
SELECT COUNT(*) AS ACCOUNT_COUNT FROM TBL_ACCOUNTS;
SELECT COUNT(*) AS TASK_COUNT FROM TBL_TASKS;
SELECT COUNT(*) AS LOOKUP_STAGES FROM LKP_ACCOUNT_STAGES;
SELECT COUNT(*) AS LOOKUP_PHASES FROM LKP_ACCOUNT_PHASES;
SELECT COUNT(*) AS LOOKUP_TECH FROM LKP_TECH_STACK;