import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime
from utils.modern_combo import ModernCombo
from utils.term_options import apply_term_combo_for_level
from utils.term_options import apply_term_combo_for_level


class BatchPickerCombo(ModernCombo):
    def __init__(self, master, on_open_popup, **kwargs):
        kwargs.setdefault("values", [""])
        super().__init__(master, **kwargs)
        self._on_open_popup = on_open_popup
        self.set("")

    def _open_dropdown_menu(self):
        if self._on_open_popup:
            self._on_open_popup()


class AttendanceSavedPopup(ctk.CTkToplevel):
    def __init__(self, parent, saved_count, att_date, skipped_count=0):
        super().__init__(parent)
        self.title("Success")
        self.geometry("400x240")
        self.resizable(False, False)
        self.configure(fg_color="#15165e")
        self.transient(parent)
        
        self.lift()
        self.attributes("-topmost", True)
        self.grab_set()

        main_frame = ctk.CTkFrame(self, fg_color="#15165e", corner_radius=0)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        icon_label = ctk.CTkLabel(
            main_frame,
            text="✓",
            font=ctk.CTkFont(family="Inter", size=48, weight="bold"),
            text_color="#00bf63"
        )
        icon_label.pack(pady=(5, 5))

        msg_label = ctk.CTkLabel(
            main_frame,
            text="Attendance Recorded",
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#ffffff"
        )
        msg_label.pack(pady=(5, 5))

        details_text = f"Attendance saved for {saved_count} student(s) on {att_date}."
        if skipped_count > 0:
            details_text += f"\n({skipped_count} student(s) skipped/not enrolled)"
            
        details_label = ctk.CTkLabel(
            main_frame,
            text=details_text,
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#cbd5e1",
            wraplength=340
        )
        details_label.pack(pady=(0, 15))

        btn = ctk.CTkButton(
            main_frame,
            text="OK",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            width=120,
            height=35,
            fg_color="#122aff",
            hover_color="#0b1eb3",
            text_color="#ffffff",
            corner_radius=8,
            command=self.destroy
        )
        btn.pack()

        # Center relative to parent
        self.update_idletasks()
        try:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_w = parent.winfo_width()
            parent_h = parent.winfo_height()
            x = parent_x + (parent_w - 400) // 2
            y = parent_y + (parent_h - 240) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass


class RecordAttendance(ctk.CTkFrame):
    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user_role = user_role
        self.tutor_id = user_id

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        # Roster UI state keyed by detailID (string)
        self.student_row_widgets = {}
        self.student_row_frames = {}
        self.attendance_vars = {}
        self.attendance_times = {}
        self.roster_rows = []          # list[dict] for current roster
        self._batch_display_to_row = {}  # display -> {batchID, level, subjCode, batchLabel, schedule}
        self._selected_batch = None    # dict from _batch_display_to_row
        self._selected_subject_code = None  # subjCode chosen via Subject picker
        self._selected_history_subject_code = None # history subject chosen
        self._h_batch_display_to_row = {}  # history batch mapping (display -> {batchID, ...})
        self._last_record_filters = {}  # saved filters from Record tab (for History tab sync)
        self._history_stats_frame = None

        self.create_ui()

    def _combo(self, parent, values, **kwargs):
        kwargs.setdefault("height", 30)
        return ModernCombo(parent, values=values, **kwargs)

    def _batch_combo(self, parent, is_history=False, **kwargs):
        kwargs.setdefault("height", 30)
        def open_popup():
            self.open_batch_popup(is_history)
        return BatchPickerCombo(parent, on_open_popup=open_popup, **kwargs)

    def _subject_combo(self, parent, **kwargs):
        kwargs.setdefault("height", 30)
        def open_popup():
            self.open_subject_popup()
        return BatchPickerCombo(parent, on_open_popup=open_popup, **kwargs)

    def _subject_combo_history(self, parent, **kwargs):
        kwargs.setdefault("height", 30)
        def open_popup():
            self.open_subject_popup_history()
        return BatchPickerCombo(parent, on_open_popup=open_popup, **kwargs)

    def _card_frame(self, parent, height=None, inner_pady=8, accent_pady=12):
        kw = {"height": height} if height else {}
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", **kw)
        
        accent_container = ctk.CTkFrame(card, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=accent_pady)
        
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=inner_pady)
        return card, inner

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

        ctk.CTkLabel(top_bar, text="Record Attendance",
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

        # Tab pill switcher
        tab_selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(12, 0))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1", width=380, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.record_tab_btn = ctk.CTkButton(
            tab_pill, text="Record Attendance",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#122aff", text_color="#ffffff",
            corner_radius=19, height=38, width=185,
            command=lambda: self.switch_tab("record"))
        self.record_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.history_tab_btn = ctk.CTkButton(
            tab_pill, text="Attendance History",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="transparent", text_color="#374151",
            corner_radius=19, height=38, width=185,
            command=lambda: self.switch_tab("history"))
        self.history_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        # Workspace container
        self.workspace_canvas = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_canvas.pack(fill="both", expand=True, padx=40, pady=(10, 20))

        self.render_record_tab()

    def switch_tab(self, tab):
        if tab == "record":
            self.record_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.history_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.render_record_tab()
        else:
            self.record_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.history_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.render_history_tab()
            # Keep History dropdowns synchronized with Record dropdowns automatically.
            self._sync_history_filters_from_record()
    def render_record_tab(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        split_body = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # Left panel
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=420)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)
        left_panel.grid_propagate(False)

        def section_label(parent, text, row):
            lbl = ctk.CTkLabel(parent, text=text,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="black")
            lbl.grid(row=row, column=0, sticky="w", pady=(4, 1))
            return lbl

        # LEVEL Dropdown
        self.class_lbl = section_label(left_panel, "LEVEL", 0)
        self.class_card, class_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        self.class_card.grid(row=1, column=0, sticky="ew")
        self.class_card.pack_propagate(False)
        self.class_combo = self._combo(class_inner, [f"Grade {i}" for i in range(1, 13)], command=self.on_class_changed)
        self.class_combo.pack(fill="x")

        # TERM Dropdown
        self.term_label_widget = section_label(left_panel, "TERM", 2)
        self.term_card, term_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        self.term_card.grid(row=3, column=0, sticky="ew")
        self.term_card.pack_propagate(False)
        self.term_combo = self._combo(term_inner, [], command=self.on_term_changed)
        self.term_combo.pack(fill="x")

        # SUBJECT picker card
        self.subject_lbl = section_label(left_panel, "SUBJECT", 4)
        self.subject_card, subject_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        self.subject_card.grid(row=5, column=0, sticky="ew")
        self.subject_card.pack_propagate(False)
        self.subject_combo = self._subject_combo(subject_inner)
        self.subject_combo.pack(fill="x")

        # BATCH Dropdown (batch-first attendance)
        self.batch_lbl = section_label(left_panel, "BATCH", 6)
        self.batch_card, batch_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        self.batch_card.grid(row=7, column=0, sticky="ew")
        self.batch_card.pack_propagate(False)
        self.batch_combo = self._batch_combo(batch_inner, is_history=False, command=self.on_batch_changed)
        self.batch_combo.pack(fill="x")

        # OK button trigger
        self.ok_btn = ctk.CTkButton(left_panel, text="OK",
                                    font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                    height=34, corner_radius=8,
                                    fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                                    command=self.on_ok_clicked)
        self.ok_btn.grid(row=8, column=0, sticky="ew", pady=(10, 0))

        # CLASS DETAILS Card
        self.details_lbl = section_label(left_panel, "CLASS DETAILS", 9)
        self.details_card, self.details_inner = self._card_frame(left_panel, inner_pady=6, accent_pady=6)
        self.details_card.grid(row=10, column=0, sticky="nsew", pady=(0, 0))

        details_frame = ctk.CTkFrame(self.details_inner, fg_color="transparent")
        details_frame.pack(fill="both", expand=True)
        details_frame.columnconfigure(0, weight=0, minsize=110)
        details_frame.columnconfigure(1, weight=1)

        self.class_detail_labels = {}
        for i, (label, val) in enumerate([
            ("Level", "—"),
            ("Term", "—"),
            ("Subject", "—"),
            ("Batch", "—"),
            ("Schedule", "—"),
            ("Time", "—"),
        ]):
            ctk.CTkLabel(
                details_frame, text=f"{label}:",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                text_color="#15165e",
            ).grid(row=i, column=0, sticky="w", pady=2)

            val_lbl = ctk.CTkLabel(
                details_frame, text=val,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#1e293b",
            )
            val_lbl.grid(row=i, column=1, sticky="w", padx=(15, 0), pady=2)
            self.class_detail_labels[label] = val_lbl

        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(10, weight=1)

        # Right panel (roster)
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=480)
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        # Header for Right Panel containing STUDENTS label on left and military live time on right
        right_header = ctk.CTkFrame(right_panel, fg_color="transparent")
        right_header.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(right_header, text="STUDENTS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="black").pack(side="left")

        self.live_time_label = ctk.CTkLabel(right_header, text="",
                                             font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                             text_color="black")
        self.live_time_label.pack(side="right")
        self.update_clock()

        sheet_outer = ctk.CTkFrame(right_panel, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1")
        sheet_outer.pack(fill="both", expand=True)

        self.roster_scroll = ctk.CTkScrollableFrame(sheet_outer, fg_color="transparent", corner_radius=8)
        self.roster_scroll.pack(fill="both", expand=True, padx=15, pady=12)

        # Roster Header
        self.hdr = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        self.hdr.pack(fill="x", pady=(0, 6))

        self.hdr.grid_columnconfigure(0, minsize=35)   # index
        self.hdr.grid_columnconfigure(1, minsize=35)   # P
        self.hdr.grid_columnconfigure(2, minsize=35)   # A
        self.hdr.grid_columnconfigure(3, minsize=35)   # L
        self.hdr.grid_columnconfigure(4, weight=1)     # Last Name
        self.hdr.grid_columnconfigure(5, weight=1)     # First Name
        self.hdr.grid_columnconfigure(6, weight=1, minsize=65)  # Middle Name
        self.hdr.grid_columnconfigure(7, minsize=120)  # Status (fixed)
        self.hdr.grid_columnconfigure(8, minsize=85)   # Time (fixed)

        ctk.CTkLabel(self.hdr, text="#", font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color="#475569", width=35).grid(row=0, column=0, padx=2)
        ctk.CTkLabel(self.hdr, text="P", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#00bf63", width=35).grid(row=0, column=1, padx=2)
        ctk.CTkLabel(self.hdr, text="A", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#e20000", width=35).grid(row=0, column=2, padx=2)
        ctk.CTkLabel(self.hdr, text="L", font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color="#122aff", width=35).grid(row=0, column=3, padx=2)

        headers = [
            ("LAST NAME", 4),
            ("FIRST NAME", 5),
            ("MIDDLE NAME", 6),
            ("STATUS", 7),
            ("TIME", 8),
        ]

        for text, col in headers:
            ctk.CTkLabel(self.hdr, text=text,
                         font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                         text_color="#475569").grid(row=0, column=col, sticky="ew" if col > 6 else "w", padx=10)

        self.roster_rows_frame = ctk.CTkFrame(self.roster_scroll, fg_color="transparent")
        self.roster_rows_frame.pack(fill="x")

        # Bottom Save Attendance button
        ctk.CTkButton(right_panel, text="SAVE ATTENDANCE",
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      height=45, corner_radius=8,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.save_attendance
                      ).pack(fill="x", pady=(12, 0))

        # Initialise fields to Empty and Readonly
        self.class_combo.set("")
        self.term_combo.set("")
        self.subject_combo.set("")
        self.batch_combo.set("")
        self._selected_subject_code = None

        self.update_combo_style(self.class_combo)
        self.update_combo_style(self.term_combo)
        self.update_combo_style(self.subject_combo)
        self.update_combo_style(self.batch_combo)

        # Render clean initial empty states
        self.show_roster_placeholder()

    def update_combo_style(self, combo):
        val = combo.get().strip()
        if val:
            combo.configure(text_color="black", font=ctk.CTkFont(family="Inter", size=13, weight="bold"))
        else:
            combo.configure(text_color="#777777", font=ctk.CTkFont(family="Inter", size=13, weight="normal"))

    def load_class_options(self):
        # Deprecated because class choices are now cleanly pre-loaded statically Grade 1 - 12
        pass

    def on_class_changed(self, choice):
        self.update_combo_style(self.class_combo)
        if not choice:
            self.term_combo.configure(values=[])
            self.term_combo.set("")
            self.subject_combo.set("")
            self.batch_combo.set("")
            self._batch_display_to_row = {}
            self._selected_batch = None
            self._selected_subject_code = None
            self.update_combo_style(self.term_combo)
            self.update_combo_style(self.subject_combo)
            self.update_combo_style(self.batch_combo)
            return

        apply_term_combo_for_level(self.term_combo, choice)
        # Prevent auto-selecting Term 1; keep term empty until user chooses.
        self.term_combo.set("")
        self._batch_display_to_row = {}
        self._selected_batch = None
        self._selected_subject_code = None
        self.subject_combo.set("")
        self.batch_combo.set("")
        self.update_combo_style(self.term_combo)
        self.update_combo_style(self.subject_combo)
        self.update_combo_style(self.batch_combo)

    def on_term_changed(self, choice):
        self.update_combo_style(self.term_combo)
        # Reset subject and batch when term changes
        self._selected_subject_code = None
        self.subject_combo.set("")
        self.update_combo_style(self.subject_combo)
        self.batch_combo.set("")
        self.update_combo_style(self.batch_combo)
        self.load_batches_for_filters()

    def on_batch_changed(self, choice):
        self.update_combo_style(self.batch_combo)
        # If _selected_batch was already set by the popup tile click, keep it
        if self._selected_batch:
            existing_short = f"Batch {self._selected_batch.get('batchLabel')} | {self._selected_batch.get('schedule')}"
            if existing_short == choice and (not self._selected_subject_code or self._selected_batch.get('subjCode') == self._selected_subject_code):
                return  # already correct, don't overwrite
        # Fallback: search by short format (e.g. when combo value changed externally)
        matched = None
        for val in self._batch_display_to_row.values():
            short_fmt = f"Batch {val.get('batchLabel')} | {val.get('schedule')}"
            if short_fmt == choice:
                if self._selected_subject_code and val.get("subjCode") == self._selected_subject_code:
                    matched = val
                    break
                elif not self._selected_subject_code:
                    matched = val
                    break
        self._selected_batch = matched

    def load_batches_for_filters(self):
        # I load batches for the selected level and term. Tutor accounts only see their own assigned batches.
        level = self.class_combo.get().strip()
        term = self.term_combo.get().strip()
        self._batch_display_to_row = {}
        self._selected_batch = None

        if not level or not term:
            self.batch_combo.configure(values=[])
            self.batch_combo.set("")
            self.update_combo_style(self.batch_combo)
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            params = [level]
            tutor_filter = ""
            if str(self.user_role).lower().startswith("tutor") and self.tutor_id:
                tutor_filter = " AND (b.tutorID = ?)"
                params.append(self.tutor_id)

            cur.execute(
                f"""
                SELECT b.batchID, b.batchLabel, b.schedule, b.level,
                       s.subjCode
                FROM BATCH b
                JOIN SUBJECT s ON s.subjectID = b.subjectID
                WHERE b.isActive = 1
                  AND b.level = ?
                  {tutor_filter}
                ORDER BY s.subjCode, b.batchLabel
                """,
                tuple(params),
            )
            rows = cur.fetchall()
            conn.close()

            values = []
            for r in rows:
                disp = f"{r['subjCode']} — Batch {r['batchLabel']} — {r['schedule']}"
                values.append(disp)
                self._batch_display_to_row[disp] = {
                    "batchID": r["batchID"],
                    "batchLabel": r["batchLabel"],
                    "schedule": r["schedule"],
                    "level": r["level"],
                    "subjCode": r["subjCode"],
                    "term": term,
                }

            self.batch_combo.configure(values=values)
            # Keep dropdown empty until user clicks/selects one.
            self.batch_combo.set("")
            self._selected_batch = None
            self.update_combo_style(self.batch_combo)
        except Exception:
            # keep UI responsive; any errors will surface on OK when loading roster
            self.batch_combo.configure(values=[])
            self.batch_combo.set("")
            self.update_combo_style(self.batch_combo)

    def _load_history_batches(self, level: str, term: str):
        # I populate the Attendance History batch dropdown for the selected level and term.
        self._h_batch_display_to_row = {}
        self.h_batch.configure(values=[])
        self.h_batch.set("")
        self.update_combo_style(self.h_batch)

        if not level or not term:
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            params = [level]
            tutor_filter = ""
            if str(self.user_role).lower().startswith("tutor") and self.tutor_id:
                tutor_filter = " AND (b.tutorID = ?)"
                params.append(self.tutor_id)

            cur.execute(
                f"""
                SELECT b.batchID, b.batchLabel, b.schedule, s.subjCode
                FROM BATCH b
                JOIN SUBJECT s ON s.subjectID = b.subjectID
                WHERE b.isActive = 1
                  AND b.level = ?
                  {tutor_filter}
                ORDER BY s.subjCode, b.batchLabel
                """,
                tuple(params),
            )
            rows = [dict(r) for r in cur.fetchall()]
            conn.close()

            values = []
            for r in rows:
                disp = f"{r['subjCode']} — Batch {r['batchLabel']} — {r['schedule']}"
                values.append(disp)
                self._h_batch_display_to_row[disp] = {
                    "batchID": r["batchID"],
                    "batchLabel": r["batchLabel"],
                    "schedule": r["schedule"],
                    "subjCode": r["subjCode"],
                    "level": level,
                    "term": term,
                }

            self.h_batch.configure(values=values)
            # Keep dropdown empty until either user selects or Record tab syncs it.
            self.h_batch.set("")
            self.update_combo_style(self.h_batch)
        except Exception:
            self._h_batch_display_to_row = {}
            self.h_batch.configure(values=[])
            self.h_batch.set("")
            self.update_combo_style(self.h_batch)

    def open_subject_popup(self):
        # I open a popup window showing all available subjects for the selected level.
        import tkinter as tk_native
        level = self.class_combo.get().strip()
        term = self.term_combo.get().strip()

        if not level:
            messagebox.showinfo("Select Level", "Please select a Level first.")
            return
        if not term:
            messagebox.showinfo("Select Term", "Please select a Term first.")
            return

        # Load subjects for selected level
        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT s.subjCode, s.subjectName
                FROM SUBJECT s
                WHERE s.level = ? AND s.isActive = 1
                ORDER BY s.subjCode
            """, (level,))
            subjects = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load subjects:\n{e}")
            return

        if not subjects:
            messagebox.showinfo("No Subjects", f"No subjects found for {level}.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Select Subject")
        popup.geometry("900x640")
        popup.resizable(True, True)
        popup.minsize(800, 500)
        popup.configure(fg_color="#e4e4e4")
        popup.transient(self.winfo_toplevel())

        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        popup.geometry(f"900x640+{(screen_w - 900) // 2}+{(screen_h - 640) // 2}")

        top_bar = ctk.CTkFrame(popup, height=60, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text=f"SELECT A SUBJECT  —  {level}",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=20, pady=15)

        scroll_outer = tk_native.Frame(popup, bg="#e4e4e4")
        scroll_outer.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        canvas = tk_native.Canvas(scroll_outer, bg="#e4e4e4", highlightthickness=0)
        scrollbar = tk_native.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
        scroll_inner = tk_native.Frame(canvas, bg="#e4e4e4")
        scroll_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_inner, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner", width=e.width))
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)) if event.delta else (-1 if event.num == 4 else 1), "units")
        canvas.bind_all("<Button-4>", _wheel)
        canvas.bind_all("<Button-5>", _wheel)
        popup.bind("<Destroy>", lambda e: (canvas.unbind_all("<Button-4>"), canvas.unbind_all("<Button-5>")))

        # Build subject tiles in 2-col grid
        tiles_wrap = tk_native.Frame(scroll_inner, bg="#e4e4e4")
        tiles_wrap.pack(fill="x", padx=4, pady=4)
        tiles_wrap.columnconfigure(0, weight=1)
        tiles_wrap.columnconfigure(1, weight=1)

        for idx, subj_row in enumerate(subjects):
            code = subj_row["subjCode"]
            name = subj_row["subjectName"]
            col = idx % 2
            row = idx // 2

            tile = tk_native.Frame(tiles_wrap, bg="#ffffff", bd=1, relief="solid",
                                   highlightthickness=1, highlightbackground="#e2e8f0",
                                   highlightcolor="#122aff")
            tile.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

            lbl_code = tk_native.Label(tile, text=code,
                                       font=("Inter", 12, "bold"), fg="#15165e", bg="#ffffff", anchor="w")
            lbl_code.pack(fill="x", padx=10, pady=(8, 0))

            lbl_name = tk_native.Label(tile, text=name,
                                       font=("Inter", 10), fg="#64748b", bg="#ffffff", anchor="w")
            lbl_name.pack(fill="x", padx=10, pady=(0, 8))

            def on_click(event, c=code):
                self._selected_subject_code = c
                self.subject_combo.set(c)
                self.update_combo_style(self.subject_combo)
                # Reset batch when subject changes
                self.batch_combo.set("")
                self.update_combo_style(self.batch_combo)
                self._selected_batch = None
                popup.destroy()

            def on_enter(event, t=tile, l1=lbl_code, l2=lbl_name):
                t.configure(bg="#eef2ff", highlightbackground="#122aff")
                l1.configure(bg="#eef2ff")
                l2.configure(bg="#eef2ff")

            def on_leave(event, t=tile, l1=lbl_code, l2=lbl_name):
                t.configure(bg="#ffffff", highlightbackground="#e2e8f0")
                l1.configure(bg="#ffffff")
                l2.configure(bg="#ffffff")

            for w in (tile, lbl_code, lbl_name):
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.configure(cursor="hand2")

        btn_frame = tk_native.Frame(popup, bg="#e4e4e4")
        btn_frame.pack(fill="x", pady=(5, 12))
        ctk.CTkButton(btn_frame, text="CLOSE",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      fg_color="#374151", hover_color="#1f2937", text_color="#ffffff",
                      width=160, height=38, corner_radius=8,
                      command=popup.destroy).pack(anchor="center")

        popup.update_idletasks()
        try:
            popup.grab_set()
        except Exception:
            pass

    def open_subject_popup_history(self):
        # I open a popup window showing all subjects for the selected history level.
        import tkinter as tk_native
        level = self.h_class.get().strip()
        term = self.h_term.get().strip()

        if not level:
            messagebox.showinfo("Select Level", "Please select a Level first.")
            return
        if not term:
            messagebox.showinfo("Select Term", "Please select a Term first.")
            return

        # Load subjects for selected level
        try:
            conn = database.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT s.subjCode, s.subjectName
                FROM SUBJECT s
                WHERE s.level = ? AND s.isActive = 1
                ORDER BY s.subjCode
            """, (level,))
            subjects = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Could not load subjects:\n{e}")
            return

        if not subjects:
            messagebox.showinfo("No Subjects", f"No subjects found for {level}.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Select Subject")
        popup.geometry("900x640")
        popup.resizable(True, True)
        popup.minsize(800, 500)
        popup.configure(fg_color="#e4e4e4")
        popup.transient(self.winfo_toplevel())

        screen_w = popup.winfo_screenwidth()
        screen_h = popup.winfo_screenheight()
        popup.geometry(f"900x640+{(screen_w - 900) // 2}+{(screen_h - 640) // 2}")

        top_bar = ctk.CTkFrame(popup, height=60, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text=f"SELECT A SUBJECT  —  {level}",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=20, pady=15)

        scroll_outer = tk_native.Frame(popup, bg="#e4e4e4")
        scroll_outer.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        canvas = tk_native.Canvas(scroll_outer, bg="#e4e4e4", highlightthickness=0)
        scrollbar = tk_native.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
        scroll_inner = tk_native.Frame(canvas, bg="#e4e4e4")
        scroll_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_inner, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("inner", width=e.width))
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)) if event.delta else (-1 if event.num == 4 else 1), "units")
        canvas.bind_all("<Button-4>", _wheel)
        canvas.bind_all("<Button-5>", _wheel)
        popup.bind("<Destroy>", lambda e: (canvas.unbind_all("<Button-4>"), canvas.unbind_all("<Button-5>")))

        # Build subject tiles in 2-col grid
        tiles_wrap = tk_native.Frame(scroll_inner, bg="#e4e4e4")
        tiles_wrap.pack(fill="x", padx=4, pady=4)
        tiles_wrap.columnconfigure(0, weight=1)
        tiles_wrap.columnconfigure(1, weight=1)

        for idx, subj_row in enumerate(subjects):
            code = subj_row["subjCode"]
            name = subj_row["subjectName"]
            col = idx % 2
            row = idx // 2

            tile = tk_native.Frame(tiles_wrap, bg="#ffffff", bd=1, relief="solid",
                                   highlightthickness=1, highlightbackground="#e2e8f0",
                                   highlightcolor="#122aff")
            tile.grid(row=row, column=col, sticky="nsew", padx=4, pady=4)

            lbl_code = tk_native.Label(tile, text=code,
                                       font=("Inter", 12, "bold"), fg="#15165e", bg="#ffffff", anchor="w")
            lbl_code.pack(fill="x", padx=10, pady=(8, 0))

            lbl_name = tk_native.Label(tile, text=name,
                                       font=("Inter", 10), fg="#64748b", bg="#ffffff", anchor="w")
            lbl_name.pack(fill="x", padx=10, pady=(0, 8))

            def on_click(event, c=code):
                self._selected_history_subject_code = c
                self.h_subject.set(c)
                self.update_combo_style(self.h_subject)
                # Reset history batch when subject changes
                self.h_batch.set("")
                self.update_combo_style(self.h_batch)
                self._selected_history_batch = None
                popup.destroy()

            def on_enter(event, t=tile, l1=lbl_code, l2=lbl_name):
                t.configure(bg="#eef2ff", highlightbackground="#122aff")
                l1.configure(bg="#eef2ff")
                l2.configure(bg="#eef2ff")

            def on_leave(event, t=tile, l1=lbl_code, l2=lbl_name):
                t.configure(bg="#ffffff", highlightbackground="#e2e8f0")
                l1.configure(bg="#ffffff")
                l2.configure(bg="#ffffff")

            for w in (tile, lbl_code, lbl_name):
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                w.configure(cursor="hand2")

        btn_frame = tk_native.Frame(popup, bg="#e4e4e4")
        btn_frame.pack(fill="x", pady=(5, 12))
        close_btn = ctk.CTkButton(btn_frame, text="CLOSE",
                                  font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                  fg_color="#374151", hover_color="#1f2937", text_color="#ffffff",
                                  width=160, height=38, corner_radius=8,
                                  command=popup.destroy)
        close_btn.pack(anchor="center")

        popup.update_idletasks()
        try:
            popup.grab_set()
        except Exception:
            pass

    def open_batch_popup(self, is_history=False):
        import tkinter as tk_native
        level = self.h_class.get().strip() if is_history else self.class_combo.get().strip()
        term = self.h_term.get().strip() if is_history else self.term_combo.get().strip()

        if not level or not term:
            messagebox.showinfo("Select Filters", "Please select Level and Term first.")
            return

        selected_subj = self._selected_history_subject_code if is_history else self._selected_subject_code
        if not selected_subj:
            messagebox.showinfo("Select Subject", "Please select a Subject first.")
            return

        full_mapping = self._h_batch_display_to_row if is_history else self._batch_display_to_row
        if not full_mapping:
            messagebox.showinfo("No Batches", "No active batches found for the selected Level and Term.")
            return

        # Filter mapping by selected subject
        batch_mapping = {k: v for k, v in full_mapping.items()
                         if v.get("subjCode") == selected_subj}
        if not batch_mapping:
            messagebox.showinfo("No Batches", f"No batches found for subject '{selected_subj}'.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Select Batch")
        popup.geometry("900x640")
        popup.resizable(True, True)
        popup.minsize(800, 500)
        popup.configure(fg_color="#e4e4e4")
        popup.transient(self.winfo_toplevel())

        # Center popup on screen BEFORE rendering content
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 900) // 2
        y = (screen_height - 640) // 2
        popup.geometry(f"900x640+{x}+{y}")

        # Top Bar (only heavy widget — just 1 frame + 1 label)
        top_bar = ctk.CTkFrame(popup, height=60, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar, text="SELECT A BATCH",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=20, pady=15)

        # Lightweight scrollable area using plain tkinter
        scroll_outer = tk_native.Frame(popup, bg="#e4e4e4")
        scroll_outer.pack(fill="both", expand=True, padx=20, pady=(10, 5))

        canvas = tk_native.Canvas(scroll_outer, bg="#e4e4e4", highlightthickness=0)
        scrollbar = tk_native.Scrollbar(scroll_outer, orient="vertical", command=canvas.yview)
        scroll_inner = tk_native.Frame(canvas, bg="#e4e4e4")

        scroll_inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_inner, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Make scroll_inner fill canvas width
        def _resize_inner(event):
            canvas.itemconfig("inner", width=event.width)
        canvas.bind("<Configure>", _resize_inner)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)) if event.delta else (-1 if event.num == 4 else 1), "units")
        canvas.bind_all("<Button-4>", _on_mousewheel)
        canvas.bind_all("<Button-5>", _on_mousewheel)
        popup.bind("<Destroy>", lambda e: (canvas.unbind_all("<Button-4>"), canvas.unbind_all("<Button-5>")))

        # Organize by subjCode
        organized = {}
        for disp, data in batch_mapping.items():
            subj = data["subjCode"]
            if subj not in organized:
                organized[subj] = []
            organized[subj].append((disp, data))

        # Build tiles with PLAIN tkinter widgets (fast!)
        for subj, batches in organized.items():
            subj_frame = tk_native.Frame(scroll_inner, bg="#ffffff", bd=1, relief="solid", padx=0, pady=0)
            subj_frame.pack(fill="x", pady=(0, 10), padx=2)

            # Accent bar + content
            accent = tk_native.Frame(subj_frame, bg="#15165e", width=5)
            accent.pack(side="left", fill="y", padx=(8, 0), pady=8)

            inner = tk_native.Frame(subj_frame, bg="#ffffff")
            inner.pack(fill="both", expand=True, padx=10, pady=8)

            tk_native.Label(inner, text=subj, font=("Inter", 12, "bold"),
                     fg="#15165e", bg="#ffffff", anchor="w").pack(fill="x", pady=(0, 6))

            tiles_wrap = tk_native.Frame(inner, bg="#ffffff")
            tiles_wrap.pack(fill="x")
            tiles_wrap.columnconfigure(0, weight=1)
            tiles_wrap.columnconfigure(1, weight=1)

            for idx, (disp, data) in enumerate(batches):
                col = idx % 2
                row = idx // 2

                tile = tk_native.Frame(tiles_wrap, bg="#f8fafc", bd=1, relief="solid",
                                highlightthickness=1, highlightbackground="#e2e8f0",
                                highlightcolor="#122aff")
                tile.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)

                lbl1 = tk_native.Label(tile, text=f"Batch {data['batchLabel']}",
                                font=("Inter", 11, "bold"), fg="#1e293b", bg="#f8fafc",
                                anchor="w")
                lbl1.pack(fill="x", padx=8, pady=(6, 0))

                lbl2 = tk_native.Label(tile, text=data['schedule'],
                                font=("Inter", 10), fg="#64748b", bg="#f8fafc",
                                anchor="w")
                lbl2.pack(fill="x", padx=8, pady=(0, 6))

                def on_click(event, d=disp, bd=data):
                    short_disp = f"Batch {bd['batchLabel']} | {bd['schedule']}"
                    if is_history:
                        self._selected_history_batch = bd
                        self.h_batch.set(short_disp)
                        cmd = self.h_batch.cget("command")
                        if cmd: cmd(short_disp)
                    else:
                        self._selected_batch = bd
                        self.batch_combo.set(short_disp)
                        cmd = self.batch_combo.cget("command")
                        if cmd: cmd(short_disp)
                    popup.destroy()

                def on_enter(event, t=tile, l1=lbl1, l2=lbl2):
                    t.configure(bg="#eef2ff", highlightbackground="#122aff")
                    l1.configure(bg="#eef2ff")
                    l2.configure(bg="#eef2ff")

                def on_leave(event, t=tile, l1=lbl1, l2=lbl2):
                    t.configure(bg="#f8fafc", highlightbackground="#e2e8f0")
                    l1.configure(bg="#f8fafc")
                    l2.configure(bg="#f8fafc")

                for widget in (tile, lbl1, lbl2):
                    widget.bind("<Button-1>", on_click)
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)
                    widget.configure(cursor="hand2")

        # Close Button
        btn_frame = tk_native.Frame(popup, bg="#e4e4e4")
        btn_frame.pack(fill="x", pady=(5, 12))
        close_btn = ctk.CTkButton(btn_frame, text="CLOSE",
                                  font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                                  fg_color="#374151", hover_color="#1f2937", text_color="#ffffff",
                                  width=160, height=38, corner_radius=8,
                                  command=popup.destroy)
        close_btn.pack(anchor="center")

        popup.update_idletasks()
        try:
            popup.grab_set()
        except Exception:
            pass

    def _sync_history_filters_from_record(self):
        # I apply Record Attendance selections to Attendance History automatically.
        if not self._last_record_filters:
            return
        if not hasattr(self, "h_class") or not hasattr(self, "h_term") or not hasattr(self, "h_batch") or not hasattr(self, "h_subject"):
            return
        if not self._history_stats_frame:
            return

        level = self._last_record_filters.get("level")
        term = self._last_record_filters.get("term")
        subj = self._last_record_filters.get("subject")
        batch_display = self._last_record_filters.get("batch_display")

        if not (level and term and subj and batch_display):
            return

        # Ensure dropdown options exist.
        self.h_class.set(level)
        apply_term_combo_for_level(self.h_term, level)
        self.h_term.set(term)
        self.update_combo_style(self.h_class)
        self.update_combo_style(self.h_term)

        # Subject selection
        self._selected_history_subject_code = subj
        self.h_subject.set(subj)
        self.update_combo_style(self.h_subject)

        # Populate history batch dropdown options and select the same one used in Record tab.
        self._load_history_batches(level, term)
        
        # Resolve history batch from display format
        matched_h_disp = ""
        for key, val in self._h_batch_display_to_row.items():
            if val.get("batchID") == (self._selected_batch.get("batchID") if self._selected_batch else None):
                matched_h_disp = key
                break
                
        if matched_h_disp:
            short_fmt = f"Batch {self._selected_batch.get('batchLabel')} | {self._selected_batch.get('schedule')}"
            self.h_batch.set(short_fmt)
            for val in self._h_batch_display_to_row.values():
                if val.get("batchID") == self._selected_batch.get("batchID"):
                    self._selected_history_batch = val
                    break
        else:
            self.h_batch.set("")
            self._selected_history_batch = None
            
        self.update_combo_style(self.h_batch)

        # Auto-load history results so user doesn't need to search again.
        self.load_history(level, term, self.h_batch.get(), self._history_stats_frame, self.hist_tree)

    def _set_class_details(self, level="—", term="—", subject="—", batch="—", schedule="—", time="—"):
        mapping = {
            "Level": level,
            "Term": term,
            "Subject": subject,
            "Batch": batch,
            "Schedule": schedule,
            "Time": time,
        }
        for key, val in mapping.items():
            if key in self.class_detail_labels:
                self.class_detail_labels[key].configure(text=val or "—")

    def show_roster_placeholder(self):
        for w in self.roster_rows_frame.winfo_children():
            w.destroy()
        self.attendance_vars.clear()
        self.attendance_times.clear()
        self.student_row_widgets.clear()
        self.student_row_frames.clear()

        lbl = ctk.CTkLabel(
            self.roster_rows_frame,
            text="Please select Level, Term, and Batch,\n"
                 "then click OK to retrieve the active class roster.",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#64748b",
            justify="center",
        )
        lbl.pack(pady=100)

    def on_ok_clicked(self):
        level = self.class_combo.get().strip()
        term = self.term_combo.get().strip()
        batch_disp = self.batch_combo.get().strip()

        if not level or not term or not batch_disp:
            messagebox.showwarning("Warning", "Please complete all filters first!")
            return
        batch_row = self._selected_batch
        if not batch_row:
            for val in self._batch_display_to_row.values():
                short_fmt = f"Batch {val.get('batchLabel')} | {val.get('schedule')}"
                if short_fmt == batch_disp:
                    if self._selected_subject_code and val.get("subjCode") == self._selected_subject_code:
                        batch_row = val
                        break
                    elif not self._selected_subject_code:
                        batch_row = val
                        break

        if not batch_row:
            messagebox.showwarning("Warning", "Please choose a valid batch.")
            return

        mil_time = datetime.now().strftime("%H:%M")
        self._set_class_details(
            level=level,
            term=term,
            subject=batch_row.get("subjCode"),
            batch=f"Batch {batch_row.get('batchLabel')}",
            schedule=batch_row.get("schedule"),
            time=mil_time,
        )
        self._selected_batch = batch_row
        # Persist the selected filters so the History tab can sync automatically.
        self._last_record_filters = {
            "level": level,
            "term": term,
            "subject": self._selected_subject_code,
            "batch_display": batch_disp,
            "batchID": batch_row.get("batchID"),
        }
        self.load_students()

    def load_students(self):
        level = self.class_combo.get().strip()
        term = self.term_combo.get().strip()
        batch_row = self._selected_batch

        if not level or not term or not batch_row:
            return
        batch_id = batch_row.get("batchID")
        if not batch_id:
            return

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT DISTINCT
                    d.detailID,
                    r.learnerID,
                    s.studentID,
                    s.studLname,
                    s.studFname,
                    s.studMname
                FROM REGISTRATION_DETAIL d
                JOIN REGISTRATION r ON r.registrationID = d.registrationID
                JOIN STUDENT s ON s.studentID = r.studentID
                WHERE r.regStatus = 'Active'
                  AND d.enrollStatus = 'Active'
                  AND r.level = ?
                  AND r.term = ?
                  AND d.batchID = ?
                ORDER BY s.studLname, s.studFname
            """, (level, term, batch_id))
            
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                for w in self.roster_rows_frame.winfo_children():
                    w.destroy()
                self.attendance_vars.clear()
                self.attendance_times.clear()
                self.student_row_widgets.clear()
                self.student_row_frames.clear()

                lbl = ctk.CTkLabel(
                    self.roster_rows_frame,
                    text="No enrolled students found for the selected filters.",
                    font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                    text_color="#ef4444",
                )
                lbl.pack(pady=60)
                return

            self.roster_rows = [dict(r) for r in rows]
            self.render_roster(self.roster_rows)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load students:\n{e}")

    def render_roster(self, roster_rows):
        for w in self.roster_rows_frame.winfo_children():
            w.destroy()
        self.attendance_vars.clear()
        self.attendance_times.clear()
        self.student_row_widgets.clear()
        self.student_row_frames.clear()

        for idx, row in enumerate(roster_rows):
            detail_key = str(row["detailID"])
            last_name = row.get("studLname") or ""
            first_name = row.get("studFname") or ""
            middle_raw = row.get("studMname")
            middle_name = f"{middle_raw[0]}." if middle_raw else ""

            row_bg = "#f8fafc" if idx % 2 == 0 else "#ffffff"
            row_frame = ctk.CTkFrame(self.roster_rows_frame, fg_color=row_bg,
                                     corner_radius=10, border_width=1, border_color="#cbd5e1",
                                     height=46)
            row_frame.pack(fill="x", pady=4, padx=5)
            row_frame.pack_propagate(False)

            self.student_row_frames[detail_key] = row_frame

            row_frame.grid_columnconfigure(0, minsize=35)
            row_frame.grid_columnconfigure(1, minsize=35)
            row_frame.grid_columnconfigure(2, minsize=35)
            row_frame.grid_columnconfigure(3, minsize=35)
            row_frame.grid_columnconfigure(4, weight=1)
            row_frame.grid_columnconfigure(5, weight=1)
            row_frame.grid_columnconfigure(6, weight=1, minsize=65)
            row_frame.grid_columnconfigure(7, minsize=120)
            row_frame.grid_columnconfigure(8, minsize=85)

            ctk.CTkLabel(row_frame, text=str(idx + 1),
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color="#475569", width=35
                         ).grid(row=0, column=0, padx=2, pady=8)

            p_var = ctk.BooleanVar(value=False)
            a_var = ctk.BooleanVar(value=False)
            l_var = ctk.BooleanVar(value=False)
            self.attendance_vars[detail_key] = (p_var, a_var, l_var)

            chk_cfg = dict(text="", width=22, height=22, corner_radius=11,
                           border_width=2, border_color="#cbd5e1",
                           checkmark_color="#ffffff")

            p_chk = ctk.CTkCheckBox(row_frame, variable=p_var, fg_color="#00bf63", hover_color="#008040", **chk_cfg)
            a_chk = ctk.CTkCheckBox(row_frame, variable=a_var, fg_color="#e20000", hover_color="#9e0000", **chk_cfg)
            l_chk = ctk.CTkCheckBox(row_frame, variable=l_var, fg_color="#122aff", hover_color="#0a1bb3", **chk_cfg)

            p_chk.configure(command=lambda k=detail_key, p=p_var, a=a_var, l=l_var: self._mutual(k, p, a, l, "P"))
            a_chk.configure(command=lambda k=detail_key, p=p_var, a=a_var, l=l_var: self._mutual(k, p, a, l, "A"))
            l_chk.configure(command=lambda k=detail_key, p=p_var, a=a_var, l=l_var: self._mutual(k, p, a, l, "L"))

            p_chk.grid(row=0, column=1, padx=2, pady=10)
            a_chk.grid(row=0, column=2, padx=2, pady=10)
            l_chk.grid(row=0, column=3, padx=2, pady=10)

            ctk.CTkLabel(row_frame, text=last_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", anchor="w").grid(row=0, column=4, padx=10, pady=10, sticky="w")

            ctk.CTkLabel(row_frame, text=first_name,
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#1e293b", anchor="w").grid(row=0, column=5, padx=10, pady=10, sticky="w")

            ctk.CTkLabel(row_frame, text=middle_name or "—",
                         font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#475569", anchor="w").grid(row=0, column=6, padx=10, pady=10, sticky="w")

            status_box = ctk.CTkFrame(row_frame, fg_color="#f1f5f9", width=70, height=22, corner_radius=8)
            status_box.grid(row=0, column=7, padx=5, pady=10)
            status_box.pack_propagate(False)
            status_lbl = ctk.CTkLabel(status_box, text="",
                                      font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                                      text_color="#64748b")
            status_lbl.pack(anchor="center", expand=True)

            time_lbl = ctk.CTkLabel(row_frame, text="—",
                                    font=ctk.CTkFont(family="Inter", size=12),
                                    text_color="#64748b")
            time_lbl.grid(row=0, column=8, padx=10, pady=10)

            self.student_row_widgets[detail_key] = (status_box, status_lbl, time_lbl)

    def _mutual(self, detail_key, p_var, a_var, l_var, selected):
        if selected == "P" and p_var.get():
            a_var.set(False)
            l_var.set(False)
        elif selected == "A" and a_var.get():
            p_var.set(False)
            l_var.set(False)
        elif selected == "L" and l_var.get():
            p_var.set(False)
            a_var.set(False)

        status_box, status_lbl, time_lbl = self.student_row_widgets[detail_key]
        row_frame = self.student_row_frames.get(detail_key)
        
        # Interactive live border coloring and Status pill formatting!
        click_time = datetime.now().strftime("%I:%M %p")
        if p_var.get():
            status_box.configure(fg_color="#00bf63")
            status_lbl.configure(text="PRESENT", text_color="white")
            time_lbl.configure(text=click_time, text_color="#0f172a")
            self.attendance_times[detail_key] = click_time
            if row_frame:
                row_frame.configure(border_color="#00bf63", border_width=1)
        elif a_var.get():
            status_box.configure(fg_color="#e20000")
            status_lbl.configure(text="ABSENT", text_color="white")
            time_lbl.configure(text=click_time, text_color="#0f172a")
            self.attendance_times[detail_key] = click_time
            if row_frame:
                row_frame.configure(border_color="#e20000", border_width=1)
        elif l_var.get():
            status_box.configure(fg_color="#122aff")
            status_lbl.configure(text="LATE", text_color="white")
            time_lbl.configure(text=click_time, text_color="#0f172a")
            self.attendance_times[detail_key] = click_time
            if row_frame:
                row_frame.configure(border_color="#122aff", border_width=1)
        else:
            status_box.configure(fg_color="#f1f5f9")
            status_lbl.configure(text="", text_color="#64748b")
            time_lbl.configure(text="—", text_color="#64748b")
            self.attendance_times.pop(detail_key, None)
            if row_frame:
                row_frame.configure(border_color="#cbd5e1", border_width=1)

    def save_attendance(self):
        att_date = datetime.now().strftime("%Y-%m-%d")
        att_time_now = datetime.now().strftime("%I:%M %p")

        if not self.attendance_vars:
            messagebox.showwarning("Warning", "No students loaded.")
            return

        unmarked = [k for k, (p, a, l) in self.attendance_vars.items()
                    if not p.get() and not a.get() and not l.get()]
        if len(unmarked) == len(self.attendance_vars):
            messagebox.showwarning("Nothing Marked",
                                   "Please mark attendance for at least one student.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        saved = 0
        skipped = []

        try:
            for detail_key, (p_var, a_var, l_var) in self.attendance_vars.items():
                if p_var.get():
                    status = "Present"
                elif a_var.get():
                    status = "Absent"
                elif l_var.get():
                    status = "Late"
                else:
                    skipped.append(detail_key)
                    continue

                detail_id = int(detail_key)

                att_time = self.attendance_times.get(detail_key)
                if not att_time and detail_key in self.student_row_widgets:
                    _, _, time_lbl = self.student_row_widgets[detail_key]
                    label_time = time_lbl.cget("text")
                    if label_time and label_time != "—":
                        att_time = label_time
                if not att_time:
                    att_time = att_time_now

                # Insert or update attendance status
                cursor.execute("""
                    SELECT attendanceID FROM ATTENDANCE
                    WHERE detailID = ? AND attDate = ?
                """, (detail_id, att_date))
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE ATTENDANCE SET attStatus = ?, attTime = ?
                        WHERE detailID = ? AND attDate = ?
                    """, (status, att_time, detail_id, att_date))
                else:
                    cursor.execute("""
                        INSERT INTO ATTENDANCE (detailID, attDate, attTime, attStatus)
                        VALUES (?, ?, ?, ?)
                    """, (detail_id, att_date, att_time, status))

                saved += 1

            conn.commit()
            AttendanceSavedPopup(self, saved, att_date, len(skipped))

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to save attendance:\n{e}")
        finally:
            conn.close()

    def update_clock(self):
        now = datetime.now()
        formatted_time = now.strftime("%B %d, %Y - %I:%M:%S %p")
        if hasattr(self, "live_time_label") and self.live_time_label.winfo_exists():
            self.live_time_label.configure(text=formatted_time)
            self.after(1000, self.update_clock)

    def render_history_tab(self):
        for w in self.workspace_canvas.winfo_children():
            w.destroy()

        import tkinter.ttk as ttk

        split_body = ctk.CTkFrame(self.workspace_canvas, fg_color="transparent")
        split_body.pack(fill="both", expand=True)

        # Left panel (same style as Record tab)
        left_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=420)
        left_panel.pack(side="left", fill="y", anchor="nw")
        left_panel.pack_propagate(False)
        left_panel.grid_propagate(False)

        def section_label(parent, text, row):
            lbl = ctk.CTkLabel(parent, text=text,
                               font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                               text_color="black")
            lbl.grid(row=row, column=0, sticky="w", pady=(4, 1))
            return lbl

        # LEVEL
        section_label(left_panel, "LEVEL", 0)
        h_class_card, h_class_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        h_class_card.grid(row=1, column=0, sticky="ew")
        h_class_card.pack_propagate(False)
        self.h_class = self._combo(h_class_inner, [f"Grade {i}" for i in range(1, 13)])
        self.h_class.pack(fill="x")

        # TERM
        section_label(left_panel, "TERM", 2)
        h_term_card, h_term_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        h_term_card.grid(row=3, column=0, sticky="ew")
        h_term_card.pack_propagate(False)
        self.h_term = self._combo(h_term_inner, [])
        self.h_term.pack(fill="x")

        # SUBJECT
        section_label(left_panel, "SUBJECT", 4)
        h_subject_card, h_subject_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        h_subject_card.grid(row=5, column=0, sticky="ew")
        h_subject_card.pack_propagate(False)
        self.h_subject = self._subject_combo_history(h_subject_inner)
        self.h_subject.pack(fill="x")

        # BATCH
        section_label(left_panel, "BATCH", 6)
        h_batch_card, h_batch_inner = self._card_frame(left_panel, height=38, inner_pady=3, accent_pady=4)
        h_batch_card.grid(row=7, column=0, sticky="ew")
        h_batch_card.pack_propagate(False)
        self.h_batch = self._batch_combo(h_batch_inner, is_history=True, command=lambda *_: self.update_combo_style(self.h_batch))
        self.h_batch.pack(fill="x")

        # SEARCH button
        ctk.CTkButton(left_panel, text="SEARCH",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      height=34, corner_radius=8,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=lambda: self.load_history(
                          self.h_class.get(),
                          self.h_term.get(),
                          self.h_batch.get(),
                          stats_frame, tree)
                      ).grid(row=8, column=0, sticky="ew", pady=(10, 0))

        left_panel.columnconfigure(0, weight=1)

        def on_h_class_changed(choice):
            apply_term_combo_for_level(self.h_term, choice)
            # Keep History dropdowns empty until user clicks/selects.
            self.h_term.set("")
            self.update_combo_style(self.h_class)
            self.update_combo_style(self.h_term)
            self.h_subject.set("")
            self.update_combo_style(self.h_subject)
            self._selected_history_subject_code = None
            self._h_batch_display_to_row = {}
            self.h_batch.configure(values=[])
            self.h_batch.set("")
            self.update_combo_style(self.h_batch)
            self._selected_history_batch = None

        def load_h_batches():
            level = self.h_class.get().strip()
            term = self.h_term.get().strip()
            self._h_batch_display_to_row = {}
            if not level or not term:
                self.h_batch.configure(values=[])
                self.h_batch.set("")
                self.update_combo_style(self.h_batch)
                return
            try:
                conn = database.get_connection()
                cur = conn.cursor()
                params = [level]
                tutor_filter = ""
                if str(self.user_role).lower().startswith("tutor") and self.tutor_id:
                    tutor_filter = " AND (b.tutorID = ?)"
                    params.append(self.tutor_id)
                cur.execute(
                    f"""
                    SELECT b.batchID, b.batchLabel, b.schedule, s.subjCode
                    FROM BATCH b
                    JOIN SUBJECT s ON s.subjectID = b.subjectID
                    WHERE b.isActive = 1
                      AND b.level = ?
                      {tutor_filter}
                    ORDER BY s.subjCode, b.batchLabel
                    """,
                    tuple(params),
                )
                rows = [dict(r) for r in cur.fetchall()]
                conn.close()
                values = []
                for r in rows:
                    disp = f"{r['subjCode']} — Batch {r['batchLabel']} — {r['schedule']}"
                    values.append(disp)
                    self._h_batch_display_to_row[disp] = {
                        "batchID": r["batchID"],
                        "batchLabel": r["batchLabel"],
                        "schedule": r["schedule"],
                        "subjCode": r["subjCode"],
                        "level": level,
                        "term": term,
                    }
                self.h_batch.configure(values=values)
                # Keep dropdown empty until user clicks/selects or Record tab syncs it.
                self.h_batch.set("")
                self.update_combo_style(self.h_batch)
            except Exception:
                self._h_batch_display_to_row = {}
                self.h_batch.configure(values=[])
                self.h_batch.set("")
                self.update_combo_style(self.h_batch)

        def on_h_term_changed(choice):
            self.update_combo_style(self.h_term)
            self.h_subject.set("")
            self.update_combo_style(self.h_subject)
            self._selected_history_subject_code = None
            self.h_batch.set("")
            self.update_combo_style(self.h_batch)
            self._selected_history_batch = None
            load_h_batches()

        self.h_class.configure(command=on_h_class_changed)
        self.h_term.configure(command=on_h_term_changed)

        # Render clean initial empty states.
        self.h_class.set("")
        self.h_term.set("")
        self.h_subject.set("")
        self.h_batch.set("")

        # Right panel
        right_panel = ctk.CTkFrame(split_body, fg_color="transparent", width=480)
        right_panel.pack(side="right", fill="both", expand=True, padx=(20, 0))

        ctk.CTkLabel(right_panel, text="ATTENDANCE RECORDS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="black").pack(anchor="w", pady=(0, 6))

        # Table
        table_card = ctk.CTkFrame(right_panel, fg_color="#ffffff",
                                  corner_radius=16, border_width=1, border_color="#cbd5e1")
        table_card.pack(fill="both", expand=True)

        tree_frame = ctk.CTkFrame(table_card, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=12)
        tree_frame.bind("<Configure>", self._fit_history_tree_columns)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Hist.Treeview.Heading",
                        background="#15165e", foreground="#ffffff",
                        font=("Inter", 11, "bold"), borderwidth=0)
        style.map("Hist.Treeview.Heading",
                  background=[("active","#1c1d7c")], foreground=[("active","#ffffff")])
        style.configure("Hist.Treeview",
                        font=("Inter", 10), rowheight=30,
                        fieldbackground="#ffffff", background="#ffffff", borderwidth=0)
        style.map("Hist.Treeview",
                  background=[("selected","#e0e7ff")],
                  foreground=[("selected","#15165e")])

        cols = ("#", "Learner ID", "Student Name", "Date", "Time", "Status")
        self.hist_tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                                      height=18, style="Hist.Treeview")
        self.hist_tree["displaycolumns"] = cols
        self.hist_tree.column("#0", width=0, stretch=False)
        tree = self.hist_tree
        tree.tag_configure("present", foreground="#008040")
        tree.tag_configure("absent",  foreground="#b91c1c")
        tree.tag_configure("late",    foreground="#122aff")
        tree.tag_configure("even",    background="#f8fafc")
        tree.tag_configure("odd",     background="#ffffff")

        self._hist_col_specs = [
            ("#", 42, "center", False),
            ("Learner ID", 118, "w", False),
            ("Student Name", 180, "w", True),
            ("Date", 100, "center", False),
            ("Time", 100, "center", False),
            ("Status", 88, "center", False),
        ]
        for col, width, anchor, stretch in self._hist_col_specs:
            tree.heading(col, text=col, anchor=anchor)
            tree.column(col, width=width, minwidth=width, anchor=anchor, stretch=stretch)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        self.after_idle(self._fit_history_tree_columns)

        # Summary stats
        stats_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        self._history_stats_frame = stats_frame
        stats_frame.pack(fill="x", pady=(12, 0))
        for col in range(4):
            stats_frame.columnconfigure(col, weight=1, uniform="stat_col")

    def _fit_history_tree_columns(self, event=None):
        """Keep history table columns aligned with headers inside the card."""
        if not hasattr(self, "hist_tree") or not self.hist_tree.winfo_exists():
            return
        tree = self.hist_tree
        tree.update_idletasks()
        total_w = tree.winfo_width()
        if total_w < 200:
            return
        fixed = 42 + 118 + 100 + 100 + 88 + 24  # #, learner, date, time, status + padding
        name_w = max(total_w - fixed, 120)
        tree.column("#", width=42, minwidth=42, stretch=False)
        tree.column("Learner ID", width=118, minwidth=100, stretch=False)
        tree.column("Student Name", width=name_w, minwidth=120, stretch=False)
        tree.column("Date", width=100, minwidth=90, stretch=False)
        tree.column("Time", width=100, minwidth=90, stretch=False)
        tree.column("Status", width=88, minwidth=72, stretch=False)

    def load_history(self, level, term, batch_display, stats_frame, tree):
        for w in stats_frame.winfo_children():
            w.destroy()

        for item in tree.get_children():
            tree.delete(item)

        if not all([level, term, batch_display]):
            messagebox.showwarning("Warning", "Please complete all filters first!")
            return

        batch_row = None
        if hasattr(self, "_selected_history_batch") and self._selected_history_batch:
            expected_short = f"Batch {self._selected_history_batch.get('batchLabel')} | {self._selected_history_batch.get('schedule')}"
            if expected_short == batch_display:
                batch_row = self._selected_history_batch

        if not batch_row:
            for val in self._h_batch_display_to_row.values():
                short_fmt = f"Batch {val.get('batchLabel')} | {val.get('schedule')}"
                if short_fmt == batch_display:
                    batch_row = val
                    break

        if not batch_row:
            messagebox.showwarning("Warning", "Please choose a valid batch.")
            return

        try:
            conn = database.get_connection()
            cur = conn.cursor()
            params = [level, term, batch_row["batchID"]]
            cur.execute("""
                SELECT r.learnerID,
                       s.studLname || ', ' || s.studFname AS studentName,
                       a.attDate, a.attTime, a.attStatus
                FROM ATTENDANCE a
                JOIN REGISTRATION_DETAIL d ON a.detailID = d.detailID
                JOIN REGISTRATION r ON d.registrationID = r.registrationID
                JOIN STUDENT s ON r.studentID = s.studentID
                WHERE r.level = ?
                  AND r.term = ?
                  AND d.batchID = ?
                ORDER BY s.studLname, s.studFname, a.attDate
            """, tuple(params))
            rows = cur.fetchall()
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history:\n{e}")
            return

        present_c = absent_c = late_c = 0
        for idx, r in enumerate(rows):
            status = r["attStatus"]
            if status == "Present":
                present_c += 1; tag_s = "present"
            elif status == "Absent":
                absent_c  += 1; tag_s = "absent"
            else:
                late_c    += 1; tag_s = "late"
            row_tag = "even" if idx % 2 == 0 else "odd"
            att_time = r["attTime"] if r["attTime"] else "—"
            tree.insert("", "end",
                        values=(idx+1, r["learnerID"], r["studentName"], r["attDate"], att_time, status),
                        tags=(tag_s, row_tag))

        if not rows:
            tree.insert("", "end", values=("", "", "No records found for the selected filters.", "", "", ""))

        # Build summary cards
        total = len(rows)
        stats = [
            ("PRESENT", present_c, "#00bf63"),
            ("ABSENT",  absent_c,  "#e20000"),
            ("LATE",    late_c,    "#122aff"),
            ("TOTAL",   total,     "#475569"),
        ]
        for col, (label, count, accent) in enumerate(stats):
            card = ctk.CTkFrame(
                stats_frame, fg_color="#ffffff", corner_radius=4,
                border_width=1, border_color="#e2e8f0", height=76,
            )
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0))
            card.grid_propagate(False)

            ctk.CTkFrame(card, height=3, fg_color=accent, corner_radius=0).pack(fill="x")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=14, pady=(10, 12))

            ctk.CTkLabel(
                inner, text=label,
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color="#64748b", anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner, text=str(count),
                font=ctk.CTkFont(family="Inter", size=26, weight="bold"),
                text_color=accent, anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        if not rows:
            from tkinter import messagebox
            messagebox.showinfo("No Records", "No attendance records found for the selected filters.")

        self.after_idle(self._fit_history_tree_columns)

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()