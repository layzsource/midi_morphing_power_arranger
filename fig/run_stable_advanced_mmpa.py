#!/usr/bin/env python3
"""
MMPA - Stable Advanced Version
Minimal base with advanced audio analysis - proven stable approach.
"""

import sys
import logging
import time
import numpy as np
from pathlib import Path
import threading

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QPushButton, QTextEdit, QProgressBar, QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont

def setup_logging():
    """Simple logging setup."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class AdvancedAudioHandler(QObject):
    """Advanced audio handler with spectral analysis but stable threading."""

    # Qt signals for thread-safe updates
    audio_data_ready = Signal(dict)
    spectral_features_ready = Signal(dict)

    def __init__(self):
        super().__init__()
        self.active = False
        self.logger = logging.getLogger(__name__)
        self.audio_thread = None
        self.stop_flag = False

        # Try to get professional audio handler
        try:
            from fig.audio.professional_audio_handler import ProfessionalAudioHandler
            from fig.core.config import get_config
            config = get_config()
            self.professional_handler = ProfessionalAudioHandler(config.audio)
            self.has_professional = True
            self.logger.info("Professional audio handler available")
        except:
            self.professional_handler = None
            self.has_professional = False
            self.logger.info("Using basic audio handler")

    def start(self):
        """Start audio processing safely."""
        if self.active:
            return True

        try:
            if self.has_professional:
                # Use professional handler
                success = self.professional_handler.start()
                if success:
                    # Connect professional signals safely
                    if hasattr(self.professional_handler, 'audio_processed'):
                        self.professional_handler.audio_processed.connect(self.audio_data_ready.emit)
                    if hasattr(self.professional_handler, 'spectral_features_extracted'):
                        self.professional_handler.spectral_features_extracted.connect(self.spectral_features_ready.emit)

                    self.active = True
                    self.logger.info("Professional audio started")
                    return True
            else:
                # Fallback to basic audio
                self._start_basic_audio()
                return True

        except Exception as e:
            self.logger.error(f"Audio start failed: {e}")
            return False

        return False

    def _start_basic_audio(self):
        """Start basic audio processing."""
        try:
            import sounddevice as sd
            self.active = True
            self.logger.info("Basic audio started (SoundDevice)")

            # Simple audio processing in thread
            self.stop_flag = False
            self.audio_thread = threading.Thread(target=self._basic_audio_loop, daemon=True)
            self.audio_thread.start()

        except ImportError:
            try:
                import pyaudio
                self.active = True
                self.logger.info("Basic audio started (PyAudio)")
            except ImportError:
                raise Exception("No audio backend available")

    def _basic_audio_loop(self):
        """Basic audio processing loop."""
        import sounddevice as sd

        def audio_callback(indata, frames, time, status):
            if self.stop_flag:
                return

            # Simple audio analysis
            audio_data = indata[:, 0] if indata.ndim > 1 else indata

            # Calculate basic features
            energy = float(np.mean(audio_data ** 2))
            peak = float(np.max(np.abs(audio_data)))

            # Simple frequency analysis
            fft = np.fft.rfft(audio_data)
            magnitude = np.abs(fft)

            # Split into basic bands
            n_freqs = len(magnitude)
            bass_end = n_freqs // 4
            mid_end = 3 * n_freqs // 4

            bass_energy = float(np.mean(magnitude[:bass_end]))
            mid_energy = float(np.mean(magnitude[bass_end:mid_end]))
            treble_energy = float(np.mean(magnitude[mid_end:]))

            # Emit data
            basic_data = {
                'energy': energy,
                'peak': peak,
                'bass_energy': bass_energy,
                'mid_energy': mid_energy,
                'treble_energy': treble_energy
            }

            self.audio_data_ready.emit(basic_data)

        # Start audio stream
        try:
            with sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=1024):
                while not self.stop_flag and self.active:
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Audio stream error: {e}")

    def stop(self):
        """Stop audio processing."""
        if not self.active:
            return

        try:
            if self.has_professional and self.professional_handler:
                self.professional_handler.stop()
            else:
                self.stop_flag = True
                if self.audio_thread:
                    self.audio_thread.join(timeout=1.0)

            self.active = False
            self.logger.info("Audio stopped")

        except Exception as e:
            self.logger.error(f"Audio stop error: {e}")

    def is_active(self):
        return self.active

class StableAdvancedWindow(QMainWindow):
    """Stable window with advanced audio analysis."""

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Handlers
        self.audio_handler = AdvancedAudioHandler()

        self.setWindowTitle("🎵 MMPA - Stable Advanced")
        self.setGeometry(100, 100, 800, 600)

        # Apply professional theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
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
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #333;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)

        self._setup_ui()
        self._connect_signals()
        self._scan_systems()

        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_displays)
        self.timer.start(100)  # 10 FPS

        self.logger.info("Stable advanced window initialized")

    def _setup_ui(self):
        """Setup stable UI with advanced displays."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Left panel - Controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(350)
        left_layout = QVBoxLayout(left_panel)

        # Title
        title = QLabel("🎵 MMPA - Stable Advanced")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Bold))
        left_layout.addWidget(title)

        subtitle = QLabel("The Language of Signals Becoming Form")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #aaa; font-size: 12px;")
        left_layout.addWidget(subtitle)

        # Audio control
        audio_group = QGroupBox("🔊 Audio Control")
        audio_layout = QVBoxLayout(audio_group)

        self.audio_button = QPushButton("🔊 START Audio")
        self.audio_button.clicked.connect(self._toggle_audio)
        audio_layout.addWidget(self.audio_button)

        self.audio_status = QLabel("Audio: STOPPED")
        self.audio_status.setAlignment(Qt.AlignCenter)
        self.audio_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        audio_layout.addWidget(self.audio_status)

        left_layout.addWidget(audio_group)

        # Advanced analysis displays
        analysis_group = QGroupBox("🎓 Advanced Analysis")
        analysis_layout = QGridLayout(analysis_group)

        # Energy levels
        analysis_layout.addWidget(QLabel("Bass:"), 0, 0)
        self.bass_bar = QProgressBar()
        self.bass_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.bass_bar, 0, 1)
        self.bass_label = QLabel("0")
        analysis_layout.addWidget(self.bass_label, 0, 2)

        analysis_layout.addWidget(QLabel("Mid:"), 1, 0)
        self.mid_bar = QProgressBar()
        self.mid_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.mid_bar, 1, 1)
        self.mid_label = QLabel("0")
        analysis_layout.addWidget(self.mid_label, 1, 2)

        analysis_layout.addWidget(QLabel("Treble:"), 2, 0)
        self.treble_bar = QProgressBar()
        self.treble_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.treble_bar, 2, 1)
        self.treble_label = QLabel("0")
        analysis_layout.addWidget(self.treble_label, 2, 2)

        # Advanced features (if available)
        analysis_layout.addWidget(QLabel("Brightness:"), 3, 0)
        self.brightness_bar = QProgressBar()
        self.brightness_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.brightness_bar, 3, 1)
        self.brightness_label = QLabel("0")
        analysis_layout.addWidget(self.brightness_label, 3, 2)

        analysis_layout.addWidget(QLabel("Onset:"), 4, 0)
        self.onset_bar = QProgressBar()
        self.onset_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.onset_bar, 4, 1)
        self.onset_label = QLabel("0.0")
        analysis_layout.addWidget(self.onset_label, 4, 2)

        left_layout.addWidget(analysis_group)
        left_layout.addStretch()

        # Right panel - Status and visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        status_label = QLabel("📊 System Status & Log")
        status_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_layout.addWidget(status_label)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        right_layout.addWidget(self.status_text)

        # Add panels to main layout
        layout.addWidget(left_panel)
        layout.addWidget(right_panel)

        # Log initial status
        self._log("🎼 MMPA Stable Advanced - Ready")
        self._log("⏸️ Audio: STOPPED (click button to start)")
        self._log("✅ Stable architecture with advanced analysis")

    def _connect_signals(self):
        """Connect audio handler signals."""
        self.audio_handler.audio_data_ready.connect(self._update_audio_displays)
        self.audio_handler.spectral_features_ready.connect(self._update_spectral_displays)

    def _scan_systems(self):
        """Scan available systems."""
        # Check audio
        try:
            import sounddevice
            self._log("🎵 SoundDevice: Available")
        except ImportError:
            pass

        try:
            import pyaudio
            self._log("🎵 PyAudio: Available")
        except ImportError:
            pass

        # Check advanced features
        if self.audio_handler.has_professional:
            self._log("🎓 Professional audio analysis: Available")
        else:
            self._log("🎵 Basic audio analysis: Available")

        # Check MIDI
        try:
            import rtmidi
            midiin = rtmidi.MidiIn()
            devices = midiin.get_ports()
            self._log(f"🎹 MIDI devices: {len(devices)} found")
        except:
            self._log("❌ MIDI not available")

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
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #45a049; }
            """)
            self.audio_status.setText("Audio: STOPPED")
            self.audio_status.setStyleSheet("color: #ff6b6b; font-weight: bold;")
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
                        font-size: 14px;
                    }
                    QPushButton:hover { background-color: #e55555; }
                """)
                self.audio_status.setText("Audio: RUNNING")
                self.audio_status.setStyleSheet("color: #4CAF50; font-weight: bold;")
                self._log("🔊 Audio processing STARTED")
                if self.audio_handler.has_professional:
                    self._log("🎓 Advanced spectral analysis active")
                else:
                    self._log("🎵 Basic frequency analysis active")
            else:
                self._log("❌ Failed to start audio")

    def _update_audio_displays(self, data):
        """Update audio level displays."""
        try:
            # Update basic energy levels
            bass = data.get('bass_energy', 0)
            mid = data.get('mid_energy', 0)
            treble = data.get('treble_energy', 0)

            # Normalize and display
            bass_norm = min(100, max(0, int(bass * 1000)))
            mid_norm = min(100, max(0, int(mid * 1000)))
            treble_norm = min(100, max(0, int(treble * 1000)))

            self.bass_bar.setValue(bass_norm)
            self.bass_label.setText(f"{bass:.3f}")

            self.mid_bar.setValue(mid_norm)
            self.mid_label.setText(f"{mid:.3f}")

            self.treble_bar.setValue(treble_norm)
            self.treble_label.setText(f"{treble:.3f}")

        except Exception as e:
            self.logger.error(f"Audio display update error: {e}")

    def _update_spectral_displays(self, features):
        """Update advanced spectral displays."""
        try:
            # Spectral centroid (brightness)
            centroid = features.get('spectral_centroid', 0)
            if centroid > 0:
                centroid_norm = min(100, max(0, int(centroid / 100)))
                self.brightness_bar.setValue(centroid_norm)
                self.brightness_label.setText(f"{centroid:.0f}")

            # Onset strength
            onset = features.get('onset_strength', 0)
            onset_norm = min(100, max(0, int(onset * 100)))
            self.onset_bar.setValue(onset_norm)
            self.onset_label.setText(f"{onset:.3f}")

            # Log significant events
            if onset > 0.5:
                self._log(f"🎵 Strong onset: {onset:.3f}")

        except Exception as e:
            self.logger.error(f"Spectral display update error: {e}")

    def _update_displays(self):
        """Periodic display updates."""
        # Keep log manageable
        if self.status_text.document().blockCount() > 100:
            cursor = self.status_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor, 20)
            cursor.removeSelectedText()

    def _log(self, message):
        """Log message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        self.status_text.append(formatted)

    def closeEvent(self, event):
        """Handle close event."""
        self.logger.info("Closing stable advanced MMPA")
        if self.audio_handler.is_active():
            self.audio_handler.stop()
        event.accept()

def main():
    """Main entry point."""
    setup_logging()

    print("🎵 MMPA - STABLE ADVANCED EDITION")
    print("=" * 40)
    print("Stable foundation + Advanced audio analysis")
    print("Manual audio toggle with spectral features")
    print()

    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("MMPA - Stable Advanced")
    app.setApplicationVersion("2.0")

    try:
        # Create and show window
        window = StableAdvancedWindow()
        window.show()

        print("✅ MMPA Stable Advanced running")
        print("🔊 Click 'START Audio' for advanced analysis")

        return app.exec()

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())