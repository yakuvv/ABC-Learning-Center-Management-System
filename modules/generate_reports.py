"""Generate Reports — staff views attendance, grades, and payment/balance per student."""
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import tkinter.ttk as ttk
from datetime import datetime

import database
from utils.modern_entry import ModernEntry
from utils.modern_combo import ModernCombo
from utils.pdf_generator import generate_student_report_pdf
from utils.enrollment_queries import fetch_enrollment_rows


class GenerateReports(ctk.CTkFrame):
    REPORT_TYPES = ["Attendance Report", "Grade Progress Report", "Payment & Balance Report"]

    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color=config.COLORS["bg"], corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user_role = user_role
        self.user_id = user_id
        self.current_student_id = None
        self._suggestions_rows = []

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()
        self.create_ui()

    def create_ui(self):
        top = ctk.CTkFrame(self, height=70, fg_color=config.COLORS["header"], corner_radius=0)
        top.pack(fill="x")
        top.pack_propagate(False)
        ctk.CTkButton(top, text="<  Back to Dashboard", fg_color="transparent", text_color="#ffffff",
                      hover_color=config.COLORS["primary_hover"], command=self.back_to_dashboard).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(top, text="Generate Reports",
                     font=ctk.CTkFont(size=36, weight="bold"), text_color="#ffffff").pack(
            side="left", expand=True, padx=(0, 100))

        # Removed unnecessary step-by-step helper guide card to clean up UI

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=40, pady=16)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        ctk.CTkLabel(left, text="SEARCH STUDENT", font=ctk.CTkFont(size=14, weight="bold"), text_color=config.COLORS["text"]).pack(anchor="w")
        self.search_entry = ModernEntry(left, placeholder_text="Name, ID, or Learner ID...")
        self.search_entry.pack(fill="x", pady=6)
        self.search_entry.bind("<KeyRelease>", self._on_search)

        self.suggest_frame = ctk.CTkFrame(left, fg_color=config.COLORS["card"], corner_radius=10,
                                          border_width=1, border_color=config.COLORS["border"])
        self.suggest_lbox = tk.Listbox(self.suggest_frame, height=4, font=("Inter", 11),
                                       bg=config.COLORS["card"], fg=config.COLORS["text"],
                                       selectbackground=config.COLORS["primary"], borderwidth=0)
        self.suggest_lbox.pack(fill="x", padx=8, pady=8)
        self.suggest_lbox.bind("<<ListboxSelect>>", self._on_pick_student)

        self.student_lbl = ctk.CTkLabel(left, text="No student selected.", text_color=config.COLORS["text_muted"],
                                        font=ctk.CTkFont(size=12), wraplength=280, justify="left")
        self.student_lbl.pack(anchor="w", pady=10)

        ctk.CTkLabel(left, text="REPORT TYPE", font=ctk.CTkFont(size=14, weight="bold"), text_color=config.COLORS["text"]).pack(anchor="w", pady=(8, 4))
        self.report_combo = ModernCombo(left, values=self.REPORT_TYPES)
        self.report_combo.set(self.REPORT_TYPES[0])
        self.report_combo.pack(fill="x", pady=4)

        ctk.CTkButton(left, text="GENERATE REPORT", fg_color=config.COLORS["primary"], hover_color=config.COLORS["primary_hover"], height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self.generate_report).pack(fill="x", pady=(12, 6))
        ctk.CTkButton(left, text="EXPORT PDF", fg_color=config.COLORS["success"], height=36,
                      command=self.export_pdf).pack(fill="x")

        right = ctk.CTkFrame(body, fg_color=config.COLORS["card"], corner_radius=16,
                             border_width=1, border_color=config.COLORS["border"])
        right.grid(row=0, column=1, sticky="nsew")
        inner = ctk.CTkFrame(right, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=12)

        cols = ("#", "Col1", "Col2", "Col3", "Col4", "Col5")
        self.tree = ttk.Treeview(inner, columns=cols, show="headings", height=18)
        sb = ttk.Scrollbar(inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self._report_data = {"headers": [], "rows": [], "meta": {}}

    def _on_search(self, event=None):
        kw = self.search_entry.get().strip()
        if not kw:
            self.suggest_frame.pack_forget()
            return
        conn = database.get_connection()
        try:
            kid = int(kw)
        except ValueError:
            kid = -1
        rows = conn.execute("""
            SELECT studentID, studFname, studLname, studMname, learnerID, gradeLevel, currentSchool
            FROM STUDENT
            WHERE studentID = ? OR studFname LIKE ? OR studLname LIKE ? OR learnerID LIKE ?
            ORDER BY studLname LIMIT 8
        """, (kid, f"%{kw}%", f"%{kw}%", f"%{kw}%")).fetchall()
        conn.close()
        self._suggestions_rows = [dict(r) for r in rows]
        if not rows:
            self.suggest_frame.pack_forget()
            return
        self.suggest_lbox.delete(0, tk.END)
        for r in self._suggestions_rows:
            m = f" {r['studMname'][0]}." if r["studMname"] else ""
            self.suggest_lbox.insert(tk.END, f" {r['studFname']}{m} {r['studLname']} ({r['learnerID'] or 'no ID'})")
        self.suggest_frame.pack(fill="x", pady=4)

    def _on_pick_student(self, event=None):
        sel = self.suggest_lbox.curselection()
        if not sel:
            return
        r = self._suggestions_rows[sel[0]]
        self.current_student_id = r["studentID"]
        self.search_entry.delete(0, tk.END)
        self.suggest_frame.pack_forget()
        self.student_lbl.configure(
            text=f"{r['studFname']} {r['studLname']}\nLearner ID: {r['learnerID'] or '—'}\n"
                 f"Grade: {r['gradeLevel']} | School: {r['currentSchool'] or '—'}")

    def _setup_tree(self, headers):
        for c in self.tree["columns"]:
            self.tree.heading(c, text="")
        self.tree["columns"] = headers
        for h in headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=max(80, int(700 / len(headers))), anchor="center")
        for i in self.tree.get_children():
            self.tree.delete(i)

    def generate_report(self):
        if not self.current_student_id:
            messagebox.showwarning("Warning", "Select a student first.")
            return
        rtype = self.report_combo.get()
        conn = database.get_connection()
        stu = conn.execute(
            "SELECT * FROM STUDENT WHERE studentID = ?", (self.current_student_id,)
        ).fetchone()
        if not stu:
            conn.close()
            return
        name = f"{stu['studFname']} {stu['studLname']}"
        lid = stu["learnerID"] or "—"
        meta = {
            "student_name": name,
            "learner_id": lid,
            "generated": datetime.now().strftime("%B %d, %Y %I:%M %p"),
        }
        headers, rows = [], []

        if rtype == "Attendance Report":
            meta["title"] = "Attendance Report"
            meta["subtitle"] = "Tutorial class attendance per subject enrollment"
            headers = ["Subject", "Date", "Time", "Status"]
            data = conn.execute("""
                SELECT sub.subjectName, a.attDate, a.attTime, a.attStatus
                FROM ATTENDANCE a
                JOIN ENROLLMENT e ON a.enrollmentID = e.enrollmentID
                JOIN BATCH b ON e.batchID = b.batchID
                JOIN SUBJECT sub ON b.subjectID = sub.subjectID
                WHERE e.studentID = ?
                ORDER BY a.attDate DESC, sub.subjectName
            """, (self.current_student_id,)).fetchall()
            rows = [(r["subjectName"], r["attDate"], r["attTime"] or "—", r["attStatus"]) for r in data]

        elif rtype == "Grade Progress Report":
            meta["title"] = "Grade Progress Report"
            meta["subtitle"] = "Quiz and progress tracking (tutorial center)"
            headers = ["Subject", "Assessment", "Score", "Feedback", "Date"]
            data = conn.execute("""
                SELECT sub.subjectName, g.assessmentType, g.score, g.feedback, g.dateRecorded
                FROM GRADE g
                JOIN ENROLLMENT e ON g.enrollmentID = e.enrollmentID
                JOIN BATCH b ON e.batchID = b.batchID
                JOIN SUBJECT sub ON b.subjectID = sub.subjectID
                WHERE e.studentID = ?
                ORDER BY sub.subjectName, g.assessmentType
            """, (self.current_student_id,)).fetchall()
            rows = [
                (r["subjectName"], r["assessmentType"],
                 r["score"] if r["score"] is not None else "—",
                 (r["feedback"] or "—")[:40], r["dateRecorded"])
                for r in data
            ]

        else:
            meta["title"] = "Payment & Balance Report"
            meta["subtitle"] = "Fees and payments per subject enrollment"
            headers = ["Subject", "Expected Fee", "Paid", "Balance", "Status"]
            data = fetch_enrollment_rows(conn, student_id=self.current_student_id)
            rows = []
            for r in data:
                bal = float(r["balance"] or 0)
                status = "Paid" if bal <= 0 else "Outstanding"
                rows.append((
                    r["subjectName"],
                    f"PHP {float(r['fee']):,.2f}",
                    f"PHP {float(r['paid']):,.2f}",
                    f"PHP {bal:,.2f}",
                    status,
                ))

        conn.close()
        self._report_data = {"headers": headers, "rows": rows, "meta": meta}
        display_cols = ["#"] + headers
        self._setup_tree(display_cols)
        if not rows:
            self.tree.insert("", "end", values=("—",) * len(display_cols))
        else:
            for idx, row in enumerate(rows):
                self.tree.insert("", "end", values=(idx + 1,) + tuple(row))

    def export_pdf(self):
        if not self._report_data.get("rows"):
            messagebox.showwarning("Warning", "Generate a report first.")
            return
        os.makedirs("reports", exist_ok=True)
        safe = self._report_data["meta"].get("student_name", "student").replace(" ", "_")
        rtype = self.report_combo.get().replace(" ", "_")
        path = os.path.join("reports", f"{rtype}_{safe}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
        try:
            generate_student_report_pdf(
                path,
                self._report_data["meta"],
                self._report_data["headers"],
                self._report_data["rows"],
            )
            messagebox.showinfo("Saved", f"Report PDF saved:\n{os.path.abspath(path)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def back_to_dashboard(self):
        d = self.master.master
        self.destroy()
        if hasattr(d, "_show_welcome"):
            d._show_welcome()
