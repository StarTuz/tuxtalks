import sqlite3
import pathlib
import urllib.parse
from players.mpris import MPRISPlayer
import subprocess
import time
import dbus

class ElisaPlayer(MPRISPlayer):
    def __init__(self, config, speak_func=print):
        super().__init__(config, speak_func, service_name="org.mpris.MediaPlayer2.elisa")
        self.db_path = pathlib.Path.home() / ".local" / "share" / "elisa" / "elisaDatabase.db"

    def _query_db(self, query, params=()):
        if not self.db_path.exists():
            print(f"❌ Elisa DB not found at {self.db_path}")
            self.announce_error("I cannot find the Elisa database.")
            return []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []

    def list_tracks(self):
        """Lists tracks for the currently playing album."""
        proxy = self._get_proxy()
        if not proxy:
            self.announce_error("Elisa is not running.")
            return None

        try:
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            metadata = props.Get(self.player_interface, "Metadata")
            
            album = metadata.get("xesam:album")
            if not album:
                self.speak("I don't know what album is playing.")
                return None
                
            # Query Elisa DB for tracks
            # Elisa DB Schema: Tracks table with AlbumTitle, Title, FileName (or Url?)
            # Let's check schema assumptions or use what we know works.
            # Earlier code used: SELECT FileName FROM Tracks WHERE AlbumTitle LIKE ?
            # So we can select Title, FileName
            query = "SELECT Title, FileName FROM Tracks WHERE AlbumTitle = ? ORDER BY DiscNumber, TrackNumber"
            results = self._query_db(query, (album,))
            
            if not results:
                self.speak(f"No tracks found for {album}.")
                return None
                
            # Return list of (Title, Path) tuples
            tracks = []
            for r in results:
                title = r[0]
                path = r[1]
                tracks.append((title, path))
                
            return tracks
            
        except Exception as e:
            print(f"Error listing tracks: {e}")
            self.speak("I couldn't list the tracks.")
            return None

    def play_files(self, files):
        """Plays a list of files."""
        self._play_files(files)

    def _play_files(self, files):
        if not files:
            self.announce_error("No files found.")
            return

        print(f"▶️  Playing {len(files)} tracks...")
        
        # Elisa supports loading files via command line
        try:
            # Elisa seems to handle file paths directly or URIs
            cmd = ["elisa"] + files
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait a bit then ensure it's playing
            time.sleep(2)
            
            # Check if already playing to avoid toggling to pause
            try:
                proxy = self._get_proxy()
                if proxy:
                    props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
                    status = props.Get(self.player_interface, "PlaybackStatus")
                    if status != "Playing":
                        self.play_pause()
            except Exception as e:
                print(f"Error checking status: {e}")
                self.play_pause() # Fallback
                
            time.sleep(0.5)
            self.what_is_playing()
        except Exception as e:
            print(f"Error launching elisa: {e}")

    def get_artist_albums(self, artist):
        """Returns a list of albums for the given artist."""
        tokens = artist.split()
        if not tokens:
            return []

        # Columns to search in Tracks table
        columns = ["ArtistName", "AlbumArtistName", "Composer", "Title", "AlbumTitle"]
        
        # 1. Broad SQL Search (finds candidates)
        # We search for rows where ANY token appears in ANY column
        # This is an optimization to reduce the dataset before Python filtering
        # We can't easily do AND logic across columns with OR logic for tokens in SQL 
        # without a complex query, so we'll just get anything that looks relevant.
        
        # Actually, to be safe and simple, let's just get rows where at least one token matches
        # But wait, we want AND logic for tokens (all tokens must be present).
        # If we do broad OR in SQL, we get too many results?
        # Let's try to do: (col1 LIKE %t1% OR col2 LIKE %t1%) AND (col1 LIKE %t2% OR col2 LIKE %t2%)
        
        def build_token_condition(token):
            # token must appear in at least one column
            conds = [f"{col} LIKE ?" for col in columns]
            return f"({' OR '.join(conds)})"
            
        where_clauses = [build_token_condition(t) for t in tokens]
        where_sql = " AND ".join(where_clauses)
        
        # We need to select all columns to check them in Python
        query = f"SELECT DISTINCT AlbumTitle, ArtistName, AlbumArtistName, Composer, Title FROM Tracks WHERE {where_sql}"
        
        params = []
        for token in tokens:
            for _ in columns:
                params.append(f"%{token}%")
                
        results = self._query_db(query, tuple(params))
        
        # 2. Precise Python Filtering (Regex)
        import re
        final_albums = set()
        
        for row in results:
            album_title = row[0]
            if not album_title: continue
            
            # Combine all text fields for checking
            # row: (AlbumTitle, ArtistName, AlbumArtistName, Composer, Title)
            full_text = " ".join([str(x) for x in row if x])
            
            # Check if ALL tokens are present as whole words
            all_tokens_found = True
            for token in tokens:
                # Regex for whole word: \btoken\b
                # We use re.IGNORECASE
                if not re.search(rf"\b{re.escape(token)}\b", full_text, re.IGNORECASE):
                    all_tokens_found = False
                    break
            
            if all_tokens_found:
                final_albums.add(album_title)
                
        return sorted(list(final_albums))

    def play_artist(self, artist):
        self.speak(f"Playing music by {artist}")
        # Simple search for now, can be improved with tokens if needed
        query = "SELECT FileName FROM Tracks WHERE ArtistName LIKE ? OR AlbumArtistName LIKE ? ORDER BY AlbumTitle, TrackNumber"
        results = self._query_db(query, (f"%{artist}%", f"%{artist}%"))
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error(f"I couldn't find any tracks by {artist}.")

    def play_album(self, album):
        self.speak(f"Playing album {album}")
        query = "SELECT FileName FROM Tracks WHERE AlbumTitle LIKE ? ORDER BY DiscNumber, TrackNumber"
        results = self._query_db(query, (f"%{album}%",))
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error(f"I couldn't find the album {album}.")

    def play_genre(self, genre):
        self.speak(f"Playing {genre} music")
        query = "SELECT FileName FROM Tracks WHERE Genre LIKE ? ORDER BY random() LIMIT 100"
        results = self._query_db(query, (f"%{genre}%",))
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error(f"I couldn't find any {genre} music.")

    def play_random(self):
        """Plays random tracks from the library."""
        self.speak("Playing random music")
        query = "SELECT FileName FROM Tracks ORDER BY random() LIMIT 100"
        results = self._query_db(query)
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error("I couldn't find any music in the library.")

    def play_any(self, query):
        self.speak(f"Searching for {query}")
        
        all_results = []
        
        # 1. Artist
        sql = "SELECT DISTINCT ArtistName FROM Tracks WHERE ArtistName LIKE ? ORDER BY ArtistName"
        results = self._query_db(sql, (f"%{query}%",))
        for r in results:
            if r[0]:
                all_results.append((f"Artist: {r[0]}", r[0], "artist_mix"))

        # 2. Album
        sql = "SELECT DISTINCT AlbumTitle FROM Tracks WHERE AlbumTitle LIKE ? ORDER BY AlbumTitle"
        results = self._query_db(sql, (f"%{query}%",))
        for r in results:
            if r[0]:
                all_results.append((f"Album: {r[0]}", r[0], "album"))

        # 3. Title (Tracks)
        sql = "SELECT Title, FileName FROM Tracks WHERE Title LIKE ? LIMIT 50"
        results = self._query_db(sql, (f"%{query}%",))
        for r in results:
            if r[0]:
                # Format: Title, Path, Type
                all_results.append((r[0], r[1], "track"))

        if not all_results:
            self.announce_error(f"I couldn't find anything matching {query}.")
            return None

        if len(all_results) == 1:
            item = all_results[0]
            type_ = item[2]
            name = item[0]
            val = item[1]
            
            if type_ == "artist_mix":
                self.play_artist(val)
            elif type_ == "album":
                self.play_album(val)
            else:
                self.speak(f"Playing {name}")
                self._play_files([val])
            return None
        
        # Multiple results -> Return list for selection
        def sort_key(item):
            type_score = {"artist_mix": 0, "album": 1, "track": 2}.get(item[2], 3)
            return (type_score, item[0])
            
        all_results.sort(key=sort_key)
        
        return all_results

    def health_check(self):
        """Checks if Elisa is running, attempts to launch if not."""
        print("Checking Elisa connection...")
        try:
            if self.bus.name_has_owner(self.service_name):
                print("✅ Elisa is running.")
                return True
            else:
                print("⚠️  Elisa is not running. Attempting to launch...")
                subprocess.Popen(["elisa"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Wait for it to appear on bus
                for _ in range(10):
                    time.sleep(1)
                    if self.bus.name_has_owner(self.service_name):
                        print("✅ Elisa started.")
                        return True
                print("❌ Could not launch Elisa.")
                return False
        except Exception as e:
            print(f"❌ Error checking Elisa: {e}")
            return False

    def play_playlist(self, playlist_name, shuffle=False):
        """Plays a playlist by name."""
        self.announce_error("Playlist support is not yet implemented for Elisa.")
