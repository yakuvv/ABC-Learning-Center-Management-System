# modules/manage_grades.py
import customtkinter as ctk
from tkinter import messagebox, ttk
import database
from datetime import datetime

class ManageGrades(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.create_ui()

    def create_ui(self):
        # Top Bar
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        back_btn = ctk.CTkButton(top_bar, text="← back to Dashboard",
                                 font=ctk.CTkFont(family="Inter", size=14),
                                 fg_color="transparent", text_color="#ffffff",
                                 hover_color="#22259c", width=150, height=40,
                                 corner_radius=0, command=self.back_to_dashboard)
        back_btn.pack(side="left", padx=20, pady=15)

        title = ctk.CTkLabel(top_bar, text="Manage Grades",
                             font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                             text_color="#ffffff")
        title.pack(side="left", expand=True)

        # Main Content
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Select Subject / Class
        ctk.CTkLabel(main_frame, text="Select Subject / Class",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold")).pack(anchor="w", pady=(0,8))

        select_frame = ctk.CTkFrame(main_frame, fg_color="#cbd5e1", height=55, corner_radius=0)
        select_frame.pack(fill="x", pady=5)
        select_frame.pack_propagate(False)

        self.subject_combo = ctk.CTkComboBox(select_frame,
                                             values=["Mathematics 7 - Grade 7", "Science 7 - Grade 7",
                                                     "English 11 - STEM", "General Chemistry 1 - STEM"],
                                             height=40, font=ctk.CTkFont(family="Inter", size=14))
        self.subject_combo.pack(side="left", fill="x", expand=True, padx=15, pady=8)

        ctk.CTkButton(select_frame, text="Load Students", width=160, height=40,
                      fg_color="#122aff", command=self.load_students).pack(side="right", padx=15)

        # Grades Table
        self.tree = ttk.Treeview(main_frame, columns=("id", "name", "grade"), show="headings", height=16)
        self.tree.heading("id", text="Student ID")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("grade", text="Grade (1.00 - 5.00)")
        self.tree.column("id", width=100, anchor="center")
        self.tree.column("name", width=320)
        self.tree.column("grade", width=150, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=15)

        # Bottom Controls
        bottom = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom.pack(fill="x", pady=10)

        ctk.CTkButton(bottom, text="Save All Grades", height=50, width=200,
                      fg_color="#122aff", font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                      command=self.save_grades).pack(side="right")

        self.load_students()  # Initial load

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Sample data (will connect to real data later)
        samples = [
            (1001, "Carias, Angelyn F."),
            (1002, "Dela Cruz, Juan S."),
            (1003, "Santos, Maria L.")
        ]

        for sid, name in samples:
            self.tree.insert("", "end", values=(sid, name, "3.00"), tags=("row",))

    def save_grades(self):
        messagebox.showinfo("Success", "All grades have been saved successfully!")
        # TODO: Later - Save to GRADE table with real data

    def back_to_dashboard(self):
        parent_frame = self.master
        self.destroy()
        if hasattr(parent_frame, "welcome_lbl"):
            parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(parent_frame.master, "welcome_lbl"):
            parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))