
import tkinter as tk
from tkinter import simpledialog

# Mocking the context
class Profile:
    def update_binding(self, action, key_data):
        print(f"Called update_binding with: {action}, {key_data}")
        return True, "Success"

def map_key_to_ed(k):
    TK_ED_LOOKUP = {
        "shift": "Key_LeftShift",
        "f1": "Key_F1",
        "space": "Key_Space"
    }
    k_lower = k.lower().replace(" ", "")
    if k_lower in TK_ED_LOOKUP: return TK_ED_LOOKUP[k_lower]
    return f"Key_{k.capitalize()}"

def parse(new_bind_str):
    print(f"Parsing: '{new_bind_str}'")
    parts = [p.strip() for p in new_bind_str.split("+") if p.strip()]
    if not parts: return None

    base_key_raw = parts[-1]
    raw_mods = parts[:-1]
    
    # --- Logic from launcher_games_tab.py ---
    TK_ED_LOOKUP = {
            "enter": "Key_Enter", "return": "Key_Enter",
            "space": "Key_Space", "backspace": "Key_Backspace", "tab": "Key_Tab",
            "escape": "Key_Escape", "delete": "Key_Delete", "insert": "Key_Insert",
            "home": "Key_Home", "end": "Key_End",
            "pageup": "Key_PageUp", "pagedown": "Key_PageDown", "prior": "Key_PageUp", "next": "Key_PageDown",
            "up": "Key_UpArrow", "down": "Key_DownArrow", "left": "Key_LeftArrow", "right": "Key_RightArrow",
            "shift": "Key_LeftShift", "leftshift": "Key_LeftShift", "rightshift": "Key_RightShift",
            "ctrl": "Key_LeftControl", "control": "Key_LeftControl", "leftcontrol": "Key_LeftControl",
            "alt": "Key_LeftAlt", "leftalt": "Key_LeftAlt"
    }
    
    def map_key_to_ed(k):
        k_lower = k.lower().replace(" ", "")
        if k_lower in TK_ED_LOOKUP: return TK_ED_LOOKUP[k_lower]
        if len(k) == 1 and k.isalnum(): return f"Key_{k.upper()}"
        if k_lower.startswith("f") and k_lower[1:].isdigit(): return f"Key_{k.upper()}"
        return f"Key_{k.capitalize()}"
        
    def map_mod_to_ed(m):
        m = m.lower().replace(" ", "")
        if "ctrl" in m or "control" in m: return "Key_RightControl" if "right" in m else "Key_LeftControl"
        if "shift" in m: return "Key_RightShift" if "right" in m else "Key_LeftShift"
        if "alt" in m: return "Key_RightAlt" if "right" in m else "Key_LeftAlt"
        return None
        
    final_key = map_key_to_ed(base_key_raw)
    final_mods = [map_mod_to_ed(m) for m in raw_mods]
    final_mods = [m for m in final_mods if m] 
    
    return {'key': final_key, 'mods': final_mods}

# Test Cases
print(parse("Shift+F1"))
print(parse("Ctrl+Alt+Delete"))
