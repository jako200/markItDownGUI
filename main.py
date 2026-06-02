# Installazione delle dipendenze:
# Aprire il terminale e digitare:
# pip install customtkinter markitdown[all]
#
# Se si riscontrano problemi con la sintassi delle parentesi quadre in alcune shell (es. PowerShell), utilizzare:
# pip install customtkinter "markitdown[all]"

import os
import sys
import threading
import datetime
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Tentativo di importazione di MarkItDown per evitare crash all'avvio in caso di mancanza della libreria
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

# Configurazione del tema e della modalità di visualizzazione predefinita
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MarkItDownStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurazione Finestra Principale
        self.title("MarkItDown Studio")
        self.geometry("800x650")
        self.minsize(700, 550)

        # Stato interno
        self.selected_input_path = ""
        self.selected_output_path = ""
        self.is_converting = False

        # Configurazione layout griglia principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # La console dei log si espande

        self.create_widgets()

        # Messaggio di benvenuto / stato librerie
        self.log_message("Benvenuto in MarkItDown Studio!", "info")
        if not MARKITDOWN_AVAILABLE:
            self.log_message(
                "ERRORE DI SISTEMA: La libreria 'markitdown' non è installata.\n"
                "Installa la libreria eseguendo: pip install \"markitdown[all]\" nel terminale.",
                "error"
            )
            self.convert_button.configure(state="disabled")
        else:
            self.log_message("Libreria 'markitdown' caricata con successo. Pronto per la conversione.", "info")

    def create_widgets(self):
        # ----------------------------------------------------
        # 1. HEADER FRAME
        # ----------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Titolo dell'applicazione
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="MarkItDown Studio", 
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Sottotitolo
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Convertitore GUI elegante per Microsoft MarkItDown", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="gray"
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # Toggle Dark/Light Mode
        self.theme_switch = ctk.CTkSwitch(
            self.header_frame, 
            text="Modalità Scura", 
            command=self.toggle_theme,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.theme_switch.select()  # Attivo di default per Dark Mode
        self.theme_switch.grid(row=0, column=1, rowspan=2, sticky="e", padx=10)

        # ----------------------------------------------------
        # 2. FILE MANAGEMENT CARD (INPUT & OUTPUT)
        # ----------------------------------------------------
        self.card_frame = ctk.CTkFrame(self, corner_radius=12)
        self.card_frame.grid(row=1, column=0, padx=25, pady=10, sticky="ew")
        self.card_frame.grid_columnconfigure(1, weight=1)

        # --- Sezione File Origine ---
        self.input_label = ctk.CTkLabel(
            self.card_frame, 
            text="File di Origine:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.input_label.grid(row=0, column=0, padx=(20, 10), pady=(20, 5), sticky="w")

        self.input_entry = ctk.CTkEntry(
            self.card_frame, 
            placeholder_text="Seleziona un file da convertire...", 
            state="readonly",
            height=35,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.input_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=(0, 15), sticky="ew")

        self.select_file_btn = ctk.CTkButton(
            self.card_frame, 
            text="Sfoglia...", 
            width=100,
            height=35,
            command=self.select_input_file,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.select_file_btn.grid(row=1, column=2, padx=(0, 20), pady=(0, 15), sticky="ew")

        # --- Sezione Destinazione Output ---
        self.output_label = ctk.CTkLabel(
            self.card_frame, 
            text="Destinazione Output:", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        )
        self.output_label.grid(row=2, column=0, padx=(20, 10), pady=(5, 5), sticky="w")

        self.output_entry = ctk.CTkEntry(
            self.card_frame, 
            placeholder_text="La cartella di output predefinita sarà la stessa del file d'origine...", 
            state="readonly",
            height=35,
            font=ctk.CTkFont(family="Segoe UI", size=12)
        )
        self.output_entry.grid(row=3, column=0, columnspan=2, padx=(20, 10), pady=(0, 20), sticky="ew")

        self.select_output_btn = ctk.CTkButton(
            self.card_frame, 
            text="Cambia...", 
            width=100,
            height=35,
            command=self.select_output_destination,
            state="disabled",  # Abilitato solo dopo la scelta dell'input
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="transparent",
            border_width=2,
            text_color=("black", "white")
        )
        self.select_output_btn.grid(row=3, column=2, padx=(0, 20), pady=(0, 20), sticky="ew")

        # ----------------------------------------------------
        # 3. CONSOLE & LOG AREA (EXPANDS TO FILL HEIGHT)
        # ----------------------------------------------------
        self.log_frame = ctk.CTkFrame(self)
        self.log_frame.grid(row=2, column=0, padx=25, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.log_title = ctk.CTkLabel(
            self.log_frame, 
            text="Console Log delle Operazioni:", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.log_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.log_textbox = ctk.CTkTextbox(
            self.log_frame, 
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled"
        )
        self.log_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # ----------------------------------------------------
        # 4. ACTION & PROGRESS AREA
        # ----------------------------------------------------
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, padx=25, pady=(10, 25), sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        # Barra di progresso
        self.progress_bar = ctk.CTkProgressBar(self.action_frame, height=8)
        self.progress_bar.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0.0)

        # Bottone di Conversione principale
        self.convert_button = ctk.CTkButton(
            self.action_frame, 
            text="Converti in Markdown", 
            height=48,
            command=self.start_conversion,
            state="disabled",  # Disabilitato fino a selezione file valido
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        self.convert_button.grid(row=1, column=0, sticky="ew")

    # ----------------------------------------------------
    # LOGICA DI INTERFACCIA ED EVENTI
    # ----------------------------------------------------
    def toggle_theme(self):
        """Alterna l'aspetto dell'applicazione tra modalità scura e chiara."""
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Modalità Scura")
            self.log_message("Passato alla modalità scura.", "info")
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Modalità Chiara")
            self.log_message("Passato alla modalità chiara.", "info")

    def select_input_file(self):
        """Apre un filedialog per selezionare il file da convertire."""
        file_types = [
            ("File supportati", "*.docx;*.pptx;*.xlsx;*.pdf;*.html;*.txt"),
            ("Documenti Word", "*.docx"),
            ("Presentazioni PowerPoint", "*.pptx"),
            ("Fogli Excel", "*.xlsx"),
            ("File PDF", "*.pdf"),
            ("File HTML", "*.html"),
            ("File di testo", "*.txt"),
            ("Tutti i file", "*.*")
        ]
        
        path = filedialog.askopenfilename(
            title="Seleziona il file da convertire",
            filetypes=file_types
        )
        
        if path:
            self.selected_input_path = os.path.abspath(path)
            
            # Mostra nel campo di testo
            self.input_entry.configure(state="normal")
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, self.selected_input_path)
            self.input_entry.configure(state="readonly")
            
            # Imposta la destinazione predefinita nello stesso folder con estensione .md
            dir_name, file_name = os.path.split(self.selected_input_path)
            base_name, _ = os.path.splitext(file_name)
            self.selected_output_path = os.path.join(dir_name, f"{base_name}.md")
            
            self.output_entry.configure(state="normal")
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, self.selected_output_path)
            self.output_entry.configure(state="readonly")

            # Abilita il bottone Sfoglia output e il pulsante Converti
            self.select_output_btn.configure(state="normal")
            if MARKITDOWN_AVAILABLE:
                self.convert_button.configure(state="normal")
                
            self.log_message(f"File caricato: {file_name} ({self.selected_input_path})", "info")
            self.log_message(f"Destinazione predefinita impostata: {self.selected_output_path}", "info")

    def select_output_destination(self):
        """Consente all'utente di selezionare manualmente una cartella e un nome file di output."""
        if not self.selected_input_path:
            return
            
        initial_dir = os.path.dirname(self.selected_output_path)
        initial_file = os.path.basename(self.selected_output_path)
        
        path = filedialog.asksaveasfilename(
            title="Seleziona la destinazione del file Markdown",
            defaultextension=".md",
            filetypes=[("File Markdown", "*.md"), ("Tutti i file", "*.*")],
            initialdir=initial_dir,
            initialfile=initial_file
        )
        
        if path:
            self.selected_output_path = os.path.abspath(path)
            self.output_entry.configure(state="normal")
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, self.selected_output_path)
            self.output_entry.configure(state="readonly")
            self.log_message(f"Destinazione output modificata in: {self.selected_output_path}", "info")

    def log_message(self, message, level="info"):
        """Scrive un log temporizzato all'interno della console grafica con codifica colore."""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        
        self.log_textbox.configure(state="normal")
        
        # Accesso robusto al widget tk.Text interno per la gestione dei tag
        text_widget = self.log_textbox._textbox if hasattr(self.log_textbox, "_textbox") else self.log_textbox
        
        # Configura i tag per supportare il dark/light mode correttamente
        is_dark = ctk.get_appearance_mode() == "Dark"
        default_color = "#E0E0E0" if is_dark else "#1A1A1A"
        
        text_widget.tag_config("info", foreground=default_color)
        text_widget.tag_config("error", foreground="#FF5252")    # Rosso acceso moderno
        text_widget.tag_config("success", foreground="#00E676")  # Verde brillante moderno
        
        self.log_textbox.insert("end", formatted_msg + "\n", level)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    # ----------------------------------------------------
    # LOGICA DI BACKEND & THREADING
    # ----------------------------------------------------
    def start_conversion(self):
        """Avvia il processo di conversione in un thread separato."""
        if not MARKITDOWN_AVAILABLE:
            self.log_message("Impossibile procedere: Microsoft MarkItDown non è installato.", "error")
            return
            
        if not self.selected_input_path or not self.selected_output_path:
            self.log_message("Impossibile procedere: Selezionare prima un file valido.", "error")
            return
            
        # Stato di conversione attivo
        self.is_converting = True
        
        # Modifiche interfaccia: disabilita bottoni di azione e attiva barra di progresso
        self.convert_button.configure(state="disabled", text="Conversione in corso...")
        self.select_file_btn.configure(state="disabled")
        self.select_output_btn.configure(state="disabled")
        
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        self.log_message(f"Avvio del thread di conversione per il file: {os.path.basename(self.selected_input_path)}", "info")
        
        # Avvio del thread di elaborazione background
        conversion_thread = threading.Thread(
            target=self.run_conversion_worker,
            args=(self.selected_input_path, self.selected_output_path),
            daemon=True
        )
        conversion_thread.start()

    def run_conversion_worker(self, input_path, output_path):
        """Funzione eseguita in background sul thread secondario."""
        try:
            # Inizializzazione della classe Microsoft MarkItDown
            md_engine = MarkItDown()
            
            # Esecuzione della conversione del documento
            result = md_engine.convert(input_path)
            
            # Scrittura del file Markdown di output in formato UTF-8
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result.text_content)
                
            # Ritorno al thread principale per aggiornare la GUI
            self.after(0, self.on_conversion_success, output_path)
            
        except Exception as e:
            # In caso di errore, inoltra la descrizione al thread principale
            self.after(0, self.on_conversion_failure, str(e))

    def on_conversion_success(self, output_path):
        """Callback del thread principale in caso di conversione riuscita."""
        self.log_message("Conversione completata con successo!", "success")
        self.log_message(f"File markdown generato correttamente: {output_path}", "success")
        self.reset_gui_state()

    def on_conversion_failure(self, error_message):
        """Callback del thread principale in caso di errore."""
        self.log_message("ERRORE DURANTE LA CONVERSIONE:", "error")
        self.log_message(error_message, "error")
        self.reset_gui_state()

    def reset_gui_state(self):
        """Ripristina i componenti della GUI allo stato originale."""
        self.is_converting = False
        
        # Ripristino bottoni
        self.select_file_btn.configure(state="normal")
        self.select_output_btn.configure(state="normal")
        self.convert_button.configure(state="normal", text="Converti in Markdown")
        
        # Spegnimento e reset barra progresso
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(0.0)

if __name__ == "__main__":
    app = MarkItDownStudio()
    app.mainloop()
