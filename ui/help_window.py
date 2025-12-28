import customtkinter as ctk
import os
import sys
import ui.theme as theme
from ui.window_utils import apply_icon # Reuse icon logic

class HelpWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("The Definitive Compendium")
        self.geometry("900x700")
        self.configure(fg_color=theme.COL_BG)
        self.attributes("-topmost", True)
        
        # Icon
        try:
            if hasattr(sys, 'frozen'):
                 root_dir = sys._MEIPASS
            else:
                 current_dir = os.path.dirname(os.path.abspath(__file__))
                 root_dir = os.path.dirname(current_dir)
                 
            icon_path = os.path.join(root_dir, "assets", "icon.ico")
            if os.path.exists(icon_path): self.after(200, lambda: self.iconbitmap(icon_path))
        except: pass

        # Header
        self.lbl_title = ctk.CTkLabel(self, text="THE OMNI-GRIMOIRE", font=("Consolas", 24, "bold"), text_color=theme.COL_ACCENT)
        self.lbl_title.pack(pady=(20, 10))
        
        ctk.CTkLabel(self, text="Knowledge is Power. Troubleshooting is Survival.", font=theme.FONT_TEXT, text_color="gray").pack(pady=(0, 20))

        # Search Bar
        self.frame_search = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_search.pack(fill="x", padx=40, pady=(0, 10))
        self.entry_search = ctk.CTkEntry(self.frame_search, placeholder_text="Search the archives...", width=300)
        self.entry_search.pack(side="right")
        self.entry_search.bind("<KeyRelease>", self.filter_content)
        ctk.CTkLabel(self.frame_search, text="SEARCH:", font=("Consolas", 12, "bold")).pack(side="right", padx=10)

        # Content Area
        self.txt_content = ctk.CTkTextbox(self, font=("Consolas", 12), wrap="word")
        self.txt_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Load Data
        self.full_content = self.load_readme()
        self.render_markdown(self.full_content)
        
        # Close Button
        ctk.CTkButton(self, text="CLOSE ARCHIVE", command=self.destroy, fg_color=theme.COL_WARN, hover_color="#550000").pack(pady=20)

    def load_readme(self):
        try:
            if hasattr(sys, 'frozen'):
                 root_dir = sys._MEIPASS
            else:
                 # We assume README.md is in the root (one level up from ui/)
                 current_dir = os.path.dirname(os.path.abspath(__file__))
                 root_dir = os.path.dirname(current_dir)
            
            readme_path = os.path.join(root_dir, "README.md")
            
            if os.path.exists(readme_path):
                with open(readme_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return "# ERROR\nREADME.md not found in root directory."
        except Exception as e:
            return f"# CRITICAL ERROR\nCould not load documentation: {e}"

    def render_markdown(self, text):
        self.txt_content.configure(state="normal")
        self.txt_content.delete("1.0", "end")
        
        # Configure tags for styling
        self.txt_content.tag_config("h1", foreground=theme.COL_ACCENT)
        self.txt_content.tag_config("h2", foreground=theme.COL_TEXT)
        self.txt_content.tag_config("h3", foreground=theme.COL_TEXT_DIM)
        self.txt_content.tag_config("code", foreground=theme.COL_ACCENT, background="#2b2b2b")
        self.txt_content.tag_config("quote", foreground=theme.COL_TEXT_DIM)
        self.txt_content.tag_config("normal", foreground=theme.COL_TEXT)
        self.txt_content.tag_config("list", foreground=theme.COL_TEXT, lmargin1=20, lmargin2=20)
        
        lines = text.split("\n")
        in_code_block = False
        
        for line in lines:
            tag = "normal"
            content = line
            
            # --- Code Block Handling ---
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue # Skip the marker line
            
            if in_code_block:
                self.txt_content.insert("end", line + "\n", "code")
                continue

            # --- Headers ---
            if line.startswith("# "):
                tag = "h1"
                content = line[2:].upper() # Make H1 uppercase
            elif line.startswith("## "):
                tag = "h2"
                content = line[3:]
            elif line.startswith("### "):
                tag = "h3"
                content = line[4:]
            
            # --- Quotes ---
            elif line.startswith("> "):
                tag = "quote"
                content = "│ " + line[2:]
            
            # --- Lists ---
            elif line.strip().startswith("- ") or line.strip().startswith("* "):
                tag = "list"
                content = "• " + line.strip()[2:]
            elif line.strip().startswith("1. "):
                tag = "list"
                # Keep numbering but indent
                content = "  " + line.strip()

            # --- Inline Formatting Stripping (The "Cleaner") ---
            # Remove **bold** markers
            content = content.replace("**", "").replace("__", "")
            # Remove *italic* markers (careful with bullet points, but we handled those above)
            # content = content.replace("*", "") # Too aggressive? Maybe just leave asterisks.
            # Remove link brackets [text](url) -> text (url)
            import re
            content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', content)
            
            self.txt_content.insert("end", content + "\n", tag)
                
        self.txt_content.configure(state="disabled")

    def filter_content(self, event=None):
        query = self.entry_search.get().lower()
        if not query:
            self.render_markdown(self.full_content)
            return
            
        # Basic Filter: Show relevant sections
        # This is hard to do perfectly with Markdown structure, so lets just highlight matches for now to keep it robust
        self.render_markdown(self.full_content)
        
        # Highlight logic
        self.txt_content.configure(state="normal")
        self.txt_content.tag_remove("found", "1.0", "end")
        
        if query:
            idx = "1.0"
            while True:
                idx = self.txt_content.search(query, idx, nocase=1, stopindex="end")
                if not idx: break
                lastidx = f"{idx}+{len(query)}c"
                self.txt_content.tag_add("found", idx, lastidx)
                idx = lastidx
            self.txt_content.tag_config("found", background="yellow", foreground="black")
            
        self.txt_content.configure(state="disabled")
