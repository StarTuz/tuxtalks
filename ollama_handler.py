"""
Ollama AI Integration Handler

Provides natural language understanding for TuxTalks voice commands.
Routes music commands through Ollama LLM, maintains fast keyword path for games.
"""

import requests
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger("tuxtalks-cli")


class OllamaHandler:
    """Handles Ollama LLM integration for intent extraction"""
    
    def __init__(self, config, player=None):
        """
        Initialize Ollama handler.
        
        Args:
            config: Configuration object with Ollama settings
            player: Media player instance for library context (optional)
        """
        self.url = config.get("OLLAMA_URL", "http://localhost:11434")
        self.model = config.get("OLLAMA_MODEL", "llama2")
        self.timeout = config.get("OLLAMA_TIMEOUT", 2000) / 1000  # ms to seconds
        self.cache = {}  # Cache for repetitive game commands
        self.enabled = config.get("OLLAMA_ENABLED", False)
        self.player = player  # Store for library context
        
        # Initialize voice fingerprint for personalized learning
        try:
            from voice_fingerprint import VoiceFingerprint
            self.voice_fingerprint = VoiceFingerprint()
            logger.debug(f"Voice fingerprint loaded: {len(self.voice_fingerprint.patterns)} patterns")
        except Exception as e:
            logger.warning(f"Could not load voice fingerprint: {e}")
            self.voice_fingerprint = None
        
        logger.info(f"Ollama handler initialized: {self.url}, model={self.model}")
    
    def health_check(self) -> bool:
        """
        Check if Ollama is available and responding.
        
        Returns:
            True if Ollama is reachable, False otherwise
        """
        try:
            response = requests.get(f"{self.url}/api/tags", timeout=2)
            available = response.status_code == 200
            
            if available:
                logger.debug("Ollama health check: OK")
            else:
                logger.warning("Ollama health check: Failed")
            
            return available
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False
    
    def extract_intent(self, text: str) -> Dict:
        """
        Extract intent from natural language text using Ollama.
        
        Args:
            text: User's voice command (already normalized)
        
        Returns:
            Dictionary with:
            - success: bool (True if intent extracted)
            - intent: str (e.g., "play_artist")
            - parameters: dict (e.g., {"artist": "beethoven"})
            - confidence: float (0.0-1.0)
            - raw_response: str (for debugging)
        """
        # Check cache first (for repetitive game commands)
        cache_key = text.lower().strip()
        if cache_key in self.cache:
            logger.debug(f"Cache hit for: '{text}'")
            return self.cache[cache_key]
        
        # Build prompt
        prompt = self._build_prompt(text)
        
        try:
            logger.debug(f"Querying Ollama: '{text}'")
            
            response = requests.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"  # Request JSON output
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                raw_response = result.get("response", "{}")
                
                try:
                    intent_data = json.loads(raw_response)
                    
                    # Validate response structure
                    if "intent" not in intent_data:
                        logger.error("Ollama response missing 'intent' field")
                        return {"success": False}
                    
                    # Build result
                    result_dict = {
                        "success": True,
                        "intent": intent_data.get("intent"),
                        "parameters": intent_data.get("parameters", {}),
                        "confidence": intent_data.get("confidence", 0.5),
                        "raw_response": raw_response
                    }
                    
                    # Cache successful results (especially game commands)
                    if len(self.cache) < 100:  # Limit cache size
                        self.cache[cache_key] = result_dict
                    
                    logger.debug(f"Ollama success: {result_dict['intent']} (conf: {result_dict['confidence']})")
                    return result_dict
                
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse Ollama JSON: {e}")
                    logger.debug(f"Raw response: {raw_response}")
                    return {"success": False}
            
            else:
                logger.error(f"Ollama HTTP {response.status_code}")
                return {"success": False}
        
        except requests.Timeout:
            logger.warning(f"Ollama timeout after {self.timeout}s - falling back to keywords")
            return {"success": False}
        
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return {"success": False}
    
    def _build_prompt(self, text: str) -> str:
        """
        Build prompt with JSON schema and ASR error correction.
        
        Includes personalized corrections from voice fingerprint!
        
        Args:
            text: User's command text
        
        Returns:
            Formatted prompt string
        """
        # Build base prompt
        prompt = '''You are a voice command interpreter for a media player and gaming voice assistant.

Extract the intent and parameters from the following voice command.

IMPORTANT: This text came from speech recognition and may contain errors.
Common ASR mistakes you should correct:
- "back oven" → "beethoven"
- "told them" → "beethoven"  
- "cargo soup" → "cargo scoop"
- "landing girl" → "landing gear"
- "hardpoint" variations → "hardpoints"
- "track gale" → "gear" (landing gear)
- "play over" → "play beethoven"
- "she economy" → "kiri te kanawa"
'''
        
        # Add personalized corrections from voice fingerprint
        if self.voice_fingerprint:
            corrections = self.voice_fingerprint.get_corrections_for(text)
            
            if corrections:
                prompt += "\nPERSONALIZED CORRECTIONS (learned from this user's voice):\n"
                for error_word, correction in corrections.items():
                    # Get confidence
                    result = self.voice_fingerprint.get_correction_with_confidence(error_word)
                    if result:
                        correct_word, confidence = result
                        prompt += f'- "{error_word}" likely means "{correct_word}" (confidence: {confidence:.0%})\n'
                
                logger.debug(f"Added {len(corrections)} personalized corrections to prompt")
        
        # Add library context (Phase 2: Library Context)
        if self.player:
            try:
                artists = self.player.get_all_artists(limit=50)
                if artists:
                    # Format as comma-separated list
                    artists_str = ", ".join(artists[:50])
                    prompt += f'''
USER'S MUSIC LIBRARY (correct ASR errors to match these artists):
{artists_str}

'''
                    logger.debug(f"Added library context: {len(artists)} artists")
            except Exception as e:
                logger.debug(f"Could not fetch library context: {e}")

        
        # Add command text and schema
        prompt += f'''
Voice Command: "{text}"

Valid Intents:
- play_artist: Play music by an artist
- play_album: Play a specific album
- play_track: Play a specific track
- play_genre: Play music by genre
- volume_up: Increase volume
- volume_down: Decrease volume
- next_track: Skip to next track
- previous_track: Go to previous track
- pause: Pause playback
- resume: Resume playback
- stop: Stop playback
- what_is_playing: Query current track
- game_command: Execute game action (ONLY if clearly game-related)
- help: Request help
- quit: Exit application

Respond with JSON only (no explanation):
{{{{
    "intent": "intent_name",
    "parameters": {{}},
    "confidence": 0.95
}}}}

Examples:
"play some beatles" → {{{{"intent": "play_artist", "parameters": {{"artist": "beatles"}}, "confidence": 0.9}}}}
"what's playing?" → {{{{"intent": "what_is_playing", "parameters": {{}}, "confidence": 1.0}}}}
"louder please" → {{{{"intent": "volume_up", "parameters": {{}}, "confidence": 0.95}}}}
"play back oven" → {{{{"intent": "play_artist", "parameters": {{"artist": "beethoven"}}, "confidence": 0.85}}}}
'''
        
        return prompt
    
    def clear_cache(self):
        """Clear the command cache"""
        self.cache.clear()
        logger.debug("Ollama cache cleared")
