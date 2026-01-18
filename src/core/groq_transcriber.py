"""
V2T 2.0 - Groq Whisper Transcriber
Online transcription using Groq's Whisper API.
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.utils.constants import ENV_PATH
from src.core.transcriber import BaseTranscriber, TranscriptionResult


# Load environment variables
load_dotenv(ENV_PATH)


class GroqTranscriber(BaseTranscriber):
    """
    Online transcription service using Groq's Whisper Large V3 API.
    Fast and accurate, requires internet connection and API key.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq transcriber.
        
        Args:
            api_key: Groq API key, or None to load from environment
        """
        self._api_key = api_key or os.getenv("key_groq_api")
        self._client = None
    
    def _get_client(self):
        """Get or create Groq client."""
        if self._client is None and self._api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self._api_key)
            except ImportError:
                print("[GroqTranscriber] groq package not installed")
            except Exception as e:
                print(f"[GroqTranscriber] Error creating client: {e}")
        return self._client
    
    def set_api_key(self, api_key: str) -> None:
        """Update the API key."""
        self._api_key = api_key
        self._client = None  # Reset client to use new key
        
        # Also save to .env file
        try:
            with open(ENV_PATH, "w", encoding="utf-8") as f:
                f.write(f'key_groq_api = "{api_key}"')
        except Exception:
            pass
    
    def is_available(self) -> bool:
        """Check if Groq API is available (has API key)."""
        return bool(self._api_key)
    
    @property
    def name(self) -> str:
        return "Groq Whisper (Online)"
    
    def transcribe(
        self, 
        audio_path: Path, 
        language: str = "fr"
    ) -> TranscriptionResult:
        """
        Transcribe audio using Groq's Whisper API.
        
        Args:
            audio_path: Path to WAV audio file
            language: Language code (e.g., "fr", "en")
            
        Returns:
            TranscriptionResult with transcribed text
        """
        # Validate
        if not self.is_available():
            return TranscriptionResult(
                text="",
                language=language,
                duration=0.0,
                is_online=True,
                success=False,
                error="Clé API Groq non configurée"
            )
        
        if not audio_path.exists():
            return TranscriptionResult(
                text="",
                language=language,
                duration=0.0,
                is_online=True,
                success=False,
                error=f"Fichier audio introuvable: {audio_path}"
            )
        
        try:
            client = self._get_client()
            if not client:
                raise Exception("Impossible de créer le client Groq")
            
            # Get audio duration
            import wave
            with wave.open(str(audio_path), "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                duration = frames / float(rate)
            
            # Transcribe
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=(str(audio_path), audio_file.read()),
                    model="whisper-large-v3",
                    language=language,
                    temperature=0.0,
                    response_format="text"
                )
            
            text = transcription.strip() if isinstance(transcription, str) else str(transcription).strip()
            
            return TranscriptionResult(
                text=text,
                language=language,
                duration=duration,
                is_online=True,
                success=True
            )
            
        except Exception as e:
            return TranscriptionResult(
                text="",
                language=language,
                duration=0.0,
                is_online=True,
                success=False,
                error=str(e)
            )


# Global instance
groq_transcriber = GroqTranscriber()
