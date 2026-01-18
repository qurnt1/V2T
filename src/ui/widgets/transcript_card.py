"""
V2T 2.0 - Transcript Card Widget
Card component for displaying saved transcriptions.
"""
from datetime import datetime
from typing import Optional, Callable

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QCursor

from src.utils.constants import Colors


class TranscriptCard(QFrame):
    """
    Card widget for displaying a transcript in the history.
    Features:
    - Title, preview text, date, duration
    - Copy to clipboard button
    - Delete button
    - Hover animations
    """
    
    # Signals
    clicked = pyqtSignal(int)  # Emits transcript ID
    copy_requested = pyqtSignal(int)
    delete_requested = pyqtSignal(int)
    
    def __init__(
        self, 
        transcript_id: int,
        title: str,
        text: str,
        created_at: datetime,
        duration: float = 0.0,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._id = transcript_id
        self._title = title
        self._text = text
        self._created_at = created_at
        self._duration = duration
        
        self._setup_ui()
        self._setup_style()
    
    def _setup_ui(self) -> None:
        """Setup the card layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Header row: Title + Date/Duration
        header = QHBoxLayout()
        header.setSpacing(10)
        
        # Title
        self._title_label = QLabel(self._title)
        self._title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._title_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        header.addWidget(self._title_label, 1)
        
        # Date and duration
        date_str = self._created_at.strftime("%d/%m/%Y")
        duration_str = self._format_duration(self._duration)
        
        info_text = f"{date_str}\n{duration_str}"
        self._info_label = QLabel(info_text)
        self._info_label.setFont(QFont("Segoe UI", 9))
        self._info_label.setStyleSheet(f"color: {Colors.TEXT_MUTED};")
        self._info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        header.addWidget(self._info_label)
        
        layout.addLayout(header)
        
        # Preview text
        preview = self._text[:150].replace("\n", " ")
        if len(self._text) > 150:
            preview += "..."
        
        self._preview_label = QLabel(preview)
        self._preview_label.setFont(QFont("Segoe UI", 10))
        self._preview_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self._preview_label.setWordWrap(True)
        layout.addWidget(self._preview_label)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.addStretch()
        
        # Copy button
        self._copy_btn = QPushButton("📋 Copier")
        self._copy_btn.setFont(QFont("Segoe UI", 9))
        self._copy_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._copy_btn.clicked.connect(self._on_copy)
        self._copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.ACCENT_PRIMARY};
                border: 1px solid {Colors.ACCENT_PRIMARY};
                border-radius: 6px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.BG_DARK};
            }}
        """)
        buttons_layout.addWidget(self._copy_btn)
        
        # Delete button
        self._delete_btn = QPushButton("🗑️")
        self._delete_btn.setFont(QFont("Segoe UI", 9))
        self._delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._delete_btn.clicked.connect(self._on_delete)
        self._delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_MUTED};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {Colors.ERROR};
                border-color: {Colors.ERROR};
                color: white;
            }}
        """)
        buttons_layout.addWidget(self._delete_btn)
        
        layout.addLayout(buttons_layout)
    
    def _setup_style(self) -> None:
        """Setup card styling."""
        self.setStyleSheet(f"""
            TranscriptCard {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 16px;
            }}
            TranscriptCard:hover {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
        """)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration to MM:SS."""
        if seconds <= 0:
            return "00:00"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _on_copy(self) -> None:
        """Handle copy button click."""
        self.copy_requested.emit(self._id)
    
    def _on_delete(self) -> None:
        """Handle delete button click."""
        self.delete_requested.emit(self._id)
    
    def mousePressEvent(self, event) -> None:
        """Handle card click."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Only emit if not clicking a button
            widget = self.childAt(event.pos())
            if not isinstance(widget, QPushButton):
                self.clicked.emit(self._id)
    
    @property
    def transcript_id(self) -> int:
        return self._id
    
    @property
    def text(self) -> str:
        return self._text
    
    def update_title(self, new_title: str) -> None:
        """Update the displayed title."""
        self._title = new_title
        self._title_label.setText(new_title)
