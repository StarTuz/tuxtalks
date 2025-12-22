import os
import sys

# Ensure we can import from local source
sys.path.insert(0, os.path.abspath("."))

from parsers.x4_parser import X4XMLParser

# Dummy XML Content (Mimicking X4 structure)
DUMMY_XML = """<?xml version="1.0" encoding="UTF-8"?>
<inputmap>
    <version>2</version>
    <action id="INPUT_ACTION_INTERACT_MENU_POLL" source="INPUT_SOURCE_KEYBOARD" code="INPUT_KEY_F" />
    <state id="INPUT_STATE_STEER_Y" source="INPUT_SOURCE_MOUSE" code="INPUT_MOUSE_Y_AXIS" />
    <state id="INPUT_STATE_FIRE_PRIMARY" source="INPUT_SOURCE_KEYBOARD" code="INPUT_KEY_SPACE" />
    <state id="INPUT_STATE_BOOST" source="INPUT_SOURCE_KEYBOARD" code="INPUT_KEY_TAB" />
    <state id="INPUT_STATE_TRAVEL_MODE" source="INPUT_SOURCE_KEYBOARD" code="INPUT_KEY_1" />
</inputmap>
"""

def test_manual():
    # Write dummy file
    filename = "test_inputmap.xml"
    with open(filename, "w") as f:
        f.write(DUMMY_XML)
        
    print(f"📄 Validation: Parsing {filename}...")
    
    try:
        parser = X4XMLParser()
        bindings = parser.parse(filename)
        
        print("\n🔍 Parsed Bindings:")
        for action, (key, mods) in bindings.items():
            print(f" - {action}: {key} + {mods}")
            
        # Assertions
        assert bindings["INPUT_STATE_FIRE_PRIMARY"][0] == "Space"
        assert bindings["INPUT_STATE_BOOST"][0] == "Tab"
        assert bindings["INPUT_STATE_TRAVEL_MODE"][0] == "1"
        assert "INPUT_STATE_STEER_Y" not in bindings # Mouse source should be filtered out
        
        print("\n✅ Verification Successful: Parser filtered inputs and mapped keys correctly.")
        
    except Exception as e:
        print(f"❌ Verification Failed: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    test_manual()
