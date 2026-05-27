# modules/manage_grades.py
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from PIL import Image
import database
from utils.pdf_generator import generate_grades_pdf
from utils.modern_entry import ModernEntry
from utils.modern_combo import ModernCombo
from utils.term_options import apply_term_combo_for_level, get_term_options


def convert_grade(numeric):
    """Convert a numeric grade (0-100) to (letter_grade, description) tuple."""
    if numeric >= 95:
        return "A+", "Excellent"
    elif numeric >= 90:
        return "A", "Very Good"
    elif numeric >= 85:
        return "B+", "Good"
    elif numeric >= 80:
        return "B", "Satisfactory"
    elif numeric >= 75:
        return "C", "Fair"
    else:
        return "D/F", "Needs Improvement"


class SuccessPopup(ctk.CTkToplevel):
    def __init__(self, parent, title, message, details=None):
        super().__init__(parent)
        self.title("Success")
        self.geometry("400x240")
        self.resizable(False, False)
        self.configure(fg_color="#15165e")
        self.transient(parent)
        
        self.lift()
        self.attributes("-topmost", True)
        try:
            self.grab_set()
        except Exception:
            pass

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
            text=title,
            font=ctk.CTkFont(family="Inter", size=20, weight="bold"),
            text_color="#ffffff"
        )
        msg_label.pack(pady=(5, 5))

        if details:
            details_text = f"{message}\n{details}"
        else:
            details_text = message
            
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


class ManageGrades(ctk.CTkFrame):
    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user_role = user_role
        self.tutor_id = user_id

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.grade_entries = {}   # Keys: detailID -> tk.Entry (numeric input)
        self.letter_labels = {}   # Keys: detailID -> tk.Label (auto letter grade)
        self.desc_labels = {}     # Keys: detailID -> tk.Label (auto description)
        self.is_editable = True
        self.card_widgets = []
        self._ind_suggestions_rows = []
        self._class_suggestions_rows = []
        self._batch_display_to_row = {}
        self._selected_batch = None
        self.create_ui()

    def _combo(self, parent, values, **kwargs):
        return ModernCombo(parent, values=values, **kwargs)

    @staticmethod
    def _add_combo_underline(parent, combo):
        """Navy underline below combo; bright blue on focus."""
        underline = ctk.CTkFrame(parent, height=2, fg_color="#15165e", corner_radius=0)
        underline.pack(fill="x", pady=(0, 2))

        def on_focus(_event=None):
            underline.configure(fg_color="#122aff")

        def on_unfocus(_event=None):
            underline.configure(fg_color="#15165e")

        combo.bind("<FocusIn>", on_focus)
        combo.bind("<FocusOut>", on_unfocus)

    def create_ui(self):
        # ── Top bar ──────────────────────────────────────────────────────────
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkButton(top_bar, text="<  Back to Dashboard",
                      font=ctk.CTkFont(family="Inter", size=14),
                      fg_color="transparent", text_color="#ffffff",
                      hover_color="#22259c", width=150, height=40,
                      corner_radius=8, command=self.back_to_dashboard
                      ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(top_bar, text="Manage Grades",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            logo_img = Image.open(logo_path)
            ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(55, 55))
            ctk.CTkLabel(top_bar, image=ctk_logo, text="").pack(side="right", padx=30)
        else:
            ctk.CTkLabel(top_bar, text="ABC",
                         font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                         text_color="#122aff").pack(side="right", padx=30)

        # ── Workspace ────────────────────────────────────────────────────────
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Tab pill
        tab_selector_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        tab_selector_frame.pack(fill="x", pady=(0, 15))

        tab_pill = ctk.CTkFrame(tab_selector_frame, fg_color="#cbd5e1",
                                width=400, height=46, corner_radius=23)
        tab_pill.pack(anchor="center")
        tab_pill.pack_propagate(False)

        self.class_tab_btn = ctk.CTkButton(
            tab_pill, text="Class Grades",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="#122aff", text_color="#ffffff",
            corner_radius=19, height=38, width=190,
            command=lambda: self.switch_tab("class")
        )
        self.class_tab_btn.pack(side="left", padx=(4, 2), pady=4)

        self.ind_tab_btn = ctk.CTkButton(
            tab_pill, text="Individual Grades",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            fg_color="transparent", text_color="#374151",
            corner_radius=19, height=38, width=190,
            command=lambda: self.switch_tab("individual")
        )
        self.ind_tab_btn.pack(side="left", padx=(2, 4), pady=4)

        # ── TAB 1: CLASS GRADING SHEET ───────────────────────────────────────
        self.class_tab_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.class_tab_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(self.class_tab_frame, text="FILTER CLASS",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 4))

        filter_card = ctk.CTkFrame(self.class_tab_frame, fg_color="#ffffff",
                                   corner_radius=16, border_width=1,
                                   border_color="#cbd5e1", height=90)
        filter_card.pack(fill="x", pady=(0, 10))
        filter_card.pack_propagate(False)

        accent_container = ctk.CTkFrame(filter_card, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)
        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        filter_inner = ctk.CTkFrame(filter_card, fg_color="transparent")
        filter_inner.pack(fill="both", expand=True, padx=15, pady=10)

        for col in range(3):
            filter_inner.grid_columnconfigure(col, weight=1)

        # Grade Level
        ctk.CTkLabel(filter_inner, text="LEVEL",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#444444").grid(row=0, column=0, sticky="w", padx=(0, 8))
        grade_wrap = ctk.CTkFrame(filter_inner, fg_color="transparent")
        grade_wrap.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.grade_combo = self._combo(
            grade_wrap, [f"Grade {i}" for i in range(1, 13)],
            command=self.on_grade_changed)
        self.grade_combo.set("")
        self.grade_combo.pack(fill="x")
        self._add_combo_underline(grade_wrap, self.grade_combo)

        # BATCH
        ctk.CTkLabel(filter_inner, text="BATCH",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#444444").grid(row=0, column=1, sticky="w", padx=(0, 8))
        section_wrap = ctk.CTkFrame(filter_inner, fg_color="transparent")
        section_wrap.grid(row=1, column=1, sticky="ew", padx=(0, 8))
        self.section_combo = self._combo(section_wrap, [], command=self.on_batch_changed)
        self.section_combo.pack(fill="x")
        self._add_combo_underline(section_wrap, self.section_combo)

        # Term
        self.term_label = ctk.CTkLabel(filter_inner, text="TERM",
                                       font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                       text_color="#444444")
        self.term_label.grid(row=0, column=2, sticky="w", padx=(0, 8))

        term_wrap = ctk.CTkFrame(filter_inner, fg_color="transparent")
        term_wrap.grid(row=1, column=2, sticky="ew", padx=(0, 8))
        self.term_combo = self._combo(term_wrap, [], command=self.on_term_changed)
        self.term_combo.pack(fill="x")
        self._add_combo_underline(term_wrap, self.term_combo)
        apply_term_combo_for_level(self.term_combo, "Grade 7")

        # Search + Load button row
        controls_row = ctk.CTkFrame(self.class_tab_frame, fg_color="transparent")
        controls_row.pack(fill="x", pady=(0, 10))

        search_card = ctk.CTkFrame(controls_row, fg_color="#ffffff", corner_radius=16,
                                   border_width=1, border_color="#cbd5e1")
        search_card.pack(side="left", fill="x", expand=True, padx=(0, 15))

        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(fill="both", expand=True, padx=15, pady=12)

        self.class_search_entry = ModernEntry(
            search_inner,
            placeholder_text="🔍 Type student name or Learner ID to search...",
            height=32, font=ctk.CTkFont(family="Inter", size=13),
        )
        self.class_search_entry.pack(fill="x")
        self.class_search_entry.bind("<KeyRelease>", self.on_class_search_key)
        self.class_search_entry.bind("<FocusOut>",
                                     lambda e: self.after(250, self.hide_class_suggestions))

        self.class_suggest_frame = ctk.CTkFrame(search_inner, fg_color="#ffffff",
                                                border_width=1, border_color="#cbd5e1",
                                                corner_radius=8)
        self.class_suggest_lbox = tk.Listbox(
            self.class_suggest_frame,
            bg="#ffffff", fg="#1e293b",
            font=("Inter", 11),
            bd=0, highlightthickness=0,
            selectbackground="#122aff", selectforeground="#ffffff",
            activestyle="none"
        )
        self.class_suggest_lbox.pack(fill="both", expand=True, padx=2, pady=2)
        self.class_suggest_lbox.bind("<<ListboxSelect>>", self.on_class_suggestion_select)

        ctk.CTkButton(controls_row, text="LOAD STUDENTS",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      height=40, width=160, corner_radius=8,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.load_students
                      ).pack(side="right")

        # Grading sheet label + scroll area
        ctk.CTkLabel(self.class_tab_frame, text="CLASS GRADING SHEET",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(5, 4))

        self.scroll_container = ctk.CTkScrollableFrame(
            self.class_tab_frame, fg_color="transparent", corner_radius=0)
        self.scroll_container.pack(fill="both", expand=True, pady=(0, 10))

        # Bottom bar
        self.bottom_bar = ctk.CTkFrame(self.class_tab_frame, fg_color="transparent")
        self.bottom_bar.pack(fill="x", pady=(10, 0))

        self.save_btn = ctk.CTkButton(
            self.bottom_bar, text="SAVE ALL GRADES",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            height=45, width=200, corner_radius=8,
            fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
            command=self.save_grades)
        self.save_btn.pack(side="right", padx=(10, 0))

        self.edit_btn = ctk.CTkButton(
            self.bottom_bar, text="EDIT / UPDATE GRADES",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            height=45, width=220, corner_radius=8,
            fg_color="#f59e0b", hover_color="#d97706", text_color="#ffffff",
            command=self.unlock_grades)
        self.edit_btn.pack(side="right", padx=(10, 0))
        self.edit_btn.pack_forget()

        ctk.CTkButton(self.bottom_bar, text="EXPORT GRADE SHEET (PDF)",
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      height=45, width=240, corner_radius=8,
                      fg_color="#15165e", hover_color="#22259c", text_color="#ffffff",
                      command=self.export_grades_pdf
                      ).pack(side="left")

        # ── TAB 2: INDIVIDUAL STUDENT GRADES ────────────────────────────────
        self.individual_tab_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

        search_card2 = ctk.CTkFrame(self.individual_tab_frame, fg_color="#ffffff",
                                    corner_radius=16, border_width=1, border_color="#cbd5e1")
        search_card2.pack(fill="x", pady=(0, 10))

        search_inner2 = ctk.CTkFrame(search_card2, fg_color="transparent")
        search_inner2.pack(padx=20, pady=15, fill="x")

        ctk.CTkLabel(
            search_inner2, text="SEARCH STUDENT FOR INDIVIDUAL GRADES",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#15165e",
        ).pack(anchor="w", pady=(0, 5))

        self.ind_search_entry = ModernEntry(
            search_inner2,
            placeholder_text="Type Student Name or Student ID...",
            height=32, font=ctk.CTkFont(family="Inter", size=13)
        )
        self.ind_search_entry.pack(fill="x")
        self.ind_search_entry.bind("<KeyRelease>", self.on_ind_search_key)
        self.ind_search_entry.bind("<FocusOut>",
                                   lambda e: self.after(250, self.hide_ind_suggestions))

        self.ind_suggest_frame = ctk.CTkFrame(search_inner2, fg_color="#ffffff",
                                              border_width=1, border_color="#cbd5e1",
                                              corner_radius=8)
        self.ind_suggest_lbox = tk.Listbox(
            self.ind_suggest_frame,
            bg="#ffffff", fg="#1e293b",
            font=("Inter", 11),
            bd=0, highlightthickness=0,
            selectbackground="#122aff", selectforeground="#ffffff",
            activestyle="none"
        )
        self.ind_suggest_lbox.pack(fill="both", expand=True, padx=2, pady=2)
        self.ind_suggest_lbox.bind("<<ListboxSelect>>", self.on_ind_suggestion_select)

        self.report_card_container = ctk.CTkFrame(
            self.individual_tab_frame, fg_color="transparent")
        self.report_card_container.pack(fill="both", expand=True, pady=10)

        self.show_class_placeholder()
        self.show_ind_placeholder()
        self.on_grade_changed("")
        self.grade_combo.set("")
        self.term_combo.set("")
        self.section_combo.set("")

    # ─────────────────────────────────────────────────────────────────────────
    # Tab switching
    # ─────────────────────────────────────────────────────────────────────────
    def switch_tab(self, tab_target):
        if tab_target == "class":
            self.class_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.ind_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.individual_tab_frame.pack_forget()
            self.class_tab_frame.pack(fill="both", expand=True)
        else:
            self.class_tab_btn.configure(fg_color="transparent", text_color="#374151")
            self.ind_tab_btn.configure(fg_color="#122aff", text_color="#ffffff")
            self.class_tab_frame.pack_forget()
            self.individual_tab_frame.pack(fill="both", expand=True)

    def on_grade_changed(self, choice):
        apply_term_combo_for_level(self.term_combo, choice)
        self.term_combo.set("")
        self.load_batches_for_filters()

    def on_term_changed(self, choice):
        # Dynamically update term in mapped batches
        for key in self._batch_display_to_row:
            self._batch_display_to_row[key]["term"] = choice

    def on_batch_changed(self, choice):
        if choice in self._batch_display_to_row:
            self._selected_batch = self._batch_display_to_row[choice]
        else:
            self._selected_batch = None

    def load_batches_for_filters(self):
        """Load batches for level. Tutor accounts only see their own batches."""
        level = self.grade_combo.get().strip()
        term = self.term_combo.get().strip()
        self._batch_display_to_row = {}
        self._selected_batch = None

        if not level:
            self.section_combo.configure(values=[])
            self.section_combo.set("")
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
                       s.subjectName
                FROM BATCH b
                JOIN SUBJECT s ON s.subjectID = b.subjectID
                WHERE b.isActive = 1
                  AND b.level = ?
                  {tutor_filter}
                ORDER BY s.subjectName, b.batchLabel
                """,
                tuple(params),
            )
            rows = cur.fetchall()
            conn.close()

            values = []
            for r in rows:
                disp = f"{r['subjectName']} — Batch {r['batchLabel']} — {r['schedule']}"
                values.append(disp)
                self._batch_display_to_row[disp] = {
                    "batchID": r["batchID"],
                    "batchLabel": r["batchLabel"],
                    "schedule": r["schedule"],
                    "level": r["level"],
                    "subjectName": r["subjectName"],
                    "term": term if term else "Term 1",
                }

            self.section_combo.configure(values=values)
            self.section_combo.set("")
            self._selected_batch = None
        except Exception as e:
            print("Error loading batches in grades:", e)
            self.section_combo.configure(values=[])
            self.section_combo.set("")

    # ─────────────────────────────────────────────────────────────────────────
    # Placeholders
    # ─────────────────────────────────────────────────────────────────────────
    def show_class_placeholder(self):
        for w in self.scroll_container.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.scroll_container,
            text="Please configure the class filters above and click 'LOAD STUDENTS'.",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#64748b",
            justify="center"
        ).pack(expand=True, pady=80)

    def show_ind_placeholder(self):
        for w in self.report_card_container.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.report_card_container,
            text="Please search and select a student above to review their individual grades.",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#64748b",
            justify="center"
        ).pack(expand=True, pady=80)

    # ─────────────────────────────────────────────────────────────────────────
    # Individual tab – search & suggestions
    # ─────────────────────────────────────────────────────────────────────────
    def on_ind_search_key(self, event):
        val = self.ind_search_entry.get().strip()
        if len(val) < 2:
            self.hide_ind_suggestions()
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.registrationID, r.studentID, r.learnerID,
                       s.studLname, s.studFname, s.studMname,
                       r.level, r.groupName, r.term
                FROM REGISTRATION r
                JOIN STUDENT s ON r.studentID = s.studentID
                WHERE r.regStatus = 'Active' AND (
                    r.learnerID LIKE ? OR
                    s.studFname LIKE ? OR
                    s.studLname LIKE ?
                )
                ORDER BY s.studLname, s.studFname
                LIMIT 20
            """, (f"%{val}%", f"%{val}%", f"%{val}%"))
            rows = cursor.fetchall()
            self._ind_suggestions_rows = rows

            if rows:
                self.ind_suggest_lbox.delete(0, tk.END)
                for r in rows:
                    mname = (f" {r['studMname'][0]}."
                             if r['studMname'] else "")
                    lbl = (f" {r['studFname']}{mname} {r['studLname']}"
                           f"  (Learner ID: {r['learnerID']}"
                           f" | {r['level']} - {r['groupName']})")
                    self.ind_suggest_lbox.insert(tk.END, lbl)
                self.ind_suggest_lbox.config(height=min(len(rows), 6))
                self.ind_suggest_frame.pack(fill="x",
                                            after=self.ind_search_entry,
                                            pady=(4, 0))
            else:
                self.hide_ind_suggestions()
        except Exception as e:
            print("Error loading suggestions:", e)
        finally:
            conn.close()

    def hide_ind_suggestions(self):
        self.ind_suggest_frame.pack_forget()

    def on_ind_suggestion_select(self, event):
        sel = self.ind_suggest_lbox.curselection()
        if not sel:
            return
        row = self._ind_suggestions_rows[sel[0]]
        self.ind_search_entry.delete(0, tk.END)
        self.hide_ind_suggestions()
        self.load_individual_report_card(row)

    # ─────────────────────────────────────────────────────────────────────────
    # Class tab – search & suggestions
    # ─────────────────────────────────────────────────────────────────────────
    def on_class_search_key(self, event):
        val = self.class_search_entry.get().strip()
        self.filter_class_sheet()

        if len(val) < 2:
            self.hide_class_suggestions()
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.registrationID, r.studentID, r.learnerID,
                       s.studLname, s.studFname, s.studMname,
                       r.level, r.term, d.batchID, b.batchLabel, sub.subjectName,
                       (sub.subjectName || ' — Batch ' || b.batchLabel || ' — ' || b.schedule) AS batchDisplay
                FROM REGISTRATION_DETAIL d
                JOIN REGISTRATION r ON d.registrationID = r.registrationID
                JOIN STUDENT s ON r.studentID = s.studentID
                JOIN BATCH b ON d.batchID = b.batchID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE r.regStatus = 'Active' AND d.enrollStatus = 'Active' AND (
                    r.learnerID LIKE ? OR
                    s.studFname LIKE ? OR
                    s.studLname LIKE ?
                )
                ORDER BY s.studLname, s.studFname
                LIMIT 20
            """, (f"%{val}%", f"%{val}%", f"%{val}%"))
            rows = cursor.fetchall()
            self._class_suggestions_rows = rows

            if rows:
                self.class_suggest_lbox.delete(0, tk.END)
                for r in rows:
                    mname = (f" {r['studMname'][0]}." if r['studMname'] else "")
                    lbl = (f" {r['studFname']}{mname} {r['studLname']}"
                           f"  (Learner ID: {r['learnerID']}"
                           f" | {r['subjectName']} - Batch {r['batchLabel']})")
                    self.class_suggest_lbox.insert(tk.END, lbl)
                self.class_suggest_lbox.config(height=min(len(rows), 6))
                self.class_suggest_frame.pack(fill="x",
                                              after=self.class_search_entry,
                                              pady=(4, 0))
            else:
                self.hide_class_suggestions()
        except Exception as e:
            print("Error loading class suggestions:", e)
        finally:
            conn.close()

    def hide_class_suggestions(self):
        self.class_suggest_frame.pack_forget()

    def on_class_suggestion_select(self, event):
        sel = self.class_suggest_lbox.curselection()
        if not sel:
            return
        row = self._class_suggestions_rows[sel[0]]
        self.hide_class_suggestions()

        # Extract values
        level = row['level']
        term = row['term']
        batch_display = row['batchDisplay']
        learner_id = row['learnerID']

        # 1. Update combos
        self.grade_combo.set(level)
        apply_term_combo_for_level(self.term_combo, level)
        self.term_combo.set(term)
        
        # 2. Fetch/populate batches for level and select the student's batch
        self.load_batches_for_filters()
        self.section_combo.set(batch_display)
        self.on_batch_changed(batch_display)

        # 3. Load students for this batch
        self.load_students()

        # 4. Filter the cards to show only this student
        self.class_search_entry.delete(0, tk.END)
        self.class_search_entry.insert(0, learner_id)
        self.filter_class_sheet()

    # ─────────────────────────────────────────────────────────────────────────
    # Individual Report Card
    # ─────────────────────────────────────────────────────────────────────────
    def reload_rc_semester(self, r):
        selected_term = self.rc_term_combo.get()
        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.registrationID, r.studentID, r.learnerID,
                       s.studLname, s.studFname, s.studMname,
                       r.level, r.groupName, r.term
                FROM REGISTRATION r
                JOIN STUDENT s ON r.studentID = s.studentID
                WHERE r.studentID = ? AND r.level = ? AND r.term = ?
                  AND r.regStatus = 'Active'
            """, (r['studentID'], r['level'], selected_term))
            row = cursor.fetchone()
            if row:
                self.load_individual_report_card(row)
            else:
                messagebox.showinfo(
                    "Not Found",
                    f"No active registration found for this student in {selected_term}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch term:\n{e}")
        finally:
            conn.close()

    def load_individual_report_card(self, r):
        for w in self.report_card_container.winfo_children():
            w.destroy()

        mname = (f" {r['studMname'][0]}." if r['studMname'] else "")
        full_name = f"{r['studFname']}{mname} {r['studLname']}"
        level = r['level']
        group_name = r['groupName']
        term = r['term']

        rc_card = ctk.CTkFrame(self.report_card_container, fg_color="#ffffff",
                               corner_radius=16, border_width=1, border_color="#cbd5e1")
        rc_card.pack(fill="both", expand=True, padx=5, pady=5)

        # Header bar
        rc_header = ctk.CTkFrame(rc_card, fg_color="#15165e", corner_radius=8, height=44)
        rc_header.pack(fill="x", side="top", padx=10, pady=(10, 5))
        rc_header.pack_propagate(False)
        ctk.CTkLabel(
            rc_header,
            text=(f"STUDENT REPORT CARD  •  {full_name.upper()}"
                  f"  (Learner ID: {r['learnerID']})"),
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(
            rc_header, text="View Profile",
            font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
            width=110, height=28, corner_radius=6,
            fg_color="#ffffff", hover_color="#e0e7ff",
            text_color="#15165e",
            command=lambda: self.show_student_detail_popup(r['studentID'], r['learnerID'])
        ).pack(side="right", padx=10, pady=8)

        # Meta row
        meta_row = ctk.CTkFrame(rc_card, fg_color="#f8fafc", height=38)
        meta_row.pack(fill="x", side="top")
        meta_row.pack_propagate(False)

        for label, val in [("Level", level), ("Group Name", group_name), ("Term", term)]:
            ctk.CTkLabel(
                meta_row, text=f"{label}:  {val}",
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#475569"
            ).pack(side="left", padx=20)

        filter_frame = ctk.CTkFrame(meta_row, fg_color="transparent")
        filter_frame.pack(side="right", padx=20, pady=4)

        ctk.CTkLabel(filter_frame, text="Select Term: ",
                     font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                     text_color="#475569").pack(side="left")

        rc_term_values = get_term_options(level)
        rc_term_wrap = ctk.CTkFrame(filter_frame, fg_color="transparent")
        rc_term_wrap.pack(side="left", padx=5)
        self.rc_term_combo = ModernCombo(rc_term_wrap, values=rc_term_values,
                                         width=130, height=28)
        if term in rc_term_values:
            self.rc_term_combo.set(term)
        elif rc_term_values:
            self.rc_term_combo.set(rc_term_values[0])
        self.rc_term_combo.pack(fill="x")
        self._add_combo_underline(rc_term_wrap, self.rc_term_combo)

        ctk.CTkButton(filter_frame, text="LOAD", width=60, height=28,
                      font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                      fg_color="#122aff", hover_color="#0b1eb3",
                      command=lambda: self.reload_rc_semester(r)
                      ).pack(side="left", padx=5)

        ctk.CTkFrame(rc_card, height=1, fg_color="#cbd5e1").pack(fill="x")

        tbl_scroll = ctk.CTkScrollableFrame(rc_card, fg_color="transparent")
        tbl_scroll.pack(fill="both", expand=True, padx=20, pady=15)

        grid_frame = ctk.CTkFrame(tbl_scroll, fg_color="transparent")
        grid_frame.pack(fill="x")

        # Simplified 4-column layout
        grid_frame.columnconfigure(0, weight=4, uniform="rc_col")
        grid_frame.columnconfigure(1, weight=1, uniform="rc_col")
        grid_frame.columnconfigure(2, weight=1, uniform="rc_col")
        grid_frame.columnconfigure(3, weight=2, uniform="rc_col")

        headers = ["SUBJECT NAME", "NUMERIC GRADE", "LETTER GRADE", "DESCRIPTION"]
        for col_idx, h_text in enumerate(headers):
            tk.Label(grid_frame, text=h_text,
                     font=("Inter", 11, "bold"),
                     fg="#475569", bg="#ffffff"
                     ).grid(row=0, column=col_idx,
                            sticky="ew" if col_idx > 0 else "w",
                            pady=(0, 6))

        conn = database.get_connection()
        cursor = conn.cursor()
        subjects_data_for_pdf = []
        try:
            cursor.execute("""
                SELECT d.detailID, sub.subjectID, sub.subjectName
                FROM REGISTRATION_DETAIL d
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE d.registrationID = ?
                ORDER BY sub.subjectName
            """, (r['registrationID'],))
            subjects = cursor.fetchall()

            for sub_idx, sub in enumerate(subjects):
                row_idx = sub_idx + 1
                row_bg = "#f8fafc" if sub_idx % 2 == 0 else "#ffffff"

                row_frame = tk.Frame(grid_frame, bg=row_bg, bd=0)
                row_frame.grid(row=row_idx, column=0,
                               columnspan=len(headers), sticky="ew", pady=3)
                row_frame.columnconfigure(0, weight=4, uniform="rc_col")
                row_frame.columnconfigure(1, weight=1, uniform="rc_col")
                row_frame.columnconfigure(2, weight=1, uniform="rc_col")
                row_frame.columnconfigure(3, weight=2, uniform="rc_col")

                tk.Label(row_frame, text=sub['subjectName'],
                         font=("Inter", 11, "bold"),
                         fg="#1e293b", bg=row_bg, anchor="w"
                         ).grid(row=0, column=0, sticky="w", padx=10, pady=8)

                # Fetch overall grade
                cursor.execute(
                    "SELECT gradeValue, letterGrade, gradeDesc "
                    "FROM GRADE WHERE detailID = ? AND period = 'Overall'",
                    (sub['detailID'],)
                )
                grade_row = cursor.fetchone()

                if grade_row and grade_row['gradeValue'] is not None:
                    nv = grade_row['gradeValue']
                    letter = (grade_row['letterGrade']
                              or convert_grade(nv)[0])
                    desc   = (grade_row['gradeDesc']
                              or convert_grade(nv)[1])
                    numeric_str  = (f"{int(nv)}" if nv == int(nv) else f"{nv}")
                    grade_color  = "#122aff" if nv >= 75 else "#ef4444"
                else:
                    numeric_str = "—"
                    letter = "—"
                    desc   = "—"
                    grade_color = "#64748b"

                tk.Label(row_frame, text=numeric_str,
                         font=("Inter", 11, "bold"),
                         fg=grade_color, bg=row_bg
                         ).grid(row=0, column=1, pady=8, sticky="ew")
                tk.Label(row_frame, text=letter,
                         font=("Inter", 11, "bold"),
                         fg=grade_color, bg=row_bg
                         ).grid(row=0, column=2, pady=8, sticky="ew")
                tk.Label(row_frame, text=desc,
                         font=("Inter", 11),
                         fg=grade_color, bg=row_bg
                         ).grid(row=0, column=3, pady=8, sticky="ew")

                subjects_data_for_pdf.append({
                    'subjectName': sub['subjectName'],
                    'numeric':     numeric_str,
                    'letter':      letter,
                    'description': desc,
                })

            # Export button
            btn_panel = ctk.CTkFrame(rc_card, fg_color="transparent", height=60)
            btn_panel.pack(fill="x", side="bottom", padx=20, pady=15)
            ctk.CTkButton(
                btn_panel, text="EXPORT STUDENT REPORT CARD (PDF)",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                height=45, fg_color="#122aff", hover_color="#0b1eb3",
                text_color="#ffffff", corner_radius=8,
                command=lambda: self.export_individual_pdf(
                    r, full_name, subjects_data_for_pdf)
            ).pack(side="right")

        except Exception as e:
            print("Error loading student report card:", e)
        finally:
            conn.close()

    def export_individual_pdf(self, r, full_name, subjects_list):
        level = r['level']
        term  = r['term']
        initial_file = (f"Report_Card_{full_name.replace(' ', '_')}"
                        f"_{level.replace(' ', '_')}_{term}.pdf")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=initial_file,
            title="Save Student Report Card PDF"
        )
        if filepath:
            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT tutorFname, tutorLname FROM TUTOR LIMIT 1")
                tutor_row = cursor.fetchone()
                conn.close()

                tutor_name = "—"
                if tutor_row:
                    tutor_name = f"{tutor_row['tutorFname']} {tutor_row['tutorLname']}"

                grades_data = [{
                    'name':      full_name,
                    'studentID': r['learnerID'],
                    'subjects':  subjects_list
                }]
                filter_info = {
                    'subject':      "OFFICIAL STUDENT REPORT CARD",
                    'grade_level':  level,
                    'term':         term,
                    'school_year':  term,
                    'tutor_name':   tutor_name,
                    'date_printed': datetime.now().strftime("%B %d, %Y")
                }
                generate_grades_pdf(filepath, filter_info, grades_data)
                messagebox.showinfo(
                    "Success",
                    f"Student Report Card PDF generated!\nPath: {filepath}")
            except Exception as e:
                messagebox.showerror("Error",
                                     f"Failed to export report card PDF:\n{e}")

    # ─────────────────────────────────────────────────────────────────────────
    # Class grading sheet – load
    # ─────────────────────────────────────────────────────────────────────────
    def load_students(self):
        for w in self.scroll_container.winfo_children():
            w.destroy()

        self.grade_entries.clear()
        self.letter_labels.clear()
        self.desc_labels.clear()
        self.card_widgets.clear()
        self.loaded_students_list = []
        self.is_editable = True
        self.save_btn.configure(state="normal")
        self.edit_btn.pack_forget()

        grade      = self.grade_combo.get()
        batch_disp = self.section_combo.get().strip()
        term       = self.term_combo.get()
 
        if not grade or not batch_disp or not term:
            return
 
        batch_row = self._batch_display_to_row.get(batch_disp)
        if not batch_row:
            messagebox.showwarning("Warning", "Please select a valid batch.")
            return
        batch_id = batch_row.get("batchID")

        loading_lbl = ctk.CTkLabel(
            self.scroll_container,
            text="Loading class grading sheet, please wait...",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color="#122aff"
        )
        loading_lbl.pack(pady=50)
        self.update()

        try:
            conn = database.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT r.registrationID, r.studentID, r.learnerID,
                       s.studLname, s.studFname, s.studMname,
                       d.detailID, sub.subjectID, sub.subjectName,
                       g.gradeValue, g.letterGrade, g.gradeDesc
                FROM REGISTRATION r
                JOIN STUDENT s ON r.studentID = s.studentID
                JOIN REGISTRATION_DETAIL d ON r.registrationID = d.registrationID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                LEFT JOIN GRADE g ON d.detailID = g.detailID
                                  AND g.period = 'Overall'
                WHERE r.level = ? AND d.batchID = ?
                  AND r.term = ? AND r.regStatus = 'Active' AND d.enrollStatus = 'Active'
                ORDER BY s.studLname, s.studFname, sub.subjectName
            """, (grade, batch_id, term))
            rows = cursor.fetchall()
            conn.close()

            loading_lbl.destroy()

            if not rows:
                ctk.CTkLabel(
                    self.scroll_container,
                    text="No enrolled students found for the selected class.",
                    font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                    text_color="#64748b"
                ).pack(pady=40)
                return

            # Group flat rows → student map
            students_map = {}
            for row in rows:
                sid = row['studentID']
                if sid not in students_map:
                    mname  = row['studMname'] or ""
                    middle = f" {mname[0]}." if mname else ""
                    full_n = f"{row['studLname']}, {row['studFname']}{middle}"
                    students_map[sid] = {
                        'studentID':      sid,
                        'learnerID':      row['learnerID'],
                        'name':           full_n,
                        'registrationID': row['registrationID'],
                        'subjects':       {}
                    }
                did = row['detailID']
                if did not in students_map[sid]['subjects']:
                    students_map[sid]['subjects'][did] = {
                        'detailID':    did,
                        'subjectID':   row['subjectID'],
                        'subjectName': row['subjectName'],
                        'gradeValue':  row['gradeValue'],
                        'letterGrade': row['letterGrade'],
                        'gradeDesc':   row['gradeDesc'],
                    }

            # Preserve SQL sort order
            students_list = []
            seen_sids = []
            for row in rows:
                sid = row['studentID']
                if sid not in seen_sids:
                    seen_sids.append(sid)
                    s_data = students_map[sid]
                    s_data['subjects'] = sorted(
                        s_data['subjects'].values(),
                        key=lambda x: x['subjectName'])
                    students_list.append(s_data)

            headers = ["SUBJECT NAME", "NUMERIC GRADE", "LETTER GRADE", "DESCRIPTION"]

            for student in students_list:
                card = ctk.CTkFrame(self.scroll_container, fg_color="#ffffff",
                                    corner_radius=16, border_width=1,
                                    border_color="#cbd5e1")
                card.pack(fill="x", pady=8, padx=10)

                self.card_widgets.append({
                    "learnerID": student['learnerID'],
                    "name":      student['name'].lower(),
                    "widget":    card
                })

                # Student header badge
                hdr = ctk.CTkFrame(card, fg_color="#15165e", corner_radius=8, height=44)
                hdr.pack(fill="x", side="top", padx=10, pady=(10, 5))
                hdr.pack_propagate(False)
                ctk.CTkLabel(
                    hdr,
                    text=(f"{student['name'].upper()}"
                          f"  (Learner ID: {student['learnerID']})"),
                    font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                    text_color="#ffffff",
                ).pack(side="left", padx=12, pady=4)
                ctk.CTkButton(
                    hdr, text="View Profile",
                    font=ctk.CTkFont(family="Inter", size=10, weight="bold"),
                    width=110, height=28, corner_radius=6,
                    fg_color="#ffffff", hover_color="#e0e7ff",
                    text_color="#15165e",
                    command=lambda sid=student['studentID'], lid=student['learnerID']:
                        self.show_student_detail_popup(sid, lid)
                ).pack(side="right", padx=10, pady=8)

                grid_frame = ctk.CTkFrame(card, fg_color="transparent")
                grid_frame.pack(fill="x", padx=15, pady=15)

                grid_frame.columnconfigure(0, weight=4, uniform="grade_col")
                grid_frame.columnconfigure(1, weight=1, uniform="grade_col")
                grid_frame.columnconfigure(2, weight=1, uniform="grade_col")
                grid_frame.columnconfigure(3, weight=2, uniform="grade_col")

                for col_idx, h_text in enumerate(headers):
                    tk.Label(grid_frame, text=h_text,
                             font=("Inter", 11, "bold"),
                             fg="#475569", bg="#ffffff"
                             ).grid(row=0, column=col_idx,
                                    sticky="ew" if col_idx > 0 else "w",
                                    pady=(0, 6))

                student_subjects_data = []

                for sub_idx, sub in enumerate(student['subjects']):
                    row_idx = sub_idx + 1
                    row_bg  = "#f8fafc" if sub_idx % 2 == 0 else "#ffffff"

                    row_frame = tk.Frame(grid_frame, bg=row_bg, bd=0)
                    row_frame.grid(row=row_idx, column=0,
                                   columnspan=len(headers), sticky="ew", pady=3)
                    row_frame.columnconfigure(0, weight=4, uniform="grade_col")
                    row_frame.columnconfigure(1, weight=1, uniform="grade_col")
                    row_frame.columnconfigure(2, weight=1, uniform="grade_col")
                    row_frame.columnconfigure(3, weight=2, uniform="grade_col")

                    tk.Label(row_frame, text=sub['subjectName'],
                             font=("Inter", 11, "bold"),
                             fg="#1e293b", bg=row_bg, anchor="w"
                             ).grid(row=0, column=0, sticky="w", padx=10, pady=6)

                    # Auto letter & description labels
                    lbl_letter = tk.Label(row_frame, text="—",
                                          font=("Inter", 11, "bold"),
                                          fg="#64748b", bg=row_bg)
                    lbl_letter.grid(row=0, column=2, pady=6, sticky="ew")

                    lbl_desc = tk.Label(row_frame, text="—",
                                        font=("Inter", 11),
                                        fg="#64748b", bg=row_bg)
                    lbl_desc.grid(row=0, column=3, pady=6, sticky="ew")

                    self.letter_labels[sub['detailID']] = lbl_letter
                    self.desc_labels[sub['detailID']]   = lbl_desc

                    # Numeric entry
                    ent = tk.Entry(row_frame,
                                   bg="#ffffff", fg="black",
                                   relief="flat", bd=0,
                                   highlightthickness=1,
                                   highlightcolor="#122aff",
                                   highlightbackground="#cbd5e1",
                                   font=("Inter", 11),
                                   justify="center",
                                   width=7)
                    ent.grid(row=0, column=1, pady=6, sticky="ew", padx=5)

                    # Pre-fill existing grade
                    existing_val = sub['gradeValue']
                    if existing_val is not None:
                        ent.insert(
                            0,
                            f"{int(existing_val) if existing_val == int(existing_val) else existing_val}"
                        )
                        letter, desc = convert_grade(existing_val)
                        gc = "#122aff" if existing_val >= 75 else "#ef4444"
                        lbl_letter.configure(text=letter, fg=gc)
                        lbl_desc.configure(text=desc,   fg=gc)

                    self.grade_entries[sub['detailID']] = ent
                    ent.bind(
                        "<KeyRelease>",
                        lambda e,
                               d_id=sub['detailID'],
                               ll=lbl_letter,
                               dl=lbl_desc: self.update_grade_display(d_id, ll, dl)
                    )

                    student_subjects_data.append({
                        "subjectID":    sub['subjectID'],
                        "subjectName":  sub['subjectName'],
                        "detailID":     sub['detailID'],
                        "entry":        ent,
                        "letter_label": lbl_letter,
                        "desc_label":   lbl_desc,
                    })

                self.loaded_students_list.append({
                    "learnerID":      student['learnerID'],
                    "name":           student['name'],
                    "registrationID": student['registrationID'],
                    "subjects":       student_subjects_data
                })

            self.filter_class_sheet()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load grading sheet:\n{e}")

    # ─────────────────────────────────────────────────────────────────────────
    # Real-time grade conversion
    # ─────────────────────────────────────────────────────────────────────────
    def update_grade_display(self, detail_id, lbl_letter, lbl_desc):
        """Called on every keystroke – instantly converts numeric → letter/desc."""
        ent = self.grade_entries.get(detail_id)
        if not ent:
            return
        val_str = ent.get().strip()
        if val_str:
            try:
                val = float(val_str)
                if 0 <= val <= 100:
                    letter, desc = convert_grade(val)
                    gc = "#122aff" if val >= 75 else "#ef4444"
                    lbl_letter.configure(text=letter, fg=gc)
                    lbl_desc.configure(text=desc,   fg=gc)
                    return
            except ValueError:
                pass
        lbl_letter.configure(text="—", fg="#64748b")
        lbl_desc.configure(text="—",   fg="#64748b")

    def filter_class_sheet(self, event=None):
        query = self.class_search_entry.get().strip().lower()
        for item in self.card_widgets:
            if (not query
                    or query in str(item['learnerID']).lower()
                    or query in item['name']):
                item['widget'].pack(fill="x", pady=8, padx=10)
            else:
                item['widget'].pack_forget()

    # ─────────────────────────────────────────────────────────────────────────
    # Save / lock / unlock
    # ─────────────────────────────────────────────────────────────────────────
    def save_grades(self):
        if not self.grade_entries:
            messagebox.showwarning("Warning", "No grades loaded to save.")
            return

        conn   = database.get_connection()
        cursor = conn.cursor()
        saved  = 0
        errors = []

        try:
            tutor_id = self.tutor_id
            if not tutor_id:
                cursor.execute("SELECT tutorID FROM TUTOR LIMIT 1")
                tutor_row = cursor.fetchone()
                tutor_id  = tutor_row['tutorID'] if tutor_row else 1

            for detail_id, ent in self.grade_entries.items():
                val_str = ent.get().strip()
                if not val_str:
                    cursor.execute(
                        "DELETE FROM GRADE WHERE detailID = ? AND period = 'Overall'",
                        (detail_id,)
                    )
                    continue

                try:
                    val = float(val_str)
                    if not (0 <= val <= 100):
                        raise ValueError()
                except ValueError:
                    errors.append(f"Invalid grade: '{val_str}'")
                    continue

                letter, desc = convert_grade(val)

                cursor.execute("""
                    INSERT INTO GRADE
                        (detailID, tutorID, period, gradeValue,
                         letterGrade, gradeDesc, dateRecorded)
                    VALUES (?, ?, 'Overall', ?, ?, ?, ?)
                    ON CONFLICT(detailID, period) DO UPDATE SET
                        gradeValue   = excluded.gradeValue,
                        letterGrade  = excluded.letterGrade,
                        gradeDesc    = excluded.gradeDesc,
                        dateRecorded = excluded.dateRecorded
                """, (detail_id, tutor_id, val, letter, desc,
                      datetime.now().strftime("%Y-%m-%d")))
                saved += 1

            conn.commit()
            self.lock_grades()

            SuccessPopup(self.winfo_toplevel(), "Grades Saved", f"Successfully saved {saved} grade record(s).", "\n".join(errors) if errors else None)

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to save grades:\n{e}")
        finally:
            conn.close()

    def lock_grades(self):
        self.is_editable = False
        for ent in self.grade_entries.values():
            ent.configure(state="disabled",
                          bg="#f1f5f9", fg="#334155",
                          disabledbackground="#f1f5f9",
                          disabledforeground="#334155")
        self.save_btn.configure(state="disabled")
        self.edit_btn.pack(side="right", padx=(10, 0))

    def unlock_grades(self):
        self.is_editable = True
        for ent in self.grade_entries.values():
            ent.configure(state="normal", bg="#ffffff", fg="black")
        self.save_btn.configure(state="normal")
        self.edit_btn.pack_forget()

    # ─────────────────────────────────────────────────────────────────────────
    # PDF export (class sheet)
    # ─────────────────────────────────────────────────────────────────────────
    def export_grades_pdf(self):
        if not hasattr(self, 'loaded_students_list') or not self.loaded_students_list:
            messagebox.showwarning("Warning", "No students loaded to export.")
            return

        grade_lvl  = self.grade_combo.get()
        batch_disp = self.section_combo.get()
        term       = self.term_combo.get()

        batch_row = self._batch_display_to_row.get(batch_disp)
        subject_name = batch_row.get("subjectName") if batch_row else "Grade_Sheet"
        clean_subj_name = subject_name.replace(' ', '_')

        initial_file = (f"Grade_Sheet_{grade_lvl.replace(' ', '_')}"
                        f"_{clean_subj_name}_{term}.pdf")
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=initial_file,
            title="Save Class Grade Sheet PDF"
        )

        if filepath:
            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT tutorFname, tutorLname FROM TUTOR LIMIT 1")
                tutor_row = cursor.fetchone()
                conn.close()

                tutor_name = "—"
                if tutor_row:
                    tutor_name = (f"{tutor_row['tutorFname']}"
                                  f" {tutor_row['tutorLname']}")

                grades_data = []
                for s in self.loaded_students_list:
                    subjects_list = []
                    for sub in s['subjects']:
                        val_str = sub['entry'].get().strip()
                        letter  = sub['letter_label'].cget("text")
                        desc    = sub['desc_label'].cget("text")
                        subjects_list.append({
                            'subjectName': sub['subjectName'],
                            'numeric':     val_str if val_str else "—",
                            'letter':      letter,
                            'description': desc,
                        })
                    grades_data.append({
                        'name':      s['name'],
                        'studentID': s['learnerID'],
                        'subjects':  subjects_list
                    })

                filter_info = {
                    'subject':      f"{subject_name} ({batch_row.get('batchLabel') if batch_row else ''})",
                    'grade_level':  grade_lvl,
                    'term':         term,
                    'school_year':  term,
                    'tutor_name':   tutor_name,
                    'date_printed': datetime.now().strftime("%B %d, %Y")
                }

                generate_grades_pdf(filepath, filter_info, grades_data)
                messagebox.showinfo(
                    "Success",
                    f"Official Grade Sheet PDF generated!\nPath: {filepath}")

            except Exception as e:
                messagebox.showerror("Error",
                                     f"Failed to export Grade Sheet PDF:\n{e}")

    # ─────────────────────────────────────────────────────────────────────────
    def show_student_detail_popup(self, student_id, learner_id=None):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT studentID, studLname, studFname, studMname, gender, dob, address, studContactNo, studEmail, level
                FROM STUDENT WHERE studentID = ?
            """, (student_id,))
            student = cursor.fetchone()
            if learner_id is None:
                cursor.execute("""
                    SELECT r.learnerID FROM REGISTRATION r
                    WHERE r.studentID = ? AND r.regStatus = 'Active'
                    ORDER BY r.registrationID DESC LIMIT 1
                """, (student_id,))
                reg = cursor.fetchone()
                learner_id = reg['learnerID'] if reg else "N/A"
            cursor.execute("""
                SELECT parName, parContactNo, parEmail, relationship
                FROM PARENT WHERE studentID = ?
            """, (student_id,))
            parent = cursor.fetchone()
            conn.close()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Database Error", f"Failed to retrieve student details: {e}")
            return

        if not student:
            from tkinter import messagebox
            messagebox.showerror("Error", "Student not found.")
            return

        popup = ctk.CTkToplevel(self)
        popup.title(f"Student Profile - {student['studFname']} {student['studLname']}")
        popup.geometry("680x530")
        popup.resizable(False, False)
        popup.configure(fg_color="#e4e4e4")
        popup.transient(self.winfo_toplevel())
        x = (popup.winfo_screenwidth() - 680) // 2
        y = (popup.winfo_screenheight() - 530) // 2
        popup.geometry(f"680x530+{x}+{y}")
        try:
            popup.grab_set()
        except Exception:
            pass

        top_bar = ctk.CTkFrame(popup, height=60, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)
        ctk.CTkLabel(top_bar,
                     text=f"STUDENT PROFILE: {student['studFname'].upper()} {student['studLname'].upper()}",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                     text_color="#ffffff").pack(side="left", padx=20, pady=15)

        container = ctk.CTkFrame(popup, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=25, pady=15)

        def create_card(parent_w, title):
            card = ctk.CTkFrame(parent_w, fg_color="#ffffff", corner_radius=12,
                                border_width=1, border_color="#cbd5e1")
            card.pack(fill="x", pady=(0, 15))
            acc = ctk.CTkFrame(card, width=5, fg_color="transparent")
            acc.pack(side="left", fill="y", padx=(10, 0), pady=10)
            ctk.CTkFrame(acc, width=5, fg_color="#15165e", corner_radius=2.5).pack(fill="both", expand=True)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=10)
            ctk.CTkLabel(inner, text=title,
                         font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                         text_color="#15165e").pack(anchor="w", pady=(0, 8))
            return inner

        def add_row(parent_w, grid_w, row_idx, label, val):
            rf = ctk.CTkFrame(grid_w, fg_color="transparent")
            rf.grid(row=row_idx // 2, column=row_idx % 2, sticky="ew", pady=3, padx=5)
            ctk.CTkLabel(rf, text=f"{label}:",
                         font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                         text_color="#64748b", width=105, anchor="w").pack(side="left")
            ctk.CTkLabel(rf, text=str(val),
                         font=ctk.CTkFont(family="Inter", size=12),
                         text_color="#0f172a", anchor="w").pack(side="left", fill="x", expand=True)

        stud_inner = create_card(container, "STUDENT INFORMATION")
        grid_s = ctk.CTkFrame(stud_inner, fg_color="transparent")
        grid_s.pack(fill="x")
        grid_s.columnconfigure(0, weight=1)
        grid_s.columnconfigure(1, weight=1)
        add_row(stud_inner, grid_s, 0, "Learner ID", learner_id)
        add_row(stud_inner, grid_s, 1, "Full Name",
                f"{student['studLname']}, {student['studFname']} {student['studMname'] or ''}")
        add_row(stud_inner, grid_s, 2, "Grade Level", student['level'] or "Unassigned")
        add_row(stud_inner, grid_s, 3, "Gender", student['gender'])
        add_row(stud_inner, grid_s, 4, "Date of Birth", student['dob'])
        add_row(stud_inner, grid_s, 5, "Contact No", student['studContactNo'] or "\u2014")
        add_row(stud_inner, grid_s, 6, "Email Address", student['studEmail'] or "\u2014")
        addr_f = ctk.CTkFrame(stud_inner, fg_color="transparent")
        addr_f.pack(fill="x", pady=(8, 0), padx=5)
        ctk.CTkLabel(addr_f, text="Full Address:",
                     font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                     text_color="#64748b", width=105, anchor="w").pack(side="left")
        ctk.CTkLabel(addr_f, text=student['address'] or "\u2014",
                     font=ctk.CTkFont(family="Inter", size=12),
                     text_color="#0f172a", anchor="w", wraplength=480).pack(side="left", fill="x", expand=True)

        par_inner = create_card(container, "PARENT / GUARDIAN INFORMATION")
        if parent:
            grid_p = ctk.CTkFrame(par_inner, fg_color="transparent")
            grid_p.pack(fill="x")
            grid_p.columnconfigure(0, weight=1)
            grid_p.columnconfigure(1, weight=1)
            add_row(par_inner, grid_p, 0, "Parent Name", parent['parName'])
            add_row(par_inner, grid_p, 1, "Relationship", parent['relationship'])
            add_row(par_inner, grid_p, 2, "Contact No", parent['parContactNo'] or "\u2014")
            add_row(par_inner, grid_p, 3, "Email Address", parent['parEmail'] or "\u2014")
        else:
            ctk.CTkLabel(par_inner,
                         text="No parent/guardian information found.",
                         font=ctk.CTkFont(family="Inter", size=12, slant="italic"),
                         text_color="#ef4444").pack(anchor="w", pady=5)

        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(5, 15))
        ctk.CTkButton(btn_frame, text="CLOSE PROFILE",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      fg_color="#374151", hover_color="#1f2937", text_color="#ffffff",
                      width=160, height=38, corner_radius=8,
                      command=popup.destroy).pack(anchor="center")

    # ─────────────────────────────────────────────────────────────────────────
    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()