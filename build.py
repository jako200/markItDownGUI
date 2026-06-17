import os
import sys
import shutil
import subprocess

def check_dependencies():
    """
    Verify if the necessary libraries (customtkinter, markitdown, and pyinstaller)
    are installed in the current Python environment.
    """
    missing_packages = []

    # Check customtkinter
    try:
        import customtkinter
    except ImportError:
        missing_packages.append("customtkinter")

    # Check markitdown
    try:
        import markitdown
    except ImportError:
        missing_packages.append("markitdown")

    # Check PyInstaller (by importing PyInstaller or searching for the executable in PATH)
    try:
        import PyInstaller
    except ImportError:
        if not shutil.which("pyinstaller"):
            missing_packages.append("pyinstaller")

    return missing_packages

def run_build():
    """
    Manages the application compilation process using PyInstaller.
    """
    # Force the current working directory to the folder containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print("=== MarkItDown Studio - Starting Compilation Script ===")
    
    # 1. Dependency verification
    missing = check_dependencies()
    if missing:
        print("\n[ERROR] Missing required dependencies for compilation:")
        for pkg in missing:
            print(f" - {pkg}")
        print("\nTo install them all, run the command:")
        print("pip install customtkinter markitdown pyinstaller")
        sys.exit(1)
    
    print("\n[OK] All required dependencies are installed.")

    # 2. Configuration of PyInstaller parameters
    # We use sys.executable -m PyInstaller to ensure the current Python environment
    # is used, avoiding PATH misalignment.
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconsole",           # Hides the terminal window on app launch
        "--onefile",             # Bundles everything into a single executable file (.exe)
        "--clean",               # Cleans PyInstaller cache before compiling
        "--name=MarkItDown_Studio", # Initial name of the .exe file
        "--collect-all", "customtkinter", # Collects all customtkinter files (e.g. themes, fonts)
        "--collect-all", "markitdown",    # Collects all markitdown modules and resources
        "--collect-all", "magika",        # Collects all magika models and resources
        "main.py"                # Main script of the application
    ]

    print(f"\n[INFO] Executing compilation command:\n{' '.join(command)}\n")
    
    try:
        # Start compilation
        subprocess.run(command, check=True)
        print("\n[OK] PyInstaller compilation completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] PyInstaller encountered an error during compilation: {e}")
        sys.exit(1)

    # 3. Rename final executable
    dist_dir = os.path.join(os.getcwd(), "dist")
    original_exe = os.path.join(dist_dir, "MarkItDown_Studio.exe")
    target_exe = os.path.join(dist_dir, "MarkItDown_Studio_Windows_x64.exe")

    if os.path.exists(original_exe):
        try:
            # If a previous version of the renamed executable exists, delete it
            if os.path.exists(target_exe):
                print(f"[INFO] Removing old existing release file...")
                os.remove(target_exe)
            
            # Rename the new executable
            os.rename(original_exe, target_exe)
            print(f"\n[SUCCESS] Executable file renamed successfully!")
            print(f"Path: {target_exe}")
            print("The executable is ready for distribution on GitHub!")
        except Exception as e:
            print(f"\n[ERROR] Unable to rename the generated file: {e}")
            sys.exit(1)
    else:
        print(f"\n[ERROR] Unable to find the generated file in {original_exe}")
        sys.exit(1)

if __name__ == "__main__":
    run_build()
