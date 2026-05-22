# database.py
import sqlite3
import random

DB_NAME = "abc_learning_center.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def generate_school_id(school_year: str) -> str:
    """Generate School ID in format: YY-RANDOM4-RANDOM2 (e.g. 25-2018-23)"""
    try:
        yy = school_year[:2]
    except:
        yy = "25"
    random4 = random.randint(1000, 9999)
    random2 = random.randint(10, 99)
    return f"{yy}-{random4}-{random2}"


def init_database():
    """Initializes the database with v2.1 schema."""
    return init_database_v2()


def init_database_v2():
    conn = get_connection()
    cursor = conn.cursor()

    print("🚀 Initializing ABC Learning Center Database to v2.1...")

    # ====================== STUDENT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STUDENT (
        studentID INTEGER PRIMARY KEY AUTOINCREMENT,
        studLname TEXT NOT NULL,
        studFname TEXT NOT NULL,
        studMname TEXT,
        gender TEXT NOT NULL CHECK(gender IN ('M', 'F')),
        dob DATE NOT NULL,
        address TEXT,
        studContactNo TEXT,
        studEmail TEXT UNIQUE,
        levelType TEXT
    )''')

    # ====================== PARENT ======================
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

    # ====================== STAFF ======================
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

    # ====================== TUTOR ======================
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

    # ====================== SUBJECT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SUBJECT (
        subjectID INTEGER PRIMARY KEY AUTOINCREMENT,
        subjectName TEXT NOT NULL,
        description TEXT,
        gradeLevel TEXT NOT NULL,
        strand TEXT,
        semester INTEGER,
        subjectType TEXT,
        termType TEXT,
        isActive INTEGER DEFAULT 1
    )''')

    # ====================== ENROLLMENT (Updated) ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ENROLLMENT (
        enrollmentID INTEGER PRIMARY KEY AUTOINCREMENT,
        studentID INTEGER NOT NULL,
        staffID INTEGER NOT NULL,
        schoolID TEXT UNIQUE,
        gradeLevel TEXT NOT NULL,
        section TEXT NOT NULL,
        levelType TEXT,
        term TEXT NOT NULL,
        schoolYear TEXT NOT NULL,
        enrDate DATE DEFAULT CURRENT_DATE,
        enrStatus TEXT DEFAULT 'Active',
        FOREIGN KEY (studentID) REFERENCES STUDENT(studentID) ON DELETE CASCADE,
        FOREIGN KEY (staffID) REFERENCES STAFF(staffID)
    )''')

    # ====================== DETAIL ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DETAIL (
        detailID INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollmentID INTEGER NOT NULL,
        subjectID INTEGER NOT NULL,
        FOREIGN KEY (enrollmentID) REFERENCES ENROLLMENT(enrollmentID) ON DELETE CASCADE,
        FOREIGN KEY (subjectID) REFERENCES SUBJECT(subjectID)
    )''')

    # ====================== ATTENDANCE ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ATTENDANCE (
        attendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID INTEGER NOT NULL,
        attDate DATE NOT NULL,
        attStatus TEXT NOT NULL CHECK(attStatus IN ('Present', 'Absent', 'Late')),
        FOREIGN KEY (detailID) REFERENCES DETAIL(detailID) ON DELETE CASCADE
    )''')

    # ====================== GRADE ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS GRADE (
        gradeID INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID INTEGER NOT NULL,
        tutorID INTEGER NOT NULL,
        quarter TEXT NOT NULL,
        gradeValue REAL NOT NULL,
        dateRecorded DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (detailID) REFERENCES DETAIL(detailID) ON DELETE CASCADE,
        FOREIGN KEY (tutorID) REFERENCES TUTOR(tutorID),
        UNIQUE(detailID, quarter) ON CONFLICT REPLACE
    )''')

    # ====================== PAYMENT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PAYMENT (
        paymentID INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollmentID INTEGER NOT NULL,
        payDate DATE DEFAULT CURRENT_DATE,
        amount REAL NOT NULL,
        payMethod TEXT NOT NULL DEFAULT 'Cash',
        payStatus TEXT NOT NULL DEFAULT 'Paid',
        FOREIGN KEY (enrollmentID) REFERENCES ENROLLMENT(enrollmentID) ON DELETE CASCADE
    )''')

    # ====================== RECEIPT ======================
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
    print("✅ Database successfully updated/initialized to v2.1!")
    return True


if __name__ == "__main__":
    init_database()