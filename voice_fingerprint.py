"""
Voice Fingerprint - Personalized Voice Learning

Learns user's voice patterns to improve ASR accuracy over time.

Three-tier learning:
1. Passive Learning: Automatic from successful Ollama corrections
2. Manual Corrections: User-specified error patterns  
3. Command Frequency: Track popular commands
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import Counter
from datetime import datetime

logger = logging.getLogger("tuxtalks-cli")


class VoiceFingerprint:
    """Learns and stores user's voice patterns for personalized ASR correction."""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize voice fingerprint.
        
        Args:
            data_dir: Directory for fingerprint storage (default: ~/.local/share/tuxtalks)
        """
        if data_dir is None:
            data_dir = Path.home() / ".local" / "share" / "tuxtalks"
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.fingerprint_file = self.data_dir / "voice_fingerprint.json"
        
        # Data structures
        self.patterns = {}  # ASR error patterns: {"ever": {"likely_meant": ["abba"], "confidence": 0.9, ...}}
        self.commands = {}  # Command frequency: {"play abba": 45, ...}
        self.metadata = {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Load existing data
        self.load()
        
        logger.debug(f"VoiceFingerprint initialized: {len(self.patterns)} patterns, {len(self.commands)} commands")
    
    def add_passive_correction(self, asr_heard: str, ollama_resolved: str, intent: str = "") -> bool:
        """
        Learn from successful Ollama correction (PASSIVE LEARNING).
        
        This is the PRIMARY learning method - learns automatically from
        every successful command execution.
        
        Args:
            asr_heard: What ASR transcribed (e.g., "play ever")
            ollama_resolved: What Ollama extracted (e.g., "abba")
            intent: Ollama intent type (e.g., "play_artist")
            
        Returns:
            True if pattern was learned/updated
            
        Example:
            User says "Abba" → ASR hears "ever" → Ollama corrects to "abba"
            → System learns: "ever" likely means "abba"
        """
        # Extract the error word(s)
        error_word, correct_word = self._extract_error_pair(asr_heard, ollama_resolved)
        
        if not error_word or not correct_word:
            logger.debug(f"Could not extract error pair from '{asr_heard}' → '{ollama_resolved}'")
            return False
        
        # Normalize to lowercase
        error_word = error_word.lower()
        correct_word = correct_word.lower()
        
        # Initialize pattern if new
        if error_word not in self.patterns:
            self.patterns[error_word] = {
                "likely_meant": [],
                "confidence": 0.0,
                "count": 0,
                "source": "passive",
                "last_seen": datetime.now().isoformat()
            }
        
        pattern = self.patterns[error_word]
        
        # Add correction to history
        pattern["likely_meant"].append(correct_word)
        pattern["count"] += 1
        pattern["last_seen"] = datetime.now().isoformat()
        
        # Recalculate confidence based on frequency
        self._recalculate_confidence(error_word)
        
        # Update metadata
        self.metadata["last_updated"] = datetime.now().isoformat()
        
        # Persist immediately
        self.save()
        
        logger.info(f"📚 Learned: '{error_word}' → '{correct_word}' (confidence: {pattern['confidence']:.2f}, count: {pattern['count']})")
        
        return True
    
    def add_manual_correction(self, expected: str, heard: str) -> bool:
        """
        Add manual correction from user training (MANUAL LEARNING).
        
        This is the OPTIONAL learning method - user explicitly teaches
        problematic words.
        
        Args:
            expected: What user intended to say (e.g., "abba")
            heard: What ASR actually heard (e.g., "ever")
            
        Returns:
            True if pattern was learned/updated
        """
        # Extract the error
        error_word, correct_word = self._extract_error_pair(heard, expected)
        
        if not error_word or not correct_word:
            logger.warning(f"Could not extract error from expected='{expected}' heard='{heard}'")
            return False
        
        # Normalize
        error_word = error_word.lower()
        correct_word = correct_word.lower()
        
        # Initialize or update pattern
        if error_word not in self.patterns:
            self.patterns[error_word] = {
                "likely_meant": [],
                "confidence": 0.0,
                "count": 0,
                "source": "manual",
                "last_seen": datetime.now().isoformat()
            }
        
        pattern = self.patterns[error_word]
        
        # Manual corrections get higher weight (add 3 times)
        pattern["likely_meant"].extend([correct_word] * 3)
        pattern["count"] += 3
        pattern["source"] = "manual"  # Mark as manually trained
        pattern["last_seen"] = datetime.now().isoformat()
        
        # Recalculate confidence
        self._recalculate_confidence(error_word)
        
        # Update metadata
        self.metadata["last_updated"] = datetime.now().isoformat()
        
        # Persist
        self.save()
        
        logger.info(f"✏️  Manual: '{error_word}' → '{correct_word}' (confidence: {pattern['confidence']:.2f})")
        
        return True
    
    def add_successful_command(self, command: str) -> None:
        """
        Track successful command execution for frequency analysis.
        
        Args:
            command: Full command text (e.g., "play abba")
        """
        command = command.lower().strip()
        self.commands[command] = self.commands.get(command, 0) + 1
        
        # Only save every 10 commands to reduce I/O
        if sum(self.commands.values()) % 10 == 0:
            self.save()
    
    def get_corrections_for(self, text: str) -> Dict[str, str]:
        """
        Get likely corrections for words in this text.
        
        Args:
            text: Text to check for known error patterns
            
        Returns:
            Dictionary mapping error words to their likely corrections
            
        Example:
            text = "play ever" → {"ever": "abba"}
        """
        corrections = {}
        words = text.lower().split()
        
        for word in words:
            if word in self.patterns:
                pattern = self.patterns[word]
                
                # Only suggest high-confidence corrections
                if pattern["confidence"] >= 0.5:
                    # Get most common correction
                    likely_meant = pattern["likely_meant"]
                    if likely_meant:
                        counter = Counter(likely_meant)
                        most_common = counter.most_common(1)[0][0]
                        corrections[word] = most_common
        
        return corrections
    
    def get_correction_with_confidence(self, word: str) -> Optional[Tuple[str, float]]:
        """
        Get correction and confidence for a specific word.
        
        Args:
            word: Word to check
            
        Returns:
            (correction, confidence) tuple or None
        """
        word = word.lower()
        
        if word not in self.patterns:
            return None
        
        pattern = self.patterns[word]
        
        if not pattern["likely_meant"]:
            return None
        
        # Get most common correction
        counter = Counter(pattern["likely_meant"])
        most_common = counter.most_common(1)[0][0]
        
        return (most_common, pattern["confidence"])
    
    def top_commands(self, n: int = 10) -> List[str]:
        """
        Get top N most frequently used commands.
        
        Args:
            n: Number of commands to return
            
        Returns:
            List of command strings, sorted by frequency
        """
        sorted_commands = sorted(
            self.commands.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [cmd for cmd, count in sorted_commands[:n]]
    
    def get_all_patterns(self) -> Dict:
        """
        Get all learned patterns for debugging/export.
        
        Returns:
            Complete patterns dictionary
        """
        return self.patterns.copy()
    
    def clear_patterns(self) -> None:
        """Clear all learned patterns (reset voice fingerprint)."""
        self.patterns.clear()
        self.metadata["last_updated"] = datetime.now().isoformat()
        self.save()
        logger.info("🗑️  Voice fingerprint cleared")
    
    def clear_commands(self) -> None:
        """Clear command frequency data."""
        self.commands.clear()
        self.save()
        logger.info("🗑️  Command history cleared")
    
    def _extract_error_pair(self, asr_text: str, correct_text: str) -> Tuple[str, str]:
        """
        Extract the error word and correct word from two strings.
        
        Simple heuristic: Find the word that differs between the two texts.
        
        Args:
            asr_text: What ASR heard (e.g., "play ever")
            correct_text: What should have been heard (e.g., "abba")
            
        Returns:
            (error_word, correct_word) tuple
        """
        asr_words = set(asr_text.lower().split())
        correct_words = set(correct_text.lower().split())
        
        # Find words unique to ASR output (the error)
        error_candidates = asr_words - correct_words
        
        # Find words unique to correct output (the correction)
        correct_candidates = correct_words - asr_words
        
        # Simple case: one word differs
        if len(error_candidates) == 1 and len(correct_candidates) == 1:
            return (list(error_candidates)[0], list(correct_candidates)[0])
        
        # Fallback: use the last word of each (often the entity name)
        # Example: "play ever" vs "abba" → error="ever", correct="abba"
        if correct_candidates:
            # ASR probably garbled the entity name
            error_word = asr_text.split()[-1] if asr_text.split() else ""
            correct_word = correct_text.split()[-1] if correct_text.split() else ""
            
            # If correct_text is just the entity (e.g., "abba"), use it
            if len(correct_text.split()) == 1:
                correct_word = correct_text
            
            return (error_word, correct_word)
        
        return ("", "")
    
    def _recalculate_confidence(self, error_word: str) -> None:
        """
        Recalculate confidence score for a pattern based on frequency.
        
        Confidence increases with:
        - More occurrences
        - Consistency (same correction repeated)
        
        Args:
            error_word: The error word to recalculate
        """
        pattern = self.patterns[error_word]
        likely_meant = pattern["likely_meant"]
        
        if not likely_meant:
            pattern["confidence"] = 0.0
            return
        
        # Count occurrences
        counter = Counter(likely_meant)
        most_common_count = counter.most_common(1)[0][1]
        total_count = len(likely_meant)
        
        # Confidence = (most common / total) * sqrt(total / 10)
        # This balances consistency with sample size
        # Examples:
        #   - 5/5 occurrences = 1.0 * sqrt(0.5) = 0.71
        #   - 10/10 occurrences = 1.0 * sqrt(1.0) = 1.0
        #   - 8/10 occurrences = 0.8 * sqrt(1.0) = 0.8
        consistency = most_common_count / total_count
        sample_factor = min(1.0, (total_count / 10) ** 0.5)
        
        confidence = consistency * sample_factor
        pattern["confidence"] = round(confidence, 2)
    
    def load(self) -> bool:
        """
        Load fingerprint from disk.
        
        Returns:
            True if loaded successfully, False if file doesn't exist
        """
        if not self.fingerprint_file.exists():
            logger.debug("No existing voice fingerprint found")
            return False
        
        try:
            with open(self.fingerprint_file, 'r') as f:
                data = json.load(f)
            
            self.patterns = data.get("asr_patterns", {})
            self.commands = data.get("command_frequency", {})
            self.metadata = data.get("metadata", self.metadata)
            
            logger.info(f"📂 Loaded voice fingerprint: {len(self.patterns)} patterns, {len(self.commands)} commands")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to load voice fingerprint: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save fingerprint to disk.
        
        Returns:
            True if saved successfully
        """
        try:
            data = {
                "metadata": self.metadata,
                "asr_patterns": self.patterns,
                "command_frequency": self.commands
            }
            
            # Atomic write: write to temp file, then rename
            temp_file = self.fingerprint_file.with_suffix(".tmp")
            
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            temp_file.replace(self.fingerprint_file)
            
            logger.debug(f"💾 Saved voice fingerprint: {len(self.patterns)} patterns")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to save voice fingerprint: {e}")
            return False
    
    def export(self, filepath: Path) -> bool:
        """
        Export fingerprint to custom location.
        
        Args:
            filepath: Path to export to
            
        Returns:
            True if exported successfully
        """
        try:
            data = {
                "metadata": self.metadata,
                "asr_patterns": self.patterns,
                "command_frequency": self.commands
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"📤 Exported voice fingerprint to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export: {e}")
            return False
    
    def import_patterns(self, filepath: Path) -> bool:
        """
        Import patterns from another fingerprint file.
        
        Merges with existing patterns (doesn't overwrite).
        
        Args:
            filepath: Path to import from
            
        Returns:
            True if imported successfully
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            imported_patterns = data.get("asr_patterns", {})
            
            # Merge patterns
            for word, pattern in imported_patterns.items():
                if word in self.patterns:
                    # Merge likely_meant lists
                    self.patterns[word]["likely_meant"].extend(pattern["likely_meant"])
                    self.patterns[word]["count"] += pattern["count"]
                    self._recalculate_confidence(word)
                else:
                    self.patterns[word] = pattern
            
            self.save()
            
            logger.info(f"📥 Imported {len(imported_patterns)} patterns from {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to import: {e}")
            return False
