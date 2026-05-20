import customtkinter as ctk
from tkinter import messagebox, ttk
import database
import random
from datetime import datetime

class ManageEnrollment(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.current_student_id = None
        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()
        self.create_ui()

    def create_ui(self):
        #Top Custom Header Bar
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        back_btn = ctk.CTkButton(top_bar, text="← back to Dashboard",
                                 font=ctk.CTkFont(family="Inter", size=14),
                                 fg_color="transparent", text_color="#ffffff",
                                 hover_color="#22259c", width=150, height=40,
                                 corner_radius=0, command=self.back_to_dashboard)
        back_btn.pack(side="left", padx=20, pady=15)
        title = ctk.CTkLabel(top_bar, text="Manage Enrollment",
                             font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                             text_color="#ffffff")
        title.pack(side="left", expand=True, padx=(0, 100))
        logo_placeholder = ctk.CTkLabel(top_bar, text="ABC",
                                        font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                                        text_color="#122aff")
        logo_placeholder.pack(side="right", padx=30)

        #Tab Selector
        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(20, 10))
        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1", width=310, height=46, corner_radius=0)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.add_tab_btn = ctk.CTkButton(tab_pill, text="New Enrollment",
                                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                         fg_color="#122aff", text_color="#ffffff",
                                         corner_radius=0, height=38, width=150,
                                         command=lambda: self.switch_tab("new"))
        self.add_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.list_tab_btn = ctk.CTkButton(tab_pill, text="Enrollment List",
                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                          fg_color="transparent", text_color="#374151",
                                          corner_radius=0, height=38, width=150,
                                          command=lambda: self.switch_tab("list"))
        self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        # 3. --- Workspace ---
        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        self.render_new_enrollment_form()

    def switch_tab(self, tab_target):
        if tab_target == "new":
            self.add_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.list_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.render_new_enrollment_form()
        else:
            self.add_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.list_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.render_enrollment_list_view()

    def render_new_enrollment_form(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()
        self.workspace_canvas.grid_columnconfigure(0, weight=4)
        self.workspace_canvas.grid_columnconfigure(1, weight=5)

        #Search Student
        ctk.CTkLabel(self.workspace_canvas, text="Search Student",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

        search_container = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", height=55, corner_radius=0)
        search_container.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        search_container.pack_propagate(False)

        accent_search = ctk.CTkFrame(search_container, width=8, fg_color="#15165e", corner_radius=0)
        accent_search.pack(side="left", fill="y")

        self.search_entry = ctk.CTkEntry(search_container, placeholder_text="Student ID or Name",
                                         height=35, corner_radius=0, fg_color="#ffffff", text_color="black",
                                         border_width=0)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=15, pady=10)

        search_btn = ctk.CTkButton(self.workspace_canvas, text="SEARCH",
                                   font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                                   width=120, height=35, corner_radius=0, fg_color="#122aff", hover_color="#0b1eb3",
                                   text_color="white", command=self.search_student)
        search_btn.grid(row=2, column=1, sticky="e", pady=(0, 10))

        #Status
        status_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", height=40, corner_radius=0,
                                    border_width=1, border_color="#a1a1a1")
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        status_frame.pack_propagate(False)
        self.student_info = ctk.CTkLabel(status_frame, text="No student selected yet..",
                                         font=ctk.CTkFont(family="Inter", size=14), text_color="#555555")
        self.student_info.pack(anchor="center", pady=8)

        #Enrollment Details
        details_col_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        details_col_frame.grid(row=4, column=0, sticky="nsew", padx=(0, 15))

        ctk.CTkLabel(details_col_frame, text="Enrollment Details",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 4))

        details_card = ctk.CTkFrame(details_col_frame, fg_color="#cbd5e1", height=215, corner_radius=0)
        details_card.pack(fill="x")
        details_card.pack_propagate(False)

        accent_details = ctk.CTkFrame(details_card, width=8, fg_color="#15165e", corner_radius=0)
        accent_details.pack(side="left", fill="y")

        inner_d = ctk.CTkFrame(details_card, fg_color="transparent")
        inner_d.pack(fill="both", expand=True, padx=15, pady=15)
        inner_d.grid_columnconfigure(1, weight=1)

        #Term, School Year, Grade Level, Section
        labels = ["Term", "School Year", "Grade Level", "Section"]
        self.term_combo = ctk.CTkComboBox(inner_d, values=["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"],
                                          height=32, corner_radius=0)
        self.sy_combo = ctk.CTkComboBox(inner_d, values=["2018-2019","2019-2020","2020-2021","2024-2025","2025-2026"],
                                        height=32, corner_radius=0)
        self.grade_combo = ctk.CTkComboBox(inner_d, values=["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6","Grade 7","Grade 8","Grade 9","Grade 10","Grade 11","Grade 12"], height=32, corner_radius=0)
        self.section_combo = ctk.CTkComboBox(inner_d, values=["A","B","C","D","STEM-A","ABM-A","HUMSS-A"], height=32, corner_radius=0)

        for i, (label, widget) in enumerate(zip(labels, [self.term_combo, self.sy_combo, self.grade_combo, self.section_combo])):
            ctk.CTkLabel(inner_d, text=label, font=ctk.CTkFont(family="Inter", size=13), text_color="#444444").grid(row=i, column=0, sticky="w", pady=6)
            widget.grid(row=i, column=1, sticky="ew", padx=(20, 0), pady=6)

        self.term_combo.set("1st Quarter")
        self.sy_combo.set("2025-2026")
        self.grade_combo.set("Grade 7")
        self.section_combo.set("A")

        # Subjects Section (your original)
        subjects_col_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        subjects_col_frame.grid(row=4, column=1, sticky="nsew", padx=(15, 0))

        ctk.CTkLabel(subjects_col_frame, text="Select Subjects",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"), text_color="#000000").pack(anchor="w", pady=(0,5))

        self.subject_frame = ctk.CTkScrollableFrame(subjects_col_frame, fg_color="#cbd5e1", height=215, corner_radius=0)
        self.subject_frame.pack(fill="x")
        self.load_all_subjects()

        # Save Button
        submit_btn = ctk.CTkButton(self.workspace_canvas, text="SAVE ENROLLMENT",
                                   font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                   height=45, width=260, corner_radius=0,
                                   fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                                   command=self.create_enrollment)
        submit_btn.grid(row=5, column=0, columnspan=2, pady=(20, 0), anchor="center")

    def load_all_subjects(self):
        for widget in self.subject_frame.winfo_children():
            widget.destroy()
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT subjectID, subjectName, gradeLevel FROM SUBJECT ORDER BY gradeLevel, subjectName")
            subjects = cursor.fetchall()
            conn.close()
        except:
            subjects = []

        self.subject_vars = {}
        for sub in subjects:
            var = ctk.BooleanVar()
            self.subject_vars[sub['subjectID']] = var
            row_item = ctk.CTkFrame(self.subject_frame, fg_color="transparent")
            row_item.pack(fill="x", padx=15, pady=4)
            chk = ctk.CTkCheckBox(row_item, text=f"{sub['subjectName']} ({sub['gradeLevel']})",
                                  variable=var, fg_color="#122aff")
            chk.pack(anchor="w")

    def search_student(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Required", "Please enter Student ID or Name")
            return
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT studentID, studFname, studLname
            FROM STUDENT
            WHERE CAST(studentID AS TEXT) = ? OR studFname LIKE ? OR studLname LIKE ?
        """, (keyword, f"%{keyword}%", f"%{keyword}%"))
        student = cursor.fetchone()
        conn.close()

        if student:
            self.current_student_id = student['studentID']
            full_name = f"{student['studFname']} {student['studLname']}"
            self.student_info.configure(text=f"Selected: {full_name}", text_color="green")
        else:
            self.student_info.configure(text="Student not found!", text_color="red")
            self.current_student_id = None

    def create_enrollment(self):
        if not self.current_student_id:
            messagebox.showwarning("Warning", "Please search and select a student first")
            return

        term = self.term_combo.get()
        school_year = self.sy_combo.get()
        grade_level = self.grade_combo.get()
        section = self.section_combo.get()

        selected_subjects = [sid for sid, var in getattr(self, 'subject_vars', {}).items() if var.get()]

        if not selected_subjects:
            messagebox.showwarning("Warning", "Please select at least one subject")
            return

        # Generate School ID
        school_id = database.generate_school_id(school_year)

        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ENROLLMENT 
                (studentID, staffID, schoolID, gradeLevel, section, term, schoolYear, enrStatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')
            """, (self.current_student_id, 1, school_id, grade_level, section, term, school_year))

            enrollment_id = cursor.lastrowid

            for subject_id in selected_subjects:
                cursor.execute("INSERT INTO DETAIL (enrollmentID, subjectID) VALUES (?, ?)",
                               (enrollment_id, subject_id))

            conn.commit()
            messagebox.showinfo("Success", f"Enrollment created successfully!\nSchool ID: {school_id}")

            self.search_entry.delete(0, 'end')
            self.student_info.configure(text="No student selected yet..", text_color="#555555")
            self.current_student_id = None

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create enrollment: {str(e)}")
        finally:
            conn.close()

    def render_enrollment_list_view(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.workspace_canvas, text="Current Enrollment Registry",
                     font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                     text_color="black").pack(pady=(10, 5))

        table_wrapper = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", corner_radius=0)
        table_wrapper.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        accent_bar = ctk.CTkFrame(table_wrapper, width=8, fg_color="#15165e", corner_radius=0)
        accent_bar.pack(side="left", fill="y")

        tree_container = ctk.CTkFrame(table_wrapper, fg_color="#ffffff", corner_radius=0)
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 4), pady=4)

        columns = ("Enrollment ID", "School ID", "Student Name", "Grade Level", "School Year", "Term", "Section", "Status")
        self.tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=15)

        col_widths = [110, 130, 180, 100, 110, 110, 80, 90]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        refresh_btn = ctk.CTkButton(self.workspace_canvas, text="Refresh List",
                                    font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                    width=140, height=35, corner_radius=0,
                                    fg_color="#122aff", text_color="white",
                                    command=self.load_enrollments)
        refresh_btn.pack(pady=10)

        self.load_enrollments()

    def load_enrollments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.enrollmentID, e.schoolID, s.studFname, s.studLname, s.studMname,
                       e.gradeLevel, e.schoolYear, e.term, e.section, e.enrStatus
                FROM ENROLLMENT e
                JOIN STUDENT s ON e.studentID = s.studentID
                ORDER BY e.enrollmentID DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                fname = row['studFname'] or ""
                lname = row['studLname'] or ""
                mname = row['studMname'] or ""
                middle = f" {mname[0]}." if mname else ""
                full_name = f"{lname}, {fname}{middle}"

                self.tree.insert("", "end", values=(
                    row['enrollmentID'],
                    row['schoolID'] or "—",
                    full_name,
                    row['gradeLevel'] or "—",
                    row['schoolYear'],
                    row['term'],
                    row['section'] or "—",
                    row['enrStatus']
                ))
        except Exception as e:
            print("Error loading enrollments:", e)

    def back_to_dashboard(self):
        parent_frame = self.master
        self.destroy()
        if hasattr(parent_frame, "welcome_lbl"):
            parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(parent_frame.master, "welcome_lbl"):
            parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))