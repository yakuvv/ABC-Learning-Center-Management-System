# dashboard.py
import customtkinter as ctk
from tkinter import messagebox
import tkinter.ttk as ttk
import config
from datetime import datetime


class Dashboard(ctk.CTkFrame):
    def __init__(self, parent=None, user_role="Admin", user_name="User"):
        if parent is None:
            self.temp_root = ctk.CTk()
            parent = self.temp_root
            is_standalone = True
        else:
            is_standalone = False

        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)

        root = parent.winfo_toplevel()
        root.overrideredirect(False)
        root.resizable(True, True)
        root.minsize(1280, 720)
        root.title(f"{config.WINDOW_TITLE} - Dashboard")
        root.configure(fg_color="#e4e4e4")

        if is_standalone:
            root.geometry("1280x720")
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            x = (screen_width - 1280) // 2
            y = (screen_height - 720) // 2
            root.geometry(f"1280x720+{x}+{y}")

        self.user_role = user_role
        self.user_name = user_name
        self.create_dashboard_ui()

    def mainloop(self, *args, **kwargs):
        if hasattr(self, "temp_root"):
            self.temp_root.mainloop(*args, **kwargs)
        else:
            super().mainloop(*args, **kwargs)

    # ── Shared widget factory (matches modules) ────────────────────────────────
    def _card(self, parent, accent_color="#15165e", height=None):
        """White card with left accent strip. Returns (card, inner)."""
        kw = {"height": height} if height else {}
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=16,
                            border_width=1, border_color="#cbd5e1", **kw)
        acc_wrap = ctk.CTkFrame(card, width=6, fg_color="transparent")
        acc_wrap.pack(side="left", fill="y", padx=(12, 0), pady=12)
        ctk.CTkFrame(acc_wrap, width=6, fg_color=accent_color,
                     corner_radius=3).pack(fill="both", expand=True)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)
        return card, inner

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def create_dashboard_ui(self):
        sidebar = ctk.CTkFrame(self, width=215, fg_color="#15165e", corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Logo area
        from PIL import Image
        import os
        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(56, 56))
            ctk.CTkLabel(sidebar, image=ctk_logo, text="").pack(pady=(22, 4))
        else:
            ctk.CTkLabel(sidebar, text="ABC",
                         font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
                         text_color="#122aff").pack(pady=(28, 2))

        ctk.CTkLabel(sidebar, text="ABC Learning Center",
                     font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                     text_color="#a5b4fc").pack(pady=(0, 4))

        # Divider
        ctk.CTkFrame(sidebar, height=1, fg_color="#22259c", corner_radius=0).pack(
            fill="x", padx=18, pady=(0, 14))

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
                width=188, height=40,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#cbd5e1",
                fg_color="transparent",
                hover_color="#22259c",
                anchor="w",
                corner_radius=10,
                command=lambda c=command, b_text=text: self._nav_click(c, b_text)
            )
            btn.pack(pady=1, padx=12, fill="x")
            self.nav_buttons.append((btn, text))

        # Bottom section
        ctk.CTkFrame(sidebar, height=1, fg_color="#22259c", corner_radius=0).pack(
            side="bottom", fill="x", padx=18, pady=(0, 0))

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
        ).pack(side="bottom", fill="x", padx=12, pady=(0, 4))

        # User chip
        role_col = "#a5b4fc" if self.user_role.lower() == "admin/staff" else "#86efac"
        user_chip = ctk.CTkFrame(sidebar, fg_color="#1e1f6e", corner_radius=10)
        user_chip.pack(side="bottom", fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(user_chip, text=self.user_name,
                     font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="#ffffff").pack(anchor="w", padx=12, pady=(8, 0))
        ctk.CTkLabel(user_chip, text=self.user_role,
                     font=ctk.CTkFont(family="Inter", size=11),
                     text_color=role_col).pack(anchor="w", padx=12, pady=(0, 8))

        # ── Main Content ──────────────────────────────────────────────────────
        self.main_content = ctk.CTkFrame(self, fg_color="#e4e4e4", corner_radius=0)
        self.main_content.pack(side="right", fill="both", expand=True)

        self._show_welcome()

    # ── Welcome screen ────────────────────────────────────────────────────────
    def _show_welcome(self):
        for w in self.main_content.winfo_children():
            w.destroy()

        # ── Top Bar ───────────────────────────────────────────────────────────
        top_bar = ctk.CTkFrame(self.main_content, height=64,
                               fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text="Dashboard",
                     font=ctk.CTkFont(family="Inter", size=28, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=26, pady=12)

        # Live clock
        self._clock_lbl = ctk.CTkLabel(top_bar, text="",
                                        font=ctk.CTkFont(family="Inter", size=12),
                                        text_color="#a5b4fc")
        self._clock_lbl.pack(side="right", padx=22)
        self._tick_clock()

        # Logo in top bar
        from PIL import Image
        import os
        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(42, 42))
            ctk.CTkLabel(top_bar, image=ctk_logo, text="").pack(side="right", padx=(0, 8))

        # ── Scrollable area ───────────────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(self.main_content,
                                        fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=28, pady=16)

        # ── Welcome / greeting card ───────────────────────────────────────────
        now = datetime.now()
        greeting = ("Good morning" if now.hour < 12
                    else ("Good afternoon" if now.hour < 17 else "Good evening"))

        greet_card = ctk.CTkFrame(scroll, fg_color="#ffffff", corner_radius=14,
                                   border_width=1, border_color="#cbd5e1",
                                   height=48)
        greet_card.pack(fill="x", pady=(0, 10))
        greet_card.pack_propagate(False)

        acc_wrap = ctk.CTkFrame(greet_card, width=5, fg_color="transparent")
        acc_wrap.pack(side="left", fill="y", padx=(10, 0), pady=6)
        ctk.CTkFrame(acc_wrap, width=5, fg_color="#122aff",
                     corner_radius=3).pack(fill="both", expand=True)

        greet_inner = ctk.CTkFrame(greet_card, fg_color="transparent")
        greet_inner.pack(fill="both", expand=True, padx=12, pady=0)

        row = ctk.CTkFrame(greet_inner, fg_color="transparent")
        row.pack(fill="both", expand=True)
        ctk.CTkLabel(row,
                     text=f"{greeting}, {self.user_name}! 👋",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#0f172a", anchor="w").pack(side="left", pady=0)
        ctk.CTkLabel(row,
                     text=f"Logged in as  {self.user_role}",
                     font=ctk.CTkFont(family="Inter", size=11),
                     text_color="#64748b", anchor="e").pack(side="right")

        # ── Pull DB counts ────────────────────────────────────────────────────
        try:
            import database
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS c FROM STUDENT")
            student_count = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM ENROLLMENT WHERE enrStatus='Active'")
            enr_count = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM PAYMENT")
            pay_count = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) AS c FROM ATTENDANCE WHERE attDate=date('now')")
            att_today = cursor.fetchone()["c"]
            conn.close()
        except Exception:
            student_count = enr_count = pay_count = att_today = 0

        # ── Stats Row ─────────────────────────────────────────────────────────
        self._section_label(scroll, "OVERVIEW")

        stats_row = ctk.CTkFrame(scroll, fg_color="transparent")
        stats_row.pack(fill="x", pady=(0, 14))

        stat_items = [
            ("Total Students",     str(student_count), "👤", "#122aff", "#eef2ff"),
            ("Active Enrollments", str(enr_count),     "📋", "#00bf63", "#f0fdf4"),
            ("Payments Recorded",  str(pay_count),     "💳", "#f59e0b", "#fffbeb"),
            ("Attendance Today",   str(att_today),     "✅", "#8b5cf6", "#f5f3ff"),
        ]

        for i, (label, val, icon, color, bg) in enumerate(stat_items):
            pad_right = (0, 8) if i < 3 else (0, 0)
            card = ctk.CTkFrame(stats_row, fg_color=bg, corner_radius=14,
                                border_width=1, border_color="#e2e8f0")
            card.grid(row=0, column=i, sticky="nsew", padx=pad_right)
            stats_row.grid_columnconfigure(i, weight=1)

            acc_wrap = ctk.CTkFrame(card, width=4, fg_color="transparent")
            acc_wrap.pack(side="left", fill="y", padx=(8, 0), pady=7)
            ctk.CTkFrame(acc_wrap, width=4, fg_color=color,
                         corner_radius=2).pack(fill="both", expand=True)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=10, pady=7)

            # Icon + value on same row
            top_row = ctk.CTkFrame(inner, fg_color="transparent")
            top_row.pack(fill="x")
            ctk.CTkLabel(top_row, text=val,
                         font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
                         text_color=color).pack(side="left")
            ctk.CTkLabel(top_row, text=icon,
                         font=ctk.CTkFont(size=14),
                         text_color=color).pack(side="right")
            ctk.CTkLabel(inner, text=label,
                         font=ctk.CTkFont(family="Inter", size=10),
                         text_color="#64748b").pack(anchor="w", pady=(1, 0))

        # ── Two-column: Modules + Recent Activity ─────────────────────────────
        body_row = ctk.CTkFrame(scroll, fg_color="transparent")
        body_row.pack(fill="both", expand=True, pady=(0, 14))
        body_row.columnconfigure(0, weight=3)
        body_row.columnconfigure(1, weight=5)

        # ── LEFT: Module quick-launch cards ───────────────────────────────────
        left_col = ctk.CTkFrame(body_row, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 14))

        self._section_label(left_col, "MODULES")

        module_items = [
            ("👤", "Profile Students",  "Add / view student profiles",  "#122aff", self.open_profile),
            ("📋", "Manage Enrollment", "Enroll students into subjects", "#00bf63", self.open_enrollment),
            ("✅", "Record Attendance", "Mark student attendance",       "#f59e0b", self.open_attendance),
            ("💳", "Process Payment",   "Record fees and receipts",      "#8b5cf6", self.open_payment),
            ("📝", "Manage Grades",     "Enter and view student grades", "#e20000", self.open_grades),
        ]

        for icon, title, desc, color, cmd in module_items:
            m_card = ctk.CTkFrame(left_col, fg_color="#ffffff", corner_radius=12,
                                  border_width=1, border_color="#cbd5e1",
                                  cursor="hand2", height=46)
            m_card.pack(fill="x", pady=(0, 4))
            m_card.pack_propagate(False)

            acc_wrap = ctk.CTkFrame(m_card, width=4, fg_color="transparent")
            acc_wrap.pack(side="left", fill="y", padx=(8, 0), pady=6)
            ctk.CTkFrame(acc_wrap, width=4, fg_color=color,
                         corner_radius=2).pack(fill="both", expand=True)

            row_inner = ctk.CTkFrame(m_card, fg_color="transparent")
            row_inner.pack(fill="both", expand=True, padx=10, pady=0)

            label_col = ctk.CTkFrame(row_inner, fg_color="transparent")
            label_col.pack(side="left", fill="both", expand=True)

            title_row = ctk.CTkFrame(label_col, fg_color="transparent")
            title_row.pack(fill="both", expand=True)
            ctk.CTkLabel(title_row, text=icon,
                         font=ctk.CTkFont(size=13),
                         text_color=color).pack(side="left", padx=(0, 5))
            ctk.CTkLabel(title_row, text=title,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#0f172a").pack(side="left")
            ctk.CTkLabel(title_row, text=desc,
                         font=ctk.CTkFont(family="Inter", size=10),
                         text_color="#94a3b8").pack(side="left", padx=(8, 0))

            ctk.CTkButton(row_inner, text="Open →",
                          font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                          width=62, height=24, corner_radius=6,
                          fg_color=color, hover_color="#0b1eb3",
                          text_color="#ffffff",
                          command=cmd).pack(side="right", padx=(8, 0))

        # ── RIGHT: Recent Attendance ──────────────────────────────────────────
        right_col = ctk.CTkFrame(body_row, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew")

        self._section_label(right_col, "RECENT ATTENDANCE  (Today)")

        att_card, att_inner = self._card(right_col, accent_color="#15165e")
        att_card.pack(fill="both", expand=True)

        # Style the Treeview to match modules
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dash.Treeview.Heading",
                        background="#15165e", foreground="#ffffff",
                        font=("Inter", 11, "bold"),
                        borderwidth=0, relief="flat", padding=(6, 5))
        style.map("Dash.Treeview.Heading",
                  background=[("active", "#1e1f80")],
                  foreground=[("active", "#ffffff")])
        style.configure("Dash.Treeview",
                        font=("Inter", 11), rowheight=34,
                        fieldbackground="#ffffff", background="#ffffff",
                        borderwidth=0, relief="flat",
                        selectbackground="#e0e7ff", selectforeground="#15165e")
        style.map("Dash.Treeview",
                  background=[("selected", "#e0e7ff")],
                  foreground=[("selected", "#15165e")])

        # Query attendance
        try:
            import database
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT s.studLname || ', ' || s.studFname AS name,
                       e.gradeLevel, e.section,
                       a.attStatus
                FROM ATTENDANCE a
                JOIN DETAIL d     ON a.detailID    = d.detailID
                JOIN ENROLLMENT e ON d.enrollmentID = e.enrollmentID
                JOIN STUDENT s    ON e.studentID    = s.studentID
                WHERE a.attDate = date('now')
                GROUP BY e.schoolID, a.attStatus
                ORDER BY
                    CAST(REPLACE(e.gradeLevel, 'Grade ', '') AS INTEGER),
                    e.section,
                    s.studLname, s.studFname
                LIMIT 25
            """)
            att_rows = cur.fetchall()
            conn.close()
        except Exception:
            att_rows = []

        cols = ("#", "Student Name", "Grade Level", "Section", "Status")
        tree = ttk.Treeview(att_inner, columns=cols, show="headings",
                            height=11, style="Dash.Treeview")

        col_cfg = {
            "#":           (34,  "center", False),
            "Student Name":(230, "w",      True),
            "Grade Level": (110, "w",      False),
            "Section":     (80,  "w",      False),
            "Status":      (90,  "center", False),
        }
        for col, (w, anch, stretch) in col_cfg.items():
            tree.heading(col, text=col, anchor=anch)
            tree.column(col, width=w, anchor=anch, stretch=stretch, minwidth=w)

        # Tag colours
        for status, fg_color, bg_even in [
            ("present", "#059669", "#f0fdf4"),
            ("absent",  "#dc2626", "#fff5f5"),
            ("late",    "#2563eb", "#eff6ff"),
        ]:
            tree.tag_configure(f"{status}_even", foreground=fg_color, background=bg_even)
            tree.tag_configure(f"{status}_odd",  foreground=fg_color, background="#ffffff")

        if att_rows:
            for idx, r in enumerate(att_rows):
                parity = "even" if idx % 2 == 0 else "odd"
                tag = f"{r['attStatus'].lower()}_{parity}"
                tree.insert("", "end",
                            values=(idx + 1, r["name"],
                                    r["gradeLevel"], r["section"],
                                    r["attStatus"]),
                            tags=(tag,))
        else:
            tree.insert("", "end",
                        values=("", "No attendance recorded today yet.", "", "", ""))

        sb = ttk.Scrollbar(att_inner, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)

        # invisible placeholder for back-nav compatibility
        self.welcome_lbl = ctk.CTkLabel(scroll, text="")

    # ── Helper: section label ─────────────────────────────────────────────────
    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text,
                     font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                     text_color="#475569").pack(anchor="w", pady=(0, 6))

    # ── Clock ─────────────────────────────────────────────────────────────────
    def _tick_clock(self):
        if hasattr(self, "_clock_lbl") and self._clock_lbl.winfo_exists():
            self._clock_lbl.configure(
                text=datetime.now().strftime("%A, %B %d, %Y   %I:%M:%S %p"))
            self._clock_lbl.after(1000, self._tick_clock)

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
        for btn, _ in self.nav_buttons:
            btn.configure(fg_color="transparent", text_color="#cbd5e1")

    def _open_module(self, ModuleClass):
        self._clear_main()
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
        from modules.record_attendance import RecordAttendance
        self._open_module(RecordAttendance)

    def open_payment(self):
        from modules.process_payment import ProcessPayment
        self._open_module(ProcessPayment)

    def open_grades(self):
        from modules.manage_grades import ManageGrades
        self._open_module(ManageGrades)

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            root = self.winfo_toplevel()
            if hasattr(self, "temp_root"):
                self.temp_root.destroy()
            else:
                self.destroy()
                root.geometry("1280x720")
                root.resizable(False, False)
                root.title(config.WINDOW_TITLE)
                root.configure(fg_color="#e5e5e5")
                if hasattr(root, "center_window"):
                    root.center_window()
                if hasattr(root, "create_login_ui"):
                    root.create_login_ui()


if __name__ == "__main__":
    app = Dashboard(user_role="Admin/Staff", user_name="Maria Santos")
    app.mainloop()