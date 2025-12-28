import os
import shutil
import json
import datetime
from utils.logger import get_logger

log = get_logger()

class MantellaPatcher:
    """
    Automated Maintenance Unit for Mantella.
    Ensures 'allow_actions' is enabled and prompts are optimized.
    """
    
    @staticmethod
    def execute_patches(mantella_path):
        if not mantella_path or not os.path.exists(mantella_path):
            log.warning("[PATCHER] Mantella path invalid or not found. Skipping patches.")
            return

        log.info(f"[PATCHER] Analyzing Mantella installation at: {mantella_path}")
        
        # 1. Config Patch
        config_path = os.path.join(mantella_path, "config.ini")
        if os.path.exists(config_path):
            MantellaPatcher._patch_config(config_path)
        else:
            log.warning("[PATCHER] config.ini not found.")

        # 2. Prompt Patch
        # inventory.json is typically in data/actions/inventory.json
        # The 'mantella_path' usually points to 'MantellaSoftware' folder.
        prompt_path = os.path.join(mantella_path, "data", "actions", "inventory.json")
        if os.path.exists(prompt_path):
            MantellaPatcher._patch_inventory_prompt(prompt_path)
        else:
            log.warning(f"[PATCHER] Action prompt not found at {prompt_path}")

        # 3. MECHANICAL BYPASS PATCH (OMNI-TOOL SPECIAL)
        # This injects the custom .pex file for the Action Fix.
        MantellaPatcher.install_bypass_patch(mantella_path)

    @staticmethod
    def _backup_file(file_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.{timestamp}.bak"
        try:
            shutil.copy2(file_path, backup_path)
            log.info(f"[PATCHER] Backup created: {os.path.basename(backup_path)}")
            return True
        except Exception as e:
            log.error(f"[PATCHER] Backup failed: {e}")
            return False

    @staticmethod
    def _patch_config(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            needs_update = False
            found_key = False
            new_lines = []
            
            for line in lines:
                if "allow_actions" in line:
                    found_key = True
                    if "True" not in line and "true" not in line: # Simple check
                        log.info("[PATCHER] Enabling 'allow_actions'...")
                        new_lines.append("allow_actions = True\n")
                        needs_update = True
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            if not found_key:
                log.info("[PATCHER] Injecting missing 'allow_actions' key.")
                new_lines.append("\nallow_actions = True\n")
                needs_update = True
                
            if needs_update and MantellaPatcher._backup_file(config_path):
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                log.info("[PATCHER] Config patched successfully.")
            else:
                log.info("[PATCHER] Config already optimal.")
                
        except Exception as e:
            log.error(f"[PATCHER] Config patch failed: {e}")

    @staticmethod
    def _patch_inventory_prompt(prompt_path):
        # ESCALATION: The previous prompt was too weak. 
        # New Strategy: Explicit Command Syntax + Example.
        target_description = "SYSTEM INSTRUCTION: To open your inventory, you MUST include the tag {key} at the end of your response. Example: 'Take a look. {key}'"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            current_desc = data.get("description", "")
            
            # Check if optimal
            if current_desc == target_description:
                log.info("[PATCHER] Inventory prompt already optimal.")
                return

            log.info("[PATCHER] Optimizing Inventory Prompt...")
            
            if MantellaPatcher._backup_file(prompt_path):
                data["description"] = target_description
                with open(prompt_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4)
                log.info("[PATCHER] Prompt optimized.")
                
        except Exception as e:
            log.error(f"[PATCHER] Prompt patch failed: {e}")

    @staticmethod
    def update_config(mantella_path, key, value):
        """
        Targeted update for a specific key in config.ini.
        value should be a boolean or string.
        """
        try:
            config_path = os.path.join(mantella_path, "config.ini")
            if not os.path.exists(config_path):
                log.warning("[PATCHER] Config not found for update.")
                return False

            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            new_lines = []
            key_found = False
            
            # Normalize boolean to capitalized string if needed
            val_str = str(value)
            if isinstance(value, bool):
                val_str = "True" if value else "False"
                
            for line in lines:
                if line.strip().startswith(key):
                    # Found the key, update it
                    new_lines.append(f"{key} = {val_str}\n")
                    key_found = True
                    log.info(f"[PATCHER] Updated {key} -> {val_str}")
                else:
                    new_lines.append(line)
            
            if not key_found:
                # Append if missing
                log.info(f"[PATCHER] Key {key} not found. Appending...")
                if new_lines and not new_lines[-1].endswith("\n"):
                    new_lines.append("\n")
                new_lines.append(f"{key} = {val_str}\n")
            
            # Backup before write
            if MantellaPatcher._backup_file(config_path):
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                return True
                
        except Exception as e:
            log.error(f"[PATCHER] Update failed: {e}")
            return False
    @staticmethod
    def install_bypass_patch(mantella_path):
        """
        Installs the 'MantellaAction_OffendForgiveFollow.pex' bypass patch.
        Checks assets/ folder for the patch and copies it to mantella_path/Scripts.
        """
        try:
            # 1. Locate Source
            # Should be in assets/ (bundled) or local dev folder
            patch_filename = "MantellaAction_OffendForgiveFollow.pex"
            
            # Use sys._MEIPASS if bundled, else local path
            import sys
            if hasattr(sys, '_MEIPASS'):
                 base_path = os.path.join(sys._MEIPASS, "assets")
            else:
                 base_path = os.path.join(os.getcwd(), "assets")
                 
            source_pex = os.path.join(base_path, patch_filename)
            
            if not os.path.exists(source_pex):
                log.error(f"[PATCHER] Bypass Patch source not found at: {source_pex}")
                return False

            # 2. Locate Destination
            # mantella_path usually ends in 'Mantella', e.g. 'Mods/Mantella'
            # Scripts is at 'Mantella/Scripts'
            dest_dir = os.path.join(mantella_path, "Scripts")
            if not os.path.exists(dest_dir):
                log.warning(f"[PATCHER] Scripts dir not found at {dest_dir}. Creating...")
                os.makedirs(dest_dir, exist_ok=True)
                
            dest_pex = os.path.join(dest_dir, patch_filename)

            # 3. Check if Update Needed (Simple size check or force)
            needs_update = True
            if os.path.exists(dest_pex):
                src_size = os.path.getsize(source_pex)
                dst_size = os.path.getsize(dest_pex)
                if src_size == dst_size:
                    log.info("[PATCHER] Bypass Patch appears current (size match).")
                    needs_update = False
                else:
                    log.info("[PATCHER] Patch size mismatch. Updating...")

            if needs_update:
                MantellaPatcher._backup_file(dest_pex)
                shutil.copy2(source_pex, dest_pex)
                log.info(f"[PATCHER] INSTALLED BYPASS PATCH to: {dest_pex}")
                return True
            
            return False

        except Exception as e:
            log.error(f"[PATCHER] Failed to install bypass patch: {e}")
            return False
