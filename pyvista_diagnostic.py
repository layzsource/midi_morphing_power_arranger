import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np

class PyVistaRenderingTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVista Rendering Test")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # PyVista widget
        self.plotter = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter)
        
        # Test buttons
        self.add_sphere_button = QPushButton("Add Red Sphere")
        self.add_sphere_button.clicked.connect(self.add_sphere)
        self.layout.addWidget(self.add_sphere_button)
        
        self.change_color_button = QPushButton("Change to Blue")
        self.change_color_button.clicked.connect(self.change_color)
        self.layout.addWidget(self.change_color_button)
        
        self.move_sphere_button = QPushButton("Move Sphere")
        self.move_sphere_button.clicked.connect(self.move_sphere)
        self.layout.addWidget(self.move_sphere_button)
        
        self.deform_sphere_button = QPushButton("Deform Sphere")
        self.deform_sphere_button.clicked.connect(self.deform_sphere)
        self.layout.addWidget(self.deform_sphere_button)
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all)
        self.layout.addWidget(self.clear_button)
        
        self.current_mesh = None
        self.current_actor = None
        
        print("PyVista Rendering Test initialized")
        print("Click buttons to test different rendering capabilities")
    
    def add_sphere(self):
        print("Adding red sphere...")
        self.current_mesh = pv.Sphere()
        self.current_actor = self.plotter.add_mesh(self.current_mesh, color='red')
        self.plotter.reset_camera()
        print("Red sphere added")
    
    def change_color(self):
        if self.current_actor:
            print("Changing color to blue...")
            self.plotter.remove_actor(self.current_actor)
            self.current_actor = self.plotter.add_mesh(self.current_mesh, color='blue')
            self.plotter.render()
            print("Color changed to blue")
        else:
            print("No sphere to change color - add sphere first")
    
    def move_sphere(self):
        if self.current_mesh:
            print("Moving sphere...")
            # Move sphere by 2 units on X axis
            moved_mesh = self.current_mesh.copy()
            moved_mesh.points[:, 0] += 2.0
            
            self.plotter.remove_actor(self.current_actor)
            self.current_actor = self.plotter.add_mesh(moved_mesh, color='green')
            self.current_mesh = moved_mesh
            self.plotter.render()
            print("Sphere moved")
        else:
            print("No sphere to move - add sphere first")
    
    def deform_sphere(self):
        if self.current_mesh:
            print("Deforming sphere...")
            # Deform sphere into an ellipsoid
            deformed_mesh = self.current_mesh.copy()
            points = deformed_mesh.points
            points[:, 0] *= 2.0  # Stretch in X
            points[:, 1] *= 0.5  # Compress in Y
            deformed_mesh.points = points
            
            self.plotter.remove_actor(self.current_actor)
            self.current_actor = self.plotter.add_mesh(deformed_mesh, color='yellow')
            self.current_mesh = deformed_mesh
            self.plotter.render()
            print("Sphere deformed into ellipsoid")
        else:
            print("No sphere to deform - add sphere first")
    
    def clear_all(self):
        print("Clearing all objects...")
        self.plotter.clear()
        self.current_mesh = None
        self.current_actor = None
        print("All objects cleared")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = PyVistaRenderingTest()
    window.resize(600, 500)
    window.show()
    
    print("\n=== PyVista Rendering Test ===")
    print("Test each button in sequence:")
    print("1. Add Red Sphere - should show a red sphere")
    print("2. Change to Blue - sphere should turn blue")
    print("3. Move Sphere - sphere should move right and turn green")
    print("4. Deform Sphere - sphere should stretch and turn yellow")
    print("5. Clear All - everything should disappear")
    print("\nIf any step doesn't work visually, PyVista rendering is broken.")
    
    sys.exit(app.exec())
