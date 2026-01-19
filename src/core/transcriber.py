"""
V2T 2.1 - Transcriber Interface
Abstract base class for transcription services.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""
    text: str
    language: str
    duration: float  # Duration of audio in seconds
    is_online: bool  # True if transcribed via API, False if local
    success: bool
    error: Optional[str] = None


class BaseTranscriber(ABC):
    """
    Abstract base class for transcription services.
    Implementations must provide transcribe() method.
    """
    
    @abstractmethod
    def transcribe(
        self, 
        audio_path: Path, 
        language: str = "fr"
    ) -> TranscriptionResult:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file (WAV format)
            language: Language code (e.g., "fr", "en")
            
        Returns:
            TranscriptionResult with transcribed text or error
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this transcription service is available.
        
        Returns:
            True if the service can be used
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Service name for display."""
        pass
