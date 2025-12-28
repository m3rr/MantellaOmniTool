import customtkinter as ctk
from PIL import Image
import os
import ui.theme as theme
from ui.window_utils import center_window, apply_icon, force_taskbar_visibility

class SplashController:
    def __init__(self, root):
        self.root = root
        
        # Window Setup
        width = 400
        height = 300
        
        self.window = ctk.CTkToplevel(self.root)
        center_window(self.window, width, height)
        self.window.overrideredirect(True) # Frameless
        self.window.attributes('-topmost', True)
        self.window.configure(fg_color="#1a1a1a") # Dark background
        
        # Enforce Taskbar visibility
        force_taskbar_visibility(self.window)
        apply_icon(self.window)

        # Logo / Image
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            logo_path = os.path.join(base_dir, "assets", "logo.png")

            if os.path.exists(logo_path):
                img_data = Image.open(logo_path)
                # Resize maintain aspect ratio if needed, but 256x256 is good
                img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(180, 180))
                self.label = ctk.CTkLabel(self.window, image=img, text="")
                self.label.pack(pady=(40, 10))
            else:
                # Fallback
                self.label = ctk.CTkLabel(self.window, text="MANTELLA\nOMNI-TOOL", 
                                        font=("Roboto", 24, "bold"),
                                        text_color=theme.COL_ACCENT)
                self.label.pack(pady=(80, 20))
        except Exception as e:
            print(f"Splash Asset Error: {e}")
            self.label = ctk.CTkLabel(self.window, text="MANTELLA", font=("Consolas", 20))
            self.label.pack(pady=50)

        # Progress Bar
        self.progress = ctk.CTkProgressBar(self.window, width=300, height=10, corner_radius=0)
        self.progress.pack(pady=10)
        self.progress.set(0)
        self.progress.start()

        # Status Label
        self.status_label = ctk.CTkLabel(self.window, text="Initializing...", 
                                       font=("Roboto", 12),
                                       text_color="gray")
        self.status_label.pack(pady=5)

        self.root.update()

    def update_status(self, text):
        """
        Updates the text below the progress bar.
        """
        try:
            self.status_label.configure(text=text)
            self.window.update_idletasks()
        except Exception:
            pass

    def close(self):
        """
        Destroys the splash window.
        """
        try:
            self.progress.stop() # Prevent bgerror
        except: pass
        self.window.destroy()