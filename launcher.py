
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import shutil
import pathlib
import json
import threading
import webbrowser
import importlib.metadata
import subprocess  # For launching tuxtalks-cli and tuxtalks-menu


try:
    setup_py_version = importlib.metadata.version("tuxtalks")
except Exception:
    setup_py_version = "1.0.29"

from config import cfg, PLAYER_SCHEMAS, Config
from player_interface import MediaPlayer
import model_manager
from game_manager import GameManager
from lal_manager import LALManager
from launcher_speech_tab import LauncherSpeechTab
from launcher_player_tab import LauncherPlayerTab
from launcher_games_tab import LauncherGamesTab
from launcher_input_tab import LauncherInputTab
from launcher_corrections_tab import LauncherCorrectionsTab
from launcher_vocabulary_tab import LauncherVocabularyTab
from launcher_training_tab import LauncherTrainingTab
from launcher_packs_tab import PacksTab
import i18n

# Initialize internationalization FIRST
i18n.set_language(cfg.get("UI_LANGUAGE", "en"))

# NOW import the translation function (after language is set)
from i18n import _



class ConfigGUI(LauncherSpeechTab, LauncherPlayerTab, LauncherGamesTab, LauncherCorrectionsTab, LauncherInputTab, LauncherVocabularyTab, LauncherTrainingTab):
    def _on_window_close(self):
        """Handle window close event (WM_DELETE_WINDOW)."""
        self.logger.info("_on_window_close() called")
        self._do_cleanup()
        self.root.quit()
    
    def _on_destroy(self):
        """Override root.destroy() to ensure cleanup."""
        self.logger.info("_on_destroy() called")
        self._do_cleanup()
        self._original_destroy()
    
    def _cleanup_on_exit(self):
        """atexit handler - last resort cleanup."""
        self.logger.info("_cleanup_on_exit() called (atexit)")
        self._do_cleanup()
    
    def _do_cleanup(self):
        """Actual cleanup logic - called by all exit paths."""
        import signal
        import subprocess as sp
        
        # Prevent multiple cleanups
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            self.logger.debug("Cleanup already done, skipping")
            return
        
        self._cleanup_done = True
        self.logger.info("Starting cleanup...")
        
        # Stop music playback before exiting
        try:
            from config import cfg
            import requests
            import dbus
            
            player_type = cfg.get("PLAYER", "jriver").lower()
            self.logger.info(f"Stopping {player_type} playback...")
            
            if player_type == "jriver":
                # JRiver: Use REST API
                ip = cfg.get("JRIVER_IP", "localhost")
                port = cfg.get("JRIVER_PORT", 52199)
                url = f"http://{ip}:{port}/MCWS/v1/Playback/Stop"
                requests.get(url, timeout=2)
                self.logger.info("✅ JRiver stopped")
                
            elif player_type in ["strawberry", "elisa", "vlc", "mpris"]:
                # MPRIS-based players: Use D-Bus
                bus = dbus.SessionBus()
                
                # Map player types to D-Bus service names
                service_map = {
                    "strawberry": "org.mpris.MediaPlayer2.strawberry",
                    "elisa": "org.mpris.MediaPlayer2.elisa",
                    "vlc": "org.mpris.MediaPlayer2.vlc",
                    "mpris": cfg.get("MPRIS_SERVICE", "org.mpris.MediaPlayer2.vlc")
                }
                
                service = service_map.get(player_type, "org.mpris.MediaPlayer2.vlc")
                player_obj = bus.get_object(service, '/org/mpris/MediaPlayer2')
                player_iface = dbus.Interface(player_obj, 'org.mpris.MediaPlayer2.Player')
                player_iface.Stop()
                self.logger.info(f"✅ {player_type} stopped via D-Bus")
            
        except Exception as e:
            self.logger.debug(f"Could not stop music: {e}")
            # Not critical if this fails
        
        # Stop any running tuxtalks-cli process
        if hasattr(self, 'tuxtalks_process') and self.tuxtalks_process and self.tuxtalks_process.poll() is None:
            pid = self.tuxtalks_process.pid
            self.logger.info(f"Stopping tuxtalks-cli (PID {pid})")
            try:
                self.tuxtalks_process.send_signal(signal.SIGTERM)
                try:
                    self.tuxtalks_process.wait(timeout=1)
                    self.logger.info("Process stopped gracefully")
                except sp.TimeoutExpired:
                    self.logger.warning("Timeout, sending SIGKILL")
                    self.tuxtalks_process.kill()
                    self.logger.info("Process killed")
            except Exception as e:
                self.logger.error(f"Error stopping process: {e}")
        
        # Nuclear fallback
        try:
            self.logger.debug("Fallback: killing all tuxtalks-cli processes")
            sp.run(["pkill", "-9", "-f", "tuxtalks-cli"], check=False)
        except:
            pass
        
        self.logger.info("Cleanup complete")
    
    def exit_app(self):
        """Exit button handler."""
        self.logger.info("exit_app() called (Exit button)")
        self._do_cleanup()
        self.root.quit()
    def __init__(self, root):
        import atexit
        from logger import setup_logger
        
        self.root = root
        self.config = cfg
        self.process = None
        self.tuxtalks_process = None  # Track launched CLI process
        self.root.title("TuxTalks Settings")
        
        # Setup logging
        log_level = cfg.get("LOG_LEVEL", "INFO")
        self.logger = setup_logger("tuxtalks-gui", log_level=log_level)
        self.logger.info("=" * 50)
        self.logger.info("GUI initialized")
        self.logger.debug(f"Log level: {log_level}")
        
        # Multiple cleanup strategies
        # 1. WM_DELETE_WINDOW protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self.logger.debug("WM_DELETE_WINDOW protocol bound to _on_window_close()")
        
        # 2. atexit handler (runs on any exit)
        atexit.register(self._cleanup_on_exit)
        self.logger.debug("atexit handler registered")
        
        # 3. Override destroy
        self._original_destroy = self.root.destroy
        self.root.destroy = self._on_destroy
        self.logger.debug("root.destroy() overridden")
        
        # Geometry handled in main()
        
        self.dynamic_vars = {} # Store StringVars for dynamic fields
        
        # Main Container
        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Header ---
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # --- Branding Section ---
        brand_frame = ttk.Frame(header_frame)
        brand_frame.pack(side=tk.LEFT)
        
        # 1. Logo (System Glyph)
        ttk.Label(brand_frame, text=_("🐧"), font=("Segoe UI Emoji", 32)).pack(side=tk.LEFT, padx=(5, 10))
        
        # 2. Text Lockup
        title_frame = ttk.Frame(brand_frame)
        title_frame.pack(side=tk.LEFT)
        
        # Row 1: "TuxTalks Settings"
        row1 = ttk.Frame(title_frame)
        row1.pack(fill=tk.X, anchor=tk.W)
        ttk.Label(row1, text=_("TuxTalks"), font=("Helvetica", 18, "bold")).pack(side=tk.LEFT)
        ttk.Label(row1, text=_(" Settings"), font=("Helvetica", 18, "normal"), foreground="gray").pack(side=tk.LEFT)
        
        # Row 2: Subtitle
        ttk.Label(title_frame, text=_("Advanced Voice Control for Linux"), font=("Helvetica", 9), foreground="gray").pack(anchor=tk.W)
        
        # Theme Selector (Right Aligned)
        theme_frame = ttk.Frame(header_frame)
        theme_frame.pack(side=tk.RIGHT, anchor=tk.CENTER)
        ttk.Label(theme_frame, text=_("Theme:")).pack(side=tk.LEFT, padx=5)
        self.theme_var = tk.StringVar(value=self.config.get("GUI_THEME", "default"))
        
        
        # Theme selection
        self.style = ttk.Style()
        
        # Curate Themes: Prioritize Sun Valley, include Clam/Alt, hide Legacy
        available = self.style.theme_names()
        self.themes = []
        
        # Priority Order
        priority = ["sun-valley-dark", "sun-valley-light", "clam", "alt"]
        for p in priority:
            if p in available:
                self.themes.append(p)
                
        # Start fresh for logic (don't rely on sorted() of all)
        if not self.themes: self.themes = sorted(available) # Fallback if nothing matches

        
        # Logic: If Sun Valley is loaded but config says "default", upgrade to Sun Valley
        current_theme = self.config.get("GUI_THEME", "default")
        if current_theme == "default" and "sun-valley-dark" in self.themes:
            current_theme = "sun-valley-dark"
            self.config.set("GUI_THEME", current_theme)
            
        self.theme_var = tk.StringVar(value=current_theme)

        self.theme_cb = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=self.themes, width=12, state="readonly")
        self.theme_cb.pack(side=tk.LEFT)
        self.theme_cb.bind("<<ComboboxSelected>>", self.change_theme)
        
        # Also apply it immediately
        try:
             self.style.theme_use(current_theme)
        except: pass
        
        # Scaling
        ttk.Label(theme_frame, text=_("Scale:")).pack(side=tk.LEFT, padx=(10, 5))
        self.scale_var = tk.DoubleVar(value=float(self.config.get("GUI_SCALING", 1.0)))
        scale_cb = ttk.Combobox(theme_frame, textvariable=self.scale_var, values=[1.0, 1.25, 1.5, 1.75, 2.0], width=5, state="readonly")
        scale_cb.pack(side=tk.LEFT)
        scale_cb.bind("<<ComboboxSelected>>", self.change_scaling)

        # --- Footer Buttons (Packed BEFORE Notebook) ---
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="tuxtalks-cli", command=self.launch_tuxtalks, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="tuxtalks-menu", command=self.launch_runtime_menu, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text=_("Stop"), command=self.stop_tuxtalks, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text=_("Save Config"), command=self.save_config, width=15).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text=_("Exit"), command=self.exit_app, width=10).pack(side=tk.RIGHT, padx=5)

        # --- Tabs ---
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # General Tab
        self.gen_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.gen_tab, text=_("General"))
        
        self.build_general_tab()

        # Player Tab
        self.build_player_tab()

        # Voice Tab
        self.voice_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.voice_tab, text=_("Voice"))
        self.build_voice_tab()

        # Games Tab
        self.games_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.games_tab, text=_("Games"))
        self.build_games_tab()
        
        # Content Packs Tab (LAL Framework)
        try:
            self.lal_manager = LALManager()
            self.packs_tab_obj = PacksTab(self.notebook, self.lal_manager)
            self.notebook.add(self.packs_tab_obj.frame, text=_("Content Packs"))
        except Exception as e:
            print(f"⚠️ Failed to initialize Content Packs tab: {e}")
        
        # Speech Engines Tab (ASR preference)
        self.speech_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.speech_tab, text=_("Speech Engines"))
        self.build_speech_tab()

        # Corrections Tab
        self.build_corrections_tab()

        # Input Tab (Calibration) implemented via LauncherInputTab
        self.input_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.input_tab, text=_("Input"))
        self.build_input_tab()
        
        # Build Vocabulary Tab (New Phase 11)
        self.vocabulary_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.insert(2, self.vocabulary_tab, text=_("Vocabulary")) # Insert after Voice/Player
        self.build_vocabulary_tab()
        
        # Build Voice Training Tab (Phase 3 - Manual Training)
        self.training_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.insert(3, self.training_tab, text=_("Voice Training"))
        self.build_training_tab()
        
        # Help Tab
        self.help_tab = ttk.Frame(self.notebook, padding="15")
        self.notebook.add(self.help_tab, text=_("Help"))
        self.build_help_tab()

        
        # Initial imports
        self.load_corrections()
        self.update_dynamic_fields()

    def build_general_tab(self):
        # Wake Word
        wrapper = ttk.Frame(self.gen_tab)
        wrapper.pack(fill=tk.X, pady=10)
        
        lbl_frame = ttk.Labelframe(wrapper, text=_("Wake Word Settings"), padding=15)
        lbl_frame.pack(fill=tk.X)
        
        ttk.Label(lbl_frame, text=_("Wake Word:")).pack(side=tk.LEFT)
        self.wake_var = tk.StringVar(value=self.config.get("WAKE_WORD"))
        ttk.Entry(lbl_frame, textvariable=self.wake_var, width=20).pack(side=tk.LEFT, padx=10)
        ttk.Label(lbl_frame, text="(e.g. 'Mango', 'Computer')").pack(side=tk.LEFT)

        # Model Section
        model_frame = ttk.Labelframe(wrapper, text=_("Speech Recognition (Vosk)"), padding=15)
        model_frame.pack(fill=tk.X, pady=15)
        
        row1 = ttk.Frame(model_frame)
        row1.pack(fill=tk.X)
        
        ttk.Label(row1, text=_("Active Model:")).pack(side=tk.LEFT)
        self.model_options = model_manager.get_available_models()
        current = self.config.get("VOSK_MODEL_PATH")
        if current not in self.model_options and current:
             self.model_options.append(current)
        
        self.model_var = tk.StringVar(value=current)
        self.model_combo = ttk.Combobox(row1, textvariable=self.model_var, values=self.model_options, width=40)
        self.model_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # Buttons
        row2 = ttk.Frame(model_frame)
        row2.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(row2, text=_("Browse Folder"), command=self.browse_model).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text=_("Download from URL"), command=self.import_model_url).pack(side=tk.LEFT, padx=2)
        ttk.Button(row2, text=_("Delete Selected"), command=self.delete_model).pack(side=tk.RIGHT, padx=2)

    def build_voice_tab(self):
        # TTS Voice (Piper)
        wrapper = ttk.Frame(self.voice_tab)
        wrapper.pack(fill=tk.X, pady=10)
        
        voice_frame = ttk.Labelframe(wrapper, text=_("Text-to-Speech (Piper)"), padding=15)
        voice_frame.pack(fill=tk.X)
        
        row1 = ttk.Frame(voice_frame)
        row1.pack(fill=tk.X)
        
        ttk.Label(row1, text=_("Active Voice:")).pack(side=tk.LEFT)
        
        from voice_manager import VoiceManager
        self.vm = VoiceManager()
        self.voice_options = self.vm.get_available_voices()
        
        current_voice = self.config.get("PIPER_VOICE")
        if current_voice not in self.voice_options:
            current_voice = "en_GB-cori-high"
            
        self.voice_var = tk.StringVar(value=current_voice)
        self.voice_combo = ttk.Combobox(row1, textvariable=self.voice_var, values=self.voice_options, state="readonly", width=40)
        self.voice_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        row2 = ttk.Frame(voice_frame)
        row2.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(row2, text=_("Delete Voice"), command=self.delete_voice).pack(side=tk.RIGHT)
        
        # Import
        imp_frame = ttk.Labelframe(wrapper, text=_("Import New Voice"), padding=15)
        imp_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(imp_frame, text=_("Download from URL"), command=self.import_voice_url).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        ttk.Button(imp_frame, text=_("Load from File (.onnx)"), command=self.import_voice_file).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)



    def build_help_tab(self):
        text_area = tk.Text(self.help_tab, font=("Consolas", 10), wrap=tk.WORD, padx=10, pady=10)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = ttk.Scrollbar(self.help_tab, command=text_area.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.config(yscrollcommand=scroll.set)
        
        help_msg = """TuxTalks Help

(See main documentation for full details)

Supported Players:
- JRiver
- Strawberry
- Elisa
- VLC

Commands:
"Play [artist]"
"Play random [genre]"
"Next track"
"Stop"

---
Adding Custom Games (New!)
You can add any game via the 'Add' button in the Games tab.

* Installation Keyword:
  Leave this BLANK for most games.
  Only use this if you have multiple copies of the same game (e.g. Steam vs GOG) and need to distinguish them. The keyword should be a unique folder name in the installation path (e.g. 'steamapps' or 'GOG').
"""
        text_area.insert("1.0", help_msg)
        text_area.config(state=tk.DISABLED)

    # --- Actions ---
    
    def change_theme(self, event):
        theme = self.theme_var.get()
        try:
             s = ttk.Style()
             s.theme_use(theme)
             
             # Force Root Background Update (Fixes dark artifacts on light themes)
             bg_color = s.lookup('TFrame', 'background')
             if bg_color:
                 self.root.configure(background=bg_color)
                 # Also update main frame if needed, though TFrame usually handles it
                 
        except:
             pass
        self.config.set("GUI_THEME", theme)
        self.config.save()
        
    def change_scaling(self, event):
        scale = self.scale_var.get()
        self.config.set("GUI_SCALING", scale)
        self.config.save()
        try:
            self.root.tk.call('tk', 'scaling', scale)
            messagebox.showinfo(_("Info"), _("Scaling saved. Restart required for full effect."))
        except:
            pass

    def has_unsaved_changes(self):
        if self.wake_var.get() != self.config.get("WAKE_WORD"): return True
        return False
        
    def launch_tuxtalks(self):
        """Launch the TuxTalks assistant"""
        if self.tuxtalks_process and self.tuxtalks_process.poll() is None:
            messagebox.showwarning(_("Warning"), _("TuxTalks is already running!"))
            return
        try:
            # Save config first
            self.config.save()
            # Launch with stdin pipe for graceful shutdown
            self.tuxtalks_process = subprocess.Popen(
                ["tuxtalks-cli"],
                stdin=subprocess.PIPE,
                text=False  # Use bytes for stdin
            )
        except Exception as e:
            messagebox.showerror(_("Error"), f"Failed to start assistant:\n{e}")
    
    def launch_runtime_menu(self):
        """Launch the TuxTalks runtime menu window."""
        try:
            subprocess.Popen(["tuxtalks-menu"])
        except Exception as e:
            messagebox.showerror(_("Error"), f"Failed to start runtime menu:\n{e}")

    def stop_tuxtalks(self):
        """Send graceful quit command to tuxtalks-cli."""
        if self.tuxtalks_process and self.tuxtalks_process.poll() is None:
            try:
                # Send "quit" command via stdin for graceful shutdown
                self.tuxtalks_process.stdin.write(b"quit\n")
                self.tuxtalks_process.stdin.flush()
                messagebox.showinfo(_("Stopping"), _("Sent quit command to assistant"))
                # Set to None after a delay to allow process to exit
                self.root.after(2000, lambda: setattr(self, 'tuxtalks_process', None))
            except Exception as e:
                # Fallback to terminate if stdin doesn't work
                self.tuxtalks_process.terminate()
                self.tuxtalks_process = None
                messagebox.showinfo(_("Stopped"), _("Assistant stopped"))
        else:
            messagebox.showinfo(_("Info"), _("Assistant is not running"))

    def save_config(self):
        self.config.set("GUI_THEME", self.theme_var.get())
        self.config.set("GUI_SCALING", self.scale_var.get())
        self.config.set("WAKE_WORD", self.wake_var.get())
        self.config.set("VOSK_MODEL_PATH", self.model_var.get())
        self.config.set("PIPER_VOICE", self.voice_var.get())
        self.config.set("PTT_ENABLED", self.ptt_enabled_var.get())
        self.config.set("PTT_MODE", self.ptt_mode_var.get())
        self.config.set("PTT_KEY", self.ptt_key_var.get())
        
        # Save selected player
        self.config.set("PLAYER", self.player_var.get())
        
        for k, v in self.dynamic_vars.items():
             self.config.set(k, v.get())
             
        self.config.save()
        if hasattr(self, 'gm'):
             for p in self.gm.profiles:
                  p.save_commands()
                  p.save_macros()
        messagebox.showinfo(_("Saved"), _("Configuration saved."))

    def exit_app(self):
        self.root.destroy()
        
    def browse_model(self):
        path = filedialog.askdirectory(title="Select Model Utils", initialdir=self.model_var.get())
        if path: self.model_var.set(path)

    def import_model_url(self):
        url = simpledialog.askstring("Import Model", "Enter URL:", initialvalue="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        if url:
             name = simpledialog.askstring("Name", "Name:", initialvalue="vosk-model-custom")
             if name:
                  dest = pathlib.Path.home() / "jriver-voice" / name
                  if dest.exists() and not messagebox.askyesno("Overwrite?", f"{dest} exists. Overwrite?"): return
                  threading.Thread(target=lambda: self._download_model(url, dest), daemon=True).start()
                  messagebox.showinfo(_("Downloading"), _("Downloading in background..."))
                  
    def _download_model(self, url, dest):
        try:
             model_manager.download_and_extract_model(url, dest)
             self.root.after(0, lambda: [self.model_var.set(str(dest)), messagebox.showinfo("Success", f"Downloaded to {dest}")])
        except Exception as e:
             self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

    def delete_model(self):
        model_path = self.model_var.get()
        if model_path and messagebox.askyesno("Delete?", f"Delete {model_path}?"):
             if model_manager.delete_model(model_path):
                  self.model_options = model_manager.get_available_models()
                  self.model_combo['values'] = self.model_options
                  self.model_var.set(self.model_options[0] if self.model_options else "")
                  messagebox.showinfo(_("Success"), _("Deleted."))
             else:
                  messagebox.showerror(_("Error"), _("Failed."))

    def delete_voice(self):
        voice = self.voice_var.get()
        if voice and messagebox.askyesno("Delete?", f"Delete {voice}?"):
             if self.vm.delete_voice(voice):
                  self.refresh_voice_list()
                  self.voice_var.set(self.voice_options[0] if self.voice_options else "")
                  messagebox.showinfo(_("Success"), _("Deleted"))
             else:
                  messagebox.showinfo(_("Error"), _("Failed (is it built-in?)"))
                  

    def import_voice_url(self):
        url = simpledialog.askstring("Import Voice", "Enter URL of .onnx file (must have .onnx.json too):")
        if not url: return
        
        name = simpledialog.askstring("Voice Name", "Enter a name for this voice:", initialvalue="custom-voice")
        if not name: return
        
        def run_import():
            if self.vm.install_voice_from_url(url, name):
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Voice '{name}' installed!"))
                self.root.after(0, self.refresh_voice_list)
            else:
                self.root.after(0, lambda: messagebox.showerror(_("Error"), _("Failed to install voice.")))
                
        threading.Thread(target=run_import, daemon=True).start()
        messagebox.showinfo(_("Importing"), _("Downloading voice in background..."))

    def import_voice_file(self):
        onnx_path = filedialog.askopenfilename(title="Select .onnx file", filetypes=[("ONNX Model", "*.onnx")])
        if not onnx_path: return
        
        json_path = filedialog.askopenfilename(title="Select .onnx.json file", filetypes=[("JSON Config", "*.json")])
        if not json_path: return
        
        name = simpledialog.askstring("Voice Name", "Enter a name for this voice:", initialvalue="custom-voice")
        if not name: return
        
        if self.vm.install_voice_from_local(onnx_path, json_path, name):
            messagebox.showinfo("Success", f"Voice '{name}' imported!")
            self.refresh_voice_list()
        else:
            messagebox.showerror(_("Error"), _("Failed to import voice."))

    def refresh_voice_list(self):
        self.voice_options = self.vm.get_available_voices()
        self.voice_combo['values'] = self.voice_options

    def test_connection(self):
        # Create a temporary config object
        test_cfg = Config()
        test_cfg._config = self.config._config.copy()
        
        # Update with current UI values
        test_cfg.set("PLAYER", self.player_var.get())
        for key, var in self.dynamic_vars.items():
            val = var.get()
            player = self.player_var.get()
            schema = PLAYER_SCHEMAS.get(player, {})
            field_info = schema.get("fields", {}).get(key, {})
            if field_info.get("type") == "number":
                try:
                    val = int(val)
                except ValueError:
                    pass
            test_cfg.set(key, val)
            
        # Instantiate player
        player_type = test_cfg.get("PLAYER")
        
        try:
            if player_type == "jriver":
                from players.jriver import JRiverPlayer
                player = JRiverPlayer(test_cfg, speak_func=lambda x: None)
            elif player_type == "strawberry":
                from players.strawberry import StrawberryPlayer
                player = StrawberryPlayer(test_cfg, speak_func=lambda x: None)
            elif player_type == "elisa":
                from players.elisa import ElisaPlayer
                player = ElisaPlayer(test_cfg, speak_func=lambda x: None)
            elif player_type == "mpris":
                from players.mpris import MPRISPlayer
                player = MPRISPlayer(test_cfg, speak_func=lambda x: None)
            else:
                messagebox.showinfo("Info", f"Test connection not implemented for {player_type}")
                return

            if player.health_check():
                messagebox.showinfo("Success", f"Connection to {player_type} successful!")
            else:
                msg = f"Could not connect to {player_type}."
                if player_type == "mpris":
                    service = test_cfg.get("MPRIS_SERVICE")
                    if "PLAYER_NAME" in service:
                        msg += "\n\nPlease replace 'PLAYER_NAME' with the actual service name (e.g., vlc)."
                    else:
                        msg += f"\n\nEnsure '{service}' is running."
                messagebox.showerror("Failure", msg)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error testing connection: {e}")

def main():
    print("Starting TuxTalks Launcher (Standard Mode)...")
    
    # Load Config (defaults)
    config = cfg
    
    root = tk.Tk()
    root.title(f"TuxTalks Settings (v{setup_py_version})")  # Use dynamic version if possible, else hardcoded
    
    # --- Theme Loading (Sun Valley) ---
    # --- Theme Loading (Sun Valley) ---
    base_dir = pathlib.Path(__file__).parent.resolve()
    # Correct path: theme/sv_ttk/sv.tcl
    theme_file = base_dir / "theme" / "sv_ttk" / "sv.tcl"
    
    print(f"DEBUG: Base Directory: {base_dir}")
    print(f"DEBUG: Looking for theme at: {theme_file}")
    
    if theme_file.exists():
        print("DEBUG: Theme file found. Attempting to source...")
        try:
            root.tk.call("source", str(theme_file))
            print("DEBUG: Theme sourced successfully.")
            # root.tk.call("set_theme", "dark") # invalid in sv.tcl 
        except Exception as e:
            print(f"⚠️ Failed to load Sun Valley theme: {e}")
    else:
         print(f"⚠️ Theme file not found: {theme_file}")
         print(f"DEBUG: Contents of base_dir: {[p.name for p in base_dir.iterdir()]}")

    # Set icon if available
    icon_path = base_dir / "resources" / "icon.png"
    if icon_path.exists():
        try:
            photo = tk.PhotoImage(file=str(icon_path))
            root.iconphoto(False, photo)
        except Exception: pass
        
    
    
    # Initialize the Application
    app = ConfigGUI(root) 
    
    # Set geometry
    root.geometry("1000x900")
    
    root.mainloop()

if __name__ == "__main__":
    main()
