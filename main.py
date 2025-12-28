import customtkinter as ctk
import os
import sys
import multiprocessing
import threading
import queue
import time
import logging
import argparse
import signal
import tkinter as tk
import ctypes
from ctypes import wintypes

# --- FIX: Frozen "NoneType object has no attribute flush" ---
# When running with console=False, sys.stdout is None. 
# We need a dummy object that accepts .write() and .flush() calls to prevent crashes.
class NullWriter:
    def write(self, data): pass
    def flush(self): pass

if sys.stdout is None: sys.stdout = NullWriter()
if sys.stderr is None: sys.stderr = NullWriter()


# Set App User Model ID for Taskbar Icons
try:
    myappid = 'h4.mantella.omnitool.v6' # Arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except: pass

from ui.splash import SplashController
from ui.app_window import h4App
from wizard_ui import WizardWindow
from h4_managers import SettingsManager
from utils.logger import setup_logger
from core.scanner import DependencyScanner
from utils.ini_surgeon import INISurgeon
from core.mantella_patcher import MantellaPatcher



# ==========================================
# UTILITIES (Restored)
# ==========================================

def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def parse_arguments():
    """
    Handle command line arguments for Debug/Safe modes.
    """
    parser = argparse.ArgumentParser(description="Mantella Omni-Tool v6")
    parser.add_argument("--debug", action="store_true", help="Enable Debug Logging & Console")
    parser.add_argument("--safe", action="store_true", help="Disable heavy scanning")
    return parser.parse_args()

def hide_console():
    """
    Hides the console window if not in Debug mode.
    """
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')

    hWnd = kernel32.GetConsoleWindow()
    if hWnd:
        user32.ShowWindow(hWnd, 0) # 0 = SW_HIDE

# ==========================================
# BOOTSTRAPPER CLASS
# ==========================================

class SystemBootstrapper:
    def __init__(self, root, debug_mode=False):
        self.root = root
        self.debug_mode = debug_mode
        self.root.withdraw() # Keep the main root hidden (it's just an anchor)
        
        # Initialize Settings Manager
        self.settings_mgr = SettingsManager()
        
        # Sync Debug Mode with CLI Argument (Strict Enforcement)
        self.settings_mgr.update_setting("debug_mode", self.debug_mode)
        if self.debug_mode:
            logger.info("Debug Mode Forced via Argument")

        # Setup Threading Queue
        self.queue = queue.Queue()
        
        # Initialize Splash Screen
        self.splash = SplashController(self.root)
        self.splash.update_status("Initializing System...")

        # Start the Loading Thread
        threading.Thread(target=self.system_load, daemon=True).start()
        
        # Start the UI Loop Monitor
        self._check_job = self.root.after(100, self.process_queue)

    def system_load(self):
        """
        The heavy lifting: Scanning, Patching, and Decision Making.
        """
        try:
            # 1. Dependency Scan & Auto-Heal (OMNI-TOOL v7.6)
            self.queue.put(("status", "Verifying Neural Pathways (Dependencies)..."))
            self.check_and_install_requirements()

            self.queue.put(("status", "Verifying Documentation (README)..."))
            self.restore_readme()

            self.queue.put(("status", "Scanning File System..."))
            scanner = DependencyScanner(logger)
            scanner.scan_system()

            # 2. INI Surgeon (Game Aware)
            self.queue.put(("status", "Checking Game Configuration..."))
            current_game = self.settings_mgr.get_setting("game_mode") or "SkyrimSE"
            logger.info(f"Bootstrapper identified game mode: {current_game}")
            
            # The Fix: Pass the game mode to the Surgeon
            surgeon = INISurgeon(logger, target_game=current_game)
            surgeon.patch_files()

            # 3. Mantella Auto-Patcher (New)
            self.queue.put(("status", "Verifying Mantella Integrity..."))
            scan_cache = self.settings_mgr.get_setting("_scan_cache")
            if scan_cache and "Mantella" in scan_cache:
                MantellaPatcher.execute_patches(scan_cache["Mantella"])
            else:
                logger.info("Mantella path not cached. Skipping auto-patch. Run 'Scan System' to enable.")

            # 3. First Run Decision Logic
            first_run = self.settings_mgr.get_setting("first_run")
            
            # SPLASH DELAY: Ensure logo is seen
            time.sleep(2.0)

            if first_run:
                self.queue.put(("wizard", None))
            else:
                self.queue.put(("launch", None))

        except Exception as e:
            logger.critical(f"Bootstrapper Failure: {e}")
            self.queue.put(("error", str(e)))

    def restore_readme(self):
        """
        Extracts README.txt from the bundle to the user's directory.
        Ensures the documentation is physically present.
        """
        readme_target = "README.txt"
        
        # Don't overwrite if it exists and is > 0 bytes (user might have their own or we extracted it already)
        if os.path.exists(readme_target) and os.path.getsize(readme_target) > 0:
            return

        readme_source = resource_path("README.txt")
        if os.path.exists(readme_source):
            try:
                import shutil
                shutil.copy2(readme_source, readme_target)
                logger.info("[BOOTSTRAP] Extracted README.txt to root.")
            except Exception as e:
                logger.warning(f"[BOOTSTRAP] Could not extract README: {e}")

    def check_and_install_requirements(self):
        """
        Nuclear Dependency Manager.
        Reads requirements.txt and ensures parity.
        """
        import subprocess
        import pkg_resources
        
        req_file = resource_path("requirements.txt")
        if not os.path.exists(req_file): return

        with open(req_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing = []
        installed = {pkg.key for pkg in pkg_resources.working_set}
        
        # Mappings for packages where pypi name != import name
        # e.g. "Pillow" is installed, but req might say "pillow"
        
        for req in requirements:
            # Handle equality like "flask==2.0"
            pkg_name = req.split('==')[0].split('>=')[0].strip().lower()
            
            # Special Handling
            if pkg_name == "pillow": pkg_name = "pillow" # usually safe, but installed as 'Pillow'
            
            if pkg_name not in installed:
                missing.append(req)
        
        if missing:
            logger.info(f"Missing Dependencies Detected: {missing}")
            self.queue.put(("status", f"Installing {len(missing)} missing modules..."))
            
            try:
                # --user flag is safer for permissions
                subprocess.check_call([sys.executable, "-m", "pip", "install", *missing, "--user"])
                logger.info("Dependencies auto-installed successfully.")
                self.queue.put(("status", "Modules Installed. Resuming..."))
            except Exception as e:
                logger.error(f"Failed to auto-install dependencies: {e}")
                self.queue.put(("error", f"Dependency Error: {e}"))

    def process_queue(self):
        """
        Polls the queue for messages from the loading thread.
        """
        try:
            while True: # Process all pending messages
                msg = self.queue.get_nowait()
                signal, data = msg
                
                if signal == "status":
                    self.splash.update_status(data)
                
                elif signal == "wizard":
                    self.cleanup_and_launch(self.launch_wizard)
                    return 
                    
                elif signal == "launch":
                    self.cleanup_and_launch(self.launch_app)
                    return 
                    
                elif signal == "error":
                    self.splash.update_status(f"Error: {data}")
                    
        except queue.Empty:
            pass
        
        # Keep looping every 100ms
        self._check_job = self.root.after(100, self.process_queue)

    def cleanup_and_launch(self, launch_func):
        if self._check_job:
            self.root.after_cancel(self._check_job)
            self._check_job = None
        
        self.splash.close()
        launch_func()

    def launch_wizard(self):
        """
        Launches the First Run Wizard.
        """
        logger.info("Launching Wizard...")
        
        # WizardWindow is a ctk.CTkToplevel
        wizard = WizardWindow(self.root)
        
        # Blocking wait
        self.root.wait_window(wizard)
        
        # NUCLEAR CHECK: Verification after Wizard closes
        self.settings_mgr.load_settings() 
        if not self.settings_mgr.get_setting("first_run"):
            logger.info("Wizard Success. Transitioning to App.")
            self.launch_app()
        else:
            logger.warning("Wizard cancelled or failed. Exiting.")
            sys.exit()

    def launch_app(self):
        """
        Launches the Main UI.
        """
        logger.info("Launching Main App...")
        
        # Destroy the temporary root and splash
        # FIX: processing pending events and quitting loop prevents "application has been destroyed" errors
        self.root.withdraw()
        self.root.quit() 
        # self.root.destroy() # quit() exits the bootstrap mainloop, allowing us to proceed below
                              # note: h4App will create a NEW root. We shouldn't leave the old one hanging though.
                              # But destroying it while CTk internal 'after' tasks are pending causes the error.
                              # Using quit() stops the loop processing them.
        self.root.destroy()
        
        # Create the real app
        app = h4App(self.settings_mgr, logger)
        app.mainloop()

# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # 1. Parse Args
    args = parse_arguments()
    
    # 2. Setup Logging
    # STRICT MODE: Only enable file logging if the FLAG is present.
    # We do NOT read settings here. We enforce the flag.
    logger = setup_logger(debug_mode=args.debug) 
    if args.debug:
        logger.info("System Start. Debug Mode ACTIVE (CLI Flag).")

    # 3. Console Management
    if not args.debug:
        hide_console()

    # 4. Root Setup
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.overrideredirect(True) # Frameless for splash
    root.withdraw() # Start hidden
    
    # 6. Icon Setup
    icon_path = resource_path("assets/icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception as e:
            logger.warning(f"Could not load icon: {e}")
            
    # 6. Run System
    try:
        # Pass args.debug directly. 
        # The Bootstrapper will UPDATE the settings file to match this state.
        # This determines the "Reset on Restart" behavior.
        bootstrap = SystemBootstrapper(root, debug_mode=args.debug)
        root.mainloop()
    except Exception as e:
        logger.critical(f"Catastrophic Main Loop Failure: {e}")
        sys.exit(1)