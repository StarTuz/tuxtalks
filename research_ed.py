import os
import glob
import psutil
import xml.etree.ElementTree as ET

# User provided path
ED_BINDINGS_PATH = "/home/startux/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/Saved Games/Frontier Developments/Elite Dangerous/"

print(f"🔍 Inspecting Elite Dangerous Config at: {ED_BINDINGS_PATH}")

try:
    if not os.path.exists(ED_BINDINGS_PATH):
        print("❌ Path not found (User execution context).")
    else:
        files = os.listdir(ED_BINDINGS_PATH)
        print(f"📂 Found {len(files)} files.")
        
        bind_files = [f for f in files if f.endswith('.binds') or f.endswith('.3.0.binds') or f.endswith('.4.0.binds')] # 4.0 is Odyssey
        
        if bind_files:
            print(f"🎮 Found Binding Files: {bind_files}")
            # Pick the latest one or standard one to inspect
            target = bind_files[0]
            # Prefer 4.0 or 3.0
            for b in bind_files:
                if '4.0' in b: target = b; break
                
            full_path = os.path.join(ED_BINDINGS_PATH, target)
            print(f"📖 Reading: {target}")
            
            try:
                tree = ET.parse(full_path)
                root = tree.getroot()
                
                # Print a few sample bindings to verify format
                count = 0
                for child in root:
                    # Look for children with <Primary Key="..."> or <Secondary Key="...">
                    primary = child.find('Primary')
                    if primary is not None:
                        device = primary.get('Device')
                        key = primary.get('Key')
                        if device == "Keyboard":
                            print(f"   - Action: {child.tag} -> Key: {key}")
                            count += 1
                    if count >= 5: break
            except Exception as e:
                print(f"❌ Error parsing XML: {e}")
        else:
            print("⚠️ No .binds files found.")

except Exception as e:
    print(f"❌ Error accessing path: {e}")

print("\n🔍 Checking for Game Process...")
found = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        # Check commonly known ED binary names
        name = proc.info['name']
        cmd = proc.info['cmdline'] or []
        if name and 'EliteDangerous' in name:
            print(f"✅ Found Process: {name} (PID: {proc.info['pid']})")
            print(f"   Cmd: {cmd}")
            found = True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

if not found:
    print("ℹ️ Elite Dangerous process is not currently running.")
