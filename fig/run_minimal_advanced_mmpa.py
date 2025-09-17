#!/usr/bin/env python3
"""
MMPA - Minimal Advanced Version
Advanced audio analysis with minimal, stable GUI to avoid freezing issues.
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

# Import the complete application as base
from run_complete_mmpa import CompleteMMPAApplication, setup_logging

class MinimalAdvancedMMPAApplication(CompleteMMPAApplication):
    """Minimal MMPA with advanced audio analysis but simple, stable GUI."""

    def _initialize_systems(self):
        """Initialize systems with advanced audio analysis but minimal GUI. Audio starts disabled."""
        self.logger.info("🚀 Initializing Minimal Advanced MMPA Application")

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

        # Initialize ADVANCED audio system but DON'T START IT
        if self.systems_available['audio']:
            try:
                from fig.audio.professional_audio_handler import ProfessionalAudioHandler
                self.audio_handler = ProfessionalAudioHandler(self.config.audio)
                self.audio_active = False  # Track audio state
                self.logger.info("✅ Advanced professional audio system initialized (STOPPED)")
            except Exception as e:
                self.logger.error(f"❌ Professional audio system failed, using standard: {e}")
                from fig.audio.audio_handler import AudioHandler
                self.audio_handler = AudioHandler(self.config.audio)
                self.audio_active = False
                self.logger.info("✅ Standard audio system initialized (STOPPED)")

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

        # Initialize MINIMAL STABLE GUI
        try:
            from fig.gui.simple_advanced_window import SimpleAdvancedWindow
            self.main_window = SimpleAdvancedWindow(self, self.config.ui)
            self.logger.info("✅ Simple advanced window initialized")
        except Exception as e:
            self.logger.error(f"❌ Simple advanced window failed, using standard: {e}")
            # Fallback to standard main window
            from fig.gui.main_window import MMPAMainWindow
            self.main_window = MMPAMainWindow(self, self.config.ui)
            self.logger.info("✅ Standard main window initialized")

        # Connect all systems
        self._connect_systems()

    def toggle_audio(self):
        """Toggle audio processing on/off."""
        if not self.audio_handler:
            return False

        try:
            if self.audio_active:
                # Stop audio
                if hasattr(self.audio_handler, 'stop'):
                    self.audio_handler.stop()
                self.audio_active = False
                self.logger.info("🔇 Audio processing STOPPED")
                return False
            else:
                # Start audio
                if hasattr(self.audio_handler, 'start'):
                    success = self.audio_handler.start()
                    if success:
                        self.audio_active = True
                        self.logger.info("🔊 Audio processing STARTED")
                        return True
                    else:
                        self.logger.error("❌ Failed to start audio processing")
                        return False
        except Exception as e:
            self.logger.error(f"Audio toggle error: {e}")
            return False

    def is_audio_active(self):
        """Check if audio is currently active."""
        return getattr(self, 'audio_active', False)

    def start(self):
        """Start MMPA systems but skip audio (manual toggle only)."""
        self.logger.info("🚀 Starting MMPA systems (Audio: Manual Toggle)")

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

        # SKIP AUDIO STARTUP - will be manually toggled
        if self.audio_handler:
            self.logger.info("⏸️ Audio system ready (use toggle to start)")
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
                from fig.visuals.scene_manager import ScenePreset
                self.scene_manager.apply_preset(ScenePreset.CIRCLE, count=8, radius=4.0)
                self.logger.info("✅ Default scene applied")
            except Exception as e:
                self.logger.error(f"❌ Default scene failed: {e}")

        self.logger.info(f"🎉 MMPA startup complete: {success_count}/{total_systems} systems active")
        self.logger.info("🔊 Use Audio Toggle button to start audio processing")

        # Show startup status
        if hasattr(self.main_window, '_log_message'):
            self.main_window._log_message(f"MMPA startup: {success_count}/{total_systems} systems active")
            self.main_window._log_message("🔊 Audio ready - use toggle button to start")

            # Log system availability
            for system, available in self.systems_available.items():
                status = "✅" if available else "❌"
                self.main_window._log_message(f"{status} {system.upper()} system")

        return success_count > 0

def apply_professional_theme(app):
    """Apply professional dark theme."""
    app.setStyle('Fusion')
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    app.setPalette(dark_palette)

def main():
    """Main entry point for minimal advanced MMPA."""
    setup_logging()

    print("=" * 70)
    print("🎵 MMPA - MINIMAL ADVANCED (Stability-First) 🎵")
    print("=" * 70)
    print("The Language of Signals Becoming Form")
    print()
    print("🎯 MINIMAL ADVANCED FEATURES:")
    print("   ✅ Advanced professional audio analysis")
    print("   ✅ Comprehensive spectral features")
    print("   ✅ Advanced onset detection")
    print("   ✅ Beat detection and tempo tracking")
    print("   ✅ MFCC and mel-spectrogram analysis")
    print("   ✅ Minimal, proven stable GUI")
    print("   ✅ Text-based visualization (no complex OpenGL)")
    print("   ✅ Professional dark theme")
    print("   ✅ Maximum stability focus")
    print("=" * 50)

    # Create and configure Qt application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    app.setApplicationName("MMPA - Minimal Advanced")
    app.setApplicationVersion("2.2")

    # Apply professional theme
    apply_professional_theme(app)

    # Create and run minimal advanced application
    mmpa_app = MinimalAdvancedMMPAApplication()
    return mmpa_app.run()

if __name__ == "__main__":
    sys.exit(main())