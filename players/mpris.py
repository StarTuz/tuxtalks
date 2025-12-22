import dbus
import time
from player_interface import MediaPlayer

class MPRISPlayer(MediaPlayer):
    def __init__(self, config, speak_func=print, service_name=None):
        super().__init__(config, speak_func)
        self.bus = dbus.SessionBus()
        # If service_name is not provided, we might need to find one or it's passed in config
        self.service_name = service_name or config.get("MPRIS_SERVICE")
        self.object_path = "/org/mpris/MediaPlayer2"
        self.player_interface = "org.mpris.MediaPlayer2.Player"
        self.main_interface = "org.mpris.MediaPlayer2"
        
        # Initialize Local Library
        import pathlib
        from local_library import LocalLibrary
        
        db_path = pathlib.Path.home() / ".local" / "share" / "tuxtalks" / "library.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.library = LocalLibrary(str(db_path))
        
        self.library_path = config.get("LIBRARY_PATH")

    def _get_proxy(self):
        try:
            if not self.service_name:
                return None
            proxy = self.bus.get_object(self.service_name, self.object_path)
            return proxy
        except dbus.exceptions.DBusException:
            return None

    def health_check(self):
        """Checks if the player is running."""
        if not self.service_name:
            print("❌ No MPRIS service name configured.")
            return False
            
        print(f"Checking {self.service_name} connection...")
        try:
            if self.bus.name_has_owner(self.service_name):
                print(f"✅ {self.service_name} is running.")
                return True
            else:
                print(f"⚠️  {self.service_name} is not running.")
                # We could try to launch it if we knew the binary name, 
                # but for generic MPRIS we might not know.
                return False
        except Exception as e:
            print(f"❌ Error checking {self.service_name}: {e}")
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
            self.speak("Player is not running.")
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
            self.speak("Player is not running.")
            return None

        try:
            props = dbus.Interface(proxy, "org.freedesktop.DBus.Properties")
            metadata = props.Get(self.player_interface, "Metadata")
            
            album = metadata.get("xesam:album")
            if not album:
                self.speak("I don't know what album is playing.")
                return None
                
            # Query library for tracks
            import sqlite3
            with sqlite3.connect(self.library.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT title, path FROM tracks WHERE album = ? ORDER BY track_number, title", (album,))
                rows = cursor.fetchall()
                
            # Return list of (title, path) tuples
            # Decode paths
            results = []
            for r in rows:
                title = r[0]
                path_blob = r[1]
                try:
                    path = path_blob.decode('utf-8', 'surrogateescape')
                except:
                    path = str(path_blob)
                results.append((title, path))
            
            if not results:
                self.speak(f"No tracks found for {album}.")
                return None
                
            return results
            
        except Exception as e:
            print(f"Error listing tracks: {e}")
            self.speak("I couldn't list the tracks.")
            return None

    def play_file(self, path):
        """Plays a specific file."""
        self._play_files([path])

    def play_files(self, paths):
        """Plays a list of files."""
        self._play_files(paths)

    def get_artist_albums(self, artist):
        """Returns a list of albums for the given artist using LocalLibrary."""
        return self.library.get_artist_albums(artist)

    def play_genre(self, genre):
        self.speak("Genre search is not supported yet.")

    def play_artist(self, artist):
        # Find tracks by artist
        tracks = self.library.search_tracks(artist, fields=['artist'])
        if not tracks:
            self.speak(f"I couldn't find any music by {artist}.")
            return
            
        self.speak(f"Playing music by {artist}")
        self._play_files([t['path'] for t in tracks])

    def play_album(self, album):
        tracks = self.library.get_album_tracks(album)
        if not tracks:
            self.speak(f"I couldn't find the album {album}.")
            return
            
        self.speak(f"Playing album {album}")
        self._play_files(tracks)

    def play_playlist(self, playlist_name, shuffle=False):
        """Plays a playlist file (.m3u, .pls) from the library."""
        playlists = self.library.search_playlists(playlist_name)
        if not playlists:
            self.speak(f"I couldn't find a playlist named {playlist_name}.")
            return
            
        # If multiple, pick first for now (or improve logic later)
        name, path = playlists[0]
        
        # Read playlist file to get tracks
        try:
            with open(path, 'r') as f:
                lines = f.readlines()
            
            tracks = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle relative paths in playlist
                    if not line.startswith("/"):
                        p_dir = os.path.dirname(path)
                        full_path = os.path.join(p_dir, line)
                        tracks.append(full_path)
                    else:
                        tracks.append(line)
            
            if not tracks:
                self.speak("The playlist is empty.")
                return

            if shuffle:
                self.speak(f"Playing random songs from playlist {name}")
                import random
                random.shuffle(tracks)
            else:
                self.speak(f"Playing playlist {name}")
                
            self._play_files(tracks)
            
        except Exception as e:
            print(f"Error reading playlist: {e}")
            self.speak("I couldn't read the playlist file.")

    def play_random(self):
        tracks = self.library.get_random_tracks(limit=50)
        if not tracks:
            self.speak("The library is empty.")
            return

        self.speak(f"Playing random music ({len(tracks)} tracks queued).")
        self._play_files([t['path'] for t in tracks])

    def play_any(self, query):
        # Try to find something matching the query
        tracks = self.library.search_tracks(query)
        if not tracks:
            self.speak(f"I couldn't find anything matching {query}.")
            return
            
        # If we found albums, maybe play the first one?
        # Or just play all found tracks?
        # Let's play all found tracks for now
        count = len(tracks)
        
        # Prioritize Albums if many hits
        if count > 10:
            # Group by Album
            albums = {}
            for t in tracks:
                alb = t.get('album', 'Unknown Album')
                if alb not in albums:
                    albums[alb] = []
                albums[alb].append(t)
            
            # If we have multiple albums, present them as options
            if len(albums) > 1:
                options = []
                for alb_name, alb_tracks in albums.items():
                    if len(alb_tracks) > 1:
                        # It's an album cluster
                        # (Title, Path, Type) -> Path is Album Name for "album" type
                        options.append((alb_name, alb_name, "album"))
                    else:
                        # Single track, add as track
                        t = alb_tracks[0]
                        options.append((t['title'], t['path'], t.get('media_type', 'audio')))
                
                # Sort options: Albums first, then tracks
                options.sort(key=lambda x: (0 if x[2] == "album" else 1, x[0] or ""))
                return options

        if len(tracks) > 1:
            # If multiple items, return them for selection
            # The main assistant will handle the announcement and listing
            
            # Return list of (title, path, media_type) tuples
            return [(t['title'], t['path'], t.get('media_type', 'audio')) for t in tracks]
            
        # Single item found, play it
        self.speak(f"Playing {tracks[0]['title']}")
        self._play_files([tracks[0]['path']])
        return None

    def _play_files(self, files):
        """Plays a list of files using OpenUri."""
        if not files:
            return
            
        proxy = self._get_proxy()
        if not proxy:
            self.speak("Player is not running.")
            return
            
        # MPRIS OpenUri usually takes one URI.
        # Some players support adding to playlist via OpenUri if called multiple times?
        # Or maybe we just play the first one and queue the rest?
        # VLC's MPRIS implementation of OpenUri: "Opens the Uri."
        # It might replace the playlist.
        
        # Let's try to OpenUri the first one.
        # For multiple files, we might need a playlist file (m3u).
        
        import tempfile
        import os
        
        if len(files) > 1:
            # Create a temporary M3U playlist
            fd, path = tempfile.mkstemp(suffix=".m3u8", text=True)
            with os.fdopen(fd, 'w') as f:
                f.write("#EXTM3U\n")
                for file_path in files:
                    f.write(f"{file_path}\n")
            
            uri = f"file://{path}"
            print(f"▶ Playing playlist: {uri}")
            proxy.OpenUri(uri, dbus_interface=self.player_interface)
            
            # We can't easily delete the temp file immediately as VLC needs to read it.
            # It will be cleaned up by OS eventually or we can clean up on exit.
        else:
            uri = f"file://{files[0]}"
            print(f"▶ Playing file: {uri}")
            proxy.OpenUri(uri, dbus_interface=self.player_interface)
            
        time.sleep(1)
        self.what_is_playing()
