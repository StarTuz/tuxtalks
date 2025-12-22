import subprocess
import time

class InputController:
    """
    Controls system input using ydotool.
    Requires ydotool to be installed and the daemon running (usually as a user service).
    """
    
    # Standard Linux Input Event Codes (from linux/input-event-codes.h)
    KEY_ENTER = 28
    KEY_SPACE = 57
    KEY_MUTE = 113
    KEY_VOLUMEDOWN = 114
    KEY_VOLUMEUP = 115
    KEY_PLAYPAUSE = 164
    KEY_PREVIOUSSONG = 165
    KEY_NEXTSONG = 163
    
    def __init__(self):
        self.available = self._check_availability()
        
    def _check_availability(self):
        """Checks if ydotool is available and working."""
        try:
            # Try a harmless command (no-op or just checking help)
            # Actually, let's just check if binary exists
            subprocess.run(["which", "ydotool"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            print("⚠️ ydotool not found. Input control disabled.")
            return False
            
    def press_key(self, key_code):
        """Simulates a key press and release."""
        if not self.available:
            return
            
        try:
            # ydotool key <code:state> ...
            # 1 is press, 0 is release
            cmd = ["ydotool", "key", f"{key_code}:1", f"{key_code}:0"]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"❌ Error pressing key {key_code}: {e}")

    def hold_key(self, key_code, duration=0.1):
        """Simulates holding a key for a duration (needed for games)."""
        if not self.available:
            return

        try:
            # ydotool key <code:state> ...
            # 1 is press, 0 is release
            cmd_press = ["ydotool", "key", f"{key_code}:1"]
            subprocess.run(cmd_press, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(duration)
            cmd_release = ["ydotool", "key", f"{key_code}:0"]
            subprocess.run(cmd_release, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"❌ Error holding key {key_code}: {e}")

    def hold_key_combo(self, key_code, modifiers, duration=0.1):
        """Simulates holding a key combo (mods + key) for a duration."""
        if not self.available:
            return

        try:
            # Prepare press commands: Modifiers down -> Key down
            # ydotool key key:1 key:1 ...
            
            # Map modifier names to ydotool codes if needed?
            # Assuming key_code coming in are valid ydotool codes (strings or hex)
            
            press_args = []
            release_args = []
            
            for mod in modifiers:
                press_args.append(f"{mod}:1")
                # Release in reverse order usually good practice, but ydotool handles batches
                release_args.insert(0, f"{mod}:0")
                
            press_args.append(f"{key_code}:1")
            release_args.insert(0, f"{key_code}:0")
            
            # Execute Press
            cmd_press = ["ydotool", "key"] + press_args
            subprocess.run(cmd_press, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            time.sleep(duration)
            
            # Execute Release
            cmd_release = ["ydotool", "key"] + release_args
            subprocess.run(cmd_release, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
        except Exception as e:
            print(f"❌ Error holding combo {modifiers}+{key_code}: {e}")

    def type_text(self, text):
        """Types text using ydotool type."""
        if not self.available:
            return
            
        try:
            subprocess.run(["ydotool", "type", text], check=True)
        except Exception as e:
            print(f"❌ Error typing text: {e}")

    # --- Media Controls ---
    
    def media_play_pause(self):
        self.press_key(self.KEY_PLAYPAUSE)
        
    def media_next(self):
        self.press_key(self.KEY_NEXTSONG)
        
    def media_prev(self):
        self.press_key(self.KEY_PREVIOUSSONG)
        
    def volume_up(self):
        self.press_key(self.KEY_VOLUMEUP)
        
    def volume_down(self):
        self.press_key(self.KEY_VOLUMEDOWN)
        
    def mute(self):
        self.press_key(self.KEY_MUTE)
