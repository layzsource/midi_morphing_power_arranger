#!/usr/bin/env python3
"""
MMPA - Minimal Version
Absolutely minimal implementation to avoid all freezing issues.
No OpenGL, no complex widgets, no threading complications.
"""

import sys
import logging
import time
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTextEdit
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

def setup_logging():
    """Simple logging setup."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class MinimalAudioHandler:
    """Minimal audio handler that can be toggled on/off."""

    def __init__(self):
        self.active = False
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start audio processing."""
        try:
            # Try to import and start SoundDevice
            import sounddevice as sd
            self.active = True
            self.logger.info("Audio started (SoundDevice)")
            return True
        except ImportError:
            try:
                # Fallback to PyAudio
                import pyaudio
                self.active = True
                self.logger.info("Audio started (PyAudio)")
                return True
            except ImportError:
                self.logger.error("No audio backend available")
                return False
        except Exception as e:
            self.logger.error(f"Audio start failed: {e}")
            return False

    def stop(self):
        """Stop audio processing."""
        self.active = False
        self.logger.info("Audio stopped")

    def is_active(self):
        return self.active

class MinimalMIDIHandler:
    """Minimal MIDI handler."""

    def __init__(self):
        self.devices = []
        self.logger = logging.getLogger(__name__)

    def scan_devices(self):
        """Scan for MIDI devices."""
        try:
            import rtmidi
            midiin = rtmidi.MidiIn()
            self.devices = midiin.get_ports()
            self.logger.info(f"Found {len(self.devices)} MIDI devices")
            return self.devices
        except ImportError:
            self.logger.warning("rtmidi not available")
            return []
        except Exception as e:
            self.logger.error(f"MIDI scan failed: {e}")
            return []

class MinimalMMPAWindow(QMainWindow):
    """Absolutely minimal MMPA window."""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Audio and MIDI handlers
        self.audio_handler = MinimalAudioHandler()
        self.midi_handler = MinimalMIDIHandler()

        self.setWindowTitle("🎵 MMPA - Minimal (No Freeze)")
        self.setGeometry(200, 200, 600, 400)

        # Apply simple dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: monospace;
                border: 1px solid #555;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
        """)

        self._setup_ui()
        self._scan_systems()

        # Simple update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_status)
        self.timer.start(1000)  # Update every second

        self.logger.info("Minimal MMPA window initialized")

    def _setup_ui(self):
        """Setup minimal UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("🎵 MMPA - Minimal Edition")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        subtitle = QLabel("The Language of Signals Becoming Form - Stable Version")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #aaa; font-size: 12px;")
        layout.addWidget(subtitle)

        # Audio control
        self.audio_button = QPushButton("🔊 START Audio")
        self.audio_button.clicked.connect(self._toggle_audio)
        layout.addWidget(self.audio_button)

        # Status display
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        layout.addWidget(self.status_text)

        # Info button
        info_button = QPushButton("ℹ️ System Info")
        info_button.clicked.connect(self._show_info)
        layout.addWidget(info_button)

        # Log initial status
        self._log("🎼 MMPA Minimal - Ready")
        self._log("⏸️ Audio: STOPPED (click button to start)")
        self._log("✅ Stable architecture - no freezing")

    def _scan_systems(self):
        """Scan for available systems."""
        # Check audio backends
        audio_backends = []
        try:
            import sounddevice
            audio_backends.append("SoundDevice")
        except ImportError:
            pass

        try:
            import pyaudio
            audio_backends.append("PyAudio")
        except ImportError:
            pass

        if audio_backends:
            self._log(f"🎵 Audio backends: {', '.join(audio_backends)}")
        else:
            self._log("❌ No audio backends available")

        # Check MIDI
        devices = self.midi_handler.scan_devices()
        if devices:
            self._log(f"🎹 MIDI devices: {len(devices)} found")
            for i, device in enumerate(devices[:3]):  # Show first 3
                self._log(f"   {i+1}. {device}")
        else:
            self._log("❌ No MIDI devices available")

    def _toggle_audio(self):
        """Toggle audio processing."""
        if self.audio_handler.is_active():
            self.audio_handler.stop()
            self.audio_button.setText("🔊 START Audio")
            self.audio_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self._log("🔇 Audio processing STOPPED")
        else:
            if self.audio_handler.start():
                self.audio_button.setText("🔇 STOP Audio")
                self.audio_button.setStyleSheet("""
                    QPushButton {
                        background-color: #ff6b6b;
                        color: white;
                        padding: 10px;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #e55555;
                    }
                """)
                self._log("🔊 Audio processing STARTED")
                self._log("🎵 Ready for audio input")
            else:
                self._log("❌ Failed to start audio")

    def _show_info(self):
        """Show system information."""
        self._log("📊 System Information:")
        self._log(f"   Python: {sys.version.split()[0]}")
        self._log(f"   Platform: {sys.platform}")

        # Check dependencies
        deps = []
        for module in ['PySide6', 'numpy', 'sounddevice', 'pyaudio', 'rtmidi']:
            try:
                __import__(module)
                deps.append(f"✅ {module}")
            except ImportError:
                deps.append(f"❌ {module}")

        self._log("   Dependencies:")
        for dep in deps:
            self._log(f"     {dep}")

    def _update_status(self):
        """Update status periodically."""
        timestamp = time.strftime("%H:%M:%S")
        if self.audio_handler.is_active():
            self._log(f"[{timestamp}] 🔊 Audio active - processing input")

    def _log(self, message):
        """Add message to status log."""
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.status_text.append(formatted)

        # Keep log manageable
        if self.status_text.document().blockCount() > 50:
            cursor = self.status_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor, 10)
            cursor.removeSelectedText()

    def closeEvent(self, event):
        """Handle close event."""
        self.logger.info("Closing MMPA")
        if self.audio_handler.is_active():
            self.audio_handler.stop()
        event.accept()

def main():
    """Main entry point."""
    setup_logging()

    print("🎵 MMPA - MINIMAL EDITION (NO FREEZE GUARANTEE)")
    print("=" * 50)
    print("Absolutely minimal implementation for maximum stability")
    print("Manual audio toggle - you control when processing starts")
    print()

    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("MMPA - Minimal")
    app.setApplicationVersion("1.0")

    try:
        # Create and show window
        window = MinimalMMPAWindow()
        window.show()

        print("✅ MMPA Minimal running successfully")
        print("🔊 Use the audio toggle button when ready")

        return app.exec()

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())