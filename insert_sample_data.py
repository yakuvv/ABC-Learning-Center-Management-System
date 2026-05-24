# insert_sample_data.py
import database


def insert_sample_data():
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR IGNORE INTO STAFF (staffFname, staffLname, position, email, password)
    VALUES ('Vince', 'Oñate', 'Administrator', 'admin', 'admin123')
    ''')

    cursor.execute('''
    INSERT OR IGNORE INTO TUTOR (tutorFname, tutorLname, tutorEmail, password, specialization)
    VALUES ('Maria', 'Santos', 'tutor', 'tutor123', 'Mathematics')
    ''')

    cursor.execute("""
        INSERT OR IGNORE INTO SUBJECT (subjectName, description, level, program, termType)
        VALUES ('Mathematics', 'High School Mathematics', 'Grade 7', NULL, 'Period')
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO SUBJECT (subjectName, description, level, program, termType)
        VALUES ('Science', 'General Science', 'Grade 7', NULL, 'Period')
    """)

    conn.commit()
    conn.close()
    print("Sample data inserted successfully!")


if __name__ == "__main__":
    insert_sample_data()
