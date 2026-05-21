import customtkinter as ctk
from typing import Optional

class ModernEntry(ctk.CTkEntry):
    def __init__(self, master, placeholder_text: str = "", **kwargs):
        # Remove default border and set transparent bg
        super().__init__(
            master,
            fg_color="transparent",           # matches card background
            border_width=0,
            corner_radius=0,
            text_color="black",
            placeholder_text=placeholder_text,
            **kwargs
        )
        
        self.underline = None
        self._create_underline()
        self.bind("<FocusIn>", self._on_focus)
        self.bind("<FocusOut>", self._on_unfocus)

    def _create_underline(self):
        self.underline = ctk.CTkFrame(
            self.master,
            height=2,
            fg_color="#15165e",   # navy default
            corner_radius=0
        )
        self.underline.pack(fill="x", pady=(0, 4))  # small gap below entry

    def _on_focus(self, event=None):
        if self.underline:
            self.underline.configure(fg_color="#122aff")  # bright blue

    def _on_unfocus(self, event=None):
        if self.underline:
            self.underline.configure(fg_color="#15165e")