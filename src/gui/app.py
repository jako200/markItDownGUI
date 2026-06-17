import os
import threading
from tkinter import filedialog
import customtkinter as ctk

from src.gui.theme import (
    BG_MAIN, BG_CARD, BORDER_CARD, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_SUCCESS, COLOR_ERROR, TEXT_PRIMARY, TEXT_MUTED, get_font,
    COLOR_ACCENT_MUTED, COLOR_WARNING
)
from src.gui.widgets import LogConsole, FileListScrollFrame
from src.core.converter import MarkdownConverter, BatchConversionWorker
from src.utils.icons import get_ctk_image
from src.utils.helpers import is_supported_file

class MarkItDownStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Main window setup
        self.title("MarkItDown Studio")
        self.geometry("900x820")
        self.minsize(850, 720)
        self.configure(fg_color=BG_MAIN)

        # Config layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Main Tabview (expands)
        self.grid_rowconfigure(2, weight=0) # Console
        
        # Core converter
        self.converter = MarkdownConverter()
        self.batch_worker = None

        # State vars
        self.selected_single_input = ""
        self.selected_single_output = ""
        
        self.batch_output_mode = "source"  # "source" or "custom"
        self.selected_batch_output_dir = ""
        self.is_converting = False

        # Load themes & icons
        self.init_icons()
        
        # Build widgets
        self.create_widgets()
        
        # Log system status
        self.log_init_status()

    def init_icons(self):
        """Pre-loads vector icons."""
        self.doc_icon = get_ctk_image("document", color="#FFFFFF", size=(18, 18))
        self.doc_icon_muted = get_ctk_image("document", color=TEXT_MUTED, size=(18, 18))
        self.folder_icon = get_ctk_image("folder", color="#FFFFFF", size=(18, 18))
        self.folder_icon_muted = get_ctk_image("folder", color=TEXT_MUTED, size=(18, 18))
        self.lightning_icon = get_ctk_image("lightning", color="#FFFFFF", size=(18, 18))
        self.gear_icon = get_ctk_image("gear", color="#FFFFFF", size=(18, 18))
        self.checkmark_icon = get_ctk_image("checkmark", color=COLOR_SUCCESS, size=(16, 16))
        self.clear_icon = get_ctk_image("clear", color="#FFFFFF", size=(16, 16))

    def create_widgets(self):
        # ----------------------------------------------------
        # 1. HEADER FRAME
        # ----------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="MarkItDown Studio", 
            font=get_font(28, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Convertitore GUI elegante per Microsoft MarkItDown", 
            font=get_font(13),
            text_color=TEXT_MUTED
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # ----------------------------------------------------
        # 2. MAIN TABVIEW
        # ----------------------------------------------------
        self.tabview = ctk.CTkTabview(
            self, 
            fg_color="transparent",
            segmented_button_fg_color=BG_CARD,
            segmented_button_selected_color=COLOR_ACCENT,
            segmented_button_selected_hover_color=COLOR_ACCENT_HOVER,
            segmented_button_unselected_color=BG_MAIN,
            segmented_button_unselected_hover_color=COLOR_ACCENT_MUTED,
            text_color=TEXT_PRIMARY,
            font=get_font(13, weight="bold")
        )
        self.tabview.grid(row=1, column=0, padx=30, pady=(0, 10), sticky="nsew")
        
        # Add tabs
        self.tabview.add("Conversione Singola")
        self.tabview.add("Conversione Multipla")
        
        # Setup tabs layouts
        self.setup_single_conversion_tab()
        self.setup_batch_conversion_tab()

        # ----------------------------------------------------
        # 3. CONSOLE LOGS (BOTTOM)
        # ----------------------------------------------------
        self.console = LogConsole(self)
        self.console.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="ew", minsize=180)

    def setup_single_conversion_tab(self):
        tab = self.tabview.tab("Conversione Singola")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=0) # Card input
        tab.grid_rowconfigure(1, weight=0) # Card output
        tab.grid_rowconfigure(2, weight=1) # Spacing
        tab.grid_rowconfigure(3, weight=0) # Action Frame

        # --- CARD INPUT ---
        self.single_input_card = ctk.CTkFrame(
            tab, fg_color=BG_CARD, border_color=BORDER_CARD, border_width=1, corner_radius=14
        )
        self.single_input_card.grid(row=0, column=0, pady=10, sticky="ew")
        self.single_input_card.grid_columnconfigure(0, weight=1)
        
        self.single_input_title = ctk.CTkLabel(
            self.single_input_card,
            text="  Seleziona File da Convertire",
            image=self.doc_icon_muted,
            compound="left",
            font=get_font(14, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.single_input_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")

        # Feedback/status line
        self.single_status_frame = ctk.CTkFrame(self.single_input_card, fg_color="transparent")
        self.single_status_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(2, 8), sticky="w")
        
        self.single_status_icon = ctk.CTkLabel(self.single_status_frame, text="")
        self.single_status_icon.pack(side="left", padx=(0, 5))
        
        self.single_status_text = ctk.CTkLabel(
            self.single_status_frame, 
            text="Nessun file selezionato per la conversione", 
            font=get_font(12, slant="italic"),
            text_color=TEXT_MUTED
        )
        self.single_status_text.pack(side="left")

        # Input Path entry & Browse btn
        self.single_input_entry = ctk.CTkEntry(
            self.single_input_card, 
            placeholder_text="Fai clic su 'Sfoglia' per caricare un file...", 
            state="readonly",
            height=38,
            font=get_font(12),
            fg_color=BG_MAIN,
            border_color=BORDER_CARD,
            text_color=TEXT_PRIMARY,
            corner_radius=8
        )
        self.single_input_entry.grid(row=2, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")

        self.single_select_input_btn = ctk.CTkButton(
            self.single_input_card, 
            text="Sfoglia...", 
            image=self.doc_icon,
            compound="left",
            width=130,
            height=38,
            command=self.select_single_input,
            font=get_font(12, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=10
        )
        self.single_select_input_btn.grid(row=2, column=1, padx=(0, 20), pady=(0, 20), sticky="e")

        # --- CARD OUTPUT ---
        self.single_output_card = ctk.CTkFrame(
            tab, fg_color=BG_CARD, border_color=BORDER_CARD, border_width=1, corner_radius=14
        )
        self.single_output_card.grid(row=1, column=0, pady=10, sticky="ew")
        self.single_output_card.grid_columnconfigure(0, weight=1)

        self.single_output_title = ctk.CTkLabel(
            self.single_output_card,
            text="  Configurazione Destinazione Output",
            image=self.folder_icon_muted,
            compound="left",
            font=get_font(14, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.single_output_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 8), sticky="w")

        # Output Path entry & Modify btn
        self.single_output_entry = ctk.CTkEntry(
            self.single_output_card, 
            placeholder_text="Verrà generato un file .md nello stesso percorso di origine...", 
            state="readonly",
            height=38,
            font=get_font(12),
            fg_color=BG_MAIN,
            border_color=BORDER_CARD,
            text_color=TEXT_PRIMARY,
            corner_radius=8
        )
        self.single_output_entry.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")

        self.single_select_output_btn = ctk.CTkButton(
            self.single_output_card, 
            text="Modifica...", 
            image=self.folder_icon_muted,
            compound="left",
            width=130,
            height=38,
            command=self.select_single_output,
            state="disabled",
            font=get_font(12, weight="bold"),
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_CARD,
            text_color=TEXT_MUTED,
            hover_color=COLOR_ACCENT_MUTED,
            corner_radius=10
        )
        self.single_select_output_btn.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky="e")

        # --- ACTIONS AREA ---
        self.single_action_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.single_action_frame.grid(row=3, column=0, pady=(10, 15), sticky="ew")
        self.single_action_frame.grid_columnconfigure(0, weight=1)

        self.single_progress = ctk.CTkProgressBar(
            self.single_action_frame, 
            height=6,
            fg_color=COLOR_ACCENT_MUTED,
            progress_color=COLOR_ACCENT,
            corner_radius=3
        )
        self.single_progress.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        self.single_progress.set(0.0)

        self.single_convert_btn = ctk.CTkButton(
            self.single_action_frame, 
            text="Converti in Markdown", 
            image=self.lightning_icon,
            compound="left",
            height=48,
            command=self.start_single_conversion,
            state="disabled",
            font=get_font(14, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=12
        )
        self.single_convert_btn.grid(row=1, column=0, sticky="ew")

    def setup_batch_conversion_tab(self):
        tab = self.tabview.tab("Conversione Multipla")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1) # File list container (expands)
        tab.grid_rowconfigure(1, weight=0) # Card output directory config
        tab.grid_rowconfigure(2, weight=0) # Action Frame

        # --- FILE LIST CONTAINER ---
        self.batch_list_container = ctk.CTkFrame(tab, fg_color="transparent")
        self.batch_list_container.grid(row=0, column=0, pady=(10, 5), sticky="nsew")
        self.batch_list_container.grid_columnconfigure(0, weight=1)
        self.batch_list_container.grid_rowconfigure(1, weight=1)

        # Top controls: "Aggiungi", "Svuota"
        self.batch_list_controls = ctk.CTkFrame(self.batch_list_container, fg_color="transparent")
        self.batch_list_controls.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        
        self.batch_count_lbl = ctk.CTkLabel(
            self.batch_list_controls,
            text="Coda file da convertire: 0 file",
            font=get_font(12, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.batch_count_lbl.pack(side="left", padx=5)

        self.batch_clear_btn = ctk.CTkButton(
            self.batch_list_controls,
            text="Svuota Lista",
            image=self.clear_icon,
            compound="left",
            width=110,
            height=30,
            fg_color="transparent",
            border_width=1,
            border_color=COLOR_ERROR,
            text_color=COLOR_ERROR,
            hover_color="#311F25",
            corner_radius=8,
            command=self.clear_batch_list
        )
        self.batch_clear_btn.pack(side="right", padx=5)

        self.batch_add_btn = ctk.CTkButton(
            self.batch_list_controls,
            text="Aggiungi File...",
            image=self.doc_icon,
            compound="left",
            width=140,
            height=30,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.select_batch_files
        )
        self.batch_add_btn.pack(side="right", padx=5)

        # File List Scroll Frame
        self.file_list_frame = FileListScrollFrame(
            self.batch_list_container, 
            on_remove_callback=self.on_batch_file_removed
        )
        self.file_list_frame.grid(row=1, column=0, sticky="nsew")

        # --- CARD BATCH OUTPUT ---
        self.batch_output_card = ctk.CTkFrame(
            tab, fg_color=BG_CARD, border_color=BORDER_CARD, border_width=1, corner_radius=14
        )
        self.batch_output_card.grid(row=1, column=0, pady=10, sticky="ew")
        self.batch_output_card.grid_columnconfigure(0, weight=1)

        self.batch_output_title = ctk.CTkLabel(
            self.batch_output_card,
            text="  Configurazione Destinazione Output Multiplo",
            image=self.folder_icon_muted,
            compound="left",
            font=get_font(14, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.batch_output_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 8), sticky="w")

        # Options
        self.batch_mode_var = ctk.StringVar(value="source")
        self.radio_source = ctk.CTkRadioButton(
            self.batch_output_card,
            text="Salva nella stessa cartella di origine del file sorgente",
            variable=self.batch_mode_var,
            value="source",
            command=self.toggle_batch_output_mode,
            font=get_font(12),
            text_color=TEXT_PRIMARY,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER
        )
        self.radio_source.grid(row=1, column=0, columnspan=2, padx=25, pady=(5, 10), sticky="w")

        self.radio_custom = ctk.CTkRadioButton(
            self.batch_output_card,
            text="Salva tutti i file convertiti in una cartella specifica",
            variable=self.batch_mode_var,
            value="custom",
            command=self.toggle_batch_output_mode,
            font=get_font(12),
            text_color=TEXT_PRIMARY,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER
        )
        self.radio_custom.grid(row=2, column=0, columnspan=2, padx=25, pady=(0, 10), sticky="w")

        # Path input & modify (initially hidden/disabled style)
        self.batch_output_entry = ctk.CTkEntry(
            self.batch_output_card, 
            placeholder_text="I file Markdown verranno posizionati accanto all'originale...", 
            state="readonly",
            height=38,
            font=get_font(12),
            fg_color=BG_MAIN,
            border_color=BORDER_CARD,
            text_color=TEXT_MUTED,
            corner_radius=8
        )
        self.batch_output_entry.grid(row=3, column=0, padx=(25, 10), pady=(0, 20), sticky="ew")

        self.batch_select_output_btn = ctk.CTkButton(
            self.batch_output_card, 
            text="Sfoglia...", 
            image=self.folder_icon_muted,
            compound="left",
            width=130,
            height=38,
            command=self.select_batch_output_dir,
            state="disabled",
            font=get_font(12, weight="bold"),
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_CARD,
            text_color=TEXT_MUTED,
            hover_color=COLOR_ACCENT_MUTED,
            corner_radius=10
        )
        self.batch_select_output_btn.grid(row=3, column=1, padx=(0, 25), pady=(0, 20), sticky="e")

        # --- BATCH ACTIONS AREA ---
        self.batch_action_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.batch_action_frame.grid(row=2, column=0, pady=(10, 15), sticky="ew")
        self.batch_action_frame.grid_columnconfigure(0, weight=1)

        self.batch_progress = ctk.CTkProgressBar(
            self.batch_action_frame, 
            height=6,
            fg_color=COLOR_ACCENT_MUTED,
            progress_color=COLOR_ACCENT,
            corner_radius=3
        )
        self.batch_progress.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        self.batch_progress.set(0.0)

        self.batch_convert_btn = ctk.CTkButton(
            self.batch_action_frame, 
            text="Converti Tutti i File", 
            image=self.lightning_icon,
            compound="left",
            height=48,
            command=self.start_batch_conversion,
            state="disabled",
            font=get_font(14, weight="bold"),
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=12
        )
        self.batch_convert_btn.grid(row=1, column=0, sticky="ew")

    # ----------------------------------------------------
    # SYSTEM INITIALIZATION & DIAGNOSTIC LOGS
    # ----------------------------------------------------
    def log_init_status(self):
        self.console.write_log("Benvenuto in MarkItDown Studio!", "info")
        if not self.converter.is_available():
            self.console.write_log(
                "ERRORE DI SISTEMA: La libreria 'markitdown' non è installata o non si è inizializzata.\n"
                "Installa la libreria eseguendo: pip install \"markitdown[all]\" nel terminale.",
                "error"
            )
            # Disable actions
            self.single_convert_btn.configure(state="disabled")
            self.batch_convert_btn.configure(state="disabled")
            self.single_select_input_btn.configure(state="disabled")
            self.batch_add_btn.configure(state="disabled")
        else:
            self.console.write_log("Libreria 'markitdown' caricata con successo. Pronto per la conversione.", "success")
            self.update_convert_buttons_state()

    # ----------------------------------------------------
    # SINGLE CONVERSION CONTROLS & LOGIC
    # ----------------------------------------------------
    def select_single_input(self):
        """Browse dialog for a single file to convert."""
        file_types = [
            ("File supportati", "*.docx;*.pptx;*.xlsx;*.pdf;*.html;*.htm;*.txt;*.csv;*.xml;*.json"),
            ("Documenti Word", "*.docx"),
            ("Presentazioni PowerPoint", "*.pptx"),
            ("Fogli Excel", "*.xlsx"),
            ("File PDF", "*.pdf"),
            ("Pagine Web HTML", "*.html;*.htm"),
            ("File di testo / Codice", "*.txt;*.csv;*.xml;*.json"),
            ("Tutti i file", "*.*")
        ]
        
        path = filedialog.askopenfilename(
            title="Seleziona il file da convertire",
            filetypes=file_types
        )
        
        if path:
            self.selected_single_input = os.path.abspath(path)
            
            # Show in entry
            self.single_input_entry.configure(state="normal")
            self.single_input_entry.delete(0, "end")
            self.single_input_entry.insert(0, self.selected_single_input)
            self.single_input_entry.configure(state="readonly")
            
            # Default output: same folder + .md
            dir_name, file_name = os.path.split(self.selected_single_input)
            base_name, _ = os.path.splitext(file_name)
            self.selected_single_output = os.path.join(dir_name, f"{base_name}.md")
            
            self.single_output_entry.configure(state="normal")
            self.single_output_entry.delete(0, "end")
            self.single_output_entry.insert(0, self.selected_single_output)
            self.single_output_entry.configure(state="readonly")

            # UI Feedback
            self.single_input_card.configure(border_color=COLOR_SUCCESS)
            self.single_status_icon.configure(image=self.checkmark_icon)
            self.single_status_text.configure(
                text=f"Pronto: {file_name}",
                text_color=COLOR_SUCCESS,
                font=get_font(12, weight="bold")
            )

            # Enable modify output btn
            self.single_select_output_btn.configure(
                state="normal",
                fg_color="transparent",
                border_color=BORDER_CARD,
                text_color=TEXT_PRIMARY,
                image=self.folder_icon
            )
            
            self.console.write_log(f"Caricato file singolo: {file_name} ({self.selected_single_input})", "info")
            self.console.write_log(f"Destinazione predefinita: {self.selected_single_output}", "info")
            
            self.update_convert_buttons_state()

    def select_single_output(self):
        """Select custom output path for single conversion."""
        if not self.selected_single_input:
            return
            
        initial_dir = os.path.dirname(self.selected_single_output)
        initial_file = os.path.basename(self.selected_single_output)
        
        path = filedialog.asksaveasfilename(
            title="Seleziona la destinazione del file Markdown",
            defaultextension=".md",
            filetypes=[("File Markdown", "*.md"), ("Tutti i file", "*.*")],
            initialdir=initial_dir,
            initialfile=initial_file
        )
        
        if path:
            self.selected_single_output = os.path.abspath(path)
            self.single_output_entry.configure(state="normal")
            self.single_output_entry.delete(0, "end")
            self.single_output_entry.insert(0, self.selected_single_output)
            self.single_output_entry.configure(state="readonly")
            self.console.write_log(f"Destinazione file singolo modificata in: {self.selected_single_output}", "info")

    def start_single_conversion(self):
        """Launch single file conversion on a background thread."""
        if not self.converter.is_available() or self.is_converting:
            return
            
        if not self.selected_single_input or not self.selected_single_output:
            self.console.write_log("Errore: Selezionare prima un file e un percorso di output validi.", "error")
            return
            
        self.is_converting = True
        
        # Disable UI components
        self.tabview.configure(state="disabled") # Disables switching tabs or changing tab options
        self.single_convert_btn.configure(state="disabled", text="Conversione in corso...")
        self.single_select_input_btn.configure(state="disabled")
        self.single_select_output_btn.configure(state="disabled")
        
        self.single_progress.configure(mode="indeterminate")
        self.single_progress.start()
        
        filename = os.path.basename(self.selected_single_input)
        self.console.write_log(f"Avvio conversione per il file: {filename}", "info")
        
        # Start worker thread
        conversion_thread = threading.Thread(
            target=self.run_single_conversion_worker,
            args=(self.selected_single_input, self.selected_single_output),
            daemon=True
        )
        conversion_thread.start()

    def run_single_conversion_worker(self, input_path, output_path):
        try:
            self.converter.convert(input_path, output_path)
            self.after(0, self.on_single_success, output_path)
        except Exception as e:
            self.after(0, self.on_single_failure, str(e))

    def on_single_success(self, output_path):
        self.console.write_log("Conversione singola completata con successo!", "success")
        self.console.write_log(f"File generato correttamente in: {output_path}", "success")
        self.reset_single_gui_state()

    def on_single_failure(self, error_message):
        self.console.write_log("ERRORE DURANTE LA CONVERSIONE SINGOLA:", "error")
        self.console.write_log(error_message, "error")
        self.reset_single_gui_state()

    def reset_single_gui_state(self):
        self.is_converting = False
        self.tabview.configure(state="normal")
        
        # Restore button states
        self.single_select_input_btn.configure(state="normal")
        self.single_select_output_btn.configure(state="normal")
        self.single_convert_btn.configure(state="normal", text="Converti in Markdown")
        
        # Stop progress
        self.single_progress.stop()
        self.single_progress.configure(mode="determinate")
        self.single_progress.set(0.0)

    # ----------------------------------------------------
    # BATCH CONVERSION CONTROLS & LOGIC (TAB 2)
    # ----------------------------------------------------
    def select_batch_files(self):
        """Browse dialog to add multiple files to the batch queue."""
        file_types = [
            ("File supportati", "*.docx;*.pptx;*.xlsx;*.pdf;*.html;*.htm;*.txt;*.csv;*.xml;*.json"),
            ("Tutti i file", "*.*")
        ]
        
        paths = filedialog.askopenfilenames(
            title="Seleziona uno o più file da aggiungere",
            filetypes=file_types
        )
        
        if paths:
            added_count = 0
            for path in paths:
                resolved_path = os.path.abspath(path)
                # Filter supported files or just load them and show warnings on conversion
                if self.file_list_frame.add_file(resolved_path):
                    added_count += 1
                    self.console.write_log(f"Aggiunto alla coda: {os.path.basename(resolved_path)}", "info")
                    
            if added_count > 0:
                self.update_batch_count()
                self.update_convert_buttons_state()

    def on_batch_file_removed(self, filepath):
        """Callback when a file is manually removed from list."""
        self.console.write_log(f"Rimosso dalla coda: {os.path.basename(filepath)}", "info")
        self.update_batch_count()
        self.update_convert_buttons_state()

    def clear_batch_list(self):
        """Clears the whole batch queue."""
        self.file_list_frame.clear_all()
        self.update_batch_count()
        self.update_convert_buttons_state()
        self.console.write_log("Coda di conversione multipla svuotata.", "info")

    def update_batch_count(self):
        num_files = len(self.file_list_frame.get_all_filepaths())
        self.batch_count_lbl.configure(text=f"Coda file da convertire: {num_files} file")

    def toggle_batch_output_mode(self):
        """Toggle output directory configuration."""
        mode = self.batch_mode_var.get()
        self.batch_output_mode = mode
        
        if mode == "source":
            self.batch_output_entry.configure(state="normal")
            self.batch_output_entry.delete(0, "end")
            self.batch_output_entry.insert(0, "")
            self.batch_output_entry.configure(
                placeholder_text="I file Markdown verranno posizionati accanto all'originale...", 
                state="readonly",
                text_color=TEXT_MUTED
            )
            self.batch_select_output_btn.configure(
                state="disabled",
                fg_color="transparent",
                border_color=BORDER_CARD,
                text_color=TEXT_MUTED,
                image=self.folder_icon_muted
            )
        else:
            # Custom mode
            self.batch_output_entry.configure(state="normal")
            self.batch_output_entry.delete(0, "end")
            if self.selected_batch_output_dir:
                self.batch_output_entry.insert(0, self.selected_batch_output_dir)
            self.batch_output_entry.configure(
                placeholder_text="Seleziona la cartella di destinazione...", 
                state="readonly",
                text_color=TEXT_PRIMARY
            )
            self.batch_select_output_btn.configure(
                state="normal",
                fg_color="transparent",
                border_color=BORDER_CARD,
                text_color=TEXT_PRIMARY,
                image=self.folder_icon
            )
            
        self.update_convert_buttons_state()

    def select_batch_output_dir(self):
        """Browse dialog for batch destination folder."""
        path = filedialog.askdirectory(
            title="Seleziona la cartella di destinazione comune"
        )
        if path:
            self.selected_batch_output_dir = os.path.abspath(path)
            self.batch_output_entry.configure(state="normal")
            self.batch_output_entry.delete(0, "end")
            self.batch_output_entry.insert(0, self.selected_batch_output_dir)
            self.batch_output_entry.configure(state="readonly")
            self.console.write_log(f"Cartella di destinazione batch impostata su: {self.selected_batch_output_dir}", "info")
            self.update_convert_buttons_state()

    def start_batch_conversion(self):
        """Triggers the batch conversion worker thread."""
        if not self.converter.is_available() or self.is_converting:
            return
            
        files = self.file_list_frame.get_all_filepaths()
        if not files:
            self.console.write_log("Errore: La coda dei file è vuota.", "error")
            return
            
        # If output mode is custom, verify path is selected
        out_dir = None
        if self.batch_output_mode == "custom":
            if not self.selected_batch_output_dir:
                self.console.write_log("Errore: Selezionare una cartella di destinazione valida per i file convertiti.", "error")
                return
            out_dir = self.selected_batch_output_dir

        self.is_converting = True
        
        # Reset all file status badges to "In attesa"
        self.file_list_frame.set_all_status("In attesa", TEXT_MUTED, "#1E293B")
        self.file_list_frame.set_actions_state(False) # Disable trash buttons
        
        # UI controls state
        self.tabview.configure(state="disabled")
        self.batch_add_btn.configure(state="disabled")
        self.batch_clear_btn.configure(state="disabled")
        self.radio_source.configure(state="disabled")
        self.radio_custom.configure(state="disabled")
        self.batch_select_output_btn.configure(state="disabled")
        
        # Turn convert button into a Cancel button
        self.batch_convert_btn.configure(
            text="Annulla Conversione",
            image=self.clear_icon,
            fg_color=COLOR_ERROR,
            hover_color=COLOR_ERROR_HOVER
        )
        # Re-link button command to cancel
        self.batch_convert_btn.configure(command=self.cancel_batch_conversion)
        
        # Setup callbacks
        callbacks = {
            "on_file_start": self.on_batch_file_start,
            "on_file_success": self.on_batch_file_success,
            "on_file_error": self.on_batch_file_error,
            "on_progress": self.on_batch_progress,
            "on_complete": self.on_batch_complete
        }
        
        self.console.write_log(f"Avvio conversione batch per {len(files)} file...", "info")
        self.batch_progress.set(0.0)
        
        # Start worker
        self.batch_worker = BatchConversionWorker(
            converter=self.converter,
            files=files,
            output_dir=out_dir,
            callbacks=callbacks
        )
        self.batch_worker.start()

    def cancel_batch_conversion(self):
        """Triggers batch conversion cancellation flag."""
        if self.batch_worker:
            self.console.write_log("Richiesta di annullamento inviata... Attesa completamento operazione corrente.", "warning")
            self.batch_worker.cancel()
            self.batch_convert_btn.configure(state="disabled", text="Annullamento in corso...")

    # --- BATCH WORKER CALLBACKS ---
    def on_batch_file_start(self, filepath):
        filename = os.path.basename(filepath)
        self.console.write_log(f"Inizio conversione: {filename}", "info")
        self.file_list_frame.update_status(filepath, "In corso...", COLOR_WARNING, "#451A03")

    def on_batch_file_success(self, filepath, output_path):
        filename = os.path.basename(filepath)
        self.console.write_log(f"Conversione riuscita: {filename} -> {os.path.basename(output_path)}", "success")
        self.file_list_frame.update_status(filepath, "Successo", COLOR_SUCCESS, "#064E3B")

    def on_batch_file_error(self, filepath, error_msg):
        filename = os.path.basename(filepath)
        self.console.write_log(f"ERRORE su {filename}: {error_msg}", "error")
        self.file_list_frame.update_status(filepath, "Errore", COLOR_ERROR, "#4C0519")

    def on_batch_progress(self, current, total):
        progress_val = current / total
        self.batch_progress.set(progress_val)

    def on_batch_complete(self, success_num, error_num, is_cancelled):
        self.is_converting = False
        
        # Restore GUI states
        self.tabview.configure(state="normal")
        self.batch_add_btn.configure(state="normal")
        self.batch_clear_btn.configure(state="normal")
        self.radio_source.configure(state="normal")
        self.radio_custom.configure(state="normal")
        self.file_list_frame.set_actions_state(True)
        
        # Restore convert button action and styling
        self.batch_convert_btn.configure(
            text="Converti Tutti i File",
            image=self.lightning_icon,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            state="normal"
        )
        self.batch_convert_btn.configure(command=self.start_batch_conversion)
        
        # Reset output selector states
        self.toggle_batch_output_mode()
        
        # Log summary
        if is_cancelled:
            self.console.write_log(f"Conversione batch ANNULLATA. File convertiti con successo: {success_num}, Falliti: {error_num}", "warning")
        else:
            self.console.write_log(f"Conversione batch completata! Riusciti: {success_num}, Falliti: {error_num}", "success")
            
        self.update_convert_buttons_state()

    # ----------------------------------------------------
    # SHARED HELPERS
    # ----------------------------------------------------
    def update_convert_buttons_state(self):
        """Enables/disables conversion run buttons depending on state validation."""
        if not self.converter.is_available():
            self.single_convert_btn.configure(state="disabled")
            self.batch_convert_btn.configure(state="disabled")
            return

        # Single
        if self.selected_single_input and self.selected_single_output and not self.is_converting:
            self.single_convert_btn.configure(state="normal")
        else:
            self.single_convert_btn.configure(state="disabled")

        # Batch
        batch_files = self.file_list_frame.get_all_filepaths()
        batch_output_valid = True
        
        if self.batch_output_mode == "custom" and not self.selected_batch_output_dir:
            batch_output_valid = False
            
        if batch_files and batch_output_valid and not self.is_converting:
            self.batch_convert_btn.configure(state="normal")
        else:
            self.batch_convert_btn.configure(state="disabled")


def launch():
    """Main launch script entry point."""
    app = MarkItDownStudio()
    app.mainloop()

if __name__ == "__main__":
    launch()
