import webview
import os
import sys
import multiprocessing
from utils.logger import get_logger

log = get_logger()

# WORKAROUND: PyInstaller + Multiprocessing Fix
# When frozen, multiprocessing tries to re-run the whole app. 
# We need to call freeze_support() in main.py, but here we just ensure the function is picklable.

def _webview_process(html_path):
    """
    Isolated process to run the WebView.
    This prevents the "Event Loop Conflict" between Tkinter and WebView (WinForms/Cocoa).
    """
    try:
        webview.create_window(
            'h4 MANTELLA CODEX', 
            url=html_path,
            width=1200, 
            height=850,
            background_color='#020617',
            text_select=True
        )
        
        # Icon Injection Strategy V2: The Win32 Hammer
        # Pywebview's native icon support can be flaky on some Windows builds.
        # We will use Win32 API to force the icon onto the window handle.
        import ctypes
        from ctypes import wintypes
        
        # 1. Resolve Path
        if hasattr(sys, '_MEIPASS'):
             icon_root = os.path.join(sys._MEIPASS, "assets")
        else:
             icon_root = os.path.join(os.getcwd(), "assets")
        icon_path = os.path.join(icon_root, "icon.ico")
        
        # 2. Define Window Finder
        def set_window_icon():
            """
            Run after the main loop starts.
            Finds the window by its title and forces the icon via Win32 API.
            """
            try:
                # Basic Wait for init
                import time
                time.sleep(0.5) 
                
                hwnd = ctypes.windll.user32.FindWindowW(None, 'h4 MANTELLA CODEX')
                
                # Retry loop for slow init
                retries = 0
                while not hwnd and retries < 10:
                    time.sleep(0.2)
                    hwnd = ctypes.windll.user32.FindWindowW(None, 'h4 MANTELLA CODEX')
                    retries += 1

                if hwnd and os.path.exists(icon_path):
                    # Load Icon
                    full_path = os.path.abspath(icon_path)
                    
                    # ICON_SMALL = 0, ICON_BIG = 1
                    # WM_SETICON = 0x0080
                    
                    # LoadImageW(hinst, name, type, cx, cy, fuLoad)
                    # Type 1 = IMAGE_ICON, Flag 0x0010 = LR_LOADFROMFILE
                    h_icon_big = ctypes.windll.user32.LoadImageW(None, full_path, 1, 0, 0, 0x0010)
                    h_icon_small = ctypes.windll.user32.LoadImageW(None, full_path, 1, 16, 16, 0x0010)
                    
                    if h_icon_big:
                        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, h_icon_big)
                    if h_icon_small:
                        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, h_icon_small)
                else:
                    print("[CODEX] Icon Injection Failed: Window not found or Icon missing.")
            except Exception as e:
                print(f"Icon Injection Failed: {e}")

        webview.start(func=set_window_icon)
    except Exception as e:
        print(f"Codex Crash: {e}")

class SystemCodex:
    @staticmethod
    def open_codex():
        """
        Launches the Codex Gigas in a separate process.
        """
        try:
            # 1. Resolve Path
            if hasattr(sys, '_MEIPASS'):
                 base_path = os.path.join(sys._MEIPASS, "assets")
            else:
                 base_path = os.path.join(os.getcwd(), "assets")
            
            html_path = os.path.join(base_path, "codex.html")
            
            if not os.path.exists(html_path):
                log.error(f"[CODEX] HTML Artifact missing at: {html_path}")
                return

            log.info(f"[CODEX] Spawning Neural Interface from: {html_path}")

            # 2. Spawn Process
            # We use multiprocessing to keep the heavy WebView memory (100MB+) 
            # separate from the main app, and to avoid GIL locking the UI.
            p = multiprocessing.Process(target=_webview_process, args=(html_path,))
            p.daemon = True # Kill if main app dies
            p.start()
            
        except Exception as e:
            log.error(f"[CODEX] Failed to launch: {e}")
