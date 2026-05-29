"""Shared queries: enrollment fees, payments, and balances."""

from __future__ import annotations


def enrollment_fee_sql() -> str:
    """Expected fee per enrollment (from enrollment row or batch default)."""
    return "COALESCE(e.feeAmount, b.feeAmount, 0)"


def enrollment_paid_sql() -> str:
    """Total paid so far for an enrollment."""
    return """(
        SELECT COALESCE(SUM(p.amount), 0)
        FROM PAYMENT p
        WHERE p.enrollmentID = e.enrollmentID AND p.payStatus = 'Paid'
    )"""


def get_enrollment_balance(conn, enrollment_id: int) -> dict:
    """Return fee, paid, balance for one subject enrollment."""
    row = conn.execute(
        f"""
        SELECT e.enrollmentID,
               {enrollment_fee_sql()} AS fee,
               {enrollment_paid_sql()} AS paid
        FROM ENROLLMENT e
        JOIN BATCH b ON e.batchID = b.batchID
        WHERE e.enrollmentID = ?
        """,
        (enrollment_id,),
    ).fetchone()
    if not row:
        return {"fee": 0.0, "paid": 0.0, "balance": 0.0}
    fee = float(row["fee"] or 0)
    paid = float(row["paid"] or 0)
    return {"fee": fee, "paid": paid, "balance": max(fee - paid, 0.0)}


def count_outstanding_enrollments(conn) -> int:
    """Active enrollments where fee > total paid."""
    row = conn.execute(
        f"""
        SELECT COUNT(*) AS c FROM ENROLLMENT e
        JOIN BATCH b ON e.batchID = b.batchID
        WHERE e.status = 'Active'
          AND {enrollment_fee_sql()} > {enrollment_paid_sql()}
        """
    ).fetchone()
    return int(row["c"]) if row else 0


def fetch_enrollment_rows(conn, student_id: int | None = None, outstanding_only: bool = False):
    """Rows for payment search / balance monitor."""
    where = ["e.status = 'Active'"]
    params: list = []
    if student_id:
        where.append("s.studentID = ?")
        params.append(student_id)
    if outstanding_only:
        where.append(f"{enrollment_fee_sql()} > {enrollment_paid_sql()}")
    sql = f"""
        SELECT e.enrollmentID, s.studentID, s.learnerID, s.studFname, s.studLname, s.studMname,
               s.gradeLevel, sub.subjectName, b.scheduleDay, b.scheduleTime, b.batchName,
               b.gradeLevel AS batchGrade,
               {enrollment_fee_sql()} AS fee,
               {enrollment_paid_sql()} AS paid,
               ({enrollment_fee_sql()} - {enrollment_paid_sql()}) AS balance
        FROM ENROLLMENT e
        JOIN STUDENT s ON e.studentID = s.studentID
        JOIN BATCH b ON e.batchID = b.batchID
        JOIN SUBJECT sub ON b.subjectID = sub.subjectID
        WHERE {' AND '.join(where)}
        ORDER BY balance DESC, s.studLname, sub.subjectName
    """
    return conn.execute(sql, params).fetchall()
