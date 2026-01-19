"""
V2T 2.1 - Transcribing Page
Shows transcription progress and result.
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QCursor, QColor

from src.utils.constants import Colors


class TranscribingPage(QWidget):
    """
    Page shown during transcription.
    Features:
    - Animated waveform line
    - "Transcribing..." text with animated dots
    - Result text area with fade-in effect
    - Cancel and Copy buttons
    """
    
    # Signals
    cancelled = pyqtSignal()
    copy_requested = pyqtSignal(str)
    done = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._dots_count = 0
        self._transcribed_text = ""
        self._is_complete = False
        
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self) -> None:
        """Setup the page layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 20, 20)
        layout.setSpacing(20)
        
        # ===== Header =====
        header = QHBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Voice to Text")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        header.addWidget(title)
        
        icon_label = QLabel(" 👽")
        icon_label.setFont(QFont("Segoe UI", 22))
        header.addWidget(icon_label)
        
        layout.addLayout(header)
        
        # ===== Animated Line =====
        self._wave_line = QLabel()
        self._wave_line.setFixedHeight(60)
        self._wave_line.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0.5, x2:1, y2:0.5,
                stop:0 transparent,
                stop:0.3 {Colors.ACCENT_PRIMARY},
                stop:0.5 {Colors.ACCENT_SECONDARY},
                stop:0.7 {Colors.ACCENT_PRIMARY},
                stop:1 transparent
            );
            border-radius: 2px;
        """)
        layout.addWidget(self._wave_line)
        
        # ===== Status Text =====
        self._status_label = QLabel("Transcribing...")
        self._status_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._status_label.setStyleSheet(f"color: {Colors.ACCENT_PRIMARY};")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._status_label)
        
        # ===== Result Text Area =====
        self._text_area = QTextEdit()
        self._text_area.setReadOnly(True)
        self._text_area.setFont(QFont("Segoe UI", 12))
        self._text_area.setPlaceholderText("Le texte transcrit apparaîtra ici...")
        self._text_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 12px;
                padding: 16px;
            }}
        """)
        self._text_area.setMinimumHeight(150)
        layout.addWidget(self._text_area, 1)
        
        # ===== Buttons =====
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Cancel button
        self._cancel_btn = QPushButton("Annuler")
        self._cancel_btn.setFont(QFont("Segoe UI", 11))
        self._cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 12px 30px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ERROR};
                color: {Colors.ERROR};
            }}
        """)
        self._cancel_btn.clicked.connect(self._on_cancel)
        buttons_layout.addWidget(self._cancel_btn)
        
        # Copy button (hidden initially)
        self._copy_btn = QPushButton("📋 Copier le texte")
        self._copy_btn.setFont(QFont("Segoe UI", 11))
        self._copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.BG_DARK};
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_SECONDARY};
            }}
        """)
        self._copy_btn.clicked.connect(self._on_copy)
        self._copy_btn.hide()
        buttons_layout.addWidget(self._copy_btn)
        
        # Done button (hidden initially)
        self._done_btn = QPushButton("✓ Terminé")
        self._done_btn.setFont(QFont("Segoe UI", 11))
        self._done_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._done_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self._done_btn.clicked.connect(self.done.emit)
        self._done_btn.hide()
        buttons_layout.addWidget(self._done_btn)
        
        layout.addLayout(buttons_layout)
    
    def _setup_animations(self) -> None:
        """Setup the dots animation timer."""
        self._dots_timer = QTimer(self)
        self._dots_timer.timeout.connect(self._update_dots)
        self._dots_timer.start(500)
    
    def _update_dots(self) -> None:
        """Update the animated dots."""
        if self._is_complete:
            return
        
        self._dots_count = (self._dots_count + 1) % 4
        dots = "." * self._dots_count
        self._status_label.setText(f"Transcribing{dots}")
    
    def _on_cancel(self) -> None:
        """Handle cancel button."""
        self.cancelled.emit()
    
    def _on_copy(self) -> None:
        """Handle copy button."""
        if self._transcribed_text:
            self.copy_requested.emit(self._transcribed_text)
    
    def start(self) -> None:
        """Start transcription UI."""
        self._is_complete = False
        self._transcribed_text = ""
        self._text_area.clear()
        self._status_label.setText("Transcribing...")
        self._status_label.setStyleSheet(f"color: {Colors.ACCENT_PRIMARY};")
        
        self._cancel_btn.show()
        self._copy_btn.hide()
        self._done_btn.hide()
        
        self._dots_timer.start(500)
    
    def set_result(self, text: str, success: bool = True) -> None:
        """
        Set the transcription result.
        
        Args:
            text: Transcribed text or error message
            success: True if transcription succeeded
        """
        self._is_complete = True
        self._dots_timer.stop()
        
        if success:
            self._transcribed_text = text
            self._status_label.setText("Transcription terminée ✓")
            self._status_label.setStyleSheet(f"color: {Colors.SUCCESS};")
            self._text_area.setText(text)
            
            self._cancel_btn.hide()
            self._copy_btn.show()
            self._done_btn.show()
        else:
            self._status_label.setText("Erreur ✗")
            self._status_label.setStyleSheet(f"color: {Colors.ERROR};")
            self._text_area.setText(f"Erreur: {text}")
            
            self._cancel_btn.setText("Retour")
            self._copy_btn.hide()
            self._done_btn.hide()
    
    def set_progress_text(self, text: str) -> None:
        """Update the text area with progressive transcription."""
        self._text_area.setText(text)
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        self._dots_timer.stop()
