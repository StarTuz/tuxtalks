import queue
import json
import pyaudio
import queue
import json
import os
import sys

# Critical Fix for UCX/Segfaults:
# We must set these environment variables BEFORE any C-libraries (like ctranslate2/torch/cuda) load.
# Setting them in python after start might be too late (as seen by persistent crashes).
# If they are not set, we set them and RE-EXECUTE the process to ensure a clean environment.
required_vars = {
    "UCX_TLS": "tcp,self",
    "UCX_MEMTYPE_CACHE": "n",
    "OMPI_MCA_btl": "^openib" 
}

needs_restart = False
for k, v in required_vars.items():
    if k not in os.environ:
        os.environ[k] = v
        needs_restart = True

if needs_restart:
    print("🔄 Restarting process to apply critical stability fixes (Disable UCX/IB)...")
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"⚠️ Failed to re-exec: {e}. Stability might be compromised.")

import re
import time
import subprocess
import sys
import argparse
from config import cfg, SYSTEM_CONFIG_FILE, PLAYER_SCHEMAS
from players.jriver import JRiverPlayer
from players.strawberry import StrawberryPlayer
from players.elisa import ElisaPlayer
from players.mpris import MPRISPlayer
from game_manager import GameManager
from player_interface import MediaPlayer
import model_manager
from local_library import LocalLibrary
from voice_manager import VoiceManager
from input_controller import InputController
from input_controller import InputController
from input_listener import InputListener
from speech_engines import get_asr_engine, get_tts_engine
from core import AssistantStateMachine, TextNormalizer, SelectionHandler, CommandProcessor

# --- Configuration ---
# Loaded from config.py
# ----------------------------

# --- Wake Word Configuration ---
WAKE_WORD = cfg.get("WAKE_WORD")
# ----------------------------

class VoiceAssistant:
    """
    Main class for the JRiver Voice Assistant.
    Handles wake word detection, command processing, and JRiver MCWS interaction.
    """
    # State constants (kept for backwards compatibility)
    STATE_LISTENING = 0          # Listening for wake word
    STATE_WAITING_SELECTION = 1  # Waiting for user to select from list
    STATE_COMMAND_MODE = 2       # Wake word detected, listening for commands

    COMMAND_TIMEOUT = 20  # Increased to 20 seconds

    def __init__(self, wake_word=WAKE_WORD, input_controller=None):
        """
        Initialize the Voice Assistant.
        
        Args:
            wake_word (str): The keyword to activate command mode (default: "Alice").
            input_controller (InputController): Optional controller for system inputs.
        """
        # Initialize state machine
        self.state_machine = AssistantStateMachine()
        self.state = self.state_machine.state  # Maintain backwards compatibility
        self.input_controller = input_controller
        # Suppress ALSA error messages
        from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
        from contextlib import contextmanager
        
        ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        def py_error_handler(filename, line, function, err, fmt):
            pass
        c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
        
        @contextmanager
        def no_alsa_err():
            asound = cdll.LoadLibrary('libasound.so.2')
            asound.snd_lib_error_set_handler(c_error_handler)
            yield
            asound.snd_lib_error_set_handler(None)

        try:
            with no_alsa_err():
                self.p = pyaudio.PyAudio()
        except:
            # Fallback if ctypes/libasound fails
            self.p = pyaudio.PyAudio()
        
        # Initialize Audio (for playback/input mixing if needed, or purely for ASR if engines share it)
        # However, ASR engine now manages its own stream. 
        # We keep self.p for now as a shared context if needed, or remove it?
        # ASRBase implementations usually manage their own PyAudio instance.
        # But wait, if we want to share the audio device?
        # For now, let's keep self.p initialization here as it handles ALSA suppression logic which is useful.
        
        self.wake_word = wake_word.lower()  # Store wake word in lowercase
        self.command_queue = None  # Will be set by main()
        self.speech_queue = queue.Queue() # Queue for speech requests
        self.config = cfg
        
        # Initialize text normalizer
        self.text_normalizer = TextNormalizer(cfg)
        
        # Initialize Player
        player_type = cfg.get("PLAYER")
        if player_type == "jriver":
            self.player = JRiverPlayer(cfg, speak_func=self.speak)
        elif player_type == "strawberry":
            self.player = StrawberryPlayer(cfg, speak_func=self.speak)
        elif player_type == "elisa":
            self.player = ElisaPlayer(cfg, speak_func=self.speak)
        elif player_type == "mpris":
            self.player = MPRISPlayer(cfg, speak_func=self.speak)
        else:
            print(f"Unknown player type: {player_type}, defaulting to JRiver")
            self.player = JRiverPlayer(cfg, speak_func=self.speak)
            
        # Initialize Game Manager
        self.game_manager = GameManager()
        self.game_manager.initialize()
        
        # Initialize Selection Handler (needs player and text_normalizer)
        self.selection_handler = SelectionHandler(
            self.player, 
            self.speak, 
            self.state_machine,
            self.text_normalizer
        )
        
        # Initialize CommandProcessor (delegates to handlers)
        self.command_processor = CommandProcessor(
            player=self.player,
            game_manager=self.game_manager,
            input_controller=self.input_controller,
            selection_handler=self.selection_handler,
            text_normalizer=self.text_normalizer,
            speak_func=self.speak,
            config=cfg,
            speech_queue=self.speech_queue,
            state_machine=self.state_machine
        )
        
        # Set up callbacks for player switching
        self.command_processor.set_reload_player_callback(self.reload_player)
        self.selection_handler._reload_player_callback = self.reload_player
        
        # Ignored Commands Log
        self.ignored_log_path = os.path.expanduser("~/.local/share/tuxtalks/ignored_commands.json")

    def log_ignored_command(self, text):
        """Logs ignored text to a JSON file for the launcher to read."""
        if not text: return
        
        try:
            # Load existing
            data = []
            if os.path.exists(self.ignored_log_path):
                with open(self.ignored_log_path, 'r') as f:
                    data = json.load(f)
            
            # Add new (if not duplicate within last few entries?)
            entry = {"text": text, "timestamp": time.time()}
            
            # Check for duplicates anywhere in the list
            if not any(d["text"] == text for d in data):
                data.append(entry)
                
                # Keep last 50
                if len(data) > 50:
                    data = data[-50:]
                    
                with open(self.ignored_log_path, 'w') as f:
                    json.dump(data, f)
        except Exception as e:
            print(f"Failed to log ignored command: {e}")

    def reload_player(self, player_id=None):
        """Reload player configuration and switch player type.
        
        Args:
            player_id: Optional player ID to switch to (e.g., 'jriver', 'strawberry')
        """
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        
        logger.info(f"reload_player called with player_id={player_id}")
        print("Reloading player configuration...")
        
        # If player_id specified, save it first
        if player_id:
            logger.info(f"Setting PLAYER to: {player_id}")
            self.config.set("PLAYER", player_id)
            self.config.save()
            logger.info("✅ Configuration saved to /home/startux/.config/tuxtalks/config.json")
            print("✅ Configuration saved to /home/startux/.config/tuxtalks/config.json")
        
        # Reload config to get latest values
        self.config.load()
        
        # Stop existing player
        if hasattr(self, 'player') and self.player:
            try:
                logger.debug("Stopping old player instance")
                self.player.stop()
            except:
                pass
        
        # Get player type from config
        player_type = self.config.get("PLAYER", "jriver").lower()
        logger.info(f"🔄 Loading player type: {player_type}")
        print(f"🔄 Loading player type: {player_type}")
        
        # Initialize new player instance with correct class names
        if player_type == "jriver":
            logger.info("📦 Creating JRiverPlayer instance...")
            print("📦 Creating JRiverPlayer instance...")
            self.player = JRiverPlayer(self.config, speak_func=self.speak)
        elif player_type == "vlc" or player_type == "mpris":
            logger.info("📦 Creating MPRISPlayer instance...")
            print("📦 Creating MPRISPlayer instance...")
            self.player = MPRISPlayer(self.config, speak_func=self.speak)
        elif player_type == "elisa":
            logger.info("📦 Creating ElisaPlayer instance...")
            print("📦 Creating ElisaPlayer instance...")
            self.player = ElisaPlayer(self.config, speak_func=self.speak)
        elif player_type == "strawberry":
            logger.info("📦 Creating StrawberryPlayer instance...")
            print("📦 Creating StrawberryPlayer instance...")
            self.player = StrawberryPlayer(self.config, speak_func=self.speak)
        else:
            logger.warning(f"⚠️ Unknown player type '{player_type}', defaulting to JRiverPlayer...")
            print(f"⚠️ Unknown player type '{player_type}', defaulting to JRiverPlayer...")
            self.player = JRiverPlayer(self.config, speak_func=self.speak)
        
        logger.info(f"✅ Player instance created: {type(self.player).__name__}")
        print(f"✅ Player instance created: {type(self.player).__name__}")
        
        # Update selection_handler with new player
        if hasattr(self, 'selection_handler'):
            self.selection_handler.player = self.player
            logger.info(f"✅ Updated selection_handler.player to {type(self.player).__name__}")
            print(f"✅ Updated selection_handler.player to {type(self.player).__name__}")
        
        # Update command_processor with new player
        if hasattr(self, 'command_processor'):
            self.command_processor.player = self.player
            logger.info(f"✅ Updated command_processor.player to {type(self.player).__name__}")
            print(f"✅ Updated command_processor.player to {type(self.player).__name__}")
        
        # Announce switch
        player_display_name = PLAYER_SCHEMAS.get(player_type, {}).get('name', player_type)
        
        # Check connection and speak status
        if self.player.health_check():
            logger.info(f"✅ Switched to {player_display_name}")
            print(f"✅ Switched to {player_display_name}")
            self.speak(f"Switched to {player_display_name}.")
        else:
            print(f"⚠️ Switched to {player_display_name}, but connection failed.")
            self.speak(f"Switched to {player_display_name}, but connection failed.")

    def speak(self, text):
        """Queues text to be spoken by the main thread."""
        # TTS Normalization
        text = text.replace("arr.", "arranged")
        text = text.replace("Op.", "Opus")
        text = text.replace("No.", "Number")
        
        # Remove redundant titles (e.g. "Silent Night: Silent Night" -> "Silent Night")
        # This happens often with classical music metadata
        import re
        # Pattern: Any text, followed by ": ", followed by the EXACT same text
        # We use backreference \1 to match the first group
        text = re.sub(r"(.+): \1", r"\1", text)
        
        print(f"🗣️ Queued to speak: {text}")
        self.speech_queue.put(text)

    def enter_command_mode(self):
        """Transitions the assistant to command mode."""
        self.state_machine.transition_to(self.STATE_COMMAND_MODE)
        self.state = self.state_machine.state  # Update backwards-compat property




    # Removed play_doctor, go_to_track, play_precise_album, play_album, play_generic
    # These are now handled by the Player interface or specific implementations


    # Removed search_artist_albums, handle_selection, go_to_track, what_is_playing_silent,
    # what_is_playing, list_tracks, play_random_genre as they are now handled by Player interface


    def normalize_command_text(self, text):
        """Normalizes spoken text to fix common recognition errors."""
        return self.text_normalizer.normalize(text, self.state, self.wake_word)

    def parse_number_word(self, text):
        """Parses a spoken number (1-99) from text."""
        return self.text_normalizer.parse_number(text)

    def speak_selection_options(self):
        """Speaks the current page of selection options."""
        self.selection_handler.speak_options()

    def handle_selection(self, text):
        """Handles user selection from a list."""
        self.selection_handler.handle_selection_command(text)

    def normalize_command(self, text):
        """Methods merged. Redirect to the regex-safe normalize_command_text."""
        return self.normalize_command_text(text)

    # Legacy method body removed to prevent 'tplays' corruption.
    # The 'hi' -> 'play' replacement in the old method was causing issues.



    def process_command(self, text):
        """Processes spoken text commands and routes them based on current state."""
        if not text:
            return
        
        # Normalize text
        text = self.normalize_command_text(text)
        
        print(f"📝 Processing: '{text}' (State: {self.state})")
        
        # Duplicate print for debugging (some setups have buffering issues)
        print(f"📝 Processing: '{text}' (State: {self.state})")
        
        # Strip "the " prefix if present
        if text.startswith("the "):
            text = text[4:]
        
        # Normalize "play" variants
        if text.startswith("play "):
            query = text.replace("play ", "").strip()
            if query and query[0].isupper():
                text = f"play {query.lower()}"
        
        # Check for command mode timeout
        if self.state == self.STATE_COMMAND_MODE:
            if self.state_machine.is_command_mode_expired():
                print("⏱ Command mode timed out, returning to wake word listening")
                self.state_machine.transition_to(self.STATE_LISTENING)
                self.state = self.state_machine.state
                  
        # State-based routing
        if self.state == self.STATE_WAITING_SELECTION:
            # Interrupt TTS if it's speaking (allows instant CLI selection)
            # User hears "1. Item A, 2. Item B, 3. Item C..."
            # User types "3" immediately - should interrupt and play
            if hasattr(self, 'tts') and self.tts:
                try:
                    self.tts.stop()  # Stop ongoing TTS playback
                    print(f"🔇 TTS interrupted by selection")
                except:
                    pass  # TTS stop might not be implemented or already stopped
            
            print(f"✅ Selection received: '{text}' (processing...)")
            self.handle_selection(text)
            # Sync state in case selection_handler cleared (returns to LISTENING)
            self.state = self.state_machine.state
            return
        
        if self.state == self.STATE_COMMAND_MODE:
            # In command mode, reset timer and process command
            self.state_machine.reset_command_timer()
            print(f"✅ Command received in command mode: '{text}'")
            
            # Delegate to command processor
            should_continue = self.command_processor.process(text, self.state)
            
            # Sync state in case selection_handler was used
            self.state = self.state_machine.state
            
            if not should_continue:
                return  # Quit was signaled
            return
        
        # STATE_LISTENING - wake word detection
        if self.state == self.STATE_LISTENING:
            # Check for wake word
            detected_wake_word = None
            for ww in [self.wake_word, self.wake_word.capitalize(), self.wake_word.upper()]:
                if text.startswith(ww + " ") or text == ww:
                    detected_wake_word = ww
                    break
            
            if not detected_wake_word:
                # No wake word - ignore
                print(f"🤷 Ignored (no wake word): {text}")
                self.log_ignored_command(text)
                return
            
            # Clear any pending commands in the queue when wake word is detected
            if self.command_queue:
                cleared = 0
                while not self.command_queue.empty():
                    try:
                        self.command_queue.get_nowait()
                        cleared += 1
                    except:
                        break
                if cleared > 0:
                    print(f"🧹 Cleared {cleared} stale command(s) from queue")
            
            # Strip wake word from command
            text = text[len(detected_wake_word):].strip()
            
            # Clean up any trailing/leading punctuation LEFT OVER after wake word removal
            text = text.lstrip(".,!?;: ")
            
            print(f"✅ Wake word detected! Command: '{text}'")
            
            # If no command after wake word, enter command mode
            if not text:
                self.state_machine.transition_to(self.STATE_COMMAND_MODE)
                self.state = self.state_machine.state
                self.speak("Yes?")
                return
            
            
            # Process the command via command processor
            should_continue = self.command_processor.process(text, self.state)
            
            # Sync state in case selection_handler was used
            self.state = self.state_machine.state
            
            if not should_continue:
                return  # Quit was signaled
            return
        
        # Fallback - should not reach here
        print(f"🤷 Ignored: {text}")
        self.log_ignored_command(text)

# --- Main Execution ---

import threading
import queue

def command_worker(assistant, command_queue):
    """Worker thread to process commands from the queue."""
    while True:
        text = command_queue.get()
        if text is None:
            break
        try:
            assistant.process_command(text)
        except KeyboardInterrupt:
            # Handle quit command from worker
            os._exit(0)
        except Exception as e:
            print(f"Error processing command: {e}")
        finally:
            command_queue.task_done()

def console_input_loop(assistant):
    """Reads input from stdin and processes it as commands."""
    print("⌨️  Console input enabled.")
    print("   - Global Shortcuts: 'Right/Left Arrows' (Instant, customizable)")
    print("   - Console Commands: Type number ('1', '12') or text ('play music') and press Enter.")
    import select
    
    while True:
        try:
            # Non-blocking check for input
            if select.select([sys.stdin], [], [], 0.1)[0]:
                text = sys.stdin.readline().strip()
                if text:
                    # Map arrow keys (if captured) and shortcuts
                    if text == '\x1b[C': text = "next"  # Right Arrow
                    elif text == '\x1b[D': text = "previous" # Left Arrow
                    elif text == 'n': text = "next"
                    elif text == 'p': text = "previous"
                    elif text == 's': text = "stop"
                    elif text == 'q': text = "quit"
                    
                    print(f"⌨️  Console input captured: '{text}'")
                    assistant.process_command(text)
        except ValueError:
            # Stdin closed
            break
        except Exception as e:
            # print(f"Console input error: {e}")
            break

def main_cli():
    """
    Direct CLI entry point (for tuxtalks-cli command).
    Always runs in CLI mode, no environment detection.
    """
    parser = argparse.ArgumentParser(description="TuxTalks Voice Assistant (CLI Mode)")
    parser.add_argument("--player", help="Specify the media player to use (e.g., jriver, elisa)")
    parser.add_argument("--setup", action="store_true", help="Run the setup wizard (CLI)")
    args = parser.parse_args()
    
    # Continue with CLI mode directly
    _run_cli(args)


def main():
    """
    Smart dispatcher entry point (for tuxtalks command).
    Auto-detects environment and launches appropriate interface.
    """
    parser = argparse.ArgumentParser(description="TuxTalks Voice Assistant")
    parser.add_argument("--player", help="Specify the media player to use (e.g., jriver, elisa)")
    parser.add_argument("--setup", action="store_true", help="Run the setup wizard (CLI)")
    parser.add_argument("--gui", action="store_true", help="Force GUI launcher (overrides environment detection)")
    parser.add_argument("--cli", action="store_true", help="Force CLI mode (overrides  environment detection)")
    args = parser.parse_args()

    # Environment Detection: Determine if GUI should be used
    def is_desktop_environment():
        """Check if running in a desktop environment with display."""
        if os.environ.get("DISPLAY"):  # X11/Wayland display available
            return True
        if os.environ.get("WAYLAND_DISPLAY"):  # Wayland-specific
            return True
        return False
    
    def is_ssh_session():
        """Check if running in SSH session."""
        return bool(os.environ.get("SSH_CLIENT") or os.environ.get("SSH_TTY"))
    
    # Decide interface mode
    use_gui = False
    if args.gui:
        use_gui = True
    elif args.cli:
        use_gui = False
    elif is_desktop_environment() and not is_ssh_session():
        # Auto-detect: desktop environment → use GUI
        use_gui = True
    
    # Launch GUI if appropriate (and not already in setup mode)
    if use_gui and not args.setup:
        import shutil
        launcher_cmd = "tuxtalks-launcher"
        if shutil.which(launcher_cmd):
            print("🖥️  Launching GUI...")
            subprocess.Popen([launcher_cmd])
            sys.exit(0)
        else:
            print(f"⚠️  GUI requested but '{launcher_cmd}' not found. Falling back to CLI.")
    
def _run_cli(args):
    """Common CLI startup logic (used by both main() and main_cli())."""
    import signal
    import sys
    import os
    from logger import setup_logger
    
    # Setup logging early
    log_level = cfg.get("LOG_LEVEL", "INFO")
    logger = setup_logger("tuxtalks-cli", log_level=log_level)
    logger.info("=" * 50)
    logger.info("TuxTalks CLI starting...")
    logger.debug(f"Log level: {log_level}")
    
    # Signal handler for Ctrl+C
    def signal_handler(sig, frame):
        logger.info("SIGINT received - exiting...")
        print("\n👋 Exiting...")
        os._exit(0)  # Force exit immediately
    
    signal.signal(signal.SIGINT, signal_handler)
    logger.debug("SIGINT handler registered")
    
    print("⌨️  Running in CLI mode")

    # 0. Check for Config (First Run)
    if not SYSTEM_CONFIG_FILE.exists() and not args.setup:
        print("⚠️  Configuration not found. Launching setup launcher...")
        import shutil
        launcher_cmd = "tuxtalks-launcher"
        if shutil.which(launcher_cmd):
            # Launch and exit
            subprocess.Popen([launcher_cmd])
            sys.exit(0)
        else:
            print(f"❌ '{launcher_cmd}' not found in PATH. Please run 'tuxtalks --setup' for CLI setup.")
            sys.exit(1)

    # Handle Setup CLI override
    if args.setup:
        cfg.setup_wizard()
        print("Setup complete. Please restart the application.")
        sys.exit(0)

    # Handle Player Override
    if args.player:
        cfg.config["PLAYER"] = args.player
        # We don't save this to disk to avoid permanent changes from a one-off flag, 
        # unless we want to? Let's keep it ephemeral for now, or maybe update config?
        # User might expect --player to just work for this session.
    # Handle Player Override
    if args.player:
        cfg.config["PLAYER"] = args.player
        print(f"🔧 Overriding player to: {args.player}")

    # Reload config to ensure we have latest if it was just created (though we exit above if it was missing)
    # But just in case
    cfg.load()

    # Check if setup is needed
    ACCESS_KEY = cfg.get("ACCESS_KEY")
    if not ACCESS_KEY:
        print("⚠️  No Access Key found.")
        if not cfg.setup_wizard():
            print("❌ Setup cancelled. Exiting.")
            sys.exit(1)
            
    MODEL_PATH = cfg.get("VOSK_MODEL_PATH")
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 4096  # Reduced from 8192 for lower latency

    # Ensure model exists (auto-download if needed)
    import model_manager
    if cfg.get("ASR_ENGINE", "vosk") == "vosk":
        if not model_manager.setup_vosk_model(MODEL_PATH):
            sys.exit(1)

    # Initialize PTT Listener
    # Initialize Input Listener (PTT & Shortcuts)
    from input_listener import InputListener
    
    # Define generic key bindings
    from input_controller import InputController
    input_ctrl = InputController()  # Instantiate here
    
    key_bindings = {}
    
    # Page Navigation
    next_key = cfg.get("PAGE_NEXT_KEY")
    prev_key = cfg.get("PAGE_PREV_KEY")
    if next_key: key_bindings[next_key] = "next"
    if prev_key: key_bindings[prev_key] = "previous"
    
    ptt_listener = None
    
    # Create listener if PTT enabled OR bindings exist
    if cfg.get("PTT_ENABLED") or key_bindings:
        ptt_key = cfg.get("PTT_KEY", "KEY_LEFTCTRL") if cfg.get("PTT_ENABLED") else None
        ptt_mode = cfg.get("PTT_MODE", "HOLD")
        
        # We pass command_queue later, but listener needs it at init logic or we pass it? 
        # Actually Listener needs queue at init. But command_queue is created below.
        # Let's create command_queue first.
        command_queue = queue.Queue()
        
        ptt_listener = InputListener(ptt_key=ptt_key, mode=ptt_mode, key_bindings=key_bindings, event_queue=command_queue)
        ptt_listener.start()
    else:
        command_queue = queue.Queue() # Create queue anyway if listener not started
    
    assistant = VoiceAssistant(input_controller=input_ctrl)
    
    # Check Player Connectivity
    if not assistant.player.health_check():
        print("⚠️  Player connection failed. Some commands may not work.")
        assistant.speak("I cannot connect to the media player. Please check your configuration.")

    # Start the worker thread
    assistant.command_queue = command_queue  # Give assistant access to queue for clearing
    worker = threading.Thread(target=command_worker, args=(assistant, command_queue), daemon=True)
    worker.start()
    
    # --- Initialize Speech Engines ---
    assistant.tts = get_tts_engine(cfg.get("TTS_ENGINE"), cfg)
    assistant.asr = get_asr_engine(cfg.get("ASR_ENGINE"), cfg)
    
    # Apply Custom Vocabulary (if any)
    vocab = cfg.get("CUSTOM_VOCABULARY")
    if vocab:
        print(f"📚 Loading {len(vocab)} custom vocabulary terms...")
        assistant.asr.set_grammar(vocab)
    
    # Start ASR
    assistant.asr.start()

    print("\n--- TuxTalks Voice Assistant Ready ---")
    
    # Start Console Input Thread
    console_thread = threading.Thread(target=console_input_loop, args=(assistant,), daemon=True)
    console_thread.start()
    
    assistant.speak("I am ready.")

    # 0b. Game Mode Startup Check
    if cfg.get("GAME_MODE_ENABLED"):
        assistant.game_manager.set_enabled(True)
        # Announce game mode on startup as requested
        # Wait slightly for "I am ready" to clear or queue it
        assistant.speak("Game mode enabled.")

    # Check timer for config polling
    last_cfg_check = time.time()

    try:
        while True:
            # 0. Poll Config (Every 1s)
            now = time.time()
            if now - last_cfg_check > 1.0:
                last_cfg_check = now
                try:
                    cfg.load() # Reload from disk
                    enabled_in_cfg = cfg.get("GAME_MODE_ENABLED", False)
                    # Sync if different
                    if enabled_in_cfg != assistant.game_manager.game_mode_enabled:
                        assistant.game_manager.set_enabled(enabled_in_cfg)
                        if enabled_in_cfg:
                            assistant.speak("Game mode enabled.")
                        else:
                            assistant.speak("Game mode disabled.")
                            
                    # Poll for Player Change
                    player_in_cfg = cfg.get("PLAYER")
                    # We can check class type or just store current name?
                    # Let's check assistant.config vs cfg? 
                    # assistant.config is ref to cfg, so it updates automatically when cfg.load() happens above?
                    # NO, python dicts are refs, but cfg.config is a dict.
                    # Wait, cfg object is shared.
                    # But we need to know what the current running player IS.
                    # We can check name of class? Or store it on assistant.
                    
                    # Hacky but works: check type names
                    current_type = "jriver"  # default
                    if isinstance(assistant.player, StrawberryPlayer): 
                        current_type = "strawberry"
                    elif isinstance(assistant.player, ElisaPlayer): 
                        current_type = "elisa"
                    elif isinstance(assistant.player, MPRISPlayer): 
                        current_type = "mpris"
                    
                    if player_in_cfg != current_type:
                        print(f"🔄 Player change detected: {current_type} -> {player_in_cfg}")
                        assistant.reload_player()
                        
                except Exception as e:
                    print(f"⚠️ Config poll error: {e}")

            # 1. Check for speech requests
            try:
                text_to_speak = assistant.speech_queue.get_nowait()
                if text_to_speak is None:
                    print("👋 Exiting...")
                    break

                # Stop ASR temporarily to prevent self-hearing and resource conflict
                if assistant.asr:
                    assistant.asr.pause()
                try:
                    assistant.tts.speak(text_to_speak)
                finally:
                    # Wait for physical echo to fade
                    if assistant.asr:
                        time.sleep(0.5)
                        assistant.asr.resume()
                
                assistant.speech_queue.task_done()
                
            except queue.Empty:
                pass

            # PTT Logic (Simulated for now via config/keyboard)
            # If PTT is enabled, we might need a way to tell ASR to ignore/listen?
            # For now, simplistic approach: ASR always listens, we ignore result if PTT off?
            # Or we can pass PTT state to ASR?
            # Let's keep it simple: consume queue but ignore unless PTT active or Command Mode.
            
            # 2. Read ASR
            try:
                # Non-blocking check for text?
                # ASRBase.get_next_text() is blocking.
                # We need non-blocking get from ASR's internal queue.
                # But our ASRBase interface says blocking.
                # Let's change tuxtalks main loop to be event driven or use non-blocking approach.
                # Actually, main loop needs to sleep to check PTT etc.
                pass 
            except: pass
            
            # Read from ASR queue (Queue access hack for now, standardized later)
            if not assistant.asr.text_queue.empty():
                 text = assistant.asr.text_queue.get()
                 command_queue.put(text)

            time.sleep(0.05)
                    
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
        os._exit(0)  # Force exit immediately
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            if 'assistant' in locals() and hasattr(assistant, 'asr'):
                assistant.asr.stop()
            if 'assistant' in locals() and hasattr(assistant, 'tts'):
                assistant.tts.stop()
            if 'assistant' in locals() and hasattr(assistant, 'player'):
                assistant.player.stop()
        except:
            pass
        
        print("👋 Exiting...")

if __name__ == "__main__":
    main()
