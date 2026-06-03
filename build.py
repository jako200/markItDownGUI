import os
import sys
import shutil
import subprocess

def check_dependencies():
    """
    Verifica se le librerie necessarie (customtkinter, markitdown e pyinstaller)
    sono installate nell'ambiente Python corrente.
    """
    missing_packages = []

    # Verifica customtkinter
    try:
        import customtkinter
    except ImportError:
        missing_packages.append("customtkinter")

    # Verifica markitdown
    try:
        import markitdown
    except ImportError:
        missing_packages.append("markitdown")

    # Verifica PyInstaller (importando PyInstaller o cercando l'eseguibile nel PATH)
    try:
        import PyInstaller
    except ImportError:
        if not shutil.which("pyinstaller"):
            missing_packages.append("pyinstaller")

    return missing_packages

def run_build():
    """
    Gestisce il processo di compilazione dell'applicazione usando PyInstaller.
    """
    # Forza la directory di lavoro corrente sulla cartella in cui si trova questo script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print("=== MarkItDown Studio - Avvio Script di Compilazione ===")
    
    # 1. Verifica delle dipendenze
    missing = check_dependencies()
    if missing:
        print("\n[ERRORE] Mancano alcune dipendenze necessarie per la compilazione:")
        for pkg in missing:
            print(f" - {pkg}")
        print("\nPer installarle tutte, esegui il comando:")
        print("pip install customtkinter markitdown pyinstaller")
        sys.exit(1)
    
    print("\n[OK] Tutte le dipendenze richieste sono installate.")

    # 2. Configurazione dei parametri di PyInstaller
    # Usiamo sys.executable -m PyInstaller per garantire che venga utilizzato 
    # l'ambiente Python corrente ed evitare disallineamenti di PATH.
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",           # Nasconde la finestra del terminale all'avvio dell'app
        "--onefile",             # Impacchetta tutto in un singolo file eseguibile (.exe)
        "--clean",               # Pulisce la cache di PyInstaller prima della compilazione
        "--name=MarkItDown_Studio", # Nome iniziale del file .exe
        "--collect-all", "customtkinter", # Raccoglie tutti i file di customtkinter (es. temi, font)
        "--collect-all", "markitdown",    # Raccoglie tutti i moduli e risorse di markitdown
        "main.py"                # Script principale dell'applicazione
    ]

    print(f"\n[INFO] Esecuzione del comando di compilazione:\n{' '.join(command)}\n")
    
    try:
        # Avvia la compilazione
        subprocess.run(command, check=True)
        print("\n[OK] Compilazione con PyInstaller completata con successo!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERRORE] PyInstaller ha riscontrato un errore durante la compilazione: {e}")
        sys.exit(1)

    # 3. Ridenominazione dell'eseguibile finale
    dist_dir = os.path.join(os.getcwd(), "dist")
    original_exe = os.path.join(dist_dir, "MarkItDown_Studio.exe")
    target_exe = os.path.join(dist_dir, "MarkItDown_Studio_Windows_x64.exe")

    if os.path.exists(original_exe):
        try:
            # Se esiste già una versione precedente dell'eseguibile rinominato, la eliminiamo
            if os.path.exists(target_exe):
                print(f"[INFO] Rimozione del vecchio file di release esistente...")
                os.remove(target_exe)
            
            # Rinominiamo il nuovo eseguibile
            os.rename(original_exe, target_exe)
            print(f"\n[SUCCESSO] File eseguibile rinominato con successo!")
            print(f"Percorso: {target_exe}")
            print("L'eseguibile è pronto per la distribuzione su GitHub!")
        except Exception as e:
            print(f"\n[ERRORE] Impossibile rinominare il file generato: {e}")
            sys.exit(1)
    else:
        print(f"\n[ERRORE] Impossibile trovare il file generato in {original_exe}")
        sys.exit(1)

if __name__ == "__main__":
    run_build()
