"""
V2T 2.1 - Waveform Visualization Widget
Displays real-time audio waveform with purple gradient.
"""
import numpy as np
from typing import Optional, List

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QPen

from src.utils.constants import Colors, UIConfig


class WaveformWidget(QWidget):
    """
    Real-time audio waveform visualization.
    Displays audio levels as animated vertical bars with purple gradient.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Settings
        self._num_bars = UIConfig.WAVEFORM_BARS
        self._bar_heights: List[float] = [0.0] * self._num_bars
        self._target_heights: List[float] = [0.0] * self._num_bars
        
        # Animation
        self._smoothing = 0.3  # Interpolation factor
        self._decay = 0.95  # How fast bars decay
        
        # Visual settings
        self._bar_spacing = 2
        self._min_bar_height = 2
        self._max_bar_height = 100
        self._border_radius = 2
        
        # Colors
        self._gradient_start = QColor(Colors.ACCENT_GRADIENT_START)
        self._gradient_end = QColor(Colors.ACCENT_GRADIENT_END)
        self._bg_color = QColor(Colors.BG_DARK)
        
        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._timer.start(30)  # ~33 FPS
        
        # Set fixed height
        self.setFixedHeight(UIConfig.WAVEFORM_HEIGHT)
        self.setMinimumWidth(200)
        
        # Idle animation
        self._idle_phase = 0.0
        self._is_active = False
    
    def set_audio_data(self, audio_data: np.ndarray) -> None:
        """
        Update waveform with new audio data.
        
        Args:
            audio_data: Numpy array of audio samples
        """
        self._is_active = True
        
        if audio_data is None or len(audio_data) == 0:
            self._target_heights = [0.0] * self._num_bars
            return
        
        # Calculate FFT for frequency visualization
        try:
            # Use FFT to get frequency components
            fft_data = np.abs(np.fft.rfft(audio_data))
            
            # Normalize
            if fft_data.max() > 0:
                fft_data = fft_data / fft_data.max()
            
            # Downsample to number of bars
            if len(fft_data) > self._num_bars:
                # Average bins for each bar
                bin_size = len(fft_data) // self._num_bars
                bars = []
                for i in range(self._num_bars):
                    start = i * bin_size
                    end = start + bin_size
                    bar_value = np.mean(fft_data[start:end])
                    bars.append(bar_value)
                self._target_heights = bars
            else:
                # Pad if needed
                self._target_heights = list(fft_data) + [0.0] * (self._num_bars - len(fft_data))
            
        except Exception:
            # Fallback: use RMS for simple volume bars
            rms = np.sqrt(np.mean(audio_data.astype(np.float32) ** 2))
            normalized = min(rms / 5000, 1.0)
            
            # Create wave pattern
            for i in range(self._num_bars):
                factor = np.sin(i / self._num_bars * np.pi)
                self._target_heights[i] = normalized * factor
    
    def set_idle(self) -> None:
        """Set waveform to idle state with subtle animation."""
        self._is_active = False
    
    def _update_animation(self) -> None:
        """Update bar heights with smooth interpolation."""
        changed = False
        
        if not self._is_active:
            # Idle animation - subtle wave
            self._idle_phase += 0.05
            for i in range(self._num_bars):
                # Create subtle wave pattern
                wave = 0.1 * np.sin(self._idle_phase + i * 0.2)
                wave = max(0.02, wave + 0.08)  # Minimum visibility
                
                old = self._bar_heights[i]
                self._bar_heights[i] += (wave - self._bar_heights[i]) * 0.1
                if abs(self._bar_heights[i] - old) > 0.001:
                    changed = True
        else:
            # Active animation - smooth to targets
            for i in range(self._num_bars):
                old = self._bar_heights[i]
                target = self._target_heights[i]
                
                # Smooth interpolation
                diff = target - self._bar_heights[i]
                self._bar_heights[i] += diff * self._smoothing
                
                # Apply decay
                self._target_heights[i] *= self._decay
                
                if abs(self._bar_heights[i] - old) > 0.001:
                    changed = True
        
        if changed:
            self.update()
    
    def paintEvent(self, event) -> None:
        """Draw the waveform bars."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_y = height / 2
        
        # Calculate bar dimensions
        total_spacing = (self._num_bars - 1) * self._bar_spacing
        bar_width = max(2, (width - total_spacing) / self._num_bars)
        
        # Create gradient
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, self._gradient_start)
        gradient.setColorAt(0.5, self._gradient_end)
        gradient.setColorAt(1, self._gradient_start)
        
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i in range(self._num_bars):
            # Calculate bar height
            bar_h = max(
                self._min_bar_height,
                self._bar_heights[i] * self._max_bar_height
            )
            
            # Calculate position (centered)
            x = i * (bar_width + self._bar_spacing)
            y = center_y - bar_h / 2
            
            # Draw bar with rounded corners
            painter.setBrush(gradient)
            painter.drawRoundedRect(
                int(x), int(y),
                int(bar_width), int(bar_h),
                self._border_radius, self._border_radius
            )
    
    def stop(self) -> None:
        """Stop the animation timer."""
        self._timer.stop()
    
    def start(self) -> None:
        """Start the animation timer."""
        if not self._timer.isActive():
            self._timer.start(30)
