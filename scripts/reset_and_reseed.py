import os, sqlite3
def run():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'abc_learning_center.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('PRAGMA foreign_keys = OFF')
    tables_to_clear = ['RECEIPT', 'PAYMENT', 'GRADE', 'ATTENDANCE', 'REGISTRATION_DETAIL', 'REGISTRATION', 'PARENT', 'STUDENT']
    for table in tables_to_clear:
        cursor.execute(f'DELETE FROM {table}')
        cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}"')
    students_data = [
        ('Dela Cruz', 'John Miguel', 'A.', 'M', '2018-05-10', '123 Mabini St, Manila', '0917-123-4567', None, 'Grade 1', 'Maria Dela Cruz', '0917-987-6543', None, 'Mother'),
        ('Reyes', 'Sophia Marie', 'B.', 'F', '2019-01-15', '456 Rizal Ave, QC', None, 'sophia.reyes@email.com', 'Grade 1', 'Jose Reyes', None, 'jose.reyes@email.com', 'Father'),
        ('Smith', 'Alexander Jose', 'C.', 'M', '2018-11-20', '789 Burgos St, Makati', '0917-987-6543', None, 'Grade 2', 'Robert Smith', '0917-111-2222', None, 'Father'),
        ('Garcia', 'Isabella Grace', 'D.', 'F', '2017-08-05', '321 BGC, Taguig', None, 'isabella.garcia@email.com', 'Grade 2', 'Linda Garcia', None, 'linda.garcia@email.com', 'Mother'),
        ('Mendoza', 'Ethan Gabriel', 'E.', 'M', '2017-02-14', '654 EDSA, Mandaluyong', '0918-111-2222', None, 'Grade 3', 'Antonio Mendoza', '0918-999-8888', None, 'Father'),
        ('Jones', 'Mia Corazon', 'F.', 'F', '2016-09-30', '987 Taft Ave, Pasay', None, 'mia.jones@email.com', 'Grade 3', 'Sarah Jones', None, 'sarah.jones@email.com', 'Mother'),
        ('Bautista', 'Jacob Elias', 'G.', 'M', '2016-04-12', '159 Ortigas Center, Pasig', '0919-333-4444', None, 'Grade 4', 'William Bautista', '0919-777-6666', None, 'Father'),
        ('Williams', 'Olivia Rosario', 'H.', 'F', '2015-12-25', '753 Shaw Blvd, San Juan', None, 'olivia.williams@email.com', 'Grade 4', 'Patricia Williams', None, 'patricia.williams@email.com', 'Mother'),
        ('Cruz', 'Lucas Mateo', 'I.', 'M', '2015-06-18', '852 Araneta Ave, Marikina', '0920-555-6666', None, 'Grade 5', 'Richard Cruz', '0920-123-4567', None, 'Father'),
        ('Brown', 'Emma Luz', 'J.', 'F', '2014-10-05', '369 Katipunan Ave, QC', None, 'emma.brown@email.com', 'Grade 5', 'Elizabeth Brown', None, 'elizabeth.brown@email.com', 'Mother'),
        ('Santos', 'Matthew Luis', 'K.', 'M', '2014-03-22', '147 Legarda St, Manila', '0921-777-8888', None, 'Grade 6', 'Joseph Santos', '0921-987-6543', None, 'Father'),
        ('Miller', 'Chloe Marisol', 'L.', 'F', '2013-07-08', '258 Commonwealth Ave, QC', None, 'chloe.miller@email.com', 'Grade 6', 'Susan Miller', None, 'susan.miller@email.com', 'Mother'),
        ('Torres', 'William Carlos', 'M.', 'M', '2013-01-30', '369 Espana Blvd, Manila', '0922-999-0000', None, 'Grade 7', 'Thomas Torres', '0922-111-2222', None, 'Father'),
        ('Davis', 'Ava Consuelo', 'N.', 'F', '2012-08-14', '741 Roxas Blvd, Pasay', None, 'ava.davis@email.com', 'Grade 8', 'Margaret Davis', None, 'margaret.davis@email.com', 'Mother'),
        ('Gonzales', 'James Rafael', 'O.', 'M', '2012-02-28', '852 Alabang, Muntinlupa', '0923-123-1111', None, 'Grade 9', 'Charles Gonzales', '0923-999-8888', None, 'Father'),
        ('Wilson', 'Sofia Carmen', 'P.', 'F', '2011-09-17', '963 Ayala Ave, Makati', None, 'sofia.wilson@email.com', 'Grade 10', 'Jessica Wilson', None, 'jessica.wilson@email.com', 'Mother'),
        ('Flores', 'Daniel Antonio', 'Q.', 'M', '2010-04-05', '159 Macapagal Blvd, Pasay', '0924-222-3333', None, 'Grade 11', 'Christopher Flores', '0924-777-6666', None, 'Father'),
        ('Moore', 'Victoria Paz', 'R.', 'F', '2009-11-22', '753 Pioneer St, Mandaluyong', None, 'victoria.moore@email.com', 'Grade 11', 'Sarah Moore', None, 'sarah.moore@email.com', 'Mother'),
        ('Villanueva', 'Sebastian Cruz', 'S.', 'M', '2009-05-10', '357 C5 Road, Taguig', '0925-444-5555', None, 'Grade 12', 'Daniel Villanueva', '0925-333-4444', None, 'Father'),
        ('Taylor', 'Camila Joy', 'T.', 'F', '2008-12-01', '456 NLEX, Valenzuela', None, 'camila.taylor@email.com', 'Grade 12', 'Nancy Taylor', None, 'nancy.taylor@email.com', 'Mother'),
    ]
    for (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, level, parName, parContactNo, parEmail, relationship) in students_data:
        cursor.execute("""INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactInfo, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (studLname, studFname, studMname, gender, dob, address, studContactNo or studEmail or '', level))
        student_id = cursor.lastrowid
        cursor.execute("""INSERT INTO PARENT (studentID, parName, parContactInfo, relationship)
            VALUES (?, ?, ?, ?)""", (student_id, parName, parContactNo or parEmail or '', relationship))
    conn.commit()
    cursor.execute('PRAGMA foreign_keys = ON')
    conn.close()
    print('Database data successfully cleared and reset with 20 fresh students and parents!')
if __name__ == '__main__':
    run()
