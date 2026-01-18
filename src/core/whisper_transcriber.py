"""
V2T 2.0 - Whisper Local Transcriber
Offline transcription using faster-whisper (CTranslate2).
"""
import threading
from pathlib import Path
from typing import Optional

from src.utils.constants import TranscriptionConfig
from src.core.transcriber import BaseTranscriber, TranscriptionResult


class WhisperTranscriber(BaseTranscriber):
    """
    Offline transcription using faster-whisper.
    Uses local Whisper model for transcription without internet.
    """
    
    _instance: Optional["WhisperTranscriber"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "WhisperTranscriber":
        """Singleton pattern - only one model instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, model_size: str = None):
        """
        Initialize Whisper transcriber.
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large-v3)
        """
        if self._initialized:
            return
        
        self._model_size = model_size or TranscriptionConfig.WHISPER_MODEL
        self._model = None
        self._model_loading = False
        self._model_loaded = False
        self._load_error: Optional[str] = None
        self._initialized = True
    
    def _load_model(self) -> bool:
        """
        Load the Whisper model (lazy loading).
        Downloads model on first use if not cached.
        """
        if self._model_loaded:
            return True
        
        if self._model_loading:
            return False
        
        self._model_loading = True
        
        try:
            from faster_whisper import WhisperModel
            
            # Check for CUDA without requiring torch
            device = "cpu"
            compute_type = "int8"
            
            try:
                import ctranslate2
                if "cuda" in ctranslate2.get_supported_compute_types("cuda"):
                    device = "cuda"
                    compute_type = "float16"
                    print("[WhisperTranscriber] Using CUDA GPU")
                else:
                    print("[WhisperTranscriber] Using CPU")
            except Exception:
                print("[WhisperTranscriber] Using CPU (CUDA not available)")
            
            print(f"[WhisperTranscriber] Loading model '{self._model_size}'...")
            
            self._model = WhisperModel(
                self._model_size,
                device=device,
                compute_type=compute_type
            )
            
            self._model_loaded = True
            self._load_error = None
            print("[WhisperTranscriber] Model loaded successfully")
            return True
            
        except ImportError as e:
            self._load_error = f"Dépendance manquante: {e}"
            print(f"[WhisperTranscriber] {self._load_error}")
            
        except Exception as e:
            self._load_error = str(e)
            print(f"[WhisperTranscriber] Error loading model: {e}")
        
        finally:
            self._model_loading = False
        
        return False

    
    def load_async(self, callback: Optional[callable] = None) -> None:
        """
        Load the model asynchronously in a background thread.
        
        Args:
            callback: Function to call when loading completes (success: bool)
        """
        def _load():
            success = self._load_model()
            if callback:
                callback(success)
        
        thread = threading.Thread(target=_load, daemon=True)
        thread.start()
    
    def is_available(self) -> bool:
        """Check if the transcriber is ready to use."""
        return self._model_loaded
    
    def is_loading(self) -> bool:
        """Check if model is currently loading."""
        return self._model_loading
    
    @property
    def name(self) -> str:
        return f"Whisper Local ({self._model_size})"
    
    @property
    def load_error(self) -> Optional[str]:
        """Get error message if model failed to load."""
        return self._load_error
    
    def transcribe(
        self, 
        audio_path: Path, 
        language: str = "fr"
    ) -> TranscriptionResult:
        """
        Transcribe audio using local Whisper model.
        
        Args:
            audio_path: Path to WAV audio file
            language: Language code (e.g., "fr", "en")
            
        Returns:
            TranscriptionResult with transcribed text
        """
        # Ensure model is loaded
        if not self._model_loaded:
            if not self._load_model():
                return TranscriptionResult(
                    text="",
                    language=language,
                    duration=0.0,
                    is_online=False,
                    success=False,
                    error=self._load_error or "Impossible de charger le modèle Whisper"
                )
        
        if not audio_path.exists():
            return TranscriptionResult(
                text="",
                language=language,
                duration=0.0,
                is_online=False,
                success=False,
                error=f"Fichier audio introuvable: {audio_path}"
            )
        
        try:
            # Transcribe with VAD filter for better results
            segments, info = self._model.transcribe(
                str(audio_path),
                language=language,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500
                )
            )
            
            # Combine all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())
            
            text = " ".join(text_parts)
            
            return TranscriptionResult(
                text=text,
                language=language,
                duration=info.duration,
                is_online=False,
                success=True
            )
            
        except Exception as e:
            return TranscriptionResult(
                text="",
                language=language,
                duration=0.0,
                is_online=False,
                success=False,
                error=str(e)
            )
    
    def unload_model(self) -> None:
        """Unload the model to free memory."""
        if self._model:
            del self._model
            self._model = None
            self._model_loaded = False
            
            # Try to free GPU memory via ctranslate2
            try:
                import gc
                gc.collect()
            except Exception:
                pass


# Global instance
whisper_transcriber = WhisperTranscriber()
