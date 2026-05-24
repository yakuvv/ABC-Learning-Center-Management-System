# database_commented.py
# -----------------------------------------------------------------------------
# REFERENCE COPY — same logic as database.py, with notes on what changed from the
# OLD schema (commit 4a2b8de / v2.1: ENROLLMENT, schoolID, gradeLevel, etc.).
#
# LIVE FILE USED BY THE APP: database.py
# Run init:  python database.py
# Wipe data: python -c "from database import clear_all_data; clear_all_data()"
# -----------------------------------------------------------------------------

import sqlite3
import random

DB_NAME = "abc_learning_center.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# CHANGED: was generate_school_id(school_year) -> "YY-RANDOM4-RANDOM2" (e.g. 25-2018-23)
#          tied to school year prefix (caused bad IDs like "1s-8079-27" when year was wrong).
# NOW:     generate_learner_id() -> "RANDOM2-RANDOM4-RANDOM4" (e.g. 47-3821-9056)
#          checks uniqueness in REGISTRATION.learnerID (not ENROLLMENT.schoolID).
def generate_learner_id(term: str = "") -> str:
    """Generate Learner ID: RANDOM2-RANDOM4-RANDOM4 (e.g. 47-3821-9056). term is unused (kept for callers)."""
    for _ in range(100):
        learner_id = (
            f"{random.randint(10, 99)}-"
            f"{random.randint(1000, 9999)}-"
            f"{random.randint(1000, 9999)}"
        )
        conn = get_connection()
        try:
            exists = conn.execute(
                "SELECT 1 FROM REGISTRATION WHERE learnerID = ?", (learner_id,)
            ).fetchone()
            if not exists:
                return learner_id
        finally:
            conn.close()
    raise RuntimeError("Could not generate a unique Learner ID")


# NEW: helper to empty all tables but keep schema (used when you asked for a clean DB).
def clear_all_data(db_path: str | None = None):
    """Remove all rows from every table; keeps schema intact."""
    path = db_path or DB_NAME
    tables = [
        "RECEIPT", "PAYMENT", "GRADE", "ATTENDANCE",
        "REGISTRATION_DETAIL", "REGISTRATION",  # was DETAIL, ENROLLMENT
        "PARENT", "STUDENT", "SUBJECT", "STAFF", "TUTOR",
    ]
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
        except sqlite3.OperationalError:
            pass
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.close()


# CHANGED: was init_database() -> init_database_v2() only (schema lived split in database_v2.py).
# NOW:     single init_database() with full tutorial-center schema below.
def init_database():
    """Initializes the database with the current schema."""
    conn = get_connection()
    cursor = conn.cursor()

    print("Initializing ABC Learning Center Database...")

    # STUDENT — CHANGED columns:
    #   BEFORE: levelType TEXT (optional)
    #   NOW:    level TEXT NOT NULL, program TEXT (tutorial center: Grade 7, program track, etc.)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STUDENT (
        studentID INTEGER PRIMARY KEY AUTOINCREMENT,
        studLname TEXT NOT NULL,
        studFname TEXT NOT NULL,
        studMname TEXT,
        gender TEXT NOT NULL CHECK(gender IN ('M','F')),
        dob DATE NOT NULL,
        address TEXT,
        studContactNo TEXT,
        studEmail TEXT UNIQUE,
        level TEXT NOT NULL,
        program TEXT
    )''')

    # PARENT — unchanged structure
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PARENT (
        parentID INTEGER PRIMARY KEY AUTOINCREMENT,
        studentID INTEGER NOT NULL,
        parName TEXT NOT NULL,
        parContactNo TEXT,
        parEmail TEXT,
        relationship TEXT NOT NULL,
        FOREIGN KEY (studentID) REFERENCES STUDENT(studentID) ON DELETE CASCADE
    )''')

    # STAFF — unchanged
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STAFF (
        staffID INTEGER PRIMARY KEY AUTOINCREMENT,
        staffFname TEXT NOT NULL,
        staffLname TEXT NOT NULL,
        position TEXT NOT NULL,
        staffContactNo TEXT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    # TUTOR — unchanged
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TUTOR (
        tutorID INTEGER PRIMARY KEY AUTOINCREMENT,
        tutorFname TEXT NOT NULL,
        tutorLname TEXT NOT NULL,
        tutorContactNo TEXT,
        tutorEmail TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        specialization TEXT
    )''')

    # SUBJECT — CHANGED columns:
    #   BEFORE: gradeLevel, strand, semester, subjectType
    #   NOW:    level, program, termType (matches REGISTRATION / tutorial center)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SUBJECT (
        subjectID INTEGER PRIMARY KEY AUTOINCREMENT,
        subjectName TEXT NOT NULL,
        description TEXT,
        level TEXT NOT NULL,
        program TEXT,
        termType TEXT,
        isActive INTEGER DEFAULT 1
    )''')

    # REGISTRATION — REPLACES old ENROLLMENT table
    #   BEFORE (ENROLLMENT): enrollmentID, schoolID, gradeLevel, section, levelType,
    #                       term, schoolYear, enrDate, enrStatus
    #   NOW:                registrationID, learnerID, level, groupName,
    #                       term, regDate, regStatus (no schoolYear / section / schoolID)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS REGISTRATION (
        registrationID INTEGER PRIMARY KEY AUTOINCREMENT,
        studentID INTEGER NOT NULL,
        staffID INTEGER NOT NULL,
        learnerID TEXT UNIQUE,
        level TEXT NOT NULL,
        groupName TEXT NOT NULL,
        term TEXT NOT NULL,
        regDate DATE DEFAULT CURRENT_DATE,
        regStatus TEXT DEFAULT 'Active',
        FOREIGN KEY (studentID) REFERENCES STUDENT(studentID) ON DELETE CASCADE,
        FOREIGN KEY (staffID) REFERENCES STAFF(staffID)
    )''')

    # REGISTRATION_DETAIL — REPLACES old DETAIL table
    #   BEFORE: DETAIL(enrollmentID, subjectID)
    #   NOW:    REGISTRATION_DETAIL(registrationID, subjectID)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS REGISTRATION_DETAIL (
        detailID INTEGER PRIMARY KEY AUTOINCREMENT,
        registrationID INTEGER NOT NULL,
        subjectID INTEGER NOT NULL,
        FOREIGN KEY (registrationID) REFERENCES REGISTRATION(registrationID) ON DELETE CASCADE,
        FOREIGN KEY (subjectID) REFERENCES SUBJECT(subjectID)
    )''')

    # ATTENDANCE — same idea; FK now points to REGISTRATION_DETAIL (was DETAIL)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ATTENDANCE (
        attendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID INTEGER NOT NULL,
        attDate DATE NOT NULL,
        attStatus TEXT NOT NULL CHECK(attStatus IN ('Present','Absent','Late')),
        FOREIGN KEY (detailID) REFERENCES REGISTRATION_DETAIL(detailID) ON DELETE CASCADE
    )''')

    # GRADE — CHANGED:
    #   BEFORE: quarter TEXT (1st Quarter, etc.)
    #   NOW:    period TEXT (1st Period / 1st Semester — aligns with term_options.py)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS GRADE (
        gradeID INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID INTEGER NOT NULL,
        tutorID INTEGER NOT NULL,
        period TEXT NOT NULL,
        gradeValue REAL NOT NULL,
        dateRecorded DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (detailID) REFERENCES REGISTRATION_DETAIL(detailID) ON DELETE CASCADE,
        FOREIGN KEY (tutorID) REFERENCES TUTOR(tutorID),
        UNIQUE(detailID, period) ON CONFLICT REPLACE
    )''')

    # PAYMENT — CHANGED FK:
    #   BEFORE: enrollmentID -> ENROLLMENT
    #   NOW:    registrationID -> REGISTRATION
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PAYMENT (
        paymentID INTEGER PRIMARY KEY AUTOINCREMENT,
        registrationID INTEGER NOT NULL,
        payDate DATE DEFAULT CURRENT_DATE,
        amount REAL NOT NULL,
        payMethod TEXT NOT NULL DEFAULT 'Cash',
        payStatus TEXT NOT NULL DEFAULT 'Paid',
        FOREIGN KEY (registrationID) REFERENCES REGISTRATION(registrationID) ON DELETE CASCADE
    )''')

    # RECEIPT — unchanged (still links to PAYMENT)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS RECEIPT (
        receiptID INTEGER PRIMARY KEY AUTOINCREMENT,
        paymentID INTEGER NOT NULL UNIQUE,
        receiptNumber TEXT UNIQUE NOT NULL,
        dateIssued DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (paymentID) REFERENCES PAYMENT(paymentID) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()
    print("Database successfully initialized!")
    return True


if __name__ == "__main__":
    init_database()
