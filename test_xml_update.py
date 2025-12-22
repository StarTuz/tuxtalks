
import xml.etree.ElementTree as ET
import os

# Mock logic from game_manager.py
def update_binding(file_path, action, key_data):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        target_node = root.find(action)
        if target_node is None: return False, "Tag not found"
        
        primary = target_node.find('Primary')
        slot_to_use = primary # Simplified
        
        slot_to_use.set('Device', 'Keyboard')
        slot_to_use.set('Key', key_data['key'])
        
        # Remove old
        for mod in slot_to_use.findall('Modifier'):
            slot_to_use.remove(mod)
            
        # Add new
        for mod_key in key_data.get('mods', []):
            new_mod = ET.SubElement(slot_to_use, 'Modifier')
            new_mod.set('Device', 'Keyboard')
            new_mod.set('Key', mod_key)
            
        tree.write(file_path, encoding='UTF-8', xml_declaration=True)
        return True, "Success"
    except Exception as e:
        return False, str(e)

# RUN TEST
key_data = {'key': 'Key_F1', 'mods': ['Key_LeftShift']}
success, msg = update_binding("mock_binds.3.0.binds", "Supercruise", key_data)
print(f"Result: {success}, {msg}")

# Print Result
with open("mock_binds.3.0.binds", "r") as f:
    print(f.read())
