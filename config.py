import os
import json
import pathlib

# Default Configuration
DEFAULTS = {
    "JRIVER_IP": "localhost",
    "JRIVER_PORT": 52199,
    "ACCESS_KEY": "",
    "WAKE_WORD": "Alice",
    "VOSK_MODEL_PATH": str(pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "models" / "vosk-model-en-gb-small"),
    "COMMAND_TIMEOUT": 5,
    "PLAYER": "jriver",
    "STRAWBERRY_DB_PATH": str(pathlib.Path.home() / ".local" / "share" / "strawberry" / "strawberry" / "strawberry.db"),
    "PIPER_VOICE": "en_GB-cori-high",
    "PTT_ENABLED": False,
    "PTT_MODE": "HOLD", # "HOLD" or "TOGGLE"
    "PTT_KEY": "KEY_LEFTCTRL",
    "PAGE_NEXT_KEY": "KEY_RIGHT",
    "PAGE_PREV_KEY": "KEY_LEFT",
    "PAGE_PREV_KEY": "KEY_LEFT",
    "VOICE_CORRECTIONS": {}, # User-defined voice corrections
    "CUSTOM_VOCABULARY": [], # User-defined vocabulary/grammar
    "GAME_MODE_ENABLED": False, # Start in Game Mode?
    "ASR_ENGINE": "vosk",
    "TTS_ENGINE": "piper",     # piper, system
    "WHISPER_MODEL_SIZE": "small.en", # tiny.en, base.en, small.en, medium.en, large-v3
    "WHISPER_DEVICE": "cuda",  # cuda, cpu
    "WYOMING_HOST": "localhost",
    "WYOMING_PORT": 10301,
    "WYOMING_AUTO_START": True,  # Auto-start Wyoming server if not running
    "WYOMING_MODEL": "tiny",  # Whisper model: tiny, base, small, medium, large-v3
    "WYOMING_LANGUAGE": "en",  # Language for transcription
    "WYOMING_DEVICE": "cpu",  # cpu or cuda
    "WYOMING_COMPUTE_TYPE": "int8",  # int8, int16, float16, float32
    "WYOMING_BEAM_SIZE": 1,  # Beam size for search (1-5, higher = slower but more accurate)
    "WYOMING_DATA_DIR": "",  # Empty = auto (~/.local/share/tuxtalks/wyoming-data)
    "UI_LANGUAGE": "en",  # Language for user interface (en, es, de, fr, uk)
    "VOICE_LANGUAGE": "en",  # Language for voice recognition (future)
    "LOG_LEVEL": "INFO",  # ALL, DEBUG, INFO, WARNING, ERROR
    
    # Ollama AI Integration (Natural Language Understanding)
    "OLLAMA_ENABLED": False,  # Opt-in feature
    "OLLAMA_URL": "http://localhost:11434",  # Local Ollama instance
    "OLLAMA_MODEL": "llama2",  # Model to use (llama2, mistral, phi, etc.)
    "OLLAMA_TIMEOUT": 2000,  # Milliseconds (2s for music commands)
    "FIRST_RUN_COMPLETE": False, # Has the user completed the setup wizard?
}

# Player Schemas for GUI generation
PLAYER_SCHEMAS = {
    "jriver": {
        "name": "JRiver Media Center",
        "fields": {
            "JRIVER_IP": {"label": "IP Address", "type": "text", "default": "localhost"},
            "JRIVER_PORT": {"label": "Port", "type": "number", "default": 52199},
            "ACCESS_KEY": {"label": "Access Key", "type": "text", "default": ""}
        }
    },
    "strawberry": {
        "name": "Strawberry Music Player",
        "fields": {
            "STRAWBERRY_DB_PATH": {"label": "Database Path", "type": "text", "default": str(pathlib.Path.home() / ".local" / "share" / "strawberry" / "strawberry" / "strawberry.db")}
        }
    },
    "elisa": {
        "name": "Elisa Music Player",
        "fields": {}
    },
    "mpris": {
        "name": "Generic / Custom Player (MPRIS)",
        "fields": {
            "MPRIS_SERVICE": {"label": "Service Name", "type": "text", "default": "org.mpris.MediaPlayer2.vlc"},
            "LIBRARY_PATH": {"label": "Music Library Path", "type": "text", "default": str(pathlib.Path.home() / "Music")}
        }
    }
}

CONFIG_DIR = pathlib.Path.home() / ".config" / "tuxtalks"
SYSTEM_CONFIG_FILE = CONFIG_DIR / "config.json"
LEGACY_CONFIG_FILE = pathlib.Path.home() / ".config" / "jriver-voice" / "config.json"

# Check CWD and Module directory
CWD_CONFIG_FILE = pathlib.Path("config.json")
MODULE_CONFIG_FILE = pathlib.Path(__file__).parent / "config.json"

class Config:
    def __init__(self):
        self._config = DEFAULTS.copy()
        
        # Determine which config file to use
        if CWD_CONFIG_FILE.exists():
            self.config_file = CWD_CONFIG_FILE
        elif MODULE_CONFIG_FILE.exists():
            self.config_file = MODULE_CONFIG_FILE
        else:
            self.config_file = SYSTEM_CONFIG_FILE
            
        self.load()

    def load(self):
        """Load config from file and environment variables."""
        # 1. Load from file
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    file_config = json.load(f)
                    self._config.update(file_config)
                    # print(f"✅ Loaded config from: {self.config_file}")
            except json.JSONDecodeError:
                print(f"⚠️  Error reading config file at {self.config_file}. Using defaults.")
        
        # 1b. Migration: If system config doesn't exist but legacy does, migrate it
        elif self.config_file == SYSTEM_CONFIG_FILE and LEGACY_CONFIG_FILE.exists():
            print(f"📦 Found legacy configuration at {LEGACY_CONFIG_FILE}. Migrating...")
            try:
                with open(LEGACY_CONFIG_FILE, "r") as f:
                    legacy_config = json.load(f)
                    self._config.update(legacy_config)
                    # Save immediately to new location
                    self.save()
            except Exception as e:
                print(f"❌ Migration failed: {e}")

        else:
            # First run, no config found.
            # Create default config file silently or with minimal noise
            # print(f"ℹ️  No config found. Using defaults.")
            pass

        # 2. Override with Environment Variables
        for key in self._config:
            env_val = os.environ.get(f"JRIVER_{key}") or os.environ.get(key)
            if env_val:
                # Handle types (int vs string)
                if isinstance(self._config[key], int):
                    try:
                        self._config[key] = int(env_val)
                    except ValueError:
                        pass
                else:
                    self._config[key] = env_val

    def save(self):
        """Save current config to file."""
        # If using system config, ensure dir exists
        if self.config_file == SYSTEM_CONFIG_FILE:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=4)
        print(f"✅ Configuration saved to {self.config_file}")

    def get(self, key, default=None):
        return self._config.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key, value):
        self._config[key] = value

    def setup_wizard(self):
        """Interactive setup wizard for first run."""
        print("\n👋 Welcome to TuxTalks Setup!")
        print("-------------------------------------------")
        print("We need a few details to connect to your media player.\n")

        # Player Selection
        current_player = self.get("PLAYER")
        player = input(f"Enter Media Player (jriver) [{current_player}]: ").strip().lower()
        if player:
            self.set("PLAYER", player)
        else:
            player = current_player

        if player == "jriver":
            # Access Key
            current_key = self.get("ACCESS_KEY")
            key = input(f"Enter JRiver Access Key [{current_key}]: ").strip()
            if key:
                self.set("ACCESS_KEY", key)
            elif not current_key:
                print("❌ Access Key is required for JRiver.")
                return False

            # IP Address
            current_ip = self.get("JRIVER_IP")
            ip = input(f"Enter JRiver IP Address [{current_ip}]: ").strip()
            if ip:
                self.set("JRIVER_IP", ip)

        # Wake Word
        current_wake = self.get("WAKE_WORD")
        wake = input(f"Enter Wake Word [{current_wake}]: ").strip()
        if wake:
            self.set("WAKE_WORD", wake)

        self.save()
        print("\n✅ Setup complete! You can change these settings later in:")
        print(f"   {self.config_file}\n")
        return True

# Global instance
cfg = Config()
