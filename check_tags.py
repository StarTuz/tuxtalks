import mutagen
from mutagen.easyid3 import EasyID3
import sys

path = "/home/startux/Music/London Symphony Orchestra/Holst The Planets, Op. 32/London Symphony Orchestra_01_The Planets, Op. 32 Mars, the bringer of war.mp3"

print(f"Inspecting: {path}")

try:
    audio = mutagen.File(path)
    if audio:
        print("--- Raw Tags ---")
        print(audio.pprint())
        
        print("\n--- EasyID3 Tags (if MP3) ---")
        try:
            easy = EasyID3(path)
            print(easy.pprint())
        except:
            print("Not an MP3 or EasyID3 not supported.")
            
except Exception as e:
    print(f"Error: {e}")
