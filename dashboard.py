# dashboard.py
import customtkinter as ctk
import config

class Dashboard(ctk.CTk):
    def __init__(self, user_role="Admin", user_name="User"):
        super().__init__()
        
        self.title(f"{config.WINDOW_TITLE} - Dashboard")
        self.geometry("1280x720")
        self.resizable(True, True)
        
        self.user_role = user_role
        self.user_name = user_name
        
        self.create_dashboard_ui()

    def create_dashboard_ui(self):
        # Sidebar
        sidebar = ctk.CTkFrame(self, width=250, fg_color=config.COLORS["surface"])
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="ABC Learning Center", 
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=config.COLORS["primary"]).pack(pady=20)

        ctk.CTkLabel(sidebar, text=f"Welcome, {self.user_name}", 
                    font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        # Menu Buttons
        buttons = [
            ("Profile Students", self.open_profile),
            ("Manage Enrollment", self.open_enrollment),
            ("Record Attendance", self.open_attendance),
            ("Process Payment", self.open_payment),
            ("Manage Grades", self.open_grades),
            ("Logout", self.logout)
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(sidebar, text=text, width=220, height=40, 
                               fg_color="transparent", anchor="w", 
                               command=command)
            btn.pack(pady=5, padx=15)

        # Main Content Area
        self.main_content = ctk.CTkFrame(self, fg_color=config.COLORS["bg"])
        self.main_content.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(self.main_content, text=f"Welcome to Dashboard\n{self.user_role} Mode", 
                    font=ctk.CTkFont(size=24, weight="bold")).pack(pady=100)

    def open_profile(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()
        
        from modules.profile_students import ProfileStudents
        ProfileStudents(self.main_content)

    def open_enrollment(self):
        messagebox.showinfo("Module", "Manage Enrollment Module - Coming Soon")

    def open_attendance(self):
        messagebox.showinfo("Module", "Record Attendance Module - Coming Soon")

    def open_payment(self):
        messagebox.showinfo("Module", "Process Payment Module - Coming Soon")

    def open_grades(self):
        messagebox.showinfo("Module", "Manage Grades Module - Coming Soon")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()

if __name__ == "__main__":
    app = Dashboard(user_role="Admin", user_name="Vince Oñate")
    app.mainloop()