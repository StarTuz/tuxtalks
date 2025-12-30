
import pytest
import os
import shutil
import sys
from unittest.mock import MagicMock, patch

# Mock pynput because we are headless (MUST be before game_manager import)
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

from game_manager import EliteDangerousProfile
# Remove real import if it was there, but Key is likely needed for tests?
# from pynput.keyboard import Key -> this would import the real one if we didn't mock it?
# The mock replaces it, so we can't import the real 'Key' enum easily.
# We might need to mock Key enum too if the test uses it.

# Define a Mock Key class for the test usage
class MockKey:
    shift_l = "Key.shift_l"
    shift_r = "Key.shift_r"
    ctrl_l = "Key.ctrl_l"
    ctrl_r = "Key.ctrl_r"
    alt_l = "Key.alt_l"
    alt_r = "Key.alt_r"
    enter = "Key.enter"
    space = "Key.space"
    tab = "Key.tab"
    esc = "Key.esc"
    backspace = "Key.backspace"
    delete = "Key.delete"
    insert = "Key.insert"
    home = "Key.home"
    end = "Key.end"
    page_up = "Key.page_up"
    page_down = "Key.page_down"
    up = "Key.up"
    down = "Key.down"
    left = "Key.left"
    right = "Key.right"
    caps_lock = "Key.caps_lock"
    num_lock = "Key.num_lock"
    scroll_lock = "Key.scroll_lock"
    f1="Key.f1";f2="Key.f2";f3="Key.f3";f4="Key.f4"
    f5="Key.f5";f6="Key.f6";f7="Key.f7";f8="Key.f8"
    f9="Key.f9";f10="Key.f10";f11="Key.f11";f12="Key.f12"

class MockKeyCode:
    @staticmethod
    def from_char(char):
        return char

# Assign mocks to the mocked module
sys.modules['pynput.keyboard'].Key = MockKey
sys.modules['pynput.keyboard'].KeyCode = MockKeyCode

class TestEliteDangerousProfile:
    
    @pytest.fixture
    def profile(self, tmp_path):
        # Create a temporary environment
        binds_dir = tmp_path / "Bindings"
        binds_dir.mkdir()
        
        # Copy sample bind file
        src = os.path.join(os.path.dirname(__file__), 'data', 'test.binds')
        dst = binds_dir / "Custom.4.0.binds"
        shutil.copy(src, dst)
        
        # Initialize Profile with mocked paths
        profile = EliteDangerousProfile()
        profile.default_path = str(binds_dir)
        profile.custom_path = None
        
        # Mock the voice map to include our test keys
        profile.action_voice_map = {
            "Landing Gear": ["gear"],
            "Lights": ["lights"],
            "Boost": ["boost"]
        }
        
        # Re-initialize tag map for test consistency
        profile.virtual_tag_map = {
            "Landing Gear": ["LandingGearToggle"],
            "Lights": ["ShipSpotLightToggle"],
            "Boost": ["UseBoostJuice"]
        }
        
        return profile

    def test_load_bindings(self, profile):
        """Test parsing of the XML file."""
        success = profile.load_bindings()
        assert success is True
        assert profile.active_binds_path.endswith("Custom.4.0.binds")
        
        # Check "Landing Gear" -> Key_L (Wait, parser returns XML Tags!)
        # So we should look for "LandingGearToggle"
        assert "LandingGearToggle" in profile.actions
        key, mods = profile.actions["LandingGearToggle"]
        # In our code Key_L maps to KeyCode.from_char('l') or 'l'
        # Verification depends on what _map_ed_key returns.
        
        # We can check the bindings map too (Voice Command -> Key)
        assert "gear" in profile.bindings
        
    def test_update_binding(self, profile):
        """Test updating a binding."""
        profile.load_bindings()
        
        # Change Landing Gear to 'G'
        new_key_data = {'key': 'Key_G', 'mods': []}
        success, msg = profile.update_binding("Landing Gear", new_key_data)
        assert success is True
        
        # Reload to verify
        profile.load_bindings()
        # Again, check XML Tag
        key, mods = profile.actions["LandingGearToggle"]
        # "Key_G" should map to '34' (Linux Input Code for G) or just 'g' if parser maps it
        # Based on logs: {'LandingGearToggle': ('l', [])} -> key is 'l'
        # If we updated to Key_G, it should be 'g' (or '34' if ydotool mapping logic applied inside parser? No, parser uses pynput logic usually)
        # Let's check parser code... EDXMLParser._map_key converts Key_G -> 'g'
        assert key == "g" or key == "34"
        
    def test_update_binding_secondary(self, profile):
        """Test updating a secondary slot when primary is taken by Joystick."""
        profile.load_bindings()
        
        # Boost has Primary=Joystick, Secondary=Tab.
        # We want to change it to Space.
        new_key_data = {'key': 'Key_Space', 'mods': []}
        success, msg = profile.update_binding("Boost", new_key_data)
        assert success is True
        
        profile.load_bindings()
        # Check XML Tag: UseBoostJuice
        key, mods = profile.actions["UseBoostJuice"]
        # Space maps to "space" or "Key.space"
        assert key == "space" or key == "Key.space"

    def test_unbind_action(self, profile):
        """Test unbinding an action."""
        profile.load_bindings()
        success = profile.unbind_action("Landing Gear")
        assert success is True
        
        profile.load_bindings()
        # Should be removed from actions map (or set to empty/Keyboard with no key?)
        # Wait, unbind usually clears it.
        # If removed from XML, it won't be in parsed actions.
        assert "LandingGearToggle" not in profile.actions
