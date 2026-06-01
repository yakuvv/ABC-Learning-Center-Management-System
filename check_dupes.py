import sqlite3

conn = sqlite3.connect('abc_learning_center.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== DUPLICATE STUDENT NAMES ===")
cur.execute("""
    SELECT studFname, studLname, COUNT(*) as cnt
    FROM STUDENT
    GROUP BY LOWER(studFname), LOWER(studLname)
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC
""")
dupes = cur.fetchall()
if dupes:
    for d in dupes:
        print(f"  {d['studFname']} {d['studLname']} -- appears {d['cnt']} times")
else:
    print("  No duplicate names found.")

print()
print("=== ALL STUDENTS (for reference) ===")
cur.execute("SELECT studentID, studFname, studMname, studLname, level FROM STUDENT ORDER BY studLname, studFname")
students = cur.fetchall()
for s in students:
    mname = s['studMname'] or ''
    print(f"  ID {s['studentID']:3} | {s['studLname']}, {s['studFname']} {mname} | {s['level']}")

print(f"\nTotal students: {len(students)}")
conn.close()
