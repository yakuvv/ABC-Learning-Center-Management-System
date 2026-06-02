# migrate_and_seed.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import sqlite3

from database import init_database, get_connection, DB_NAME, price_for_level

BACKUP_NAME = os.path.join(os.path.dirname(DB_NAME), "abc_learning_center_backup.db")


def drop_all_tables(cursor):
    # I drop all application tables in a foreign-key-safe order.
    tables = [
        "RECEIPT", "PAYMENT", "GRADE", "ATTENDANCE",
        "REGISTRATION_DETAIL", "REGISTRATION",
        "BATCH",
        "PARENT", "STUDENT", "SUBJECT", "STAFF", "TUTOR",
        # legacy names from older schema
        "DETAIL", "ENROLLMENT",
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")


def seed_staff_and_tutor(cursor):
    cursor.execute('''
        INSERT OR IGNORE INTO STAFF (staffFname, staffLname, staffMname, staffContactInfo, password)
        VALUES ('Vince', 'Oñate', 'A.', 'vince.onate@abclearning.com', 'ilovecpu')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO TUTOR (tutorFname, tutorLname, tutorMname, tutorContactInfo, password)
        VALUES ('Maria', 'Santos', 'C.', 'maria.santos@abclearning.com', 'iloveccs')
    ''')


def seed_sample_students(cursor):
    samples = [
        ("Dela Cruz", "John Miguel", "A.", "M", "2018-05-10", "123 Mabini St, Manila", "0917-123-4567", None, "Grade 1", "Maria Dela Cruz", "0917-987-6543", None, "Mother"),
        ("Reyes", "Sophia Marie", "B.", "F", "2019-01-15", "456 Rizal Ave, QC", None, "sophia.reyes@email.com", "Grade 1", "Jose Reyes", None, "jose.reyes@email.com", "Father"),
        ("Smith", "Alexander Jose", "C.", "M", "2018-11-20", "789 Burgos St, Makati", "0917-987-6543", None, "Grade 2", "Robert Smith", "0917-111-2222", None, "Father"),
        ("Garcia", "Isabella Grace", "D.", "F", "2017-08-05", "321 BGC, Taguig", None, "isabella.garcia@email.com", "Grade 2", "Linda Garcia", None, "linda.garcia@email.com", "Mother"),
        ("Mendoza", "Ethan Gabriel", "E.", "M", "2017-02-14", "654 EDSA, Mandaluyong", "0918-111-2222", None, "Grade 3", "Antonio Mendoza", "0918-999-8888", None, "Father"),
        ("Jones", "Mia Corazon", "F.", "F", "2016-09-30", "987 Taft Ave, Pasay", None, "mia.jones@email.com", "Grade 3", "Sarah Jones", None, "sarah.jones@email.com", "Mother"),
        ("Bautista", "Jacob Elias", "G.", "M", "2016-04-12", "159 Ortigas Center, Pasig", "0919-333-4444", None, "Grade 4", "William Bautista", "0919-777-6666", None, "Father"),
        ("Williams", "Olivia Rosario", "H.", "F", "2015-12-25", "753 Shaw Blvd, San Juan", None, "olivia.williams@email.com", "Grade 4", "Patricia Williams", None, "patricia.williams@email.com", "Mother"),
        ("Cruz", "Lucas Mateo", "I.", "M", "2015-06-18", "852 Araneta Ave, Marikina", "0920-555-6666", None, "Grade 5", "Richard Cruz", "0920-123-4567", None, "Father"),
        ("Brown", "Emma Luz", "J.", "F", "2014-10-05", "369 Katipunan Ave, QC", None, "emma.brown@email.com", "Grade 5", "Elizabeth Brown", None, "elizabeth.brown@email.com", "Mother"),
        ("Santos", "Matthew Luis", "K.", "M", "2014-03-22", "147 Legarda St, Manila", "0921-777-8888", None, "Grade 6", "Joseph Santos", "0921-987-6543", None, "Father"),
        ("Miller", "Chloe Marisol", "L.", "F", "2013-07-08", "258 Commonwealth Ave, QC", None, "chloe.miller@email.com", "Grade 6", "Susan Miller", None, "susan.miller@email.com", "Mother"),
        ("Torres", "William Carlos", "M.", "M", "2013-01-30", "369 Espana Blvd, Manila", "0922-999-0000", None, "Grade 7", "Thomas Torres", "0922-111-2222", None, "Father"),
        ("Davis", "Ava Consuelo", "N.", "F", "2012-08-14", "741 Roxas Blvd, Pasay", None, "ava.davis@email.com", "Grade 8", "Margaret Davis", None, "margaret.davis@email.com", "Mother"),
        ("Gonzales", "James Rafael", "O.", "M", "2012-02-28", "852 Alabang, Muntinlupa", "0923-123-1111", None, "Grade 9", "Charles Gonzales", "0923-999-8888", None, "Father"),
        ("Wilson", "Sofia Carmen", "P.", "F", "2011-09-17", "963 Ayala Ave, Makati", None, "sofia.wilson@email.com", "Grade 10", "Jessica Wilson", None, "jessica.wilson@email.com", "Mother"),
        ("Flores", "Daniel Antonio", "Q.", "M", "2010-04-05", "159 Macapagal Blvd, Pasay", "0924-222-3333", None, "Grade 11", "Christopher Flores", "0924-777-6666", None, "Father"),
        ("Moore", "Victoria Paz", "R.", "F", "2009-11-22", "753 Pioneer St, Mandaluyong", None, "victoria.moore@email.com", "Grade 11", "Sarah Moore", None, "sarah.moore@email.com", "Mother"),
        ("Villanueva", "Sebastian Cruz", "S.", "M", "2009-05-10", "357 C5 Road, Taguig", "0925-444-5555", None, "Grade 12", "Daniel Villanueva", "0925-333-4444", None, "Father"),
        ("Taylor", "Camila Joy", "T.", "F", "2008-12-01", "456 NLEX, Valenzuela", None, "camila.taylor@email.com", "Grade 12", "Nancy Taylor", None, "nancy.taylor@email.com", "Mother")
    ]

    for (lname, fname, mname, gender, dob, address, studContactNo, studEmail, level, parName, parContactNo, parEmail, relationship) in samples:
        cursor.execute("""
            INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob,
                                 address, studContactInfo, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (lname, fname, mname, gender, dob, address, studContactNo or studEmail or '', level))
        student_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO PARENT (studentID, parName, parContactInfo, relationship)
            VALUES (?, ?, ?, ?)
        """, (student_id, parName, parContactNo or parEmail or '', relationship))



def seed_batches(cursor):
    # I create 4 active batches per subject (A, B, C, and D) with a capacity of 15 students each.
    tutor_row = cursor.execute("SELECT tutorID FROM TUTOR ORDER BY tutorID LIMIT 1").fetchone()
    tutor_id = tutor_row[0] if tutor_row else None

    subjects = cursor.execute(
        "SELECT subjectID, level FROM SUBJECT WHERE isActive=1 ORDER BY subjectID"
    ).fetchall()

    for subject_id, level in subjects:
        for label, sched in [
            ("A", "Saturday 9:00 AM – 11:00 AM"),
            ("B", "Saturday 1:00 PM – 3:00 PM"),
            ("C", "Sunday 9:00 AM – 11:00 AM"),
            ("D", "Sunday 1:00 PM – 3:00 PM"),
        ]:
            cursor.execute(
                """
                INSERT INTO BATCH (subjectID, level, schedule, batchLabel, tutorID, capacity, isActive)
                VALUES (?, ?, ?, ?, ?, 15, 1)
                """,
                (subject_id, level, sched, label, tutor_id),
            )


def seed_subjects(cursor):
    # I seed subjects by grade level, optional program, and term type.
    # Elementary Grade 1-3
    for g in range(1, 4):
        level = f"Grade {g}"
        price = 900.0
        subjects = [
            ("AP", "Araling Panlipunan"),
            ("ESP", "Edukasyon sa Pagpapakatao"),
            ("ENG", "English"),
            ("FIL", "Filipino"),
            ("MATH", "Mathematics"),
            ("SCI", "Science")
        ]
        for code, name in subjects:
            subj_code = f"{code}{g}"
            cursor.execute("""
                INSERT INTO SUBJECT (subjCode, subjectName, level, pricePerTerm)
                VALUES (?, ?, ?, ?)
            """, (subj_code, name, level, price))

    # Elementary Grade 4-6
    for g in range(4, 7):
        level = f"Grade {g}"
        price = 1000.0
        subjects = [
            ("AP", "Araling Panlipunan"),
            ("ESP", "Edukasyon sa Pagpapakatao"),
            ("ENG", "English"),
            ("FIL", "Filipino"),
            ("MATH", "Mathematics"),
            ("SCI", "Science")
        ]
        for code, name in subjects:
            subj_code = f"{code}{g}"
            cursor.execute("""
                INSERT INTO SUBJECT (subjCode, subjectName, level, pricePerTerm)
                VALUES (?, ?, ?, ?)
            """, (subj_code, name, level, price))

    # Junior High Grade 7-8
    for g in range(7, 9):
        level = f"Grade {g}"
        price = 1100.0
        subjects = [
            ("AP", "Araling Panlipunan"),
            ("COMP", "Computer Education"),
            ("ENG", "English"),
            ("FIL", "Filipino"),
            ("MATH", "Mathematics"),
            ("SCI", "Science"),
            ("TLE", "TLE (Technology and Livelihood Education)")
        ]
        for code, name in subjects:
            subj_code = f"{code}{g}"
            cursor.execute("""
                INSERT INTO SUBJECT (subjCode, subjectName, level, pricePerTerm)
                VALUES (?, ?, ?, ?)
            """, (subj_code, name, level, price))

    # Junior High Grade 9-10
    for g in range(9, 11):
        level = f"Grade {g}"
        price = 1200.0
        subjects = [
            ("AP", "Araling Panlipunan"),
            ("COMP", "Computer Education"),
            ("ENG", "English"),
            ("FIL", "Filipino"),
            ("MAPEH", "MAPEH"),
            ("MATH", "Mathematics"),
            ("SCI", "Science"),
            ("TLE", "TLE (Technology and Livelihood Education)")
        ]
        for code, name in subjects:
            subj_code = f"{code}{g}"
            cursor.execute("""
                INSERT INTO SUBJECT (subjCode, subjectName, level, pricePerTerm)
                VALUES (?, ?, ?, ?)
            """, (subj_code, name, level, price))

    # Senior High Grade 11-12
    for g in range(11, 13):
        level = f"Grade {g}"
        price = 1400.0
        subjects = [
            ("GenMATH", "General Mathematics"),
            ("STAT", "Statistics and Probability"),
            ("READ", "Reading and Writing Skills"),
            ("EAPP", "English for Academic and Professional Purposes"),
            ("ELS", "Earth and Life Science"),
            ("PS", "Physical Science"),
            ("GenBIO1_", "General Biology 1"),
            ("GenBIO2_", "General Biology 2"),
            ("GenCHEM1_", "General Chemistry 1"),
            ("GenCHEM2_", "General Chemistry 2"),
            ("GenPHYS1_", "General Physics 1"),
            ("GenPHYS2_", "General Physics 2"),
            ("BusMATH", "Business Mathematics"),
            ("ORG", "Organization and Management"),
            ("ECON", "Applied Economics"),
            ("ENTREP", "Entrepreneurship"),
            ("PreCAL", "Pre-Calculus"),
            ("BasicCAL", "Basic Calculus")
        ]
        for code, name in subjects:
            subj_code = f"{code}{g}"
            cursor.execute("""
                INSERT INTO SUBJECT (subjCode, subjectName, level, pricePerTerm)
                VALUES (?, ?, ?, ?)
            """, (subj_code, name, level, price))


def run_migration():
    print("=== ABC Learning Center Database Migration & Seeder ===")

    if os.path.exists(DB_NAME):
        print(f"Creating database backup: '{BACKUP_NAME}'...")
        shutil.copyfile(DB_NAME, BACKUP_NAME)
        print("Backup created successfully.")
    else:
        print("No existing database found; creating fresh database.")

    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    try:
        print("\nDropping legacy tables...")
        drop_all_tables(cursor)

        print("Creating new schema...")
        conn.commit()
        conn.close()
        init_database()

        conn = get_connection()
        cursor = conn.cursor()

        print("\nSeeding staff, tutor, and subjects...")
        seed_staff_and_tutor(cursor)
        seed_subjects(cursor)
        seed_sample_students(cursor)
        seed_batches(cursor)

        conn.commit()
        print("\nDatabase migration and seeding completed successfully!")
    except Exception as e:
        conn.rollback()
        print(f"\nError during migration: {e}")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    run_migration()
