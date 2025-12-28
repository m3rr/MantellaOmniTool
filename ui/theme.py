# ui/theme.py
# h4 Mantella Omni Tool - Theme Definitions

# Branding
APP_TITLE = "h4 - Mantella Omni Tool (v1.0b)"
ASCII_BANNER = r"""
  _       _  _         
 | |__   | || |        
 | '_ \  | || |_       
 | | | | |__   _|      
 |_| |_|    |_|        
                       
  MANTELLA OMNI-TOOL   
"""

# Nuclear Palette (Revised)
COL_BG = "#1a1a1a"         # Rich Charcoal (Matches Splash)
COL_PANEL = "#1a1a1a"      # Subtle separation
COL_ACCENT = "#00ff99"     # Cyber Green
COL_TEXT = "#ffffff"       # Pure White
COL_TEXT_DIM = "#bbbbbb"   # Lighter Grey for readability
COL_BTN_BORDER = "#00ff99" 
COL_BTN_HOVER = "#00331f"
COL_DISABLED = "#555555"   # Much lighter grey for disabled states
COL_ERR = "#ff3333"
COL_WARN = "#ffcc00"
COL_TOOLTIP_BG = "#202020"

# DYNAMIC THEME COLORS
THEME_CYCLE = [
    ("#00ff99", "#00331f"), # Cyber Green
    ("#00ccff", "#002244"), # Electric Blue
    ("#ff00ff", "#440044"), # Cyberpunk Pink
    ("#ff9900", "#442200"), # Industrial Orange
    ("#ff3333", "#330000"), # Crimson Red
    ("#cc00ff", "#220044"), # Deep Purple
    ("#ffff00", "#333300"), # Hazard Yellow
]
THEME_INDEX = 0

# Active Vars
COL_ACCENT = THEME_CYCLE[0][0]
COL_BTN_BORDER = THEME_CYCLE[0][0]
COL_BTN_HOVER = THEME_CYCLE[0][1]

# Typography
FONT_LOGO = ("Consolas", 60, "bold")
FONT_HEADER = ("Consolas", 22, "bold")
FONT_TITLE = ("Consolas", 16, "bold")
FONT_BTN = ("Consolas", 14, "bold")
FONT_TEXT = ("Consolas", 13)
FONT_STATUS = ("Consolas", 12)
FONT_TOOLTIP = ("Consolas", 11)