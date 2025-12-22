import subprocess
import os
import shutil
import json
from .base import TTSBase

class PiperTTS(TTSBase):
    def __init__(self, config):
        super().__init__(config)
        self.base_dir = os.path.expanduser("~/.local/share/tuxtalks")
        
        # Locate Binary
        self.piper_binary = None
        candidates = [
            os.path.join(self.base_dir, "piper", "piper"),
            os.path.expanduser("~/.local/bin/piper"),
            shutil.which("piper")
        ]
        
        for cand in candidates:
            if cand and os.path.exists(cand):
                self.piper_binary = cand
                break
                
        if not self.piper_binary and candidates[2]: # shutil.which
             self.piper_binary = candidates[2]

        self.voice_name = config.get("PIPER_VOICE", "en_GB-cori-high")

    def speak(self, text):
        if not text: return
        
        if not self.piper_binary:
            print("❌ Piper binary not found.")
            return

        # Construct model path
        model_path = os.path.join(self.base_dir, "voices", f"{self.voice_name}.onnx")
        if not os.path.exists(model_path):
            # Fallback check?
            if os.path.exists(f"{self.voice_name}"): # If absolute path was passed
                model_path = self.voice_name
            else:
                print(f"❌ Piper model not found at: {model_path}")
                return

        # print(f"🗣 Speaking (Piper): {text}")
        print(f"🗣 Speaking (Piper): {text} | Model: {model_path}")
        if shutil.which("aplay"):
             player_cmd = ["aplay", "-q"] # ALSA player, reads WAV header automatically
        elif shutil.which("paplay"):
             # paplay usually expects a file, but let's try.
             # Actually, without aplay, let's try pacat with --file-format=wav if supported, or just stick to raw if we must.
             # But chipmunk suggests raw rate mismatch.
             # Let's assume aplay exists on most linux distros with audio.
             # Fallback to pacat but we need to strip header or hope it ignores it?
             # No, feeding WAV header to raw s16le pacat produces a "pop" at start.
             # Giving up on paplay for stdin.
             print("❌ Error: 'aplay' not found. Please install alsa-utils.")
             return
        else:
             print("❌ Error: 'aplay' not found.")
             return

        try:
             # Use WAV output (header includes sample rate)
             piper_cmd = [
                 self.piper_binary,
                 "--model", model_path,
                 "--output_file", "-"
             ]
             
             # Start Piper
             piper_proc = subprocess.Popen(piper_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
             
             # Start Player (aplay)
             # aplay reads stdin by default if no file specified? No, usually needs '-' or just works.
             # 'aplay' with no args reads stdin.
             player_proc = subprocess.Popen(player_cmd, stdin=piper_proc.stdout, stderr=subprocess.PIPE)
             
             # Close our handle to piper's stdout
             piper_proc.stdout.close()
             
             try:
                 piper_proc.stdin.write(text.encode('utf-8'))
                 piper_proc.stdin.close()
             except Exception as e:
                 print(f"   [Piper] Write Error: {e}")

             # Read stderr from piper (suppress info logs, only show real errors)
             piper_err = piper_proc.stderr.read()
             if piper_proc.wait() != 0:
                 # Filter out info logs that look like errors
                 err_text = piper_err.decode() if piper_err else 'Unknown'
                 if '[piper] [info]' not in err_text:  # Only show actual errors
                     print(f"❌ Piper Error: {err_text}")

             # Check Player (suppress expected "Interrupted system call" from TTS interruption)
             p_out, p_err = player_proc.communicate()
             if player_proc.returncode != 0:
                 err_text = p_err.decode() if p_err else 'Unknown'
                 # Ignore "Interrupted system call" - this is expected when we kill aplay
                 if 'Interrupted system call' not in err_text and err_text != 'Unknown':
                     print(f"❌ Player Error: {err_text}")
             
        except Exception as e:
            print(f"err: Piper TTS failed: {e}")

    def stop(self):
        subprocess.run(["pkill", "aplay"], stderr=subprocess.DEVNULL)
