import customtkinter as ctk


class ModernEntry(ctk.CTkFrame):
    # I created this self-contained entry widget with an animated underline. The underline is navy (#15165e) at rest and turns bright blue (#122aff) on focus. This is a drop-in replacement for CTkEntry that exposes .get(), .delete(), .insert(), and .configure() methods.

    def __init__(self, master, placeholder_text: str = "", **kwargs):
        # The frame itself is transparent so it blends with any card background
        super().__init__(master, fg_color="transparent", corner_radius=0)

        self._entry = ctk.CTkEntry(
            self,
            fg_color="transparent",
            border_width=0,
            corner_radius=0,
            text_color="black",
            placeholder_text=placeholder_text,
            **kwargs
        )
        self._entry.pack(fill="x")

        # Underline sits directly below the entry, inside the same frame
        self._underline = ctk.CTkFrame(self, height=2, fg_color="#15165e", corner_radius=0)
        self._underline.pack(fill="x", pady=(0, 2))

        self._entry.bind("<FocusIn>",  self._on_focus)
        self._entry.bind("<FocusOut>", self._on_unfocus)

    # Focus animation

    def _on_focus(self, event=None):
        self._underline.configure(fg_color="#122aff")

    def _on_unfocus(self, event=None):
        self._underline.configure(fg_color="#15165e")

    # Proxy methods so existing code works unchanged

    def get(self):
        return self._entry.get()

    def delete(self, first, last=None):
        if last is not None:
            self._entry.delete(first, last)
        else:
            self._entry.delete(first)

    def insert(self, index, string):
        self._entry.insert(index, string)

    def configure(self, require_redraw=False, **kwargs):
        try:
            self._entry.configure(**kwargs)
        except Exception:
            super().configure(**kwargs)

    def bind(self, sequence=None, func=None, add=None):
        # Always use add="+" to preserve internal focus bindings
        if add is None:
            add = "+"
        return self._entry.bind(sequence, func, add)