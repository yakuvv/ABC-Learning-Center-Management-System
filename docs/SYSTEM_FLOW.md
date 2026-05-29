# ABC Learning Center — How the System Works (Simple Guide)

**Who uses the system:** Admin/Staff and Tutors only.  
**Who does NOT log in:** Students and parents (they fill paper forms at the center).

---

## Real-world → System flow

```
1. Parent/student visits center
2. Fills printed enrollment form (see forms/ABC_Enrollment_Form.pdf)
3. Staff encodes data in this order:
```

| Step | Module | What gets saved in SQLite |
|------|--------|---------------------------|
| A | **Profile Students** | `STUDENT` + `PARENT` (name, school, grade, contact) |
| B | **Manage Enrollment** | `ENROLLMENT` (which subject + which batch/schedule + expected `feeAmount`) |
| C | **Process Payment** | `PAYMENT` + `RECEIPT` (money received for that enrollment) |
| D | **Generate Reports** | Reads existing data (no new tables) |

**Tutors (after enrollment):**

| Module | Table |
|--------|--------|
| Record Attendance | `ATTENDANCE` (per class session, per enrollment) |
| Manage Grades | `GRADE` (quiz/progress per enrollment) |

---

## Database logic (why each table exists)

| Table | Meaning |
|-------|---------|
| `STUDENT` | Child goes to regular school; ABC only tutors selected subjects |
| `BATCH` | One class slot: Subject + Grade + Day/Time + Tutor |
| `ENROLLMENT` | Student joined one batch (one subject) — includes expected fee |
| `PAYMENT` | Money paid toward that enrollment |
| `ATTENDANCE` | Present/Absent/Late for that enrollment on a date |
| `GRADE` | Progress scores/notes for that enrollment |

**Balance formula (per subject enrollment):**  
`Balance = Expected Fee − Sum(Payments)`  
Fee comes from `ENROLLMENT.feeAmount` (copied from batch when enrolled).

---

## Module access

| Module | Admin/Staff | Tutor |
|--------|-------------|-------|
| Profile Students | Yes | No |
| Manage Enrollment | Yes | No |
| Process Payment | Yes | No |
| Generate Reports | Yes | No |
| Record Attendance | Yes (all batches) | Yes (own batches) |
| Manage Grades | Yes | Yes (own batches) |
