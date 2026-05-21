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
                      corner_radius=0, command=self.back_to_dashboard
                      ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(top_bar, text="Manage Enrollment",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        ctk.CTkLabel(top_bar, text="ABC",
                     font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                     text_color="#122aff").pack(side="right", padx=30)

        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(20, 10))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1",
                                width=310, height=46, corner_radius=0)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.new_tab_btn = ctk.CTkButton(tab_pill, text="New Enrollment",
                                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                         fg_color="#122aff", text_color="#ffffff",
                                         corner_radius=0, height=38, width=150,
                                         command=lambda: self.switch_tab("new"))
        self.new_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.list_tab_btn = ctk.CTkButton(tab_pill, text="Enrollment List",
                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                          fg_color="transparent", text_color="#374151",
                                          corner_radius=0, height=38, width=150,
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

    def _card(self, parent, height=None):
        card = ctk.CTkFrame(parent, fg_color="#cbd5e1", corner_radius=0)
        if height:
            card.configure(height=height)
            card.pack_propagate(False)

        accent = ctk.CTkFrame(card, width=8, fg_color="#15165e", corner_radius=0)
        accent.pack(side="left", fill="y")

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
                                         height=35, corner_radius=0, fg_color="#ffffff",
                                         text_color="black", border_width=0)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10)

        ctk.CTkButton(search_inner, text="SEARCH", width=120, fg_color="#122aff",
                      corner_radius=0, command=self.search_student).pack(side="right", padx=10)

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
        det_card.pack(fill="both", expand=True)

        det_inner.columnconfigure(1, weight=1)

        self.term_combo = self._combo(det_inner, ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter", "1st Semester", "2nd Semester"])
        self.sy_combo = self._combo(det_inner, ["2025-2026", "2026-2027"])
        self.grade_combo = self._combo(det_inner, [f"Grade {i}" for i in range(1, 13)])
        self.section_combo = self._combo(det_inner, ["A", "B", "C", "D", "STEM-A", "ABM-A", "HUMSS-A"])

        self.term_combo.set("1st Quarter")
        self.sy_combo.set("2025-2026")
        self.grade_combo.set("Grade 7")
        self.section_combo.set("A")

        fields = ["Term", "School Year", "Grade Level", "Section"]
        widgets = [self.term_combo, self.sy_combo, self.grade_combo, self.section_combo]

        for i, (label, widget) in enumerate(zip(fields, widgets)):
            ctk.CTkLabel(det_inner, text=label, text_color="#444444",
                         font=ctk.CTkFont(size=13)).grid(row=i, column=0, sticky="w", pady=8)
            widget.grid(row=i, column=1, sticky="ew", padx=(20, 0), pady=8)

        # OK button OUTSIDE the card, below the left column
        ctk.CTkButton(left_frame, text="OK", fg_color="#24894c", text_color="#ffffff",
                      height=40, corner_radius=0,
                      font=ctk.CTkFont(weight="bold"),
                      command=self.ok_details).pack(anchor="w", pady=(10, 0))

        # --- RIGHT: Select Subjects ---
        right_frame = ctk.CTkFrame(two_col, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        ctk.CTkLabel(right_frame, text="Select Subjects",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 5))

        self.sub_card, self.sub_inner = self._card(right_frame, height=240)
        self.sub_card.pack(fill="both", expand=True)

        # placeholder text inside subjects card
        self.sub_placeholder = ctk.CTkLabel(self.sub_inner,
                                             text="Press OK to load subjects.",
                                             font=ctk.CTkFont(size=13),
                                             text_color="#888888")
        self.sub_placeholder.pack(expand=True)

        # LOAD SUBJECTS + SAVE STUDENT PROFILE outside the card, bottom-right aligned
        btn_right_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        btn_right_frame.pack(anchor="e", pady=(10, 0))

        ctk.CTkButton(btn_right_frame, text="LOAD SUBJECTS", fg_color="#122aff",
                      text_color="#ffffff", corner_radius=0, height=40, width=200,
                      font=ctk.CTkFont(weight="bold"),
                      command=self.load_subjects).pack(pady=(0, 6))

        ctk.CTkButton(btn_right_frame, text="SAVE STUDENT PROFILE", fg_color="#24894c",
                      text_color="#ffffff", corner_radius=0, height=40, width=200,
                      font=ctk.CTkFont(weight="bold"),
                      command=self.create_enrollment).pack()

    def ok_details(self):
        # Just a visual confirmation, triggers subject load
        self.load_subjects()

    def _combo(self, parent, values):
        return ctk.CTkComboBox(parent, values=values, height=35, corner_radius=0,
                               fg_color="#ffffff", text_color="black",
                               button_color="#000000", button_hover_color="#222222",
                               dropdown_fg_color="#000000", dropdown_text_color="#ffffff")

    def load_subjects(self):
        for widget in self.sub_inner.winfo_children():
            widget.destroy()

        grade = self.grade_combo.get()

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT subjectID, subjectName FROM SUBJECT WHERE gradeLevel=? ORDER BY subjectName", (grade,))
        subjects = cursor.fetchall()
        conn.close()

        self.subject_vars = {}

        grid_frame = ctk.CTkFrame(self.sub_inner, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        for idx, s in enumerate(subjects):
            var = ctk.BooleanVar()
            self.subject_vars[s['subjectID']] = var
            row = idx // 2
            col = idx % 2
            ctk.CTkCheckBox(grid_frame, text=s['subjectName'], variable=var,
                            font=ctk.CTkFont(size=12)).grid(
                            row=row, column=col, sticky="w", pady=4, padx=10)

    # ==================== Other Functions ====================
    def search_student(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Required", "Please enter Student ID or Name")
            return
        messagebox.showinfo("Search", "Student search logic - add your code here")

    def create_enrollment(self):
        selected = [k for k, v in self.subject_vars.items() if v.get()]
        if not selected:
            messagebox.showwarning("Warning", "Select at least one subject before saving.")
            return
        messagebox.showinfo("Success", "Enrollment saved successfully!")

    def render_enrollment_list(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.workspace_canvas, text="Enrollment List",
                     font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(10, 15))

        search_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", height=60, corner_radius=0)
        search_frame.pack(fill="x", pady=(0, 15))
        search_frame.pack_propagate(False)

        accent = ctk.CTkFrame(search_frame, width=8, fg_color="#15165e", corner_radius=0)
        accent.pack(side="left", fill="y")

        inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)

        search_row = ctk.CTkFrame(inner, fg_color="transparent")
        search_row.pack(fill="x")

        self.class_search_entry = ctk.CTkEntry(search_row, placeholder_text="Grade 7 - A",
                                               height=40, corner_radius=0, fg_color="#ffffff")
        self.class_search_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(search_row, text="SEARCH", width=130, height=40,
                      fg_color="#122aff", corner_radius=0,
                      command=self.search_enrollment_by_class).pack(side="right", padx=(10, 0))

        ctk.CTkButton(inner, text="Show All Enrollments", width=180, height=35,
                      fg_color="#374151", corner_radius=0,
                      command=self.load_all_enrollments).pack(anchor="w", pady=(5, 0))

        table_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", corner_radius=0)
        table_card.pack(fill="both", expand=True, padx=5)

        accent_table = ctk.CTkFrame(table_card, width=8, fg_color="#15165e", corner_radius=0)
        accent_table.pack(side="left", fill="y")

        self.tree_frame = ctk.CTkFrame(table_card, fg_color="#ffffff", corner_radius=0)
        self.tree_frame.pack(fill="both", expand=True, padx=(0, 4), pady=4)

        import tkinter.ttk as ttk
        columns = ("School ID", "Student Name", "Grade & Section", "Term", "School Year", "Staff", "Status")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)

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

            for row in rows:
                full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
                grade_section = f"{row['gradeLevel']} - {row['section']}"
                staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"

                self.tree.insert("", "end", values=(
                    row['schoolID'] or "—", full_name, grade_section,
                    row['term'], row['schoolYear'], staff_name, row['enrStatus']
                ))
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

            if not rows:
                messagebox.showinfo("No Results", f"No enrollments found for '{keyword}'")
                return

            for row in rows:
                full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
                grade_section = f"{row['gradeLevel']} - {row['section']}"
                staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"

                self.tree.insert("", "end", values=(
                    row['schoolID'] or "—", full_name, grade_section,
                    row['term'], row['schoolYear'], staff_name, row['enrStatus']
                ))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def back_to_dashboard(self):
        self.destroy()
        if hasattr(self.master, "welcome_lbl"):
            self.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(self.master.master, "welcome_lbl"):
            self.master.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))