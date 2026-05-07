# config.py
import customtkinter as ctk

# Modern Professional Dark Theme
COLORS = {
    "bg": "#0F172A",           # Main background
    "surface": "#1E2937",      # Cards and panels
    "primary": "#2563EB",      # Main blue
    "primary_hover": "#1E40AF",
    "accent": "#8B5CF6",
    "text": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "success": "#22C55E",
    "danger": "#EF4444",
    "warning": "#F59E0B"
}

# Global Settings
WINDOW_TITLE = "ABC Learning Center Management System"
DEFAULT_SIZE = "1280x720"

# Apply CustomTkinter settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")