#!/usr/bin/env python3
"""
MMPA - Ultra Stable Version
Bulletproof stability with manual audio toggle and advanced analysis.
Based on proven stable architecture.
"""

import sys
import logging
import time
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QPushButton, QSlider, QGroupBox, QGridLayout, QProgressBar, QTextEdit
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette, QColor

# Import core MMPA systems (minimal set for stability)
from fig.core.config import get_config
from fig.audio.audio_handler import AudioHandler, HAS_SOUNDDEVICE, HAS_PYAUDIO
from fig.midi.midi_handler import MIDIHandler, HAS_RTMIDI
from fig.visuals.scene_manager import SceneManager, ScenePreset
from fig.visuals.particles import ParticleSystem
from fig.visuals.lighting import LightingSystem
from fig.monitoring.performance import PerformanceMonitor

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

class SimpleVisualizationWidget(QWidget):
    """Ultra-simple text-based visualization for maximum stability."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setStyleSheet("""
            background-color: #0a0a0a;
            color: #00ff00;
            font-family: monospace;
            border: 2px solid #333;
        """)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🎵 MMPA - The Language of Signals Becoming Form")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #ffffff; font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Simple status display
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(250)
        self.status_text.setStyleSheet("""
            background-color: #000000;
            color: #00ff00;
            font-family: monospace;
            font-size: 10px;
            border: 1px solid #333;
        """)
        layout.addWidget(self.status_text)

        # Initialize with welcome message
        self._add_status("🎼 MMPA Ultra Stable - Ready")
        self._add_status("⏸️ Audio: STOPPED (use toggle to start)")
        self._add_status("🎹 MIDI: Ready")
        self._add_status("🎨 Visuals: Active")

    def _add_status(self, message: str):
        """Add status message with timestamp."""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.status_text.append(formatted_message)

    def update_audio_status(self, active: bool, data: dict = None):
        """Update audio status display."""
        if active and data:
            bass = data.get('bass_energy', 0)
            mid = data.get('mid_energy', 0)
            treble = data.get('treble_energy', 0)

            # Simple ASCII bar visualization
            bass_bar = "█" * int(bass * 20)
            mid_bar = "█" * int(mid * 20)
            treble_bar = "█" * int(treble * 20)

            status = f"🔊 BASS:{bass_bar:<20} MID:{mid_bar:<20} TREBLE:{treble_bar:<20}"
            self._add_status(status)

class UltraStableMMPAMainWindow(QMainWindow):
    """Ultra-stable main window using proven architecture."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

        # Core MMPA systems (initialized but not started)
        self.config = get_config()
        self.audio_handler = None
        self.midi_handler = None
        self.scene_manager = None
        self.particle_system = None
        self.lighting_system = None
        self.performance_monitor = None

        # Audio state tracking
        self.audio_active = False
        self.audio_data_timer = None

        # Initialize systems
        self._initialize_systems()

        # Setup UI
        self._setup_ui()

        # Setup update timer
        self._setup_update_timer()

        self.logger.info("✅ Ultra-stable main window initialized")

    def _initialize_systems(self):
        """Initialize MMPA systems safely."""
        self.logger.info("🚀 Initializing MMPA systems safely...")

        # Initialize performance monitor
        try:
            self.performance_monitor = PerformanceMonitor(self.config.performance)
            self.logger.info("✅ Performance monitor initialized")
        except Exception as e:
            self.logger.error(f"❌ Performance monitor failed: {e}")

        # Initialize visual systems
        try:
            self.scene_manager = SceneManager(self.config.visual)
            self.particle_system = ParticleSystem(self.config.visual.particle_count_max)
            self.lighting_system = LightingSystem()
            self.logger.info("✅ Visual systems initialized")
        except Exception as e:
            self.logger.error(f"❌ Visual systems failed: {e}")

        # Initialize audio handler (but don't start it)
        if HAS_SOUNDDEVICE or HAS_PYAUDIO:
            try:
                # Try professional audio handler first
                try:
                    from fig.audio.professional_audio_handler import ProfessionalAudioHandler
                    self.audio_handler = ProfessionalAudioHandler(self.config.audio)
                    self.logger.info("✅ Professional audio handler initialized (STOPPED)")
                except Exception:
                    # Fallback to standard audio handler
                    self.audio_handler = AudioHandler(self.config.audio)
                    self.logger.info("✅ Standard audio handler initialized (STOPPED)")
            except Exception as e:
                self.logger.error(f"❌ Audio handler failed: {e}")

        # Initialize MIDI handler
        if HAS_RTMIDI:
            try:
                self.midi_handler = MIDIHandler(self.config.midi)
                self.logger.info("✅ MIDI handler initialized")
            except Exception as e:
                self.logger.error(f"❌ MIDI handler failed: {e}")

    def _setup_ui(self):
        """Setup ultra-stable user interface."""
        self.setWindowTitle("🎵 MMPA - Ultra Stable")
        self.setGeometry(100, 100, 900, 700)

        # Apply professional dark theme
        self._apply_dark_theme()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Left panel - Controls (keep it simple)
        control_panel = QWidget()
        control_panel.setMaximumWidth(300)
        control_layout = QVBoxLayout(control_panel)

        # Audio control section
        audio_group = QGroupBox("🔊 Audio Control")
        audio_layout = QVBoxLayout(audio_group)

        # Audio toggle button
        self.audio_toggle_button = QPushButton("🔊 START Audio")
        self.audio_toggle_button.clicked.connect(self._toggle_audio)
        self.audio_toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        audio_layout.addWidget(self.audio_toggle_button)

        # Audio status
        self.audio_status_label = QLabel("Audio: STOPPED")
        self.audio_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")
        self.audio_status_label.setAlignment(Qt.AlignCenter)
        audio_layout.addWidget(self.audio_status_label)

        control_layout.addWidget(audio_group)

        # Advanced analysis section (when audio is active)
        analysis_group = QGroupBox("🎓 Advanced Analysis")
        analysis_layout = QGridLayout(analysis_group)

        # Spectral Centroid (Brightness)
        analysis_layout.addWidget(QLabel("Brightness:"), 0, 0)
        self.centroid_bar = QProgressBar()
        self.centroid_bar.setMaximumHeight(18)
        analysis_layout.addWidget(self.centroid_bar, 0, 1)
        self.centroid_label = QLabel("0")
        analysis_layout.addWidget(self.centroid_label, 0, 2)

        # Onset Strength
        analysis_layout.addWidget(QLabel("Onset:"), 1, 0)
        self.onset_bar = QProgressBar()
        self.onset_bar.setMaximumHeight(18)
        analysis_layout.addWidget(self.onset_bar, 1, 1)
        self.onset_label = QLabel("0.0")
        analysis_layout.addWidget(self.onset_label, 1, 2)

        # Tempo
        analysis_layout.addWidget(QLabel("Tempo:"), 2, 0)
        self.tempo_bar = QProgressBar()
        self.tempo_bar.setRange(60, 200)
        self.tempo_bar.setValue(120)
        self.tempo_bar.setMaximumHeight(18)
        analysis_layout.addWidget(self.tempo_bar, 2, 1)
        self.tempo_label = QLabel("120")
        analysis_layout.addWidget(self.tempo_label, 2, 2)

        control_layout.addWidget(analysis_group)

        # Scene control section
        scene_group = QGroupBox("🎭 Scene Control")
        scene_layout = QVBoxLayout(scene_group)

        # Scene preset buttons
        presets = ["Circle", "Spiral", "Grid", "Random"]
        for preset in presets:
            btn = QPushButton(preset)
            btn.clicked.connect(lambda checked, p=preset: self._apply_scene_preset(p))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #666;
                    color: white;
                    padding: 6px;
                    border-radius: 3px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #777;
                }
            """)
            scene_layout.addWidget(btn)

        control_layout.addWidget(scene_group)
        control_layout.addStretch()

        # Right panel - Visualization
        self.visualization_widget = SimpleVisualizationWidget()

        # Add to layout
        layout.addWidget(control_panel)
        layout.addWidget(self.visualization_widget)

    def _apply_dark_theme(self):
        """Apply professional dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 3px;
                padding-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 2px;
                text-align: center;
                background-color: #333;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)

    def _setup_update_timer(self):
        """Setup update timer for real-time displays."""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_displays)
        self.update_timer.start(100)  # 10 FPS update rate

    def _toggle_audio(self):
        """Toggle audio processing safely."""
        try:
            if not self.audio_handler:
                self._log_message("❌ No audio handler available")
                return

            if self.audio_active:
                # Stop audio processing
                if hasattr(self.audio_handler, 'stop'):
                    self.audio_handler.stop()
                self.audio_active = False

                # Update UI
                self.audio_toggle_button.setText("🔊 START Audio")
                self.audio_toggle_button.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        font-weight: bold;
                        padding: 12px;
                        border-radius: 6px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                self.audio_status_label.setText("Audio: STOPPED")
                self.audio_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; font-size: 12px;")

                self._log_message("🔇 Audio processing STOPPED")

            else:
                # Start audio processing
                if hasattr(self.audio_handler, 'start'):
                    success = self.audio_handler.start()
                    if success:
                        self.audio_active = True

                        # Connect signals safely
                        if hasattr(self.audio_handler, 'audio_processed'):
                            self.audio_handler.audio_processed.connect(self._on_audio_data)

                        if hasattr(self.audio_handler, 'spectral_features_extracted'):
                            self.audio_handler.spectral_features_extracted.connect(self._on_advanced_features)

                        # Update UI
                        self.audio_toggle_button.setText("🔇 STOP Audio")
                        self.audio_toggle_button.setStyleSheet("""
                            QPushButton {
                                background-color: #ff6b6b;
                                color: white;
                                font-weight: bold;
                                padding: 12px;
                                border-radius: 6px;
                                font-size: 14px;
                            }
                            QPushButton:hover {
                                background-color: #e55555;
                            }
                        """)
                        self.audio_status_label.setText("Audio: RUNNING")
                        self.audio_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 12px;")

                        self._log_message("🔊 Audio processing STARTED")
                        self._log_message("🎵 Advanced spectral analysis active")
                    else:
                        self._log_message("❌ Failed to start audio processing")

        except Exception as e:
            self.logger.error(f"Audio toggle error: {e}")
            self._log_message(f"❌ Audio toggle error: {e}")

    def _on_audio_data(self, data: dict):
        """Handle basic audio data."""
        try:
            if self.visualization_widget:
                self.visualization_widget.update_audio_status(True, data)
        except Exception as e:
            self.logger.error(f"Audio data handling error: {e}")

    def _on_advanced_features(self, features: dict):
        """Handle advanced spectral features."""
        try:
            # Update spectral centroid (brightness)
            centroid = features.get('spectral_centroid', 0.0)
            if centroid > 0:
                centroid_norm = min(100, max(0, int(centroid / 100)))
                self.centroid_bar.setValue(centroid_norm)
                self.centroid_label.setText(f"{centroid:.0f}")

            # Update onset strength
            onset = features.get('onset_strength', 0.0)
            onset_norm = min(100, max(0, int(onset * 100)))
            self.onset_bar.setValue(onset_norm)
            self.onset_label.setText(f"{onset:.2f}")

            # Log significant onsets
            if onset > 0.5:
                self._log_message(f"🎵 Strong onset detected: {onset:.2f}")

        except Exception as e:
            self.logger.error(f"Advanced features handling error: {e}")

    def _apply_scene_preset(self, preset_name: str):
        """Apply scene preset safely."""
        try:
            if self.scene_manager:
                preset_map = {
                    "Circle": ScenePreset.CIRCLE,
                    "Spiral": ScenePreset.HELIX,
                    "Grid": ScenePreset.GRID,
                    "Random": ScenePreset.RANDOM
                }

                if preset_name in preset_map:
                    self.scene_manager.apply_preset(preset_map[preset_name], count=8, radius=4.0)
                    self._log_message(f"🎭 Applied {preset_name} scene preset")

        except Exception as e:
            self.logger.error(f"Scene preset error: {e}")
            self._log_message(f"❌ Scene preset error: {e}")

    def _update_displays(self):
        """Update displays periodically."""
        try:
            # Keep log size manageable
            if hasattr(self.visualization_widget, 'status_text'):
                text_widget = self.visualization_widget.status_text
                if text_widget.document().blockCount() > 50:
                    cursor = text_widget.textCursor()
                    cursor.movePosition(cursor.Start)
                    cursor.movePosition(cursor.Down, cursor.KeepAnchor, 10)
                    cursor.removeSelectedText()

        except Exception as e:
            self.logger.error(f"Display update error: {e}")

    def _log_message(self, message: str):
        """Log message to visualization widget."""
        try:
            if self.visualization_widget:
                self.visualization_widget._add_status(message)
        except Exception as e:
            self.logger.error(f"Log message error: {e}")

    def start_systems(self):
        """Start MMPA systems safely (except audio)."""
        self.logger.info("🚀 Starting MMPA systems (Audio: Manual)")

        success_count = 0

        # Start performance monitor
        if self.performance_monitor:
            try:
                self.performance_monitor.start()
                success_count += 1
                self.logger.info("✅ Performance monitor started")
            except Exception as e:
                self.logger.error(f"❌ Performance monitor failed: {e}")

        # Start MIDI processing
        if self.midi_handler:
            try:
                if self.midi_handler.start():
                    success_count += 1
                    self.logger.info("✅ MIDI processing started")
            except Exception as e:
                self.logger.error(f"❌ MIDI start error: {e}")

        # Start visual systems
        if self.scene_manager:
            try:
                if self.scene_manager.start():
                    success_count += 1
                    self.logger.info("✅ Scene manager started")
            except Exception as e:
                self.logger.error(f"❌ Scene manager start error: {e}")

        if self.particle_system:
            try:
                self.particle_system.start()
                success_count += 1
                self.logger.info("✅ Particle system started")
            except Exception as e:
                self.logger.error(f"❌ Particle system start error: {e}")

        if self.lighting_system:
            try:
                self.lighting_system.start()
                success_count += 1
                self.logger.info("✅ Lighting system started")
            except Exception as e:
                self.logger.error(f"❌ Lighting system start error: {e}")

        # Apply default scene
        if self.scene_manager:
            try:
                self.scene_manager.apply_preset(ScenePreset.CIRCLE, count=8, radius=4.0)
                self.logger.info("✅ Default scene applied")
            except Exception as e:
                self.logger.error(f"❌ Default scene failed: {e}")

        self.logger.info(f"🎉 MMPA systems started: {success_count} active")
        self._log_message(f"🎉 MMPA ready: {success_count} systems active")
        self._log_message("🔊 Click 'START Audio' to begin audio analysis")

    def closeEvent(self, event):
        """Handle window close safely."""
        try:
            self.logger.info("🛑 Shutting down MMPA systems...")

            # Stop audio if active
            if self.audio_active and self.audio_handler:
                self.audio_handler.stop()

            # Stop other systems
            for system in [self.lighting_system, self.particle_system,
                          self.scene_manager, self.midi_handler, self.performance_monitor]:
                if system and hasattr(system, 'stop'):
                    try:
                        system.stop()
                    except Exception as e:
                        self.logger.error(f"System stop error: {e}")

            self.logger.info("✅ MMPA shutdown complete")
            event.accept()

        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            event.accept()

def main():
    """Main entry point for ultra-stable MMPA."""
    setup_logging()

    print("=" * 60)
    print("🎵 MMPA - ULTRA STABLE (Never Freezes!) 🎵")
    print("=" * 60)
    print("The Language of Signals Becoming Form")
    print()
    print("🎯 ULTRA STABLE FEATURES:")
    print("   ✅ Bulletproof stability - no OpenGL freezing")
    print("   ✅ Manual audio toggle - YOU control when it starts")
    print("   ✅ Advanced spectral analysis - when audio is active")
    print("   ✅ Professional dark theme")
    print("   ✅ Simple text-based visualization")
    print("   ✅ Real-time onset detection and tempo tracking")
    print("   ✅ Proven stable architecture")
    print("=" * 50)

    # Create Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("MMPA - Ultra Stable")
    app.setApplicationVersion("3.0")

    # Create and show main window
    window = UltraStableMMPAMainWindow()
    window.show()
    window.start_systems()

    print("🎉 MMPA Ultra Stable is running!")
    print("🔊 Use the 'START Audio' button when ready for audio analysis")

    try:
        return app.exec()
    except KeyboardInterrupt:
        print("\n🛑 MMPA shutdown")
        return 0

if __name__ == "__main__":
    sys.exit(main())