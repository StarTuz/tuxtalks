
import json
import os

# Path to user's config
config_path = os.path.expanduser("~/.local/share/tuxtalks/games/elite_dangerous_commands.json")

# New defaults to inject
new_defaults = {
    # UI Navigation
    "UI_Up": ["menu up", "up"],
    "UI_Down": ["menu down", "down"],
    "UI_Left": ["menu left", "left", "previous tab"],
    "UI_Right": ["menu right", "right", "next tab"],
    "UI_Select": ["menu select", "select", "enter", "confirm"],
    "UI_Back": ["menu back", "back", "cancel"],
    "CycleNextPanel": ["next panel", "tab next"],
    "CyclePreviousPanel": ["previous panel", "tab previous"],
    "UIFocus": ["ui focus", "focus"],
    "QuickCommsPanel": ["comms", "chat"],
    "TargetPanel": ["target panel", "left panel"],
    "SystemPanel": ["system panel", "right panel"],
    "RolePanel": ["role panel", "bottom panel"]
}

if os.path.exists(config_path):
    print(f"Found existing config: {config_path}")
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        updates = 0
        for key, val in new_defaults.items():
            if key not in data:
                data[key] = val
                updates += 1
                print(f"Adding new command: {key}")
                
        if updates > 0:
            with open(config_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"✅ patched {updates} new commands into config.")
        else:
            print("Config is already up to date.")
            
    except Exception as e:
        print(f"Error patching config: {e}")
else:
    print("Config file not found.")
