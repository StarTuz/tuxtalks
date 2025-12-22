"""
Voice Training Tab - Manual voice pattern training
Implements Phase 3 of the Voice Learning system
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from pathlib import Path
import i18n

# Translation helper
def _(text):
    return i18n._(text)


class LauncherTrainingTab:
    """Manual voice training interface for VoiceFingerprint"""
    
    def build_training_tab(self):
        """Build the Voice Training tab interface"""
        
        # Main container with scrollbar
        container = ttk.Frame(self.training_tab)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        header_frame = ttk.Frame(container)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            header_frame, 
            text=_("🎓 Voice Learning"),
            font=("Helvetica", 14, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text=_("Train the system to recognize YOUR voice patterns"),
            font=("Helvetica", 9),
            foreground="gray"
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Info panel
        info_frame = ttk.LabelFrame(container, text=_("How It Works"), padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_text = _(
            "TuxTalks learns automatically from your commands (passive learning).\n"
            "Use manual training for:\n"
            "  • Artists ASR consistently mishears\n"
            "  • Non-English pronunciations\n"
            "  • Immediate fixes (no waiting for passive learning)\n\n"
            "Say the correct phrase 3-5 times to teach the system."
        )
        
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Learned Patterns section
        patterns_frame = ttk.LabelFrame(container, text=_("Learned Patterns"), padding=15)
        patterns_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Toolbar
        toolbar = ttk.Frame(patterns_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text=_("➕ Train New Command"),
            command=self.train_new_command,
            width=20
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            toolbar,
            text=_("🗑️ Delete Selected"),
            command=self.delete_pattern,
            width=18
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text=_("🔄 Refresh"),
            command=self.refresh_patterns,
            width=12
        ).pack(side=tk.LEFT, padx=5)
        
        # Patterns list (Treeview)
        list_frame = ttk.Frame(patterns_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(list_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("asr_heard", "correction", "confidence", "count", "source", "last_seen")
        self.patterns_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=10
        )
        
        # Column headers
        self.patterns_tree.heading("asr_heard", text=_("ASR Heard"))
        self.patterns_tree.heading("correction", text=_("Correction"))
        self.patterns_tree.heading("confidence", text=_("Confidence"))
        self.patterns_tree.heading("count", text=_("Count"))
        self.patterns_tree.heading("source", text=_("Source"))
        self.patterns_tree.heading("last_seen", text=_("Last Seen"))
        
        # Column widths
        self.patterns_tree.column("asr_heard", width=150)
        self.patterns_tree.column("correction", width=150)
        self.patterns_tree.column("confidence", width=100)
        self.patterns_tree.column("count", width=60)
        self.patterns_tree.column("source", width=80)
        self.patterns_tree.column("last_seen", width=180)
        
        vsb.config(command=self.patterns_tree.yview)
        hsb.config(command=self.patterns_tree.xview)
        
        self.patterns_tree.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.training_status = tk.StringVar(value=_("Ready"))
        status_bar = ttk.Label(
            container,
            textvariable=self.training_status,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Load patterns on init
        self.refresh_patterns()
    
    def refresh_patterns(self):
        """Reload patterns from VoiceFingerprint"""
        try:
            from voice_fingerprint import VoiceFingerprint
            
            vf = VoiceFingerprint()
            
            # Clear tree
            for item in self.patterns_tree.get_children():
                self.patterns_tree.delete(item)
            
            # Load patterns
            count = 0
            for error_word, pattern in vf.patterns.items():
                # Get most common correction
                if pattern.get("likely_meant"):
                    corrections = pattern["likely_meant"]
                    # Count occurrences
                    from collections import Counter
                    counter = Counter(corrections)
                    most_common = counter.most_common(1)[0][0]
                else:
                    most_common = "N/A"
                
                confidence = pattern.get("confidence", 0.0)
                total_count = pattern.get("count", 0)
                source = pattern.get("source", "unknown")
                last_seen = pattern.get("last_seen", "Never")
                
                # Format last_seen (just date/time, no microseconds)
                if last_seen != "Never" and "T" in last_seen:
                    last_seen = last_seen.split(".")[0].replace("T", " ")
                
                # Insert into tree
                self.patterns_tree.insert(
                    "",
                    tk.END,
                    values=(
                        error_word,
                        most_common,
                        f"{confidence:.0%}",
                        total_count,
                        source,
                        last_seen
                    ),
                    tags=(source,)
                )
                count += 1
            
            # Tag styling
            self.patterns_tree.tag_configure("passive", foreground="lightblue")
            self.patterns_tree.tag_configure("manual", foreground="lightgreen")
            
            self.training_status.set(_(f"Loaded {count} patterns"))
            
        except Exception as e:
            messagebox.showerror(_("Error"), _(f"Failed to load patterns: {e}"))
    
    def train_new_command(self):
        """Open dialog to train a new voice command"""
        
        # Ask for the correct phrase
        correct_phrase = simpledialog.askstring(
            _("Train Command"),
            _("Enter the CORRECT phrase you want to train:\n(e.g., 'Johann Strauss', 'Cradle of Filth')"),
            parent=self.root
        )
        
        if not correct_phrase:
            return
        
        correct_phrase = correct_phrase.strip()
        
        # Show instructions
        msg = _(
            f"You will now record '{correct_phrase}' 5 times.\n\n"
            "Speak clearly in your natural voice.\n"
            "The system will learn how YOU pronounce it.\n\n"
            "Click OK when ready to start."
        )
        
        if not messagebox.askokcancel(_("Ready to Record?"), msg):
            return
        
        # Start recording session
        self.run_training_session(correct_phrase)
    
    def run_training_session(self, correct_phrase):
        """Record multiple utterances and save to VoiceFingerprint"""
        
        try:
            from voice_fingerprint import VoiceFingerprint
            import pyaudio
            import wave
            import tempfile
            import os
            
            # Initialize
            vf = VoiceFingerprint()
            recordings = []
            num_samples = 5
            
            # Audio parameters (match Wyoming/Vosk)
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000
            RECORD_SECONDS = 3
            
            p = pyaudio.PyAudio()
            
            for i in range(num_samples):
                # Update status
                status_msg = f"Recording {i+1}/{num_samples}... Speak now!"
                self.training_status.set(status_msg)
                self.root.update()
                
                # Record
                stream = p.open(
                    format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK
                )
                
                frames = []
                for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                
                stream.stop_stream()
                stream.close()
                
                # Save to temp file for ASR
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    wf = wave.open(tmp.name, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                    wf.close()
                    
                    # Transcribe with Vosk
                    transcription = self.transcribe_audio(tmp.name)
                    recordings.append(transcription)
                    
                    # Cleanup
                    os.unlink(tmp.name)
                
                # Pause between recordings
                status_msg = f"Recorded {i+1}/{num_samples}. Next in 2s..."
                self.training_status.set(status_msg)
                self.root.update()
                self.root.after(2000)
            
            p.terminate()
            
            # Show what was heard
            heard_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(recordings)])
            
            msg = (
                f"Recordings complete!\n\n"
                f"You said: '{correct_phrase}'\n"
                f"ASR heard:\n{heard_text}\n\n"
                f"Save this training data?"
            )
            
            if messagebox.askyesno(i18n._("Confirm Training"), msg):
                # Add each transcription as manual training
                for heard in recordings:
                    vf.add_manual_correction(
                        expected=correct_phrase,
                        heard=heard
                    )
                
                self.training_status.set(f"✅ Trained '{correct_phrase}'!")
                self.refresh_patterns()
                messagebox.showinfo("Success", f"Successfully trained '{correct_phrase}'!")
            else:
                self.training_status.set(i18n._("Training cancelled"))
        
        except Exception as e:
            import traceback
            import logging
            
            # Get full traceback
            tb = traceback.format_exc()
            
            # Log it
            logger = logging.getLogger("tuxtalks-gui")
            logger.error(f"Training failed with full traceback:\n{tb}")
            
            # Also print to console
            print("=" * 60)
            print("TRAINING ERROR - Full Traceback:")
            print(tb)
            print("=" * 60)
            
            self.training_status.set("Error during training")
            messagebox.showerror("Error", f"Training failed: {e}\n\nCheck console for details.")
    
    def transcribe_audio(self, wav_file):
        """Transcribe audio file with Vosk"""
        try:
            from vosk import Model, KaldiRecognizer
            import json
            import wave
            from config import cfg
            
            # Load model
            model_path = cfg.get("VOSK_MODEL_PATH")
            model = Model(model_path)
            
            # Open audio
            wf = wave.open(wav_file, "rb")
            rec = KaldiRecognizer(model, wf.getframerate())
            
            # Transcribe
            text = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text += result.get("text", "")
            
            # Final result
            final = json.loads(rec.FinalResult())
            text += " " + final.get("text", "")
            
            wf.close()
            return text.strip()
            
        except Exception as e:
            return f"[transcription error: {e}]"
    
    def delete_pattern(self):
        """Delete selected pattern from VoiceFingerprint"""
        
        selection = self.patterns_tree.selection()
        if not selection:
            messagebox.showwarning(_("No Selection"), _("Please select a pattern to delete"))
            return
        
        # Get selected item
        item = selection[0]
        values = self.patterns_tree.item(item, "values")
        error_word = values[0]
        
        if not messagebox.askyesno(_("Confirm Delete"), _(f"Delete pattern '{error_word}'?")):
            return
        
        try:
            from voice_fingerprint import VoiceFingerprint
            
            vf = VoiceFingerprint()
            
            # Remove pattern
            if error_word in vf.patterns:
                del vf.patterns[error_word]
                vf.save()
                
                self.training_status.set(_(f"Deleted '{error_word}'"))
                self.refresh_patterns()
                messagebox.showinfo(_("Success"), _(f"Pattern '{error_word}' deleted"))
            else:
                messagebox.showerror(_("Error"), _("Pattern not found"))
        
        except Exception as e:
            messagebox.showerror(_("Error"), _(f"Failed to delete: {e}"))
