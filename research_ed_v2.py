import os
import psutil
import xml.etree.ElementTree as ET

# Corrected Path
BINDINGS_PATH = "/home/startux/.local/share/Steam/steamapps/compatdata/359320/pfx/drive_c/users/steamuser/AppData/Local/Frontier Developments/Elite Dangerous/Options/Bindings"
TARGET_FILE = os.path.join(BINDINGS_PATH, "Custom.4.2.binds") # Try 4.2 first

print(f"📖 Parsing Bindings: {TARGET_FILE}")

if os.path.exists(TARGET_FILE):
    try:
        tree = ET.parse(TARGET_FILE)
        root = tree.getroot()
        
        print("\n--- Sample Keybindings ---")
        count = 0
        target_actions = ["SelectTargetsTarget", "LandingGearToggle", "HyperSuperCombination", "OrderRequestDock"]
        
        for child in root:
            # Structure: <ActionName><Primary Device="..." Key="..." /><Secondary ... /></ActionName>
            # Dump if it's in our target list OR just generic sample
            if child.tag in target_actions:
                 primary = child.find('Primary')
                 print(f"   [{child.tag.ljust(25)}] -> P: {primary.get('Device')}:{primary.get('Key')}")
                 secondary = child.find('Secondary')
                 print(f"                                S: {secondary.get('Device')}:{secondary.get('Key')}")
                 
            primary = child.find('Primary')
            if primary is not None:
                device = primary.get('Device')
                key = primary.get('Key')
                if device == "Keyboard" and key:
                    # Generic logging
                    if count < 5: 
                         print(f"   (Sample) [{child.tag.ljust(25)}] -> {key}")
                         count += 1
    except Exception as e:
        print(f"❌ Error parsing XML: {e}")
else:
    print(f"⚠️ Target file not found, trying to list dir again.")
    if os.path.exists(BINDINGS_PATH):
        print(os.listdir(BINDINGS_PATH))

print("\n🔍 Checking for ANY Elite Dangerous process...")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        name = proc.info['name']
        cmd = proc.info['cmdline'] or []
        # Check wide variety of names
        if name and ('Elite' in name or 'elite' in name):
            print(f"✅ Found: {name} (PID: {proc.info['pid']})")
    except:
        pass
