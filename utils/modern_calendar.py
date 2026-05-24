import customtkinter as ctk
import calendar
from datetime import datetime

class ModernCalendar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="#ffffff", corner_radius=16, border_width=1, border_color="#e2e8f0", **kwargs)
        
        self.current_date = datetime.now()
        self.view_month = self.current_date.month
        self.view_year = self.current_date.year
        
        self.cal = calendar.TextCalendar(calendar.SUNDAY)
        
        # Header frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=16, pady=(16, 12))
        
        self.prev_btn = ctk.CTkButton(self.header_frame, text="<", width=32, height=32,
                                      fg_color="transparent", text_color="#64748b", hover_color="#f1f5f9",
                                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                      command=self._prev_month)
        self.prev_btn.pack(side="left")
        
        self.month_lbl = ctk.CTkLabel(self.header_frame, text="",
                                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                      text_color="#0f172a")
        self.month_lbl.pack(side="left", expand=True)
        
        self.next_btn = ctk.CTkButton(self.header_frame, text=">", width=32, height=32,
                                      fg_color="transparent", text_color="#64748b", hover_color="#f1f5f9",
                                      font=ctk.CTkFont(family="Inter", size=15, weight="bold"),
                                      command=self._next_month)
        self.next_btn.pack(side="right")
        
        # Days grid
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        
        days_of_week = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        for col, day in enumerate(days_of_week):
            lbl = ctk.CTkLabel(self.grid_frame, text=day,
                               font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                               text_color="#94a3b8")
            lbl.grid(row=0, column=col, padx=2, pady=(0, 8))
            self.grid_frame.grid_columnconfigure(col, weight=1)
            
        self.day_buttons = {}
        for r in range(1, 7):
            for c in range(7):
                btn = ctk.CTkButton(self.grid_frame, text="", width=34, height=34,
                                    fg_color="transparent", text_color="#334155",
                                    hover_color="#e0e7ff", corner_radius=17,
                                    font=ctk.CTkFont(family="Inter", size=13))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.day_buttons[(r, c)] = btn
                
        self._update_calendar()

    def _prev_month(self):
        if self.view_month == 1:
            self.view_month = 12
            self.view_year -= 1
        else:
            self.view_month -= 1
        self._update_calendar()

    def _next_month(self):
        if self.view_month == 12:
            self.view_month = 1
            self.view_year += 1
        else:
            self.view_month += 1
        self._update_calendar()

    def _update_calendar(self):
        month_name = calendar.month_name[self.view_month]
        self.month_lbl.configure(text=f"{month_name} {self.view_year}")
        
        for btn in self.day_buttons.values():
            btn.configure(text="", state="disabled", fg_color="transparent")
            
        month_days = self.cal.monthdayscalendar(self.view_year, self.view_month)
        
        for r_idx, week in enumerate(month_days):
            for c_idx, day in enumerate(week):
                btn = self.day_buttons[(r_idx + 1, c_idx)]
                if day != 0:
                    btn.configure(text=str(day), state="normal")
                    
                    if day == self.current_date.day and self.view_month == self.current_date.month and self.view_year == self.current_date.year:
                        btn.configure(fg_color="#122aff", text_color="#ffffff", hover_color="#0f24d6")
                    else:
                        btn.configure(fg_color="transparent", text_color="#334155", hover_color="#e0e7ff")
