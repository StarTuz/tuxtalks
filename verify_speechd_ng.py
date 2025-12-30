from speech_engines.speechd_ng_tts import SpeechdNgTTS
import time

class MockConfig:
    pass

print("Testing SpeechdNgTTS...")
tts = SpeechdNgTTS(MockConfig())

if tts.health_check():
    print("Health check passed!")
    print("Speaking 'Hello from TuxTalks integration verification'...")
    tts.speak("Hello from TuxTalks integration verification")
    time.sleep(2)
    print("Done.")
else:
    print("Health check failed. speechd-ng might not be running.")
