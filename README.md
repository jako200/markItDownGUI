# MarkItDown Studio

A modern and elegant Graphical User Interface (GUI) for the **Microsoft MarkItDown** tool, developed in Python using the **CustomTkinter** library. It allows users to easily convert various file formats into Markdown (`.md`) documents without having to use the command line.

---

## 🚀 Key Features

- **Premium Dark Interface**: Modern design inspired by the *Obsidian* dark palette, featuring support for micro-interactions and dynamically generated icons.
- **Multi-Format Support**: Seamless conversion of Word documents (`.docx`), PowerPoint presentations (`.pptx`), Excel spreadsheets (`.xlsx`), PDF files (`.pdf`), HTML pages (`.html`), and plain text files (`.txt`).
- **Asynchronous Conversion**: Conversion processes run on a separate background thread to prevent the GUI from freezing.
- **Progress Bar**: Real-time visual feedback during operations.
- **Dedicated Log Console**: Detailed history of operations with color-coded messaging based on severity (General Messages, Successes, and Errors).
- **Flexible Path Management**: Automatic output file name generation (saved in the same directory as the input file) with an option for manual destination customization.
- **Automated Compiler**: Built-in build script to easily generate a standalone `.exe` executable for Windows.

---

## 🛠️ Prerequisites and Installation

Ensure you have **Python 3.8** or higher installed on your system.

### 1. Clone the repository
```bash
git clone https://github.com/jako200/markItDownGUI
cd markItDownUI

```

### 2. Install dependencies

You can install the dependencies listed in the `requirements.txt` file by running the following command in your terminal:

```bash
pip install -r requirements.txt

```

*Note: If you are using PowerShell and encounter syntax issues with square brackets for `markitdown[all]`, install the dependencies manually by enclosing the package name in quotes:*

```powershell
pip install customtkinter Pillow "markitdown[all]"

```

---

## 💻 How to Run the Application

To launch the graphical interface in a development environment, execute the `main.py` file:

```bash
python main.py

```

---

## 📦 Compilation and Distribution (Creating the .exe)

The project includes an automated build script named `build.py` that utilizes **PyInstaller** to package the application into a single standalone executable file for Windows (`.exe`), which will not require a Python installation on the end-user's computer.

To compile the application:

1. Install PyInstaller (if not already installed):
```bash
pip install pyinstaller

```


2. Run the build script:
```bash
python build.py

```



The script will automatically perform the following operations:

* Verify the presence of all required dependencies.
* Launch PyInstaller, correctly importing the graphical assets and themes from `customtkinter` and `markitdown`.
* Create a standalone executable in the `dist/` directory, renaming it to `MarkItDown_Studio_Windows_x64.exe`.

---

## 🗂️ Supported File Formats by MarkItDown

The underlying conversion engine converts the following formats into Markdown:

* **Word** (`.docx`)
* **PowerPoint** (`.pptx`)
* **Excel** (`.xlsx`)
* **PDF** (`.pdf`)
* **HTML** (`.html`)
* **Plain text** (`.txt`, etc.)
