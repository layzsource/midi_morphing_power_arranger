#!/usr/bin/env python3
"""
MMPA - Stable Version
Optimized for stability with core MMPA functionality and simplified GUI.
"""

import sys
import logging
import time
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QSlider, QGroupBox, QGridLayout, QProgressBar, QTextEdit
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QPalette, QColor

# Import core MMPA systems
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
    """Simple text-based visualization for stability."""

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
        title = QLabel("🎼 MMPA Visualization Engine")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("monospace", 14, QFont.Bold))
        layout.addWidget(title)

        # Status display
        self.status_display = QTextEdit()
        self.status_display.setStyleSheet("""
            background-color: #000;
            color: #00ff00;
            border: 1px solid #333;
            font-family: monospace;
            font-size: 12px;
        """)
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)

        # Audio bars
        bars_layout = QHBoxLayout()
        self.audio_bars = {}
        for band in ['Bass', 'Mid', 'Treble']:
            bar_layout = QVBoxLayout()
            bar_layout.addWidget(QLabel(band))

            bar = QProgressBar()
            bar.setOrientation(Qt.Vertical)
            bar.setRange(0, 100)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #333;
                    text-align: center;
                    color: white;
                }}
                QProgressBar::chunk {{
                    background-color: {'#ff4444' if band == 'Bass' else '#44ff44' if band == 'Mid' else '#4444ff'};
                }}
            """)
            self.audio_bars[band.lower()] = bar
            bar_layout.addWidget(bar)

            bars_layout.addLayout(bar_layout)

        layout.addLayout(bars_layout)

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_display)
        self.update_timer.start(100)

        self._log("🎼 MMPA Visualization Ready")

    def _update_display(self):
        """Update the simple visualization."""
        # Create ASCII-style visual based on audio levels
        bass = self.audio_bars['bass'].value()
        mid = self.audio_bars['mid'].value()
        treble = self.audio_bars['treble'].value()

        # Simple ASCII visualization
        visual_lines = []
        visual_lines.append("=" * 40)
        visual_lines.append(f"BASS:   {'█' * (bass // 10)} {bass}%")
        visual_lines.append(f"MID:    {'█' * (mid // 10)} {mid}%")
        visual_lines.append(f"TREBLE: {'█' * (treble // 10)} {treble}%")
        visual_lines.append("=" * 40)

        # Add some "particles" based on audio
        if bass > 70 or mid > 70 or treble > 70:
            visual_lines.append("✨ " * 10)

        if bass > 50:
            visual_lines.append("🔥 BASS ACTIVE")

        if treble > 60:
            visual_lines.append("⚡ TREBLE ACTIVE")

        visual_lines.append("")
        visual_lines.append("🎵 The Language of Signals Becoming Form")

        # Update display
        self.status_display.clear()
        for line in visual_lines:
            self.status_display.append(line)

    def update_audio_data(self, audio_data):
        """Update with audio data."""
        bass = min(100, int(audio_data.get('bass_energy', 0) * 100))
        mid = min(100, int(audio_data.get('mid_energy', 0) * 100))
        treble = min(100, int(audio_data.get('treble_energy', 0) * 100))

        self.audio_bars['bass'].setValue(bass)
        self.audio_bars['mid'].setValue(mid)
        self.audio_bars['treble'].setValue(treble)

        # Log significant events
        if bass > 80:
            self._log("🔥 Strong bass detected!")
        if treble > 80:
            self._log("⚡ High treble spike!")

    def update_midi_data(self, note, velocity, note_on):
        """Update with MIDI data."""
        if note_on:
            note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note % 12]
            octave = note // 12 - 1
            self._log(f"🎹 MIDI: {note_name}{octave} vel:{velocity}")

    def _log(self, message):
        """Add message to display."""
        current_time = time.strftime("%H:%M:%S")
        self.status_display.append(f"[{current_time}] {message}")

        # Auto-scroll
        scrollbar = self.status_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class StableMMPAMainWindow(QMainWindow):
    """Stable main window with essential controls."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MMPA - Stable Version")
        self.setGeometry(200, 200, 800, 600)

        # Core systems
        self.config = get_config()
        self.audio_handler = None
        self.midi_handler = None
        self.scene_manager = None
        self.particle_system = None
        self.lighting_system = None
        self.performance_monitor = None

        # Create UI
        self._create_ui()

        # Initialize systems
        self._initialize_systems()

        # Start update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_status)
        self.update_timer.start(200)  # 5 Hz updates

    def _create_ui(self):
        """Create simple, stable UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Left panel - Controls
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # System status
        status_group = QGroupBox("System Status")
        status_layout = QGridLayout(status_group)

        self.status_labels = {}
        systems = ['Audio', 'MIDI', 'Visuals', 'Monitor']
        for i, system in enumerate(systems):
            status_layout.addWidget(QLabel(f"{system}:"), i, 0)
            label = QLabel("❌ Inactive")
            label.setStyleSheet("color: #ff4444;")
            self.status_labels[system.lower()] = label
            status_layout.addWidget(label, i, 1)

        control_layout.addWidget(status_group)

        # Scene controls
        scene_group = QGroupBox("Scene Control")
        scene_layout = QVBoxLayout(scene_group)

        # Scene preset buttons
        presets = ["Circle", "Spiral", "Grid", "Random"]
        for preset in presets:
            btn = QPushButton(preset)
            btn.clicked.connect(lambda checked, p=preset: self._apply_scene_preset(p))
            scene_layout.addWidget(btn)

        control_layout.addWidget(scene_group)

        # Audio sensitivity
        audio_group = QGroupBox("Audio Sensitivity")
        audio_layout = QVBoxLayout(audio_group)

        for band in ['Bass', 'Mid', 'Treble']:
            slider_layout = QHBoxLayout()
            slider_layout.addWidget(QLabel(f"{band}:"))
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(50)
            slider_layout.addWidget(slider)
            audio_layout.addLayout(slider_layout)

        control_layout.addWidget(audio_group)

        # Performance info
        perf_group = QGroupBox("Performance")
        perf_layout = QGridLayout(perf_group)

        self.perf_labels = {}
        metrics = [('fps', 'FPS'), ('cpu', 'CPU %'), ('memory', 'Memory MB')]
        for i, (key, name) in enumerate(metrics):
            perf_layout.addWidget(QLabel(f"{name}:"), i, 0)
            label = QLabel("--")
            label.setStyleSheet("font-family: monospace; color: #00aa00;")
            self.perf_labels[key] = label
            perf_layout.addWidget(label, i, 1)

        control_layout.addWidget(perf_group)

        control_panel.setMaximumWidth(250)
        layout.addWidget(control_panel)

        # Right panel - Visualization
        self.viz_widget = SimpleVisualizationWidget()
        layout.addWidget(self.viz_widget)

    def _initialize_systems(self):
        """Initialize MMPA systems safely."""
        self._log("🚀 Initializing MMPA systems...")

        # Performance monitor
        try:
            self.performance_monitor = PerformanceMonitor(self.config.performance)
            self.performance_monitor.start()
            self.status_labels['monitor'].setText("✅ Active")
            self.status_labels['monitor'].setStyleSheet("color: #44ff44;")
            self._log("✅ Performance monitor started")
        except Exception as e:
            self._log(f"❌ Performance monitor failed: {e}")

        # Visual systems
        try:
            self.scene_manager = SceneManager(self.config.visual)
            self.particle_system = ParticleSystem(self.config.visual.particle_count_max)
            self.lighting_system = LightingSystem()

            # Start visual systems
            self.scene_manager.start()
            self.particle_system.start()
            self.lighting_system.start()

            # Apply default scene
            self.scene_manager.apply_preset(ScenePreset.CIRCLE, count=6, radius=3.0)

            self.status_labels['visuals'].setText("✅ Active")
            self.status_labels['visuals'].setStyleSheet("color: #44ff44;")
            self._log("✅ Visual systems started")
        except Exception as e:
            self._log(f"❌ Visual systems failed: {e}")

        # Audio system
        if HAS_SOUNDDEVICE or HAS_PYAUDIO:
            try:
                self.audio_handler = AudioHandler(self.config.audio)
                if self.audio_handler.start():
                    # Connect audio signals
                    self.audio_handler.audio_processed.connect(self._on_audio_data)
                    self.status_labels['audio'].setText("✅ Active")
                    self.status_labels['audio'].setStyleSheet("color: #44ff44;")
                    self._log("✅ Audio system started")
                else:
                    self._log("❌ Audio system failed to start")
            except Exception as e:
                self._log(f"❌ Audio system error: {e}")
        else:
            self._log("⚠️ No audio backend available")

        # MIDI system
        if HAS_RTMIDI:
            try:
                self.midi_handler = MIDIHandler(self.config.midi)
                if self.midi_handler.start():
                    # Connect MIDI signals
                    self.midi_handler.note_on.connect(self._on_midi_note_on)
                    self.midi_handler.note_off.connect(self._on_midi_note_off)
                    self.status_labels['midi'].setText("✅ Active")
                    self.status_labels['midi'].setStyleSheet("color: #44ff44;")

                    # List connected devices
                    devices = self.midi_handler.get_connected_devices()
                    if devices:
                        device_names = list(devices.values())
                        self._log(f"✅ MIDI connected: {', '.join(device_names)}")
                    else:
                        self._log("✅ MIDI system ready (no devices connected)")
                else:
                    self._log("❌ MIDI system failed to start")
            except Exception as e:
                self._log(f"❌ MIDI system error: {e}")
        else:
            self._log("⚠️ MIDI not available (install rtmidi)")

        self._log("🎵 MMPA systems initialized - ready to make music!")

    def _apply_scene_preset(self, preset_name):
        """Apply scene preset."""
        if self.scene_manager:
            try:
                preset_map = {
                    "Circle": ScenePreset.CIRCLE,
                    "Spiral": ScenePreset.SPIRAL,
                    "Grid": ScenePreset.GRID,
                    "Random": ScenePreset.RANDOM
                }
                if preset_name in preset_map:
                    self.scene_manager.apply_preset(preset_map[preset_name], count=8, radius=4.0)
                    self._log(f"✅ Applied scene: {preset_name}")
            except Exception as e:
                self._log(f"❌ Scene preset error: {e}")

    def _on_audio_data(self, audio_data):
        """Handle audio data."""
        # Update visualization
        self.viz_widget.update_audio_data(audio_data)

        # Update scene manager
        if self.scene_manager:
            self.scene_manager.on_audio_update(audio_data)

        # Update particle system
        if self.particle_system:
            bass = audio_data.get('bass_energy', 0)
            mid = audio_data.get('mid_energy', 0)
            treble = audio_data.get('treble_energy', 0)
            onset = audio_data.get('onset_strength', 0) > 0.3
            self.particle_system.set_audio_data(bass, mid, treble, onset)

        # Update lighting
        if self.lighting_system:
            bass = audio_data.get('bass_energy', 0)
            mid = audio_data.get('mid_energy', 0)
            treble = audio_data.get('treble_energy', 0)
            onset = audio_data.get('onset_strength', 0) > 0.3
            self.lighting_system.update_audio_data(bass, mid, treble, onset)

    def _on_midi_note_on(self, note, velocity, channel):
        """Handle MIDI note on."""
        # Update visualization
        self.viz_widget.update_midi_data(note, velocity, True)

        # Update scene manager
        if self.scene_manager:
            self.scene_manager.on_midi_note_on(note, velocity, channel)

        # Update particle system
        if self.particle_system:
            self.particle_system.set_midi_data(note, velocity, channel, True)

        # Update lighting
        if self.lighting_system:
            self.lighting_system.update_midi_data(note, velocity, channel, True)

    def _on_midi_note_off(self, note, velocity, channel):
        """Handle MIDI note off."""
        self.viz_widget.update_midi_data(note, velocity, False)

        # Update systems
        if self.scene_manager:
            self.scene_manager.on_midi_note_off(note, velocity, channel)
        if self.lighting_system:
            self.lighting_system.update_midi_data(note, velocity, channel, False)

    def _update_status(self):
        """Update status displays."""
        # Update performance metrics
        if self.performance_monitor:
            metrics = self.performance_monitor.get_current_metrics()
            self.perf_labels['fps'].setText(f"{metrics.get('fps', 0):.1f}")
            self.perf_labels['cpu'].setText(f"{metrics.get('cpu_percent', 0):.1f}")
            self.perf_labels['memory'].setText(f"{metrics.get('memory_mb', 0):.0f}")

    def _log(self, message):
        """Log message to visualization widget."""
        self.viz_widget._log(message)

    def closeEvent(self, event):
        """Handle close event."""
        self._log("🛑 Shutting down MMPA...")

        # Stop all systems
        systems = [
            ('Performance Monitor', self.performance_monitor),
            ('Lighting System', self.lighting_system),
            ('Particle System', self.particle_system),
            ('Scene Manager', self.scene_manager),
            ('MIDI Handler', self.midi_handler),
            ('Audio Handler', self.audio_handler)
        ]

        for name, system in systems:
            if system and hasattr(system, 'stop'):
                try:
                    system.stop()
                    self._log(f"✅ {name} stopped")
                except Exception as e:
                    self._log(f"❌ {name} stop error: {e}")

        # Save configuration
        try:
            self.config.save()
            self._log("✅ Configuration saved")
        except:
            pass

        event.accept()

def main():
    """Main entry point."""
    setup_logging()

    print("🎼 MMPA - Stable Version")
    print("The Language of Signals Becoming Form")
    print("Optimized for reliability and performance")
    print("=" * 50)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MMPA Stable")

    # Create main window
    window = StableMMPAMainWindow()
    window.show()

    # Run application
    try:
        return app.exec()
    except KeyboardInterrupt:
        print("\n👋 MMPA interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ MMPA error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())