import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
import pyvista as pv
from pyvistaqt import QtInteractor

class PyVistaTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVista Test")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add a label
        layout.addWidget(QLabel("PyVista 3D View should appear below:"))
        
        try:
            # Create PyVista widget
            self.plotter = QtInteractor(central_widget)
            layout.addWidget(self.plotter)
            
            # Add a simple sphere
            sphere = pv.Sphere()
            self.plotter.add_mesh(sphere, color='red')
            self.plotter.reset_camera()
            
            print("PyVista widget created successfully")
            
        except Exception as e:
            layout.addWidget(QLabel(f"PyVista Error: {e}"))
            print(f"PyVista failed: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyVistaTest()
    window.show()
    sys.exit(app.exec())
