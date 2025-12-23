import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import pathlib
import i18n
from i18n import _
from config import cfg

# Language to Vosk Model Mapping
LANGUAGE_MODELS = {
    "en": {
        "name": "English (US) - Small",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        "size": "40MB"
    },
    "es": {
        "name": "Spanish - Small",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip",
        "size": "39MB"
    },
    "de": {
        "name": "German - Small",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip",
        "size": "45MB"
    },
    "fr": {
        "name": "French - Small",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip",
        "size": "44MB"
    },
    "uk": {
        "name": "Ukrainian - Nano",
        "url": "https://alphacephei.com/vosk/models/vosk-model-small-uk-v3-nano.zip",
        "size": "50MB"
    },
    "ar": {
        "name": "Arabic - Standard",
        "url": "https://alphacephei.com/vosk/models/vosk-model-ar-mgb2-0.4.zip",
        "size": "80MB"
    }
}

class SetupWizard(tk.Toplevel):
    def __init__(self, parent, on_complete_callback):
        super().__init__(parent)
        self.title(_("TuxTalks First-Run Setup"))
        self.geometry("650x550")
        self.resizable(False, False)
        self.on_complete = on_complete_callback
        
        # Center the window
        self.transient(parent)
        self.grab_set()
        
        self.current_step = 0
        self.steps = [
            self.step_welcome,
            self.step_language,
            self.step_voice_model,
            self.step_media_game,
            self.step_finish
        ]
        
        # UI State
        self.selected_lang = tk.StringVar(value=cfg.get("UI_LANGUAGE", "en"))
        self.download_progress = tk.DoubleVar(value=0)
        self.status_msg = tk.StringVar(value=_("Ready"))
        
        self.setup_ui()
        self.show_step(0)
        
        # Handle "X" (Close button)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle window close event."""
        if self.current_step < len(self.steps) - 1:
            # If not on the last page, explain that closing marks it as done.
            if messagebox.askyesno(_("Skip Setup?"), _("Closing this window will skip the setup wizard. You can still configure everything manually in the settings.\n\nSkip and don't show again?")):
                self.finish()
        else:
            self.finish()

    def setup_ui(self):
        # Progress Bar at the top
        self.step_progress = ttk.Progressbar(self, maximum=len(self.steps)-1)
        self.step_progress.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Main content frame
        self.content_frame = ttk.Frame(self, padding="20")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Navigation buttons
        self.nav_frame = ttk.Frame(self, padding="20")
        self.nav_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.btn_back = ttk.Button(self.nav_frame, text=i18n._("Back"), command=self.prev_step)
        self.btn_back.pack(side=tk.LEFT)
        
        self.btn_next = ttk.Button(self.nav_frame, text=i18n._("Next"), command=self.next_step)
        self.btn_next.pack(side=tk.RIGHT)

    def show_step(self, step_idx):
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
        self.current_step = step_idx
        self.step_progress['value'] = step_idx
        
        # Manage button states
        self.btn_back.config(state=tk.NORMAL if step_idx > 0 else tk.DISABLED)
        btn_next_text = i18n._("Finish") if step_idx == len(self.steps)-1 else i18n._("Next")
        self.btn_next.config(text=btn_next_text)
        
        # Run step function
        self.steps[step_idx]()

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self.show_step(self.current_step + 1)
        else:
            self.finish()

    def prev_step(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def step_welcome(self):
        ttk.Label(self.content_frame, text=i18n._("Welcome to TuxTalks! 🐧"), font=("Helvetica", 24, "bold")).pack(pady=(0, 20))
        
        msg = i18n._("TuxTalks is your powerful, secure, and offline voice command assistant for Linux gaming.\n\n"
              "This wizard will help you set up your core preferences in just a few minutes so you can start talking to your favorite games and media players.")
        
        lbl = ttk.Label(self.content_frame, text=msg, wraplength=550, justify=tk.LEFT)
        lbl.pack(pady=10)
        
        ttk.Label(self.content_frame, text=i18n._("Ready to begin?")).pack(pady=20)

    def step_language(self):
        ttk.Label(self.content_frame, text=i18n._("Step 1: Interface Language"), font=("Helvetica", 18, "bold")).pack(pady=(0, 20))
        
        ttk.Label(self.content_frame, text=i18n._("Select the language for the TuxTalks interface:")).pack(pady=10)
        
        languages = {
            "English": "en",
            "Español": "es",
            "Deutsch": "de",
            "Français": "fr",
            "Українська": "uk",
            "Cymraeg": "cy",
            "العربية": "ar"
        }
        
        # Reverse mapping for display
        lang_to_display = {v: k for k, v in languages.items()}
        selected_display = tk.StringVar(value=lang_to_display.get(self.selected_lang.get(), "English"))
        
        lang_combo = ttk.Combobox(self.content_frame, textvariable=selected_display, values=list(languages.keys()), state="readonly", width=30)
        lang_combo.pack(pady=10)
        
        def on_lang_change(event):
            code = languages[selected_display.get()]
            self.selected_lang.set(code)
            cfg.set("UI_LANGUAGE", code)
            i18n.set_language(code)
            # We don't refresh the wizard's own text yet to avoid complexity, 
            # but we save the preference.
            
        lang_combo.bind("<<ComboboxSelected>>", on_lang_change)
        
        msg = i18n._("Note: RTL support is automatically enabled for Arabic.")
        ttk.Label(self.content_frame, text=msg, font=("Helvetica", 9, "italic"), foreground="gray").pack(pady=10)

    def step_voice_model(self):
        ttk.Label(self.content_frame, text=i18n._("Step 2: Voice Recognition (ASR)"), font=("Helvetica", 18, "bold")).pack(pady=(0, 20))
        
        lang_code = self.selected_lang.get()
        model_info = LANGUAGE_MODELS.get(lang_code, LANGUAGE_MODELS['en'])
        
        msg = i18n._("To process your voice offline, TuxTalks needs a language model.\n\n"
              "Based on your language selection, we recommend the following model:")
        ttk.Label(self.content_frame, text=msg, wraplength=550).pack(pady=10)
        
        model_frame = ttk.Frame(self.content_frame, padding=10, relief="groove")
        model_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(model_frame, text=f"{model_info['name']} ({model_info['size']})", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT)
        
        self.btn_download = ttk.Button(model_frame, text=i18n._("Download & Install"), command=self.download_model)
        self.btn_download.pack(side=tk.RIGHT)
        
        # Progress tracking
        self.progress_bar = ttk.Progressbar(self.content_frame, variable=self.download_progress, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(20, 5))
        
        ttk.Label(self.content_frame, textvariable=self.status_msg).pack()

    def download_model(self):
        self.btn_download.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_back.config(state=tk.DISABLED)
        
        lang_code = self.selected_lang.get()
        model_info = LANGUAGE_MODELS.get(lang_code, LANGUAGE_MODELS['en'])
        
        url = model_info['url']
        dest_name = url.split('/')[-1].replace(".zip", "")
        dest_path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "models" / dest_name
        
        def run():
            import urllib.request
            import zipfile
            import shutil
            
            try:
                self.status_msg.set(i18n._("Downloading..."))
                zip_path = "setup_model.zip"
                
                def reporthook(blocknum, blocksize, totalsize):
                    readsofar = blocknum * blocksize
                    if totalsize > 0:
                        percent = readsofar * 1e2 / totalsize
                        self.download_progress.set(percent)
                    else:
                        self.download_progress.set(0)

                urllib.request.urlretrieve(url, zip_path, reporthook)
                
                self.status_msg.set(i18n._("Extracting..."))
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall("temp_wizard_extract")
                
                # Move folder
                extracted = list(pathlib.Path("temp_wizard_extract").iterdir())[0]
                if dest_path.exists():
                    shutil.rmtree(dest_path)
                shutil.move(str(extracted), str(dest_path))
                
                # Cleanup
                os.remove(zip_path)
                shutil.rmtree("temp_wizard_extract")
                
                cfg.set("VOSK_MODEL_PATH", str(dest_path))
                self.status_msg.set(i18n._("Vosk Model Installed Successfully! ✅"))
                self.after(0, lambda: self.btn_next.config(state=tk.NORMAL))
                
            except Exception as e:
                self.status_msg.set(f"Error: {str(e)}")
                self.after(0, lambda: self.btn_download.config(state=tk.NORMAL))
            
            finally:
                self.after(0, lambda: self.btn_back.config(state=tk.NORMAL))

        threading.Thread(target=run, daemon=True).start()

    def step_media_game(self):
        ttk.Label(self.content_frame, text=i18n._("Step 3: Initial Integration"), font=("Helvetica", 18, "bold")).pack(pady=(0, 20))
        
        ttk.Label(self.content_frame, text=i18n._("Choose your primary media player:")).pack(anchor=tk.W, pady=5)
        
        players = ["JRiver Media Center", "Strawberry Music Player", "Elisa Music Player", "VLC / Generic (MPRIS)"]
        player_map = {players[0]: "jriver", players[1]: "strawberry", players[2]: "elisa", players[3]: "mpris"}
        
        self.player_var = tk.StringVar(value=players[0])
        player_combo = ttk.Combobox(self.content_frame, textvariable=self.player_var, values=players, state="readonly")
        player_combo.pack(fill=tk.X, pady=5)
        
        ttk.Label(self.content_frame, text=i18n._("Tip: You can change this and add games later in the main settings.")).pack(anchor=tk.W, pady=20)
        
        def on_player_change(event):
            cfg.set("PLAYER", player_map[self.player_var.get()])

    def step_finish(self):
        ttk.Label(self.content_frame, text=i18n._("All Set! 🎉"), font=("Helvetica", 24, "bold")).pack(pady=(0, 20))
        
        msg = i18n._("Setup is complete. TuxTalks is now configured with your language and voice preferences.\n\n"
              "Click 'Finish' to open the main settings where you can further customize your experience, add games, and calibrate your microphone.")
        
        ttk.Label(self.content_frame, text=msg, wraplength=550).pack(pady=10)
        
        ttk.Label(self.content_frame, text=i18n._("Happy Gaming!"), font=("Helvetica", 12, "italic")).pack(pady=20)

    def finish(self):
        cfg.set("FIRST_RUN_COMPLETE", True)
        cfg.save()
        self.grab_release()
        self.destroy()
        if self.on_complete:
            self.on_complete()

# For testing independently
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    SetupWizard(root, lambda: print("Setup Complete!"))
    root.mainloop()
