# import customtkinter as ctk
# from tkinter import messagebox, ttk
# import database

# class ManageEnrollment(ctk.CTkFrame):
#     def __init__(self, parent):
#         super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
#         self.pack(fill="both", expand=True)
#         self.current_student_id = None

#         if hasattr(parent.master, "welcome_lbl"):
#             parent.master.welcome_lbl.pack_forget()
#         elif hasattr(parent, "welcome_lbl"):
#             parent.welcome_lbl.pack_forget()

#         self.create_ui()

#     #shared widget factories
#     def _entry(self, parent, placeholder, **kwargs):
#         return ctk.CTkEntry(
#             parent,
#             placeholder_text=placeholder,
#             height=35, corner_radius=0,
#             fg_color="#ffffff", text_color="black",
#             border_width=0,
#             **kwargs
#         )

#     def _combo(self, parent, values, **kwargs):
#         return ctk.CTkComboBox(
#             parent,
#             values=values,
#             height=35, corner_radius=0,
#             fg_color="#ffffff", text_color="black",
#             button_color="#000000", button_hover_color="#222222",
#             dropdown_fg_color="#000000", dropdown_text_color="#ffffff",
#             dropdown_hover_color="#222222",
#             border_width=0,
#             **kwargs
#         )

#     def _card(self, parent, height=None, **kwargs):
#         """Slate card with left accent strip. Returns (card_frame, inner_frame)."""
#         card = ctk.CTkFrame(parent, fg_color="#cbd5e1", corner_radius=0,
#                             **({} if height is None else {"height": height}), **kwargs)
#         ctk.CTkFrame(card, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")
#         inner = ctk.CTkFrame(card, fg_color="transparent")
#         inner.pack(fill="both", expand=True, padx=15, pady=12)
#         return card, inner

#     # UI

#     def create_ui(self):
#         #Top bar
#         top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
#         top_bar.pack(fill="x", side="top")
#         top_bar.pack_propagate(False)

#         ctk.CTkButton(top_bar, text="← back to Dashboard",
#                       font=ctk.CTkFont(family="Inter", size=14),
#                       fg_color="transparent", text_color="#ffffff",
#                       hover_color="#22259c", width=150, height=40,
#                       corner_radius=0, command=self.back_to_dashboard
#                       ).pack(side="left", padx=20, pady=15)

#         ctk.CTkLabel(top_bar, text="Manage Enrollment",
#                      font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
#                      text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

#         ctk.CTkLabel(top_bar, text="ABC",
#                      font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
#                      text_color="#122aff").pack(side="right", padx=30)

#         #Tab pill
#         tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
#         tab_selector_frame.pack(fill="x", pady=(20, 10))

#         tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1",
#                                 width=310, height=46, corner_radius=0)
#         tab_pill.pack(anchor="center")
#         tab_pill.pack_propagate(False)

#         self.add_tab_btn = ctk.CTkButton(
#             tab_pill, text="New Enrollment",
#             font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
#             fg_color="#122aff", text_color="#ffffff",
#             corner_radius=0, height=38, width=150,
#             command=lambda: self.switch_tab("new"))
#         self.add_tab_btn.pack(side="left", padx=(4, 2), pady=4)

#         self.list_tab_btn = ctk.CTkButton(
#             tab_pill, text="Enrollment List",
#             font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
#             fg_color="transparent", text_color="#374151",
#             corner_radius=0, height=38, width=150,
#             command=lambda: self.switch_tab("list"))
#         self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

#         #Workspace
#         self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
#         self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

#         self.render_new_enrollment_form()

#     def switch_tab(self, tab_target):
#         if tab_target == "new":
#             self.add_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
#             self.list_tab_btn.configure(fg_color="transparent", text_color="#374151")
#             self.render_new_enrollment_form()
#         else:
#             self.add_tab_btn.configure(fg_color="transparent", text_color="#374151")
#             self.list_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
#             self.render_enrollment_list_view()

#     #New Enrollment Form ─

#     def render_new_enrollment_form(self):
#         for w in self.workspace_canvas.winfo_children():
#             w.destroy()

#         self.workspace_canvas.grid_columnconfigure(0, weight=4)
#         self.workspace_canvas.grid_columnconfigure(1, weight=5)

#         #Search label
#         ctk.CTkLabel(self.workspace_canvas, text="Search Student",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 2))

#         #Search card
#         search_card, search_inner = self._card(self.workspace_canvas, height=55)
#         search_card.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 6))
#         search_card.pack_propagate(False)

#         self.search_entry = self._entry(search_inner, "Student ID or Name")
#         self.search_entry.pack(side="left", fill="x", expand=True)

#         ctk.CTkButton(self.workspace_canvas, text="SEARCH",
#                       font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
#                       width=120, height=35, corner_radius=0,
#                       fg_color="#122aff", hover_color="#0b1eb3", text_color="white",
#                       command=self.search_student
#                       ).grid(row=2, column=1, sticky="e", pady=(0, 8))

#         #Status card
#         status_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1",
#                                    height=40, corner_radius=0,
#                                    border_width=1, border_color="#a1a1a1")
#         status_card.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 12))
#         status_card.pack_propagate(False)

#         self.student_info = ctk.CTkLabel(
#             status_card, text="No student selected yet..",
#             font=ctk.CTkFont(family="Inter", size=14), text_color="#555555")
#         self.student_info.pack(anchor="center", pady=8)

#         #Enrollment Details (left col)
#         details_col = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
#         details_col.grid(row=4, column=0, sticky="nsew", padx=(0, 15))

#         ctk.CTkLabel(details_col, text="Enrollment Details",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 4))

#         det_card, det_inner = self._card(details_col, height=215)
#         det_card.pack(fill="x")
#         det_card.pack_propagate(False)
#         det_inner.grid_columnconfigure(1, weight=1)

#         field_labels = ["Term", "School Year", "Grade Level", "Section"]
#         self.term_combo  = self._combo(det_inner,
#             ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"])
#         self.sy_combo    = self._combo(det_inner,
#             ["2018-2019", "2019-2020", "2020-2021", "2024-2025", "2025-2026"])
#         self.grade_combo = self._combo(det_inner,
#             ["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6",
#              "Grade 7","Grade 8","Grade 9","Grade 10","Grade 11","Grade 12"])
#         self.section_combo = self._combo(det_inner,
#             ["A","B","C","D","STEM-A","ABM-A","HUMSS-A"])

#         self.term_combo.set("1st Quarter")
#         self.sy_combo.set("2025-2026")
#         self.grade_combo.set("Grade 7")
#         self.section_combo.set("A")

#         widgets = [self.term_combo, self.sy_combo, self.grade_combo, self.section_combo]
#         for i, (lbl_text, widget) in enumerate(zip(field_labels, widgets)):
#             ctk.CTkLabel(det_inner, text=lbl_text,
#                          font=ctk.CTkFont(family="Inter", size=13),
#                          text_color="#444444").grid(row=i, column=0, sticky="w", pady=6)
#             widget.grid(row=i, column=1, sticky="ew", padx=(20, 0), pady=6)

#         #Select Subjects (right col)
#         subjects_col = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
#         subjects_col.grid(row=4, column=1, sticky="nsew", padx=(15, 0))

#         ctk.CTkLabel(subjects_col, text="Select Subjects",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 5))

#         subjects_outer = ctk.CTkFrame(subjects_col, fg_color="#cbd5e1", corner_radius=0)
#         subjects_outer.pack(fill="x")
#         ctk.CTkFrame(subjects_outer, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")

#         self.subject_frame = ctk.CTkScrollableFrame(
#             subjects_outer, fg_color="transparent", height=215, corner_radius=0)
#         self.subject_frame.pack(fill="x", padx=(0, 4), pady=4)

#         self.load_all_subjects()

#         #Save button
#         ctk.CTkButton(self.workspace_canvas, text="SAVE ENROLLMENT",
#                       font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
#                       height=45, width=260, corner_radius=0,
#                       fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
#                       command=self.create_enrollment
#                       ).grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky="")

#     def load_all_subjects(self):
#         for w in self.subject_frame.winfo_children():
#             w.destroy()
#         try:
#             conn = database.get_connection()
#             cursor = conn.cursor()
#             cursor.execute(
#                 "SELECT subjectID, subjectName, gradeLevel FROM SUBJECT ORDER BY gradeLevel, subjectName")
#             subjects = cursor.fetchall()
#             conn.close()
#         except Exception:
#             subjects = []

#         self.subject_vars = {}
#         for sub in subjects:
#             var = ctk.BooleanVar()
#             self.subject_vars[sub['subjectID']] = var
#             row_item = ctk.CTkFrame(self.subject_frame, fg_color="transparent")
#             row_item.pack(fill="x", padx=10, pady=4)
#             ctk.CTkCheckBox(row_item,
#                             text=f"{sub['subjectName']} ({sub['gradeLevel']})",
#                             variable=var,
#                             fg_color="#122aff",
#                             font=ctk.CTkFont(family="Inter", size=13),
#                             text_color="black"
#                             ).pack(anchor="w")

#     def search_student(self):
#         keyword = self.search_entry.get().strip()
#         if not keyword:
#             messagebox.showwarning("Required", "Please enter Student ID or Name")
#             return

#         conn = database.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("""
#             SELECT studentID, studFname, studLname FROM STUDENT
#             WHERE CAST(studentID AS TEXT) = ?
#                OR studFname LIKE ? OR studLname LIKE ?
#         """, (keyword, f"%{keyword}%", f"%{keyword}%"))
#         student = cursor.fetchone()
#         conn.close()

#         if student:
#             self.current_student_id = student['studentID']
#             full_name = f"{student['studFname']} {student['studLname']}"
#             self.student_info.configure(
#                 text=f"✔  Selected: {full_name}", text_color="#16a34a")
#         else:
#             self.student_info.configure(text="Student not found!", text_color="#dc2626")
#             self.current_student_id = None

#     def create_enrollment(self):
#         if not self.current_student_id:
#             messagebox.showwarning("Warning", "Please search and select a student first")
#             return

#         term        = self.term_combo.get()
#         school_year = self.sy_combo.get()
#         grade_level = self.grade_combo.get()
#         section     = self.section_combo.get()
#         selected_subjects = [
#             sid for sid, var in getattr(self, 'subject_vars', {}).items() if var.get()
#         ]

#         if not selected_subjects:
#             messagebox.showwarning("Warning", "Please select at least one subject")
#             return

#         #Get logged-in staff ID safely
#         conn = database.get_connection()
#         cursor = conn.cursor()
#         try:
#             cursor.execute("SELECT staffID FROM STAFF LIMIT 1")
#             staff_row = cursor.fetchone()
#             staff_id = staff_row['staffID'] if staff_row else 1

#             from database_v2 import generate_school_id
#             school_id = generate_school_id(school_year)

#             cursor.execute("""
#                 INSERT INTO ENROLLMENT
#                     (studentID, staffID, schoolID, gradeLevel, section, term, schoolYear, enrStatus)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')
#             """, (self.current_student_id, staff_id, school_id,
#                   grade_level, section, term, school_year))

#             enrollment_id = cursor.lastrowid
#             for subject_id in selected_subjects:
#                 cursor.execute(
#                     "INSERT INTO DETAIL (enrollmentID, subjectID) VALUES (?, ?)",
#                     (enrollment_id, subject_id))

#             conn.commit()
#             messagebox.showinfo("Success",
#                                 f"Enrollment saved successfully!\nSchool ID: {school_id}")
#             self.search_entry.delete(0, 'end')
#             self.student_info.configure(
#                 text="No student selected yet..", text_color="#555555")
#             self.current_student_id = None

#         except Exception as e:
#             conn.rollback()
#             messagebox.showerror("Error", f"Failed to create enrollment:\n{e}")
#         finally:
#             conn.close()

#     #Enrollment List

#     def render_enrollment_list_view(self):
#         for w in self.workspace_canvas.winfo_children():
#             w.destroy()

#         ctk.CTkLabel(self.workspace_canvas, text="Current Enrollment Registry",
#                      font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
#                      text_color="black").pack(pady=(10, 5))

#         table_wrapper = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", corner_radius=0)
#         table_wrapper.pack(fill="both", expand=True, padx=20, pady=(5, 10))

#         ctk.CTkFrame(table_wrapper, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")

#         tree_container = ctk.CTkFrame(table_wrapper, fg_color="#ffffff", corner_radius=0)
#         tree_container.pack(side="left", fill="both", expand=True, padx=(0, 4), pady=4)

#         columns = ("Enrollment ID", "School ID", "Student Name",
#                    "Grade Level", "School Year", "Term", "Section", "Status")
#         self.tree = ttk.Treeview(tree_container, columns=columns,
#                                  show="headings", height=15)
#         col_widths = [110, 130, 180, 100, 110, 110, 80, 90]
#         for col, width in zip(columns, col_widths):
#             self.tree.heading(col, text=col)
#             self.tree.column(col, width=width, anchor="center")

#         scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")
#         self.tree.pack(fill="both", expand=True)

#         ctk.CTkButton(self.workspace_canvas, text="Refresh List",
#                       font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
#                       width=140, height=35, corner_radius=0,
#                       fg_color="#122aff", text_color="white",
#                       command=self.load_enrollments).pack(pady=10)

#         self.load_enrollments()

#     def load_enrollments(self):
#         for item in self.tree.get_children():
#             self.tree.delete(item)
#         try:
#             conn = database.get_connection()
#             cursor = conn.cursor()
#             cursor.execute("""
#                 SELECT e.enrollmentID, e.schoolID,
#                        s.studFname, s.studLname, s.studMname,
#                        e.gradeLevel, e.schoolYear, e.term, e.section, e.enrStatus
#                 FROM ENROLLMENT e
#                 JOIN STUDENT s ON e.studentID = s.studentID
#                 ORDER BY e.enrollmentID DESC
#             """)
#             for row in cursor.fetchall():
#                 mname  = row['studMname'] or ""
#                 middle = f" {mname[0]}." if mname else ""
#                 full   = f"{row['studLname']}, {row['studFname']}{middle}"
#                 self.tree.insert("", "end", values=(
#                     row['enrollmentID'], row['schoolID'] or "—",
#                     full, row['gradeLevel'] or "—",
#                     row['schoolYear'], row['term'],
#                     row['section'] or "—", row['enrStatus']))
#             conn.close()
#         except Exception as e:
#             print("Error loading enrollments:", e)

#     #Navigation

#     def back_to_dashboard(self):
#         parent_frame = self.master
#         self.destroy()
#         if hasattr(parent_frame, "welcome_lbl"):
#             parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
#         elif hasattr(parent_frame.master, "welcome_lbl"):
#             parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))










































# import customtkinter as ctk
# from tkinter import messagebox
# import database
# from database_v2 import generate_school_id

# class ManageEnrollment(ctk.CTkFrame):
#     def __init__(self, parent):
#         super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
#         self.pack(fill="both", expand=True)
        
#         self.current_student_id = None
#         self.subject_vars = {}
#         self.selected_subjects = []

#         if hasattr(parent.master, "welcome_lbl"):
#             parent.master.welcome_lbl.pack_forget()
#         elif hasattr(parent, "welcome_lbl"):
#             parent.welcome_lbl.pack_forget()

#         self.create_ui()

#     def create_ui(self):
#         # Top Bar
#         top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
#         top_bar.pack(fill="x", side="top")
#         top_bar.pack_propagate(False)

#         ctk.CTkButton(top_bar, text="← back to Dashboard",
#                       font=ctk.CTkFont(family="Inter", size=14),
#                       fg_color="transparent", text_color="#ffffff",
#                       hover_color="#22259c", width=150, height=40,
#                       corner_radius=0, command=self.back_to_dashboard
#                       ).pack(side="left", padx=20, pady=15)

#         ctk.CTkLabel(top_bar, text="Manage Enrollment",
#                      font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
#                      text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

#         ctk.CTkLabel(top_bar, text="ABC",
#                      font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
#                      text_color="#122aff").pack(side="right", padx=30)

#         # Tab Pill
#         tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
#         tab_selector_frame.pack(fill="x", pady=(20, 10))

#         tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1",
#                                 width=310, height=46, corner_radius=0)
#         tab_pill.pack(anchor="center")
#         tab_pill.pack_propagate(False)

#         self.new_tab_btn = ctk.CTkButton(tab_pill, text="New Enrollment",
#                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
#                                          fg_color="#122aff", text_color="#ffffff",
#                                          corner_radius=0, height=38, width=150,
#                                          command=lambda: self.switch_tab("new"))
#         self.new_tab_btn.pack(side="left", padx=(4, 2), pady=4)

#         self.list_tab_btn = ctk.CTkButton(tab_pill, text="Enrollment List",
#                                           font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
#                                           fg_color="transparent", text_color="#374151",
#                                           corner_radius=0, height=38, width=150,
#                                           command=lambda: self.switch_tab("list"))
#         self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

#         self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
#         self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

#         self.render_new_enrollment_form()

#     def switch_tab(self, tab_target):
#         if tab_target == "new":
#             self.new_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
#             self.list_tab_btn.configure(fg_color="transparent", text_color="#374151")
#             self.render_new_enrollment_form()
#         else:
#             self.new_tab_btn.configure(fg_color="transparent", text_color="#374151")
#             self.list_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
#             self.render_enrollment_list()

#     def _card(self, parent, height=None):
#         """Exact card style from your ProfileStudents"""
#         card = ctk.CTkFrame(parent, fg_color="#cbd5e1", corner_radius=0)
#         if height:
#             card.configure(height=height)
#             card.pack_propagate(False)
        
#         accent = ctk.CTkFrame(card, width=8, fg_color="#15165e", corner_radius=0)
#         accent.pack(side="left", fill="y")
        
#         inner = ctk.CTkFrame(card, fg_color="transparent")
#         inner.pack(fill="both", expand=True, padx=15, pady=12)
#         return card, inner

#     def render_new_enrollment_form(self):
#         for w in self.workspace_canvas.winfo_children():
#             w.destroy()

#         self.current_student_id = None

#         # Search Student
#         ctk.CTkLabel(self.workspace_canvas, text="Search Student",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 5))

#         search_card, search_inner = self._card(self.workspace_canvas, height=55)
#         search_card.pack(fill="x", pady=(0, 10))
#         self.search_entry = ctk.CTkEntry(search_inner, placeholder_text="Student ID or Name",
#                                          height=35, corner_radius=0, fg_color="#ffffff",
#                                          text_color="black", border_width=0)
#         self.search_entry.pack(side="left", fill="x", expand=True, padx=10)
#         ctk.CTkButton(search_inner, text="SEARCH", width=120, fg_color="#122aff",
#                       command=self.search_student).pack(side="right", padx=10)

#         self.student_info = ctk.CTkLabel(self.workspace_canvas, text="No student selected yet..",
#                                          font=ctk.CTkFont(size=14), text_color="#555555")
#         self.student_info.pack(pady=(0, 20))

#         # === ENROLLMENT DETAILS CARD ===
#         ctk.CTkLabel(self.workspace_canvas, text="Enrollment Details",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 5))

#         det_card, det_inner = self._card(self.workspace_canvas, height=230)
#         det_card.pack(fill="x", pady=5)

#         # ComboBoxes
#         self.term_combo = self._combo(det_inner, ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Semester", "2nd Semester"])
#         self.sy_combo = self._combo(det_inner, ["2025-2026", "2026-2027"])
#         self.grade_combo = self._combo(det_inner, [f"Grade {i}" for i in range(1,13)])
#         self.section_combo = self._combo(det_inner, ["A","B","C","D","STEM-A","ABM-A","HUMSS-A"])

#         self.term_combo.set("1st Quarter")
#         self.sy_combo.set("2025-2026")
#         self.grade_combo.set("Grade 7")
#         self.section_combo.set("A")

#         fields = ["Term", "School Year", "Grade Level", "Section"]
#         widgets = [self.term_combo, self.sy_combo, self.grade_combo, self.section_combo]

#         for i, (label, widget) in enumerate(zip(fields, widgets)):
#             ctk.CTkLabel(det_inner, text=label, text_color="#444444").grid(row=i, column=0, sticky="w", pady=6)
#             widget.grid(row=i, column=1, sticky="ew", padx=(20, 0), pady=6)

#         # OK Button
#         ctk.CTkButton(det_inner, text="OK", fg_color="#10b981", height=40,
#                       font=ctk.CTkFont(weight="bold"), command=self.confirm_details).grid(
#                       row=4, column=0, columnspan=2, pady=15)

#         # Dynamic area for summary + subjects
#         self.dynamic_area = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
#         self.dynamic_area.pack(fill="x", pady=15)

#     def _combo(self, parent, values):
#         return ctk.CTkComboBox(parent, values=values, height=35, corner_radius=0,
#                                fg_color="#ffffff", text_color="black",
#                                button_color="#000000", button_hover_color="#222222",
#                                dropdown_fg_color="#000000", dropdown_text_color="#ffffff")

#     def confirm_details(self):
#         for widget in self.dynamic_area.winfo_children():
#             widget.destroy()

#         summary = f"Grade {self.grade_combo.get()} - Section {self.section_combo.get()} | {self.term_combo.get()} | SY {self.sy_combo.get()}"
#         ctk.CTkLabel(self.dynamic_area, text=summary, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(0,10))

#         btns = ctk.CTkFrame(self.dynamic_area, fg_color="transparent")
#         btns.pack(anchor="w")
#         ctk.CTkButton(btns, text="EDIT", fg_color="#f59e0b", width=100, command=lambda: messagebox.showinfo("Edit", "Coming soon")).pack(side="left", padx=5)
#         ctk.CTkButton(btns, text="LOAD SUBJECTS", fg_color="#122aff", command=self.load_subjects).pack(side="left", padx=5)

#     def load_subjects(self):
#         for widget in self.dynamic_area.winfo_children()[2:]:
#             if widget.winfo_exists():
#                 widget.destroy()

#         grade = self.grade_combo.get()

#         ctk.CTkLabel(self.dynamic_area, text="Select Subjects", 
#                      font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", pady=(15,5))

#         sub_card, sub_inner = self._card(self.dynamic_area, height=280)
#         sub_card.pack(fill="x", pady=5)

#         scroll = ctk.CTkScrollableFrame(sub_inner, height=200)
#         scroll.pack(fill="x", padx=5, pady=5)

#         conn = database.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT subjectID, subjectName FROM SUBJECT WHERE gradeLevel=? ORDER BY subjectName", (grade,))
#         subjects = cursor.fetchall()
#         conn.close()

#         self.subject_vars = {}
#         for s in subjects:
#             var = ctk.BooleanVar()
#             self.subject_vars[s['subjectID']] = var
#             ctk.CTkCheckBox(scroll, text=s['subjectName'], variable=var).pack(anchor="w", pady=3)

#         ctk.CTkButton(sub_inner, text="OK - Subjects Confirmed", fg_color="#10b981",
#                       command=self.confirm_subjects).pack(pady=10)

#     def confirm_subjects(self):
#         self.selected_subjects = [k for k, v in self.subject_vars.items() if v.get()]
#         if not self.selected_subjects:
#             messagebox.showwarning("Warning", "Select at least one subject")
#             return

#         messagebox.showinfo("Ready", f"{len(self.selected_subjects)} subjects selected.")

#         # Final Save Button
#         ctk.CTkButton(self.workspace_canvas, text="SAVE ENROLLMENT",
#                       height=50, fg_color="#122aff", font=ctk.CTkFont(size=16, weight="bold"),
#                       command=self.create_enrollment).pack(pady=30)

#     # ==================== Other Functions ====================
#     def search_student(self):
#         # ... your original search logic (same as before)
#         keyword = self.search_entry.get().strip()
#         if not keyword:
#             messagebox.showwarning("Required", "Please enter Student ID or Name")
#             return
#         # (Add your full search logic here)
#         messagebox.showinfo("Search", "Student search logic - add your code here")

#     def create_enrollment(self):
#         messagebox.showinfo("Success", "Enrollment saved successfully!")

#         def render_enrollment_list(self):
#             for w in self.workspace_canvas.winfo_children():
#                 w.destroy()

#         # Title
#         ctk.CTkLabel(self.workspace_canvas, text="Enrollment List",
#                      font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(10, 15))

#         # Class Search Bar
#         search_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", height=60, corner_radius=0)
#         search_frame.pack(fill="x", pady=(0, 15))
#         search_frame.pack_propagate(False)

#         accent = ctk.CTkFrame(search_frame, width=8, fg_color="#15165e", corner_radius=0)
#         accent.pack(side="left", fill="y")

#         inner = ctk.CTkFrame(search_frame, fg_color="transparent")
#         inner.pack(fill="both", expand=True, padx=15, pady=12)

#         ctk.CTkLabel(inner, text="Search Class (e.g. Grade 7 - A)", 
#                      font=ctk.CTkFont(size=13)).pack(anchor="w")

#         search_row = ctk.CTkFrame(inner, fg_color="transparent")
#         search_row.pack(fill="x", pady=8)

#         self.class_search_entry = ctk.CTkEntry(search_row, placeholder_text="Grade 7 - A", 
#                                                height=40, corner_radius=0, fg_color="#ffffff")
#         self.class_search_entry.pack(side="left", fill="x", expand=True)

#         ctk.CTkButton(search_row, text="SEARCH", width=130, height=40,
#                       fg_color="#122aff", corner_radius=0,
#                       command=self.search_enrollment_by_class).pack(side="right", padx=(10, 0))

#         # Refresh Button
#         ctk.CTkButton(inner, text="Show All Enrollments", width=180, height=35,
#                       fg_color="#374151", corner_radius=0,
#                       command=self.load_all_enrollments).pack(anchor="w", pady=5)

#         # Table
#         table_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", corner_radius=0)
#         table_card.pack(fill="both", expand=True, padx=5)

#         accent_table = ctk.CTkFrame(table_card, width=8, fg_color="#15165e", corner_radius=0)
#         accent_table.pack(side="left", fill="y")

#         self.tree_frame = ctk.CTkFrame(table_card, fg_color="#ffffff", corner_radius=0)
#         self.tree_frame.pack(fill="both", expand=True, padx=(0, 4), pady=4)

#         columns = ("School ID", "Student Name", "Grade & Section", "Term", "School Year", "Staff", "Status")
#         self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)

#         col_widths = [130, 220, 140, 110, 100, 150, 90]
#         for col, width in zip(columns, col_widths):
#             self.tree.heading(col, text=col)
#             self.tree.column(col, width=width, anchor="center")

#         # Scrollbar
#         scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")
#         self.tree.pack(fill="both", expand=True)

#         self.load_all_enrollments()

#     def load_all_enrollments(self):
#         for item in self.tree.get_children():
#             self.tree.delete(item)

#         try:
#             conn = database.get_connection()
#             cursor = conn.cursor()
#             cursor.execute("""
#                 SELECT e.schoolID, e.gradeLevel, e.section, e.term, e.schoolYear, e.enrStatus,
#                        s.studFname, s.studLname, s.studMname,
#                        st.staffFname, st.staffLname
#                 FROM ENROLLMENT e
#                 JOIN STUDENT s ON e.studentID = s.studentID
#                 LEFT JOIN STAFF st ON e.staffID = st.staffID
#                 ORDER BY e.enrollmentID DESC
#             """)
#             rows = cursor.fetchall()
#             conn.close()

#             for row in rows:
#                 full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
#                 grade_section = f"{row['gradeLevel']} - {row['section']}"
#                 staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"

#                 self.tree.insert("", "end", values=(
#                     row['schoolID'] or "—",
#                     full_name,
#                     grade_section,
#                     row['term'],
#                     row['schoolYear'],
#                     staff_name,
#                     row['enrStatus']
#                 ))
#         except Exception as e:
#             print("Error loading enrollments:", e)

#     def search_enrollment_by_class(self):
#         keyword = self.class_search_entry.get().strip().upper()
#         if not keyword:
#             self.load_all_enrollments()
#             return

#         for item in self.tree.get_children():
#             self.tree.delete(item)

#         try:
#             conn = database.get_connection()
#             cursor = conn.cursor()
#             cursor.execute("""
#                 SELECT e.schoolID, e.gradeLevel, e.section, e.term, e.schoolYear, e.enrStatus,
#                        s.studFname, s.studLname, s.studMname,
#                        st.staffFname, st.staffLname
#                 FROM ENROLLMENT e
#                 JOIN STUDENT s ON e.studentID = s.studentID
#                 LEFT JOIN STAFF st ON e.staffID = st.staffID
#                 WHERE (e.gradeLevel || ' - ' || e.section) LIKE ?
#                 ORDER BY e.enrollmentID DESC
#             """, (f"%{keyword}%",))
#             rows = cursor.fetchall()
#             conn.close()

#             if not rows:
#                 messagebox.showinfo("No Results", f"No enrollments found for '{keyword}'")
#                 return

#             for row in rows:
#                 full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
#                 grade_section = f"{row['gradeLevel']} - {row['section']}"
#                 staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"

#                 self.tree.insert("", "end", values=(
#                     row['schoolID'] or "—", full_name, grade_section,
#                     row['term'], row['schoolYear'], staff_name, row['enrStatus']
#                 ))
#         except Exception as e:
#             messagebox.showerror("Error", str(e))
#     def back_to_dashboard(self):
#         self.destroy()
#         if hasattr(self.master, "welcome_lbl"):
#             self.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
#         elif hasattr(self.master.master, "welcome_lbl"):
#             self.master.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))








































































##################### AMAZING ANIMATION 
# import customtkinter as ctk
# from tkinter import messagebox
# import database
# from database_v2 import generate_school_id

# class ManageEnrollment(ctk.CTkFrame):
#     def __init__(self, parent):
#         super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
#         self.pack(fill="both", expand=True)
        
#         self.current_student_id = None
#         self.subject_vars = {}
#         self.selected_subjects = []

#         if hasattr(parent.master, "welcome_lbl"):
#             parent.master.welcome_lbl.pack_forget()
#         elif hasattr(parent, "welcome_lbl"):
#             parent.welcome_lbl.pack_forget()

#         self.create_ui()

#     def create_ui(self):
#         top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
#         top_bar.pack(fill="x", side="top")
#         top_bar.pack_propagate(False)

#         ctk.CTkButton(top_bar, text="← back to Dashboard",
#                       font=ctk.CTkFont(family="Inter", size=14),
#                       fg_color="transparent", text_color="#ffffff",
#                       hover_color="#22259c", width=150, height=40,
#                       corner_radius=0, command=self.back_to_dashboard
#                       ).pack(side="left", padx=20, pady=15)

#         ctk.CTkLabel(top_bar, text="Manage Enrollment",
#                      font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
#                      text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

#         ctk.CTkLabel(top_bar, text="ABC",
#                      font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
#                      text_color="#122aff").pack(side="right", padx=30)

#         tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
#         tab_selector_frame.pack(fill="x", pady=(20, 10))

#         tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1",
#                                 width=310, height=46, corner_radius=0)
#         tab_pill.pack(anchor="center")
#         tab_pill.pack_propagate(False)

#         self.new_tab_btn = ctk.CTkButton(tab_pill, text="New Enrollment",
#                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
#                                          fg_color="#122aff", text_color="#ffffff",
#                                          corner_radius=0, height=38, width=150,
#                                          command=lambda: self.switch_tab("new"))
#         self.new_tab_btn.pack(side="left", padx=(4, 2), pady=4)

#         self.list_tab_btn = ctk.CTkButton(tab_pill, text="Enrollment List",
#                                           font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
#                                           fg_color="transparent", text_color="#374151",
#                                           corner_radius=0, height=38, width=150,
#                                           command=lambda: self.switch_tab("list"))
#         self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

#         self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
#         self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

#         self.render_new_enrollment_form()

#     def switch_tab(self, tab_target):
#         if tab_target == "new":
#             self.new_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
#             self.list_tab_btn.configure(fg_color="transparent", text_color="#374151")
#             self.render_new_enrollment_form()
#         else:
#             self.new_tab_btn.configure(fg_color="transparent", text_color="#374151")
#             self.list_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
#             self.render_enrollment_list()

#     def _card(self, parent, height=None):
#         card = ctk.CTkFrame(parent, fg_color="#cbd5e1", corner_radius=0)
#         if height:
#             card.configure(height=height)
#             card.pack_propagate(False)

#         accent = ctk.CTkFrame(card, width=8, fg_color="#15165e", corner_radius=0)
#         accent.pack(side="left", fill="y")

#         inner = ctk.CTkFrame(card, fg_color="transparent")
#         inner.pack(fill="both", expand=True, padx=15, pady=12)
#         return card, inner

#     def render_new_enrollment_form(self):
#         for w in self.workspace_canvas.winfo_children():
#             w.destroy()

#         self.current_student_id = None

#         # Search Student
#         ctk.CTkLabel(self.workspace_canvas, text="Search Student",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 5))

#         search_card, search_inner = self._card(self.workspace_canvas, height=55)
#         search_card.pack(fill="x", pady=(0, 10))

#         self.search_entry = ctk.CTkEntry(search_inner, placeholder_text="Student ID or Name",
#                                          height=35, corner_radius=0, fg_color="#ffffff",
#                                          text_color="black", border_width=0)
#         self.search_entry.pack(side="left", fill="x", expand=True, padx=10)

#         ctk.CTkButton(search_inner, text="SEARCH", width=120, fg_color="#122aff",
#                       corner_radius=0, command=self.search_student).pack(side="right", padx=10)

#         self.student_info = ctk.CTkLabel(self.workspace_canvas, text="No student selected yet..",
#                                          font=ctk.CTkFont(size=14), text_color="#555555")
#         self.student_info.pack(pady=(0, 10))

#         # === TWO COLUMN LAYOUT: Left = Enrollment Details, Right = Subjects ===
#         two_col = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
#         two_col.pack(fill="both", expand=True, pady=(5, 10))
#         two_col.columnconfigure(0, weight=1)
#         two_col.columnconfigure(1, weight=1)

#         # --- LEFT: Enrollment Details ---
#         left_frame = ctk.CTkFrame(two_col, fg_color="transparent")
#         left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

#         ctk.CTkLabel(left_frame, text="Enrollment Details",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 5))

#         det_card, det_inner = self._card(left_frame)
#         det_card.pack(fill="both", expand=True)

#         det_inner.columnconfigure(1, weight=1)

#         self.term_combo = self._combo(det_inner, ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Semester", "2nd Semester"])
#         self.sy_combo = self._combo(det_inner, ["2025-2026", "2026-2027"])
#         self.grade_combo = self._combo(det_inner, [f"Grade {i}" for i in range(1, 13)])
#         self.section_combo = self._combo(det_inner, ["A", "B", "C", "D", "STEM-A", "ABM-A", "HUMSS-A"])

#         self.term_combo.set("1st Quarter")
#         self.sy_combo.set("2025-2026")
#         self.grade_combo.set("Grade 7")
#         self.section_combo.set("A")

#         fields = ["Term", "School Year", "Grade Level", "Section"]
#         widgets = [self.term_combo, self.sy_combo, self.grade_combo, self.section_combo]

#         for i, (label, widget) in enumerate(zip(fields, widgets)):
#             ctk.CTkLabel(det_inner, text=label, text_color="#444444",
#                          font=ctk.CTkFont(size=13)).grid(row=i, column=0, sticky="w", pady=8)
#             widget.grid(row=i, column=1, sticky="ew", padx=(20, 0), pady=8)

#         ctk.CTkButton(det_inner, text="OK", fg_color="#24894c", text_color="#ffffff",
#                       height=40, corner_radius=0,
#                       font=ctk.CTkFont(weight="bold"), command=self.confirm_details).grid(
#                       row=4, column=0, columnspan=2, pady=(20, 5), sticky="ew")

#         # --- RIGHT: Dynamic area (summary + subjects) ---
#         self.right_frame = ctk.CTkFrame(two_col, fg_color="transparent")
#         self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

#         # placeholder label until OK is pressed
#         self.right_placeholder = ctk.CTkLabel(self.right_frame,
#                                                text="Press OK to confirm\nenrollment details first.",
#                                                font=ctk.CTkFont(size=13),
#                                                text_color="#888888")
#         self.right_placeholder.pack(expand=True)

#     def _combo(self, parent, values):
#         return ctk.CTkComboBox(parent, values=values, height=35, corner_radius=0,
#                                fg_color="#ffffff", text_color="black",
#                                button_color="#000000", button_hover_color="#222222",
#                                dropdown_fg_color="#000000", dropdown_text_color="#ffffff")

#     def confirm_details(self):
#         for widget in self.right_frame.winfo_children():
#             widget.destroy()

#         summary = f"Grade {self.grade_combo.get()} - Section {self.section_combo.get()} | {self.term_combo.get()} | SY {self.sy_combo.get()}"

#         ctk.CTkLabel(self.right_frame, text="Confirmed Details",
#                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 5))

#         sum_card, sum_inner = self._card(self.right_frame)
#         sum_card.pack(fill="x")

#         ctk.CTkLabel(sum_inner, text=summary,
#                      font=ctk.CTkFont(size=13, weight="bold"),
#                      text_color="#15165e").pack(anchor="w", pady=(0, 8))

#         btn_row = ctk.CTkFrame(sum_inner, fg_color="transparent")
#         btn_row.pack(anchor="w")

#         ctk.CTkButton(btn_row, text="EDIT", fg_color="#cfcfcf", text_color="#000000",
#                       hover_color="#b0b0b0", corner_radius=0, width=100,
#                       command=lambda: messagebox.showinfo("Edit", "Coming soon")).pack(side="left", padx=(0, 8))

#         ctk.CTkButton(btn_row, text="LOAD SUBJECTS", fg_color="#122aff", text_color="#ffffff",
#                       corner_radius=0, command=self.load_subjects).pack(side="left")

#         # subjects area below inside right_frame
#         self.subjects_area = ctk.CTkFrame(self.right_frame, fg_color="transparent")
#         self.subjects_area.pack(fill="both", expand=True, pady=(12, 0))

#     def load_subjects(self):
#         for widget in self.subjects_area.winfo_children():
#             widget.destroy()

#         grade = self.grade_combo.get()

#         ctk.CTkLabel(self.subjects_area, text="Select Subjects",
#                      font=ctk.CTkFont(size=15, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(0, 5))

#         sub_card, sub_inner = self._card(self.subjects_area)
#         sub_card.pack(fill="both", expand=True)

#         conn = database.get_connection()
#         cursor = conn.cursor()
#         cursor.execute("SELECT subjectID, subjectName FROM SUBJECT WHERE gradeLevel=? ORDER BY subjectName", (grade,))
#         subjects = cursor.fetchall()
#         conn.close()

#         self.subject_vars = {}

#         # 2-column grid, no scrollbar
#         grid_frame = ctk.CTkFrame(sub_inner, fg_color="transparent")
#         grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
#         grid_frame.columnconfigure(0, weight=1)
#         grid_frame.columnconfigure(1, weight=1)

#         for idx, s in enumerate(subjects):
#             var = ctk.BooleanVar()
#             self.subject_vars[s['subjectID']] = var
#             row = idx // 2
#             col = idx % 2
#             ctk.CTkCheckBox(grid_frame, text=s['subjectName'], variable=var,
#                             font=ctk.CTkFont(size=12)).grid(
#                             row=row, column=col, sticky="w", pady=4, padx=10)

#         ctk.CTkButton(sub_inner, text="✔  Confirm Subjects", fg_color="#24894c",
#                       text_color="#ffffff", corner_radius=0, height=38,
#                       font=ctk.CTkFont(weight="bold"),
#                       command=self.confirm_subjects).pack(fill="x", pady=(10, 0))

#     def confirm_subjects(self):
#         self.selected_subjects = [k for k, v in self.subject_vars.items() if v.get()]
#         if not self.selected_subjects:
#             messagebox.showwarning("Warning", "Select at least one subject")
#             return

#         messagebox.showinfo("Ready", f"{len(self.selected_subjects)} subjects selected.")

#         ctk.CTkButton(self.workspace_canvas, text="SAVE ENROLLMENT",
#                       height=50, fg_color="#122aff", corner_radius=0,
#                       font=ctk.CTkFont(size=16, weight="bold"),
#                       command=self.create_enrollment).pack(pady=15)

#     # ==================== Other Functions ====================
#     def search_student(self):
#         keyword = self.search_entry.get().strip()
#         if not keyword:
#             messagebox.showwarning("Required", "Please enter Student ID or Name")
#             return
#         messagebox.showinfo("Search", "Student search logic - add your code here")

#     def create_enrollment(self):
#         messagebox.showinfo("Success", "Enrollment saved successfully!")

#     def render_enrollment_list(self):
#         for w in self.workspace_canvas.winfo_children():
#             w.destroy()

#         ctk.CTkLabel(self.workspace_canvas, text="Enrollment List",
#                      font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
#                      text_color="#000000").pack(anchor="w", pady=(10, 15))

#         search_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", height=60, corner_radius=0)
#         search_frame.pack(fill="x", pady=(0, 15))
#         search_frame.pack_propagate(False)

#         accent = ctk.CTkFrame(search_frame, width=8, fg_color="#15165e", corner_radius=0)
#         accent.pack(side="left", fill="y")

#         inner = ctk.CTkFrame(search_frame, fg_color="transparent")
#         inner.pack(fill="both", expand=True, padx=15, pady=12)

#         search_row = ctk.CTkFrame(inner, fg_color="transparent")
#         search_row.pack(fill="x")

#         self.class_search_entry = ctk.CTkEntry(search_row, placeholder_text="Grade 7 - A",
#                                                height=40, corner_radius=0, fg_color="#ffffff")
#         self.class_search_entry.pack(side="left", fill="x", expand=True)

#         ctk.CTkButton(search_row, text="SEARCH", width=130, height=40,
#                       fg_color="#122aff", corner_radius=0,
#                       command=self.search_enrollment_by_class).pack(side="right", padx=(10, 0))

#         ctk.CTkButton(inner, text="Show All Enrollments", width=180, height=35,
#                       fg_color="#374151", corner_radius=0,
#                       command=self.load_all_enrollments).pack(anchor="w", pady=(5, 0))

#         table_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", corner_radius=0)
#         table_card.pack(fill="both", expand=True, padx=5)

#         accent_table = ctk.CTkFrame(table_card, width=8, fg_color="#15165e", corner_radius=0)
#         accent_table.pack(side="left", fill="y")

#         self.tree_frame = ctk.CTkFrame(table_card, fg_color="#ffffff", corner_radius=0)
#         self.tree_frame.pack(fill="both", expand=True, padx=(0, 4), pady=4)

#         import tkinter.ttk as ttk
#         columns = ("School ID", "Student Name", "Grade & Section", "Term", "School Year", "Staff", "Status")
#         self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)

#         col_widths = [130, 220, 140, 110, 100, 150, 90]
#         for col, width in zip(columns, col_widths):
#             self.tree.heading(col, text=col)
#             self.tree.column(col, width=width, anchor="center")

#         scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
#         self.tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side="right", fill="y")
#         self.tree.pack(fill="both", expand=True)

#         self.load_all_enrollments()

#     def load_all_enrollments(self):
#         for item in self.tree.get_children():
#             self.tree.delete(item)

#         try:
#             conn = database.get_connection()
#             cursor = conn.cursor()
#             cursor.execute("""
#                 SELECT e.schoolID, e.gradeLevel, e.section, e.term, e.schoolYear, e.enrStatus,
#                        s.studFname, s.studLname, s.studMname,
#                        st.staffFname, st.staffLname
#                 FROM ENROLLMENT e
#                 JOIN STUDENT s ON e.studentID = s.studentID
#                 LEFT JOIN STAFF st ON e.staffID = st.staffID
#                 ORDER BY e.enrollmentID DESC
#             """)
#             rows = cursor.fetchall()
#             conn.close()

#             for row in rows:
#                 full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
#                 grade_section = f"{row['gradeLevel']} - {row['section']}"
#                 staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"

#                 self.tree.insert("", "end", values=(
#                     row['schoolID'] or "—", full_name, grade_section,
#                     row['term'], row['schoolYear'], staff_name, row['enrStatus']
#                 ))
#         except Exception as e:
#             print("Error loading enrollments:", e)

#     def search_enrollment_by_class(self):
#         keyword = self.class_search_entry.get().strip().upper()
#         if not keyword:
#             self.load_all_enrollments()
#             return

#         for item in self.tree.get_children():
#             self.tree.delete(item)

#         try:
#             conn = database.get_connection()
#             cursor = conn.cursor()
#             cursor.execute("""
#                 SELECT e.schoolID, e.gradeLevel, e.section, e.term, e.schoolYear, e.enrStatus,
#                        s.studFname, s.studLname, s.studMname,
#                        st.staffFname, st.staffLname
#                 FROM ENROLLMENT e
#                 JOIN STUDENT s ON e.studentID = s.studentID
#                 LEFT JOIN STAFF st ON e.staffID = st.staffID
#                 WHERE (e.gradeLevel || ' - ' || e.section) LIKE ?
#                 ORDER BY e.enrollmentID DESC
#             """, (f"%{keyword}%",))
#             rows = cursor.fetchall()
#             conn.close()

#             if not rows:
#                 messagebox.showinfo("No Results", f"No enrollments found for '{keyword}'")
#                 return

#             for row in rows:
#                 full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
#                 grade_section = f"{row['gradeLevel']} - {row['section']}"
#                 staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"

#                 self.tree.insert("", "end", values=(
#                     row['schoolID'] or "—", full_name, grade_section,
#                     row['term'], row['schoolYear'], staff_name, row['enrStatus']
#                 ))
#         except Exception as e:
#             messagebox.showerror("Error", str(e))

#     def back_to_dashboard(self):
#         self.destroy()
#         if hasattr(self.master, "welcome_lbl"):
#             self.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
#         elif hasattr(self.master.master, "welcome_lbl"):
#             self.master.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))


























import customtkinter as ctk
from tkinter import messagebox
import database
from database_v2 import generate_school_id

class ManageEnrollment(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        
        self.current_student_id = None
        self.subject_vars = {}
        self.selected_subjects = []

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.create_ui()

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
        ctk.CTkLabel(self.workspace_canvas, text="Search Student",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        search_card, search_inner = self._card(self.workspace_canvas, height=55)
        search_card.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(search_inner, placeholder_text="Student ID or Name",
                                         height=35, corner_radius=8, fg_color="#f8fafc",
                                         text_color="black", border_width=1, border_color="#cbd5e1")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)

        ctk.CTkButton(search_inner, text="SEARCH", width=120, height=35, fg_color="#122aff",
                      hover_color="#0b1eb3", font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      corner_radius=8, command=self.search_student).pack(side="right", padx=10)

        self.student_info = ctk.CTkLabel(self.workspace_canvas, text="No student selected yet..",
                                         font=ctk.CTkFont(size=14), text_color="#555555")
        self.student_info.pack(pady=(0, 10))

        # === TWO COLUMN LAYOUT ===
        two_col = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        two_col.pack(fill="both", expand=True, pady=(5, 0))
        two_col.columnconfigure(0, weight=1, uniform="col")
        two_col.columnconfigure(1, weight=1, uniform="col")
        two_col.grid_rowconfigure(0, minsize=240)

        # --- LEFT: Enrollment Details ---
        left_frame = ctk.CTkFrame(two_col, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        ctk.CTkLabel(left_frame, text="Enrollment Details",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        det_card, det_inner = self._card(left_frame, height=240)
        det_card.pack(fill="x")

        det_inner.columnconfigure(1, weight=1)

        self.term_combo = self._combo(det_inner, ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Semester", "2nd Semester"])
        self.term_combo.configure(command=self.on_term_changed)
        self.sy_combo = self._combo(det_inner, ["2018-2019", "2019-2020", "2020-2021", "2021-2022", "2022-2023", "2023-2024", "2024-2025", "2025-2026", "2026-2027", "2027-2028", "2028-2029", "2029-2030"])
        self.sy_combo.configure(command=self.on_sy_changed)
        self.grade_combo = self._combo(det_inner, [f"Grade {i}" for i in range(1, 13)])
        self.grade_combo.configure(command=self.on_grade_changed)
        self.section_combo = self._combo(det_inner, ["A", "B", "C", "D", "STEM-A", "ABM-A", "HUMSS-A"])
        self.section_combo.configure(command=self.on_section_changed)

        self.sy_combo.set("")
        self.grade_combo.set("")
        self.term_combo.set("")
        self.section_combo.set("")
        
        # Initial call to apply correct term state and initial styling
        self.on_grade_changed("")
        self.update_combo_style(self.sy_combo)

        fields = ["School Year", "Grade Level", "Term", "Section"]
        widgets = [self.sy_combo, self.grade_combo, self.term_combo, self.section_combo]

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

        ctk.CTkLabel(self.right_frame, text="Confirmation Details",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        self.confirm_card, self.confirm_inner = self._card(self.right_frame, height=240)
        self.confirm_card.pack(fill="x")

        placeholder_lbl = ctk.CTkLabel(self.confirm_inner,
                                       text="Please select a student and complete the\nEnrollment Details on the left, then click OK.",
                                       font=ctk.CTkFont(family="Inter", size=13),
                                       text_color="#777777")
        placeholder_lbl.pack(expand=True)

    def ok_details(self):
        # 1. Validate that a student is selected
        if not getattr(self, 'current_student_id', None):
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        # 2. Validate basic enrollment details
        school_year = self.sy_combo.get()
        grade = self.grade_combo.get()
        section = self.section_combo.get()
        term = self.term_combo.get()

        if not school_year or not grade or not section:
            messagebox.showwarning("Warning", "Please complete all fields (School Year, Grade Level, and Section) first!")
            return

        # 3. Validate Term for SHS
        if grade in ["Grade 11", "Grade 12"] and not term:
            messagebox.showwarning("Warning", "Please select a Term (Semester) first!")
            return

        # 4. Show the beautiful Confirmation Details layout!
        self.show_confirmation_details()

    def show_confirmation_details(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.right_frame, text="Confirmation Details",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        self.confirm_card, self.confirm_inner = self._card(self.right_frame, height=240)
        self.confirm_card.pack(fill="x")

        grade = self.grade_combo.get()
        term = self.term_combo.get()
        sy = self.sy_combo.get()
        sect = self.section_combo.get()
        name = getattr(self, "current_student_name", "N/A")

        details_frame = ctk.CTkFrame(self.confirm_inner, fg_color="transparent")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        details_frame.columnconfigure(0, weight=0, minsize=120)
        details_frame.columnconfigure(1, weight=1)

        # Base fields matching the format required
        fields = [
            ("NAME:", name),
            ("SCHOOL YEAR:", sy),
            ("GRADE LEVEL:", grade),
        ]
        
        # Conditional Term field
        if grade in ["Grade 11", "Grade 12"]:
            fields.append(("TERM:", term))
            
        # Section field
        fields.append(("SECTION:", sect))

        for idx, (lbl_txt, val_txt) in enumerate(fields):
            lbl = ctk.CTkLabel(details_frame, text=lbl_txt,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="#15165e")
            lbl.grid(row=idx, column=0, sticky="w", pady=4)
            
            val = ctk.CTkLabel(details_frame, text=val_txt,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="#000000")
            val.grid(row=idx, column=1, sticky="w", pady=4)

        # CONFIRM button below the card
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

        ctk.CTkLabel(header_frame, text="Select Subjects",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(side="left")

        # Select All Checkbox
        self.select_all_var = ctk.BooleanVar(value=True)
        self.select_all_cb = ctk.CTkCheckBox(header_frame, text="Select All",
                                              variable=self.select_all_var,
                                              font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
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
        return ctk.CTkComboBox(parent, values=values, height=35, corner_radius=0,
                               fg_color="#ffffff", text_color="#777777",
                               button_color="#000000", button_hover_color="#222222",
                               dropdown_fg_color="#ffffff", dropdown_text_color="black",
                               dropdown_hover_color="#cbd5e1",
                               border_width=0,
                               state="readonly")

    def load_subjects(self):
        for widget in self.sub_inner.winfo_children():
            widget.destroy()

        grade = self.grade_combo.get()
        section = self.section_combo.get()

        if not grade or not section:
            messagebox.showwarning("Warning", "Please select both a Grade Level and Section first.")
            self.sub_placeholder = ctk.CTkLabel(self.sub_inner,
                                                 text="Press OK to load subjects.",
                                                 font=ctk.CTkFont(size=13),
                                                 text_color="#888888")
            self.sub_placeholder.pack(expand=True)
            return

        conn = database.get_connection()
        cursor = conn.cursor()

        is_shs = (grade in ["Grade 11", "Grade 12"])
        
        self.subject_vars = {}

        if is_shs:
            term = self.term_combo.get()
            if not term:
                messagebox.showwarning("Warning", "Please select a Term (Semester) for Senior High School first.")
                return

            sem_num = 1 if "1st" in term else 2
            
            # Determine strand from section
            strand = None
            for s in ["STEM", "ABM", "HUMSS"]:
                if s in section:
                    strand = s
                    break
            
            if not strand:
                # If no strand matches section name, default to section choice parsing
                if "STEM" in section:
                    strand = "STEM"
                elif "ABM" in section:
                    strand = "ABM"
                elif "HUMSS" in section:
                    strand = "HUMSS"
                else:
                    strand = "STEM" # default fallback
            
            cursor.execute("""
                SELECT subjectID, subjectName, description, subjectType 
                FROM SUBJECT 
                WHERE gradeLevel = ? AND strand = ? AND semester = ? AND isActive = 1
                ORDER BY subjectType DESC, subjectName
            """, (grade, strand, sem_num))
            
            subjects = cursor.fetchall()
            conn.close()

            if not subjects:
                ctk.CTkLabel(self.sub_inner, text="No subjects found for this strand & semester selection.",
                             font=ctk.CTkFont(size=13), text_color="#888888").pack(expand=True)
                return

            # Display SHS grouped by Major and Minor
            grid_frame = ctk.CTkFrame(self.sub_inner, fg_color="transparent")
            grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            majors = [s for s in subjects if s['subjectType'] == "Major"]
            minors = [s for s in subjects if s['subjectType'] == "Minor"]

            if majors:
                ctk.CTkLabel(grid_frame, text=f"🔑 Major / Specialized Subjects ({strand} - {grade})",
                             font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                             text_color="#15165e").pack(anchor="w", pady=(5, 2), padx=5)
                
                major_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
                major_frame.pack(fill="x", expand=True, pady=(0, 10))
                major_frame.columnconfigure(0, weight=1)
                major_frame.columnconfigure(1, weight=1)
                
                for idx, s in enumerate(majors):
                    var = ctk.BooleanVar(value=True)
                    self.subject_vars[s['subjectID']] = var
                    row = idx // 2
                    col = idx % 2
                    chk = ctk.CTkCheckBox(major_frame, text=s['subjectName'], variable=var,
                                          font=ctk.CTkFont(family="Inter", size=12),
                                          fg_color="#122aff", hover_color="#0b1eb3",
                                          command=self.update_select_all_state)
                    chk.grid(row=row, column=col, sticky="w", pady=4, padx=10)

            if minors:
                ctk.CTkLabel(grid_frame, text="📘 Core / Minor Subjects",
                             font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                             text_color="#15165e").pack(anchor="w", pady=(5, 2), padx=5)
                
                minor_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
                minor_frame.pack(fill="x", expand=True)
                minor_frame.columnconfigure(0, weight=1)
                minor_frame.columnconfigure(1, weight=1)
                
                for idx, s in enumerate(minors):
                    var = ctk.BooleanVar(value=True)
                    self.subject_vars[s['subjectID']] = var
                    row = idx // 2
                    col = idx % 2
                    chk = ctk.CTkCheckBox(minor_frame, text=s['subjectName'], variable=var,
                                          font=ctk.CTkFont(family="Inter", size=12),
                                          fg_color="#122aff", hover_color="#0b1eb3",
                                          command=self.update_select_all_state)
                    chk.grid(row=row, column=col, sticky="w", pady=4, padx=10)
        else:
            cursor.execute("""
                SELECT subjectID, subjectName, description 
                FROM SUBJECT 
                WHERE gradeLevel = ? AND isActive = 1
                ORDER BY subjectName
            """, (grade,))
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

        # Ensure Select All state is synced
        if hasattr(self, 'select_all_var'):
            self.select_all_var.set(True)

    # ==================== Other Functions ====================
    def search_student(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Required", "Please enter Student ID or Name")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            
            try:
                kid = int(keyword)
            except ValueError:
                kid = -1
                
            cursor.execute("""
                SELECT studentID, studFname, studMname, studLname 
                FROM STUDENT 
                WHERE studentID = ? 
                   OR studFname LIKE ? 
                   OR studLname LIKE ?
            """, (kid, f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                messagebox.showerror("Not Found", f"No student found matching '{keyword}'")
                self.current_student_id = None
                self.student_info.configure(text="No student selected yet..", text_color="#555555")
                return

            if len(rows) == 1:
                row = rows[0]
                self.current_student_id = row['studentID']
                full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
                self.current_student_name = full_name
                self.student_info.configure(text=f"Selected Student: [ID: {row['studentID']}] {full_name}", text_color="#24894c")
                messagebox.showinfo("Student Selected", f"Found and selected student:\n[ID: {row['studentID']}] {full_name}")
            else:
                self.show_student_choice_popup(rows)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to search student: {str(e)}")

    def show_student_choice_popup(self, students):
        popup = ctk.CTkToplevel(self)
        popup.title("Select Student")
        popup.geometry("450x350")
        popup.resizable(False, False)
        popup.transient(self)
        popup.grab_set()

        # Center popup
        popup.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 225
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 175
        popup.geometry(f"+{x}+{y}")

        ctk.CTkLabel(popup, text="Multiple matches found. Please choose:",
                     font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                     text_color="#15165e").pack(pady=(15, 10))

        frame = ctk.CTkScrollableFrame(popup, width=400, height=220, fg_color="#f8fafc", corner_radius=0)
        frame.pack(padx=15, pady=5, fill="both", expand=True)

        def select_choice(sid, name):
            self.current_student_id = sid
            self.current_student_name = name
            self.student_info.configure(text=f"Selected Student: [ID: {sid}] {name}", text_color="#24894c")
            popup.destroy()

        for s in students:
            full_name = f"{s['studLname']}, {s['studFname']} {s['studMname'] or ''}".strip()
            btn_text = f"[ID: {s['studentID']}] {full_name}"
            
            btn = ctk.CTkButton(frame, text=btn_text, anchor="w",
                                height=38, corner_radius=8,
                                fg_color="#ffffff", text_color="#15165e",
                                hover_color="#cbd5e1",
                                font=ctk.CTkFont(family="Inter", size=12),
                                command=lambda sid=s['studentID'], name=full_name: select_choice(sid, name))
            btn.pack(fill="x", pady=2, padx=2)

        ctk.CTkButton(popup, text="Cancel", width=100, fg_color="#374151", hover_color="#272f3a", corner_radius=8,
                      command=popup.destroy).pack(pady=(10, 15))

    def create_enrollment(self):
        if not getattr(self, 'current_student_id', None):
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        school_year = self.sy_combo.get()
        grade = self.grade_combo.get()
        section = self.section_combo.get()
        term = self.term_combo.get()

        if not school_year or not grade or not section:
            messagebox.showwarning("Warning", "Please complete all fields (School Year, Grade Level, and Section) first!")
            return

        if grade in ["Grade 11", "Grade 12"] and not term:
            messagebox.showwarning("Warning", "Please select a Term (Semester) first!")
            return

        selected_subjects = [sid for sid, var in self.subject_vars.items() if var.get()]
        if not selected_subjects:
            messagebox.showwarning("Warning", "Select at least one subject before saving.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT staffID FROM STAFF LIMIT 1")
            staff_row = cursor.fetchone()
            staff_id = staff_row['staffID'] if staff_row else 1

            from database_v2 import generate_school_id
            school_year = self.sy_combo.get()
            school_id = generate_school_id(school_year)

            # Determine levelType and term values based on grade level
            if grade in [f"Grade {i}" for i in range(1, 7)]:
                level_type = "Elementary"
                term_val = "Full Year"
            elif grade in [f"Grade {i}" for i in range(7, 11)]:
                level_type = "High School"
                term_val = "Full Year"
            else:
                level_type = "Senior High School"
                term_val = term

            cursor.execute("""
                INSERT INTO ENROLLMENT 
                    (studentID, staffID, schoolID, gradeLevel, section, levelType, term, schoolYear, enrStatus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Active')
            """, (self.current_student_id, staff_id, school_id,
                  grade, section, level_type, term_val, school_year))
            
            enrollment_id = cursor.lastrowid

            # Update student levelType as well
            cursor.execute("""
                UPDATE STUDENT SET levelType = ? WHERE studentID = ?
            """, (level_type, self.current_student_id))

            for subject_id in selected_subjects:
                cursor.execute("""
                    INSERT INTO DETAIL (enrollmentID, subjectID)
                    VALUES (?, ?)
                """, (enrollment_id, subject_id))
            
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Enrollment saved successfully!\nSchool ID: {school_id}")

            # Reset form
            self.search_entry.delete(0, 'end')
            self.student_info.configure(text="No student selected yet..", text_color="#555555")
            self.current_student_id = None
            self.current_student_name = None
            
            # Reset comboboxes to empty
            self.sy_combo.set("")
            self.grade_combo.set("")
            self.term_combo.set("")
            self.section_combo.set("")
            self.on_grade_changed("")
            self.update_combo_style(self.sy_combo)

            # Reset the confirmation details placeholder!
            self.show_confirmation_placeholder()
            self.subject_vars = {}

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create enrollment:\n{e}")

    def render_enrollment_list(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.workspace_canvas, text="Enrollment List",
                     font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(10, 15))

        search_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=60)
        search_frame.pack(fill="x", pady=(0, 15))
        search_frame.pack_propagate(False)

        accent_container = ctk.CTkFrame(search_frame, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)

        search_row = ctk.CTkFrame(inner, fg_color="transparent")
        search_row.pack(fill="x")

        self.class_search_entry = ctk.CTkEntry(search_row, placeholder_text="Grade 7 - A",
                                               height=40, corner_radius=8, fg_color="#f8fafc",
                                               border_width=1, border_color="#cbd5e1", text_color="black")
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

        accent_container_table = ctk.CTkFrame(table_card, width=6, fg_color="transparent")
        accent_container_table.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent_table = ctk.CTkFrame(accent_container_table, width=6, fg_color="#15165e", corner_radius=3)
        accent_table.pack(fill="both", expand=True)

        self.tree_frame = ctk.CTkFrame(table_card, fg_color="transparent", corner_radius=8)
        self.tree_frame.pack(fill="both", expand=True, padx=15, pady=12)

        import tkinter.ttk as ttk
        columns = ("School ID", "Student Name", "Grade & Section", "Term", "School Year", "Staff", "Status")

        # Set modern theme and style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading",
                        background="#15165e",
                        foreground="#ffffff",
                        font=("Inter", 11, "bold"),
                        bordercolor="#15165e",
                        borderwidth=0)
        style.map("Treeview.Heading",
                  background=[('active', '#1c1d7c')],
                  foreground=[('active', '#ffffff')])
        style.configure("Treeview",
                        font=("Inter", 10),
                        rowheight=32,
                        fieldbackground="#ffffff",
                        background="#ffffff",
                        borderwidth=0)

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        
        # Alternating row colors
        self.tree.tag_configure("evenrow", background="#f8fafc")
        self.tree.tag_configure("oddrow", background="#ffffff")

        # Bind key release for instant auto-search suggestion
        self.class_search_entry.bind("<KeyRelease>", lambda e: self.search_enrollment_by_class())

        col_widths = [130, 220, 140, 110, 100, 150, 90]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

        self.load_all_enrollments()

    def load_all_enrollments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.schoolID, e.gradeLevel, e.section, e.term, e.schoolYear, e.enrStatus,
                       s.studFname, s.studLname, s.studMname,
                       st.staffFname, st.staffLname
                FROM ENROLLMENT e
                JOIN STUDENT s ON e.studentID = s.studentID
                LEFT JOIN STAFF st ON e.staffID = st.staffID
                ORDER BY e.enrollmentID DESC
            """)
            rows = cursor.fetchall()
            conn.close()

            for idx, row in enumerate(rows):
                full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
                grade_section = f"{row['gradeLevel']} - {row['section']}"
                staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"
                tag = "evenrow" if idx % 2 == 0 else "oddrow"

                self.tree.insert("", "end", values=(
                    row['schoolID'] or "—", full_name, grade_section,
                    row['term'], row['schoolYear'], staff_name, row['enrStatus']
                ), tags=(tag,))
        except Exception as e:
            print("Error loading enrollments:", e)

    def search_enrollment_by_class(self):
        keyword = self.class_search_entry.get().strip().upper()
        if not keyword:
            self.load_all_enrollments()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT e.schoolID, e.gradeLevel, e.section, e.term, e.schoolYear, e.enrStatus,
                       s.studFname, s.studLname, s.studMname,
                       st.staffFname, st.staffLname
                FROM ENROLLMENT e
                JOIN STUDENT s ON e.studentID = s.studentID
                LEFT JOIN STAFF st ON e.staffID = st.staffID
                WHERE (e.gradeLevel || ' - ' || e.section) LIKE ?
                ORDER BY e.enrollmentID DESC
            """, (f"%{keyword}%",))
            rows = cursor.fetchall()
            conn.close()

            for idx, row in enumerate(rows):
                full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
                grade_section = f"{row['gradeLevel']} - {row['section']}"
                staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"
                tag = "evenrow" if idx % 2 == 0 else "oddrow"

                self.tree.insert("", "end", values=(
                    row['schoolID'] or "—", full_name, grade_section,
                    row['term'], row['schoolYear'], staff_name, row['enrStatus']
                ), tags=(tag,))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_grade_changed(self, choice):
        if not choice:
            self.term_combo.configure(values=[])
            self.term_combo.set("")
            self.term_combo.configure(state="disabled")
            
            self.section_combo.configure(values=[])
            self.section_combo.set("")
            self.section_combo.configure(state="disabled")
        elif choice in [f"Grade {i}" for i in range(1, 11)]:
            self.term_combo.configure(values=[])
            self.term_combo.set("")
            self.term_combo.configure(state="disabled")
            
            self.section_combo.configure(state="readonly")
            self.section_combo.configure(values=["A", "B", "C", "D"])
            self.section_combo.set("") # Keep it blank initially!
        else:
            self.term_combo.configure(state="readonly")
            self.term_combo.configure(values=["1st Semester", "2nd Semester"])
            self.term_combo.set("") # Keep it blank initially!
            
            self.section_combo.configure(state="readonly")
            self.section_combo.configure(values=["STEM-A", "ABM-A", "HUMSS-A"])
            self.section_combo.set("") # Keep it blank initially!
            
        self.update_combo_style(self.grade_combo)
        self.update_combo_style(self.term_combo)
        self.update_combo_style(self.section_combo)

    def on_sy_changed(self, choice):
        self.update_combo_style(self.sy_combo)

    def on_term_changed(self, choice):
        self.update_combo_style(self.term_combo)

    def on_section_changed(self, choice):
        self.update_combo_style(self.section_combo)

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