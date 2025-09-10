import sys
import logging
import time
import threading
import colorsys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QStatusBar, QPushButton
)
from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject
from pyvistaqt import QtInteractor
import pyvista as pv

from config import Config
from geometry import create_initial_meshes, blend_meshes

# MIDI imports
try:
    import pygame
    import pygame.midi
    MIDI_AVAILABLE = True
    print("Using pygame for MIDI support")
except ImportError:
    MIDI_AVAILABLE = False
    print("pygame not available - MIDI disabled")

logger = logging.getLogger(__name__)

class MidiHandler(QObject):
    """Handles MIDI input using pygame."""
    
    # Signals to communicate with main thread
    note_on_signal = Signal(int, float)  # note, velocity
    note_off_signal = Signal(int)        # note
    cc_signal = Signal(int, float)       # cc_number, value
    
    def __init__(self):
        super().__init__()
        self.midi_input = None
        self.running = False
        self.thread = None
        
    def start(self, device_name=None):
        """Start MIDI input."""
        if not MIDI_AVAILABLE:
            return False
            
        try:
            pygame.midi.init()
            
            # Find MIDI input device
            device_id = self._find_device(device_name)
            if device_id is None:
                print("No MIDI input devices found")
                return False
            
            self.midi_input = pygame.midi.Input(device_id)
            device_info = pygame.midi.get_device_info(device_id)
            device_name = device_info[1].decode() if isinstance(device_info[1], bytes) else str(device_info[1])
            print(f"Connected to MIDI device: {device_name}")
            
            # Start polling thread
            self.running = True
            self.thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start MIDI: {e}")
            return False
    
    def _find_device(self, preferred_name=None):
        """Find a suitable MIDI input device."""
        device_count = pygame.midi.get_count()
        
        for i in range(device_count):
            info = pygame.midi.get_device_info(i)
            name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
            is_input = info[2]  # 1 for input
            
            if is_input:
                if preferred_name and preferred_name.lower() in name.lower():
                    return i
                elif not preferred_name:
                    return i  # Return first available input
        
        return None
    
    def _midi_loop(self):
        """Main MIDI polling loop."""
        while self.running and self.midi_input:
            try:
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    
                    for event in midi_events:
                        self._process_midi_event(event[0])
                
                time.sleep(0.001)  # Small delay
                
            except Exception as e:
                print(f"MIDI polling error: {e}")
                break
    
    def _process_midi_event(self, midi_data):
        """Process a single MIDI event."""
        if len(midi_data) < 3:
            return
            
        status, data1, data2 = midi_data[:3]
        
        # Note On (144-159)
        if 144 <= status <= 159:
            if data2 > 0:  # Velocity > 0 = note on
                velocity = data2 / 127.0
                self.note_on_signal.emit(data1, velocity)
            else:  # Velocity = 0 = note off
                self.note_off_signal.emit(data1)
        
        # Note Off (128-143)
        elif 128 <= status <= 143:
            self.note_off_signal.emit(data1)
        
        # Control Change (176-191)
        elif 176 <= status <= 191:
            cc_value = data2 / 127.0
            self.cc_signal.emit(data1, cc_value)
    
    def stop(self):
        """Stop MIDI input."""
        self.running = False
        if self.midi_input:
            self.midi_input.close()
            pygame.midi.quit()
        print("MIDI stopped")
    
    @staticmethod
    def list_devices():
        """List available MIDI devices."""
        if not MIDI_AVAILABLE:
            return []
            
        devices = []
        try:
            pygame.midi.init()
            device_count = pygame.midi.get_count()
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                if info[2]:  # is_input
                    name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                    devices.append(name)
            
            pygame.midi.quit()
        except Exception as e:
            print(f"Error listing MIDI devices: {e}")
        
        return devices

class MidiMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI to OSC Morphing Interface with Dynamic Lighting")
        
        # Load settings
        self.settings = QSettings("MorphingVisualizer", "Config")
        self.config.load_from_settings(self.settings)
        
        # Initialize state
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "icosahedron"
        self.note_light_actors = {}  # Store light visualization actors
        
        # MIDI setup
        self.midi_handler = MidiHandler()
        
        self._setup_ui()
        self._initialize_visualization()
        self._setup_midi()
        
        # Timer for light cleanup
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_lights)
        self.cleanup_timer.start(5000)  # Clean up every 5 seconds
    
    def _setup_ui(self):
        """Setup the user interface."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Loading...")

        # Initialize plotter
        self.plotter_widget = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter_widget)
        
        # Create meshes
        self.initial_meshes = create_initial_meshes(self.config.MESH_RESOLUTION)
        logger.info(f"Created {len(self.initial_meshes)} meshes")

        # UI Controls
        self.target_shape_combo = QComboBox()
        self.target_shape_combo.addItems(sorted(list(self.initial_meshes.keys())))
        self.layout.addWidget(QLabel("Target Shape:"))
        self.layout.addWidget(self.target_shape_combo)

        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setMinimum(0)
        self.morph_slider.setMaximum(100)
        self.layout.addWidget(QLabel("Morph Blend (or use MIDI CC#1):"))
        self.layout.addWidget(self.morph_slider)
        
        # MIDI controls
        self.midi_button = QPushButton("Reconnect MIDI")
        self.midi_button.clicked.connect(self._reconnect_midi)
        self.layout.addWidget(self.midi_button)
        
        # Light count display
        self.light_count_label = QLabel("Active Note Lights: 0")
        self.layout.addWidget(self.light_count_label)
        
        # Clear lights button
        self.clear_lights_button = QPushButton("Clear All Lights")
        self.clear_lights_button.clicked.connect(self._clear_all_lights)
        self.layout.addWidget(self.clear_lights_button)

    def _initialize_visualization(self):
        """Initialize the 3D visualization."""
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
        
        # Get bounds for light positioning
        bounds = self.current_mesh.bounds
        self.z_min, self.z_max = bounds[4:6]
        
        # Add the mesh to plotter with lighting-friendly properties
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh, 
            color='white',  # Start with white so colored lights show up better
            smooth_shading=True,
            show_edges=False
        )
        
        # Set up basic lighting
        self.plotter_widget.enable_lightkit()
        
        self.plotter_widget.reset_camera()
        
        # Connect signals
        self.morph_slider.valueChanged.connect(self.on_morph_slider_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_shape_change)
        
        self.status_bar.showMessage("Visualization ready - MIDI will create colored lights")
    
    def _setup_midi(self):
        """Setup MIDI connections."""
        if not MIDI_AVAILABLE:
            self.status_bar.showMessage("MIDI not available")
            return
        
        # Connect MIDI signals
        self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
        self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
        self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        # Try to start MIDI
        if self.midi_handler.start(self.config.MIDI_PORT):
            self.status_bar.showMessage("MIDI connected - play notes to create colored lights")
        else:
            self.status_bar.showMessage("MIDI connection failed - check devices")
    
    def _reconnect_midi(self):
        """Attempt to reconnect MIDI."""
        self.midi_handler.stop()
        if self.midi_handler.start(self.config.MIDI_PORT):
            self.status_bar.showMessage("MIDI reconnected")
        else:
            self.status_bar.showMessage("MIDI reconnection failed")
    
    def _on_midi_note_on(self, note, velocity):
        """Handle MIDI note on - create a light visualization."""
        try:
            # Remove existing light for this note
            if note in self.note_light_actors:
                self._remove_light_visualization(note)
            
            # Create visual light representation and change main object color
            self._create_light_visualization(note, velocity)
            self._update_main_object_lighting(note, velocity)
            
            self._update_light_count()
            self.plotter_widget.render()
            
            print(f"Note ON: {note} (velocity: {velocity:.2f}) - Light effect created")
                
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note):
        """Handle MIDI note off - remove light visualization."""
        try:
            if note in self.note_light_actors:
                self._remove_light_visualization(note)
                self._update_light_count()
                self.plotter_widget.render()
                print(f"Note OFF: {note} - Light effect removed")
                
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value):
        """Handle MIDI control change."""
        try:
            if cc_number == 1:  # Mod wheel controls morphing
                slider_value = int(value * 100)
                self.morph_slider.setValue(slider_value)
                print(f"CC1 (Mod Wheel): {value:.2f}")
            
        except Exception as e:
            print(f"Error handling CC: {e}")
    
    def _create_light_visualization(self, note_number, velocity):
        """Create a visual representation of the light effect."""
        try:
            # Map note to hue
            hue = note_number / 127.0
            rgb_color = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
            
            # Position around the main object
            angle = (note_number / 127.0) * 2 * np.pi
            distance = 3.0
            height = np.interp(note_number, [0, 127], [-1.5, 1.5])
            
            x = distance * np.cos(angle)
            y = distance * np.sin(angle)
            z = height
            
            # Create a small glowing sphere to represent the light source
            light_sphere = pv.Sphere(radius=0.1 + velocity * 0.2, center=(x, y, z))
            
            # Add glowing effect with emissive-like properties
            light_actor = self.plotter_widget.add_mesh(
                light_sphere,
                color=rgb_color,
                opacity=0.8 + velocity * 0.2,
                smooth_shading=True
            )
            
            # Store the light info
            self.note_light_actors[note_number] = {
                'actor': light_actor,
                'sphere': light_sphere,
                'timestamp': time.time(),
                'velocity': velocity,
                'color': rgb_color,
                'position': (x, y, z)
            }
            
        except Exception as e:
            print(f"Failed to create light visualization: {e}")
    
    def _update_main_object_lighting(self, note_number, velocity):
        """Update the main object's color based on active notes."""
        try:
            if not self.note_light_actors:
                # No lights - return to default color
                self.plotter_widget.remove_actor(self.actor)
                self.actor = self.plotter_widget.add_mesh(
                    self.current_mesh,
                    color='lightblue',
                    smooth_shading=True
                )
                return
            
            # Blend colors from all active lights
            total_color = np.array([0.0, 0.0, 0.0])
            total_weight = 0.0
            
            for note_info in self.note_light_actors.values():
                weight = note_info['velocity']
                color = np.array(note_info['color'])
                total_color += color * weight
                total_weight += weight
            
            if total_weight > 0:
                blended_color = total_color / total_weight
                
                # Update the main object color
                self.plotter_widget.remove_actor(self.actor)
                self.actor = self.plotter_widget.add_mesh(
                    self.current_mesh,
                    color=blended_color,
                    smooth_shading=True
                )
            
        except Exception as e:
            print(f"Error updating main object lighting: {e}")
    
    def _remove_light_visualization(self, note_number):
        """Remove a light visualization."""
        if note_number in self.note_light_actors:
            light_info = self.note_light_actors.pop(note_number)
            try:
                self.plotter_widget.remove_actor(light_info['actor'])
                
                # Update main object color with remaining lights
                if self.note_light_actors:
                    # Find any remaining note to trigger color update
                    remaining_note = next(iter(self.note_light_actors.keys()))
                    remaining_info = self.note_light_actors[remaining_note]
                    self._update_main_object_lighting(remaining_note, remaining_info['velocity'])
                else:
                    # No lights left - return to default
                    self._update_main_object_lighting(0, 0)
                    
            except Exception as e:
                print(f"Error removing light visualization: {e}")
    
    def _cleanup_expired_lights(self):
        """Remove lights that have been on too long."""
        current_time = time.time()
        expired_notes = []
        
        for note, light_info in self.note_light_actors.items():
            if current_time - light_info['timestamp'] > 30:  # 30 second timeout
                expired_notes.append(note)
        
        for note in expired_notes:
            self._remove_light_visualization(note)
        
        if expired_notes:
            self._update_light_count()
            self.plotter_widget.render()
    
    def _clear_all_lights(self):
        """Remove all light visualizations."""
        for note in list(self.note_light_actors.keys()):
            self._remove_light_visualization(note)
        self._update_light_count()
        self.plotter_widget.render()
    
    def _update_light_count(self):
        """Update the light count display."""
        count = len(self.note_light_actors)
        self.light_count_label.setText(f"Active Note Lights: {count}")
    
    def on_morph_slider_change(self, value):
        """Handle morph slider changes."""
        alpha = value / 100.0
        
        blended_points = blend_meshes(
            self.initial_meshes, 
            self.current_mesh_key, 
            self.target_mesh_key, 
            alpha
        )
        self.current_mesh.points = blended_points
        
        # Update the actor with new geometry
        self.plotter_widget.remove_actor(self.actor)
        
        # Determine current color based on active lights
        if self.note_light_actors:
            # Calculate blended color from active lights
            total_color = np.array([0.0, 0.0, 0.0])
            total_weight = 0.0
            
            for note_info in self.note_light_actors.values():
                weight = note_info['velocity']
                color = np.array(note_info['color'])
                total_color += color * weight
                total_weight += weight
            
            if total_weight > 0:
                current_color = total_color / total_weight
            else:
                current_color = 'lightblue'
        else:
            current_color = 'lightblue'
        
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh,
            color=current_color,
            smooth_shading=True
        )
        
        self.plotter_widget.render()
    
    def on_target_shape_change(self, target_key):
        """Handle target shape changes."""
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            self.on_morph_slider_change(self.morph_slider.value())
    
    def closeEvent(self, event):
        """Clean shutdown."""
        self.midi_handler.stop()
        self.cleanup_timer.stop()
        event.accept()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # List available MIDI devices
    devices = MidiHandler.list_devices()
    if devices:
        print("Available MIDI devices:")
        for device in devices:
            print(f"  - {device}")
    else:
        print("No MIDI devices found")
    
    app = QApplication(sys.argv)
    
    window = MidiMainWindow()
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())
