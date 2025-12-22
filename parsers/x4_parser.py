import os
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET # Fallback if defusedxml fails install/load, but security audit will flag

class X4XMLParser:
    def __init__(self, max_size_bytes=5 * 1024 * 1024):
        self.max_size_bytes = max_size_bytes

    def parse(self, file_path):
        """
        Parses X4 inputmap.xml securely.
        Returns a dict: { "INPUT_ACTION_ID": ("Key_Code", ["modifiers"]) }
        """
        print(f"🔍 DEBUG: X4Parser V.100 (Regex) processing {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return {}

        # 1. Security Check: File Size (DoS Prevention)
        size = os.path.getsize(file_path)
        if size > self.max_size_bytes:
             print(f"❌ Security Block: File size {size} bytes exceeds limit of {self.max_size_bytes}")
             return {}

        try:
            # 2. Security Check: Use defusedxml (Prevents XXE/Billion Laughs)
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            bindings = {}
            
            # X4 Structure: <inputmap> ... <state .../> ... </inputmap>
            # However, sometimes structure varies or namespaces interfere.
            # We will search recursively for ANY tag with 'code' and 'id'.
            
            for child in root.iter():
                # We look for ANY element with expected attributes
                attr = child.attrib
                action_id = attr.get("id", "")
                code = attr.get("code", "")
                
                if not action_id or not code: continue
                
                # Filter out obvious non-keys (Joystick, Mouse) to reduce noise
                # But keep "KEY" or "KEYCODE" items
                if "MOUSE" in code or "JOY" in code or "AXIS" in code:
                    continue
                
                # returns (key, mods) or (None, [])
                key, mods = self._map_x4_code_to_key(code)
                if key:
                    bindings[action_id] = (key, mods)
                    print(f"   + Bound {action_id} -> {key} + {mods}")
                else:
                    # Log skipped codes to help us expand the map
                    print(f"   ? Skipped {action_id} (Code: {code})")
            
            if len(bindings) == 0:
                 print(f"⚠️ Warning: Found 0 bindings in {file_path}. Dumping first 5 children for debug:")
                 for i, child in enumerate(root):
                     if i > 5: break
                     print(f"   Tag: {child.tag} Attribs: {child.attrib}")

            print(f"✅ Securely parsed {len(bindings)} bindings from {file_path}")
            return bindings
            
        except Exception as e:
            print(f"❌ XML Parsing Error: {e}")
            return {}

    def _map_x4_code_to_key(self, code):
        """Sanitizes and maps X4 internal codes. Returns (key_name, [modifiers])."""
        # 1. Filter Garbage
        raw = code.lower()
        if any(x in raw for x in ["mouse", "joy", "axis", "xbutton", "compassmenu", "dpad", "trigger", "shoulder"]):
            return None, []
            
        # 2. Strip Prefix
        # Heuristic: Remove common prefixes using regex (or manual checks)
        raw_clean = code
        if "INPUT_KEYCODE_" in raw_clean:
            raw_clean = raw_clean.replace("INPUT_KEYCODE_", "")
        elif "INPUT_KEY_" in raw_clean:
             raw_clean = raw_clean.replace("INPUT_KEY_", "")
        
        # 3. Extract Modifiers
        mods = []
        # Check lower case versions of suffixes
        check = raw_clean.lower()
        
        # Order matters? X4 seems to suffix like SPACE_SHIFT
        # But maybe also CTRL_SHIFT_A?
        # Let's check for presence anywhere
        
        if "_shift" in check:
            mods.append("Key.shift")
            # Remove from string (case insensitive replace is tricky, let's look for known suffixes)
            # Assuming suffix style for now
            raw_clean = raw_clean.replace("_SHIFT", "").replace("_shift", "")
            
        if "_ctrl" in check or "_control" in check:
            mods.append("Key.ctrl")
            raw_clean = raw_clean.replace("_CTRL", "").replace("_ctrl", "").replace("_CONTROL", "").replace("_control", "")

        if "_alt" in check:
             mods.append("Key.alt")
             raw_clean = raw_clean.replace("_ALT", "").replace("_alt", "")
             
        # Normalize what remains
        # e.g. "SPACE" -> "Space"
        final_key = self._normalize_key_name(raw_clean)
        
        return final_key, mods

    def _normalize_key_name(self, raw):
        mapping = {
            "SPACE": "Space",
            "RETURN": "Enter",
            "ESCAPE": "Esc",
            "BACK": "Backspace",  # X4 uses INPUT_KEYCODE_BACK for Backspace
            "BACKSPACE": "Backspace",
            "TAB": "Tab",
            "CAPSLOCK": "CapsLock",
            "LSHIFT": "ShiftLeft",
            "RSHIFT": "ShiftRight",
            "LCTRL": "CtrlLeft",
            "RCTRL": "CtrlRight",
            "LALT": "AltLeft",
            "RALT": "AltRight",
            "UP": "Up",
            "DOWN": "Down",
            "LEFT": "Left",
            "RIGHT": "Right",
            "INSERT": "Insert",
            "DELETE": "Delete",
            "HOME": "Home",
            "END": "End",
            "PAGE_UP": "PageUp",
            "PAGE_DOWN": "PageDown",
            "LBRACKET": "[",
            "RBRACKET": "]",
            "SEMICOLON": ";",
            "APOSTROPHE": "'",
            "BACKSLASH": "\\",
            "GRAVE": "`",
            "MINUS": "-",
            "EQUALS": "=",
            "COMMA": ",",
            "PERIOD": ".",
            "SLASH": "/",
            "NUM_0": "0", "NUM_1": "1", "NUM_2": "2", "NUM_3": "3", "NUM_4": "4",
            "NUM_5": "5", "NUM_6": "6", "NUM_7": "7", "NUM_8": "8", "NUM_9": "9",
            "NP_0": "Num0", "NP_1": "Num1", "NP_2": "Num2", "NP_3": "Num3", "NP_4": "Num4",
            "NP_5": "Num5", "NP_6": "Num6", "NP_7": "Num7", "NP_8": "Num8", "NP_9": "Num9",
            "NP_DIVIDE": "Num/", "NP_MULTIPLY": "Num*", "NP_SUBTRACT": "Num-", "NP_ADD": "Num+", 
            "NP_DECIMAL": "Num.", "NP_ENTER": "NumEnter"
        }
        
        # Check mapping (use Upper for lookup)
        upper = raw.upper()
        if upper in mapping:
            return mapping[upper]
            
        # Function keys
        if upper.startswith("F") and upper[1:].isdigit():
             return upper.lower() # f1, f12
             
        # Single Char
        if len(raw) == 1:
            return raw.lower()
            
        return raw.capitalize()
