import os
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from pynput.keyboard import Key

class EDXMLParser:
    def __init__(self):
        # Mapping ED Key Names to Pynput format or internal strings handled by game_manager
        self.key_mapping = {
            "Key_LeftShift": "Key.shift", "Key_RightShift": "Key.shift_r",
            "Key_LeftControl": "Key.ctrl", "Key_RightControl": "Key.ctrl_r",
            "Key_LeftAlt": "Key.alt", "Key_RightAlt": "Key.alt_r",
            "Key_Enter": "Key.enter", "Key_Space": "Key.space",
            "Key_Tab": "Key.tab", "Key_Backspace": "Key.backspace",
            "Key_Delete": "Key.delete", "Key_Insert": "Key.insert",
            "Key_Home": "Key.home", "Key_End": "Key.end",
            "Key_PageUp": "Key.page_up", "Key_PageDown": "Key.page_down",
            "Key_Up": "Key.up", "Key_Down": "Key.down",
            "Key_Left": "Key.left", "Key_Right": "Key.right",
            "Key_CapsLock": "Key.caps_lock", "Key_NumLock": "Key.num_lock",
            "Key_ScrollLock": "Key.scroll_lock",
            "Key_F1": "Key.f1", "Key_F2": "Key.f2", "Key_F3": "Key.f3", "Key_F4": "Key.f4",
            "Key_F5": "Key.f5", "Key_F6": "Key.f6", "Key_F7": "Key.f7", "Key_F8": "Key.f8",
            "Key_F9": "Key.f9", "Key_F10": "Key.f10", "Key_F11": "Key.f11", "Key_F12": "Key.f12",
            "Key_Apostrophe": "'", "Key_SemiColon": ";", "Key_BackSlash": "\\", "Key_Slash": "/",
            "Key_Comma": ",", "Key_Period": ".", "Key_Minus": "-", "Key_Equals": "=",
            "Key_LeftBracket": "[", "Key_RightBracket": "]", "Key_Grave": "`",
        }

    def parse(self, file_path):
        """
        Parses Elite Dangerous .binds file.
        Returns dict: { ActionName: (Key, [Mods]) }
        """
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return {}

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            bindings = {}

            for child in root:
                action_name = child.tag
                
                # ED often has <Primary Device="Keyboard" Key="Key_X" /> 
                # and <Secondary Device="..." ... />
                # We prioritize Primary, then Secondary if Primary is empty or not Keyboard
                
                primary = child.find("Primary")
                secondary = child.find("Secondary")
                
                chosen = None
                
                # Check Primary
                if primary is not None:
                    dev = primary.attrib.get("Device", "")
                    key = primary.attrib.get("Key", "")
                    if dev == "Keyboard" and key:
                        chosen = primary
                
                # Check Secondary if Primary failed
                if chosen is None and secondary is not None:
                    dev = secondary.attrib.get("Device", "")
                    key = secondary.attrib.get("Key", "")
                    if dev == "Keyboard" and key:
                         chosen = secondary
                         
                if chosen is not None:
                    key_attr = chosen.attrib.get("Key", "")
                    
                    # Parse Modifiers
                    # <Modifier Device="Keyboard" Key="Key_LeftShift" />
                    mods = []
                    for mod in chosen.findall("Modifier"):
                         m_dev = mod.attrib.get("Device", "")
                         m_key = mod.attrib.get("Key", "")
                         if m_dev == "Keyboard" and m_key:
                             mapped_mod = self._map_key(m_key)
                             if mapped_mod: mods.append(mapped_mod)

                    final_key = self._map_key(key_attr)
                    
                    if final_key:
                        bindings[action_name] = (final_key, mods)
                        
            print(f"✅ ED Parser: Found {len(bindings)} bindings in {os.path.basename(file_path)}")
            return bindings
            
        except Exception as e:
            print(f"❌ ED Parse Error: {e}")
            return {}
            
    def _map_key(self, ed_key):
        """Maps ED key string to internal/pynput string."""
        if not ed_key: return None
        
        # Check explicit map
        if ed_key in self.key_mapping:
            return self.key_mapping[ed_key]
            
        # Handle "Key_A" -> "a"
        if ed_key.startswith("Key_"):
            return ed_key[4:].lower()
            
        return ed_key.lower()
