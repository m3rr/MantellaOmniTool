import os
import logging

class INISurgeon:
    def __init__(self, logger, target_game="Skyrim"):
        self.logger = logger
        self.target_game = target_game
        self.target_files = self.setup_targets()

    def setup_targets(self):
        """
        Determines INI paths based strictly on the selected game.
        """
        paths = []
        user_profile = os.environ.get('USERPROFILE')
        
        if self.target_game.lower() == "fallout4":
            self.logger.info("INI Surgeon Configured for: FALLOUT 4")
            paths = [
                os.path.join(user_profile, "Documents", "My Games", "Fallout4", "Fallout4.ini"),
                os.path.join(user_profile, "Documents", "My Games", "Fallout4", "Fallout4Prefs.ini"),
                os.path.join(user_profile, "Documents", "My Games", "Fallout4", "Fallout4Custom.ini")
            ]
        elif self.target_game.lower() == "skyrim" or "skyrim" in self.target_game.lower():
            self.logger.info("INI Surgeon Configured for: SKYRIM")
            paths = [
                os.path.join(user_profile, "Documents", "My Games", "Skyrim Special Edition", "Skyrim.ini"),
                os.path.join(user_profile, "Documents", "My Games", "Skyrim Special Edition", "SkyrimPrefs.ini"),
                os.path.join(user_profile, "Documents", "My Games", "Skyrim Special Edition", "SkyrimCustom.ini")
            ]
        else:
            self.logger.warning(f"INI Surgeon: Unknown game mode '{self.target_game}'. No targets set.")
            
        return paths

    def patch_files(self):
        """
        Iterates through target files and attempts to sanitize/patch them.
        """
        if not self.target_files:
            self.logger.info("[SURGEON] No files to patch.")
            return

        self.logger.info(f"[SURGEON] Initializing Protocol on {len(self.target_files)} potential files...")
        
        patched_count = 0
        
        for file_path in self.target_files:
            if not os.path.exists(file_path):
                # Valid behavior: If the file isn't there, we don't patch it. 
                # We do NOT error out.
                continue

            try:
                # Placeholder for actual INI manipulation logic
                # For now, we just verify access
                with open(file_path, 'r+') as f:
                    pass 
                patched_count += 1
            except PermissionError:
                self.logger.warning(f"[SURGEON] Permission Denied: {file_path}")
            except Exception as e:
                self.logger.error(f"[SURGEON] Error accessing {file_path}: {e}")

        self.logger.info(f"[SURGEON] Operation Complete. Accessed {patched_count} files.")