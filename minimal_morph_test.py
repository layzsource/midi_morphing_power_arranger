import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
import pyvista as pv
import numpy as np

class MinimalMorphTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal PyVista Morph Test")
        
        # Create basic shapes
        self.sphere = pv.Sphere(radius=1.0, phi_resolution=30, theta_resolution=30)
        self.cube = pv.Cube()
        
        print(f"Sphere vertices: {self.sphere.n_points}")
        print(f"Cube vertices: {self.cube.n_points}")
        
        # Resample cube to match sphere vertex count
        self.cube = self.cube.subdivide(2).smooth(1000)
        print(f"Resampled cube vertices: {self.cube.n_points}")
        
        # Make them have same vertex count by resampling
        if self.sphere.n_points != self.cube.n_points:
            print("Resampling to match vertex counts...")
            target_points = min(self.sphere.n_points, self.cube.n_points)
            
            # Decimate to same point count
            if self.sphere.n_points > target_points:
                self.sphere = self.sphere.decimate(1.0 - target_points/self.sphere.n_points)
            if self.cube.n_points > target_points:
                self.cube = self.cube.decimate(1.0 - target_points/self.cube.n_points)
        
        print(f"Final sphere vertices: {self.sphere.n_points}")
        print(f"Final cube vertices: {self.cube.n_points}")
        
        self.current_actor = None
        self._setup_ui()
    
    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.layout.addWidget(QLabel("Minimal Morph Test - Sphere to Cube"))
        
        # PyVista widget
        self.plotter = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setValue(0)
        self.slider.valueChanged.connect(self.morph)
        self.layout.addWidget(self.slider)
        
        self.value_label = QLabel("Morph: 0%")
        self.layout.addWidget(self.value_label)
        
        # Initial sphere
        self.current_actor = self.plotter.add_mesh(self.sphere, color='red', show_edges=True)
        self.plotter.reset_camera()
        
        print("UI setup complete")
    
    def morph(self, value):
        alpha = value / 100.0
        self.value_label.setText(f"Morph: {value}% (alpha={alpha:.2f})")
        
        print(f"\n=== MORPH {value}% ===")
        
        try:
            # Remove current actor
            if self.current_actor:
                self.plotter.remove_actor(self.current_actor)
            
            # Create morphed mesh
            if self.sphere.n_points == self.cube.n_points:
                morphed_points = (1 - alpha) * self.sphere.points + alpha * self.cube.points
                morphed_mesh = pv.PolyData(morphed_points, self.sphere.faces)
                
                # Add new actor
                self.current_actor = self.plotter.add_mesh(
                    morphed_mesh, 
                    color=[1-alpha, alpha, 0],  # Color change from red to green
                    show_edges=True
                )
                
                # Force render
                self.plotter.render()
                
                print(f"Morphed successfully: {len(morphed_points)} points")
            else:
                print(f"Cannot morph: vertex mismatch {self.sphere.n_points} vs {self.cube.n_points}")
                
        except Exception as e:
            print(f"Morph error: {e}")
        
        print("=== END MORPH ===\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MinimalMorphTest()
    window.resize(600, 500)
    window.show()
    
    sys.exit(app.exec())
