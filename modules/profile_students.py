
import customtkinter as ctk
from tkinter import messagebox, ttk
import database
from datetime import datetime

class ProfileStudents(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        self.create_ui()

    def create_ui(self):
        # Title
        title = ctk.CTkLabel(self, text="Profile Students", 
                            font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        self.tabview.add("Add New Student")
        self.tabview.add("Student List")

        self.create_add_tab(self.tabview.tab("Add New Student"))
        self.create_list_tab(self.tabview.tab("Student List"))

    def create_add_tab(self, tab):
        # Student Info
        ctk.CTkLabel(tab, text="Student Information", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20,10))

        frame = ctk.CTkFrame(tab)
        frame.pack(fill="x", padx=20, pady=10)

        # Left column
        left = ctk.CTkFrame(frame, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=10)

        self.fname = ctk.CTkEntry(left, placeholder_text="First Name")
        self.fname.pack(fill="x", pady=5)
        self.lname = ctk.CTkEntry(left, placeholder_text="Last Name")
        self.lname.pack(fill="x", pady=5)
        self.mname = ctk.CTkEntry(left, placeholder_text="Middle Name")
        self.mname.pack(fill="x", pady=5)

        # Right column
        right = ctk.CTkFrame(frame, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=10)

        self.gender = ctk.CTkComboBox(right, values=["M", "F"])
        self.gender.pack(fill="x", pady=5)
        self.dob = ctk.CTkEntry(right, placeholder_text="Date of Birth (YYYY-MM-DD)")
        self.dob.pack(fill="x", pady=5)
        self.contact = ctk.CTkEntry(right, placeholder_text="Contact Number")
        self.contact.pack(fill="x", pady=5)

        # Address & Email
        ctk.CTkLabel(tab, text="Address & Email").pack(anchor="w", padx=20, pady=(15,5))
        self.address = ctk.CTkEntry(tab, placeholder_text="Full Address")
        self.address.pack(fill="x", padx=20, pady=5)
        self.email = ctk.CTkEntry(tab, placeholder_text="Email Address")
        self.email.pack(fill="x", padx=20, pady=5)

        # Parent Info
        ctk.CTkLabel(tab, text="Parent/Guardian Information", 
        font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20,10))

        self.par_name = ctk.CTkEntry(tab, placeholder_text="Parent Full Name")
        self.par_name.pack(fill="x", padx=20, pady=5)
        self.par_contact = ctk.CTkEntry(tab, placeholder_text="Parent Contact Number")
        self.par_contact.pack(fill="x", padx=20, pady=5)
        self.relationship = ctk.CTkEntry(tab, placeholder_text="Relationship (Mother, Father, etc.)")
        self.relationship.pack(fill="x", padx=20, pady=5)

        # Save Button
        ctk.CTkButton(tab, text="Save Student Profile", height=45, 
        fg_color="#2563EB", command=self.save_student).pack(pady=30)

    def save_student(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            # Insert Student
            cursor.execute('''
                INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.lname.get(), self.fname.get(), self.mname.get(),
                  self.gender.get(), self.dob.get(), self.address.get(),
                  self.contact.get(), self.email.get()))

            student_id = cursor.lastrowid

            # Insert Parent
            cursor.execute('''
                INSERT INTO PARENT (studentID, parName, parContactNo, parEmail, relationship)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, self.par_name.get(), self.par_contact.get(), 
                  "", self.relationship.get()))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Student profile saved successfully!")
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save student: {str(e)}")

    def clear_fields(self):
        for entry in [self.fname, self.lname, self.mname, self.dob, self.address, 
                     self.contact, self.email, self.par_name, self.par_contact, self.relationship]:
            entry.delete(0, 'end')

    def create_list_tab(self, tab):

        label = ctk.CTkLabel(tab, text="Student List (Coming Soon - Enhanced Version)", 
                            font=ctk.CTkFont(size=20))
        label.pack(pady=100)