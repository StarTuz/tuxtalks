
import tkinter as tk
from tkinter import ttk, messagebox
from speech_engines import ENGINES as SPEECH_ENGINES
from i18n import _

class LauncherSpeechTab:
    def build_speech_tab(self):
        """Builds the Modular Speech Engine selection UI."""
        
        # Top Frame: Split View (ASR | TTS)
        split_frame = ttk.Frame(self.speech_tab)
        split_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- Left Column: ASR ---
        asr_frame = ttk.LabelFrame(split_frame, text=_("Speech Recognition (ASR)"), padding="5")
        asr_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.asr_list = tk.Listbox(asr_frame, height=5)
        self.asr_list.pack(fill=tk.X, pady=5)
        self.asr_list.bind("<<ListboxSelect>>", self.on_asr_select)
        
        # Populate ASR
        for key in SPEECH_ENGINES["ASR"]:
            self.asr_list.insert(tk.END, key)
            
        self.asr_info = ttk.Label(asr_frame, text=_("Select an engine..."), wraplength=250, justify=tk.LEFT)
        self.asr_info.pack(fill=tk.BOTH, expand=True)
        
        # --- Right Column: TTS ---
        tts_frame = ttk.LabelFrame(split_frame, text=_("Text-to-Speech (TTS)"), padding="5")
        tts_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.tts_list = tk.Listbox(tts_frame, height=5)
        self.tts_list.pack(fill=tk.X, pady=5)
        self.tts_list.bind("<<ListboxSelect>>", self.on_tts_select)
        
        # Populate TTS
        for key in SPEECH_ENGINES["TTS"]:
            self.tts_list.insert(tk.END, key)
            
        self.tts_info = ttk.Label(tts_frame, text=_("Select an engine..."), wraplength=250, justify=tk.LEFT)
        self.tts_info.pack(fill=tk.BOTH, expand=True)
        
        # --- Bottom: Actions ---
        btn_frame = ttk.Frame(self.speech_tab)
        btn_frame.pack(fill=tk.X, pady=10)
        ttk.Button(btn_frame, text=_("Apply Speech Settings"), command=self.save_speech_settings).pack(side=tk.RIGHT)
        
        # --- Wyoming Config ---
        wyo_frame = ttk.LabelFrame(self.speech_tab, text=_("Wyoming Settings (External Server)"), padding="5")
        wyo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(wyo_frame, text=_("Host:")).pack(side=tk.LEFT)
        self.wyo_host_var = tk.StringVar(value=self.config.get("WYOMING_HOST", "localhost"))
        ttk.Entry(wyo_frame, textvariable=self.wyo_host_var).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(wyo_frame, text=_("Port:")).pack(side=tk.LEFT)
        self.wyo_port_var = tk.StringVar(value=str(self.config.get("WYOMING_PORT", 10300)))
        ttk.Entry(wyo_frame, textvariable=self.wyo_port_var, width=6).pack(side=tk.LEFT, padx=5)

        # Select current from config
        curr_asr = self.config.get("ASR_ENGINE")
        curr_tts = self.config.get("TTS_ENGINE")
        
        # Helper to select by string
        try:
             # Check if key exists (could be old config)
             if curr_asr in SPEECH_ENGINES["ASR"]:
                 idx = list(SPEECH_ENGINES["ASR"].keys()).index(curr_asr)
                 self.asr_list.selection_set(idx)
                 self.on_asr_select(None)
        except: pass
        
        try:
             if curr_tts in SPEECH_ENGINES["TTS"]:
                 idx = list(SPEECH_ENGINES["TTS"].keys()).index(curr_tts)
                 self.tts_list.selection_set(idx)
                 self.on_tts_select(None)
        except: pass

    def on_asr_select(self, event):
        sel = self.asr_list.curselection()
        if not sel: return
        key = self.asr_list.get(sel[0])
        meta = SPEECH_ENGINES["ASR"][key]
        
        txt = f"Name: {meta['name']}\n\n{meta['description']}\n\n"
        if meta.get("experimental"): txt += "⚠️ EXPERIMENTAL\n\n"
        txt += "✅ Pros:\n" + "\n".join([f"• {p}" for p in meta['pros']]) + "\n\n"
        txt += "❌ Cons:\n" + "\n".join([f"• {c}" for c in meta['cons']])
        
        self.asr_info.config(text=txt)

    def on_tts_select(self, event):
        sel = self.tts_list.curselection()
        if not sel: return
        key = self.tts_list.get(sel[0])
        meta = SPEECH_ENGINES["TTS"][key]
        
        txt = f"Name: {meta['name']}\n\n{meta['description']}\n\n"
        if meta.get("experimental"): txt += "⚠️ EXPERIMENTAL\n\n"
        txt += "✅ Pros:\n" + "\n".join([f"• {p}" for p in meta['pros']]) + "\n\n"
        txt += "❌ Cons:\n" + "\n".join([f"• {c}" for c in meta['cons']])
        
        self.tts_info.config(text=txt)

    def save_speech_settings(self):
        # ASR
        sel = self.asr_list.curselection()
        if sel:
            self.config.set("ASR_ENGINE", self.asr_list.get(sel[0]))
            
        # TTS
        sel = self.tts_list.curselection()
        if sel:
            self.config.set("TTS_ENGINE", self.tts_list.get(sel[0]))
            
        # Save Wyoming
        self.config.set("WYOMING_HOST", self.wyo_host_var.get())
        try:
            self.config.set("WYOMING_PORT", int(self.wyo_port_var.get()))
        except: pass
            
        self.config.save()
        messagebox.showinfo(_("Saved"), _("Speech settings saved!\nRestart the assistant to apply changes."))

