import customtkinter as ctk


class ModernCombo(ctk.CTkComboBox):
    """A drop‑in replacement for CTkComboBox with the project's default styling.
    This subclass avoids the wrapper‑frame approach that caused attribute errors
    during widget destruction. All standard ComboBox methods (get, set, bind, etc.)
    are inherited unchanged.
    """

    def __init__(self, master, values=None, command=None, **kwargs):
        # Default styling matching the navy‑accented design language
        defaults = {
            "values": values or [],
            "height": 35,
            "corner_radius": 0,
            "fg_color": "#ffffff",
            "text_color": "black",
            "border_width": 0,
            "button_color": "#15165e",
            "button_hover_color": "#122aff",
            "dropdown_fg_color": "#15165e",
            "dropdown_text_color": "#ffffff",
            "dropdown_hover_color": "#122aff",
            "state": "readonly",
            "font": ctk.CTkFont(family="Inter", size=13),
        }
        if command is not None:
            defaults["command"] = command
        defaults.update(kwargs)
        super().__init__(master, **defaults)
        # Ensure the ComboBox has the internal _font attribute required by CustomTkinter's destroy()
        if not hasattr(self, "_font"):
            self._font = ctk.CTkFont(family="Inter", size=13)
