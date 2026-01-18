"""
V2T 2.0 - Settings Manager
Handles loading and saving user preferences.
"""
import json
import threading
from typing import Any, Optional
from pathlib import Path

from src.utils.constants import CONFIG_FILE, DEFAULT_SETTINGS


class SettingsManager:
    """
    Thread-safe settings manager with JSON persistence.
    Singleton pattern ensures one instance across the app.
    """
    _instance: Optional["SettingsManager"] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> "SettingsManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._settings: dict = dict(DEFAULT_SETTINGS)
        self._settings_lock = threading.Lock()
        self._load()
        self._initialized = True
    
    def _load(self) -> None:
        """Load settings from JSON file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                with self._settings_lock:
                    self._settings.update(data)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[Settings] Error loading settings: {e}")
    
    def save(self) -> None:
        """Save current settings to JSON file."""
        try:
            # Ensure parent directory exists
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with self._settings_lock:
                payload = dict(self._settings)
            
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"[Settings] Error saving settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        with self._settings_lock:
            return self._settings.get(key, default)
    
    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        """Set a setting value."""
        with self._settings_lock:
            self._settings[key] = value
        if auto_save:
            self.save()
    
    def get_all(self) -> dict:
        """Get all settings as a dictionary copy."""
        with self._settings_lock:
            return dict(self._settings)
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values."""
        with self._settings_lock:
            self._settings = dict(DEFAULT_SETTINGS)
        self.save()


# Global instance for easy access
settings = SettingsManager()
