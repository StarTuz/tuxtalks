import dbus
import time
import sqlite3
import pathlib
import urllib.parse
from player_interface import MediaPlayer

class StrawberryPlayer(MediaPlayer):
    def __init__(self, config, speak_func=print):
        super().__init__(config, speak_func)
        self.bus = dbus.SessionBus()
        self.service_name = "org.mpris.MediaPlayer2.strawberry"
        self.object_path = "/org/mpris/MediaPlayer2"
        self.player_interface = "org.mpris.MediaPlayer2.Player"
        self.main_interface = "org.mpris.MediaPlayer2"
        
        # Strawberry DB Path
        self.db_path = pathlib.Path(config.get("STRAWBERRY_DB_PATH"))

    def _get_proxy(self):
        try:
            proxy = self.bus.get_object(self.service_name, self.object_path)
            return proxy
        except dbus.exceptions.DBusException:
            return None

    def health_check(self):
        """Checks if Strawberry is running."""
        print("Checking Strawberry connection...")
        try:
            # Check if service exists on bus
            if self.bus.name_has_owner(self.service_name):
                print("✅ Strawberry is running.")
                return True
            else:
                print("⚠️  Strawberry is not running. Attempting to launch...")
                import subprocess
                subprocess.Popen(["strawberry"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Wait for it to appear on bus
                for _ in range(10):
                    time.sleep(1)
                    if self.bus.name_has_owner(self.service_name):
                        print("✅ Strawberry started.")
                        return True
                print("❌ Could not launch Strawberry.")
                return False
        except Exception as e:
            print(f"❌ Error checking Strawberry: {e}")
            return False

    def play_pause(self):
        proxy = self._get_proxy()
        if proxy:
            proxy.PlayPause(dbus_interface=self.player_interface)

    def stop(self):
        proxy = self._get_proxy()
        if proxy:
            proxy.Stop(dbus_interface=self.player_interface)

    def next_track(self):
        proxy = self._get_proxy()
        if proxy:
            proxy.Next(dbus_interface=self.player_interface)
            time.sleep(0.5)
            self.what_is_playing()

    def previous_track(self):
        proxy = self._get_proxy()
        if proxy:
            proxy.Previous(dbus_interface=self.player_interface)
            time.sleep(0.5)
            self.what_is_playing()

    def volume_up(self):
        # MPRIS Volume is 0.0 to 1.0
        # We can't easily "step" without reading current, but let's try
        proxy = self._get_proxy()
        if proxy:
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            current_vol = props.Get(self.player_interface, "Volume")
            new_vol = min(1.0, current_vol + 0.1)
            props.Set(self.player_interface, "Volume", new_vol)

    def volume_down(self):
        proxy = self._get_proxy()
        if proxy:
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            current_vol = props.Get(self.player_interface, "Volume")
            new_vol = max(0.0, current_vol - 0.1)
            props.Set(self.player_interface, "Volume", new_vol)

    def what_is_playing(self):
        proxy = self._get_proxy()
        if not proxy:
            self.announce_error("Strawberry is not running.")
            return

        try:
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            metadata = props.Get(self.player_interface, "Metadata")
            
            title = metadata.get("xesam:title", "Unknown Title")
            artist = metadata.get("xesam:artist", ["Unknown Artist"])
            if isinstance(artist, dbus.Array):
                artist = artist[0]
            
            self.announce_now_playing(title, artist)
            
        except Exception as e:
            print(f"Error getting metadata: {e}")
            self.announce_error("I couldn't get playback info.")

    def list_tracks(self):
        """Lists tracks for the currently playing album."""
        proxy = self._get_proxy()
        if not proxy:
            self.announce_error("Strawberry is not running.")
            return None

        try:
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            metadata = props.Get(self.player_interface, "Metadata")
            
            album = metadata.get("xesam:album")
            if not album:
                self.speak("I don't know what album is playing.")
                return None
                
            # Query Strawberry DB for tracks
            query = "SELECT title, url FROM songs WHERE album = ? ORDER BY track, disc"
            results = self._query_db(query, (album,))
            
            if not results:
                self.speak(f"No tracks found for {album}.")
                return None
                
            # Return list of (Title, Path) tuples
            tracks = []
            for r in results:
                title = r[0]
                url = r[1]
                # Convert URL to path if needed, but play_files handles URIs
                tracks.append((title, url))
                
            return tracks
            
        except Exception as e:
            print(f"Error listing tracks: {e}")
            self.speak("I couldn't list the tracks.")
            return None

    # --- Search & Play via SQLite ---

    def _query_db(self, query, params=()):
        if not self.db_path.exists():
            # Try fallback path
            fallback_path = pathlib.Path.home() / ".local" / "share" / "strawberry" / "strawberry" / "strawberry.db"
            if fallback_path.exists():
                print(f"⚠️  Configured DB not found, using fallback: {fallback_path}")
                self.db_path = fallback_path
            else:
                print(f"❌ Strawberry DB not found at {self.db_path}")
                self.announce_error("I cannot find the Strawberry database. Please check your configuration.")
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

    def play_files(self, files):
        """Plays a list of files."""
        self._play_files(files)

    def _play_files(self, files):
        if not files:
            self.announce_error("No files found.")
            return

        proxy = self._get_proxy()
        if not proxy:
            return

        # Clear playlist (optional, but usually desired when playing new thing)
        # Strawberry might not expose Clear via MPRIS.
        # We can use OpenUri with the first file, which usually replaces or appends.
        # Standard MPRIS OpenUri takes one URI.
        # Strawberry might support adding multiple via command line, but let's try OpenUri loop?
        # No, OpenUri usually starts playing immediately.
        
        # Better approach: Use Strawberry's command line interface to load tracks?
        # strawberry --load [files]
        
        import subprocess
        # Convert to file URIs
        file_uris = []
        for f in files:
            # Ensure it's a valid URI
            if not f.startswith("file://"):
                f_path = pathlib.Path(f).absolute()
                f_uri = f_path.as_uri()
                file_uris.append(f_uri)
            else:
                file_uris.append(f)
        
        print(f"▶️  Playing {len(file_uris)} tracks...")
        
        # Use subprocess to call strawberry with files
        # This is often more reliable for "Play this list" than MPRIS OpenUri one by one
        try:
            cmd = ["strawberry", "--load"] + file_uris
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2) # Wait for load
            self.play_pause() # Trigger playback via DBus
            time.sleep(0.5)
            self.what_is_playing()
        except Exception as e:
            print(f"Error launching strawberry: {e}")

    def play_genre(self, genre):
        self.speak(f"Playing {genre} music")
        # Strawberry DB usually has a 'genre' column in songs table
        query = "SELECT url FROM songs WHERE genre LIKE ? ORDER BY random() LIMIT 100"
        results = self._query_db(query, (f"%{genre}%",))
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error(f"I couldn't find any {genre} music.")

    def play_random(self):
        """Plays random tracks from the library."""
        self.speak("Playing random music")
        query = "SELECT url FROM songs ORDER BY random() LIMIT 100"
        results = self._query_db(query)
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error("I couldn't find any music in the library.")

    def get_artist_albums(self, artist):
        """Returns a list of albums for the given artist."""
        # Split query into tokens to handle "Gustav Holst" vs "Holst, Gustav"
        tokens = artist.split()
        if not tokens:
            return []
            
        # Helper to build AND condition for a single column
        def build_col_condition(col_name):
            conditions = [f"{col_name} LIKE ?" for _ in tokens]
            return f"({' AND '.join(conditions)})"

        # Columns to search
        columns = ["artist", "album", "composer", "albumartist", "performer", "title"]
        
        # Build the full WHERE clause
        # (artist LIKE %t1% AND artist LIKE %t2%) OR (album LIKE %t1% AND album LIKE %t2%) ...
        where_clauses = [build_col_condition(col) for col in columns]
        where_sql = " OR ".join(where_clauses)
        
        query = f"SELECT DISTINCT album FROM songs WHERE {where_sql} ORDER BY album"
        
        # Parameters: each token repeated for each column
        # tokens = [t1, t2]
        # params = [t1, t2, t1, t2, ...]
        params = []
        for _ in columns:
            for token in tokens:
                params.append(f"%{token}%")
        
        try:
            results = self._query_db(query, tuple(params))
        except:
            # Fallback for older DBs (missing columns)
            # Just search artist and album with simple LIKE
            query = "SELECT DISTINCT album FROM songs WHERE artist LIKE ? OR album LIKE ? ORDER BY album"
            results = self._query_db(query, (f"%{artist}%", f"%{artist}%"))
            
        return [r[0] for r in results if r[0]]

    def play_artist(self, artist):
        self.speak(f"Playing music by {artist}")
        # Find tracks by artist
        # Schema usually: songs table with artist, title, url/filename
        query = "SELECT url FROM songs WHERE artist LIKE ? ORDER BY album, track, disc"
        results = self._query_db(query, (f"%{artist}%",))
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error(f"I couldn't find any tracks by {artist}.")

    def play_album(self, album):
        self.speak(f"Playing album {album}")
        query = "SELECT url FROM songs WHERE album LIKE ? ORDER BY track, disc"
        results = self._query_db(query, (f"%{album}%",))
        files = [r[0] for r in results]
        
        if files:
            self._play_files(files)
        else:
            self.announce_error(f"I couldn't find the album {album}.")

    def play_any(self, query):
        self.speak(f"Searching for {query}")
        
        all_results = []
        
        # 1. Artist
        sql = "SELECT DISTINCT artist FROM songs WHERE artist LIKE ? ORDER BY artist"
        results = self._query_db(sql, (f"%{query}%",))
        for r in results:
            if r[0]:
                all_results.append((f"Artist: {r[0]}", r[0], "artist_mix"))

        # 2. Album
        sql = "SELECT DISTINCT album FROM songs WHERE album LIKE ? ORDER BY album"
        results = self._query_db(sql, (f"%{query}%",))
        for r in results:
            if r[0]:
                all_results.append((f"Album: {r[0]}", r[0], "album"))

        # 3. Title (Tracks)
        sql = "SELECT title, url FROM songs WHERE title LIKE ? ORDER BY album, track, title LIMIT 50"
        results = self._query_db(sql, (f"%{query}%",))
        for r in results:
            if r[0]:
                # Format: Title, Path, Type
                all_results.append((r[0], r[1], "track"))

        if not all_results:
            self.announce_error(f"I couldn't find anything matching {query}.")
            return None

        # If strict match found, maybe prioritize? 
        # But user wants list if ambiguity exists.
        
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
        # Sort logic: Artists top, then Albums, then Tracks
        def sort_key(item):
            # item[2] is type
            type_score = {"artist_mix": 0, "album": 1, "track": 2}.get(item[2], 3)
            return (type_score, item[0])
            
        all_results.sort(key=sort_key)
        
        # Limit to reasonable number to avoid overwhelming?
        # The main app handles pagination (groups of 10), so returning 50 is fine.
        return all_results

    def play_playlist(self, playlist_name, shuffle=False):
        """Plays a playlist by name."""
        self.speak(f"Searching for playlist {playlist_name}")
        
        # 1. Find Playlist ID
        query = "SELECT rowid, name FROM playlists WHERE name LIKE ?"
        try:
            results = self._query_db(query, (f"%{playlist_name}%",))
            if not results:
                 self.speak(f"I couldn't find a playlist named {playlist_name}.")
                 return
            
            # Use first match
            pid, pname = results[0]
            self.speak(f"Playing playlist {pname}")
            
            # 2. Get tracks
            # Strawberry schema: playlist_items table usually has 'url' or 'collection_id'
            # Let's check typical schema: playlist_items (playlist_id, url, ...)
            
            track_query = "SELECT url FROM playlist_items WHERE playlist_id = ? ORDER BY rowid"
            if shuffle:
                 track_query = "SELECT url FROM playlist_items WHERE playlist_id = ? ORDER BY random()"
            
            track_results = self._query_db(track_query, (pid,))
            files = [r[0] for r in track_results if r[0]]
            
            if files:
                self._play_files(files)
            else:
                self.speak("The playlist is empty.")
                
        except Exception as e:
            print(f"Error playing playlist: {e}")
            self.speak("I couldn't access playlists.")
