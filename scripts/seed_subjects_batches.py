import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

conn = get_connection()
cur = conn.cursor()

# 1. Clear existing SUBJECT and BATCH tables
print("Clearing SUBJECT and BATCH tables...")
cur.execute("PRAGMA foreign_keys = OFF")
cur.execute("DELETE FROM BATCH")
cur.execute("DELETE FROM SUBJECT")
cur.execute("DELETE FROM sqlite_sequence WHERE name='BATCH'")
cur.execute("DELETE FROM sqlite_sequence WHERE name='SUBJECT'")
cur.execute("PRAGMA foreign_keys = ON")
conn.commit()

# 2. Insert new list of subjects
print("Inserting new subjects...")

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
        cur.execute("""
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
        cur.execute("""
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
        cur.execute("""
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
        cur.execute("""
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
        cur.execute("""
            INSERT INTO SUBJECT (subjCode, subjectName, level, pricePerTerm)
            VALUES (?, ?, ?, ?)
        """, (subj_code, name, level, price))

conn.commit()
subject_count = cur.execute("SELECT COUNT(*) FROM SUBJECT").fetchone()[0]
print(f"  Inserted {subject_count} subjects.")

# 3. Create the recommended Batch records (Batch A, B, C, D)
print("Seeding batches (A, B, C, D) for all subjects...")

tutor_row = cur.execute("SELECT tutorID FROM TUTOR ORDER BY tutorID LIMIT 1").fetchone()
tutor_id = tutor_row[0] if tutor_row else None

subjects = cur.execute("SELECT subjectID, level FROM SUBJECT WHERE isActive=1 ORDER BY subjectID").fetchall()
for subject_id, level in subjects:
    for label, sched in [
        ("A", "Saturday 9:00 AM – 11:00 AM"),
        ("B", "Saturday 1:00 PM – 3:00 PM"),
        ("C", "Sunday 9:00 AM – 11:00 AM"),
        ("D", "Sunday 1:00 PM – 3:00 PM"),
    ]:
        cur.execute("""
            INSERT INTO BATCH (subjectID, level, schedule, batchLabel, tutorID, capacity, isActive)
            VALUES (?, ?, ?, ?, ?, 15, 1)
        """, (subject_id, level, sched, label, tutor_id))

conn.commit()
batch_count = cur.execute("SELECT COUNT(*) FROM BATCH").fetchone()[0]
print(f"  Inserted {batch_count} batches.")

conn.close()
print("\nDone! Database successfully cleared and updated with new subjects, pricing, and batches.")
