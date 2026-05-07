# insert_sample_data.py
import database
import sqlite3

def insert_sample_data():
    conn = database.get_connection()
    cursor = conn.cursor()

    # Sample Staff (Admin)
    cursor.execute('''
    INSERT OR IGNORE INTO STAFF (staffFname, staffLname, position, email, password)
    VALUES ('Vince', 'Oñate', 'Administrator', 'admin', 'admin123')
    ''')

    # Sample Tutor
    cursor.execute('''
    INSERT OR IGNORE INTO TUTOR (tutorFname, tutorLname, tutorEmail, password, specialization)
    VALUES ('Maria', 'Santos', 'tutor', 'tutor123', 'Mathematics')
    ''')

    # Sample Subject
    cursor.execute("INSERT OR IGNORE INTO SUBJECT (subjectName, gradeLevel) VALUES ('Mathematics', 'Grade 7')")
    cursor.execute("INSERT OR IGNORE INTO SUBJECT (subjectName, gradeLevel) VALUES ('Science', 'Grade 7')")

    conn.commit()
    conn.close()
    print("✅ Sample data inserted successfully!")

if __name__ == "__main__":
    insert_sample_data()