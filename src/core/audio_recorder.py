"""
V2T 2.1 - Audio Recorder
Handles microphone capture using sounddevice.
"""
import threading
import queue
import tempfile
import wave
from typing import Optional, Callable, List
import time
from pathlib import Path

import numpy as np
import sounddevice as sd

from src.utils.constants import AudioConfig, DATA_DIR


class AudioRecorder:
    """
    Real-time audio recorder using sounddevice.
    Captures audio and provides level data for visualization.
    """
    
    def __init__(self, device_index: Optional[int] = None):
        """
        Initialize the audio recorder.
        
        Args:
            device_index: Specific device index, or None for default
        """
        self.device_index = device_index
        self.sample_rate = AudioConfig.SAMPLE_RATE
        self.channels = AudioConfig.CHANNELS
        self.chunk_size = AudioConfig.CHUNK_SIZE
        
        self._stream: Optional[sd.InputStream] = None
        self._frames: List[np.ndarray] = []
        self._is_recording = False
        self._lock = threading.Lock()
        
        # Callback for real-time audio data (for waveform visualization)
        self._on_audio_data: Optional[Callable[[np.ndarray], None]] = None
        self._on_silence_detected: Optional[Callable[[], None]] = None
        
        # Silence detection
        self._last_sound_time = 0.0
        self._silence_threshold_amp = 0.02  # Amplitude threshold (0.0 - 1.0)
        self._silence_limit = 3.0  # Seconds before stopping
        
        # Queue for audio chunks (thread-safe)
        self._audio_queue: queue.Queue = queue.Queue()
    
    @staticmethod
    def get_devices() -> List[dict]:
        """
        Get list of available input devices.
        
        Returns:
            List of dicts with 'index' and 'name' keys
        """
        devices = []
        try:
            device_list = sd.query_devices()
            for i, device in enumerate(device_list):
                if device.get("max_input_channels", 0) > 0:
                    devices.append({
                        "index": i,
                        "name": device.get("name", f"Device {i}"),
                        "channels": device.get("max_input_channels", 1),
                        "sample_rate": device.get("default_samplerate", 44100)
                    })
        except Exception as e:
            print(f"[AudioRecorder] Error getting devices: {e}")
        return devices
    
    @staticmethod
    def get_default_device() -> Optional[int]:
        """Get the default input device index."""
        try:
            return sd.default.device[0]  # Input device
        except Exception:
            return None
    
    def set_device(self, device_index: Optional[int]) -> None:
        """Set the input device to use."""
        self.device_index = device_index
    
    def set_audio_callback(self, callback: Callable[[np.ndarray], None]) -> None:
        """
        Set callback for real-time audio data.
        The callback receives numpy array of audio samples.
        """
        self._on_audio_data = callback
        
    def set_silence_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for silence detected."""
        self._on_silence_detected = callback
        
    def update_silence_threshold(self, limit_seconds: float) -> None:
        """Update silence limit in seconds."""
        self._silence_limit = limit_seconds
    
    def _audio_callback(
        self, 
        indata: np.ndarray, 
        frames: int, 
        time_info, 
        status
    ) -> None:
        """Internal callback for sounddevice stream."""
        if status:
            print(f"[AudioRecorder] Stream status: {status}")
        
        # Copy data
        audio_chunk = indata.copy()
        
        with self._lock:
            if self._is_recording:
                self._frames.append(audio_chunk)
        
        # Send to visualization callback
        if self._on_audio_data:
            try:
                self._on_audio_data(audio_chunk.flatten())
            except Exception:
                pass
    
    def start(self) -> bool:
        """
        Start recording audio.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self._is_recording:
            return True
        
        try:
            with self._lock:
                self._frames = []
                self._is_recording = True
                self._last_sound_time = time.time()  # Reset silence timer
            
            self._stream = sd.InputStream(
                device=self.device_index,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.int16,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            self._stream.start()
            return True
            
        except Exception as e:
            print(f"[AudioRecorder] Error starting: {e}")
            self._is_recording = False
            return False
    
    def stop(self) -> Optional[np.ndarray]:
        """
        Stop recording and return the recorded audio.
        
        Returns:
            Numpy array of recorded audio, or None if error
        """
        if not self._is_recording:
            return None
        
        try:
            with self._lock:
                self._is_recording = False
            
            if self._stream:
                self._stream.stop()
                self._stream.close()
                self._stream = None
            
            with self._lock:
                if not self._frames:
                    return None
                audio_data = np.concatenate(self._frames, axis=0)
                self._frames = []
            
            return audio_data
            
        except Exception as e:
            print(f"[AudioRecorder] Error stopping: {e}")
            return None
    
    def save_to_file(self, audio_data: np.ndarray, filename: Optional[str] = None) -> Optional[Path]:
        """
        Save audio data to a WAV file.
        
        Args:
            audio_data: Numpy array of audio samples
            filename: Optional filename, auto-generated if None
            
        Returns:
            Path to saved file, or None if error
        """
        if audio_data is None or len(audio_data) == 0:
            return None
        
        try:
            if filename:
                filepath = DATA_DIR / filename
            else:
                # Create temp file
                fd, temp_path = tempfile.mkstemp(suffix=".wav", prefix="v2t_")
                filepath = Path(temp_path)
            
            # Ensure int16 format
            if audio_data.dtype != np.int16:
                audio_data = (audio_data * 32767).astype(np.int16)
            
            with wave.open(str(filepath), "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit = 2 bytes
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data.tobytes())
            
            return filepath
            
        except Exception as e:
            print(f"[AudioRecorder] Error saving file: {e}")
            return None
    
    def get_duration(self, audio_data: np.ndarray) -> float:
        """Get duration of audio data in seconds."""
        if audio_data is None or len(audio_data) == 0:
            return 0.0
        return len(audio_data) / self.sample_rate
    
    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
    
    def get_rms_level(self, audio_data: np.ndarray) -> float:
        """
        Calculate RMS (volume level) of audio data.
        
        Returns:
            RMS value normalized to 0.0 - 1.0
        """
        if audio_data is None or len(audio_data) == 0:
            return 0.0
        
        # Calculate RMS
        rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
        
        # Normalize (assuming 16-bit audio max of 32767)
        normalized = min(rms / 32767 * 10, 1.0)  # Scale up for visibility
        
        return normalized
