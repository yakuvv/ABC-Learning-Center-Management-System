"""Insert 12 sample students (Grade 1–12) for demo / testing."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection, generate_learner_id

SAMPLES = [
    ("Reyes", "Andrea", "M.", "F", "2019-06-15", "123 Sampaguita St, Quezon City", "09171234001", "andrea.reyes.g1@email.com", "Quezon City Elementary School", "Grade 1", "Maria Reyes", "09171234002", "Mother"),
    ("Santos", "Miguel", "L.", "M", "2018-03-22", "45 Narra Ave, Makati", "09171234003", "miguel.santos.g2@email.com", "Makati Central School", "Grade 2", "Liza Santos", "09171234004", "Mother"),
    ("Garcia", "Sophia", "R.", "F", "2017-11-08", "78 Molave St, Pasig", "09171234005", "sophia.garcia.g3@email.com", "Pasig Elementary School", "Grade 3", "Rosa Garcia", "09171234006", "Mother"),
    ("Cruz", "Ethan", "D.", "M", "2016-01-30", "12 Acacia Rd, Mandaluyong", "09171234007", "ethan.cruz.g4@email.com", "Mandaluyong Elementary School", "Grade 4", "Diana Cruz", "09171234008", "Mother"),
    ("Lopez", "Isabella", "J.", "F", "2015-09-12", "56 Ipil St, Taguig", "09171234009", "isabella.lopez.g5@email.com", "Taguig Integrated School", "Grade 5", "Jose Lopez", "09171234010", "Father"),
    ("Torres", "Noah", "P.", "M", "2014-07-25", "90 Yakal St, Paranaque", "09171234011", "noah.torres.g6@email.com", "Paranaque Elementary School", "Grade 6", "Patricia Torres", "09171234012", "Mother"),
    ("Mendoza", "Chloe", "A.", "F", "2013-04-18", "34 Mahogany St, Las Pinas", "09171234013", "chloe.mendoza.g7@email.com", "Las Pinas National High School", "Grade 7", "Ana Mendoza", "09171234014", "Mother"),
    ("Ramos", "Lucas", "G.", "M", "2012-12-05", "67 Palm St, Muntinlupa", "09171234015", "lucas.ramos.g8@email.com", "Muntinlupa National High School", "Grade 8", "Grace Ramos", "09171234016", "Mother"),
    ("Flores", "Emma", "V.", "F", "2011-08-20", "21 Bamboo St, Caloocan", "09171234017", "emma.flores.g9@email.com", "Caloocan High School", "Grade 9", "Victor Flores", "09171234018", "Father"),
    ("Bautista", "James", "N.", "M", "2010-05-14", "88 Cedar St, Marikina", "09171234019", "james.bautista.g10@email.com", "Marikina Science High School", "Grade 10", "Nora Bautista", "09171234020", "Mother"),
    ("Aquino", "Olivia", "S.", "F", "2009-02-28", "15 Molave Ext, Pasay", "09171234021", "olivia.aquino.g11@email.com", "Pasay City National High School", "Grade 11", "Susan Aquino", "09171234022", "Mother"),
    ("Villanueva", "Daniel", "K.", "M", "2008-10-10", "42 Orchid St, Manila", "09171234023", "daniel.villanueva.g12@email.com", "Manila Science High School", "Grade 12", "Karen Villanueva", "09171234024", "Mother"),
]


def seed():
    conn = get_connection()
    cur = conn.cursor()
    added = 0
    for row in SAMPLES:
        lname, fname, mname, gender, dob, address, contact, email, school, grade, par_name, par_contact, relation = row
        exists = cur.execute("SELECT 1 FROM STUDENT WHERE studEmail = ?", (email,)).fetchone()
        if exists:
            continue
        learner_id = generate_learner_id()
        cur.execute("""
            INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address,
                studContactNo, studEmail, currentSchool, gradeLevel, learnerID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lname, fname, mname, gender, dob, address, contact, email, school, grade, learner_id))
        sid = cur.lastrowid
        cur.execute("""
            INSERT INTO PARENT (studentID, parName, parContactNo, relationship)
            VALUES (?, ?, ?, ?)
        """, (sid, par_name, par_contact, relation))
        added += 1
    conn.commit()
    conn.close()
    print(f"Added {added} student(s) (Grade 1–12).")


if __name__ == "__main__":
    seed()
