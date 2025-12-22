import threading
import os
import time

try:
    import soundfile as sf
    import simpleaudio as sa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Warning: soundfile or simpleaudio not installed. Audio feedback disabled.")

class AudioFeedbackPlayer:
    """
    Handles non-blocking audio playback for macro feedback.
    Designed to be thread-safe and lightweight.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(AudioFeedbackPlayer, cls).__new__(cls)
                    cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if self.initialized: return
        self.initialized = True
        self.current_play_obj = None

    def play(self, file_path: str, wait_until_done: bool = False):
        """
        Plays an audio file.
        
        Args:
            file_path (str): Absolute path to the audio file.
            wait_until_done (bool): If True, blocks until playback finishes.
        """
        if not AUDIO_AVAILABLE: return
        if not file_path or not os.path.exists(file_path):
            print(f"Audio file not found: {file_path}")
            return

        def _play_thread():
            try:
                # soundfile reads the file, simpleaudio plays the buffer
                # This is more robust than simpleaudio.WaveObject directly for some formats
                # But simpleaudio wave object is simplest for .wav
                # soundfile + numpy allows support for FLAC/OGG if needed, but simpleaudio mainly does WAV
                # For Phase 1, we stick to WAV using simpleaudio direct if possible, or convert via soundfile
                
                ext = os.path.splitext(file_path)[1].lower()
                if ext == ".wav":
                    wave_obj = sa.WaveObject.from_wave_file(file_path)
                    play_obj = wave_obj.play()
                else:
                    # Fallback or simpleaudio doesn't support it directly
                    # For now just print warning for non-wav if simpleaudio is restricted
                    # To support OGG/FLAC properly we need soundfile reading to numpy array
                    # and simpleaudio playing that array.
                    data, fs = sf.read(file_path, dtype='int16')
                    play_obj = sa.play_buffer(data, 1 if data.ndim==1 else 2, 2, fs)

                self.current_play_obj = play_obj
                
                if wait_until_done:
                    play_obj.wait_done()
                    
            except Exception as e:
                print(f"Audio Playback Error: {e}")

        if wait_until_done:
            _play_thread()
        else:
            threading.Thread(target=_play_thread, daemon=True).start()

    def stop(self):
        """Stops current playback."""
        if self.current_play_obj:
            self.current_play_obj.stop()
