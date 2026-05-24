"""Legacy bulk generator — run migrate_and_seed.py first, then this script."""
import sqlite3
import random

from database import generate_learner_id, DB_NAME


def run():
    print("Generating clean sample registrations...")
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()

    for table in ["RECEIPT", "PAYMENT", "GRADE", "ATTENDANCE", "REGISTRATION_DETAIL", "REGISTRATION", "PARENT", "STUDENT"]:
        cursor.execute(f"DELETE FROM {table}")

    cursor.execute("SELECT staffID FROM STAFF LIMIT 1")
    staff_id = cursor.fetchone()[0]
    term = "1st Period"

    for i in range(1, 51):
        cursor.execute("""
            INSERT INTO STUDENT (studLname, studFname, gender, dob, level)
            VALUES (?, ?, 'F', '2011-03-10', 'Unassigned')
        """, (f"Student{i}", f"Test{i}"))
        sid = cursor.lastrowid
        level = f"Grade {((i - 1) % 6) + 1}"
        group_name = ["A", "B", "C", "D"][(i - 1) % 4]
        learner_id = generate_learner_id(term)
        cursor.execute("""
            INSERT INTO REGISTRATION (studentID, staffID, learnerID, level, groupName, term, regStatus)
            VALUES (?, ?, ?, ?, ?, ?, 'Active')
        """, (sid, staff_id, learner_id, level, group_name, term))
        reg_id = cursor.lastrowid
        cursor.execute("UPDATE STUDENT SET level=? WHERE studentID=?", (level, sid))
        cursor.execute("SELECT subjectID FROM SUBJECT WHERE level=? LIMIT 2", (level,))
        for (sub_id,) in cursor.fetchall():
            cursor.execute("INSERT INTO REGISTRATION_DETAIL (registrationID, subjectID) VALUES (?, ?)", (reg_id, sub_id))

    conn.commit()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.close()
    print("Done: 50 students with registrations.")


if __name__ == "__main__":
    run()
