"""
V2T 2.0 - PyQt6 Theme & Stylesheets
"""
from src.utils.constants import Colors, UIConfig


def get_main_stylesheet() -> str:
    """
    Returns the main QSS stylesheet for the entire application.
    Dark theme with purple accents.
    """
    return f"""
    /* ========================================
       GLOBAL STYLES
    ======================================== */
    
    QWidget {{
        background-color: {Colors.BG_DARK};
        color: {Colors.TEXT_PRIMARY};
        font-family: 'Segoe UI', 'Inter', sans-serif;
        font-size: 14px;
    }}
    
    QMainWindow {{
        background-color: {Colors.BG_DARK};
    }}
    
    /* ========================================
       SCROLL AREAS
    ======================================== */
    
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        background-color: {Colors.BG_DARK};
        width: 8px;
        border-radius: 4px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {Colors.BORDER_DEFAULT};
        border-radius: 4px;
        min-height: 30px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {Colors.ACCENT_PRIMARY};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    /* ========================================
       LABELS
    ======================================== */
    
    QLabel {{
        background-color: transparent;
        color: {Colors.TEXT_PRIMARY};
    }}
    
    QLabel[class="title"] {{
        font-size: 24px;
        font-weight: bold;
        color: {Colors.TEXT_PRIMARY};
    }}
    
    QLabel[class="subtitle"] {{
        font-size: 16px;
        color: {Colors.TEXT_SECONDARY};
    }}
    
    QLabel[class="muted"] {{
        font-size: 12px;
        color: {Colors.TEXT_MUTED};
    }}
    
    /* ========================================
       BUTTONS
    ======================================== */
    
    QPushButton {{
        background-color: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 500;
    }}
    
    QPushButton:hover {{
        background-color: {Colors.BG_CARD_HOVER};
        border-color: {Colors.ACCENT_PRIMARY};
    }}
    
    QPushButton:pressed {{
        background-color: {Colors.ACCENT_PRIMARY};
        color: {Colors.BG_DARK};
    }}
    
    QPushButton[class="primary"] {{
        background-color: {Colors.ACCENT_PRIMARY};
        color: {Colors.BG_DARK};
        border: none;
        font-weight: 600;
    }}
    
    QPushButton[class="primary"]:hover {{
        background-color: {Colors.ACCENT_SECONDARY};
    }}
    
    QPushButton[class="ghost"] {{
        background-color: transparent;
        border: 1px solid {Colors.BORDER_DEFAULT};
    }}
    
    QPushButton[class="ghost"]:hover {{
        border-color: {Colors.ACCENT_PRIMARY};
        color: {Colors.ACCENT_PRIMARY};
    }}
    
    /* ========================================
       TEXT INPUTS
    ======================================== */
    
    QLineEdit, QTextEdit {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 14px;
        selection-background-color: {Colors.ACCENT_PRIMARY};
    }}
    
    QLineEdit:focus, QTextEdit:focus {{
        border-color: {Colors.ACCENT_PRIMARY};
    }}
    
    QLineEdit::placeholder {{
        color: {Colors.TEXT_MUTED};
    }}
    
    /* ========================================
       COMBO BOX (Dropdown)
    ======================================== */
    
    QComboBox {{
        background-color: {Colors.BG_INPUT};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 14px;
    }}
    
    QComboBox:hover {{
        border-color: {Colors.ACCENT_PRIMARY};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QComboBox::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 6px solid {Colors.TEXT_SECONDARY};
        margin-right: 10px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {Colors.BG_CARD};
        color: {Colors.TEXT_PRIMARY};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: 8px;
        selection-background-color: {Colors.ACCENT_PRIMARY};
        selection-color: {Colors.BG_DARK};
        outline: none;
    }}
    
    /* ========================================
       SWITCH / CHECKBOX
    ======================================== */
    
    QCheckBox {{
        color: {Colors.TEXT_PRIMARY};
        spacing: 10px;
    }}
    
    QCheckBox::indicator {{
        width: 44px;
        height: 24px;
        border-radius: 12px;
        background-color: {Colors.BORDER_DEFAULT};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {Colors.ACCENT_PRIMARY};
    }}
    
    /* ========================================
       CARDS (Custom Widget Base)
    ======================================== */
    
    QFrame[class="card"] {{
        background-color: {Colors.BG_CARD};
        border: 1px solid {Colors.BORDER_DEFAULT};
        border-radius: 16px;
        padding: 16px;
    }}
    
    QFrame[class="card"]:hover {{
        border-color: {Colors.ACCENT_PRIMARY};
    }}
    
    /* ========================================
       PROGRESS BAR
    ======================================== */
    
    QProgressBar {{
        background-color: {Colors.BORDER_DEFAULT};
        border: none;
        border-radius: 4px;
        height: 8px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {Colors.ACCENT_PRIMARY};
        border-radius: 4px;
    }}
    """


def get_mic_button_style(is_recording: bool = False) -> str:
    """
    Returns style for the microphone button based on recording state.
    """
    if is_recording:
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.ERROR},
                    stop:1 #DC2626
                );
                border: 3px solid {Colors.ERROR};
                border-radius: 50px;
            }}
        """
    else:
        return f"""
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.ACCENT_GRADIENT_START},
                    stop:1 {Colors.ACCENT_GRADIENT_END}
                );
                border: 3px solid {Colors.ACCENT_PRIMARY};
                border-radius: 50px;
            }}
            QPushButton:hover {{
                border-color: {Colors.ACCENT_SECONDARY};
            }}
        """


def get_card_style(is_selected: bool = False) -> str:
    """
    Returns style for transcript cards.
    """
    border_color = Colors.ACCENT_PRIMARY if is_selected else Colors.BORDER_DEFAULT
    return f"""
        QFrame {{
            background-color: {Colors.BG_CARD};
            border: 1px solid {border_color};
            border-radius: 16px;
            padding: 16px;
        }}
        QFrame:hover {{
            border-color: {Colors.ACCENT_PRIMARY};
        }}
    """
