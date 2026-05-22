import sqlite3
import random

DB_NAME = "abc_learning_center.db"

first_names = [
    "John Paul", "Mary Grace", "Mark Anthony", "Sarah Jane", "James Patrick",
    "Charles Andrew", "Kristine Joy", "Hannah Mae", "Joshua Miguel", "Patricia Anne",
    "William Robert", "Michael Dave", "Angela Marie", "Robert Jose", "David John",
    "Elizabeth Ann", "Joseph Gabriel", "Jessica Nicole", "Daniel Francis", "Chloe Sophia"
]

last_names = [
    "Santos", "Reyes", "Cruz", "Bautista", "Ocampo",
    "Gonzales", "Aquino", "Smith", "Johnson", "Miller",
    "Davis", "Garcia", "Rodriguez", "Jones", "Williams",
    "Brown", "Wilson", "Taylor", "Anderson", "Thomas"
]

middle_names = [
    "A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "I.", "J.",
    "K.", "L.", "M.", "N.", "P.", "R.", "S.", "T.", "V.", "Y."
]

school_years = [
    "2018-2019", "2019-2020", "2020-2021", "2021-2022",
    "2022-2023", "2023-2024", "2024-2025", "2025-2026"
]

def generate_school_id(school_year: str) -> str:
    yy = school_year[2:4]
    random4 = random.randint(1000, 9999)
    random2 = random.randint(10, 99)
    return f"{yy}-{random4}-{random2}"

def run():
    print("🚀 Running custom American-Filipino Student Generator and Enroller...")
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    student_count = 0
    enrollment_count = 0
    detail_count = 0
    email_idx = 1000  # Starts counter to guarantee unique emails

    try:
        for sy in school_years:
            # 1. Grades 1-10 (sections A, B, C, D)
            for g in range(1, 11):
                grade_lvl = f"Grade {g}"
                level_type = "Elementary" if g <= 6 else "High School"
                term = "Full Year"
                
                for sec in ["A", "B", "C", "D"]:
                    # Enroll 10 students for this grade + section + SY combination
                    for s_idx in range(10):
                        fname = random.choice(first_names)
                        lname = random.choice(last_names)
                        mname = random.choice(middle_names)
                        gender = random.choice(["M", "F"])
                        dob = f"{2026 - g - 6}-0{random.randint(1,9)}-{random.randint(10,28)}"
                        email = f"{fname.lower().replace(' ', '')}.{lname.lower()}{email_idx}@gmail.com"
                        email_idx += 1
                        
                        # Save Student profile
                        cursor.execute("""
                            INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, levelType)
                            VALUES (?, ?, ?, ?, ?, 'Manila, Philippines', '0917' || CAST(random() AS TEXT) || '123', ?, ?)
                        """, (lname, fname, mname, gender, dob, email, level_type))
                        
                        student_id = cursor.lastrowid
                        student_count += 1
                        
                        # Save Parent profile
                        par_name = f"{random.choice(first_names)} {lname}"
                        relationship = "Mother" if gender == "F" else "Father"
                        cursor.execute("""
                            INSERT INTO PARENT (studentID, parName, parContactNo, relationship)
                            VALUES (?, ?, '09181122334', ?)
                        """, (student_id, par_name, relationship))
                        
                        # Generate unique school ID and save Enrollment
                        school_id = generate_school_id(sy)
                        cursor.execute("""
                            INSERT INTO ENROLLMENT (studentID, staffID, schoolID, gradeLevel, section, levelType, term, schoolYear, enrStatus)
                            VALUES (?, 1, ?, ?, ?, ?, ?, ?, 'Active')
                        """, (student_id, school_id, grade_lvl, sec, level_type, term, sy))
                        
                        enrollment_id = cursor.lastrowid
                        enrollment_count += 1
                        
                        # Fetch all subjects for this Grade
                        cursor.execute("SELECT subjectID FROM SUBJECT WHERE gradeLevel = ? AND isActive = 1", (grade_lvl,))
                        subjects = cursor.fetchall()
                        
                        # Insert enrollment details for subjects
                        for sub in subjects:
                            cursor.execute("INSERT INTO DETAIL (enrollmentID, subjectID) VALUES (?, ?)", (enrollment_id, sub[0]))
                            detail_count += 1

            # 2. Grades 11-12 (STEM-A, ABM-A, HUMSS-A)
            for g in [11, 12]:
                grade_lvl = f"Grade {g}"
                level_type = "Senior High School"
                term = "1st Semester"
                
                for sec in ["STEM-A", "ABM-A", "HUMSS-A"]:
                    strand = "STEM" if "STEM" in sec else "ABM" if "ABM" in sec else "HUMSS"
                    
                    # Enroll 10 students for this grade + section + SY combination
                    for s_idx in range(10):
                        fname = random.choice(first_names)
                        lname = random.choice(last_names)
                        mname = random.choice(middle_names)
                        gender = random.choice(["M", "F"])
                        dob = f"{2026 - g - 6}-0{random.randint(1,9)}-{random.randint(10,28)}"
                        email = f"{fname.lower().replace(' ', '')}.{lname.lower()}{email_idx}@gmail.com"
                        email_idx += 1
                        
                        # Save Student profile
                        cursor.execute("""
                            INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, levelType)
                            VALUES (?, ?, ?, ?, ?, 'Cebu City, Philippines', '0917' || CAST(random() AS TEXT) || '123', ?, ?)
                        """, (lname, fname, mname, gender, dob, email, level_type))
                        
                        student_id = cursor.lastrowid
                        student_count += 1
                        
                        # Save Parent profile
                        par_name = f"{random.choice(first_names)} {lname}"
                        relationship = "Mother" if gender == "F" else "Father"
                        cursor.execute("""
                            INSERT INTO PARENT (studentID, parName, parContactNo, relationship)
                            VALUES (?, ?, '09181122334', ?)
                        """, (student_id, par_name, relationship))
                        
                        # Generate unique school ID and save Enrollment
                        school_id = generate_school_id(sy)
                        cursor.execute("""
                            INSERT INTO ENROLLMENT (studentID, staffID, schoolID, gradeLevel, section, levelType, term, schoolYear, enrStatus)
                            VALUES (?, 1, ?, ?, ?, ?, ?, ?, 'Active')
                        """, (student_id, school_id, grade_lvl, sec, level_type, term, sy))
                        
                        enrollment_id = cursor.lastrowid
                        enrollment_count += 1
                        
                        # Fetch all subjects for Grade 11-12 matching Grade, Strand, and 1st Semester
                        cursor.execute("""
                            SELECT subjectID FROM SUBJECT 
                            WHERE gradeLevel = ? AND strand = ? AND semester = 1 AND isActive = 1
                        """, (grade_lvl, strand))
                        subjects = cursor.fetchall()
                        
                        # Insert enrollment details for subjects
                        for sub in subjects:
                            cursor.execute("INSERT INTO DETAIL (enrollmentID, subjectID) VALUES (?, ?)", (enrollment_id, sub[0]))
                            detail_count += 1

        conn.commit()
        print(f"\n🎉 SUCCESS: Data Generation Complete!")
        print(f"👥 Total Students generated and saved: {student_count}")
        print(f"📄 Total Enrollments linked and saved: {enrollment_count}")
        print(f"📚 Total Subject Enrollments (DETAIL entries): {detail_count}")

    except Exception as e:
        conn.rollback()
        print(f"❌ Error during student generation: {e}")
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()

if __name__ == '__main__':
    run()
