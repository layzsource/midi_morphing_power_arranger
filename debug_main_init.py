import sys
import logging
from PySide6.QtWidgets import QApplication
from config import Config

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger(__name__)

def test_main_window_init():
    """Test MainWindow initialization step by step"""
    
    print("=== Testing MainWindow initialization ===")
    
    try:
        print("Step 1: Creating Config...")
        config = Config()
        print("✓ Config created")
        
        print("Step 2: Testing Settings...")
        from PySide6.QtCore import QSettings
        settings = QSettings("MorphingVisualizer", "Config")
        config.load_from_settings(settings)
        print("✓ Settings loaded")
        
        print("Step 3: Testing mesh creation...")
        from geometry import create_initial_meshes
        initial_meshes = create_initial_meshes(config.MESH_RESOLUTION)
        print(f"✓ Created {len(initial_meshes)} meshes")
        
        print("Step 4: Testing full MainWindow import...")
        from main_window import MainWindow
        print("✓ MainWindow imported")
        
        print("Step 5: Creating MainWindow instance...")
        app = QApplication(sys.argv)
        
        # Create window but don't show it yet
        window = MainWindow()
        print("✓ MainWindow created")
        
        print("Step 6: Checking window size...")
        print(f"Window size: {window.size()}")
        print(f"Window geometry: {window.geometry()}")
        
        print("Step 7: Showing window...")
        window.show()
        window.resize(1000, 700)  # Force a reasonable size
        window.raise_()
        
        print("✓ All steps completed successfully")
        print("If you see a tiny window, the issue is in the UI layout")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"✗ Failed at step: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_window_init()
