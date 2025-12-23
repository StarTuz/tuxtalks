"""Selection Handler

Manages selection lists and pagination for the voice assistant.
Handles user selection from multi-result searches with voice commands.
"""

import re
from typing import List, Tuple, Callable, Optional, Any


class SelectionHandler:
    """Handles selection lists, pagination, and user selection commands."""
    
    ITEMS_PER_PAGE = 5
    
    def __init__(self, player, speak_func: Callable, state_machine, text_normalizer):
        """
        Initialize selection handler.
        
        Args:
            player: Media player instance
            speak_func: Function to queue speech (e.g., assistant.speak)
            state_machine: AssistantStateMachine instance
            text_normalizer: TextNormalizer instance for number parsing
        """
        self.player = player
        self.speak = speak_func
        self.state_machine = state_machine
        self.text_normalizer = text_normalizer
        self._reload_player_callback = None  # For player switching
        
        # Selection state
        self.context_items: List = []
        self.selection_page = 0
        self.current_field = "Artist"
    
    def set_items(self, items: List, field: str = "Artist") -> None:
        """
        Set items for selection and transition to selection state.
        
        Args:
            items: List of items (strings or tuples)
            field: Field type being selected (Artist, Album, Track, etc.)
        """
        self.context_items = items
        self.selection_page = 0
        self.current_field = field
        
        # Try IPC first (if runtime menu is available)
        if self._try_ipc_selection():
            return  # Selection handled via GUI, done
        
        # Fallback: Transition to waiting selection state (voice/console)
        self.state_machine.transition_to(self.state_machine.STATE_WAITING_SELECTION)
    
    def _try_ipc_selection(self) -> bool:
        """
        Try to send selection to tuxtalks-menu via IPC.
        
        Returns:
            True if handled via IPC, False if fallback needed
        """
        try:
            import ipc_client
            
            # Check if menu is running
            if not ipc_client.is_menu_running():
                return False
            
            # Format items for display (with hierarchical structure)
            formatted_items = []
            for item in self.context_items:
                item_dict = {}
                
                if isinstance(item, tuple):
                    title = item[0]
                    item_value = item[1]
                    item_type = item[2] if len(item) > 2 else None
                    
                    # Clean up title
                    import re
                    title = re.sub(r"vlc-record-\d{4}-\d{2}-\d{2}-\d+h\d+m\d+s-", "", title)
                    title = re.sub(r"\.[a-zA-Z0-9]{3,4}$", "", title)
                    title = title.replace("_", " ")
                    
                    # Add type prefix if not present
                    if item_type == "album" and not title.startswith("Album:"):
                        title = f"Album: {title}"
                    elif item_type == "playlist" and not title.startswith("Playlist:"):
                        title = f"Playlist: {title}"
                    
                    item_dict['text'] = title
                    item_dict['type'] = item_type
                    
                    # Pre-fetch tracks for albums/playlists
                    if item_type in ["album", "playlist"] and hasattr(self.player, f'get_{item_type}_tracks'):
                        print(f"[Selection] Pre-fetching tracks for {item_type}: {item_value}")
                        try:
                            if item_type == "album":
                                tracks = self.player.get_album_tracks(item_value)
                            else:  # playlist
                                tracks = self.player.get_playlist_tracks(item_value)
                            
                            if tracks:
                                # Format tracks as children
                                children = []
                                for track_data in tracks:
                                    if item_type == "album":
                                        track_title, track_key, track_num = track_data
                                    else:  # playlist
                                        track_title, track_key = track_data
                                        track_num = None
                                    
                                    children.append({
                                        'text': track_title,
                                        'type': 'track',
                                        'key': track_key
                                    })
                                
                                item_dict['children'] = children
                                print(f"[Selection] Added {len(children)} tracks to {item_type}")
                        except Exception as e:
                            print(f"[Selection] Error fetching tracks: {e}")
                else:
                    # Simple string item
                    title = str(item)
                    title = title.replace("_", " ")
                    item_dict['text'] = title
                    item_dict['type'] = 'simple'
                
                formatted_items.append(item_dict)
            
            # Send to menu
            print(f"[Selection] Sending to GUI menu: {len(formatted_items)} items (hierarchical)")
            print(f"[Selection] DEBUG: About to call send_selection_request...")
            response = ipc_client.send_selection_request(
                title=f"Select {self.current_field}",
                items=formatted_items,
                page=1
            )
            print(f"[Selection] DEBUG: Response received: {response}")
            
            if response and not response['cancelled']:
                # User selected via GUI
                idx = response['index']
                child_idx = response.get('child_index', None)
                
                if child_idx is not None:
                    # User selected a child (track)
                    print(f"[Selection] GUI selection: parent={idx}, child={child_idx}")
                    # Handle track selection from album/playlist
                    parent_item = self.context_items[idx]
                    if isinstance(parent_item, tuple) and len(parent_item) > 2:
                        item_type = parent_item[2]
                        item_value = parent_item[1]
                        
                        # Get the track key from pre-fetched data
                        if item_type == "album" and hasattr(self.player, 'get_album_tracks'):
                            tracks = self.player.get_album_tracks(item_value)
                            if child_idx < len(tracks):
                                track_title, track_key, track_num = tracks[child_idx]
                                # Play this track
                                print(f"🎵 Playing track: {track_title}")
                                if hasattr(self.player, 'play_files'):
                                    self.player.play_files([track_key])
                        elif item_type == "playlist" and hasattr(self.player, 'get_playlist_tracks'):
                            tracks = self.player.get_playlist_tracks(item_value)
                            if child_idx < len(tracks):
                                track_title, track_key = tracks[child_idx]
                                # Play this track
                                print(f"🎵 Playing track: {track_title}")
                                if hasattr(self.player, 'play_files'):
                                    self.player.play_files([track_key])
                    
                    self.clear()
                else:
                    # User selected a parent item
                    print(f"[Selection] GUI selection: {idx}")
                    self._execute_selection(idx, "")
                
                return True
            else:
                # User cancelled or timed out in GUI
                if response and response.get('cancelled'):
                    # Check if it was explicit cancel or timeout
                    if response.get('explicit_cancel'):
                        print("[Selection] GUI cancelled by user")
                        self.speak("Selection cancelled.")
                    else:
                        print("[Selection] GUI timed out")
                        self.speak("Selection timed out. You can re-issue the command.")
                else:
                    print("[Selection] GUI connection lost or error")
                    return False  # Return False to trigger voice fallback
                
                self.clear()
                return True
                
        except ImportError:
            # IPC not available
            return False
        except Exception as e:
            print(f"[Selection] IPC error: {e}, falling back to voice")
            return False
    
    def speak_options(self) -> None:
        """Speak the current page of selection options."""
        if not self.context_items:
            return
        
        start_idx = self.selection_page * self.ITEMS_PER_PAGE
        end_idx = min(start_idx + self.ITEMS_PER_PAGE, len(self.context_items))
        
        current_items = self.context_items[start_idx:end_idx]
        
        # Handle tuples (Title, Path) for tracks, or strings for albums
        spoken_items = []
        for i, item in enumerate(current_items):
            if isinstance(item, tuple):
                # item is (Title, Path) or (Title, Path, MediaType)
                title = item[0]
                if len(item) > 2 and item[2] == "album":
                    title = f"Album: {title}"
            else:
                title = item  # String
            
            # Remove vlc-record prefix
            # Pattern: vlc-record-YYYY-MM-DD-HHhMMmSSs-
            title = re.sub(r"vlc-record-\d{4}-\d{2}-\d{2}-\d+h\d+m\d+s-", "", title)
            
            # Remove file extension
            title = re.sub(r"\.[a-zA-Z0-9]{3,4}$", "", title)
            
            # Replace underscores with spaces
            title = title.replace("_", " ")
            
            spoken_items.append(f"{start_idx + i + 1}. {title}")
        
        msg = f"Found {len(self.context_items)} matches. "
        if self.selection_page > 0:
            msg = f"Page {self.selection_page + 1}. " + msg
        elif len(self.context_items) > self.ITEMS_PER_PAGE:
            # Announce "Page 1" if there are multiple pages
            msg = "Page 1. " + msg
        
        msg += ", ".join(spoken_items)
        
        if end_idx < len(self.context_items):
            msg += ". Say 'next' for more."
        
        self.speak(msg)
    
    def handle_selection_command(self, text: str) -> bool:
        """
        Handle user selection from a list.
        
        Args:
            text: User's spoken command
            
        Returns:
            True if command was handled, False otherwise
        """
        text = text.lower().strip()
        
        # Pagination commands
        if "next" in text or "more" in text:
            max_page = (len(self.context_items) - 1) // self.ITEMS_PER_PAGE
            if self.selection_page < max_page:
                self.selection_page += 1
                self.speak_options()
            else:
                self.speak("No more items.")
            return True
        
        if "previous" in text or "back" in text:
            if self.selection_page > 0:
                self.selection_page -= 1
                self.speak_options()
            else:
                self.speak("This is the first page.")
            return True
        
        if "cancel" in text or "stop" in text or "quit" in text or "exit" in text:
            self.speak("Cancelled.")
            self.clear()
            return True
        
        # Strip common prefixes for selection
        text = text.lower()
        for prefix in ["number ", "play number ", "option ", "play option ", "choice ", "play "]:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break
        
        # Try to parse a number
        selection_index = self.text_normalizer.parse_number(text)
        
        if selection_index is not None:
            # Adjust for 0-based index (user says "1", we want index 0)
            idx = selection_index - 1
            
            if idx >= 0 and idx < len(self.context_items):
                self._execute_selection(idx, text)
                return True
            else:
                self.speak(f"Please choose a number between 1 and {len(self.context_items)}.")
                return True
        
        self.speak("Please say a number, 'next', or 'cancel'.")
        return True
    
    def _execute_selection(self, idx: int, original_text: str) -> None:
        """
        Execute the selected item.
        
        Args:
            idx: Index of selected item
            original_text: Original user command (for shuffle detection)
        """
        selected_item = self.context_items[idx]
        
        if isinstance(selected_item, tuple):
            # (Title, Path/ID, Type)
            if len(selected_item) > 2:
                type_ = selected_item[2]
                
                # Handle player selection
                if type_ == "player":
                    import logging
                    logger = logging.getLogger("tuxtalks-cli")
                    
                    player_name = selected_item[0]
                    player_id = selected_item[1]
                    logger.info(f"Player selection: {player_name} ({player_id})")
                    print(f"🔄 Switching to player: {player_name} ({player_id})")
                    
                    # Import and use reload callback
                    from config import cfg
                    logger.debug(f"Has reload callback: {hasattr(self, '_reload_player_callback')}")
                    if hasattr(self, '_reload_player_callback'):
                        logger.info(f"Calling reload_player with: {player_id}")
                        self._reload_player_callback(player_id)
                        cfg.set("PLAYER", player_id)
                        cfg.save()
                        logger.info(f"Config saved: PLAYER={player_id}")
                        self.speak(f"Switched to {player_name}")
                    else:
                        logger.error("reload_player_callback not set!")
                        self.speak("Player switching not available in this mode")
                    
                    # Always clear menu for player switching (ignore "Keep list open")
                    self.clear()
                    
                    # Also send explicit clear to runtime menu if it was used
                    try:
                        import ipc_client
                        if ipc_client.is_menu_running():
                            # Menu will clear on its own after selection, no extra IPC needed
                            pass
                    except:
                        pass
                    
                    return
                
                # Check for shuffle request in the selection command
                shuffle = False
                if "random" in original_text or "shuffle" in original_text:
                    shuffle = True
                
                # Check if we're using hierarchical GUI mode or CLI drill-down mode
                # In hierarchical mode (menu running), tracks are already children - play parent directly
                # In CLI mode (no menu), we need to drill down to show tracks for voice selection
                using_hierarchical_gui = False
                try:
                    import ipc_client
                    # If menu is running, we sent hierarchical data, so don't drill down
                    if ipc_client.is_menu_running():
                        using_hierarchical_gui = True
                except:
                    pass
                
                # **HIERARCHICAL GUI MODE**: Albums/playlists already have child tracks
                # Selecting parent = play whole album/playlist
                if using_hierarchical_gui:
                    if type_ == "album":
                        print(f"💿 Playing album (hierarchical mode): {selected_item[1]}")
                        self.player.play_album(selected_item[1])
                        self.clear()
                        return
                    elif type_ == "playlist":
                        print(f"📜 Playing playlist (hierarchical mode): {selected_item[1]}")
                        if hasattr(self.player, 'play_playlist'):
                            self.player.play_playlist(selected_item[1], shuffle=shuffle)
                        self.clear()
                        return
                    elif type_ == "artist_mix":
                        artist_name = selected_item[1]
                        print(f"👨‍🎤 Playing artist mix: {artist_name}")
                        print(f"DEBUG: Full selected_item = {selected_item}")
                        self.player.play_artist(artist_name)
                        self.clear()
                        return
                
                # **CLI/VOICE MODE**: Play the album/playlist directly (same as GUI parent selection)
                else:
                    if type_ == "album":
                        print(f"💿 Playing album: {selected_item[1]}")
                        self.player.play_album(selected_item[1])
                            
                    elif type_ == "playlist":
                        print(f"📜 Playing playlist: {selected_item[1]} (Shuffle: {shuffle})")
                        if hasattr(self.player, 'play_playlist'):
                            self.player.play_playlist(selected_item[1], shuffle=shuffle)
                                
                    elif type_ == "artist_mix":
                        print(f"👨‍🎤 Playing artist mix: {selected_item[1]}")
                        self.player.play_artist(selected_item[1])
                
                # Common: Handle track selection (works for both modes)
                if type_ not in ["album", "playlist", "artist_mix"]:
                    # It's a track - play this track and subsequent tracks
                    remaining_items = self.context_items[idx:]
                    
                    # Filter out non-tracks
                    paths = [item[1] for item in remaining_items 
                            if isinstance(item, tuple) and 
                            (len(item) < 3 or item[2] not in ["album", "playlist", "artist_mix"])]
                    
                    if hasattr(self.player, 'play_files'):
                        self.player.play_files(paths)
                    elif hasattr(self.player, 'play_file'):
                        self.player.play_file(paths[0])
                    else:
                        self.speak("This player cannot play specific files.")
        else:
            # Item is Album Name (string) - Legacy fallback
            self.player.play_album(selected_item)
        
        self.clear()
    
    def clear(self) -> None:
        """Clear selection state and return to listening mode."""
        self.state_machine.transition_to(self.state_machine.STATE_LISTENING)
        self.context_items = []
        self.current_field = "Artist"  # Reset default
    
    def has_items(self) -> bool:
        """Check if there are items in the selection list."""
        return len(self.context_items) > 0
