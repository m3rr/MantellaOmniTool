"""
h4 Mantella Omni Tool - __init__.py
Module: core
"""
# core/__init__.py

# Network Constants
PROXY_HOST = '127.0.0.1'
PROXY_PORT = 5001 # Changed from 5000 to avoid conflict with Mantella.exe
OLLAMA_PORT = 11434
OLLAMA_BASE = f'http://localhost:{OLLAMA_PORT}'

# File System Constants
# NUCLEAR OPTION: Minimized Blacklist.
# We REMOVED "AppData" (Where Ollama lives) and "Program Files" (Where Games live).
# We only skip OS-level infinite loops or massive system dumps.
BLACKLIST_DIRS = {
    "$RECYCLE.BIN", 
    "System Volume Information", 
    "Config.Msi", 
    "Windows", 
    "node_modules", 
    ".git",
    "__pycache__",
    
    # SYSTEM IRRELEVANCE (Speed Optimization)
    "ProgramData", # Mostly MS/System configs
    "Common Files",
    
    # APPDATA TRASH (The real bottlenecks)
    "Temp",
    "Google", "Mozilla", "Microsoft", "BraveSoftware",
    "Packages", # Windows Store Apps (Restricted access anyway)
    "nvidia", "intel", "amd" # Driver caches
}

# The Hunter's Target List
TARGETS = {
    "Mantella":     {"file": "Mantella.exe", "type": "dir", "found": None, "candidates": []},
    "xVASynth":     {"file": "xVASynth.exe", "type": "dir", "found": None, "candidates": []},
    
    # ELDER SCROLLS
    "SkyrimVR":     {"file": "SkyrimVR.exe", "type": "dir", "found": None, "candidates": []},
    "SkyrimSE":     {"file": "SkyrimSE.exe", "type": "dir", "found": None, "candidates": []},
    
    # FALLOUT
    "Fallout4":     {"file": "Fallout4.exe", "type": "dir", "found": None, "candidates": []},
    "Fallout4VR":   {"file": "Fallout4VR.exe", "type": "dir", "found": None, "candidates": []},

    # TOOLS
    "ModOrganizer": {"file": "ModOrganizer.exe", "type": "exe", "found": None, "candidates": []},
    "Vortex":       {"file": "Vortex.exe", "type": "exe", "found": None, "candidates": []},
    "Ollama":       {"file": "ollama.exe", "type": "exe", "found": None, "candidates": []},
    
    # CRITICAL DEPENDENCIES
    "PapyrusUtil":  {"file": "PapyrusUtil.dll", "type": "dll", "found": None, "candidates": []},
    
    # FIX: Corrected typo "uiaxtensions" -> "UIExtensions"
    "UIExtensions": {"file": "UIExtensions.esp", "type": "esp", "found": None, "candidates": []},
    
    "SkyUI_SE":     {"file": "SkyUI_SE.esp",    "type": "esp", "found": None, "candidates": []},
    
    # ADDRESS LIBRARY (Pattern Match)
    "Address Library": {"file": "versionlib-", "type": "pattern", "found": None, "candidates": []},
    
    "Models":       {"file": "manifests", "type": "special", "found": None}
}