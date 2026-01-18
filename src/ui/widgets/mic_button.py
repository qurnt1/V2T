"""
V2T 2.0 - Animated Microphone Button
Large circular button with glow effect and animations.
"""
from typing import Optional

from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, 
    pyqtProperty, QTimer, QSize
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QRadialGradient,
    QBrush, QPainterPath, QFont
)

from src.utils.constants import Colors, UIConfig


class MicButton(QWidget):
    """
    Animated microphone button with glow effect.
    Features:
    - Pulsing glow when idle
    - Recording state with red color
    - Smooth state transitions
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Button state
        self._is_recording = False
        self._glow_intensity = 0.0
        self._pulse_phase = 0.0
        self._hover = False
        
        # Size
        self._size = 120
        self.setFixedSize(self._size + 40, self._size + 40)  # Extra space for glow
        
        # Colors
        self._color_idle = QColor(Colors.ACCENT_PRIMARY)
        self._color_recording = QColor(Colors.ERROR)
        self._color_glow = QColor(Colors.ACCENT_GLOW)
        
        # Animation
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_timer.start(30)
        
        # Glow animation
        self._glow_anim = QPropertyAnimation(self, b"glowIntensity")
        self._glow_anim.setDuration(UIConfig.ANIMATION_NORMAL)
        self._glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Enable mouse tracking for hover
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Click callback
        self._on_click = None
    
    def set_on_click(self, callback) -> None:
        """Set click callback."""
        self._on_click = callback
    
    def set_recording(self, recording: bool) -> None:
        """Set recording state with animation."""
        if self._is_recording != recording:
            self._is_recording = recording
            self.update()
    
    @pyqtProperty(float)
    def glowIntensity(self) -> float:
        return self._glow_intensity
    
    @glowIntensity.setter
    def glowIntensity(self, value: float) -> None:
        self._glow_intensity = value
        self.update()
    
    def _update_pulse(self) -> None:
        """Update pulse animation."""
        self._pulse_phase += 0.05
        if self._pulse_phase > 2 * 3.14159:
            self._pulse_phase = 0
        self.update()
    
    def mousePressEvent(self, event) -> None:
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self._on_click:
                self._on_click()
    
    def enterEvent(self, event) -> None:
        """Handle mouse enter."""
        self._hover = True
        self._glow_anim.stop()
        self._glow_anim.setStartValue(self._glow_intensity)
        self._glow_anim.setEndValue(1.0)
        self._glow_anim.start()
    
    def leaveEvent(self, event) -> None:
        """Handle mouse leave."""
        self._hover = False
        self._glow_anim.stop()
        self._glow_anim.setStartValue(self._glow_intensity)
        self._glow_anim.setEndValue(0.0)
        self._glow_anim.start()
    
    def paintEvent(self, event) -> None:
        """Draw the button."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Calculate pulse
        import math
        pulse = 0.5 + 0.5 * math.sin(self._pulse_phase)
        
        # Current color
        if self._is_recording:
            main_color = self._color_recording
        else:
            main_color = self._color_idle
        
        # Draw glow
        glow_radius = self._size / 2 + 20
        glow_alpha = int(100 * (self._glow_intensity + pulse * 0.3))
        
        glow_gradient = QRadialGradient(center_x, center_y, glow_radius)
        glow_color = QColor(main_color)
        glow_color.setAlpha(glow_alpha)
        glow_gradient.setColorAt(0.5, glow_color)
        glow_gradient.setColorAt(1.0, QColor(0, 0, 0, 0))
        
        painter.setBrush(QBrush(glow_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(center_x - glow_radius),
            int(center_y - glow_radius),
            int(glow_radius * 2),
            int(glow_radius * 2)
        )
        
        # Draw outer ring
        ring_radius = self._size / 2 + 5
        painter.setPen(QPen(main_color, 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            int(center_x - ring_radius),
            int(center_y - ring_radius),
            int(ring_radius * 2),
            int(ring_radius * 2)
        )
        
        # Draw main circle with gradient
        button_gradient = QRadialGradient(
            center_x, center_y - 20,
            self._size / 2
        )
        
        lighter = QColor(main_color)
        lighter = lighter.lighter(130)
        
        button_gradient.setColorAt(0, lighter)
        button_gradient.setColorAt(1, main_color)
        
        painter.setBrush(QBrush(button_gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(
            int(center_x - self._size / 2),
            int(center_y - self._size / 2),
            self._size,
            self._size
        )
        
        # Draw microphone icon
        self._draw_mic_icon(painter, center_x, center_y)
    
    def _draw_mic_icon(self, painter: QPainter, cx: float, cy: float) -> None:
        """Draw microphone icon in the center."""
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(Colors.BG_DARK))
        
        # Mic body (rounded rectangle)
        mic_width = 24
        mic_height = 40
        mic_radius = 10
        
        path = QPainterPath()
        path.addRoundedRect(
            cx - mic_width / 2,
            cy - mic_height / 2 - 5,
            mic_width,
            mic_height,
            mic_radius, mic_radius
        )
        painter.drawPath(path)
        
        # Mic arc (bottom curve)
        painter.setPen(QPen(QColor(Colors.BG_DARK), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        arc_width = 40
        arc_height = 30
        painter.drawArc(
            int(cx - arc_width / 2),
            int(cy - 5),
            int(arc_width),
            int(arc_height),
            0, -180 * 16  # Bottom half arc
        )
        
        # Mic stand
        painter.setPen(QPen(QColor(Colors.BG_DARK), 4))
        painter.drawLine(
            int(cx), int(cy + arc_height / 2 + 5),
            int(cx), int(cy + arc_height / 2 + 15)
        )
        
        # Mic base
        painter.drawLine(
            int(cx - 15), int(cy + arc_height / 2 + 15),
            int(cx + 15), int(cy + arc_height / 2 + 15)
        )
    
    def stop(self) -> None:
        """Stop animations."""
        self._pulse_timer.stop()
        self._glow_anim.stop()
