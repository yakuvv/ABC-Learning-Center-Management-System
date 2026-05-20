# modules/process_payment.py
import customtkinter as ctk
from tkinter import messagebox
import database
from datetime import datetime


class ProcessPayment(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#e4e4e4", corner_radius=0)
        self.pack(fill="both", expand=True)
        self.current_enrollment_id = None
        self.create_ui()

    def create_ui(self):
        # Top Bar
        top_bar = ctk.CTkFrame(self, height=70, fg_color="#15165e", corner_radius=0)
        top_bar.pack(fill="x", side="top")
        top_bar.pack_propagate(False)

        back_btn = ctk.CTkButton(top_bar, text="← back to Dashboard",
                                 font=ctk.CTkFont(family="Inter", size=14),
                                 fg_color="transparent", text_color="#ffffff",
                                 hover_color="#22259c", width=150, height=40,
                                 corner_radius=0, command=self.back_to_dashboard)
        back_btn.pack(side="left", padx=20, pady=15)

        title = ctk.CTkLabel(top_bar, text="Process Payment",
                             font=ctk.CTkFont(family="Inter", size=36, weight="bold"),
                             text_color="#ffffff")
        title.pack(side="left", expand=True)

        # Main Content
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Search
        ctk.CTkLabel(main_frame, text="Search Enrollment / Student",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold")).pack(anchor="w", pady=(0, 8))

        search_frame = ctk.CTkFrame(main_frame, fg_color="#cbd5e1", height=55, corner_radius=0)
        search_frame.pack(fill="x", pady=5)
        search_frame.pack_propagate(False)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="School ID or Student Name", height=40)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=15, pady=8)

        ctk.CTkButton(search_frame, text="Search", width=140, height=40,
                      fg_color="#122aff", command=self.search_enrollment).pack(side="right", padx=15)

        # Info Area
        self.info_label = ctk.CTkLabel(main_frame, text="No enrollment selected yet...",
                                       font=ctk.CTkFont(family="Inter", size=14),
                                       text_color="#666666")
        self.info_label.pack(fill="x", pady=20)

        # Payment Form
        ctk.CTkLabel(main_frame, text="Payment Details",
                     font=ctk.CTkFont(family="Inter", size=16, weight="bold")).pack(anchor="w", pady=(10, 8))

        p_frame = ctk.CTkFrame(main_frame, fg_color="#cbd5e1", corner_radius=0)
        p_frame.pack(fill="x", pady=5)

        inner = ctk.CTkFrame(p_frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(inner, text="Amount (₱)").grid(row=0, column=0, sticky="w", pady=8)
        self.amount_entry = ctk.CTkEntry(inner, placeholder_text="1500.00")
        self.amount_entry.grid(row=0, column=1, sticky="ew", padx=20, pady=8)

        ctk.CTkLabel(inner, text="Payment Method").grid(row=1, column=0, sticky="w", pady=8)
        self.method_combo = ctk.CTkComboBox(inner, values=["Cash", "GCash", "Bank Transfer"])
        self.method_combo.grid(row=1, column=1, sticky="ew", padx=20, pady=8)
        self.method_combo.set("Cash")

        ctk.CTkButton(main_frame, text="Record Payment & Generate Receipt",
                      height=50, fg_color="#122aff",
                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                      command=self.process_payment).pack(pady=30)

    def search_enrollment(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Required", "Please enter School ID or Student Name")
            return

        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
                       SELECT e.enrollmentID,
                              e.schoolID,
                              s.studFname,
                              s.studLname,
                              s.studMname,
                              e.gradeLevel,
                              e.schoolYear,
                              e.term
                       FROM ENROLLMENT e
                                JOIN STUDENT s ON e.studentID = s.studentID
                       WHERE e.schoolID = ?
                          OR s.studFname LIKE ?
                          OR s.studLname LIKE ? LIMIT 5
                       """, (keyword, f"%{keyword}%", f"%{keyword}%"))

        row = cursor.fetchone()
        conn.close()

        if row:
            full_name = f"{row['studFname']} {row['studLname']}"
            if row.get('studMname'):
                full_name += f" {row['studMname'][0]}."

            info = f"✅ Found!\n\n"
            info += f"School ID : {row['schoolID']}\n"
            info += f"Student   : {full_name}\n"
            info += f"Grade     : {row['gradeLevel']}\n"
            info += f"Term      : {row['term']} | {row['schoolYear']}"

            self.info_label.configure(text=info, text_color="#10b981")
            self.current_enrollment_id = row['enrollmentID']
        else:
            self.info_label.configure(text="❌ No enrollment found with that School ID or Name.",
                                      text_color="red")
            self.current_enrollment_id = None

    def process_payment(self):
        if not hasattr(self, 'current_enrollment_id') or not self.current_enrollment_id:
            messagebox.showwarning("Warning", "Please search and select an enrollment first")
            return

        try:
            amount = float(self.amount_entry.get() or 0)
        except:
            messagebox.showwarning("Invalid", "Please enter a valid amount")
            return

        method = self.method_combo.get()

        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           INSERT INTO PAYMENT (enrollmentID, amount, payMethod, payStatus)
                           VALUES (?, ?, ?, 'Paid')
                           """, (self.current_enrollment_id, amount, method))

            payment_id = cursor.lastrowid
            receipt_num = f"REC-{datetime.now().strftime('%Y%m%d')}-{payment_id}"

            cursor.execute("INSERT INTO RECEIPT (paymentID, receiptNumber) VALUES (?, ?)",
                           (payment_id, receipt_num))

            conn.commit()
            messagebox.showinfo("Success", f"Payment Recorded!\nReceipt: {receipt_num}")

            # Clear
            self.search_entry.delete(0, 'end')
            self.amount_entry.delete(0, 'end')
            self.info_label.configure(text="No enrollment selected yet...", text_color="#666666")
            self.current_enrollment_id = None

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def back_to_dashboard(self):
        parent_frame = self.master
        self.destroy()
        if hasattr(parent_frame, "welcome_lbl"):
            parent_frame.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))
        elif hasattr(parent_frame.master, "welcome_lbl"):
            parent_frame.master.welcome_lbl.pack(fill="x", padx=40, pady=(45, 20))