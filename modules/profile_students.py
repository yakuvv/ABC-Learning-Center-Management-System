import customtkinter as ctk
from customtkinter import ThemeManager
from tkinter import messagebox, Toplevel, ttk
import database
import calendar
from datetime import datetime
from utils.modern_entry import ModernEntry
from utils.modern_combo import ModernCombo


class DatePickerCombo(ModernCombo):
    # I created this combo with a ModernCombo appearance that opens a calendar popup instead of a value list.

    def __init__(self, master, on_open_calendar, placeholder_text="Date of Birth (MM-DD-YYYY)", **kwargs):
        kwargs.setdefault("values", [""])
        super().__init__(master, **kwargs)
        self._on_open_calendar = on_open_calendar
        self._placeholder_text = placeholder_text
        self._has_value = False
        self._field_font = kwargs.get("font", ctk.CTkFont(family="Inter", size=13))
        self.set("")

    def _placeholder_text_color(self):
        colors = ThemeManager.theme["CTkEntry"]["placeholder_text_color"]
        return colors[1 if ctk.get_appearance_mode() == "Dark" else 0]

    def _show_placeholder(self):
        self._has_value = False
        super().set(self._placeholder_text)
        self.configure(
            text_color=self._placeholder_text_color(),
            font=self._field_font,
        )

    def set(self, value):
        if value:
            self._has_value = True
            super().set(value)
            self.configure(text_color="black", font=self._field_font)
        else:
            self._show_placeholder()

    def get(self):
        if not self._has_value:
            return ""
        val = super().get()
        if val == self._placeholder_text:
            return ""
        return val

    def _open_dropdown_menu(self):
        if self._on_open_calendar:
            self._on_open_calendar()


class ProfileStudents(ctk.CTkFrame):
    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user_role = user_role
        self.user_id = user_id

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
                                 corner_radius=8, command=self.back_to_dashboard)
        back_btn.pack(side="left", padx=20, pady=15)

        title = ctk.CTkLabel(top_bar, text="Profile Students",
                              font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                              text_color="#ffffff")
        title.pack(side="left", expand=True, padx=(0, 100))

        from PIL import Image
        import os
        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(55, 55))
            logo_lbl = ctk.CTkLabel(top_bar, image=ctk_logo, text="")
            logo_lbl.pack(side="right", padx=30)
        else:
            logo_placeholder = ctk.CTkLabel(top_bar, text="▲\n▬",
                                            font=ctk.CTkFont(family="Inter", size=18),
                                            text_color="#122aff")
            logo_placeholder.pack(side="right", padx=30)

        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(20, 10))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1", width=310, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.add_tab_btn = ctk.CTkButton(tab_pill, text="Add New Student",
                                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                         fg_color="#122aff", text_color="#ffffff",
                                         corner_radius=19, height=38, width=150,
                                         command=lambda: self.switch_tab("add"))
        self.add_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.list_tab_btn = ctk.CTkButton(tab_pill, text="Student List",
                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                          fg_color="transparent", text_color="#374151",
                                          corner_radius=19, height=38, width=150,
                                          command=lambda: self.switch_tab("list"))
        self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        self.render_add_student_form()

    @staticmethod
    def _add_combo_underline(parent, combo):
        """Match ModernEntry: navy underline below combo, bright blue on focus."""
        underline = ctk.CTkFrame(parent, height=2, fg_color="#15165e", corner_radius=0)
        underline.pack(fill="x", pady=(0, 2))

        def on_focus(_event=None):
            underline.configure(fg_color="#122aff")

        def on_unfocus(_event=None):
            underline.configure(fg_color="#15165e")

        combo.bind("<FocusIn>", on_focus)
        combo.bind("<FocusOut>", on_unfocus)

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
        left_card = ctk.CTkFrame(split_card_frame, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=200)
        left_card.pack(side="left", fill="x", expand=True, padx=(0, 15))
        left_card.pack_propagate(False)

        accent_container_l = ctk.CTkFrame(left_card, width=6, fg_color="transparent")
        accent_container_l.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent_l = ctk.CTkFrame(accent_container_l, width=6, fg_color="#15165e", corner_radius=3)
        accent_l.pack(fill="both", expand=True)

        inner_l = ctk.CTkFrame(left_card, fg_color="transparent")
        inner_l.pack(fill="both", expand=True, padx=15, pady=12)

        self.fname = ModernEntry(inner_l, placeholder_text="First Name",
                                  height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.fname.pack(fill="x", pady=(4, 0))
        self.lname = ModernEntry(inner_l, placeholder_text="Last Name",
                                 height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.lname.pack(fill="x", pady=(4, 0))
        self.mname = ModernEntry(inner_l, placeholder_text="Middle Name",
                                 height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.mname.pack(fill="x", pady=(4, 0))

        #Right Card 
        right_card = ctk.CTkFrame(split_card_frame, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=200)
        right_card.pack(side="right", fill="x", expand=True, padx=(15, 0))
        right_card.pack_propagate(False)

        accent_container_r = ctk.CTkFrame(right_card, width=6, fg_color="transparent")
        accent_container_r.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent_r = ctk.CTkFrame(accent_container_r, width=6, fg_color="#15165e", corner_radius=3)
        accent_r.pack(fill="both", expand=True)

        inner_r = ctk.CTkFrame(right_card, fg_color="transparent")
        inner_r.pack(fill="both", expand=True, padx=15, pady=12)

        meta_row = ctk.CTkFrame(inner_r, fg_color="transparent")
        meta_row.pack(fill="x", pady=4)

        # Gender dropdown (ModernCombo — same design as other modules)
        gender_wrap = ctk.CTkFrame(meta_row, fg_color="transparent")
        gender_wrap.pack(side="left", padx=(0, 5))
        self.gender_entry = ModernCombo(gender_wrap, values=["M", "F"], height=35, width=120, placeholder_text="Gender")
        self.gender_entry.pack(fill="x")
        self._add_combo_underline(gender_wrap, self.gender_entry)

        # DOB picker (ModernCombo appearance; calendar popup unchanged)
        dob_wrap = ctk.CTkFrame(meta_row, fg_color="transparent")
        dob_wrap.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.dob = DatePickerCombo(dob_wrap, self.popup_flutter_calendar, height=35)
        self.dob.pack(fill="x")
        self._add_combo_underline(dob_wrap, self.dob)

        self.stud_contact_info = ModernEntry(inner_r, placeholder_text="Contact Information (Phone No. or Email)",
                                             height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.stud_contact_info.pack(fill="x", pady=(4, 0))

        # Level dropdown
        level_wrap = ctk.CTkFrame(inner_r, fg_color="transparent")
        level_wrap.pack(fill="x", pady=(4, 0))
        self.level_entry = ModernCombo(level_wrap, values=[f"Grade {i}" for i in range(1, 13)], height=35, placeholder_text="Grade Level")
        self.level_entry.pack(fill="x")
        self._add_combo_underline(level_wrap, self.level_entry)

        #Address
        address_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=60)
        address_card.pack(fill="x", pady=(0, 20))
        address_card.pack_propagate(False)

        accent_container_add = ctk.CTkFrame(address_card, width=6, fg_color="transparent")
        accent_container_add.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent_add = ctk.CTkFrame(accent_container_add, width=6, fg_color="#15165e", corner_radius=3)
        accent_add.pack(fill="both", expand=True)

        self.address = ModernEntry(address_card, placeholder_text="Full Address",
                                   height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.address.pack(fill="x", padx=15, pady=10)

        #Parent/Guardian 
        ctk.CTkLabel(self.workspace_canvas, text="PARENT/GUARDIAN INFORMATION",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(5, 5))

        parent_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=160)
        parent_card.pack(fill="x", pady=(0, 25))
        parent_card.pack_propagate(False)

        accent_container_par = ctk.CTkFrame(parent_card, width=6, fg_color="transparent")
        accent_container_par.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent_par = ctk.CTkFrame(accent_container_par, width=6, fg_color="#15165e", corner_radius=3)
        accent_par.pack(fill="both", expand=True)

        inner_p = ctk.CTkFrame(parent_card, fg_color="transparent")
        inner_p.pack(fill="both", expand=True, padx=15, pady=12)

        self.par_name = ModernEntry(inner_p, placeholder_text="Parent/Guardian Full Name",
                                    height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.par_name.pack(fill="x", pady=(4, 0))
        self.par_contact_info = ModernEntry(inner_p, placeholder_text="Contact Information (Phone No. or Email)",
                                            height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.par_contact_info.pack(fill="x", pady=(4, 0))
        self.relationship = ModernEntry(inner_p, placeholder_text="Relationship (Mother, Father, etc.)",
                                        height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.relationship.pack(fill="x", pady=(4, 0))

        #Save Button 
        save_btn = ctk.CTkButton(self.workspace_canvas, text="SAVE STUDENT PROFILE",
                                 font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                 height=45, width=260, corner_radius=8,
                                 fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                                 command=self.save_student)
        save_btn.pack(anchor="center")

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
            self.dob.set(formatted_date)
            popup.destroy()

        update_calendar_grid()

    def render_student_list_view(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.workspace_canvas, text="STUDENT DIRECTORY",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(5, 5))

        search_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=60)
        search_frame.pack(fill="x", pady=(0, 15))
        search_frame.pack_propagate(False)

        inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)

        search_row = ctk.CTkFrame(inner, fg_color="transparent")
        search_row.pack(fill="x")

        self.student_search_entry = ModernEntry(search_row, placeholder_text="Search Student ID, Last Name, First Name...",
                                                height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.student_search_entry.pack(side="left", fill="x", expand=True)
        self.student_search_entry.bind("<KeyRelease>", lambda e: self.search_students_list())

        ctk.CTkButton(search_row, text="SEARCH", width=130, height=40,
                      fg_color="#122aff", hover_color="#0b1eb3", corner_radius=8,
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      command=self.search_students_list).pack(side="right", padx=(10, 0))

        ctk.CTkButton(inner, text="Show All Students", width=180, height=35,
                      fg_color="#374151", hover_color="#272f3a", corner_radius=8,
                      font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                      command=self.load_all_students_list).pack(anchor="w", pady=(5, 0))

        table_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        table_card.pack(fill="both", expand=True, padx=5)

        self.tree_frame = ctk.CTkFrame(table_card, fg_color="transparent", corner_radius=8)
        self.tree_frame.pack(fill="both", expand=True, padx=15, pady=12)

        import tkinter.ttk as ttk
        columns = ("#", "Last Name", "First Name", "Middle Name", "Gender", "Date of Birth", "Level", "Contact Information")

        # Set modern theme and style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading",
                        background="#15165e",
                        foreground="#ffffff",
                        font=("Inter", 11, "bold"),
                        bordercolor="#15165e",
                        borderwidth=0)
        style.map("Treeview.Heading",
                  background=[('active', '#1c1d7c')],
                  foreground=[('active', '#ffffff')])
        style.configure("Treeview",
                        font=("Inter", 10),
                        rowheight=32,
                        fieldbackground="#ffffff",
                        background="#ffffff",
                        borderwidth=0)

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)
        
        # Alternating row colors
        self.tree.tag_configure("evenrow", background="#f8fafc")
        self.tree.tag_configure("oddrow", background="#ffffff")

        col_widths = [40, 130, 130, 100, 70, 100, 120, 280]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center" if col == "#" else "center")

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        
        self.tree.bind("<Double-1>", self.on_student_double_click)

        self.load_all_students_list()

    def _populate_student_tree(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for idx, row in enumerate(rows):
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert("", "end", iid=str(row['studentID']), values=(
                idx + 1,
                row['studLname'], row['studFname'], row['studMname'] or "—",
                row['gender'], row['dob'], row['level'] or "Unassigned",
                row['studContactInfo'] or "—",
            ), tags=(tag,))

    def on_student_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return
        try:
            student_id = int(item_id)
        except ValueError:
            return
        self.show_student_detail_popup(student_id)

    def show_student_detail_popup(self, student_id):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT studentID, studLname, studFname, studMname, gender, dob, address, studContactInfo, level
                FROM STUDENT
                WHERE studentID = ?
            """, (student_id,))
            student = cursor.fetchone()

            cursor.execute("""
                SELECT parName, parContactInfo, relationship
                FROM PARENT
                WHERE studentID = ?
            """, (student_id,))
            parent = cursor.fetchone()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to retrieve student details: {e}")
            return

        if not student:
            messagebox.showerror("Error", "Student not found.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title(f"Student Profile - {student['studFname']} {student['studLname']}")
        popup.geometry("680x520")
        popup.resizable(False, False)
        popup.configure(fg_color="#e4e4e4")
        popup.transient(self.winfo_toplevel())
        
        # Center popup on screen
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 680) // 2
        y = (screen_height - 520) // 2
        popup.geometry(f"680x520+{x}+{y}")
        
        try:
            popup.grab_set()
        except Exception:
            pass

        # Accent Top Bar
        top_bar = ctk.CTkFrame(popup, height=60, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkLabel(top_bar, text=f"STUDENT PROFILE: {student['studFname'].upper()} {student['studLname'].upper()}",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=20, pady=15)

        container = ctk.CTkFrame(popup, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=15)

        def create_detail_card(parent_widget, title):
            card = ctk.CTkFrame(parent_widget, fg_color="#ffffff", corner_radius=12, border_width=1, border_color="#cbd5e1")
            card.pack(fill="x", pady=(0, 15))
            
            acc_wrap = ctk.CTkFrame(card, width=5, fg_color="transparent")
            acc_wrap.pack(side="left", fill="y", padx=(10, 0), pady=10)
            ctk.CTkFrame(acc_wrap, width=5, fg_color="#15165e", corner_radius=2.5).pack(fill="both", expand=True)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=10)
            
            ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#15165e").pack(anchor="w", pady=(0, 8))
            return inner

        def add_info_row(parent, row_idx, label, val):
            row_frame = ctk.CTkFrame(parent, fg_color="transparent")
            row_frame.grid(row=row_idx // 2, column=row_idx % 2, sticky="ew", pady=3, padx=5)
            
            ctk.CTkLabel(row_frame, text=f"{label}:", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#64748b", width=105, anchor="w").pack(side="left")
            ctk.CTkLabel(row_frame, text=str(val), font=ctk.CTkFont(family="Inter", size=12), text_color="#0f172a", anchor="w").pack(side="left", fill="x", expand=True)

        # Student Details Card
        student_inner = create_detail_card(container, "STUDENT INFORMATION")
        grid_s = ctk.CTkFrame(student_inner, fg_color="transparent")
        grid_s.pack(fill="x")
        grid_s.columnconfigure(0, weight=1)
        grid_s.columnconfigure(1, weight=1)

        add_info_row(grid_s, 0, "Student ID", f"STUD-{student['studentID']:04d}")
        add_info_row(grid_s, 1, "Full Name", f"{student['studLname']}, {student['studFname']} {student['studMname'] or ''}")
        add_info_row(grid_s, 2, "Grade Level", student['level'] or "Unassigned")
        add_info_row(grid_s, 3, "Gender", student['gender'])
        add_info_row(grid_s, 4, "Date of Birth", student['dob'])
        add_info_row(grid_s, 5, "Contact Information", student['studContactInfo'] or "—")

        addr_frame = ctk.CTkFrame(student_inner, fg_color="transparent")
        addr_frame.pack(fill="x", pady=(8, 0), padx=5)
        ctk.CTkLabel(addr_frame, text="Full Address:", font=ctk.CTkFont(family="Inter", size=11, weight="bold"), text_color="#64748b", width=105, anchor="w").pack(side="left")
        ctk.CTkLabel(addr_frame, text=student['address'] or "—", font=ctk.CTkFont(family="Inter", size=12), text_color="#0f172a", anchor="w", justify="left", wraplength=480).pack(side="left", fill="x", expand=True)

        # Parent Details Card
        parent_inner = create_detail_card(container, "PARENT / GUARDIAN INFORMATION")
        if parent:
            grid_p = ctk.CTkFrame(parent_inner, fg_color="transparent")
            grid_p.pack(fill="x")
            grid_p.columnconfigure(0, weight=1)
            grid_p.columnconfigure(1, weight=1)

            add_info_row(grid_p, 0, "Parent Name", parent['parName'])
            add_info_row(grid_p, 1, "Relationship", parent['relationship'])
            add_info_row(grid_p, 2, "Contact Information", parent['parContactInfo'] or "—")
        else:
            ctk.CTkLabel(parent_inner, text="No parent/guardian information found.", font=ctk.CTkFont(family="Inter", size=12, italic=True), text_color="#ef4444").pack(anchor="w", pady=5)

        # Close Button
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 15))
        close_btn = ctk.CTkButton(btn_frame, text="CLOSE PROFILE",
                                  font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                  fg_color="#374151", hover_color="#1f2937", text_color="#ffffff",
                                  width=160, height=38, corner_radius=8,
                                  command=popup.destroy)
        close_btn.pack(anchor="center")

    def load_all_students_list(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT studentID, studLname, studFname, studMname, gender, dob, level, studContactInfo
                FROM STUDENT
                ORDER BY studentID ASC
            """)
            rows = cursor.fetchall()
            conn.close()

            self._populate_student_tree(rows)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load students: {str(e)}")

    def search_students_list(self):
        keyword = self.student_search_entry.get().strip()
        if not keyword:
            self.load_all_students_list()
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT studentID, studLname, studFname, studMname, gender, dob, level, studContactInfo
                FROM STUDENT
                WHERE studentID = ? 
                   OR studLname LIKE ? 
                   OR studFname LIKE ? 
                   OR studMname LIKE ?
                ORDER BY studentID ASC
            """
            val = f"%{keyword}%"
            try:
                kid = int(keyword)
            except ValueError:
                kid = -1
                
            cursor.execute(query, (kid, val, val, val))
            rows = cursor.fetchall()
            conn.close()

            self._populate_student_tree(rows)
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to search students: {str(e)}")

    def save_student(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO STUDENT (studLname, studFname, studMname, gender, dob, address, studContactInfo, level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (self.lname.get(), self.fname.get(), self.mname.get(),
                  self.gender_entry.get(), self.dob.get(), self.address.get(),
                  self.stud_contact_info.get(), self.level_entry.get()))

            student_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO PARENT (studentID, parName, parContactInfo, relationship)
                VALUES (?, ?, ?, ?)
            ''', (student_id, self.par_name.get(), self.par_contact_info.get(), self.relationship.get()))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Student profile saved successfully!")
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save student data: {str(e)}")

    def clear_fields(self):
        self.gender_entry.set("Gender")
        self.level_entry.set("Grade Level")

        for entry in [self.fname, self.lname, self.mname, self.address,
                      self.stud_contact_info, self.par_name, self.par_contact_info,
                      self.relationship]:
            try:
                entry.delete(0, 'end')
            except Exception:
                pass

        self.dob.set("")

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()