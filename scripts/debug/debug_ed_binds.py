import os
import xml.etree.ElementTree as ET

# Path from game_manager.py
path = os.path.expanduser("~/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings")

if not os.path.exists(path):
    print(f"Path not found: {path}")
    exit()

files = os.listdir(path)
bind_files = [f for f in files if f.endswith('.binds')]
bind_files.sort(reverse=True)

if not bind_files:
    print("No binds found")
    exit()

target = os.path.join(path, bind_files[0])
print(f"Reading: {target}")

tree = ET.parse(target)
root = tree.getroot()

print("-" * 40)
print(f"{'XML Tag':<30} | {'Binding'}")
print("-" * 40)

for child in root:
    tag = child.tag
    primary = child.find('Primary')
    
    key = None
    mods = []
    
    if primary is not None and primary.get('Device') == "Keyboard":
        key = primary.get('Key')
        for m in primary.findall('Modifier'):
            mods.append(m.get('Key'))
            
    if key:
        mod_str = "+".join(mods) + "+" if mods else ""
        print(f"{tag:<30} | {mod_str}{key}")
        
    # Check secondary too?
    secondary = child.find('Secondary')
    if secondary is not None and secondary.get('Device') == "Keyboard":
         key2 = secondary.get('Key')
         mods2 = [m.get('Key') for m in secondary.findall('Modifier')]
         mod_str2 = "+".join(mods2) + "+" if mods2 else ""
         print(f"{tag:<30} | {mod_str2}{key2} (Secondary)")
