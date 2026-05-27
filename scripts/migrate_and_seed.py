# migrate_and_seed.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import sqlite3

from database import init_database, get_connection, DB_NAME, price_for_level

BACKUP_NAME = os.path.join(os.path.dirname(DB_NAME), "abc_learning_center_backup.db")


def drop_all_tables(cursor):
    """Drop all application tables in FK-safe order."""
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
        INSERT OR IGNORE INTO STAFF (staffFname, staffLname, position, email, password)
        VALUES ('Vince', 'Oñate', 'Administrator', 'admin', 'ilovecpu')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO TUTOR (tutorFname, tutorLname, tutorEmail, password, specialization)
        VALUES ('Maria', 'Santos', 'tutor', 'iloveccs', 'Mathematics')
    ''')


def seed_sample_students(cursor):
    """Insert 12 sample students, Grades 1–12, if they do not exist yet."""
    samples = [
        ("Garcia",   "Liam",      "A.", "Grade 1"),
        ("Reyes",    "Sophia",    "B.", "Grade 2"),
        ("Cruz",     "Noah",      "C.", "Grade 3"),
        ("Santos",   "Isabella",  "D.", "Grade 4"),
        ("Torres",   "Ethan",     "E.", "Grade 5"),
        ("Flores",   "Mia",       "F.", "Grade 6"),
        ("Ramos",    "Jacob",     "G.", "Grade 7"),
        ("Mendoza",  "Olivia",    "H.", "Grade 8"),
        ("Gutierrez","Lucas",     "I.", "Grade 9"),
        ("Domingo",  "Emma",      "J.", "Grade 10"),
        ("Villanueva","Alexander","K.", "Grade 11"),
        ("Del Rosario","Chloe",   "L.", "Grade 12"),
    ]

    for lname, fname, mname, level in samples:
        cursor.execute("""
            INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob,
                                 address, studContactNo, studEmail, level, program)
            VALUES (?, ?, ?, 'M', date('2008-01-01'), '', '', NULL, ?, NULL)
        """, (lname, fname, mname, level))


def seed_batches(cursor):
    """
    Create 2 active batches per subject (A and B), capacity 15.
    Simple schedules are placeholders for the proposed system.
    """
    tutor_row = cursor.execute("SELECT tutorID FROM TUTOR ORDER BY tutorID LIMIT 1").fetchone()
    tutor_id = tutor_row[0] if tutor_row else None

    subjects = cursor.execute(
        "SELECT subjectID, level FROM SUBJECT WHERE isActive=1 ORDER BY subjectID"
    ).fetchall()

    for subject_id, level in subjects:
        for label, sched in (("A", "Saturday 9:00 AM - 11:00 AM"), ("B", "Sunday 1:00 PM - 3:00 PM")):
            batch_code = f"{level}-{subject_id}-{label}"
            cursor.execute(
                """
                INSERT INTO BATCH (batchCode, subjectID, level, schedule, batchLabel, tutorID, capacity, isActive)
                VALUES (?, ?, ?, ?, ?, ?, 15, 1)
                """,
                (batch_code, subject_id, level, sched, label, tutor_id),
            )


def seed_subjects(cursor):
    """Seed subjects by level, optional program, and termType."""
    for g in range(1, 7):
        level = f"Grade {g}"
        term_price = price_for_level(level)
        for name, desc in [
            ("Mathematics", "Elementary Mathematics"),
            ("Science", "General Science"),
            ("English", "English Language Arts"),
            ("Filipino", "Wika at Panitikan"),
            ("Araling Panlipunan", "Social Studies / History"),
            ("MAPEH", "Music, Arts, Physical Education, and Health"),
            ("ESP", "Edukasyon sa Pagpapakatao"),
        ]:
            cursor.execute("""
                INSERT INTO SUBJECT (subjectName, description, level, program, termType, pricePerTerm)
                VALUES (?, ?, ?, NULL, 'Period', ?)
            """, (name, desc, level, term_price))

    for g in range(7, 11):
        level = f"Grade {g}"
        term_price = price_for_level(level)
        for name, desc in [
            ("Mathematics", "High School Mathematics"),
            ("English", "High School English"),
            ("Science", "General Science and Applied Technology"),
            ("Filipino", "Panitikan at Retorika"),
            ("Araling Panlipunan", "Kasaysayan at Lipunan"),
            ("MAPEH", "Music, Arts, Physical Education, and Health"),
            ("ESP", "Edukasyon sa Pagpapakatao"),
            ("TLE", "Technology and Livelihood Education"),
            ("Computer Education", "Introduction to ICT"),
        ]:
            cursor.execute("""
                INSERT INTO SUBJECT (subjectName, description, level, program, termType, pricePerTerm)
                VALUES (?, ?, ?, NULL, 'Period', ?)
            """, (name, desc, level, term_price))

    shs_programs = {
        "Grade 11": ["STEM", "ABM", "HUMSS"],
        "Grade 12": ["STEM", "ABM", "HUMSS"],
    }
    shs_core = [
        ("General Mathematics", "Core mathematical operations"),
        ("Oral Communication", "Public speaking and communicative strategies"),
        ("Reading and Writing", "Critical reading and academic writing"),
        ("Physical Education and Health", "Physical fitness and wellness"),
    ]
    for level, programs in shs_programs.items():
        term_price = price_for_level(level)
        for program in programs:
            for name, desc in shs_core:
                cursor.execute("""
                    INSERT INTO SUBJECT (subjectName, description, level, program, termType, pricePerTerm)
                    VALUES (?, ?, ?, ?, 'Period', ?)
                """, (name, desc, level, program, term_price))


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
