# ui/frames.py
import tkinter as tk
from tkinter import messagebox, filedialog as fd
import customtkinter as ctk
from PIL import Image
import threading
import os
import shutil
import time
import subprocess
import configparser
import ctypes
import queue
import tkinter.filedialog as fd
from tkinter import messagebox
from pathlib import Path
from PIL import Image

# UI Imports
import ui.theme as theme
from ui.components import CTkTooltip, GlowingButton, SelectionDialog, ComponentManagerDialog, MissingModsDialog
from ui.tooltips import HoverTooltip # TOOLTIP SYSTEM
from ui.codex_window import SystemCodex # CODEX GIGA
from ui.help_window import HelpWindow # RESTORED: LEGACY COMPENDIUM

# Core Logic Imports
from core import scanner, ollama_mgr, bridge_server, TARGETS, PROXY_PORT, audit_log
from core.log_watcher import LogWatcher
import utils.safe_injector as safe_injector
from h4_managers import SettingsManager
from utils.logger import get_logger 

# PRIVACY IMPORT
from utils.privacy import sanitize

sys_log = get_logger()

# --- HELPER: ICON INJECTOR (LOCAL) ---
def apply_icon(window):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        icon_path = os.path.join(root_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            window.after(200, lambda: window.iconbitmap(icon_path))
    except: pass

# --- HEADER FRAME ---
class HeaderFrame(ctk.CTkFrame):
    def __init__(self, master, title="Title", close_cmd=None, min_cmd=None):
        super().__init__(master, height=40, fg_color=theme.COL_PANEL) # Integrated Header
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        # Title
        self.lbl_title = ctk.CTkLabel(self, text=title, font=theme.FONT_TITLE, text_color=theme.COL_ACCENT)
        self.lbl_title.pack(side="left", padx=20)
        
        # [ DEBUG MODE ] INDICATOR
        if hasattr(master, 'debug_mode') and master.debug_mode:
            self.lbl_debug = ctk.CTkLabel(self, text="[ DEBUG MODE ]", font=("Consolas", 10, "bold"), text_color="#ff00ff")
            self.lbl_debug.pack(side="left", padx=5)
        
        # Buttons Container
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(side="right", padx=5)

        # Help (?)
        self.btn_help = ctk.CTkButton(self.btn_frame, text="?", width=40, height=30, 
                                   fg_color="transparent", hover_color=theme.COL_ACCENT, 
                                   command=lambda: self.launch_help_selector())
        self.btn_help.pack(side="left", padx=2)
        
        # Minimize
        self.btn_min = ctk.CTkButton(self.btn_frame, text="_", width=40, height=30, 
                                   fg_color="transparent", hover_color="#222222", 
                                   command=min_cmd)
        self.btn_min.pack(side="left", padx=2)
        
        # Close
        self.btn_close = ctk.CTkButton(self.btn_frame, text="X", width=40, height=30, 
                                     fg_color="transparent", hover_color="#cc0000", 
                                     command=close_cmd)
        self.btn_close.pack(side="left", padx=2)

        # Drag Bindings
        self.lbl_title.bind("<Button-1>", master.start_move)
        self.lbl_title.bind("<B1-Motion>", master.do_move)
        self.bind("<Button-1>", master.start_move)
        self.bind("<B1-Motion>", master.do_move)

    def launch_help_selector(self):
        """
        Directly launch the Codex Gigas.
        Legacy Readme option removed per v1.0b cleanup.
        """
        SystemCodex.open_codex()

# --- GAME SELECTOR POPUP ---
class GameSelectorDialog(ctk.CTkToplevel):
    def __init__(self, parent, available_games, callback):
        super().__init__(parent)
        apply_icon(self)
        self.callback = callback
        self.title("TARGET CONFLICT")
        self.geometry("400x350")
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        
        try:
            x = parent.winfo_x() + (parent.winfo_width()//2) - 200
            y = parent.winfo_y() + (parent.winfo_height()//2) - 175
            self.geometry(f"+{x}+{y}")
        except: pass

        ctk.CTkLabel(self, text="⚠️ MULTIPLE TARGETS", font=theme.FONT_HEADER, text_color=theme.COL_WARN).pack(pady=20)
        ctk.CTkLabel(self, text="Select the injection target:", font=theme.FONT_TEXT).pack(pady=10)
        
        for game in available_games:
            GlowingButton(self, text=game, width=200, height=40, command=lambda g=game: self.select(g)).pack(pady=5)
            
    def select(self, game):
        self.callback(game)
        self.destroy()

# --- DEBUG POPUP CLASS ---
class DebugIntroDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_close_callback):
        super().__init__(parent)
        apply_icon(self)
        self.on_close_callback = on_close_callback
        self.title("DEBUG PROTOCOL ACTIVE")
        self.geometry("600x450")
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        
        try:
            x = parent.winfo_x() + (parent.winfo_width()//2) - 300
            y = parent.winfo_y() + (parent.winfo_height()//2) - 225
            self.geometry(f"+{x}+{y}")
        except: pass

        ctk.CTkLabel(self, text="⚠️ DEBUG MODE ACTIVE", font=theme.FONT_HEADER, text_color=theme.COL_WARN).pack(pady=20)
        
        msg = (
            "While in debug mode - you will get crazy levels of verbosity for debugging.\n"
            "This will also create a new file located at the root of wherever the exe is.\n"
            "It's called h4_Omni_debug.log.\n\n"
            "This will show EVERY - SINGLE - INTERACTION that my app, the papyrus,\n"
            "and game it self have with each other.\n"
            "This is for troubleshooting as AI can be a bitch to setup.\n\n"
            "Your next step?\n"
            "I'd advise you to SCAN AGAIN - Inject the config AGAIN,\n"
            "and then activate services in order to provide the log a complete stack of actions taken."
        )
        
        ctk.CTkLabel(self, text=msg, font=("Roboto", 12), justify="center", wraplength=550).pack(pady=10, padx=20)
        GlowingButton(self, text="Understood", height=40, width=200, command=self.close_me).pack(pady=20)

    def close_me(self):
        self.destroy()
        if self.on_close_callback:
            self.on_close_callback()

class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller

# --- LANDING SCREEN ---
class LandingFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, "assets", "logo.png")
        
        if os.path.exists(logo_path):
            try:
                img_data = Image.open(logo_path)
                img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(120, 120))
                ctk.CTkLabel(self, image=img, text="").pack(pady=(40, 10))
            except:
                ctk.CTkLabel(self, text="h4", font=theme.FONT_LOGO, text_color=theme.COL_ACCENT).pack(pady=(60, 20))
        else:
            ctk.CTkLabel(self, text="INITIALIZING...", font=theme.FONT_HEADER, text_color=theme.COL_ACCENT).pack(pady=(60, 20))

        ctk.CTkLabel(self, text="Do you have LLMs installed locally?", font=theme.FONT_TEXT).pack(pady=10)
        
        local_models = ollama_mgr.OllamaManager.scan_local_manifests()
        if local_models:
            ctk.CTkLabel(self, text=f"Detected {len(local_models)} models in storage.", text_color=theme.COL_ACCENT, font=theme.FONT_TEXT).pack(pady=5)
            
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=30)
        
        # YES Button Logic: If models found, go to Dashboard. If not, go to Dashboard but maybe hint at scan? 
        # User said: "if it can't find any there it initates the hunter protocol"
        # We can pass a flag to Dashboard to auto-scan.
        
        btn_yes = GlowingButton(btn_box, text="YES (Scan System)", width=220, height=50, command=self.on_yes_click)
        btn_yes.pack(side="left", padx=20)
        
        btn_no = GlowingButton(btn_box, text="NO (I need one)", border_color=theme.COL_ERR, hover_color="#330000", width=220, height=50, command=lambda: controller.show_frame("DownloadFrame"))
        btn_no.pack(side="left", padx=20)

    def on_yes_click(self):
        # Check standard locations first
        models = ollama_mgr.OllamaManager.scan_local_manifests()
        if models:
            self.controller.show_frame("DashboardFrame")
        else:
            # If explicit "Yes" but no models found, go to dashboard and trigger scan
            self.controller.show_frame("DashboardFrame")
            dashboard = self.controller.frames.get("DashboardFrame")
            if dashboard:
                 dashboard.log_write("Quick Scan failed. Initiating Hunter Protocol for Models...")
                 dashboard.run_scan() # Auto-trigger scan

# --- DOWNLOAD SCREEN ---
class DownloadFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        ctk.CTkLabel(self, text="MODEL ACQUISITION", font=theme.FONT_HEADER, text_color=theme.COL_ACCENT).pack(pady=20)
        default_model = "dolphin-llama3:8b"
        btn_def = GlowingButton(self, text=f"DOWNLOAD DEFAULT\n({default_model})", height=70, width=350, command=lambda: self.start_download(default_model))
        btn_def.pack(pady=20)
        ctk.CTkLabel(self, text="OR INPUT SPECIFIC MODEL:", font=theme.FONT_TEXT).pack(pady=5)
        link = ctk.CTkLabel(self, text="[View Ollama Library]", font=("Consolas", 12, "underline"), text_color="#5555ff", cursor="hand2")
        link.pack(pady=2)
        link.bind("<Button-1>", lambda e: os.startfile("https://ollama.com/library"))
        self.custom_entry = ctk.CTkEntry(self, width=350, placeholder_text="e.g., mistral:7b", font=theme.FONT_TEXT)
        self.custom_entry.pack(pady=10)
        btn_cust = GlowingButton(self, text="DOWNLOAD CUSTOM", border_color=theme.COL_ACCENT, width=350, height=40, command=lambda: self.start_download(self.custom_entry.get()))
        btn_cust.pack(pady=10)
        self.lbl_status = ctk.CTkLabel(self, text="", font=theme.FONT_TEXT, text_color=theme.COL_WARN)
        self.lbl_status.pack(pady=10)
        self.progress = ctk.CTkProgressBar(self, width=500, progress_color=theme.COL_ACCENT)
        self.progress.pack(pady=10)
        self.progress.set(0)
        ctk.CTkButton(self, text="<< BACK", fg_color="transparent", text_color=theme.COL_TEXT_DIM, command=lambda: controller.show_frame("LandingFrame")).pack(side="bottom", pady=20)

    def start_download(self, model_name):
        if not model_name: return
        self.lbl_status.configure(text=f"Starting download service for {model_name}...")
        threading.Thread(target=lambda: self.run_pull(model_name), daemon=True).start()

    def run_pull(self, model_name):
        if not ollama_mgr.OllamaManager.ensure_running():
            self.lbl_status.configure(text="ERROR: Could not start Ollama service.")
            return
        def update(status, pct):
            self.lbl_status.configure(text=f"{status.upper()}")
            if pct >= 0: self.progress.set(pct)
        success = ollama_mgr.OllamaManager.pull_model(model_name, update)
        if success:
            self.lbl_status.configure(text="INSTALLATION COMPLETE", text_color=theme.COL_ACCENT)
            self.after(1500, lambda: self.controller.show_frame("DashboardFrame"))
        else:
            self.lbl_status.configure(text="DOWNLOAD FAILED", text_color=theme.COL_ERR)

# --- DASHBOARD SCREEN ---
class DashboardFrame(BaseFrame):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        super().__init__(master, controller)
        
        # DYNAMIC LAYOUT: Only allocate space for Column 3 if Debug Mode is ON
        # This prevents "dead space" on the right in normal mode.
        if self.controller.debug_mode:
             self.grid_columnconfigure((0,1,2,3), weight=1)
        else:
             self.grid_columnconfigure((0,1,2), weight=1)
             
        self.grid_rowconfigure(3, weight=1)
        self.resolving_conflict = False 
        self.settings = SettingsManager()
        self.current_theme_idx = 0
        self.is_scanning = False 
        self.last_easter_egg_time = 0
        self.scanner_thread = None
        self.log_queue = queue.Queue()
        self.active_bridge_server = None # LIFECYCLE MANAGEMENT
        
        # PULSE STATE
        self.pulsing_btn = None
        self.pulse_job = None
        self.pulse_state = False
        
        self.btn_scan = GlowingButton(self, text="[1] SCAN SYSTEM", height=40, command=self.run_scan)
        self.btn_scan.grid(row=0, column=0, padx=5, sticky="ew")
        HoverTooltip(self.btn_scan, "Initiates the Hunter Protocol.\n\nScans C:/D: drives for Skyrim, Fallout, and Mod Managers (MO2/Vortex).\nFinds dependencies like PapyrusUtil and Mantella.exe.")
        self.btn_fix = GlowingButton(self, text="[2] CONFIGURE", state="disabled", border_color=theme.COL_DISABLED, text_color=theme.COL_DISABLED, height=40, command=self.open_config)
        self.btn_fix.grid(row=0, column=1, padx=5, sticky="ew")
        HoverTooltip(self.btn_fix, "Opens the Configuration Matrix.\n\nSelect your AI Model (Llama3/Mistral), adjust Context Memory (Tokens),\nand configure TTS engines.")
        self.btn_fix = GlowingButton(self, text="[2] CONFIGURE", state="disabled", border_color=theme.COL_DISABLED, text_color=theme.COL_DISABLED, height=40, command=self.open_config)
        self.btn_fix.grid(row=0, column=1, padx=5, sticky="ew")
        HoverTooltip(self.btn_fix, "Opens the Configuration Matrix.\n\nSelect your AI Model (Llama3/Mistral), adjust Context Memory (Tokens),\nand configure TTS engines.")
        
        self.btn_serv = GlowingButton(self, text="[3] ACTIVATE SERVICES", state="disabled", border_color=theme.COL_DISABLED, text_color=theme.COL_DISABLED, height=40, command=self.run_services)
        self.btn_serv.grid(row=0, column=2, padx=5, sticky="ew")
        HoverTooltip(self.btn_serv, "Starts the Neural Bridge.\n\n1. Boots Port 5000 Server.\n2. Connects to Ollama (Port 11434).\n3. Listens for Skyrim's 'Mantella_Server_Status' handshake.")

        # [4] DIAGNOSTIC (Added per user request, conditional on Debug Mode)
        # Note: self.controller is h4App, which has self.debug_mode
        self.btn_diag = GlowingButton(self, text="[4] DIAGNOSTIC", border_color="#555555", text_color="#aaaaaa", height=40, command=self.run_diagnostics)
        HoverTooltip(self.btn_diag, "Checks connection status.\n\nPings Ports 5000, 5001, 11434.\nUse this to troubleshoot 'Failed to Connect' errors.")
        
        if self.controller.debug_mode:
             self.btn_diag.grid(row=0, column=3, padx=5, sticky="ew")
             self.btn_diag.configure(state="normal", border_color=theme.COL_ACCENT, text_color=theme.COL_ACCENT) # LIGHT UP DEFAULT
        else:
             self.btn_diag.grid_forget() # Hide if not debug

        self.status_container = ctk.CTkScrollableFrame(self, fg_color=theme.COL_PANEL, height=150, corner_radius=5)
        self.status_container.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(15, 5))
        self.lbl_det_header = ctk.CTkLabel(self.status_container, text="DETECTED COMPONENTS (Click to Manage)", font=("Consolas", 12, "bold"), text_color=theme.COL_ACCENT)
        self.lbl_det_header.pack(pady=5)
        
        self.progress = ctk.CTkProgressBar(self, height=4, progress_color=theme.COL_ACCENT)
        self.progress.grid(row=2, column=0, columnspan=4, sticky="ew", padx=2, pady=(10, 0))
        self.progress.set(0)

        # LOG BOX (The big one)
        self.log_box = ctk.CTkTextbox(self, fg_color="#0a0a0a", text_color="#cccccc", font=theme.FONT_TEXT, height=150, border_width=1, border_color=theme.COL_DISABLED, state="disabled")
        self.log_box.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=5)
        
        # --- NEW: ACTIVE SCAN LINE ---
        self.lbl_active_scan = ctk.CTkLabel(self, text="", font=("Consolas", 11, "bold"), text_color=theme.COL_ACCENT, anchor="w")
        self.lbl_active_scan.grid(row=4, column=0, columnspan=4, sticky="ew", padx=10, pady=(0, 5))
        
        # --- TAGS ---
        self.log_box._textbox.tag_config("found", foreground="#00ff00", font=("Consolas", 12, "bold"))
        self.log_box._textbox.tag_config("done", foreground="#00ff99")
        self.log_box._textbox.tag_config("skyrim", foreground="#00ccff") 
        self.log_box._textbox.tag_config("scr_log", foreground="#ffff00") 
        self.log_box._textbox.tag_config("net_log", foreground="#ff00ff") 
        self.log_box._textbox.tag_config("error", foreground="#ff3333", font=("Consolas", 12, "bold"))  
        
        self.log_box._textbox.tag_config("hyperlink", foreground="#3399ff", underline=True)
        self.log_box._textbox.tag_bind("hyperlink", "<Button-1>", self.open_config_target)
        self.log_box._textbox.tag_bind("hyperlink", "<Enter>", lambda e: self.log_box.configure(cursor="hand2"))
        self.log_box._textbox.tag_bind("hyperlink", "<Leave>", lambda e: self.log_box.configure(cursor="arrow"))

        self.log_write(f"{theme.ASCII_BANNER}\n\n[SYSTEM READY]\nClick 'SCAN SYSTEM' to begin hunter protocol.\n")

        self.launcher_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.launcher_frame.grid(row=5, column=0, columnspan=4, sticky="ew", pady=10)
        self.launcher_frame.grid_columnconfigure((0, 1), weight=1)
        self.btn_mo2 = GlowingButton(self.launcher_frame, text="LAUNCH MO2", state="disabled", fg_color=theme.COL_ACCENT, border_color=theme.COL_ACCENT, text_color="black", height=45, command=lambda: self.launch_app("ModOrganizer"))
        self.btn_mo2.grid(row=0, column=0, padx=5, sticky="ew")
        self.btn_vortex = GlowingButton(self.launcher_frame, text="LAUNCH VORTEX", state="disabled", fg_color=theme.COL_ACCENT, border_color=theme.COL_ACCENT, text_color="black", height=45, command=lambda: self.launch_app("Vortex"))
        self.btn_vortex.grid(row=0, column=1, padx=5, sticky="ew")

        # --- FOOTER ---
        self.status_footer = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.status_footer.grid(row=6, column=0, columnspan=4, sticky="s", pady=(10, 5))
        
        self.lbl_motto = ctk.CTkLabel(self.status_footer, text="h4 - { Be Your Best }", text_color="#444444", font=("Consolas", 10, "italic"))
        self.lbl_motto.pack(anchor="center")

        self.lbl_sig = ctk.CTkLabel(self.status_footer, text="(b'.')b", text_color="#444444", font=("Consolas", 12, "bold"), cursor="hand2")
        self.lbl_sig.pack(anchor="center")
        self.lbl_sig.bind("<Button-1>", self.on_sig_click)
        CTkTooltip(self.lbl_sig, "CTRL+SHIFT+H+4", delay=10000)

        self.controller.register_log_widget(self.log_box)
        bridge_server.set_log_callback(self.log_write)
        
        self.watcher = LogWatcher()
        self.watcher.set_callback(self.log_watcher_cb)
        self.watcher.start()

        self.check_log_queue()
        self.log_write("[SYSTEM] Input Monitor: ACTIVE")
        self.monitor_input()
        
        if self.settings.load_scan_data(TARGETS):
             self.log_write("[MEMORY] Previous Scan Data Loaded.")
             self.progress.configure(mode="determinate")
             self.progress.set(1.0)
             self.refresh_components_list() 
             self.update_action_buttons()
        else:
             self.refresh_components_list()

        if self.controller.debug_mode:
            self.after(500, self.show_debug_popup)

    def start_pulse(self, btn):
        self.stop_pulse() 
        self.pulsing_btn = btn
        self._pulse_loop()

    def stop_pulse(self):
        if self.pulse_job:
            self.after_cancel(self.pulse_job)
            self.pulse_job = None
        if self.pulsing_btn:
            self.pulsing_btn.configure(border_color=theme.COL_BTN_BORDER) 
            self.pulsing_btn = None

    def _pulse_loop(self):
        if not self.pulsing_btn: return
        color = "#ff0000" if self.pulse_state else "#550000" 
        self.pulsing_btn.configure(border_color=color)
        self.pulse_state = not self.pulse_state
        self.pulse_job = self.after(400, self._pulse_loop)

    def show_debug_popup(self):
        DebugIntroDialog(self, on_close_callback=self.start_debug_flow)

    def start_debug_flow(self):
        self.start_pulse(self.btn_scan)

    def open_config_target(self, event):
        if TARGETS["Mantella"]["found"]:
            path = os.path.join(TARGETS["Mantella"]["found"], "config.ini")
            if os.path.exists(path):
                try: os.startfile(path); self.log_write("[SYSTEM] Opened config.ini externally.")
                except Exception as e: self.log_write(f"[ERROR] Could not open file: {e}")

    def log_watcher_cb(self, msg):
        tag = "skyrim"
        if "[SCR]" in msg: tag = "scr_log"
        elif "[NET]" in msg: tag = "net_log"
        self.log_queue.put((msg, tag))

    def destroy(self):
        # CLEANUP: Stop all threads/timers
        self.stop_pulse()
        if hasattr(self, 'watcher'): self.watcher.stop()
        
        # NUCLEAR EXIT: Kill Server
        if self.active_bridge_server:
            try:
                self.active_bridge_server.shutdown()
                self.active_bridge_server.server_close()
            except: pass
            
        super().destroy()

    def check_log_queue(self):
        if not self.winfo_exists(): return
        while not self.log_queue.empty():
            try:
                data = self.log_queue.get_nowait()
                if isinstance(data, tuple) and data[0] in ["SCAN_RAPID", "SCAN_LOG", "FOUND", "MISSING", "CONFLICT", "DONE", "MISSING_MODS"]:
                     self.scan_status_cb(data)
                elif isinstance(data, tuple):
                     self.log_write(data[0], data[1])
                else:
                     self.log_write(str(data))
            except: break
        self.after(50, self.check_log_queue)

    def monitor_input(self):
        if not self.winfo_exists(): return
        try:
            VK_CONTROL = 0x11
            VK_SHIFT = 0x10
            VK_H = 0x48
            VK_4 = 0x34
            VK_NUMPAD4 = 0x64
            ctrl = ctypes.windll.user32.GetAsyncKeyState(VK_CONTROL) & 0x8000
            shift = ctypes.windll.user32.GetAsyncKeyState(VK_SHIFT) & 0x8000
            h_key = ctypes.windll.user32.GetAsyncKeyState(VK_H) & 0x8000
            four = (ctypes.windll.user32.GetAsyncKeyState(VK_4) & 0x8000) or \
                   (ctypes.windll.user32.GetAsyncKeyState(VK_NUMPAD4) & 0x8000)
            if ctrl and shift and h_key and four:
                if time.time() - self.last_easter_egg_time > 2.0:
                    self.last_easter_egg_time = time.time()
                    self.log_write("[SYSTEM] 🥚 SEQUENCE DETECTED")
                    threading.Thread(target=lambda: audit_log.run_diagnostics_check(self.controller)).start()
        except: pass 
        self.after(50, self.monitor_input)

    def on_sig_click(self, event):
        self.cycle_theme()

    def cycle_theme(self, event=None):
        self.current_theme_idx = (self.current_theme_idx + 1) % len(theme.THEME_CYCLE)
        new_accent, new_hover = theme.THEME_CYCLE[self.current_theme_idx]
        theme.COL_ACCENT = new_accent
        theme.COL_BTN_BORDER = new_accent
        theme.COL_BTN_HOVER = new_hover
        self.log_write(f"[THEME] Cycled to: {new_accent}")
        self.lbl_det_header.configure(text_color=new_accent)
        self.progress.configure(progress_color=new_accent)
        buttons = [self.btn_scan, self.btn_fix, self.btn_serv]
        for btn in buttons:
            if btn.cget("state") != "disabled":
                btn.configure(border_color=new_accent, text_color=theme.COL_TEXT)
        launchers = [self.btn_mo2, self.btn_vortex]
        for btn in launchers:
            btn.configure(fg_color=new_accent, border_color=new_accent)
        for widget in self.status_container.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                if "✔" in widget.cget("text"): widget.configure(border_color=new_accent)

    def log_write(self, msg, tag=None):
        clean_msg = sanitize(str(msg))
        if "ERROR" in clean_msg: sys_log.error(clean_msg)
        elif "Scanning" not in clean_msg: sys_log.info(clean_msg)
        def _insert():
            # Defensive check
            if not self.winfo_exists(): return
            self.log_box.configure(state="normal")
            
            # --- HYPERLINK LOGIC CONFIRMED ---
            try:
                if "ready for inspection" in clean_msg:
                    prefix, match, suffix = clean_msg.partition("inspection")
                    self.log_box.insert("end", prefix, tag)
                    self.log_box.insert("end", match, "hyperlink") 
                    self.log_box.insert("end", suffix + "\n", tag)
                else:
                    self.log_box.insert("end", clean_msg + "\n", tag)

                # MEMORY FIX: Check line count periodically or if buffer is large
                # We use a lazy check to avoid hammering the Tcl interpreter
                if (len(clean_msg) > 100) or (self.log_queue.qsize() > 10):
                     line_count = int(self.log_box.index('end-1c').split('.')[0])
                     if line_count > 800: # Reduced limit to 800
                         self.log_box.delete("1.0", "300.0") # Delete chunk
                         
            except Exception as e:
                # If Tcl crashes or OOM, clear half the log as emergency
                print(f"Log Error: {e}")
                try: self.log_box.delete("1.0", "500.0")
                except: pass

            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(50, _insert) # Slow down refresh rate slightly to 50ms from 0ms

    def refresh_components_list(self):
        for w in self.status_container.winfo_children():
            if w != self.lbl_det_header: w.destroy()
        
        for name in sorted(TARGETS.keys()):
            data = TARGETS[name]
            if name == "Models": continue 
            found = bool(data["found"])
            color = theme.COL_ACCENT if found else theme.COL_ERR
            text_val = f"✔ {name} : {data['found']}" if found else f"X {name} (Missing)"
            if not found and len(data.get("candidates", [])) > 1:
                color = theme.COL_WARN
                text_val = f"⚠ {name} : CONFLICT DETECTED ({len(data['candidates'])} found)"
            btn = ctk.CTkButton(
                self.status_container, 
                text=text_val, 
                fg_color="transparent", 
                border_width=1, 
                border_color=color, 
                text_color=theme.COL_TEXT, 
                anchor="w", 
                font=("Consolas", 11), 
                command=lambda n=name: self.handle_component_click(n)
            )
            btn.pack(fill="x", pady=2, padx=5)
            CTkTooltip(btn, f"Click to Manually Set/Change {name} Path")

    def handle_component_click(self, name):
        data = TARGETS[name]
        current_path = data.get("found", "Not Set")
        candidates = data.get("candidates", [])
        def manager_action(action_type, payload):
            if action_type == "OPEN":
                if current_path and os.path.exists(current_path):
                    path_to_open = current_path
                    if os.path.isfile(path_to_open): path_to_open = os.path.dirname(path_to_open)
                    try: os.startfile(path_to_open); self.log_write(f"[SYSTEM] Opened: {path_to_open}")
                    except Exception as e: self.log_write(f"[ERROR] Cannot open path: {e}")
            elif action_type == "SWITCH":
                TARGETS[name]["found"] = payload
                self.log_write(f"[USER] Switched {name} to: {payload}")
                self.settings.save_scan_data(TARGETS)
                self.refresh_components_list()
                self.update_action_buttons() 
            elif action_type == "BROWSE":
                self.browse_for_target(name)
        ComponentManagerDialog(self.controller, name, current_path, candidates, manager_action)

    def browse_for_target(self, name):
        data = TARGETS[name]
        is_exe = (data["type"] == "exe")
        title = f"Select {data['file']}" if is_exe else f"Select {name} Installation Folder"
        path = fd.askopenfilename(title=title, filetypes=[(name, "*.exe")]) if is_exe else fd.askdirectory(title=title)
        if path:
            path = path.replace("/", "\\")
            TARGETS[name]["found"] = path
            self.log_write(f"[USER] Manually set {name} -> {path}")
            self.settings.save_scan_data(TARGETS)
            self.refresh_components_list()
            self.update_action_buttons()

    def run_diagnostics(self):
        import socket
        from utils import firewall_mgr
        
        self.log_write("\n--- DIAGNOSTIC SCAN ---")
        
        # Read Configured Ports
        proxy_port = self.settings.get_setting("proxy_port") or PROXY_PORT
        game_port = self.settings.get_setting("game_port") or 4999
        brain_port = 11434
        
        targets = [
            (game_port, "Mantella.exe (Game)"),
            (proxy_port, "Omni-Tool (Proxy)"),
            (brain_port, "Ollama (Brain)")
        ]
        
        all_green = True
        for port, name in targets:
            try:
                # 1. LISTENING CHECK
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                s.close()
                status = "ONLINE" if result == 0 else "OFFLINE"
                tag = "found" if result == 0 else "error"
                
                # 2. FIREWALL CHECK
                fw_ok = firewall_mgr.check_rule_exists(port)
                fw_status = "[FW: OK]" if fw_ok else "[FW: ?]"
                
                self.log_write(f"[{'PASS' if result==0 else 'FAIL'}] {name}: {status} (Port {port}) {fw_status}", tag)
                if result != 0: all_green = False
                
            except Exception as e:
                 self.log_write(f"[ERR] {name}: {e}", "error")
                 all_green = False
        
        if all_green:
            self.log_write("SYSTEM GREEN. Chain is Valid.", "done")
        else:
            self.log_write("SYSTEM RED. Connection Broken.", "error")
            if not all_green:
                 self.log_write("Hint: If Game is offline, Launch Skyrim.", "scr_log")

    def run_scan(self):
        if self.is_scanning: return
        self.is_scanning = True 
        if self.pulsing_btn == self.btn_scan: self.stop_pulse()
        self.log_write("Hunter Protocol Initiated...")
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self.scanner_thread = scanner.HunterProtocol(callback=self.scan_queue_injector)
        self.scanner_thread.daemon = True
        self.scanner_thread.start()

    def scan_queue_injector(self, data):
        self.log_queue.put(data)

    def scan_status_cb(self, data):
        try:
            msg_type, msg = data
            if msg_type == "SCAN_LOG":
                self.log_write(msg)
            elif msg_type == "SCAN_RAPID":
                self.lbl_active_scan.configure(text=msg)
            elif msg_type == "FOUND":
                self.log_write(f"✔ {msg}", "found")
                self.refresh_components_list()
            elif msg_type == "CONFLICT":
                self.log_write(f"⚠ {msg}")
            elif msg_type == "DONE":
                found, missing, duration = msg
                self.lbl_active_scan.configure(text="")
                self.log_write("\n")
                self.log_write(f"[ Scan Complete: {found} Components Found | {missing} Missing ]", "done")
                self.log_write(f"Operation took {duration}s")
                self.log_write("Hint: Click red bars above to manually set missing paths.", "done")
                self.is_scanning = False
                
                # FIX: Switch to determinate mode so it fills green
                self.progress.stop()
                self.progress.configure(mode="determinate") 
                self.progress.set(1.0)
                
                if self.settings: self.settings.save_scan_data(TARGETS)
                self.refresh_components_list()
                self.update_action_buttons()
                if self.controller.debug_mode: self.start_pulse(self.btn_fix)
            elif msg_type == "MISSING_MODS":
                self.show_missing_mods_popup(msg)
        except Exception as e: print(f"UI Update Error: {e}")

    def show_missing_mods_popup(self, missing_list):
        MissingModsDialog(self.controller, missing_list)

    def check_conflicts(self):
        if not self.resolving_conflict:
            for name, data in TARGETS.items():
                if not data["found"] and len(data.get("candidates", [])) > 1:
                    self.resolving_conflict = True
                    self.log_write(f"[SYSTEM] Resolving conflict for {name}...")
                    SelectionDialog(self.controller, name, data["candidates"], lambda choice, n=name: self.resolve_conflict(n, choice))
                    return 

    def update_action_buttons(self):
        has_game = any(bool(TARGETS[k]["found"]) for k in ["SkyrimSE", "SkyrimVR", "Fallout4", "Fallout4VR"])
        if TARGETS["Mantella"]["found"] and has_game: 
            self.btn_fix.configure(state="normal", border_color=theme.COL_BTN_BORDER, text_color=theme.COL_TEXT)
            self.btn_serv.configure(state="normal", border_color=theme.COL_BTN_BORDER, text_color=theme.COL_TEXT)
        if TARGETS["ModOrganizer"]["found"]: self.btn_mo2.configure(state="normal")
        if TARGETS["Vortex"]["found"]: self.btn_vortex.configure(state="normal")

    def resolve_conflict(self, name, choice):
        TARGETS[name]["found"] = choice
        self.log_write(f"[USER] Selected {name} path: {choice}")
        self.settings.save_scan_data(TARGETS)
        self.resolving_conflict = False
        self.update_action_buttons()
        self.refresh_components_list()
        self.check_conflicts() 

    def open_config(self):
        if self.pulsing_btn == self.btn_fix: self.stop_pulse()
        path = TARGETS["Mantella"]["found"]
        if path and os.path.isfile(path):
            path = os.path.dirname(path)
        if path: 
            def on_save_wrapper():
                if self.controller.debug_mode: self.start_pulse(self.btn_serv)
            ConfigPopup(self, path, on_save_wrapper)

    def run_services(self):
        if self.pulsing_btn == self.btn_serv: self.stop_pulse()
        
        def _activate():
            # --- LIFECYCLE CHECK ---
            if self.active_bridge_server:
                self.log_write("Bridge detected. Stopping to restart service...", "net_log")
                try:
                    self.active_bridge_server.shutdown()
                    self.active_bridge_server.server_close()
                    self.active_bridge_server = None
                    self.log_write("Previous Bridge halted.", "net_log")
                    time.sleep(1) # Give OS a moment to release port
                except Exception as e:
                    self.log_write(f"Error stopping bridge: {e}")

            # --- OLLAMA CHECK ---
            self.log_write("Activating Ollama...")
            if ollama_mgr.OllamaManager.ensure_running(): 
                self.log_write("Ollama Service: [ONLINE]")
            else: 
                self.log_write("Ollama Service: [FAILED]")
                return

            # --- CONFIG READ ---
            mantella_path = TARGETS["Mantella"]["found"]
            if mantella_path and os.path.isfile(mantella_path):
                mantella_path = os.path.dirname(mantella_path)

            # --- AUTOMATED PATCHING (OMNI-TOOL BYPASS) ---
            try:
                self.log_write("Verifying Mantella Integrity & Patches...")
                from core.mantella_patcher import MantellaPatcher
                MantellaPatcher.execute_patches(mantella_path)
            except Exception as e:
                self.log_write(f"[WARN] Patch verification failed: {e}")
            
            config_file = os.path.join(mantella_path, "config.ini")
            if os.path.exists(config_file):
                try:
                    parser = configparser.ConfigParser()
                    parser.read(config_file)
                    tts_val = "Piper"
                    for sec in parser.sections():
                        if "tts_service" in parser[sec]: 
                            tts_val = parser[sec]["tts_service"]
                            break
                    self.log_write(f"Config Read: TTS Service = '{tts_val}'")
                    
                    if tts_val.strip().lower() == "xvasynth":
                        xva_exe = TARGETS["xVASynth"]["found"]
                        if xva_exe and os.path.exists(xva_exe):
                            self.log_write(f"Launching xVASynth...")
                            try: 
                                os.startfile(xva_exe)
                                self.log_write("xVASynth Service: [LAUNCHED]")
                            except: pass
                except: pass

            # --- FIREWALL ENFORCEMENT ---
            self.log_write("Enforcing Firewall Rules...")
            try:
                from utils import firewall_mgr
                firewall_mgr.enforce_omni_ports()
                self.log_write("Firewall Ports (5000, 5001, 11434) rules verified.")
            except Exception as e:
                self.log_write(f"[WARN] Firewall Rule Error: {e}")

            # --- BRIDGE START ---
            # --- BRIDGE START ---
            proxy_port = self.settings.get_setting("proxy_port") or PROXY_PORT # Read dynamic port
            self.log_write(f"Activating AI Proxy on Port {proxy_port}...")
            server_instance = bridge_server.start_bridge_thread(port=proxy_port)
            
            if server_instance:
                self.active_bridge_server = server_instance # Store handle
                self.log_write(f"Proxy Service: [ONLINE]", "net_log")
                self.log_write(f"Listening on localhost:{proxy_port}")
                self.log_write("Ready for Mantella.exe connection.")
            else:
                self.log_write("[CRITICAL] Proxy Failed to Start", "net_log")

        threading.Thread(target=_activate).start()

    def launch_app(self, app_name):
        exe = TARGETS[app_name]["found"]
        if exe and os.path.exists(exe):
            try: os.startfile(exe)
            except: pass

# ... [Previous Code] ...

from core.mantella_patcher import MantellaPatcher

# ... [Existing Imports] ...

class ConfigPopup(ctk.CTkToplevel):
    def __init__(self, parent, mantella_path, on_save):
        super().__init__(parent)
        apply_icon(self) 
        self.dashboard = parent
        self.title("Configuration Lab")
        self.geometry("600x650") 
        self.configure(fg_color=theme.COL_BG)
        self.mantella_path = mantella_path
        self.config_file = os.path.join(mantella_path, "config.ini")
        self.on_save = on_save
        self.grab_set()
        self.attributes("-topmost", True)
        self.dashboard.log_write("... Config Injection Open")

        ctk.CTkLabel(self, text="CONFIG INJECTOR", font=theme.FONT_HEADER, text_color=theme.COL_ACCENT).pack(pady=20)
        self.tabs = ctk.CTkTabview(self, width=580, height=450)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)
        
        # TAB ORDER: NETWORK / BRAIN / VOICE / VISION / MANTELLA / PLAYER
        self.tabs.add("NETWORK")
        self.tabs.add("BRAIN")
        self.tabs.add("VOICE")
        self.tabs.add("VISION")
        self.tabs.add("MANTELLA")
        self.tabs.add("PLAYER")
        
        # --- TAB 1: MANTELLA (CORE CONTROLS) ---
        man_tab = self.tabs.tab("MANTELLA")
        ctk.CTkLabel(man_tab, text="Core Features:", font=theme.FONT_HEADER).pack(pady=(20, 10))
        
        # Read current state
        self.var_actions = ctk.BooleanVar(value=True)
        self.var_follow = ctk.BooleanVar(value=False)
        self.var_aggro = ctk.BooleanVar(value=False)
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "allow_actions = True" in content: self.var_actions.set(True)
                elif "allow_actions = False" in content: self.var_actions.set(False)

                if "allow_follow = True" in content: self.var_follow.set(True)
                elif "allow_follow = False" in content: self.var_follow.set(False)
                
                if "allow_aggro = True" in content: self.var_aggro.set(True)
                elif "allow_aggro = False" in content: self.var_aggro.set(False)
        except: pass
        
        # Switches
        def toggle_mantella(key, var):
             val = var.get()
             if MantellaPatcher.update_config(self.mantella_path, key, val):
                 self.dashboard.log_write(f"[CONFIG] {key} -> {val}")
             else:
                 self.dashboard.log_write(f"[ERROR] Failed to update {key}", "error")

        ctk.CTkSwitch(man_tab, text="Allow Actions (Inventory/Trade)", variable=self.var_actions, 
                      command=lambda: toggle_mantella("allow_actions", self.var_actions)).pack(pady=10)
        
        ctk.CTkSwitch(man_tab, text="Allow Following (Shadow Mode)", variable=self.var_follow, 
                      command=lambda: toggle_mantella("allow_follow", self.var_follow)).pack(pady=10)
        
        ctk.CTkSwitch(man_tab, text="Allow Aggro (Combat Hostility)", variable=self.var_aggro, 
                      command=lambda: toggle_mantella("allow_aggro", self.var_aggro)).pack(pady=10)

        ctk.CTkLabel(man_tab, text="Note: Toggling creates a backup (.bak) of config.ini", text_color="gray", font=("Consolas", 10)).pack(pady=20)
        
        # --- TAB 2: NETWORK ---
        net_tab = self.tabs.tab("NETWORK")
        
        ctk.CTkLabel(net_tab, text="Connection Strategy:", font=theme.FONT_TEXT).pack(pady=(15, 5))
        self.combo_net = ctk.CTkComboBox(net_tab, values=["Localhost (Default)", "Custom Network"], 
                                         height=35, width=250, command=self.on_net_change)
        self.combo_net.set("Localhost (Default)")
        self.combo_net.pack(pady=5)
        
        self.frame_custom_net = ctk.CTkFrame(net_tab, fg_color="transparent")
        ctk.CTkLabel(self.frame_custom_net, text="Ollama Host IP:").pack(anchor="w", padx=15)
        self.ent_host = ctk.CTkEntry(self.frame_custom_net, width=250, placeholder_text="127.0.0.1")
        self.ent_host.pack(pady=5)
        ctk.CTkLabel(self.frame_custom_net, text="Proxy Port (Default 5001):").pack(anchor="w", padx=15)
        self.ent_proxy_port = ctk.CTkEntry(self.frame_custom_net, width=250, placeholder_text="5001")
        self.ent_proxy_port.pack(pady=5)
        ctk.CTkLabel(self.frame_custom_net, text="Game Port (Default 4999):").pack(anchor="w", padx=15)
        self.ent_game_port = ctk.CTkEntry(self.frame_custom_net, width=250, placeholder_text="4999")
        self.ent_game_port.pack(pady=5)
        
        # Firewall
        ctk.CTkLabel(net_tab, text="Firewall Management:", font=theme.FONT_TEXT).pack(pady=(20, 5))
        GlowingButton(net_tab, text="[OPEN FIREWALL PORTS]", width=200, height=35, border_color="#aa0000", hover_color="#550000", command=self.manual_firewall).pack(pady=5)
        HoverTooltip(net_tab.winfo_children()[-1], "Forces Windows Firewall to Allow TCP Ports:\n- 4999 (Mantella)\n- 5001 (Proxy)\n- 11434 (Ollama)\n\nRequires Admin Privileges.")

        # --- TAB 2: BRAIN ---
        brain_tab = self.tabs.tab("BRAIN")
        
        # Model
        ctk.CTkLabel(brain_tab, text="Select Intelligence Model:", font=theme.FONT_HEADER).pack(pady=(20, 10))
        self.combo_model = ctk.CTkComboBox(brain_tab, values=["Scanning..."], width=300, height=40, font=theme.FONT_TEXT, command=self.on_model_change)
        self.combo_model.pack(pady=10)
        HoverTooltip(self.combo_model, "The 'Soul' of the NPC.\nSelect a localized LLM hosted by Ollama.\n'llama3' is recommended.")
        
        # Context (Memory)
        ctk.CTkLabel(brain_tab, text="Context Window (Memory):", font=theme.FONT_TEXT).pack(pady=(20, 5))
        self.slider_tokens = ctk.CTkSlider(brain_tab, from_=2048, to=32768, number_of_steps=15, width=400)
        self.slider_tokens.set(4096)
        self.slider_tokens.pack(pady=5)
        self.lbl_tokens = ctk.CTkLabel(brain_tab, text="4096 Tokens")
        self.lbl_tokens.pack()
        self.slider_tokens.configure(command=lambda v: self.lbl_tokens.configure(text=f"{int(v)} Tokens"))
        
        # Async Load
        threading.Thread(target=self._async_load_models, daemon=True).start()

        # --- TAB 3: VOICE ---
        voice_tab = self.tabs.tab("VOICE")
        ctk.CTkLabel(voice_tab, text="Text-to-Speech Engine:", font=theme.FONT_HEADER).pack(pady=(20, 10))
        
        self.tts_mode = ctk.StringVar(value="Piper")
        
        frame_rdo = ctk.CTkFrame(voice_tab, fg_color="transparent")
        frame_rdo.pack(pady=10)
        r1 = ctk.CTkRadioButton(frame_rdo, text="Piper (Standard)", variable=self.tts_mode, value="Piper", command=self.on_tts_change)
        r1.pack(side="left", padx=20)
        r2 = ctk.CTkRadioButton(frame_rdo, text="xVASynth (Premium)", variable=self.tts_mode, value="xVASynth", command=self.on_tts_change)
        r2.pack(side="left", padx=20)
        
        # xVA Path Select
        self.frame_xva = ctk.CTkFrame(voice_tab)
        self.frame_xva.pack(pady=10, fill="x", padx=40)
        ctk.CTkLabel(self.frame_xva, text="xVASynth.exe Path:").pack(anchor="w", padx=10, pady=5)
        self.entry_xva = ctk.CTkEntry(self.frame_xva, placeholder_text="C:/.../xVASynth.exe")
        self.entry_xva.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkButton(self.frame_xva, text="Browse...", width=100, command=self.find_xva_exe).pack(anchor="e", padx=10, pady=(0, 10))
        if TARGETS["xVASynth"]["found"]: self.entry_xva.insert(0, TARGETS["xVASynth"]["found"])

        # --- TAB 4: VISION ---
        vision_tab = self.tabs.tab("VISION")
        ctk.CTkLabel(vision_tab, text="Visual Cortex:", font=theme.FONT_HEADER).pack(pady=20)
        self.vision_enabled = ctk.BooleanVar(value=False)
        ctk.CTkSwitch(vision_tab, text="Enable Vision (Experimental)", variable=self.vision_enabled).pack(pady=10)
        ctk.CTkLabel(vision_tab, text="Vision Model:", font=theme.FONT_TEXT).pack(pady=(10, 5))
        self.combo_vision = ctk.CTkComboBox(vision_tab, values=["llava:latest"], width=250)
        self.combo_vision.pack(pady=5)
        ctk.CTkLabel(vision_tab, text="Note: Requires 'llava' or 'llama-vision' models pulled.", text_color="gray").pack()
        
        # --- TAB 5: PLAYER (New Feature) ---
        ply_tab = self.tabs.tab("PLAYER")
        ctk.CTkLabel(ply_tab, text="Who are you?", font=theme.FONT_HEADER).pack(pady=(20, 10))
        ctk.CTkLabel(ply_tab, text="Describe your character to the AI.\nThis text is injected into the prompt as {player_description}.\nUse this to define your appearance, race, or reputation.", 
                     font=theme.FONT_TEXT, justify="center").pack(pady=5)
        
        # Placeholder Text with Prompt Guide
        self.txt_player_desc = ctk.CTkTextbox(ply_tab, width=450, height=200, font=theme.FONT_TEXT)
        self.txt_player_desc.pack(pady=20)
        
        self.placeholder_txt = (
            "[PROMPT GUIDE]\n"
            "The AI observes your physical presence. It cannot read your mind or memories.\n\n"
            "BAD (Backstory/Hidden Info):\n"
            "\"I am an orphan looking for my parents. I hate goblins.\"\n\n"
            "GOOD (Visuals/Aura/Reputation):\n"
            "\"I am a weary traveler with a hopeful expression. I wear tattered robes.\"\n"
            "\"I carry myself with the swagger of a known thief.\"\n\n"
            "Describe your looks, gear, and the immediate 'vibe' you give off."
        )
        self.txt_player_desc.insert("1.0", self.placeholder_txt)
        self.txt_player_desc.configure(text_color="gray")
        
        def _on_focus_in(event):
            if "[PROMPT GUIDE]" in self.txt_player_desc.get("1.0", "end"):
                self.txt_player_desc.delete("1.0", "end")
                self.txt_player_desc.configure(text_color="white")
        
        self.txt_player_desc.bind("<FocusIn>", _on_focus_in)

        # ACTIONS
        btn_box = ctk.CTkFrame(self, fg_color="transparent")
        btn_box.pack(pady=20)
        GlowingButton(btn_box, text="SAFE INJECT CONFIG", height=50, width=180, command=self.save_config).pack(side="left", padx=10)
        GlowingButton(btn_box, text="RESTORE DEFAULTS", border_color=theme.COL_WARN, text_color=theme.COL_WARN, height=50, width=180, command=self.restore_defaults).pack(side="left", padx=10)

    def on_net_change(self, choice):
        if "Custom" in choice:
            self.frame_custom_net.pack(pady=10)
        else:
            self.frame_custom_net.pack_forget()

    def manual_firewall(self):
        try:
            from utils import firewall_mgr
            firewall_mgr.enforce_omni_ports()
            self.dashboard.log_write("Firewall Rules Updated (Check Console for Details).", "net_log")
            tk.messagebox.showinfo("Firewall", "Commands sent to Windows Firewall.\nIf ports were closed, they should now be open.")
        except Exception as e:
             tk.messagebox.showerror("Firewall Error", str(e))

    def on_model_change(self, choice): self.dashboard.log_write(f"... Model Changed to {choice}")
    def on_tts_change(self): self.dashboard.log_write(f"... TTS Engine switched to {self.tts_mode.get()}")
    
    def find_xva_exe(self):
        self.attributes("-topmost", False)
        path = fd.askopenfilename(title="Locate xVASynth.exe", filetypes=[("xVASynth", "xVASynth.exe")])
        self.attributes("-topmost", True)
        self.lift()
        if path:
            self.entry_xva.delete(0, "end"); self.entry_xva.insert(0, path); self.tts_mode.set("xVASynth") 

    def restore_defaults(self):
        if not messagebox.askyesno("Confirm Reset", "Are you sure you want to reset config.ini to defaults?"): return
        self.tts_mode.set("Piper"); self.slider_tokens.set(4096); self.combo_model.set("dolphin-llama3:8b")
        self.vision_enabled.set(False)
        
        # Reset Player Desc
        self.txt_player_desc.delete("1.0", "end")
        self.txt_player_desc.insert("1.0", self.placeholder_txt)
        self.txt_player_desc.configure(text_color="gray")
        
        if safe_injector.inject_safely(self.config_file, {
            "model": "dolphin-llama3:8b", "tokens": 4096, "tts_service": "Piper", "vision_enabled": False,
            "player_description": "",
            "game_mode": self.dashboard.settings.get_setting("game_mode") or "SkyrimSE"
        }, log_callback=self.dashboard.log_write):
            self.on_save(); self.destroy()

    def save_config(self):
        # 1. CHECK FOR GAME CONFLICTS
        found_games = [g for g in ["SkyrimSE", "SkyrimVR", "Fallout4", "Fallout4VR"] if TARGETS[g]["found"]]
        current_setting = self.dashboard.settings.get_setting("game_mode") or "SkyrimSE"
        
        # If multiple games found, we MUST ask (Conflict Protocol)
        if len(found_games) > 1:
            self.attributes("-topmost", False)
            GameSelectorDialog(self, found_games, self.finish_injection)
        else:
            # If 1 game, use it. If 0, use setting.
            target = found_games[0] if len(found_games) == 1 else current_setting
            self.finish_injection(target)

    def finish_injection(self, selected_game):
        self.attributes("-topmost", True)
        if not messagebox.askyesno("Confirm Injection", f"Overwrite Mantella/config.ini for {selected_game}?"): return
        
        data = {
            "model": self.combo_model.get(),
            "tokens": int(self.slider_tokens.get()),
            "tts_service": self.tts_mode.get(),
            "vision_enabled": self.vision_enabled.get(),
            "vision_model": self.combo_vision.get(),
            "game_mode": selected_game
        }
        if self.tts_mode.get() == "xVASynth":
            path = self.entry_xva.get()
            if path: data["xvasynth_path"] = path
            
        if safe_injector.inject_safely(self.config_file, data, log_callback=self.dashboard.log_write):
            # --- PROXY CONFIGURATION ---
            # We must force Mantella to use US as the LLM provider.
            # This means setting llm_service='OpenAI' and url='http://localhost:5001/v1'
            pass
            
            # Since safe_injector merges data, we need to pass these extra keys
            # injecting Ollama keys to route traffic to US
            # AND enforcing Server Port 5000 (to match SKSE client)
            # Determine Network Settings
            if "Custom" in self.combo_net.get():
                target_host = self.ent_host.get().strip() or "127.0.0.1"
                try: target_proxy_port = int(self.ent_proxy_port.get().strip())
                except: target_proxy_port = PROXY_PORT
                
                try: target_game_port = int(self.ent_game_port.get().strip())
                except: target_game_port = 4999
                
                # PERSIST SETTINGS
                self.dashboard.settings.update_setting("proxy_port", target_proxy_port)
                self.dashboard.settings.update_setting("game_port", target_game_port)
            else:
                target_host = "127.0.0.1"
                target_proxy_port = PROXY_PORT
                target_game_port = 4999
                # Reset to defaults in settings? Or just leave them. Best to save active choice.
                self.dashboard.settings.update_setting("proxy_port", PROXY_PORT)
                self.dashboard.settings.update_setting("game_port", 4999)

            proxy_payload = {
                "ollama_host": target_host,
                "ollama_port": target_proxy_port,
                "port": target_game_port, 
                "llm_service": "Ollama", # Force mode
                "llm_model": self.combo_model.get()
            }
            
            # --- AUTO-DETECT MOD ROOT (Fix for Missing Subtitles) ---
            # Default fallback
            target_mod_root = r"C:\Modding\MO2\Skyrim\mods\Mantella"
            
            # Try to derive from Mantella EXE location
            # Structure: .../Data/SKSE/Plugins/MantellaSoftware/Mantella.exe
            # We want:   .../Data/
            mantella_exe = TARGETS["Mantella"]["found"]
            if mantella_exe and os.path.exists(mantella_exe):
                try:
                    # Stair-step up 4 levels
                    d1 = os.path.dirname(mantella_exe) # MantellaSoftware
                    d2 = os.path.dirname(d1)           # Plugins
                    d3 = os.path.dirname(d2)           # SKSE
                    target_mod_root = os.path.dirname(d3) # Data / ModRoot
                    self.dashboard.log_write(f"[CONFIG] Auto-Detected Mod Root: {target_mod_root}")
                except Exception as e:
                     self.dashboard.log_write(f"[WARN] Path Detection Failed: {e}")

            proxy_payload["mod_root"] = target_mod_root
            
            # --- GET PLAYER DESCRIPTION ---
            raw_desc = self.txt_player_desc.get("1.0", "end-1c")
            if "Example:" in raw_desc: raw_desc = "" # Don't save placeholder
            # Sanitize (remove crazy newlines for ini safety if needed, though injector handles it)
            raw_desc = raw_desc.replace("\n", " ").strip()
            proxy_payload["player_description"] = raw_desc

            # Re-inject proxy settings (Quick double-tap)

            # Re-inject proxy settings (Quick double-tap)
            success = safe_injector.inject_safely(self.config_file, proxy_payload, log_callback=None)
            
            # --- DUAL INJECTION SUPPORT (DOCS FOLDER) ---
            # Fix for Mantella reading from My Games instead of local folder
            try:
                docs_path = os.path.join(os.path.expanduser("~"), "Documents", "My Games", "Mantella", "config.ini")
                if os.path.exists(docs_path) or os.path.exists(os.path.dirname(docs_path)):
                    self.dashboard.log_write("[SYSTEM] Detected secondary config in Documents. Injecting...")
                    safe_injector.inject_safely(docs_path, proxy_payload, log_callback=None)
            except Exception as e:
                self.dashboard.log_write(f"[WARN] Secondary Injection Failed: {e}", "error")

            if success:
                 self.dashboard.log_write("Config.ini is now ready for inspection") # RESTORED HYPERLINK TRIGGER
            else:
                 self.dashboard.log_write("[FAIL] Config Injection Failed.", "error")

            # --- HYPERLINK RESTORED HERE ---
            self.dashboard.log_write(f"Target Configured for Proxy Mode.")
            self.dashboard.settings.update_setting("game_mode", selected_game) # Remember choice
            self.on_save(); self.destroy()

    def _async_load_models(self):
        # 1. Ensure Service is Alive (Auto-Spawn / Retry)
        if not ollama_mgr.OllamaManager.ensure_running():
             self.dashboard.after(0, lambda: self.combo_model.set("Ollama Not Detected"))
             return

        # 2. Get Models
        models = ollama_mgr.OllamaManager.scan_local_manifests()
        
        def _update_combos():
            try:
                if models:
                    self.combo_model.configure(values=models)
                    self.combo_model.set(models[0])
                else:
                    self.combo_model.set("No Models Found (Run: ollama pull llama3)")
                
                # Also update vision combo if it exists
                if hasattr(self, 'combo_vision'):
                    vision_candidates = [m for m in models if "vision" in m or "llava" in m] if models else []
                    vision_vals = vision_candidates if vision_candidates else ["(No Vision Models Detected)"]
                    self.combo_vision.configure(values=vision_vals)
                    if vision_candidates: self.combo_vision.set(vision_candidates[0])
                    else: self.combo_vision.set("llava:latest")
            except: pass

        try: self.dashboard.after(0, _update_combos)
        except: pass