#!/usr/bin/env python3
"""
MMPA - Enhanced Complete Application
Restored advanced multi-window interface with all the original visual features.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the complete application but with enhanced GUI
from run_complete_mmpa import CompleteMMPAApplication, setup_logging
from fig.gui.enhanced_main_window import EnhancedMMPAMainWindow

class EnhancedMMPAApplication(CompleteMMPAApplication):
    """Enhanced MMPA with restored advanced GUI features."""

    def _initialize_systems(self):
        """Initialize systems with enhanced GUI."""
        # Initialize everything except GUI first
        self.logger.info("🚀 Initializing Complete MMPA Application")

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

        # Initialize audio system
        if self.systems_available['audio']:
            try:
                from fig.audio.audio_handler import AudioHandler
                self.audio_handler = AudioHandler(self.config.audio)
                self.logger.info("✅ Audio system initialized")
            except Exception as e:
                self.logger.error(f"❌ Audio system failed: {e}")
                self.systems_available['audio'] = False

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

        # Initialize ENHANCED GUI
        try:
            self.main_window = EnhancedMMPAMainWindow(self, self.config.ui)
            self.logger.info("✅ Enhanced main window initialized")
        except Exception as e:
            self.logger.error(f"❌ Enhanced main window failed: {e}")
            # Create minimal fallback window
            self.main_window = self._create_minimal_window()

        # Connect all systems
        self._connect_systems()

def main():
    """Main entry point for enhanced MMPA."""
    setup_logging()

    print("🎼 MMPA Enhanced - The Language of Signals Becoming Form")
    print("🎨 Loading advanced multi-window interface...")
    print("=" * 60)

    # Create and run enhanced application
    app = EnhancedMMPAApplication()
    return app.run()

if __name__ == "__main__":
    sys.exit(main())