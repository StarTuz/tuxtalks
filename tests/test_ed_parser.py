
import pytest
import os
import shutil
import sys
from unittest.mock import MagicMock, patch
from game_manager import EliteDangerousProfile
from pynput.keyboard import Key, KeyCode

# Mock pynput because we are headless
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()

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
        
        # Check "Landing Gear" -> Key_L
        assert "Landing Gear" in profile.actions
        key, mods = profile.actions["Landing Gear"]
        # In our code Key_L maps to KeyCode.from_char('l')
        # We need to verify what _map_ed_key returns.
        # But we can check the bindings map too.
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
        key, mods = profile.actions["Landing Gear"]
        # "Key_G" should map to '34' (Linux Input Code for G)
        assert key == "34"

    def test_update_binding_secondary(self, profile):
        """Test updating a secondary slot when primary is taken by Joystick."""
        profile.load_bindings()
        
        # Boost has Primary=Joystick, Secondary=Tab.
        # We want to change it to Space.
        new_key_data = {'key': 'Key_Space', 'mods': []}
        success, msg = profile.update_binding("Boost", new_key_data)
        assert success is True
        
        profile.load_bindings()
        key, mods = profile.actions["Boost"]
        # Space maps to "57" (Linux Input Code for Space)
        assert key == "57"

    def test_unbind_action(self, profile):
        """Test unbinding an action."""
        profile.load_bindings()
        success = profile.unbind_action("Landing Gear")
        assert success is True
        
        profile.load_bindings()
        # Should be removed from actions map
        assert "Landing Gear" not in profile.actions

