# ui/components.py
import customtkinter as ctk
import ui.theme as theme
import webbrowser
import os

def apply_icon(window):
    """Universal Icon Injector"""
    try:
        # Resolve Root from ui/components.py -> ui -> root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        icon_path = os.path.join(root_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            window.after(200, lambda: window.iconbitmap(icon_path))
    except: pass

class CTkTooltip:
    def __init__(self, widget, text, delay=300):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.unschedule)
        self.widget.bind("<ButtonPress>", self.unschedule)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show)

    def unschedule(self, event=None):
        id = self.id
        self.id = None
        if id: self.widget.after_cancel(id)
        self.hide()

    def show(self):
        if self.tooltip_window or not self.text: return
        try:
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        except: return
        
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes('-topmost', True)

        frame = ctk.CTkFrame(self.tooltip_window, fg_color=theme.COL_TOOLTIP_BG, border_width=1, border_color=theme.COL_ACCENT)
        frame.pack()
        ctk.CTkLabel(frame, text=self.text, font=theme.FONT_TOOLTIP, text_color=theme.COL_TEXT, justify="left", padx=10, pady=5).pack()

    def hide(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class GlowingButton(ctk.CTkButton):
    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", theme.COL_BG)
        kwargs.setdefault("border_width", 2)
        if "border_color" not in kwargs: kwargs["border_color"] = theme.COL_BTN_BORDER
        if "hover_color" not in kwargs: kwargs["hover_color"] = theme.COL_BTN_HOVER
        kwargs.setdefault("text_color", theme.COL_TEXT)
        kwargs.setdefault("font", theme.FONT_BTN)
        
        # Safety for duplicate args
        if "fg_color" in kwargs and kwargs["fg_color"] == theme.COL_BG:
             pass 
             
        super().__init__(master, **kwargs)

class SelectionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, options, callback):
        super().__init__(parent)
        apply_icon(self) # <--- ICON FIX
        self.callback = callback
        self.title("Conflict Resolution")
        self.geometry("600x300")
        self.resizable(False, False)
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 300
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 150
            self.geometry(f"+{x}+{y}")
        except: pass

        ctk.CTkLabel(self, text=f"MULTIPLE CANDIDATES: {title}", font=theme.FONT_HEADER, text_color=theme.COL_WARN).pack(pady=(20, 10))
        ctk.CTkLabel(self, text="Please select the correct installation:", font=theme.FONT_TEXT, text_color=theme.COL_TEXT_DIM).pack(pady=5)

        self.selected_val = ctk.StringVar(value=options[0])
        self.combo = ctk.CTkComboBox(self, values=options, variable=self.selected_val, width=550, height=30, font=("Consolas", 11))
        self.combo.pack(pady=30, padx=20)

        GlowingButton(self, text="CONFIRM SELECTION", width=200, height=40, fg_color=theme.COL_ACCENT, text_color="black", command=self.confirm).pack(pady=10)
        self.grab_set()

    def confirm(self):
        choice = self.selected_val.get()
        if self.callback: self.callback(choice)
        self.destroy()

class ComponentManagerDialog(ctk.CTkToplevel):
    def __init__(self, parent, name, current_path, candidates, on_change_callback):
        super().__init__(parent)
        apply_icon(self) # <--- ICON FIX
        self.name = name
        self.callback = on_change_callback
        self.candidates = candidates if candidates else []
        
        self.title(f"MANAGE: {name.upper()}")
        self.geometry("600x450")
        self.resizable(False, False)
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        
        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 300
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 225
            self.geometry(f"+{x}+{y}")
        except: pass

        ctk.CTkLabel(self, text=f"MANAGE {name.upper()}", font=theme.FONT_HEADER, text_color=theme.COL_ACCENT).pack(pady=(20, 10))
        
        path_frame = ctk.CTkFrame(self, fg_color=theme.COL_PANEL)
        path_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(path_frame, text="CURRENT ACTIVE PATH:", font=("Consolas", 10, "bold"), text_color=theme.COL_TEXT_DIM).pack(anchor="w", padx=10, pady=(5,0))
        
        display_path = str(current_path) if current_path else "Not Set"
        if len(display_path) > 65: display_path = "..." + display_path[-60:]
        ctk.CTkLabel(path_frame, text=display_path, font=("Consolas", 11), text_color=theme.COL_TEXT).pack(anchor="w", padx=10, pady=(0,5))

        if len(self.candidates) > 1:
            cand_frame = ctk.CTkFrame(self, fg_color="transparent", border_width=1, border_color=theme.COL_DISABLED)
            cand_frame.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(cand_frame, text=f"⚠ DETECTED {len(self.candidates)} ALTERNATE VERSIONS", text_color=theme.COL_WARN, font=("Consolas", 11, "bold")).pack(pady=5)
            self.cand_var = ctk.StringVar(value=self.candidates[0])
            self.combo = ctk.CTkComboBox(cand_frame, values=self.candidates, variable=self.cand_var, width=500, font=("Consolas", 11))
            self.combo.pack(pady=5)
            GlowingButton(cand_frame, text="SWITCH TO SELECTED", height=30, width=200, command=self.apply_switch).pack(pady=10)
        
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=20)
        GlowingButton(action_frame, text="OPEN FOLDER", border_color=theme.COL_ACCENT, width=220, height=50, command=self.open_folder).grid(row=0, column=0, padx=10)
        GlowingButton(action_frame, text="BROWSE MANUALLY...", border_color="#3B8ED0", width=220, height=50, command=self.browse_manual).grid(row=0, column=1, padx=10)
        ctk.CTkButton(self, text="Close", fg_color="transparent", text_color=theme.COL_TEXT_DIM, command=self.destroy).pack(side="bottom", pady=10)
        self.grab_set()

    def apply_switch(self):
        new_path = self.cand_var.get()
        self.callback("SWITCH", new_path)
        self.destroy()

    def open_folder(self):
        self.callback("OPEN", None)

    def browse_manual(self):
        self.attributes("-topmost", False)
        self.withdraw()
        self.update() 
        self.destroy()
        self.callback("BROWSE", None)

class MissingModsDialog(ctk.CTkToplevel):
    def __init__(self, parent, missing_list):
        super().__init__(parent)
        apply_icon(self) # <--- ICON FIX
        self.title("CRITICAL: MISSING COMPONENTS")
        self.geometry("600x500")
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        
        ctk.CTkLabel(self, text="SKELETON CREW CHECK FAILED", font=theme.FONT_HEADER, text_color=theme.COL_ERR).pack(pady=20)
        ctk.CTkLabel(self, text="The following mods are required for the Neural Bridge to function.\nThe system cannot detect them in your active load order.", font=theme.FONT_TEXT).pack(pady=10)
        
        scroll = ctk.CTkScrollableFrame(self, fg_color=theme.COL_PANEL)
        scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        for name, url in missing_list:
            row = ctk.CTkFrame(scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=f"MISSING: {name}", font=("Consolas", 12, "bold"), text_color=theme.COL_WARN).pack(side="left", padx=10)
            btn = ctk.CTkButton(row, text="OPEN NEXUS PAGE", width=120, height=25, fg_color=theme.COL_ACCENT, text_color=theme.COL_BG, command=lambda u=url: webbrowser.open(u))
            btn.pack(side="right", padx=10)

        ctk.CTkLabel(self, text="* URLs are scraped/cached. Verify mod names manually before downloading.", font=("Consolas", 10, "italic"), text_color=theme.COL_TEXT_DIM).pack(pady=10)
        ctk.CTkButton(self, text="ACKNOWLEDGE", command=self.destroy, fg_color=theme.COL_DISABLED).pack(pady=20)

class NavigationBar(ctk.CTkFrame):
    def __init__(self, master, command=None):
        super().__init__(master, width=70, corner_radius=0, fg_color=theme.COL_PANEL)
        self.command = command
        self.grid_propagate(False) # Fixed width

        # Simple Icons (Text based for now)
        self.btn_home = self.create_nav_btn("🏠", "LandingFrame")
        self.btn_dash = self.create_nav_btn("⚙", "DashboardFrame")
        self.btn_comp = self.create_nav_btn("📚", "Compendium") # Special case

        self.btn_home.pack(pady=(20, 10), padx=5)
        self.btn_dash.pack(pady=10, padx=5)
        ctk.CTkFrame(self, height=2, fg_color=theme.COL_DISABLED).pack(fill="x", padx=10, pady=10)
        self.btn_comp.pack(pady=10, padx=5)

    def create_nav_btn(self, icon, target):
        return ctk.CTkButton(self, text=icon, width=50, height=50, 
                           font=("Segoe UI Emoji", 24), 
                           fg_color="transparent", 
                           hover_color=theme.COL_BTN_HOVER,
                           command=lambda: self.handle_click(target))

    def handle_click(self, target):
        if self.command: self.command(target)
