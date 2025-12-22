from abc import ABC, abstractmethod

class ASRBase(ABC):
    """Abstract Base Class for ASR (Speech-to-Text) Engines."""
    
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def start(self, input_device_index=None):
        """Start the ASR stream."""
        pass

    @abstractmethod
    def stop(self):
        """Stop the ASR stream."""
        pass

    @abstractmethod
    def get_next_text(self):
        """
        Blocking call to get the next recognized text segment.
        Returns:
            dict: {"text": str, "mode": "wake"|"command"} or similar metadata
            OR just str (simpler)
        """
        pass
    
    def health_check(self):
        return True

    def pause(self):
        """Pause listening (e.g. while speaking)."""
        pass
        
    def resume(self):
        """Resume listening."""
        pass

    def set_grammar(self, vocabulary: list[str]):
        """
        Set the grammar/vocabulary for the ASR engine.
        Args:
            vocabulary: List of strings (phrases) to recognize.
        """
        pass

class TTSBase(ABC):
    """Abstract Base Class for TTS (Text-to-Speech) Engines."""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def speak(self, text):
        """Speak the text. Should block until audio starts or is queued?"""
        pass

    @abstractmethod
    def stop(self):
        """Stop current speech immediately."""
        pass
        
    def health_check(self):
        return True
