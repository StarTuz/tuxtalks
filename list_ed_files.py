import os

ED_BINDINGS_PATH = "/home/startux/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/"

try:
    files = os.listdir(ED_BINDINGS_PATH)
    print(f"📂 Files in {ED_BINDINGS_PATH}:")
    for f in files[:20]: # Inspect first 20
        print(f" - {f}")
except Exception as e:
    print(f"Error: {e}")
