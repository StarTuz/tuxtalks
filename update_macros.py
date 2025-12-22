
import json
import os

macros_path = os.path.expanduser("~/.local/share/tuxtalks/games/elite_dangerous_macros.json")

# The Standard Docking Macro
docking_macro = {
    "triggers": ["request docking", "dock", "docking request"],
    "steps": [
        {"action": "TargetPanel", "delay": 500},
        {"action": "UI_Right", "delay": 200},
        {"action": "UI_Right", "delay": 200},
        {"action": "UI_Select", "delay": 200},
        {"action": "UI_Right", "delay": 200},
        {"action": "UI_Select", "delay": 200},
        {"action": "TargetPanel", "delay": 200}
    ]
}

macros = {}
if os.path.exists(macros_path):
    print(f"Reading existing macros from {macros_path}")
    try:
        with open(macros_path, 'r') as f:
            macros = json.load(f)
    except:
        print("Error reading file, starting fresh.")

# Inject if not present (or update it, since user said they didn't complete it)
print("Injecting 'RequestDocking' macro...")
macros["RequestDocking"] = docking_macro

with open(macros_path, 'w') as f:
    json.dump(macros, f, indent=4)

print("✅ Macro injected successfully.")
