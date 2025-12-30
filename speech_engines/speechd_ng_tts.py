import dbus
from .base import TTSBase

class SpeechdNgTTS(TTSBase):
    """
    TTS Engine that connects to the local speechd-ng daemon via D-Bus.
    Service: org.speech.Service
    Path: /org/speech/Service
    Interface: org.speech.Service
    """
    
    BUS_NAME = "org.speech.Service"
    OBJECT_PATH = "/org/speech/Service"
    INTERFACE = "org.speech.Service"

    def __init__(self, config):
        super().__init__(config)
        self.bus = None
        self.iface = None
        self._connect()

    def _connect(self):
        """Establish connection to the speechd-ng D-Bus service."""
        try:
            self.bus = dbus.SessionBus()
            obj = self.bus.get_object(self.BUS_NAME, self.OBJECT_PATH)
            self.iface = dbus.Interface(obj, self.INTERFACE)
            print("✅ Connected to speechd-ng via D-Bus")
        except dbus.DBusException as e:
            print(f"⚠️ Could not connect to speechd-ng: {e}")
            self.iface = None

    def speak(self, text):
        """Speak text using speechd-ng."""
        if not self.iface:
            # Try reconnecting once if disconnected
            self._connect()
            
        if self.iface:
            try:
                # Use standard Speak method
                # We could support voice selection later if config has it
                self.iface.Speak(text)
                print(f"🗣️ speechd-ng: {text}")
            except Exception as e:
                print(f"❌ speechd-ng speak error: {e}")
        else:
            print(f"❌ speechd-ng not available. Dropped: '{text}'")

    def stop(self):
        """Stop current speech/audio."""
        if self.iface:
            try:
                # API Reference says StopAudio()
                self.iface.StopAudio()
                print("🔇 speechd-ng stopped")
            except Exception as e:
                print(f"⚠️ speechd-ng stop error: {e}")

    def health_check(self):
        """Returns True if connected to speechd-ng."""
        if not self.iface:
            self._connect()
            
        # Verify connection by pinging or checking name has owner
        if self.iface:
            try:
                # Basic check: verify service name exists on bus
                return self.bus.name_has_owner(self.BUS_NAME)
            except:
                pass
        return False
