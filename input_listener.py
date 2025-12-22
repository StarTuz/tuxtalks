import evdev
import threading
import time
import select

class InputListener:
    """
    Listens for global key events using evdev.
    Used for Push-to-Talk (PTT) functionality.
    """
    
    def __init__(self, ptt_key="KEY_LEFTCTRL", mode="HOLD", key_bindings=None, event_queue=None):
        self.ptt_key = ptt_key
        self.mode = mode # "HOLD" or "TOGGLE"
        self.key_bindings = key_bindings or {} # {key_code: event_name}
        self.event_queue = event_queue
        self.active = False
        self.running = False
        self.thread = None
        self.devices = []
        self.last_toggle_time = 0
        self._find_keyboards()
        
    def _find_keyboards(self):
        """Finds all input devices that look like keyboards."""
        self.devices = []
        try:
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            for device in devices:
                if "keyboard" in device.name.lower():
                    self.devices.append(device)
            print(f"⌨️  Found {len(self.devices)} keyboard device(s).")
        except Exception as e:
            print(f"❌ Error finding keyboards: {e}")
            
    def start(self):
        """Starts the listener thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        print("👂 Input listener started.")
        
    def stop(self):
        """Stops the listener thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
            
    def set_ptt_key(self, key_code):
        """Sets the PTT key code (e.g., 'KEY_LEFTCTRL')."""
        self.ptt_key = key_code
        print(f"🎤 PTT Key set to: {self.ptt_key}")
        
    def set_mode(self, mode):
        """Sets the PTT mode ('HOLD' or 'TOGGLE')."""
        self.mode = mode
        self.active = False # Reset state on mode change
        print(f"🎤 PTT Mode set to: {self.mode}")
        
    def is_active(self):
        """Returns True if PTT is currently active."""
        return self.active
        
    def _listen_loop(self):
        """Main loop for monitoring input events."""
        while self.running:
            try:
                # Re-scan devices if none found
                if not self.devices:
                    self._find_keyboards()
                    if not self.devices:
                        time.sleep(2)
                        continue
                
                # Map fd to device
                fd_to_device = {dev.fd: dev for dev in self.devices}
                
                # Use select to wait for events
                r, w, x = select.select(fd_to_device.keys(), [], [], 1.0)
                
                for fd in r:
                    device = fd_to_device.get(fd)
                    if device:
                        try:
                            for event in device.read():
                                if event.type == evdev.ecodes.EV_KEY:
                                    key_event = evdev.categorize(event)
                                    key_code = key_event.keycode
                                    
                                    if isinstance(key_code, list):
                                        key_code = key_code[0]
                                        
                                    if key_code == self.ptt_key:
                                        if self.mode == "HOLD":
                                            if key_event.keystate == key_event.key_down:
                                                self.active = True
                                            elif key_event.keystate == key_event.key_up:
                                                self.active = False
                                        elif self.mode == "TOGGLE":
                                            if key_event.keystate == key_event.key_down:
                                                current_time = time.time()
                                                if current_time - self.last_toggle_time > 0.5:
                                                    self.active = not self.active
                                                    self.last_toggle_time = current_time
                                                    print(f"🎤 PTT Toggled: {'ON' if self.active else 'OFF'}")
                                        
                                        # Check generic key bindings
                                        elif key_code in self.key_bindings and self.event_queue:
                                            if key_event.keystate == key_event.key_down:
                                                command = self.key_bindings[key_code]
                                                print(f"🔑 Key '{key_code}' pressed -> Triggering '{command}'")
                                                self.event_queue.put(command)
                        except BlockingIOError:
                            pass # No more data
                        except OSError as e:
                            if e.errno == 19: # No such device
                                print(f"❌ Device disconnected: {device.name}")
                                if device in self.devices:
                                    self.devices.remove(device)
                            else:
                                print(f"❌ Error reading device: {e}")

            except Exception as e:
                print(f"❌ Error in input listener: {e}")
                time.sleep(1)
