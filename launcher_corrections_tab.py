import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import json
import time
import pathlib
from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
from contextlib import contextmanager
from i18n import _

class LauncherCorrectionsTab:
    def build_corrections_tab(self):
        """Builds the Corrections Tab UI."""
        self.corr_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.corr_tab, text=_("Corrections"))
        
        # Use PanedWindow for flexible resizing
        paned = tk.PanedWindow(self.corr_tab, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=4)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # --- Top Pane: Active Corrections ---
        top_pane = ttk.Frame(paned)
        paned.add(top_pane, height=200)
        
        # Buttons for Corrections
        btn_frame = ttk.Frame(top_pane)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text=_("Add"), command=self.add_correction).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=_("Edit"), command=self.edit_correction).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text=_("Delete"), command=self.delete_correction).pack(side=tk.LEFT, padx=2)
        
        # Corrections List
        corr_list_frame = ttk.LabelFrame(top_pane, text=_("Voice Corrections (Heard -> Meant)"), padding="5")
        corr_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        columns = ("heard", "meant")
        self.corr_tree = ttk.Treeview(corr_list_frame, columns=columns, show="headings")
        self.corr_tree.heading("heard", text=_("When I hear..."))
        self.corr_tree.heading("meant", text=_("I should understand..."))
        self.corr_tree.column("heard", width=200)
        self.corr_tree.column("meant", width=200)
        self.corr_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(corr_list_frame, orient=tk.VERTICAL, command=self.corr_tree.yview)
        self.corr_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Bottom Pane: Tools (Ignored + Test) ---
        bottom_pane = ttk.Frame(paned)
        paned.add(bottom_pane)
        
        # Test Frame
        test_frame = ttk.LabelFrame(bottom_pane, text=_("Test & Train"), padding="5")
        test_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        rec_frame = ttk.Frame(test_frame)
        rec_frame.pack(fill=tk.X)
        
        self.test_btn = ttk.Button(rec_frame, text=_("🎤 Record"), command=self.test_voice_recording)
        self.test_btn.pack(side=tk.LEFT, padx=5)
        
        self.duration_var = tk.IntVar(value=10)
        ttk.Label(rec_frame, text=_("Dur:")).pack(side=tk.LEFT)
        self.duration_scale = ttk.Scale(rec_frame, from_=5, to=30, variable=self.duration_var, orient=tk.HORIZONTAL)
        self.duration_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.test_result_var = tk.StringVar(value="(Ready)")
        ttk.Label(test_frame, textvariable=self.test_result_var).pack(pady=2)
        
        train_row = ttk.Frame(test_frame)
        train_row.pack(fill=tk.X, pady=2)
        ttk.Button(train_row, text=_("Add as Correction"), command=self.add_from_test).pack(side=tk.LEFT, expand=True)
        
        # Train Buttons Row
        train_btns = ttk.Frame(test_frame)
        train_btns.pack(fill=tk.X, pady=2)
        ttk.Button(train_btns, text=_("Targeted Train"), command=self.train_phrase).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(train_btns, text=_("Basic"), command=self.train_basic_phrase).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(train_btns, text=_("Advanced"), command=self.train_advanced_phrase).pack(side=tk.LEFT, expand=True, fill=tk.X)

        # Ignored Frame
        ignored_frame = ttk.LabelFrame(bottom_pane, text=_("Recent Ignored/Missed Commands"), padding="5")
        ignored_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        
        ign_btn_frame = ttk.Frame(ignored_frame)
        ign_btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=2)
        
        ttk.Button(ign_btn_frame, text=_("Use Selected"), command=self.use_ignored_command).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(ign_btn_frame, text=_("Delete"), command=self.delete_ignored_command).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(ign_btn_frame, text=_("Clear All"), command=self.clear_ignored_commands).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(ign_btn_frame, text=_("Refresh"), command=self.load_ignored_commands).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.ignored_list = tk.Listbox(ignored_frame, height=6, selectmode=tk.EXTENDED)
        ignored_scroll = ttk.Scrollbar(ignored_frame, orient=tk.VERTICAL, command=self.ignored_list.yview)
        
        ignored_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.ignored_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.ignored_list.configure(yscroll=ignored_scroll.set)

        self.load_ignored_commands()
        self.load_corrections()

    def load_corrections(self):
        for item in self.corr_tree.get_children():
            self.corr_tree.delete(item)
        corrections = self.config.get("VOICE_CORRECTIONS") or {}
        for heard, meant in corrections.items():
            self.corr_tree.insert("", tk.END, values=(heard, meant))

    def add_correction(self):
        heard = simpledialog.askstring("Add Correction", "When I hear (misrecognized phrase):")
        if not heard: return
        meant = simpledialog.askstring("Add Correction", f"I should understand '{heard}' as:")
        if not meant: return
        self.corr_tree.insert("", tk.END, values=(heard, meant))
        self.update_corrections_config()

    def edit_correction(self):
        selected = self.corr_tree.selection()
        if not selected: return
        item = self.corr_tree.item(selected[0])
        old_heard, old_meant = item['values']
        
        heard = simpledialog.askstring("Edit Correction", "When I hear:", initialvalue=old_heard)
        if not heard: return
        meant = simpledialog.askstring("Edit Correction", "I should understand as:", initialvalue=old_meant)
        if not meant: return
        
        self.corr_tree.item(selected[0], values=(heard, meant))
        self.update_corrections_config()

    def delete_correction(self):
        selected = self.corr_tree.selection()
        if not selected: return
        if messagebox.askyesno(_("Confirm Delete"), _("Delete selected correction?")):
            self.corr_tree.delete(selected[0])
            self.update_corrections_config()

    def update_corrections_config(self):
        corrections = {}
        for item in self.corr_tree.get_children():
            heard, meant = self.corr_tree.item(item)['values']
            corrections[heard] = meant
        self.config.set("VOICE_CORRECTIONS", corrections)
        self.config.save()

    def load_ignored_commands(self):
        self.ignored_list.delete(0, tk.END)
        path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "ignored_commands.json"
        if not path.exists(): return
        try:
            with open(path, "r") as f:
                data = json.load(f)
                # Data is list of dicts: [{"text": "...", "timestamp": ...}]
                # We want the text, most recent first
                for entry in reversed(data):
                    self.ignored_list.insert(tk.END, entry.get("text", ""))
        except Exception as e:
            print(f"Error loading ignored: {e}")

    def clear_ignored_commands(self):
        path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "ignored_commands.json"
        try:
            with open(path, "w") as f:
                json.dump([], f)
            self.load_ignored_commands()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear log: {e}")

    def delete_ignored_command(self):
        selection = self.ignored_list.curselection()
        if not selection: return
        for i in reversed(selection):
            self.ignored_list.delete(i)
        # Note: This only deletes from view, not file (for simplicity)

    def use_ignored_command(self):
        selection = self.ignored_list.curselection()
        if not selection: return
        selected_items = [self.ignored_list.get(i) for i in selection]
        if len(selected_items) == 1:
            heard = selected_items[0]
            meant = simpledialog.askstring("Add Correction", f"I heard: '{heard}'\n\nWhat should this be recognized as?")
        else:
            items_list = "\n".join(f"  • {item}" for item in selected_items)
            meant = simpledialog.askstring("Batch Add Corrections", f"Selected {len(selected_items)} phrases:\n{items_list}\n\nWhat should ALL of these be recognized as?")
        
        if meant:
            for heard in selected_items:
                self.corr_tree.insert("", tk.END, values=(heard, meant))
            self.update_corrections_config()
            messagebox.showinfo("Success", f"Added {len(selected_items)} corrections!")

    def add_from_test(self):
        result_text = self.test_result_var.get()
        if not result_text.startswith("Result: '"):
             messagebox.showinfo(_("Info"), _("Test a phrase first."))
             return
        heard = result_text.replace("Result: '", "").replace("'", "")
        meant = simpledialog.askstring("Add Correction", f"I heard: '{heard}'\n\nWhat should this be recognized as?")
        if meant:
             self.corr_tree.insert("", tk.END, values=(heard, meant))
             self.update_corrections_config()

    def test_voice_recording(self, duration=10, callback=None):
        self.test_btn.config(state="disabled", text=f"Recording... ({duration}s)")
        self.test_result_var.set("Result: Listening...")
        
        def record_thread():
            import pyaudio
            import vosk
            
            # ALSA Error Suppressor
            ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
            def py_error_handler(filename, line, function, err, fmt): pass
            c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

            @contextmanager
            def no_alsa_error():
                try:
                    asound = cdll.LoadLibrary('libasound.so')
                    asound.snd_lib_error_set_handler(c_error_handler)
                    yield
                    asound.snd_lib_error_set_handler(None)
                except: yield

            try:
                model_path = self.model_var.get()
                if not model_path or not pathlib.Path(model_path).exists():
                    self.root.after(0, lambda: messagebox.showerror(_("Error"), _("Model not found. Please check General settings.")))
                    return

                with no_alsa_error():
                    model = vosk.Model(model_path)
                    rec = vosk.KaldiRecognizer(model, 16000)
                    p = pyaudio.PyAudio()
                    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4000)
                    
                    start = time.time()
                    while (time.time() - start) < duration:
                         data = stream.read(4000, exception_on_overflow=False)
                         if rec.AcceptWaveform(data): pass
                    
                    final_res = rec.FinalResult()
                    res_json = json.loads(final_res)
                    text = res_json.get("text", "")
                    
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    
                    if callback: callback(text)
                    else:
                        self.root.after(0, lambda: self.test_result_var.set(f"Result: '{text}'"))
                        self.root.after(0, lambda: self.test_btn.config(state="normal", text=_("🎤 Record")))
                        
            except Exception as e:
                self.root.after(0, lambda: self.test_result_var.set(f"Error: {e}"))
            finally:
                if not callback: 
                    self.root.after(0, lambda: self.test_btn.config(state="normal", text=_("🎤 Record")))

        threading.Thread(target=record_thread, daemon=True).start()

    def train_basic_phrase(self):
        self.prompt_training("play music", "basic")

    def train_advanced_phrase(self):
         self.prompt_training("play artist queen", "advanced")

    def train_phrase(self):
        phrase = simpledialog.askstring("Train Phrase", "Enter the exact phrase you want to train (e.g. 'Play Rock'):")
        if not phrase: return
        self.prompt_training(phrase, "custom")

    def prompt_training(self, target_phrase, train_type):
        self.test_result_var.set(f"Please say: '{target_phrase}'")
        def on_complete(heard_text):
            self.root.after(0, lambda: self.test_result_var.set(f"Result: '{heard_text}'"))
            self.root.after(0, lambda: self.test_btn.config(state="normal", text=_("🎤 Record")))
            if heard_text.lower() == target_phrase.lower():
                self.root.after(0, lambda: messagebox.showinfo(_("Success"), _("Perfect match! No training needed.")))
            else:
                self.root.after(0, lambda: self.confirm_correction(heard_text, target_phrase))
        self.test_voice_recording(duration=5, callback=on_complete)

    def confirm_correction(self, heard, meant):
        if messagebox.askyesno("Mismatch Detected", f"I heard: '{heard}'\n\nMap this to: '{meant}'?"):
             self.corr_tree.insert("", tk.END, values=(heard, meant))
             self.update_corrections_config()
             messagebox.showinfo(_("Saved"), _("Correction added."))
