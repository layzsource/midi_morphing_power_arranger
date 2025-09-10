import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QStatusBar, QPushButton
)
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
import pyvista as pv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple MIDI to OSC Morphing Interface")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Simplified version - testing layout")
        
        # Add some basic controls first
        self.layout.addWidget(QLabel("Target Shape:"))
        
        self.target_shape_combo = QComboBox()
        self.target_shape_combo.addItems(["sphere", "cone", "cube", "torus", "icosahedron"])
        self.layout.addWidget(self.target_shape_combo)
        
        self.layout.addWidget(QLabel("Morph Blend:"))
        
        self.morph_slider = QSlider(Qt.Orientation.Horizontal)
        self.morph_slider.setMinimum(0)
        self.morph_slider.setMaximum(100)
        self.layout.addWidget(self.morph_slider)
        
        # Add a test button
        test_button = QPushButton("Test Button")
        self.layout.addWidget(test_button)
        
        # NOW add the 3D widget
        logger.info("Adding 3D visualization...")
        try:
            self.plotter_widget = QtInteractor(self.central_widget)
            self.layout.addWidget(self.plotter_widget)
            
            # Add a simple sphere
            sphere = pv.Sphere()
            self.plotter_widget.add_mesh(sphere, color='lightblue')
            self.plotter_widget.reset_camera()
            
            logger.info("3D widget added successfully")
            self.status_bar.showMessage("3D visualization loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to add 3D widget: {e}")
            self.layout.addWidget(QLabel(f"3D Error: {e}"))
            self.status_bar.showMessage(f"3D Error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = SimpleMainWindow()
    window.show()
    
    print(f"Window visible: {window.isVisible()}")
    print(f"Window size: {window.size()}")
    print(f"Central widget size: {window.central_widget.size()}")
    
    sys.exit(app.exec())
