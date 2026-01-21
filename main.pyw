#!/usr/bin/env python3
"""
V2T 2.0 - Voice to Text
Main entry point for the application.

Usage:
    python main.py          # Launch the GUI application
    python main.py --help   # Show help
"""
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main entry point."""
    # Check for help flag
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        print("V2T 2.0 - Voice to Text Application")
        print("")
        print("Features:")
        print("  - Real-time voice recording with waveform visualization")
        print("  - Online transcription (Groq Whisper API)")
        print("  - Offline transcription (faster-whisper)")
        print("  - Transcription history")
        print("  - Global hotkey support (F8 by default)")
        print("  - Auto-paste to active application")
        print("")
        print("Requirements:")
        print("  - Python 3.10+")
        print("  - See requirements.txt for dependencies")
        print("")
        print("Configuration:")
        print("  - Set Groq API key in .env file or Settings page")
        print("  - Configure hotkey, language, and more in Settings")
        return 0
    
    # Import and run application
    try:
        from src.app import main as run_app
        return run_app()
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Run: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())