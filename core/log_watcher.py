# core/log_watcher.py
import time
import os
import threading
from pathlib import Path
from utils.logger import get_logger

log = get_logger()

class LogWatcher:
    def __init__(self):
        self.stop_event = threading.Event()
        self.threads = []
        self.callback = None
        
        # DEFINING THE TARGET LIST
        # We hunt for every relevant log file identified in the user's dump.
        self.targets = [
            # 1. The Loader (Boot process)
            {"name": "LOADER", "file": "skse64_loader.log", "subpath": "My Games/Skyrim Special Edition/SKSE"},
            # 2. The Runtime (Core SKSE)
            {"name": "SKSE",   "file": "skse64.log",        "subpath": "My Games/Skyrim Special Edition/SKSE"},
            # 3. The Network Bridge (The Plugin)
            {"name": "NET",    "file": "SKSE_HTTP.log",     "subpath": "My Games/Skyrim Special Edition/SKSE"},
            # 4. The Audio Engine (Lip Sync)
            {"name": "FUZ",    "file": "Fuz Ro D-oh.log",   "subpath": "My Games/Skyrim Special Edition/SKSE"},
            # 5. The Script Engine (The Brains - Papyrus)
            {"name": "SCR",    "file": "Papyrus.0.log",     "subpath": "My Games/Skyrim Special Edition/Logs/Script"},
            # 6. VR Support (Just in case)
            {"name": "VR",     "file": "sksevr.log",        "subpath": "My Games/Skyrim VR/SKSE"},
            # 7. Mantella Core (The Brain)
            {"name": "MANT",   "file": "logging.log",       "subpath": "My Games/Mantella"}
        ]

    def set_callback(self, func):
        self.callback = func

    def _find_log_path(self, target):
        """
        Smart-Search for log files. 
        It checks the standard 'Documents' location for various game versions.
        """
        try:
            user_docs = Path(os.path.expanduser("~")) / "Documents"
            
            # Construct candidate path based on the target definition
            # We assume the subpath in self.targets is relative to 'Documents'
            # Adjusting to handle the subpath string correctly
            
            parts = target["subpath"].split("/")
            candidate_root = user_docs
            for part in parts:
                candidate_root = candidate_root / part
            
            candidate_file = candidate_root / target["file"]
            
            if candidate_file.exists():
                return candidate_file
            
            # If not found, try the OneDrive variant (Common Windows issue)
            one_drive_docs = Path(os.path.expanduser("~")) / "OneDrive" / "Documents"
            candidate_root_od = one_drive_docs
            for part in parts:
                candidate_root_od = candidate_root_od / part
            
            candidate_file_od = candidate_root_od / target["file"]
            
            if candidate_file_od.exists():
                return candidate_file_od

            return None
        except Exception as e:
            return None

    def start(self):
        if self.callback: self.callback("[SYSTEM] Initializing Forensic Log Aggregator (Matrix Mode)...")

        self.stop_event.clear()
        
        # Launch a dedicated thread for each log target
        for target in self.targets:
            t = threading.Thread(target=self._retry_monitor_loop, args=(target,), daemon=True)
            self.threads.append(t)
            t.start()

    def stop(self):
        self.stop_event.set()
        for t in self.threads:
            t.join(timeout=0.5)

    def _retry_monitor_loop(self, target):
        """
        Continually attempts to find and attach to the log file.
        This handles cases where the game starts AFTER the tool.
        """
        file_path = None
        tag = target["name"]
        
        while not self.stop_event.is_set():
            if not file_path:
                file_path = self._find_log_path(target)
                if file_path:
                    if self.callback: self.callback(f"[SYSTEM] Attached to {tag}: {file_path.name}")
                    self._tail_file(tag, file_path)
                    # If _tail_file returns, it means the file closed or we stopped.
                    # We loop back to see if we need to find it again (unlikely) or just exit.
                    if self.stop_event.is_set(): break
                else:
                    # Wait 2 seconds before looking again so we don't spam CPU
                    time.sleep(2)
            else:
                # If we had a path but lost it, reset
                file_path = None

    def _tail_file(self, tag, file_path):
        """
        Reads the file in real-time.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                # --- HISTORY DUMP (Context) ---
                # Read the last 4KB to give the user immediate context
                file_size = os.fstat(f.fileno()).st_size
                read_size = 4096
                if file_size > read_size:
                    f.seek(file_size - read_size)
                    f.readline() # Skip partial line
                
                # Ingest existing lines
                while True:
                    line = f.readline()
                    if not line: break
                    if self.callback and line.strip():
                        self.callback(f"[{tag}-HIST] {line.strip()}")

                # --- REALTIME MONITORING ---
                f.seek(0, os.SEEK_END)
                
                while not self.stop_event.is_set():
                    line = f.readline()
                    if line:
                        clean = line.strip()
                        if clean and self.callback:
                            self.callback(f"[{tag}] {clean}")
                    else:
                        time.sleep(0.1) # Efficient polling
                        
                        # Check if file was rotated/deleted
                        if not os.path.exists(file_path):
                            if self.callback: self.callback(f"[{tag}] File Access Lost.")
                            return
                            
        except Exception as e:
            if self.callback: self.callback(f"[{tag}] Error: {e}")
            time.sleep(1)