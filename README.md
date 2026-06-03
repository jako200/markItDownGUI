# MarkItDown Studio

Una moderna ed elegante interfaccia grafica (GUI) per il tool **Microsoft MarkItDown**, sviluppata in Python utilizzando la libreria **CustomTkinter**. Consente di convertire facilmente vari formati di file in documenti Markdown (`.md`) senza dover utilizzare la riga di comando.

---

## 🚀 Caratteristiche principali

- **Interfaccia Premium Dark**: Design moderno ispirato alla palette scura *Obsidian* con supporto per micro-interazioni ed icone generate dinamicamente.
- **Supporto Multi-Formato**: Conversione semplice di documenti Word (`.docx`), presentazioni PowerPoint (`.pptx`), fogli Excel (`.xlsx`), file PDF (`.pdf`), pagine HTML (`.html`) e file di testo (`.txt`).
- **Conversione Asincrona**: I processi di conversione vengono eseguiti su un thread in background separato per evitare il congelamento dell'interfaccia grafica.
- **Barra di Progresso**: Feedback visivo in tempo reale durante le operazioni.
- **Console Log Dedicata**: Storico dettagliato delle operazioni con colorazione differenziata in base alla gravità (Messaggi Generali, Successi ed Errori).
- **Gestione Flessibile dei Percorsi**: Generazione automatica del nome del file di output (nella stessa cartella del file di input) con opzione di personalizzazione manuale della destinazione.
- **Compilatore Automatico**: Script di build integrato per generare facilmente un file eseguibile `.exe` standalone per Windows.

---

## 🛠️ Prerequisiti e Installazione

Assicurati di avere installato **Python 3.8** o superiore sul tuo sistema.

### 1. Clona il repository
```bash
git clone https://github.com/tuo-username/markItDownUI.git
cd markItDownUI
```

### 2. Installa le dipendenze
Puoi installare le dipendenze elencate nel file `requirements.txt` digitando nel terminale:

```bash
pip install -r requirements.txt
```

*Nota: Se utilizzi PowerShell e riscontri problemi con la sintassi delle parentesi quadre per `markitdown[all]`, installa le dipendenze manualmente racchiudendo il pacchetto tra virgolette:*
```powershell
pip install customtkinter Pillow "markitdown[all]"
```

---

## 💻 Come avviare l'applicazione

Per avviare l'interfaccia grafica in ambiente di sviluppo, esegui il file `main.py`:

```bash
python main.py
```

---

## 📦 Compilazione e Distribuzione (Creazione del .exe)

Il progetto include uno script di compilazione automatica chiamato `build.py` che sfrutta **PyInstaller** per impacchettare l'applicazione in un unico file eseguibile per Windows (`.exe`), che non richiederà l'installazione di Python sul computer dell'utente finale.

Per compilare l'applicazione:

1. Installa PyInstaller (se non lo hai già installato):
   ```bash
   pip install pyinstaller
   ```
2. Esegui lo script di build:
   ```bash
   python build.py
   ```

Lo script eseguirà automaticamente le seguenti operazioni:
- Verificherà la presenza di tutte le dipendenze necessarie.
- Avvierà PyInstaller importando correttamente le risorse grafiche e i temi di `customtkinter` e `markitdown`.
- Creerà un eseguibile standalone nella cartella `dist/` rinominandolo in `MarkItDown_Studio_Windows_x64.exe`.

---

## 🗂️ Formati di File Supportati da MarkItDown
Il motore di conversione sottostante converte in Markdown i seguenti formati:
* **Word** (`.docx`)
* **PowerPoint** (`.pptx`)
* **Excel** (`.xlsx`)
* **PDF** (`.pdf`)
* **HTML** (`.html`)
* **Testo semplice** (`.txt`, ecc.)
