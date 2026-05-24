import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from PIL import Image
import subprocess
import database
import config
from utils.pdf_generator import generate_receipt_pdf
from utils.modern_entry import ModernEntry
from utils.modern_combo import ModernCombo

class ProcessPayment(ctk.CTkFrame):
    def __init__(self, parent, user_role="Admin/Staff", user_id=None):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user_role = user_role
        self.user_id = user_id
        self.current_registration_id = None
        self.current_student_data = None
        self._suggestions_rows = []

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.create_ui()

    # Shared widget factories
    def _entry(self, parent, placeholder, **kwargs):
        return ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=40, corner_radius=8,
            fg_color="#ffffff", text_color="#1e293b",
            border_width=1, border_color="#cbd5e1",
            font=ctk.CTkFont(family="Inter", size=13),
            **kwargs
        )

    def _combo(self, parent, values, **kwargs):
        return ModernCombo(parent, values=values, **kwargs)

    def _card(self, parent, height=None):
        """Slate card with left accent. Returns (card, inner)."""
        kw = {"height": height} if height else {}
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", **kw)

        accent_container = ctk.CTkFrame(card, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)

        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)
        return card, inner

    def create_ui(self):
        # Top bar
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkButton(
            top_bar, text="← back to Dashboard",
            font=ctk.CTkFont(family="Inter", size=14),
            fg_color="transparent", text_color="#ffffff",
            hover_color="#22259c", width=150, height=40,
            corner_radius=8, command=self.back_to_dashboard
        ).pack(side="left", padx=20, pady=15)

        ctk.CTkLabel(
            top_bar, text="Process Payment",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", expand=True, padx=(0, 100))

        logo_path = os.path.abspath("assets/logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(55, 55))
                ctk.CTkLabel(top_bar, image=ctk_logo, text="").pack(side="right", padx=30)
            except Exception:
                ctk.CTkLabel(top_bar, text="ABC", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#ffffff").pack(side="right", padx=30)
        else:
            ctk.CTkLabel(top_bar, text="ABC", font=ctk.CTkFont(family="Inter", size=18, weight="bold"), text_color="#ffffff").pack(side="right", padx=30)

        # Workspace Grid Layout
        workspace = ctk.CTkFrame(self, fg_color="transparent")
        workspace.pack(fill="both", expand=True, padx=40, pady=25)
        workspace.columnconfigure(0, weight=1, uniform="workspace_col")
        workspace.columnconfigure(1, weight=1, uniform="workspace_col")

        # --- LEFT COLUMN: SEARCH & ENROLLEE DETAILS ---
        left_col = ctk.CTkFrame(workspace, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        ctk.CTkLabel(
            left_col, text="SEARCH STUDENT ENROLLMENT",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1e293b"
        ).pack(anchor="w", pady=(0, 6))

        # Search Card
        search_card, search_inner = self._card(left_col)
        search_card.pack(fill="x", pady=(0, 12))

        self.search_entry = ModernEntry(search_inner, placeholder_text="Type Student ID, Name, or Learner ID...",
                                        height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.search_entry.pack(fill="x", pady=2)
        self.search_entry.bind("<KeyRelease>", self._on_search_key)
        self.search_entry.bind("<FocusOut>", lambda _: self.after(250, self._hide_suggestions))

        # Autocomplete Suggestion Listbox Frame
        self.suggest_frame = ctk.CTkFrame(left_col, fg_color="#ffffff", corner_radius=10, border_width=1, border_color="#cbd5e1")
        self.suggest_lbox = tk.Listbox(
            self.suggest_frame,
            bg="#ffffff", fg="#1e293b",
            selectbackground="#122aff", selectforeground="#ffffff",
            font=("Inter", 12), borderwidth=0, highlightthickness=0, height=5, activestyle="none"
        )
        self.suggest_lbox.pack(fill="x", padx=8, pady=8)
        self.suggest_lbox.bind("<<ListboxSelect>>", self._on_suggestion_select)

        # Info Display Card
        ctk.CTkLabel(
            left_col, text="ENROLLEE INFORMATION",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1e293b"
        ).pack(anchor="w", pady=(10, 6))

        self.info_card, self.info_inner = self._card(left_col)
        self.info_card.pack(fill="both", expand=True)

        self.info_placeholder = ctk.CTkLabel(
            self.info_inner,
            text="Please search and select a student above\nto load enrollment & status details.",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#64748b",
            justify="center"
        )
        self.info_placeholder.pack(expand=True, pady=40)

        # --- RIGHT COLUMN: PAYMENT DETAILS ---
        right_col = ctk.CTkFrame(workspace, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        ctk.CTkLabel(
            right_col, text="PAYMENT SETTINGS",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1e293b"
        ).pack(anchor="w", pady=(0, 6))

        pay_card, pay_inner = self._card(right_col)
        pay_card.pack(fill="x", pady=(0, 20))
        pay_inner.columnconfigure(1, weight=1)

        # Amount Input
        ctk.CTkLabel(
            pay_inner, text="Amount (₱)",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#1e293b"
        ).grid(row=0, column=0, sticky="w", pady=12)
        self.amount_entry = ModernEntry(pay_inner, placeholder_text="e.g. 1500.00",
                                        height=32, font=ctk.CTkFont(family="Inter", size=13))
        self.amount_entry.grid(row=0, column=1, sticky="ew", padx=(20, 0), pady=12)

        # Payment Method Dropdown
        ctk.CTkLabel(
            pay_inner, text="Payment Method",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#1e293b"
        ).grid(row=1, column=0, sticky="w", pady=12)
        self.method_combo = self._combo(pay_inner, ["Cash", "GCash", "Bank Transfer"])
        self.method_combo.set("Cash")
        self.method_combo.grid(row=1, column=1, sticky="ew", padx=(20, 0), pady=12)

        # Actions Panel
        self.record_btn = ctk.CTkButton(
            right_col,
            text="RECORD PAYMENT & GENERATE RECEIPT",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            height=52, corner_radius=8,
            fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
            command=self.process_payment
        )
        self.record_btn.pack(fill="x", pady=(10, 10))

        self.clear_btn = ctk.CTkButton(
            right_col,
            text="CLEAR FORM",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            height=40, corner_radius=8,
            fg_color="#cbd5e1", hover_color="#94a3b8", text_color="#1e293b",
            command=self.clear_form
        )
        self.clear_btn.pack(fill="x")

    def _on_search_key(self, event):
        kw = self.search_entry.get().strip()
        if not kw:
            self._hide_suggestions()
            return

        try:
            kid = int(kw)
        except ValueError:
            kid = -1

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.registrationID, r.learnerID, r.level, r.groupName, r.term,
                   s.studentID, s.studFname, s.studLname, s.studMname
            FROM REGISTRATION r
            JOIN STUDENT s ON r.studentID = s.studentID
            WHERE r.learnerID LIKE ?
               OR s.studentID = ?
               OR s.studFname LIKE ?
               OR s.studLname LIKE ?
               OR (s.studFname || ' ' || s.studLname) LIKE ?
            ORDER BY r.registrationID DESC
            LIMIT 8
        """, (f"%{kw}%", kid, f"%{kw}%", f"%{kw}%", f"%{kw}%"))
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()

        if rows:
            self._suggestions_rows = rows
            self.suggest_lbox.delete(0, tk.END)
            for r in rows:
                mname = f" {r['studMname'][0]}." if r.get('studMname') else ""
                lbl = f" {r['studFname']}{mname} {r['studLname']}  (Learner ID: {r['learnerID'] or '—'} | {r['level'] or '—'} - {r['groupName'] or '—'})"
                self.suggest_lbox.insert(tk.END, lbl)
            self.suggest_lbox.config(height=min(len(rows), 6))
            self.suggest_frame.pack(fill="x", after=self.search_entry, pady=(4, 0))
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
        self.select_registration(row)
        self.search_entry.delete(0, tk.END)
        self._hide_suggestions()

    def select_registration(self, r):
        self.current_registration_id = r['registrationID']
        self.current_student_data = r

        for w in self.info_inner.winfo_children():
            w.destroy()

        mname = f" {r['studMname'][0]}." if r.get('studMname') else ""
        full_name = f"{r['studFname']}{mname} {r['studLname']}"

        details_frame = ctk.CTkFrame(self.info_inner, fg_color="transparent")
        details_frame.pack(fill="both", expand=True)

        info_items = [
            ("Learner ID", r['learnerID'] or "—"),
            ("Student Name", full_name),
            ("Level & Group", f"{r['level'] or '—'} - {r['groupName'] or '—'}"),
            ("Term", r['term'] or "—")
        ]

        for i, (label, val) in enumerate(info_items):
            lbl_title = ctk.CTkLabel(
                details_frame, text=f"{label}:",
                font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
                text_color="#15165e"
            )
            lbl_title.grid(row=i, column=0, sticky="w", pady=6)

            lbl_val = ctk.CTkLabel(
                details_frame, text=val,
                font=ctk.CTkFont(family="Inter", size=13),
                text_color="#1e293b"
            )
            lbl_val.grid(row=i, column=1, sticky="w", padx=(20, 0), pady=6)

    def process_payment(self):
        if not self.current_registration_id:
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        try:
            amount = float(self.amount_entry.get().strip() or 0)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid payment amount greater than 0.")
            return

        method = self.method_combo.get()
        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO PAYMENT (registrationID, amount, payMethod, payStatus)
                VALUES (?, ?, ?, 'Paid')
            """, (self.current_registration_id, amount, method))

            payment_id = cursor.lastrowid
            receipt_num = f"REC-{datetime.now().strftime('%Y%m%d')}-{payment_id:04d}"

            cursor.execute(
                "INSERT INTO RECEIPT (paymentID, receiptNumber) VALUES (?, ?)",
                (payment_id, receipt_num)
            )
            conn.commit()

            r = self.current_student_data
            mname = f" {r['studMname'][0]}." if r.get('studMname') else ""
            student_name = f"{r['studFname']}{mname} {r['studLname']}"

            # Modern Auto-save Receipt PDF flow
            receipts_dir = os.path.abspath("receipts")
            os.makedirs(receipts_dir, exist_ok=True)
            filepath = os.path.join(receipts_dir, f"Receipt_{receipt_num}.pdf")

            receipt_data = {
                'receipt_number': receipt_num,
                'date': datetime.now().strftime("%B %d, %Y - %I:%M %p"),
                'amount': amount,
                'method': method,
                'student_name': student_name,
                'school_id': r['learnerID'] or "—",
                'grade_level': r['level'] or "—",
                'term': r['term'] or "—",
                'school_year': r['term'] or "—"
            }
            generate_receipt_pdf(filepath, receipt_data)

            # Show the beautiful, modern success modal
            self.show_success_modal(receipt_num, amount, method, filepath, receipts_dir)
            self.clear_form()

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to record payment:\n{str(e)}")
        finally:
            conn.close()

    def show_success_modal(self, receipt_num, amount, method, filepath, folderpath):
        modal = ReceiptSuccessModal(self, receipt_num, amount, method, filepath, folderpath)
        self.wait_window(modal)

    def clear_form(self):
        self.search_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.method_combo.set("Cash")
        self.current_registration_id = None
        self.current_student_data = None

        for w in self.info_inner.winfo_children():
            w.destroy()

        self.info_placeholder = ctk.CTkLabel(
            self.info_inner,
            text="Please search and select a student above\to load enrollment & status details.",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#64748b",
            justify="center"
        )
        self.info_placeholder.pack(expand=True, pady=40)

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()


class ReceiptSuccessModal(ctk.CTkToplevel):
    def __init__(self, parent, receipt_num, amount, method, filepath, folderpath):
        super().__init__(parent)
        self.title("Payment Recorded Successfully")
        self.geometry("520x400")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        self.filepath = filepath
        self.folderpath = folderpath
        
        # Ensure window is mapped and visible on screen on Linux before grabbing focus
        self.transient(parent)
        self.deiconify()
        self.wait_visibility()
        self.grab_set()

        # Center Window relative to parent/main window
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 260
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 200
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass
        
        # UI Elements
        # Circular checkmark badge
        badge_frame = ctk.CTkFrame(self, width=64, height=64, corner_radius=32, fg_color="#e6f4ea")
        badge_frame.pack(pady=(30, 10))
        badge_frame.pack_propagate(False)
        
        badge_lbl = ctk.CTkLabel(badge_frame, text="✓", font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color="#137333")
        badge_lbl.pack(expand=True)
        
        # Success Title
        ctk.CTkLabel(
            self, text="Payment Recorded Successfully",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#15165e"
        ).pack(pady=5)
        
        # Details Card
        details_card = ctk.CTkFrame(self, fg_color="#f8fafc", corner_radius=12, border_width=1, border_color="#cbd5e1")
        details_card.pack(fill="x", padx=40, pady=15)
        
        inner_details = ctk.CTkFrame(details_card, fg_color="transparent")
        inner_details.pack(padx=15, pady=12, fill="both", expand=True)
        inner_details.columnconfigure(0, minsize=100)
        inner_details.columnconfigure(1, weight=1)
        
        rows = [
            ("Receipt No:", receipt_num),
            ("Amount Paid:", f"₱{amount:,.2f}"),
            ("Method:", method),
            ("Receipt File:", os.path.basename(filepath))
        ]
        
        for idx, (label, val) in enumerate(rows):
            lbl_title = ctk.CTkLabel(
                inner_details, text=label,
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#64748b"
            )
            lbl_title.grid(row=idx, column=0, sticky="w", pady=3)
            
            lbl_val = ctk.CTkLabel(
                inner_details, text=val,
                font=ctk.CTkFont(family="Inter", size=12, weight="bold" if idx == 1 else "normal"),
                text_color="#122aff" if idx == 1 else "#1e293b"
            )
            lbl_val.grid(row=idx, column=1, sticky="w", padx=(15, 0), pady=3)
            
        # Button Row
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=40, pady=(10, 20))
        
        ctk.CTkButton(
            btn_row, text="👁  Open Receipt",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            height=38, fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
            corner_radius=8,
            command=self.open_pdf
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            btn_row, text="📁  Open Folder",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            height=38, fg_color="#cbd5e1", hover_color="#94a3b8", text_color="#1e293b",
            corner_radius=8,
            command=self.open_folder
        ).pack(side="left", fill="x", expand=True, padx=(6, 6))
        
        ctk.CTkButton(
            btn_row, text="Close",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            height=38, fg_color="#ef4444", hover_color="#dc2626", text_color="#ffffff",
            corner_radius=8,
            width=80,
            command=self.destroy
        ).pack(side="left", padx=(6, 0))

    def _open_path(self, path):
        if os.name == "nt":
            os.startfile(path)
        else:
            subprocess.run(["xdg-open", path], check=True)

    def open_pdf(self):
        try:
            self._open_path(self.filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF file:\n{str(e)}", parent=self)

    def open_folder(self):
        try:
            self._open_path(self.folderpath)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{str(e)}", parent=self)