# utils/bootstrapper.py
import sys
import subprocess
import importlib
import os
import tkinter as tk
from tkinter import messagebox

# Map: {ImportName: PackageName}
REQUIRED_LIBS = {
    "flask": "flask",
    "requests": "requests",
    "customtkinter": "customtkinter",
    "PIL": "pillow",
    "win32api": "pywin32"
}

def check_and_install():
    missing_packages = []
    
    # 1. Check what is missing
    for import_name, package_name in REQUIRED_LIBS.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing_packages.append(package_name)

    # 2. Install if needed
    if missing_packages:
        # Show a quick popup so you know it's not frozen
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("h4 Omni-Tool (v1.0b)", f"Installing system updates:\n{', '.join(missing_packages)}\n\nThis will take a moment.")
        root.destroy()

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("[SYSTEM] Dependencies installed. Restarting...")
            
            # 3. RESTART THE SCRIPT AUTOMATICALLY
            # We re-execute the current script to load the new modules fresh
            os.execv(sys.executable, ['python'] + sys.argv)
            
        except Exception as e:
            messagebox.showerror("Critical Failure", f"Could not install dependencies:\n{e}")
            sys.exit(1)

if __name__ == "__main__":
    check_and_install()