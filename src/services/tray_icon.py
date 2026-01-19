"""
V2T 2.1 - System Tray Icon
Provides system tray icon with menu for quick access.
"""
import threading
from typing import Callable, Optional
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as Item

from src.utils.constants import ICON_FILE


class TrayIconManager:
    """
    Manages the system tray icon and its menu.
    Runs in a separate thread to not block the main UI.
    """
    
    def __init__(
        self,
        on_show: Optional[Callable] = None,
        on_settings: Optional[Callable] = None,
        on_quit: Optional[Callable] = None
    ):
        """
        Initialize tray icon manager.
        
        Args:
            on_show: Callback when "Show" is clicked
            on_settings: Callback when "Settings" is clicked  
            on_quit: Callback when "Quit" is clicked
        """
        self.on_show = on_show
        self.on_settings = on_settings
        self.on_quit = on_quit
        
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
    
    def _create_icon_image(self) -> Image.Image:
        """Load or create the tray icon image."""
        # Try to load custom icon
        if ICON_FILE.exists():
            try:
                return Image.open(str(ICON_FILE))
            except Exception:
                pass
        
        # Fallback: Create a simple purple circle
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Purple gradient-like circle
        draw.ellipse(
            (4, 4, size - 4, size - 4),
            fill=(139, 92, 246, 255),  # Purple #8B5CF6
            outline=(168, 85, 247, 255)  # Lighter purple
        )
        
        # Microphone icon (simplified)
        mic_color = (255, 255, 255, 255)
        center = size // 2
        
        # Mic body
        draw.rounded_rectangle(
            (center - 6, 16, center + 6, 36),
            radius=6,
            fill=mic_color
        )
        # Mic base
        draw.arc(
            (center - 12, 28, center + 12, 48),
            start=0, end=180,
            fill=mic_color,
            width=2
        )
        draw.line(
            (center, 48, center, 54),
            fill=mic_color,
            width=2
        )
        
        return img
    
    def _create_menu(self) -> tuple:
        """Create the tray icon menu."""
        return (
            Item(
                "Afficher V2T",
                lambda icon, item: self._handle_show(),
                default=True
            ),
            Item(
                "Paramètres",
                lambda icon, item: self._handle_settings()
            ),
            pystray.Menu.SEPARATOR,
            Item(
                "Quitter",
                lambda icon, item: self._handle_quit()
            ),
        )
    
    def _handle_show(self) -> None:
        """Handle show window action."""
        if self.on_show:
            self.on_show()
    
    def _handle_settings(self) -> None:
        """Handle open settings action."""
        if self.on_settings:
            self.on_settings()
    
    def _handle_quit(self) -> None:
        """Handle quit action."""
        self.stop()
        if self.on_quit:
            self.on_quit()
    
    def _run(self) -> None:
        """Run the tray icon (blocking)."""
        self._icon = pystray.Icon(
            name="V2T",
            icon=self._create_icon_image(),
            title="V2T - Voice to Text",
            menu=pystray.Menu(*self._create_menu())
        )
        self._icon.run()
    
    def start(self) -> None:
        """Start the tray icon in a background thread."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop and remove the tray icon."""
        self._running = False
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
    
    def update_icon(self, image: Optional[Image.Image] = None) -> None:
        """Update the tray icon image."""
        if self._icon:
            self._icon.icon = image or self._create_icon_image()
    
    def show_notification(self, title: str, message: str) -> None:
        """Show a system notification via the tray icon."""
        if self._icon:
            try:
                self._icon.notify(message, title)
            except Exception:
                pass
