"""
V2T 2.0 - History Page
Displays saved transcriptions.
"""
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea,
    QFrame, QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QCursor

from src.utils.constants import Colors
from src.ui.widgets.transcript_card import TranscriptCard
from src.services.storage import storage, Transcript
from src.core.groq_transcriber import groq_transcriber


class HistoryPage(QWidget):
    """
    Page displaying saved transcription history.
    Features:
    - Scrollable list of transcript cards
    - Copy to clipboard
    - Delete transcripts
    - Back navigation
    """
    
    # Signals
    navigate_back = pyqtSignal()
    text_copied = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._cards: List[TranscriptCard] = []
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the page layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # ===== Header =====
        header = QHBoxLayout()
        
        # Back button
        self._back_btn = QPushButton("← Retour")
        self._back_btn.setFont(QFont("Segoe UI", 11))
        self._back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_SECONDARY};
                border: none;
                padding: 8px 12px;
            }}
            QPushButton:hover {{
                color: {Colors.ACCENT_PRIMARY};
            }}
        """)
        self._back_btn.clicked.connect(self.navigate_back.emit)
        header.addWidget(self._back_btn)
        
        header.addStretch()
        
        # Title
        title = QLabel("Saved Transcripts")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY};")
        header.addWidget(title)
        
        header.addStretch()
        
        # Spacer for balance
        spacer = QLabel()
        spacer.setFixedWidth(80)
        header.addWidget(spacer)
        
        
        layout.addLayout(header)
        
        # ===== Search Bar =====
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("🔍 Rechercher...")
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {Colors.ACCENT_PRIMARY};
            }}
        """)
        self._search_input.textChanged.connect(self._filter_transcripts)
        layout.addWidget(self._search_input)
        
        # ===== Count Label =====
        self._count_label = QLabel("0 transcriptions")
        self._count_label.setFont(QFont("Segoe UI", 10))
        self._count_label.setStyleSheet(f"color: {Colors.TEXT_MUTED};")
        layout.addWidget(self._count_label)
        
        # ===== Scroll Area for Cards =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)
        
        # Container for cards
        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(12)
        self._cards_layout.addStretch()
        
        scroll.setWidget(self._cards_container)
        layout.addWidget(scroll, 1)
        
        # ===== Empty State =====
        self._empty_label = QLabel("Aucune transcription sauvegardée")
        self._empty_label.setFont(QFont("Segoe UI", 14))
        self._empty_label.setStyleSheet(f"color: {Colors.TEXT_MUTED};")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        layout.addWidget(self._empty_label)
    
    def load_transcripts(self) -> None:
        """Load and display all transcripts."""
        # Clear existing cards
        self._clear_cards()
        
        # Get transcripts from storage
        transcripts = storage.get_all(limit=100)
        
        # Update count
        count = len(transcripts)
        self._count_label.setText(f"{count} transcription{'s' if count != 1 else ''}")
        
        if count == 0:
            self._empty_label.show()
            return
        
        self._empty_label.hide()
        
        # Create cards
        for transcript in transcripts:
            card = TranscriptCard(
                transcript_id=transcript.id,
                title=transcript.title,
                text=transcript.text,
                created_at=transcript.created_at,
                duration=transcript.duration
            )
            
            # Connect signals
            card.copy_requested.connect(self._on_copy)
            card.delete_requested.connect(self._on_delete)
            card.correct_requested.connect(self._on_correct)
            card.clicked.connect(self._on_card_clicked)
            
            # Insert before stretch
            self._cards_layout.insertWidget(
                self._cards_layout.count() - 1, 
                card
            )
            self._cards.append(card)
    
    def _clear_cards(self) -> None:
        """Remove all card widgets."""
        for card in self._cards:
            card.deleteLater()
        self._cards.clear()
    
    def _on_copy(self, transcript_id: int) -> None:
        """Handle copy request from a card."""
        transcript = storage.get_by_id(transcript_id)
        if transcript:
            self.text_copied.emit(transcript.text)
    
    def _on_delete(self, transcript_id: int) -> None:
        """Handle delete request from a card."""
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Supprimer la transcription",
            "Êtes-vous sûr de vouloir supprimer cette transcription ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if storage.delete(transcript_id):
                # Remove card from UI
                for card in self._cards:
                    if card.transcript_id == transcript_id:
                        card.deleteLater()
                        self._cards.remove(card)
                        break
                
                # Update count
                count = len(self._cards)
                self._count_label.setText(
                    f"{count} transcription{'s' if count != 1 else ''}"
                )
                
                if count == 0:
                    self._empty_label.show()

    def _on_correct(self, transcript_id: int) -> None:
        """Handle correction request."""
        transcript = storage.get_by_id(transcript_id)
        if not transcript:
            return
            
        # Run in thread to avoid freezing UI
        import threading
        def run_correction():
            corrected_text = groq_transcriber.correct_grammar(transcript.text)
            if corrected_text:
                # Emit signal to copy text (must be done in main thread really, 
                # but pyqtSignal is thread safe)
                self.text_copied.emit(corrected_text)
        
        threading.Thread(target=run_correction, daemon=True).start()

    def _on_card_clicked(self, transcript_id: int) -> None:
        """Handle card click - could show detail view."""
        # For now, just copy the text
        self._on_copy(transcript_id)
    
    def refresh(self) -> None:
        """Refresh the transcript list."""
        self.load_transcripts()
        
    def _filter_transcripts(self, text: str) -> None:
        """Filter visible cards based on search text."""
        text = text.lower().strip()
        visible_count = 0
        
        for card in self._cards:
            if not text or text in card.text.lower() or text in card._title.lower():
                card.show()
                visible_count += 1
            else:
                card.hide()
                
        # Update count label
        self._count_label.setText(f"{visible_count} transcription{'s' if visible_count != 1 else ''}")
        
        if visible_count == 0 and len(self._cards) > 0:
             self._empty_label.setText("Aucun résultat")
             self._empty_label.show()
        elif len(self._cards) == 0:
             self._empty_label.setText("Aucune transcription sauvegardée")
             self._empty_label.show()
        else:
             self._empty_label.hide()
