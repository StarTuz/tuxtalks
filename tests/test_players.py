
import pytest
from unittest.mock import MagicMock, patch
from players.jriver import JRiverPlayer
from players.mpris import MPRISPlayer
from players.strawberry import StrawberryPlayer
from players.elisa import ElisaPlayer

class TestPlayers:
    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        config.get.return_value = "mock_value"
        return config

    @pytest.fixture
    def mock_speak(self):
        return MagicMock()

    @patch('players.mpris.dbus')
    def test_mpris_instantiation(self, mock_dbus, mock_config, mock_speak):
        player = MPRISPlayer(mock_config, speak_func=mock_speak)
        assert player.speak_func == mock_speak
        mock_dbus.SessionBus.assert_called_once()
        # Verify it has MediaPlayer methods
        assert hasattr(player, 'announce_error')

    @patch('players.jriver.requests')
    def test_jriver_instantiation(self, mock_requests, mock_config, mock_speak):
        player = JRiverPlayer(mock_config, speak_func=mock_speak)
        assert player.speak_func == mock_speak
        assert hasattr(player, 'announce_error')

    @patch('players.strawberry.dbus')
    @patch('players.strawberry.pathlib.Path') 
    def test_strawberry_instantiation(self, mock_path, mock_dbus, mock_config, mock_speak):
        player = StrawberryPlayer(mock_config, speak_func=mock_speak)
        assert player.speak_func == mock_speak
        assert hasattr(player, 'announce_error')

    @patch('players.elisa.dbus')
    @patch('players.elisa.pathlib.Path')
    def test_elisa_instantiation(self, mock_path, mock_dbus, mock_config, mock_speak):
        player = ElisaPlayer(mock_config, speak_func=mock_speak)
        # Elisa inherits MPRIS, check if it called super init correctly
        assert player.service_name == "org.mpris.MediaPlayer2.elisa"
        assert player.speak_func == mock_speak
        assert hasattr(player, 'announce_error')

    def test_all_players_have_play_random(self, mock_config, mock_speak):
        """Ensure all players implement play_random."""
        mpris = MPRISPlayer(mock_config, speak_func=mock_speak)
        jriver = JRiverPlayer(mock_config, speak_func=mock_speak)
        # Mock file paths/dbus for others to avoid init errors
        with patch('players.strawberry.dbus'), patch('players.strawberry.pathlib.Path'):
            strawberry = StrawberryPlayer(mock_config, speak_func=mock_speak)
        with patch('players.elisa.dbus'), patch('players.elisa.pathlib.Path'):
            elisa = ElisaPlayer(mock_config, speak_func=mock_speak)

        for p in [mpris, jriver, strawberry, elisa]:
            assert hasattr(p, 'play_random'), f"{p.__class__.__name__} missing play_random"
            assert callable(p.play_random)
