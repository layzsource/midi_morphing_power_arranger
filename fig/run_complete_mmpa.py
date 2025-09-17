#!/usr/bin/env python3
"""
MMPA - Complete Working Application
Fully integrated Midi Morphing Power Arranger with GUI, audio, and visual systems.
"""

import sys
import logging
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTimer

# Import MMPA systems
from fig.core.config import get_config
from fig.core.app import EnhancedApplication
from fig.audio.audio_handler import AudioHandler, HAS_SOUNDDEVICE, HAS_PYAUDIO
from fig.midi.midi_handler import MIDIHandler, HAS_RTMIDI
from fig.visuals.scene_manager import SceneManager, ScenePreset
from fig.visuals.particles import ParticleSystem
from fig.visuals.lighting import LightingSystem
from fig.monitoring.performance import PerformanceMonitor
from fig.monitoring.recorder import PerformanceRecorder
from fig.gui.main_window import MMPAMainWindow
from fig.gui.opengl_renderer import OPENGL_AVAILABLE

def setup_logging():
    """Configure logging for the complete application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mmpa_complete.log'),
            logging.StreamHandler()
        ]
    )

class CompleteMMPAApplication:
    """Complete MMPA application with all systems integrated."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.config = get_config()

        # Qt Application
        self.qt_app = QApplication.instance()
        if self.qt_app is None:
            self.qt_app = QApplication(sys.argv)

        self.qt_app.setApplicationName("MMPA - Complete")
        self.qt_app.setApplicationVersion("1.0")

        # Core systems
        self.audio_handler = None
        self.midi_handler = None
        self.scene_manager = None
        self.particle_system = None
        self.lighting_system = None
        self.performance_monitor = None
        self.recorder = None
        self.main_window = None

        # System availability
        self.systems_available = {
            'audio': HAS_SOUNDDEVICE or HAS_PYAUDIO,
            'midi': HAS_RTMIDI,
            'opengl': OPENGL_AVAILABLE
        }

        # Initialize systems
        self._initialize_systems()

    def _initialize_systems(self):
        """Initialize all MMPA systems."""
        self.logger.info("🚀 Initializing Complete MMPA Application")

        # Initialize performance monitor first
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

        # Initialize audio system
        if self.systems_available['audio']:
            try:
                self.audio_handler = AudioHandler(self.config.audio)
                self.logger.info("✅ Audio system initialized")
            except Exception as e:
                self.logger.error(f"❌ Audio system failed: {e}")
                self.systems_available['audio'] = False
        else:
            self.logger.warning("⚠️ Audio system not available (install sounddevice or pyaudio)")

        # Initialize MIDI system
        if self.systems_available['midi']:
            try:
                self.midi_handler = MIDIHandler(self.config.midi)
                self.logger.info("✅ MIDI system initialized")
            except Exception as e:
                self.logger.error(f"❌ MIDI system failed: {e}")
                self.systems_available['midi'] = False
        else:
            self.logger.warning("⚠️ MIDI system not available (install rtmidi)")

        # Initialize recorder
        try:
            self.recorder = PerformanceRecorder(self.config.performance)
            self.logger.info("✅ Performance recorder initialized")
        except Exception as e:
            self.logger.error(f"❌ Performance recorder failed: {e}")

        # Initialize GUI
        try:
            self.main_window = MMPAMainWindow(self, self.config.ui)
            self.logger.info("✅ Main window initialized")
        except Exception as e:
            self.logger.error(f"❌ Main window failed: {e}")
            # Create minimal fallback window
            self.main_window = self._create_minimal_window()

        # Connect all systems
        self._connect_systems()

    def _create_minimal_window(self):
        """Create minimal window if main window fails."""
        from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

        class MinimalWindow(QMainWindow):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("MMPA - Minimal Mode")
                self.setGeometry(200, 200, 600, 400)

                central_widget = QWidget()
                layout = QVBoxLayout()

                title = QLabel("🎼 MMPA - Midi Morphing Power Arranger")
                title.setAlignment(Qt.AlignCenter)
                title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
                layout.addWidget(title)

                subtitle = QLabel("The Language of Signals Becoming Form")
                subtitle.setAlignment(Qt.AlignCenter)
                subtitle.setStyleSheet("font-size: 14px; color: #666; margin: 10px;")
                layout.addWidget(subtitle)

                status = QLabel("Minimal interface mode - check console for details")
                status.setAlignment(Qt.AlignCenter)
                status.setStyleSheet("font-size: 12px; margin: 20px;")
                layout.addWidget(status)

                central_widget.setLayout(layout)
                self.setCentralWidget(central_widget)

        return MinimalWindow()

    def _connect_systems(self):
        """Connect all systems together."""
        self.logger.info("🔗 Connecting MMPA systems")

        # Connect audio to visuals
        if self.audio_handler and self.scene_manager:
            self.audio_handler.audio_processed.connect(self.scene_manager.on_audio_update)
            self.logger.info("✅ Audio → Scene Manager connected")

        # Connect audio to particles
        if self.audio_handler and self.particle_system:
            self.audio_handler.audio_processed.connect(
                lambda data: self.particle_system.set_audio_data(
                    data.get('bass_energy', 0),
                    data.get('mid_energy', 0),
                    data.get('treble_energy', 0),
                    data.get('onset_strength', 0) > 0.3
                )
            )
            self.logger.info("✅ Audio → Particle System connected")

        # Connect audio to lighting
        if self.audio_handler and self.lighting_system:
            self.audio_handler.audio_processed.connect(
                lambda data: self.lighting_system.update_audio_data(
                    data.get('bass_energy', 0),
                    data.get('mid_energy', 0),
                    data.get('treble_energy', 0),
                    data.get('onset_strength', 0) > 0.3
                )
            )
            self.logger.info("✅ Audio → Lighting System connected")

        # Connect MIDI to visuals
        if self.midi_handler and self.scene_manager:
            self.midi_handler.note_on.connect(self.scene_manager.on_midi_note_on)
            self.midi_handler.note_off.connect(self.scene_manager.on_midi_note_off)
            self.logger.info("✅ MIDI → Scene Manager connected")

        # Connect MIDI to particles
        if self.midi_handler and self.particle_system:
            self.midi_handler.note_on.connect(
                lambda note, vel, ch: self.particle_system.set_midi_data(note, vel, ch, True)
            )
            self.logger.info("✅ MIDI → Particle System connected")

        # Connect MIDI to lighting
        if self.midi_handler and self.lighting_system:
            self.midi_handler.note_on.connect(
                lambda note, vel, ch: self.lighting_system.update_midi_data(note, vel, ch, True)
            )
            self.midi_handler.note_off.connect(
                lambda note, vel, ch: self.lighting_system.update_midi_data(note, vel, ch, False)
            )
            self.logger.info("✅ MIDI → Lighting System connected")

        # Connect performance monitor
        if self.performance_monitor:
            # Set system references for quality adjustment
            self.performance_monitor.set_system_references(
                particle_system=self.particle_system,
                scene_manager=self.scene_manager,
                lighting_system=self.lighting_system
            )
            self.logger.info("✅ Performance monitor connected")

        # Connect recorder data sources
        if self.recorder:
            self.recorder.set_data_sources(
                audio_handler=self.audio_handler,
                midi_handler=self.midi_handler,
                scene_manager=self.scene_manager,
                lighting_system=self.lighting_system,
                particle_system=self.particle_system,
                performance_monitor=self.performance_monitor
            )
            self.logger.info("✅ Recorder data sources connected")

        # Connect GUI to systems
        if self.main_window and hasattr(self.main_window, 'connect_signals'):
            self.main_window.connect_signals(self)
            self.logger.info("✅ GUI connections established")

    def start(self):
        """Start all MMPA systems."""
        self.logger.info("🚀 Starting MMPA systems")

        success_count = 0
        total_systems = 0

        # Start performance monitoring
        if self.performance_monitor:
            try:
                self.performance_monitor.start()
                success_count += 1
                self.logger.info("✅ Performance monitor started")
            except Exception as e:
                self.logger.error(f"❌ Performance monitor start failed: {e}")
            total_systems += 1

        # Start audio processing
        if self.audio_handler:
            try:
                if self.audio_handler.start():
                    success_count += 1
                    self.logger.info("✅ Audio processing started")
                else:
                    self.logger.error("❌ Audio processing failed to start")
            except Exception as e:
                self.logger.error(f"❌ Audio start error: {e}")
            total_systems += 1

        # Start MIDI processing
        if self.midi_handler:
            try:
                if self.midi_handler.start():
                    success_count += 1
                    self.logger.info("✅ MIDI processing started")
                else:
                    self.logger.error("❌ MIDI processing failed to start")
            except Exception as e:
                self.logger.error(f"❌ MIDI start error: {e}")
            total_systems += 1

        # Start visual systems
        if self.scene_manager:
            try:
                if self.scene_manager.start():
                    success_count += 1
                    self.logger.info("✅ Scene manager started")
            except Exception as e:
                self.logger.error(f"❌ Scene manager start error: {e}")
            total_systems += 1

        if self.particle_system:
            try:
                self.particle_system.start()
                success_count += 1
                self.logger.info("✅ Particle system started")
            except Exception as e:
                self.logger.error(f"❌ Particle system start error: {e}")
            total_systems += 1

        if self.lighting_system:
            try:
                self.lighting_system.start()
                success_count += 1
                self.logger.info("✅ Lighting system started")
            except Exception as e:
                self.logger.error(f"❌ Lighting system start error: {e}")
            total_systems += 1

        # Show main window
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            self.logger.info("✅ Main window displayed")

        # Apply default scene preset
        if self.scene_manager:
            try:
                self.scene_manager.apply_preset(ScenePreset.CIRCLE, count=8, radius=4.0)
                self.logger.info("✅ Default scene applied")
            except Exception as e:
                self.logger.error(f"❌ Default scene failed: {e}")

        self.logger.info(f"🎉 MMPA startup complete: {success_count}/{total_systems} systems active")

        # Show startup status
        if hasattr(self.main_window, '_log_message'):
            self.main_window._log_message(f"MMPA startup: {success_count}/{total_systems} systems active")

            # Log system availability
            for system, available in self.systems_available.items():
                status = "✅" if available else "❌"
                self.main_window._log_message(f"{status} {system.upper()} system")

        return success_count > 0

    def get_audio_handler(self):
        """Get the audio handler instance."""
        return self.audio_handler

    def get_midi_handler(self):
        """Get the MIDI handler instance."""
        return self.midi_handler

    def get_scene_manager(self):
        """Get the scene manager instance."""
        return self.scene_manager

    def get_performance_monitor(self):
        """Get the performance monitor instance."""
        return self.performance_monitor

    def get_recorder(self):
        """Get the performance recorder instance."""
        return self.recorder

    def shutdown(self):
        """Initiate application shutdown."""
        self.stop()

    def stop(self):
        """Stop all MMPA systems."""
        self.logger.info("🛑 Stopping MMPA systems")

        # Stop in reverse order
        systems_to_stop = [
            ('Lighting', self.lighting_system),
            ('Particle', self.particle_system),
            ('Scene Manager', self.scene_manager),
            ('MIDI', self.midi_handler),
            ('Audio', self.audio_handler),
            ('Performance Monitor', self.performance_monitor)
        ]

        for name, system in systems_to_stop:
            if system and hasattr(system, 'stop'):
                try:
                    system.stop()
                    self.logger.info(f"✅ {name} system stopped")
                except Exception as e:
                    self.logger.error(f"❌ {name} stop error: {e}")

        # Save configuration
        try:
            self.config.save()
            self.logger.info("✅ Configuration saved")
        except Exception as e:
            self.logger.error(f"❌ Configuration save error: {e}")

    def run(self):
        """Run the complete MMPA application."""
        self.logger.info("🎼 MMPA - The Language of Signals Becoming Form")
        self.logger.info("=" * 60)

        try:
            # Start all systems
            if not self.start():
                self.logger.error("❌ Failed to start MMPA - no systems active")
                return 1

            # Show welcome message
            if hasattr(self.main_window, '_log_message'):
                self.main_window._log_message("🎼 Welcome to MMPA!")
                self.main_window._log_message("The Language of Signals Becoming Form")

                if self.systems_available['audio']:
                    self.main_window._log_message("🎵 Audio input ready - make some sound!")

                if self.systems_available['midi']:
                    self.main_window._log_message("🎹 MIDI input ready - connect your keyboard!")

                if not any(self.systems_available.values()):
                    self.main_window._log_message("⚠️ Limited functionality - install audio/MIDI libraries")

            # Run Qt application
            self.logger.info("🎵 MMPA is now running - make some music!")
            result = self.qt_app.exec()

            return result

        except KeyboardInterrupt:
            self.logger.info("👋 MMPA interrupted by user")
            return 0
        except Exception as e:
            self.logger.error(f"❌ MMPA runtime error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self.stop()

def main():
    """Main entry point for complete MMPA application."""
    setup_logging()

    # Check if we can run
    if not (HAS_SOUNDDEVICE or HAS_PYAUDIO or HAS_RTMIDI or OPENGL_AVAILABLE):
        print("❌ Cannot run MMPA - no audio/MIDI/OpenGL libraries available")
        print("Install with: pip install sounddevice rtmidi PyOpenGL PySide6")
        return 1

    # Create and run application
    app = CompleteMMPAApplication()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())