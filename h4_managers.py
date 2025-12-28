import json
import os
import logging

class SettingsManager:
    def __init__(self, settings_file="omni_settings.json"):
        self.settings_file = settings_file
        self.logger = logging.getLogger("h4_managers")
        
        self.default_settings = {
            "first_run": True,
            "game_mode": "Skyrim", 
            "game_path": "",
            "scan_depth": 3,
            "theme": "Dark",
            "debug_mode": False
        }
        
        self.settings = self.load_settings()

    def load_settings(self):
        """
        Nuclear Load: Reads file. Only patches missing keys. 
        Never overwrites existing data with defaults unless file is corrupt.
        """
        if not os.path.exists(self.settings_file):
            self.logger.warning("Settings file not found. Creating new.")
            self.save_settings(self.default_settings)
            return self.default_settings.copy()

        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
            
            # Validation: Only inject defaults for KEYS THAT DO NOT EXIST
            dirty = False
            for key, value in self.default_settings.items():
                if key not in data:
                    self.logger.info(f"Key '{key}' missing in config. Injecting default.")
                    data[key] = value
                    dirty = True
            
            if dirty:
                self.save_settings(data)
            
            self.settings = data # FORCE UPDATE INTERNAL STATE
            return data
            
        except json.JSONDecodeError:
            self.logger.error("Settings file is corrupt (JSON Error). Backing up and resetting.")
            if os.path.exists(self.settings_file):
                os.rename(self.settings_file, self.settings_file + ".bak")
            self.save_settings(self.default_settings)
            return self.default_settings.copy()
        except Exception as e:
            self.logger.error(f"Critical error loading settings: {e}")
            return self.default_settings.copy()

    def save_settings(self, settings_data):
        """
        Nuclear Save: Flushes buffer to disk immediately.
        """
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings_data, f, indent=4)
                f.flush()
                os.fsync(f.fileno()) # The "Nuclear" option: Force OS to write to disk
            self.settings = settings_data
            self.logger.info("Settings saved and flushed to disk.")
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")

    def get_setting(self, key):
        return self.settings.get(key, self.default_settings.get(key))

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)

    def save_scan_data(self, targets_dict):
        """
        Persists the found paths from the Hunter Protocol.
        We only save 'found', not the whole object to keep it clean.
        """
        scan_data = {}
        for name, data in targets_dict.items():
            if data.get("found"):
                scan_data[name] = data["found"]
        
        self.settings["_scan_cache"] = scan_data
        self.save_settings(self.settings)

    def load_scan_data(self, targets_dict):
        """
        Hydrates the TARGETS dict with cached paths.
        Returns True if any data was loaded.
        """
        cache = self.settings.get("_scan_cache", {})
        if not cache: return False
        
        loaded = False
        for name, path in cache.items():
            if name in targets_dict and os.path.exists(path):
                targets_dict[name]["found"] = path
                loaded = True
        return loaded