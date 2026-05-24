# migrate_and_seed.py
import shutil
import os
import sqlite3

from database import init_database, get_connection, DB_NAME

BACKUP_NAME = "abc_learning_center_backup.db"


def drop_all_tables(cursor):
    """Drop all application tables in FK-safe order."""
    tables = [
        "RECEIPT", "PAYMENT", "GRADE", "ATTENDANCE",
        "REGISTRATION_DETAIL", "REGISTRATION",
        "PARENT", "STUDENT", "SUBJECT", "STAFF", "TUTOR",
        # legacy names from older schema
        "DETAIL", "ENROLLMENT",
    ]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")


def seed_staff_and_tutor(cursor):
    cursor.execute('''
        INSERT OR IGNORE INTO STAFF (staffFname, staffLname, position, email, password)
        VALUES ('Vince', 'Oñate', 'Administrator', 'admin', 'admin123')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO TUTOR (tutorFname, tutorLname, tutorEmail, password, specialization)
        VALUES ('Maria', 'Santos', 'tutor', 'tutor123', 'Mathematics')
    ''')


def seed_subjects(cursor):
    """Seed subjects by level, optional program, and termType."""
    for g in range(1, 7):
        level = f"Grade {g}"
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
                INSERT INTO SUBJECT (subjectName, description, level, program, termType)
                VALUES (?, ?, ?, NULL, 'Period')
            """, (name, desc, level))

    for g in range(7, 11):
        level = f"Grade {g}"
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
                INSERT INTO SUBJECT (subjectName, description, level, program, termType)
                VALUES (?, ?, ?, NULL, 'Period')
            """, (name, desc, level))

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
        for program in programs:
            for name, desc in shs_core:
                cursor.execute("""
                    INSERT INTO SUBJECT (subjectName, description, level, program, termType)
                    VALUES (?, ?, ?, ?, 'Period')
                """, (name, desc, level, program))


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
