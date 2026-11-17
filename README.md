# MarkItDown GUI

A modern, elegant **graphical desktop application** for [Microsoft MarkItDown](https://github.com/microsoft/markitdown), built in Python with [CustomTkinter](https://customtkinter.tomschimansky.com/).  
Convert Word, PowerPoint, Excel, PDF, HTML and more to Markdown in a few clicks — no command line required.

> **Two flavours available — pick yours:**
>
> | | Repo | Best for |
> |---|---|---|
> | 🖥️ **MarkItDown Studio** (this one) | [github.com/jako200/markItDownGUI](https://github.com/jako200/markItDownGUI) | Desktop users, Windows / macOS / Linux with GUI |
> | 🖮 **MarkItDown TUI** | [github.com/jako200/markItDownTUI](https://github.com/jako200/markItDownTUI) | Terminal users, headless servers, SSH sessions |
>
> Both share the same conversion engine and support the same file formats.

---

## 🚀 Key Features

- **Premium Dark Theme** — Obsidian-inspired palette with smooth micro-interactions and dynamically generated SVG icons.
- **Single File Conversion** — browse, preview file info, choose a custom output destination and convert in one click.
- **Batch Conversion** — queue multiple files or entire folders, monitor per-file status, cancel at any time.
- **Asynchronous Engine** — conversion runs on a background thread; the UI never freezes.
- **Progress Bar & Log Console** — real-time progress and colour-coded log (Info / Success / Warning / Error).
- **Windows Executable** — built-in `build.py` script produces a standalone `.exe` via PyInstaller (no Python required on the target machine).

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

### 2. Install dependencies
```bash
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
