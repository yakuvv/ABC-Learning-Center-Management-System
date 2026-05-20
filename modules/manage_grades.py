import customtkinter as ctk
from tkinter import messagebox, ttk
import database
from datetime import datetime


class ManageGrades(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.grade_entries = {}
        self.create_ui()

    #shared widget factories

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

    def _card(self, parent, height=None):
        kw = {"height": height} if height else {}
        card = ctk.CTkFrame(parent, fg_color="#cbd5e1", corner_radius=0, **kw)
        ctk.CTkFrame(card, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=10)
        return card, inner

    #UI
    def create_ui(self):
        #Top bar
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkButton(top_bar, text="← back to Dashboard",
                      font=ctk.CTkFont(family="Inter", size=14),
                      fg_color="transparent", text_color="#ffffff",
                      hover_color="#22259c", width=150, height=40,
                      corner_radius=0, command=self.back_to_dashboard
                      ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(top_bar, text="Manage Grades",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        ctk.CTkLabel(top_bar, text="ABC",
                     font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                     text_color="#122aff").pack(side="right", padx=30)

        #Workspace
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        #Filtering rows
        ctk.CTkLabel(main_frame, text="Filter Class",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 4))

        filter_card, filter_inner = self._card(main_frame, height=80)
        filter_card.pack(fill="x", pady=(0, 6))
        filter_card.pack_propagate(False)

        for col in range(4):
            filter_inner.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(filter_inner, text="Subject",
                     font=ctk.CTkFont(family="Inter", size=12),
                     text_color="#444444").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.subject_combo = self._combo(filter_inner, self._load_subject_list())
        self.subject_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(filter_inner, text="Grade Level",
                     font=ctk.CTkFont(family="Inter", size=12),
                     text_color="#444444").grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.grade_combo = self._combo(filter_inner,
            ["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6",
             "Grade 7","Grade 8","Grade 9","Grade 10","Grade 11","Grade 12"])
        self.grade_combo.set("Grade 7")
        self.grade_combo.grid(row=1, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(filter_inner, text="Term",
                     font=ctk.CTkFont(family="Inter", size=12),
                     text_color="#444444").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.term_combo = self._combo(filter_inner,
            ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"])
        self.term_combo.set("1st Quarter")
        self.term_combo.grid(row=1, column=2, sticky="ew", padx=(0, 8))

        ctk.CTkLabel(filter_inner, text="School Year",
                     font=ctk.CTkFont(family="Inter", size=12),
                     text_color="#444444").grid(row=0, column=3, sticky="w")
        self.sy_combo = self._combo(filter_inner,
            ["2018-2019","2019-2020","2024-2025","2025-2026"])
        self.sy_combo.set("2025-2026")
        self.sy_combo.grid(row=1, column=3, sticky="ew")

        ctk.CTkButton(main_frame, text="LOAD STUDENTS",
                      font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                      height=38, corner_radius=0,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.load_students
                      ).pack(anchor="e", pady=(4, 12))

        #Grade Sheet table
        ctk.CTkLabel(main_frame, text="Grade Sheet",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 4))

        table_outer = ctk.CTkFrame(main_frame, fg_color="#cbd5e1", corner_radius=0)
        table_outer.pack(fill="both", expand=True)

        ctk.CTkFrame(table_outer, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")

        self.grade_scroll = ctk.CTkScrollableFrame(
            table_outer, fg_color="#ffffff", corner_radius=0)
        self.grade_scroll.pack(fill="both", expand=True, padx=(0, 4), pady=4)

        #Column headers
        hdr = ctk.CTkFrame(self.grade_scroll, fg_color="#15165e", corner_radius=0, height=36)
        hdr.pack(fill="x", pady=(0, 4))
        hdr.pack_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(hdr, text="#", width=40,
                     font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                     text_color="#ffffff").grid(row=0, column=0, padx=(10, 0), pady=6)
        ctk.CTkLabel(hdr, text="STUDENT NAME",
                     font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                     text_color="#ffffff", anchor="w"
                     ).grid(row=0, column=1, sticky="ew", padx=10, pady=6)
        ctk.CTkLabel(hdr, text="GRADE", width=120,
                     font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                     text_color="#ffffff").grid(row=0, column=2, padx=(0, 10), pady=6)

        self.rows_container = ctk.CTkFrame(self.grade_scroll, fg_color="transparent")
        self.rows_container.pack(fill="x")

        #Bottom controls
        bottom = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom.pack(fill="x", pady=(10, 0))

        ctk.CTkButton(bottom, text="SAVE ALL GRADES",
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      height=45, width=200, corner_radius=0,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.save_grades
                      ).pack(side="right")

        self.load_students()

    #Helpers

    def _load_subject_list(self):
        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT subjectName FROM SUBJECT ORDER BY subjectName")
            names = [r['subjectName'] for r in cursor.fetchall()]
            conn.close()
            return names if names else ["Mathematics", "Science", "English"]
        except Exception:
            return ["Mathematics", "Science", "English"]

    #Load Students

    def load_students(self):
        for w in self.rows_container.winfo_children():
            w.destroy()
        self.grade_entries.clear()
        self.rows_container.grid_columnconfigure(1, weight=1)

        try:
            conn = database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT s.studentID, s.studLname, s.studFname, s.studMname,
                       d.detailID
                FROM STUDENT s
                JOIN ENROLLMENT e ON s.studentID = e.studentID
                JOIN DETAIL d ON e.enrollmentID = d.enrollmentID
                JOIN SUBJECT sub ON d.subjectID = sub.subjectID
                WHERE sub.subjectName LIKE ?
                  AND e.gradeLevel LIKE ?
                  AND e.term = ?
                  AND e.schoolYear = ?
                ORDER BY s.studLname, s.studFname
            """, (
                f"%{self.subject_combo.get()}%",
                f"%{self.grade_combo.get()}%",
                self.term_combo.get(),
                self.sy_combo.get()
            ))
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            print("load_students error:", e)
            rows = []

        if not rows:
            rows = [
                {"studentID": 1001, "studLname": "Carias",
                 "studFname": "Angelyn", "studMname": "F", "detailID": None},
                {"studentID": 1002, "studLname": "Dela Cruz",
                 "studFname": "Juan", "studMname": None, "detailID": None},
                {"studentID": 1003, "studLname": "Santos",
                 "studFname": "Maria", "studMname": "L", "detailID": None},
            ]

        for idx, row in enumerate(rows):
            mname  = row['studMname'] or ""
            middle = f" {mname[0]}." if mname else ""
            full   = f"{row['studLname']}, {row['studFname']}{middle}"

            bg_color = "#f8fafc" if idx % 2 == 0 else "#f1f5f9"

            row_frame = ctk.CTkFrame(self.rows_container, fg_color=bg_color,
                                     corner_radius=0, height=42)
            row_frame.pack(fill="x", pady=1)
            row_frame.pack_propagate(False)
            row_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row_frame, text=str(idx + 1), width=40,
                         font=ctk.CTkFont(family="Inter", size=13),
                         text_color="#374151").grid(row=0, column=0, padx=(10, 0), pady=8)

            ctk.CTkLabel(row_frame, text=full,
                         font=ctk.CTkFont(family="Inter", size=13),
                         text_color="#111827", anchor="w"
                         ).grid(row=0, column=1, sticky="ew", padx=10, pady=8)

            grade_entry = ctk.CTkEntry(
                row_frame,
                placeholder_text="e.g. 90",
                width=110, height=30,
                corner_radius=0,
                fg_color="#ffffff",
                text_color="black",
                border_width=1,
                border_color="#cbd5e1"
            )
            grade_entry.grid(row=0, column=2, padx=(0, 10), pady=6)

            self.grade_entries[row['detailID']] = (grade_entry, row['studentID'])

    #Save Grades

    def save_grades(self):
        if not self.grade_entries:
            messagebox.showwarning("Empty", "No students loaded to save grades for.")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        saved  = 0
        errors = []

        try:
            cursor.execute("SELECT tutorID FROM TUTOR LIMIT 1")
            tutor_row = cursor.fetchone()
            tutor_id  = tutor_row['tutorID'] if tutor_row else 1

            for detail_id, (entry_widget, student_id) in self.grade_entries.items():
                raw = entry_widget.get().strip()
                if not raw:
                    continue
                try:
                    grade_val = float(raw)
                except ValueError:
                    errors.append(f"Student #{student_id}: invalid value '{raw}'")
                    continue

                if detail_id is not None:
                    cursor.execute("""
                        INSERT INTO GRADE (detailID, tutorID, gradeValue, dateRecorded)
                        VALUES (?, ?, ?, ?)
                    """, (detail_id, tutor_id, grade_val,
                          datetime.now().strftime("%Y-%m-%d")))
                    saved += 1

            conn.commit()

            msg = f"Saved {saved} grade(s) successfully."
            if errors:
                msg += "\n\nSkipped (invalid):\n" + "\n".join(errors)
            messagebox.showinfo("Grades Saved", msg)

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    #Navigation

    def back_to_dashboard(self):
        parent_frame = self.master
        self.destroy()
        if hasattr(parent_frame, "welcome_lbl"):
            parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(parent_frame.master, "welcome_lbl"):
            parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))