import sys
import logging
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from pyvistaqt import QtInteractor
import pyvista as pv

# Set up logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DebugMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Starting DebugMainWindow initialization")
        
        self.setWindowTitle("Debug MIDI to OSC Morphing Interface")
        self.setGeometry(100, 100, 1000, 700)
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add status label
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)
        
        try:
            logger.info("Creating PyVista widget")
            self.plotter_widget = QtInteractor(central_widget)
            layout.addWidget(self.plotter_widget)
            self.status_label.setText("PyVista widget created")
            
            logger.info("Creating test sphere")
            sphere = pv.Sphere()
            self.plotter_widget.add_mesh(sphere, color='lightblue')
            self.plotter_widget.reset_camera()
            self.status_label.setText("Test sphere added - App should be working")
            
            logger.info("Initialization complete")
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            self.status_label.setText(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    logger.info("Starting application")
    
    window = DebugMainWindow()
    window.show()
    
    logger.info("Window shown, starting event loop")
    sys.exit(app.exec())
