"""
V2T 2.0 - Application Entry Point
Main application class initializing all components.
"""
import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtCore import Qt

from src.ui.main_window import MainWindow
from src.services.tray_icon import TrayIconManager
from src.services.settings import settings


class V2TApp:
    """
    Main application class.
    Initializes Qt application and manages lifecycle.
    """
    
    def __init__(self):
        self._app: Optional[QApplication] = None
        self._main_window: Optional[MainWindow] = None
        self._tray_manager: Optional[TrayIconManager] = None
    
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
        
        # Set default font
        font = QFont("Segoe UI", 10)
        app.setFont(font)
        
        return app
    
    def _init_tray(self) -> TrayIconManager:
        """Initialize the system tray icon."""
        tray = TrayIconManager(
            on_show=self._show_window,
            on_settings=self._show_settings,
            on_quit=self._quit_app
        )
        return tray
    
    def _show_window(self) -> None:
        """Show the main window."""
        if self._main_window:
            self._main_window.show()
            self._main_window.activateWindow()
            self._main_window.raise_()
    
    def _show_settings(self) -> None:
        """Show settings page."""
        if self._main_window:
            self._main_window.show()
            self._main_window._show_settings()
    
    def _quit_app(self) -> None:
        """Quit the application."""
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
        
        # Show window
        self._main_window.show()
        
        # Show notification
        self._tray_manager.show_notification(
            "V2T Démarré",
            "Appuyez sur F8 pour enregistrer"
        )
        
        # Run event loop
        return self._app.exec()


def main():
    """Application entry point."""
    app = V2TApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
