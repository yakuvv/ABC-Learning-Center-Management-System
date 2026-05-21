# dashboard.py
import customtkinter as ctk
from tkinter import messagebox
import config


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

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=250, fg_color="#15165e", corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        # Logo
        ctk.CTkLabel(sidebar, text="ABC",
                     font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
                     text_color="#122aff").pack(pady=(40, 2))
        ctk.CTkLabel(sidebar, text="ABC Learning Center",
                     font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                     text_color="#122aff").pack(pady=(0, 30))

        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color="#22259c", corner_radius=0).pack(
            fill="x", padx=20, pady=(0, 20))

        # Nav buttons
        nav_items = [
            ("👤  Profile Students",  self.open_profile),
            ("📋  Manage Enrollment", self.open_enrollment),
            ("✅  Record Attendance", self.open_attendance),
            ("💳  Process Payment",   self.open_payment),
            ("📝  Manage Grades",     self.open_grades),
        ]

        self.nav_buttons = []
        for text, command in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=text,
                width=210, height=42,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#cbd5e1",
                fg_color="transparent",
                hover_color="#22259c",
                anchor="w",
                corner_radius=0,
                command=lambda c=command, b_text=text: self._nav_click(c, b_text)
            )
            btn.pack(pady=2, padx=15, fill="x")
            self.nav_buttons.append((btn, text))

        # Logout at bottom
        ctk.CTkFrame(sidebar, height=1, fg_color="#22259c", corner_radius=0).pack(
            side="bottom", fill="x", padx=20, pady=(0, 10))
        ctk.CTkButton(
            sidebar, text="⏻  Log Out",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#94a3b8",
            fg_color="transparent",
            hover_color="#22259c",
            anchor="w",
            height=38,
            corner_radius=0,
            command=self.logout
        ).pack(side="bottom", fill="x", padx=15, pady=(0, 5))

        # ── Main Content ──────────────────────────────────────────────────────
        self.main_content = ctk.CTkFrame(self, fg_color="#e4e4e4", corner_radius=0)
        self.main_content.grid(row=0, column=1, sticky="nsew")

        self._show_welcome()

    # ── Welcome screen ────────────────────────────────────────────────────────

    def _show_welcome(self):
        for w in self.main_content.winfo_children():
            w.destroy()

        # Top bar (same style as modules)
        top_bar = ctk.CTkFrame(self.main_content, height=70,
                               fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text="Dashboard",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=30, pady=15)

        ctk.CTkLabel(top_bar, text="ABC",
                     font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                     text_color="#122aff").pack(side="right", padx=30)

        # Content area
        content = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Welcome label
        role_color = "#122aff" if self.user_role.lower() == "admin/staff" else "#8B5CF6"
        ctk.CTkLabel(content,
                     text=f"Welcome back, {self.user_name}!",
                     font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
                     text_color="#000000",
                     anchor="w").pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(content,
                     text=f"Logged in as  {self.user_role}",
                     font=ctk.CTkFont(family="Inter", size=14),
                     text_color=role_color,
                     anchor="w").pack(fill="x", pady=(0, 30))

        # Summary cards row
        cards_row = ctk.CTkFrame(content, fg_color="transparent")
        cards_row.pack(fill="x", pady=(0, 25))

        summary_items = [
            ("Profile Students",  "Add and view\nstudent profiles",   "👤"),
            ("Manage Enrollment", "Enroll students\ninto subjects",    "📋"),
            ("Record Attendance", "Mark student\nattendance",          "✅"),
            ("Process Payment",   "Record fees\nand receipts",         "💳"),
            ("Manage Grades",     "Enter and view\nstudent grades",    "📝"),
        ]

        for i, (title, desc, icon) in enumerate(summary_items):
            card = ctk.CTkFrame(cards_row, fg_color="#cbd5e1", corner_radius=0)
            card.grid(row=0, column=i, sticky="nsew", padx=(0, 10) if i < 4 else 0)
            cards_row.grid_columnconfigure(i, weight=1)

            # Left accent
            ctk.CTkFrame(card, width=6, fg_color="#15165e", corner_radius=0).pack(
                side="left", fill="y")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=14)

            ctk.CTkLabel(inner, text=icon,
                         font=ctk.CTkFont(size=22),
                         text_color="#122aff").pack(anchor="w")
            ctk.CTkLabel(inner, text=title,
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color="#0f172a").pack(anchor="w", pady=(4, 2))
            ctk.CTkLabel(inner, text=desc,
                         font=ctk.CTkFont(family="Inter", size=11),
                         text_color="#64748b",
                         justify="left").pack(anchor="w")

        # Quick info card
        ctk.CTkLabel(content, text="Quick Info",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 6))

        info_card = ctk.CTkFrame(content, fg_color="#cbd5e1", corner_radius=0)
        info_card.pack(fill="x")
        ctk.CTkFrame(info_card, width=8, fg_color="#15165e", corner_radius=0).pack(
            side="left", fill="y")

        info_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        info_inner.pack(fill="both", expand=True, padx=20, pady=16)
        info_inner.grid_columnconfigure((0, 1, 2), weight=1)

        # Pull counts from DB
        try:
            import database
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as c FROM STUDENT")
            student_count = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM ENROLLMENT WHERE enrStatus='Active'")
            enr_count = cursor.fetchone()['c']
            cursor.execute("SELECT COUNT(*) as c FROM PAYMENT")
            pay_count = cursor.fetchone()['c']
            conn.close()
        except Exception:
            student_count = enr_count = pay_count = 0

        for col, (label, val) in enumerate([
            ("Total Students",      str(student_count)),
            ("Active Enrollments",  str(enr_count)),
            ("Payments Recorded",   str(pay_count)),
        ]):
            ctk.CTkLabel(info_inner, text=val,
                         font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
                         text_color="#122aff").grid(row=0, column=col, sticky="w", padx=20)
            ctk.CTkLabel(info_inner, text=label,
                         font=ctk.CTkFont(family="Inter", size=12),
                         text_color="#555555").grid(row=1, column=col, sticky="w", padx=20, pady=(2, 0))

        # Store welcome_lbl reference for back_to_dashboard compatibility
        self.welcome_lbl = ctk.CTkLabel(content, text="")  # invisible placeholder

    # ── Nav helpers ───────────────────────────────────────────────────────────

    def _nav_click(self, command, active_text):
        for btn, text in self.nav_buttons:
            if text == active_text:
                btn.configure(fg_color="#122aff", text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")
        command()

    def _clear_main(self):
        for w in self.main_content.winfo_children():
            w.destroy()
        # Reset nav highlight
        for btn, _ in self.nav_buttons:
            btn.configure(fg_color="transparent", text_color="#cbd5e1")

    def _open_module(self, ModuleClass):
        self._clear_main()
        # Re-create welcome_lbl so back_to_dashboard in modules can pack it back
        self.welcome_lbl = ctk.CTkLabel(self.main_content, text="")
        ModuleClass(self.main_content)

    # ── Module openers ────────────────────────────────────────────────────────

    def open_profile(self):
        from modules.profile_students import ProfileStudents
        self._open_module(ProfileStudents)

    def open_enrollment(self):
        from modules.manage_enrollment import ManageEnrollment
        self._open_module(ManageEnrollment)

    def open_attendance(self):
        if self.user_role.lower() == "tutor":
            from modules.record_attendance import RecordAttendance
            self._open_module(RecordAttendance)
        else:
            messagebox.showwarning("Access Denied",
                "Only Tutors can record attendance.\nPlease login as a Tutor.")

    def open_payment(self):
        from modules.process_payment import ProcessPayment
        self._open_module(ProcessPayment)

    def open_grades(self):
        from modules.manage_grades import ManageGrades
        self._open_module(ManageGrades)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()


if __name__ == "__main__":
    app = Dashboard(user_role="Admin/Staff", user_name="Maria Santos")
    app.mainloop()