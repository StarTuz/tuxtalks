import subprocess
import shutil
from .base import TTSBase

class SystemTTS(TTSBase):
    def __init__(self, config):
        super().__init__(config)
        self.cmd = None
        if shutil.which("espeak-ng"):
            self.cmd = ["espeak-ng"]
        elif shutil.which("espeak"):
            self.cmd = ["espeak"]
        elif shutil.which("spd-say"):
            self.cmd = ["spd-say", "--wait"] # wait needed to block
            
    def speak(self, text):
        if not self.cmd: 
            print("err: No system TTS found (espeak/spd-say).")
            return

        print(f"🤖 Robotics: {text}")
        try:
            full_cmd = self.cmd.copy()
            full_cmd.append(text)
            subprocess.run(full_cmd)
        except Exception as e:
            print(f"err: System TTS failed: {e}")

    def stop(self):
        # Kill espeak
        subprocess.run(["pkill", "espeak"], stderr=subprocess.DEVNULL)
