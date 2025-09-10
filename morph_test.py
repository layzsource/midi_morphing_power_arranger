import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QPushButton
)
from PySide6.QtCore import Qt
from pyvistaqt import QtInteractor
import numpy as np

from config import Config
from geometry import create_initial_meshes
from scene_manager import SceneManager

logger = logging.getLogger(__name__)

class MorphTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Morphing Test - Debug Version")
        
        self.config = Config()
        
        # Initialize visualization
        self._initialize_visualization()
        self._setup_ui()
        
        print("=== MORPH TEST INITIALIZED ===")
        print(f"Initial meshes: {list(self.initial_meshes.keys())}")
        print(f"Scene objects: {list(self.scene_manager.objects.keys())}")
    
    def _initialize_visualization(self):
        # Create meshes
        self.initial_meshes = create_initial_meshes(50)
        logger.info(f"Created {len(self.initial_meshes)} meshes")
        
        # Initialize scene manager (plotter will be set later)
        self.scene_manager = SceneManager(self.initial_meshes, None)
        print("Scene manager initialized for morph test")
    
    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Instructions
        self.layout.addWidget(QLabel("Morphing Test Application"))
        self.layout.addWidget(QLabel("Move slider to test morphing functionality"))

        # Initialize plotter
        self.plotter_widget = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter_widget)

        # Target shape selection
        self.target_shape_combo = QComboBox()
        self.target_shape_combo.addItems(sorted(list(self.initial_meshes.keys())))
        self.layout.addWidget(QLabel("Target Shape:"))
        self.layout.addWidget(self.target_shape_combo)

        # Morph slider
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setMinimum(0)
        self.morph_slider.setMaximum(100)
        self.morph_slider.setValue(0)
        self.layout.addWidget(QLabel("Morph Amount:"))
        self.layout.addWidget(self.morph_slider)
        
        # Value display
        self.value_label = QLabel("Morph: 0%")
        self.layout.addWidget(self.value_label)
        
        # Test buttons
        self.test_25_button = QPushButton("Test 25%")
        self.test_25_button.clicked.connect(lambda: self.manual_morph_test(25))
        self.layout.addWidget(self.test_25_button)
        
        self.test_50_button = QPushButton("Test 50%")
        self.test_50_button.clicked.connect(lambda: self.manual_morph_test(50))
        self.layout.addWidget(self.test_50_button)
        
        self.test_100_button = QPushButton("Test 100%")
        self.test_100_button.clicked.connect(lambda: self.manual_morph_test(100))
        self.layout.addWidget(self.test_100_button)
        
        # Debug info button
        self.debug_button = QPushButton("Show Debug Info")
        self.debug_button.clicked.connect(self.show_debug_info)
        self.layout.addWidget(self.debug_button)
        
        # Finalize visualization setup
        self._finalize_visualization_setup()
        
        # Connect slider signal
        print("Connecting slider signal...")
        self.morph_slider.valueChanged.connect(self.on_morph_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_change)
        print("Slider connected!")
        
        # Test initial connection
        print("Testing initial connection...")
        self.on_morph_change(0)
    
    def _finalize_visualization_setup(self):
        # Set the plotter widget
        self.scene_manager.plotter_widget = self.plotter_widget
        
        # Create default scene with single object for testing
        from scene_manager import NoteRange, LayerBlendMode
        
        # Create one test object
        note_range = NoteRange(min_note=60, max_note=72, name="Test Object")
        self.scene_manager.add_object(
            id="test_object",
            note_range=note_range,
            shape_type="sphere",  # Start with sphere
            position=np.array([0.0, 0.0, 0.0]),
            scale=1.0,
            depth_layer=1,
            blend_mode=LayerBlendMode.NORMAL
        )
        
        self.plotter_widget.reset_camera()
        print("Single test object created")
    
    def on_morph_change(self, value):
        print(f"\n=== MORPH SLIDER MOVED TO {value}% ===")
        self.value_label.setText(f"Morph: {value}%")
        
        alpha = value / 100.0
        target_shape = self.target_shape_combo.currentText()
        
        print(f"Alpha: {alpha:.2f}, Target: {target_shape}")
        
        if not self.scene_manager:
            print("ERROR: No scene manager!")
            return
        
        if "test_object" not in self.scene_manager.objects:
            print("ERROR: No test object!")
            return
        
        visual_obj = self.scene_manager.objects["test_object"]
        current_shape = visual_obj.shape_type
        
        print(f"Morphing {current_shape} -> {target_shape}")
        
        if current_shape in self.initial_meshes and target_shape in self.initial_meshes:
            base_mesh = self.initial_meshes[current_shape]
            target_mesh = self.initial_meshes[target_shape]
            
            print(f"Base mesh vertices: {len(base_mesh.points)}")
            print(f"Target mesh vertices: {len(target_mesh.points)}")
            
            if len(base_mesh.points) == len(target_mesh.points):
                # Perform morphing
                blended_points = (1 - alpha) * base_mesh.points + alpha * target_mesh.points
                
                    # Update mesh
                if "test_object" in self.scene_manager.meshes:
                    current_mesh = self.scene_manager.meshes["test_object"]
                    
                    # Create a new mesh with the blended points instead of modifying existing
                    import pyvista as pv
                    new_mesh = pv.PolyData(blended_points, current_mesh.faces)
                    
                    # Replace the mesh in scene manager
                    self.scene_manager.meshes["test_object"] = new_mesh
                    
                    # Force visual update by completely recreating the actor
                    if "test_object" in self.scene_manager.actors:
                        old_actor = self.scene_manager.actors["test_object"]
                        self.plotter_widget.remove_actor(old_actor)
                        
                        new_actor = self.plotter_widget.add_mesh(
                            new_mesh,
                            color=[0.8, 0.2, 0.2],  # Red for visibility
                            smooth_shading=True
                        )
                        
                        self.scene_manager.actors["test_object"] = new_actor
                        
                        # Force complete render update
                        self.plotter_widget.render()
                        self.plotter_widget.update()
                        
                        print("Visual update completed!")
                    else:
                        print("ERROR: No actor found!")
                else:
                    print("ERROR: No mesh found!")
            else:
                print(f"ERROR: Vertex count mismatch! {len(base_mesh.points)} vs {len(target_mesh.points)}")
        else:
            print(f"ERROR: Missing shapes! {current_shape} or {target_shape}")
        
        print("=== END MORPH ===\n")
    
    def on_target_change(self, target_shape):
        print(f"Target shape changed to: {target_shape}")
        # Re-apply current morph with new target
        current_value = self.morph_slider.value()
        self.on_morph_change(current_value)
    
    def manual_morph_test(self, value):
        print(f"Manual test: Setting slider to {value}%")
        self.morph_slider.setValue(value)
    
    def show_debug_info(self):
        print("\n=== DEBUG INFO ===")
        print(f"Scene manager exists: {self.scene_manager is not None}")
        if self.scene_manager:
            print(f"Objects: {list(self.scene_manager.objects.keys())}")
            print(f"Meshes: {list(self.scene_manager.meshes.keys())}")
            print(f"Actors: {list(self.scene_manager.actors.keys())}")
            print(f"Plotter widget: {self.scene_manager.plotter_widget is not None}")
        
        print(f"Available shapes: {list(self.initial_meshes.keys())}")
        print(f"Current target: {self.target_shape_combo.currentText()}")
        print(f"Current slider value: {self.morph_slider.value()}")
        
        # Test mesh vertex counts
        for shape_name, mesh in self.initial_meshes.items():
            print(f"{shape_name}: {len(mesh.points)} vertices")
        
        print("=== END DEBUG ===\n")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    window = MorphTestWindow()
    window.resize(800, 600)
    window.show()
    
    sys.exit(app.exec())
