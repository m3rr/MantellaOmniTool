# ui/compendium.py
import customtkinter as ctk
import tkinter as tk
import ui.theme as theme
import re
import os

class CompendiumPopup(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("h4 Compendium")
        self.geometry("900x800") # Slightly wider for the art
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        
        # --- ICON LOGIC ---
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_dir, "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.after(200, lambda: self.iconbitmap(icon_path))
        except:
            pass
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(header, text="THE COMPENDIUM", font=theme.FONT_HEADER, text_color=theme.COL_ACCENT).pack(side="left")
        
        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.perform_search)
        self.entry_search = ctk.CTkEntry(header, placeholder_text="Search protocols...", width=200, textvariable=self.search_var, font=theme.FONT_TEXT)
        self.entry_search.pack(side="right")

        # Content Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # --- CONTENT AREA (Using tk.Text for Rich Font Support) ---
        self.textbox = tk.Text(
            container, 
            bg="#101010", 
            fg="#dddddd", 
            font=("Consolas", 11), # Slightly smaller font for ASCII art fitting
            wrap="word", 
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground="white"
        )
        self.textbox.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scroll = ctk.CTkScrollbar(container, command=self.textbox.yview)
        scroll.pack(side="right", fill="y")
        self.textbox.configure(yscrollcommand=scroll.set)
        
        # Define Markdown Tags
        self.textbox.tag_config("h1", font=("Consolas", 20, "bold"), foreground=theme.COL_ACCENT, spacing3=10)
        self.textbox.tag_config("h2", font=("Consolas", 16, "bold"), foreground="#ffffff", spacing3=5)
        self.textbox.tag_config("bold", font=("Consolas", 11, "bold"), foreground="#ffffff")
        self.textbox.tag_config("italic", font=("Consolas", 11, "italic"))
        self.textbox.tag_config("quote", font=("Consolas", 11, "italic"), foreground=theme.COL_TEXT_DIM, lmargin1=20, lmargin2=20)
        self.textbox.tag_config("list", lmargin1=20, lmargin2=30)
        self.textbox.tag_config("separator", foreground=theme.COL_DISABLED, justify="center")
        self.textbox.tag_config("highlight", background=theme.COL_ACCENT, foreground="black")

        # Render Content
        content = self.load_readme()
        self.render_markdown(content)
        self.textbox.configure(state="disabled")

    def load_readme(self):
        """Dynamic Loader: Reads README.md from project root."""
        try:
            # ui/compendium.py -> ui -> root
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            readme_path = os.path.join(root_dir, "README.md")
            
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return "# ERROR\n\nREADME.md not found in application root."
        except Exception as e:
            return f"# ERROR\n\nCould not load Compendium:\n{e}"

    def render_markdown(self, text):
        lines = text.split("\n")
        
        for line in lines:
            tag = None
            content = line
            
            if line.startswith("# "):
                tag = "h1"
                content = line[2:]
            elif line.startswith("## "):
                tag = "h2"
                content = line[3:]
            elif line.startswith("> "):
                tag = "quote"
                content = line[2:]
            elif line.strip().startswith("* ") or line.strip().startswith("- "):
                tag = "list"
            elif line.strip() == "---":
                tag = "separator"
                content = "────────────────────────────────────────"

            start_index = self.textbox.index("insert")
            self.textbox.insert("end", content + "\n")
            end_index = self.textbox.index("insert")
            
            if tag:
                self.textbox.tag_add(tag, start_index, end_index)

        self.highlight_pattern(r"\*\*(.*?)\*\*", "bold")

    def highlight_pattern(self, pattern, tag):
        start = "1.0"
        while True:
            pos_start = self.textbox.search("**", start, stopindex="end")
            if not pos_start: break
            
            pos_end = self.textbox.search("**", f"{pos_start}+2c", stopindex="end")
            if not pos_end: break
            
            self.textbox.delete(pos_start, f"{pos_start}+2c")
            pos_end = self.textbox.search("**", pos_start, stopindex="end")
            self.textbox.delete(pos_end, f"{pos_end}+2c")
            
            self.textbox.tag_add(tag, pos_start, pos_end)
            start = pos_end

    def perform_search(self, *args):
        query = self.search_var.get().lower()
        self.textbox.tag_remove("highlight", "1.0", "end")
        
        if not query: return

        start = "1.0"
        while True:
            pos = self.textbox.search(query, start, stopindex="end", nocase=True)
            if not pos: break
            
            end = f"{pos}+{len(query)}c"
            self.textbox.tag_add("highlight", pos, end)
            start = end