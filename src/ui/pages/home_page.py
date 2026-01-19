"""
V2T 2.0 - Home Page
Main recording screen with microphone button and waveform.
"""
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QCursor

from src.utils.constants import Colors, UIConfig
from src.ui.widgets.waveform import WaveformWidget
from src.ui.widgets.mic_button import MicButton


class HomePage(QWidget):
    """
    Main home page with:
    - App title and icon
    - Microphone button (start/stop recording)
    - Waveform visualization
    - Transcription status feedback
    - Navigation buttons (Settings, History)
    """
    
    # Signals
    recording_toggled = pyqtSignal(bool)  # Emitted when recording starts/stops
    navigate_settings = pyqtSignal()
    navigate_history = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._is_recording = False
        self._is_transcribing = False
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the page layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(0)
        
        # ===== Header =====
        header = QHBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Voice to Text")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        header.addWidget(title)
        
        layout.addLayout(header)
        
        # Spacer
        layout.addSpacing(40)
        
        # ===== Microphone Button =====
        mic_container = QHBoxLayout()
        mic_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._mic_button = MicButton()
        self._mic_button.set_on_click(self._on_mic_click)
        mic_container.addWidget(self._mic_button)
        
        layout.addLayout(mic_container)
        
        # Status text
        self._status_label = QLabel("Appuyez pour enregistrer")
        self._status_label.setFont(QFont("Segoe UI", 12))
        self._status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self._status_label)
        
        # Hotkey hint
        self._hotkey_label = QLabel("ou appuyez sur F8")
        self._hotkey_label.setFont(QFont("Segoe UI", 10))
        self._hotkey_label.setStyleSheet(f"color: {Colors.TEXT_MUTED};")
        self._hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._hotkey_label)
        
        # Spacer
        layout.addStretch(1)
        
        # ===== Waveform =====
        self._waveform = WaveformWidget()
        layout.addWidget(self._waveform)
        
        # Spacer
        layout.addStretch(1)
        
        # ===== Bottom Navigation =====
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(20)
        
        # Settings button
        self._settings_btn = QPushButton("⚙️ Paramètres")
        self._settings_btn.setFont(QFont("Segoe UI", 11))
        self._settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._settings_btn.setStyleSheet(self._get_nav_button_style())
        self._settings_btn.clicked.connect(self.navigate_settings.emit)
        nav_layout.addWidget(self._settings_btn)
        
        # Center spacer / Play button (optional)
        nav_layout.addStretch()
        
        # History button
        self._history_btn = QPushButton("📂 Historique")
        self._history_btn.setFont(QFont("Segoe UI", 11))
        self._history_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._history_btn.setStyleSheet(self._get_nav_button_style())
        self._history_btn.clicked.connect(self.navigate_history.emit)
        nav_layout.addWidget(self._history_btn)
        
        layout.addLayout(nav_layout)
    
    def _get_nav_button_style(self) -> str:
        """Get style for navigation buttons."""
        return f"""
            QPushButton {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 10px 20px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.ACCENT_PRIMARY};
            }}
        """
    
    def _on_mic_click(self) -> None:
        """Handle microphone button click."""
        if self._is_transcribing:
            return  # Don't allow clicks while transcribing
        
        self._is_recording = not self._is_recording
        self.set_recording(self._is_recording)
        self.recording_toggled.emit(self._is_recording)
    
    def set_recording(self, recording: bool) -> None:
        """Update UI for recording state."""
        self._is_recording = recording
        self._mic_button.set_recording(recording)
        
        if recording:
            self._status_label.setText("Enregistrement en cours...")
            self._status_label.setStyleSheet(f"color: {Colors.ERROR};")
            self._hotkey_label.setText("Appuyez à nouveau pour arrêter")
        else:
            if not self._is_transcribing:
                self._status_label.setText("Appuyez pour enregistrer")
                self._status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
                self._hotkey_label.setText("ou appuyez sur F8")
    
    def set_transcribing(self, transcribing: bool) -> None:
        """Update UI for transcribing state."""
        self._is_transcribing = transcribing
        
        if transcribing:
            self._status_label.setText("Transcription en cours...")
            self._status_label.setStyleSheet(f"color: {Colors.ACCENT_PRIMARY};")
            self._hotkey_label.setText("Veuillez patienter")
            self._mic_button.setEnabled(False)
        else:
            self._status_label.setText("Appuyez pour enregistrer")
            self._status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
            self._hotkey_label.setText("ou appuyez sur F8")
            self._mic_button.setEnabled(True)
    
    def set_transcription_result(self, success: bool, message: str) -> None:
        """Show transcription result feedback."""
        self._is_transcribing = False
        self._mic_button.setEnabled(True)
        
        if success:
            self._status_label.setText("Transcription terminée (Copié !) ✓")
            self._status_label.setStyleSheet(f"color: {Colors.SUCCESS};")
        else:
            self._status_label.setText(message)
            self._status_label.setStyleSheet(f"color: {Colors.ERROR};")
        
        self._hotkey_label.setText("ou appuyez sur F8")
    
    def update_hotkey_text(self, hotkey: str) -> None:
        """Update the hotkey hint text."""
        if not self._is_recording and not self._is_transcribing:
            self._hotkey_label.setText(f"ou appuyez sur {hotkey}")
    
    def update_waveform(self, audio_data) -> None:
        """Update waveform with audio data."""
        if audio_data is not None:
            self._waveform.set_audio_data(audio_data)
        else:
            self._waveform.set_idle()
    
    @property
    def is_recording(self) -> bool:
        return self._is_recording
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self._waveform.stop()
        self._mic_button.stop()
