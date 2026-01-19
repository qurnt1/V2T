"""
V2T 2.1 - Settings Page
Configuration options for the application.
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox,
    QLineEdit, QCheckBox, QFrame, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

from src.utils.constants import Colors, TranscriptionConfig
from src.services.settings import settings
from src.core.audio_recorder import AudioRecorder
from src.core.hotkey_manager import hotkey_manager


class SettingsPage(QWidget):
    """
    Settings page for app configuration.
    Options:
    - Microphone selection
    - Language selection
    - API key input
    - Hotkey configuration
    - Online/Offline mode toggle
    - Sound effects toggle
    - Auto-stop on silence
    """
    
    # Signals
    navigate_back = pyqtSignal()
    settings_changed = pyqtSignal()
    hotkey_changed = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._capturing_hotkey = False
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self) -> None:
        """Setup the page layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # ===== Header =====
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 5)
        
        self._back_btn = QPushButton("← Retour")
        self._back_btn.setFont(QFont("Segoe UI", 10))
        self._back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: none;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                color: {Colors.ACCENT_PRIMARY};
            }}
        """)
        self._back_btn.clicked.connect(self.navigate_back.emit)
        header.addWidget(self._back_btn)
        
        header.addStretch()
        
        title = QLabel("Paramètres")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        header.addWidget(title)
        
        header.addStretch()
        
        spacer = QLabel()
        spacer.setFixedWidth(70)
        header.addWidget(spacer)
        
        layout.addLayout(header)
        
        # --- Microphone ---
        layout.addWidget(self._create_section_label("Microphone"))
        
        self._mic_combo = QComboBox()
        self._mic_combo.setStyleSheet(self._get_combo_style())
        self._mic_combo.currentIndexChanged.connect(self._on_mic_changed)
        layout.addWidget(self._mic_combo)
        
        # --- Language ---
        layout.addWidget(self._create_section_label("Langue"))
        
        self._lang_combo = QComboBox()
        self._lang_combo.setStyleSheet(self._get_combo_style())
        for name, code in TranscriptionConfig.LANGUAGES.items():
            self._lang_combo.addItem(name, code)
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        layout.addWidget(self._lang_combo)
        
        # --- API Key ---
        layout.addWidget(self._create_section_label("Clé API Groq"))
        
        api_layout = QHBoxLayout()
        api_layout.setSpacing(8)
        api_layout.setContentsMargins(0, 0, 0, 0)
        
        self._api_input = QLineEdit()
        self._api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_input.setPlaceholderText("gsk_xxx...")
        self._api_input.setStyleSheet(self._get_input_style())
        api_layout.addWidget(self._api_input, 1)
        
        self._api_save_btn = QPushButton("OK")
        self._api_save_btn.setFixedWidth(50)
        self._api_save_btn.setStyleSheet(self._get_button_style())
        self._api_save_btn.clicked.connect(self._on_api_save)
        api_layout.addWidget(self._api_save_btn)
        
        layout.addLayout(api_layout)
        
        # API link
        api_link = QLabel(
            '<a href="https://console.groq.com" style="color: #8B5CF6;">'
            'Obtenir une clé API →</a>'
        )
        api_link.setOpenExternalLinks(True)
        api_link.setFont(QFont("Segoe UI", 9))
        layout.addWidget(api_link)
        
        # --- Hotkey ---
        layout.addWidget(self._create_section_label("Raccourci clavier"))
        
        self._hotkey_btn = QPushButton("F8")
        self._hotkey_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.BG_DARK};
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_SECONDARY};
            }}
        """)
        self._hotkey_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._hotkey_btn.clicked.connect(self._on_hotkey_capture)
        layout.addWidget(self._hotkey_btn)
        
        # --- Mode ---
        layout.addWidget(self._create_section_label("Mode de transcription"))
        
        self._mode_combo = QComboBox()
        self._mode_combo.setStyleSheet(self._get_combo_style())
        self._mode_combo.addItem("Online (Groq API)", True)
        self._mode_combo.addItem("Offline (Whisper local)", False)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        layout.addWidget(self._mode_combo)
        
        # --- Toggles ---
        layout.addSpacing(5)
        
        # Auto paste toggle
        self._auto_paste_check = QCheckBox("Coller automatiquement")
        self._auto_paste_check.stateChanged.connect(self._on_auto_paste_changed)
        layout.addWidget(self._auto_paste_check)
        
        # Sound toggle
        self._sound_check = QCheckBox("Effets sonores")
        self._sound_check.stateChanged.connect(self._on_sound_changed)
        layout.addWidget(self._sound_check)

        # Silence Detection toggle
        self._silence_check = QCheckBox("Arrêt auto (silence)")
        self._silence_check.stateChanged.connect(self._on_silence_changed)
        layout.addWidget(self._silence_check)

        # Silence threshold slider (immediately under the checkbox)
        self._silence_options = QWidget()
        silence_layout = QVBoxLayout(self._silence_options)
        silence_layout.setContentsMargins(25, 2, 0, 0)
        silence_layout.setSpacing(3)

        # Label for slider value
        self._silence_label = QLabel("Durée: 3 secondes")
        self._silence_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px;")
        silence_layout.addWidget(self._silence_label)

        # Slider
        self._silence_slider = QSlider(Qt.Orientation.Horizontal)
        self._silence_slider.setMinimum(2)
        self._silence_slider.setMaximum(15)
        self._silence_slider.setValue(3)
        self._silence_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                background: {Colors.BG_INPUT};
                height: 6px;
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {Colors.ACCENT_PRIMARY};
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }}
        """)
        self._silence_slider.valueChanged.connect(self._on_silence_slider_changed)
        silence_layout.addWidget(self._silence_slider)

        layout.addWidget(self._silence_options)
        
        # Add stretch to push everything up
        layout.addStretch()
    
    def _create_section_label(self, text: str) -> QLabel:
        """Create a section label."""
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 10))
        label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        return label
    
    def _get_combo_style(self) -> str:
        return f"""
            QComboBox {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }}
            QComboBox:hover {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 22px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                selection-background-color: {Colors.ACCENT_PRIMARY};
                padding: 3px;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 5px 8px;
                min-height: 18px;
            }}
        """
    
    def _get_input_style(self) -> str:
        return f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
        """
    
    def _get_button_style(self) -> str:
        return f"""
            QPushButton {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
        """
    
    def _get_checkbox_style_on(self) -> str:
        return f"""
            QCheckBox {{
                color: {Colors.TEXT_PRIMARY};
                font-size: 12px;
                spacing: 8px;
                padding: 3px 0;
            }}
            QCheckBox::indicator {{
                width: 32px;
                height: 18px;
                border-radius: 9px;
                border: none;
                background-color: {Colors.SUCCESS};
            }}
        """
    
    def _get_checkbox_style_off(self) -> str:
        return f"""
            QCheckBox {{
                color: {Colors.TEXT_MUTED};
                font-size: 12px;
                spacing: 8px;
                padding: 3px 0;
            }}
            QCheckBox::indicator {{
                width: 32px;
                height: 18px;
                border-radius: 9px;
                border: none;
                background-color: {Colors.ERROR};
            }}
        """
    
    def _load_current_settings(self) -> None:
        """Load and display current settings."""
        # Microphones
        self._mic_combo.clear()
        self._mic_combo.addItem("Par défaut", None)
        
        devices = AudioRecorder.get_devices()
        for device in devices:
            self._mic_combo.addItem(device["name"], device["index"])
        
        current_mic = settings.get("mic_index")
        if current_mic is not None:
            for i in range(self._mic_combo.count()):
                if self._mic_combo.itemData(i) == current_mic:
                    self._mic_combo.setCurrentIndex(i)
                    break
        
        # Language
        current_lang = settings.get("language", "fr")
        for i in range(self._lang_combo.count()):
            if self._lang_combo.itemData(i) == current_lang:
                self._lang_combo.setCurrentIndex(i)
                break
        
        # API Key
        from src.core.groq_transcriber import groq_transcriber
        if groq_transcriber._api_key:
            self._api_input.setText(groq_transcriber._api_key)
        
        # Hotkey
        hotkey = settings.get("hotkey", "F8")
        self._hotkey_btn.setText(f"Touche: {hotkey}")
        
        # Mode
        use_online = settings.get("use_online", True)
        self._mode_combo.setCurrentIndex(0 if use_online else 1)
        
        # Toggles
        auto_paste = settings.get("auto_paste", True)
        self._auto_paste_check.setChecked(auto_paste)
        self._update_checkbox_style(self._auto_paste_check, auto_paste)
        
        sound_enabled = settings.get("sound_enabled", True)
        self._sound_check.setChecked(sound_enabled)
        self._update_checkbox_style(self._sound_check, sound_enabled)

        # Silence settings
        silence_enabled = settings.get("silence_detection_enabled", False)
        self._silence_check.setChecked(silence_enabled)
        self._update_checkbox_style(self._silence_check, silence_enabled)
        self._silence_options.setVisible(silence_enabled)

        silence_seconds = settings.get("silence_threshold_seconds", 3)
        self._silence_slider.setValue(silence_seconds)
        self._silence_label.setText(f"Durée: {silence_seconds} secondes")
    
    def _on_mic_changed(self, index: int) -> None:
        mic_index = self._mic_combo.itemData(index)
        settings.set("mic_index", mic_index)
        self.settings_changed.emit()
    
    def _on_lang_changed(self, index: int) -> None:
        lang_code = self._lang_combo.itemData(index)
        settings.set("language", lang_code)
        self.settings_changed.emit()
    
    def _on_api_save(self) -> None:
        api_key = self._api_input.text().strip()
        if api_key:
            from src.core.groq_transcriber import groq_transcriber
            groq_transcriber.set_api_key(api_key)
            
            self._api_save_btn.setText("✓")
            self._api_save_btn.setStyleSheet(
                self._get_button_style().replace(
                    Colors.BG_CARD, Colors.SUCCESS
                )
            )
            
            # Reset after delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, self._reset_api_button)
    
    def _reset_api_button(self) -> None:
        self._api_save_btn.setText("OK")
        self._api_save_btn.setStyleSheet(self._get_button_style())
    
    def _on_hotkey_capture(self) -> None:
        if self._capturing_hotkey:
            return
        
        self._capturing_hotkey = True
        self._hotkey_btn.setText("Appuyez...")
        self._hotkey_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WARNING};
                color: {Colors.BG_DARK};
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: 600;
            }}
        """)
        
        # Capture hotkey in thread
        import threading
        def capture():
            try:
                key = hotkey_manager.wait_for_key(timeout=5.0)
                if key:
                    settings.set("hotkey", key)
                    self.hotkey_changed.emit(key)
                    
                    # Update UI in main thread
                    from PyQt6.QtCore import QMetaObject, Qt, Q_ARG
                    QMetaObject.invokeMethod(
                        self, "_update_hotkey_display",
                        Qt.ConnectionType.QueuedConnection
                    )
            finally:
                self._capturing_hotkey = False
        
        threading.Thread(target=capture, daemon=True).start()
    
    def _update_hotkey_display(self) -> None:
        hotkey = settings.get("hotkey", "F8")
        self._hotkey_btn.setText(f"Touche: {hotkey}")
        self._hotkey_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.BG_DARK};
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_SECONDARY};
            }}
        """)
    
    def _on_mode_changed(self, index: int) -> None:
        use_online = self._mode_combo.itemData(index)
        settings.set("use_online", use_online)
        self.settings_changed.emit()
    
    def _on_auto_paste_changed(self, state: int) -> None:
        is_checked = state == Qt.CheckState.Checked.value
        settings.set("auto_paste", is_checked)
        self._update_checkbox_style(self._auto_paste_check, is_checked)
    
    def _on_sound_changed(self, state: int) -> None:
        is_checked = state == Qt.CheckState.Checked.value
        settings.set("sound_enabled", is_checked)
        self._update_checkbox_style(self._sound_check, is_checked)

    def _on_silence_changed(self, state: int) -> None:
        is_checked = state == Qt.CheckState.Checked.value
        settings.set("silence_detection_enabled", is_checked)
        self._update_checkbox_style(self._silence_check, is_checked)
        self._silence_options.setVisible(is_checked)

    def _on_silence_slider_changed(self, value: int) -> None:
        settings.set("silence_threshold_seconds", value)
        self._silence_label.setText(f"Durée: {value} secondes")
    
    def _update_checkbox_style(self, checkbox: QCheckBox, checked: bool) -> None:
        """Update checkbox style based on state."""
        if checked:
            checkbox.setStyleSheet(self._get_checkbox_style_on())
        else:
            checkbox.setStyleSheet(self._get_checkbox_style_off())
    
    def refresh(self) -> None:
        """Refresh settings display."""
        self._load_current_settings()
