
import customtkinter as ctk
from tkinter import messagebox, ttk
import database
from datetime import datetime


class ManageEnrollment(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        self.current_student_id = None
        self.create_ui()

    def create_ui(self):
        title = ctk.CTkLabel(self, text="Manage Enrollment",
                             font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tabview.add("New Enrollment")
        self.tabview.add("Enrollment List")

        self.create_new_enrollment_tab(self.tabview.tab("New Enrollment"))
        self.create_enrollment_list_tab(self.tabview.tab("Enrollment List"))

    def create_new_enrollment_tab(self, tab):
        # Search Student
        ctk.CTkLabel(tab, text="Search Student", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20,
                                                                                                pady=(20, 5))

        search_frame = ctk.CTkFrame(tab)
        search_frame.pack(fill="x", padx=20, pady=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Student ID or Name")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ctk.CTkButton(search_frame, text="Search", width=120, command=self.search_student).pack(side="right")

        self.student_info = ctk.CTkLabel(tab, text="No student selected yet...", text_color="gray")
        self.student_info.pack(pady=15)

        # Enrollment Details
        ctk.CTkLabel(tab, text="Enrollment Details", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20,
                                                                                                    pady=(10, 5))

        detail_frame = ctk.CTkFrame(tab)
        detail_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(detail_frame, text="Term:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.term_combo = ctk.CTkComboBox(detail_frame, values=["1st Term", "2nd Term", "Summer Term"])
        self.term_combo.grid(row=0, column=1, padx=10, pady=8, sticky="ew")

        ctk.CTkLabel(detail_frame, text="School Year:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.sy_entry = ctk.CTkEntry(detail_frame, placeholder_text="2025-2026")
        self.sy_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        # Subject Selection
        ctk.CTkLabel(tab, text="Select Subjects", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20,
                                                                                                 pady=(20, 5))

        self.subject_frame = ctk.CTkScrollableFrame(tab, height=180)
        self.subject_frame.pack(fill="x", padx=20, pady=5)

        self.load_subjects()

        ctk.CTkButton(tab, text="Create Enrollment", height=45,
                      fg_color="#2563EB", command=self.create_enrollment).pack(pady=25)

    def load_subjects(self):
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT subjectID, subjectName, gradeLevel FROM SUBJECT")
        subjects = cursor.fetchall()
        conn.close()

        self.subject_vars = {}
        for subject in subjects:
            var = ctk.BooleanVar()
            self.subject_vars[subject['subjectID']] = var
            chk = ctk.CTkCheckBox(self.subject_frame, text=f"{subject['subjectName']} ({subject['gradeLevel']})",
                                  variable=var)
            chk.pack(anchor="w", pady=2, padx=10)

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
                       WHERE CAST(studentID AS TEXT) = ?
                          OR studFname LIKE ?
                          OR studLname LIKE ?
                       """, (keyword, f"%{keyword}%", f"%{keyword}%"))

        student = cursor.fetchone()
        conn.close()

        if student:
            self.current_student_id = student['studentID']
            full_name = f"{student['studFname']} {student['studLname']}"
            self.student_info.configure(text=f"✓ Selected: {full_name} (ID: {student['studentID']})",
                                        text_color="lightgreen")
        else:
            self.student_info.configure(text="❌ Student not found!", text_color="red")
            self.current_student_id = None

    def create_enrollment(self):
        if not self.current_student_id:
            messagebox.showwarning("Warning", "Please search and select a student first")
            return

        term = self.term_combo.get()
        school_year = self.sy_entry.get().strip()

        if not term or not school_year:
            messagebox.showwarning("Warning", "Please fill Term and School Year")
            return

        selected_subjects = [sid for sid, var in self.subject_vars.items() if var.get()]
        if not selected_subjects:
            messagebox.showwarning("Warning", "Please select at least one subject")
            return

        conn = database.get_connection()
        cursor = conn.cursor()

        try:
            # Create Enrollment
            cursor.execute("""
                           INSERT INTO ENROLLMENT (studentID, staffID, term, schoolYear, enrStatus)
                           VALUES (?, ?, ?, ?, 'Active')
                           """, (self.current_student_id, 1, term, school_year))

            enrollment_id = cursor.lastrowid

            # Create Detail records for selected subjects
            for subject_id in selected_subjects:
                cursor.execute("""
                               INSERT INTO DETAIL (enrollmentID, subjectID)
                               VALUES (?, ?)
                               """, (enrollment_id, subject_id))

            conn.commit()
            messagebox.showinfo("Success", f"Enrollment created successfully with {len(selected_subjects)} subject(s)!")

            # Clear form
            self.search_entry.delete(0, 'end')
            self.sy_entry.delete(0, 'end')
            self.student_info.configure(text="No student selected yet...", text_color="gray")
            self.current_student_id = None

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create enrollment: {str(e)}")
        finally:
            conn.close()

    def create_enrollment_list_tab(self, tab):
        ctk.CTkLabel(tab, text="Current Enrollments", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        # Will be enhanced with Treeview in next update
        label = ctk.CTkLabel(tab, text="Enrollment List will be shown here (Coming in next improvement)",
                             font=ctk.CTkFont(size=16))
        label.pack(pady=100)