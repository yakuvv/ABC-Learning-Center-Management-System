# modules/record_attendance.py
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

        self.create_ui()

    def create_ui(self):
        # 1. --- Top Header Ribbon Panel ---
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        back_btn = ctk.CTkButton(top_bar, text="〈  back to Dashboard",
                                 font=ctk.CTkFont(family="Inter", size=14),
                                 fg_color="transparent", text_color="#ffffff",
                                 hover_color="#22259c", width=150, height=40,
                                 corner_radius=0, command=self.back_to_dashboard)
        back_btn.pack(side="left", padx=20, pady=15)

        title = ctk.CTkLabel(top_bar, text="Record Attendance",
                             font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                             text_color="#ffffff")
        title.pack(side="left", expand=True, padx=(0, 100))

        logo_placeholder = ctk.CTkLabel(top_bar, text="▲\n📖",
                                        font=ctk.CTkFont(family="Inter", size=18),
                                        text_color="#122aff")
        logo_placeholder.pack(side="right", padx=30)

        # 2. --- Core Workspace Padding Wrapper ---
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=40, pady=20)

        # Greeting Title
        ctk.CTkLabel(workspace, text="Good Day, Mr. Val",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 20))

        # Split Container (Left Panel vs Right Panel)
        split_body = ctk.CTkFrame(workspace, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # --- LEFT PANEL FIELD GROUPS ---
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=480)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)

        dropdown_args = {
            "height": 35, "corner_radius": 0, "fg_color": "#ffffff", "text_color": "black",
            "button_color": "#000000", "button_hover_color": "#222222", "dropdown_fg_color": "#000000",
            "dropdown_text_color": "#ffffff", "dropdown_hover_color": "#222222", "border_width": 0
        }

        def build_input_block(master, title, values, placeholder):
            container = ctk.CTkFrame(master, fg_color="transparent", width=220, height=95)
            container.pack_propagate(False)

            ctk.CTkLabel(container, text=title, font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="black").pack(anchor="w")

            card = ctk.CTkFrame(container, fg_color="#cbd5e1", height=40, corner_radius=0)
            card.pack(fill="x", pady=2)
            card.pack_propagate(False)

            ctk.CTkFrame(card, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")

            red_lbl = ctk.CTkLabel(container, text="", font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                                   text_color="#e20000")

            def on_changed(val):
                red_lbl.configure(text=val.upper())

            combo = ctk.CTkComboBox(card, values=values, **dropdown_args, command=on_changed)
            combo.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=2)
            combo.set(placeholder)

            red_lbl.pack(anchor="center", pady=(2, 0))
            return container, combo

        # Row 1 Layout: CLASS & TERM
        row1_frame = ctk.CTkFrame(left_panel, fg_color="transparent", height=100)
        row1_frame.pack(fill="x", pady=5)

        c_block, self.class_combo = build_input_block(row1_frame, "CLASS", ["Grade 1 - A", "Grade 2 - B"],
                                                      "Search Class")
        c_block.pack(side="left", padx=(0, 10))

        t_block, self.term_combo = build_input_block(row1_frame, "TERM",
                                                     ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"],
                                                     "Select Term")
        t_block.pack(side="left", padx=(10, 0))

        # Row 2 Layout: SCHOOL YEAR & SUBJECT
        row2_frame = ctk.CTkFrame(left_panel, fg_color="transparent", height=100)
        row2_frame.pack(fill="x", pady=5)

        sy_block, self.sy_combo = build_input_block(row2_frame, "SCHOOL YEAR", ["2018-2019", "2019-2020", "2025-2026"],
                                                    "Select School Year")
        sy_block.pack(side="left", padx=(0, 10))

        sub_block, self.subject_combo = build_input_block(row2_frame, "SUBJECT",
                                                          ["Mathematics 1", "English 1", "Science 1"], "Search Subject")
        sub_block.pack(side="left", padx=(10, 0))

        # Row 3 Layout: DATE TODAY
        date_block = ctk.CTkFrame(left_panel, fg_color="transparent", width=220, height=95)
        date_block.pack(anchor="w", pady=5)
        date_block.pack_propagate(False)

        ctk.CTkLabel(date_block, text="DATE TODAY", font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="black").pack(anchor="w")
        date_card = ctk.CTkFrame(date_block, fg_color="#cbd5e1", height=40, corner_radius=0)
        date_card.pack(fill="x", pady=2)
        date_card.pack_propagate(False)

        ctk.CTkFrame(date_card, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")
        self.date_entry = ctk.CTkEntry(date_card, placeholder_text="Select Date", height=35, corner_radius=0,
                                       fg_color="#ffffff", text_color="black", border_width=0)
        self.date_entry.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=2)

        dob_dropdown_btn = ctk.CTkButton(date_card, text="▼", width=35, height=35, corner_radius=0, fg_color="#000000",
                                         hover_color="#222222", text_color="#ffffff",
                                         command=self.popup_flutter_calendar)
        dob_dropdown_btn.pack(side="right", padx=2, pady=2)

        self.date_red_lbl = ctk.CTkLabel(date_block, text="", font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                                         text_color="#e20000")
        self.date_red_lbl.pack(anchor="center", pady=(2, 0))

        # --- RIGHT PANEL FRAME STRUCTURE (STUDENT DIRECTION SHEET AREA) ---
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        ctk.CTkLabel(right_panel, text="STUDENTS", font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                     text_color="black").pack(anchor="w", pady=(0, 4))

        sheet_container = ctk.CTkFrame(right_panel, fg_color="#cbd5e1", corner_radius=0)
        sheet_container.pack(fill="both", expand=True)

        ctk.CTkFrame(sheet_container, width=15, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")

        self.roster_scroll = ctk.CTkScrollableFrame(sheet_container, fg_color="transparent", corner_radius=0)
        self.roster_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.roster_scroll._scrollbar.configure(button_color="#15165e", button_hover_color="#111240", width=12)

        # Roster Sheet Columns Headers Configuration Grid
        hdr = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hdr, text="", width=30).grid(row=0, column=0, padx=2)
        ctk.CTkLabel(hdr, text="P", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#00bf63",
                     width=35).grid(row=0, column=1, padx=4)
        ctk.CTkLabel(hdr, text="A", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#e20000",
                     width=35).grid(row=0, column=2, padx=4)
        ctk.CTkLabel(hdr, text="L", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color="#122aff",
                     width=35).grid(row=0, column=3, padx=4)

        lbl_box = ctk.CTkFrame(hdr, fg_color="#ffffff", height=30, width=240, corner_radius=0, border_width=1,
                               border_color="black")
        lbl_box.grid(row=0, column=4, padx=(15, 0), sticky="ew")
        lbl_box.pack_propagate(False)
        ctk.CTkLabel(lbl_box, text="STUDENT NAME", font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="black").pack(pady=3)

        self.samples = ["Carias, Angelyn F.", "Dela Cruz, Juan G.", "Cruz, Joan H.", "Santos, Maria T."]
        self.attendance_records_map = {}

        # Build layout elements list
        self.render_roster_items()

        # "LOAD STUDENTS" Action submit button panel
        load_btn = ctk.CTkButton(right_panel, text="LOAD STUDENTS",
                                 font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                 height=45, width=180, corner_radius=0,
                                 fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                                 command=self.save_attendance)
        load_btn.pack(side="right", pady=(15, 0))

    def render_roster_items(self):
        self.roster_scroll.grid_columnconfigure(4, weight=1)

        for idx, student_name in enumerate(self.samples):
            row_idx = idx + 1
            ctk.CTkLabel(self.roster_scroll, text=str(row_idx),
                         font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color="black", width=30).grid(
                row=row_idx, column=0, padx=2, pady=5)

            p_var = ctk.BooleanVar(value=True)
            a_var = ctk.BooleanVar()
            l_var = ctk.BooleanVar()
            self.attendance_records_map[student_name] = (p_var, a_var, l_var)

            p_chk = ctk.CTkCheckBox(self.roster_scroll, text="", variable=p_var, width=35, height=35, corner_radius=0,
                                    border_width=2, fg_color="#00bf63", border_color="#ffffff",
                                    checkmark_color="#ffffff")
            a_chk = ctk.CTkCheckBox(self.roster_scroll, text="", variable=a_var, width=35, height=35, corner_radius=0,
                                    border_width=2, fg_color="#e20000", border_color="#ffffff",
                                    checkmark_color="#ffffff")
            l_chk = ctk.CTkCheckBox(self.roster_scroll, text="", variable=l_var, width=35, height=35, corner_radius=0,
                                    border_width=2, fg_color="#122aff", border_color="#ffffff",
                                    checkmark_color="#ffffff")

            p_chk.configure(command=lambda p=p_var, a=a_var, l=l_var: self.toggle_mutual_checkbox(p, a, l, "P"))
            a_chk.configure(command=lambda p=p_var, a=a_var, l=l_var: self.toggle_mutual_checkbox(p, a, l, "A"))
            l_chk.configure(command=lambda p=p_var, a=a_var, l=l_var: self.toggle_mutual_checkbox(p, a, l, "L"))

            p_chk.grid(row=row_idx, column=1, padx=4, pady=5)
            a_chk.grid(row=row_idx, column=2, padx=4, pady=5)
            l_chk.grid(row=row_idx, column=3, padx=4, pady=5)

            name_box = ctk.CTkFrame(self.roster_scroll, fg_color="#ffffff", height=35, corner_radius=0, border_width=1,
                                    border_color="#a1a1a1")
            name_box.grid(row=row_idx, column=4, padx=(15, 0), pady=5, sticky="ew")
            name_box.pack_propagate(False)

            lbl = ctk.CTkLabel(name_box, text=student_name, font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="black")
            lbl.pack(side="left", padx=15, pady=4)

    def toggle_mutual_checkbox(self, p_var, a_var, l_var, selected_type):
        if selected_type == "P":
            a_var.set(False);
            l_var.set(False)
            if not p_var.get(): p_var.set(True)
        elif selected_type == "A":
            p_var.set(False);
            l_var.set(False)
            if not a_var.get(): a_var.set(True)
        elif selected_type == "L":
            p_var.set(False);
            a_var.set(False)
            if not l_var.get(): l_var.set(True)

    def popup_flutter_calendar(self):
        popup = Toplevel(self)
        popup.title("Select Date")
        popup.geometry("340x390")
        popup.resizable(False, False)
        popup.configure(bg="#15165e")
        popup.transient(self)

        popup.update_idletasks()
        popup.update()
        try:
            popup.grab_set()
        except Exception:
            pass

        self.current_cal_year = datetime.now().year
        self.current_cal_month = datetime.now().month

        shortcut_bar = ctk.CTkFrame(popup, fg_color="#111240", height=45, corner_radius=0)
        shortcut_bar.pack(fill="x", side="top")
        shortcut_bar.pack_propagate(False)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Cal.TCombobox", fieldbackground="#000000", background="#000000", foreground="#ffffff",
                        arrowcolor="#ffffff", bd=0, relief="flat")
        style.map("Cal.TCombobox", fieldbackground=[('readonly', '#000000')], foreground=[('readonly', '#ffffff')])

        months_list = [calendar.month_name[i] for i in range(1, 13)]
        years_list = [str(y) for y in range(datetime.now().year + 5, datetime.now().year - 10, -1)]

        def shortcut_changed(event):
            try:
                self.current_cal_month = months_list.index(month_shortcut.get()) + 1
                self.current_cal_year = int(year_shortcut.get())
                update_calendar_grid()
            except ValueError:
                pass

        month_shortcut = ttk.Combobox(shortcut_bar, values=months_list, state="readonly", width=14, font=("Inter", 11),
                                      style="Cal.TCombobox", height=6)
        month_shortcut.pack(side="left", padx=(15, 5), pady=8)
        month_shortcut.set(calendar.month_name[self.current_cal_month])
        month_shortcut.bind("<<ComboboxSelected>>", shortcut_changed)

        year_shortcut = ttk.Combobox(shortcut_bar, values=years_list, state="readonly", width=8, font=("Inter", 11),
                                     style="Cal.TCombobox", height=6)
        year_shortcut.pack(side="left", padx=5, pady=8)
        year_shortcut.set(str(self.current_cal_year))
        year_shortcut.bind("<<ComboboxSelected>>", shortcut_changed)

        header = ctk.CTkFrame(popup, fg_color="#15165e", height=45, corner_radius=0)
        header.pack(fill="x", side="top", pady=(5, 0))
        header.pack_propagate(False)

        month_year_lbl = ctk.CTkLabel(header, text="", font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                      text_color="#ffffff")

        days_frame = ctk.CTkFrame(popup, fg_color="#15165e", height=25, corner_radius=0)
        days_frame.pack(fill="x")
        days_headers = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for col, d_name in enumerate(days_headers):
            lbl = ctk.CTkLabel(days_frame, text=d_name, font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                               text_color="#a5b4fc", width=42)
            lbl.grid(row=0, column=col, padx=2)

        grid_canvas = ctk.CTkFrame(popup, fg_color="#111240", corner_radius=0)
        grid_canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.day_buttons = {}
        for r in range(6):
            for c in range(7):
                btn = ctk.CTkButton(grid_canvas, text="", width=38, height=35,
                                    font=ctk.CTkFont(family="Inter", size=11), fg_color="transparent",
                                    text_color="#ffffff", hover_color="#122aff", corner_radius=0)
                btn.grid(row=r, column=c, padx=1, pady=1)
                self.day_buttons[(r, c)] = btn

        def update_calendar_grid():
            month_year_lbl.configure(text=f"{calendar.month_name[self.current_cal_month]} {self.current_cal_year}")
            if month_shortcut.get() != calendar.month_name[self.current_cal_month]: month_shortcut.set(
                calendar.month_name[self.current_cal_month])
            if year_shortcut.get() != str(self.current_cal_year): year_shortcut.set(str(self.current_cal_year))

            for btn in self.day_buttons.values(): btn.configure(text="", state="disabled", fg_color="transparent",
                                                                hover=False)
            _, num_days = calendar.monthrange(self.current_cal_year, self.current_cal_month)
            first_day_date = datetime(self.current_cal_year, self.current_cal_month, 1)
            start_col = (first_day_date.weekday() + 1) % 7

            current_row, current_col = 0, start_col
            for day in range(1, num_days + 1):
                btn = self.day_buttons[(current_row, current_col)]
                btn.configure(text=str(day), state="normal", fg_color="transparent", hover=True,
                              command=lambda d=day: select_date_return(d))
                current_col += 1
                if current_col > 6: current_col, current_row = 0, current_row + 1

        def change_month(step):
            self.current_cal_month += step
            if self.current_cal_month > 12:
                self.current_cal_month, self.current_cal_year = 1, self.current_cal_year + 1
            elif self.current_cal_month < 1:
                self.current_cal_month, self.current_cal_year = 12, self.current_cal_year - 1
            update_calendar_grid()

        def select_date_return(day_num):
            formatted_date = f"{self.current_cal_year}-{self.current_cal_month:02d}-{day_num:02d}"
            self.date_entry.delete(0, 'end')
            self.date_entry.insert(0, formatted_date)
            self.date_red_lbl.configure(text=formatted_date)
            popup.destroy()

        prev_btn = ctk.CTkButton(header, text="◀", width=30, height=30, fg_color="transparent", text_color="white",
                                 hover_color="#122aff", command=lambda: change_month(-1))
        prev_btn.pack(side="left", padx=10)
        month_year_lbl.pack(side="left", expand=True)
        next_btn = ctk.CTkButton(header, text="▶", width=30, height=30, fg_color="transparent", text_color="white",
                                 hover_color="#122aff", command=lambda: change_month(1))
        next_btn.pack(side="right", padx=10)

        update_calendar_grid()

    def save_attendance(self):
        messagebox.showinfo("Success", "Attendance logging compiled successfully into database logs!")

    def back_to_dashboard(self):
        parent_frame = self.master
        self.destroy()
        if hasattr(parent_frame, "welcome_lbl"):
            parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(parent_frame.master, "welcome_lbl"):
            parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
