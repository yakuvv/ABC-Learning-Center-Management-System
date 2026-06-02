import customtkinter as ctk
from tkinter import font as tkfont


class ModernCombo(ctk.CTkComboBox):
    # I created this drop-in replacement for CTkComboBox with the project's default styling. This subclass avoids the wrapper-frame approach that caused attribute errors during widget destruction. All standard ComboBox methods (get, set, bind, etc.) are inherited unchanged.

    def __init__(self, master, values=None, command=None, placeholder_text="", **kwargs):
        # Default styling matching the navy‑accented design language
        defaults = {
            "values": values or [],
            "height": 35,
            "corner_radius": 0,
            "fg_color": "#ffffff",
            "text_color": "black",
            "border_width": 0,
            "button_color": "#ffffff",
            "button_hover_color": "#122aff",
            "dropdown_fg_color": "#15165e",
            "dropdown_text_color": "#ffffff",
            "dropdown_hover_color": "#122aff",
            "dropdown_width": 0,
            "state": "readonly",
            "font": ctk.CTkFont(family="Inter", size=13),
        }
        if command is not None:
            defaults["command"] = command
        defaults.update(kwargs)
        self._placeholder = placeholder_text
        dropdown_width = defaults.pop("dropdown_width", 0)
        super().__init__(master, **defaults)
        # Ensure the ComboBox has the internal _font attribute required by CustomTkinter's destroy()
        if not hasattr(self, "_font"):
            self._font = ctk.CTkFont(family="Inter", size=13)
        self._dropdown_width = dropdown_width
        self.after_idle(self._sync_dropdown_width)
        # Apply placeholder styling after widget is fully initialized
        self.after_idle(self._apply_placeholder)

    def _apply_placeholder(self):
        # I show gray placeholder text if nothing is selected.
        try:
            current = self.get()
        except Exception:
            return
        if not current or current == self._placeholder:
            if self._placeholder:
                super().set(self._placeholder)
            self.configure(text_color="#b0b0b0")

    def set(self, value):
        # I override set to handle placeholder color.
        super().set(value)
        if hasattr(self, "_placeholder"):
            if value and value != self._placeholder:
                self.configure(text_color="#0f172a")
            else:
                self.configure(text_color="#b0b0b0")

    def _dropdown_callback(self, value: str):
        # I am called when an item is selected from the dropdown menu.
        super()._dropdown_callback(value)
        if hasattr(self, "_placeholder"):
            if value and value != self._placeholder:
                self.configure(text_color="#0f172a")
            else:
                self.configure(text_color="#b0b0b0")

    def _sync_dropdown_width(self):
        # I match the dropdown menu width to the combo width via min_character_width.
        if self._dropdown_width == 0:
            pixel_width = self._current_width
            if pixel_width < 20:
                pixel_width = 400
        else:
            pixel_width = self._dropdown_width

        try:
            char_w = max(tkfont.Font(font=self._entry.cget("font")).measure("0"), 1)
        except tkfont.TclError:
            char_w = 8

        longest = max((len(v) for v in self._values), default=0)
        min_chars = max(int(pixel_width / char_w), longest)
        self._dropdown_menu._min_character_width = min_chars
        self._dropdown_menu._add_menu_commands()

    def configure(self, require_redraw=False, **kwargs):
        sync_dropdown = "dropdown_width" in kwargs or "width" in kwargs
        if "dropdown_width" in kwargs:
            self._dropdown_width = kwargs.pop("dropdown_width")
        super().configure(require_redraw=require_redraw, **kwargs)
        if sync_dropdown:
            self.after_idle(self._sync_dropdown_width)

    def _open_dropdown_menu(self):
        # Clear placeholder text when dropdown opens so real values show cleanly
        if hasattr(self, "_placeholder") and self.get() == self._placeholder:
            super().set("")
        self._sync_dropdown_width()
        super()._open_dropdown_menu()
        # After dropdown closes, re-apply placeholder if nothing was chosen
        self.after(200, self._recheck_placeholder)

    def _recheck_placeholder(self):
        try:
            val = self.get()
        except Exception:
            return
        if not val or val == self._placeholder:
            if self._placeholder:
                super().set(self._placeholder)
            self.configure(text_color="#b0b0b0")
        else:
            self.configure(text_color="#0f172a")
