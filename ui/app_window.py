import customtkinter as ctk
import logging
from ui.frames import HeaderFrame, LandingFrame, DownloadFrame, DashboardFrame
from ui.compendium import CompendiumPopup
import ui.theme as theme
from ui.window_utils import center_window, apply_icon, force_taskbar_visibility

class h4App(ctk.CTk):
    def __init__(self, settings_manager, logger):
        super().__init__()

        self.settings = settings_manager
        self.logger = logger
        self.debug_mode = self.settings.get_setting("debug_mode") 
        
        # Window Setup
        self.title("Mantella Omni-Tool")
        self.geometry("900x600")
        self.overrideredirect(True) # Frameless
        self.resizable(False, False)
        self.configure(fg_color=theme.COL_BG) # Consistency
        
        # Taskbar Logic
        force_taskbar_visibility(self)
        apply_icon(self)
        
        # Grid Configuration
        self.grid_rowconfigure(1, weight=1) # Main Content Area
        self.grid_columnconfigure(0, weight=1) # Single Column

        # State
        self.frames = {}
        self.current_frame = None

        # UI Initialization
        self.setup_ui()
        center_window(self, 900, 600)
        
        # Input Bindings for Dragging (Window level)
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

    def setup_ui(self):
        # 1. Header (Top)
        self.header = HeaderFrame(self, 
                                  title="MANTELLA OMNI-TOOL", 
                                  close_cmd=self.close_app, 
                                  min_cmd=self.minimize_window)
        self.header.grid(row=0, column=0, sticky="ew")

        # 2. Main Container (Single Window View)
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Make the container expandable
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Initialize Pages
        self.init_frames()

        # Start at Landing OR Dashboard if we have memory
        scan_cache = self.settings.get_setting("_scan_cache")
        if scan_cache and len(scan_cache) > 0:
            self.logger.info("Previous scan data found. Bypassing Landing.")
            self.show_frame("DashboardFrame")
        else:
            self.show_frame("LandingFrame")

    def init_frames(self):
        for F in (LandingFrame, DownloadFrame, DashboardFrame):
            page_name = F.__name__
            frame = F(master=self.container, controller=self)
            self.frames[page_name] = frame
            # Stack them all on top of each other
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, frame_name):
        self.logger.info(f"Navigating to {frame_name}")
        
        if frame_name not in self.frames:
            self.logger.error(f"Frame {frame_name} not found!")
            return

        frame = self.frames[frame_name]
        frame.tkraise() # Bring to front
        self.current_frame = frame_name
            
    # --- LOG WIDGET REGISTRATION (Interface for Frames) ---
    def register_log_widget(self, widget):
        pass 

    def minimize_window(self):
        try:
            self.withdraw() 
            self.overrideredirect(False) 
            self.iconify() 
            self.update_idletasks() 
            self.bind("<Map>", self.on_deiconify) 
        except Exception as e:
            self.logger.error(f"Minimize Crash Averted: {e}")

    def on_deiconify(self, event):
        if self.state() == 'normal':
            self.overrideredirect(True) 
            self.unbind("<Map>") 

        # Protocol Handling
        self.protocol("WM_DELETE_WINDOW", self.close_app)

    def close_app(self):
        self.logger.info("Application Shutdown Initiated.")
        
        # 0. AGGRESSIVE CLEANUP: Cancel ALL pending Tcl/Tk callbacks
        # This prevents "invalid command name" errors from ghost threads (like check_dpi_scaling)
        try:
            # Get list of all pending after IDs
            after_ids = self.tk.call('after', 'info')
            if after_ids:
                # after_ids is a space-separated string or tuple depending on version
                if isinstance(after_ids, str):
                    ids = after_ids.split()
                else:
                    ids = after_ids
                
                for aid in ids:
                    try: self.after_cancel(aid)
                    except: pass
        except Exception as e:
            self.logger.debug(f"Cleanup Loop Error: {e}")

        # 1. Cleanup Frames
        for frame in self.frames.values():
            if hasattr(frame, 'destroy'):
                try: frame.destroy()
                except: pass
        
        # 3. Terminate Child Processes (The "Triple Check")
        try:
            from core.ollama_mgr import OllamaManager
            OllamaManager.shutdown()
        except: pass

        # 4. Kill Window
        try:
            self.quit()
            self.destroy()
        except: pass
        
        # 5. NUCLEAR EXIT (Scorched Earth)
        # sys.exit() can be blocked by non-daemon threads or join() calls.
        # os._exit() kills the process immediately at the OS level.
        import os
        os._exit(0)

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        if self.x is None or self.y is None: return
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")