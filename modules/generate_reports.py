# Generate Reports — I created this module for Admin/Staff to generate, view, and export student reports.
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from PIL import Image

import database
from utils.modern_entry import ModernEntry
from utils.modern_combo import ModernCombo
from utils.pdf_generator import generate_student_report_pdf


class GenerateReports(ctk.CTkFrame):
    REPORT_TYPES = [
        "Attendance Report",
        "Grade Report",
        "Payments Report",
        "Enrollment Summary",
        "Full Student Profile Report"
    ]

    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#f8fafc", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user_role = user_role
        self.user_id = user_id

        self.current_student_id = None
        self.current_student_data = None
        self._suggestions_rows = []

        # Remove welcome label if present
        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.create_ui()

    def create_ui(self):
        # Header bar
        self.top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)

        ctk.CTkButton(
            self.top_bar, text="<  Back to Dashboard",
            font=ctk.CTkFont(family="Inter", size=14),
            fg_color="transparent", text_color="#ffffff",
            hover_color="#22259c", width=150, height=40,
            corner_radius=8, command=self.back_to_dashboard
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            self.top_bar, text="Generate Reports",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", expand=True, padx=(0, 100))

        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(55, 55))
                ctk.CTkLabel(self.top_bar, image=ctk_logo, text="").pack(side="right", padx=30)
            except Exception:
                ctk.CTkLabel(self.top_bar, text="ABC", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#ffffff").pack(side="right", padx=30)
        else:
            ctk.CTkLabel(self.top_bar, text="ABC", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#ffffff").pack(side="right", padx=30)

        # Main body content
        self.body_container = ctk.CTkFrame(self, fg_color="transparent")
        self.body_container.pack(fill="both", expand=True, padx=40, pady=16)

        # Row 1: Search controls & Generate Button
        self.controls_row = ctk.CTkFrame(self.body_container, fg_color="transparent")
        self.controls_row.pack(fill="x", pady=(0, 12))

        # Search Card
        self.search_card = ctk.CTkFrame(
            self.controls_row, fg_color="#ffffff", corner_radius=16,
            border_width=1, border_color="#cbd5e1"
        )
        self.search_card.pack(side="left", fill="x", expand=True, padx=(0, 15))

        self.search_inner = ctk.CTkFrame(self.search_card, fg_color="transparent")
        self.search_inner.pack(fill="both", expand=True, padx=15, pady=12)

        self.search_entry = ModernEntry(
            self.search_inner,
            placeholder_text="🔍 Type Student Name or Learner ID to search...",
            height=32, font=ctk.CTkFont(family="Inter", size=13),
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self.on_search_key)
        self.search_entry.bind("<FocusOut>", lambda e: self.after(250, self.hide_suggestions))

        # Generate Button
        self.generate_btn = ctk.CTkButton(
            self.controls_row, text="GENERATE",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            width=160, height=58, corner_radius=16,
            fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
            command=self.on_click_generate
        )
        self.generate_btn.pack(side="right")

        # Autocomplete Suggestion Listbox (hidden by default)
        self.suggest_frame = ctk.CTkFrame(
            self.search_inner, fg_color="#ffffff",
            border_width=1, border_color="#cbd5e1", corner_radius=10
        )
        self.suggest_lbox = tk.Listbox(
            self.suggest_frame,
            bg="#ffffff", fg="#1e293b",
            selectbackground="#122aff", selectforeground="#ffffff",
            font=("Inter", 12), borderwidth=0, highlightthickness=0, height=5, activestyle="none"
        )
        self.suggest_lbox.pack(fill="x", padx=8, pady=8)
        self.suggest_lbox.bind("<<ListboxSelect>>", self.on_suggestion_select)

        # Main Report card
        self.report_card = ctk.CTkFrame(
            self.body_container, fg_color="#ffffff", corner_radius=16,
            border_width=1, border_color="#cbd5e1"
        )
        self.report_card.pack(fill="both", expand=True)
        self.report_card.pack_propagate(False)

        self.show_placeholder()

    # Placeholder state
    def show_placeholder(self):
        for w in self.report_card.winfo_children():
            w.destroy()

        pl_inner = ctk.CTkFrame(self.report_card, fg_color="transparent")
        pl_inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            pl_inner, text="📊",
            font=ctk.CTkFont(family="Inter", size=48),
            text_color="#94a3b8"
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            pl_inner,
            text="Search and select a student above, then click GENERATE to view the report.",
            font=ctk.CTkFont(family="Inter", size=14, weight="normal"),
            text_color="#64748b", justify="center"
        ).pack()

    # Render active report container
    def render_report_container(self, r):
        for w in self.report_card.winfo_children():
            w.destroy()

        mname = (f" {r['studMname'][0]}." if r['studMname'] else "")
        full_name = f"{r['studFname']}{mname} {r['studLname']}"

        # Card header bar
        rc_header = ctk.CTkFrame(self.report_card, fg_color="#15165e", corner_radius=8, height=44)
        rc_header.pack(fill="x", side="top", padx=10, pady=(10, 5))
        rc_header.pack_propagate(False)

        ctk.CTkLabel(
            rc_header,
            text=f"REPORTS SUMMARY  •  {full_name.upper()}  (Learner ID: {r['learnerID'] or '—'})",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=15, pady=5)

        # View Profile Button
        ctk.CTkButton(
            rc_header, text="View Profile",
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            width=100, height=28, corner_radius=6,
            fg_color="#ffffff", hover_color="#e0e7ff",
            text_color="#15165e",
            command=lambda: self.show_student_detail_popup(r['studentID'], r['learnerID'])
        ).pack(side="right", padx=10, pady=8)

        # Report Type Dropdown
        self.report_type_combo = ModernCombo(
            rc_header, values=self.REPORT_TYPES, width=220, height=28,
            command=self.on_report_type_changed
        )
        self.report_type_combo.set(self.REPORT_TYPES[0])
        self.report_type_combo.pack(side="right", padx=(10, 5), pady=8)

        ctk.CTkLabel(
            rc_header, text="Report Type:",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#cbd5e1"
        ).pack(side="right", padx=(10, 0), pady=8)

        # Dynamic body scroll container
        self.scroll_container = ctk.CTkScrollableFrame(self.report_card, fg_color="transparent")
        self.scroll_container.pack(fill="both", expand=True, padx=15, pady=(5, 10))

        # Bottom export bar
        self.bottom_bar = ctk.CTkFrame(self.report_card, fg_color="#f8fafc", height=50)
        self.bottom_bar.pack(fill="x", side="bottom", padx=10, pady=(5, 10))
        self.bottom_bar.pack_propagate(False)

        ctk.CTkButton(
            self.bottom_bar, text="EXPORT REPORT (PDF)",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            fg_color="#15165e", hover_color="#22259c", text_color="#ffffff",
            width=180, height=36, corner_radius=8,
            command=self.export_report_pdf
        ).pack(side="right", padx=10, pady=7)

        # Load initial report
        self.load_report_data()

    # Populate report data
    def on_report_type_changed(self, *args):
        self.load_report_data()

    def load_report_data(self):
        for w in self.scroll_container.winfo_children():
            w.destroy()

        report_type = self.report_type_combo.get()
        student_id = self.current_student_id

        conn = database.get_connection()
        cursor = conn.cursor()

        try:
            if report_type == "Attendance Report":
                cursor.execute("""
                    SELECT sub.subjCode, a.attDate, a.attTime, a.attStatus
                    FROM ATTENDANCE a
                    JOIN REGISTRATION_DETAIL rd ON a.detailID = rd.detailID
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    WHERE r.studentID = ?
                    ORDER BY a.attDate DESC, sub.subjCode
                """, (student_id,))
                rows = cursor.fetchall()
                self.render_attendance_report(rows)

            elif report_type == "Grade Report":
                cursor.execute("""
                    SELECT sub.subjCode, r.term, g.gradeValue, g.letterGrade, g.gradeDesc
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    LEFT JOIN GRADE g ON rd.detailID = g.detailID AND g.period = 'Overall'
                    WHERE r.studentID = ?
                    ORDER BY r.term, sub.subjCode
                """, (student_id,))
                rows = cursor.fetchall()
                self.render_grade_report(rows)

            elif report_type == "Payments Report":
                # Get payments list
                cursor.execute("""
                    SELECT p.payDate, p.payTime, p.amount, p.payMethod, r.receiptNumber, reg.term
                    FROM PAYMENT p
                    JOIN REGISTRATION reg ON p.registrationID = reg.registrationID
                    LEFT JOIN RECEIPT r ON r.paymentID = p.paymentID
                    WHERE reg.studentID = ?
                    ORDER BY p.paymentID DESC
                """, (student_id,))
                payments_rows = cursor.fetchall()

                # Get financials
                cursor.execute("""
                    SELECT SUM(COALESCE(rd.feeAmount, s.pricePerTerm, 0)) AS total_due
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    JOIN SUBJECT s ON s.subjectID = rd.subjectID
                    WHERE r.studentID = ? AND rd.enrollStatus = 'Active'
                """, (student_id,))
                due_row = cursor.fetchone()
                total_due = float(due_row['total_due'] or 0)

                cursor.execute("""
                    SELECT SUM(p.amount) AS total_paid
                    FROM PAYMENT p
                    JOIN REGISTRATION reg ON p.registrationID = reg.registrationID
                    WHERE reg.studentID = ? AND p.payStatus = 'Paid'
                """, (student_id,))
                paid_row = cursor.fetchone()
                total_paid = float(paid_row['total_paid'] or 0)

                self.render_payments_report(payments_rows, total_due, total_paid)

            elif report_type == "Enrollment Summary":
                cursor.execute("""
                    SELECT sub.subjCode, b.batchLabel, b.schedule, r.term, rd.enrollStatus
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    LEFT JOIN BATCH b ON rd.batchID = b.batchID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    WHERE r.studentID = ?
                    ORDER BY r.term, sub.subjCode
                """, (student_id,))
                rows = cursor.fetchall()
                self.render_enrollment_report(rows)

            elif report_type == "Full Student Profile Report":
                # Get Academic details sorted from A-Z alphabetically
                cursor.execute("""
                    SELECT sub.subjCode, b.batchLabel, b.schedule, r.term, rd.enrollStatus
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    LEFT JOIN BATCH b ON rd.batchID = b.batchID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    WHERE r.studentID = ?
                    ORDER BY sub.subjCode ASC
                """, (student_id,))
                acad_rows = cursor.fetchall()

                # Parent details
                cursor.execute("""
                    SELECT parName, parContactInfo, relationship
                    FROM PARENT WHERE studentID = ?
                """, (student_id,))
                parent = cursor.fetchone()

                self.render_profile_report(acad_rows, parent)

            conn.close()
        except Exception as e:
            conn.close()
            messagebox.showerror("Error", f"Failed to load report data: {e}")

    # Render specific tables

    # 1. Attendance Report Table
    def render_attendance_report(self, rows):
        if not rows:
            ctk.CTkLabel(
                self.scroll_container, text="No attendance records found for this student.",
                font=ctk.CTkFont(family="Inter", size=13, slant="italic"), text_color="#64748b"
            ).pack(anchor="w", padx=10, pady=20)
            return

        headers = ["SUBJECT NAME", "DATE", "TIME", "STATUS"]
        weights = [4, 2, 2, 2]
        
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.pack(fill="x", padx=5, pady=5)
        for col_idx, (header, weight) in enumerate(zip(headers, weights)):
            grid.columnconfigure(col_idx, weight=weight, uniform="rep_col")
            lbl = tk.Label(
                grid, text=header, font=("Inter", 10, "bold"),
                fg="#64748b", bg="#f1f5f9", anchor="w", padx=10, pady=8
            )
            lbl.grid(row=0, column=col_idx, sticky="ew")

        for idx, r in enumerate(rows):
            is_even = (idx % 2 == 0)
            row_bg = "#f8fafc" if is_even else "#ffffff"
            
            row_container = tk.Frame(grid, bg=row_bg, bd=0)
            row_container.grid(row=idx + 1, column=0, columnspan=len(weights), sticky="ew", pady=2)
            for col_idx, weight in enumerate(weights):
                row_container.columnconfigure(col_idx, weight=weight, uniform="rep_col")

            tk.Label(row_container, text=r['subjCode'], font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=r['attDate'], font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=1, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=r['attTime'] or "—", font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=2, sticky="ew", padx=10, pady=8)
            
            status = r['attStatus'].upper()
            status_color = "#15803d" if status == "PRESENT" else "#b91c1c" if status == "ABSENT" else "#1d4ed8"
            status_bg = "#dcfce7" if status == "PRESENT" else "#fee2e2" if status == "ABSENT" else "#dbeafe"
            
            status_pill = ctk.CTkFrame(row_container, fg_color=status_bg, corner_radius=6)
            status_pill.grid(row=0, column=3, sticky="w", padx=10, pady=6)
            ctk.CTkLabel(
                status_pill, text=status, font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                text_color=status_color
            ).pack(padx=8, pady=3)

    # 2. Grade Report Table
    def render_grade_report(self, rows):
        if not rows:
            ctk.CTkLabel(
                self.scroll_container, text="No grade records found for this student.",
                font=ctk.CTkFont(family="Inter", size=13, slant="italic"), text_color="#64748b"
            ).pack(anchor="w", padx=10, pady=20)
            return

        headers = ["SUBJECT NAME", "TERM", "NUMERIC GRADE", "LETTER GRADE", "DESCRIPTION"]
        weights = [4, 2, 2, 2, 3]
        
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.pack(fill="x", padx=5, pady=5)
        for col_idx, (header, weight) in enumerate(zip(headers, weights)):
            grid.columnconfigure(col_idx, weight=weight, uniform="rep_col")
            lbl = tk.Label(
                grid, text=header, font=("Inter", 10, "bold"),
                fg="#64748b", bg="#f1f5f9", anchor="w", padx=10, pady=8
            )
            lbl.grid(row=0, column=col_idx, sticky="ew")

        for idx, r in enumerate(rows):
            is_even = (idx % 2 == 0)
            row_bg = "#f8fafc" if is_even else "#ffffff"
            
            row_container = tk.Frame(grid, bg=row_bg, bd=0)
            row_container.grid(row=idx + 1, column=0, columnspan=len(weights), sticky="ew", pady=2)
            for col_idx, weight in enumerate(weights):
                row_container.columnconfigure(col_idx, weight=weight, uniform="rep_col")

            tk.Label(row_container, text=r['subjCode'], font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=r['term'], font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=1, sticky="ew", padx=10, pady=8)
            
            val = r['gradeValue']
            if val is not None:
                numeric_str = f"{int(val)}" if val == int(val) else f"{val}"
                letter = r['letterGrade'] or "—"
                desc = r['gradeDesc'] or "—"
                grade_color = "#122aff" if val >= 75 else "#ef4444"
            else:
                numeric_str = "—"
                letter = "—"
                desc = "—"
                grade_color = "#64748b"

            tk.Label(row_container, text=numeric_str, font=("Inter", 11, "bold"), fg=grade_color, bg=row_bg, anchor="w").grid(row=0, column=2, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=letter, font=("Inter", 11, "bold"), fg=grade_color, bg=row_bg, anchor="w").grid(row=0, column=3, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=desc, font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=4, sticky="ew", padx=10, pady=8)

    # 3. Payments Report Table
    def render_payments_report(self, rows, total_due, total_paid):
        balance = max(total_due - total_paid, 0.0)

        # Financial Summary Banner Card
        banner = ctk.CTkFrame(self.scroll_container, fg_color="#eef2ff", corner_radius=12, border_width=1, border_color="#c7d2fe")
        banner.pack(fill="x", padx=5, pady=(5, 15))
        banner_inner = ctk.CTkFrame(banner, fg_color="transparent")
        banner_inner.pack(fill="x", padx=16, pady=12)

        for col, (label, val, color) in enumerate([
            ("Total Enrollment Fees", f"₱{total_due:,.2f}", "#15165e"),
            ("Total Amount Paid", f"₱{total_paid:,.2f}", "#15803d"),
            ("Remaining Balance", f"₱{balance:,.2f}", "#b45309" if balance > 0 else "#15803d")
        ]):
            banner_inner.columnconfigure(col, weight=1)
            cell = ctk.CTkFrame(banner_inner, fg_color="transparent")
            cell.grid(row=0, column=col, sticky="ew")
            ctk.CTkLabel(cell, text=label, font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#64748b").pack(anchor="w")
            ctk.CTkLabel(cell, text=val, font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color=color).pack(anchor="w")

        if not rows:
            ctk.CTkLabel(
                self.scroll_container, text="No payment history records found for this student.",
                font=ctk.CTkFont(family="Inter", size=13, slant="italic"), text_color="#64748b"
            ).pack(anchor="w", padx=10, pady=10)
            return

        headers = ["RECEIPT NO.", "DATE & TIME", "AMOUNT PAID", "PAYMENT METHOD", "STATUS"]
        weights = [3, 3, 2, 2, 2]
        
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.pack(fill="x", padx=5, pady=5)
        for col_idx, (header, weight) in enumerate(zip(headers, weights)):
            grid.columnconfigure(col_idx, weight=weight, uniform="rep_col")
            lbl = tk.Label(
                grid, text=header, font=("Inter", 10, "bold"),
                fg="#64748b", bg="#f1f5f9", anchor="w", padx=10, pady=8
            )
            lbl.grid(row=0, column=col_idx, sticky="ew")

        for idx, r in enumerate(rows):
            is_even = (idx % 2 == 0)
            row_bg = "#f8fafc" if is_even else "#ffffff"
            
            row_container = tk.Frame(grid, bg=row_bg, bd=0)
            row_container.grid(row=idx + 1, column=0, columnspan=len(weights), sticky="ew", pady=2)
            for col_idx, weight in enumerate(weights):
                row_container.columnconfigure(col_idx, weight=weight, uniform="rep_col")

            tk.Label(row_container, text=r['receiptNumber'] or "—", font=("Inter", 11, "bold"), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=f"{r['payDate']}  ·  {r['payTime'] or '—'}", font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=1, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=f"₱{float(r['amount']):,.2f}", font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=2, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=r['payMethod'], font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=3, sticky="ew", padx=10, pady=8)
            
            status_pill = ctk.CTkFrame(row_container, fg_color="#dcfce7", corner_radius=6)
            status_pill.grid(row=0, column=4, sticky="w", padx=10, pady=6)
            ctk.CTkLabel(
                status_pill, text="PAID", font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                text_color="#15803d"
            ).pack(padx=8, pady=3)

    # 4. Enrollment Summary Table
    def render_enrollment_report(self, rows):
        if not rows:
            ctk.CTkLabel(
                self.scroll_container, text="No enrollment history records found for this student.",
                font=ctk.CTkFont(family="Inter", size=13, slant="italic"), text_color="#64748b"
            ).pack(anchor="w", padx=10, pady=20)
            return

        headers = ["SUBJECT NAME", "BATCH", "SCHEDULE", "TERM", "STATUS"]
        weights = [4, 2, 3, 2, 2]
        
        grid = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        grid.pack(fill="x", padx=5, pady=5)
        for col_idx, (header, weight) in enumerate(zip(headers, weights)):
            grid.columnconfigure(col_idx, weight=weight, uniform="rep_col")
            lbl = tk.Label(
                grid, text=header, font=("Inter", 10, "bold"),
                fg="#64748b", bg="#f1f5f9", anchor="w", padx=10, pady=8
            )
            lbl.grid(row=0, column=col_idx, sticky="ew")

        for idx, r in enumerate(rows):
            is_even = (idx % 2 == 0)
            row_bg = "#f8fafc" if is_even else "#ffffff"
            
            row_container = tk.Frame(grid, bg=row_bg, bd=0)
            row_container.grid(row=idx + 1, column=0, columnspan=len(weights), sticky="ew", pady=2)
            for col_idx, weight in enumerate(weights):
                row_container.columnconfigure(col_idx, weight=weight, uniform="rep_col")

            tk.Label(row_container, text=r['subjCode'], font=("Inter", 11, "bold"), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=r['batchLabel'] or "—", font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=1, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=r['schedule'] or "—", font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=2, sticky="ew", padx=10, pady=8)
            tk.Label(row_container, text=r['term'], font=("Inter", 11), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=3, sticky="ew", padx=10, pady=8)
            
            status = r['enrollStatus'].upper()
            status_color = "#15803d" if status == "ACTIVE" else "#64748b"
            status_bg = "#dcfce7" if status == "ACTIVE" else "#f1f5f9"

            status_pill = ctk.CTkFrame(row_container, fg_color=status_bg, corner_radius=6)
            status_pill.grid(row=0, column=4, sticky="w", padx=10, pady=6)
            ctk.CTkLabel(
                status_pill, text=status, font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                text_color=status_color
            ).pack(padx=8, pady=3)

    # 5. Full Student Profile Report (Beautifully structured panel dossier)
    def render_profile_report(self, acad_rows, parent):
        s = self.current_student_data

        # Custom panel cards
        def create_panel(title):
            panel = ctk.CTkFrame(self.scroll_container, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#cbd5e1")
            panel.pack(fill="x", pady=(0, 15))
            
            accent = ctk.CTkFrame(panel, width=5, fg_color="#15165e", corner_radius=2.5)
            accent.pack(side="left", fill="y", padx=(12, 0), pady=12)
            
            inner = ctk.CTkFrame(panel, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=15, pady=12)
            
            ctk.CTkLabel(
                inner, text=title, font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                text_color="#15165e"
            ).pack(anchor="w", pady=(0, 8))
            return inner

        def add_row_detail(grid, row_idx, label, val):
            rf = ctk.CTkFrame(grid, fg_color="transparent")
            rf.grid(row=row_idx // 2, column=row_idx % 2, sticky="ew", pady=4, padx=5)
            ctk.CTkLabel(rf, text=f"{label}:", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#64748b", width=110, anchor="w").pack(side="left")
            ctk.CTkLabel(rf, text=str(val), font=ctk.CTkFont(family="Inter", size=12), text_color="#0f172a", anchor="w").pack(side="left", fill="x", expand=True)

        # I. Personal Information Dossier
        pers_inner = create_panel("I. STUDENT PERSONAL DETAILS")
        grid_pers = ctk.CTkFrame(pers_inner, fg_color="transparent")
        grid_pers.pack(fill="x")
        grid_pers.columnconfigure(0, weight=1)
        grid_pers.columnconfigure(1, weight=1)

        add_row_detail(grid_pers, 0, "Learner ID", s['learnerID'] or "—")
        add_row_detail(grid_pers, 1, "Full Name", f"{s['studLname']}, {s['studFname']} {s['studMname'] or ''}")
        add_row_detail(grid_pers, 2, "Grade Level", s['level'] or "Unassigned")
        add_row_detail(grid_pers, 3, "Gender", s['gender'] or "—")
        add_row_detail(grid_pers, 4, "Date of Birth", s['dob'] or "—")
        add_row_detail(grid_pers, 5, "Contact Information", s['studContactInfo'] or "—")
        add_row_detail(grid_pers, 6, "Home Address", s['address'] or "—")

        # II. Parent / Guardian Details
        par_inner = create_panel("II. PARENT / GUARDIAN INFORMATION")
        if parent:
            grid_par = ctk.CTkFrame(par_inner, fg_color="transparent")
            grid_par.pack(fill="x")
            grid_par.columnconfigure(0, weight=1)
            grid_par.columnconfigure(1, weight=1)

            add_row_detail(grid_par, 0, "Parent Name", parent['parName'])
            add_row_detail(grid_par, 1, "Relationship", parent['relationship'])
            add_row_detail(grid_par, 2, "Contact Information", parent['parContactInfo'] or "—")
        else:
            ctk.CTkLabel(
                par_inner, text="No parent/guardian information found.",
                font=ctk.CTkFont(family="Inter", size=12, slant="italic"), text_color="#ef4444"
            ).pack(anchor="w", pady=5)

        # III. Academic Enrollments
        acad_inner = create_panel("III. ACADEMIC ENROLLMENTS (Sorted A-Z)")
        if not acad_rows:
            ctk.CTkLabel(
                acad_inner, text="No academic subject enrollments found.",
                font=ctk.CTkFont(family="Inter", size=12, slant="italic"), text_color="#64748b"
            ).pack(anchor="w", pady=5)
        else:
            headers = ["SUBJECT NAME", "BATCH", "SCHEDULE", "TERM", "STATUS"]
            weights = [4, 2, 3, 2, 2]
            
            # Custom grid nested inside panel
            grid_acad = ctk.CTkFrame(acad_inner, fg_color="transparent")
            grid_acad.pack(fill="x", pady=5)
            
            for col_idx, (header, weight) in enumerate(zip(headers, weights)):
                grid_acad.columnconfigure(col_idx, weight=weight, uniform="acad_col")
                lbl = tk.Label(
                    grid_acad, text=header, font=("Inter", 9, "bold"),
                    fg="#64748b", bg="#f1f5f9", anchor="w", padx=8, pady=6
                )
                lbl.grid(row=0, column=col_idx, sticky="ew")

            for idx, r in enumerate(acad_rows):
                is_even = (idx % 2 == 0)
                row_bg = "#f8fafc" if is_even else "#ffffff"
                row_container = tk.Frame(grid_acad, bg=row_bg, bd=0)
                row_container.grid(row=idx + 1, column=0, columnspan=len(weights), sticky="ew", pady=1)
                
                for col_idx, weight in enumerate(weights):
                    row_container.columnconfigure(col_idx, weight=weight, uniform="acad_col")

                tk.Label(row_container, text=r['subjCode'], font=("Inter", 10, "bold"), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=0, sticky="ew", padx=8, pady=5)
                tk.Label(row_container, text=r['batchLabel'] or "—", font=("Inter", 10), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=1, sticky="ew", padx=8, pady=5)
                tk.Label(row_container, text=r['schedule'] or "—", font=("Inter", 10), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=2, sticky="ew", padx=8, pady=5)
                tk.Label(row_container, text=r['term'], font=("Inter", 10), fg="#1e293b", bg=row_bg, anchor="w").grid(row=0, column=3, sticky="ew", padx=8, pady=5)

                status = r['enrollStatus'].upper()
                status_color = "#15803d" if status == "ACTIVE" else "#64748b"
                status_bg = "#dcfce7" if status == "ACTIVE" else "#f1f5f9"

                status_pill = ctk.CTkFrame(row_container, fg_color=status_bg, corner_radius=6)
                status_pill.grid(row=0, column=4, sticky="w", padx=8, pady=3)
                ctk.CTkLabel(
                    status_pill, text=status, font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                    text_color=status_color
                ).pack(padx=8, pady=2)

    # Key events & search suggestions
    def on_search_key(self, event):
        val = self.search_entry.get().strip()
        if len(val) < 2:
            self.hide_suggestions()
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.registrationID, r.studentID, r.learnerID,
                       s.studLname, s.studFname, s.studMname,
                       r.level, r.groupName, r.term,
                       s.gender, s.dob, s.address, s.studContactInfo
                FROM REGISTRATION r
                JOIN STUDENT s ON r.studentID = s.studentID
                WHERE r.regStatus = 'Active' AND (
                    r.learnerID LIKE ? OR
                    s.studFname LIKE ? OR
                    s.studLname LIKE ? OR
                    (s.studFname || ' ' || s.studLname) LIKE ?
                )
                ORDER BY s.studLname, s.studFname
                LIMIT 10
            """, (f"%{val}%", f"%{val}%", f"%{val}%", f"%{val}%"))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()

            if rows:
                self._suggestions_rows = rows
                self.suggest_lbox.delete(0, tk.END)
                for r in rows:
                    mname = f" {r['studMname'][0]}." if r['studMname'] else ""
                    self.suggest_lbox.insert(
                        tk.END,
                        f" {r['studFname']}{mname} {r['studLname']}  (Learner ID: {r['learnerID'] or '—'} | {r['level'] or '—'})"
                    )
                self.suggest_lbox.config(height=min(len(rows), 6))
                self.suggest_frame.pack(fill="x", after=self.search_entry, pady=(4, 0))
            else:
                self.hide_suggestions()
        except Exception as e:
            conn.close()
            self.hide_suggestions()

    def hide_suggestions(self):
        self.suggest_frame.pack_forget()
        self._suggestions_rows = []

    def on_suggestion_select(self, event):
        sel = self.suggest_lbox.curselection()
        if not sel:
            return
        r = self._suggestions_rows[sel[0]]
        self.current_student_id = r['studentID']
        self.current_student_data = r
        mname = f" {r['studMname'][0]}." if r['studMname'] else ""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, f"{r['studFname']}{mname} {r['studLname']}")
        self.hide_suggestions()
        
        # Auto render
        self.render_report_container(r)

    def on_click_generate(self):
        if not self.current_student_id:
            messagebox.showwarning("Warning", "Please type and select a student from suggestions first.")
            return
        self.render_report_container(self.current_student_data)

    # Export PDF report
    def export_report_pdf(self):
        if not self.current_student_id:
            messagebox.showwarning("Warning", "No active report generated.")
            return

        report_type = self.report_type_combo.get()
        student_name = f"{self.current_student_data['studFname']} {self.current_student_data['studLname']}"
        safe_name = student_name.replace(" ", "_")
        safe_type = report_type.replace(" ", "_")

        # Select file path
        reports_dir = os.path.abspath("reports")
        os.makedirs(reports_dir, exist_ok=True)
        default_file = f"Report_{safe_type}_{safe_name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = os.path.join(reports_dir, default_file)

        # Retrieve headers and rows dynamically based on the current data loaded
        conn = database.get_connection()
        cursor = conn.cursor()

        try:
            # We fetch exactly what was shown in the custom tables
            if report_type == "Attendance Report":
                headers = ["SUBJECT NAME", "DATE", "TIME", "STATUS"]
                cursor.execute("""
                    SELECT sub.subjCode, a.attDate, a.attTime, a.attStatus
                    FROM ATTENDANCE a
                    JOIN REGISTRATION_DETAIL rd ON a.detailID = rd.detailID
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    WHERE r.studentID = ?
                    ORDER BY a.attDate DESC, sub.subjCode
                """, (self.current_student_id,))
                rows = [list(r) for r in cursor.fetchall()]

            elif report_type == "Grade Report":
                headers = ["SUBJECT NAME", "TERM", "NUMERIC GRADE", "LETTER GRADE", "DESCRIPTION"]
                cursor.execute("""
                    SELECT sub.subjCode, r.term, g.gradeValue, g.letterGrade, g.gradeDesc
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    LEFT JOIN GRADE g ON rd.detailID = g.detailID AND g.period = 'Overall'
                    WHERE r.studentID = ?
                    ORDER BY r.term, sub.subjCode
                """, (self.current_student_id,))
                grade_rows = cursor.fetchall()
                rows = []
                for r in grade_rows:
                    val = r['gradeValue']
                    num_str = f"{int(val)}" if val == int(val) else f"{val}" if val is not None else "—"
                    rows.append([
                        r['subjCode'],
                        r['term'],
                        num_str,
                        r['letterGrade'] or "—",
                        r['gradeDesc'] or "—"
                    ])

            elif report_type == "Payments Report":
                headers = ["RECEIPT NO.", "DATE & TIME", "AMOUNT PAID", "PAYMENT METHOD", "STATUS"]
                cursor.execute("""
                    SELECT p.payDate, p.payTime, p.amount, p.payMethod, r.receiptNumber
                    FROM PAYMENT p
                    JOIN REGISTRATION reg ON p.registrationID = reg.registrationID
                    LEFT JOIN RECEIPT r ON r.paymentID = p.paymentID
                    WHERE reg.studentID = ?
                    ORDER BY p.paymentID DESC
                """, (self.current_student_id,))
                pay_rows = cursor.fetchall()
                rows = []
                for r in pay_rows:
                    rows.append([
                        r['receiptNumber'] or "—",
                        f"{r['payDate']} {r['payTime'] or ''}",
                        f"₱{float(r['amount']):,.2f}",
                        r['payMethod'],
                        "PAID"
                    ])

            elif report_type == "Enrollment Summary":
                headers = ["SUBJECT NAME", "BATCH", "SCHEDULE", "TERM", "STATUS"]
                cursor.execute("""
                    SELECT sub.subjCode, b.batchLabel, b.schedule, r.term, rd.enrollStatus
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    LEFT JOIN BATCH b ON rd.batchID = b.batchID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    WHERE r.studentID = ?
                    ORDER BY r.term, sub.subjCode
                """, (self.current_student_id,))
                rows = [
                    [r['subjCode'], r['batchLabel'] or "—", r['schedule'] or "—", r['term'], r['enrollStatus'].upper()]
                    for r in cursor.fetchall()
                ]

            elif report_type == "Full Student Profile Report":
                headers = ["SUBJECT NAME", "BATCH", "SCHEDULE", "TERM", "STATUS"]
                cursor.execute("""
                    SELECT sub.subjCode, b.batchLabel, b.schedule, r.term, rd.enrollStatus
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON rd.registrationID = r.registrationID
                    LEFT JOIN BATCH b ON rd.batchID = b.batchID
                    JOIN SUBJECT sub ON rd.subjectID = sub.subjectID
                    WHERE r.studentID = ?
                    ORDER BY sub.subjCode ASC
                """, (self.current_student_id,))
                rows = [
                    [r['subjCode'], r['batchLabel'] or "—", r['schedule'] or "—", r['term'], r['enrollStatus'].upper()]
                    for r in cursor.fetchall()
                ]

            # Parent info for full profile report
            cursor.execute("""
                SELECT parName, parContactInfo, relationship
                FROM PARENT WHERE studentID = ?
            """, (self.current_student_id,))
            parent = cursor.fetchone()

            conn.close()
        except Exception as e:
            conn.close()
            messagebox.showerror("Error", f"Failed to retrieve data for PDF: {e}")
            return

        s = self.current_student_data
        meta = {
            "student_name": student_name,
            "learner_id": s['learnerID'] or "—",
            "level": s['level'] or "—",
            "dob": s['dob'] or "—",
            "gender": s['gender'] or "—",
            "contact_info": s['studContactInfo'] or "—",
            "address": s['address'] or "—",
            "parent_name": parent['parName'] if parent else "—",
            "parent_relationship": parent['relationship'] if parent else "—",
            "parent_contact_info": parent['parContactInfo'] if parent else "—",
            "generated": datetime.now().strftime("%B %d, %Y - %I:%M %p")
        }

        try:
            generate_student_report_pdf(filepath, meta, headers, rows, report_type)
            messagebox.showinfo("Export Successful", f"PDF report successfully exported and saved to:\n\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export report PDF:\n{str(e)}")

    # Student details popup
    def show_student_detail_popup(self, student_id, learner_id=None):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT studentID, studLname, studFname, studMname, gender, dob, address, studContactInfo, level
                FROM STUDENT WHERE studentID = ?
            """, (student_id,))
            student = cursor.fetchone()
            if learner_id is None:
                cursor.execute("""
                    SELECT r.learnerID FROM REGISTRATION r
                    WHERE r.studentID = ? AND r.regStatus = 'Active'
                    ORDER BY r.registrationID DESC LIMIT 1
                """, (student_id,))
                reg = cursor.fetchone()
                learner_id = reg['learnerID'] if reg else "N/A"
            cursor.execute("""
                SELECT parName, parContactInfo, relationship
                FROM PARENT WHERE studentID = ?
            """, (student_id,))
            parent = cursor.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve student details: {e}")
            return

        if not student:
            messagebox.showerror("Error", "Student not found.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title(f"Student Profile - {student['studFname']} {student['studLname']}")
        popup.geometry("680x530")
        popup.resizable(False, False)
        popup.configure(fg_color="#e4e4e4")
        popup.transient(self.winfo_toplevel())
        x = (popup.winfo_screenwidth() - 680) // 2
        y = (popup.winfo_screenheight() - 530) // 2
        popup.geometry(f"680x530+{x}+{y}")
        try:
            popup.grab_set()
        except Exception:
            pass

        top_bar = ctk.CTkFrame(popup, height=60, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar,
                     text=f"STUDENT PROFILE: {student['studFname'].upper()} {student['studLname'].upper()}",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=20, pady=15)

        container = ctk.CTkFrame(popup, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=15)

        def create_card(parent_w, title):
            card = ctk.CTkFrame(parent_w, fg_color="#ffffff", corner_radius=12,
                                border_width=1, border_color="#cbd5e1")
            card.pack(fill="x", pady=(0, 15))
            acc = ctk.CTkFrame(card, width=5, fg_color="transparent")
            acc.pack(side="left", fill="y", padx=(10, 0), pady=10)
            ctk.CTkFrame(acc, width=5, fg_color="#15165e", corner_radius=2.5).pack(fill="both", expand=True)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=10)
            ctk.CTkLabel(inner, text=title,
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color="#15165e").pack(anchor="w", pady=(0, 8))
            return inner

        def add_row(parent_w, grid_w, row_idx, label, val):
            rf = ctk.CTkFrame(grid_w, fg_color="transparent")
            rf.grid(row=row_idx // 2, column=row_idx % 2, sticky="ew", pady=3, padx=5)
            ctk.CTkLabel(rf, text=f"{label}:",
                         font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                         text_color="#64748b", width=105, anchor="w").pack(side="left")
            ctk.CTkLabel(rf, text=str(val),
                         font=ctk.CTkFont(family="Inter", size=12),
                         text_color="#0f172a", anchor="w").pack(side="left", fill="x", expand=True)

        stud_inner = create_card(container, "STUDENT INFORMATION")
        grid_s = ctk.CTkFrame(stud_inner, fg_color="transparent")
        grid_s.pack(fill="x")
        grid_s.columnconfigure(0, weight=1)
        grid_s.columnconfigure(1, weight=1)
        add_row(stud_inner, grid_s, 0, "Learner ID", learner_id)
        add_row(stud_inner, grid_s, 1, "Full Name",
                f"{student['studLname']}, {student['studFname']} {student['studMname'] or ''}")
        add_row(stud_inner, grid_s, 2, "Grade Level", student['level'] or "Unassigned")
        add_row(stud_inner, grid_s, 3, "Gender", student['gender'])
        add_row(stud_inner, grid_s, 4, "Date of Birth", student['dob'])
        add_row(stud_inner, grid_s, 5, "Contact Information", student['studContactInfo'] or "—")
        addr_f = ctk.CTkFrame(stud_inner, fg_color="transparent")
        addr_f.pack(fill="x", pady=(8, 0), padx=5)
        ctk.CTkLabel(addr_f, text="Full Address:",
                     font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                     text_color="#64748b", width=105, anchor="w").pack(side="left")
        ctk.CTkLabel(addr_f, text=student['address'] or "—",
                     font=ctk.CTkFont(family="Inter", size=12),
                     text_color="#0f172a", anchor="w", wraplength=480).pack(side="left", fill="x", expand=True)

        par_inner = create_card(container, "PARENT / GUARDIAN INFORMATION")
        if parent:
            grid_p = ctk.CTkFrame(par_inner, fg_color="transparent")
            grid_p.pack(fill="x")
            grid_p.columnconfigure(0, weight=1)
            grid_p.columnconfigure(1, weight=1)
            add_row(par_inner, grid_p, 0, "Parent Name", parent['parName'])
            add_row(par_inner, grid_p, 1, "Relationship", parent['relationship'])
            add_row(par_inner, grid_p, 2, "Contact Information", parent['parContactInfo'] or "—")
        else:
            ctk.CTkLabel(par_inner,
                         text="No parent/guardian information found.",
                         font=ctk.CTkFont(family="Inter", size=12, slant="italic"),
                         text_color="#ef4444").pack(anchor="w", pady=5)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 15))
        ctk.CTkButton(btn_frame, text="CLOSE PROFILE",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      fg_color="#374151", hover_color="#1f2937", text_color="#ffffff",
                      width=160, height=38, corner_radius=8,
                      command=popup.destroy).pack(anchor="center")

    def back_to_dashboard(self):
        d = self.master.master
        self.destroy()
        if hasattr(d, "_show_welcome"):
            d._show_welcome()
