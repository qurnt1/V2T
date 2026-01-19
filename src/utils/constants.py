"""
V2T 2.0 - Constants and Configuration
"""
import os
from pathlib import Path

# ===========================================
# PATHS
# ===========================================
BASE_DIR = Path(__file__).parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SOUNDS_DIR = DATA_DIR / "sounds"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
SOUNDS_DIR.mkdir(exist_ok=True)

# Files
ENV_PATH = BASE_DIR / ".env"
CONFIG_FILE = DATA_DIR / "settings.json"
DATABASE_FILE = DATA_DIR / "transcripts.db"
ICON_FILE = DATA_DIR / "icon.ico"
SOUND_FILE = SOUNDS_DIR / "pop.wav"

# ===========================================
# COLORS - Purple/Dark Theme
# ===========================================
class Colors:
    # Backgrounds
    BG_DARK = "#0D0D0D"
    BG_CARD = "#1A1A2E"
    BG_CARD_HOVER = "#252542"
    BG_INPUT = "#16162A"
    
    # Purple Accents
    ACCENT_PRIMARY = "#8B5CF6"      # Main purple
    ACCENT_SECONDARY = "#A855F7"    # Lighter purple
    ACCENT_GLOW = "#7C3AED"         # Glow effect
    ACCENT_GRADIENT_START = "#A855F7"
    ACCENT_GRADIENT_END = "#6366F1"
    
    # Text
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#9CA3AF"
    TEXT_MUTED = "#6B7280"
    
    # States
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    
    # Borders
    BORDER_DEFAULT = "#2D2D44"
    BORDER_ACTIVE = "#8B5CF6"

# ===========================================
# AUDIO SETTINGS
# ===========================================
class AudioConfig:
    SAMPLE_RATE = 16000  # 16kHz for Whisper
    CHANNELS = 1         # Mono
    CHUNK_SIZE = 1024
    DTYPE = "int16"

# ===========================================
# UI SETTINGS
# ===========================================
class UIConfig:
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 700
    WINDOW_TITLE = "V2T - Voice to Text"
    
    # Animation durations (ms)
    ANIMATION_FAST = 150
    ANIMATION_NORMAL = 300
    ANIMATION_SLOW = 500
    
    # Waveform
    WAVEFORM_BARS = 64
    WAVEFORM_HEIGHT = 80

# ===========================================
# TRANSCRIPTION SETTINGS
# ===========================================
class TranscriptionConfig:
    # Whisper model for offline
    WHISPER_MODEL = "base"  # tiny, base, small, medium, large-v3
    
    # Supported languages
    LANGUAGES = {
        "Français": "fr",
        "English": "en",
        "Español": "es",
        "Deutsch": "de",
        "Italiano": "it",
        "Português": "pt",
        "日本語": "ja",
        "中文": "zh"
    }
    
    # Default language
    DEFAULT_LANGUAGE = "fr"

# ===========================================
# DEFAULT SETTINGS
# ===========================================
DEFAULT_SETTINGS = {
    "mic_index": None,
    "language": "fr",
    "hotkey": "F8",
    "use_online": True,      # True = Groq, False = Offline Whisper
    "auto_paste": True,
    "sound_enabled": True,
    "silence_detection_enabled": False,
    "silence_threshold_seconds": 3,
    "theme": "dark"
}
