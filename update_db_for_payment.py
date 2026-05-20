# update_db_for_payment.py
import database

conn = database.get_connection()
cursor = conn.cursor()

print("🔧 Adding missing columns for Payment Module...")

# Add schoolID, gradeLevel, section to ENROLLMENT
for col, col_type in [
    ("schoolID", "TEXT"),
    ("gradeLevel", "TEXT"),
    ("section", "TEXT")
]:
    try:
        cursor.execute(f"ALTER TABLE ENROLLMENT ADD COLUMN {col} {col_type}")
        print(f"✓ Added column: {col}")
    except Exception as e:
        print(f"• {col} already exists or error: {e}")

conn.commit()
conn.close()
print("\n✅ Database updated! You can now use Process Payment.")