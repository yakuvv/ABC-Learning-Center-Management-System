import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime


class ProcessPayment(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.current_enrollment_id = None

        if hasattr(parent.master, "welcome_lbl"):
            parent.master.welcome_lbl.pack_forget()
        elif hasattr(parent, "welcome_lbl"):
            parent.welcome_lbl.pack_forget()

        self.create_ui()

    #shared widget factories

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

    def _card(self, parent, height=None):
        """Slate card with left accent. Returns (card, inner)."""
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

        ctk.CTkLabel(top_bar, text="Process Payment",
                     font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                     text_color="#ffffff").pack(side="left", expand=True, padx=(0, 100))

        ctk.CTkLabel(top_bar, text="ABC",
                     font=ctk.CTkFont(family="Inter", size=18, weight="bold"),
                     text_color="#122aff").pack(side="right", padx=30)

        #Workspace
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        #Search section
        ctk.CTkLabel(main_frame, text="Search Enrollment / Student",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 4))

        search_card, search_inner = self._card(main_frame, height=55)
        search_card.pack(fill="x", pady=(0, 4))
        search_card.pack_propagate(False)

        self.search_entry = self._entry(search_inner, "School ID or Student Name")
        self.search_entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(search_inner, text="SEARCH",
                      font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                      width=120, height=35, corner_radius=0,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="white",
                      command=self.search_enrollment
                      ).pack(side="right", padx=(10, 0))

        #Status display
        status_card = ctk.CTkFrame(main_frame, fg_color="#cbd5e1", corner_radius=0,
                                   border_width=1, border_color="#a1a1a1")
        status_card.pack(fill="x", pady=(0, 20))
        ctk.CTkFrame(status_card, width=8, fg_color="#15165e", corner_radius=0).pack(side="left", fill="y")

        self.info_label = ctk.CTkLabel(
            status_card,
            text="No enrollment selected yet...",
            font=ctk.CTkFont(family="Inter", size=14),
            text_color="#555555",
            justify="left",
            anchor="w"
        )
        self.info_label.pack(fill="x", padx=15, pady=12)

        #Payment Details
        ctk.CTkLabel(main_frame, text="Payment Details",
                     font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                     text_color="#000000").pack(anchor="w", pady=(0, 4))

        pay_card, pay_inner = self._card(main_frame)
        pay_card.pack(fill="x", pady=(0, 20))
        pay_inner.grid_columnconfigure(1, weight=1)

        #Amount
        ctk.CTkLabel(pay_inner, text="Amount (₱)",
                     font=ctk.CTkFont(family="Inter", size=13),
                     text_color="#444444").grid(row=0, column=0, sticky="w", pady=8)
        self.amount_entry = self._entry(pay_inner, "e.g. 1500.00")
        self.amount_entry.grid(row=0, column=1, sticky="ew", padx=(20, 0), pady=8)

        #Payment Method
        ctk.CTkLabel(pay_inner, text="Payment Method",
                     font=ctk.CTkFont(family="Inter", size=13),
                     text_color="#444444").grid(row=1, column=0, sticky="w", pady=8)
        self.method_combo = self._combo(pay_inner, ["Cash", "GCash", "Bank Transfer"])
        self.method_combo.set("Cash")
        self.method_combo.grid(row=1, column=1, sticky="ew", padx=(20, 0), pady=8)

        #Submit button
        ctk.CTkButton(main_frame,
                      text="RECORD PAYMENT & GENERATE RECEIPT",
                      font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                      height=50, corner_radius=0,
                      fg_color="#122aff", hover_color="#0b1eb3", text_color="#ffffff",
                      command=self.process_payment
                      ).pack(fill="x", pady=(10, 0))

    #Logic

    def search_enrollment(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Required", "Please enter a School ID or Student Name")
            return

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.enrollmentID, e.schoolID,
                   s.studFname, s.studLname, s.studMname,
                   e.gradeLevel, e.schoolYear, e.term
            FROM ENROLLMENT e
            JOIN STUDENT s ON e.studentID = s.studentID
            WHERE e.schoolID = ?
               OR s.studFname LIKE ?
               OR s.studLname LIKE ?
            LIMIT 1
        """, (keyword, f"%{keyword}%", f"%{keyword}%"))
        row = cursor.fetchone()
        conn.close()

        if row:
            mname = f" {row['studMname'][0]}." if row.get('studMname') else ""
            full  = f"{row['studFname']} {row['studLname']}{mname}"
            info  = (f"✔  Found\n\n"
                     f"School ID : {row['schoolID']}\n"
                     f"Student   : {full}\n"
                     f"Grade     : {row['gradeLevel']}\n"
                     f"Term      : {row['term']}  |  {row['schoolYear']}")
            self.info_label.configure(text=info, text_color="#16a34a")
            self.current_enrollment_id = row['enrollmentID']
        else:
            self.info_label.configure(
                text="No enrollment found with that School ID or Name.",
                text_color="#dc2626")
            self.current_enrollment_id = None

    def process_payment(self):
        if not self.current_enrollment_id:
            messagebox.showwarning("Warning", "Please search and select an enrollment first")
            return

        try:
            amount = float(self.amount_entry.get() or 0)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid", "Please enter a valid amount greater than 0")
            return

        method = self.method_combo.get()
        conn   = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO PAYMENT (enrollmentID, amount, payMethod, payStatus)
                VALUES (?, ?, ?, 'Paid')
            """, (self.current_enrollment_id, amount, method))

            payment_id  = cursor.lastrowid
            receipt_num = f"REC-{datetime.now().strftime('%Y%m%d')}-{payment_id:04d}"

            cursor.execute(
                "INSERT INTO RECEIPT (paymentID, receiptNumber) VALUES (?, ?)",
                (payment_id, receipt_num))

            conn.commit()
            messagebox.showinfo("Payment Recorded",
                                f"Receipt Number: {receipt_num}\n"
                                f"Amount: ₱{amount:,.2f}\n"
                                f"Method: {method}")

            #Reset
            self.search_entry.delete(0, 'end')
            self.amount_entry.delete(0, 'end')
            self.info_label.configure(
                text="No enrollment selected yet...", text_color="#555555")
            self.current_enrollment_id = None

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