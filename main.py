# main.py
import customtkinter as ctk
from tkinter import messagebox
import config
import database

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(config.WINDOW_TITLE)
        self.geometry("1280x720")
        self.resizable(False, False)
        
        self.center_window()
        self.create_login_ui()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1280) // 2
        y = (screen_height - 720) // 2
        self.geometry(f"1280x720+{x}+{y}")

    def create_login_ui(self):
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=config.COLORS["bg"])
        main_frame.pack(fill="both", expand=True)

        # Left Branding Panel
        left_frame = ctk.CTkFrame(main_frame, width=550, fg_color=config.COLORS["surface"])
        left_frame.pack(side="left", fill="both", expand=True)
        left_frame.pack_propagate(False)

        ctk.CTkLabel(left_frame, text="ABC", 
                    font=ctk.CTkFont(size=48, weight="bold"),
                    text_color=config.COLORS["primary"]).pack(pady=(120, 5))
        
        ctk.CTkLabel(left_frame, text="Learning Center", 
                    font=ctk.CTkFont(size=28, weight="bold"),
                    text_color=config.COLORS["text"]).pack()
        
        ctk.CTkLabel(left_frame, text="Management System", 
                    font=ctk.CTkFont(size=18),
                    text_color=config.COLORS["text_secondary"]).pack()

        # Right Login Form
        right_frame = ctk.CTkFrame(main_frame, fg_color=config.COLORS["surface"])
        right_frame.pack(side="right", fill="both", expand=True, padx=60, pady=60)

        ctk.CTkLabel(right_frame, text="Sign In", 
                    font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(40, 30))

        self.username_entry = ctk.CTkEntry(right_frame, placeholder_text="Email or Username", 
                                          width=340, height=50, font=ctk.CTkFont(size=14))
        self.username_entry.pack(pady=12)

        self.password_entry = ctk.CTkEntry(right_frame, placeholder_text="Password", 
                                          show="*", width=340, height=50, font=ctk.CTkFont(size=14))
        self.password_entry.pack(pady=12)

        ctk.CTkButton(right_frame, text="LOGIN", width=340, height=50,
                     fg_color=config.COLORS["primary"],
                     hover_color=config.COLORS["primary_hover"],
                     font=ctk.CTkFont(size=16, weight="bold"),
                     command=self.login).pack(pady=30)

        ctk.CTkLabel(right_frame, text="LAN-based Desktop Application", 
                    font=ctk.CTkFont(size=12), 
                    text_color=config.COLORS["text_secondary"]).pack(side="bottom", pady=20)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Required", "Please enter email/username and password")
            return

        conn = database.get_connection()
        cursor = conn.cursor()

        # Check Staff/Admin
        cursor.execute("""
            SELECT staffID, staffFname, staffLname 
            FROM STAFF 
            WHERE email = ? AND password = ?
        """, (username, password))
        staff = cursor.fetchone()

        if staff:
            full_name = f"{staff['staffFname']} {staff['staffLname']}"
            messagebox.showinfo("Success", f"Welcome, {staff['staffFname']}!")
            self.destroy()
            
            from dashboard import Dashboard
            dashboard = Dashboard(user_role="Admin/Staff", user_name=full_name)
            dashboard.mainloop()
            return

        # Check Tutor
        cursor.execute("""
            SELECT tutorID, tutorFname, tutorLname 
            FROM TUTOR 
            WHERE tutorEmail = ? AND password = ?
        """, (username, password))
        tutor = cursor.fetchone()

        if tutor:
            full_name = f"{tutor['tutorFname']} {tutor['tutorLname']}"
            messagebox.showinfo("Success", f"Welcome, {tutor['tutorFname']}!")
            self.destroy()
            
            from dashboard import Dashboard
            dashboard = Dashboard(user_role="Tutor", user_name=full_name)
            dashboard.mainloop()
            return

        conn.close()
        messagebox.showerror("Login Failed", "Invalid email or password")


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()