import customtkinter as ctk
import ctypes
import os
import sys

def force_taskbar_visibility(window):
    """
    Forces a frameless window (overrideredirect=True) to appear in the Taskbar and Alt-Tab.
    """
    def _force():
        try:
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            
            # Get the HWND. For CTk/Tk, typically we need the parent of the inner frame for overrideredirect
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            
            # If GetParent returns 0, use the window id directly
            if hwnd == 0:
                hwnd = window.winfo_id()
                
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            
            # Toggle visibility to refresh style
            window.withdraw()
            window.deiconify()
        except Exception as e:
            print(f"Taskbar Force Error: {e}")
            
    # Small delay to ensure window handle is ready
    window.after(100, _force)

def center_window(window, width, height):
    """
    Centers the window on the screen.
    """
    try:
        container_width = window.winfo_screenwidth()
        container_height = window.winfo_screenheight()
        x = (container_width // 2) - (width // 2)
        y = (container_height // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")
    except: pass

def apply_icon(window):
    """
    Applies the application icon to the window.
    Asserts AUMID and aggressively sets iconbitmap.
    """
    try:
        # 1. Enforce AppUserModelID (Critical for Taskbar Grouping)
        myappid = 'h4.mantella.omnitool.v6' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # 2. Locate Icon
        if hasattr(sys, 'frozen'):
            base_dir = sys._MEIPASS
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_dir = os.path.dirname(current_dir)
            
        icon_path = os.path.join(base_dir, "assets", "icon.ico")
        
        if os.path.exists(icon_path):
            # 3. Apply Immediately (Aggressive Mode)
            # Use 'default' to persist across dialogs
            try: window.wm_iconbitmap(default=icon_path) 
            except: window.iconbitmap(icon_path)

            # 4. Refresh Title (Forces WM update)
            # window.title(window.title())
            
            # 5. Apply Deferred (Catch-all for slow WM or CTk override)
            def _refresh_icon():
                try: window.iconbitmap(icon_path)
                except: pass
            
            window.after(200, _refresh_icon)
            
    except Exception as e:
        # User reported "Silence" - let's make the error LOUD.
        # Only show this if we are frozen (end user), otherwise dev console is fine.
        if hasattr(sys, 'frozen'):
            ctypes.windll.user32.MessageBoxW(0, f"Icon Load Failed:\n{e}\nPath: {icon_path if 'icon_path' in locals() else 'Unknown'}", "Icon Error", 0x10)
        else:
            print(f"Icon Error: {e}")
