"""
V2T 2.0 - Main Window
Central window managing all pages and navigation.
"""
import threading
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget,
    QVBoxLayout, QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QIcon

import pyperclip
import numpy as np

from src.utils.constants import Colors, UIConfig, ICON_FILE
from src.ui.styles.theme import get_main_stylesheet
from src.ui.pages.home_page import HomePage
from src.ui.pages.history_page import HistoryPage
from src.ui.pages.settings_page import SettingsPage
from src.core.audio_recorder import AudioRecorder
from src.core.hotkey_manager import hotkey_manager
from src.core.groq_transcriber import groq_transcriber
from src.core.whisper_transcriber import whisper_transcriber
from src.services.settings import settings
from src.services.storage import storage


class MainWindow(QMainWindow):
    """
    Main application window.
    Manages page navigation and core functionality.
    """
    
    # Internal signals for thread-safe UI updates
    _transcription_complete = pyqtSignal(str, bool)
    _audio_data_ready = pyqtSignal(object)
    _hotkey_triggered = pyqtSignal()  # Thread-safe hotkey signal
    _show_notification = pyqtSignal(str, str)  # title, message
    
    def __init__(self):
        super().__init__()
        
        self._audio_recorder: Optional[AudioRecorder] = None
        self._is_recording = False
        self._is_transcribing = False
        self._current_audio_data: Optional[np.ndarray] = None
        self._tray_manager = None
        
        self._setup_window()
        self._setup_pages()
        self._setup_connections()
        self._setup_hotkey()
        self._setup_audio()
    
    def set_tray_manager(self, tray_manager) -> None:
        """Set the tray manager for notifications."""
        self._tray_manager = tray_manager
    
    def _setup_window(self) -> None:
        """Setup main window properties."""
        self.setWindowTitle(UIConfig.WINDOW_TITLE)
        self.setFixedSize(UIConfig.WINDOW_WIDTH, UIConfig.WINDOW_HEIGHT)
        
        # Set window icon
        if ICON_FILE.exists():
            self.setWindowIcon(QIcon(str(ICON_FILE)))
        
        # Apply stylesheet
        self.setStyleSheet(get_main_stylesheet())
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Stacked widget for pages
        self._stack = QStackedWidget()
        layout.addWidget(self._stack)
    
    def _setup_pages(self) -> None:
        """Create and add all pages."""
        # Home page
        self._home_page = HomePage()
        self._stack.addWidget(self._home_page)
        
        # History page
        self._history_page = HistoryPage()
        self._stack.addWidget(self._history_page)
        
        # Settings page
        self._settings_page = SettingsPage()
        self._stack.addWidget(self._settings_page)
        
        # Start on home
        self._stack.setCurrentWidget(self._home_page)
    
    def _setup_connections(self) -> None:
        """Connect all signals."""
        # Home page
        self._home_page.recording_toggled.connect(self._on_recording_toggled)
        self._home_page.navigate_settings.connect(self._show_settings)
        self._home_page.navigate_history.connect(self._show_history)
        
        # History page
        self._history_page.navigate_back.connect(self._show_home)
        self._history_page.text_copied.connect(self._copy_to_clipboard)
        self._history_page.notification_requested.connect(self._on_notification_requested)
        
        # Settings page
        self._settings_page.navigate_back.connect(self._show_home)
        self._settings_page.settings_changed.connect(self._on_settings_changed)
        self._settings_page.hotkey_changed.connect(self._on_hotkey_changed)
        
        # Internal signals (thread-safe)
        self._transcription_complete.connect(self._on_transcription_result)
        self._audio_data_ready.connect(self._on_audio_data)
        self._hotkey_triggered.connect(self._on_hotkey_main_thread)
        self._show_notification.connect(self._on_show_notification)
    
    def _setup_hotkey(self) -> None:
        """Setup global hotkey."""
        hotkey = settings.get("hotkey", "F8")
        # Use a lambda that emits a signal instead of direct UI manipulation
        hotkey_manager.register(hotkey, self._emit_hotkey_signal)
        self._home_page.update_hotkey_text(hotkey)
    
    def _emit_hotkey_signal(self) -> None:
        """Emit hotkey signal from any thread (thread-safe)."""
        self._hotkey_triggered.emit()
    
    def _on_hotkey_main_thread(self) -> None:
        """Handle hotkey press in main thread."""
        self._toggle_recording()
    
    def _setup_audio(self) -> None:
        """Setup audio recorder."""
        mic_index = settings.get("mic_index")
        self._audio_recorder = AudioRecorder(device_index=mic_index)
        self._audio_recorder.set_audio_callback(self._on_audio_callback)
    
    # === Navigation ===
    
    def _show_home(self) -> None:
        """Navigate to home page."""
        self._stack.setCurrentWidget(self._home_page)
    
    def _show_history(self) -> None:
        """Navigate to history page."""
        self._history_page.load_transcripts()
        self._stack.setCurrentWidget(self._history_page)
    
    def _show_settings(self) -> None:
        """Navigate to settings page."""
        self._settings_page.refresh()
        self._stack.setCurrentWidget(self._settings_page)
    
    # === Recording ===
    
    def _on_recording_toggled(self, recording: bool) -> None:
        """Handle recording toggle from UI."""
        if recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _toggle_recording(self) -> None:
        """Toggle recording state."""
        if self._is_transcribing:
            return  # Don't toggle while transcribing
        
        if self._is_recording:
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self) -> None:
        """Start audio recording."""
        if self._is_recording or self._is_transcribing:
            return
        
        # Play start sound
        self._play_sound()
        
        # Update UI
        self._is_recording = True
        self._home_page.set_recording(True)
        
        # Start recorder
        if self._audio_recorder:
            self._audio_recorder.start()
    
    def _stop_recording(self) -> None:
        """Stop recording and start transcription."""
        if not self._is_recording:
            return
        
        # Play stop sound
        self._play_sound()
        
        # Update UI
        self._is_recording = False
        self._home_page.set_recording(False)
        
        # Stop recorder and get audio
        if self._audio_recorder:
            audio_data = self._audio_recorder.stop()
            
            if audio_data is not None and len(audio_data) > 0:
                self._current_audio_data = audio_data
                self._is_transcribing = True
                self._home_page.set_transcribing(True)
                self._start_transcription(audio_data)
            else:
                # No audio recorded
                self._home_page.update_waveform(None)
    
    def _on_audio_callback(self, audio_chunk: np.ndarray) -> None:
        """Handle real-time audio data from recorder."""
        # Emit signal to update UI in main thread
        self._audio_data_ready.emit(audio_chunk)
    
    def _on_audio_data(self, audio_chunk) -> None:
        """Update waveform with audio data (main thread)."""
        if self._is_recording:
            self._home_page.update_waveform(audio_chunk)
    
    # === Transcription ===
    
    def _start_transcription(self, audio_data: np.ndarray) -> None:
        """Start transcription in background thread."""
        def transcribe():
            try:
                # Save audio to temp file
                audio_path = self._audio_recorder.save_to_file(audio_data)
                if not audio_path:
                    self._transcription_complete.emit("Erreur: impossible de sauvegarder l'audio", False)
                    return
                
                language = settings.get("language", "fr")
                use_online = settings.get("use_online", True)
                
                # Choose transcriber
                if use_online and groq_transcriber.is_available():
                    result = groq_transcriber.transcribe(audio_path, language)
                else:
                    result = whisper_transcriber.transcribe(audio_path, language)
                
                # Clean up temp file
                try:
                    audio_path.unlink()
                except Exception:
                    pass
                
                if result.success:
                    # Save to history
                    storage.save(
                        text=result.text,
                        language=result.language,
                        duration=result.duration,
                        is_online=result.is_online
                    )
                    
                    # Copy to clipboard
                    try:
                        pyperclip.copy(result.text)
                    except Exception:
                        pass
                    
                    # Auto-paste if enabled
                    if settings.get("auto_paste", True):
                        self._auto_paste(result.text)
                    
                    self._transcription_complete.emit(result.text, True)
                else:
                    self._transcription_complete.emit(result.error or "Erreur inconnue", False)
                    
            except Exception as e:
                self._transcription_complete.emit(str(e), False)
        
        threading.Thread(target=transcribe, daemon=True).start()
    
    def _auto_paste(self, text: str) -> None:
        """Simulate Ctrl+V (runs in transcription thread)."""
        try:
            import time
            time.sleep(0.05)
            import keyboard
            keyboard.press_and_release("ctrl+v")
        except Exception as e:
            print(f"[Clipboard] Error pasting: {e}")
    
    def _on_transcription_result(self, text: str, success: bool) -> None:
        """Handle transcription result (main thread)."""
        self._is_transcribing = False
        
        if success:
            self._home_page.set_transcription_result(True, "Transcription terminée (Copié !)")
        else:
            self._home_page.set_transcription_result(False, f"Erreur: {text}")
        
        # Reset status after 3 seconds
        QTimer.singleShot(3000, self._reset_transcription_status)
    
    def _reset_transcription_status(self) -> None:
        """Reset transcription status label."""
        if not self._is_recording and not self._is_transcribing:
            self._home_page.set_transcribing(False)
    
    # === Clipboard ===
    
    def _copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard and show feedback."""
        try:
            pyperclip.copy(text)
        except Exception as e:
            print(f"[Clipboard] Error: {e}")
    
    # === Notifications ===
    
    def _on_notification_requested(self, title: str, message: str) -> None:
        """Handle notification request from other pages."""
        self._show_notification.emit(title, message)
    
    def _on_show_notification(self, title: str, message: str) -> None:
        """Show notification via tray (main thread)."""
        if self._tray_manager:
            self._tray_manager.show_notification(title, message)
    
    # === Sound ===
    
    def _play_sound(self) -> None:
        """Play feedback sound."""
        if not settings.get("sound_enabled", True):
            return
        
        # Simple beep for now
        try:
            import winsound
            winsound.Beep(800, 100)
        except Exception:
            pass
    
    # === Settings ===
    
    def _on_settings_changed(self) -> None:
        """Handle settings change."""
        # Update audio device
        mic_index = settings.get("mic_index")
        if self._audio_recorder:
            self._audio_recorder.set_device(mic_index)
    
    def _on_hotkey_changed(self, new_hotkey: str) -> None:
        """Handle hotkey change."""
        old_hotkey = settings.get("hotkey", "F8")
        
        hotkey_manager.update_hotkey(
            old_hotkey, 
            new_hotkey, 
            self._emit_hotkey_signal  # Use signal emitter, not direct callback
        )
        
        self._home_page.update_hotkey_text(new_hotkey)
    
    # === Window Events ===
    
    def showEvent(self, event) -> None:
        """Handle window show - restart animations."""
        super().showEvent(event)
        # Use QTimer.singleShot to ensure we're in the main thread
        QTimer.singleShot(0, self._restart_animations)
    
    def _restart_animations(self) -> None:
        """Restart animations (called from main thread)."""
        try:
            self._home_page._waveform.start()
            self._home_page._mic_button._pulse_timer.start(30)
        except Exception:
            pass
        # Force repaint
        self.repaint()
        self.update()
    
    def hideEvent(self, event) -> None:
        """Handle window hide - pause animations to save CPU."""
        super().hideEvent(event)
        # Stop animations to save resources
        try:
            self._home_page._waveform.stop()
            self._home_page._mic_button._pulse_timer.stop()
        except Exception:
            pass
    
    def closeEvent(self, event) -> None:
        """Handle window close - hide to tray instead of quitting."""
        # Hide window instead of closing
        self.hide()
        event.ignore()  # Don't actually close
    
    def force_quit(self) -> None:
        """Force quit the application (called from tray menu)."""
        # Stop recording if active
        if self._is_recording and self._audio_recorder:
            self._audio_recorder.stop()
        
        # Unregister hotkeys
        hotkey_manager.unregister_all()
        
        # Cleanup pages
        self._home_page.cleanup()
        
        # Accept close
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
