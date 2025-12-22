import sys
import os
import unittest.mock

# Mock pynput so we can import game_manager if needed, 
# or just sufficient to run x4_parser if it had deps (it doesn't, but safety first)
sys.modules['pynput'] = unittest.mock.MagicMock()
sys.modules['pynput.keyboard'] = unittest.mock.MagicMock()

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from parsers.x4_parser import X4XMLParser
except ImportError as e:
    print(f"Error importing X4XMLParser: {e}")
    sys.exit(1)

print("--- X4 Binding Debugger (Standalone) ---")

def detect_x4_folder():
    """Native GOG Path Detection"""
    # Check both case variations just in case
    candidates = [
        os.path.expanduser("~/.config/Egosoft/X4"),
        os.path.expanduser("~/.config/EgoSoft/X4")
    ]
    
    for base in candidates:
        if os.path.exists(base):
            # Find numeric UserID folder
            subdirs = [d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)) and d.isdigit()]
            if subdirs:
                 # Sort by mtime
                 subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(base, x)), reverse=True)
                 return os.path.join(base, subdirs[0])
            # Fallback
            if os.path.exists(os.path.join(base, "inputmap.xml")):
                return base
    return None

detected_folder = detect_x4_folder()
print(f"Detected X4 Folder: {detected_folder}")

if detected_folder:
    target_file = os.path.join(detected_folder, "inputmap.xml")
    print(f"Parsing: {target_file}")
    
    if os.path.exists(target_file):
        parser = X4XMLParser()
        bindings = parser.parse(target_file)
        
        # Search for bindings to Esc
        print("\n--- Reverse Lookup: What triggers Esc? ---")
        for aid, (key, mods) in bindings.items():
            if key in ["Esc", "Escape"]:
                print(f"{aid} -> {key} + {mods}")
        
        # Check primary weapon group again to be absolutely sure
        print("\n--- Check Weapon Group 1 ---")
        aid = "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_1"
        if aid in bindings:
             k, m = bindings[aid]
             print(f"{aid} -> '{k}' + {m}")


    else:
        print(f"File not found: {target_file}")
else:
    print("Could not detect X4 folder.")

