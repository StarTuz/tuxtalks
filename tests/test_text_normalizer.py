
import pytest
from unittest.mock import MagicMock
from core.text_normalizer import TextNormalizer

class TestTextNormalizer:
    @pytest.fixture
    def mock_config(self):
        config = MagicMock()
        # Default empty config
        config.get.side_effect = lambda key, default=None: {
            "WAKE_WORD": "computer",
            "VOICE_CORRECTIONS": {}
        }.get(key, default)
        return config

    @pytest.fixture
    def normalizer(self, mock_config):
        return TextNormalizer(mock_config)

    def test_basic_normalization(self, normalizer):
        """Test basic lowercase and punctuation stripping."""
        assert normalizer.normalize("Hello World!") == "hello world"
        assert normalizer.normalize("  Test.  ") == "test"

    def test_alias_replacement(self, normalizer):
        """Test phonetic alias replacement."""
        # "flight" -> "play"
        assert normalizer.normalize("flight some music") == "play some music"
        # "mangle" -> "mango"
        assert normalizer.normalize("play mangle") == "play mango"

    def test_word_boundary_protection(self, normalizer):
        """Ensure replacements don't affect partial matches."""
        # "flight" -> "play", but "flightless" should stay "flightless"
        assert normalizer.normalize("flightless bird") == "flightless bird"
        
    def test_wake_word_stripping(self, normalizer):
        """Test wake word stripping based on state."""
        # State 0 (LISTENING) -> Keep wake word
        assert normalizer.normalize("computer play music", state=0, wake_word="computer") == "computer play music"
        
        # State 1 (WAITING) -> Strip wake word
        assert normalizer.normalize("computer play music", state=1, wake_word="computer") == "play music"
        
        # Check case insensitivity
        assert normalizer.normalize("Computer play music", state=1, wake_word="computer") == "play music"

    def test_user_defined_corrections(self, mock_config):
        """Test user-defined corrections from config."""
        mock_config.get.side_effect = lambda key, default=None: {
            "WAKE_WORD": "computer",
            "VOICE_CORRECTIONS": {"foo": "bar", "baz": "qux"}
        }.get(key, default)
        
        normalizer = TextNormalizer(mock_config)
        assert normalizer.normalize("say foo") == "say bar"
        assert normalizer.normalize("find baz") == "find qux"

    def test_parse_number_digits(self, normalizer):
        """Test parsing simple digit words."""
        assert normalizer.parse_number("one") == 1
        assert normalizer.parse_number("five") == 5
        assert normalizer.parse_number("ten") == 10
        assert normalizer.parse_number("twenty") == 20

    def test_parse_number_compounds(self, normalizer):
        """Test parsing compound numbers."""
        assert normalizer.parse_number("twenty one") == 21
        assert normalizer.parse_number("forty two") == 42
        assert normalizer.parse_number("ninety nine") == 99

    def test_parse_number_homophones(self, normalizer):
        """Test parsing number homophones."""
        assert normalizer.parse_number("track for") == 4
        assert normalizer.parse_number("track two") == 2
        assert normalizer.parse_number("track too") == 2
        assert normalizer.parse_number("track to") == 2
        assert normalizer.parse_number("track won") == 1

    def test_parse_number_digit_strings(self, normalizer):
        """Test parsing actual digit characters."""
        assert normalizer.parse_number("track 5") == 5
        assert normalizer.parse_number("level 42") == 42
