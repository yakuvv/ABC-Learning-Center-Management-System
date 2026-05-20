import customtkinter as ctk
from tkinter import messagebox, Toplevel, ttk
import database
import calendar
from datetime import datetime


class ProfileStudents(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.create_ui()

    def create_ui(self):
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        back_btn = ctk.CTkButton(top_bar, text="<  Back to Dashboard",
                                 font=ctk.CTkFont(family="Inter", size=14),
                                 fg_color="transparent", text_color="#ffffff",
                                 hover_color="#22259c", width=150, height=40,
                                 corner_radius=0, command=self.back_to_dashboard)
        back_btn.pack(side="left", padx=20, pady=15)

        title = ctk.CTkLabel(top_bar, text="Profile Students",
                             font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                             text_color="#ffffff")
        title.pack(side="left", expand=True, padx=(0, 100))

        logo_placeholder = ctk.CTkLabel(top_bar, text="▲\n▬",
                                        font=ctk.CTkFont(family="Inter", size=18),
                                        text_color="#122aff")
        logo_placeholder.pack(side="right", padx=30)

        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(20, 10))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1", width=310, height=46, corner_radius=0)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.add_tab_btn = ctk.CTkButton(tab_pill, text="Add New Student",
                                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                         fg_color="#122aff", text_color="#ffffff",
                                         corner_radius=0, height=38, width=150,
                                         command=lambda: self.switch_tab("add"))
        self.add_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.list_tab_btn = ctk.CTkButton(tab_pill, text="Student List",
                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                          fg_color="transparent", text_color="#374151",
                                          corner_radius=0, height=38, width=150,
                                          command=lambda: self.switch_tab("list"))
        self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        self.render_add_student_form()

    def switch_tab(self, tab_target):
        if tab_target == "add":
            self.add_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.list_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.render_add_student_form()
        else:
            self.add_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.list_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.render_student_list_view()

    def render_add_student_form(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.workspace_canvas, text="STUDENT INFORMATION",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(5, 5))

        split_card_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        split_card_frame.pack(fill="x", pady=(0, 15))

        #Left Card
        left_card = ctk.CTkFrame(split_card_frame, fg_color="#cbd5e1", corner_radius=0, height=160)
        left_card.pack(side="left", fill="x", expand=True, padx=(0, 15))
        left_card.pack_propagate(False)

        accent_l = ctk.CTkFrame(left_card, width=8, fg_color="#15165e", corner_radius=0)
        accent_l.pack(side="left", fill="y")

        inner_l = ctk.CTkFrame(left_card, fg_color="transparent")
        inner_l.pack(fill="both", expand=True, padx=15, pady=12)

        self.fname = ctk.CTkEntry(inner_l, placeholder_text="First Name", height=35, corner_radius=0,
                                  fg_color="#ffffff", text_color="black", border_width=0)
        self.fname.pack(fill="x", pady=4)
        self.lname = ctk.CTkEntry(inner_l, placeholder_text="Last Name", height=35, corner_radius=0,
                                  fg_color="#ffffff", text_color="black", border_width=0)
        self.lname.pack(fill="x", pady=4)
        self.mname = ctk.CTkEntry(inner_l, placeholder_text="Middle Name", height=35, corner_radius=0,
                                  fg_color="#ffffff", text_color="black", border_width=0)
        self.mname.pack(fill="x", pady=4)

        #Right Card 
        right_card = ctk.CTkFrame(split_card_frame, fg_color="#cbd5e1", corner_radius=0, height=160)
        right_card.pack(side="right", fill="x", expand=True, padx=(15, 0))
        right_card.pack_propagate(False)

        accent_r = ctk.CTkFrame(right_card, width=8, fg_color="#15165e", corner_radius=0)
        accent_r.pack(side="left", fill="y")

        inner_r = ctk.CTkFrame(right_card, fg_color="transparent")
        inner_r.pack(fill="both", expand=True, padx=15, pady=12)

        meta_row = ctk.CTkFrame(inner_r, fg_color="transparent")
        meta_row.pack(fill="x", pady=4)

        #Gender custom dropdown (same style as DOB button)
        gender_frame = ctk.CTkFrame(meta_row, fg_color="transparent", height=35)
        gender_frame.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.gender_entry = ctk.CTkEntry(gender_frame, placeholder_text="Gender", height=35,
                                         corner_radius=0, fg_color="#ffffff", text_color="black",
                                         border_width=0)
        self.gender_entry.pack(side="left", fill="both", expand=True)
        self.gender_entry.insert(0, "F")
        self.gender_entry.configure(state="readonly")

        gender_btn = ctk.CTkButton(gender_frame, text="▼", width=35, height=35, corner_radius=0,
                                   fg_color="#000000", hover_color="#222222", text_color="#ffffff",
                                   command=self.toggle_gender_dropdown)
        gender_btn.pack(side="right")

        #DOB custom dropdown
        dob_combo_frame = ctk.CTkFrame(meta_row, fg_color="transparent", height=35)
        dob_combo_frame.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.dob = ctk.CTkEntry(dob_combo_frame, placeholder_text="Date of Birth (YYYY-MM-DD)", height=35,
                                corner_radius=0, fg_color="#ffffff", text_color="black", border_width=0)
        self.dob.pack(side="left", fill="both", expand=True)

        dob_dropdown_btn = ctk.CTkButton(dob_combo_frame, text="▼", width=35, height=35, corner_radius=0,
                                         fg_color="#000000", hover_color="#222222", text_color="#ffffff",
                                         command=self.popup_flutter_calendar)
        dob_dropdown_btn.pack(side="right")

        self.email = ctk.CTkEntry(inner_r, placeholder_text="Email Address", height=35, corner_radius=0,
                                  fg_color="#ffffff", text_color="black", border_width=0)
        self.email.pack(fill="x", pady=4)
        self.contact = ctk.CTkEntry(inner_r, placeholder_text="Contact Number", height=35, corner_radius=0,
                                    fg_color="#ffffff", text_color="black", border_width=0)
        self.contact.pack(fill="x", pady=4)

        #Address
        address_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", corner_radius=0, height=60)
        address_card.pack(fill="x", pady=(0, 20))
        address_card.pack_propagate(False)

        accent_add = ctk.CTkFrame(address_card, width=8, fg_color="#15165e", corner_radius=0)
        accent_add.pack(side="left", fill="y")

        self.address = ctk.CTkEntry(address_card, placeholder_text="Full Address", height=35, corner_radius=0,
                                    fg_color="#ffffff", text_color="black", border_width=0)
        self.address.pack(fill="x", padx=15, pady=12)

        #Parent/Guardian 
        ctk.CTkLabel(self.workspace_canvas, text="PARENT/GUARDIAN INFORMATION",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(5, 5))

        parent_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#cbd5e1", corner_radius=0, height=160)
        parent_card.pack(fill="x", pady=(0, 25))
        parent_card.pack_propagate(False)

        accent_par = ctk.CTkFrame(parent_card, width=8, fg_color="#15165e", corner_radius=0)
        accent_par.pack(side="left", fill="y")

        inner_p = ctk.CTkFrame(parent_card, fg_color="transparent")
        inner_p.pack(fill="both", expand=True, padx=15, pady=12)

        self.par_name = ctk.CTkEntry(inner_p, placeholder_text="Parent/Guardian Full Name", height=35,
                                     corner_radius=0, fg_color="#ffffff", text_color="black", border_width=0)
        self.par_name.pack(fill="x", pady=4)
        self.par_contact = ctk.CTkEntry(inner_p, placeholder_text="Parent/Guardian Contact Information", height=35,
                                        corner_radius=0, fg_color="#ffffff", text_color="black", border_width=0)
        self.par_contact.pack(fill="x", pady=4)
        self.relationship = ctk.CTkEntry(inner_p, placeholder_text="Relationship (Mother, Father, etc.)", height=35,
                                         corner_radius=0, fg_color="#ffffff", text_color="black", border_width=0)
        self.relationship.pack(fill="x", pady=4)

        #Save Button 
        save_btn = ctk.CTkButton(self.workspace_canvas, text="SAVE STUDENT PROFILE",
                                 font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                 height=45, width=260, corner_radius=0,
                                 fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                                 command=self.save_student)
        save_btn.pack(anchor="center")

    def toggle_gender_dropdown(self):
        if hasattr(self, "_gender_menu") and self._gender_menu.winfo_exists():
            self._gender_menu.destroy()
            return

        self.gender_entry.update_idletasks()
        x = self.gender_entry.winfo_rootx()
        y = self.gender_entry.winfo_rooty() + self.gender_entry.winfo_height()
        w = self.gender_entry.winfo_width() + 35

        self._gender_menu = Toplevel(self)
        self._gender_menu.overrideredirect(True)
        self._gender_menu.geometry(f"{w}x70+{x}+{y}")
        self._gender_menu.configure(bg="#000000")

        for val in ["M", "F"]:
            btn = ctk.CTkButton(self._gender_menu, text=val, height=35, corner_radius=0,
                                fg_color="#000000", hover_color="#222222", text_color="#ffffff",
                                anchor="w", command=lambda v=val: self._select_gender(v))
            btn.pack(fill="x")

    def _select_gender(self, value):
        self.gender_entry.configure(state="normal")
        self.gender_entry.delete(0, "end")
        self.gender_entry.insert(0, value)
        self.gender_entry.configure(state="readonly")
        if hasattr(self, "_gender_menu") and self._gender_menu.winfo_exists():
            self._gender_menu.destroy()

    def popup_flutter_calendar(self):
        popup = Toplevel(self)
        popup.title("Select Date of Birth")
        popup.geometry("340x420")
        popup.resizable(False, False)
        popup.configure(bg="#15165e")
        popup.transient(self)

        popup.update_idletasks()
        popup.update()
        try:
            popup.grab_set()
        except Exception:
            pass

        now = datetime.now()
        self.current_cal_year = now.year
        self.current_cal_month = now.month

        #Shortcut bar
        shortcut_bar = ctk.CTkFrame(popup, fg_color="#111240", height=45, corner_radius=0)
        shortcut_bar.pack(fill="x", side="top")
        shortcut_bar.pack_propagate(False)

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Cal.TCombobox", fieldbackground="#000000", background="#000000",
                        foreground="#ffffff", arrowcolor="#ffffff", bd=0, relief="flat")
        style.map("Cal.TCombobox",
                  fieldbackground=[('readonly', '#000000')],
                  foreground=[('readonly', '#ffffff')])

        months_list = [calendar.month_name[i] for i in range(1, 13)]
        years_list = [str(y) for y in range(datetime.now().year, datetime.now().year - 90, -1)]

        def shortcut_changed(event):
            try:
                self.current_cal_month = months_list.index(month_shortcut.get()) + 1
                self.current_cal_year = int(year_shortcut.get())
                update_calendar_grid()
            except ValueError:
                pass

        month_shortcut = ttk.Combobox(shortcut_bar, values=months_list, state="readonly", width=14,
                                      font=("Inter", 11), style="Cal.TCombobox", height=6)
        month_shortcut.pack(side="left", padx=(15, 5), pady=8)
        month_shortcut.set(calendar.month_name[self.current_cal_month])
        month_shortcut.bind("<<ComboboxSelected>>", shortcut_changed)

        year_shortcut = ttk.Combobox(shortcut_bar, values=years_list, state="readonly", width=8,
                                     font=("Inter", 11), style="Cal.TCombobox", height=6)
        year_shortcut.pack(side="left", padx=5, pady=8)
        year_shortcut.set(str(self.current_cal_year))
        year_shortcut.bind("<<ComboboxSelected>>", shortcut_changed)

        #Navigation header
        header = ctk.CTkFrame(popup, fg_color="#15165e", height=45, corner_radius=0)
        header.pack(fill="x", side="top", pady=(5, 0))
        header.pack_propagate(False)

        month_year_lbl = ctk.CTkLabel(header, text="",
                                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                      text_color="#ffffff")

        prev_btn = ctk.CTkButton(header, text="◀", width=30, height=30, fg_color="transparent",
                                 text_color="white", hover_color="#122aff",
                                 command=lambda: change_month(-1))
        prev_btn.pack(side="left", padx=10)

        month_year_lbl.pack(side="left", expand=True)

        next_btn = ctk.CTkButton(header, text="▶", width=30, height=30, fg_color="transparent",
                                 text_color="white", hover_color="#122aff",
                                 command=lambda: change_month(1))
        next_btn.pack(side="right", padx=10)

        #Unified grid frame for headers + day buttons
        grid_frame = ctk.CTkFrame(popup, fg_color="#111240", corner_radius=0)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        col_width = 40
        for c in range(7):
            grid_frame.columnconfigure(c, minsize=col_width, uniform="cal_col")

        days_headers = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for col, d_name in enumerate(days_headers):
            lbl = ctk.CTkLabel(grid_frame, text=d_name,
                               font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                               text_color="#a5b4fc", width=col_width)
            lbl.grid(row=0, column=col, padx=1, pady=(6, 2))

        self.day_buttons = {}
        for r in range(6):
            for c in range(7):
                btn = ctk.CTkButton(grid_frame, text="", width=col_width, height=35,
                                    font=ctk.CTkFont(family="Inter", size=11),
                                    fg_color="transparent", text_color="#ffffff",
                                    hover_color="#122aff", corner_radius=0)
                btn.grid(row=r + 1, column=c, padx=1, pady=1)
                self.day_buttons[(r, c)] = btn

        def update_calendar_grid():
            month_year_lbl.configure(
                text=f"{calendar.month_name[self.current_cal_month]} {self.current_cal_year}")

            if month_shortcut.get() != calendar.month_name[self.current_cal_month]:
                month_shortcut.set(calendar.month_name[self.current_cal_month])
            if year_shortcut.get() != str(self.current_cal_year):
                year_shortcut.set(str(self.current_cal_year))

            for btn in self.day_buttons.values():
                btn.configure(text="", state="disabled", fg_color="transparent", hover=False)

            _, num_days = calendar.monthrange(self.current_cal_year, self.current_cal_month)
            first_day_date = datetime(self.current_cal_year, self.current_cal_month, 1)
            first_weekday_idx = first_day_date.weekday()
            start_col = (first_weekday_idx + 1) % 7

            current_row = 0
            current_col = start_col

            for day in range(1, num_days + 1):
                btn = self.day_buttons[(current_row, current_col)]
                btn.configure(text=str(day), state="normal", fg_color="transparent", hover=True,
                              command=lambda d=day: select_date_return(d))
                current_col += 1
                if current_col > 6:
                    current_col = 0
                    current_row += 1

        def change_month(step):
            self.current_cal_month += step
            if self.current_cal_month > 12:
                self.current_cal_month = 1
                self.current_cal_year += 1
            elif self.current_cal_month < 1:
                self.current_cal_month = 12
                self.current_cal_year -= 1
            update_calendar_grid()

        def select_date_return(day_num):
            formatted_date = f"{self.current_cal_year}-{self.current_cal_month:02d}-{day_num:02d}"
            self.dob.delete(0, 'end')
            self.dob.insert(0, formatted_date)
            popup.destroy()

        update_calendar_grid()

    def render_student_list_view(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        lbl = ctk.CTkLabel(self.workspace_canvas, text="Student Directory List View",
                           font=ctk.CTkFont(family="Inter", size=24, weight="bold"),
                           text_color="black")
        lbl.pack(pady=100)

    def save_student(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.lname.get(), self.fname.get(), self.mname.get(),
                  self.gender_entry.get(), self.dob.get(), self.address.get(),
                  self.contact.get(), self.email.get()))

            student_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO PARENT (studentID, parName, parContactNo, relationship)
                VALUES (?, ?, ?, ?)
            ''', (student_id, self.par_name.get(), self.par_contact.get(), self.relationship.get()))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Student profile saved successfully!")
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save student data: {str(e)}")

    def clear_fields(self):
        self.gender_entry.configure(state="normal")
        self.gender_entry.delete(0, "end")
        self.gender_entry.insert(0, "F")
        self.gender_entry.configure(state="readonly")

        for entry in [self.fname, self.lname, self.mname, self.dob, self.address,
                      self.contact, self.email, self.par_name, self.par_contact, self.relationship]:
            if isinstance(entry, ctk.CTkEntry):
                entry.delete(0, 'end')

    def back_to_dashboard(self):
        parent_frame = self.master
        self.destroy()

        if hasattr(parent_frame, "welcome_lbl"):
            parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(parent_frame.master, "welcome_lbl"):
            parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))