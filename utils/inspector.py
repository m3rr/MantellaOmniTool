import os
import json

TARGET_FILE = r"D:\Modding\Mods\mods\Mantella\SKSE\Plugins\MantellaSoftware\data\actions\inventory.json"

NEW_CONTENT = {
    "identifier": "mantella_npc_inventory",
    "name": "Inventory",
    "description": "If you agree to trade, show your goods, or open your inventory, you must add the tag {key} to the end of your response.",
    "is-interrupting": True,
    "one-on-one": True
}

def patch_file():
    print(f"--- PATCHING {TARGET_FILE} ---")
    try:
        with open(TARGET_FILE, 'w', encoding='utf-8') as f:
            json.dump(NEW_CONTENT, f, indent=4)
        print("SUCCESS: inventory.json updated with simplified instructions.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    patch_file()
