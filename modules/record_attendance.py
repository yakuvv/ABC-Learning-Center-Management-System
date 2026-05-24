import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime
from utils.modern_combo import ModernCombo
from utils.term_options import apply_term_combo_for_level, get_term_options


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
    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user_role = user_role
        self.tutor_id = user_id

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
        return ModernCombo(parent, values=values, **kwargs)

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

        ctk.CTkButton(top_bar, text="<  Back to Dashboard",
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

        # ── TAB PILL SWITCHER ─────────────────────────────────────────────────
        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(12, 0))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1", width=380, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.record_tab_btn = ctk.CTkButton(
            tab_pill, text="Record Attendance",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#122aff", text_color="#ffffff",
            corner_radius=19, height=38, width=185,
            command=lambda: self.switch_tab("record"))
        self.record_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.history_tab_btn = ctk.CTkButton(
            tab_pill, text="Attendance History",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="transparent", text_color="#374151",
            corner_radius=19, height=38, width=185,
            command=lambda: self.switch_tab("history"))
        self.history_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        # ── WORKSPACE CONTAINER ───────────────────────────────────────────────
        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        self.render_record_tab()

    def switch_tab(self, tab):
        if tab == "record":
            self.record_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.history_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.render_record_tab()
        else:
            self.record_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.history_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.render_history_tab()

    def render_record_tab(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        split_body = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # ── LEFT PANEL ───────────────────────────────────────────────────────
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=420)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)
        left_panel.grid_propagate(False)

        def section_label(parent, text, row):
            lbl = ctk.CTkLabel(parent, text=text,
                               font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                               text_color="black")
            lbl.grid(row=row, column=0, sticky="w", pady=(8, 2))
            return lbl

        # LEVEL Dropdown
        self.class_lbl = section_label(left_panel, "LEVEL", 0)
        self.class_card, class_inner = self._card_frame(left_panel, height=50)
        self.class_card.grid(row=1, column=0, sticky="ew")
        self.class_card.pack_propagate(False)
        self.class_combo = self._combo(class_inner, [f"Grade {i}" for i in range(1, 13)], command=self.on_class_changed)
        self.class_combo.pack(fill="x")

        # GROUP NAME Dropdown
        self.section_lbl = section_label(left_panel, "GROUP NAME", 2)
        self.section_card, section_inner = self._card_frame(left_panel, height=50)
        self.section_card.grid(row=3, column=0, sticky="ew")
        self.section_card.pack_propagate(False)
        self.section_combo = self._combo(section_inner, ["A", "B", "C", "D"], command=self.on_section_changed)
        self.section_combo.pack(fill="x")

        # TERM Dropdown
        self.term_label_widget = section_label(left_panel, "TERM", 4)
        self.term_card, term_inner = self._card_frame(left_panel, height=50)
        self.term_card.grid(row=5, column=0, sticky="ew")
        self.term_card.pack_propagate(False)
        self.term_combo = self._combo(term_inner, [], command=self.on_term_changed)
        self.term_combo.pack(fill="x")

        # SUBJECT Dropdown
        self.sub_lbl = section_label(left_panel, "SUBJECT", 6)
        self.sub_card, sub_inner = self._card_frame(left_panel, height=50)
        self.sub_card.grid(row=7, column=0, sticky="ew")
        self.sub_card.pack_propagate(False)
        self.subject_combo = self._combo(sub_inner, [], command=self.on_subject_changed)
        self.subject_combo.pack(fill="x")

        # OK button trigger
        self.ok_btn = ctk.CTkButton(left_panel, text="OK",
                                    font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                    height=40, corner_radius=8,
                                    fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                                    command=self.on_ok_clicked)
        self.ok_btn.grid(row=8, column=0, sticky="ew", pady=(15, 0))

        # CLASS DETAILS Card
        self.details_lbl = section_label(left_panel, "CLASS DETAILS", 9)
        self.details_card, self.details_inner = self._card_frame(left_panel)
        self.details_card.grid(row=10, column=0, sticky="nsew", pady=(0, 5))

        details_frame = ctk.CTkFrame(self.details_inner, fg_color="transparent")
        details_frame.pack(fill="both", expand=True)
        details_frame.columnconfigure(0, weight=0, minsize=110)
        details_frame.columnconfigure(1, weight=1)

        self.class_detail_labels = {}
        for i, (label, val) in enumerate([
            ("Level", "—"),
            ("Group Name", "—"),
            ("Term", "—"),
            ("Subject", "—"),
            ("Time", "—"),
        ]):
            ctk.CTkLabel(
                details_frame, text=f"{label}:",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                text_color="#15165e",
            ).grid(row=i, column=0, sticky="w", pady=6)

            val_lbl = ctk.CTkLabel(
                details_frame, text=val,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#1e293b",
            )
            val_lbl.grid(row=i, column=1, sticky="w", padx=(20, 0), pady=6)
            self.class_detail_labels[label] = val_lbl

        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(10, weight=1)

        # ── RIGHT PANEL (ROSTER) ─────────────────────────────────────────────
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        # Header for Right Panel containing STUDENTS label on left and military live time on right
        right_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        right_header.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(right_header, text="STUDENTS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="black").pack(side="left")

        self.live_time_label = ctk.CTkLabel(right_header, text="",
                                             font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                             text_color="black")
        self.live_time_label.pack(side="right")
        self.update_clock()

        sheet_outer = ctk.CTkFrame(right_panel, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        sheet_outer.pack(fill="both", expand=True)

        self.roster_scroll = ctk.CTkScrollableFrame(sheet_outer, fg_color="transparent", corner_radius=8)
        self.roster_scroll.pack(fill="both", expand=True, padx=15, pady=12)

        # Roster Header
        self.hdr = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        self.hdr.pack(fill="x", pady=(0, 6))

        self.hdr.grid_columnconfigure(0, minsize=35)  # index
        self.hdr.grid_columnconfigure(1, minsize=35)  # P
        self.hdr.grid_columnconfigure(2, minsize=35)  # A
        self.hdr.grid_columnconfigure(3, minsize=35)  # L
        self.hdr.grid_columnconfigure(4, weight=3)    # Last Name
        self.hdr.grid_columnconfigure(5, weight=3)    # First Name
        self.hdr.grid_columnconfigure(6, weight=1)    # Middle Name
        self.hdr.grid_columnconfigure(7, minsize=80)  # Status (fixed)
        self.hdr.grid_columnconfigure(8, minsize=65)  # Time (fixed)

        ctk.CTkLabel(self.hdr, text="#", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color="#475569", width=35).grid(row=0, column=0, padx=2)
        ctk.CTkLabel(self.hdr, text="P", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#00bf63", width=35).grid(row=0, column=1, padx=2)
        ctk.CTkLabel(self.hdr, text="A", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#e20000", width=35).grid(row=0, column=2, padx=2)
        ctk.CTkLabel(self.hdr, text="L", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#122aff", width=35).grid(row=0, column=3, padx=2)

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
        self.section_combo.set("")
        self.term_combo.set("")
        self.subject_combo.set("")
        
        self.update_combo_style(self.class_combo)
        self.update_combo_style(self.section_combo)
        self.update_combo_style(self.term_combo)
        self.update_combo_style(self.subject_combo)

        self.class_combo.set("Grade 7")
        self.on_class_changed("Grade 7")

        # Render clean initial empty states
        self.show_roster_placeholder()

    def update_combo_style(self, combo):
        val = combo.get().strip()
        if val:
            combo.configure(text_color="black", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
        else:
            combo.configure(text_color="#777777", font=ctk.CTkFont(family="Inter", size=13, weight="normal"))

    def load_class_options(self):
        # Deprecated because class choices are now cleanly pre-loaded statically Grade 1 - 12
        pass

    def on_class_changed(self, choice):
        self.update_combo_style(self.class_combo)
        if not choice:
            self.section_combo.configure(values=[])
            self.section_combo.set("")
            self.update_combo_style(self.section_combo)
            return

        if choice in ["Grade 11", "Grade 12"]:
            self.section_combo.configure(values=["STEM-A", "ABM-A", "HUMSS-A"])
            self.section_combo.set("STEM-A")
        else:
            self.section_combo.configure(values=["A", "B", "C", "D"])
            self.section_combo.set("A")

        apply_term_combo_for_level(self.term_combo, choice)
        self.update_combo_style(self.section_combo)
        self.update_combo_style(self.term_combo)
        self.load_subjects_for_class()

    def on_section_changed(self, choice):
        self.update_combo_style(self.section_combo)
        self.load_subjects_for_class()

    def on_term_changed(self, choice):
        self.update_combo_style(self.term_combo)
        self.load_subjects_for_class()

    def on_subject_changed(self, choice):
        self.update_combo_style(self.subject_combo)

    def _extract_program(self, group_name):
        for prog in ("STEM", "ABM", "HUMSS"):
            if prog in group_name:
                return prog
        return None

    def load_subjects_for_class(self):
        level = self.class_combo.get().strip()
        group_name = self.section_combo.get().strip()
        if not level or not group_name:
            self.subject_combo.configure(values=[])
            self.subject_combo.set("")
            self.update_combo_style(self.subject_combo)
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            program = self._extract_program(group_name)
            if program:
                cursor.execute("""
                    SELECT DISTINCT subjectName
                    FROM SUBJECT
                    WHERE level = ? AND program = ? AND isActive = 1
                    ORDER BY subjectName
                """, (level, program))
            else:
                cursor.execute("""
                    SELECT DISTINCT subjectName
                    FROM SUBJECT
                    WHERE level = ? AND (program IS NULL OR program = '') AND isActive = 1
                    ORDER BY subjectName
                """, (level,))
                
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

    def _set_class_details(self, level="—", group_name="—", term="—", subject="—", time="—"):
        mapping = {
            "Level": level,
            "Group Name": group_name,
            "Term": term,
            "Subject": subject,
            "Time": time,
        }
        for key, val in mapping.items():
            if key in self.class_detail_labels:
                self.class_detail_labels[key].configure(text=val or "—")

    def show_roster_placeholder(self):
        for w in self.roster_rows_frame.winfo_children():
            w.destroy()
        self.attendance_vars.clear()
        self.student_row_widgets.clear()
        self.student_row_frames.clear()

        lbl = ctk.CTkLabel(
            self.roster_rows_frame,
            text="Please select Level, Group Name, Term, and Subject,\n"
                 "then click OK to retrieve the active class roster.",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#64748b",
            justify="center",
        )
        lbl.pack(pady=100)

    def on_ok_clicked(self):
        level = self.class_combo.get().strip()
        group_name = self.section_combo.get().strip()
        term = self.term_combo.get().strip()
        sub = self.subject_combo.get().strip()

        if not level or not group_name or not term or not sub:
            messagebox.showwarning("Warning", "Please complete all filters first!")
            return

        mil_time = datetime.now().strftime("%H:%M")
        self._set_class_details(
            level=level, group_name=group_name, term=term, subject=sub, time=mil_time,
        )
        self.load_students()

    def load_students(self):
        level = self.class_combo.get().strip()
        group_name = self.section_combo.get().strip()
        term = self.term_combo.get().strip()
        sub = self.subject_combo.get().strip()

        if not level or not group_name or not term or not sub:
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT s.studentID, s.studLname, s.studFname, s.studMname, d.detailID
                FROM STUDENT s
                JOIN REGISTRATION r ON s.studentID = r.studentID
                JOIN REGISTRATION_DETAIL d ON r.registrationID = d.registrationID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE r.level = ?
                  AND r.groupName = ?
                  AND r.term = ?
                  AND sub.subjectName = ?
                  AND r.regStatus = 'Active'
                ORDER BY s.studLname, s.studFname
            """, (level, group_name, term, sub))
            
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                for w in self.roster_rows_frame.winfo_children():
                    w.destroy()
                self.attendance_vars.clear()
                self.student_row_widgets.clear()
                self.student_row_frames.clear()

                lbl = ctk.CTkLabel(
                    self.roster_rows_frame,
                    text="No enrolled students found for the selected filters.",
                    font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                    text_color="#ef4444",
                )
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

        for idx, name in enumerate(student_list):
            last_name, first_name, middle_name = self._parse_name(name)

            row_bg = "#f8fafc" if idx % 2 == 0 else "#ffffff"
            row_frame = ctk.CTkFrame(self.roster_rows_frame, fg_color=row_bg,
                                     corner_radius=10, border_width=1, border_color="#cbd5e1",
                                     height=46)
            row_frame.pack(fill="x", pady=4, padx=5)
            row_frame.pack_propagate(False)

            self.student_row_frames[name] = row_frame

            row_frame.grid_columnconfigure(0, minsize=35)
            row_frame.grid_columnconfigure(1, minsize=35)
            row_frame.grid_columnconfigure(2, minsize=35)
            row_frame.grid_columnconfigure(3, minsize=35)
            row_frame.grid_columnconfigure(4, weight=3)
            row_frame.grid_columnconfigure(5, weight=3)
            row_frame.grid_columnconfigure(6, weight=1)
            row_frame.grid_columnconfigure(7, minsize=80)
            row_frame.grid_columnconfigure(8, minsize=65)

            ctk.CTkLabel(row_frame, text=str(idx + 1),
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color="#475569", width=35
                         ).grid(row=0, column=0, padx=2, pady=8)

            p_var = ctk.BooleanVar(value=False)
            a_var = ctk.BooleanVar(value=False)
            l_var = ctk.BooleanVar(value=False)
            self.attendance_vars[name] = (p_var, a_var, l_var)

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

            ctk.CTkLabel(row_frame, text=last_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", anchor="w").grid(row=0, column=4, padx=10, pady=10, sticky="w")

            ctk.CTkLabel(row_frame, text=first_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", anchor="w").grid(row=0, column=5, padx=10, pady=10, sticky="w")

            ctk.CTkLabel(row_frame, text=middle_name or "—",
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#475569", anchor="w").grid(row=0, column=6, padx=10, pady=10, sticky="w")

            status_box = ctk.CTkFrame(row_frame, fg_color="#f1f5f9", width=70, height=22, corner_radius=11)
            status_box.grid(row=0, column=7, padx=5, pady=10)
            status_box.pack_propagate(False)
            status_lbl = ctk.CTkLabel(status_box, text="",
                                      font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                                      text_color="#64748b")
            status_lbl.pack(anchor="center", expand=True)

            time_lbl = ctk.CTkLabel(row_frame, text="—",
                                    font=ctk.CTkFont(family="Inter", size=12),
                                    text_color="#64748b")
            time_lbl.grid(row=0, column=8, padx=10, pady=10)

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
                        FROM REGISTRATION_DETAIL d
                        JOIN REGISTRATION r ON d.registrationID = r.registrationID
                        JOIN STUDENT s ON r.studentID = s.studentID
                        JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                        WHERE s.studLname LIKE ?
                          AND s.studFname LIKE ?
                          AND r.term = ?
                          AND r.level = ?
                          AND r.groupName = ?
                          AND sub.subjectName LIKE ?
                        LIMIT 1
                    """, (
                        f"%{lname}%",
                        f"%{fname}%",
                        self.term_combo.get(),
                        self.class_combo.get(),
                        self.section_combo.get(),
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
        if hasattr(self, "live_time_label") and self.live_time_label.winfo_exists():
            self.live_time_label.configure(text=formatted_time)
            self.after(1000, self.update_clock)

    def render_history_tab(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        import tkinter.ttk as ttk

        split_body = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # ── LEFT PANEL (same style as Record tab) ────────────────────────────
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=420)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)
        left_panel.grid_propagate(False)

        def section_label(parent, text, row):
            lbl = ctk.CTkLabel(parent, text=text,
                               font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                               text_color="black")
            lbl.grid(row=row, column=0, sticky="w", pady=(8, 2))
            return lbl

        # LEVEL
        section_label(left_panel, "LEVEL", 0)
        h_class_card, h_class_inner = self._card_frame(left_panel, height=50)
        h_class_card.grid(row=1, column=0, sticky="ew")
        h_class_card.pack_propagate(False)
        self.h_class = self._combo(h_class_inner, [f"Grade {i}" for i in range(1, 13)])
        self.h_class.pack(fill="x")

        # GROUP NAME
        section_label(left_panel, "GROUP NAME", 2)
        h_sec_card, h_sec_inner = self._card_frame(left_panel, height=50)
        h_sec_card.grid(row=3, column=0, sticky="ew")
        h_sec_card.pack_propagate(False)
        self.h_section = self._combo(h_sec_inner, ["A","B","C","D"])
        self.h_section.pack(fill="x")

        # TERM
        section_label(left_panel, "TERM", 4)
        h_term_card, h_term_inner = self._card_frame(left_panel, height=50)
        h_term_card.grid(row=5, column=0, sticky="ew")
        h_term_card.pack_propagate(False)
        self.h_term = self._combo(h_term_inner, [])
        self.h_term.pack(fill="x")

        # PERIOD filter
        self.h_period_lbl = section_label(left_panel, "PERIOD", 6)
        h_per_card, h_per_inner = self._card_frame(left_panel, height=50)
        h_per_card.grid(row=7, column=0, sticky="ew")
        h_per_card.pack_propagate(False)
        self.h_period = self._combo(h_per_inner, ["All Periods","1st Period","2nd Period","3rd Period","4th Period"])
        self.h_period.set("All Periods")
        self.h_period.pack(fill="x")

        # SUBJECT
        section_label(left_panel, "SUBJECT", 8)
        h_sub_card, h_sub_inner = self._card_frame(left_panel, height=50)
        h_sub_card.grid(row=9, column=0, sticky="ew")
        h_sub_card.pack_propagate(False)
        self.h_subject = self._combo(h_sub_inner, [])
        self.h_subject.pack(fill="x")

        # SEARCH button
        ctk.CTkButton(left_panel, text="SEARCH",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      height=40, corner_radius=8,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=lambda: self.load_history(
                          self.h_class.get(), self.h_section.get(),
                          self.h_term.get(), self.h_period.get(),
                          self.h_subject.get(), stats_frame, tree)
                      ).grid(row=10, column=0, sticky="ew", pady=(15, 0))

        left_panel.columnconfigure(0, weight=1)

        def on_h_class_changed(choice):
            if choice in ["Grade 11", "Grade 12"]:
                self.h_section.configure(values=["STEM-A","ABM-A","HUMSS-A"])
                self.h_section.set("STEM-A")
            else:
                self.h_section.configure(values=["A","B","C","D"])
                self.h_section.set("A")
            apply_term_combo_for_level(self.h_term, choice)
            period_opts = ["All Periods"] + get_term_options(choice)
            self.h_period.configure(values=period_opts)
            self.h_period.set("All Periods")
            self.update_combo_style(self.h_class)
            self.update_combo_style(self.h_section)
            self.update_combo_style(self.h_term)
            self.update_combo_style(self.h_period)
            load_h_subjects()

        def load_h_subjects():
            level = self.h_class.get()
            group_name = self.h_section.get()
            if not level or not group_name:
                return
            try:
                conn = database.get_connection()
                cur = conn.cursor()
                program = self._extract_program(group_name)
                if program:
                    cur.execute("""SELECT DISTINCT subjectName FROM SUBJECT
                                   WHERE level=? AND program=? AND isActive=1
                                   ORDER BY subjectName""", (level, program))
                else:
                    cur.execute("""SELECT DISTINCT subjectName FROM SUBJECT
                                   WHERE level=? AND (program IS NULL OR program='') AND isActive=1
                                   ORDER BY subjectName""", (level,))
                rows = cur.fetchall()
                conn.close()
                names = [r["subjectName"] for r in rows]
                self.h_subject.configure(values=names)
                self.h_subject.set(names[0] if names else "")
                self.update_combo_style(self.h_subject)
            except Exception:
                pass

        self.h_class.configure(command=on_h_class_changed)
        self.h_class.set("Grade 7")
        on_h_class_changed("Grade 7")

        # ── RIGHT PANEL ───────────────────────────────────────────────────────
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        ctk.CTkLabel(right_panel, text="ATTENDANCE RECORDS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="black").pack(anchor="w", pady=(0, 6))

        # ── TABLE ────────────────────────────────────────────────────────────
        table_card = ctk.CTkFrame(right_panel, fg_color="#ffffff",
                                  corner_radius=16, border_width=1, border_color="#cbd5e1")
        table_card.pack(fill="both", expand=True)

        tree_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=12)
        tree_frame.bind("<Configure>", self._fit_history_tree_columns)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Hist.Treeview.Heading",
                        background="#15165e", foreground="#ffffff",
                        font=("Inter", 11, "bold"), borderwidth=0)
        style.map("Hist.Treeview.Heading",
                  background=[("active","#1c1d7c")], foreground=[("active","#ffffff")])
        style.configure("Hist.Treeview",
                        font=("Inter", 10), rowheight=30,
                        fieldbackground="#ffffff", background="#ffffff", borderwidth=0)
        style.map("Hist.Treeview",
                  background=[("selected","#e0e7ff")],
                  foreground=[("selected","#15165e")])

        cols = ("#", "Learner ID", "Student Name", "Date", "Status")
        self.hist_tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                      height=18, style="Hist.Treeview")
        self.hist_tree["displaycolumns"] = cols
        self.hist_tree.column("#0", width=0, stretch=False)
        tree = self.hist_tree
        tree.tag_configure("present", foreground="#008040")
        tree.tag_configure("absent",  foreground="#b91c1c")
        tree.tag_configure("late",    foreground="#122aff")
        tree.tag_configure("even",    background="#f8fafc")
        tree.tag_configure("odd",     background="#ffffff")

        self._hist_col_specs = [
            ("#", 42, "center", False),
            ("Learner ID", 118, "w", False),
            ("Student Name", 200, "w", True),
            ("Date", 108, "center", False),
            ("Status", 88, "center", False),
        ]
        for col, width, anchor, stretch in self._hist_col_specs:
            tree.heading(col, text=col, anchor=anchor)
            tree.column(col, width=width, minwidth=width, anchor=anchor, stretch=stretch)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        self.after_idle(self._fit_history_tree_columns)

        # ── SUMMARY STATS ────────────────────────────────────────────────────
        stats_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(12, 0))
        for col in range(4):
            stats_frame.columnconfigure(col, weight=1, uniform="stat_col")

    def _fit_history_tree_columns(self, event=None):
        """Keep history table columns aligned with headers inside the card."""
        if not hasattr(self, "hist_tree") or not self.hist_tree.winfo_exists():
            return
        tree = self.hist_tree
        tree.update_idletasks()
        total_w = tree.winfo_width()
        if total_w < 200:
            return
        fixed = 42 + 118 + 108 + 88 + 24  # #, learner, date, status + padding
        name_w = max(total_w - fixed, 140)
        tree.column("#", width=42, minwidth=42, stretch=False)
        tree.column("Learner ID", width=118, minwidth=100, stretch=False)
        tree.column("Student Name", width=name_w, minwidth=140, stretch=False)
        tree.column("Date", width=108, minwidth=95, stretch=False)
        tree.column("Status", width=88, minwidth=72, stretch=False)

    def load_history(self, level, group_name, term, period, subject, stats_frame, tree):
        for w in stats_frame.winfo_children():
            w.destroy()

        for item in tree.get_children():
            tree.delete(item)

        if not all([level, group_name, term, subject]):
            messagebox.showwarning("Warning", "Please complete all filters first!")
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT r.learnerID,
                       s.studLname || ', ' || s.studFname AS studentName,
                       a.attDate, a.attStatus
                FROM ATTENDANCE a
                JOIN REGISTRATION_DETAIL d ON a.detailID = d.detailID
                JOIN REGISTRATION r ON d.registrationID = r.registrationID
                JOIN STUDENT s ON r.studentID = s.studentID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE r.level = ?
                  AND r.groupName = ?
                  AND r.term = ?
                  AND sub.subjectName = ?
                ORDER BY s.studLname, s.studFname, a.attDate
            """, (level, group_name, term, subject))
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history:\n{e}")
            return

        present_c = absent_c = late_c = 0
        for idx, r in enumerate(rows):
            status = r["attStatus"]
            if status == "Present":
                present_c += 1; tag_s = "present"
            elif status == "Absent":
                absent_c  += 1; tag_s = "absent"
            else:
                late_c    += 1; tag_s = "late"
            row_tag = "even" if idx % 2 == 0 else "odd"
            tree.insert("", "end",
                        values=(idx+1, r["learnerID"], r["studentName"], r["attDate"], status),
                        tags=(tag_s, row_tag))

        if not rows:
            tree.insert("", "end", values=("", "", "No records found for the selected filters.", "", ""))

        # Build summary cards
        total = len(rows)
        stats = [
            ("PRESENT", present_c, "#00bf63"),
            ("ABSENT",  absent_c,  "#e20000"),
            ("LATE",    late_c,    "#122aff"),
            ("TOTAL",   total,     "#475569"),
        ]
        for col, (label, count, accent) in enumerate(stats):
            card = ctk.CTkFrame(
                stats_frame, fg_color="#ffffff", corner_radius=4,
                border_width=1, border_color="#e2e8f0", height=76,
            )
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0))
            card.grid_propagate(False)

            ctk.CTkFrame(card, height=3, fg_color=accent, corner_radius=0).pack(fill="x")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=(10, 12))

            ctk.CTkLabel(
                inner, text=label,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color="#64748b", anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner, text=str(count),
                font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
                text_color=accent, anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        if not rows:
            from tkinter import messagebox
            messagebox.showinfo("No Records", "No attendance records found for the selected filters.")

        self.after_idle(self._fit_history_tree_columns)

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()