
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import queue
import statistics
import struct
import math
import os
import wave
import tempfile
import sys
from i18n import _

# Try importing pyaudio, but handle missing dependency gracefully
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

class LauncherInputTab:
    """
    Mixin class for providing Voice Calibration functionality.
    """
    
    def build_input_tab(self):
        """Builds the Voice Calibration tab."""
        self.input_monitor_active = False
        self.input_monitor_thread = None
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.is_playing = False
        self.recording_frames = []
        
        # --- Voice Calibration Section ---
        calib_frame = ttk.Labelframe(self.input_tab, text=_("Voice Calibration & Testing"), padding="10")
        calib_frame.pack(fill=tk.X, pady=10)
        
        # 1. Monitor Sub-Frame
        monitor_frame = ttk.Frame(calib_frame)
        monitor_frame.pack(fill=tk.X, pady=5)
        
        # Audio Device Info
        dev_info_frame = ttk.Frame(monitor_frame)
        dev_info_frame.pack(fill=tk.X, pady=2)
        
        if not PYAUDIO_AVAILABLE:
            ttk.Label(dev_info_frame, text=_("⚠️ PyAudio not installed. Cannot monitor audio."), foreground="red").pack()
            return

        self.p = pyaudio.PyAudio()
        try:
            default_info = self.p.get_default_input_device_info()
            dev_name = default_info.get('name', 'Unknown')
            rate = int(default_info.get('defaultSampleRate', 44100))
            channels = int(default_info.get('maxInputChannels', 1))
            
            ttk.Label(dev_info_frame, text=f"Device: {dev_name} ({rate}Hz, {channels}ch)").pack(anchor="w")
        except:
            ttk.Label(dev_info_frame, text=_("No Default Input Device found."), foreground="red").pack(anchor="w")

        # VU Meter Line
        vu_row = ttk.Frame(monitor_frame)
        vu_row.pack(fill=tk.X, pady=5)
        
        self.monitor_btn = ttk.Button(vu_row, text=_("Start Monitor"), command=self.toggle_monitor, width=15)
        self.monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.vu_meter = ttk.Progressbar(vu_row, orient=tk.HORIZONTAL, length=200, mode='determinate')
        self.vu_meter.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Sensitivity / VAD config (Placeholder for future)
        # We can expose generic gain here if supported, but usually it's OS level.
        # Maybe exposed VAD threshold if we had an engine that supported it.
        
        # 2. Test Recording Sub-Frame
        rec_row = ttk.Frame(calib_frame)
        rec_row.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(rec_row, text=_("Test Loop:")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.rec_btn = ttk.Button(rec_row, text=_("🔴 Record 5s"), command=self.start_test_recording)
        self.rec_btn.pack(side=tk.LEFT, padx=5)
        
        self.play_btn = ttk.Button(rec_row, text=_("▶️ Playback"), command=self.play_test_recording, state=tk.DISABLED)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        
        self.rec_status_var = tk.StringVar(value="(Overwrites previous test)")
        ttk.Label(rec_row, textvariable=self.rec_status_var, foreground="gray").pack(side=tk.LEFT, padx=10)
        
        # --- PTT & Shortcuts (Integrated) ---
        self.build_ptt_settings(self.input_tab)

    def build_ptt_settings(self, parent_frame):
        wrapper = ttk.Frame(parent_frame)
        wrapper.pack(fill=tk.X, pady=5)
        
        # PTT
        ptt_frame = ttk.Labelframe(wrapper, text=_("Push-to-Talk Configuration"), padding=10)
        ptt_frame.pack(fill=tk.X, pady=5)
        
        # Enable Switch
        self.ptt_enabled_var = tk.BooleanVar(value=self.config.get("PTT_ENABLED"))
        ttk.Checkbutton(ptt_frame, text=_("Enable Push-to-Talk"), variable=self.ptt_enabled_var).pack(anchor=tk.W)
        
        # Settings
        grid = ttk.Frame(ptt_frame)
        grid.pack(fill=tk.X, pady=5)
        
        ttk.Label(grid, text=_("Mode:")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.ptt_mode_var = tk.StringVar(value=self.config.get("PTT_MODE"))
        ttk.Combobox(grid, textvariable=self.ptt_mode_var, values=["HOLD", "TOGGLE"], state="readonly", width=10).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(grid, text=_("Trigger Key:")).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.ptt_key_var = tk.StringVar(value=self.config.get("PTT_KEY"))
        ttk.Entry(grid, textvariable=self.ptt_key_var, width=20).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(grid, text=_("(Using pynput key codes, e.g. Key.space, Key.ctrl)")).grid(row=1, column=2, sticky=tk.W, padx=5)
        
        self.dynamic_vars["PTT_ENABLED"] = self.ptt_enabled_var
        self.dynamic_vars["PTT_MODE"] = self.ptt_mode_var
        self.dynamic_vars["PTT_KEY"] = self.ptt_key_var
        
        # Shortcuts
        nav_frame = ttk.Labelframe(wrapper, text=_("Navigation Shortcuts"), padding=10)
        nav_frame.pack(fill=tk.X, pady=10)
        
        n_grid = ttk.Frame(nav_frame)
        n_grid.pack(fill=tk.X)
        
        ttk.Label(n_grid, text=_("Next Page:")).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.next_key_var = tk.StringVar(value=self.config.get("PAGE_NEXT_KEY"))
        ttk.Entry(n_grid, textvariable=self.next_key_var, width=15).grid(row=0, column=1, sticky=tk.W, padx=5)
        self.dynamic_vars["PAGE_NEXT_KEY"] = self.next_key_var
        
        ttk.Label(n_grid, text=_("Prev Page:")).grid(row=0, column=2, sticky=tk.W, padx=(20, 5), pady=2)
        self.prev_key_var = tk.StringVar(value=self.config.get("PAGE_PREV_KEY"))
        ttk.Entry(n_grid, textvariable=self.prev_key_var, width=15).grid(row=0, column=3, sticky=tk.W, padx=5)
        self.dynamic_vars["PAGE_PREV_KEY"] = self.prev_key_var

    def toggle_monitor(self):
        if self.input_monitor_active:
            self.stop_monitor()
        else:
            self.start_monitor()
            
    def start_monitor(self):
        if not PYAUDIO_AVAILABLE: return
        self.input_monitor_active = True
        self.monitor_btn.config(text=_("Stop Monitor"))
        self.input_monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.input_monitor_thread.start()
        # Schedule UI update
        self.root.after(100, self._update_vu_meter)
        
    def stop_monitor(self):
        self.input_monitor_active = False
        self.monitor_btn.config(text=_("Start Monitor"))
        self.vu_meter['value'] = 0
        
    def _monitor_loop(self):
        try:
            stream = self.p.open(format=pyaudio.paInt16,
                                 channels=1,
                                 rate=16000,
                                 input=True,
                                 frames_per_buffer=1024)
            
            while self.input_monitor_active:
                data = stream.read(1024, exception_on_overflow=False)
                
                # Calculate RMS
                # unpack to 16-bit integers
                shorts = struct.unpack(f"{len(data)//2}h", data)
                sum_squares = sum(s**2 for s in shorts)
                rms = math.sqrt(sum_squares / len(shorts))
                
                # Normalize (16-bit signed max is 32767)
                # But audio is logarithmic. Let's make it look responsive.
                # RMS of 0-32767 mapped to 0-100
                level = min(100, (rms / 32767) * 200) # Boost by 2x for visibility
                
                self.audio_queue.put(level)
                
                # Identify if clipping? (Near max)
                if rms > 30000:
                    pass # Could signal clip
                    
            stream.stop_stream()
            stream.close()
        except Exception as e:
            print(f"Monitor error: {e}")
            self.input_monitor_active = False

    def _update_vu_meter(self):
        if not self.input_monitor_active: return
        
        try:
            level = 0
            # Get latest level (flush queue)
            while not self.audio_queue.empty():
                level = self.audio_queue.get_nowait()
            
            # Smooth decay could be implemented, but raw is fine for now
            self.vu_meter['value'] = level
            
            # Change color if high? (ttk theme specific)
            
        except: pass
        
        self.root.after(50, self._update_vu_meter)
        
    def start_test_recording(self):
        if not PYAUDIO_AVAILABLE: return
        if self.is_recording or self.is_playing: return
        
        self.is_recording = True
        self.rec_btn.config(state=tk.DISABLED)
        self.play_btn.config(state=tk.DISABLED)
        self.rec_status_var.set("Recording...")
        self.recording_frames = []
        
        threading.Thread(target=self._record_loop, daemon=True).start()
        
    def _record_loop(self):
        try:
            stream = self.p.open(format=pyaudio.paInt16,
                                 channels=1,
                                 rate=16000,
                                 input=True,
                                 frames_per_buffer=1024)
            
            # Record 5 seconds
            for _ in range(0, int(16000 / 1024 * 5)):
                data = stream.read(1024)
                self.recording_frames.append(data)
                
            stream.stop_stream()
            stream.close()
            
            # Save to temp file
            self.temp_wav = os.path.join(tempfile.gettempdir(), "tuxtalks_test.wav")
            wf = wave.open(self.temp_wav, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.recording_frames))
            wf.close()
            
            self.root.after(0, self._rec_finished)
            
        except Exception as e:
            print(f"Record error: {e}")
            self.root.after(0, lambda: self.rec_status_var.set(f"Error: {e}"))
            self.is_recording = False
            self.root.after(0, lambda: self.rec_btn.config(state=tk.NORMAL))

    def _rec_finished(self):
        self.is_recording = False
        self.rec_status_var.set("Recording Complete.")
        self.rec_btn.config(state=tk.NORMAL)
        self.play_btn.config(state=tk.NORMAL)
        
    def play_test_recording(self):
        if not hasattr(self, 'temp_wav') or not os.path.exists(self.temp_wav):
            return
        if self.is_playing or self.is_recording: return
            
        self.is_playing = True
        self.play_btn.config(state=tk.DISABLED)
        self.rec_btn.config(state=tk.DISABLED)
        self.rec_status_var.set("Playing...")
        
        threading.Thread(target=self._play_loop, daemon=True).start()
        
    def _play_loop(self):
        try:
            wf = wave.open(self.temp_wav, 'rb')
            stream = self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)
            
            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)
                
            stream.stop_stream()
            stream.close()
            wf.close()
            
        except Exception as e:
            print(f"Playback error: {e}")
            
        finally:
            self.is_playing = False
            self.root.after(0, self._play_finished)

    def _play_finished(self):
        self.play_btn.config(state=tk.NORMAL)
        self.rec_btn.config(state=tk.NORMAL)
        self.rec_status_var.set("Ready")
