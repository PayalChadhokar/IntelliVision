-- ============================================================
-- INTELLIVISION
-- Agentic AI-Based Intelligent Investigation Assistant
-- Complete MySQL Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS intellivision_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE intellivision_db;


-- ============================================================
-- 1. POLICE STATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS police_stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,

    station_name VARCHAR(150) NOT NULL,
    district VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    address TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. USERS / POLICE OFFICERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,

    officer_id VARCHAR(50) NOT NULL UNIQUE,
    officer_name VARCHAR(150) NOT NULL,
    officer_rank VARCHAR(100) NOT NULL,

    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    role ENUM(
        'ADMIN',
        'OFFICER'
    ) DEFAULT 'OFFICER',

    station_id INT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (station_id)
        REFERENCES police_stations(station_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);


-- ============================================================
-- 3. LEGAL ACTS
-- ============================================================
-- Stores the Acts from which legal sections can be retrieved.
--
-- Examples:
-- BNS  = Bharatiya Nyaya Sanhita, 2023
-- BNSS = Bharatiya Nagarik Suraksha Sanhita, 2023
-- BSA  = Bharatiya Sakshya Adhiniyam, 2023
--
-- Other special Acts can be added later.
-- ============================================================

CREATE TABLE IF NOT EXISTS legal_acts (
    act_id INT AUTO_INCREMENT PRIMARY KEY,

    act_code VARCHAR(30) NOT NULL UNIQUE,

    act_name VARCHAR(255) NOT NULL,

    short_name VARCHAR(100),

    act_year INT,

    act_category ENUM(
        'OFFENCE',
        'PROCEDURE',
        'EVIDENCE',
        'SPECIAL_LAW',
        'OTHER'
    ) DEFAULT 'OTHER',

    description TEXT,

    source_name VARCHAR(150),

    source_url VARCHAR(500),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- ============================================================
-- 4. LEGAL SECTIONS
-- ============================================================
-- Stores individual sections belonging to Acts.
--
-- section_number is VARCHAR because sections can contain:
-- 106(1), 106(2), 303, 303(1), etc.
--
-- keywords are used by the Investigation Agent for retrieval.
-- ============================================================

CREATE TABLE IF NOT EXISTS legal_sections (
    section_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    act_id INT NOT NULL,

    section_number VARCHAR(30) NOT NULL,

    chapter_number VARCHAR(30),

    chapter_title VARCHAR(255),

    section_title VARCHAR(500) NOT NULL,

    section_description TEXT,

    section_text LONGTEXT,

    keywords TEXT,

    is_offence BOOLEAN DEFAULT FALSE,

    is_active BOOLEAN DEFAULT TRUE,

    source_name VARCHAR(150),

    source_url VARCHAR(500),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (act_id)
        REFERENCES legal_acts(act_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    UNIQUE KEY unique_act_section (
        act_id,
        section_number
    ),

    INDEX idx_section_number (
        section_number
    ),

    INDEX idx_section_active (
        is_active
    ),

    FULLTEXT KEY idx_legal_search (
        section_title,
        section_description,
        keywords
    )
);


-- ============================================================
-- 5. COMPLAINTS
-- ============================================================

CREATE TABLE IF NOT EXISTS complaints (
    complaint_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    complaint_name VARCHAR(150),

    original_audio_path VARCHAR(500),

    detected_language VARCHAR(20),

    original_transcription LONGTEXT,

    complaint_status ENUM(
        'RECEIVED',
        'TRANSCRIBED',
        'ANALYZED',
        'DRAFT_GENERATED',
        'APPROVED',
        'REJECTED'
    ) DEFAULT 'RECEIVED',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);


-- ============================================================
-- 6. TRANSCRIPTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS transcriptions (
    transcription_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    complaint_id BIGINT NOT NULL,

    original_text LONGTEXT NOT NULL,

    edited_text LONGTEXT,

    detected_language VARCHAR(20),

    transcription_status ENUM(
        'ORIGINAL',
        'EDITED',
        'CONFIRMED'
    ) DEFAULT 'ORIGINAL',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    INDEX idx_transcription_complaint (
        complaint_id
    )
);


-- ============================================================
-- 7. FIR DRAFTS
-- ============================================================

CREATE TABLE IF NOT EXISTS fir_drafts (
    fir_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    complaint_id BIGINT NOT NULL,

    -- --------------------------------------------------------
    -- FIR NUMBER
    -- --------------------------------------------------------
    -- proposed_fir_number:
    -- number shown while draft is being prepared.
    --
    -- fir_number:
    -- actual registered FIR number.
    --
    -- The actual number is assigned/committed only after
    -- officer approval.
    -- --------------------------------------------------------

    proposed_fir_number INT,

    fir_number INT,

    district VARCHAR(100),

    police_station VARCHAR(150),

    year INT,

    fir_date_time DATETIME,

    -- --------------------------------------------------------
    -- OCCURRENCE INFORMATION
    -- --------------------------------------------------------

    occurrence_from DATETIME,

    occurrence_to DATETIME,

    information_received_datetime DATETIME,

    general_diary_reference VARCHAR(100),

    type_of_information VARCHAR(50),

    place_of_occurrence TEXT,

    -- --------------------------------------------------------
    -- COMPLAINANT / INFORMANT
    -- --------------------------------------------------------

    complainant_name VARCHAR(150),

    father_husband_name VARCHAR(150),

    date_of_birth VARCHAR(50),

    nationality VARCHAR(100),

    uid_number VARCHAR(100),

    passport_number VARCHAR(100),

    other_id_details VARCHAR(255),

    occupation VARCHAR(150),

    complainant_address TEXT,

    phone_number VARCHAR(30),

    mobile_number VARCHAR(30),

    -- --------------------------------------------------------
    -- ACCUSED
    -- --------------------------------------------------------

    accused_details TEXT,

    -- --------------------------------------------------------
    -- DELAY
    -- --------------------------------------------------------

    reason_for_delay TEXT,

    -- --------------------------------------------------------
    -- PROPERTY
    -- --------------------------------------------------------

    property_details TEXT,

    total_property_value DECIMAL(15,2),

    -- --------------------------------------------------------
    -- INQUEST / U.D.
    -- --------------------------------------------------------

    inquest_ud_case VARCHAR(255),

    -- --------------------------------------------------------
    -- ORIGINAL FIRST INFORMATION
    -- --------------------------------------------------------
    -- IMPORTANT:
    -- This field must preserve the complainant's statement.
    -- The system must NOT automatically rewrite it.
    -- --------------------------------------------------------

    first_information_contents LONGTEXT NOT NULL,

    -- --------------------------------------------------------
    -- ACTION TAKEN
    -- --------------------------------------------------------

    action_taken TEXT,

    -- --------------------------------------------------------
    -- AI ANALYSIS
    -- --------------------------------------------------------

    crime_category VARCHAR(150),

    crime_classification_confidence DECIMAL(5,2),

    missing_information JSON,

    inconsistent_information JSON,

    structured_ai_data JSON,

    agent_trace JSON,

    -- --------------------------------------------------------
    -- FIR STATUS
    -- --------------------------------------------------------

    draft_status ENUM(
        'DRAFT',
        'APPROVED',
        'REJECTED'
    ) DEFAULT 'DRAFT',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (complaint_id)
        REFERENCES complaints(complaint_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_fir_complaint (
        complaint_id
    ),

    INDEX idx_fir_status (
        draft_status
    ),

    INDEX idx_fir_year (
        year
    ),

    -- Only approved/registered FIRs should receive actual numbers.
    UNIQUE KEY unique_registered_fir_number (
        year,
        fir_number
    )
);


-- ============================================================
-- 8. FIR DRAFT SECTIONS
-- ============================================================
-- This table connects FIRs with multiple legal sections.
--
-- Example:
--
-- FIR #25
--   ├── BNS 303
--   └── BNS 317
--
-- The Investigation Agent can suggest sections.
-- The officer then verifies/rejects/adds sections.
-- ============================================================

CREATE TABLE IF NOT EXISTS fir_draft_sections (
    fir_draft_section_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    fir_id BIGINT NOT NULL,

    section_id BIGINT NOT NULL,

    suggestion_source ENUM(
        'AI_AGENT',
        'OFFICER'
    ) DEFAULT 'AI_AGENT',

    suggestion_reason TEXT,

    confidence_score DECIMAL(5,2),

    verification_status ENUM(
        'AI_SUGGESTED',
        'OFFICER_VERIFIED',
        'OFFICER_REJECTED'
    ) DEFAULT 'AI_SUGGESTED',

    officer_remarks TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (fir_id)
        REFERENCES fir_drafts(fir_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (section_id)
        REFERENCES legal_sections(section_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    UNIQUE KEY unique_fir_section (
        fir_id,
        section_id
    ),

    INDEX idx_fir_sections_fir (
        fir_id
    ),

    INDEX idx_fir_sections_section (
        section_id
    )
);


-- ============================================================
-- 9. FIR APPROVALS
-- ============================================================

CREATE TABLE IF NOT EXISTS fir_approvals (
    approval_id BIGINT AUTO_INCREMENT PRIMARY KEY,

    fir_id BIGINT NOT NULL,

    officer_id INT NOT NULL,

    decision ENUM(
        'APPROVED',
        'REJECTED'
    ) NOT NULL,

    officer_remarks TEXT,

    approved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (fir_id)
        REFERENCES fir_drafts(fir_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (officer_id)
        REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_approval_fir (
        fir_id
    ),

    INDEX idx_approval_officer (
        officer_id
    )
);


-- ============================================================
-- 10. INITIAL LEGAL ACTS
-- ============================================================
-- These are the major central criminal-law Acts relevant to
-- the project.
--
-- Section data will be populated separately from verified
-- official sources.
-- ============================================================

INSERT IGNORE INTO legal_acts
(
    act_code,
    act_name,
    short_name,
    act_year,
    act_category,
    description,
    source_name,
    source_url
)
VALUES

(
    'BNS',
    'Bharatiya Nyaya Sanhita, 2023',
    'BNS',
    2023,
    'OFFENCE',
    'Law relating to offences and punishments.',
    'National Crime Records Bureau',
    'https://cytrain.ncrb.gov.in/staticpage/web_pages/IndexBNS.html'
),

(
    'BNSS',
    'Bharatiya Nagarik Suraksha Sanhita, 2023',
    'BNSS',
    2023,
    'PROCEDURE',
    'Law relating to criminal procedure.',
    'National Crime Records Bureau',
    'https://cytrain.ncrb.gov.in/staticpage/web_pages/IndexBNSS.html'
),

(
    'BSA',
    'Bharatiya Sakshya Adhiniyam, 2023',
    'BSA',
    2023,
    'EVIDENCE',
    'Law relating to evidence.',
    'National Crime Records Bureau',
    'https://cytrain.ncrb.gov.in/staticpage/web_pages/IndexBSA.html'
);


-- ============================================================
-- 11. CHECK DATABASE
-- ============================================================

SELECT
    'IntelliVision database created successfully'
    AS database_status;

SHOW TABLES;
SELECT * FROM legal_acts;
