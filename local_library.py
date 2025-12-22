import os
import sqlite3
import pathlib
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
import threading

class LocalLibrary:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if schema needs update (add composer, media_type)
            try:
                cursor.execute("SELECT media_type FROM tracks LIMIT 1")
            except sqlite3.OperationalError:
                # Column missing, recreate table
                cursor.execute("DROP TABLE IF EXISTS tracks")
            
            # path is now BLOB to handle non-UTF-8 filenames safely
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path BLOB UNIQUE,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    composer TEXT,
                    genre TEXT,
                    track_number INTEGER,
                    media_type TEXT
                )
            """)
            
            # Playlists table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path BLOB UNIQUE,
                    name TEXT
                )
            """)
            conn.commit()

    def scan_directory(self, root_path, callback=None, clear_db=True):
        """
        Scans the directory for audio files and updates the database.
        
        Args:
            root_path (str): Path to scan.
            callback (func): Progress callback (current, total).
            clear_db (bool): If True, clears the library before scanning.
        """
        root = pathlib.Path(root_path).resolve()
        if not root.exists():
            print(f"❌ Library path not found: {root_path}")
            return

        print(f"📂 Scanning library at: {root_path}")
        
        # Support both audio and video extensions
        audio_exts = {'.mp3', '.flac', '.ogg', '.m4a', '.wav'}
        video_exts = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.mpg', '.mpeg'}
        playlist_exts = {'.m3u', '.m3u8', '.pls'}
        media_extensions = audio_exts.union(video_exts).union(playlist_exts)
        
        files_to_process = []
        
        # 1. Find all files
        # Directories to ignore (junk/system folders)
        JUNK_DIRS = {'.cache', '.git', '.vscode', '.idea', 'node_modules', '__pycache__', '.venv', 'venv', '.npm', '.pip', '.flatpak-info'}
        
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip junk directories
            dirnames[:] = [d for d in dirnames if d not in JUNK_DIRS]
            
            for filename in filenames:
                path = pathlib.Path(dirpath) / filename
                if path.suffix.lower() in media_extensions:
                    files_to_process.append(path)
        
        total = len(files_to_process)
        print(f"   Found {total} media files.")
        
        # 2. Process files
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if clear_db:
                cursor.execute("DELETE FROM tracks")
                cursor.execute("DELETE FROM playlists")
            
            count = 0
            p_count = 0
            for path in files_to_process:
                try:
                    ext = path.suffix.lower()
                    path_bytes = str(path).encode('utf-8', 'surrogateescape')
                    
                    if ext in playlist_exts:
                        # Handle Playlist
                        name = path.stem
                        cursor.execute("INSERT OR REPLACE INTO playlists (path, name) VALUES (?, ?)", (path_bytes, name))
                        p_count += 1
                    else:
                        # Handle Track/Video
                        metadata = self._read_metadata(path)
                        m_type = 'video' if ext in video_exts else 'audio'
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO tracks (path, title, artist, album, composer, genre, track_number, media_type)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            path_bytes,
                            metadata.get('title') or path.stem,
                            metadata.get('artist') or 'Unknown Artist',
                            metadata.get('album') or 'Unknown Album',
                            metadata.get('composer') or '',
                            metadata.get('genre') or '',
                            metadata.get('track_number', 0),
                            m_type
                        ))
                        count += 1
                        
                    if callback and (count + p_count) % 10 == 0:
                        callback(count + p_count, total)
                except Exception as e:
                    print(f"   Error processing {path.name}: {e}")
            
            conn.commit()
            print(f"✅ Library scan complete. Indexed {count} tracks and {p_count} playlists.")

    def _read_metadata(self, path):
        """Reads metadata using mutagen."""
        info = {}
        try:
            audio = mutagen.File(path, easy=True)
            if audio:
                info['title'] = audio.get('title', [None])[0]
                info['artist'] = audio.get('artist', [None])[0]
                info['album'] = audio.get('album', [None])[0]
                info['composer'] = audio.get('composer', [None])[0]
                info['genre'] = audio.get('genre', [None])[0]
                
                track = audio.get('tracknumber', [None])[0]
                if track:
                    try:
                        info['track_number'] = int(track.split('/')[0])
                    except:
                        pass
        except Exception:
            pass
        return info

    def search_tracks(self, query, fields=None):
        """
        Searches for tracks matching the query.
        """
        if not fields:
            fields = ['title', 'artist', 'album', 'composer']
            
        tokens = query.split()
        if not tokens:
            return []
            
        conds = []
        params = []
        for token in tokens:
            token_conds = []
            for field in fields:
                token_conds.append(f"{field} LIKE ?")
                params.append(f"%{token}%")
            # Always search path too (cast to text for safety)
            token_conds.append("CAST(path AS TEXT) LIKE ?")
            params.append(f"%{token}%")
            conds.append(f"({' OR '.join(token_conds)})")
            
        where_clause = " AND ".join(conds)
        sql = f"SELECT path, title, artist, album, composer, media_type FROM tracks WHERE {where_clause}"
        
        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            
            import re
            for row in rows:
                path_bytes, title, artist, album, composer, media_type = row
                
                # Decode path back to string (with surrogates if needed)
                path_str = path_bytes.decode('utf-8', 'surrogateescape')
                
                # Include path in full_text for search (allows searching by folder name)
                full_text = f"{title} {artist} {album} {composer or ''} {path_str}"
                
                all_found = True
                for token in tokens:
                     if not re.search(rf"\b{re.escape(token)}\b", full_text, re.IGNORECASE):
                        # Special case for path: allow partial match (not whole word) for folder names
                        if token.lower() in path_str.lower():
                            continue
                        all_found = False
                        break
                
                if all_found:
                    results.append({
                        'path': path_str,
                        'title': title,
                        'artist': artist,
                        'album': album,
                        'composer': composer or "",
                        'media_type': media_type
                    })
                    
        return results

    def get_artist_albums(self, query):
        """Returns list of album names for an artist, sorted by relevance."""
        # Search for tracks matching the query
        tracks = self.search_tracks(query, fields=['artist', 'album', 'title', 'composer'])
        
        # Group by album and calculate score
        # Score 0: Artist match (Best)
        # Score 1: Album match
        # Score 2: Composer match
        # Score 3: Other (Title)
        
        album_scores = {}
        query_tokens = query.lower().split()
        
        for t in tracks:
            album = t['album']
            if not album:
                continue
                
            current_score = 3 # Default
            
            # Helper to check if all tokens are in a field
            def matches_tokens(field_value):
                if not field_value: return False
                val = field_value.lower()
                return all(token in val for token in query_tokens)

            # Check Artist
            if matches_tokens(t['artist']):
                current_score = 0
            # Check Album
            elif matches_tokens(album):
                current_score = min(current_score, 1)
            # Check Composer
            elif matches_tokens(t['composer']):
                current_score = min(current_score, 2)
            
            # Special case: If query is just "Holst", "Holst: The Planets" matches album (Score 1)
            # But "Gustav Holst" query vs "Holst: The Planets" album?
            # "Gustav" is missing from album title.
            # So it falls back to Composer (Score 2) or Title (Score 3).
            # Wait, if "Gustav" is missing from Album title, it SHOULD NOT be Score 1.
            # The issue is that "The Planets" is a dedicated album but the metadata doesn't say "Gustav Holst" in Album title.
            # But it likely says "Gustav Holst" in Composer.
            # So "The Planets" gets Score 2 (Composer).
            # "Christmas Carols" also gets Score 2 (Composer).
            
            # We want "The Planets" to beat "Christmas Carols".
            # Why? Because "The Planets" is *defined* by Holst, whereas "Christmas Carols" just *contains* Holst.
            # Maybe we can check if the Artist contains the query tokens?
            # For "The Planets", Artist is "London Symphony Orchestra". No match.
            
            # If both are Score 2 (Composer match), how do we break ties?
            # Maybe ratio of Holst tracks to total tracks? Too complex for now.
            # Or maybe check if Album Title contains *any* of the tokens (e.g. "Holst")?
            # "Holst: The Planets" contains "Holst". "Christmas Carols" does not.
            
            # Refined Logic:
            # If Score is tied (e.g. both Composer matches), prefer albums where Title matches PART of the query.
            
            if album not in album_scores:
                album_scores[album] = current_score
            else:
                album_scores[album] = min(album_scores[album], current_score)
                
        # Refined Sort:
        # Primary: Score (0=Artist, 1=Album, 2=Composer)
        # Secondary: If Score is 2 (Composer), prefer albums that contain at least one query token in the Album Name.
        # Tertiary: Alphabetical
        
        def sort_key(a):
            score = album_scores[a]
            # Secondary sort for Composer matches:
            # If score is 2, check if Album name contains any query token.
            # We want those to come FIRST, so we give them a sub-score.
            sub_score = 1
            if score == 2:
                a_lower = a.lower()
                if any(token in a_lower for token in query_tokens):
                    sub_score = 0 # Better
            
            return (score, sub_score, a)

        sorted_albums = sorted(album_scores.keys(), key=sort_key)
        return sorted_albums

    def get_album_tracks(self, album):
        """Returns list of file paths for an album."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path FROM tracks WHERE album = ? ORDER BY track_number, title", (album,))
            rows = cursor.fetchall()
            if rows:
                # Decode paths
                return [r[0].decode('utf-8', 'surrogateescape') for r in rows]
            return []

    def search_playlists(self, query):
        """Searches for playlists matching the query."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Simple LIKE search
            cursor.execute("SELECT path, name FROM playlists WHERE name LIKE ?", (f"%{query}%",))
            rows = cursor.fetchall()
            
            results = []
            for r in rows:
                path_bytes, name = r
                path = path_bytes.decode('utf-8', 'surrogateescape')
                results.append((name, path))
            return results

    def get_random_tracks(self, limit=50):
        """Returns a list of random tracks."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT title, path, media_type FROM tracks ORDER BY RANDOM() LIMIT ?", (limit,))
            rows = cursor.fetchall()
            
            results = []
            for r in rows:
                title, path_blob, media_type = r
                path = path_blob.decode('utf-8', 'surrogateescape')
                results.append({'title': title, 'path': path, 'media_type': media_type})
            return results
