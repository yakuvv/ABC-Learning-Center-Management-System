import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
from PIL import Image
import subprocess
import database
from database import price_for_level
from config import SESSION_HOURS
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
        self._total_due = 0.0
        self._total_paid = 0.0
        self._total_recorded = 0.0
        self._overpaid = 0.0
        self._balance = 0.0
        self._enrolled_lines = []

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

    def _card(self, parent, height=None, scrollable=False):
        """White card with left accent. Returns (card, inner)."""
        kw = {"height": height} if height else {}
        card = ctk.CTkFrame(parent, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#cbd5e1", **kw)
        if height:
            card.pack_propagate(False)

        accent_container = ctk.CTkFrame(card, width=6, fg_color="transparent")
        accent_container.pack(side="left", fill="y", padx=(12, 0), pady=12)

        accent = ctk.CTkFrame(accent_container, width=6, fg_color="#15165e", corner_radius=3)
        accent.pack(fill="both", expand=True)

        if scrollable:
            inner = ctk.CTkScrollableFrame(card, fg_color="transparent", corner_radius=0)
        else:
            inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=12)
        return card, inner

    def _money(self, amount):
        return f"₱{float(amount):,.2f}"

    def _format_payment_when(self, pay_date, pay_time):
        date_part = pay_date or "—"
        if pay_time:
            return f"{date_part}  ·  {pay_time}"
        return str(date_part)

    def _parse_money_field(self, entry):
        try:
            return max(float(entry.get().strip() or 0), 0.0)
        except ValueError:
            return 0.0

    def _is_cash_payment(self):
        return (self.method_combo.get() or "").strip().lower() == "cash"

    def _on_method_changed(self, *_):
        cash = self._is_cash_payment()
        state = "normal" if cash else "disabled"
        for widget in (
            self.cash_tendered_lbl, self.tendered_entry,
            self.change_title_lbl, self.change_lbl,
        ):
            widget.grid() if cash else widget.grid_remove()
        if not cash:
            self.tendered_entry.delete(0, tk.END)
        self._update_change_display()

    def _update_change_display(self, *_):
        due = self._parse_money_field(self.amount_entry)
        if not self._is_cash_payment():
            self.change_lbl.configure(text="—", text_color="#64748b")
            return
        tendered = self._parse_money_field(self.tendered_entry)
        change = max(tendered - due, 0.0)
        if tendered > 0 and tendered + 0.009 < due:
            self.change_lbl.configure(
                text=f"{self._money(change)} — need {self._money(due - tendered)} more",
                text_color="#ef4444",
            )
        else:
            self.change_lbl.configure(text=self._money(change), text_color="#15803d")

    def create_ui(self):
        # Top bar
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        ctk.CTkButton(
            top_bar, text="<  Back to Dashboard",
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

        self.info_card, self.info_inner = self._card(left_col, scrollable=True)
        self.info_card.pack(fill="both", expand=True)

        self._show_info_placeholder()

        # --- RIGHT COLUMN: PAYMENT DETAILS ---
        right_col = ctk.CTkFrame(workspace, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        ctk.CTkLabel(
            right_col, text="RECORD PAYMENT",
            font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
            text_color="#1e293b"
        ).pack(anchor="w", pady=(0, 6))

        self.balance_banner = ctk.CTkFrame(right_col, fg_color="#eef2ff", corner_radius=12,
                                           border_width=1, border_color="#c7d2fe")
        self.balance_banner.pack(fill="x", pady=(0, 10))
        self.balance_banner_inner = ctk.CTkFrame(self.balance_banner, fg_color="transparent")
        self.balance_banner_inner.pack(fill="x", padx=16, pady=12)
        self._render_balance_banner_placeholder()

        pay_card, self.pay_inner = self._card(right_col)
        pay_card.pack(fill="x", pady=(0, 10))
        self.pay_inner.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.pay_inner, text="Payment due (₱)",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#1e293b",
        ).grid(row=0, column=0, sticky="w", pady=(12, 6))
        self.amount_entry = ModernEntry(
            self.pay_inner, placeholder_text="Amount applied to balance",
            height=32, font=ctk.CTkFont(family="Inter", size=13),
        )
        self.amount_entry.grid(row=0, column=1, sticky="ew", padx=(20, 0), pady=(12, 6))
        self.amount_entry.bind("<KeyRelease>", self._update_change_display)

        ctk.CTkLabel(
            self.pay_inner, text="Payment Method",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#1e293b",
        ).grid(row=1, column=0, sticky="w", pady=6)
        self.method_combo = self._combo(
            self.pay_inner, ["Cash", "GCash", "Bank Transfer"],
            command=self._on_method_changed,
        )
        self.method_combo.set("Cash")
        self.method_combo.grid(row=1, column=1, sticky="ew", padx=(20, 0), pady=6)

        self.cash_tendered_lbl = ctk.CTkLabel(
            self.pay_inner, text="Cash received (₱)",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#1e293b",
        )
        self.cash_tendered_lbl.grid(row=2, column=0, sticky="w", pady=6)
        self.tendered_entry = ModernEntry(
            self.pay_inner, placeholder_text="e.g. 1000.00",
            height=32, font=ctk.CTkFont(family="Inter", size=13),
        )
        self.tendered_entry.grid(row=2, column=1, sticky="ew", padx=(20, 0), pady=6)
        self.tendered_entry.bind("<KeyRelease>", self._update_change_display)

        self.change_title_lbl = ctk.CTkLabel(
            self.pay_inner, text="Change due",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#1e293b",
        )
        self.change_title_lbl.grid(row=3, column=0, sticky="w", pady=6)
        self.change_lbl = ctk.CTkLabel(
            self.pay_inner, text="₱0.00",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#15803d",
        )
        self.change_lbl.grid(row=3, column=1, sticky="w", padx=(20, 0), pady=6)

        self.pay_full_btn = ctk.CTkButton(
            self.pay_inner, text="Use full balance",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            height=32, fg_color="#cbd5e1", hover_color="#94a3b8", text_color="#1e293b",
            command=self._fill_full_balance,
        )
        self.pay_full_btn.grid(row=4, column=1, sticky="e", padx=(20, 0), pady=(4, 10))

        ctk.CTkLabel(
            right_col, text="PAYMENT HISTORY",
            font=ctk.CTkFont(family="Inter", size=13, weight="bold"),
            text_color="#1e293b"
        ).pack(anchor="w", pady=(4, 4))

        self.history_card, self.history_inner = self._card(right_col, height=140, scrollable=True)
        self.history_card.pack(fill="both", expand=True, pady=(0, 10))
        self._render_history_placeholder()

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
        self.after_idle(self._on_method_changed)

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
            WHERE r.regStatus = 'Active'
              AND (
                   r.learnerID LIKE ?
                OR s.studentID = ?
                OR s.studFname LIKE ?
                OR s.studLname LIKE ?
                OR (s.studFname || ' ' || s.studLname) LIKE ?
              )
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

    def _load_registration_financials(self, registration_id):
        conn = database.get_connection()
        cursor = conn.cursor()

        lines = cursor.execute(
            """
            SELECT s.subjectName, b.batchLabel, b.schedule, rd.enrollStatus,
                   COALESCE(rd.feeAmount, s.pricePerTerm, 0) AS feeAmount
            FROM REGISTRATION_DETAIL rd
            JOIN SUBJECT s ON s.subjectID = rd.subjectID
            LEFT JOIN BATCH b ON b.batchID = rd.batchID
            WHERE rd.registrationID = ? AND rd.enrollStatus = 'Active'
            ORDER BY s.subjectName
            """,
            (registration_id,),
        ).fetchall()
        self._enrolled_lines = [dict(row) for row in lines]

        reg_level = cursor.execute(
            "SELECT level FROM REGISTRATION WHERE registrationID = ?",
            (registration_id,),
        ).fetchone()
        fallback_price = price_for_level(reg_level["level"] if reg_level else "")

        for line in self._enrolled_lines:
            fee = float(line.get("feeAmount") or 0)
            if fee <= 0:
                fee = fallback_price
                line["feeAmount"] = fee

        self._total_due = sum(float(ln["feeAmount"]) for ln in self._enrolled_lines)

        paid_row = cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM PAYMENT
            WHERE registrationID = ? AND payStatus = 'Paid'
            """,
            (registration_id,),
        ).fetchone()
        self._total_recorded = float(paid_row["total"] if paid_row else 0)
        self._total_paid = min(self._total_recorded, self._total_due)
        self._overpaid = max(self._total_recorded - self._total_due, 0.0)
        self._balance = max(self._total_due - self._total_recorded, 0.0)

        payments = cursor.execute(
            """
            SELECT p.payDate, p.payTime, p.amount, p.amountTendered, p.changeDue,
                   p.payMethod, r.receiptNumber
            FROM PAYMENT p
            LEFT JOIN RECEIPT r ON r.paymentID = p.paymentID
            WHERE p.registrationID = ?
            ORDER BY p.paymentID DESC
            """,
            (registration_id,),
        ).fetchall()
        conn.close()
        return [dict(p) for p in payments]

    def _show_info_placeholder(self):
        for w in self.info_inner.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.info_inner,
            text="Search and select an active enrollment\nto view subjects, batches, and balance.",
            font=ctk.CTkFont(family="Inter", size=13),
            text_color="#64748b",
            justify="center",
        ).pack(expand=True, pady=40)

    def _render_balance_banner_placeholder(self):
        for w in self.balance_banner_inner.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.balance_banner_inner,
            text="Select a student to see amount due and balance.",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#64748b",
        ).pack(anchor="w")

    def _render_balance_banner(self):
        for w in self.balance_banner_inner.winfo_children():
            w.destroy()

        paid_in_full = self._balance <= 0 and self._total_due > 0
        banner_bg = "#dcfce7" if paid_in_full else "#eef2ff"
        border = "#86efac" if paid_in_full else "#c7d2fe"
        self.balance_banner.configure(fg_color=banner_bg, border_color=border)

        grid = ctk.CTkFrame(self.balance_banner_inner, fg_color="transparent")
        grid.pack(fill="x")
        for col in range(3):
            grid.columnconfigure(col, weight=1)

        for col, (label, val, color) in enumerate([
            ("Total due", self._money(self._total_due), "#15165e"),
            ("Paid (applied)", self._money(self._total_paid), "#15803d"),
            ("Balance", self._money(self._balance), "#b45309" if self._balance > 0 else "#15803d"),
        ]):
            cell = ctk.CTkFrame(grid, fg_color="transparent")
            cell.grid(row=0, column=col, sticky="ew", padx=4)
            ctk.CTkLabel(cell, text=label, font=ctk.CTkFont(family="Inter", size=11),
                         text_color="#64748b").pack(anchor="w")
            ctk.CTkLabel(cell, text=val, font=ctk.CTkFont(family="Inter", size=16, weight="bold"),
                         text_color=color).pack(anchor="w")

        fee_note = ctk.CTkLabel(
            self.balance_banner_inner,
            text=(
                f"{len(self._enrolled_lines)} subject(s) · "
                f"{SESSION_HOURS}-hour sessions · total fees {self._money(self._total_due)}"
            ),
            font=ctk.CTkFont(family="Inter", size=11),
            text_color="#64748b",
        )
        fee_note.pack(anchor="w", pady=(8, 0))

        if paid_in_full:
            ctk.CTkLabel(
                self.balance_banner_inner, text="Fully paid for this enrollment.",
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#15803d",
            ).pack(anchor="w", pady=(6, 0))

    def _render_history_placeholder(self):
        for w in self.history_inner.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.history_inner, text="No payments yet.",
            font=ctk.CTkFont(family="Inter", size=12),
            text_color="#94a3b8",
        ).pack(anchor="w", pady=8)

    def _render_payment_history(self, payments):
        for w in self.history_inner.winfo_children():
            w.destroy()
        if not payments:
            self._render_history_placeholder()
            return
        for p in payments:
            row = ctk.CTkFrame(self.history_inner, fg_color="#f8fafc", corner_radius=8,
                               border_width=1, border_color="#e2e8f0")
            row.pack(fill="x", pady=4)
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=10, pady=8)
            inner.columnconfigure(0, weight=1)

            top = ctk.CTkFrame(inner, fg_color="transparent")
            top.grid(row=0, column=0, columnspan=2, sticky="ew")
            ctk.CTkLabel(
                top,
                text=p.get("receiptNumber") or "—",
                font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                text_color="#15165e",
            ).pack(side="left")
            ctk.CTkLabel(
                top,
                text=self._money(p["amount"]),
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#122aff",
            ).pack(side="right")

            ctk.CTkLabel(
                inner,
                text=self._format_payment_when(p.get("payDate"), p.get("payTime")),
                font=ctk.CTkFont(family="Inter", size=10),
                text_color="#64748b",
            ).grid(row=1, column=0, sticky="w", pady=(2, 0))

            method = p.get("payMethod") or "—"
            tendered = p.get("amountTendered")
            change = p.get("changeDue")
            if method.lower() == "cash" and tendered is not None:
                detail = f"{method} · Received {self._money(tendered)}"
                if change and float(change) > 0.009:
                    detail += f" · Change {self._money(change)}"
            else:
                detail = method
            ctk.CTkLabel(
                inner, text=detail,
                font=ctk.CTkFont(family="Inter", size=10),
                text_color="#64748b",
            ).grid(row=1, column=1, sticky="e", pady=(2, 0))

    def _fill_full_balance(self):
        if not self.current_registration_id:
            messagebox.showwarning("Warning", "Please select a student enrollment first.")
            return
        if self._balance <= 0:
            messagebox.showinfo("Paid", "This enrollment has no outstanding balance.")
            return
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, f"{self._balance:.2f}")

    def select_registration(self, r):
        self.current_registration_id = r['registrationID']
        self.current_student_data = r
        payments = self._load_registration_financials(self.current_registration_id)

        for w in self.info_inner.winfo_children():
            w.destroy()

        mname = f" {r['studMname'][0]}." if r.get('studMname') else ""
        full_name = f"{r['studFname']}{mname} {r['studLname']}"

        summary = ctk.CTkFrame(self.info_inner, fg_color="transparent")
        summary.pack(fill="x", pady=(0, 10))

        info_items = [
            ("Learner ID", r['learnerID'] or "—"),
            ("Student", full_name),
            ("Level", r['level'] or "—"),
            ("Term", r['term'] or "—"),
        ]
        for i, (label, val) in enumerate(info_items):
            ctk.CTkLabel(summary, text=f"{label}:", font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                         text_color="#15165e").grid(row=i, column=0, sticky="w", pady=3)
            ctk.CTkLabel(summary, text=val, font=ctk.CTkFont(family="Inter", size=12),
                         text_color="#1e293b").grid(row=i, column=1, sticky="w", padx=(12, 0), pady=3)

        ctk.CTkLabel(
            self.info_inner, text="ENROLLED SUBJECTS & BATCHES",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color="#15165e",
        ).pack(anchor="w", pady=(8, 6))

        if not self._enrolled_lines:
            ctk.CTkLabel(
                self.info_inner, text="No active subject enrollments for this registration.",
                font=ctk.CTkFont(family="Inter", size=12), text_color="#ef4444",
            ).pack(anchor="w")
        else:
            for line in self._enrolled_lines:
                row = ctk.CTkFrame(self.info_inner, fg_color="#f8fafc", corner_radius=8,
                                   border_width=1, border_color="#e2e8f0")
                row.pack(fill="x", pady=4)
                inner = ctk.CTkFrame(row, fg_color="transparent")
                inner.pack(fill="x", padx=10, pady=8)
                batch_txt = line.get("batchLabel") or "—"
                sched = line.get("schedule") or "—"
                ctk.CTkLabel(
                    inner, text=line["subjectName"],
                    font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                    text_color="#15165e",
                ).pack(anchor="w")
                fee = float(line.get("feeAmount") or 0)
                ctk.CTkLabel(
                    inner,
                    text=f"Batch {batch_txt}  ·  {sched}  ·  {self._money(fee)}",
                    font=ctk.CTkFont(family="Inter", size=11),
                    text_color="#64748b",
                ).pack(anchor="w")

        self._render_balance_banner()
        self._render_payment_history(payments)
        self.record_btn.configure(state="normal" if self._balance > 0 else "disabled")

        self.amount_entry.delete(0, tk.END)
        self.tendered_entry.delete(0, tk.END)
        if self._balance > 0:
            self.amount_entry.insert(0, f"{self._balance:.2f}")
        self._on_method_changed()
        self._update_change_display()

    def process_payment(self):
        if not self.current_registration_id:
            messagebox.showwarning("Warning", "Please search and select a student first!")
            return

        if not self._enrolled_lines:
            messagebox.showwarning("Warning", "This registration has no active subject enrollments.")
            return

        if self._balance <= 0:
            messagebox.showinfo("Paid", "This enrollment is already fully paid.")
            return

        amount = self._parse_money_field(self.amount_entry)
        if amount <= 0:
            messagebox.showwarning("Invalid Amount", "Please enter a valid payment due amount greater than 0.")
            return

        if amount > self._balance + 0.009:
            messagebox.showwarning(
                "Invalid Amount",
                f"Payment due cannot exceed the outstanding balance of {self._money(self._balance)}.",
            )
            return

        method = self.method_combo.get()
        if self._is_cash_payment():
            tendered = self._parse_money_field(self.tendered_entry)
            if tendered < amount - 0.009:
                messagebox.showwarning(
                    "Insufficient Cash",
                    f"Cash received ({self._money(tendered)}) is less than payment due ({self._money(amount)}).",
                )
                return
            change_due = round(tendered - amount, 2)
            amount_tendered = tendered
        else:
            amount_tendered = amount
            change_due = 0.0

        pay_time = datetime.now().strftime("%I:%M %p")
        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO PAYMENT
                    (registrationID, amount, amountTendered, changeDue, payMethod, payStatus, payTime)
                VALUES (?, ?, ?, ?, ?, 'Paid', ?)
            """, (
                self.current_registration_id, amount, amount_tendered, change_due,
                method, pay_time,
            ))

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

            enrolled_summary = [
                (
                    f"{ln['subjectName']} (Batch {ln.get('batchLabel') or '—'}) — "
                    f"{self._money(ln.get('feeAmount', 0))}"
                )
                for ln in self._enrolled_lines
            ]
            receipt_data = {
                'receipt_number': receipt_num,
                'date': datetime.now().strftime("%B %d, %Y - %I:%M %p"),
                'amount': amount,
                'amount_tendered': amount_tendered,
                'change_due': change_due,
                'method': method,
                'student_name': student_name,
                'school_id': r['learnerID'] or "—",
                'grade_level': r['level'] or "—",
                'term': r['term'] or "—",
                'school_year': r['term'] or "—",
                'total_due': self._total_due,
                'total_paid': self._total_paid + amount,
                'balance_after': max(self._balance - amount, 0),
                'enrolled_lines': enrolled_summary,
            }
            generate_receipt_pdf(filepath, receipt_data)

            self.show_success_modal(
                receipt_num, amount, method, filepath, receipts_dir,
                amount_tendered=amount_tendered, change_due=change_due,
            )
            self.select_registration(self.current_student_data)
            self.amount_entry.delete(0, tk.END)
            self.tendered_entry.delete(0, tk.END)

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Failed to record payment:\n{str(e)}")
        finally:
            conn.close()

    def show_success_modal(self, receipt_num, amount, method, filepath, folderpath,
                           amount_tendered=0.0, change_due=0.0):
        modal = ReceiptSuccessModal(
            self, receipt_num, amount, method, filepath, folderpath,
            amount_tendered=amount_tendered, change_due=change_due,
        )
        self.wait_window(modal)

    def clear_form(self):
        self.search_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.tendered_entry.delete(0, tk.END)
        self.method_combo.set("Cash")
        self._on_method_changed()
        self.current_registration_id = None
        self.current_student_data = None
        self._total_due = 0.0
        self._total_paid = 0.0
        self._total_recorded = 0.0
        self._overpaid = 0.0
        self._balance = 0.0
        self._enrolled_lines = []

        self._show_info_placeholder()
        self._render_balance_banner_placeholder()
        self.balance_banner.configure(fg_color="#eef2ff", border_color="#c7d2fe")
        self._render_history_placeholder()
        self.record_btn.configure(state="normal")

    def back_to_dashboard(self):
        dashboard = self.master.master
        self.destroy()
        if hasattr(dashboard, "_show_welcome"):
            dashboard._show_welcome()


class ReceiptSuccessModal(ctk.CTkToplevel):
    MODAL_W = 480
    MODAL_H = 520
    BTN_H = 44

    def __init__(self, parent, receipt_num, amount, method, filepath, folderpath,
                 amount_tendered=0.0, change_due=0.0):
        super().__init__(parent)
        self.title("Payment Recorded Successfully")
        self.geometry(f"{self.MODAL_W}x{self.MODAL_H}")
        self.minsize(self.MODAL_W, self.MODAL_H)
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        self.filepath = filepath
        self.folderpath = folderpath

        self.transient(parent)
        self.deiconify()
        self.wait_visibility()
        self.grab_set()

        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.MODAL_W // 2)
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.MODAL_H // 2)
            self.geometry(f"{self.MODAL_W}x{self.MODAL_H}+{x}+{y}")
        except Exception:
            pass

        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=28, pady=24)
        root.grid_rowconfigure(2, weight=1)
        root.grid_columnconfigure(0, weight=1)

        badge_frame = ctk.CTkFrame(root, width=64, height=64, corner_radius=32, fg_color="#e6f4ea")
        badge_frame.grid(row=0, column=0, pady=(0, 8))
        badge_frame.pack_propagate(False)
        ctk.CTkLabel(
            badge_frame, text="✓",
            font=ctk.CTkFont(family="Inter", size=32, weight="bold"),
            text_color="#137333",
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            root, text="Payment Recorded Successfully",
            font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
            text_color="#15165e",
        ).grid(row=1, column=0, pady=(0, 12))

        details_card = ctk.CTkFrame(
            root, fg_color="#f8fafc", corner_radius=12,
            border_width=1, border_color="#cbd5e1",
        )
        details_card.grid(row=2, column=0, sticky="nsew", pady=(0, 16))

        inner_details = ctk.CTkFrame(details_card, fg_color="transparent")
        inner_details.pack(fill="both", expand=True, padx=16, pady=14)
        inner_details.columnconfigure(0, minsize=118)
        inner_details.columnconfigure(1, weight=1)

        rows = [
            ("Receipt No:", receipt_num),
            ("Amount Paid:", f"₱{amount:,.2f}"),
            ("Method:", method),
        ]
        if method.lower() == "cash" and amount_tendered:
            rows.append(("Cash Received:", f"₱{float(amount_tendered):,.2f}"))
            rows.append(("Change:", f"₱{float(change_due):,.2f}"))
        rows.append(("Receipt File:", os.path.basename(filepath)))

        for idx, (label, val) in enumerate(rows):
            ctk.CTkLabel(
                inner_details, text=label,
                font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                text_color="#64748b",
            ).grid(row=idx, column=0, sticky="nw", pady=4)
            val_color = "#122aff" if label == "Amount Paid:" else "#1e293b"
            if label == "Change:":
                val_color = "#15803d"
            ctk.CTkLabel(
                inner_details, text=val,
                font=ctk.CTkFont(
                    family="Inter", size=12,
                    weight="bold" if label in ("Amount Paid:", "Change:") else "normal",
                ),
                text_color=val_color,
                wraplength=280,
                justify="left",
            ).grid(row=idx, column=1, sticky="w", padx=(12, 0), pady=4)

        btn_area = ctk.CTkFrame(root, fg_color="transparent")
        btn_area.grid(row=3, column=0, sticky="ew")
        btn_area.grid_columnconfigure(0, weight=1)
        btn_area.grid_columnconfigure(1, weight=1)

        btn_font = ctk.CTkFont(family="Inter", size=13, weight="bold")

        ctk.CTkButton(
            btn_area, text="Open Receipt",
            font=btn_font, height=self.BTN_H,
            fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
            corner_radius=8, command=self.open_pdf,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=(0, 8))

        ctk.CTkButton(
            btn_area, text="Open Folder",
            font=btn_font, height=self.BTN_H,
            fg_color="#e2e8f0", hover_color="#cbd5e1", text_color="#1e293b",
            corner_radius=8, command=self.open_folder,
        ).grid(row=0, column=1, sticky="ew", padx=(6, 0), pady=(0, 8))

        ctk.CTkButton(
            btn_area, text="Close",
            font=btn_font, height=self.BTN_H,
            fg_color="#64748b", hover_color="#475569", text_color="#ffffff",
            corner_radius=8, command=self.destroy,
        ).grid(row=1, column=0, columnspan=2, sticky="ew")

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