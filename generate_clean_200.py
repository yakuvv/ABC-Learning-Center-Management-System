# generate_clean_200.py
import sqlite3
import random
import os
import shutil

DB_NAME = "abc_learning_center.db"
BACKUP_NAME = "abc_learning_center_backup.db"

first_names = [
    "John Paul", "Mary Grace", "Mark Anthony", "Sarah Jane", "James Patrick",
    "Charles Andrew", "Kristine Joy", "Hannah Mae", "Joshua Miguel", "Patricia Anne",
    "William Robert", "Michael Dave", "Angela Marie", "Robert Jose", "David John",
    "Elizabeth Ann", "Joseph Gabriel", "Jessica Nicole", "Daniel Francis", "Chloe Sophia",
    "Liam Asher", "Sophia Isabella", "Noah Gabriel", "Olivia Grace", "Ethan Jude",
    "Ava Marie", "Lucas Gabriel", "Mia Celestia", "Mason Alexander", "Isabella Rose",
    "Benjamin Cruz", "Charlotte Anne", "Oliver James", "Amelia Joy", "Jacob Santos",
    "Sofia Beatrice", "William Henry", "Emily Grace", "James Alfonso", "Harper Jade"
]

last_names = [
    "Santos", "Reyes", "Cruz", "Bautista", "Ocampo",
    "Gonzales", "Aquino", "Smith", "Johnson", "Miller",
    "Davis", "Garcia", "Rodriguez", "Jones", "Williams",
    "Brown", "Wilson", "Taylor", "Anderson", "Thomas",
    "Mercado", "Del Rosario", "Salazar", "Villanueva", "Castro"
]

middle_names = [
    "A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "J.",
    "K.", "L.", "M.", "N.", "P.", "R.", "S.", "T.", "V.", "Y."
]

def generate_school_id(idx: int) -> str:
    # Generates a sequential but realistic looking school ID: 25-7000-XX
    return f"25-7{idx:03d}-95"

def run():
    print("🧹 Wiping existing student data from database...")
    
    if not os.path.exists(DB_NAME):
        print(f"Error: {DB_NAME} not found!")
        return

    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    try:
        # Wipe tables
        cursor.execute("DELETE FROM RECEIPT")
        cursor.execute("DELETE FROM PAYMENT")
        cursor.execute("DELETE FROM GRADE")
        cursor.execute("DELETE FROM ATTENDANCE")
        cursor.execute("DELETE FROM DETAIL")
        cursor.execute("DELETE FROM ENROLLMENT")
        cursor.execute("DELETE FROM PARENT")
        cursor.execute("DELETE FROM STUDENT")
        conn.commit()
        print("✓ All old student, enrollment, parent, grades, payment, and attendance records cleared!")

        student_count = 0
        enrollment_count = 0
        detail_count = 0
        email_idx = 1000
        school_year = "2025-2026"

        # We will generate exactly 200 enrolled students.
        # Distribution:
        # - Grades 1 to 10: 10 grades * 14 students each = 140 students.
        # - Grades 11 and 12: 2 grades * 30 students each = 60 students.
        # Total = 200 students.

        # 1. Grades 1-10
        for g in range(1, 11):
            grade_lvl = f"Grade {g}"
            level_type = "Elementary" if g <= 6 else "High School"
            term = "Full Year"
            
            # 14 students per grade level, distributed across sections:
            # A: 4 students, B: 3 students, C: 3 students, D: 4 students.
            sections_list = ["A", "A", "A", "A", "B", "B", "B", "C", "C", "C", "D", "D", "D", "D"]
            for sec in sections_list:
                fname = random.choice(first_names)
                lname = random.choice(last_names)
                mname = random.choice(middle_names)
                gender = random.choice(["M", "F"])
                dob = f"{2026 - g - 6}-0{random.randint(1,9)}-{random.randint(10,28)}"
                email = f"{fname.lower().replace(' ', '')}.{lname.lower()}{email_idx}@gmail.com"
                email_idx += 1
                
                # Insert Student
                cursor.execute("""
                    INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, levelType)
                    VALUES (?, ?, ?, ?, ?, 'Manila, Philippines', '0917' || CAST(random() AS TEXT) || '123', ?, ?)
                """, (lname, fname, mname, gender, dob, email, level_type))
                student_id = cursor.lastrowid
                student_count += 1
                
                # Insert Parent
                par_name = f"{random.choice(first_names)} {lname}"
                relationship = "Mother" if gender == "F" else "Father"
                cursor.execute("""
                    INSERT INTO PARENT (studentID, parName, parContactNo, relationship)
                    VALUES (?, ?, '09181122334', ?)
                """, (student_id, par_name, relationship))
                
                # Generate unique sequential School ID (1 to 200)
                school_id = generate_school_id(student_count)
                cursor.execute("""
                    INSERT INTO ENROLLMENT (studentID, staffID, schoolID, gradeLevel, section, levelType, term, schoolYear, enrStatus)
                    VALUES (?, 1, ?, ?, ?, ?, ?, ?, 'Active')
                """, (student_id, school_id, grade_lvl, sec, level_type, term, school_year))
                enrollment_id = cursor.lastrowid
                enrollment_count += 1
                
                # Fetch all subjects for this Grade
                cursor.execute("SELECT subjectID FROM SUBJECT WHERE gradeLevel = ? AND isActive = 1", (grade_lvl,))
                subjects = cursor.fetchall()
                for sub in subjects:
                    cursor.execute("INSERT INTO DETAIL (enrollmentID, subjectID) VALUES (?, ?)", (enrollment_id, sub[0]))
                    detail_count += 1

        # 2. Grades 11-12 (STEM-A, ABM-A, HUMSS-A)
        for g in [11, 12]:
            grade_lvl = f"Grade {g}"
            level_type = "Senior High School"
            term = "1st Semester"
            
            # 30 students per grade level:
            # STEM-A: 10 students, ABM-A: 10 students, HUMSS-A: 10 students.
            for sec in ["STEM-A", "ABM-A", "HUMSS-A"]:
                strand = "STEM" if "STEM" in sec else "ABM" if "ABM" in sec else "HUMSS"
                
                for s_idx in range(10):
                    fname = random.choice(first_names)
                    lname = random.choice(last_names)
                    mname = random.choice(middle_names)
                    gender = random.choice(["M", "F"])
                    dob = f"{2026 - g - 6}-0{random.randint(1,9)}-{random.randint(10,28)}"
                    email = f"{fname.lower().replace(' ', '')}.{lname.lower()}{email_idx}@gmail.com"
                    email_idx += 1
                    
                    # Insert Student
                    cursor.execute("""
                        INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, levelType)
                        VALUES (?, ?, ?, ?, ?, 'Manila, Philippines', '0917' || CAST(random() AS TEXT) || '123', ?, ?)
                    """, (lname, fname, mname, gender, dob, email, level_type))
                    student_id = cursor.lastrowid
                    student_count += 1
                    
                    # Insert Parent
                    par_name = f"{random.choice(first_names)} {lname}"
                    relationship = "Mother" if gender == "F" else "Father"
                    cursor.execute("""
                        INSERT INTO PARENT (studentID, parName, parContactNo, relationship)
                        VALUES (?, ?, '09181122334', ?)
                    """, (student_id, par_name, relationship))
                    
                    # Generate unique School ID (1 to 200)
                    school_id = generate_school_id(student_count)
                    cursor.execute("""
                        INSERT INTO ENROLLMENT (studentID, staffID, schoolID, gradeLevel, section, levelType, term, schoolYear, enrStatus)
                        VALUES (?, 1, ?, ?, ?, ?, ?, ?, 'Active')
                    """, (student_id, school_id, grade_lvl, sec, level_type, term, school_year))
                    enrollment_id = cursor.lastrowid
                    enrollment_count += 1
                    
                    # Fetch all subjects for SHS matching gradeLevel, strand, and semester=1
                    cursor.execute("""
                        SELECT subjectID FROM SUBJECT 
                        WHERE gradeLevel = ? AND strand = ? AND semester = 1 AND isActive = 1
                    """, (grade_lvl, strand))
                    subjects = cursor.fetchall()
                    for sub in subjects:
                        cursor.execute("INSERT INTO DETAIL (enrollmentID, subjectID) VALUES (?, ?)", (enrollment_id, sub[0]))
                        detail_count += 1

        conn.commit()
        print(f"\n🎉 SUCCESS: Data Generation Complete!")
        print(f"👥 Total Students generated and enrolled: {student_count}")
        print(f"📄 Total Enrollments linked: {enrollment_count}")
        print(f"📚 Total Subject Enrollments (DETAIL entries): {detail_count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error during student generation: {e}")
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

    # Copy to backup database to keep them synced
    print(f"📦 Syncing clean database to backup '{BACKUP_NAME}'...")
    shutil.copyfile(DB_NAME, BACKUP_NAME)
    print("✓ Backup synced successfully!")

if __name__ == '__main__':
    run()
