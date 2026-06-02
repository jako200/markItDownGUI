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
import math
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageDraw

# Tentativo di importazione di MarkItDown per evitare crash all'avvio in caso di mancanza della libreria
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False

# Configurazione del tema e della modalità di visualizzazione predefinita
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def create_icon_image(icon_type, color="#FFFFFF"):
    """
    Genera un'immagine PNG 64x64 in memoria per fungere da icona, con sfondo trasparente.
    """
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    if icon_type == "document":
        # Disegna il foglio
        draw.polygon([(16, 8), (40, 8), (48, 16), (48, 56), (16, 56)], outline=color, width=4)
        # Disegna la piega dell'angolo
        draw.line([(40, 8), (40, 16), (48, 16)], fill=color, width=4)
        # Righe interne del documento
        draw.line([(24, 26), (40, 26)], fill=color, width=3)
        draw.line([(24, 36), (40, 36)], fill=color, width=3)
        draw.line([(24, 46), (34, 46)], fill=color, width=3)
        
    elif icon_type == "folder":
        # Disegna la cartella
        draw.polygon([(8, 14), (22, 14), (28, 22), (56, 22), (56, 52), (8, 52)], outline=color, width=4)
        draw.line([(8, 22), (28, 22)], fill=color, width=4)
        
    elif icon_type == "lightning":
        # Disegna il fulmine
        draw.polygon([(36, 4), (16, 32), (32, 32), (28, 60), (48, 32), (32, 32)], fill=color)
        
    elif icon_type == "gear":
        # Disegna l'ingranaggio
        center_x, center_y = 32, 32
        draw.ellipse([(16, 16), (48, 48)], outline=color, width=4)
        draw.ellipse([(26, 26), (38, 38)], outline=color, width=3)
        for i in range(8):
            angle = i * (2 * math.pi / 8)
            x1 = center_x + 16 * math.cos(angle)
            y1 = center_y + 16 * math.sin(angle)
            x2 = center_x + 24 * math.cos(angle)
            y2 = center_y + 24 * math.sin(angle)
            draw.line([(x1, y1), (x2, y2)], fill=color, width=5)
            
    elif icon_type == "checkmark":
        # Disegna la spunta
        draw.line([(16, 32), (28, 44)], fill=color, width=6)
        draw.line([(28, 44), (48, 18)], fill=color, width=6)
        
    return img

class MarkItDownStudio(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurazione Finestra Principale (Premium Obsidian Palette)
        self.title("MarkItDown Studio")
        self.geometry("800x700")
        self.minsize(720, 600)
        self.configure(fg_color="#0B0F19")

        # Stato interno
        self.selected_input_path = ""
        self.selected_output_path = ""
        self.is_converting = False

        # Griglia principale della finestra
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=1) # La console dei log si espande verticalmente
        self.grid_rowconfigure(4, weight=0)

        # Generazione e caricamento delle icone in memoria
        self.init_icons()

        # Creazione dei widget
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

    def init_icons(self):
        """Inizializza le icone in formato CTkImage partendo dai disegni in memoria."""
        # Icone bianche per i pulsanti e le card
        self.doc_icon = ctk.CTkImage(
            light_image=create_icon_image("document", "#FFFFFF"),
            dark_image=create_icon_image("document", "#FFFFFF"),
            size=(18, 18)
        )
        self.folder_icon = ctk.CTkImage(
            light_image=create_icon_image("folder", "#FFFFFF"),
            dark_image=create_icon_image("folder", "#FFFFFF"),
            size=(18, 18)
        )
        self.lightning_icon = ctk.CTkImage(
            light_image=create_icon_image("lightning", "#FFFFFF"),
            dark_image=create_icon_image("lightning", "#FFFFFF"),
            size=(18, 18)
        )
        
        # Icone grigie per lo stato disabilitato o secondario
        self.doc_icon_muted = ctk.CTkImage(
            light_image=create_icon_image("document", "#9CA3AF"),
            dark_image=create_icon_image("document", "#9CA3AF"),
            size=(18, 18)
        )
        self.folder_icon_muted = ctk.CTkImage(
            light_image=create_icon_image("folder", "#9CA3AF"),
            dark_image=create_icon_image("folder", "#9CA3AF"),
            size=(18, 18)
        )

        # Icona di spunta verde per il successo del caricamento
        self.checkmark_icon = ctk.CTkImage(
            light_image=create_icon_image("checkmark", "#10B981"),
            dark_image=create_icon_image("checkmark", "#10B981"),
            size=(16, 16)
        )

    def create_widgets(self):
        # ----------------------------------------------------
        # 1. HEADER FRAME
        # ----------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        # Titolo dell'applicazione
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="MarkItDown Studio", 
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        # Sottotitolo
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame, 
            text="Convertitore GUI elegante per Microsoft MarkItDown", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#9CA3AF"
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        # ----------------------------------------------------
        # 2. FILE MANAGEMENT - CARD 1 (INPUT)
        # ----------------------------------------------------
        self.input_card = ctk.CTkFrame(
            self, 
            fg_color="#151B26", 
            border_color="#2D3748", 
            border_width=1, 
            corner_radius=14
        )
        self.input_card.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        self.input_card.grid_columnconfigure(0, weight=1)

        # Titolo Card con Icona
        self.input_card_title = ctk.CTkLabel(
            self.input_card,
            text="  Seleziona File da Convertire",
            image=self.doc_icon_muted,
            compound="left",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#FFFFFF"
        )
        self.input_card_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")

        # Feedback Area per File Selezionato (micro-interazione)
        self.status_frame = ctk.CTkFrame(self.input_card, fg_color="transparent")
        self.status_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(2, 8), sticky="w")
        
        self.status_icon_label = ctk.CTkLabel(self.status_frame, text="")
        self.status_icon_label.pack(side="left", padx=(0, 5))
        
        self.status_text_label = ctk.CTkLabel(
            self.status_frame, 
            text="Nessun file selezionato per la conversione", 
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color="#9CA3AF"
        )
        self.status_text_label.pack(side="left")

        # Casella di inserimento e Pulsante
        self.input_entry = ctk.CTkEntry(
            self.input_card, 
            placeholder_text="Fai clic su 'Sfoglia' per caricare un file...", 
            state="readonly",
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#0B0F19",
            border_color="#2D3748",
            text_color="#FFFFFF",
            corner_radius=8
        )
        self.input_entry.grid(row=2, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")

        self.select_file_btn = ctk.CTkButton(
            self.input_card, 
            text="Sfoglia...", 
            image=self.doc_icon,
            compound="left",
            width=130,
            height=38,
            command=self.select_input_file,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            corner_radius=10
        )
        self.select_file_btn.grid(row=2, column=1, padx=(0, 20), pady=(0, 20), sticky="e")

        # ----------------------------------------------------
        # 3. FILE MANAGEMENT - CARD 2 (OUTPUT)
        # ----------------------------------------------------
        self.output_card = ctk.CTkFrame(
            self, 
            fg_color="#151B26", 
            border_color="#2D3748", 
            border_width=1, 
            corner_radius=14
        )
        self.output_card.grid(row=2, column=0, padx=30, pady=10, sticky="ew")
        self.output_card.grid_columnconfigure(0, weight=1)

        # Titolo Card con Icona
        self.output_card_title = ctk.CTkLabel(
            self.output_card,
            text="  Configurazione Destinazione Output",
            image=self.folder_icon_muted,
            compound="left",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#FFFFFF"
        )
        self.output_card_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 8), sticky="w")

        # Casella di inserimento e Pulsante
        self.output_entry = ctk.CTkEntry(
            self.output_card, 
            placeholder_text="Verrà generato un file .md nello stesso percorso di origine...", 
            state="readonly",
            height=38,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color="#0B0F19",
            border_color="#2D3748",
            text_color="#FFFFFF",
            corner_radius=8
        )
        self.output_entry.grid(row=1, column=0, padx=(20, 10), pady=(0, 20), sticky="ew")

        self.select_output_btn = ctk.CTkButton(
            self.output_card, 
            text="Modifica...", 
            image=self.folder_icon_muted,
            compound="left",
            width=130,
            height=38,
            command=self.select_output_destination,
            state="disabled",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="transparent",
            border_width=1,
            border_color="#2D3748",
            text_color="#9CA3AF",
            hover_color="#1F2937",
            corner_radius=10
        )
        self.select_output_btn.grid(row=1, column=1, padx=(0, 20), pady=(0, 20), sticky="e")

        # ----------------------------------------------------
        # 4. CONSOLE & LOG AREA (EXPANDS TO FILL HEIGHT)
        # ----------------------------------------------------
        self.log_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.log_frame.grid(row=3, column=0, padx=30, pady=10, sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.log_title = ctk.CTkLabel(
            self.log_frame, 
            text="Console Log delle Operazioni:", 
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#9CA3AF"
        )
        self.log_title.grid(row=0, column=0, padx=5, pady=(5, 5), sticky="w")

        self.log_textbox = ctk.CTkTextbox(
            self.log_frame, 
            font=ctk.CTkFont(family="Consolas", size=11),
            state="disabled",
            fg_color="#0D111A",
            text_color="#9CA3AF",
            border_width=1,
            border_color="#1E293B",
            corner_radius=10
        )
        self.log_textbox.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        # ----------------------------------------------------
        # 5. ACTION & PROGRESS AREA
        # ----------------------------------------------------
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=4, column=0, padx=30, pady=(10, 25), sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        # Barra di progresso
        self.progress_bar = ctk.CTkProgressBar(
            self.action_frame, 
            height=6,
            fg_color="#1E293B",
            progress_color="#2563EB",
            corner_radius=3
        )
        self.progress_bar.grid(row=0, column=0, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0.0)

        # Bottone di Conversione principale
        self.convert_button = ctk.CTkButton(
            self.action_frame, 
            text="Converti in Markdown", 
            image=self.lightning_icon,
            compound="left",
            height=48,
            command=self.start_conversion,
            state="disabled",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            corner_radius=12
        )
        self.convert_button.grid(row=1, column=0, sticky="ew")

    # ----------------------------------------------------
    # LOGICA DI INTERFACCIA ED EVENTI
    # ----------------------------------------------------
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

            # Micro-interazione: aggiorna lo stato visivo della Card 1
            self.input_card.configure(border_color="#10B981")
            self.status_icon_label.configure(image=self.checkmark_icon)
            self.status_text_label.configure(
                text=f"File pronto: {file_name}",
                text_color="#10B981",
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
            )

            # Abilita il bottone Sfoglia output e il pulsante Converti
            self.select_output_btn.configure(
                state="normal",
                fg_color="transparent",
                border_color="#374151",
                text_color="#FFFFFF",
                image=self.folder_icon
            )
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
        
        # Configura i tag per il tema scuro personalizzato
        text_widget.tag_config("info", foreground="#9CA3AF")
        text_widget.tag_config("error", foreground="#EF4444")    # Rosso moderno
        text_widget.tag_config("success", foreground="#10B981")  # Verde moderno
        
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
