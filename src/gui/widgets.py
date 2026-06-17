import datetime
import os
import customtkinter as ctk
from src.gui.theme import (
    BG_CARD, BORDER_CARD, BG_CONSOLE, BORDER_CONSOLE,
    TEXT_PRIMARY, TEXT_MUTED, COLOR_ACCENT, COLOR_ERROR,
    COLOR_SUCCESS, COLOR_WARNING, get_font
)
from src.utils.icons import get_ctk_image
from src.utils.helpers import format_size, get_file_type_description

class LogConsole(ctk.CTkFrame):
    """
    Thread-safe, color-coded scrollable logging console.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        # Grid config
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Label
        self.label = ctk.CTkLabel(
            self, 
            text="Operations Log Console:", 
            font=get_font(12, weight="bold"),
            text_color=TEXT_MUTED
        )
        self.label.grid(row=0, column=0, padx=5, pady=(5, 5), sticky="w")
        
        # Text box
        self.textbox = ctk.CTkTextbox(
            self, 
            font=get_font(11, mono=True),
            state="disabled",
            fg_color=BG_CONSOLE,
            text_color=TEXT_MUTED,
            border_width=1,
            border_color=BORDER_CONSOLE,
            corner_radius=10
        )
        self.textbox.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")
        
        # Setup tags on underlying tk.Text
        self.textbox_widget = self.textbox._textbox if hasattr(self.textbox, "_textbox") else self.textbox
        self.textbox_widget.tag_config("info", foreground=TEXT_MUTED)
        self.textbox_widget.tag_config("error", foreground=COLOR_ERROR)
        self.textbox_widget.tag_config("success", foreground=COLOR_SUCCESS)
        self.textbox_widget.tag_config("warning", foreground=COLOR_WARNING)
        
    def write_log(self, message, level="info"):
        """
        Thread-safe logger. Automatically schedules UI updates on the main thread.
        """
        def _do_write():
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            formatted_msg = f"[{timestamp}] {message}\n"
            
            self.textbox.configure(state="normal")
            self.textbox.insert("end", formatted_msg, level)
            self.textbox.see("end")
            self.textbox.configure(state="disabled")
            
        self.after(0, _do_write)

    def clear_log(self):
        """
        Clears the console.
        """
        def _do_clear():
            self.textbox.configure(state="normal")
            self.textbox.delete("1.0", "end")
            self.textbox.configure(state="disabled")
        self.after(0, _do_clear)


class FileListScrollFrame(ctk.CTkScrollableFrame):
    """
    Scrollable panel displaying a list of files queued for batch conversion,
    including file size, format icons, status labels, and single removal buttons.
    """
    def __init__(self, parent, on_remove_callback=None, **kwargs):
        # Apply standard styles
        kwargs.setdefault("fg_color", BG_CONSOLE)
        kwargs.setdefault("border_color", BORDER_CONSOLE)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 10)
        super().__init__(parent, **kwargs)
        
        self.on_remove_callback = on_remove_callback
        self.grid_columnconfigure(0, weight=1)
        
        # Internal files registry: path -> row GUI components dictionary
        self.files_registry = {}
        
        # Cache icons
        self.trash_icon = get_ctk_image("trash", color=COLOR_ERROR, size=(16, 16))
        self.doc_icon = get_ctk_image("document", color=TEXT_MUTED, size=(18, 18))
        self.success_icon = get_ctk_image("checkmark", color=COLOR_SUCCESS, size=(14, 14))

    def add_file(self, filepath):
        """
        Adds a file to the list visually.
        """
        filepath = os.path.abspath(filepath)
        if filepath in self.files_registry:
            return False  # Already in list
            
        filename = os.path.basename(filepath)
        size_bytes = os.path.getsize(filepath) if os.path.exists(filepath) else -1
        size_str = format_size(size_bytes)
        
        # Create row frame
        row_frame = ctk.CTkFrame(
            self, 
            fg_color=BG_CARD, 
            border_color=BORDER_CARD, 
            border_width=1, 
            corner_radius=8,
            height=45
        )
        row_frame.grid(row=len(self.files_registry), column=0, padx=5, pady=4, sticky="ew")
        row_frame.grid_propagate(False)
        row_frame.grid_columnconfigure(1, weight=1)  # Name expands
        row_frame.grid_rowconfigure(0, weight=1)
        
        # Icon col (0)
        icon_label = ctk.CTkLabel(row_frame, text="", image=self.doc_icon)
        icon_label.grid(row=0, column=0, padx=(12, 8), sticky="w")
        
        # Name col (1)
        name_label = ctk.CTkLabel(
            row_frame, 
            text=filename, 
            font=get_font(12, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w"
        )
        name_label.grid(row=0, column=1, padx=2, sticky="ew")
        
        # Size col (2)
        size_label = ctk.CTkLabel(
            row_frame, 
            text=size_str, 
            font=get_font(11),
            text_color=TEXT_MUTED
        )
        size_label.grid(row=0, column=2, padx=15, sticky="e")
        
        # Status Badge (3)
        status_label = ctk.CTkLabel(
            row_frame,
            text="Pending",
            font=get_font(11, weight="bold"),
            text_color=TEXT_MUTED,
            fg_color="#1E293B",
            corner_radius=6,
            height=20,
            padx=8
        )
        status_label.grid(row=0, column=3, padx=(0, 15), sticky="e")
        
        # Action button (4)
        remove_btn = ctk.CTkButton(
            row_frame,
            text="",
            image=self.trash_icon,
            width=28,
            height=28,
            fg_color="transparent",
            hover_color="#311F25",
            corner_radius=6,
            command=lambda: self.remove_file(filepath)
        )
        remove_btn.grid(row=0, column=4, padx=(0, 10), sticky="e")
        
        # Store components
        self.files_registry[filepath] = {
            "frame": row_frame,
            "status_label": status_label,
            "remove_btn": remove_btn
        }
        
        return True

    def remove_file(self, filepath):
        """
        Removes a file from the list.
        """
        filepath = os.path.abspath(filepath)
        if filepath in self.files_registry:
            # Destroy widgets
            components = self.files_registry[filepath]
            components["frame"].destroy()
            del self.files_registry[filepath]
            
            # Re-index remaining grid items
            self.reindex_grid()
            
            # Trigger callback
            if self.on_remove_callback:
                self.on_remove_callback(filepath)

    def reindex_grid(self):
        """
        Re-align grid indexes of frames to avoid gaps when removing.
        """
        for i, filepath in enumerate(self.files_registry):
            self.files_registry[filepath]["frame"].grid(row=i, column=0, padx=5, pady=4, sticky="ew")

    def update_status(self, filepath, status_text, color, fg_bg=None):
        """
        Updates the status text and color badge for a specific file. Thread-safe.
        """
        filepath = os.path.abspath(filepath)
        if filepath in self.files_registry:
            def _do_update():
                lbl = self.files_registry[filepath]["status_label"]
                lbl.configure(text=status_text, text_color=color)
                if fg_bg:
                    lbl.configure(fg_color=fg_bg)
            self.after(0, _do_update)

    def set_all_status(self, status_text, color, fg_bg=None):
        """
        Resets status for all files in the list.
        """
        for filepath in self.files_registry:
            self.update_status(filepath, status_text, color, fg_bg)

    def set_actions_state(self, enabled=True):
        """
        Enables or disables individual deletion buttons (e.g. during active conversions).
        """
        state = "normal" if enabled else "disabled"
        def _do_toggle():
            for filepath in self.files_registry:
                self.files_registry[filepath]["remove_btn"].configure(state=state)
        self.after(0, _do_toggle)

    def clear_all(self):
        """
        Clears the whole list.
        """
        def _do_clear():
            for filepath in list(self.files_registry.keys()):
                self.files_registry[filepath]["frame"].destroy()
            self.files_registry.clear()
        self.after(0, _do_clear)

    def get_all_filepaths(self):
        """
        Returns a list of all current filepaths in the registry.
        """
        return list(self.files_registry.keys())
