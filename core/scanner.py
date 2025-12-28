# core/scanner.py
import os
import shutil
import time
import threading
import win32api
from utils.logger import get_logger
from core import TARGETS, BLACKLIST_DIRS

log = get_logger()

# Common paths to hunt for dependencies (Keep this for Splash Screen)
OLLAMA_PATHS = [
    os.path.join(os.environ["LOCALAPPDATA"], "Programs", "Ollama", "ollama.exe"),
    os.path.join(os.environ["PROGRAMFILES"], "Ollama", "ollama.exe"),
    r"C:\Ollama\ollama.exe"
]

def scan_dependencies(status_callback=None):
    """
    LIGHTWEIGHT: Only checks for critical system dependencies (Ollama).
    """
    log.info("Scanning Dependencies...")
    if status_callback: status_callback("SCAN_PROGRESS", "Checking Neural Pathways (Ollama)...")
    
    ollama_found = False
    
    # 1. Quick File Check
    for path in OLLAMA_PATHS:
        try:
            if os.path.exists(path):
                log.info(f"[DEP] Found Ollama: {path}")
                ollama_found = True
                if status_callback: status_callback("FOUND", "Ollama Detected")
                break
        except Exception as e:
            log.warning(f"Ollama Path Check Error: {e}")

    # 2. Path Check (Fallback)
    if not ollama_found:
        try:
            check = shutil.which("ollama")
            if check:
                log.info(f"[DEP] Found Ollama in PATH: {check}")
                ollama_found = True
                if status_callback: status_callback("FOUND", "Ollama (System PATH)")
        except: pass

    if not ollama_found:
        log.warning("[DEP] Ollama NOT found.")
        if status_callback: status_callback("MISSING", "Ollama Not Found")
    
    if status_callback: status_callback("DONE", "Dependency Scan Complete")
    return ollama_found

class DependencyScanner:
    def __init__(self, logger):
        self.logger = logger
    
    def scan_system(self):
        # Wrapper for the functional approach
        return scan_dependencies()


class HunterProtocol(threading.Thread):
    """
    The Nuclear Option.
    Scans drives for targets in a separate thread.
    Includes THROTTLING to prevent UI freezes.
    """
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self._stop_event = threading.Event()
        self.found_count = 0
        self.missing_count = 0
        self.last_ui_update = 0 

    def run(self):
        start_time = time.time()
        log.info("Hunter Protocol Initiated.")
        self.callback(("SCAN_LOG", "[SYSTEM] Hunter Protocol Initiated..."))

        # 1. Reset Targets
        for key in TARGETS:
            TARGETS[key]["found"] = None
            TARGETS[key]["candidates"] = [] 
            
        # 2. QUICK STRIKE (Speed Optimization)
        self._quick_scan()

        drives = self._get_drives()
        
        # 3. Main Hunt Loop
        for i, drive in enumerate(drives):
            if self._stop_event.is_set(): break
            
            # Cinematic "Mounting"
            self.callback(("SCAN_LOG", f"[SYSTEM] Mounting Drive {drive}"))
            time.sleep(0.3) 

            self._scan_drive(drive)
            
            # Cinematic "Checking next"
            if i < len(drives) - 1:
                self.callback(("SCAN_LOG", "[SYSTEM] Checking for other storage media..."))
                time.sleep(0.2)

        # 4. Check Missing / Finalize
        self._finalize_scan(start_time)

    def stop(self):
        self._stop_event.set()
        
    def _quick_scan(self):
        """Checks likely locations before the crawl."""
        self.callback(("SCAN_LOG", "[SYSTEM] Checking Common Locations..."))
        
        common_paths = [
            r"C:\Games",
            r"C:\Modding",
            r"D:\Games", 
            r"D:\Modding",
            "D:\\SteamLibrary\\steamapps\\common",
            os.path.join(os.environ.get("ProgramFiles(x86)", "C:"), "Steam", "steamapps", "common"),
            os.path.join(os.environ.get("ProgramFiles", "C:"), "Steam", "steamapps", "common"),
            os.path.join(os.environ.get("LOCALAPPDATA", "C:"), "Programs", "Ollama")
        ]
        
        # User Specific Override (The USER_REQUEST mentioned this path)
        common_paths.append(r"d:\Modding\h4_Mantella_Omni_Tool_v6")

        for path in common_paths:
            if os.path.exists(path):
                self.callback(("SCAN_RAPID", f"Quick Check: {path}"))
                self._scan_directory_flat(path)
                
    def _scan_directory_flat(self, path):
        """Non-recursive scan for quick hits."""
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.name.lower() in [t["file"].lower() for t in TARGETS.values()]:
                        target_map = {data["file"].lower(): name for name, data in TARGETS.items()}
                        if entry.name.lower() in target_map:
                            self._register_hit(target_map[entry.name.lower()], path, entry.name)
                            
                    # SPECIAL: Check one deep for Skyrim/Fallout 
                    if entry.is_dir():
                        if entry.name.lower() == "mods": # MO2 Detection
                             self.callback(("SCAN_RAPID", f"MO2 Structure: {entry.path}"))
                             self._scan_mo2_mods(entry.path)
                        elif "vortex" in entry.name.lower() and "mods" in entry.name.lower(): # Vortex Detection
                             self.callback(("SCAN_RAPID", f"Vortex Structure: {entry.path}"))
                             self._scan_vortex_mods(entry.path)
                        else:
                             self._scan_directory_recursive_limit(entry.path, depth=2)
        except: pass

    def _scan_mo2_mods(self, mods_path):
        """
        Targeted Deep Scan for MO2 'mods' folder.
        Structure: mods/<ModName>/...
        """
        try:
            with os.scandir(mods_path) as it:
                for entry in it:
                    if entry.is_dir():
                        self._scan_directory_recursive_limit(entry.path, depth=5)
        except: pass

    def _scan_vortex_mods(self, mods_path):
        """
        Targeted Deep Scan for Vortex Staging folder.
        Structure: Vortex Mods/skyrimse/<ModName>/...
        OR: Vortex Mods/<ModName>/... (depending on user config)
        We scan depth 5 to be safe.
        """
        try:
            # Vortex often organizes by GAME name first
            self._scan_directory_recursive_limit(mods_path, depth=5)
        except: pass

    def _scan_directory_recursive_limit(self, path, depth):
        if depth == 0: return
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_file():
                        target_map = {data["file"].lower(): name for name, data in TARGETS.items()}
                        if entry.name.lower() in target_map:
                            self._register_hit(target_map[entry.name.lower()], path, entry.name)
                    elif entry.is_dir():
                         self._scan_directory_recursive_limit(entry.path, depth-1)
        except: pass

    def _get_drives(self):
        try:
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]
            return drives
        except: return ["C:\\"]

    def _scan_drive(self, drive_path):
        # Create a LOWERCASE map for case-insensitive matching
        # { "mantella.exe": "Mantella", "ollama.exe": "Ollama" }
        target_map = {data["file"].lower(): name for name, data in TARGETS.items() if data.get("type") != "pattern"}

        for root, dirs, files in os.walk(drive_path, topdown=True):
            if self._stop_event.is_set(): return

            # --- OPTIMIZATION: PRUNE IGNORED DIRS ---
            # Use set lookup for O(1) speed
            dirs[:] = [d for d in dirs if d not in BLACKLIST_DIRS and not d.startswith(".")]

            # --- THROTTLED UI UPDATE ---
            now = time.time()
            if now - self.last_ui_update > 0.08:
                if files:
                    display_path = os.path.join(root, files[0])
                    if len(display_path) > 75: display_path = "..." + display_path[-72:]
                    self.callback(("SCAN_RAPID", f"{display_path}"))
                    self.last_ui_update = now

            for file in files:
                file_lower = file.lower()
                
                # 1. Exact Matches (Case Insensitive)
                if file_lower in target_map:
                    self._register_hit(target_map[file_lower], root, file)
                
                # 2. Pattern Matches (Address Library)
                elif file_lower.startswith("versionlib-") and file_lower.endswith(".bin"):
                    # Optimization: Only check for ADL if we are in an SKSE-like folder
                    if "skse" in root.lower():
                        self._register_hit("Address Library", root, file)
                
                # 3. MO2 "mods" Folder Discovery (During Scan)
                elif file_lower == "modorganizer.exe":
                    # We found the EXE, so check for a 'mods' folder next to it
                    possible_mods = os.path.join(root, "mods")
                    if os.path.exists(possible_mods):
                         self.callback(("SCAN_RAPID", f"MO2 Hub Detected: {possible_mods}"))
                         self._scan_mo2_mods(possible_mods)

                # 4. Vortex "Vortex Mods" detection is tricky via Exe but we check for common patterns
                elif file_lower == "vortex.exe":
                     # Vortex.exe is usually in AppData or Program Files, but staging is elsewhere.
                     # We can't easily infer the staging folder from the Exe location.
                     # However, we can check for a "Vortex Mods" folder in the ROOT of the drive we are currently scanning
                     drive_root = os.path.splitdrive(root)[0] + "\\"
                     checks = ["Vortex Mods", "VortexMods", "vortex_mods"]
                     for c in checks:
                         p = os.path.join(drive_root, c)
                         if os.path.exists(p):
                             self.callback(("SCAN_RAPID", f"Vortex Staging Detected: {p}"))
                             self._scan_vortex_mods(p)

    def _register_hit(self, name, root, file):
        full_path = os.path.join(root, file)
        
        # Validate (Mantella specific check)
        # Validate (Mantella specific check)
        if name == "Mantella":
             # RELAXED CHECK: If we are deep in a Mod Manager folder, we trust the hit.
             # The original check required adjacent 'Speech' or 'SKSE' folders, which might be one level down
             # in some MO2 pack structures (e.g. mods/Mantella/Root/Mantella.exe)
             is_manager_managed = "mods" in root.lower() or "vortex" in root.lower()
             
             if not is_manager_managed:
                 if not (os.path.exists(os.path.join(root, "Speech")) or 
                         os.path.exists(os.path.join(root, "SKSE"))):
                     return

        # --- CRITICAL FIX: RESPECT TYPE="DIR" ---
        # If the target is defined as a directory (like Mantella), store the ROOT, not the FILE.
        # This prevents paths like ".../Mantella.exe/config.ini"
        
        target_type = TARGETS[name].get("type", "exe")
        stored_path = root if target_type == "dir" else full_path

        # Handle Candidates
        TARGETS[name]["candidates"].append(stored_path)
        
        # If this is the FIRST time finding it, mark as found & notify user
        if TARGETS[name]["found"] is None:
            TARGETS[name]["found"] = stored_path
            self.found_count += 1
            self.callback(("FOUND", f"{name} FOUND!"))
            log.info(f"Hunter found {name} at {stored_path}")
            time.sleep(0.1) 
        else:
            # Conflict found
            # Don't spam log if we found the same folder via multiple files
            if stored_path != TARGETS[name]["found"]:
                log.info(f"Hunter found ALTERNATE {name} at {stored_path}")
                self.callback(("CONFLICT", f"{name} duplicate detected."))

    def _finalize_scan(self, start_time):
        duration = round(time.time() - start_time, 2)
        missing_list = []
        for name, data in TARGETS.items():
            if not data["found"]:
                self.missing_count += 1
                self.callback(("MISSING", name))
                if name in ["PapyrusUtil", "UIExtensions", "SkyUI_SE", "Address Library"]:
                     missing_list.append((name, "https://www.nexusmods.com/skyrimspecialedition/mods/13048")) 

        self.callback(("DONE", (self.found_count, self.missing_count, duration)))
        if missing_list: self.callback(("MISSING_MODS", missing_list))