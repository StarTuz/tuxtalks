import vosk
import pyaudio
import json
import queue
import threading
import time
from .base import ASRBase

class VoskASR(ASRBase):
    def __init__(self, config):
        super().__init__(config)
        self.model_path = config.get("VOSK_MODEL_PATH")
        self.sample_rate = 16000
        self.chunk_size = 8000
        
        self.model = None
        self.recognizer = None
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.paused = False # New flag
        
        self.text_queue = queue.Queue()
        self.thread = None

        self._load_model()
    
    # ... (Load Model and Start unchanged) ...

    def _load_model(self):
        print(f"log: Loading Vosk Model from {self.model_path}...")
        try:
            self.model = vosk.Model(self.model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            print("log: Vosk Model Loaded.")
        except Exception as e:
            print(f"err: Failed to load Vosk model: {e}")
        except Exception as e:
            print(f"err: Failed to load Vosk model: {e}")

    def set_grammar(self, vocabulary: list[str]):
        """Update the Vosk recognizer with a specific vocabulary."""
        if not self.model: return
        
        # Add [unk] for unknown words handling
        if "[unk]" not in vocabulary:
            vocabulary.append("[unk]")
            
        print(f"log: Updating Vosk Grammar ({len(vocabulary)} terms)...")
        try:
            grammar_json = json.dumps(vocabulary)
            # Re-initialize recognizer with grammar
            # Note: This is thread-safe enough as we just replace the pointer, 
            # though active processing might drop a frame. Ideally pause first.
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate, grammar_json)
            print("log: Vosk Grammar Updated.")
        except Exception as e:
            print(f"err: Failed to set grammar: {e}")
    def start(self, input_device_index=None):
        if not self.model: return
        
        try:
            self.stream = self.p.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=self.sample_rate,
                                      input=True,
                                      frames_per_buffer=self.chunk_size,
                                      input_device_index=input_device_index)
            self.running = True
            
            self.thread = threading.Thread(target=self._worker, daemon=True)
            self.thread.start()
            print("log: Vosk ASR Started.")
        except Exception as e:
            print(f"err: Failed to start audio stream: {e}")

    def stop(self):
        self.running = False
        # Suppress ALSA errors during shutdown
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
        except:
            pass  # Ignore PyAudio/ALSA cleanup errors

    def pause(self):
        """Pause ASR processing (drain buffer)."""
        self.paused = True
        # Clear queue to remove old commands
        with self.text_queue.mutex:
            self.text_queue.queue.clear()

    def resume(self):
        """Resume ASR processing."""
        self.paused = False
        # Clear queue again to ensure fresh start
        with self.text_queue.mutex:
            self.text_queue.queue.clear()

    def get_next_text(self):
        """Blocking call."""
        return self.text_queue.get()

    def _worker(self):
        while self.running:
            try:
                # Always read to keep buffer empty
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                if self.paused:
                    continue

                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        self.text_queue.put(text)
            except Exception as e:
                # print(f"pyaudio error: {e}")
                time.sleep(0.1)
