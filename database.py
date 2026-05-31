# database.py
import os
import sqlite3
import random

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "abc_learning_center.db")

# Per subject per term (2-hour sessions); by student grade level
GRADE_TERM_PRICES = {
    (1, 3): 900.0,
    (4, 6): 1000.0,
    (7, 8): 1100.0,
    (9, 10): 1200.0,
    (11, 12): 1400.0,
}


def price_for_level(level: str) -> float:
    """Return tuition per subject per term for a grade level string (e.g. 'Grade 5')."""
    if not level:
        return 0.0
    digits = "".join(ch for ch in level if ch.isdigit())
    if not digits:
        return 0.0
    grade = int(digits)
    for (lo, hi), price in GRADE_TERM_PRICES.items():
        if lo <= grade <= hi:
            return price
    return 0.0


def _ensure_payment_time_column(conn):
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='PAYMENT'"
    ).fetchone()
    if not table:
        return
    cols = [row[1] for row in conn.execute("PRAGMA table_info(PAYMENT)")]
    if "payTime" not in cols:
        conn.execute("ALTER TABLE PAYMENT ADD COLUMN payTime TEXT")
    if "amountTendered" not in cols:
        conn.execute("ALTER TABLE PAYMENT ADD COLUMN amountTendered REAL")
    if "changeDue" not in cols:
        conn.execute("ALTER TABLE PAYMENT ADD COLUMN changeDue REAL")
    conn.commit()


def _ensure_attendance_time_column(conn):
    # Fresh databases will not have tables yet; avoid ALTER TABLE before init.
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='ATTENDANCE'"
    ).fetchone()
    if not table:
        return
    cols = [row[1] for row in conn.execute("PRAGMA table_info(ATTENDANCE)")]
    if "attTime" not in cols:
        conn.execute("ALTER TABLE ATTENDANCE ADD COLUMN attTime TEXT")


def _ensure_grade_columns(conn):
    """Add letterGrade and gradeDesc to GRADE if they don't exist yet."""
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='GRADE'"
    ).fetchone()
    if not table:
        return
    cols = [row[1] for row in conn.execute("PRAGMA table_info(GRADE)")]
    if "letterGrade" not in cols:
        conn.execute("ALTER TABLE GRADE ADD COLUMN letterGrade TEXT")
    if "gradeDesc" not in cols:
        conn.execute("ALTER TABLE GRADE ADD COLUMN gradeDesc TEXT")
    conn.commit()


def _ensure_parent_contact_info_column(conn):
    """Merge parContactNo and parEmail into a single parContactInfo TEXT column."""
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='PARENT'"
    ).fetchone()
    if not table:
        return
    cols = [row[1] for row in conn.execute("PRAGMA table_info(PARENT)")]
    if "parContactInfo" not in cols:
        conn.execute("ALTER TABLE PARENT ADD COLUMN parContactInfo TEXT")
        # Migrate existing data: combine parContactNo and parEmail into one field
        conn.execute("""
            UPDATE PARENT SET parContactInfo =
            CASE
                WHEN parContactNo IS NOT NULL AND parEmail IS NOT NULL
                    THEN parContactNo || ' / ' || parEmail
                WHEN parContactNo IS NOT NULL THEN parContactNo
                WHEN parEmail IS NOT NULL THEN parEmail
                ELSE NULL
            END
            WHERE parContactInfo IS NULL
        """)
    conn.commit()


def _ensure_student_contact_info_column(conn):
    """Merge studContactNo and studEmail into a single studContactInfo TEXT column."""
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='STUDENT'"
    ).fetchone()
    if not table:
        return
    cols = [row[1] for row in conn.execute("PRAGMA table_info(STUDENT)")]
    if "studContactInfo" not in cols:
        conn.execute("ALTER TABLE STUDENT ADD COLUMN studContactInfo TEXT")
        # Migrate existing data: combine studContactNo and studEmail into one field
        conn.execute("""
            UPDATE STUDENT SET studContactInfo =
            CASE
                WHEN studContactNo IS NOT NULL AND studEmail IS NOT NULL
                    THEN studContactNo || ' / ' || studEmail
                WHEN studContactNo IS NOT NULL THEN studContactNo
                WHEN studEmail IS NOT NULL THEN studEmail
                ELSE NULL
            END
            WHERE studContactInfo IS NULL
        """)
    conn.commit()


def _ensure_student_program_column(conn):
    """Ensure the program column exists in the STUDENT table."""
    table = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='STUDENT'"
    ).fetchone()
    if not table:
        return
    cols = [row[1] for row in conn.execute("PRAGMA table_info(STUDENT)")]
    if "program" not in cols:
        conn.execute("ALTER TABLE STUDENT ADD COLUMN program TEXT")
    conn.commit()


def _ensure_pricing_columns(conn):
    """Add pricePerTerm / feeAmount and backfill from grade-level pricing."""
    if not conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='SUBJECT'"
    ).fetchone():
        return
    subject_cols = [row[1] for row in conn.execute("PRAGMA table_info(SUBJECT)")]
    if "pricePerTerm" not in subject_cols:
        conn.execute("ALTER TABLE SUBJECT ADD COLUMN pricePerTerm REAL")

    # Guard: REGISTRATION_DETAIL may not exist yet on a fresh install
    if not conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='REGISTRATION_DETAIL'"
    ).fetchone():
        return
    detail_cols = [row[1] for row in conn.execute("PRAGMA table_info(REGISTRATION_DETAIL)")]
    if "feeAmount" not in detail_cols:
        conn.execute("ALTER TABLE REGISTRATION_DETAIL ADD COLUMN feeAmount REAL")

    levels = conn.execute("SELECT DISTINCT level FROM SUBJECT WHERE level IS NOT NULL").fetchall()
    for row in levels:
        level = row[0]
        price = price_for_level(level)
        if price > 0:
            conn.execute(
                "UPDATE SUBJECT SET pricePerTerm = ? WHERE level = ?",
                (price, level),
            )

    conn.execute(
        """
        UPDATE REGISTRATION_DETAIL
        SET feeAmount = (
            SELECT COALESCE(s.pricePerTerm, 0)
            FROM SUBJECT s
            WHERE s.subjectID = REGISTRATION_DETAIL.subjectID
        )
        WHERE feeAmount IS NULL OR feeAmount = 0
        """
    )
    missing = conn.execute(
        """
        SELECT rd.detailID, r.level
        FROM REGISTRATION_DETAIL rd
        JOIN REGISTRATION r ON r.registrationID = rd.registrationID
        WHERE rd.feeAmount IS NULL OR rd.feeAmount = 0
        """
    ).fetchall()
    for detail_id, level in missing:
        conn.execute(
            "UPDATE REGISTRATION_DETAIL SET feeAmount = ? WHERE detailID = ?",
            (price_for_level(level), detail_id),
        )
    conn.commit()

_migrations_done = False


def get_connection():
    global _migrations_done
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if not _migrations_done:
        _ensure_attendance_time_column(conn)
        _ensure_pricing_columns(conn)
        _ensure_payment_time_column(conn)
        _ensure_grade_columns(conn)
        _ensure_parent_contact_info_column(conn)
        _ensure_student_contact_info_column(conn)
        _ensure_student_program_column(conn)
        _migrations_done = True
    return conn


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


def clear_all_data(db_path: str | None = None):
    """Remove all rows from every table; keeps schema intact."""
    path = db_path or DB_NAME
    tables = [
        "RECEIPT", "PAYMENT", "GRADE", "ATTENDANCE",
        "REGISTRATION_DETAIL", "REGISTRATION",
        "BATCH",
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


def init_database():
    """Initializes the database with the current schema."""
    conn = get_connection()
    cursor = conn.cursor()

    print("Initializing ABC Learning Center Database...")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STUDENT (
        studentID INTEGER PRIMARY KEY AUTOINCREMENT,
        studLname TEXT NOT NULL,
        studFname TEXT NOT NULL,
        studMname TEXT,
        gender TEXT NOT NULL CHECK(gender IN ('M','F')),
        dob DATE NOT NULL,
        address TEXT,
        studContactInfo TEXT,
        level TEXT NOT NULL,
        program TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PARENT (
        parentID INTEGER PRIMARY KEY AUTOINCREMENT,
        studentID INTEGER NOT NULL,
        parName TEXT NOT NULL,
        parContactInfo TEXT,
        relationship TEXT NOT NULL,
        FOREIGN KEY (studentID) REFERENCES STUDENT(studentID) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STAFF (
        staffID INTEGER PRIMARY KEY AUTOINCREMENT,
        staffFname TEXT NOT NULL,
        staffLname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TUTOR (
        tutorID INTEGER PRIMARY KEY AUTOINCREMENT,
        tutorFname TEXT NOT NULL,
        tutorLname TEXT NOT NULL,
        tutorEmail TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SUBJECT (
        subjectID INTEGER PRIMARY KEY AUTOINCREMENT,
        subjCode TEXT NOT NULL,
        subjectName TEXT NOT NULL,
        description TEXT,
        level TEXT NOT NULL,
        pricePerTerm REAL,
        isActive INTEGER DEFAULT 1
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BATCH (
        batchID INTEGER PRIMARY KEY AUTOINCREMENT,
        batchCode TEXT UNIQUE NOT NULL,
        subjectID INTEGER NOT NULL,
        level TEXT NOT NULL,
        schedule TEXT NOT NULL,
        batchLabel TEXT NOT NULL,
        tutorID INTEGER,
        capacity INTEGER NOT NULL DEFAULT 15,
        isActive INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (subjectID) REFERENCES SUBJECT(subjectID),
        FOREIGN KEY (tutorID) REFERENCES TUTOR(tutorID)
    )''')

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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS REGISTRATION_DETAIL (
        detailID INTEGER PRIMARY KEY AUTOINCREMENT,
        registrationID INTEGER NOT NULL,
        subjectID INTEGER NOT NULL,
        batchID INTEGER,
        feeAmount REAL,
        enrollStatus TEXT NOT NULL DEFAULT 'Active' CHECK(enrollStatus IN ('Active','Completed','Dropped')),
        FOREIGN KEY (registrationID) REFERENCES REGISTRATION(registrationID) ON DELETE CASCADE,
        FOREIGN KEY (subjectID) REFERENCES SUBJECT(subjectID),
        FOREIGN KEY (batchID) REFERENCES BATCH(batchID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ATTENDANCE (
        attendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID INTEGER NOT NULL,
        attDate DATE NOT NULL,
        attTime TEXT,
        attStatus TEXT NOT NULL CHECK(attStatus IN ('Present','Absent','Late')),
        FOREIGN KEY (detailID) REFERENCES REGISTRATION_DETAIL(detailID) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS GRADE (
        gradeID INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID INTEGER NOT NULL,
        tutorID INTEGER NOT NULL,
        period TEXT NOT NULL DEFAULT 'Overall',
        gradeValue REAL NOT NULL,
        letterGrade TEXT,
        gradeDesc TEXT,
        dateRecorded DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (detailID) REFERENCES REGISTRATION_DETAIL(detailID) ON DELETE CASCADE,
        FOREIGN KEY (tutorID) REFERENCES TUTOR(tutorID),
        UNIQUE(detailID, period) ON CONFLICT REPLACE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PAYMENT (
        paymentID INTEGER PRIMARY KEY AUTOINCREMENT,
        registrationID INTEGER NOT NULL,
        payDate DATE DEFAULT CURRENT_DATE,
        payTime TEXT,
        amount REAL NOT NULL,
        amountTendered REAL,
        changeDue REAL,
        payMethod TEXT NOT NULL DEFAULT 'Cash',
        payStatus TEXT NOT NULL DEFAULT 'Paid',
        FOREIGN KEY (registrationID) REFERENCES REGISTRATION(registrationID) ON DELETE CASCADE
    )''')

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
