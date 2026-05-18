# database.py
import sqlite3
from datetime import datetime

DB_NAME = "abc_learning_center.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_database():
    # Initiates all the Tables
    conn = get_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # ====================== STUDENT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STUDENT (
        studentID       INTEGER PRIMARY KEY AUTOINCREMENT,
        studLname       TEXT NOT NULL,
        studFname       TEXT NOT NULL,
        studMname       TEXT,
        gender          TEXT NOT NULL CHECK(gender IN ('M', 'F')),
        dob             DATE NOT NULL,
        address         TEXT,
        studContactNo   TEXT,
        studEmail       TEXT UNIQUE
    )''')

    # ====================== PARENT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PARENT (
        parentID        INTEGER PRIMARY KEY AUTOINCREMENT,
        studentID       INTEGER NOT NULL,
        parName         TEXT NOT NULL,
        parContactNo    TEXT,
        parEmail        TEXT,
        relationship    TEXT NOT NULL,
        FOREIGN KEY (studentID) REFERENCES STUDENT(studentID) ON DELETE CASCADE
    )''')

    # ====================== STAFF ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STAFF (
        staffID         INTEGER PRIMARY KEY AUTOINCREMENT,
        staffFname      TEXT NOT NULL,
        staffLname      TEXT NOT NULL,
        position        TEXT NOT NULL,
        staffContactNo  TEXT,
        email           TEXT UNIQUE NOT NULL,
        password        TEXT NOT NULL
    )''')

    # ====================== TUTOR ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS TUTOR (
        tutorID         INTEGER PRIMARY KEY AUTOINCREMENT,
        tutorFname      TEXT NOT NULL,
        tutorLname      TEXT NOT NULL,
        tutorContactNo  TEXT,
        tutorEmail      TEXT UNIQUE NOT NULL,
        password        TEXT NOT NULL,
        specialization  TEXT
    )''')

    # ====================== SUBJECT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SUBJECT (
        subjectID       INTEGER PRIMARY KEY AUTOINCREMENT,
        subjectName     TEXT NOT NULL,
        description     TEXT,
        gradeLevel      TEXT NOT NULL
    )''')

    # ====================== ENROLLMENT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ENROLLMENT (
        enrollmentID    INTEGER PRIMARY KEY AUTOINCREMENT,
        studentID       INTEGER NOT NULL,
        staffID         INTEGER NOT NULL,
        enrDate         DATE DEFAULT CURRENT_DATE,
        term            TEXT NOT NULL,
        schoolYear      TEXT NOT NULL,
        enrStatus       TEXT DEFAULT 'Active',
        FOREIGN KEY (studentID) REFERENCES STUDENT(studentID),
        FOREIGN KEY (staffID) REFERENCES STAFF(staffID)
    )''')

    # ====================== DETAIL ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DETAIL (
        detailID        INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollmentID    INTEGER NOT NULL,
        subjectID       INTEGER NOT NULL,
        FOREIGN KEY (enrollmentID) REFERENCES ENROLLMENT(enrollmentID),
        FOREIGN KEY (subjectID) REFERENCES SUBJECT(subjectID)
    )''')

    # ====================== ATTENDANCE ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ATTENDANCE (
        attendanceID    INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID        INTEGER NOT NULL,
        attDate         DATE NOT NULL,
        attStatus       TEXT NOT NULL CHECK(attStatus IN ('Present', 'Absent', 'Late')),
        FOREIGN KEY (detailID) REFERENCES DETAIL(detailID)
    )''')

    # ====================== GRADE ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS GRADE (
        gradeID         INTEGER PRIMARY KEY AUTOINCREMENT,
        detailID        INTEGER NOT NULL,
        tutorID         INTEGER NOT NULL,
        gradeValue      REAL NOT NULL,
        dateRecorded    DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (detailID) REFERENCES DETAIL(detailID),
        FOREIGN KEY (tutorID) REFERENCES TUTOR(tutorID)
    )''')

    # ====================== PAYMENT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PAYMENT (
        paymentID       INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollmentID    INTEGER NOT NULL,
        payDate         DATE DEFAULT CURRENT_DATE,
        amount          REAL NOT NULL,
        payMethod       TEXT NOT NULL DEFAULT 'Cash',
        payStatus       TEXT NOT NULL DEFAULT 'Paid',
        FOREIGN KEY (enrollmentID) REFERENCES ENROLLMENT(enrollmentID)
    )''')

    # ====================== RECEIPT ======================
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS RECEIPT (
        receiptID       INTEGER PRIMARY KEY AUTOINCREMENT,
        paymentID       INTEGER NOT NULL,
        receiptNumber   TEXT UNIQUE NOT NULL,
        dateIssued      DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (paymentID) REFERENCES PAYMENT(paymentID)
    )''')

    conn.commit()
    conn.close()
    print("Database initialized successfully with all tables!")

if __name__ == "__main__":
    init_database()