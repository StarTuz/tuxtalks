"""
Game Manager for TuxTalks - Handles game profiles, bindings, and voice commands.
Supports Elite Dangerous, X4 Foundations, and generic games.
"""

import os
import glob
import psutil
import xml.etree.ElementTree as ET
import time
import threading
import json
from abc import ABC, abstractmethod
from pynput.keyboard import Key, KeyCode, Controller

# LAL Framework
try:
    from lal_manager import LALManager
except ImportError:
    LALManager = None
    print("⚠️ LAL Manager not available (lal_manager.py missing)")

from speech_engines.audio_player import AudioFeedbackPlayer
from config import cfg # Need config lookup for resolving paths
import logging

USER_GAMES_FILE = os.path.expanduser("~/.config/tuxtalks/user_games.json")

class GameProfile:
    def __init__(self, name, path_discriminator=None, group=None):
        self.name = name
        self.group = group if group else name # Default group = name (Standard fallback)
        self.path_discriminator = path_discriminator
        self.runtime_env = "Native Linux" # Default, can be "Proton/Wine"
        self.bindings = {} # Runtime Map of VoicePhrase -> (Key, Modifiers)
        
        # Default Mapping for Voice -> ActionID
        # Based on default context.bindings or custom binds
        self.action_voice_map = {} # Defined subclasses will populate this
        self.enabled = False
        
        # Default Categories
        self.categories = ["All", "General"]
        
        # Phase 1d: Hierarchical directory structure
        game_slug = self.group.lower().replace(' ', '_')
        game_dir = os.path.expanduser(f"~/.local/share/tuxtalks/games/{game_slug}")
        
        # New hierarchical paths
        new_commands_file = os.path.join(game_dir, "commands.json")
        new_macros_file = os.path.join(game_dir, "macros", "default.json")
        new_config_file = os.path.join(game_dir, "config.json")
        
        # Old flat structure paths (for backward compatibility)
        old_name_slug = name.lower().replace(' ', '_')
        old_commands_file = os.path.expanduser(f"~/.local/share/tuxtalks/games/{old_name_slug}_commands.json")
        old_macros_file = os.path.expanduser(f"~/.local/share/tuxtalks/games/{old_name_slug}_macros.json")
        old_config_file = os.path.expanduser(f"~/.local/share/tuxtalks/games/{old_name_slug}_config.json")
        
        # Resolve paths with backward compatibility
        self.commands_file = self._resolve_path(new_commands_file, old_commands_file)
        self.macros_file = self._resolve_path(new_macros_file, old_macros_file)
        self.config_file = self._resolve_path(new_config_file, old_config_file)
        
        self.macros = {} # Name -> {triggers: [], steps: []}
        self.active_binds_path = None # Path to the currently loaded bindings file
        
        # Phase 14: Modular Attributes
        self.process_name = "" 
        self.custom_bindings_path = "" # User defined path
        self.custom_commands = {} # Phase 7: Custom Commands (ID -> {name, key, triggers...})
        self.selected_macro_profile = "Built-in" # Default macro profile
        
        # Try load config immediately
        self.load_config()
    
    def _resolve_path(self, new_path, old_path):
        """
        Resolve file path with backward compatibility.
        
        Checks new hierarchical path first, falls back to old flat structure.
        If neither exists, returns new path for future creation.
        """
        if os.path.exists(new_path):
            return new_path
        elif os.path.exists(old_path):
            # Old flat structure exists - will be migrated later
            return old_path
        else:
            # Neither exists - use new path for creation
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            return new_path

    def backup_bindings(self, destination):
        """Backs up the currently active bindings file to the destination."""
        if not self.active_binds_path or not os.path.exists(self.active_binds_path):
            print(f"❌ No active bindings file to backup for {self.name}")
            return False, "No active bindings file found."
            
        try:
            import shutil
            shutil.copy2(self.active_binds_path, destination)
            print(f"✅ Backed up bindings to: {destination}")
            return True, f"Successfully backed up to {destination}"
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False, str(e)

    def restore_bindings(self, source_path):
        """Restores bindings from source_path to the active bindings file."""
        if not self.active_binds_path:
            return False, "No active bindings file known (Game not detected?)"
            
        if not os.path.exists(source_path):
            return False, "Source file does not exist."
            
        try:
            import shutil
            # Overwrite!
            shutil.copy2(source_path, self.active_binds_path)
            print(f"✅ Restored bindings from {source_path} -> {self.active_binds_path}")
            return True, "Bindings restored successfully. Please RESTART the game and launcher."
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False, str(e)

    def load_commands(self):
        """Loads voice aliases from JSON."""
        if os.path.exists(self.commands_file):
            try:
                import json
                with open(self.commands_file, 'r') as f:
                    # Update existing defaults with user overrides (merging)
                    # This ensures new defaults (added by updates) appear even if user config exists
                    user_cmds = json.load(f)
                    self.action_voice_map.update(user_cmds)
                print(f"📖 Loaded custom commands for {self.name}")
                return True
            except Exception as e:
                print(f"❌ Failed to load commands for {self.name}: {e}")
        return False

    def save_commands(self):
        """Saves voice aliases to JSON."""
        try:
            import json
            os.makedirs(os.path.dirname(self.commands_file), exist_ok=True)
            with open(self.commands_file, 'w') as f:
                json.dump(self.action_voice_map, f, indent=4)
            print(f"💾 Saved commands for {self.name}")
        except Exception as e:
            print(f"❌ Failed to save commands for {self.name}: {e}")

    def load_macros(self):
        """Loads macros from JSON."""
        if os.path.exists(self.macros_file):
            try:
                import json
                with open(self.macros_file, 'r') as f:
                    user_macros = json.load(f)
                    self.macros.update(user_macros)
                print(f"📜 Loaded macros for {self.name}")
                return True
            except Exception as e:
                print(f"❌ Failed to load macros for {self.name}: {e}")
        return False

    def save_macros(self):
        """Saves macros to JSON."""
        try:
            import json
            os.makedirs(os.path.dirname(self.macros_file), exist_ok=True)
            with open(self.macros_file, 'w') as f:
                json.dump(self.macros, f, indent=4)
            print(f"💾 Saved macros for {self.name}")
        except Exception as e:
            print(f"❌ Failed to save macros for {self.name}: {e}")

    def load_config(self):
        """Loads modular configuration (process name, bindings path)."""
        if os.path.exists(self.config_file):
            try:
                import json
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    p_name = data.get("process_name", "")
                    if p_name: self.process_name = p_name
                    
                    self.custom_bindings_path = data.get("bindings_path", "")
                    # If custom path is set, it overrides active_binds_path eventually
                    if self.custom_bindings_path:
                         self.active_binds_path = self.custom_bindings_path
                    
                    
                    self.runtime_env = data.get("runtime_env", "Native Linux") # Load runtime_env
                    self.custom_commands = data.get("custom_commands", {}) # Phase 7
            except Exception as e:
                print(f"❌ Failed to load config for {self.name}: {e}")

    def save_config(self):
        """Saves modular configuration."""
        try:
            import json
            data = {
                "process_name": self.process_name,
                "bindings_path": self.custom_bindings_path,
                "bindings_path": self.custom_bindings_path,
                "runtime_env": self.runtime_env, # Save runtime_env
                "custom_commands": self.custom_commands # Phase 7
            }
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"💾 Saved config for {self.name}")
        except Exception as e:
            print(f"❌ Failed to save config for {self.name}: {e}")

    @abstractmethod
    def load_bindings(self):
        pass

    @abstractmethod
    def load_bindings(self):
        pass

    def is_running(self):
        """Checks if the game process is running."""
        # Generic check if process_name is defined
        if self.process_name:
            # Normalize list of targets
            targets = [self.process_name.lower()] if isinstance(self.process_name, str) else [n.lower() for n in self.process_name]
            
            for proc in psutil.process_iter(['name', 'cmdline', 'exe']):
                try:
                    # Check Name
                    p_name = proc.info['name'].lower() if proc.info['name'] else ""
                    if any(t in p_name for t in targets):
                        # If discriminator is set, verify path/cmdline
                        if self.path_discriminator:
                            disc = self.path_discriminator.lower()
                            # Check Exe Path
                            if proc.info.get('exe') and disc in proc.info['exe'].lower():
                                return True
                            # Check Cmdline
                            if proc.info.get('cmdline'):
                                for arg in proc.info['cmdline']:
                                    if disc in arg.lower():
                                        return True
                            continue # Name matched but discriminator didn't
                        return True
                        
                    # Check Cmdline (for Wine/Proton wrappers or scripts like ./X4)
                    if proc.info['cmdline']:
                        cmd_str = " ".join(proc.info['cmdline']).lower()
                        if any(t in cmd_str for t in targets):
                            # Discriminator Check
                            if self.path_discriminator:
                                disc = self.path_discriminator.lower()
                                # Check Exe
                                if proc.info.get('exe') and disc in proc.info['exe'].lower():
                                    return True
                                # Check Cmdline args
                                if disc in cmd_str:
                                    return True
                                continue
                            return True
                                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        return False

    def get_friendly_name(self, action_id):
        """Returns human readable name for action if available."""
        if hasattr(self, 'friendly_name_map') and action_id in self.friendly_name_map:
            return self.friendly_name_map[action_id]
        return action_id.replace("INPUT_", "").replace("_", " ").title()

    def get_category(self, action_name):
        """Returns the category for a given action. Override in subclasses."""
        return "General"

    def _merge_custom_commands(self):
        """Merges custom commands into the runtime bindings map."""
        if not hasattr(self, 'custom_commands'): return
        
        count = 0
        for cmd_id, data in self.custom_commands.items():
            if not data.get('enabled', True): continue
            
            key_str = data['key']
            mods_str_list = data.get('modifiers', [])
            
            # Map key using existing helper
            key_code = self.get_key_code(key_str)
            if not key_code: 
                print(f"⚠️ Custom Command '{data.get('name')}' has invalid key '{key_str}'")
                continue
                
            triggers = data.get('triggers', [])
            for trigger in triggers:
                # Add to bindings: trigger -> (key_code, [mods])
                self.bindings[trigger] = (key_code, mods_str_list)
                count += 1
                
        if count > 0:
            print(f"➕ Merged {count} custom command triggers.")

    def execute_macro(self, macro_name, input_controller):
        """Executes the macro steps."""
        if macro_name not in self.macros:
            print(f"❌ Macro '{macro_name}' not found.")
            return False
            
        print(f"▶️ Executing Macro: {macro_name}")
        macro = self.macros[macro_name]
        steps = macro.get("steps", [])
        
        for step in steps:
            # step = {"action": "Name", "delay": 200, "key": "Shift+A"}
            
            # 1. Determine Key/Mods to press
            key_code = None
            mods = []
            
            if "key" in step and step["key"]:
                # Custom Action: Parse raw key string (e.g. "Shift+F10")
                parts = step["key"].split("+")
                # Last part is the key, previous are modifiers
                raw_key = parts[-1].strip()
                raw_mods = [m.strip().lower() for m in parts[:-1]]
                
                key_code = self.get_key_code(raw_key)
                for rm in raw_mods:
                    mc = self.get_key_code(rm)
                    if mc: mods.append(mc)
                    
            elif "action" in step:
                # Standard Action: Lookup in bindings
                action = step["action"]
                if action in self.actions:
                     # self.actions[action] = (key, [mods])
                     key_code, mods = self.actions[action]
                else:
                     print(f"⚠️ Action '{action}' not bound. Skipping step.")
                     continue
            
            # --- Audio Feedback (Sound Pool - Phase 13 Option A) ---
            audio_pool = step.get("audio_pool", [])
            playback_mode = step.get("playback_mode", "Random")
            
            # Legacy Fallback: If no pool but file specified, treat as pool of 1
            if not audio_pool:
                legacy_file = step.get("audio_feedback_file")
                audio_id = step.get("audio_feedback")
                
                # Check IDs / LAL
                if audio_id:
                     # (Previous LAL logic - reduced for brevity, assuming pools are direct paths for now)
                     # If we want LAL support in pools, we'd need to resolve them.
                     # For now, let's just stick to the existing ID fallback logic if pool is empty.
                     pass 
                elif legacy_file and legacy_file != "(Sound Pool)":
                     audio_pool = [legacy_file]

            # Process Pool
            files_to_play = []
            
            if audio_pool:
                if playback_mode == "Simultaneous":
                    files_to_play = audio_pool
                elif playback_mode == "Sequential (Round-Robin)":
                    # State tracking
                    state_key = f"{macro_name}_step_{steps.index(step)}"
                    if not hasattr(self, "macro_state"): self.macro_state = {}
                    
                    idx = self.macro_state.get(state_key, 0)
                    if idx >= len(audio_pool): idx = 0 # Handle pool shrinking
                    
                    files_to_play = [audio_pool[idx]]
                    
                    # Advance state
                    self.macro_state[state_key] = (idx + 1) % len(audio_pool)
                else:
                    # Random (Default)
                    import random
                    if audio_pool:
                        files_to_play = [random.choice(audio_pool)]
            
            # Fallback to ID/LAL if pool processing yielded nothing but ID exists
            # (Original Logic for IDs)
            audio_id = step.get("audio_feedback")
            if not files_to_play and audio_id:
                # Try LAL packs first
                audio_file = None
                if hasattr(self, 'lal_manager') and self.lal_manager:
                    audio_file = self.lal_manager.get_audio(audio_id, profile_type=self.type)
                
                # Fallback to custom audio directory
                if not audio_file:
                    from config import load_config
                    cfg = load_config()
                    custom_dir = cfg.get("CUSTOM_AUDIO_DIR", "")
                    if custom_dir and os.path.exists(custom_dir):
                        for ext in ['.wav', '.ogg', '.mp3']:
                            candidate = os.path.join(custom_dir, f"{audio_id}{ext}")
                            if os.path.exists(candidate):
                                audio_file = candidate
                                break
                if audio_file:
                    files_to_play = [audio_file]

            # Execute Playback
            for f_path in files_to_play:
                # Handle Audio Directory logic (Legacy/Implicit) if single path is a dir
                # Only check if it's a single item to avoid recursion madness or spam
                final_path = f_path
                
                # Resolve relative paths
                if not os.path.isabs(f_path):
                     from config import load_config
                     cfg = load_config()
                     custom_dir = cfg.get("CUSTOM_AUDIO_DIR", "")
                     if custom_dir:
                         candidate = os.path.join(custom_dir, f_path)
                         if os.path.exists(candidate):
                             final_path = candidate
                
                if os.path.isdir(final_path):
                     # Legacy Directory Randomizer
                     import random
                     import glob
                     candidates = []
                     for ext in ["*.wav", "*.mp3", "*.ogg", "*.flac"]:
                        candidates.extend(glob.glob(os.path.join(final_path, ext)))
                     if candidates:
                        final_path = random.choice(candidates)
                
                if final_path and os.path.exists(final_path):
                    print(f"🔊 Playing: {os.path.basename(final_path)}")
                    AudioFeedbackPlayer().play(final_path)
                elif f_path and f_path != "(Sound Pool)":
                    print(f"⚠️ Audio file not found: {f_path}")
                     
            
            # 2. Execute Press
            if key_code:
                print(f"   -> Pressing: {mods} + {key_code}")
                if input_controller:
                    # FIX: Linux/Wayland ydotool fix for numeric keys
                    # ydotool interprets '1', '2' strings as Scancodes 1 (Esc), 2 (1), etc.
                    # We must map chars to correct Scancodes: 1->2, 2->3 ... 0->11.
                    final_key = key_code
                    if hasattr(key_code, 'char') and key_code.char and key_code.char.isdigit():
                        digit_map = {
                            '1': 2, '2': 3, '3': 4, '4': 5, '5': 6,
                            '6': 7, '7': 8, '8': 9, '9': 10, '0': 11
                        }
                        if key_code.char in digit_map:
                            final_key = digit_map[key_code.char]
                            print(f"DEBUG: Remapped '{key_code.char}' to Scancode {final_key}")

                    # Execute via abstract controller
                    # Note: hold_key_combo might be blocking or async depending on implementation
                    input_controller.hold_key_combo(final_key, mods, duration=0.1)
                else:
                    print("⚠️ No input controller available to execute binding.")
                
            # 3. Handle Delay
            delay_ms = step.get("delay", 100)
            if delay_ms > 0:
                time.sleep(delay_ms / 1000.0)
                
        return True

    def get_key_code(self, key_str):
        """Converts a string representation of a key (e.g., "Key_L", "LShift", "Enter")
        to a pynput Key or KeyCode object."""
        key_str = key_str.lower()

        # Handle special keys
        if key_str == "lshift" or key_str == "shiftleft" or key_str == "leftshift": return Key.shift_l
        if key_str == "rshift" or key_str == "shiftright" or key_str == "rightshift": return Key.shift_r
        if key_str == "lcontrol" or key_str == "controlleft" or key_str == "leftcontrol": return Key.ctrl_l
        if key_str == "rcontrol" or key_str == "controlright" or key_str == "rightcontrol": return Key.ctrl_r
        if key_str == "lalt" or key_str == "altleft" or key_str == "leftalt": return Key.alt_l
        if key_str == "ralt" or key_str == "altright" or key_str == "rightalt": return Key.alt_r
        if key_str == "enter": return Key.enter
        if key_str == "space": return Key.space
        if key_str == "tab": return Key.tab
        if key_str == "escape": return Key.esc
        if key_str == "back": return Key.backspace
        if key_str == "delete": return Key.delete
        if key_str == "insert": return Key.insert
        if key_str == "home": return Key.home
        if key_str == "end": return Key.end
        if key_str == "pageup": return Key.page_up
        if key_str == "pagedown": return Key.page_down
        if key_str == "up": return Key.up
        if key_str == "down": return Key.down
        if key_str == "left": return Key.left
        if key_str == "right": return Key.right
        if key_str == "capslock": return Key.caps_lock
        if key_str == "numlock": return Key.num_lock
        if key_str == "scrolllock": return Key.scroll_lock
        if key_str.startswith("f") and len(key_str) > 1 and key_str[1:].isdigit():
            f_num = int(key_str[1:])
            if 1 <= f_num <= 24:
                return getattr(Key, f"f{f_num}")
        
        # Handle Elite Dangerous specific key names (e.g., "Key_A", "Key_1")
        if key_str.startswith("key_"):
            key_str = key_str[4:] # Remove "Key_" prefix

        # For single characters or numbers
        if len(key_str) == 1:
            return KeyCode.from_char(key_str)
        
        # Fallback for unknown keys (might be a pynput Key enum directly)
        try:
            return getattr(Key, key_str)
        except AttributeError:
            print(f"⚠️ Warning: Unknown key string '{key_str}'")
            return None

            print(f"⚠️ Warning: Unknown key string '{key_str}'")
            return None

# Import parser locally or at top if module structure permits. 
# For this file stricture, we assume parsers package is available.
try:
    from parsers.x4_parser import X4XMLParser
    from parsers.ed_parser import EDXMLParser
except ImportError:
    X4XMLParser = None
    EDXMLParser = None

class X4Profile(GameProfile):
    def __init__(self, name="X4 Foundations", discriminator=None, default_path_override=None, group=None):
        super().__init__(name, path_discriminator=discriminator, group=group)
        
        # Default Path logic
        if default_path_override:
            self.custom_bindings_path = default_path_override  # FIX: Store in correct field
            self.default_path = default_path_override  # Keep for backwards compatibility
        else:
             # Standard Steam path or Proton path default
            self.default_path = os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/392160/pfx/drive_c/users/steamuser/Documents/Egosoft/X4/inputmap.xml")
            
        self.custom_path = None
        self.process_name = ["X4.exe", "X4", "./X4", "x4start.sh", "Main"]
        self.default_process_name = "X4.exe"
        
        # X4 Specific Categories
        self.categories = ["All", "General", "Flight", "Menu", "Platform", "Drones"]
        
        # Mapping X4 Action IDs to Voice Commands
        self.action_voice_map = {
             "INPUT_ACTION_STOP": ["stop engines", "stop", "all stop"],  # Actual action ID (Backspace)
             "INPUT_STATE_STOP_SHIP": ["stop engines", "stop", "all stop"], # Legacy/Alt
             "INPUT_STATE_DECCELERATE": ["stop engines", "stop", "all stop"], # Primary
             "INPUT_STATE_MATCH_SPEED": ["match speed"],
             "INPUT_STATE_BOOST": ["boost", "engine boost"],
             "INPUT_STATE_TRAVEL_MODE": ["travel mode", "engage travel mode"],
             "INPUT_ACTION_TOGGLE_TRAVEL_MODE": ["travel mode", "engage travel mode"], # New toggle ID
             "INPUT_STATE_SCAN_MODE": ["scan mode", "scanner"],
             "INPUT_ACTION_TOGGLE_SCAN_MODE": ["scan mode", "scanner"], # New toggle ID
             "INPUT_STATE_LONG_RANGE_SCAN": ["long range scan", "pulse scan"],
             "INPUT_ACTION_TOGGLE_LONGRANGE_SCAN_MODE": ["long range scan", "pulse scan"], # New toggle ID
             "INPUT_STATE_FIRE_PRIMARY": ["fire", "fire weapons"],
             "INPUT_STATE_FIRE_SECONDARY": ["fire missiles", "fire secondary"],
             "INPUT_STATE_LOWER_SHIELDS": ["drop shields"], 
             
             # Weapon Groups - Primary
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_1": ["primary weapon group one", "primary group one", "select primary one", "weapon group one", "weapons group one", "group one", "select group one", "weapon group 1", "weapons group 1", "group 1", "weapons growth one", "weapons growth 1"],
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_2": ["primary weapon group two", "primary group two", "select primary two", "weapon group two", "weapons group two", "group two", "group too", "group to", "select group two", "weapon group 2", "weapons group 2", "group 2", "weapons group too", "weapons group to", "weapons growth two", "weapons growth to", "weapons growth too"],
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_3": ["primary weapon group three", "primary group three", "select primary three", "weapon group three", "weapons group three", "group three", "select group three", "weapon group 3", "weapons group 3", "group 3", "weapons growth three"],
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_4": ["primary weapon group four", "primary group four", "select primary four", "weapon group four", "weapons group four", "group four", "select group four", "weapon group 4", "weapons group 4", "group 4", "weapons growth four"],
             "INPUT_ACTION_CYCLE_NEXT_PRIMARY_WEAPONGROUP": ["next primary weapon group", "next primary group", "next primary weapon", "next weapon group", "next weapons group", "next group"],
             "INPUT_ACTION_CYCLE_PREV_PRIMARY_WEAPONGROUP": ["previous primary weapon group", "previous primary group", "previous primary weapon", "previous weapon group", "previous weapons group", "previous group"],
             
             # Weapon Groups - Secondary
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_1": ["secondary weapon group one", "secondary group one", "select secondary one"],
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_2": ["secondary weapon group two", "secondary group two", "select secondary two"],
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_3": ["secondary weapon group three", "secondary group three", "select secondary three"],
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_4": ["secondary weapon group four", "secondary group four", "select secondary four"],
             "INPUT_ACTION_CYCLE_NEXT_SECONDARY_WEAPONGROUP": ["next secondary weapon group", "next secondary group", "next secondary weapon"],
             "INPUT_ACTION_CYCLE_PREV_SECONDARY_WEAPONGROUP": ["previous secondary weapon group", "previous secondary group", "previous secondary weapon"],
             
             # Weapon Controls
             "INPUT_ACTION_TOGGLE_AIM_ASSIST": ["toggle aim assist", "aim assist"],
             "INPUT_ACTION_NEXT_AMMUNITION": ["next ammunition", "next ammo", "cycle ammunition"],
             "INPUT_ACTION_DEPLOY_COUNTERMEASURES": ["deploy countermeasures", "countermeasures", "flares", "chaff"],
             
             # Map & Navigation
             "INPUT_ACTION_OPEN_MAP": ["map", "galaxy map", "open map"],
             "INPUT_ACTION_UNDOCK": ["undock", "depart"],
             "INPUT_ACTION_INTERACT": ["interact", "use"],
             "INPUT_ACTION_GET_UP": ["get up", "stand up", "leave seat"],
             "INPUT_STATE_NEXT_TARGET": ["next target", "target next"],
             "INPUT_STATE_PREV_TARGET": ["previous target", "target previous"],
             "INPUT_STATE_NEXT_SUBCOMPONENT": ["next subcomponent", "target subcomponent"],
             "INPUT_STATE_PREV_SUBCOMPONENT": ["previous subcomponent", "previous subsystem"],
             "INPUT_STATE_TOGGLE_MOUSE_CURSOR": ["mouse cursor", "toggle mouse"],
             
             # Modes
             "INPUT_STATE_MODE_DIRECT_MOUSE": ["direct mouse mode", "mouse flight"],
             "INPUT_STATE_MODE_STEERING": ["steering mode"],
             
             # Docking
             "INPUT_ACTION_REQUEST_DOCK": ["request docking", "dock", "permission to dock"],
             
             # Views
             "INPUT_STATE_CAMERA_TARGET_VIEW": ["target view", "view target"],
             "INPUT_STATE_CAMERA_EXTERNAL_VIEW": ["external view", "third person"],
             "INPUT_STATE_CAMERA_COCKPIT_VIEW": ["cockpit view", "first person", "reset view"],
             
             # Drones
             "INPUT_ACTION_DRONE_COLLECT": ["collect loot", "drones collect"],
             "INPUT_ACTION_DRONE_ATTACK": ["drones attack", "attack my target"],
             
             # Menus
             "INPUT_ACTION_OPEN_HELP_MENU": ["help"],
             "INPUT_ACTION_OPEN_INFO_MENU": ["info", "information"],
             "INPUT_ACTION_OPEN_PLAYER_MENU": ["player menu", "my empire"],
             "INPUT_ACTION_OPEN_MISSHION_MENU": ["missions", "mission manager"],
        }

        # UI Polish: Friendly Names
        self.friendly_name_map = {
             "INPUT_ACTION_STOP": "Stop Engines",  # Actual action ID in X4 (Backspace key)
             "INPUT_STATE_STOP_SHIP": "Stop Engines (State)",  # Alternate/legacy ID
             "INPUT_STATE_BOOST": "Boost Engines",
             "INPUT_STATE_TRAVEL_MODE": "Travel Mode",
             "INPUT_STATE_SCAN_MODE": "Scan Mode",
             "INPUT_STATE_LONG_RANGE_SCAN": "Long Range Scan",
             "INPUT_STATE_FIRE_PRIMARY": "Fire Primary Weapons",
             "INPUT_STATE_FIRE_SECONDARY": "Fire Secondary Weapons",
             "INPUT_STATE_LOWER_SHIELDS": "Lower Shields", 
             
             # Weapon Groups - Primary
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_1": "Select Primary Weapon Group 1",
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_2": "Select Primary Weapon Group 2",
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_3": "Select Primary Weapon Group 3",
             "INPUT_ACTION_SELECT_PRIMARY_WEAPONGROUP_4": "Select Primary Weapon Group 4",
             "INPUT_ACTION_CYCLE_NEXT_PRIMARY_WEAPONGROUP": "Next Primary Weapon Group",
             "INPUT_ACTION_CYCLE_PREV_PRIMARY_WEAPONGROUP": "Previous Primary Weapon Group",
             
             # Weapon Groups - Secondary
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_1": "Select Secondary Weapon Group 1",
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_2": "Select Secondary Weapon Group 2",
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_3": "Select Secondary Weapon Group 3",
             "INPUT_ACTION_SELECT_SECONDARY_WEAPONGROUP_4": "Select Secondary Weapon Group 4",
             "INPUT_ACTION_CYCLE_NEXT_SECONDARY_WEAPONGROUP": "Next Secondary Weapon Group",
             "INPUT_ACTION_CYCLE_PREV_SECONDARY_WEAPONGROUP": "Previous Secondary Weapon Group",
             
             # Weapon Controls
             "INPUT_ACTION_TOGGLE_AIM_ASSIST": "Toggle Aim Assist",
             "INPUT_ACTION_NEXT_AMMUNITION": "Next Ammunition",
             "INPUT_ACTION_DEPLOY_COUNTERMEASURES": "Deploy Countermeasures",
             
             # Map & Navigation
             "INPUT_ACTION_OPEN_MAP": "Open Galaxy Map",
             "INPUT_ACTION_UNDOCK": "Undock Ship",
             "INPUT_ACTION_INTERACT": "Interact/Use",
             "INPUT_ACTION_GET_UP": "Get Up from Seat",
             "INPUT_STATE_NEXT_TARGET": "Next Target",
             "INPUT_STATE_PREV_TARGET": "Previous Target",
             "INPUT_STATE_NEXT_SUBCOMPONENT": "Next Subcomponent",
             "INPUT_STATE_PREV_SUBCOMPONENT": "Previous Subcomponent",
             "INPUT_STATE_TOGGLE_MOUSE_CURSOR": "Toggle Mouse Cursor",
             "INPUT_STATE_MODE_DIRECT_MOUSE": "Direct Mouse Mode",
             "INPUT_STATE_MODE_STEERING": "Steering Mode",
             "INPUT_ACTION_REQUEST_DOCK": "Request Docking",
             "INPUT_STATE_CAMERA_TARGET_VIEW": "Target View",
             "INPUT_STATE_CAMERA_EXTERNAL_VIEW": "External View",
             "INPUT_STATE_CAMERA_COCKPIT_VIEW": "Cockpit View",
             "INPUT_ACTION_DRONE_COLLECT": "Drones: Collect",
             "INPUT_ACTION_DRONE_ATTACK": "Drones: Attack",
             "INPUT_ACTION_OPEN_PLAYER_MENU": "Player Menu",
             "INPUT_ACTION_OPEN_MISSHION_MENU": "Mission Menu",
             "INPUT_STATE_DECCELERATE": "Stop Engines (Decel)",
             "INPUT_STATE_MATCH_SPEED": "Match Speed",
             "INPUT_ACTION_TOGGLE_TRAVEL_MODE": "Travel Mode",
             "INPUT_ACTION_TOGGLE_SCAN_MODE": "Scan Mode",
             "INPUT_ACTION_TOGGLE_LONGRANGE_SCAN_MODE": "Long Range Scan",
        }
        
        # Interface compatibility
        self.actions = {}

        # Clear inherited Elite Dangerous macros (Fix for "artifacts")
        # And define X4 specific ones
        self.macros = {
            "EscapeVector": {
                "triggers": ["escape", "emergency escape", "flee"],
                "steps": [
                    {"action": "Boost Engines", "delay": 0},      # Boost immediately
                    {"action": "Travel Mode", "delay": 200},      # Engage Travel Mode
                    {"action": "Boost Engines", "delay": 1000}    # Boost again to reach speed
                ]
            },
            "ScanSurroundings": {
                "triggers": ["scan sector", "scan area"],
                "steps": [
                    {"action": "Scan Mode", "delay": 0},
                    {"action": "Long Range Scan", "delay": 1500}  # Hold for 1.5s usually required? 
                                                                  # Note: 'action' currently just presses key. 
                                                                  # Long range scan often requires HOLDING key. 
                                                                  # We might need a "hold" param in macro step later.
                ]
            },
            "CombatReady": {
                "triggers": ["combat ready", "battle stations", "prepare for combat"],
                "steps": [
                    {"action": "Cockpit View", "delay": 0},
                    {"action": "Fire Primary Weapons", "delay": 100},  # Test fire
                    {"action": "Next Target", "delay": 500}
                ]
            },
            "DockingProcedure": {
                "triggers": ["docking procedure", "prepare to dock", "dock now"],
                "steps": [
                    {"action": "Stop Engines", "delay": 0},
                    {"action": "Request Docking", "delay": 1000},
                    {"action": "Lower Shields", "delay": 500}
                ]
            },
            "EmergencyRetreat": {
                "triggers": ["emergency retreat", "get out of here", "escape now"],
                "steps": [
                    {"action": "Travel Mode", "delay": 0},
                    {"action": "Boost Engines", "delay": 500}
                ]
            },
            "DeployDrones": {
                "triggers": ["deploy drones", "launch drones", "drones out"],
                "steps": [
                    {"action": "Drones: Collect", "delay": 0}
                ]
            },
            "AttackMyTarget": {
                "triggers": ["attack my target", "drones attack", "engage target"],
                "steps": [
                    {"action": "Drones: Attack", "delay": 0},
                    {"action": "Fire Primary Weapons", "delay": 200}
                ]
            }
        }
    
    def execute_macro(self, macro_name, input_controller):
        """Override to handle X4 specific macro logic if needed, or use base."""
        # For now, base implementation is fine, but we need to ensure 'action' names match friendly names 
        # because our `action_voice_map` keys are IDs, but macros use Friendly Names or IDs?
        # Base `execute_macro` uses `self.bindings[action_name]`.
        # `self.bindings` is populated with `voice_command` keys.
        # So macro steps should use "voice commands" or we need to resolve Friendly Name -> Voice Command -> Key.
        # Actually base `execute_macro` does:
        # command_name = step['action']
        # if command_name in self.bindings: ...
        
        # Issue: "Boost Engines" is a Friendly Name, NOT a voice command. 
        # "boost" is the voice command.
        # So macro steps should use "boost" OR we need to map Friendly -> Binding.
        # Let's use the primary voice command in the macro definition for now.
        super().execute_macro(macro_name, input_controller)

    def get_friendly_name(self, action_id):
        return self.friendly_name_map.get(action_id, action_id)
        
    def _find_steam_libraries(self):
        """Locate all Steam library folders from libraryfolders.vdf."""
        libraries = []
        # Standard locations
        home = os.path.expanduser("~")
        possible_vdfs = [
            f"{home}/.steam/steam/steamapps/libraryfolders.vdf",
            f"{home}/.local/share/Steam/steamapps/libraryfolders.vdf"
        ]
        
        for vdf_path in possible_vdfs:
            if os.path.exists(vdf_path):
                try:
                    with open(vdf_path, 'r') as f:
                        for line in f:
                            # Simple regex-like grab: "path" "/games/steamgames"
                            if '"path"' in line:
                                parts = line.strip().split('"')
                                # parts: ['', 'path', '\t\t', '/games/steamgames', '']
                                # Find the path part
                                for p in parts:
                                    if len(p) > 2 and p.startswith("/"):
                                        libraries.append(p)
                except Exception as e:
                    print(f"Error reading Steam VDF: {e}")
                    
        # Add defaults just in case
        libraries.append(f"{home}/.local/share/Steam")
        return list(set(libraries))

    def _detect_x4_folder(self):
        """Finds the active X4 user folder, prioritizing Native Linux paths."""
        
        # 1. Native Linux Check (Priority)
        # Paths: ~/.config/Egosoft/X4/{UID}/  or  ~/.config/EgoSoft/X4/{UID}/
        native_candidates = [
            os.path.expanduser("~/.config/Egosoft/X4"),
            os.path.expanduser("~/.config/EgoSoft/X4")
        ]
        
        for native_base in native_candidates:
            if os.path.exists(native_base):
                 # Check subdirs (User ID)
                subdirs = [d for d in os.listdir(native_base) if os.path.isdir(os.path.join(native_base, d)) and d.isdigit()]
                if subdirs:
                    subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(native_base, x)), reverse=True)
                    path = os.path.join(native_base, subdirs[0])
                    print(f"🐧 NATIVE X4 PATH DETECTED: {path}")
                    return path
                # Fallback to direct check
                if os.path.exists(os.path.join(native_base, "inputmap.xml")):
                    print(f"🐧 NATIVE X4 PATH DETECTED (Root): {native_base}")
                    return native_base

        # 2. Proton/Steam Check (Fallback)
        libraries = self._find_steam_libraries()
        
        for lib in libraries:
            # Check Proton Compatdata
            candidate = os.path.join(lib, "steamapps/compatdata/392160/pfx/drive_c/users/steamuser/Documents/Egosoft/X4")
            if os.path.exists(candidate):
                subdirs = [d for d in os.listdir(candidate) if os.path.isdir(os.path.join(candidate, d)) and d.isdigit()]
                if subdirs:
                    subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(candidate, x)), reverse=True)
                    return os.path.join(candidate, subdirs[0])
                if os.path.exists(os.path.join(candidate, "inputmap.xml")):
                    return candidate
                    
        return None

    def sync_profiles(self, direction="proton_to_native"):
        """
        Syncs inputmap profiles between Proton (Windows) and Native (Linux) locations.
        direction: 'proton_to_native' or 'native_to_proton'
        """
        proton_folder = self._detect_x4_folder()
        
        # Detect Native Folder
        # Path: ~/.config/Egosoft/X4/{UID}/
        native_base = os.path.expanduser("~/.config/Egosoft/X4")
        if not os.path.exists(native_base):
             # Try case sensitive variants if needed, or check 'EgoSoft'
             native_base = os.path.expanduser("~/.config/EgoSoft/X4")
        
        native_folder = None
        if os.path.exists(native_base):
            # Find UID folder
            subdirs = [d for d in os.listdir(native_base) if os.path.isdir(os.path.join(native_base, d)) and d.isdigit()]
            if subdirs:
                subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(native_base, x)), reverse=True)
                native_folder = os.path.join(native_base, subdirs[0])
            else:
                # Fallback to root if UID folder missing
                native_folder = native_base
                
        if not proton_folder or not native_folder:
            return False, "Could not locate both Proton and Native folders."
            
        src = proton_folder if direction == "proton_to_native" else native_folder
        dst = proton_folder if direction != "proton_to_native" else native_folder
        
        # Copy inputmap*.xml files
        import shutil
        count = 0
        try:
            for f in os.listdir(src):
                if f.startswith("inputmap") and f.endswith(".xml"):
                    src_file = os.path.join(src, f)
                    dst_file = os.path.join(dst, f)
                    
                    # Backup if exists
                    if os.path.exists(dst_file):
                        shutil.copy2(dst_file, dst_file + ".bak")
                        
                    shutil.copy2(src_file, dst_file)
                    count += 1
            return True, f"Synced {count} profiles from {direction}."
        except Exception as e:
            return False, f"Sync failed: {e}"

    def load_bindings(self):
        if not X4XMLParser:
            print("❌ Security Error: X4XMLParser module missing (defusedxml dependency?)")
            return
            
        target_path = self.custom_bindings_path
        
        # Auto-Detect if no custom path
        if not target_path:
             detected_folder = self._detect_x4_folder()
             if detected_folder:
                 # Default to standard inputmap.xml
                 target_path = os.path.join(detected_folder, "inputmap.xml")
                 print(f"✨ Auto-Detected X4 Path: {target_path}")
                 
                 # Bonus: List usage of other profiles
                 # Check for inputmap_1.xml etc
                 try:
                     files = os.listdir(detected_folder)
                     profiles = [f for f in files if f.startswith("inputmap") and f.endswith(".xml")]
                     if len(profiles) > 1:
                         print(f"   Found {len(profiles)} X4 input profiles in {detected_folder}: {profiles}")
                 except: pass
                 
             else:
                 # Fallback to hardcoded defaults
                 target_path = self.default_path
        
        # Modular Framework: If not set in code, fall back to what user set in GUI (active_binds_path)
        if not target_path and self.active_binds_path:
             target_path = self.active_binds_path
             
        if target_path and os.path.exists(target_path):
            print(f"📂 Parsing X4 Bindings: {target_path}")
            parser = X4XMLParser()
            self.actions = parser.parse(target_path)
            self.active_binds_path = target_path
            
            # Populate self.bindings (Voice Command -> Key)
            self.bindings = {}
            bound_count = 0
            
            for action_id, voice_commands in self.action_voice_map.items():
                if action_id in self.actions:
                    key_data = self.actions[action_id]
                    # key_data is (Key, Mods)
                    # X4 Parser returns (Key, [])
                    if key_data and key_data[0]:
                        final_key = key_data[0] # Key string
                        # Add to bindings for EACH voice alias
                        for alias in voice_commands:
                            self.bindings[alias] = (final_key, [])
                        bound_count += 1
            
            print(f"✅ X4 Profile Loaded: {bound_count} actions bound to voice commands.")
            self._merge_custom_commands()
            return True
        else:
            print(f"⚠️ X4 Bindings file not found: {target_path}")
            # Try to help user diagnose
            print("   (Tip: Use 'Edit Game' to browse to 'steamapps/compatdata/392160/.../Documents/Egosoft/X4/UID/')")
            return False

class EliteDangerousProfile(GameProfile):
    def __init__(self, name="Elite Dangerous", discriminator=None, default_path_override=None, group=None):
        super().__init__(name, path_discriminator=discriminator, group=group)
        self.process_name = "EliteDangerous64.exe"
        self.default_process_name = "EliteDangerous64.exe"
        self.default_path = os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings")
        
        # Override default path if provided (e.g. for custom profiles pointing to a specific file or folder)
        if default_path_override:
            # If it's a file, we might treating it as a reference or active bind? 
            # ED usually scans a folder. But if user specifies a file, maybe we should use it?
            # For now, let's assume if they provide a path, it's the Custom Bindings Path.
            self.custom_bindings_path = default_path_override

        # Find latest binds file if default path is a folder
        self._resolve_active_binds_path()
    
        # Interface compatibility
        self.actions = {}

    def _resolve_active_binds_path(self):
        """Locates the most relevant bindings file."""
        target_path = self.custom_bindings_path if self.custom_bindings_path else self.default_path
        
        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                # Search for *.binds or *.3.0.binds, sort by modified time
                try:
                    files = [os.path.join(target_path, f) for f in os.listdir(target_path) if f.endswith(".binds")]
                    if files:
                        # Priorities: .3.0.binds > .binds? Or just latest modified?
                        # ED usually updates the file with the preset name.
                        # Let's pick latest modified.
                        files.sort(key=os.path.getmtime, reverse=True)
                        self.active_binds_path = files[0]
                except Exception as e:
                    print(f"Error scanning ED binds dir: {e}")
            else:
                 self.active_binds_path = target_path

    def load_bindings(self):
        """Parses the active Elite Dangerous bindings file."""
        if not EDXMLParser:
            print("❌ EDXMLParser not available.")
            return

        binding_file = self.active_binds_path
        if not binding_file or not os.path.exists(binding_file):
            # Try to resolve again just in case
            self._resolve_active_binds_path()
            binding_file = self.active_binds_path
        
        if not binding_file or not os.path.exists(binding_file):
            print(f"⚠️ No Binding File found for Elite Dangerous at {self.custom_bindings_path or self.default_path}")
            return

        print(f"📂 Parsing ED Bindings: {binding_file}")
        parser = EDXMLParser()
        self.actions = parser.parse(binding_file)
        
        # --- 1. Define Defaults & Maps (MOVED UP) ---
        
        # Elite Specific Categories
        self.categories = ["All", "General", "Ship", "SRV", "On Foot"]
        
        # Mapping known ED action names to nice voice commands
        self.action_voice_map = {
            "Landing Gear": ["landing gear", "gear", "toggle gear", "deploy landing gear", "retract landing gear", "deploy gear", "retract gear"],
            "Lights": ["lights", "ship lights", "toggle lights"],
            "Night Vision": ["night vision", "vision", "toggle night vision"],
            "Hardpoints": ["deploy hardpoints", "retract hardpoints", "hardpoints", "deploy hard points", "retract hard points", "open hard points", "close hard points", "toggle hard points", "toggle hardpoints"],
            "Frame Shift Drive": ["jump", "engage jump", "frameshift drive", "engage frameshift drive", "engage fsd", "fsd", "engage drive"],
            "Supercruise": ["supercruise", "engage supercruise"],
            "Hyperspace": ["hyperspace", "engage hyperspace"],
            "Galaxy Map": ["galaxy map", "map", "open galaxy map", "open map"],
            "System Map": ["system map", "open system map"],
            "TargetNextRouteSystem": ["next system", "route", "target next system", "target route"],
            "SelectTarget": ["target ahead", "select target", "select target ahead", "target"],
            "SelectTargetsTarget": ["target ahead (secondary)", "select target (secondary)"], 
            "SelectHighestThreat": ["target nearest enemy", "target nearest", "target highest threat", "target threat", "target hostile"],
            "CycleNextTarget": ["next target", "cycle target"],
            "CycleNextHostileTarget": ["next hostile", "hostile", "cycle hostile"],
            "DeployHeatSink": ["heatsink", "deploy heatsink", "fire heatsink"],
            "UseShieldCell": ["shield cell", "cell", "fire shield cell", "use shield cell"],
            "FireChaffLauncher": ["chaff", "fire chaff", "deploy chaff"],
            "ChargeECM": ["ecm", "electronic countermeasures", "fire ecm"],
            "CycleFireGroupNext": ["next fire group", "next group", "cycle fire group", "secondary armaments", "secondary fire group", "next weapon", "switch weapon", "cycle weapon", "next five group", "next five groups"], 
            "CycleFireGroupPrevious": ["previous fire group", "previous group"],
            "OrderRequestDock": ["request docking", "docking request", "dock request"], 
            
            # --- Power Distributor ---
            "IncreaseEnginesPower": ["power to engines", "engines", "increase engines"],
            "IncreaseWeaponsPower": ["power to weapons", "weapons", "increase weapons"],
            "IncreaseSystemsPower": ["power to systems", "systems", "increase systems", "shields", "power to shields"],
            "ResetPowerDistribution": ["balance power", "reset power", "power reset"],
            
            # --- Subsystems ---
            "CycleNextSubsystem": ["next subsystem", "target power plant", "target drive"],
            "CyclePreviousSubsystem": ["previous subsystem", "previous sub"], 
            
            # --- Flight & Systems ---
            "Flight Assist": ["flight assist", "fa off", "fa on", "toggle flight assist"],
            "Boost": ["boost", "engine boost", "afterburner"],
            "Cargo Scoop": ["cargo scoop", "scoop", "toggle scoop"],
            "ToggleRotationCorrect": ["rotational correction", "rotation"],
            "OrbitLinesToggle": ["orbit lines", "lines", "toggle orbit lines"],
            "HMDReset": ["reset hmd", "center hmd", "center view"],
            "PlayerHUDModeToggle": ["hud mode", "analysis mode", "combat mode", "switch mode"],
            "ExplorationFSSEnter": ["fss", "scanner", "full spectrum scanner"],
            "ExplorationSAAEnter": ["dss", "probes", "surface scanner"],
            
            # --- Fighter & Orders ---
            "OrderDefend": ["fighter defend", "defend"],
            "OrderAggressive": ["fighter attack", "attack", "sic em"],
            "OrderFollow": ["fighter follow", "follow", "form up"],
            "OrderHoldFire": ["fighter hold", "hold fire", "cease fire"],
            "OrderHoldPosition": ["fighter hold position", "stay here"],
            "OrderRecall": ["fighter recall", "recall fighter", "dock fighter"],
            
            # --- Camera ---
            "PhotoCameraToggle": ["camera", "external camera", "toggle camera", "selfie"],
            "PhotoCameraToggle_Buggy": ["srv camera", "buggy camera"],
            "VanityCameraScrollLeft": ["camera next"],
            "VanityCameraScrollRight": ["camera previous"], 
            
            # --- SRV Controls ---
            "ToggleDriveAssist": ["drive assist", "toggle drive assist"],
            "AutoBreakBuggyButton": ["handbrake", "brake", "toggle handbrake"],
            "HeadlightsBuggyButton": ["srv lights", "buggy lights"],
            "ToggleBuggyTurretButton": ["turret", "toggle turret"],
            "RecallDismissShip": ["recall ship", "dismiss ship", "call ship"],
            
            # --- On Foot (Odyssey) ---
            "HumanoidToggleFlashlight": ["flashlight", "torch", "toggle flashlight"],
            "HumanoidSelectPrimaryWeapon": ["primary weapon", "rifle", "assault rifle"],
            "HumanoidSelectSecondaryWeapon": ["secondary weapon", "pistol", "sidearm"],
            "HumanoidSelectUtilityWeapon": ["utility tool", "utility"],
            "HumanoidSwitchToRechargeTool": ["energylink", "recharge tool"],
            "HumanoidSwitchToCompAnalyser": ["analyzer", "sampler", "genetic sampler"],
            "HumanoidItemWheelButton": ["item wheel", "wheel"],
            "HumanoidUseMedkit": ["medkit", "heal", "use medkit"],
            "HumanoidUseEnergyLink": ["recharge suit", "use energylink"],
            "HumanoidUseShieldCell": ["foot shield", "personal shield"],
            "HumanoidThrowGrenade": ["grenade", "throw grenade", "humanoid throw grenade button"],
            "HumanoidMeleeButton": ["melee", "punch", "bash", "humanoid melee button"],
            "HumanoidClearAuthorityLevel": ["drop profile", "clear profile"],
            "HumanoidHealthPack": ["medkit", "health pack"],
            "HumanoidBattery": ["battery", "energy cell"],
            "HumanoidCrouchButton": ["crouch", "kneel", "humanoid crouch button"],
            "HumanoidJumpButton": ["jump", "humanoid jump button"],
            "HumanoidPrimaryInteractButton": ["primary interact", "interact", "humanoid primary interact button"],
            "HumanoidSecondaryInteractButton": ["secondary interact", "humanoid secondary interact button"],
            "HumanoidItemWheelButton": ["item wheel", "wheel", "humanoid item wheel button"],
            "HumanoidEmoteWheelButton": ["emote wheel", "emote", "humanoid emote wheel button"],
            "HumanoidUtilityWheelCycleMode": ["utility cycle", "humanoid utility wheel cycle mode"],
            "HumanoidReloadButton": ["reload", "humanoid reload button"],
            "HumanoidSelectPrimaryWeaponButton": ["select primary", "humanoid select primary weapon"],
            "HumanoidSelectSecondaryWeaponButton": ["select secondary", "humanoid select secondary weapon"],
            "HumanoidSelectUtilityWeaponButton": ["select utility", "humanoid select utility weapon"],

            # --- UI Navigation (Primitives for Macros) ---
            "UI_Up": ["menu up", "up"],
            "UI_Down": ["menu down", "down"],
            "UI_Left": ["menu left", "left", "previous tab"],
            "UI_Right": ["menu right", "right", "next tab"],
            "UI_Select": ["menu select", "select", "enter", "confirm"],
            "UI_Back": ["menu back", "back", "cancel"],
            "CycleNextPanel": ["next panel", "tab next"],
            "CyclePreviousPanel": ["previous panel", "tab previous"],
            "CycleNextPage": ["next page", "cycle next page"],
            "CyclePreviousPage": ["previous page", "cycle previous page"],
            "UIFocus": ["ui focus", "focus"],
            "QuickCommsPanel": ["comms", "chat", "communications"],
            "External Panel": ["target panel", "left panel", "external panel"],
            "Internal Panel": ["system panel", "right panel", "internal panel"], 
            "Role Panel": ["role panel", "bottom panel", "engineer panel"],
            "Comms Panel": ["comms panel", "chat panel"],
            "Galaxy Map": ["galaxy map", "map", "open galaxy map", "open map"],
            "System Map": ["system map", "open system map"],
            
            # --- Wings / Team ---
            "TargetWingman0": ["target wingman 1", "target leader"],
            "TargetWingman1": ["target wingman 2"],
            "TargetWingman2": ["target wingman 3"],
            "SelectTargetsTarget": ["target wingman target", "assist wingman"],
            "WingNavLock": ["nav lock", "wing nav lock"],

            # --- Multi-Crew ---
            "MultiCrewToggleMode": ["multicrew mode", "toggle mode"],
            "MultiCrewPrimaryFire": ["gunner fire"],
            "MultiCrewSecondaryFire": ["gunner missile"],
        }
        
        # Mapping: Tkinter KeySyms -> Elite Dangerous XML Key Names
        self.TK_TO_ED_MAP = {
            "return": "Key_Enter", "enter": "Key_Enter",
            "space": "Key_Space",
            "backspace": "Key_Backspace",
            "tab": "Key_Tab",
            "escape": "Key_Escape",
            "delete": "Key_Delete",
            "insert": "Key_Insert",
            "home": "Key_Home",
            "end": "Key_End",
            "prior": "Key_PageUp", "page_up": "Key_PageUp",
            "next": "Key_PageDown", "page_down": "Key_PageDown",
            "up": "Key_UpArrow",
            "down": "Key_DownArrow",
            "left": "Key_LeftArrow",
            "right": "Key_RightArrow",
            "shift_l": "Key_LeftShift", "shift_r": "Key_RightShift",
            "control_l": "Key_LeftControl", "control_r": "Key_RightControl",
            "alt_l": "Key_LeftAlt", "alt_r": "Key_RightAlt",
            "caps_lock": "Key_CapsLock",
            "num_lock": "Key_NumLock",
            "scroll_lock": "Key_ScrollLock",
            "f1": "Key_F1", "f2": "Key_F2", "f3": "Key_F3", "f4": "Key_F4",
            "f5": "Key_F5", "f6": "Key_F6", "f7": "Key_F7", "f8": "Key_F8",
            "f9": "Key_F9", "f10": "Key_F10", "f11": "Key_F11", "f12": "Key_F12",
            "minus": "Key_Minus", "equal": "Key_Equals",
            "bracketleft": "Key_LeftBracket", "bracketright": "Key_RightBracket",
            "semicolon": "Key_Semicolon", "apostrophe": "Key_Apostrophe",
            "comma": "Key_Comma", "period": "Key_Period", "slash": "Key_Slash",
            "backslash": "Key_BackSlash",
            "grave": "Key_Grave",
            "0": "Key_0", "1": "Key_1", "2": "Key_2", "3": "Key_3", "4": "Key_4",
            "5": "Key_5", "6": "Key_6", "7": "Key_7", "8": "Key_8", "9": "Key_9",
        }
        # Add a-z -> Key_A
        for char in "abcdefghijklmnopqrstuvwxyz":
            self.TK_TO_ED_MAP[char] = f"Key_{char.upper()}"
        
        # Virtual Tag Map: Friendly Name -> List of XML Tags that trigger it
        # This allows us to unify legacy/modern tags under one clean UI name.
        self.virtual_tag_map = {
            "External Panel": ["FocusLeftPanel", "TargetPanel"],
            "Internal Panel": ["FocusRightPanel", "SystemPanel"],
            "Role Panel": ["FocusRadarPanel", "RolePanel"],
            "Comms Panel": ["FocusCommsPanel", "QuickCommsPanel"],
            "Galaxy Map": ["GalaxyMapOpen"],
            "System Map": ["SystemMapOpen"],
            "Landing Gear": ["LandingGearToggle", "LandingGear"], # Support both Toggle and State
            "Cargo Scoop": ["ToggleCargoScoop", "CargoScoop"],
            "Flight Assist": ["ToggleFlightAssist", "FlightAssist"],
            "Boost": ["UseBoostJuice"], # New mapping
            "Frame Shift Drive": ["HyperSuperCombination", "Supercruise", "Hyperspace"],
            
            # Missing Common Bindings
            "Lights": ["ShipSpotLightToggle", "Headlights"],
            "Night Vision": ["NightVisionToggle"],
            "Hardpoints": ["DeployHardpointToggle", "DeployHardpoints"],
            "DeployHeatSink": ["DeployHeatSink"], # Self-referential for safety if Friendly Name == Tag
            "UseShieldCell": ["UseShieldCell"],
            "FireChaffLauncher": ["FireChaffLauncher"],
            "ChargeECM": ["ChargeECM"],
            "TargetNextRouteSystem": ["TargetNextRouteSystem"],
            "SelectTarget": ["SelectTarget"],
            "SelectHighestThreat": ["SelectHighestThreat"],
            "CycleNextTarget": ["CycleNextTarget"],
            "CycleNextHostileTarget": ["CycleNextHostileTarget"],
            "Supercruise": ["Supercruise"],
            "Hyperspace": ["Hyperspace"],
            "Galaxy Map": ["GalaxyMapOpen"],
            "System Map": ["SystemMapOpen"],
            
            # Fix for rotation and orbit lines - map friendly names to actual XML tags
            "ToggleRotationCorrect": ["DisableRotationCorrectToggle"],
            "OrbitLinesToggle": ["OrbitLinesToggle"],  # This one is correct already
        }
        
        # Default Macros (Starter Pack)
        # Uses ONLY verified action names from action_voice_map
        if not self.macros:
            self.macros = {
                "RequestDocking": {
                    "triggers": ["request docking", "dock", "docking request"],
                    "steps": [
                        {"action": "External Panel", "delay": 500},  # Open Left Panel (Targets Navigation Tab 1 by default, but remembers last)
                        {"action": "CyclePreviousPanel", "delay": 100}, # Reset Tab (Force left)
                        {"action": "CyclePreviousPanel", "delay": 100},
                        {"action": "CyclePreviousPanel", "delay": 100},
                        {"action": "CycleNextPanel", "delay": 200},     # Tab to Transactions
                        {"action": "CycleNextPanel", "delay": 200},     # Tab to Contacts (Tab 3)
                        {"action": "UI_Select", "delay": 200},          # Select Station (Assuming top of list)
                        {"action": "UI_Down", "delay": 200},            # Move down to 'Request Docking' (usually 2nd item)
                        {"action": "UI_Select", "delay": 200},          # Execute Request
                        {"action": "External Panel", "delay": 200}      # Close Panel
                    ]
                },
                "CombatReady": {
                    "triggers": ["combat ready", "battle stations", "prepare for combat"],
                    "steps": [
                        {"action": "Hardpoints", "delay": 300},              # Deploy hardpoints
                        {"action": "ResetPowerDistribution", "delay": 200},  # Balance power (4-4-4)
                        {"action": "SelectHighestThreat", "delay": 300}      # Target highest threat
                    ]
                },
                "LandingMode": {
                    "triggers": ["landing mode", "prepare landing", "landing prep"],
                    "steps": [
                        {"action": "Hardpoints", "delay": 300},      # Retract hardpoints
                        {"action": "Landing Gear", "delay": 500},    # Deploy landing gear
                        {"action": "Lights", "delay": 200}           # Enable lights
                    ]
                },
                "SupercruisePrep": {
                    "triggers": ["prepare supercruise", "supercruise prep", "travel mode"],
                    "steps": [
                        {"action": "Hardpoints", "delay": 300},      # Retract hardpoints
                        {"action": "Landing Gear", "delay": 300},    # Retract landing gear
                        {"action": "Cargo Scoop", "delay": 300},     # Retract cargo scoop
                        {"action": "Supercruise", "delay": 200}      # Engage supercruise
                    ]
                },
                "BoostedEscape": {
                    "triggers": ["emergency escape", "boosted escape", "gtfo"],
                    "steps": [
                        {"action": "FireChaffLauncher", "delay": 100},  # Chaff
                        {"action": "Boost", "delay": 100},              # Boost (UseBoostJuice)
                        {"action": "Boost", "delay": 1000},             # Boost again
                        {"action": "DeployHeatSink", "delay": 200}      # Heat sink
                    ]
                },
                "SilentRunningCombat": {
                    "triggers": ["silent running", "go dark", "go silent", "button up"],
                    "steps": [
                        {"action": "ToggleButtonUpInput", "delay": 200},  # Silent running ON ("Button Up")
                        {"action": "Hardpoints", "delay": 300},           # Deploy hardpoints
                        {"action": "DeployHeatSink", "delay": 200}        # Fire heat sink
                    ]
                }
            }
            
        # Load custom commands (overwrites defaults if file exists)
        if not self.load_commands():
            # If no file exists, save the defaults we just defined
            self.save_commands()
            
        # Load macros (merges with defaults or overwrites)
        if self.load_macros():
            pass
        else:
            self.save_macros()

        # Map actions to voice commands
        self.bindings = {}
        bound_count = 0
        
        for action_id, voice_commands in self.action_voice_map.items():
            # Resolve potential XML tags for this action ID (Friendly Name)
            tags_to_check = [action_id]
            if hasattr(self, 'virtual_tag_map') and action_id in self.virtual_tag_map:
                tags_to_check.extend(self.virtual_tag_map[action_id])
            


            found = False
            for tag in tags_to_check:
                if tag in self.actions:
                    key, mods = self.actions[tag]
                    for alias in voice_commands:
                        self.bindings[alias] = (key, mods)
                    bound_count += 1
                    found = True
                    break # Stop after finding the first valid binding match
            
            if not found and action_id in self.actions:
                 # Fallback if action_id match strictly (already covered by first item in tags_to_check, but safe to keep)
                 pass
                
        print(f"✅ ED Profile Loaded: {bound_count} actions bound.")
        self._merge_custom_commands()
        

    def is_running(self):
        # Check for EliteDangerous executable in process list
        # Also check for steamtinkerlaunch as proxy?
        # Robust check: look for cmdline containing "Elite Dangerous"
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = proc.info['cmdline']
                if cmd:
                    cmd_str = " ".join(cmd)
                    if "EliteDangerous" in cmd_str: # Binary name usually 'EliteDangerous64.exe'
                        return True
                    # Also check AppID for Steam launches
                    if "359320" in cmd_str and "steamtinkerlaunch" not in cmd_str: 
                        # Be careful not to match the launcher script itself if the game isn't running?
                        # Actually process check for binary is best.
                        if "EliteDangerous64.exe" in cmd_str:
                            return True
            except:
                pass
        return False

    def get_category(self, action_name):
        """Returns the UI category for a given action."""
        if not action_name: return "General"
        action_name = action_name.lower()
        
        # SRV Keywords
        srv_keywords = ["buggy", "driveassist", "srv", "turret", "driving", "vehicle"]
        if any(k in action_name for k in srv_keywords):
            return "SRV"
            
        # On Foot Keywords
        foot_keywords = ["humanoid", "foot", "onfoot", "rifle", "pistol", "suit", "energylink", "consumable", "grenade", "health", "battery"]
        if any(k in action_name for k in foot_keywords):
            return "On Foot"
            
        # General Keywords
        general_keywords = ["map", "ui", "microphone", "interface", "menu", "playlist", "mode", "switch", "binding"]
        if any(k in action_name for k in general_keywords):
            return "General"
            
        # Default to Ship for everything else (flight, weapons, etc.)
        return "Ship"



    def update_binding(self, action_name, key_data):
        """
        Updates the key binding for a given action in the current .binds file.
        action_name: The Friendly Name or Tag (e.g. "Landing Gear" or "LandingGearToggle")
        key_data: {"key": "Key_A", "mods": ["Key_LeftShift"]}
        """
        if not self.active_binds_path:
            return False, "No active bindings file found."
            
        # 1. Resolve to XML Tag(s)
        # If it's a friendly name, we might have multiple tags. 
        # But we only need to update ONE of them to make it work.
        # However, usually we should check if one is already bound and update that one.
        # Or look for the 'Keyboard' one.
        
        tags_to_check = self.virtual_tag_map.get(action_name, [action_name])
        
        try:
            tree = ET.parse(self.active_binds_path)
            root = tree.getroot()
            
            target_node = None
            target_tag = None
            
            # Find the best tag to update
            for tag in tags_to_check:
                node = root.find(tag)
                if node is not None:
                     target_node = node
                     target_tag = tag
                     break
                     
            if target_node is None:
                 print(f"⚠️ Tag not found in XML: {tags_to_check}")
                 # Maybe generic "Custom" bind file didn't include it?
                 # We should create it? For now, fail safely.
                 return False, f"Game setting '{action_name}' not found in file."
                 
            # 2. Check Slots (Primary / Secondary)
            primary = target_node.find('Primary')
            secondary = target_node.find('Secondary')
            
            slot_to_use = None
            
            # Helper to check if a slot is 'free' or 'keyboard'
            def is_available(slot):
                if slot is None: return True # Wait, if missing, we create it? Usually XML has empty tags <Primary Device="{NoDevice}" Key="" />
                dev = slot.get('Device')
                return dev == "{NoDevice}" or dev == "Keyboard"
                
            # Logic:
            # 1. If Primary is Keyboard or Empty, use Primary.
            # 2. If Primary is Joystick/Mouse, check Secondary.
            # 3. If Secondary is Keyboard/Empty, use Secondary.
            # 4. If both are Joystick, FAIL (don't overwrite joystick).
            
            if is_available(primary):
                slot_to_use = primary
                print(f"   -> Using Primary slot.")
            elif is_available(secondary):
                slot_to_use = secondary
                print(f"   -> Primary occupied by {primary.get('Device')}. Using Secondary slot.")
            else:
                return False, f"All slots for '{action_name}' are occupied by non-keyboard devices (Joystick/Mouse). Safety abort."
                
            # 3. Apply Update
            slot_to_use.set('Device', 'Keyboard')
            slot_to_use.set('Key', key_data['key'])
            
            # Remove old modifiers
            for mod in slot_to_use.findall('Modifier'):
                slot_to_use.remove(mod)
                
            # Add new modifiers
            for mod_key in key_data.get('mods', []):
                new_mod = ET.SubElement(slot_to_use, 'Modifier')
                new_mod.set('Device', 'Keyboard')
                new_mod.set('Key', mod_key)
                
            # 4. Save
            tree.write(self.active_binds_path, encoding='UTF-8', xml_declaration=True)
            print(f"✅ Updated binding for {action_name} in {self.active_binds_path}")
            
            # 5. Reload in-memory
            self.load_bindings()
            return True, "Binding updated successfully."
            
        except Exception as e:
            print(f"❌ Error updating binding: {e}")
            import traceback
            traceback.print_exc()
            return False, str(e)

    def unbind_action(self, action_name):
        """
        Unbinds a specific action (sets Device="{NoDevice}" and Key="").
        """
        if not self.active_binds_path: return False
        
        tags_to_check = self.virtual_tag_map.get(action_name, [action_name])
        
        try:
            tree = ET.parse(self.active_binds_path)
            root = tree.getroot()
            
            target_node = None
            for tag in tags_to_check:
                node = root.find(tag)
                if node is not None:
                     target_node = node
                     break
            
            if target_node is None: return True # Already effectively unbound if missing
            
            # Unbind both Primary and Secondary if they are Keyboard?
            # Or just unbind the one that correlates to our key?
            # Safest: Unbind any keyboard slot.
            
            updated = False
            for slot_name in ['Primary', 'Secondary']:
                slot = target_node.find(slot_name)
                if slot is not None and slot.get('Device') == 'Keyboard':
                    slot.set('Device', '{NoDevice}')
                    slot.set('Key', '')
                    # Remove modifiers
                    for mod in slot.findall('Modifier'):
                        slot.remove(mod)
                    updated = True
                    
            if updated:
                tree.write(self.active_binds_path, encoding='UTF-8', xml_declaration=True)
                self.load_bindings()
                print(f"✅ Unbound action: {action_name}")
                
            return True
            
        except Exception as e:
            print(f"❌ Error unbinding: {e}")
            return False

    def check_collisions(self, key_data, proposed_action=None):
        """
        Checks if the proposed key_data is already bound to another action.
        Returns a list of conflicting Action Names (Friendly Names).
        key_data: {'key': 'Key_L', 'mods': ['Key_LeftShift']}
        proposed_action: Name of the action we are binding (for context checking)
        """
        collisions = []
        
        target_key = key_data['key']
        target_mods = set(key_data['mods'])
        
        # Determine Context of Proposed Action
        proposed_cat = self.get_category(proposed_action) if proposed_action else "General"
        
        for action_name, (bound_key, bound_mods) in self.actions.items():
            # Skip self
            if action_name == proposed_action: continue
            
            # Check for exact match
            if bound_key == target_key:
                # Check mods
                if set(bound_mods) == target_mods:
                    # CONTEXT CHECK
                    # If categories are different, and neither is "General", it's allowed.
                    cat = self.get_category(action_name)
                    
                    # Conflict if:
                    # 1. Same Category (Ship vs Ship)
                    # 2. One is General (General vs Ship) -> General overrides/conflicts with all
                    
                    if proposed_cat == cat or proposed_cat == "General" or cat == "General":
                         collisions.append(f"{action_name} ({cat})")
                    
        return collisions



class GenericGameProfile(GameProfile):
    """
    Profile for any game/application without specific parser logic.
    Bindings are manually managed via the GUI.
    """
    def __init__(self, name, process_name=None, discriminator=None, reference_path=None, group=None):
        super().__init__(name, path_discriminator=discriminator, group=group)
        self.process_name = process_name if process_name else []
        self.reference_path = reference_path # Path to external bindings for reference
        self.active_binds_path = None # No external bind file
        
        # Use reference_path as manual_bindings_file if set (User Control)
        if self.reference_path:
             expanded_path = os.path.expanduser(self.reference_path)
             if os.path.isdir(expanded_path):
                  # If folder, create standard filename inside it
                  self.manual_bindings_file = os.path.join(expanded_path, f"{name.lower().replace(' ', '_')}_bnd.json")
             else:
                  # Assume it's the target file
                  self.manual_bindings_file = expanded_path
        else:
             # Default to internal storage
             self.manual_bindings_file = os.path.expanduser(f"~/.local/share/tuxtalks/games/{name.lower().replace(' ', '_')}_bnd.json")
        
        # Load any saved manual bindings
        self.load_bindings()
        
    def load_bindings(self):
        # Load simple JSON: Action -> [Key, Mods] or similar
        self.actions = {}
        if os.path.exists(self.manual_bindings_file):
            try:
                import json
                with open(self.manual_bindings_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        # Empty file is valid - just no bindings yet
                        print(f"📖 Bindings file is empty for {self.name} (new profile)")
                        return
                    data = json.loads(content)
                    # Data format: {"Unlock Target": ["t", []], "Fire": ["1", []]}
                    for action, (key, mods) in data.items():
                        self.actions[action] = (key, mods)
                self._merge_custom_commands()
                print(f"📖 Loaded {len(self.actions)} generic bindings for {self.name}")
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error in bindings file: {e}")
            except Exception as e:
                print(f"❌ Error loading generic bindings: {e}")

    def save_bindings(self):
        try:
            import json
            os.makedirs(os.path.dirname(self.manual_bindings_file), exist_ok=True)
            # Save self.actions
            with open(self.manual_bindings_file, 'w') as f:
                json.dump(self.actions, f, indent=4)
            print(f"💾 Saved generic bindings for {self.name}")
        except Exception as e:
            print(f"❌ Error saving generic bindings: {e}")

    def update_binding(self, action, key_data):
        # Override to save to local JSON
        try:
            self.actions[action] = (key_data['key'], key_data['mods'])
            self.save_bindings()
            return True, f"Bound '{action}' successfully."
        except Exception as e:
            return False, str(e)

    def get_friendly_name(self, action):
        return action # Direct mapping

class GameManager:
    def __init__(self):
        self.profiles = []
        self.active_profile = None # Init before loading
        self.active_macro_profile = "Built-in"  # Phase 1c: Default macro source
        self.game_mode_enabled = False
        
        self.load_profiles() # Load from JSON (restores active state)
        
        # Determine starting profile (fallback if none active)
        if not self.active_profile and self.profiles:
            self.active_profile = self.profiles[0]
            # Try to load last active profile from config if possible (future enhancement)
        
        # LAL Framework: Load content packs
        if LALManager:
            try:
                self.lal_manager = LALManager()
            except Exception as e:
                print(f"⚠️ Failed to initialize LAL Manager: {e}")
                self.lal_manager = None
        else:
            self.lal_manager = None
            
    def load_profiles(self):
        """Loads profiles from user_games.json or initializes defaults."""
        defaults = [
            EliteDangerousProfile(),
            X4Profile(
                name="X4 Foundations (Steam)", 
                discriminator="steamapps",
                default_path_override=os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/392160/pfx/drive_c/users/steamuser/Documents/Egosoft/X4/inputmap.xml"),
                group="X4 Foundations"
            ),
            X4Profile(
                name="X4 Foundations (GOG)", 
                discriminator="X4", # Broad discriminator since 'games2' is custom. We rely on Steam profile catching 'spamapps' first.
                default_path_override=os.path.expanduser("~/Games/gog/x4-foundations/drive_c/users/steamuser/Documents/Egosoft/X4/inputmap.xml"),
                group="X4 Foundations"
            )
        ]

        # Only load from file if profiles haven't been set yet (e.g., by a previous call or init)
        if not self.profiles:
            try:
                print(f"DEBUG: Loading profiles from: {USER_GAMES_FILE}")
                if os.path.exists(USER_GAMES_FILE):
                     with open(USER_GAMES_FILE, 'r') as f:
                         data = json.load(f)
                    
                self.profiles = []
                for entry in data:
                    try:
                        p = None
                        group = entry.get('group')
                        p_type = entry.get('type')
                        name = entry.get('name')
                        
                        if not name:
                             print("DEBUG: Skipping unnamed profile entry.")
                             continue
                        
                        if p_type == 'EliteDangerous':
                            group = "Elite Dangerous" if not group else group
                            p = EliteDangerousProfile(
                                name=name,
                                discriminator=entry.get('discriminator'),
                                default_path_override=entry.get('bindings_path'),
                                group=group
                            )
                            # Ensure we restore the process name logic if saved
                            if 'process_name' in entry:
                                p.process_name = entry['process_name']
                        
                        elif p_type == 'X4':
                            group = "X4 Foundations" if not group else group
                            p = X4Profile(
                                name=name,
                                discriminator=entry.get('discriminator'),
                                default_path_override=entry.get('bindings_path'),
                                group=group
                            )
                            # Ensure we restore the process name logic if saved
                            if 'process_name' in entry:
                                p.process_name = entry['process_name']
                            
                        elif p_type == 'Generic':
                            # Migration Heuristics
                            if not group:
                                # Try to split "Game (Variant X)"
                                if " (Variant" in name:
                                    try:
                                        group = name.split(" (Variant")[0]
                                    except:
                                        group = name
                                else:
                                    group = name
                            
                            p = GenericGameProfile(
                                name=name,
                                process_name=entry.get('process_name'),
                                discriminator=entry.get('discriminator'),
                                reference_path=entry.get('reference_path'),
                                group=group
                            )
                        
                        # Common restoration for all types
                        if p:
                            if 'runtime_env' in entry:
                                p.runtime_env = entry['runtime_env']
                            
                            # Restore Macro Profile Selection
                            if 'macro_profile' in entry:
                                p.selected_macro_profile = entry['macro_profile']
                            else:
                                p.selected_macro_profile = "Built-in"
                            
                            self.profiles.append(p)
                            
                            # Check if this profile was marked as active
                            if entry.get('active'):
                                self.active_profile = p
                                print(f"DEBUG: Restored active profile: {p.name}")
                            
                    except Exception as entry_e:
                        print(f"⚠️ Error loading profile entry '{entry.get('name', 'Unknown')}': {entry_e}")
                        continue

                print(f"📖 Loaded {len(self.profiles)} profiles from {USER_GAMES_FILE}")
                
                # If no active profile was marked, default to first profile
                if not self.active_profile and self.profiles:
                    self.active_profile = self.profiles[0]
                    print(f"DEBUG: No active profile found, defaulting to: {self.active_profile.name}")
                
                return
                
            except Exception as e:
                print(f"❌ Error loading user profiles: {e}")
                print("⚠️ Falling back to defaults.")
        
        # If no file, start with empty list. Do NOT force defaults.
        # User wants a blank slate if they delete the file.
        self.profiles = []
        if not os.path.exists(USER_GAMES_FILE):
             # Don't save empty file yet, wait for user action.
             pass
            
    def import_ed_standard_profiles(self, target_group="Elite Dangerous"):
        """Scans Elite Dangerous standard ControlSchemes and adds profiles."""
        base_path = os.path.expanduser("~/.local/share/Steam/steamapps/common/Elite Dangerous/Products/elite-dangerous-odyssey-64/ControlSchemes/")
        if not os.path.exists(base_path):
             print(f"⚠️ ED ControlSchemes not found at: {base_path}")
             # Check for legacy path?
             base_path = os.path.expanduser("~/.local/share/Steam/steamapps/common/Elite Dangerous/Products/elite-dangerous-64/ControlSchemes/")
             if not os.path.exists(base_path):
                  return 0, []
        
        print(f"DEBUG: Scanning ED profiles at {base_path}")
         
        profiles_to_add = []
        added_names = []
        
        for f in os.listdir(base_path):
            if f.endswith(".binds"):
                name_variant = os.path.splitext(f)[0] # e.g. "SaitekX52"
                
                full_name = f"Elite Dangerous ({name_variant})"
                full_path = os.path.join(base_path, f)
                
                # Check duplicates
                if any(p.name == full_name for p in self.profiles):
                    print(f"DEBUG: Skipping duplicate {full_name}")
                    continue
                    
                # Create Profile
                try:
                    p = EliteDangerousProfile(name=full_name, group=target_group, default_path_override=full_path)
                    
                    # Temporarily load to check for keys
                    p.load_bindings()
                    
                    if p.actions:
                        profiles_to_add.append(p)
                        added_names.append(name_variant)
                    else:
                         print(f"DEBUG: No actions found in {f}, skipping.")
                         
                except Exception as e:
                    print(f"Skipping {f}: {e}")
        
        # Batch add all profiles (single save cycle)
        count = self.batch_add_profiles(profiles_to_add)
        return count, added_names
    def import_x4_profiles(self, target_group="X4 Foundations"):
        """Scans X4 detected folder for inputmap_*.xml profiles."""
        # Use a dummy profile to access logic
        detector = X4Profile(name="Temp")
        proton_folder = detector._detect_x4_folder()
        
        # Native Folder explicit check
        native_folder = None
        native_base = os.path.expanduser("~/.config/Egosoft/X4")
        if not os.path.exists(native_base):
             native_base = os.path.expanduser("~/.config/EgoSoft/X4")
             
        if os.path.exists(native_base):
         # Logic Split: GOG vs Steam
         if "GOG" in target_group:
              # GOG uses root folder
              native_folder = native_base
              print(f"DEBUG: GOG Import - Using Root: {native_folder}")
         else:
             # Steam: Find UID
             subdirs = [d for d in os.listdir(native_base) if os.path.isdir(os.path.join(native_base, d)) and d.isdigit()]
             if subdirs:
                 subdirs.sort(key=lambda x: os.path.getmtime(os.path.join(native_base, x)), reverse=True)
                 native_folder = os.path.join(native_base, subdirs[0])
                 print(f"DEBUG: Steam Import - Using UID: {native_folder}")
             else:
                 native_folder = native_base # Check root if no UID (Fallback)
        
        folders_to_scan = []
        
        # Filter based on Target Group (Strict Containment)
        if "Steam Proton" in target_group:
            if proton_folder and os.path.exists(proton_folder):
                 folders_to_scan.append(("Proton", proton_folder))
                 
        elif "Steam Native" in target_group or "GOG" in target_group:
            if native_folder and os.path.exists(native_folder):
                 folders_to_scan.append(("Native", native_folder))
                 
        else:
             # Fallback: Scan everything (should not happen in strict mode)
             if proton_folder and os.path.exists(proton_folder):
                 folders_to_scan.append(("Proton", proton_folder))
             if native_folder and os.path.exists(native_folder):
                 folders_to_scan.append(("Native", native_folder))
             
        if not folders_to_scan:
            print("⚠️ X4 Folders not found for import.")
            return 0, []
        
        # PHASE 1: Auto-cleanup orphaned profiles (1:1 sync)
        # Scan all files that currently exist
        all_found_files = []
        for location, folder in folders_to_scan:
            if os.path.exists(folder):
                for f in os.listdir(folder):
                    if f.startswith("inputmap") and f.endswith(".xml"):
                        # Determine expected name
                        if location == "Proton":
                            base_group = "X4 Foundations (Steam Proton)"
                        else:
                            if "GOG" in target_group:
                                base_group = "X4 Foundations (GOG)"
                            else:
                                base_group = "X4 Foundations (Steam Native)"
                        expected_name = f"{base_group} ({f})"
                        all_found_files.append(expected_name)
        
        # Remove orphaned profiles (files no longer exist)
        orphaned = [p for p in self.profiles 
                    if p.group == target_group 
                    and p.name not in all_found_files]
        
        removed_count = 0
        for p in orphaned:
            self.profiles.remove(p)
            print(f"♻️ Auto-removed orphaned profile: {p.name}")
            removed_count += 1
        
        # PHASE 2: Add new profiles
        profiles_to_add = []
        added_names = []
        
        for location, folder in folders_to_scan:
            if not os.path.exists(folder):
                 continue
                 
            for f in os.listdir(folder):
                if f.startswith("inputmap") and f.endswith(".xml"):
                     # Determine variant based on filename + location
                     
                     if location == "Proton":
                         base_group = "X4 Foundations (Steam Proton)"
                     else:
                         # Native Location
                         if "GOG" in target_group:
                             base_group = "X4 Foundations (GOG)"
                         else:
                             base_group = "X4 Foundations (Steam Native)"
                     
                     if f == "inputmap.xml":
                         # Clean name for main
                         name_variant = f"{base_group} (inputmap.xml)"
                     else:
                          # e.g. inputmap_1.xml -> 1
                          variant = f.replace("inputmap_", "").replace(".xml", "")
                          name_variant = f"{base_group} ({f})"
                     
                     full_path = os.path.join(folder, f)
                     
                     # Check duplicates
                     if any(p.name == name_variant for p in self.profiles):
                        continue
                        
                     # Create Profile
                     try:
                         # Use specific group
                         p = X4Profile(name=name_variant, group=base_group, default_path_override=full_path)
                         p.runtime_env = "Proton/Wine" if location == "Proton" else "Native Linux"
                         p.process_name = "X4.exe" if location == "Proton" else "Main()"
                         
                         profiles_to_add.append(p)
                         added_names.append(name_variant)
                     except Exception as e:
                         print(f"Skipping {f}: {e}")
        
        # Batch add all profiles (single save cycle)
        count = self.batch_add_profiles(profiles_to_add)
        
        # Return stats: (added_count, removed_count, added_names)
        return count, removed_count, added_names


    def remove_profile(self, profile):
        """Removes a profile and saves config."""
        if profile in self.profiles:
            self.profiles.remove(profile)
            self.save_profiles()
            # Reset active if needed
            if self.active_profile == profile:
                self.active_profile = self.profiles[0] if self.profiles else None
            return True
        return False

    def remove_group(self, group_name):
        """Removes all profiles belonging to a specific group."""
        initial_count = len(self.profiles)
        self.profiles = [p for p in self.profiles if p.group != group_name]
        removed_count = initial_count - len(self.profiles)
        
        if removed_count > 0:
             self.save_profiles()
             # Check if active profile was removed
             if self.active_profile and self.active_profile.group == group_name:
                  self.active_profile = self.profiles[0] if self.profiles else None
                  
        return removed_count


    def save_profiles(self):
        """Saves current profiles to user_games.json."""
        data = []
        for p in self.profiles:
            entry = {
                "name": p.name,
                "group": p.group,
                "process_name": p.process_name,
            }
            
            if isinstance(p, EliteDangerousProfile):
                 entry["type"] = "EliteDangerous"
                 entry["discriminator"] = p.path_discriminator
                 entry["bindings_path"] = p.custom_bindings_path # Save custom path if set

            elif isinstance(p, X4Profile):
                 entry["type"] = "X4"
                 entry["discriminator"] = p.path_discriminator
                 entry["bindings_path"] = p.default_path
            elif isinstance(p, GenericGameProfile):
                 entry["type"] = "Generic"
                 entry["discriminator"] = p.path_discriminator
                 entry["reference_path"] = p.reference_path
            if hasattr(p, 'runtime_env'):
                     entry["runtime_env"] = p.runtime_env
            
            # Save Active State
            if self.active_profile and p == self.active_profile:
                entry["active"] = True
            
            # Save Macro Profile Selection
            if hasattr(p, 'selected_macro_profile'):
                 entry['macro_profile'] = p.selected_macro_profile
                
            data.append(entry)
            
        try:
            import json
            os.makedirs(os.path.dirname(USER_GAMES_FILE), exist_ok=True)
            with open(USER_GAMES_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"💾 Saved {len(data)} profiles to {USER_GAMES_FILE}")
        except Exception as e:
            print(f"❌ Error saving profiles: {e}")
    
    # Phase 1c: Macro Profile Management
    
    def reload_macros(self):
        """Reload macros from active macro profile with priority system."""
        if not self.active_profile:
            return
        
        # Sync global active_macro_profile with profile's selection if needed
        # (This handles the first load case)
        if not hasattr(self, 'active_macro_profile') or not self.active_macro_profile:
             if hasattr(self.active_profile, 'selected_macro_profile'):
                 self.active_macro_profile = self.active_profile.selected_macro_profile
             else:
                 self.active_macro_profile = "Built-in"

        # Clear current macros
        self.active_profile.macros = {}
        
        # Reset to default macro file (default.json) initially
        game_slug = self.active_profile.group.lower().replace(' ', '_')
        game_dir = os.path.expanduser(f"~/.local/share/tuxtalks/games/{game_slug}")
        default_macros_path = os.path.join(game_dir, "macros", "default.json")
        self.active_profile.macros_file = default_macros_path

        is_named_custom = False

        if self.active_macro_profile and self.active_macro_profile != "Built-in":
            # 1. Custom Default
            if self.active_macro_profile == "Custom":
                self.active_profile.load_macros() # Loads default.json
                # "Custom" (default) acts as an overlay on Built-in, so we keep built-in.
                
            else:
                # 2. Check for Named Custom Profile
                profile_filename = self.active_macro_profile.lower().replace(' ', '_') + ".json"
                custom_profile_path = os.path.join(game_dir, "macros", profile_filename)
                
                if os.path.exists(custom_profile_path):
                     # It is a Named Custom Profile
                     print(f"📂 Switching to Custom Profile: {self.active_macro_profile}")
                     self.active_profile.macros_file = custom_profile_path
                     self.active_profile.load_macros()
                     is_named_custom = True
                else:
                     # 3. Assume Pack
                     self.load_pack_macros(self.active_macro_profile)
        
        # Load Built-in Macros
        # LOGIC CHANGE: If using a Named Custom Profile (Clean Slate), DO NOT load built-ins.
        if not is_named_custom:
            self.load_builtin_macros()
        else:
            print("🚫 Skipping Built-in macros (Named Custom Profile selected)")
        
        print(f"✅ Reloaded macros from: {self.active_macro_profile}")
    
    def load_pack_macros(self, pack_name):
        """Load macros from LAL content pack."""
        if not self.active_profile:
            return
        
        if not self.lal_manager:
            print(f"⚠️ LAL Manager not available")
            return
        
        pack = self.lal_manager.packs.get(pack_name)
        if not pack:
            print(f"⚠️ Pack '{pack_name}' not found")
            return
        
        # Get macros for current game
        pack_macros = pack.get_macros_for_game(self.active_profile.group)
        
        if pack_macros:
            # Merge into active profile (pack macros override built-in)
            self.active_profile.macros.update(pack_macros)
            print(f"📜 Loaded {len(pack_macros)} macros from pack: {pack_name}")
        else:
            print(f"ℹ️ No macros found in pack '{pack_name}' for {self.active_profile.group}")
    
    def load_builtin_macros(self):
        """Load built-in macros (base layer, lowest priority)."""
        if not self.active_profile:
            return
        
        # Built-in macros are typically defined in the profile's submit_command method
        # or in profile-specific macro definitions
        # For now, we preserve any macros that were loaded by the profile itself
        # In the future, we could extract built-in macros to a separate method
        
        # This is a placeholder - built-in macros are typically already in the profile
        # from its initialization or from submit_command processing
        pass
    
    def get_macro_source(self, macro_name):
        """
        Determine where a macro comes from.
        
        Args:
            macro_name: Name of the macro
            
        Returns:
            str: "Built-in", "Pack: [name]", or "Custom"
        """
        if not self.active_profile or macro_name not in self.active_profile.macros:
            return "Unknown"
        
        # Check if from pack (LAL content pack)
        if self.active_macro_profile and hasattr(self, 'lal_manager') and self.lal_manager:
            if self.active_macro_profile in self.lal_manager.packs:
                pack = self.lal_manager.packs.get(self.active_macro_profile)
                if pack:
                    pack_macros = pack.get_macros_for_game(self.active_profile.group)
                    if macro_name in pack_macros:
                        return f"Pack: {self.active_macro_profile}"
        
        # Check if from custom macro profile (any profile that's not Built-in and not a pack)
        # This includes "Custom" and any user-created profiles like "Combat Macros", etc.
        if self.active_macro_profile and self.active_macro_profile != "Built-in":
            # If it's not a pack (checked above), it's a custom profile
            if not (hasattr(self, 'lal_manager') and self.lal_manager and 
                    self.active_macro_profile in self.lal_manager.packs):
                return "Custom"
        
        return "Built-in"
    
    # Custom Macro Profile Management
    
    def get_custom_macro_profiles(self):
        """
        Get list of custom macro profile names for the current game.
        
        Returns:
            list: Profile names (e.g., ["Combat Macros", "Trading Macros"])
        """
        if not self.active_profile:
            return []
        
        # Custom profiles stored in: ~/.local/share/tuxtalks/games/{game}/macros/
        game_slug = self.active_profile.group.lower().replace(' ', '_')
        macros_dir = os.path.expanduser(f"~/.local/share/tuxtalks/games/{game_slug}/macros")
        
        if not os.path.exists(macros_dir):
            return []
        
        profiles = []
        for filename in os.listdir(macros_dir):
            if filename.endswith('.json'):
                # Convert filename to profile name
                profile_name = filename[:-5].replace('_', ' ').title()
                profiles.append(profile_name)
        
        return profiles
    
    def create_custom_macro_profile(self, profile_name):
        """
        Create a new custom macro profile.
        
        Args:
            profile_name: Display name (e.g., "Combat Macros")
            
        Returns:
            bool: Success status
        """
        if not self.active_profile:
            return False
        
        game_slug = self.active_profile.group.lower().replace(' ', '_')
        macros_dir = os.path.expanduser(f"~/.local/share/tuxtalks/games/{game_slug}/macros")
        
        # Create directory if needed
        os.makedirs(macros_dir, exist_ok=True)
        
        # Convert profile name to filename
        filename = profile_name.lower().replace(' ', '_') + '.json'
        filepath = os.path.join(macros_dir, filename)
        
        # Prevent overwriting default.json via this method (it should be managed via "Custom" profile)
        if filename == "default.json":
             print("⚠️ Cannot name a profile 'default' (reserved).")
             return False
        
        # Check if already exists
        if os.path.exists(filepath):
            return False
        
        # Create empty macro profile
        try:
            with open(filepath, 'w') as f:
                json.dump({}, f, indent=4)
            print(f"✅ Created custom macro profile: {profile_name}")
            
            # Switch to it immediately so subsequent saves target it!
            self.active_macro_profile = profile_name
            self.active_profile.macros_file = filepath 
            self.active_profile.macros = {} # Clear current rules
            # We don't need to load because we just created an empty file.
            
            return True
        except Exception as e:
            print(f"❌ Failed to create macro profile: {e}")
            return False
    
    def rename_custom_macro_profile(self, old_name, new_name):
        """
        Rename a custom macro profile.
        
        Args:
            old_name: Current profile name
            new_name: New profile name
            
        Returns:
            bool: Success status
        """
        if not self.active_profile:
            return False
        
        game_slug = self.active_profile.group.lower().replace(' ', '_')
        macros_dir = os.path.expanduser(f"~/.local/share/tuxtalks/games/{game_slug}/macros")
        
        old_filename = old_name.lower().replace(' ', '_') + '.json'
        new_filename = new_name.lower().replace(' ', '_') + '.json'
        old_path = os.path.join(macros_dir, old_filename)
        new_path = os.path.join(macros_dir, new_filename)
        
        if not os.path.exists(old_path):
            return False
        
        if os.path.exists(new_path):
            return False  # New name already exists
        
        try:
            os.rename(old_path, new_path)
            print(f"✅ Renamed macro profile: {old_name} → {new_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to rename macro profile: {e}")
            return False
    
    def delete_custom_macro_profile(self, profile_name):
        """
        Delete a custom macro profile.
        
        Args:
            profile_name: Profile name to delete
            
        Returns:
            bool: Success status
        """
        if not self.active_profile:
            return False
        
        game_slug = self.active_profile.group.lower().replace(' ', '_')
        macros_dir = os.path.expanduser(f"~/.local/share/tuxtalks/games/{game_slug}/macros")
        
        filename = profile_name.lower().replace(' ', '_') + '.json'
        filepath = os.path.join(macros_dir, filename)
        
        if not os.path.exists(filepath):
            return False
        
        try:
            os.remove(filepath)
            print(f"✅ Deleted macro profile: {profile_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to delete macro profile: {e}")
            return False

    def refresh_profile_list(self):
        """Reloads profiles from the user_games.json file to ensure the in-memory list is up-to-date."""
        self.load_profiles()

    def add_profile(self, profile):
        """Adds a new profile and saves."""
        self.profiles.append(profile)
        self.save_profiles()
        # DO NOT reload from disk here - we already have the data in memory!
        # The UI callback will trigger its own refresh.
        return True # Assuming success if no exception
    
    def batch_add_profiles(self, profiles):
        """Adds multiple profiles efficiently (single save/refresh cycle)."""
        if not profiles:
            return 0
        
        for p in profiles:
            self.profiles.append(p)
        
        self.save_profiles()
        # No refresh here - caller will trigger UI refresh
        return len(profiles)

    def remove_profile(self, profile):
        """Removes a profile and saves."""
        if profile in self.profiles:
            self.profiles.remove(profile)
            self.save_profiles()
            self.refresh_profile_list() # Ensure the list is refreshed after removing
            return True
        return False

    def get_profile_by_name(self, name):
        for p in self.profiles:
            if p.name == name:
                return p
        return None

    def initialize(self):
        print("🎮 Initializing Game Manager...")
        for p in self.profiles:
            if p.load_bindings():
                print(f"   -> Loaded profile: {p.name}")
            else:
                print(f"   -> Failed to load profile: {p.name}")

    def detect_game(self):
        """Scans for running games and returns the name of the first one found, or None."""
        for p in self.profiles:
            if p.is_running():
                return p.name
        return None

    def check_active_game(self):
        """Checks if a supported game is running and sets active profile."""
        if not self.game_mode_enabled:
            return None

        # If we already have an active profile, re-verify it's running?
        # Or check all if none active
        
        if self.active_profile and self.active_profile.is_running():
            return self.active_profile
            
        # Scan for games
        for p in self.profiles:
            if p.is_running():
                if self.active_profile != p:
                    print(f"🎮 Game Detected: {p.name}")
                    self.active_profile = p
                return p
        
        self.active_profile = None
        return None

    def handle_command(self, text, input_controller):
        """Returns True if command handled by game manager."""
        if not self.game_mode_enabled or not self.active_profile:
            return (False, None)
            
        # Strip punctuation and whitespace
        # "retract gear." -> "retract gear"
        cmd = text.lower().strip().rstrip('.!,?')
        
        # Check Macros
        for macro_name, data in self.active_profile.macros.items():
            triggers = data.get("triggers", [])
            if cmd in triggers:
                self.active_profile.execute_macro(macro_name, input_controller)
                return (True, f"Executing macro {macro_name}")

        # Check bindings
        if cmd in self.active_profile.bindings:
            # Bindings are now (key, [modifiers])
            binding = self.active_profile.bindings[cmd]
            key = binding[0]
            mods = binding[1]
            
            mod_str = "+".join(mods) + "+" if mods else ""
            print(f"🎮 Game Command: '{cmd}' -> Pressing '{mod_str}{key}'")
        
            # FIX: Linux/Wayland ydotool fix for keys
            # Key might be a string "1" OR a KeyCode object OR a Key enum.
            # We must map "1" -> Scancode 2, "2" -> Scancode 3.
            # AND "Tab" -> Scancode 15, "Enter" -> 28, etc.
            final_key = key
            
            # 1. Handle Digits (String or KeyCode)
            key_char = None
            if isinstance(key, str) and len(key) == 1 and key.isdigit():
                key_char = key
            elif hasattr(key, 'char') and key.char and key.char.isdigit():
                key_char = key.char
                
            if key_char:
                digit_map = {
                    '1': 2, '2': 3, '3': 4, '4': 5, '5': 6,
                    '6': 7, '7': 8, '8': 9, '9': 10, '0': 11
                }
                if key_char in digit_map:
                    final_key = digit_map[key_char]
                    print(f"DEBUG: Remapped Digit '{key_char}' to Scancode {final_key}")
            
            # 2. Handle Special Keys (pynput Key enums OR Strings)
            try:
                from pynput.keyboard import Key
                scancode_map = {
                    # Enums
                    Key.tab: 15, Key.enter: 28, Key.space: 57, Key.esc: 1,
                    Key.backspace: 14, Key.delete: 111, 
                    Key.up: 103, Key.down: 108, Key.left: 105, Key.right: 106,
                    # Strings (Common case)
                    "Tab": 15, "Enter": 28, "Return": 28, "Space": 57, "Esc": 1, "Escape": 1,
                    "Backspace": 14, "Delete": 111,
                    "Up": 103, "Down": 108, "Left": 105, "Right": 106,
                    # Function Keys
                    Key.f1: 59, Key.f2: 60, Key.f3: 61, Key.f4: 62,
                    Key.f5: 63, Key.f6: 64, Key.f7: 65, Key.f8: 66,
                    Key.f9: 67, Key.f10: 68, Key.f11: 87, Key.f12: 88,
                    "F1": 59, "F2": 60, "F3": 61, "F4": 62, "F5": 63, "F6": 64,
                    "F7": 65, "F8": 66, "F9": 67, "F10": 68, "F11": 87, "F12": 88
                }
                
                # Check direct match or string
                mapped_code = None
                if key in scancode_map:
                    mapped_code = scancode_map[key]
                elif str(key) in scancode_map:
                    mapped_code = scancode_map[str(key)]
                    
                if mapped_code:
                    final_key = mapped_code
                    print(f"DEBUG: Remapped Special Key '{key}' to Scancode {final_key}")
            except Exception as e:
                print(f"DTOOL DEBUG: Error checking special key: {e}")

            
            # Increased duration to 0.3s to ensure reliable detection of
            # complex combos (e.g. Ctrl+Alt+H) in games like Elite Dangerous
            input_controller.hold_key_combo(final_key, mods, 0.3)
            # Return feedback string
            return (True, f"Executing {cmd}")
            
        # Check if it was a valid command but UNBOUND
        for action, phrases in self.active_profile.action_voice_map.items():
            if cmd in phrases:
                print(f"⚠️  Command '{cmd}' recognized, but action '{action}' is UNBOUND in '{self.active_profile.name}' settings.")
                return (True, f"Command {cmd} is not bound")
        
        return (False, None)

    def set_enabled(self, enabled):
        self.game_mode_enabled = enabled
        if enabled:
            print("🎮 Game Mode ENABLED")
            self.check_active_game()
        else:
            print("🎮 Game Mode DISABLED")
            self.active_profile = None
