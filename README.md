<<<<<<< HEAD
# MarkItDown GUI — Graphical Desktop App
=======
# MarkItDown GUI
>>>>>>> eb35b1c2c2078378d0a5087ddadb2fb8cf08dd03

A modern **graphical desktop application** for [Microsoft MarkItDown](https://github.com/microsoft/markitdown), built in Python with [CustomTkinter](https://customtkinter.tomschimansky.com/).  
Convert Word, PowerPoint, Excel, PDF, HTML and more to Markdown in a few clicks — no command line required.

> **Two flavours available — pick yours:**
>
> | | Repo | Best for |
> |---|---|---|
> | 🖥️ **MarkItDown GUI** (this one) | [github.com/jako200/markItDownGUI](https://github.com/jako200/markItDownGUI) | Desktop users, Windows / macOS / Linux with GUI |
> | 🖮 **MarkItDown TUI** | [github.com/jako200/markItDownTUI](https://github.com/jako200/markItDownTUI) | Terminal users, headless servers, SSH sessions |
>
> Both share the same conversion engine and support the same file formats.

---

## 🚀 Features

### Single File Conversion
- Browse for a file with a native file-picker dialog
- Preview file info (format, size) before converting
- Optional custom output destination (defaults to same folder as input)
- Asynchronous conversion — the UI stays fully responsive

### Batch Conversion
- Queue multiple files or entire folders via drag-and-drop or file dialogs
- Automatic format validation and duplicate prevention
- Optional custom output directory (or save alongside each source file)
- Scrollable file list with per-file live status badges: `queued` → `converting` → `OK` / `error`
- Progress bar with file count
- **Cancel** button to cooperatively interrupt a running batch at any time

### Built-in Log Console
- Timestamped, colour-coded log (Info / Success / Warning / Error)
- One-click clear button

### Design & Usability
- Premium dark theme — Obsidian-inspired palette with dynamically generated SVG icons
- Tab-based layout (Single / Batch)
- Native file dialogs for a familiar desktop experience
- Cross-platform: Windows, macOS, Linux

### Standalone Executable (Windows)
- Built-in `build.py` script produces a self-contained `.exe` via PyInstaller — no Python required on the target machine

---

## 🗂️ Supported Formats

| Format | Extension(s) |
|---|---|
| Word Document | `.docx` |
| PowerPoint Presentation | `.pptx` |
| Excel Spreadsheet | `.xlsx` |
| PDF | `.pdf` |
| HTML / Web page | `.html`, `.htm` |
| Plain text / Code | `.txt`, `.csv`, `.xml`, `.json` |

---

## 🛠️ Requirements & Installation

Requires **Python 3.8+**.

### 1. Clone the repository
```bash
git clone https://github.com/jako200/markItDownGUI.git
cd markItDownGUI
```

### 2. Create a virtual environment (recommended)

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> **PowerShell note:** if you get a syntax error with square brackets, quote the package name:
> ```powershell
> pip install customtkinter Pillow "markitdown[all]"
> ```

---

## 💻 Run the Application

```bash
python main.py
```

---

## 📦 Build a Standalone Executable (Windows)

```bash
pip install pyinstaller
python build.py
```

The script will verify dependencies, run PyInstaller and place `MarkItDown_Studio_Windows_x64.exe` in the `dist/` folder.

---

## 🏗️ Project Structure

```
markItDownGUI/
├── main.py               # Entry point
├── requirements.txt      # Dependencies (customtkinter, Pillow, markitdown[all])
├── build.py              # PyInstaller automation script
├── src/
│   ├── core/
│   │   └── converter.py  # MarkItDown wrapper + BatchConversionWorker
│   ├── gui/
│   │   ├── app.py        # Main window, tabs, event handling
│   │   ├── widgets.py    # LogConsole, FileListScrollFrame
│   │   └── theme.py      # Obsidian colour palette & fonts
│   └── utils/
│       ├── helpers.py    # Format detection & size formatting
│       └── icons.py      # SVG icon generator
└── dist/                 # Output folder for the compiled .exe
```

---

## 🔗 Related Project

Looking for a **terminal version** that runs anywhere without a desktop environment?  
➡️ Check out [**MarkItDown TUI**](https://github.com/jako200/markItDownTUI) — same features, same engine, pure terminal UI powered by [Textual](https://textual.textualize.io/).
