# reset_database.py
import database

print("WARNING: This will DELETE ALL data in your database!")

confirm = input("Type 'YES' to continue and reset database: ")

if confirm == "YES":
    conn = database.get_connection()
    cursor = conn.cursor()

    # Delete data in correct order (respect foreign keys)
    cursor.execute("DELETE FROM RECEIPT")
    cursor.execute("DELETE FROM PAYMENT")
    cursor.execute("DELETE FROM GRADE")
    cursor.execute("DELETE FROM ATTENDANCE")
    cursor.execute("DELETE FROM DETAIL")
    cursor.execute("DELETE FROM ENROLLMENT")
    cursor.execute("DELETE FROM PARENT")
    cursor.execute("DELETE FROM STUDENT")
    # Don't delete STAFF and TUTOR (you need login accounts)

    conn.commit()
    conn.close()
    print("✅ Database has been reset successfully! All student data cleared.")
else:
    print("Cancelled.")