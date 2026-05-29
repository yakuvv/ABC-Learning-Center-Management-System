import sqlite3
import os

def run():
    # Dynamically find the database file in the parent directory
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "abc_learning_center.db")
    print(f"Connecting to database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    print("Deleting student data from database tables...")
    tables_to_clear = [
        "RECEIPT", "PAYMENT", "GRADE", "ATTENDANCE", 
        "REGISTRATION_DETAIL", "REGISTRATION", "PARENT", "STUDENT"
    ]
    for table in tables_to_clear:
        cursor.execute(f"DELETE FROM {table}")
        cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        
    print("Seeding fresh 12 students (Grades 1-12) with parents...")
    students_data = [
        ("Miller", "Liam", "J.", "M", "2019-05-10", "123 Maple St, QC", "0917-111-2222", "liam.miller@student.com", "Grade 1", 
         "Sarah Miller", "0917-999-8888", "sarah.miller@email.com", "Mother"),
         
        ("Davis", "Sophia", "M.", "F", "2018-08-15", "456 Oak Rd, Pasig", "0917-222-3333", "sophia.davis@student.com", "Grade 2", 
         "John Davis", "0917-888-7777", "john.davis@email.com", "Father"),
         
        ("Anderson", "Noah", "K.", "M", "2017-11-20", "789 Pine Ave, Makati", "0917-333-4444", "noah.anderson@student.com", "Grade 3", 
         "Robert Anderson", "0917-777-6666", "robert.anderson@email.com", "Father"),
         
        ("Taylor", "Isabella", "L.", "F", "2016-04-05", "12 Cedar Lane, Taguig", "0917-444-5555", "isabella.taylor@student.com", "Grade 4", 
         "Mary Taylor", "0917-666-5555", "mary.taylor@email.com", "Mother"),
         
        ("Thomas", "Ethan", "N.", "M", "2015-09-30", "56 Elm Blvd, Mandaluyong", "0917-555-6666", "ethan.thomas@student.com", "Grade 5", 
         "James Thomas", "0917-555-4444", "james.thomas@email.com", "Father"),
         
        ("White", "Mia", "P.", "F", "2014-02-14", "78 Birch Dr, San Juan", "0917-666-7777", "mia.white@student.com", "Grade 6", 
         "Linda White", "0917-444-3333", "linda.white@email.com", "Mother"),
         
        ("Harris", "Jacob", "R.", "M", "2013-07-25", "34 Redwood Rd, Manila", "0917-777-8888", "jacob.harris@student.com", "Grade 7", 
         "William Harris", "0917-333-2222", "william.harris@email.com", "Father"),
         
        ("Martin", "Olivia", "S.", "F", "2012-12-12", "90 Cypress Way, Alabang", "0917-888-9999", "olivia.martin@student.com", "Grade 8", 
         "Patricia Martin", "0917-222-1111", "patricia.martin@email.com", "Mother"),
         
        ("Clark", "Lucas", "T.", "M", "2011-03-08", "15 Magnolia Ave, Caloocan", "0917-999-0000", "lucas.clark@student.com", "Grade 9", 
         "Richard Clark", "0917-111-0000", "richard.clark@email.com", "Father"),
         
        ("Rodriguez", "Emma", "V.", "F", "2010-06-18", "67 Willow St, Marikina", "0917-000-1111", "emma.rodriguez@student.com", "Grade 10", 
         "Elizabeth Rodriguez", "0917-000-9999", "elizabeth.rodriguez@email.com", "Mother"),
         
        ("Lewis", "Alexander", "W.", "M", "2009-10-05", "88 Spruce Ct, Las Piñas", "0917-123-1234", "alexander.lewis@student.com", "Grade 11", 
         "Joseph Lewis", "0917-987-9876", "joseph.lewis@email.com", "Father"),
         
        ("Walker", "Chloe", "Z.", "F", "2008-01-22", "42 Chestnut St, Parañaque", "0917-234-2345", "chloe.walker@student.com", "Grade 12", 
         "Susan Walker", "0917-876-8765", "susan.walker@email.com", "Mother")
     ]
     
     for (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, level,
          parName, parContactNo, parEmail, relationship) in students_data:
         cursor.execute("""
             INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, level)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
         """, (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, level))
         student_id = cursor.lastrowid
         
         cursor.execute("""
             INSERT INTO PARENT (studentID, parName, parContactNo, parEmail, relationship)
             VALUES (?, ?, ?, ?, ?)
         """, (student_id, parName, parContactNo, parEmail, relationship))
         
    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON")
    conn.close()
    print("Database data successfully cleared and reset with 12 fresh students and parents!")

if __name__ == "__main__":
    run()
