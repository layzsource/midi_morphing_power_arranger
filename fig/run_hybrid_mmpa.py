#!/usr/bin/env python3
"""
MMPA - Hybrid Advanced Version
Combines stable GUI from stable version with advanced audio analysis from professional version.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor

# Import the complete application
from run_complete_mmpa import CompleteMMPAApplication, setup_logging

class HybridMMPAApplication(CompleteMMPAApplication):
    """Hybrid MMPA with advanced audio analysis and stable GUI."""

    def _initialize_systems(self):
        """Initialize systems with advanced audio analysis but stable GUI."""
        # Initialize everything except GUI first
        self.logger.info("🚀 Initializing Hybrid MMPA Application")

        # Initialize performance monitor first
        try:
            from fig.monitoring.performance import PerformanceMonitor
            self.performance_monitor = PerformanceMonitor(self.config.performance)
            self.logger.info("✅ Performance monitor initialized")
        except Exception as e:
            self.logger.error(f"❌ Performance monitor failed: {e}")

        # Initialize visual systems
        try:
            from fig.visuals.scene_manager import SceneManager
            from fig.visuals.particles import ParticleSystem
            from fig.visuals.lighting import LightingSystem

            self.scene_manager = SceneManager(self.config.visual)
            self.particle_system = ParticleSystem(self.config.visual.particle_count_max)
            self.lighting_system = LightingSystem()
            self.logger.info("✅ Visual systems initialized")
        except Exception as e:
            self.logger.error(f"❌ Visual systems failed: {e}")

        # Initialize ADVANCED audio system
        if self.systems_available['audio']:
            try:
                from fig.audio.professional_audio_handler import ProfessionalAudioHandler
                self.audio_handler = ProfessionalAudioHandler(self.config.audio)
                self.logger.info("✅ Advanced professional audio system initialized")
            except Exception as e:
                self.logger.error(f"❌ Professional audio system failed, using standard: {e}")
                # Fallback to standard audio handler
                from fig.audio.audio_handler import AudioHandler
                self.audio_handler = AudioHandler(self.config.audio)
                self.logger.info("✅ Standard audio system initialized")

        # Initialize MIDI system
        if self.systems_available['midi']:
            try:
                from fig.midi.midi_handler import MIDIHandler
                self.midi_handler = MIDIHandler(self.config.midi)
                self.logger.info("✅ MIDI system initialized")
            except Exception as e:
                self.logger.error(f"❌ MIDI system failed: {e}")
                self.systems_available['midi'] = False

        # Initialize recorder
        try:
            from fig.monitoring.recorder import PerformanceRecorder
            self.recorder = PerformanceRecorder(self.config.performance)
            self.logger.info("✅ Performance recorder initialized")
        except Exception as e:
            self.logger.error(f"❌ Performance recorder failed: {e}")

        # Initialize STABLE GUI (use the working one)
        try:
            from fig.gui.hybrid_main_window import HybridMMPAMainWindow
            self.main_window = HybridMMPAMainWindow(self, self.config.ui)
            self.logger.info("✅ Hybrid main window initialized")
        except Exception as e:
            self.logger.error(f"❌ Hybrid main window failed, using standard: {e}")
            # Fallback to standard main window
            from fig.gui.main_window import MMPAMainWindow
            self.main_window = MMPAMainWindow(self, self.config.ui)
            self.logger.info("✅ Standard main window initialized")

        # Connect all systems
        self._connect_systems()

def apply_professional_theme(app):
    """Apply the professional dark theme."""
    app.setStyle('Fusion')

    # Apply professional dark theme
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)

def main():
    """Main entry point for hybrid MMPA."""
    setup_logging()

    print("=" * 80)
    print("🎵 MIDI MORPHING POWER ARRANGER (MMPA) - Hybrid Advanced Version 🎵")
    print("=" * 80)
    print("The Language of Signals Becoming Form")
    print()
    print("🎯 HYBRID FEATURES:")
    print("   ✅ Advanced professional audio analysis")
    print("   ✅ Comprehensive spectral features (centroid, rolloff, bandwidth)")
    print("   ✅ Advanced onset detection with adaptive thresholds")
    print("   ✅ Beat detection and tempo tracking")
    print("   ✅ Zero-crossing rate and spectral flux analysis")
    print("   ✅ MFCC and mel-spectrogram support")
    print("   ✅ Stable, tested GUI interface")
    print("   ✅ Professional dark theme")
    print("   ✅ All modular systems integrated")
    print("=" * 60)

    # Create and configure Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("MMPA - Hybrid Advanced")
    app.setApplicationVersion("2.1")

    # Apply professional theme
    apply_professional_theme(app)

    # Create and run hybrid application
    mmpa_app = HybridMMPAApplication()
    return mmpa_app.run()

if __name__ == "__main__":
    sys.exit(main())