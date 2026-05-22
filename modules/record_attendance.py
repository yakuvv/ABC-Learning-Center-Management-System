import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime


class AttendanceSavedPopup(ctk.CTkToplevel):
    def __init__(self, parent, saved_count, att_date, skipped_count=0):
        super().__init__(parent)
        self.title("Success")
        self.geometry("400x240")
        self.resizable(False, False)
        self.configure(fg_color="#15165e")
        self.transient(parent)
        
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        main_frame = ctk.CTkFrame(self, fg_color="#15165e", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_label = ctk.CTkLabel(
            main_frame,
            text="✓",
            font=ctk.CTkFont(family="Inter", size=48, weight="bold"),
            text_color="#00bf63"
        )
        icon_label.pack(pady=(5, 5))

        msg_label = ctk.CTkLabel(
            main_frame,
            text="Attendance Recorded",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#ffffff"
        )
        msg_label.pack(pady=(5, 5))

        details_text = f"Attendance saved for {saved_count} student(s) on {att_date}."
        if skipped_count > 0:
            details_text += f"\n({skipped_count} student(s) skipped/not enrolled)"
            
        details_label = ctk.CTkLabel(
            main_frame,
            text=details_text,
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#cbd5e1",
            wraplength=340
        )
        details_label.pack(pady=(0, 15))

        btn = ctk.CTkButton(
            main_frame,
            text="OK",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            width=120,
            height=35,
            fg_color="#122aff",
            hover_color="#0b1eb3",
            text_color="#ffffff",
            corner_radius=8,
            command=self.destroy
        )
        btn.pack()

        # Center relative to parent
        self.update_idletasks()
        try:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            x = parent_x + (parent_w - 400) // 2
            y = parent_y + (parent_h - 240) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass


class RecordAttendance(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.student_row_widgets = {}
        self.student_row_frames = {}
        self.attendance_vars = {}
        self.loaded_detail_ids = {}

        self.create_ui()

    def _combo(self, parent, values, **kwargs):
        return ctk.CTkComboBox(
            parent,
            values=values,
            height=30, corner_radius=0,
            fg_color="#ffffff", text_color="#777777",
            button_color="#000000", button_hover_color="#222222",
            dropdown_fg_color="#ffffff", dropdown_text_color="black",
            dropdown_hover_color="#cbd5e1",
            border_width=0,
            state="readonly",
            **kwargs
        )

    def _card_frame(self, parent, height=None):
        kw = {"height": height} if height else {}
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", **kw)
        
        accent_container = ctk.CTkFrame(card, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(10, 0), pady=6)
        
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=10, pady=3)
        return card, inner

    def create_ui(self):
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkButton(top_bar, text="← back to Dashboard",
                      font=ctk.CTkFont(family="Inter", size=14),
                      fg_color="transparent", text_color="#ffffff",
                      hover_color="#22259c", width=150, height=40,
                      corner_radius=8, command=self.back_to_dashboard
                      ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(top_bar, text="Record Attendance",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        from PIL import Image
        import os
        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(55, 55))
            ctk.CTkLabel(top_bar, image=ctk_logo, text="").pack(side="right", padx=30)
        else:
            ctk.CTkLabel(top_bar, text="ABC",
                         font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                         text_color="#122aff").pack(side="right", padx=30)

        # ── Pill‑style Tab Selector (Attendance / History) ──
        tab_selector = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector.pack(fill="x", pady=(20, 10))

        tab_pill = ctk.CTkFrame(tab_selector, fg_color="#cbd5e1", width=310, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        # Attendance button (active by default)
        self.attendance_tab_btn = ctk.CTkButton(tab_pill, text="Attendance",
                                             font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                             fg_color="#122aff", text_color="#ffffff",
                                             corner_radius=19, height=38, width=150,
                                             command=lambda: self.switch_attendance_tab("attendance"))
        self.attendance_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        # History button (inactive)
        self.history_tab_btn = ctk.CTkButton(tab_pill, text="History",
                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                          fg_color="transparent", text_color="#374151",
                                          corner_radius=19, height=38, width=150,
                                          command=lambda: self.switch_attendance_tab("history"))
        self.history_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        # Containers for each tab's content
        self.attendance_container = ctk.CTkFrame(self, fg_color="transparent")
        self.attendance_container.pack(fill="both", expand=True, padx=40, pady=20)

        self.history_container = ctk.CTkFrame(self, fg_color="transparent")
        self.history_container.pack(fill="both", expand=True, padx=40, pady=20)
        self.history_container.forget()  # hide history initially

        # ── History filter bar ────────────────────────────────────────────────
        hist_filter_bar = ctk.CTkFrame(self.history_container, fg_color="#f1f5f9", corner_radius=12,
                                       border_width=1, border_color="#cbd5e1")
        hist_filter_bar.pack(fill="x", padx=15, pady=(12, 6))

        def _hlabel(parent, text):
            ctk.CTkLabel(parent, text=text,
                         font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                         text_color="#64748b").pack(anchor="w", padx=(10, 0), pady=(6, 0))

        def _hcombo(parent, values, cmd=None):
            kw = {"command": cmd} if cmd else {}
            return ctk.CTkComboBox(parent, values=values, height=30, corner_radius=6,
                                   fg_color="#ffffff", text_color="#333333",
                                   button_color="#15165e", button_hover_color="#22259c",
                                   dropdown_fg_color="#ffffff", dropdown_text_color="black",
                                   dropdown_hover_color="#cbd5e1",
                                   border_width=1, border_color="#cbd5e1",
                                   state="readonly", width=145, **kw)

        filter_cols = ctk.CTkFrame(hist_filter_bar, fg_color="transparent")
        filter_cols.pack(fill="x", padx=6, pady=(4, 10))

        # CLASS
        col1 = ctk.CTkFrame(filter_cols, fg_color="transparent")
        col1.pack(side="left", padx=6)
        _hlabel(col1, "CLASS")
        self.h_class_combo = _hcombo(col1, [], cmd=self._h_on_class_changed)
        self.h_class_combo.pack()

        # SECTION
        col2 = ctk.CTkFrame(filter_cols, fg_color="transparent")
        col2.pack(side="left", padx=6)
        _hlabel(col2, "SECTION")
        self.h_section_combo = _hcombo(col2, [])
        self.h_section_combo.pack()

        # TERM
        col3 = ctk.CTkFrame(filter_cols, fg_color="transparent")
        col3.pack(side="left", padx=6)
        _hlabel(col3, "TERM")
        self.h_term_combo = _hcombo(col3, [])
        self.h_term_combo.pack()

        # SCHOOL YEAR
        col4 = ctk.CTkFrame(filter_cols, fg_color="transparent")
        col4.pack(side="left", padx=6)
        _hlabel(col4, "SCHOOL YEAR")
        self.h_sy_combo = _hcombo(col4,
            ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023",
             "2023-2024", "2024-2025", "2025-2026", "2026-2027", "2027-2028",
             "2028-2029", "2029-2030"])
        self.h_sy_combo.pack()

        # SUBJECT
        col5 = ctk.CTkFrame(filter_cols, fg_color="transparent")
        col5.pack(side="left", padx=6)
        _hlabel(col5, "SUBJECT")
        self.h_subject_combo = _hcombo(col5, [])
        self.h_subject_combo.pack()

        # Load button
        col6 = ctk.CTkFrame(filter_cols, fg_color="transparent")
        col6.pack(side="left", padx=(12, 6))
        ctk.CTkLabel(col6, text=" ", font=ctk.CTkFont(size=10)).pack(pady=(6, 0))  # spacer
        self.load_history_btn = ctk.CTkButton(col6, text="Load History",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            height=30, corner_radius=6, width=120,
            fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
            command=self.load_history)
        self.load_history_btn.pack()

        # Initialise history combos
        self._h_load_class_options()
        self.h_class_combo.set("")
        self.h_section_combo.set("")
        self.h_term_combo.set("")
        self.h_sy_combo.set("")
        self.h_subject_combo.set("")

        # Scrollable area for history records
        self.history_scroll = ctk.CTkScrollableFrame(self.history_container, fg_color="transparent", corner_radius=8)
        self.history_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        # Build the attendance tab body
        self._build_attendance_tab(self.attendance_container)

    def switch_attendance_tab(self, tab):
        """Toggle between Attendance and History tabs.
        Called by the pill‑style buttons.
        """
        # Hide both containers first
        self.attendance_container.pack_forget()
        self.history_container.pack_forget()
        if tab == "attendance":
            self.attendance_container.pack(fill="both", expand=True, padx=40, pady=20)
            self.attendance_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.history_tab_btn.configure(fg_color="transparent", text_color="#374151")
        else:
            self.history_container.pack(fill="both", expand=True, padx=40, pady=20)
            self.history_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.attendance_tab_btn.configure(fg_color="transparent", text_color="#374151")

    def load_history(self):
        """Load attendance history based on current filter selections."""
        grade = self.h_class_combo.get().strip()
        section = self.h_section_combo.get().strip()
        term = self.h_term_combo.get().strip()
        sy = self.h_sy_combo.get().strip()
        subject = self.h_subject_combo.get().strip()

        if not all([grade, section, term, sy, subject]):
            messagebox.showwarning("Warning", "Please select Class, Section, Term, School Year, and Subject before loading history.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT att.attDate, s.studLname, s.studFname, s.studMname, att.attStatus
                FROM ATTENDANCE att
                JOIN DETAIL d ON att.detailID = d.detailID
                JOIN ENROLLMENT e ON d.enrollmentID = e.enrollmentID
                JOIN STUDENT s ON e.studentID = s.studentID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE e.gradeLevel = ? AND e.section = ? AND e.term = ? AND e.schoolYear = ? AND sub.subjectName = ?
                ORDER BY att.attDate DESC, s.studLname, s.studFname
            """, (grade, section, term, sy, subject))
            rows = cursor.fetchall()
            conn.close()

            # Clear previous content
            for w in self.history_scroll.winfo_children():
                if w != self.load_history_btn:
                    w.destroy()

            if not rows:
                ctk.CTkLabel(self.history_scroll, text="No attendance records found for the selected filters.",
                    font=ctk.CTkFont(family="Inter", size=13), text_color="#64748b").pack(pady=20)
                return

            # Header
            hdr = ctk.CTkFrame(self.history_scroll, fg_color="#eef2f7", corner_radius=8, height=34)
            hdr.pack(fill="x", pady=(0,5))
            hdr.pack_propagate(False)
            w_date, w_name, w_status = 80, 250, 80
            bold = ctk.CTkFont(family="Inter", size=12, weight="bold")
            ctk.CTkLabel(hdr, text="DATE", font=bold, width=w_date).pack(side="left", padx=(10,0))
            ctk.CTkLabel(hdr, text="STUDENT", font=bold, width=w_name).pack(side="left")
            ctk.CTkLabel(hdr, text="STATUS", font=bold, width=w_status).pack(side="left", padx=(4,0))

            # Rows
            for row in rows:
                date_str = row['attDate']
                lname = row['studLname']
                fname = row['studFname']
                mname = row['studMname']
                middle = f" {mname[0]}." if mname else ""
                full_name = f"{lname}, {fname}{middle}"
                status = row['attStatus']

                row_frame = ctk.CTkFrame(self.history_scroll, fg_color="#ffffff", corner_radius=8, height=34)
                row_frame.pack(fill="x", pady=2, padx=2)
                row_frame.pack_propagate(False)
                ctk.CTkLabel(row_frame, text=date_str, font=bold, width=w_date).pack(side="left", padx=(10,0))
                ctk.CTkLabel(row_frame, text=full_name, font=bold, width=w_name, anchor="w").pack(side="left")
                ctk.CTkLabel(row_frame, text=status, font=bold, width=w_status, anchor="w").pack(side="left", padx=(4,0))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load attendance history:\n{e}")

    # ── History tab helper methods ──────────────────────────────────────────

    def _h_load_class_options(self):
        """Populate the History CLASS combo from the database."""
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT gradeLevel
                FROM ENROLLMENT
                WHERE enrStatus = 'Active'
                ORDER BY CAST(SUBSTR(gradeLevel, 7) AS INTEGER), gradeLevel
            """)
            rows = cursor.fetchall()
            conn.close()
            options = [r['gradeLevel'] for r in rows if r['gradeLevel']]
            if not options:
                options = [f"Grade {i}" for i in range(1, 13)]
        except Exception:
            options = [f"Grade {i}" for i in range(1, 13)]
        self.h_class_combo.configure(values=options)

    def _h_on_class_changed(self, choice):
        """Respond to CLASS selection change in the History filter bar."""
        if not choice:
            self.h_section_combo.configure(values=[])
            self.h_section_combo.set("")
            self.h_term_combo.configure(values=[])
            self.h_term_combo.set("")
            self.h_subject_combo.configure(values=[])
            self.h_subject_combo.set("")
            return

        # Set term options based on grade level
        is_grade_1_to_10 = choice in [f"Grade {i}" for i in range(1, 11)]
        if is_grade_1_to_10:
            self.h_term_combo.configure(values=["Full Year"])
            self.h_term_combo.set("Full Year")
        else:
            self.h_term_combo.configure(values=["1st Semester", "2nd Semester"])
            if self.h_term_combo.get() not in ["1st Semester", "2nd Semester"]:
                self.h_term_combo.set("1st Semester")

        # Load sections for the chosen grade
        sections = []
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT section
                FROM ENROLLMENT
                WHERE gradeLevel = ? AND enrStatus = 'Active'
                ORDER BY section
            """, (choice,))
            rows = cursor.fetchall()
            conn.close()
            sections = [r['section'] for r in rows if r['section']]
        except Exception:
            pass

        if not sections:
            if is_grade_1_to_10:
                sections = ["A", "B", "C", "D"]
            elif choice in ["Grade 11", "Grade 12"]:
                sections = ["ABM-A", "HUMSS-A", "STEM-A"]
            else:
                sections = ["A", "B"]

        self.h_section_combo.configure(values=sections)
        self.h_section_combo.set(sections[0] if sections else "")

        # Load subjects based on grade/section/term
        self._h_load_subjects()

    def _h_load_subjects(self):
        """Load subject options for the History filter based on current grade/section/term."""
        grade = self.h_class_combo.get().strip()
        section = self.h_section_combo.get().strip()
        term = self.h_term_combo.get().strip()
        if not grade:
            self.h_subject_combo.configure(values=[])
            self.h_subject_combo.set("")
            return
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            is_shs = grade in ["Grade 11", "Grade 12"]
            if is_shs:
                sem_num = 1 if "1st" in term else 2
                strand = next((s for s in ["STEM", "ABM", "HUMSS"] if s in section.upper()), "STEM")
                cursor.execute("""
                    SELECT DISTINCT subjectName FROM SUBJECT
                    WHERE gradeLevel = ? AND strand = ? AND semester = ? AND isActive = 1
                    ORDER BY subjectName
                """, (grade, strand, sem_num))
            else:
                cursor.execute("""
                    SELECT DISTINCT subjectName FROM SUBJECT
                    WHERE gradeLevel = ? AND isActive = 1
                    ORDER BY subjectName
                """, (grade,))
            rows = cursor.fetchall()
            conn.close()
            subjects = [r['subjectName'] for r in rows]
        except Exception:
            subjects = []
        self.h_subject_combo.configure(values=subjects)
        self.h_subject_combo.set(subjects[0] if subjects else "")

    def _build_attendance_tab(self, workspace):
        """Build the full Attendance tab UI inside workspace frame."""
        split_body = ctk.CTkFrame(workspace, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # ── LEFT PANEL ───────────────────────────────────────────────────────
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=340)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)

        def section_label(parent, text):
            ctk.CTkLabel(parent, text=text,
                         font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                         text_color="black").pack(anchor="w", pady=(6, 1))

        # CLASS Dropdown
        section_label(left_panel, "CLASS")
        class_card, class_inner = self._card_frame(left_panel, height=42)
        class_card.pack(fill="x")
        class_card.pack_propagate(False)
        self.class_combo = self._combo(class_inner, [], command=self.on_class_changed)
        self.class_combo.pack(fill="x")

        # SECTION Dropdown
        section_label(left_panel, "SECTION")
        section_card, section_inner = self._card_frame(left_panel, height=42)
        section_card.pack(fill="x")
        section_card.pack_propagate(False)
        self.section_combo = self._combo(section_inner, [], command=self.on_section_changed)
        self.section_combo.pack(fill="x")

        # TERM Dropdown
        section_label(left_panel, "TERM")
        term_card, term_inner = self._card_frame(left_panel, height=42)
        term_card.pack(fill="x")
        term_card.pack_propagate(False)
        self.term_combo = self._combo(term_inner, [], command=self.on_term_changed)
        self.term_combo.pack(fill="x")

        # SCHOOL YEAR Dropdown
        section_label(left_panel, "SCHOOL YEAR")
        sy_card, sy_inner = self._card_frame(left_panel, height=42)
        sy_card.pack(fill="x")
        sy_card.pack_propagate(False)
        self.sy_combo = self._combo(sy_inner,
            ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023",
             "2023-2024", "2024-2025", "2025-2026", "2026-2027", "2027-2028",
             "2028-2029", "2029-2030"], command=self.on_sy_changed)
        self.sy_combo.pack(fill="x")

        # SUBJECT Dropdown
        section_label(left_panel, "SUBJECT")
        sub_card, sub_inner = self._card_frame(left_panel, height=42)
        sub_card.pack(fill="x")
        sub_card.pack_propagate(False)
        self.subject_combo = self._combo(sub_inner, [], command=self.on_subject_changed)
        self.subject_combo.pack(fill="x")

        # OK button (triggers details printing and student loading)
        self.ok_btn = ctk.CTkButton(
            left_panel,
            text="OK",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            height=38, corner_radius=8,
            fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
            command=self.on_ok_clicked
        )
        self.ok_btn.pack(fill="x", pady=(14, 0))

        # CLASS DETAILS Card
        self.details_card, self.details_inner = self._card_frame(left_panel)
        self.details_label = ctk.CTkLabel(
            self.details_inner,
            text="",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="black",
            justify="left",
            anchor="w"
        )
        self.details_label.pack(fill="both", expand=True, padx=8, pady=8)

        # ── RIGHT PANEL (ROSTER) ─────────────────────────────────────────────
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        # STUDENTS card header layout with relocated dynamically updating live clock on top right
        students_hdr_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        students_hdr_frame.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(students_hdr_frame, text="STUDENTS",
                     font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                     text_color="black").pack(side="left")

        self.live_time_label = ctk.CTkLabel(students_hdr_frame, text="",
                                            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                            text_color="black")
        self.live_time_label.pack(side="right")
        self.update_clock()

        sheet_outer = ctk.CTkFrame(right_panel, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        sheet_outer.pack(fill="both", expand=True)
        
        accent_container = ctk.CTkFrame(sheet_outer, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        self.roster_scroll = ctk.CTkScrollableFrame(sheet_outer, fg_color="transparent", corner_radius=8)
        self.roster_scroll.pack(fill="both", expand=True, padx=15, pady=12)

        # ── Column widths (px) shared between header and every data row ──
        # num, P, A, L, LastName, FirstName, Middle, Status, Time
        self._CW = (38, 28, 36, 36, 125, 125, 58, 120, 82)

        # Roster Header
        self.hdr = ctk.CTkFrame(self.roster_scroll, fg_color="#eef2f7", corner_radius=8, height=34)
        self.hdr.pack(fill="x", pady=(0, 5))
        self.hdr.pack_propagate(False)

        _n, _c, _l, _f, _m, _s, _t = (self._CW[0], self._CW[1],
                                        self._CW[4], self._CW[5],
                                        self._CW[6], self._CW[7], self._CW[8])
        bold11 = ctk.CTkFont(family="Inter", size=11, weight="bold")
        bold13 = ctk.CTkFont(family="Inter", size=13, weight="bold")
        bold12 = ctk.CTkFont(family="Inter", size=12, weight="bold")

        ctk.CTkLabel(self.hdr, text="#",        font=bold12, text_color="#475569", width=_n).pack(side="left", padx=(10, 0))
        ctk.CTkLabel(self.hdr, text="P",        font=bold13, text_color="#00bf63", width=_c).pack(side="left")
        ctk.CTkLabel(self.hdr, text="A",        font=bold13, text_color="#e20000", width=_c).pack(side="left")
        ctk.CTkLabel(self.hdr, text="L",        font=bold13, text_color="#122aff", width=_c).pack(side="left")
        ctk.CTkLabel(self.hdr, text="LAST NAME",  font=bold11, text_color="#475569", width=_l, anchor="w").pack(side="left", padx=(6, 0))
        ctk.CTkLabel(self.hdr, text="FIRST NAME", font=bold11, text_color="#475569", width=_f, anchor="w").pack(side="left")
        ctk.CTkLabel(self.hdr, text="MI",          font=bold11, text_color="#475569", width=_m, anchor="w").pack(side="left")
        ctk.CTkLabel(self.hdr, text="STATUS",      font=bold11, text_color="#475569", width=_s).pack(side="left", padx=(4, 0))
        ctk.CTkLabel(self.hdr, text="TIME",        font=bold11, text_color="#475569", width=_t).pack(side="left", padx=(4, 0))

        self.roster_rows_frame = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        self.roster_rows_frame.pack(fill="x")

        # Bottom Save Attendance button
        ctk.CTkButton(right_panel, text="💾 SAVE ATTENDANCE",
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      height=45, corner_radius=8,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.save_attendance
                      ).pack(fill="x", pady=(12, 0))

        # Initialise fields to Empty and Readonly
        self.class_combo.set("")
        self.section_combo.set("")
        self.term_combo.set("")
        self.sy_combo.set("")
        self.subject_combo.set("")
        
        self.update_combo_style(self.class_combo)
        self.update_combo_style(self.section_combo)
        self.update_combo_style(self.term_combo)
        self.update_combo_style(self.sy_combo)
        self.update_combo_style(self.subject_combo)

        # Dynamic choices loader
        self.load_class_options()

        # Render clean initial empty states
        self.show_roster_placeholder()

    def update_combo_style(self, combo):
        val = combo.get().strip()
        if val:
            combo.configure(text_color="black", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
        else:
            combo.configure(text_color="#777777", font=ctk.CTkFont(family="Inter", size=13, weight="normal"))

    def load_class_options(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT gradeLevel 
                FROM ENROLLMENT 
                WHERE enrStatus = 'Active' 
                ORDER BY CAST(SUBSTR(gradeLevel, 7) AS INTEGER), gradeLevel
            """)
            rows = cursor.fetchall()
            conn.close()
            
            options = [r['gradeLevel'] for r in rows if r['gradeLevel']]
            if not options:
                options = [f"Grade {i}" for i in range(1, 13)]
            self.class_combo.configure(values=options)
        except Exception:
            options = [f"Grade {i}" for i in range(1, 13)]
            self.class_combo.configure(values=options)

    def on_class_changed(self, choice):
        self.update_combo_style(self.class_combo)
        if not choice:
            self.term_combo.configure(values=[])
            self.term_combo.set("")
            self.update_combo_style(self.term_combo)
            self.section_combo.configure(values=[])
            self.section_combo.set("")
            self.update_combo_style(self.section_combo)
            return

        # Conditional term state logic
        is_grade_1_to_10 = choice in [f"Grade {i}" for i in range(1, 11)]
        if is_grade_1_to_10:
            self.term_combo.configure(values=["Full Year"], state="disabled")
            self.term_combo.set("Full Year")
        else:
            self.term_combo.configure(values=["1st Semester", "2nd Semester"], state="readonly")
            if self.term_combo.get() not in ["1st Semester", "2nd Semester"]:
                self.term_combo.set("1st Semester")
        
        self.update_combo_style(self.term_combo)
        self.load_sections_for_class(choice)

    def on_section_changed(self, choice):
        self.update_combo_style(self.section_combo)
        self.load_subjects_for_class()

    def load_sections_for_class(self, grade):
        if not grade:
            self.section_combo.configure(values=[])
            self.section_combo.set("")
            self.update_combo_style(self.section_combo)
            return

        sections = []
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT section 
                FROM ENROLLMENT 
                WHERE gradeLevel = ? AND enrStatus = 'Active' 
                ORDER BY section
            """, (grade,))
            rows = cursor.fetchall()
            conn.close()
            sections = [r['section'] for r in rows if r['section']]
        except Exception:
            pass

        if not sections:
            is_grade_1_to_10 = grade in [f"Grade {i}" for i in range(1, 11)]
            if is_grade_1_to_10:
                sections = ["A", "B", "C", "D"]
            elif grade == "Grade 11" or grade == "Grade 12":
                sections = ["ABM-A", "HUMSS-A", "STEM-A"]
            else:
                sections = ["A", "B"]

        self.section_combo.configure(values=sections)
        if sections:
            self.section_combo.set(sections[0])
        else:
            self.section_combo.set("")

        self.update_combo_style(self.section_combo)
        self.load_subjects_for_class()

    def on_term_changed(self, choice):
        self.update_combo_style(self.term_combo)
        self.load_subjects_for_class()

    def on_sy_changed(self, choice):
        self.update_combo_style(self.sy_combo)

    def on_subject_changed(self, choice):
        self.update_combo_style(self.subject_combo)

    def load_subjects_for_class(self):
        grade = self.class_combo.get().strip()
        section = self.section_combo.get().strip()
        if not grade:
            self.subject_combo.configure(values=[])
            self.subject_combo.set("")
            self.update_combo_style(self.subject_combo)
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            is_shs = (grade in ["Grade 11", "Grade 12"])
            if is_shs:
                term = self.term_combo.get()
                sem_num = 1 if "1st" in term else 2
                
                strand = None
                for s in ["STEM", "ABM", "HUMSS"]:
                    if s in section.upper():
                        strand = s
                        break
                if not strand:
                    strand = "STEM"
                    
                cursor.execute("""
                    SELECT DISTINCT subjectName 
                    FROM SUBJECT 
                    WHERE gradeLevel = ? AND strand = ? AND semester = ? AND isActive = 1
                    ORDER BY subjectName
                """, (grade, strand, sem_num))
            else:
                cursor.execute("""
                    SELECT DISTINCT subjectName 
                    FROM SUBJECT 
                    WHERE gradeLevel = ? AND isActive = 1
                    ORDER BY subjectName
                """, (grade,))
                
            rows = cursor.fetchall()
            conn.close()
            
            subject_names = [r['subjectName'] for r in rows]
            self.subject_combo.configure(values=subject_names)
            if subject_names:
                self.subject_combo.set(subject_names[0])
            else:
                self.subject_combo.set("")
            
            self.update_combo_style(self.subject_combo)
        except Exception:
            pass

    def show_roster_placeholder(self):
        for w in self.roster_rows_frame.winfo_children():
            w.destroy()
        self.attendance_vars.clear()
        self.student_row_widgets.clear()
        self.student_row_frames.clear()
        
        lbl = ctk.CTkLabel(self.roster_rows_frame,
                           text="Please select Class, Section, Term, School Year, and Subject,\nthen click OK to retrieve the active class roster.",
                           font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                           text_color="#64748b",
                           justify="center")
        lbl.pack(pady=100)

    def on_ok_clicked(self):
        grade = self.class_combo.get().strip()
        section = self.section_combo.get().strip()
        term = self.term_combo.get().strip()
        sy = self.sy_combo.get().strip()
        subject = self.subject_combo.get().strip()

        if not grade or not section or not term or not sy or not subject:
            messagebox.showwarning("Warning", "Please complete all filters first!")
            return

        now_time = datetime.now().strftime("%H:%M")

        details_text = (
            f"CLASS: {grade}\n"
            f"SECTION: {section}\n"
            f"TERM: {term}\n"
            f"SCHOOL YEAR: {sy}\n"
            f"SUBJECT: {subject}\n"
            f"TIME: {now_time}"
        )

        self.details_label.configure(text=details_text)
        self.details_card.pack(fill="x", pady=(10, 0))

        # Retrieve roster
        self.load_students()

    def load_students(self):
        grade = self.class_combo.get().strip()
        section = self.section_combo.get().strip()
        term = self.term_combo.get().strip()
        sy = self.sy_combo.get().strip()
        subject = self.subject_combo.get().strip()

        if not grade or not section or not term or not sy or not subject:
            messagebox.showwarning("Warning", "Please complete all filters first!")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT s.studentID, s.studLname, s.studFname, s.studMname, d.detailID
                FROM STUDENT s
                JOIN ENROLLMENT e ON s.studentID = e.studentID
                JOIN DETAIL d ON e.enrollmentID = d.enrollmentID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE e.gradeLevel = ?
                  AND e.section = ?
                  AND e.term = ?
                  AND e.schoolYear = ?
                  AND sub.subjectName = ?
                  AND e.enrStatus = 'Active'
                ORDER BY s.studLname, s.studFname
            """, (grade, section, term, sy, subject))
            
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                for w in self.roster_rows_frame.winfo_children():
                    w.destroy()
                self.attendance_vars.clear()
                self.student_row_widgets.clear()
                self.student_row_frames.clear()
                
                lbl = ctk.CTkLabel(self.roster_rows_frame, text="No enrolled students found for the selected filters.",
                                   font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                   text_color="#ef4444")
                lbl.pack(pady=60)
                return

            names = []
            detail_ids = {}
            for r in rows:
                m = f" {r['studMname'][0]}." if r['studMname'] else ""
                full_name = f"{r['studLname']}, {r['studFname']}{m}"
                names.append(full_name)
                detail_ids[full_name] = r['detailID']
                
            self.loaded_detail_ids = detail_ids
            self.render_roster(names)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students:\n{e}")

    def _parse_name(self, name_str):
        parts = name_str.split(",", 1)
        last_name = parts[0].strip()
        rest = parts[1].strip() if len(parts) > 1 else ""
        
        first_name = rest
        middle_name = ""
        
        if rest:
            rest_parts = rest.rsplit(" ", 1)
            if len(rest_parts) > 1 and (rest_parts[1].endswith(".") or len(rest_parts[1]) <= 2):
                first_name = rest_parts[0].strip()
                middle_name = rest_parts[1].strip()
                
        return last_name, first_name, middle_name

    def render_roster(self, student_list):
        for w in self.roster_rows_frame.winfo_children():
            w.destroy()
        self.attendance_vars.clear()
        self.student_row_widgets.clear()
        self.student_row_frames.clear()

        # Column widths must match self._CW set in create_ui
        w_num, w_chk, w_l, w_f, w_m, w_s, w_t = (
            self._CW[0], self._CW[1],
            self._CW[4], self._CW[5], self._CW[6],
            self._CW[7], self._CW[8]
        )

        chk_cfg = dict(text="", width=18, height=18, corner_radius=9,
                       border_width=2, border_color="#cbd5e1",
                       checkmark_color="#ffffff")

        for idx, name in enumerate(student_list):
            last_name, first_name, middle_name = self._parse_name(name)

            row_bg = "#f8fafc" if idx % 2 == 0 else "#ffffff"
            row_frame = ctk.CTkFrame(self.roster_rows_frame, fg_color=row_bg,
                                     corner_radius=8, border_width=1, border_color="#cbd5e1",
                                     height=44)
            row_frame.pack(fill="x", pady=2, padx=2)
            row_frame.pack_propagate(False)
            self.student_row_frames[name] = row_frame

            # ── Row number ──
            ctk.CTkLabel(row_frame, text=str(idx + 1),
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#475569", width=w_num
                         ).pack(side="left", padx=(10, 0))

            # ── P / A / L checkboxes in fixed-width cells ──
            p_var = ctk.BooleanVar(value=False)
            a_var = ctk.BooleanVar(value=False)
            l_var = ctk.BooleanVar(value=False)
            self.attendance_vars[name] = (p_var, a_var, l_var)

            def _chk_cell(par, var, fg, hover):
                cell = ctk.CTkFrame(par, fg_color="transparent", width=w_chk)
                cell.pack(side="left")
                cell.pack_propagate(False)
                c = ctk.CTkCheckBox(cell, variable=var, fg_color=fg, hover_color=hover, **chk_cfg)
                c.pack(expand=True, pady=10)
                return c

            p_chk = _chk_cell(row_frame, p_var, "#00bf63", "#008040")
            a_chk = _chk_cell(row_frame, a_var, "#e20000", "#9e0000")
            l_chk = _chk_cell(row_frame, l_var, "#122aff", "#0a1bb3")

            p_chk.configure(command=lambda n=name, p=p_var, a=a_var, l=l_var: self._mutual(n, p, a, l, "P"))
            a_chk.configure(command=lambda n=name, p=p_var, a=a_var, l=l_var: self._mutual(n, p, a, l, "A"))
            l_chk.configure(command=lambda n=name, p=p_var, a=a_var, l=l_var: self._mutual(n, p, a, l, "L"))

            # ── Name columns ──
            ctk.CTkLabel(row_frame, text=last_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", width=w_l, anchor="w"
                         ).pack(side="left", padx=(6, 0))

            ctk.CTkLabel(row_frame, text=first_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", width=w_f, anchor="w"
                         ).pack(side="left")

            ctk.CTkLabel(row_frame, text=middle_name or "—",
                         font=ctk.CTkFont(family="Inter", size=12),
                         text_color="#475569", width=w_m, anchor="w"
                         ).pack(side="left")

            # ── Status pill (single CTkLabel with corner_radius) ──
            status_lbl = ctk.CTkLabel(row_frame, text="",
                                      font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                                      text_color="#64748b",
                                      fg_color="#f1f5f9", corner_radius=13,
                                      width=w_s, height=26)
            status_lbl.pack(side="left", padx=(4, 0))

            # ── Time ──
            time_lbl = ctk.CTkLabel(row_frame, text="—",
                                    font=ctk.CTkFont(family="Inter", size=12),
                                    text_color="#64748b", width=w_t)
            time_lbl.pack(side="left", padx=(4, 0))

            # Store only what _mutual needs
            self.student_row_widgets[name] = (status_lbl, time_lbl)

    def _mutual(self, name, p_var, a_var, l_var, selected):
        if selected == "P" and p_var.get():
            a_var.set(False)
            l_var.set(False)
        elif selected == "A" and a_var.get():
            p_var.set(False)
            l_var.set(False)
        elif selected == "L" and l_var.get():
            p_var.set(False)
            a_var.set(False)

        status_lbl, time_lbl = self.student_row_widgets[name]
        row_frame = self.student_row_frames.get(name)

        # Live border coloring and status pill update
        if p_var.get():
            status_lbl.configure(fg_color="#00bf63", text="PRESENT", text_color="white")
            time_lbl.configure(text=datetime.now().strftime("%I:%M %p"), text_color="#0f172a")
            if row_frame:
                row_frame.configure(border_color="#00bf63", border_width=2)
        elif a_var.get():
            status_lbl.configure(fg_color="#e20000", text="ABSENT", text_color="white")
            time_lbl.configure(text=datetime.now().strftime("%I:%M %p"), text_color="#0f172a")
            if row_frame:
                row_frame.configure(border_color="#e20000", border_width=2)
        elif l_var.get():
            status_lbl.configure(fg_color="#122aff", text="LATE", text_color="white")
            time_lbl.configure(text=datetime.now().strftime("%I:%M %p"), text_color="#0f172a")
            if row_frame:
                row_frame.configure(border_color="#122aff", border_width=2)
        else:
            status_lbl.configure(fg_color="#f1f5f9", text="", text_color="#64748b")
            time_lbl.configure(text="—", text_color="#64748b")
            if row_frame:
                row_frame.configure(border_color="#cbd5e1", border_width=1)

    def save_attendance(self):
        att_date = datetime.now().strftime("%Y-%m-%d")

        if not self.attendance_vars:
            messagebox.showwarning("Warning", "No students loaded.")
            return

        unmarked = [n for n, (p, a, l) in self.attendance_vars.items()
                    if not p.get() and not a.get() and not l.get()]
        if len(unmarked) == len(self.attendance_vars):
            messagebox.showwarning("Nothing Marked",
                                   "Please mark attendance for at least one student.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        saved = 0
        skipped = []

        try:
            for name, (p_var, a_var, l_var) in self.attendance_vars.items():
                if p_var.get():
                    status = "Present"
                elif a_var.get():
                    status = "Absent"
                elif l_var.get():
                    status = "Late"
                else:
                    skipped.append(name)
                    continue

                detail_id = getattr(self, "loaded_detail_ids", {}).get(name)
                if not detail_id:
                    parts = name.split(", ", 1)
                    lname = parts[0].strip() if len(parts) > 0 else ""
                    fname = parts[1].split(" ")[0].strip() if len(parts) > 1 else ""

                    cursor.execute("""
                        SELECT d.detailID
                        FROM DETAIL d
                        JOIN ENROLLMENT e ON d.enrollmentID = e.enrollmentID
                        JOIN STUDENT s ON e.studentID = s.studentID
                        JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                        WHERE s.studLname LIKE ?
                          AND s.studFname LIKE ?
                          AND e.term = ?
                          AND e.schoolYear = ?
                          AND sub.subjectName LIKE ?
                        LIMIT 1
                    """, (
                        f"%{lname}%",
                        f"%{fname}%",
                        self.term_combo.get(),
                        self.sy_combo.get(),
                        f"%{self.subject_combo.get()}%"
                    ))
                    detail_row = cursor.fetchone()
                    detail_id = detail_row['detailID'] if detail_row else None

                if not detail_id:
                    skipped.append(name)
                    continue

                # Insert or update attendance status
                cursor.execute("""
                    SELECT attendanceID FROM ATTENDANCE
                    WHERE detailID = ? AND attDate = ?
                """, (detail_id, att_date))
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE ATTENDANCE SET attStatus = ?
                        WHERE detailID = ? AND attDate = ?
                    """, (status, detail_id, att_date))
                else:
                    cursor.execute("""
                        INSERT INTO ATTENDANCE (detailID, attDate, attStatus)
                        VALUES (?, ?, ?)
                    """, (detail_id, att_date, status))

                saved += 1

            conn.commit()
            AttendanceSavedPopup(self, saved, att_date, len(skipped))

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to save attendance:\\n{e}")
        finally:
            conn.close()

    def update_clock(self):
        now = datetime.now()
        formatted_time = now.strftime("%B %d, %Y TIME %H:%M")
        if hasattr(self, "live_time_label") and self.live_time_label.winfo_exists():
            self.live_time_label.configure(text=formatted_time)
            self.after(1000, self.update_clock)

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()