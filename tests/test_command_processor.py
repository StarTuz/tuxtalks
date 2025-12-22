
import pytest
from unittest.mock import MagicMock
from core.command_processor import CommandProcessor

class TestCommandProcessor:
    
    @pytest.fixture
    def processor(self, mock_player, mock_game_manager, mock_config, 
                 mock_input_controller, mock_selection_handler, 
                 mock_text_normalizer, mock_state_machine):
        # Create processor with mocked dependencies
        cp = CommandProcessor(
            player=mock_player,
            game_manager=mock_game_manager,
            input_controller=mock_input_controller,
            selection_handler=mock_selection_handler,
            text_normalizer=mock_text_normalizer,
            speak_func=MagicMock(),
            config=mock_config,
            speech_queue=MagicMock(),
            state_machine=mock_state_machine
        )
        # Manually ensure active_player set if logic requires it
        # (Though CommandProcessor usually delegates to self.player directly)
        return cp

    def test_media_controls(self, processor, mock_player):
        """Test basic media control commands."""
        # Play
        assert processor.process("play", 0) is True
        mock_player.play_pause.assert_called_once()
        
        # Next
        assert processor.process("next song", 0) is True
        mock_player.next_track.assert_called_once()
        
        # Stop
        assert processor.process("stop music", 0) is True
        mock_player.stop.assert_called_once()
        
    def test_game_mode_handling(self, processor, mock_game_manager):
        """Test game mode toggling and command routing."""
        
        # Turn On
        assert processor.process("enable game mode", 0) is True
        mock_game_manager.set_enabled.assert_called_with(True)
        
        # Routing (Mock game handled it)
        mock_game_manager.handle_command.return_value = (True, "Executed")
        
        # "landing gear" -> game handled
        assert processor.process("landing gear", 0) is True
        mock_game_manager.handle_command.assert_called_with("landing gear", processor.input_controller)

    def test_play_random_fallback(self, processor, mock_player):
        """Test fallback logic for play random."""
        # Setup: Player has play_random but NO play_random_genre
        # This simulates MPRIS player
        del mock_player.play_random_genre 
        
        # "Play random anything"
        assert processor.process("play random anything", 0) is True
        mock_player.play_random.assert_called_once()
        
        # Ensure play_any("random") was NOT called (which was the bug)
        check_call_count = mock_player.play_any.call_count
        assert check_call_count == 0

    def test_play_random_genre_support(self, processor, mock_player):
        """Test play random with genre support."""
        # Setup: Player HAS play_random_genre
        mock_player.play_random_genre = MagicMock()
        
        assert processor.process("play random rock", 0) is True
        mock_player.play_random_genre.assert_called_with("rock")

    def test_play_search(self, processor, mock_player):
        """Test search command."""
        assert processor.process("play beethoven", 0) is True
        mock_player.play_any.assert_called_with("beethoven")

    def test_system_commands(self, processor):
        """Test system commands."""
        # We need to mock sys.exit or similar if we test shutdown, 
        # but volume controls are safer.
        
        # Mock input controller
        processor.input_controller = MagicMock()
        
        assert processor.process("volume up", 0) is True
        # Volume usually goes to player AND/OR input controller depending on implementation
        # CommandProcessor logic: calls self.active_player.volume_up() if available
        # But wait, CommandProcessor logic uses self.player (singular) based on initialization
        processor.player.volume_up.assert_called()

