import customtkinter as ctk
import ui.theme as theme
from tkinter import Toplevel, Label

class HoverTooltip:
    """
    A lightweight, theme-aware tooltip that appears on hover.
    Compatible with CustomTkinter widgets.
    """
    def __init__(self, widget, text, wait_time=500, wraplength=300):
        self.widget = widget
        self.text = text
        self.wait_time = wait_time
        self.wraplength = wraplength
        
        self.tooltip_window = None
        self.id = None
        
        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.unschedule)
        self.widget.bind("<ButtonPress>", self.unschedule)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.wait_time, self.show)

    def unschedule(self, event=None):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)
        self.hide()

    def show(self):
        # 1. Get Coordinates
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        
        # 2. Create Frameless Window
        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # 3. Apply Styling (Simulate CTk Frame with standard Tk Label)
        # Why not CTkLabel? Toplevel can sometimes fight with CTk scaling in sub-windows.
        # Standard Label gives us exact pixel control for borders.
        
        label = Label(self.tooltip_window, 
                      text=self.text, 
                      justify='left',
                      background="#1a1a1a", # Hardcoded Dark Grey
                      foreground="#ffffff", # Hardcoded White
                      relief='solid', 
                      borderwidth=1,
                      wraplength=self.wraplength,
                      font=("Segoe UI", 10),
                      padx=8, pady=6)
        
        label.pack()

    def hide(self):
        tw = self.tooltip_window
        self.tooltip_window = None
        if tw:
            tw.destroy()
