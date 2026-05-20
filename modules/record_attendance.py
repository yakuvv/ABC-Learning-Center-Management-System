import customtkinter as ctk
from tkinter import messagebox, Toplevel, ttk
import database
import calendar
from datetime import datetime


class RecordAttendance(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.current_cal_year  = datetime.now().year
        self.current_cal_month = datetime.now().month
        self.create_ui()

    def _entry(self, parent, placeholder, **kwargs):
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=35, corner_radius=0,
            fg_color="#ffffff", text_color="black",
            border_width=0,
            **kwargs
        )

    def _combo(self, parent, values, **kwargs):
        return ctk.CTkComboBox(
            parent,
            values=values,
            height=35, corner_radius=0,
            fg_color="#ffffff", text_color="black",
            button_color="#000000", button_hover_color="#222222",
            dropdown_fg_color="#000000", dropdown_text_color="#ffffff",
            dropdown_hover_color="#222222",
            border_width=0,
            **kwargs
        )

    def _card_frame(self, parent, height=None):
        kw = {"height": height} if height else {}
        card = ctk.CTkFrame(parent, fg_color="#cbd5e1", corner_radius=0, **kw)
        ctk.CTkFrame(card, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=8)
        return card, inner

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

        ctk.CTkLabel(top_bar, text="Record Attendance",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        ctk.CTkLabel(top_bar, text="ABC",
                     font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                     text_color="#122aff").pack(side="right", padx=30)

        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=40, pady=20)

        split_body = ctk.CTkFrame(workspace, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # ── LEFT PANEL ───────────────────────────────────────────────────────
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=480)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)

        def section_label(parent, text):
            ctk.CTkLabel(parent, text=text,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="black").pack(anchor="w", pady=(8, 2))

        section_label(left_panel, "CLASS")
        class_card, class_inner = self._card_frame(left_panel, height=50)
        class_card.pack(fill="x")
        class_card.pack_propagate(False)
        self.class_combo = self._combo(class_inner, ["Grade 1 - A", "Grade 2 - B", "Grade 7 - A"])
        self.class_combo.set("Grade 7 - A")
        self.class_combo.pack(fill="x")

        section_label(left_panel, "TERM")
        term_card, term_inner = self._card_frame(left_panel, height=50)
        term_card.pack(fill="x")
        term_card.pack_propagate(False)
        self.term_combo = self._combo(term_inner,
            ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"])
        self.term_combo.set("1st Quarter")
        self.term_combo.pack(fill="x")

        section_label(left_panel, "SCHOOL YEAR")
        sy_card, sy_inner = self._card_frame(left_panel, height=50)
        sy_card.pack(fill="x")
        sy_card.pack_propagate(False)
        self.sy_combo = self._combo(sy_inner,
            ["2018-2019", "2019-2020", "2024-2025", "2025-2026"])
        self.sy_combo.set("2025-2026")
        self.sy_combo.pack(fill="x")

        section_label(left_panel, "SUBJECT")
        sub_card, sub_inner = self._card_frame(left_panel, height=50)
        sub_card.pack(fill="x")
        sub_card.pack_propagate(False)
        self.subject_combo = self._combo(sub_inner,
            ["Mathematics", "Science", "English"])
        self.subject_combo.set("Mathematics")
        self.subject_combo.pack(fill="x")

        section_label(left_panel, "DATE TODAY")
        date_card, date_inner = self._card_frame(left_panel, height=50)
        date_card.pack(fill="x")
        date_card.pack_propagate(False)
        self.date_entry = self._entry(date_inner, "YYYY-MM-DD")
        self.date_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(date_inner, text="▼", width=35, height=35,
                      corner_radius=0, fg_color="#000000",
                      hover_color="#222222", text_color="#ffffff",
                      command=self.popup_calendar
                      ).pack(side="right")

        ctk.CTkButton(left_panel, text="LOAD STUDENTS",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      height=40, corner_radius=0,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.load_students
                      ).pack(fill="x", pady=(18, 0))

        # ── RIGHT PANEL ───────────────────────────────────────────────────────
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        ctk.CTkLabel(right_panel, text="STUDENTS",
                     font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                     text_color="black").pack(anchor="w", pady=(0, 4))

        sheet_outer = ctk.CTkFrame(right_panel, fg_color="#cbd5e1", corner_radius=0)
        sheet_outer.pack(fill="both", expand=True)
        ctk.CTkFrame(sheet_outer, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")

        self.roster_scroll = ctk.CTkScrollableFrame(
            sheet_outer, fg_color="transparent", corner_radius=0)
        self.roster_scroll.pack(fill="both", expand=True, padx=6, pady=6)

        # Column headers
        hdr = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(hdr, text="", width=30).grid(row=0, column=0, padx=2)
        for col_idx, (letter, color) in enumerate(
                [("P", "#00bf63"), ("A", "#e20000"), ("L", "#122aff")], start=1):
            ctk.CTkLabel(hdr, text=letter,
                         font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                         text_color=color, width=35).grid(row=0, column=col_idx, padx=4)

        name_hdr = ctk.CTkFrame(hdr, fg_color="#ffffff", height=30, width=240,
                                corner_radius=0, border_width=1, border_color="black")
        name_hdr.grid(row=0, column=4, padx=(15, 0), sticky="ew")
        name_hdr.pack_propagate(False)
        ctk.CTkLabel(name_hdr, text="STUDENT NAME",
                     font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="black").pack(pady=3)

        self.attendance_vars = {}
        self.roster_rows_frame = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        self.roster_rows_frame.pack(fill="x")

        self._samples = [
            "Carias, Angelyn F.", "Dela Cruz, Juan G.",
            "Cruz, Joan H.", "Santos, Maria T."
        ]
        self.render_roster(self._samples)

        ctk.CTkButton(right_panel, text="SAVE ATTENDANCE",
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      height=45, corner_radius=0,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.save_attendance
                      ).pack(fill="x", pady=(12, 0))

    def render_roster(self, student_list):
        for w in self.roster_rows_frame.winfo_children():
            w.destroy()
        self.attendance_vars.clear()
        self.roster_rows_frame.grid_columnconfigure(4, weight=1)

        for idx, name in enumerate(student_list):
            ctk.CTkLabel(self.roster_rows_frame,
                         text=str(idx + 1),
                         font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
                         text_color="black", width=30
                         ).grid(row=idx, column=0, padx=2, pady=5)

            p_var = ctk.BooleanVar(value=False)
            a_var = ctk.BooleanVar(value=False)
            l_var = ctk.BooleanVar(value=False)
            self.attendance_vars[name] = (p_var, a_var, l_var)

            chk_cfg = dict(text="", width=35, height=35, corner_radius=0,
                           border_width=2, border_color="#ffffff",
                           checkmark_color="#ffffff")

            p_chk = ctk.CTkCheckBox(self.roster_rows_frame, variable=p_var,
                                    fg_color="#00bf63", **chk_cfg)
            a_chk = ctk.CTkCheckBox(self.roster_rows_frame, variable=a_var,
                                    fg_color="#e20000", **chk_cfg)
            l_chk = ctk.CTkCheckBox(self.roster_rows_frame, variable=l_var,
                                    fg_color="#122aff", **chk_cfg)

            p_chk.configure(command=lambda p=p_var, a=a_var, l=l_var:
                            self._mutual(p, a, l, "P"))
            a_chk.configure(command=lambda p=p_var, a=a_var, l=l_var:
                            self._mutual(p, a, l, "A"))
            l_chk.configure(command=lambda p=p_var, a=a_var, l=l_var:
                            self._mutual(p, a, l, "L"))

            p_chk.grid(row=idx, column=1, padx=4, pady=5)
            a_chk.grid(row=idx, column=2, padx=4, pady=5)
            l_chk.grid(row=idx, column=3, padx=4, pady=5)

            name_box = ctk.CTkFrame(self.roster_rows_frame, fg_color="#ffffff",
                                    height=35, corner_radius=0,
                                    border_width=1, border_color="#a1a1a1")
            name_box.grid(row=idx, column=4, padx=(15, 0), pady=5, sticky="ew")
            name_box.pack_propagate(False)
            ctk.CTkLabel(name_box, text=name,
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color="black").pack(side="left", padx=15, pady=4)

    def _mutual(self, p_var, a_var, l_var, selected):
        if selected == "P" and p_var.get():
            a_var.set(False)
            l_var.set(False)
        elif selected == "A" and a_var.get():
            p_var.set(False)
            l_var.set(False)
        elif selected == "L" and l_var.get():
            p_var.set(False)
            a_var.set(False)

    def load_students(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT s.studLname, s.studFname, s.studMname
                FROM STUDENT s
                JOIN ENROLLMENT e ON s.studentID = e.studentID
                JOIN DETAIL d ON e.enrollmentID = d.enrollmentID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE e.term = ? AND e.schoolYear = ?
                  AND e.gradeLevel LIKE ?
                  AND sub.subjectName LIKE ?
                ORDER BY s.studLname, s.studFname
            """, (
                self.term_combo.get(),
                self.sy_combo.get(),
                f"%{self.class_combo.get().split(' - ')[0]}%",
                f"%{self.subject_combo.get()}%"
            ))
            rows = cursor.fetchall()
            conn.close()

            if rows:
                names = []
                for r in rows:
                    m = f" {r['studMname'][0]}." if r.get('studMname') else ""
                    names.append(f"{r['studLname']}, {r['studFname']}{m}")
                self.render_roster(names)
            else:
                self.render_roster(self._samples)
                messagebox.showinfo("Info",
                    "No enrolled students found for these filters.\nShowing sample data.")
        except Exception as e:
            print("load_students error:", e)
            self.render_roster(self._samples)

    def save_attendance(self):
        att_date = self.date_entry.get().strip()
        if not att_date:
            messagebox.showwarning("Required", "Please select a date first.")
            return

        if not self.attendance_vars:
            messagebox.showwarning("Empty", "No students loaded.")
            return

        unmarked = [n for n, (p, a, l) in self.attendance_vars.items()
                    if not p.get() and not a.get() and not l.get()]
        if len(unmarked) == len(self.attendance_vars):
            messagebox.showwarning("Nothing Marked",
                                   "Please mark attendance for at least one student.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        saved   = 0
        skipped = []

        try:
            for name, (p_var, a_var, l_var) in self.attendance_vars.items():
                if p_var.get():
                    status = "Present"
                elif a_var.get():
                    status = "Absent"
                elif l_var.get():
                    status = "Late"
                else:
                    skipped.append(name)
                    continue

                parts = name.split(", ", 1)
                lname = parts[0].strip() if len(parts) > 0 else ""
                fname = parts[1].split(" ")[0].strip() if len(parts) > 1 else ""

                cursor.execute("""
                    SELECT d.detailID
                    FROM DETAIL d
                    JOIN ENROLLMENT e ON d.enrollmentID = e.enrollmentID
                    JOIN STUDENT s ON e.studentID = s.studentID
                    JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                    WHERE s.studLname LIKE ?
                      AND s.studFname LIKE ?
                      AND e.term = ?
                      AND e.schoolYear = ?
                      AND sub.subjectName LIKE ?
                    LIMIT 1
                """, (
                    f"%{lname}%",
                    f"%{fname}%",
                    self.term_combo.get(),
                    self.sy_combo.get(),
                    f"%{self.subject_combo.get()}%"
                ))
                detail_row = cursor.fetchone()

                if not detail_row:
                    skipped.append(f"{name} (not enrolled / no detailID found)")
                    continue

                detail_id = detail_row['detailID']

                cursor.execute("""
                    SELECT attendanceID FROM ATTENDANCE
                    WHERE detailID = ? AND attDate = ?
                """, (detail_id, att_date))
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE ATTENDANCE SET attStatus = ?
                        WHERE detailID = ? AND attDate = ?
                    """, (status, detail_id, att_date))
                else:
                    cursor.execute("""
                        INSERT INTO ATTENDANCE (detailID, attDate, attStatus)
                        VALUES (?, ?, ?)
                    """, (detail_id, att_date, status))

                saved += 1

            conn.commit()
            msg = f"Attendance saved for {saved} student(s).\nDate: {att_date}"
            if skipped:
                msg += f"\n\nSkipped ({len(skipped)}):\n" + "\n".join(skipped)
            messagebox.showinfo("Attendance Saved", msg)

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def popup_calendar(self):
        popup = Toplevel(self)
        popup.title("Select Date")
        popup.geometry("340x390")
        popup.resizable(False, False)
        popup.configure(bg="#15165e")
        popup.transient(self)
        popup.update_idletasks()
        try:
            popup.grab_set()
        except Exception:
            pass

        self.current_cal_year  = datetime.now().year
        self.current_cal_month = datetime.now().month

        shortcut_bar = ctk.CTkFrame(popup, fg_color="#111240", height=45, corner_radius=0)
        shortcut_bar.pack(fill="x", side="top")
        shortcut_bar.pack_propagate(False)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Cal.TCombobox",
                        fieldbackground="#000000", background="#000000",
                        foreground="#ffffff", arrowcolor="#ffffff",
                        bd=0, relief="flat")
        style.map("Cal.TCombobox",
                  fieldbackground=[('readonly', '#000000')],
                  foreground=[('readonly', '#ffffff')])

        months_list = [calendar.month_name[i] for i in range(1, 13)]
        years_list  = [str(y) for y in range(
            datetime.now().year + 2, datetime.now().year - 10, -1)]

        def shortcut_changed(event):
            try:
                self.current_cal_month = months_list.index(month_cb.get()) + 1
                self.current_cal_year  = int(year_cb.get())
                update_grid()
            except ValueError:
                pass

        month_cb = ttk.Combobox(shortcut_bar, values=months_list, state="readonly",
                                width=14, font=("Inter", 11),
                                style="Cal.TCombobox", height=6)
        month_cb.pack(side="left", padx=(15, 5), pady=8)
        month_cb.set(calendar.month_name[self.current_cal_month])
        month_cb.bind("<<ComboboxSelected>>", shortcut_changed)

        year_cb = ttk.Combobox(shortcut_bar, values=years_list, state="readonly",
                               width=8, font=("Inter", 11),
                               style="Cal.TCombobox", height=6)
        year_cb.pack(side="left", padx=5, pady=8)
        year_cb.set(str(self.current_cal_year))
        year_cb.bind("<<ComboboxSelected>>", shortcut_changed)

        header = ctk.CTkFrame(popup, fg_color="#15165e", height=45, corner_radius=0)
        header.pack(fill="x", pady=(5, 0))
        header.pack_propagate(False)

        month_year_lbl = ctk.CTkLabel(header, text="",
                                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                      text_color="#ffffff")

        ctk.CTkButton(header, text="◀", width=30, height=30,
                      fg_color="transparent", text_color="white",
                      hover_color="#122aff",
                      command=lambda: change_month(-1)).pack(side="left", padx=10)
        month_year_lbl.pack(side="left", expand=True)
        ctk.CTkButton(header, text="▶", width=30, height=30,
                      fg_color="transparent", text_color="white",
                      hover_color="#122aff",
                      command=lambda: change_month(1)).pack(side="right", padx=10)

        days_frame = ctk.CTkFrame(popup, fg_color="#15165e", height=25, corner_radius=0)
        days_frame.pack(fill="x")
        for col, d in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            ctk.CTkLabel(days_frame, text=d,
                         font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                         text_color="#a5b4fc", width=42).grid(row=0, column=col, padx=2)

        grid_canvas = ctk.CTkFrame(popup, fg_color="#111240", corner_radius=0)
        grid_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        day_btns = {}
        for r in range(6):
            for c in range(7):
                btn = ctk.CTkButton(grid_canvas, text="", width=38, height=35,
                                    font=ctk.CTkFont(family="Inter", size=11),
                                    fg_color="transparent", text_color="#ffffff",
                                    hover_color="#122aff", corner_radius=0)
                btn.grid(row=r, column=c, padx=1, pady=1)
                day_btns[(r, c)] = btn

        def update_grid():
            month_year_lbl.configure(
                text=f"{calendar.month_name[self.current_cal_month]} {self.current_cal_year}")
            month_cb.set(calendar.month_name[self.current_cal_month])
            year_cb.set(str(self.current_cal_year))
            for btn in day_btns.values():
                btn.configure(text="", state="disabled", fg_color="transparent", hover=False)
            _, num_days = calendar.monthrange(self.current_cal_year, self.current_cal_month)
            start_col = (datetime(self.current_cal_year, self.current_cal_month, 1
                                  ).weekday() + 1) % 7
            row, col = 0, start_col
            for day in range(1, num_days + 1):
                day_btns[(row, col)].configure(
                    text=str(day), state="normal",
                    fg_color="transparent", hover=True,
                    command=lambda d=day: pick_date(d))
                col += 1
                if col > 6:
                    col, row = 0, row + 1

        def change_month(step):
            self.current_cal_month += step
            if self.current_cal_month > 12:
                self.current_cal_month, self.current_cal_year = 1, self.current_cal_year + 1
            elif self.current_cal_month < 1:
                self.current_cal_month, self.current_cal_year = 12, self.current_cal_year - 1
            update_grid()

        def pick_date(day_num):
            fmt = f"{self.current_cal_year}-{self.current_cal_month:02d}-{day_num:02d}"
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, fmt)
            popup.destroy()

        update_grid()

    def back_to_dashboard(self):
        parent_frame = self.master
        self.destroy()
        if hasattr(parent_frame, "welcome_lbl"):
            parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(parent_frame.master, "welcome_lbl"):
            parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))