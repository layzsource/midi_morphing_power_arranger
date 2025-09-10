import sys
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Import our modules
from config import Config
from main_window import MainWindow

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugMainWindow(MainWindow):
    def __init__(self):
        logger.info("=== Starting MainWindow initialization ===")
        
        # Call parent QMainWindow.__init__ but skip MainWindow.__init__
        from PySide6.QtWidgets import QMainWindow
        QMainWindow.__init__(self)
        
        # Initialize step by step
        logger.info("Step 1: Basic setup")
        self.config = Config()
        self.setWindowTitle("MIDI to OSC Morphing Interface")
        
        # Load settings
        logger.info("Step 2: Loading settings")
        self.settings = QSettings("MorphingVisualizer", "Config")
        self.config.load_from_settings(self.settings)
        
        # Initialize state variables
        logger.info("Step 3: Initializing state")
        self.initial_meshes = {}
        self.current_mesh = None
        self.actor = None
        self.note_lights = {}
        self.integrated_thread = None
        self.audio_thread = None
        self.current_audio_features = {}
        self.audio_morph_influence = 0.0
        self._last_alpha = -1
        self._render_timer = None
        self.performance_dialog = None
        
        # Setup UI (this might be where it fails)
        logger.info("Step 4: Setting up UI")
        try:
            self._setup_ui()
            logger.info("✓ UI setup completed")
        except Exception as e:
            logger.error(f"✗ UI setup failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Skip the complex initialization for now
        logger.info("Skipping complex initialization (timers, threads, etc.)")
        logger.info("=== Initialization complete ===")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        window = DebugMainWindow()
        window.resize(1000, 700)
        window.show()
        
        print(f"Final window size: {window.size()}")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Failed to create window: {e}")
        import traceback
        traceback.print_exc()
