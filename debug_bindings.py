from game_manager import GameManager
import os

gm = GameManager()
profile = gm.profiles[0] # Elite Dangerous

print(f"Checking path: {profile.default_path}")
if os.path.exists(profile.default_path):
    print("Path exists!")
    files = os.listdir(profile.default_path)
    print(f"Files found: {files}")
else:
    print("Path DOES NOT exist.")

print("\nAttempting to load bindings...")
success = profile.load_bindings()
print(f"Load success: {success}")

print(f"\nLoaded Actions: {len(profile.actions)}")
for action, key in list(profile.actions.items())[:10]:
    print(f"  {action}: {key}")

print(f"\nMapped Voice Bindings: {len(profile.bindings)}")
for voice, key in list(profile.bindings.items())[:10]:
    print(f"  '{voice}': {key}")

print("\n--- Raw XML Dump of first few lines of target file ---")
# Re-find the file manually to dump it
bind_files = [f for f in os.listdir(profile.default_path) if f.endswith('.binds')]
bind_files.sort(reverse=True)
if bind_files:
    target = os.path.join(profile.default_path, bind_files[0])
    print(f"Target file: {target}")
    with open(target, 'r') as f:
        print(f.read()[:500])
