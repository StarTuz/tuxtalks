import os
import xml.etree.ElementTree as ET

BINDINGS_PATH = "/home/startux/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings"

def scan_files():
    if not os.path.exists(BINDINGS_PATH):
        print("Path not found!")
        return

    files = [f for f in os.listdir(BINDINGS_PATH) if f.endswith('.binds')]
    files.sort(reverse=True)
    
    print(f"Found {len(files)} binding files.")
    
    for f in files:
        path = os.path.join(BINDINGS_PATH, f)
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            
            # Check for SelectTargetsTarget
            node = root.find('SelectTargetsTarget')
            if node is not None:
                p = node.find('Primary')
                s = node.find('Secondary')
                
                print(f"\n📄 File: {f}")
                print(f"   SelectTargetsTarget Primary:   Device={p.get('Device')} Key={p.get('Key')}")
                print(f"   SelectTargetsTarget Secondary: Device={s.get('Device')} Key={s.get('Key')}")
                
                # Check for Modifiers
                if s is not None:
                    mods = s.findall('Modifier')
                    if mods:
                        for m in mods:
                            print(f"      + Modifier: Device={m.get('Device')} Key={m.get('Key')}")

        except Exception as e:
            print(f"Error parsing {f}: {e}")

if __name__ == "__main__":
    scan_files()
