
import json
import os
import pathlib

CONFIG_FILE = pathlib.Path.home() / ".config" / "tuxtalks" / "config.json"

if not CONFIG_FILE.exists():
    print("Config file not found, nothing to migrate.")
    exit(0)

with open(CONFIG_FILE, 'r') as f:
    data = json.load(f)

updated = False

# Migrate VOSK
old_vosk = data.get("VOSK_MODEL_PATH", "")
if "jriver-voice" in old_vosk:
    new_vosk = str(pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "models" / "vosk-model-en-gb-small")
    print(f"Migrating VOSK_MODEL_PATH: {old_vosk} -> {new_vosk}")
    data["VOSK_MODEL_PATH"] = new_vosk
    updated = True

# Migrate Piper Base (implicit in code, but maybe user set PIPER_VOICE path?)
# Usually PIPER_VOICE is just "en_GB-cori-high".
# But if they set it to a path...
voice = data.get("PIPER_VOICE", "")
if "jriver-voice" in voice:
    # Just reset to name
    name = pathlib.Path(voice).stem
    print(f"Migrating PIPER_VOICE: {voice} -> {name}")
    data["PIPER_VOICE"] = name
    updated = True

if updated:
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print("Config updated successfully.")
else:
    print("Config already clean.")
