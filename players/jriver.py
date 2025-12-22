import requests
import xml.etree.ElementTree as ET
import urllib.parse
import time
import difflib
from player_interface import MediaPlayer

class JRiverPlayer(MediaPlayer):
    def __init__(self, config, speak_func=print):
        super().__init__(config, speak_func)
        self.ip = config.get("JRIVER_IP")
        self.port = config.get("JRIVER_PORT")
        self.access_key = config.get("ACCESS_KEY")
        self.base_url = f"http://{self.ip}:{self.port}/MCWS/v1/"
        self.cache = {}

    def health_check(self):
        """Checks if JRiver is running and reachable."""
        print("Checking JRiver connection...")
        try:
            requests.get(f"http://{self.ip}:{self.port}/MCWS/v1/Alive", timeout=2)
            print("✅ JRiver is running.")
            return True
        except requests.exceptions.ConnectionError:
            print("⚠️  JRiver is not running. Attempting to launch...")
            try:
                import subprocess
                subprocess.Popen(["mediacenter35"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("⏳ Waiting for JRiver to start (15s)...")
                time.sleep(15)
                return True
            except FileNotFoundError:
                print("❌ Could not launch 'mediacenter35'. Please start JRiver manually.")
                return False


    def send_mcws_command(self, command_path, extra_params="", return_xml=False):
        """Sends a command to JRiver's MCWS API."""
        url = f"{self.base_url}{command_path}?Zone=-1&ZoneType=ID&Key={self.access_key}"
        if extra_params:
            url += "&" + extra_params
            
        # Retry logic for connection robustness
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status() 
                # print(f"✅ Sent MCWS command: {command_path}")
                
                if return_xml:
                    return response.text
                return response
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait 1 second before retrying
                else:
                    print(f"❌ Error sending command to JRiver: {e}")
                    self.announce_error("I couldn't reach JRiver.")
                    return None
            return None

    def get_all_values(self, field):
        """Fetches ALL values for a field from JRiver and caches them."""
        if field in self.cache:
            return self.cache[field]
            
        print(f"📥 Fetching all {field}s from library...")
        params = f"Field={field}&Limit=10000"
        xml_response = self.send_mcws_command("Library/Values", extra_params=params, return_xml=True)
        
        values = []
        if xml_response:
            try:
                root = ET.fromstring(xml_response)
                values = [item.text for item in root.findall('Item') if item.text]
                self.cache[field] = values
                print(f"   -> Cached {len(values)} {field}s.")
            except ET.ParseError:
                print("❌ Error parsing XML.")
        
        return values

    def play_pause(self):
        self.send_mcws_command("Playback/Pause")

    def stop(self):
        self.send_mcws_command("Playback/Stop")

    def next_track(self):
        self.send_mcws_command("Playback/Next")
        time.sleep(0.5)
        self.what_is_playing_silent()

    def previous_track(self):
        self.send_mcws_command("Playback/Previous")
        time.sleep(0.5)
        self.what_is_playing_silent()

    def volume_up(self):
        self.send_mcws_command("Playback/Volume", extra_params="Level=600")

    def volume_down(self):
        self.send_mcws_command("Playback/Volume", extra_params="Level=400")

    def play_genre(self, genre):
        # This logic was in play_random_genre in original
        genres = self.get_all_values("Genre")
        
        # Fuzzy match
        best_match = None
        highest_score = 0.0
        
        for g in genres:
            score = difflib.SequenceMatcher(None, genre.lower(), g.lower()).ratio()
            if score > highest_score:
                highest_score = score
                best_match = g
        
        if highest_score > 0.6:
            print(f"🎯 Matched Genre: '{best_match}' (Score: {highest_score:.2f})")
            self.speak(f"Playing random {best_match} music.")
            
            # Use PlayDoctor with Genre seed
            encoded_genre = urllib.parse.quote(best_match)
            params = f"Seed=[Genre]=[{encoded_genre}]&Action=Play"
            self.send_mcws_command("Playback/PlayDoctor", extra_params=params)
            
            time.sleep(1)
            self.what_is_playing_silent()
        else:
            self.speak(f"I couldn't find a genre named {genre}.")

    def normalize_text(self, text):
        """Normalizes spoken text to match library conventions."""
        text = text.lower()
        replacements = {
            "number one": "no. 1", "number two": "no. 2", "number three": "no. 3",
            "number four": "no. 4", "number five": "no. 5", "number six": "no. 6",
            "number seven": "no. 7", "number eight": "no. 8", "number nine": "no. 9",
            "number 1": "no. 1", "number 2": "no. 2", "number 3": "no. 3",
            "number 4": "no. 4", "number 5": "no. 5", "number 6": "no. 6",
            "number 7": "no. 7", "number 8": "no. 8", "number 9": "no. 9",
            " op ": " op. ", " opus ": " op. ",
            "simply": "symphony" 
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text


    def find_matches(self, search_term, all_values, n=5):
        """Helper to find matches. Returns list of (value, score)."""
        search_lower = search_term.lower()
        search_term = self.normalize_text(search_term)
        
        matches = []
        
        # 1. Exact Match
        for v in all_values:
            if v.lower() == search_term:
                matches.append((v, 1.0))
        
        # 2. Fuzzy Match
        close = difflib.get_close_matches(search_term, all_values, n=n, cutoff=0.6)
        for m in close:
            score = difflib.SequenceMatcher(None, search_term, m.lower()).ratio()
            # Avoid duplicates if exact matched already
            if not any(x[0] == m for x in matches):
                matches.append((m, score))
                
        # Sort by score desc
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def find_best_match(self, search_term, field="Artist"):
        """Wrapper for legacy calls. Returns (best_val, score)."""
        all_values = self.get_all_values(field)
        if not all_values: return None, 0
        
        candidates = self.find_matches(search_term, all_values, n=5)
        if candidates:
            # Debug log
            print(f"   [Debug] Matches for '{search_term}' in {field}:")
            for m, s in candidates:
                print(f"      - {m} (Score: {s:.2f})")
            return candidates[0]
        return None, 0

    def play_smartlist(self, name):
        """Plays a smartlist (wrapper for play_playlist with specific TTS)."""
        self.play_playlist(name, item_type="smartlist")

    def play_playlist(self, playlist_name, shuffle=False, item_type="playlist", announce=True):
        """Plays a playlist/smartlist by name using fuzzy matching.
           item_type: 'playlist' or 'smartlist' for TTS customization.
           announce: Whether to announce the search (False when called from play_any).
        """
        if announce:
            self.speak(f"Searching for {item_type} {playlist_name}")
        
        # Fetch all playlists
        xml_response = self.send_mcws_command("Playlists/List", return_xml=True)
        if not xml_response:
            self.speak(f"I couldn't fetch the {item_type}s.")
            return

        try:
            root = ET.fromstring(xml_response)
            best_match = None
            best_score = 0
            best_id = None
            
            for item in root.findall('Item'):
                p_name = ""
                p_id = ""
                for field in item.findall('Field'):
                    if field.get('Name') == 'Name':
                        p_name = field.text
                    elif field.get('Name') == 'ID':
                        p_id = field.text
                
                if p_name:
                    score = difflib.SequenceMatcher(None, playlist_name.lower(), p_name.lower()).ratio()
                    if score > 0.6:
                         pass
                    
                    if score > best_score:
                        best_score = score
                        best_match = p_name
                        best_id = p_id
            
            if best_score > 0.6:
                if shuffle:
                    if announce:
                        self.speak(f"Playing random songs from {best_match}")
                    self.send_mcws_command("Playback/PlayPlaylist", extra_params=f"Playlist={best_id}&PlaylistType=ID")
                    time.sleep(0.5) 
                    self.send_mcws_command("Playback/Shuffle", extra_params="Mode=reshuffle")
                else:
                    if announce:
                        self.speak(f"Playing {item_type} {best_match}")
                    self.send_mcws_command("Playback/PlayPlaylist", extra_params=f"Playlist={best_id}&PlaylistType=ID")
                
                # Poll for playback start
                max_polls = 20 if shuffle else 10
                for i in range(max_polls):
                    time.sleep(0.5)
                    xml_response = self.send_mcws_command("Playback/Info", return_xml=True)
                    if xml_response:
                        try:
                            root = ET.fromstring(xml_response)
                            state = int(root.find(".//Item[@Name='State']").text or 0)
                            if state == 2: # Playing
                                break
                        except: pass
                    
                self.what_is_playing_silent()
            else:
                self.speak(f"I couldn't find a {item_type} named {playlist_name}.")
                
        except Exception as e:
            print(f"Error parsing playlists: {e}")
            self.speak(f"I couldn't find that {item_type}.")

    def play_album(self, album):
        if album.startswith("Playlist: "):
            pl_name = album[10:] # Strip "Playlist: "
            self.play_playlist(pl_name, shuffle=True)
            return
            
        self.speak(f"Playing {album}")
        self.play_precise_album(album)

    def play_any(self, query):
        self.speak(f"Searching for {query}")
        normalized_query = self.normalize_text(query)
        
        # Check for specific work keywords
        specific_work_keywords = ["symphony", "concerto", "sonata", "quartet", "quintet", 
                                   "no.", "op.", "movement", "adagio", "allegro", "andante"]
        is_specific_work = any(keyword in normalized_query for keyword in specific_work_keywords)
        
        # Collect all candidates
        # Structure: (Display, Value, Type, Score)
        candidates = []
        
        # Artist
        for m, s in self.find_matches(query, self.get_all_values("Artist")):
            candidates.append((f"Artist: {m}", m, "artist_mix", s))
            if s > 0.8:
                # Contextual Album Search
                # Find albums where this artist appears (even if not in album title)
                context_albums = self.get_artist_albums(m)
                for alb in context_albums:
                    # Avoid duplicates if already found directly
                    if not any(c[1] == alb and c[2] == "album" for c in candidates):
                         candidates.append((f"Album: {alb} (by {m})", alb, "album", s * 0.98))
            
        # Composer
        for m, s in self.find_matches(query, self.get_all_values("Composer")):
            candidates.append((f"Composer: {m}", m, "artist_mix", s))
            if s > 0.8:
                # Contextual Album Search for Composer
                context_albums = self.get_artist_albums(m)
                for alb in context_albums:
                    if not any(c[1] == alb and c[2] == "album" for c in candidates):
                         candidates.append((f"Album: {alb} (by {m})", alb, "album", s * 0.98))
            
        # Album
        for m, s in self.find_matches(query, self.get_all_values("Album")):
            candidates.append((f"Album: {m}", m, "album", s))
            
        # Playlist
        try:
             pl_xml = self.send_mcws_command("Playlists/List", return_xml=True)
             if pl_xml:
                 root = ET.fromstring(pl_xml)
                 pl_names = []
                 for item in root.findall('Item'):
                     for field in item.findall('Field'):
                         if field.get('Name') == 'Name':
                             pl_names.append(field.text)
                 
                 for m, s in self.find_matches(query, pl_names):
                     candidates.append((f"Playlist: {m}", m, "playlist", s))
        except: pass

        # Sort all
        candidates.sort(key=lambda x: x[3], reverse=True)
        
        # Filter low scores
        candidates = [c for c in candidates if c[3] > 0.6]
        
        if not candidates:
            # Fallback if no specific match exceeded threshold
            success = self.play_doctor(normalized_query)
            if success:
                self.speak(f"Playing {normalized_query}")
                return (0, "Playing generic search", None)
            else:
                self.speak(f"Sorry, I couldn't find anything for {normalized_query}.")
                return (0, "Nothing found", None)
            
        # Decision Logic
        top = candidates[0]
        
        # If clear winner
        # (Top > 0.9 AND (Only one OR Top is significantly better than second))
        if top[3] > 0.9 and (len(candidates) == 1 or (top[3] - candidates[1][3] > 0.15)):
            print(f"🎯 Auto-playing Best Match: {top[0]} ({top[3]:.2f})")
            if top[2] == "album": self.play_album(top[1])
            elif top[2] == "artist_mix": self.play_artist(top[1])
            elif top[2] == "playlist": self.play_playlist(top[1], shuffle=False, announce=False)
            return (0, f"Playing {top[0]}", None)
            
        # Ambiguity -> Return List
        selection_list = [(c[0], c[1], c[2]) for c in candidates[:10]] # Limit to 10
        
        return (1, "Select option", selection_list)
    
    def play_random_smartlist(self):
        """Plays the default random smartlist, or falls back to random play."""
        # Try common smartlist names
        smartlist_candidates = [
            "Audio - 100 random songs",
            "Audio - Random",
            "Random 100",
            "Random Songs"
        ]
        
        # Get all playlists to find the best match
        xml_response = self.send_mcws_command("Playlists/List", return_xml=True)
        
        if xml_response:
            try:
                root = ET.fromstring(xml_response)
                pl_names = []
                for item in root.findall('Item'):
                    for field in item.findall('Field'):
                        if field.get('Name') == 'Name':
                            pl_names.append(field.text)
                
                # Try to find a random smartlist
                for candidate in smartlist_candidates:
                    if candidate in pl_names:
                        print(f"✅ Found smartlist: {candidate}")
                        self.speak("Playing random music.")
                        self.play_playlist(candidate, shuffle=False, item_type="smartlist", announce=False)
                        return
                
                # No exact match, try fuzzy
                close = difflib.get_close_matches("random", pl_names, n=1, cutoff=0.5)
                if close:
                    print(f"✅ Using closest match: {close[0]}")
                    self.speak("Playing random music.")
                    self.play_playlist(close[0], shuffle=False, item_type="smartlist", announce=False)
                    return
                    
            except Exception as e:
                print(f"Error finding random smartlist: {e}")
        
        # Fallback: use PlayDoctor with no seed for random
        print("⚠️  No random smartlist found, using PlayDoctor fallback")
        self.speak("Playing random music.")
        self.play_doctor("", show_track=True)

    def play_random_genre(self, genre):
        """Calls play_genre (original method name was play_random_genre)."""
        self.play_genre(genre)
    
    def get_all_artists(self, limit=50):
        """Returns a list of all artists in the library for Ollama library context.
        
        Args:
            limit: Maximum number of artists to return (default: 50)
            
        Returns:
            List of artist names (strings)
        """
        artists = self.get_all_values("Artist")
        return artists[:limit] if artists else []

    def play_random(self):
        """Standard interface method for playing random music."""
        self.play_random_smartlist()
    
    def get_album_tracks(self, album_name):
        """
        Returns a list of tracks for the given album.
        
        Args:
            album_name: Name of the album
            
        Returns:
            List of tuples: (track_title, track_key, track_number)
        """
        # Use same query logic as play_precise_album
        queries_to_try = [f"[Album]=[{album_name}]"]
        
        xml_response = None
        for i, q in enumerate(queries_to_try):
            encoded_query = urllib.parse.quote(q)
            temp_response = self.send_mcws_command("Files/Search", extra_params=f"Query={encoded_query}", return_xml=True)
            if temp_response:
                try:
                    root = ET.fromstring(temp_response)
                    items = root.findall('Item')
                    if len(items) > 0:
                        xml_response = temp_response
                        break
                except:
                    pass
        
        if not xml_response:
            return []
            
        try:
            root = ET.fromstring(xml_response)
            tracks = []
            
            for item in root.findall('Item'):
                track_num = None
                key = None
                title = None
                
                for field in item.findall('Field'):
                    field_name = field.get('Name')
                    if field_name == 'Track #':
                        try:
                            track_num = int(field.text)
                        except:
                            track_num = 9999
                    elif field_name == 'Key':
                        key = field.text
                    elif field_name == 'Name':
                        title = field.text
                
                if key and title:
                    if track_num is None:
                        track_num = 9999
                    tracks.append((title, key, track_num))
            
            # Sort by track number
            tracks.sort(key=lambda x: x[2])
            return tracks
            
        except Exception as e:
            print(f"Error in get_album_tracks: {e}")
            return []
    
    def get_playlist_tracks(self, playlist_name):
        """
        Returns a list of tracks for the given playlist.
        
        Args:
            playlist_name: Name of the playlist
            
        Returns:
            List of tuples: (track_title, track_key)
        """
        # Find playlist ID first
        xml_response = self.send_mcws_command("Playlists/List", return_xml=True)
        if not xml_response:
            return []
        
        try:
            root = ET.fromstring(xml_response)
            playlist_id = None
            
            for item in root.findall('Item'):
                p_name = ""
                p_id = ""
                for field in item.findall('Field'):
                    if field.get('Name') == 'Name':
                        p_name = field.text
                    elif field.get('Name') == 'ID':
                        p_id = field.text
                
                if p_name and p_name.lower() == playlist_name.lower():
                    playlist_id = p_id
                    break
            
            if not playlist_id:
                # Try fuzzy match
                best_score = 0
                for item in root.findall('Item'):
                    p_name = ""
                    p_id = ""
                    for field in item.findall('Field'):
                        if field.get('Name') == 'Name':
                            p_name = field.text
                        elif field.get('Name') == 'ID':
                            p_id = field.text
                    
                    if p_name:
                        score = difflib.SequenceMatcher(None, playlist_name.lower(), p_name.lower()).ratio()
                        if score > best_score and score > 0.6:
                            best_score = score
                            playlist_id = p_id
            
            if not playlist_id:
                return []
            
            # Get playlist contents
            pl_response = self.send_mcws_command("Playlist/Files", extra_params=f"Playlist={playlist_id}&PlaylistType=ID", return_xml=True)
            if not pl_response:
                return []
            
            pl_root = ET.fromstring(pl_response)
            tracks = []
            
            for item in pl_root.findall('Item'):
                title = None
                key = None
                
                for field in item.findall('Field'):
                    field_name = field.get('Name')
                    if field_name == 'Name':
                        title = field.text
                    elif field_name == 'Key':
                        key = field.text
                
                if title and key:
                    tracks.append((title, key))
            
            return tracks
            
        except Exception as e:
            print(f"Error in get_playlist_tracks: {e}")
            return []

    def play_artist(self, artist):
        # This is a simplified version, original had complex search logic
        # For now, we'll implement a basic PlayDoctor for artist
        self.speak(f"Playing music by {artist}")
        encoded_artist = urllib.parse.quote(artist)
        params = f"Seed=[Artist]=[{encoded_artist}]&Action=Play"
        self.send_mcws_command("Playback/PlayDoctor", extra_params=params)
        time.sleep(1)
        self.what_is_playing_silent()

    def get_artist_albums(self, artist):
        """Returns a list of albums for the given artist."""
        tokens = artist.split()
        if not tokens:
            return []
            
        # 1. Broad MCWS Search
        # We want to find files where ANY of the tokens appear in Artist, Album, or Composer.
        # MCWS Search Language supports simple keyword search which covers multiple fields.
        # If we just send the tokens joined by space, it usually does an AND search across default fields.
        # But to be safe and broad (like we did for Elisa), let's just search for the raw string
        # and let JRiver return candidates, then we filter precisely.
        
        # However, "Gustav Holst" might not match "Holst, Gustav" in a simple phrase search if JRiver treats it as a phrase.
        # But usually JRiver search is tokenized by default.
        # Let's try searching for just the tokens joined by space.
        
        encoded_query = urllib.parse.quote(artist)
        
        # We request Album, Artist, Composer, and Name (Title) to check against
        xml_response = self.send_mcws_command("Files/Search", extra_params=f"Query={encoded_query}&Fields=Album,Artist,Composer,Name", return_xml=True)
        
        albums = set()
        if xml_response:
            try:
                root = ET.fromstring(xml_response)
                
                import re
                
                for item in root.findall('Item'):
                    item_album = None
                    full_text_parts = []
                    
                    for field in item.findall('Field'):
                        name = field.get('Name')
                        val = field.text or ""
                        
                        if name == 'Album':
                            item_album = val
                        
                        if name in ['Album', 'Artist', 'Composer', 'Name']:
                            full_text_parts.append(val)
                    
                    if item_album:
                        # 2. Precise Python Filtering (Regex)
                        # Combine all fields
                        full_text = " ".join(full_text_parts)
                        
                        # Check if ALL tokens are present as whole words
                        all_tokens_found = True
                        for token in tokens:
                            # Regex for whole word: \btoken\b
                            if not re.search(rf"\b{re.escape(token)}\b", full_text, re.IGNORECASE):
                                all_tokens_found = False
                                break
                        
                        if all_tokens_found:
                            albums.add(item_album)
            except Exception as e:
                print(f"Error parsing JRiver search results: {e}")
                pass
        
        return sorted(list(albums))

    def list_albums(self, artist=None):
        """Lists albums, optionally filtered by artist."""
        if artist:
            self.speak(f"Searching for albums by {artist}")
            # Use JRiver search to find albums by this artist
            # We can use the cache if available, or fetch fresh
            # For robustness, let's fetch all albums and filter? No, too slow.
            # Use Search MCWS
            encoded_query = urllib.parse.quote(f"[Artist]=[{artist}]")
            xml_response = self.send_mcws_command("Files/Search", extra_params=f"Query={encoded_query}&Fields=Album", return_xml=True)
            
            albums = set()
            if xml_response:
                try:
                    root = ET.fromstring(xml_response)
                    for item in root.findall('Item'):
                        for field in item.findall('Field'):
                            if field.get('Name') == 'Album':
                                albums.add(field.text)
                except:
                    pass
            
            if albums:
                sorted_albums = sorted(list(albums))
                count = len(sorted_albums)
                self.speak(f"I found {count} albums by {artist}.")
                
                # List first few
                display_count = min(5, count)
                for i in range(display_count):
                    print(f"   - {sorted_albums[i]}")
                    self.speak(sorted_albums[i])
                    time.sleep(0.5)
                
                if count > display_count:
                    self.speak(f"And {count - display_count} more.")
            else:
                self.speak(f"I couldn't find any albums by {artist}.")
                
        else:
            # Original list_tracks behavior (list Playing Now)
            # But the interface says list_tracks... 
            # Let's keep list_tracks as is, and this is a new method or we overload?
            # The interface doesn't have list_albums. We should add it to tuxtalks.py to call this specific method.
            pass

    # --- JRiver Specific Methods (exposed for now) ---

    def play_doctor(self, seed, show_track=True):
        """Plays using Play Doctor with a seed, forcing sequential playback.
        
        Returns:
            bool: True if tracks were found and playing, False otherwise
        """
        encoded_seed = urllib.parse.quote(seed)
        params = f"Seed={encoded_seed}&Radio=0"
        self.send_mcws_command("Playback/PlayDoctor", extra_params=params)
        
        total_tracks = 0
        if show_track:
            # Poll for up to 5 seconds for the playlist to populate
            for _ in range(10):
                time.sleep(0.5)
                # Check if playlist is ready
                xml_response = self.send_mcws_command("Playback/Info", return_xml=True)
                if xml_response:
                    try:
                        root = ET.fromstring(xml_response)
                        total_tracks = int(root.find(".//Item[@Name='PlayingNowTracks']").text or 0)
                        if total_tracks > 0:
                            break
                    except:
                        pass
            
            if total_tracks > 0:
                self.what_is_playing_silent()
        
        return total_tracks > 0

    def what_is_playing_silent(self, force_track_num=None):
        """Shows what's playing without speaking (just prints)."""
        xml_response = self.send_mcws_command("Playback/Info", return_xml=True)
        if not xml_response:
            return
            
        try:
            root = ET.fromstring(xml_response)
            info = {}
            for item in root.findall('Item'):
                info[item.get('Name')] = item.text
            
            name = info.get('Name', 'Unknown Track')
            artist = info.get('Artist', 'Unknown Artist')
            file_key = info.get('FileKey')
            position = int(info.get('PlayingNowPosition', 0)) + 1  # 1-indexed
            total = info.get('PlayingNowTracks', '?')
            
            display_pos = force_track_num if force_track_num is not None else position
            
            track_num = "?"
            if file_key and file_key != '-1':
                file_info = self.send_mcws_command("File/GetInfo", extra_params=f"File={file_key}", return_xml=True)
                if file_info:
                    try:
                        file_root = ET.fromstring(file_info)
                        for field in file_root.findall('.//Field'):
                            if field.get('Name') == 'Track #':
                                track_num = field.text
                                break
                    except:
                        pass
            
            print(f"\n🎵 Now Playing (Track {display_pos} of {total}):")
            print(f"   Album Track #: {track_num}")
            print(f"   Title: {name}")
            print(f"   Artist: {artist}\n")
            
        except Exception as e:
            print(f"Error getting track info: {e}")

    def what_is_playing(self):
        """Announces the currently playing track with track number info."""
        xml_response = self.send_mcws_command("Playback/Info", return_xml=True)
        if not xml_response:
            return
            
        try:
            root = ET.fromstring(xml_response)
            info = {}
            for item in root.findall('Item'):
                info[item.get('Name')] = item.text
            
            name = info.get('Name', 'Unknown Track')
            artist = info.get('Artist', 'Unknown Artist')
            file_key = info.get('FileKey')
            
            response = f"Playing {name} by {artist}"
            
            if file_key and file_key != '-1':
                file_info = self.send_mcws_command("File/GetInfo", extra_params=f"File={file_key}", return_xml=True)
                if file_info:
                    try:
                        file_root = ET.fromstring(file_info)
                        track_num = None
                        disc_num = None
                        
                        for field in file_root.findall('.//Field'):
                            field_name = field.get('Name')
                            if field_name == 'Track #':
                                track_num = field.text
                            elif field_name == 'Disc #':
                                disc_num = field.text
                        
                        if track_num:
                            if disc_num and disc_num != '1':
                                response += f", track {track_num} of disc {disc_num}"
                            else:
                                response += f", track {track_num}"
                    except:
                        pass
            
            response += "."
            self.speak(response)
            
        except Exception as e:
            print(f"Error in what_is_playing: {e}")
            self.speak("I couldn't get playback info.")

    def go_to_track(self, track_number):
        """Navigate to a specific track number in the current Playing Now playlist."""
        if track_number == 1:
            xml_response = self.send_mcws_command("Playback/Info", return_xml=True)
            if not xml_response:
                return
            
            try:
                root = ET.fromstring(xml_response)
                info = {}
                for item in root.findall('Item'):
                    info[item.get('Name')] = item.text
                
                current_pos = int(info.get('PlayingNowPosition', 0))
                
                if current_pos == 0:
                    self.speak(f"Already at the beginning.")
                    self.what_is_playing_silent()
                    return
                else:
                    self.speak(f"Going to the beginning.")
                    for _ in range(current_pos):
                        self.send_mcws_command("Playback/Previous")
                    self.what_is_playing_silent()
                    return
                    
            except Exception as e:
                print(f"Error: {e}")
                self.speak("I couldn't go to the beginning.")
                return
        
        xml_response = self.send_mcws_command("Playback/Info", return_xml=True)
        if not xml_response:
            return
        
        try:
            root = ET.fromstring(xml_response)
            info = {}
            for item in root.findall('Item'):
                info[item.get('Name')] = item.text
            
            current_pos = int(info.get('PlayingNowPosition', 0))
            total_tracks = int(info.get('PlayingNowTracks', 0))
            
            if total_tracks == 0:
                self.speak(f"The playlist is still loading. Try again in a moment.")
                return
            
            if track_number < 1 or track_number > total_tracks:
                self.speak(f"Track {track_number} is out of range. There are {total_tracks} tracks.")
                return
            
            target_pos = track_number - 1
            offset = target_pos - current_pos
            
            if offset == 0:
                self.speak(f"Already on track {track_number}.")
                self.what_is_playing_silent()
                return
            elif offset > 0:
                self.speak(f"Going to track {track_number}.")
                for _ in range(offset):
                    self.send_mcws_command("Playback/Next")
                time.sleep(0.5)
                self.what_is_playing_silent()
            else:
                self.speak(f"Going to track {track_number}.")
                for _ in range(abs(offset)):
                    self.send_mcws_command("Playback/Previous")
                time.sleep(0.5)
                self.what_is_playing_silent()
                    
        except Exception as e:
            print(f"Error in go_to_track: {e}")
            self.speak("I couldn't navigate to that track.")

    def list_tracks(self):
        """Lists information about the current Playing Now playlist."""
        xml_response = self.send_mcws_command("Playback/Info", return_xml=True)
        if not xml_response:
            return None
        
        try:
            root = ET.fromstring(xml_response)
            info = {}
            for item in root.findall('Item'):
                info[item.get('Name')] = item.text
            
            current_pos = int(info.get('PlayingNowPosition', 0)) + 1
            total_tracks = int(info.get('PlayingNowTracks', 0))
            
            if total_tracks == 0:
                self.speak("The playlist is empty.")
                return None
            
            playlist_xml = self.send_mcws_command("Playback/Playlist", return_xml=True)
            results = []
            
            if playlist_xml:
                try:
                    playlist_root = ET.fromstring(playlist_xml)
                    # Enumerate to get playlist position (1-based)
                    for i, item in enumerate(playlist_root.findall('Item'), 1):
                        track_info = {}
                        for field in item.findall('Field'):
                            field_name = field.get('Name')
                            if field_name in ['Name']:
                                track_info[field_name] = field.text
                        
                        track_name = track_info.get('Name', 'Unknown Track')
                        
                        # Return (Title, Position) tuples
                        # Position is the 1-based index in the playlist
                        results.append((track_name, i))
                        
                except Exception as e:
                    print(f"   Error parsing playlist: {e}\n")
            
            if not results:
                self.speak("I couldn't get the track list.")
                return None

            return results
            
        except Exception as e:
            print(f"Error listing tracks: {e}")
            self.speak("I couldn't get playlist info.")
            return None

    def play_files(self, files):
        """Plays a list of files (or indices for JRiver)."""
        if not files:
            return
        
        # For JRiver, 'files' are indices (integers) if coming from list_tracks
        # Check if the first item is an integer or string digit
        first = files[0]
        try:
            index = int(first)
            self.go_to_track(index)
        except ValueError:
            print(f"❌ JRiver play_files expected indices, got: {first}")
            self.speak("I can't play that.")

    def get_artist_albums(self, artist):
        """Returns a list of albums for the given artist, sorted by relevance."""
        tokens = artist.lower().split()
        if not tokens:
            return []
            
        encoded_query = urllib.parse.quote(artist)
        
        # We request Album, Artist, Composer to check against
        xml_response = self.send_mcws_command("Files/Search", extra_params=f"Query={encoded_query}&Fields=Album,Artist,Composer", return_xml=True)
        
        album_scores = {} # Album -> Score
        # Score 0: Artist match
        # Score 1: Album match
        # Score 2: Composer match
        
        if xml_response:
            try:
                root = ET.fromstring(xml_response)
                
                for item in root.findall('Item'):
                    item_album = None
                    item_artist = ""
                    item_composer = ""
                    
                    for field in item.findall('Field'):
                        name = field.get('Name')
                        val = field.text or ""
                        
                        if name == 'Album':
                            item_album = val
                        elif name == 'Artist':
                            item_artist = val
                        elif name == 'Composer':
                            item_composer = val
                    
                    if item_album:
                        # Determine match type
                        score = 3
                        
                        # Check Artist Match
                        if all(t in item_artist.lower() for t in tokens):
                            score = 0
                        # Check Album Match
                        elif all(t in item_album.lower() for t in tokens):
                            score = 1
                        # Check Composer Match
                        elif all(t in item_composer.lower() for t in tokens):
                            score = 2
                        
                        if score < 3:
                            # Update best score for this album
                            if item_album not in album_scores or score < album_scores[item_album]:
                                album_scores[item_album] = score
                                
            except Exception as e:
                print(f"Error parsing JRiver search results: {e}")
                pass
        
        # Sort logic
        def sort_key(a):
            score = album_scores[a]
            sub_score = 1
            # Secondary sort for Composer matches: prefer if Album title has tokens
            if score == 2:
                a_lower = a.lower()
                if any(token in a_lower for token in tokens):
                    sub_score = 0 # Better
            return (score, sub_score, a)

        sorted_albums = sorted(album_scores.keys(), key=sort_key)
        return sorted_albums

    def play_precise_album(self, album_name):
        """Plays exactly the tracks of an album in order."""
        # Try bracket syntax (proper JRiver search format)
        queries_to_try = [f"[Album]=[{album_name}]"]
        
        xml_response = None
        for i, q in enumerate(queries_to_try):
            print(f"Trying album search query ({i+1}/{len(queries_to_try)}): {q}")
            encoded_query = urllib.parse.quote(q)
            temp_response = self.send_mcws_command("Files/Search", extra_params=f"Query={encoded_query}", return_xml=True)
            if temp_response:
                try:
                    root = ET.fromstring(temp_response)
                    items = root.findall('Item')
                    if len(items) > 0:
                        print(f"✅ Found {len(items)} tracks with query: {q}")
                        xml_response = temp_response
                        break
                    else:
                        print(f"⚠️  Query returned 0 results, trying next...")
                except:
                    print(f"⚠️  Query returned invalid XML, trying next...")
                    pass
        
        if not xml_response:
            self.speak("I couldn't find the album tracks. The album name might have special characters that are difficult to search for.")
            return
            
        try:
            root = ET.fromstring(xml_response)
            tracks = []
            
            for item in root.findall('Item'):
                track_num = None
                key = None
                
                for field in item.findall('Field'):
                    field_name = field.get('Name')
                    if field_name == 'Track #':
                        try:
                            track_num = int(field.text)
                        except:
                            track_num = 9999
                    elif field_name == 'Key':
                        key = field.text
                
                if key:
                    if track_num is None:
                        track_num = 9999
                    tracks.append((track_num, key))
            
            if not tracks:
                self.speak("No tracks found for this album.")
                return
            
            tracks.sort(key=lambda x: x[0])
            keys = [key for _, key in tracks]
                
            print(f"Found {len(keys)} tracks for album {album_name}, sorted by track number")
            
            keys_str = ",".join(keys)
            self.send_mcws_command("Playback/PlayByKey", extra_params=f"Key={keys_str}")
            
            time.sleep(1)
            self.what_is_playing_silent()
            
        except Exception as e:
            print(f"Error in play_precise_album: {e}")
            self.speak("Something went wrong playing the album.")
