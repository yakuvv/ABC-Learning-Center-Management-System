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
            height=35, corner_radius=0,
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
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)
        
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=8)
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

        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=40, pady=20)

        split_body = ctk.CTkFrame(workspace, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # ── LEFT PANEL ───────────────────────────────────────────────────────
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=480)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)

        def section_label(parent, text):
            ctk.CTkLabel(parent, text=text,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="black").pack(anchor="w", pady=(8, 2))

        # CLASS Dropdown
        section_label(left_panel, "CLASS")
        class_card, class_inner = self._card_frame(left_panel, height=50)
        class_card.pack(fill="x")
        class_card.pack_propagate(False)
        self.class_combo = self._combo(class_inner, [], command=self.on_class_changed)
        self.class_combo.pack(fill="x")

        # TERM Dropdown
        section_label(left_panel, "TERM")
        term_card, term_inner = self._card_frame(left_panel, height=50)
        term_card.pack(fill="x")
        term_card.pack_propagate(False)
        self.term_combo = self._combo(term_inner, [], command=self.on_term_changed)
        self.term_combo.pack(fill="x")

        # SCHOOL YEAR Dropdown
        section_label(left_panel, "SCHOOL YEAR")
        sy_card, sy_inner = self._card_frame(left_panel, height=50)
        sy_card.pack(fill="x")
        sy_card.pack_propagate(False)
        self.sy_combo = self._combo(sy_inner,
            ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023",
             "2023-2024", "2024-2025", "2025-2026", "2026-2027", "2027-2028",
             "2028-2029", "2029-2030"], command=self.on_sy_changed)
        self.sy_combo.pack(fill="x")

        # SUBJECT Dropdown
        section_label(left_panel, "SUBJECT")
        sub_card, sub_inner = self._card_frame(left_panel, height=50)
        sub_card.pack(fill="x")
        sub_card.pack_propagate(False)
        self.subject_combo = self._combo(sub_inner, [], command=self.on_subject_changed)
        self.subject_combo.pack(fill="x")

        # LIVE TIME Displays
        section_label(left_panel, "LIVE TIME")
        time_card, time_inner = self._card_frame(left_panel, height=50)
        time_card.pack(fill="x")
        time_card.pack_propagate(False)
        self.time_label = ctk.CTkLabel(time_inner, text="",
                                       font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                       text_color="black")
        self.time_label.pack(side="left", padx=15, pady=8)
        self.update_clock()

        # Load Students trigger
        ctk.CTkButton(left_panel, text="🔍 LOAD STUDENTS",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      height=40, corner_radius=8,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.load_students
                      ).pack(fill="x", pady=(18, 0))

        # ── RIGHT PANEL (ROSTER) ─────────────────────────────────────────────
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        ctk.CTkLabel(right_panel, text="STUDENTS",
                     font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                     text_color="black").pack(anchor="w", pady=(0, 4))

        sheet_outer = ctk.CTkFrame(right_panel, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        sheet_outer.pack(fill="both", expand=True)
        
        accent_container = ctk.CTkFrame(sheet_outer, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        self.roster_scroll = ctk.CTkScrollableFrame(sheet_outer, fg_color="transparent", corner_radius=8)
        self.roster_scroll.pack(fill="both", expand=True, padx=15, pady=12)

        # Roster Header
        self.hdr = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        self.hdr.pack(fill="x", pady=(0, 6))
        
        self.hdr.grid_columnconfigure(0, minsize=40)  # index
        self.hdr.grid_columnconfigure(1, minsize=45)  # P
        self.hdr.grid_columnconfigure(2, minsize=45)  # A
        self.hdr.grid_columnconfigure(3, minsize=45)  # L
        self.hdr.grid_columnconfigure(4, weight=2)    # Last Name
        self.hdr.grid_columnconfigure(5, weight=2)    # First Name
        self.hdr.grid_columnconfigure(6, weight=1)    # Middle Name
        self.hdr.grid_columnconfigure(7, weight=1)    # Status
        self.hdr.grid_columnconfigure(8, weight=1)    # Time

        ctk.CTkLabel(self.hdr, text="#", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color="#475569", width=40).grid(row=0, column=0, padx=2)
        ctk.CTkLabel(self.hdr, text="P", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#00bf63", width=45).grid(row=0, column=1, padx=2)
        ctk.CTkLabel(self.hdr, text="A", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#e20000", width=45).grid(row=0, column=2, padx=2)
        ctk.CTkLabel(self.hdr, text="L", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#122aff", width=45).grid(row=0, column=3, padx=2)

        headers = [
            ("LAST NAME", 4),
            ("FIRST NAME", 5),
            ("MIDDLE NAME", 6),
            ("STATUS", 7),
            ("TIME", 8),
        ]
        
        for text, col in headers:
            ctk.CTkLabel(self.hdr, text=text,
                         font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                         text_color="#475569").grid(row=0, column=col, sticky="ew" if col > 6 else "w", padx=10)

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
        self.term_combo.set("")
        self.sy_combo.set("")
        self.subject_combo.set("")
        
        self.update_combo_style(self.class_combo)
        self.update_combo_style(self.term_combo)
        self.update_combo_style(self.sy_combo)
        self.update_combo_style(self.subject_combo)

        # Dynamic choices loader
        self.load_class_options()

        # Render clean initial empty states (No default students text)
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
                SELECT DISTINCT gradeLevel, section 
                FROM ENROLLMENT 
                WHERE enrStatus = 'Active' 
                ORDER BY gradeLevel, section
            """)
            rows = cursor.fetchall()
            conn.close()
            
            options = []
            for r in rows:
                options.append(f"{r['gradeLevel']} - {r['section']}")
                
            if not options:
                # Premium fallback list if no active database enrollments yet
                options = [
                    "Grade 1 - A", "Grade 2 - A", "Grade 3 - A", "Grade 4 - A", "Grade 5 - A", "Grade 6 - A",
                    "Grade 7 - A", "Grade 8 - A", "Grade 9 - A", "Grade 10 - A",
                    "Grade 11 - STEM-A", "Grade 11 - ABM-A", "Grade 11 - HUMSS-A",
                    "Grade 12 - STEM-A", "Grade 12 - ABM-A", "Grade 12 - HUMSS-A"
                ]
            self.class_combo.configure(values=options)
        except Exception:
            pass

    def on_class_changed(self, choice):
        self.update_combo_style(self.class_combo)
        if not choice:
            self.term_combo.configure(values=[])
            self.term_combo.set("")
            self.update_combo_style(self.term_combo)
            return

        # Dynamically set TERM options matching enrollment rules
        if any(f"Grade {i} " in choice for i in range(1, 11)):
            self.term_combo.configure(values=["Full Year"])
            self.term_combo.set("Full Year")
        else:
            self.term_combo.configure(values=["1st Semester", "2nd Semester"])
            self.term_combo.set("1st Semester")
        
        self.update_combo_style(self.term_combo)
        self.load_subjects_for_class()

    def on_term_changed(self, choice):
        self.update_combo_style(self.term_combo)
        self.load_subjects_for_class()

    def on_sy_changed(self, choice):
        self.update_combo_style(self.sy_combo)

    def on_subject_changed(self, choice):
        self.update_combo_style(self.subject_combo)

    def load_subjects_for_class(self):
        choice = self.class_combo.get()
        if not choice:
            self.subject_combo.configure(values=[])
            self.subject_combo.set("")
            self.update_combo_style(self.subject_combo)
            return

        parts = choice.split(" - ")
        grade = parts[0].strip()
        section = parts[1].strip() if len(parts) > 1 else ""

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            is_shs = (grade in ["Grade 11", "Grade 12"])
            if is_shs:
                term = self.term_combo.get()
                sem_num = 1 if "1st" in term else 2
                
                strand = None
                for s in ["STEM", "ABM", "HUMSS"]:
                    if s in section:
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
                           text="Please select Class, Term, School Year, and Subject,\nthen click LOAD STUDENTS to retrieve the active class roster.",
                           font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                           text_color="#64748b",
                           justify="center")
        lbl.pack(pady=100)

    def load_students(self):
        choice = self.class_combo.get()
        term = self.term_combo.get()
        sy = self.sy_combo.get()
        sub = self.subject_combo.get()

        if not choice or not term or not sy or not sub:
            messagebox.showwarning("Warning", "Please complete all filters first!")
            return

        parts = choice.split(" - ")
        grade = parts[0].strip()
        section = parts[1].strip() if len(parts) > 1 else ""

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            
            # Query active student enrollments matching class and subject
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
            """, (grade, section, term, sy, sub))
            
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
                m = f" {r['studMname'][0]}." if r.get('studMname') else ""
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

        for idx, name in enumerate(student_list):
            last_name, first_name, middle_name = self._parse_name(name)

            # Elegant rounded background container for each row
            row_bg = "#f8fafc" if idx % 2 == 0 else "#ffffff"
            row_frame = ctk.CTkFrame(self.roster_rows_frame, fg_color=row_bg,
                                     corner_radius=10, border_width=1, border_color="#cbd5e1",
                                     height=46)
            row_frame.pack(fill="x", pady=4, padx=5)
            row_frame.pack_propagate(False)

            self.student_row_frames[name] = row_frame

            row_frame.grid_columnconfigure(0, minsize=40)
            row_frame.grid_columnconfigure(1, minsize=45)
            row_frame.grid_columnconfigure(2, minsize=45)
            row_frame.grid_columnconfigure(3, minsize=45)
            row_frame.grid_columnconfigure(4, weight=2)
            row_frame.grid_columnconfigure(5, weight=2)
            row_frame.grid_columnconfigure(6, weight=1)
            row_frame.grid_columnconfigure(7, weight=1)
            row_frame.grid_columnconfigure(8, weight=1)

            # Roster index number
            ctk.CTkLabel(row_frame, text=str(idx + 1),
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color="#475569", width=40
                         ).grid(row=0, column=0, padx=2, pady=8)

            p_var = ctk.BooleanVar(value=False)
            a_var = ctk.BooleanVar(value=False)
            l_var = ctk.BooleanVar(value=False)
            self.attendance_vars[name] = (p_var, a_var, l_var)

            # Premium circular checkbox design (corner_radius=11 for size 22 perfect circle)
            chk_cfg = dict(text="", width=22, height=22, corner_radius=11,
                           border_width=2, border_color="#cbd5e1",
                           checkmark_color="#ffffff")

            p_chk = ctk.CTkCheckBox(row_frame, variable=p_var, fg_color="#00bf63", hover_color="#008040", **chk_cfg)
            a_chk = ctk.CTkCheckBox(row_frame, variable=a_var, fg_color="#e20000", hover_color="#9e0000", **chk_cfg)
            l_chk = ctk.CTkCheckBox(row_frame, variable=l_var, fg_color="#122aff", hover_color="#0a1bb3", **chk_cfg)

            p_chk.configure(command=lambda n=name, p=p_var, a=a_var, l=l_var: self._mutual(n, p, a, l, "P"))
            a_chk.configure(command=lambda n=name, p=p_var, a=a_var, l=l_var: self._mutual(n, p, a, l, "A"))
            l_chk.configure(command=lambda n=name, p=p_var, a=a_var, l=l_var: self._mutual(n, p, a, l, "L"))

            p_chk.grid(row=0, column=1, padx=2, pady=10)
            a_chk.grid(row=0, column=2, padx=2, pady=10)
            l_chk.grid(row=0, column=3, padx=2, pady=10)

            # Last Name label
            ctk.CTkLabel(row_frame, text=last_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", anchor="w").grid(row=0, column=4, padx=10, pady=10, sticky="w")

            # First Name label
            ctk.CTkLabel(row_frame, text=first_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", anchor="w").grid(row=0, column=5, padx=10, pady=10, sticky="w")

            # Middle Name label
            ctk.CTkLabel(row_frame, text=middle_name or "—",
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#475569", anchor="w").grid(row=0, column=6, padx=10, pady=10, sticky="w")

            # Elegant rounded Status Pill container
            status_box = ctk.CTkFrame(row_frame, fg_color="#f1f5f9", height=26, corner_radius=13)
            status_box.grid(row=0, column=7, padx=10, pady=10, sticky="ew")
            status_box.pack_propagate(False)
            status_lbl = ctk.CTkLabel(status_box, text="",
                                      font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                                      text_color="#64748b")
            status_lbl.pack(anchor="center", pady=3)

            # Time Cell
            time_lbl = ctk.CTkLabel(row_frame, text="—",
                                    font=ctk.CTkFont(family="Inter", size=12),
                                    text_color="#64748b")
            time_lbl.grid(row=0, column=8, padx=10, pady=10, sticky="center")

            self.student_row_widgets[name] = (status_box, status_lbl, time_lbl)

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

        status_box, status_lbl, time_lbl = self.student_row_widgets[name]
        row_frame = self.student_row_frames.get(name)
        
        # Interactive live border coloring and Status pill formatting!
        if p_var.get():
            status_box.configure(fg_color="#00bf63")
            status_lbl.configure(text="PRESENT", text_color="white")
            time_lbl.configure(text=datetime.now().strftime("%I:%M %p"), text_color="#0f172a")
            if row_frame:
                row_frame.configure(border_color="#00bf63", border_width=2)
        elif a_var.get():
            status_box.configure(fg_color="#e20000")
            status_lbl.configure(text="ABSENT", text_color="white")
            time_lbl.configure(text=datetime.now().strftime("%I:%M %p"), text_color="#0f172a")
            if row_frame:
                row_frame.configure(border_color="#e20000", border_width=2)
        elif l_var.get():
            status_box.configure(fg_color="#122aff")
            status_lbl.configure(text="LATE", text_color="white")
            time_lbl.configure(text=datetime.now().strftime("%I:%M %p"), text_color="#0f172a")
            if row_frame:
                row_frame.configure(border_color="#122aff", border_width=2)
        else:
            status_box.configure(fg_color="#f1f5f9")
            status_lbl.configure(text="", text_color="#64748b")
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

                # Query detailID directly from cached mappings, or query database if not found
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
            messagebox.showerror("Error", f"Failed to save attendance:\n{e}")
        finally:
            conn.close()

    def update_clock(self):
        now = datetime.now()
        formatted_time = now.strftime("%B %d, %Y - %I:%M:%S %p")
        if hasattr(self, "time_label") and self.time_label.winfo_exists():
            self.time_label.configure(text=formatted_time)
            self.after(1000, self.update_clock)

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()