
import pytest
import sys
import os
from unittest.mock import MagicMock

# Ensure the root directory is in the path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def mock_config():
    config = MagicMock()
    data = {
        "ASR_ENGINE": "mock",
        "WAKE_WORD": "computer",
        "VAD_SENSITIVITY": 3,
        "INPUT_DEVICE": "default"
    }
    config.get.side_effect = lambda k, default=None: data.get(k, default)
    def set_val(k, v):
        data[k] = v
    config.set.side_effect = set_val
    return config

@pytest.fixture
def mock_player():
    player = MagicMock()
    # Mock common methods
    player.play_pause = MagicMock()
    player.next_track = MagicMock()
    player.previous_track = MagicMock()
    player.stop = MagicMock()
    player.volume_up = MagicMock()
    player.volume_down = MagicMock()
    player.play_random = MagicMock()
    player.play_random_genre = MagicMock()
    player.play_any = MagicMock()
    return player

@pytest.fixture
def mock_game_manager():
    gm = MagicMock()
    gm.game_mode_enabled = False
    gm.active_profile = None
    gm.handle_command.return_value = (False, None)
    return gm

@pytest.fixture
def mock_voice_manager():
    vm = MagicMock()
    vm.speak = MagicMock()
    return vm

@pytest.fixture
def mock_input_controller():
    ic = MagicMock()
    ic.hold_key_combo = MagicMock()
    return ic

@pytest.fixture
def mock_selection_handler():
    sh = MagicMock()
    sh.handle_selection = MagicMock(return_value=False)
    sh.is_selecting = False
    return sh

@pytest.fixture
def mock_text_normalizer():
    tn = MagicMock()
    tn.normalize.side_effect = lambda x: x # Identity function for tests
    return tn

@pytest.fixture
def mock_state_machine():
    sm = MagicMock()
    return sm
