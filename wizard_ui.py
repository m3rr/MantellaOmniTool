import customtkinter as ctk
import os
import ui.theme as theme
from h4_managers import SettingsManager
from ui.components import GlowingButton
from ui.window_utils import center_window, apply_icon, force_taskbar_visibility

class WizardWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        
        apply_icon(self)
        self.on_close_callback = on_close_callback
        self.title("h4 Omni Tool - Setup")
        
        # Geometry & Taskbar
        self.geometry("600x500") 
        center_window(self, 600, 500)
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        self.overrideredirect(True) # Borderless
        
        force_taskbar_visibility(self)


        self.step = 0
        self.settings = SettingsManager()
        self.selected_game = ctk.StringVar(value="SkyrimSE")

        # UI Container
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.pack(expand=True, fill="both", padx=20, pady=20)

        self.setup_step_0()

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    # --- STEP 0: GAME SELECTION ---
    def setup_step_0(self):
        self.clear_frame()
        
        ctk.CTkLabel(self.frame, text="INITIAL CONFIGURATION", font=theme.FONT_HEADER, text_color=theme.COL_ACCENT).pack(pady=(20, 10))
        ctk.CTkLabel(self.frame, text="Select your Target Game Protocol:", font=theme.FONT_TEXT).pack(pady=10)

        btn_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        def set_game(game):
            self.selected_game.set(game)
            self.next_step()

        # SKYRIM
        GlowingButton(btn_frame, text="SKYRIM SE / AE", width=250, height=50, command=lambda: set_game("SkyrimSE")).pack(pady=5)
        GlowingButton(btn_frame, text="SKYRIM VR", width=250, height=50, command=lambda: set_game("SkyrimVR")).pack(pady=5)
        
        # FALLOUT
        GlowingButton(btn_frame, text="FALLOUT 4", width=250, height=50, border_color="#ffaa00", text_color="#ffaa00", command=lambda: set_game("Fallout4")).pack(pady=5)
        GlowingButton(btn_frame, text="FALLOUT 4 VR", width=250, height=50, border_color="#ffaa00", text_color="#ffaa00", command=lambda: set_game("Fallout4VR")).pack(pady=5)

    def next_step(self):
        self.settings.update_setting("game_mode", self.selected_game.get())
        
        self.clear_frame()
        ctk.CTkLabel(self.frame, text="CONFIGURATION LOCKED", font=theme.FONT_HEADER, text_color=theme.COL_ACCENT).pack(pady=(40, 20))
        ctk.CTkLabel(self.frame, text=f"Target: {self.selected_game.get()}", font=("Consolas", 14, "bold")).pack(pady=10)
        ctk.CTkLabel(self.frame, text="The system will now initialize the Dashboard.", font=theme.FONT_TEXT).pack(pady=20)
        
        GlowingButton(self.frame, text="ENTER SYSTEM", width=200, height=50, command=self.finish).pack(pady=40)

    def finish(self):
        # 1. Write the flag to disk
        self.settings.update_setting("first_run", False)
        
        # 2. Destroy the window. 
        self.destroy()