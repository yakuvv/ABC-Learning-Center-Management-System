-- =============================================================================
-- ABC Learning Center — SQLite schema (tutorial center / REGISTRATION model)
-- =============================================================================
-- Text-only SQL script. Run with:
--   sqlite3 abc_learning_center.db < database_schema.sql
-- Or open in DB Browser for SQLite and execute.
--
-- LIVE APP uses: database.py (python database.py)
--
-- CHANGES FROM OLD v2.1 SCHEMA (ENROLLMENT, schoolID, gradeLevel, etc.):
--   ENROLLMENT  -> REGISTRATION  (schoolID -> learnerID, gradeLevel -> level,
--                                 section -> groupName; removed schoolYear)
--   DETAIL      -> REGISTRATION_DETAIL (enrollmentID -> registrationID)
--   PAYMENT     -> registrationID FK (was enrollmentID)
--   GRADE       -> period column (was quarter)
--   STUDENT     -> level NOT NULL + program (was optional levelType)
--   SUBJECT     -> level, program, termType (was gradeLevel, strand, semester, subjectType)
--   Learner ID: ##-####-#### (generated in app by generate_learner_id(), not in SQL)
-- =============================================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- STUDENT
-- BEFORE: levelType TEXT (optional)
-- NOW:    level TEXT NOT NULL, program TEXT
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS STUDENT (
    studentID INTEGER PRIMARY KEY AUTOINCREMENT,
    studLname TEXT NOT NULL,
    studFname TEXT NOT NULL,
    studMname TEXT,
    gender TEXT NOT NULL CHECK (gender IN ('M', 'F')),
    dob DATE NOT NULL,
    address TEXT,
    studContactNo TEXT,
    studEmail TEXT UNIQUE,
    level TEXT NOT NULL,
    program TEXT
);

-- -----------------------------------------------------------------------------
-- PARENT (unchanged)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS PARENT (
    parentID INTEGER PRIMARY KEY AUTOINCREMENT,
    studentID INTEGER NOT NULL,
    parName TEXT NOT NULL,
    parContactNo TEXT,
    parEmail TEXT,
    relationship TEXT NOT NULL,
    FOREIGN KEY (studentID) REFERENCES STUDENT (studentID) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- STAFF (unchanged)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS STAFF (
    staffID INTEGER PRIMARY KEY AUTOINCREMENT,
    staffFname TEXT NOT NULL,
    staffLname TEXT NOT NULL,
    position TEXT NOT NULL,
    staffContactNo TEXT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- -----------------------------------------------------------------------------
-- TUTOR (unchanged)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS TUTOR (
    tutorID INTEGER PRIMARY KEY AUTOINCREMENT,
    tutorFname TEXT NOT NULL,
    tutorLname TEXT NOT NULL,
    tutorContactNo TEXT,
    tutorEmail TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    specialization TEXT
);

-- -----------------------------------------------------------------------------
-- SUBJECT
-- BEFORE: gradeLevel, strand, semester, subjectType
-- NOW:    level, program, termType
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS SUBJECT (
    subjectID INTEGER PRIMARY KEY AUTOINCREMENT,
    subjectName TEXT NOT NULL,
    description TEXT,
    level TEXT NOT NULL,
    program TEXT,
    termType TEXT,
    isActive INTEGER DEFAULT 1
);

-- -----------------------------------------------------------------------------
-- REGISTRATION (replaces ENROLLMENT)
-- BEFORE: enrollmentID, schoolID, gradeLevel, section, levelType,
--         term, schoolYear, enrDate, enrStatus
-- NOW:    registrationID, learnerID, level, groupName,
--         term, regDate, regStatus
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS REGISTRATION (
    registrationID INTEGER PRIMARY KEY AUTOINCREMENT,
    studentID INTEGER NOT NULL,
    staffID INTEGER NOT NULL,
    learnerID TEXT UNIQUE,
    level TEXT NOT NULL,
    groupName TEXT NOT NULL,
    term TEXT NOT NULL,
    regDate DATE DEFAULT (CURRENT_DATE),
    regStatus TEXT DEFAULT 'Active',
    FOREIGN KEY (studentID) REFERENCES STUDENT (studentID) ON DELETE CASCADE,
    FOREIGN KEY (staffID) REFERENCES STAFF (staffID)
);

-- -----------------------------------------------------------------------------
-- REGISTRATION_DETAIL (replaces DETAIL)
-- BEFORE: DETAIL (enrollmentID, subjectID)
-- NOW:    REGISTRATION_DETAIL (registrationID, subjectID)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS REGISTRATION_DETAIL (
    detailID INTEGER PRIMARY KEY AUTOINCREMENT,
    registrationID INTEGER NOT NULL,
    subjectID INTEGER NOT NULL,
    FOREIGN KEY (registrationID) REFERENCES REGISTRATION (registrationID) ON DELETE CASCADE,
    FOREIGN KEY (subjectID) REFERENCES SUBJECT (subjectID)
);

-- -----------------------------------------------------------------------------
-- ATTENDANCE
-- Same columns; FK now references REGISTRATION_DETAIL (was DETAIL)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ATTENDANCE (
    attendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    detailID INTEGER NOT NULL,
    attDate DATE NOT NULL,
    attStatus TEXT NOT NULL CHECK (attStatus IN ('Present', 'Absent', 'Late')),
    FOREIGN KEY (detailID) REFERENCES REGISTRATION_DETAIL (detailID) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- GRADE
-- BEFORE: quarter TEXT
-- NOW:    period TEXT (1st Period, 1st Semester, etc.)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS GRADE (
    gradeID INTEGER PRIMARY KEY AUTOINCREMENT,
    detailID INTEGER NOT NULL,
    tutorID INTEGER NOT NULL,
    period TEXT NOT NULL,
    gradeValue REAL NOT NULL,
    dateRecorded DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (detailID) REFERENCES REGISTRATION_DETAIL (detailID) ON DELETE CASCADE,
    FOREIGN KEY (tutorID) REFERENCES TUTOR (tutorID),
    UNIQUE (detailID, period) ON CONFLICT REPLACE
);

-- -----------------------------------------------------------------------------
-- PAYMENT
-- BEFORE: enrollmentID -> ENROLLMENT
-- NOW:    registrationID -> REGISTRATION
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS PAYMENT (
    paymentID INTEGER PRIMARY KEY AUTOINCREMENT,
    registrationID INTEGER NOT NULL,
    payDate DATE DEFAULT (CURRENT_DATE),
    amount REAL NOT NULL,
    payMethod TEXT NOT NULL DEFAULT 'Cash',
    payStatus TEXT NOT NULL DEFAULT 'Paid',
    FOREIGN KEY (registrationID) REFERENCES REGISTRATION (registrationID) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- RECEIPT (unchanged; links to PAYMENT)
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS RECEIPT (
    receiptID INTEGER PRIMARY KEY AUTOINCREMENT,
    paymentID INTEGER NOT NULL UNIQUE,
    receiptNumber TEXT UNIQUE NOT NULL,
    dateIssued DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (paymentID) REFERENCES PAYMENT (paymentID) ON DELETE CASCADE
);

-- =============================================================================
-- OPTIONAL: wipe all data (keeps tables). Uncomment to run.
-- =============================================================================
-- PRAGMA foreign_keys = OFF;
-- DELETE FROM RECEIPT;
-- DELETE FROM PAYMENT;
-- DELETE FROM GRADE;
-- DELETE FROM ATTENDANCE;
-- DELETE FROM REGISTRATION_DETAIL;
-- DELETE FROM REGISTRATION;
-- DELETE FROM PARENT;
-- DELETE FROM STUDENT;
-- DELETE FROM SUBJECT;
-- DELETE FROM STAFF;
-- DELETE FROM TUTOR;
-- DELETE FROM sqlite_sequence;
-- PRAGMA foreign_keys = ON;
