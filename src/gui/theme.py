import customtkinter as ctk

# Obsidian inspired premium dark palette colors
BG_MAIN = "#0B0F19"         # Deep slate main window background
BG_CARD = "#151B26"         # Dark card background
BORDER_CARD = "#2D3748"     # Charcoal card border

# Text colors
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED = "#9CA3AF"
TEXT_SECONDARY = "#D1D5DB"

# Action / Accent colors
COLOR_ACCENT = "#2563EB"    # Modern vibrant blue
COLOR_ACCENT_HOVER = "#1D4ED8"
COLOR_ACCENT_MUTED = "#1E293B"

# Severity states
COLOR_SUCCESS = "#10B981"   # Emerald green
COLOR_SUCCESS_HOVER = "#059669"
COLOR_ERROR = "#EF4444"     # Crimson red
COLOR_ERROR_HOVER = "#DC2626"
COLOR_WARNING = "#F59E0B"   # Amber yellow

# Logging & Terminal
BG_CONSOLE = "#0D111A"
BORDER_CONSOLE = "#1E293B"

# Font definitions
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

def get_font(size=12, weight="normal", slant="roman", mono=False):
    """
    Convenience helper to build a CTkFont.
    """
    family = FONT_MONO if mono else FONT_FAMILY
    return ctk.CTkFont(family=family, size=size, weight=weight, slant=slant)
