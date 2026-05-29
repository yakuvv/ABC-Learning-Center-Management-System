"""Create sample Grade 1 class schedules (batches) for enrollment testing."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_connection

BATCHES = [
    ("Mathematics", "Saturday", "9:00 AM", "Batch A", 12, 2000),
    ("English", "Saturday", "10:30 AM", "Batch A", 12, 1800),
    ("Filipino", "Sunday", "9:00 AM", "Batch A", 10, 1800),
    ("Science", "Sunday", "10:30 AM", "Batch A", 10, 1900),
]


def seed():
    conn = get_connection()
    cur = conn.cursor()
    tutor = cur.execute("SELECT tutorID FROM TUTOR LIMIT 1").fetchone()
    if not tutor:
        print("No tutor found. Run migrate_and_seed.py first.")
        conn.close()
        return
    tid = tutor["tutorID"]
    added = 0
    for subj_name, day, time, bname, slots, fee in BATCHES:
        sub = cur.execute(
            "SELECT subjectID FROM SUBJECT WHERE subjectName = ? AND gradeLevel = 'Grade 1' LIMIT 1",
            (subj_name,),
        ).fetchone()
        if not sub:
            print(f"Skip {subj_name}: subject not found")
            continue
        try:
            cur.execute("""
                INSERT INTO BATCH (subjectID, gradeLevel, scheduleDay, scheduleTime, batchName,
                                   tutorID, maxSlots, feeAmount)
                VALUES (?, 'Grade 1', ?, ?, ?, ?, ?, ?)
            """, (sub["subjectID"], day, time, bname, tid, slots, fee))
            added += 1
        except Exception:
            pass
    conn.commit()
    conn.close()
    print(f"Grade 1 batches ready ({added} new).")


if __name__ == "__main__":
    seed()
