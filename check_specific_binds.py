from game_manager import GameManager
import os
import xml.etree.ElementTree as ET

gm = GameManager()
profile = gm.profiles[0]
path = profile.custom_path or profile.default_path
bind_files = [f for f in os.listdir(path) if f.endswith('.binds')]
bind_files.sort(reverse=True)
target = os.path.join(path, bind_files[0])

print(f"Checking file: {target}")

tree = ET.parse(target)
root = tree.getroot()

keys_to_check = ["Supercruise", "Hyperspace", "SelectTargetsTarget", "SelectTarget"]

for key in keys_to_check:
    node = root.find(key)
    if node is not None:
        primary = node.find('Primary')
        secondary = node.find('Secondary')
        p_key = primary.get('Key') if primary is not None else "None"
        s_key = secondary.get('Key') if secondary is not None else "None"
        print(f"[{key}]: Primary='{p_key}', Secondary='{s_key}'")
    else:
        print(f"[{key}]: TAG NOT FOUND")
