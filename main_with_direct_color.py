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
        self.setWindowTitle("MIDI Color-Changing Morphing Interface")
        
        # Load settings
        self.settings = QSettings("MorphingVisualizer", "Config")
        self.config.load_from_settings(self.settings)
        
        # Initialize state
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "icosahedron"
        self.active_notes = {}  # Track active notes and their colors
        self.default_color = 'lightblue'
        
        # MIDI setup
        self.midi_handler = MidiHandler()
        
        self._setup_ui()
        self._initialize_visualization()
        self._setup_midi()
        
        # Timer for note cleanup
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_notes)
        self.cleanup_timer.start(2000)  # Clean up every 2 seconds
    
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
        
        # Active notes display
        self.notes_label = QLabel("Active Notes: None")
        self.layout.addWidget(self.notes_label)
        
        # Clear notes button
        self.clear_notes_button = QPushButton("Clear All Notes")
        self.clear_notes_button.clicked.connect(self._clear_all_notes)
        self.layout.addWidget(self.clear_notes_button)

    def _initialize_visualization(self):
        """Initialize the 3D visualization."""
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
        
        # Add the mesh to plotter
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh, 
            color=self.default_color, 
            smooth_shading=True
        )
        
        self.plotter_widget.reset_camera()
        
        # Connect signals
        self.morph_slider.valueChanged.connect(self.on_morph_slider_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_shape_change)
        
        self.status_bar.showMessage("Ready - Play MIDI notes to change object color")
    
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
            self.status_bar.showMessage("MIDI connected - notes will change object color directly")
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
        """Handle MIDI note on - add note to active notes and update color."""
        try:
            # Map note to hue
            hue = note / 127.0
            rgb_color = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            
            # Add to active notes
            self.active_notes[note] = {
                'color': rgb_color,
                'velocity': velocity,
                'timestamp': time.time()
            }
            
            # Update object color immediately
            self._update_object_color()
            
            self._update_notes_display()
            print(f"Note ON: {note} (velocity: {velocity:.2f}) - Object color updated")
                
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note):
        """Handle MIDI note off - remove note and update color."""
        try:
            if note in self.active_notes:
                del self.active_notes[note]
                
                # Update object color
                self._update_object_color()
                
                self._update_notes_display()
                print(f"Note OFF: {note} - Object color updated")
                
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
    
    def _update_object_color(self):
        """Update the main object's color based on active notes."""
        try:
            if not self.active_notes:
                # No active notes - use default color
                new_color = self.default_color
            elif len(self.active_notes) == 1:
                # Single note - use its color directly
                note_info = next(iter(self.active_notes.values()))
                new_color = note_info['color']
            else:
                # Multiple notes - blend colors weighted by velocity
                total_color = np.array([0.0, 0.0, 0.0])
                total_weight = 0.0
                
                for note_info in self.active_notes.values():
                    weight = note_info['velocity']
                    color = np.array(note_info['color'])
                    total_color += color * weight
                    total_weight += weight
                
                if total_weight > 0:
                    new_color = total_color / total_weight
                else:
                    new_color = self.default_color
            
            # Remove old actor and add new one with updated color
            self.plotter_widget.remove_actor(self.actor)
            self.actor = self.plotter_widget.add_mesh(
                self.current_mesh,
                color=new_color,
                smooth_shading=True
            )
            
            self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error updating object color: {e}")
    
    def _cleanup_expired_notes(self):
        """Remove notes that have been held too long."""
        current_time = time.time()
        expired_notes = []
        
        for note, note_info in self.active_notes.items():
            if current_time - note_info['timestamp'] > 60:  # 60 second timeout
                expired_notes.append(note)
        
        for note in expired_notes:
            del self.active_notes[note]
        
        if expired_notes:
            self._update_object_color()
            self._update_notes_display()
    
    def _clear_all_notes(self):
        """Clear all active notes."""
        self.active_notes.clear()
        self._update_object_color()
        self._update_notes_display()
    
    def _update_notes_display(self):
        """Update the active notes display."""
        if self.active_notes:
            note_names = [f"Note {note}" for note in sorted(self.active_notes.keys())]
            self.notes_label.setText(f"Active Notes: {', '.join(note_names)}")
        else:
            self.notes_label.setText("Active Notes: None")
    
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
        
        # Maintain current color during morphing
        current_color = self.default_color
        if self.active_notes:
            if len(self.active_notes) == 1:
                note_info = next(iter(self.active_notes.values()))
                current_color = note_info['color']
            else:
                # Recalculate blended color
                total_color = np.array([0.0, 0.0, 0.0])
                total_weight = 0.0
                
                for note_info in self.active_notes.values():
                    weight = note_info['velocity']
                    color = np.array(note_info['color'])
                    total_color += color * weight
                    total_weight += weight
                
                if total_weight > 0:
                    current_color = total_color / total_weight
        
        # Update actor with new geometry and maintain color
        self.plotter_widget.remove_actor(self.actor)
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
