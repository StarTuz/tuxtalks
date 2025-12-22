"""Text Normalization Utilities

Handles voice recognition text processing including:
- Phonetic corrections and aliases
- User-defined corrections from config
- Spoken number parsing (1-99)
- Wake word stripping
"""

import re
from typing import Optional, Dict


class TextNormalizer:
    """Normalizes voice recognition text for command processing."""
    
    def __init__(self, config):
        """
        Initialize text normalizer.
        
        Args:
            config: Configuration object with VOICE_CORRECTIONS and WAKE_WORD
        """
        self.config = config
        self._build_aliases()
    
    def _load_system_corrections(self) -> dict:
        """Load system-wide corrections from data/system_corrections.json"""
        import json
        from pathlib import Path
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        
        try:
            # Look for system_corrections.json in package data
            system_file = Path(__file__).parent.parent / "data" / "system_corrections.json"
            if system_file.exists():
                data = json.loads(system_file.read_text())
                corrections = data.get("VOICE_CORRECTIONS", {})
                logger.debug(f"Loaded {len(corrections)} system corrections")
                return {k.lower(): v.lower() for k, v in corrections.items()}
        except Exception as e:
            logger.debug(f"Could not load system corrections: {e}")
        
        return {}
    
    def _load_personal_corrections(self) -> dict:
        """Load user's personal corrections from ~/.local/share/tuxtalks/personal_corrections.json"""
        import json
        from pathlib import Path
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        
        try:
            personal_file = Path.home() / ".local/share/tuxtalks/personal_corrections.json"
            if personal_file.exists():
                data = json.loads(personal_file.read_text())
                corrections = data.get("VOICE_CORRECTIONS", {})
                logger.debug(f"Loaded {len(corrections)} personal corrections")
                return {k.lower(): v.lower() for k, v in corrections.items()}
        except Exception as e:
            logger.debug(f"Could not load personal corrections: {e}")
        
        return {}
    
    def _load_game_corrections(self) -> dict:
        """Load active game profile corrections"""
        import json
        from pathlib import Path
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        
        try:
            # Only load if game mode is enabled
            if not self.config.get("GAME_MODE_ENABLED", False):
                return {}
            
            game_profile = self.config.get("LAST_GAME_PROFILE")
            if not game_profile:
                return {}
            
            game_dir = Path.home() / ".local/share/tuxtalks/games" / game_profile
            game_config = game_dir / "config.json"
            
            if game_config.exists():
                data = json.loads(game_config.read_text())
                corrections = data.get("VOICE_CORRECTIONS", {})
                logger.debug(f"Loaded {len(corrections)} game corrections from {game_profile}")
                return {k.lower(): v.lower() for k, v in corrections.items()}
        except Exception as e:
            logger.debug(f"Could not load game corrections: {e}")
        
        return {}
    
    def _build_aliases(self) -> Dict[str, str]:
        """Build phonetic aliases dictionary from multiple sources with priority system.
        
        Priority (lowest to highest):
        1. Built-in hardcoded aliases
        2. System corrections (system_corrections.json)
        3. Personal corrections (personal_corrections.json)
        4. Game corrections (when game mode enabled)
        5. Config.json (backwards compatibility, highest priority)
        """
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        
        # Base phonetic aliases / corrections (Priority 1 - Lowest)
        aliases = {
            "von": "vaughan",
            "vaughn": "vaughan",
            "von williams": "vaughan williams",
            "vaughn williams": "vaughan williams",
            "play von": "play vaughan",
            "play vaughn": "play vaughan",
            "council": "cancel",
            "counsel": "cancel",
            "abo": "abba",
            "play abo": "play abba",
            "stuff host": "gustav holst",
            "stuff housed": "gustav holst",
            "stuff house": "gustav holst",
            "plague": "play",
            "plate": "play",
            "flight": "play",
            "blake": "play",
            "like": "play",
            "the l c": "vlc",
            "we'll see": "vlc",
            "v l c": "vlc",
            "list commands for": "help",
            "list commands": "help",
            "what can i say": "help",
            "help me": "help",
            "dot house": "gustav holst",
            "good stuff": "gustav",
            "good gustav": "gustav",
            "lift tracks": "list tracks",
            "mangle": "mango",
            "to lay": "play",
            "played": "play",
            "both home": "beethoven",
            "by toll and": "beethoven",
            "bite over": "beethoven",
            "bay toven": "beethoven",
            "bee toven": "beethoven",
            "beth oven": "beethoven",
            "by told them": "beethoven",
            "bite how them": "beethoven",
            "slay": "play",
            "slay a": "play",
            "bait open": "beethoven",
            "bait hold them": "beethoven",
            "bait over": "beethoven",
            "bait home": "beethoven",
            "boat over": "beethoven",
            "take both of them": "play beethoven",
            "both of them": "beethoven",
            "slight": "play",
            "play over": "play beethoven",
            "back home": "beethoven",
            "both over": "beethoven",
            "bite of them": "beethoven",
            "so a bite of them": "play beethoven",
            "so a": "play",
            "ball mr williams": "vaughan williams",
            "born williams": "vaughan williams",
        }
        
        # Dynamic aliases based on wake word
        wake_word = self.config.get("WAKE_WORD", "").lower()
        if wake_word == "picard":
            aliases.update({
                "card": "picard",
                "pick a card": "picard",
                "pick card": "picard",
                "the card": "picard",
                "pick card the god": "picard",
                "be card": "picard",
                "a picard": "picard",
            })
        
        # Additional common corrections
        aliases.update({
            "glide": "play",
            "make it so": "play",
            "bracket elmer": "brachypelma",
            "bracket palma": "brachypelma",
            "tragic": "brachypelma",
            "bragg sheila": "brachypelma",
            "triangular us": "tarantula",
            "trans you liar": "tarantula",
            "trench hiller": "tarantula",
            "trench lower": "tarantula",
            "trench you look hideous": "tarantula",
            "spider": "tarantula",
            "clay": "play",
            "place by the": "play",
            "to a": "play",
            "spice go": "play",
        })
        
        logger.debug(f"Built-in aliases: {len(aliases)}")
        
        # Priority 2: System corrections
        system_corrections = self._load_system_corrections()
        if system_corrections:
            aliases.update(system_corrections)
            logger.debug(f"After system corrections: {len(aliases)} total")
        
        # Priority 3: Personal corrections
        personal_corrections = self._load_personal_corrections()
        if personal_corrections:
            aliases.update(personal_corrections)
            logger.debug(f"After personal corrections: {len(aliases)} total")
        
        # Priority 4: Game corrections (only when game mode active)
        game_corrections = self._load_game_corrections()
        if game_corrections:
            aliases.update(game_corrections)
            logger.debug(f"After game corrections: {len(aliases)} total")
        
        # Priority 5: Config.json corrections (backwards compatibility, highest)
        user_corrections = self.config.get("VOICE_CORRECTIONS")
        if user_corrections and isinstance(user_corrections, dict):
            normalized_corrections = {k.lower(): v.lower() for k, v in user_corrections.items()}
            aliases.update(normalized_corrections)
            logger.debug(f"After config.json: {len(aliases)} total (final)")
        
        self.aliases = aliases
        logger.info(f"Text normalizer loaded {len(aliases)} total corrections")
        return aliases
    
    def normalize(self, text: str, state: int = 0, wake_word: str = "") -> str:
        """
        Normalize spoken text to fix common recognition errors.
        
        Args:
            text: Input text from voice recognition
            state: Current assistant state (0=LISTENING, 1=WAITING_SELECTION, 2=COMMAND_MODE)
            wake_word: Wake word to strip if not in listening mode
            
        Returns:
            Normalized text
        """
        text = text.lower()
        
        # Apply replacements using word boundaries to avoid substring matching
        for wrong, right in self.aliases.items():
            pattern = r'\b' + re.escape(wrong) + r'\b'
            text = re.sub(pattern, right, text)
        
        # Strip wake word if present (but only if NOT in listening mode)
        # In LISTENING mode (0), we need the wake word to trigger the transition
        if state != 0 and wake_word:
            wake_word_lower = wake_word.lower()
            if text.startswith(wake_word_lower + " "):
                text = text[len(wake_word_lower)+1:]
        
        return text.strip(".,!?;: ")
    
    def parse_number(self, text: str) -> Optional[int]:
        """
        Parse a spoken number (1-99) from text.
        
        Args:
            text: Text containing spoken number
            
        Returns:
            Parsed integer or None if no number found
        """
        text = text.lower()
        
        # Simple map for 0-19 and tens
        num_map = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14,
            'fifteen': 15, 'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50,
            'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
        }
        
        # Homophones / Common misrecognitions
        corrections = {
            "for": "four", "to": "two", "too": "two", "tree": "three", "ate": "eight",
            "won": "one", "sea": "three", "sex": "six", "night": "eight"
        }
        
        # Strip punctuation from words
        cleaned_words = [w.strip(".,!?;:") for w in text.split()]
        
        words = cleaned_words
        current = 0
        found_number = False
        
        for word in words:
            word = corrections.get(word, word)
            
            val = None
            if word.isdigit():
                val = int(word)
            elif word in num_map:
                val = num_map[word]
            
            if val is not None:
                if val < 100:
                    # Only add if current is a multiple of 10 (>= 20) and val is a single digit
                    if current >= 20 and current % 10 == 0 and val < 10:
                        current += val
                    else:
                        current = val
                    found_number = True
            elif word == "hundred":
                pass  # Ignore for now, we only care about < 100
        
        if found_number:
            return current
        return None
