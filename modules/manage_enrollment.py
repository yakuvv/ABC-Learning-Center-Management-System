import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import database
from database import generate_learner_id
from utils.modern_entry import ModernEntry
from utils.modern_combo import ModernCombo
from utils.term_options import apply_term_combo_for_level

class ManageEnrollment(ctk.CTkFrame):
    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        
        self.user_role = user_role
        self.staff_id = user_id
        self.current_student_id = None
        self.subject_vars = {}
        self.selected_subjects = []
        self._suggestions_rows = []

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.create_ui()

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

        ctk.CTkLabel(top_bar, text="Manage Enrollment",
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

        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(20, 10))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1",
                                width=310, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.new_tab_btn = ctk.CTkButton(tab_pill, text="New Enrollment",
                                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                         fg_color="#122aff", text_color="#ffffff",
                                         corner_radius=19, height=38, width=150,
                                         command=lambda: self.switch_tab("new"))
        self.new_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.list_tab_btn = ctk.CTkButton(tab_pill, text="Enrollment List",
                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                          fg_color="transparent", text_color="#374151",
                                          corner_radius=19, height=38, width=150,
                                          command=lambda: self.switch_tab("list"))
        self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        self.render_new_enrollment_form()

    def switch_tab(self, tab_target):
        if tab_target == "new":
            self.new_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.list_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.render_new_enrollment_form()
        else:
            self.new_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.list_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.render_enrollment_list()

    def _card(self, parent, height=None, scrollable=False):
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        if height:
            card.configure(height=height)
            card.pack_propagate(False)

        accent_container = ctk.CTkFrame(card, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)
        
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        if scrollable:
            inner = ctk.CTkScrollableFrame(card, fg_color="transparent", corner_radius=0)
        else:
            inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)
        return card, inner

    def render_new_enrollment_form(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        self.current_student_id = None

        # --- Search Student ---
        ctk.CTkLabel(self.workspace_canvas, text="SEARCH STUDENT",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#1e293b").pack(anchor="w", pady=(0, 5))

        search_block = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        search_block.pack(fill="x", pady=(0, 4))

        search_card, search_inner = self._card(search_block, height=55)
        search_card.pack(fill="x")

        self.search_entry = ModernEntry(search_inner, placeholder_text="Type Student ID or Name...",
                                        height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search_key)
        self.search_entry.bind("<FocusOut>", lambda _: self.after(250, self._hide_suggestions))

        self.suggest_frame = ctk.CTkFrame(
            search_block, fg_color="#ffffff", corner_radius=10,
            border_width=1, border_color="#cbd5e1"
        )
        self.suggest_lbox = tk.Listbox(
            self.suggest_frame,
            bg="#ffffff", fg="#1e293b",
            selectbackground="#122aff", selectforeground="#ffffff",
            font=("Inter", 12), borderwidth=0, highlightthickness=0,
            height=5, activestyle="none"
        )
        self.suggest_lbox.pack(fill="x", padx=8, pady=8)
        self.suggest_lbox.bind("<<ListboxSelect>>", self._on_suggestion_select)

        self._build_student_info_area(self.workspace_canvas)
        self.show_no_student_selected()

        # === TWO COLUMN LAYOUT ===
        two_col = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        two_col.pack(fill="both", expand=True, pady=(0, 0))
        two_col.columnconfigure(0, weight=1, uniform="col")
        two_col.columnconfigure(1, weight=1, uniform="col")
        two_col.grid_rowconfigure(0, minsize=240)

        # --- LEFT: Enrollment Details ---
        left_frame = ctk.CTkFrame(two_col, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(left_frame, text="ENROLLMENT DETAILS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        det_card, det_inner = self._card(left_frame, height=240)
        det_card.pack(fill="x")

        det_inner.columnconfigure(1, weight=1)

        self.term_combo = self._combo(det_inner, [])
        self.term_combo.configure(command=self.on_term_changed)
        self.level_combo = self._combo(det_inner, [f"Grade {i}" for i in range(1, 13)])
        self.level_combo.configure(command=self.on_level_changed)
        self.group_combo = self._combo(det_inner, ["A", "B", "C", "D", "STEM-A", "ABM-A", "HUMSS-A"])
        self.group_combo.configure(command=self.on_group_changed)

        self.level_combo.set("")
        self.term_combo.set("")
        self.group_combo.set("")
        
        self.on_level_changed("")
        self.update_combo_style(self.term_combo)

        fields = ["Level", "Group Name", "Term"]
        widgets = [self.level_combo, self.group_combo, self.term_combo]

        for i, (label, widget) in enumerate(zip(fields, widgets)):
            ctk.CTkLabel(det_inner, text=label, text_color="#444444",
                         font=ctk.CTkFont(size=13)).grid(row=i, column=0, sticky="w", pady=8)
            widget.grid(row=i, column=1, sticky="ew", padx=(20, 0), pady=8)

        # OK button OUTSIDE the card, below the left column
        ctk.CTkButton(left_frame, text="OK", fg_color="#24894c", hover_color="#1d6f3d", text_color="#ffffff",
                      height=40, corner_radius=8, width=120,
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      command=self.ok_details).pack(anchor="w", pady=(10, 0))

        # --- RIGHT: Modern Container for Confirmation & Subjects ---
        self.right_frame = ctk.CTkFrame(two_col, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.show_confirmation_placeholder()

    def show_confirmation_placeholder(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.right_frame, text="CONFIRMATION DETAILS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        self.confirm_card, self.confirm_inner = self._card(self.right_frame, height=240)
        self.confirm_card.pack(fill="x")

        placeholder_lbl = ctk.CTkLabel(self.confirm_inner,
                                       text="Please select a student and complete the\nEnrollment Details on the left, then click OK.",
                                       font=ctk.CTkFont(family="Inter", size=13),
                                       text_color="#777777")
        placeholder_lbl.pack(expand=True)

    def _build_student_info_area(self, parent):
        self.student_info_card = ctk.CTkFrame(
            parent, fg_color="#ffffff", corner_radius=12,
            border_width=1, border_color="#cbd5e1"
        )
        self.student_info_card.pack(fill="x", pady=(0, 8))

        self.student_info_inner = ctk.CTkFrame(self.student_info_card, fg_color="transparent")
        self.student_info_inner.pack(fill="x", padx=14, pady=10)

    def show_no_student_selected(self):
        for w in self.student_info_inner.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.student_info_inner,
            text="No student selected yet..",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#64748b",
        ).pack(anchor="w")

    def show_selected_student(self, student_id, full_name):
        for w in self.student_info_inner.winfo_children():
            w.destroy()

        row = ctk.CTkFrame(self.student_info_inner, fg_color="transparent")
        row.pack(fill="x")

        name_lbl = ctk.CTkLabel(
            row,
            text=full_name,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#15165e",
        )
        name_lbl.pack(side="left")

        ctk.CTkLabel(
            row,
            text=f"  ·  ID {student_id}",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#64748b",
        ).pack(side="left")

    def _on_search_key(self, event):
        kw = self.search_entry.get().strip()
        if not kw:
            self._hide_suggestions()
            return

        try:
            kid = int(kw)
        except ValueError:
            kid = -1

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT studentID, studFname, studMname, studLname
                FROM STUDENT
                WHERE studentID = ?
                   OR studFname LIKE ?
                   OR studLname LIKE ?
                   OR (studFname || ' ' || studLname) LIKE ?
                ORDER BY studLname, studFname
                LIMIT 8
            """, (kid, f"%{kw}%", f"%{kw}%", f"%{kw}%"))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search student: {str(e)}")
            self._hide_suggestions()
            return

        if rows:
            self._suggestions_rows = rows
            self.suggest_lbox.delete(0, tk.END)
            for row in rows:
                mname = f" {row['studMname'][0]}." if row.get("studMname") else ""
                lbl = f" {row['studFname']}{mname} {row['studLname']}  (Student ID: {row['studentID']})"
                self.suggest_lbox.insert(tk.END, lbl)
            self.suggest_lbox.config(height=min(len(rows), 6))
            self.suggest_frame.pack(fill="x", pady=(4, 0))
        else:
            self._hide_suggestions()

    def _hide_suggestions(self):
        self.suggest_frame.pack_forget()
        self._suggestions_rows = []

    def _on_suggestion_select(self, event):
        sel = self.suggest_lbox.curselection()
        if not sel:
            return
        row = self._suggestions_rows[sel[0]]
        self._select_student(row)
        self.search_entry.delete(0, tk.END)
        self._hide_suggestions()

    def _select_student(self, row):
        self.current_student_id = row["studentID"]
        full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
        self.current_student_name = full_name
        self.show_selected_student(row["studentID"], full_name)

    def ok_details(self):
        # 1. Validate that a student is selected
        if not getattr(self, 'current_student_id', None):
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        # 2. Validate basic registration details
        level = self.level_combo.get()
        group_name = self.group_combo.get()
        term = self.term_combo.get()

        if not level or not group_name or not term:
            messagebox.showwarning("Warning", "Please complete all fields (Level, Group Name, and Term) first!")
            return
        # 3. Show the Confirmation Details layout
        self.show_confirmation_details()

    def show_confirmation_details(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.right_frame, text="CONFIRMATION DETAILS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        self.confirm_card, self.confirm_inner = self._card(self.right_frame, height=240)
        self.confirm_card.pack(fill="x")

        level = self.level_combo.get()
        term = self.term_combo.get()
        group_name = self.group_combo.get()
        name = getattr(self, "current_student_name", "N/A")

        details_frame = ctk.CTkFrame(self.confirm_inner, fg_color="transparent")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        details_frame.columnconfigure(0, weight=0, minsize=120)
        details_frame.columnconfigure(1, weight=1)

        fields = [
            ("NAME:", name),
            ("LEVEL:", level),
            ("GROUP NAME:", group_name),
            ("TERM:", term),
        ]

        for idx, (lbl_txt, val_txt) in enumerate(fields):
            lbl = ctk.CTkLabel(details_frame, text=lbl_txt,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="#15165e")
            lbl.grid(row=idx, column=0, sticky="w", pady=4)
            
            val = ctk.CTkLabel(details_frame, text=val_txt,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="#000000")
            val.grid(row=idx, column=1, sticky="w", pady=4)

        ctk.CTkButton(self.right_frame, text="CONFIRM", fg_color="#24894c", hover_color="#1d6f3d", text_color="#ffffff",
                      height=40, corner_radius=8, width=120,
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      command=self.confirm_details).pack(anchor="w", pady=(10, 0))

    def confirm_details(self):
        # Automatically load the Select Subjects card in the right frame!
        self.show_select_subjects_view()

    def show_select_subjects_view(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        ctk.CTkLabel(header_frame, text="SELECT SUBJECTS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(side="left")

        # Select All Checkbox
        self.select_all_var = ctk.BooleanVar(value=True)
        self.select_all_cb = ctk.CTkCheckBox(header_frame, text="SELECT ALL",
                                              variable=self.select_all_var,
                                              font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                              fg_color="#122aff", hover_color="#0b1eb3",
                                              command=self.toggle_select_all_subjects)
        self.select_all_cb.pack(side="right", padx=5)

        self.sub_card, self.sub_inner = self._card(self.right_frame, height=240, scrollable=True)
        self.sub_card.pack(fill="x")

        # Create bottom buttons frame for Save Profile
        btn_right_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        btn_right_frame.pack(anchor="e", pady=(10, 0))

        ctk.CTkButton(btn_right_frame, text="SAVE STUDENT PROFILE", fg_color="#24894c", hover_color="#1d6f3d",
                      text_color="#ffffff", corner_radius=8, height=40, width=200,
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      command=self.create_enrollment).pack()

        # Load subjects automatically matching the selection!
        self.load_subjects()

    def toggle_select_all_subjects(self):
        val = self.select_all_var.get()
        if hasattr(self, 'subject_vars') and self.subject_vars:
            for var in self.subject_vars.values():
                var.set(val)

    def update_select_all_state(self):
        if hasattr(self, 'subject_vars') and self.subject_vars:
            all_checked = all(var.get() for var in self.subject_vars.values())
            self.select_all_var.set(all_checked)

    def _combo(self, parent, values):
        return ModernCombo(parent, values=values)

    def _extract_program(self, group_name):
        for prog in ("STEM", "ABM", "HUMSS"):
            if prog in group_name:
                return prog
        return None

    def load_subjects(self):
        for widget in self.sub_inner.winfo_children():
            widget.destroy()

        level = self.level_combo.get()
        group_name = self.group_combo.get()

        if not level or not group_name:
            messagebox.showwarning("Warning", "Please select both a Level and Group Name first.")
            self.sub_placeholder = ctk.CTkLabel(self.sub_inner,
                                                 text="Press OK to load subjects.",
                                                 font=ctk.CTkFont(size=13),
                                                 text_color="#888888")
            self.sub_placeholder.pack(expand=True)
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        self.subject_vars = {}

        program = self._extract_program(group_name)
        if program:
            cursor.execute("""
                SELECT subjectID, subjectName, description
                FROM SUBJECT
                WHERE level = ? AND program = ? AND isActive = 1
                ORDER BY subjectName
            """, (level, program))
        else:
            cursor.execute("""
                SELECT subjectID, subjectName, description
                FROM SUBJECT
                WHERE level = ? AND (program IS NULL OR program = '') AND isActive = 1
                ORDER BY subjectName
            """, (level,))

        subjects = cursor.fetchall()
        conn.close()

        if not subjects:
            ctk.CTkLabel(self.sub_inner, text="No subjects found for this selection.",
                         font=ctk.CTkFont(size=13), text_color="#888888").pack(expand=True)
            return

        grid_frame = ctk.CTkFrame(self.sub_inner, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        for idx, s in enumerate(subjects):
            var = ctk.BooleanVar(value=True)
            self.subject_vars[s['subjectID']] = var
            row = idx // 2
            col = idx % 2
            chk = ctk.CTkCheckBox(grid_frame, text=s['subjectName'], variable=var,
                                  font=ctk.CTkFont(family="Inter", size=12),
                                  fg_color="#122aff", hover_color="#0b1eb3",
                                  command=self.update_select_all_state)
            chk.grid(row=row, column=col, sticky="w", pady=4, padx=10)

        if hasattr(self, 'select_all_var'):
            self.select_all_var.set(True)

    # ==================== Other Functions ====================
    def create_enrollment(self):
        if not getattr(self, 'current_student_id', None):
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        level = self.level_combo.get()
        group_name = self.group_combo.get()
        term = self.term_combo.get()

        if not level or not group_name or not term:
            messagebox.showwarning("Warning", "Please complete all fields (Level, Group Name, and Term) first!")
            return

        selected_subjects = [sid for sid, var in self.subject_vars.items() if var.get()]
        if not selected_subjects:
            messagebox.showwarning("Warning", "Select at least one subject before saving.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            staff_id = self.staff_id
            if not staff_id:
                cursor.execute("SELECT staffID FROM STAFF LIMIT 1")
                staff_row = cursor.fetchone()
                staff_id = staff_row['staffID'] if staff_row else 1

            learner_id = generate_learner_id(term)
            program = self._extract_program(group_name)

            cursor.execute("""
                INSERT INTO REGISTRATION
                    (studentID, staffID, learnerID, level, groupName, term, regStatus)
                VALUES (?, ?, ?, ?, ?, ?, 'Active')
            """, (self.current_student_id, staff_id, learner_id,
                  level, group_name, term))

            registration_id = cursor.lastrowid

            cursor.execute("""
                UPDATE STUDENT SET level = ?, program = ? WHERE studentID = ?
            """, (level, program, self.current_student_id))

            for subject_id in selected_subjects:
                cursor.execute("""
                    INSERT INTO REGISTRATION_DETAIL (registrationID, subjectID)
                    VALUES (?, ?)
                """, (registration_id, subject_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Registration saved successfully!\nLearner ID: {learner_id}")

            self.search_entry.delete(0, 'end')
            self.show_no_student_selected()
            self.current_student_id = None
            self.current_student_name = None

            self.level_combo.set("")
            self.term_combo.set("")
            self.group_combo.set("")
            self.on_level_changed("")
            self.update_combo_style(self.term_combo)

            self.show_confirmation_placeholder()
            self.subject_vars = {}

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create registration:\n{e}")

    def render_enrollment_list(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.workspace_canvas, text="ENROLLMENT LIST",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(10, 15))

        search_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=60)
        search_frame.pack(fill="x", pady=(0, 15))
        search_frame.pack_propagate(False)

        inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)

        search_row = ctk.CTkFrame(inner, fg_color="transparent")
        search_row.pack(fill="x")

        self.class_search_entry = ModernEntry(search_row, placeholder_text="Grade 7 - A",
                                              height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.class_search_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(search_row, text="SEARCH", width=130, height=40,
                      fg_color="#122aff", hover_color="#0b1eb3", corner_radius=8,
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      command=self.search_enrollment_by_class).pack(side="right", padx=(10, 0))

        ctk.CTkButton(inner, text="Show All Enrollments", width=180, height=35,
                      fg_color="#374151", hover_color="#272f3a", corner_radius=8,
                      font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                      command=self.load_all_enrollments).pack(anchor="w", pady=(5, 0))

        table_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        table_card.pack(fill="both", expand=True, padx=5)

        self.tree_frame = ctk.CTkFrame(table_card, fg_color="transparent", corner_radius=8)
        self.tree_frame.pack(fill="both", expand=True, padx=15, pady=12)
        self.tree_frame.bind("<Configure>", self._fit_enrollment_tree_to_card)

        import tkinter.ttk as ttk
        columns = ("Learner ID", "Student Name", "Level & Group", "Term", "Staff", "Status")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Enrollment.Treeview.Heading",
            background="#15165e",
            foreground="#ffffff",
            font=("Inter", 11, "bold"),
            bordercolor="#15165e",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Enrollment.Treeview.Heading",
            background=[("active", "#1c1d7c")],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "Enrollment.Treeview",
            font=("Inter", 11),
            rowheight=36,
            fieldbackground="#ffffff",
            background="#ffffff",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Enrollment.Treeview",
            background=[("selected", "#122aff")],
            foreground=[("selected", "#ffffff")],
        )

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Enrollment.Treeview",
        )

        self.tree.tag_configure("evenrow", background="#f8fafc")
        self.tree.tag_configure("oddrow", background="#ffffff")

        self.class_search_entry.bind("<KeyRelease>", lambda e: self.search_enrollment_by_class())

        col_widths = [130, 220, 140, 110, 150, 90]
        col_anchors = ["center", "w", "center", "center", "center", "center"]
        for col, width, anchor in zip(columns, col_widths, col_anchors):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor, minwidth=width)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.load_all_enrollments()
        self.after_idle(self._fit_enrollment_tree_to_card)

    def _fit_enrollment_tree_to_card(self, event=None):
        """Size Treeview row count to fill the white card without squashing row height."""
        if not hasattr(self, "tree") or not hasattr(self, "tree_frame"):
            return
        self.tree_frame.update_idletasks()
        frame_h = self.tree_frame.winfo_height()
        if frame_h < 80:
            return
        row_h = 36
        heading_h = 32
        rows = max((frame_h - heading_h) // row_h, len(self.tree.get_children()), 8)
        rows = min(rows, 40)
        if int(self.tree.cget("height")) != rows:
            self.tree.configure(height=rows)

    def _insert_enrollment_rows(self, rows):
        for idx, row in enumerate(rows):
            full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
            level_group = f"{row['level']} - {row['groupName']}"
            staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                "end",
                values=(
                    row["learnerID"] or "—",
                    full_name,
                    level_group,
                    row["term"],
                    staff_name,
                    row["regStatus"],
                ),
                tags=(tag,),
            )
        self.after_idle(self._fit_enrollment_tree_to_card)

    def load_all_enrollments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.learnerID, r.level, r.groupName, r.term, r.regStatus,
                       s.studFname, s.studLname, s.studMname,
                       st.staffFname, st.staffLname
                FROM REGISTRATION r
                JOIN STUDENT s ON r.studentID = s.studentID
                LEFT JOIN STAFF st ON r.staffID = st.staffID
                ORDER BY r.registrationID DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            self._insert_enrollment_rows(rows)
        except Exception as e:
            print("Error loading enrollments:", e)

    def search_enrollment_by_class(self):
        keyword = self.class_search_entry.get().strip()
        if not keyword:
            self.load_all_enrollments()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.learnerID, r.level, r.groupName, r.term, r.regStatus,
                       s.studFname, s.studLname, s.studMname,
                       st.staffFname, st.staffLname
                FROM REGISTRATION r
                JOIN STUDENT s ON r.studentID = s.studentID
                LEFT JOIN STAFF st ON r.staffID = st.staffID
                WHERE UPPER(r.level || ' - ' || r.groupName) LIKE UPPER(?)
                ORDER BY r.registrationID DESC
            """, (f"%{keyword}%",))
            rows = cursor.fetchall()
            conn.close()

            self._insert_enrollment_rows(rows)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_level_changed(self, choice):
        if not choice:
            self.group_combo.configure(values=[])
            self.group_combo.set("")
            self.group_combo.configure(state="disabled")
            apply_term_combo_for_level(self.term_combo, "")
        elif choice in [f"Grade {i}" for i in range(1, 11)]:
            self.group_combo.configure(state="readonly")
            self.group_combo.configure(values=["A", "B", "C", "D"])
            self.group_combo.set("")
            apply_term_combo_for_level(self.term_combo, choice)
        else:
            self.group_combo.configure(state="readonly")
            self.group_combo.configure(values=["STEM-A", "ABM-A", "HUMSS-A"])
            self.group_combo.set("")
            apply_term_combo_for_level(self.term_combo, choice)

        self.update_combo_style(self.level_combo)
        self.update_combo_style(self.term_combo)
        self.update_combo_style(self.group_combo)

    def on_term_changed(self, choice):
        self.update_combo_style(self.term_combo)

    def on_group_changed(self, choice):
        self.update_combo_style(self.group_combo)

    def update_combo_style(self, combo):
        val = combo.get().strip()
        if val:
            combo.configure(text_color="black", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
        else:
            combo.configure(text_color="#777777", font=ctk.CTkFont(family="Inter", size=13, weight="normal"))

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()