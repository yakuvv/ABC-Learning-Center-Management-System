import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import database
from database import generate_learner_id, price_for_level
from utils.modern_entry import ModernEntry
from utils.modern_combo import ModernCombo
from utils.term_options import apply_term_combo_for_level

class ManageEnrollment(ctk.CTkFrame):
    # Right-panel scroll areas
    H_CONFIRM = 160
    H_SUBJECTS = 280

    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        
        self.user_role = user_role
        self.staff_id = user_id
        self.current_student_id = None
        self.subject_vars = {}
        self.selected_subjects = []
        self.selected_batches = {}  # subjectID -> batchID
        self._suggestions_rows = []

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.create_ui()

    def create_ui(self):
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkButton(top_bar, text="<  Back to Dashboard",
                      font=ctk.CTkFont(family="Inter", size=14),
                      fg_color="transparent", text_color="#ffffff",
                      hover_color="#22259c", width=150, height=40,
                      corner_radius=8, command=self.back_to_dashboard
                      ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(top_bar, text="Manage Enrollment",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        from PIL import Image
        import os
        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(55, 55))
            ctk.CTkLabel(top_bar, image=ctk_logo, text="").pack(side="right", padx=30)
        else:
            ctk.CTkLabel(top_bar, text="ABC", 
                         font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                         text_color="#122aff").pack(side="right", padx=30)

        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(20, 10))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1",
                                width=310, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.new_tab_btn = ctk.CTkButton(tab_pill, text="New Enrollment",
                                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                         fg_color="#122aff", text_color="#ffffff",
                                         corner_radius=19, height=38, width=150,
                                         command=lambda: self.switch_tab("new"))
        self.new_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.list_tab_btn = ctk.CTkButton(tab_pill, text="Enrollment List",
                                          font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                          fg_color="transparent", text_color="#374151",
                                          corner_radius=19, height=38, width=150,
                                          command=lambda: self.switch_tab("list"))
        self.list_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        self.render_new_enrollment_form()

    def switch_tab(self, tab_target):
        if tab_target == "new":
            self.new_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.list_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.render_new_enrollment_form()
        else:
            self.new_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.list_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.render_enrollment_list()

    def _card(self, parent, height=None, scrollable=False, accent_color="#15165e"):
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=14, border_width=1, border_color="#cbd5e1")
        if height:
            card.configure(height=height)
            card.pack_propagate(False)

        accent_container = ctk.CTkFrame(card, width=5, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(10, 0), pady=10)
        ctk.CTkFrame(accent_container, width=5, fg_color=accent_color, corner_radius=3).pack(fill="y", expand=True)

        if scrollable:
            inner = ctk.CTkScrollableFrame(card, fg_color="transparent", corner_radius=0)
        else:
            inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=10)
        return card, inner

    def _section_header(self, parent, title, subtitle=None):
        wrap = ctk.CTkFrame(parent, fg_color="transparent")
        wrap.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(
            wrap, text=title,
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1e293b",
        ).pack(anchor="w")
        if subtitle:
            ctk.CTkLabel(
                wrap, text=subtitle,
                font=ctk.CTkFont(family="Inter", size=11),
                text_color="#64748b",
            ).pack(anchor="w", pady=(2, 0))
        return wrap

    def _info_banner(self, parent, text, accent="#eef2ff"):
        banner = ctk.CTkFrame(
            parent, fg_color=accent, corner_radius=10,
            border_width=1, border_color="#cbd5e1",
        )
        banner.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            banner, text=text,
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#334155",
            wraplength=520, justify="left",
        ).pack(anchor="w", padx=12, pady=8)
        return banner

    def _batch_slot_text(self, enrolled, capacity):
        remaining = max(capacity - enrolled, 0)
        if remaining <= 0:
            return f"FULL ({capacity}/{capacity})"
        return f"{remaining} of {capacity} slots open"

    def _batch_slot_subtext(self, enrolled, capacity):
        return f"{enrolled} student(s) enrolled"

    def _select_batch_tile(self, subject_id, batch_id, tile, peer_tiles):
        for t in peer_tiles:
            t.configure(border_color="#e2e8f0", fg_color="#ffffff")
        tile.configure(border_color="#122aff", fg_color="#eef2ff")
        self.selected_batches[subject_id] = batch_id

    def _build_batch_tiles(self, parent, subject_id, batches):
        """Two clickable Batch A / B tiles instead of a long dropdown."""
        tiles_wrap = ctk.CTkFrame(parent, fg_color="transparent")
        tiles_wrap.pack(fill="x", pady=(4, 0))
        tiles_wrap.columnconfigure(0, weight=1)
        tiles_wrap.columnconfigure(1, weight=1)

        peer_tiles = []
        first_available = None

        for col, b in enumerate(batches[:2]):
            enrolled = int(b["enrolled"])
            capacity = int(b["capacity"])
            full = enrolled >= capacity
            remaining = max(capacity - enrolled, 0)

            border = "#fecaca" if full else "#e2e8f0"
            bg = "#fef2f2" if full else "#ffffff"

            tile = ctk.CTkFrame(
                tiles_wrap, fg_color=bg, corner_radius=10,
                border_width=2, border_color=border, height=100,
            )
            tile.grid(row=0, column=col, sticky="nsew", padx=(0, 6) if col == 0 else (6, 0), pady=2)
            tile.pack_propagate(False)
            peer_tiles.append(tile)

            inner = ctk.CTkFrame(tile, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=10, pady=8)

            top_row = ctk.CTkFrame(inner, fg_color="transparent")
            top_row.pack(fill="x")

            ctk.CTkLabel(                top_row, text=f"Batch {b['batchLabel']}",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                text_color="#15165e" if not full else "#991b1b",
            ).pack(side="left")

            badge_bg = "#fee2e2" if full else "#dcfce7"
            badge_fg = "#991b1b" if full else "#166534"
            badge = ctk.CTkFrame(top_row, fg_color=badge_bg, corner_radius=6)
            badge.pack(side="right")
            ctk.CTkLabel(
                badge, text=self._batch_slot_text(enrolled, capacity),
                font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                text_color=badge_fg,
            ).pack(padx=8, pady=3)

            ctk.CTkLabel(
                inner, text=b["schedule"],
                font=ctk.CTkFont(family="Inter", size=11),
                text_color="#64748b",
                wraplength=200, justify="left",
            ).pack(anchor="w", pady=(4, 2))

            ctk.CTkLabel(
                inner, text=self._batch_slot_subtext(enrolled, capacity),
                font=ctk.CTkFont(family="Inter", size=10),
                text_color="#64748b",
            ).pack(anchor="w")

            if not full:
                bid = b["batchID"]
                if first_available is None:
                    first_available = (bid, tile)

        for b, tile in zip(batches[:2], peer_tiles):
            enrolled = int(b["enrolled"])
            capacity = int(b["capacity"])
            if enrolled >= capacity:
                continue
            bid = b["batchID"]
            inner = tile.winfo_children()[0]
            clickables = [tile, inner, *inner.winfo_children()]
            for widget in clickables:
                widget.bind(
                    "<Button-1>", 
                    lambda _e, sid=subject_id, batch_id=bid, t=tile, peers=peer_tiles: self._select_batch_tile(
                        sid, batch_id, t, peers
                    ),
                )
                try:
                    widget.configure(cursor="hand2")
                except Exception:
                    pass

        if first_available:
            bid, tile = first_available
            self._select_batch_tile(subject_id, bid, tile, peer_tiles)

        return peer_tiles

    def render_new_enrollment_form(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        self.current_student_id = None
        self.selected_batches = {}

        self._section_header(self.workspace_canvas, "Search student", "Find the learner to enroll.")

        self.search_block = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        self.search_block.pack(fill="x", pady=(0, 6))

        search_shell = ctk.CTkFrame(
            self.search_block, fg_color="#ffffff", corner_radius=12,
            border_width=1, border_color="#cbd5e1",
        )
        search_shell.pack(fill="x")

        search_inner = ctk.CTkFrame(search_shell, fg_color="transparent")
        search_inner.pack(fill="x", padx=14, pady=10)

        self.search_entry = ModernEntry(
            search_inner, placeholder_text="Student ID or name...",
            height=34, font=ctk.CTkFont(family="Inter", size=13),
        )
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self._on_search_key)
        self.search_entry.bind("<FocusOut>", lambda _: self.after(250, self._hide_suggestions))

        self.suggest_frame = ctk.CTkFrame(
            self.search_block, fg_color="#ffffff", corner_radius=10,
            border_width=1, border_color="#cbd5e1",
        )
        self.suggest_lbox = tk.Listbox(
            self.suggest_frame,
            bg="#ffffff", fg="#1e293b",
            selectbackground="#122aff", selectforeground="#ffffff",
            font=("Inter", 12), borderwidth=0, highlightthickness=0,
            height=5, activestyle="none",
        )
        self.suggest_lbox.pack(fill="x", padx=8, pady=8)
        self.suggest_lbox.bind("<<ListboxSelect>>", self._on_suggestion_select)

        self._build_student_info_area(self.workspace_canvas)
        self.show_no_student_selected()

        two_col = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        two_col.pack(fill="both", expand=True, pady=(4, 0))
        two_col.columnconfigure(0, weight=2)
        two_col.columnconfigure(1, weight=3)
        two_col.rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(two_col, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self._section_header(
            left_frame, "Enrollment details",
            "Grade level and term (Term 1 or Term 2).",
        )

        det_card, det_inner = self._card(left_frame, accent_color="#24894c")
        det_card.pack(fill="x")

        det_inner.columnconfigure(1, weight=1)

        self.term_combo = self._combo(det_inner, [])
        self.term_combo.configure(command=self.on_term_changed)
        self.level_combo = self._combo(det_inner, [f"Grade {i}" for i in range(1, 13)])
        self.level_combo.configure(command=self.on_level_changed)

        self.level_combo.set("")
        self.term_combo.set("")
        self.on_level_changed("")
        self.update_combo_style(self.term_combo)

        for i, (label, widget) in enumerate(zip(["Level", "Term"], [self.level_combo, self.term_combo])):
            ctk.CTkLabel(det_inner, text=label, text_color="#475569",
                         font=ctk.CTkFont(size=12, weight="bold")).grid(row=i, column=0, sticky="w", pady=6)
            widget.grid(row=i, column=1, sticky="ew", padx=(16, 0), pady=6)

        ctk.CTkButton(
            det_inner, text="Continue →",
            fg_color="#24894c", hover_color="#1d6f3d", text_color="#ffffff",
            height=38, corner_radius=8,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            command=self.ok_details,
        ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        self.right_frame = ctk.CTkFrame(two_col, fg_color="transparent")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.show_confirmation_placeholder()

    def show_confirmation_placeholder(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

        self._section_header(
            self.right_frame, "CONFIRMATION DETAILS",
            "Complete the steps on the left to continue.",
        )

        self.confirm_card, self.confirm_inner = self._card(self.right_frame, height=self.H_CONFIRM)
        self.confirm_card.pack(fill="both", expand=True)

        placeholder_lbl = ctk.CTkLabel(
            self.confirm_inner,
            text="1. Search and select a student\n2. Choose Level and Term, then click OK",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#64748b",
            justify="left",
        )
        placeholder_lbl.pack(expand=True, anchor="w", padx=8)

    def _build_student_info_area(self, parent):
        self.student_info_card = ctk.CTkFrame(
            parent, fg_color="#eef2ff", corner_radius=10,
            border_width=1, border_color="#c7d2fe", height=44,
        )
        self.student_info_card.pack_propagate(False)
        self.student_info_inner = ctk.CTkFrame(self.student_info_card, fg_color="transparent")
        self.student_info_inner.pack(fill="both", expand=True, padx=12, pady=8)

    def show_no_student_selected(self):
        self.student_info_card.pack_forget()

    def show_selected_student(self, student_id, full_name):
        self.student_info_card.pack(fill="x", pady=(0, 8), after=self.search_block)

        for w in self.student_info_inner.winfo_children():
            w.destroy()

        row = ctk.CTkFrame(self.student_info_inner, fg_color="transparent")
        row.pack(fill="x")

        ctk.CTkLabel(
            row, text="Selected:",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#64748b",
        ).pack(side="left")

        ctk.CTkLabel(
            row, text=full_name,
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#15165e",
        ).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(
            row, text=f"· ID {student_id}",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#64748b",
        ).pack(side="left", padx=(6, 0))

    def _on_search_key(self, event):
        kw = self.search_entry.get().strip()
        if not kw:
            self._hide_suggestions()
            return

        try:
            kid = int(kw)
        except ValueError:
            kid = -1

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT studentID, studFname, studMname, studLname
                FROM STUDENT
                WHERE studentID = ?
                   OR studFname LIKE ?
                   OR studLname LIKE ?
                   OR (studFname || ' ' || studLname) LIKE ?
                ORDER BY studLname, studFname
                LIMIT 8
            """, (kid, f"%{kw}%", f"%{kw}%", f"%{kw}%"))
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to search student: {str(e)}")
            self._hide_suggestions()
            return

        if rows:
            self._suggestions_rows = rows
            self.suggest_lbox.delete(0, tk.END)
            for row in rows:
                mname = f" {row['studMname'][0]}." if row.get("studMname") else ""
                lbl = f" {row['studFname']}{mname} {row['studLname']}  (Student ID: {row['studentID']})"
                self.suggest_lbox.insert(tk.END, lbl)
            self.suggest_lbox.config(height=min(len(rows), 6))
            self.suggest_frame.pack(fill="x", pady=(4, 0))
        else:
            self._hide_suggestions()

    def _hide_suggestions(self):
        self.suggest_frame.pack_forget()
        self._suggestions_rows = []

    def _on_suggestion_select(self, event):
        sel = self.suggest_lbox.curselection()
        if not sel:
            return
        row = self._suggestions_rows[sel[0]]
        self._select_student(row)
        self.search_entry.delete(0, tk.END)
        self._hide_suggestions()

    def _select_student(self, row):
        self.current_student_id = row["studentID"]
        full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
        self.current_student_name = full_name
        self.show_selected_student(row["studentID"], full_name)

    def ok_details(self):
        # 1. Validate that a student is selected
        if not getattr(self, 'current_student_id', None):
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        # 2. Validate basic registration details
        level = self.level_combo.get()
        term = self.term_combo.get()

        if not level or not term:
            messagebox.showwarning("Warning", "Please complete all fields (Level and Term) first!")
            return
        # 3. Show the Confirmation Details layout
        self.show_confirmation_details()

    def show_confirmation_details(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

        self._section_header(
            self.right_frame, "CONFIRMATION DETAILS",
            "Review student, level, and term before choosing subjects.",
        )

        self.confirm_card, self.confirm_inner = self._card(self.right_frame, height=self.H_CONFIRM)
        self.confirm_card.pack(fill="both", expand=True)

        level = self.level_combo.get()
        term = self.term_combo.get()
        group_name = "Batch Enrollment"
        name = getattr(self, "current_student_name", "N/A")

        details_frame = ctk.CTkFrame(self.confirm_inner, fg_color="transparent")
        details_frame.pack(fill="both", expand=True, padx=10, pady=10)
        details_frame.columnconfigure(0, weight=0, minsize=120)
        details_frame.columnconfigure(1, weight=1)

        fields = [
            ("NAME:", name),
            ("LEVEL:", level),
            ("TERM:", term),
        ]

        for idx, (lbl_txt, val_txt) in enumerate(fields):
            lbl = ctk.CTkLabel(details_frame, text=lbl_txt,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="#15165e")
            lbl.grid(row=idx, column=0, sticky="w", pady=4)
            
            val = ctk.CTkLabel(details_frame, text=val_txt,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="#000000")
            val.grid(row=idx, column=1, sticky="w", pady=4)

        ctk.CTkButton(self.right_frame, text="CONFIRM", fg_color="#24894c", hover_color="#1d6f3d", text_color="#ffffff",
                      height=40, corner_radius=8, width=120,
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      command=self.confirm_details).pack(anchor="w", pady=(10, 0))

    def confirm_details(self):
        # Automatically load the Select Subjects card in the right frame!
        self.show_select_subjects_view()

    def show_select_subjects_view(self):
        for w in self.right_frame.winfo_children():
            w.destroy()

        header_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))

        title_col = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(title_col, text="SELECT SUBJECTS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#1e293b").pack(anchor="w")
        ctk.CTkLabel(title_col, text="Uncheck subjects the student is not taking.",
                     font=ctk.CTkFont(family="Inter", size=11),
                     text_color="#64748b").pack(anchor="w")

        self.select_all_var = ctk.BooleanVar(value=False)
        self.select_all_cb = ctk.CTkCheckBox(header_frame, text="SELECT ALL",
                                              variable=self.select_all_var,
                                              font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                              fg_color="#122aff", hover_color="#0b1eb3",
                                              command=self.toggle_select_all_subjects)
        self.select_all_cb.pack(side="right", padx=5)

        self.sub_card, self.sub_inner = self._card(
            self.right_frame, height=self.H_SUBJECTS, scrollable=True, accent_color="#122aff",
        )
        self.sub_card.pack(fill="both", expand=True)

        # Create bottom buttons frame for Save Profile
        btn_right_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        btn_right_frame.pack(anchor="e", pady=(10, 0))

        ctk.CTkButton(btn_right_frame, text="NEXT: CHOOSE BATCHES →", fg_color="#24894c", hover_color="#1d6f3d",
                      text_color="#ffffff", corner_radius=8, height=40, width=220,
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      command=self.show_select_batches_view).pack()

        # Load subjects automatically matching the selection!
        self.load_subjects()

    def show_select_batches_view(self):
        level = self.level_combo.get()
        term = self.term_combo.get()
        if not level or not term:
            messagebox.showwarning("Warning", "Please select Level and Term first.")
            return

        for w in self.right_frame.winfo_children():
            w.destroy()

        header_row = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 4))

        title_col = ctk.CTkFrame(header_row, fg_color="transparent")
        title_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            title_col, text="Select batches",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1e293b",
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_col,
            text="Check only subjects the student will take, then pick Batch A or B.",
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#64748b",
        ).pack(anchor="w")

        preselected = set()
        if getattr(self, "subject_vars", None):
            preselected = {sid for sid, v in self.subject_vars.items() if v.get()}

        self._info_banner(
            self.right_frame,
            "First-come, first-served: each batch holds up to 15 students per term. "
            "Green badge = slots still available.",
        )

        card, inner = self._card(self.right_frame, scrollable=True, accent_color="#122aff")
        card.pack(fill="both", expand=True)

        self.selected_batches = {}
        self.batch_subject_vars = {}
        self._batch_tiles_wraps = {}
        self._batch_row_cards = {}

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            all_subjects = cursor.execute(
                """
                SELECT subjectID, subjectName, pricePerTerm FROM SUBJECT
                WHERE level = ? AND isActive = 1
                ORDER BY subjectName
                """,
                (level,),
            ).fetchall()

            if not all_subjects:
                ctk.CTkLabel(inner, text="No subjects for this grade level.",
                             text_color="#64748b").pack(pady=20)
                conn.close()
                return

            self.batch_select_all_var = ctk.BooleanVar(
                value=len(preselected) == len(all_subjects) and bool(all_subjects),
            )
            ctk.CTkCheckBox(
                header_row, text="Select all subjects",
                variable=self.batch_select_all_var,
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                fg_color="#122aff", hover_color="#0b1eb3",
                command=self.toggle_select_all_batch_subjects,
            ).pack(side="right", padx=4)

            term_price = price_for_level(level)
            price_hint = (
                f"₱{term_price:,.0f} per subject per term "
                f"({level} · 2-hour sessions)"
            )
            ctk.CTkLabel(
                header_row, text=price_hint,
                font=ctk.CTkFont(family="Inter", size=11),
                text_color="#64748b",
            ).pack(side="left", padx=(0, 8))

            for subj in all_subjects:
                subject_id = subj["subjectID"]
                subj_name = subj["subjectName"]
                subj_price = float(subj["pricePerTerm"] or term_price)

                include_var = ctk.BooleanVar(value=subject_id in preselected)
                self.batch_subject_vars[subject_id] = include_var

                row_card = ctk.CTkFrame(
                    inner, fg_color="#ffffff", corner_radius=12,
                    border_width=1, border_color="#cbd5e1",
                )
                row_card.pack(fill="x", padx=2, pady=8)
                self._batch_row_cards[subject_id] = row_card

                row_inner = ctk.CTkFrame(row_card, fg_color="transparent")
                row_inner.pack(fill="x", padx=14, pady=12)

                head = ctk.CTkFrame(row_inner, fg_color="transparent")
                head.pack(fill="x", pady=(0, 4))

                ctk.CTkFrame(head, width=4, height=18, fg_color="#122aff", corner_radius=2).pack(
                    side="left", padx=(0, 8),
                )
                title_col = ctk.CTkFrame(head, fg_color="transparent")
                title_col.pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(
                    title_col, text=subj_name,
                    font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                    text_color="#15165e",
                ).pack(anchor="w")
                ctk.CTkLabel(
                    title_col, text=f"₱{subj_price:,.0f} / term",
                    font=ctk.CTkFont(family="Inter", size=11),
                    text_color="#64748b",
                ).pack(anchor="w")

                ctk.CTkCheckBox(
                    head, text="Enroll in this subject",
                    variable=include_var,
                    font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                    fg_color="#122aff", hover_color="#0b1eb3",
                    command=lambda sid=subject_id: self._on_batch_subject_toggle(sid),
                ).pack(side="right")

                tiles_wrap = ctk.CTkFrame(row_inner, fg_color="transparent")
                self._batch_tiles_wraps[subject_id] = tiles_wrap

                batches = cursor.execute(
                    """
                    SELECT batchID, batchLabel, schedule, capacity,
                           (
                             SELECT COUNT(*)
                             FROM REGISTRATION_DETAIL rd
                             JOIN REGISTRATION r ON r.registrationID = rd.registrationID
                             WHERE rd.batchID = b.batchID AND rd.enrollStatus='Active' AND r.term = ?
                           ) AS enrolled
                    FROM BATCH b
                    WHERE b.subjectID = ? AND b.level = ? AND b.isActive = 1
                    ORDER BY b.batchLabel
                    """,
                    (term, subject_id, level),
                ).fetchall()

                if not batches:
                    ctk.CTkLabel(
                        tiles_wrap, text="No batches available for this subject.",
                        font=ctk.CTkFont(family="Inter", size=12),
                        text_color="#ef4444",
                    ).pack(anchor="w")
                elif not any(int(b["enrolled"]) < int(b["capacity"]) for b in batches):
                    ctk.CTkLabel(
                        tiles_wrap,
                        text="All batches are full for this term.",
                        font=ctk.CTkFont(family="Inter", size=12),
                        text_color="#b45309",
                    ).pack(anchor="w")
                else:
                    self._build_batch_tiles(tiles_wrap, subject_id, batches)

                self._on_batch_subject_toggle(subject_id)

            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load batches: {e}")
            return

        btn_right_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        btn_right_frame.pack(anchor="e", pady=(12, 0))

        ctk.CTkButton(
            btn_right_frame,
            text="CONFIRM ENROLLMENT",
            fg_color="#24894c",
            hover_color="#1d6f3d",
            text_color="#ffffff",
            corner_radius=8,
            height=40,
            width=200,
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            command=self.create_enrollment,
        ).pack()

    def toggle_select_all_subjects(self):
        val = self.select_all_var.get()
        if hasattr(self, 'subject_vars') and self.subject_vars:
            for var in self.subject_vars.values():
                var.set(val)

    def update_select_all_state(self):
        if hasattr(self, 'subject_vars') and self.subject_vars:
            all_checked = all(var.get() for var in self.subject_vars.values())
            self.select_all_var.set(all_checked)

    def _combo(self, parent, values):
        return ModernCombo(parent, values=values)

    def _extract_program(self, group_name):
        for prog in ("STEM", "ABM", "HUMSS"):
            if prog in group_name:
                return prog
        return None

    def load_subjects(self):
        for widget in self.sub_inner.winfo_children():
            widget.destroy()

        level = self.level_combo.get()

        if not level:
            messagebox.showwarning("Warning", "Please select a Level first.")
            self.sub_placeholder = ctk.CTkLabel(self.sub_inner,
                                                 text="Press OK to load subjects.",
                                                 font=ctk.CTkFont(size=13),
                                                 text_color="#888888")
            self.sub_placeholder.pack(expand=True)
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        self.subject_vars = {}

        cursor.execute("""
            SELECT subjectID, subjectName, description
            FROM SUBJECT
            WHERE level = ? AND isActive = 1
            ORDER BY subjectName
        """, (level,))

        subjects = cursor.fetchall()
        conn.close()

        if not subjects:
            ctk.CTkLabel(self.sub_inner, text="No subjects found for this selection.",
                         font=ctk.CTkFont(size=13), text_color="#888888").pack(expand=True)
            return

        grid_frame = ctk.CTkFrame(self.sub_inner, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)

        for idx, s in enumerate(subjects):
            var = ctk.BooleanVar(value=False)
            self.subject_vars[s['subjectID']] = var
            row = idx // 2
            col = idx % 2
            chk = ctk.CTkCheckBox(grid_frame, text=s['subjectName'], variable=var,
                                  font=ctk.CTkFont(family="Inter", size=12),
                                  fg_color="#122aff", hover_color="#0b1eb3",
                                  command=self.update_select_all_state)
            chk.grid(row=row, column=col, sticky="w", pady=4, padx=10)

        if hasattr(self, 'select_all_var'):
            self.select_all_var.set(False)

    def _get_enrolled_subject_ids(self):
        """Subjects the student will enroll in (batch screen or subject screen)."""
        if getattr(self, "batch_subject_vars", None):
            return [sid for sid, var in self.batch_subject_vars.items() if var.get()]
        return [sid for sid, var in self.subject_vars.items() if var.get()]

    def toggle_select_all_batch_subjects(self):
        val = self.batch_select_all_var.get()
        for sid, var in self.batch_subject_vars.items():
            var.set(val)
            self._on_batch_subject_toggle(sid)

    def _on_batch_subject_toggle(self, subject_id):
        """Show/hide batch tiles when user checks or unchecks a subject."""
        include = self.batch_subject_vars[subject_id].get()
        tiles_wrap = self._batch_tiles_wraps.get(subject_id)
        row_card = self._batch_row_cards.get(subject_id)
        if not tiles_wrap or not row_card:
            return
        if include:
            tiles_wrap.pack(fill="x", pady=(4, 0))
            row_card.configure(fg_color="#ffffff", border_color="#cbd5e1")
        else:
            tiles_wrap.pack_forget()
            row_card.configure(fg_color="#f8fafc", border_color="#e2e8f0")
            self.selected_batches.pop(subject_id, None)

    # ==================== Other Functions ====================
    def create_enrollment(self):
        if not getattr(self, 'current_student_id', None):
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        level = self.level_combo.get()
        term = self.term_combo.get()

        if not level or not term:
            messagebox.showwarning("Warning", "Please complete all fields (Level and Term) first!")
            return

        selected_subjects = self._get_enrolled_subject_ids()
        if not selected_subjects:
            messagebox.showwarning(
                "Warning",
                "Check at least one subject to enroll in, then choose a batch for each.",
            )
            return

        if any(sid not in self.selected_batches for sid in selected_subjects):
            messagebox.showwarning("Warning", "Please choose a batch for each selected subject.")
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            staff_id = self.staff_id
            if not staff_id:
                cursor.execute("SELECT staffID FROM STAFF LIMIT 1")
                staff_row = cursor.fetchone()
                staff_id = staff_row['staffID'] if staff_row else 1

            learner_id = generate_learner_id(term)
            group_name = "Batch Enrollment"
            program = None

            cursor.execute("""
                INSERT INTO REGISTRATION
                    (studentID, staffID, learnerID, level, groupName, term, regStatus)
                VALUES (?, ?, ?, ?, ?, ?, 'Active')
            """, (self.current_student_id, staff_id, learner_id,
                  level, group_name, term))

            registration_id = cursor.lastrowid

            cursor.execute("""
                UPDATE STUDENT SET level = ?, program = ? WHERE studentID = ?
            """, (level, program, self.current_student_id))

            # Capacity check: max 15 students per batch per term
            for subject_id in selected_subjects:
                batch_id = self.selected_batches.get(subject_id)
                cursor.execute(
                    """
                    SELECT COUNT(*) AS c
                    FROM REGISTRATION_DETAIL rd
                    JOIN REGISTRATION r ON r.registrationID = rd.registrationID
                    WHERE rd.batchID = ? AND rd.enrollStatus = 'Active' AND r.term = ?
                    """,
                    (batch_id, term),
                )
                enrolled_count = cursor.fetchone()["c"]
                cursor.execute("SELECT capacity, isActive FROM BATCH WHERE batchID = ?", (batch_id,))
                batch_row = cursor.fetchone()
                if not batch_row or int(batch_row["isActive"]) != 1:
                    raise ValueError("Selected batch is not active.")
                if enrolled_count >= int(batch_row["capacity"]):
                    raise ValueError(
                        "One of the selected batches is already full (max 15). "
                        "Enrollment is first-come, first-served — try another batch or term."
                    )

            for subject_id in selected_subjects:
                batch_id = self.selected_batches.get(subject_id)
                sub_row = cursor.execute(
                    "SELECT pricePerTerm FROM SUBJECT WHERE subjectID = ?",
                    (subject_id,),
                ).fetchone()
                fee_amount = (
                    float(sub_row["pricePerTerm"])
                    if sub_row and sub_row["pricePerTerm"] is not None
                    else price_for_level(level)
                )
                cursor.execute("""
                    INSERT INTO REGISTRATION_DETAIL
                        (registrationID, subjectID, batchID, feeAmount, enrollStatus)
                    VALUES (?, ?, ?, ?, 'Active')
                """, (registration_id, subject_id, batch_id, fee_amount))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", f"Registration saved successfully!\nLearner ID: {learner_id}")

            self.search_entry.delete(0, 'end')
            self.show_no_student_selected()
            self.current_student_id = None
            self.current_student_name = None

            self.level_combo.set("")
            self.term_combo.set("")
            self.on_level_changed("")
            self.update_combo_style(self.term_combo)

            self.show_confirmation_placeholder()
            self.subject_vars = {}
            self.selected_batches = {}

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create registration:\n{e}")

    def render_enrollment_list(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.workspace_canvas, text="ENROLLMENT LIST",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(10, 15))

        search_frame = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", height=60)
        search_frame.pack(fill="x", pady=(0, 15))
        search_frame.pack_propagate(False)

        inner = ctk.CTkFrame(search_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)

        search_row = ctk.CTkFrame(inner, fg_color="transparent")
        search_row.pack(fill="x")

        self.class_search_entry = ModernEntry(search_row, placeholder_text="Search grade level or batch…",
                                              height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.class_search_entry.pack(side="left", fill="x", expand=True)
        self.class_search_entry.delete(0, tk.END)

        ctk.CTkButton(search_row, text="SEARCH", width=130, height=40,
                      fg_color="#122aff", hover_color="#0b1eb3", corner_radius=8,
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      command=self.search_enrollment_by_class).pack(side="right", padx=(10, 0))

        ctk.CTkButton(inner, text="Show All Enrollments", width=180, height=35,
                      fg_color="#374151", hover_color="#272f3a", corner_radius=8,
                      font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                      command=self.load_all_enrollments).pack(anchor="w", pady=(5, 0))

        table_card = ctk.CTkFrame(self.workspace_canvas, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        table_card.pack(fill="both", expand=True, padx=5)

        self.tree_frame = ctk.CTkFrame(table_card, fg_color="transparent", corner_radius=8)
        self.tree_frame.pack(fill="both", expand=True, padx=15, pady=12)
        self.tree_frame.bind("<Configure>", self._fit_enrollment_tree_to_card)

        import tkinter.ttk as ttk
        columns = ("Learner ID", "Student Name", "Grade Level", "Batch", "Term", "Staff", "Status")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Enrollment.Treeview.Heading",
            background="#15165e",
            foreground="#ffffff",
            font=("Inter", 11, "bold"),
            bordercolor="#15165e",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Enrollment.Treeview.Heading",
            background=[("active", "#1c1d7c")],
            foreground=[("active", "#ffffff")],
        )
        style.configure(
            "Enrollment.Treeview",
            font=("Inter", 11),
            rowheight=36,
            fieldbackground="#ffffff",
            background="#ffffff",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Enrollment.Treeview",
            background=[("selected", "#122aff")],
            foreground=[("selected", "#ffffff")],
        )

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            height=12,
            style="Enrollment.Treeview",
        )

        self.tree.tag_configure("evenrow", background="#f8fafc")
        self.tree.tag_configure("oddrow", background="#ffffff")

        self.class_search_entry.bind("<KeyRelease>", lambda e: self.search_enrollment_by_class())

        col_widths = [120, 200, 100, 90, 90, 140, 80]
        col_anchors = ["center", "w", "center", "center", "center", "center", "center"]
        for col, width, anchor in zip(columns, col_widths, col_anchors):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor, minwidth=width)

        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.load_all_enrollments()
        self.after_idle(self._fit_enrollment_tree_to_card)

    def _fit_enrollment_tree_to_card(self, event=None):
        """Size Treeview row count to fill the white card without squashing row height."""
        if not hasattr(self, "tree") or not hasattr(self, "tree_frame"):
            return
        self.tree_frame.update_idletasks()
        frame_h = self.tree_frame.winfo_height()
        if frame_h < 80:
            return
        row_h = 36
        heading_h = 32
        rows = max((frame_h - heading_h) // row_h, len(self.tree.get_children()), 8)
        rows = min(rows, 40)
        if int(self.tree.cget("height")) != rows:
            self.tree.configure(height=rows)

    def _format_batch_labels(self, batch_labels):
        """Comma-separated batch labels from DB -> 'Batch A, Batch B' or —."""
        if not batch_labels:
            return "—"
        parts = [b.strip() for b in str(batch_labels).split(",") if b.strip()]
        if not parts:
            return "—"
        return ", ".join(f"Batch {p}" if not p.upper().startswith("BATCH") else p for p in parts)

    def _insert_enrollment_rows(self, rows):
        for idx, row in enumerate(rows):
            full_name = f"{row['studLname']}, {row['studFname']} {row['studMname'] or ''}".strip()
            staff_name = f"{row['staffFname']} {row['staffLname']}" if row['staffFname'] else "—"
            tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                "end",
                values=(
                    row["learnerID"] or "—",
                    full_name,
                    row["level"] or "—",
                    self._format_batch_labels(row["batchLabels"] if row["batchLabels"] else None),
                    row["term"],
                    staff_name,
                    row["regStatus"],
                ),
                tags=(tag,),
            )
        self.after_idle(self._fit_enrollment_tree_to_card)

    def _enrollment_list_query(self, where_clause="", params=()):
        """Shared SELECT for enrollment list with aggregated batch labels."""
        return f"""
            SELECT r.learnerID, r.level, r.term, r.regStatus,
                   s.studFname, s.studLname, s.studMname,
                   st.staffFname, st.staffLname,
                   (
                     SELECT GROUP_CONCAT(DISTINCT b.batchLabel)
                     FROM REGISTRATION_DETAIL rd
                     JOIN BATCH b ON b.batchID = rd.batchID
                     WHERE rd.registrationID = r.registrationID
                       AND rd.enrollStatus = 'Active'
                   ) AS batchLabels
            FROM REGISTRATION r
            JOIN STUDENT s ON r.studentID = s.studentID
            LEFT JOIN STAFF st ON r.staffID = st.staffID
            {where_clause}
            ORDER BY r.registrationID DESC
        """

    def load_all_enrollments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute(self._enrollment_list_query())
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()

            self._insert_enrollment_rows(rows)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load enrollment list:\n{e}")

    def search_enrollment_by_class(self):
        keyword = self.class_search_entry.get().strip()
        if not keyword:
            self.load_all_enrollments()
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            like = f"%{keyword}%"
            cursor.execute(
                self._enrollment_list_query(
                    """
                WHERE UPPER(r.level) LIKE UPPER(?)
                   OR EXISTS (
                        SELECT 1
                        FROM REGISTRATION_DETAIL rd
                        JOIN BATCH b ON b.batchID = rd.batchID
                        WHERE rd.registrationID = r.registrationID
                          AND rd.enrollStatus = 'Active'
                          AND UPPER(b.batchLabel) LIKE UPPER(?)
                   )
                """
                ),
                (like, like),
            )
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()

            self._insert_enrollment_rows(rows)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_level_changed(self, choice):
        if not choice:
            apply_term_combo_for_level(self.term_combo, "")
        else:
            apply_term_combo_for_level(self.term_combo, choice)

        self.update_combo_style(self.level_combo)
        self.update_combo_style(self.term_combo)

    def on_term_changed(self, choice):
        self.update_combo_style(self.term_combo)

    def update_combo_style(self, combo):
        val = combo.get().strip()
        if val:
            combo.configure(text_color="black", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
        else:
            combo.configure(text_color="#777777", font=ctk.CTkFont(family="Inter", size=13, weight="normal"))

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()