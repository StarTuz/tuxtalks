"""Command Processor

Handles voice command routing and execution for the voice assistant.
Delegates to appropriate handlers based on command type.
"""

from typing import Tuple, Optional, Any


class CommandProcessor:
    """Processes voice commands and routes to appropriate handlers."""
    
    def __init__(self, player, game_manager, input_controller, 
                 selection_handler, text_normalizer, speak_func, config, speech_queue, state_machine):
        """
        Initialize command processor.
        
        Args:
            player: Media player instance
            game_manager: GameManager instance
            input_controller: InputController instance
            selection_handler: SelectionHandler instance
            text_normalizer: TextNormalizer instance
            speak_func: Function to queue speech
            config: Configuration object
            speech_queue: Queue for speech/exit signals
            state_machine: AssistantStateMachine for state sync
        """
        self.player = player
        self.game_manager = game_manager
        self.input_controller = input_controller
        self.selection_handler = selection_handler
        self.text_normalizer = text_normalizer
        self.speak = speak_func
        self.config = config
        self.speech_queue = speech_queue
        self.state_machine = state_machine
    
    def _sync_state(self):
        """Helper to sync state after selection_handler changes it."""
        # This will be called by VoiceAssistant after process() returns
        pass
    
    def process(self, text: str, state: int) -> bool:
        """
        Process a voice command with smart routing.
        
        **Routing Strategy:**
        1. Simple media controls → Fast keywords (always <100ms)
        2. Complex queries + Gaming → Ollama (prevents misrouting to game commands)
        3. Complex queries + Not Gaming → Keyword fallback (faster response)
        
        Args:
            text: Command text (already normalized)
            state: Current assistant state
            
        Returns:
            True to continue, False to quit
        """
        # Pre-process text corrections
        text = self._preprocess_text(text)
        
        # Store original ASR output for passive learning
        self.last_asr_output = text
        
        # STRATEGY 1: Simple media controls → Always fast keywords (safe & fast)
        SIMPLE_CONTROLS = [
            "next", "previous", "pause", "stop", "resume", 
            "volume up", "volume down", "louder", "quieter",
            "what's playing", "what is playing"
        ]
        
        if any(text.startswith(ctrl) or text == ctrl for ctrl in SIMPLE_CONTROLS):
            import logging
            logger = logging.getLogger("tuxtalks-cli")
            logger.debug(f"Simple media control, using fast keywords: '{text}'")
            
            if self._handle_media_control(text):
                return True
        
        # STRATEGY 2 & 3: Complex queries - route based on game mode
        is_music_command = self._quick_media_check(text)
        
        if is_music_command:
            import logging
            logger = logging.getLogger("tuxtalks-cli")
            
            # Check if we're currently gaming
            is_gaming = self.game_manager.game_mode_enabled
            
            if is_gaming:
                # STRATEGY 2: Gaming → Force Ollama (prevents music→game misrouting)
                logger.debug(f"Music command while gaming, forcing Ollama: '{text}'")
                
                if self.config.get("OLLAMA_ENABLED", False):
                    try:
                        # Lazy import
                        if not hasattr(self, '_ollama'):
                            from ollama_handler import OllamaHandler
                            self._ollama = OllamaHandler(self.config, player=self.player)
                            
                            # Health check on first use
                            if not self._ollama.health_check():
                                print("⚠️  Ollama not available, using keywords")
                                self._ollama_available = False
                            else:
                                self._ollama_available = True
                        
                        # Try Ollama if available
                        if getattr(self, '_ollama_available', True):
                            result = self._ollama.extract_intent(text)
                            
                            if result.get("success") and result.get("confidence", 0) > 0.8:
                                intent = result.get("intent")
                                params = result.get("parameters", {})
                                
                                logger.info(f"Ollama: {intent} (confidence: {result['confidence']:.2f})")
                                
                                # Execute intent and learn from success!
                                if self._execute_ollama_intent(intent, params):
                                    logger.debug("Ollama path succeeded")
                                    self._learn_from_success(intent, params)
                                    return True
                                else:
                                    logger.warning("Ollama intent execution failed")
                    
                    except ImportError as e:
                        print(f"⚠️  Ollama module not found: {e}")
                    except Exception as e:
                        logger.warning(f"Ollama error: {e}")
                
                # Ollama failed or unavailable - fall through to keyword fallback
                logger.debug("Ollama unavailable, using keywords")
            
            else:
                # STRATEGY 3: Not gaming → Try Ollama but allow quick keyword fallback
                logger.debug(f"Music command (not gaming), trying Ollama with keyword fallback: '{text}'")
                
                if self.config.get("OLLAMA_ENABLED", False):
                    try:
                        # Lazy import
                        if not hasattr(self, '_ollama'):
                            from ollama_handler import OllamaHandler
                            self._ollama = OllamaHandler(self.config, player=self.player)
                            
                            if not self._ollama.health_check():
                                print("⚠️  Ollama not available, using keywords")
                                self._ollama_available = False
                            else:
                                self._ollama_available = True
                        
                        # Try Ollama if available
                        if getattr(self, '_ollama_available', True):
                            result = self._ollama.extract_intent(text)
                            
                            if result.get("success") and result.get("confidence", 0) > 0.8:
                                intent = result.get("intent")
                                params = result.get("parameters", {})
                                
                                logger.info(f"Ollama: {intent} (confidence: {result['confidence']:.2f})")
                                
                                if self._execute_ollama_intent(intent, params):
                                    logger.debug("Ollama path succeeded")
                                    self._learn_from_success(intent, params)
                                    return True
                    
                    except ImportError:
                        pass
                    except Exception as e:
                        logger.debug(f"Ollama error: {e}, using keywords")
            
            # Music keyword fallback (works for both gaming and non-gaming)
            logger.debug("Using media keywords")
            
            if self._handle_media_control(text):
                return True
            if self._handle_playback_command(text):
                return True
            
            print(f"🤷 Ignored music command: {text}")
            return True
        
        # Non-music commands: Use fast keyword path (<100ms)
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        logger.debug("Game/system command, using fast keywords")
        
        # System commands (highest priority)
        if self._handle_quit_command(text):
            return False  # Signal quit
        
        if self._handle_help_command(text):
            return True
        
        # Game mode commands
        if self._handle_game_mode_command(text):
            return True
        
        # Player switching
        if self._handle_player_switch(text):
            return True
        
        # Game command delegation (if game mode enabled)
        if self._handle_game_command(text):
            return True
        
        # Media control commands (shouldn't hit here if pre-filter works)
        if self._handle_media_control(text):
            return True
        
        # Search and playback commands
        if self._handle_playback_command(text):
            return True
        
        # If nothing matched, ignore
        print(f"🤷 Ignored: {text}")
        return True
    
    def _quick_media_check(self, text: str) -> bool:
        """
        Fast heuristic to detect music commands (2ms overhead).
        
        Args:
            text: Command text
            
        Returns:
            True if likely a music/media command
        """
        media_keywords = [
            "play", "pause", "stop", "next", "previous",
            "volume", "louder", "quieter", "shuffle",
            "album", "artist", "track", "music", "song",
            "resume", "skip", "what"  # "what is playing"
        ]
        
        # Check first 2 words only (fast!)
        words = text.lower().split()[:2]
        return any(keyword in words for keyword in media_keywords)
    
    def _execute_ollama_intent(self, intent: str, params: dict) -> bool:
        """
        Execute an Ollama-extracted intent.
        
        Args:
            intent: Intent name (e.g., "play_artist")
            params: Intent parameters (e.g., {"artist": "beethoven"})
            
        Returns:
            True if successfully executed
        """
        try:
            if intent == "play_artist":
                artist = params.get("artist", "")
                if artist:
                    # Route to existing playback command
                    return self._handle_playback_command(f"play {artist}")
            
            elif intent == "play_album":
                album = params.get("album", "")
                if album:
                    return self._handle_playback_command(f"play album {album}")
            
            elif intent == "play_track":
                track = params.get("track", "")
                if track:
                    return self._handle_playback_command(f"play track {track}")
            
            elif intent == "play_genre":
                genre = params.get("genre", "")
                if genre:
                    # Route to player's genre method
                    if hasattr(self.player, 'play_random_genre'):
                        self.player.play_random_genre(genre)
                        return True
                    else:
                        return self._handle_playback_command(f"play {genre}")
            
            elif intent == "volume_up":
                self.player.volume_up()
                return True
            
            elif intent == "volume_down":
                self.player.volume_down()
                return True
            
            elif intent == "next_track":
                self.player.next_track()
                return True
            
            elif intent == "previous_track":
                self.player.previous_track()
                return True
            
            elif intent == "pause":
                self.player.pause()
                return True
            
            elif intent == "resume":
                self.player.resume()
                return True
            
            elif intent == "stop":
                self.player.stop()
                return True
            
            elif intent == "what_is_playing":
                self.player.whats_playing()
                return True
            
            elif intent == "help":
                return self._handle_help_command("help")
            
            elif intent == "quit":
                return self._handle_quit_command("quit")
            
            else:
                import logging
                logger = logging.getLogger("tuxtalks-cli")
                logger.warning(f"Unknown Ollama intent: {intent}")
                return False
        
        except Exception as e:
            import logging
            logger = logging.getLogger("tuxtalks-cli")
            logger.error(f"Error executing intent {intent}: {e}")
            return False
    
    def _learn_from_success(self, intent: str, params: dict) -> None:
        """
        Learn from successful Ollama correction (PASSIVE LEARNING).
        
        Detects when Ollama successfully corrected an ASR error and
        teaches the voice fingerprint.
        
        Example:
            User says "Abba" → ASR hears "play ever"
            → Ollama extracts artist="abba"
            → Music plays successfully
            → System learns: "ever" → "abba"
        
        Args:
            intent: Successful intent (e.g., "play_artist")
            params: Extracted parameters (e.g., {"artist": "abba"})
        """
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        
        # Debug: Show what we're analyzing
        logger.debug(f"🔍 Passive learning check: intent={intent}, params={params}")
        logger.debug(f"🔍 Original ASR: '{self.last_asr_output}'")
        
        if not hasattr(self, '_ollama') or not self._ollama:
            logger.debug("🔍 No Ollama instance, skipping learning")
            return
        
        if not self._ollama.voice_fingerprint:
            logger.debug("🔍 No voice fingerprint, skipping learning")
            return
        
        # Check if Ollama corrected an entity name
        # (artist, album, track, genre)
        entity_params = ["artist", "album", "track", "genre"]
        
        for param_name in entity_params:
            if param_name in params:
                extracted = params[param_name].lower()
                original_asr = self.last_asr_output.lower()
                
                logger.debug(f"🔍 Checking {param_name}: extracted='{extracted}', asr='{original_asr}'")
                logger.debug(f"🔍 Is '{extracted}' in '{original_asr}'? {extracted in original_asr}")
                
                # If Ollama extracted something NOT in the ASR output,
                # it means it successfully corrected an error!
                if extracted and extracted not in original_asr:
                    # This is a correction worth learning!
                    logger.info(f"🎯 CORRECTION DETECTED! ASR had '{original_asr}' but Ollama extracted '{extracted}'")
                    
                    self._ollama.voice_fingerprint.add_passive_correction(
                        asr_heard=self.last_asr_output,
                        ollama_resolved=extracted,
                        intent=intent
                    )
                    
                    logger.info(f"📚 Passive learning: '{self.last_asr_output}' → '{extracted}'")
                    
                    break  # Only learn one correction per command
                else:
                    logger.debug(f"🔍 No correction needed - '{extracted}' was in ASR output")
    
    def _preprocess_text(self, text: str) -> str:
        """Apply text corrections before processing."""
        # Common misrecognition: "but" → "play"
        if text.startswith("but "):
            text = text.replace("but ", "play ", 1)
            print(f"🔧 Corrected 'but' to 'play': {text}")
        return text
    
    def _handle_quit_command(self, text: str) -> bool:
        """Handle quit/exit commands."""
        if any(word in text for word in ["quit", "exit", "stop listening", "goodbye", "good bye", "leave"]):
            self.player.stop()
            self.speak("Goodbye.")
            self.speech_queue.put(None)  # Sentinel for exit
            return True
        return False
    
    def _handle_help_command(self, text: str) -> bool:
        """Handle help commands."""
        if text == "list commands":
            print("Commands: play [anything], stop, next, quit, what's playing")
            self.speak("You can say play [artist or album], stop, next, quit, or what's playing.")
            return True
        return False
    
    def _handle_game_mode_command(self, text: str) -> bool:
        """Handle game mode enable/disable."""
        if "enable game mode" in text.lower():
            self.game_manager.set_enabled(True)
            self.config.set("GAME_MODE_ENABLED", True)
            self.config.save()
            self.speak("Game mode enabled.")
            return True
        elif "disable game mode" in text.lower():
            self.game_manager.set_enabled(False)
            self.config.set("GAME_MODE_ENABLED", False)
            self.config.save()
            self.speak("Game mode disabled.")
            return True
        return False
    
    def _handle_player_switch(self, text: str) -> bool:
        """Handle player switching commands. Returns True if handled."""
        import logging
        logger = logging.getLogger("tuxtalks-cli")
        
        # Match various phrasings
        if any(phrase in text.lower() for phrase in ["change player", "switch player", "select player"]) or text.strip().lower() == "player":
            logger.info(f"Player switch requested: '{text}'")
            
            # Clear any active selection state - player switching takes priority
            if hasattr(self.selection_handler, 'clear'):
                logger.debug("Clearing selection state for player switch")
                self.selection_handler.clear()
            
            # Get available players
            available_players = self._detect_available_players()
            logger.debug(f"Detected {len(available_players)} players")
            
            if not available_players:
                self.speak("No media players detected.")
                return True
            
            # Show in runtime menu for selection
            player_items = [(name, player_id) for name, player_id in available_players]
            display_names = [name for name, _ in player_items]
            
            self.speak(f"Available players detected: {len(available_players)}")
            logger.debug(f"Setting player items: {player_items}")
            self.selection_handler.set_items(
                [(name, player_id, "player") for name, player_id in player_items],
                "Player"
            )
            self.selection_handler.speak_options()
            
            # Note: Selection will be handled by selection_handler
            # which will call _execute_selection → needs special handling for player type
            return True
        
        # Also handle direct "change player to X" commands
        if "change player to" in text.lower() or "switch player to" in text.lower():
            target = text.lower().replace("change player to", "").replace("switch player to", "").strip()
            
            # Map common names
            player_map = {
                "jriver": "jriver",
                "j river": "jriver",
                "vlc": "vlc",
                "elisa": "elisa",
                "strawberry": "strawberry",
                "mpris": "mpris"
            }
            
            player_id = player_map.get(target)
            if player_id and hasattr(self, '_reload_player'):
                self._reload_player(player_id)
                self.config.set("PLAYER", player_id)
                self.config.save()
                self.speak(f"Switched to {target}")
            else:
                self.speak(f"Unknown player: {target}")
            return True
        
        return False
    
    def _detect_available_players(self):
        """Get available media players from config PLAYER_SCHEMAS."""
        from config import PLAYER_SCHEMAS
        available = []
        
        # Get current player from config
        current_player = self.config.get("PLAYER", "").lower()
        
        # Use PLAYER_SCHEMAS as source of truth (same as GUI dropdown)
        for player_id in PLAYER_SCHEMAS.keys():
            # Create display name (capitalize first letter)
            name = player_id.capitalize()
            
            # Better display names
            if player_id == "jriver":
                name = "JRiver Media Center"
            elif player_id == "mpris":
                name = "MPRIS (Generic)"
            elif player_id == "elisa":
                name = "Elisa Music Player"
            elif player_id == "strawberry":
                name = "Strawberry Music Player"
            
            # Mark current player
            if player_id == current_player:
                name += " (current)"
            
            available.append((name, player_id))
        
        return available
    
    def _handle_game_command(self, text: str) -> bool:
        """Delegate to game manager if applicable."""
        handled, msg = self.game_manager.handle_command(text, self.input_controller)
        if handled:
            if msg:
                self.speak(msg)
            return True
        return False
    
    def _handle_media_control(self, text: str) -> bool:
        """Handle media control commands (pause, next, stop, etc.)."""
        if "pause" in text:
            self.player.play_pause()
            return True
        
        if "stop" in text:
            self.player.stop()
            return True
        
        if text in ["play", "resume", "start music"]:
            self.player.play_pause()
            return True
        
        if "next track" in text or "next song" in text or text in ["next", "skip"]:
            self.player.next_track()
            return True
        
        if "previous track" in text or "previous song" in text or text in ["previous", "back"]:
            self.player.previous_track()
            return True
        
        if "volume up" in text:
            self.player.volume_up()
            return True
        
        if "volume down" in text:
            self.player.volume_down()
            return True
        
        if text in ["turn it off", "shut down", "stop all"]:
            self.speak("Stopping playback and turning off.")
            self.player.stop()
            return True
        
        if "what is playing" in text or "what song is this" in text or "what's playing" in text or "what song" in text or "what track" in text:
            self.player.whats_playing()
            return True
        
        return False
    
    def _handle_playback_command(self, text: str) -> bool:
        """Handle complex playback commands (searches, playlists, etc.)."""
        
        # List tracks
        if "list tracks" in text or "show tracks" in text or "show playlist" in text:
            items = self.player.list_tracks()
            if items and isinstance(items, list):
                self.selection_handler.set_items(items, "Track")
                self.selection_handler.speak_options()
            return True
        
        # Go to track N
        if "go to track" in text or "jump to track" in text or "play track" in text or "play truck" in text or "play crack" in text or "play black" in text or "play check" in text:
            words = text.split()
            track_num = None
            
            for word in words:
                if word.isdigit():
                    track_num = int(word)
                    break
                parsed = self.text_normalizer.parse_number(word)
                if parsed:
                    track_num = parsed
                    break
            
            if track_num:
                if hasattr(self.player, 'go_to_track'):
                    if self.player.go_to_track(track_num):
                        self.speak(f"Going to track {track_num}")
                    else:
                        self.speak(f"Could not go to track {track_num}")
                return True
        
        # Play playlist
        if text.startswith("play playlist ") or text.startswith("play smartlist ") or "from playlist" in text or "from smartlist" in text:
            query = text.replace("play playlist ", "").replace("play smartlist ", "")
            query = query.replace("from playlist ", "").replace("from smartlist ", "").strip()
            
            shuffle = "random" in text or "shuffle" in text
            
            if query:
                if hasattr(self.player, 'play_playlist'):
                    result = self.player.play_playlist(query, shuffle=shuffle)
                    if result and isinstance(result, tuple):
                        status, message, context = result
                        if status == 1 and context:
                            self.selection_handler.set_items(context, "Option")
                            self.selection_handler.speak_options()
                else:
                    self.speak(f"Playing playlist {query}")
                    if hasattr(self.player, 'play_doctor'):
                        self.player.play_doctor(query)
            return True
        
        # Play artist
        if text.startswith("play artist") or text.startswith("find artist") or text.startswith("search for artist"):
            query = text.replace("play artist ", "").replace("find artist ", "").replace("search for artist ", "").strip()
            
            if query:
                self.speak(f"Searching for {query}")
                
                albums = []
                if hasattr(self.player, 'get_artist_albums'):
                    albums = self.player.get_artist_albums(query)
                
                if len(albums) > 1:
                    self.selection_handler.set_items(albums, "Artist")
                    self.selection_handler.speak_options()
                elif len(albums) == 1:
                    self.player.play_album(albums[0])
                else:
                    is_explicit_artist = text.startswith("play artist")
                    if is_explicit_artist:
                        self.player.play_artist(query)
                    else:
                         result = self.player.play_any(query)
                         if result and isinstance(result, list):
                            if len(result) == 0:
                                self.speak(f"Sorry, I couldn't find anything for {query}.")
                                return True
                            self.selection_handler.set_items(result, "Track")
                            self.selection_handler.speak_options()
                         elif not result:
                            self.speak(f"Sorry, I couldn't find anything for {query}.")
            return True
        
        # Play album
        if text.startswith("play album") or text.startswith("find album") or text.startswith("search for album"):
            query = text.replace("play album ", "").replace("find album ", "").replace("search for album ", "").strip()
            
            if query:
                result = self.player.play_any(query)
                if result and isinstance(result, tuple):
                    status, message, context = result
                    if status == 1 and context:
                        self.selection_handler.set_items(context, "Option")
                        self.selection_handler.speak_options()
                elif result and isinstance(result, list):
                    self.selection_handler.set_items(result, "Track")
                    self.selection_handler.speak_options()
            else:
                self.speak("Please say what to search for.")
            return True
        
        # Search for
        if text.startswith("search for "):
            query = text.replace("search for ", "").strip()
            
            if query:
                result = self.player.play_any(query)
                if result and isinstance(result, tuple):
                    status, message, context = result
                    if status == 1 and context:
                        self.selection_handler.set_items(context, "Option")
                        self.selection_handler.speak_options()
                elif result and isinstance(result, list):
                    self.selection_handler.set_items(result, "Track")
                    self.selection_handler.speak_options()
            else:
                self.speak("Please say what to search for.")
            return True
        
        # List albums by artist
        if text.startswith("list albums by ") or text.startswith("show albums by "):
            artist = text.replace("list albums by ", "").replace("show albums by ", "").strip()
            if artist and hasattr(self.player, 'get_artist_albums'):
                albums = self.player.get_artist_albums(artist)
                if albums:
                    self.speak(f"Albums by {artist}")
                    for album in albums:
                        self.speak(album)
            return True
        
        # Play whatever → random smartlist
        if text in ["play whatever", "whatever"]:
            if hasattr(self.player, 'play_random_smartlist'):
                self.player.play_random_smartlist()
            elif hasattr(self.player, 'play_random'):
                self.player.play_random()
            else:
                # Fallback: just play/resume
                self.speak("Playing random music.")
                self.player.play_pause()
            return True
        
        # Generic play command
        if text.startswith("play "):
            query = text.replace("play ", "").strip()
            
            # Check for "random" keyword
            if "play random" in text:
                genre_or_artist = query.replace("random ", "").strip()
                if genre_or_artist:
                    if hasattr(self.player, 'play_random_genre'):
                        self.player.play_random_genre(genre_or_artist)
                    elif hasattr(self.player, 'play_random'):
                        # Fallback for players without genre support (like MPRIS)
                        self.speak(f"Genre selection not supported. Playing random music.")
                        self.player.play_random()
                    else:
                        self.speak(f"Playing random {genre_or_artist} music.")
                        self.player.play_any("random")
                else:
                    if hasattr(self.player, 'play_random'):
                        self.player.play_random()
                    else:
                        self.player.play_any("random")
                return True
            
            if query:
                result = self.player.play_any(query)
                if result and isinstance(result, tuple):
                    status, message, context = result
                    if status == 1 and context:
                        self.selection_handler.set_items(context, "Option")
                        self.selection_handler.speak_options()
                elif result and isinstance(result, list):
                    self.selection_handler.set_items(result, "Track")
                    self.selection_handler.speak_options()
            else:
                self.player.play_pause()
            return True
        
        return False
    
    def set_reload_player_callback(self, callback):
        """Set callback for reloading player (used for player switching)."""
        self._reload_player = callback
