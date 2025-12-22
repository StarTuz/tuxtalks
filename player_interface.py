from abc import ABC, abstractmethod

class MediaPlayer(ABC):
    def __init__(self, config=None, speak_func=None):
        """
        Initialize the media player.
        
        Args:
            config: Configuration object (optional)
            speak_func: function(text) to output voice feedback (optional)
        """
        self.speak_func = speak_func

    def speak(self, text):
        """Outputs voice feedback if a speaker function is registered."""
        if self.speak_func:
            self.speak_func(text)
        else:
            print(f"🗣️ [Mock Speak]: {text}")

    def announce_now_playing(self, title, artist, album=None):
        """Standard announcement for currently playing track."""
        msg = f"Playing {title} by {artist}."
        if album:
            msg += f" from album {album}."
        self.speak(msg)

    def announce_error(self, message):
        """Standard announcement for errors."""
        self.speak(f"Sorry, {message}")
        print(f"❌ {message}")

    @abstractmethod
    def play_genre(self, genre):
        pass

    @abstractmethod
    def play_random(self):
        """Play random tracks from the library."""
        pass

    @abstractmethod
    def play_artist(self, artist):
        pass

    @abstractmethod
    def play_album(self, album):
        pass

    @abstractmethod
    def play_playlist(self, playlist, shuffle=False):
        pass

    @abstractmethod
    def play_any(self, query):
        """
        Attempts to play the query. 
        Returns a tuple: (status_code, message, data)
        status_code: 0 (Done), 1 (Ask Selection), 2 (Error)
        """
        pass

    @abstractmethod
    def play_pause(self):
        pass

    @abstractmethod
    def next_track(self):
        pass

    @abstractmethod
    def previous_track(self):
        pass

    @abstractmethod
    def volume_up(self):
        pass

    @abstractmethod
    def volume_down(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def what_is_playing(self):
        pass

    @abstractmethod
    def list_tracks(self):
        pass

    @abstractmethod
    def health_check(self):
        """
        Checks if the player is running and reachable.
        Returns True if healthy, False otherwise.
        """
        pass

    @abstractmethod
    def get_artist_albums(self, artist):
        """
        Returns a list of albums for the given artist.
        Returns empty list if none found.
        """
        pass

    def get_all_artists(self, limit=50):
        """
        Returns a list of all artists in the library.
        Default implementation returns empty list - players should override.
        
        Args:
            limit: Maximum number of artists to return (default: 50)
            
        Returns:
            List of artist names (strings)
        """
        return []
    
    def get_album_tracks(self, album_name):
        """
        Returns a list of tracks for the given album.
        
        Args:
            album_name: Name of the album
            
        Returns:
            List of tuples: (track_title, track_key/path, track_number)
            or empty list if not found
        """
        return []
    
    def get_playlist_tracks(self, playlist_name):
        """
        Returns a list of tracks for the given playlist.
        
        Args:
            playlist_name: Name of the playlist
            
        Returns:
            List of tuples: (track_title, track_key/path)
            or empty list if not found
        """
        return []
