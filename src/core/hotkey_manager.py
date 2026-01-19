"""
V2T 2.1 - Hotkey Manager
Global keyboard shortcut handling.
"""
import threading
from typing import Callable, Optional, Set

import keyboard


class HotkeyManager:
    """
    Manages global keyboard shortcuts.
    Handles registration and callback execution.
    """
    
    def __init__(self):
        self._hotkeys: dict[str, Callable] = {}
        self._active_keys: Set[str] = set()
        self._lock = threading.Lock()
        self._running = False
    
    def register(self, hotkey: str, callback: Callable) -> bool:
        """
        Register a global hotkey.
        
        Args:
            hotkey: Key combination (e.g., "F8", "ctrl+shift+r")
            callback: Function to call when hotkey is pressed
            
        Returns:
            True if registered successfully
        """
        try:
            with self._lock:
                # Unregister if already exists
                if hotkey in self._active_keys:
                    keyboard.remove_hotkey(hotkey)
                
                # Register new hotkey
                keyboard.add_hotkey(hotkey, callback, suppress=False)
                self._hotkeys[hotkey] = callback
                self._active_keys.add(hotkey)
            
            return True
            
        except Exception as e:
            print(f"[HotkeyManager] Error registering {hotkey}: {e}")
            return False
    
    def unregister(self, hotkey: str) -> bool:
        """
        Unregister a hotkey.
        
        Args:
            hotkey: The key combination to unregister
            
        Returns:
            True if unregistered successfully
        """
        try:
            with self._lock:
                if hotkey in self._active_keys:
                    keyboard.remove_hotkey(hotkey)
                    self._active_keys.discard(hotkey)
                    self._hotkeys.pop(hotkey, None)
            return True
            
        except Exception as e:
            print(f"[HotkeyManager] Error unregistering {hotkey}: {e}")
            return False
    
    def unregister_all(self) -> None:
        """Unregister all hotkeys."""
        with self._lock:
            for hotkey in list(self._active_keys):
                try:
                    keyboard.remove_hotkey(hotkey)
                except Exception:
                    pass
            self._active_keys.clear()
            self._hotkeys.clear()
    
    def is_pressed(self, key: str) -> bool:
        """Check if a key is currently pressed."""
        try:
            return keyboard.is_pressed(key)
        except Exception:
            return False
    
    def wait_for_key(self, timeout: float = 5.0) -> Optional[str]:
        """
        Wait for any key press and return it.
        Used for capturing custom hotkeys in settings.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            Key name or None if timeout
        """
        try:
            event = keyboard.read_hotkey(suppress=False)
            return event
        except Exception:
            return None
    
    def update_hotkey(self, old_key: str, new_key: str, callback: Callable) -> bool:
        """
        Update an existing hotkey to a new key.
        
        Args:
            old_key: Current hotkey to replace
            new_key: New hotkey
            callback: Callback function
            
        Returns:
            True if updated successfully
        """
        self.unregister(old_key)
        return self.register(new_key, callback)
    
    @property
    def active_hotkeys(self) -> Set[str]:
        """Get set of currently registered hotkeys."""
        with self._lock:
            return set(self._active_keys)


# Global instance
hotkey_manager = HotkeyManager()
