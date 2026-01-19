"""
V2T 2.2 - Application Entry Point
Main application class initializing all components.
"""
import sys
import time
import os
from typing import Optional

# Suppress HuggingFace symlinks warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt, QObject, pyqtSignal, QTimer

from src.ui.main_window import MainWindow
from src.services.tray_icon import TrayIconManager
from src.services.settings import settings


class TrayBridge(QObject):
    """Bridge to handle tray callbacks in the main Qt thread."""
    show_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()


class V2TApp:
    """
    Main application class.
    Initializes Qt application and manages lifecycle.
    """
    
    def __init__(self):
        self._app: Optional[QApplication] = None
        self._main_window: Optional[MainWindow] = None
        self._tray_manager: Optional[TrayIconManager] = None
        self._tray_bridge: Optional[TrayBridge] = None
    
    def _init_app(self) -> QApplication:
        """Initialize the Qt application."""
        # Enable high DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication(sys.argv)
        app.setApplicationName("V2T")
        app.setApplicationDisplayName("V2T - Voice to Text")
        app.setOrganizationName("V2T")
        
        # Don't quit when last window closes (we have tray)
        app.setQuitOnLastWindowClosed(False)
        
        # Set default font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        return app
    
    def _init_tray(self) -> TrayIconManager:
        """Initialize the system tray icon."""
        # Create bridge for thread-safe communication
        self._tray_bridge = TrayBridge()
        self._tray_bridge.show_requested.connect(self._show_window)
        self._tray_bridge.settings_requested.connect(self._show_settings)
        self._tray_bridge.quit_requested.connect(self._quit_app)
        
        # Tray callbacks emit signals instead of direct calls
        tray = TrayIconManager(
            on_show=lambda: self._tray_bridge.show_requested.emit(),
            on_settings=lambda: self._tray_bridge.settings_requested.emit(),
            on_quit=lambda: self._tray_bridge.quit_requested.emit()
        )
        return tray
    
    def _show_window(self) -> None:
        """Show the main window (main thread)."""
        if self._main_window:
            self._main_window.show()
            self._main_window.activateWindow()
            self._main_window.raise_()
    
    def _show_settings(self) -> None:
        """Show settings page (main thread)."""
        if self._main_window:
            self._main_window.show()
            self._main_window._show_settings()
    
    def _quit_app(self) -> None:
        """Quit the application (main thread)."""
        # Show exit notification BEFORE stopping tray
        if self._tray_manager:
            self._tray_manager.show_notification(
                "V2T Fermé",
                "À bientôt !"
            )
            # Small delay to ensure notification is sent
            QTimer.singleShot(300, self._do_quit)
        else:
            self._do_quit()
    
    def _do_quit(self) -> None:
        """Actually perform the quit operation."""
        if self._tray_manager:
            self._tray_manager.stop()
        if self._main_window:
            self._main_window.force_quit()
    
    def run(self) -> int:
        """Run the application."""
        # Initialize Qt
        self._app = self._init_app()
        
        # Create main window
        self._main_window = MainWindow()
        
        # Initialize tray icon
        self._tray_manager = self._init_tray()
        self._tray_manager.start()
        
        # Pass tray manager to main window for notifications
        self._main_window.set_tray_manager(self._tray_manager)
        
        # Show window
        self._main_window.show()
        
        # Show notification after a short delay
        QTimer.singleShot(500, lambda: self._tray_manager.show_notification(
            "V2T Démarré",
            "Appuyez sur F8 pour enregistrer"
        ))
        
        # Run event loop
        return self._app.exec()


def main():
    """Application entry point."""
    app = V2TApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
