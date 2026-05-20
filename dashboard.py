# dashboard.py
import customtkinter as ctk
from tkinter import messagebox
import config

ctk.set_appearance_mode("light")

class Dashboard(ctk.CTk):
    def __init__(self, user_role="Admin", user_name="User"):
        super().__init__()
        self.overrideredirect(False)
        self.resizable(True, True)
        self.minsize(1280, 720)
        self.title(f"{config.WINDOW_TITLE} - Dashboard")
        self.geometry("1280x720")
        self.configure(fg_color="#e4e4e4")
        self.user_role = user_role
        self.user_name = user_name
        self.center_window()
        self.create_dashboard_ui()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 720) // 2
        self.geometry(f"1280x720+{x}+{y}")

    def create_dashboard_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self, width=250, fg_color="#15165e", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo & Title
        ctk.CTkLabel(sidebar, text="ABC",
                     font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
                     text_color="#122aff").pack(pady=(40, 5))
        ctk.CTkLabel(sidebar, text="ABC Learning Center",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#122aff").pack(pady=(0, 40))

        # Menu Buttons
        buttons = [
            ("Profile Students", self.open_profile),
            ("Manage Enrollment", self.open_enrollment),
            ("Record Attendance", self.open_attendance),
            ("Process Payment", self.open_payment),
            ("Manage Grades", self.open_grades)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(sidebar, text=text, width=210, height=40,
                                font=ctk.CTkFont(family="Inter", size=14),
                                text_color="#ffffff",
                                fg_color="transparent",
                                hover_color="#122aff",
                                anchor="w",
                                corner_radius=0,
                                command=command)
            btn.pack(pady=5, padx=20, fill="x")

        # Logout
        logout_btn = ctk.CTkButton(sidebar, text="Log Out",
                                   font=ctk.CTkFont(family="Inter", size=14),
                                   text_color="#ffffff",
                                   fg_color="transparent",
                                   hover_color="#122aff",
                                   anchor="w",
                                   height=35,
                                   corner_radius=0,
                                   command=self.logout)
        logout_btn.pack(side="bottom", fill="x", padx=20, pady=30)

        # Main Content
        self.main_content = ctk.CTkFrame(self, fg_color="#e4e4e4", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")

        self.welcome_lbl = ctk.CTkLabel(self.main_content,
                                        text=f"Welcome, {self.user_name}!",
                                        font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
                                        text_color="#000000",
                                        anchor="w")
        self.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))

    # ==================== MODULE OPENERS ====================
    def open_profile(self):
        for widget in self.main_content.winfo_children():
            if widget != self.welcome_lbl:
                widget.destroy()
        from modules.profile_students import ProfileStudents
        ProfileStudents(self.main_content)

    def open_enrollment(self):
        for widget in self.main_content.winfo_children():
            if widget != self.welcome_lbl:
                widget.destroy()
        from modules.manage_enrollment import ManageEnrollment
        ManageEnrollment(self.main_content)

    def open_attendance(self):
        for widget in self.main_content.winfo_children():
            if widget != self.welcome_lbl:
                widget.destroy()
        if self.user_role.lower() == "tutor":
            from modules.record_attendance import RecordAttendance
            RecordAttendance(self.main_content)
        else:
            messagebox.showwarning("Access Denied",
                "Only Tutors can record attendance.\nPlease login as Tutor.")

    def open_payment(self):
        for widget in self.main_content.winfo_children():
            if widget != self.welcome_lbl:
                widget.destroy()
        from modules.process_payment import ProcessPayment
        ProcessPayment(self.main_content)

    def open_grades(self):
        for widget in self.main_content.winfo_children():
            if widget != self.welcome_lbl:
                widget.destroy()
        from modules.manage_grades import ManageGrades
        ManageGrades(self.main_content)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()


if __name__ == "__main__":
    app = Dashboard(user_role="Admin", user_name="Maria Santos")
    app.mainloop()