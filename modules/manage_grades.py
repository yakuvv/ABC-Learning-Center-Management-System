# modules/manage_grades.py
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from PIL import Image
import database
from utils.pdf_generator import generate_grades_pdf

class ManageGrades(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.grade_entries = {}  # Keys: (detailID, quarter) -> CTkEntry
        self.final_labels = {}   # Keys: detailID -> CTkLabel
        self.is_editable = True
        self.card_widgets = []
        self._ind_suggestions_rows = []
        self.create_ui()

    def _combo(self, parent, values, **kwargs):
        return ctk.CTkComboBox(
            parent,
            values=values,
            height=35, corner_radius=0,
            fg_color="#ffffff", text_color="#000000",
            button_color="#000000", button_hover_color="#222222",
            dropdown_fg_color="#ffffff", dropdown_text_color="black",
            dropdown_hover_color="#cbd5e1",
            border_width=0,
            state="readonly",
            **kwargs
        )

    def create_ui(self):
        # Top bar
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkButton(top_bar, text="← back to Dashboard",
                      font=ctk.CTkFont(family="Inter", size=14),
                      fg_color="transparent", text_color="#ffffff",
                      hover_color="#22259c", width=150, height=40,
                      corner_radius=8, command=self.back_to_dashboard
                      ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(top_bar, text="Manage Grades",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(55, 55))
            ctk.CTkLabel(top_bar, image=ctk_logo, text="").pack(side="right", padx=30)
        else:
            ctk.CTkLabel(top_bar, text="ABC",
                         font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                         text_color="#122aff").pack(side="right", padx=30)

        # Workspace
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Tabs selector (Sleek Apple-style Segments control matching profile_students.py)
        tab_selector_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(0, 15))

        # 400px pill containing two buttons (190px each + margins)
        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1", width=400, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.class_tab_btn = ctk.CTkButton(
            tab_pill, text="Class Grades",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#122aff", text_color="#ffffff",
            corner_radius=19, height=38, width=190,
            command=lambda: self.switch_tab("class")
        )
        self.class_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.ind_tab_btn = ctk.CTkButton(
            tab_pill, text="Individual Grades",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="transparent", text_color="#374151",
            corner_radius=19, height=38, width=190,
            command=lambda: self.switch_tab("individual")
        )
        self.ind_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        # ----- TAB 1: CLASS GRADING SHEET -----
        self.class_tab_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.class_tab_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.class_tab_frame, text="Filter Class",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 4))

        # Main filter card
        filter_card = ctk.CTkFrame(self.class_tab_frame, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=90)
        filter_card.pack(fill="x", pady=(0, 10))
        filter_card.pack_propagate(False)

        accent_container = ctk.CTkFrame(filter_card, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        filter_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_inner.pack(fill="both", expand=True, padx=15, pady=10)

        for col in range(4):
            filter_inner.grid_columnconfigure(col, weight=1)

        # Grade Level Filter
        ctk.CTkLabel(filter_inner, text="Grade Level",
                     font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="#444444").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.grade_combo = self._combo(filter_inner,
            [f"Grade {i}" for i in range(1, 13)],
            command=self.on_grade_changed)
        self.grade_combo.set("Grade 7")
        self.grade_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        # Section Filter
        ctk.CTkLabel(filter_inner, text="Section",
                     font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="#444444").grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.section_combo = self._combo(filter_inner, ["A", "B", "C", "D"])
        self.section_combo.set("A")
        self.section_combo.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        # Semester Filter
        self.term_label = ctk.CTkLabel(filter_inner, text="Semester",
                                       font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                                       text_color="#444444")
        self.term_label.grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.term_label.grid_remove()

        self.term_combo = self._combo(filter_inner, ["1st Semester", "2nd Semester"])
        self.term_combo.set("")
        self.term_combo.configure(state="disabled")
        self.term_combo.grid(row=1, column=2, sticky="ew", padx=(0, 8))
        self.term_combo.grid_remove()

        # School Year Filter
        ctk.CTkLabel(filter_inner, text="School Year",
                     font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="#444444").grid(row=0, column=3, sticky="w")
        self.sy_combo = self._combo(filter_inner,
            ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023",
             "2023-2024", "2024-2025", "2025-2026", "2026-2027", "2027-2028",
             "2028-2029", "2029-2030"])
        self.sy_combo.set("2025-2026")
        self.sy_combo.grid(row=1, column=3, sticky="ew")

        # Load Students & Class Search Bar (placed side by side for a clean layout)
        controls_row = ctk.CTkFrame(self.class_tab_frame, fg_color="transparent")
        controls_row.pack(fill="x", pady=(0, 10))

        # Search Bar on the Left
        self.class_search_entry = ctk.CTkEntry(
            controls_row,
            placeholder_text="🔍 Filter sheet below by student name or school ID...",
            height=40, corner_radius=8,
            fg_color="#ffffff", text_color="black",
            border_width=1, border_color="#cbd5e1",
            font=ctk.CTkFont(family="Inter", size=13)
        )
        self.class_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.class_search_entry.bind("<KeyRelease>", self.filter_class_sheet)

        # Load Students on the Right
        ctk.CTkButton(controls_row, text="🔍 LOAD STUDENTS",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      height=40, width=160, corner_radius=8,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.load_students
                      ).pack(side="right")

        # Scrollable container
        ctk.CTkLabel(self.class_tab_frame, text="Class Grading Sheet",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(5, 4))

        self.scroll_container = ctk.CTkScrollableFrame(self.class_tab_frame, fg_color="transparent", corner_radius=0)
        self.scroll_container.pack(fill="both", expand=True, pady=(0, 10))

        # Bottom Controls
        self.bottom_bar = ctk.CTkFrame(self.class_tab_frame, fg_color="transparent")
        self.bottom_bar.pack(fill="x", pady=(10, 0))

        self.save_btn = ctk.CTkButton(self.bottom_bar, text="💾 SAVE ALL GRADES",
                                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                      height=45, width=200, corner_radius=8,
                                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                                      command=self.save_grades)
        self.save_btn.pack(side="right", padx=(10, 0))

        self.edit_btn = ctk.CTkButton(self.bottom_bar, text="✏️ EDIT / UPDATE GRADES",
                                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                      height=45, width=220, corner_radius=8,
                                      fg_color="#f59e0b", hover_color="#d97706", text_color="#ffffff",
                                      command=self.unlock_grades)
        self.edit_btn.pack(side="right", padx=(10, 0))
        self.edit_btn.pack_forget()

        ctk.CTkButton(self.bottom_bar, text="📄 EXPORT GRADE SHEET (PDF)",
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      height=45, width=240, corner_radius=8,
                      fg_color="#15165e", hover_color="#22259c", text_color="#ffffff",
                      command=self.export_grades_pdf
                      ).pack(side="left")

        # ----- TAB 2: INDIVIDUAL STUDENT GRADES -----
        self.individual_tab_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        # Kept hidden initially

        # Search Card
        search_card = ctk.CTkFrame(self.individual_tab_frame, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        search_card.pack(fill="x", pady=(0, 10))

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(padx=20, pady=15, fill="x")

        ctk.CTkLabel(
            search_inner, text="🔍 Search Student for Individual Grades",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#15165e"
        ).pack(anchor="w", pady=(0, 5))

        self.ind_search_entry = ctk.CTkEntry(
            search_inner,
            placeholder_text="Type Student Name or Student ID...",
            height=40, corner_radius=8,
            fg_color="#f8fafc", text_color="black",
            border_width=1, border_color="#cbd5e1",
            font=ctk.CTkFont(family="Inter", size=13)
        )
        self.ind_search_entry.pack(fill="x")
        self.ind_search_entry.bind("<KeyRelease>", self.on_ind_search_key)
        self.ind_search_entry.bind("<FocusOut>", lambda e: self.after(250, self.hide_ind_suggestions))

        # Suggestions Dropdown
        self.ind_suggest_frame = ctk.CTkFrame(search_inner, fg_color="#ffffff", border_width=1, border_color="#cbd5e1", corner_radius=8)
        self.ind_suggest_lbox = tk.Listbox(
            self.ind_suggest_frame,
            bg="#ffffff", fg="#1e293b",
            font=("Inter", 11),
            bd=0, highlightthickness=0,
            selectbackground="#122aff", selectforeground="#ffffff",
            activestyle="none"
        )
        self.ind_suggest_lbox.pack(fill="both", expand=True, padx=2, pady=2)
        self.ind_suggest_lbox.bind("<<ListboxSelect>>", self.on_ind_suggestion_select)

        # Workspace Container for individual student details / card
        self.report_card_container = ctk.CTkFrame(self.individual_tab_frame, fg_color="transparent")
        self.report_card_container.pack(fill="both", expand=True, pady=10)

        # Initial placeholders
        self.show_class_placeholder()
        self.show_ind_placeholder()

        # Trigger initial settings
        self.on_grade_changed("Grade 7")

    def switch_tab(self, tab_target):
        if tab_target == "class":
            self.class_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.ind_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.individual_tab_frame.pack_forget()
            self.class_tab_frame.pack(fill="both", expand=True)
        else:
            self.class_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.ind_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.class_tab_frame.pack_forget()
            self.individual_tab_frame.pack(fill="both", expand=True)

    def on_grade_changed(self, choice):
        if choice in [f"Grade {i}" for i in range(1, 11)]:
            self.term_label.grid_remove()
            self.term_combo.grid_remove()
            self.term_combo.configure(values=[])
            self.term_combo.set("")
            self.term_combo.configure(state="disabled")
            self.section_combo.configure(values=["A", "B", "C", "D"])
            self.section_combo.set("A")
        else:
            self.term_label.grid(row=0, column=2, sticky="w", padx=(0, 8))
            self.term_combo.grid(row=1, column=2, sticky="ew", padx=(0, 8))
            self.term_combo.configure(state="readonly")
            self.term_combo.configure(values=["1st Semester", "2nd Semester"])
            self.term_combo.set("1st Semester")
            self.section_combo.configure(values=["STEM-A", "ABM-A", "HUMSS-A"])
            self.section_combo.set("STEM-A")

    def show_class_placeholder(self):
        for w in self.scroll_container.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.scroll_container,
            text="Please configure the class filters above and click 'LOAD STUDENTS'.",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#64748b",
            justify="center"
        ).pack(expand=True, pady=80)

    def show_ind_placeholder(self):
        for w in self.report_card_container.winfo_children():
            w.destroy()
        
        lbl_ph = ctk.CTkLabel(
            self.report_card_container,
            text="Please search and select a student above to review their individual grades.",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#64748b",
            justify="center"
        )
        lbl_ph.pack(expand=True, pady=80)

    def on_ind_search_key(self, event):
        val = self.ind_search_entry.get().strip()
        if len(val) < 2:
            self.hide_ind_suggestions()
            return
            
        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT e.enrollmentID, e.studentID, e.schoolID, s.studLname, s.studFname, s.studMname,
                       e.gradeLevel, e.section, e.schoolYear, e.term
                FROM ENROLLMENT e
                JOIN STUDENT s USING (studentID)
                WHERE e.enrStatus = 'Active' AND (
                    e.schoolID LIKE ? OR
                    s.studFname LIKE ? OR
                    s.studLname LIKE ?
                )
                ORDER BY s.studLname, s.studFname
                LIMIT 20
            """, (f"%{val}%", f"%{val}%", f"%{val}%"))
            rows = cursor.fetchall()
            
            self._ind_suggestions_rows = rows
            
            if rows:
                self.ind_suggest_lbox.delete(0, tk.END)
                for r in rows:
                    mname = f" {r['studMname'][0]}." if (r['studMname'] is not None and r['studMname'] != "") else ""
                    lbl = f" {r['studFname']}{mname} {r['studLname']}  (School ID: {r['schoolID']} | {r['gradeLevel']} - {r['section']})"
                    self.ind_suggest_lbox.insert(tk.END, lbl)
                self.ind_suggest_lbox.config(height=min(len(rows), 6))
                self.ind_suggest_frame.pack(fill="x", after=self.ind_search_entry, pady=(4, 0))
            else:
                self.hide_ind_suggestions()
        except Exception as e:
            print("Error loading suggestions:", e)
        finally:
            conn.close()

    def hide_ind_suggestions(self):
        self.ind_suggest_frame.pack_forget()

    def on_ind_suggestion_select(self, event):
        sel = self.ind_suggest_lbox.curselection()
        if not sel:
            return
        row = self._ind_suggestions_rows[sel[0]]
        self.ind_search_entry.delete(0, tk.END)
        self.hide_ind_suggestions()
        self.load_individual_report_card(row)

    def reload_rc_semester(self, r):
        selected_term = self.rc_term_combo.get()
        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT e.enrollmentID, e.studentID, e.schoolID, s.studLname, s.studFname, s.studMname,
                       e.gradeLevel, e.section, e.schoolYear, e.term
                FROM ENROLLMENT e
                JOIN STUDENT s USING (studentID)
                WHERE e.studentID = ? AND e.gradeLevel = ? AND e.schoolYear = ? AND e.term = ? AND e.enrStatus = 'Active'
            """, (r['studentID'], r['gradeLevel'], r['schoolYear'], selected_term))
            row = cursor.fetchone()
            if row:
                self.load_individual_report_card(row)
            else:
                messagebox.showinfo("Not Found", f"No active enrollment record found for this student in {selected_term}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch term:\n{e}")
        finally:
            conn.close()

    def load_individual_report_card(self, r):
        for w in self.report_card_container.winfo_children():
            w.destroy()

        mname = f" {r['studMname'][0]}." if (r['studMname'] is not None and r['studMname'] != "") else ""
        full_name = f"{r['studFname']}{mname} {r['studLname']}"
        grade = r['gradeLevel']
        section = r['section']
        school_year = r['schoolYear']
        semester = r['term']

        is_shs = grade in ["Grade 11", "Grade 12"]

        rc_card = ctk.CTkFrame(self.report_card_container, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        rc_card.pack(fill="both", expand=True, padx=5, pady=5)

        rc_header = ctk.CTkFrame(rc_card, fg_color="#15165e", corner_radius=8, height=32)
        rc_header.pack(fill="x", side="top", padx=10, pady=(10, 5))
        rc_header.pack_propagate(False)

        accent = ctk.CTkFrame(rc_header, width=4, height=18, fg_color="#122aff", corner_radius=2)
        accent.pack(side="left", padx=(8, 0), pady=7)

        ctk.CTkLabel(
            rc_header,
            text=f"🎓  STUDENT REPORT CARD  •  {full_name.upper()}  (School ID: {r['schoolID']})",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=10, pady=5)

        meta_row = ctk.CTkFrame(rc_card, fg_color="#f8fafc", height=38)
        meta_row.pack(fill="x", side="top")
        meta_row.pack_propagate(False)

        meta_items = [
            ("Grade Level", grade),
            ("Section", section),
            ("School Year", school_year)
        ]
        if is_shs and semester:
            meta_items.append(("Semester", semester))

        for (label, val) in meta_items:
            ctk.CTkLabel(
                meta_row, text=f"{label}:  {val}",
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#475569"
            ).pack(side="left", padx=20)

        # Upper right corner Semester / Term Filter Dropdown for Senior High School (Grade 11/12)
        if is_shs:
            filter_frame = ctk.CTkFrame(meta_row, fg_color="transparent")
            filter_frame.pack(side="right", padx=20, pady=4)

            ctk.CTkLabel(
                filter_frame, text="Select Term: ",
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#475569"
            ).pack(side="left")

            self.rc_term_combo = ctk.CTkComboBox(filter_frame, values=["1st Semester", "2nd Semester"], width=130, height=28, state="readonly")
            self.rc_term_combo.set(semester if semester else "1st Semester")
            self.rc_term_combo.pack(side="left", padx=5)

            load_btn = ctk.CTkButton(
                filter_frame, text="LOAD", width=60, height=28,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                fg_color="#122aff", hover_color="#0b1eb3",
                command=lambda: self.reload_rc_semester(r)
            )
            load_btn.pack(side="left", padx=5)

        ctk.CTkFrame(rc_card, height=1, fg_color="#cbd5e1").pack(fill="x")

        tbl_scroll = ctk.CTkScrollableFrame(rc_card, fg_color="transparent")
        tbl_scroll.pack(fill="both", expand=True, padx=20, pady=15)

        grid_frame = ctk.CTkFrame(tbl_scroll, fg_color="transparent")
        grid_frame.pack(fill="x")

        # Quarters are unified to 1st Qtr - 4th Qtr + Final Grade for both Elementary/Junior High and Senior High
        grid_frame.columnconfigure(0, weight=4, uniform="rc_col")
        grid_frame.columnconfigure(1, weight=1, uniform="rc_col")
        grid_frame.columnconfigure(2, weight=1, uniform="rc_col")
        grid_frame.columnconfigure(3, weight=1, uniform="rc_col")
        grid_frame.columnconfigure(4, weight=1, uniform="rc_col")
        grid_frame.columnconfigure(5, weight=2, uniform="rc_col")
        headers = ["Subject Name", "1st Qtr", "2nd Qtr", "3rd Qtr", "4th Qtr", "Final Grade"]
        quarters = ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"]

        for col_idx, h_text in enumerate(headers):
            lbl = tk.Label(grid_frame, text=h_text,
                           font=("Inter", 11, "bold"),
                           fg="#475569", bg="#ffffff")
            lbl.grid(row=0, column=col_idx, sticky="ew" if col_idx > 0 else "w", pady=(0, 6))

        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT d.detailID, sub.subjectID, sub.subjectName
                FROM DETAIL d
                JOIN SUBJECT sub USING (subjectID)
                WHERE d.enrollmentID = ?
                ORDER BY sub.subjectName
            """, (r['enrollmentID'],))
            subjects = cursor.fetchall()

            subjects_data_for_pdf = []

            for sub_idx, sub in enumerate(subjects):
                row_idx = sub_idx + 1
                row_bg = "#f8fafc" if sub_idx % 2 == 0 else "#ffffff"

                # Native tk.Frame for maximum speed
                row_frame = tk.Frame(grid_frame, bg=row_bg, bd=0)
                row_frame.grid(row=row_idx, column=0, columnspan=len(headers), sticky="ew", pady=3)

                row_frame.columnconfigure(0, weight=4, uniform="rc_col")
                row_frame.columnconfigure(1, weight=1, uniform="rc_col")
                row_frame.columnconfigure(2, weight=1, uniform="rc_col")
                row_frame.columnconfigure(3, weight=1, uniform="rc_col")
                row_frame.columnconfigure(4, weight=1, uniform="rc_col")
                row_frame.columnconfigure(5, weight=2, uniform="rc_col")

                lbl_sub = tk.Label(row_frame, text=sub['subjectName'],
                                   font=("Inter", 11, "bold"),
                                   fg="#1e293b", bg=row_bg, anchor="w")
                lbl_sub.grid(row=0, column=0, sticky="w", padx=10, pady=8)

                cursor.execute("SELECT quarter, gradeValue FROM GRADE WHERE detailID = ?", (sub['detailID'],))
                grade_map = {gr['quarter']: gr['gradeValue'] for gr in cursor.fetchall()}

                vals = []
                q_vals_pdf = {}

                for q_idx, quarter in enumerate(quarters):
                    existing_val = grade_map.get(quarter)
                    val_str = "—"
                    if existing_val is not None:
                        val_str = f"{int(existing_val) if existing_val.is_integer() else existing_val}"
                        vals.append(existing_val)

                    q_vals_pdf[quarter] = val_str

                    lbl_q = tk.Label(row_frame, text=val_str,
                                     font=("Inter", 11),
                                     fg="black", bg=row_bg)
                    lbl_q.grid(row=0, column=q_idx+1, pady=8, sticky="ew")

                final_str = "—"
                if vals:
                    avg = sum(vals) / len(vals)
                    final_str = f"{avg:.1f}"
                    text_color = "#122aff" if avg >= 75 else "#ef4444"
                else:
                    text_color = "#64748b"

                lbl_final = tk.Label(row_frame, text=final_str,
                                     font=("Inter", 11, "bold"),
                                     fg=text_color, bg=row_bg)
                lbl_final.grid(row=0, column=len(headers)-1, pady=8, sticky="ew")

                subjects_data_for_pdf.append({
                    'subjectName': sub['subjectName'],
                    '1st': q_vals_pdf.get("1st Quarter", "—"),
                    '2nd': q_vals_pdf.get("2nd Quarter", "—"),
                    '3rd': q_vals_pdf.get("3rd Quarter", "—"),
                    '4th': q_vals_pdf.get("4th Quarter", "—"),
                    'final': final_str
                })

            btn_panel = ctk.CTkFrame(rc_card, fg_color="transparent", height=60)
            btn_panel.pack(fill="x", side="bottom", padx=20, pady=15)

            ctk.CTkButton(
                btn_panel, text="📄 EXPORT STUDENT REPORT CARD (PDF)",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                height=45, fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                corner_radius=8,
                command=lambda: self.export_individual_pdf(r, full_name, subjects_data_for_pdf)
            ).pack(side="right")

        except Exception as e:
            print("Error loading student report card:", e)
        finally:
            conn.close()

    def export_individual_pdf(self, r, full_name, subjects_list):
        grade_lvl = r['gradeLevel']
        school_year = r['schoolYear']
        semester = r['term']

        initial_file = f"Report_Card_{full_name.replace(' ', '_')}_{grade_lvl.replace(' ', '_')}_{school_year}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=initial_file,
            title="Save Student Report Card PDF"
        )

        if filepath:
            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT tutorFname, tutorLname FROM TUTOR LIMIT 1")
                tutor_row = cursor.fetchone()
                conn.close()

                tutor_name = "—"
                if tutor_row:
                    tutor_name = f"{tutor_row['tutorFname']} {tutor_row['tutorLname']}"

                grades_data = [{
                    'name': full_name,
                    'studentID': r['studentID'],
                    'subjects': subjects_list
                }]

                filter_info = {
                    'subject': "OFFICIAL STUDENT REPORT CARD",
                    'grade_level': grade_lvl,
                    'term': semester if semester else "Full Year",
                    'school_year': school_year,
                    'tutor_name': tutor_name,
                    'date_printed': datetime.now().strftime("%B %d, %Y")
                }

                generate_grades_pdf(filepath, filter_info, grades_data)
                messagebox.showinfo("Success", f"Student Report Card PDF generated successfully!\nPath: {filepath}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report card PDF:\n{e}")

    def load_students(self):
        # Clear existing widgets
        for w in self.scroll_container.winfo_children():
            w.destroy()

        self.grade_entries.clear()
        self.final_labels.clear()
        self.card_widgets.clear()
        self.loaded_students_list = []
        self.is_editable = True

        self.save_btn.configure(state="normal")
        self.edit_btn.pack_forget()

        grade = self.grade_combo.get()
        section = self.section_combo.get()
        semester = self.term_combo.get()
        school_year = self.sy_combo.get()

        if not grade or not section or not school_year:
            return

        is_shs = grade in ["Grade 11", "Grade 12"]

        # Show native loading label immediately and refresh UI to prevent glitchy freezing
        loading_lbl = ctk.CTkLabel(
            self.scroll_container,
            text="⏳ Loading class grading sheet, please wait...",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#122aff"
        )
        loading_lbl.pack(pady=50)
        self.update()

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            # SINGLE highly-optimized JOIN query to fetch everything in one pass
            query = """
                SELECT e.enrollmentID, e.studentID, e.schoolID, s.studLname, s.studFname, s.studMname,
                       d.detailID, sub.subjectID, sub.subjectName,
                       g.quarter, g.gradeValue
                FROM ENROLLMENT e
                JOIN STUDENT s USING (studentID)
                JOIN DETAIL d ON e.enrollmentID = d.enrollmentID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                LEFT JOIN GRADE g ON d.detailID = g.detailID
                WHERE e.gradeLevel = ? AND e.section = ? AND e.schoolYear = ? AND e.enrStatus = 'Active'
            """
            params = [grade, section, school_year]
            if is_shs and semester:
                query += " AND e.term = ?"
                params.append(semester)

            query += " ORDER BY s.studLname, s.studFname, sub.subjectName"
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

            loading_lbl.destroy()

            if not rows:
                ctk.CTkLabel(self.scroll_container, text="No enrolled students found for the selected class.",
                             font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                             text_color="#64748b").pack(pady=40)
                conn.close()
                return

            # Group flat SQL rows into Python data structures in microseconds
            students_map = {}
            for row in rows:
                sid = row['studentID']
                if sid not in students_map:
                    mname = row['studMname'] or ""
                    middle = f" {mname[0]}." if mname else ""
                    full_name = f"{row['studLname']}, {row['studFname']}{middle}"
                    students_map[sid] = {
                        'studentID': row['schoolID'],
                        'name': full_name,
                        'enrollmentID': row['enrollmentID'],
                        'subjects': {}
                    }

                did = row['detailID']
                if did not in students_map[sid]['subjects']:
                    students_map[sid]['subjects'][did] = {
                        'detailID': did,
                        'subjectID': row['subjectID'],
                        'subjectName': row['subjectName'],
                        'grades': {}
                    }

                q = row['quarter']
                if q:
                    students_map[sid]['subjects'][did]['grades'][q] = row['gradeValue']

            # Extract students list preserving the order sorted by SQL
            students_list = []
            seen_sids = []
            for row in rows:
                sid = row['studentID']
                if sid not in seen_sids:
                    seen_sids.append(sid)
                    s_data = students_map[sid]
                    subj_list = list(s_data['subjects'].values())
                    subj_list.sort(key=lambda x: x['subjectName'])
                    s_data['subjects'] = subj_list
                    students_list.append(s_data)

            # Define headers and quarters (Unified to 1st Qtr - 4th Qtr layout for all grade levels)
            headers = ["Subject Name", "1st Qtr", "2nd Qtr", "3rd Qtr", "4th Qtr", "Final Grade"]
            quarters = ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"]

            # Render student cards
            for s_idx, student in enumerate(students_list):
                card = ctk.CTkFrame(self.scroll_container, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
                card.pack(fill="x", pady=8, padx=10)

                # Save references for real-time search filtering
                self.card_widgets.append({
                    "studentID": student['studentID'],
                    "name": student['name'].lower(),
                    "widget": card
                })

                # Sleek, rounded nested header badge inside the card
                header = ctk.CTkFrame(card, fg_color="#15165e", corner_radius=8, height=32)
                header.pack(fill="x", side="top", padx=10, pady=(10, 5))
                header.pack_propagate(False)

                accent = ctk.CTkFrame(header, width=4, height=18, fg_color="#122aff", corner_radius=2)
                accent.pack(side="left", padx=(8, 0), pady=7)

                ctk.CTkLabel(header, text=f"👤  {student['name'].upper()}  (School ID: {student['studentID']})",
                             font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                             text_color="#ffffff").pack(side="left", padx=10, pady=4)

                grid_frame = ctk.CTkFrame(card, fg_color="transparent")
                grid_frame.pack(fill="x", padx=15, pady=15)

                # Set up grid columns (Unified to 1st Qtr - 4th Qtr layout for all grade levels)
                grid_frame.columnconfigure(0, weight=4, uniform="grade_col")
                grid_frame.columnconfigure(1, weight=1, uniform="grade_col")
                grid_frame.columnconfigure(2, weight=1, uniform="grade_col")
                grid_frame.columnconfigure(3, weight=1, uniform="grade_col")
                grid_frame.columnconfigure(4, weight=1, uniform="grade_col")
                grid_frame.columnconfigure(5, weight=2, uniform="grade_col")

                for col_idx, h_text in enumerate(headers):
                    lbl = tk.Label(grid_frame, text=h_text,
                                   font=("Inter", 11, "bold"),
                                   fg="#475569", bg="#ffffff")
                    lbl.grid(row=0, column=col_idx, sticky="ew" if col_idx > 0 else "w", pady=(0, 6))

                student_subjects_data = []

                for sub_idx, sub in enumerate(student['subjects']):
                    row_idx = sub_idx + 1
                    row_bg = "#f8fafc" if sub_idx % 2 == 0 else "#ffffff"

                    # Highly-optimized native tk.Frame row background to remove lag
                    row_frame = tk.Frame(grid_frame, bg=row_bg, bd=0)
                    row_frame.grid(row=row_idx, column=0, columnspan=len(headers), sticky="ew", pady=3)

                    # Unified grid layout config for row frame
                    row_frame.columnconfigure(0, weight=4, uniform="grade_col")
                    row_frame.columnconfigure(1, weight=1, uniform="grade_col")
                    row_frame.columnconfigure(2, weight=1, uniform="grade_col")
                    row_frame.columnconfigure(3, weight=1, uniform="grade_col")
                    row_frame.columnconfigure(4, weight=1, uniform="grade_col")
                    row_frame.columnconfigure(5, weight=2, uniform="grade_col")

                    lbl_sub = tk.Label(row_frame, text=sub['subjectName'],
                                       font=("Inter", 11, "bold"),
                                       fg="#1e293b", bg=row_bg, anchor="w")
                    lbl_sub.grid(row=0, column=0, sticky="w", padx=10, pady=6)

                    q_entries = []
                    
                    final_val_lbl = tk.Label(row_frame, text="—",
                                             font=("Inter", 11, "bold"),
                                             fg="#64748b", bg=row_bg)
                    final_val_lbl.grid(row=0, column=len(headers)-1, pady=6, sticky="ew")
                    self.final_labels[sub['detailID']] = final_val_lbl

                    for q_idx, quarter in enumerate(quarters):
                        ent = tk.Entry(row_frame,
                                       bg="#ffffff", fg="black",
                                       relief="flat", bd=0,
                                       highlightthickness=1,
                                       highlightcolor="#122aff",
                                       highlightbackground="#cbd5e1",
                                       font=("Inter", 11),
                                       justify="center",
                                       width=7)
                        ent.grid(row=0, column=q_idx+1, pady=6, sticky="ew", padx=5)

                        existing_val = sub['grades'].get(quarter)
                        if existing_val is not None:
                            ent.insert(0, f"{int(existing_val) if existing_val.is_integer() else existing_val}")

                        self.grade_entries[(sub['detailID'], quarter)] = ent
                        q_entries.append(ent)

                        ent.bind("<KeyRelease>", lambda e, d_id=sub['detailID'], qe=q_entries, fl=final_val_lbl: self.calculate_final_grade(d_id, qe, fl))

                    self.calculate_final_grade(sub['detailID'], q_entries, final_val_lbl)

                    student_subjects_data.append({
                        "subjectID": sub['subjectID'],
                        "subjectName": sub['subjectName'],
                        "detailID": sub['detailID'],
                        "entries": q_entries,
                        "final_label": final_val_lbl
                    })

                self.loaded_students_list.append({
                    "studentID": student['studentID'],
                    "name": student['name'],
                    "enrollmentID": student['enrollmentID'],
                    "subjects": student_subjects_data
                })

            conn.close()

            # Apply any active search filter immediately
            self.filter_class_sheet()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load grading sheet:\n{e}")

    def filter_class_sheet(self, event=None):
        query = self.class_search_entry.get().strip().lower()
        for item in self.card_widgets:
            if not query or query in str(item['studentID']).lower() or query in item['name']:
                item['widget'].pack(fill="x", pady=8, padx=10)
            else:
                item['widget'].pack_forget()

    def calculate_final_grade(self, detail_id, entries, label):
        vals = []
        for e in entries:
            val_str = e.get().strip()
            if val_str:
                try:
                    val = float(val_str)
                    if 0 <= val <= 100:
                        vals.append(val)
                except ValueError:
                    pass
        if vals:
            avg = sum(vals) / len(vals)
            label.configure(text=f"{avg:.1f}", fg="#122aff" if avg >= 75 else "#ef4444")
        else:
            label.configure(text="—", fg="#64748b")

    def save_grades(self):
        if not self.grade_entries:
            messagebox.showwarning("Warning", "No grades loaded to save.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        saved = 0
        errors = []

        try:
            cursor.execute("SELECT tutorID FROM TUTOR LIMIT 1")
            tutor_row = cursor.fetchone()
            tutor_id = tutor_row['tutorID'] if tutor_row else 1

            for (detail_id, quarter), ent in self.grade_entries.items():
                val_str = ent.get().strip()
                if not val_str:
                    cursor.execute("DELETE FROM GRADE WHERE detailID = ? AND quarter = ?", (detail_id, quarter))
                    continue

                try:
                    val = float(val_str)
                    if not (0 <= val <= 100):
                        raise ValueError()
                except ValueError:
                    errors.append(f"Invalid grade value: '{val_str}' for: {quarter}")
                    continue

                cursor.execute("""
                    INSERT INTO GRADE (detailID, tutorID, quarter, gradeValue, dateRecorded)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(detailID, quarter) DO UPDATE SET
                        gradeValue = excluded.gradeValue,
                        dateRecorded = excluded.dateRecorded
                """, (detail_id, tutor_id, quarter, val, datetime.now().strftime("%Y-%m-%d")))
                saved += 1

            conn.commit()
            self.lock_grades()

            msg = f"Successfully updated {saved} quarterly/semestral grade records."
            if errors:
                msg += "\n\nSkipped validation failures:\n" + "\n".join(errors)
            messagebox.showinfo("Success", msg)

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to save grades:\n{e}")
        finally:
            conn.close()

    def lock_grades(self):
        self.is_editable = False
        for ent in self.grade_entries.values():
            ent.configure(state="disabled", bg="#f1f5f9", fg="#334155", disabledbackground="#f1f5f9", disabledforeground="#334155")
        self.save_btn.configure(state="disabled")
        self.edit_btn.pack(side="right", padx=(10, 0))

    def unlock_grades(self):
        self.is_editable = True
        for ent in self.grade_entries.values():
            ent.configure(state="normal", bg="#ffffff", fg="black")
        self.save_btn.configure(state="normal")
        self.edit_btn.pack_forget()

    def export_grades_pdf(self):
        if not hasattr(self, 'loaded_students_list') or not self.loaded_students_list:
            messagebox.showwarning("Warning", "No students loaded to export.")
            return

        grade_lvl = self.grade_combo.get()
        section = self.section_combo.get()
        semester = self.term_combo.get()
        school_year = self.sy_combo.get()

        is_shs = grade_lvl in ["Grade 11", "Grade 12"]

        initial_file = f"Grade_Sheet_{grade_lvl.replace(' ', '_')}_{section.replace(' ', '_')}_{school_year}.pdf"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=initial_file,
            title="Save Class Grade Sheet PDF"
        )

        if filepath:
            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT tutorFname, tutorLname FROM TUTOR LIMIT 1")
                tutor_row = cursor.fetchone()
                conn.close()

                tutor_name = "—"
                if tutor_row:
                    tutor_name = f"{tutor_row['tutorFname']} {tutor_row['tutorLname']}"

                grades_data = []
                for s in self.loaded_students_list:
                    subjects_list = []
                    for sub in s['subjects']:
                        val_1 = sub['entries'][0].get().strip()
                        val_2 = sub['entries'][1].get().strip()
                        val_3 = sub['entries'][2].get().strip()
                        val_4 = sub['entries'][3].get().strip()
                        final_val = sub['final_label'].cget("text")
                        subjects_list.append({
                            'subjectName': sub['subjectName'],
                            '1st': val_1 if val_1 else "—",
                            '2nd': val_2 if val_2 else "—",
                            '3rd': val_3 if val_3 else "—",
                            '4th': val_4 if val_4 else "—",
                            'final': final_val
                        })

                    grades_data.append({
                        'name': s['name'],
                        'studentID': s['studentID'],
                        'subjects': subjects_list
                    })

                filter_info = {
                    'subject': "Class Curriculum Breakdown",
                    'grade_level': grade_lvl,
                    'term': semester if semester else "Full Year",
                    'school_year': school_year,
                    'tutor_name': tutor_name,
                    'date_printed': datetime.now().strftime("%B %d, %Y")
                }

                generate_grades_pdf(filepath, filter_info, grades_data)
                messagebox.showinfo("Success", f"Official Grade Sheet PDF generated successfully!\nPath: {filepath}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to export Grade Sheet PDF:\n{e}")

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()