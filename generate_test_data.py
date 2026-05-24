import sqlite3
import random

from database import generate_learner_id, DB_NAME

first_names = ["John Paul", "Mary Grace", "Mark Anthony", "Sarah Jane", "James Patrick"]
last_names = ["Santos", "Reyes", "Cruz", "Bautista", "Ocampo"]
terms = ["1st Period", "2nd Period"]


def run():
    print("Running test data generator...")
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    email_idx = 1000
    student_count = 0

    try:
        cursor.execute("SELECT staffID FROM STAFF LIMIT 1")
        staff_id = cursor.fetchone()[0]

        for term in terms:
            for g in range(7, 9):
                level = f"Grade {g}"
                for group_name in ["A", "B"]:
                    for _ in range(5):
                        fname = random.choice(first_names)
                        lname = random.choice(last_names)
                        email = f"{fname.lower().replace(' ', '')}.{lname.lower()}{email_idx}@test.com"
                        email_idx += 1

                        cursor.execute("""
                            INSERT INTO STUDENT (studLname, studFname, gender, dob, address, level)
                            VALUES (?, ?, 'M', '2010-05-15', 'Manila', 'Unassigned')
                        """, (lname, fname))
                        student_id = cursor.lastrowid
                        student_count += 1

                        cursor.execute("""
                            INSERT INTO PARENT (studentID, parName, relationship)
                            VALUES (?, ?, 'Mother')
                        """, (student_id, f"Parent {lname}"))

                        learner_id = generate_learner_id(term)
                        cursor.execute("""
                            INSERT INTO REGISTRATION (studentID, staffID, learnerID, level, groupName, term, regStatus)
                            VALUES (?, ?, ?, ?, ?, ?, 'Active')
                        """, (student_id, staff_id, learner_id, level, group_name, term))
                        reg_id = cursor.lastrowid

                        cursor.execute("UPDATE STUDENT SET level=? WHERE studentID=?", (level, student_id))

                        cursor.execute("SELECT subjectID FROM SUBJECT WHERE level=? AND (program IS NULL OR program='') LIMIT 3", (level,))
                        for (sub_id,) in cursor.fetchall():
                            cursor.execute("INSERT INTO REGISTRATION_DETAIL (registrationID, subjectID) VALUES (?, ?)", (reg_id, sub_id))

        conn.commit()
        print(f"Generated {student_count} students with registrations.")
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.close()


if __name__ == "__main__":
    run()
