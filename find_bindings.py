import os

PREFIX_ROOT = "/home/startux/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser"
BINDINGS_PATH = os.path.join(PREFIX_ROOT, "AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings")

print(f"🔍 Checking real bindings path: {BINDINGS_PATH}")

if os.path.exists(BINDINGS_PATH):
    print("✅ Found Bindings Directory!")
    files = os.listdir(BINDINGS_PATH)
    binds = [f for f in files if f.endswith('.binds')]
    print(f"📂 Found {len(binds)} binding files: {binds}")
else:
    print("❌ Path does not exist.")
    # Try searching?
    print("   Searching recursively for .binds in prefix...")
    for root, dirs, files in os.walk(PREFIX_ROOT):
        for f in files:
            if f.endswith('.binds'):
                print(f"   -> Found at: {os.path.join(root, f)}")
