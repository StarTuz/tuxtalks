from .vosk_asr import VoskASR
from .piper_tts import PiperTTS
from .system_tts import SystemTTS
try:
    from .whisper_asr import WhisperASR
except ImportError:
    WhisperASR = None
try:
    from .wyoming_asr import WyomingASR
except ImportError:
    WyomingASR = None


# Metadata Registry
ENGINES = {
    "ASR": {
        "vosk": {
            "class": VoskASR,
            "name": "Vosk (Offline)",
            "description": "Fast, privacy-focused offline recognition. Default.",
            "pros": ["Stable", "Low Latency"],
            "cons": ["Limited Vocabulary"],
            "experimental": False,
            "recommended": True
        },
        "wyoming": {
            "class": WyomingASR,
            "name": "Wyoming (External)",
            "description": "Connects to external server (e.g. wyoming-faster-whisper). Safe & Powerful.",
            "pros": ["High Accuracy (Whisper)", "Zero Crashes (Isolated)"],
            "cons": ["Requires running external server"],
            "experimental": False,
            "recommended": False
        }
    },
    "TTS": {
        "piper": {
            "class": PiperTTS,
            "name": "Piper Neural TTS",
            "description": "High-quality neural text-to-speech. Runs offline.",
            "pros": ["Near-human quality", "Fast", "Offline"],
            "cons": ["Limited voices (installed manually)"],
            "experimental": False,
            "recommended": True
        },
        "system": {
            "class": SystemTTS,
            "name": "System (eSpeak)",
            "description": "Basic robotic system synthesizer.",
            "pros": ["Always available", "Zero latency"],
            "cons": ["Robotic voice", "Low quality"],
            "experimental": False,
            "recommended": False
        }
    }
}

def get_asr_engine(name, config):
    start_info = ENGINES["ASR"].get(name) or ENGINES["ASR"]["vosk"]
    cls = start_info["class"]
    return cls(config)

def get_tts_engine(name, config):
    start_info = ENGINES["TTS"].get(name) or ENGINES["TTS"]["piper"]
    cls = start_info["class"]
    return cls(config)
