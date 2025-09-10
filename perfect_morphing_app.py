#!/usr/bin/env python3
"""
Final MIDI Morphing Visualizer - Perfect Smooth Morphing
This version ensures all meshes have identical vertex counts for perfect morphing.
FIXED: Safe color handling to prevent invalid color crashes.
"""

import sys
import logging
import time
import threading
import colorsys
import numpy as np
import queue

# FIXED: Import safe color utilities
from color_utils import safe_hsv_to_rgb, safe_color_array, blend_colors_safe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check core dependencies
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QObject
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✓ Core GUI dependencies available")
except ImportError as e:
    print(f"✗ Missing core dependencies: {e}")
    sys.exit(1)

# Config
class SimpleConfig:
    def __init__(self):
        self.MESH_RESOLUTION = 25  # Even lower for better compatibility
        self.AUDIO_SAMPLE_RATE = 44100
        self.AUDIO_CHUNK_SIZE = 512
        self.AUDIO_ONSET_THRESHOLD = 1.5
        self.DEFAULT_COLOR = [0.8, 0.8, 0.8]

# Optional dependencies
MIDI_AVAILABLE = False
try:
    import pygame.midi
    MIDI_AVAILABLE = True
    print("✓ Pygame MIDI support available")
except ImportError:
    print("⚠ MIDI support not available")

AUDIO_AVAILABLE = False
try:
    import pyaudio
    AUDIO_AVAILABLE = True
    print("✓ PyAudio available")
except ImportError:
    print("⚠ Audio analysis not available")

def create_perfectly_matched_meshes(resolution=25):
    """Create meshes with IDENTICAL vertex counts for perfect morphing."""
    sphere = pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution)
    
    base_points = sphere.points
    base_count = sphere.n_points
    
    meshes = {}
    
    # Sphere (baseline)
    meshes["sphere"] = sphere.copy()
    
    # Cube (quantize to cube faces)
    cube_points = base_points.copy()
    for i in range(len(cube_points)):
        # Find the dominant axis and snap to cube face
        abs_coords = np.abs(cube_points[i])
        max_axis = np.argmax(abs_coords)
        
        # Preserve ratios while snapping to cube
        for j in range(3):
            if j == max_axis:
                cube_points[i][j] = np.sign(cube_points[i][j]) * 0.8
            else:
                cube_points[i][j] *= 0.6
    
    cube = sphere.copy()
    cube.points = cube_points
    meshes["cube"] = cube
    
    # Cone (project toward apex)
    cone_points = base_points.copy()
    for i in range(len(cone_points)):
        x, y, z = cone_points[i]
        # Normalize z to [0,1] and use as scaling factor
        height_factor = (z + 1) / 2
        scale = height_factor * 0.8 + 0.1
        cone_points[i] = [x * scale, y * scale, z * 0.9]
    
    cone = sphere.copy()
    cone.points = cone_points
    meshes["cone"] = cone
    
    # Torus (project to torus surface)
    torus_points = base_points.copy()
    major_radius = 0.8
    minor_radius = 0.25
    
    for i in range(len(torus_points)):
        x, y, z = torus_points[i]
        
        # Convert to cylindrical coordinates
        r = np.sqrt(x**2 + y**2)
        if r > 1e-6:
            theta = np.arctan2(y, x)
            
            # Project to torus surface
            torus_r = major_radius + minor_radius * np.cos(z * np.pi)
            torus_z = minor_radius * np.sin(z * np.pi)
            
            torus_points[i] = [
                torus_r * np.cos(theta),
                torus_r * np.sin(theta), 
                torus_z
            ]
        else:
            # Handle points at origin
            torus_points[i] = [major_radius, 0, 0]
    
    torus = sphere.copy()
    torus.points = torus_points
    meshes["torus"] = torus
    
    # Icosahedron (quantize to icosahedral symmetry)
    ico_points = base_points.copy()
    for i in range(len(ico_points)):
        # Normalize to unit sphere
        point = ico_points[i]
        norm = np.linalg.norm(point)
        if norm > 1e-6:
            normalized = point / norm
            
            # Quantize to icosahedral directions (simplified)
            quantized = np.round(normalized * 2.5) / 2.5
            quantized_norm = np.linalg.norm(quantized)
            if quantized_norm > 1e-6:
                ico_points[i] = quantized / quantized_norm * 0.9
            else:
                ico_points[i] = [1, 0, 0]
        else:
            ico_points[i] = [1, 0, 0]
    
    icosahedron = sphere.copy()
    icosahedron.points = ico_points
    meshes["icosahedron"] = icosahedron
    
    # Verify all meshes have identical vertex counts
    for name, mesh in meshes.items():
        if mesh.n_points != base_count:
            raise ValueError(f"Mesh {name} has {mesh.n_points} vertices, expected {base_count}")
        print(f"✓ {name}: {mesh.n_points} vertices")
    
    print(f"✓ Created {len(meshes)} perfectly matched meshes")
    return meshes

def perfect_mesh_blend(meshes, source_key, target_key, alpha):
    """Perfect mesh blending with validation."""
    if source_key not in meshes or target_key not in meshes:
        return None
    
    source_mesh = meshes[source_key]
    target_mesh = meshes[target_key]
    
    # Verify identical vertex counts
    if source_mesh.n_points != target_mesh.n_points:
        print(f"ERROR: Vertex count mismatch: {source_mesh.n_points} vs {target_mesh.n_points}")
        print("This should not happen with perfectly matched meshes!")
        return source_mesh.points
    
    # Perfect linear interpolation
    source_points = source_mesh.points
    target_points = target_mesh.points
    
    return (1 - alpha) * source_points + alpha * target_points

# Simple MIDI Handler
class SimpleMidiHandler(QObject):
    note_on_signal = Signal(int, float)
    note_off_signal = Signal(int)
    cc_signal = Signal(int, float)
    
    def __init__(self):
        super().__init__()
        self.midi_input = None
        self.running = False
        self.thread = None
        
    def start(self):
        if not MIDI_AVAILABLE:
            return False
            
        try:
            pygame.midi.init()
            
            # Find first input device
            for i in range(pygame.midi.get_count()):
                info = pygame.midi.get_device_info(i)
                if info[2]:  # is input
                    self.midi_input = pygame.midi.Input(i)
                    device_name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                    print(f"✓ Connected to MIDI: {device_name}")
                    
                    self.running = True
                    self.thread = threading.Thread(target=self._midi_loop, daemon=True)
                    self.thread.start()
                    return True
            
            return False
            
        except Exception as e:
            print(f"MIDI start failed: {e}")
            return False
    
    def _midi_loop(self):
        while self.running and self.midi_input:
            try:
                if self.midi_input.poll():
                    events = self.midi_input.read(10)
                    for event in events:
                        self._process_event(event[0])
                time.sleep(0.001)
            except Exception as e:
                print(f"MIDI error: {e}")
                break
    
    def _process_event(self, event_data):
        status, note, velocity, _ = event_data
        
        if status == 144 and velocity > 0:  # Note On
            self.note_on_signal.emit(note, velocity / 127.0)
        elif status == 128 or (status == 144 and velocity == 0):  # Note Off
            self.note_off_signal.emit(note)
        elif status == 176:  # Control Change
            self.cc_signal.emit(note, velocity / 127.0)
    
    def stop(self):
        self.running = False
        if self.midi_input:
            self.midi_input.close()

# Simple Audio Analyzer
class SimpleAudioAnalyzer(QObject):
    onset_detected_signal = Signal(float)
    amplitude_signal = Signal(float)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.audio = None
        self.stream = None
        self.running = False
        self.thread = None
        self.audio_queue = queue.Queue()
        
    def start(self):
        if not AUDIO_AVAILABLE:
            return False
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.config.AUDIO_SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.config.AUDIO_CHUNK_SIZE,
                stream_callback=self._audio_callback
            )
            
            self.running = True
            self.stream.start_stream()
            
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            print("✓ Audio analysis started")
            return True
            
        except Exception as e:
            print(f"Audio start failed: {e}")
            return False
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        try:
            self.audio_queue.put_nowait(audio_data)
        except queue.Full:
            pass
        return (None, pyaudio.paContinue)
    
    def _analysis_loop(self):
        self.previous_energy = 0.0
        
        while self.running:
            try:
                chunk = self.audio_queue.get(timeout=0.1)
                
                rms = np.sqrt(np.mean(chunk ** 2))
                self.amplitude_signal.emit(rms)
                
                energy = np.sum(chunk ** 2)
                if self.previous_energy > 0:
                    ratio = energy / max(self.previous_energy, 1e-10)
                    if ratio > self.config.AUDIO_ONSET_THRESHOLD:
                        self.onset_detected_signal.emit(rms)
                
                self.previous_energy = energy * 0.1 + self.previous_energy * 0.9
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio analysis error: {e}")
                break
    
    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

# Main Window
class PerfectMorphingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = SimpleConfig()
        self.setWindowTitle("MIDI Morphing Visualizer - Perfect Morphing (FIXED)")
        
        # State
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "cube"
        self.active_notes = {}
        self.default_color = safe_color_array(self.config.DEFAULT_COLOR)
        self.audio_color_influence = 0.0
        
        # Components
        self.midi_handler = SimpleMidiHandler() if MIDI_AVAILABLE else None
        self.audio_analyzer = SimpleAudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        
        # Initialize
        self._initialize_visualization()
        self._setup_ui()
        self._setup_connections()
        
        # Timers
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_notes)
        self.cleanup_timer.start(5000)
        
        print("✅ Perfect morphing application ready with SAFE COLOR HANDLING!")
    
    def _initialize_visualization(self):
        """Initialize 3D visualization with perfectly matched meshes."""
        self.initial_meshes = create_perfectly_matched_meshes(self.config.MESH_RESOLUTION)
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
    
    def _setup_ui(self):
        """Setup user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 3D Visualization
        self.plotter_widget = QtInteractor(self)
        self.plotter_widget.set_background("black")
        layout.addWidget(self.plotter_widget)
        
        # Create initial actor with safe color
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh,
            color=self.default_color,
            smooth_shading=True
        )
        
        self.plotter_widget.camera_position = 'xy'
        self.plotter_widget.camera.zoom(1.5)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        # Target shape selector
        shape_layout = QVBoxLayout()
        shape_layout.addWidget(QLabel("Target Shape:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(["sphere", "cube", "cone", "icosahedron", "torus"])
        self.target_combo.setCurrentText("cube")
        shape_layout.addWidget(self.target_combo)
        controls_layout.addLayout(shape_layout)
        
        # Morph slider
        morph_layout = QVBoxLayout()
        morph_layout.addWidget(QLabel("Morph Amount:"))
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        morph_layout.addWidget(self.morph_slider)
        controls_layout.addLayout(morph_layout)
        
        # Audio controls
        if AUDIO_AVAILABLE:
            self.audio_check = QCheckBox("Enable Audio Analysis")
            controls_layout.addWidget(self.audio_check)
        
        # MIDI controls
        if MIDI_AVAILABLE:
            self.midi_button = QPushButton("Start MIDI")
            controls_layout.addWidget(self.midi_button)
        
        layout.addLayout(controls_layout)
        
        # Status labels
        self.notes_label = QLabel("Active Notes: None")
        layout.addWidget(self.notes_label)
        
        self.audio_label = QLabel("Audio: Disabled")
        layout.addWidget(self.audio_label)
        
        # Clear button
        clear_button = QPushButton("Clear All Notes")
        clear_button.clicked.connect(self._clear_all_notes)
        layout.addWidget(clear_button)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        vertex_count = list(self.initial_meshes.values())[0].n_points
        self.status_bar.showMessage(f"Ready - Perfect morphing enabled ({vertex_count} vertices per shape)")
    
    def _setup_connections(self):
        """Setup signal connections."""
        # UI
        self.morph_slider.valueChanged.connect(self._on_morph_change)
        self.target_combo.currentTextChanged.connect(self._on_target_change)
        
        # Audio
        if self.audio_analyzer:
            self.audio_check.toggled.connect(self._toggle_audio)
            self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
            self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
        
        # MIDI
        if self.midi_handler:
            self.midi_button.clicked.connect(self._toggle_midi)
            self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
            self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
            self.midi_handler.cc_signal.connect(self._on_midi_cc)
    
    def _on_morph_change(self, value):
        """Handle morph slider changes."""
        alpha = value / 100.0
        try:
            blended_points = perfect_mesh_blend(
                self.initial_meshes,
                self.current_mesh_key,
                self.target_mesh_key,
                alpha
            )
            
            if blended_points is not None:
                self.current_mesh.points = blended_points
                self._update_visualization()
                self.status_bar.showMessage(f"Morphing: {self.current_mesh_key} → {self.target_mesh_key} ({value}%)", 1000)
                
        except Exception as e:
            print(f"Morphing error: {e}")
    
    def _on_target_change(self, target_key):
        """Handle target shape changes."""
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            # Re-apply current morph amount to new target
            self._on_morph_change(self.morph_slider.value())
    
    def _on_midi_note_on(self, note, velocity):
        """FIXED: Handle MIDI note on with safe color conversion."""
        # Calculate hue from note (chromatic mapping)
        hue = (note % 12) / 12.0
        
        # FIXED: Use safe HSV to RGB conversion
        rgb_color = safe_hsv_to_rgb(hue, 0.8, 1.0)
        
        self.active_notes[note] = {
            'color': rgb_color,
            'velocity': velocity,
            'timestamp': time.time()
        }
        
        self._update_color()
        self._update_notes_display()
        
        print(f"Note ON: {note} (vel: {velocity:.2f})")
    
    def _on_midi_note_off(self, note):
        """Handle MIDI note off."""
        if note in self.active_notes:
            del self.active_notes[note]
            self._update_color()
            self._update_notes_display()
            print(f"Note OFF: {note}")
    
    def _on_midi_cc(self, cc_number, value):
        """Handle MIDI control change."""
        if cc_number == 1:  # Mod wheel
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
            print(f"CC1 (Mod Wheel): {value:.2f} -> Morph: {slider_value}%")
    
    def _on_audio_onset(self, amplitude):
        """FIXED: Handle audio onset with safe color handling."""
        try:
            # FIXED: Clamp audio color influence
            self.audio_color_influence = np.clip(amplitude * 2.0, 0.0, 1.0)
            self._update_color()
            
            # Fade out flash
            QTimer.singleShot(150, self._fade_audio_flash)
            
            print(f"Audio onset: {amplitude:.3f}")
            
        except Exception as e:
            print(f"Error handling audio onset: {e}")
    
    def _on_audio_amplitude(self, amplitude):
        """Handle audio amplitude."""
        self.audio_label.setText(f"Audio: Amplitude {amplitude:.3f}")
    
    def _fade_audio_flash(self):
        """FIXED: Fade audio flash with safe values."""
        self.audio_color_influence *= 0.3
        self.audio_color_influence = np.clip(self.audio_color_influence, 0.0, 1.0)
        
        if self.audio_color_influence > 0.01:
            self._update_color()
            QTimer.singleShot(50, self._fade_audio_flash)
        else:
            self.audio_color_influence = 0.0
    
    def _update_color(self):
        """FIXED: Update color with safe color handling."""
        try:
            if self.active_notes:
                if len(self.active_notes) == 1:
                    note_info = next(iter(self.active_notes.values()))
                    base_color = safe_color_array(note_info['color'])
                else:
                    # FIXED: Safe color blending for multiple notes
                    colors = [note_info['color'] for note_info in self.active_notes.values()]
                    weights = [note_info['velocity'] for note_info in self.active_notes.values()]
                    base_color = blend_colors_safe(colors, weights)
            else:
                base_color = safe_color_array(self.default_color)
            
            # Apply audio flash
            if self.audio_color_influence > 0:
                flash_color = np.array([1.0, 1.0, 1.0])
                influence = np.clip(self.audio_color_influence, 0.0, 1.0)
                final_color = (1 - influence) * base_color + influence * flash_color
                final_color = safe_color_array(final_color)  # FIXED: Ensure final color is safe
            else:
                final_color = base_color
            
            # Update visualization
            self._update_visualization(final_color)
            
        except Exception as e:
            print(f"Color update error: {e}")
    
    def _update_visualization(self, color=None):
        """FIXED: Update visualization with safe color handling."""
        try:
            if color is None:
                color = safe_color_array(self.default_color)
            else:
                color = safe_color_array(color)
            
            # Update the mesh with safe color
            self.plotter_widget.remove_actor(self.actor)
            self.actor = self.plotter_widget.add_mesh(
                self.current_mesh,
                color=color,
                smooth_shading=True
            )
            self.plotter_widget.render()
            
        except Exception as e:
            print(f"Visualization update error: {e}")
    
    def _update_notes_display(self):
        """Update the notes display label."""
        if self.active_notes:
            note_names = [f"Note {note}" for note in sorted(self.active_notes.keys())]
            self.notes_label.setText(f"Active Notes: {', '.join(note_names)}")
        else:
            self.notes_label.setText("Active Notes: None")
    
    def _toggle_audio(self, enabled):
        """Toggle audio analysis."""
        if enabled and self.audio_analyzer:
            if self.audio_analyzer.start():
                self.audio_label.setText("Audio: Active")
                print("✓ Audio analysis enabled")
            else:
                self.audio_check.setChecked(False)
                self.audio_label.setText("Audio: Failed to start")
        else:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
            self.audio_label.setText("Audio: Disabled")
    
    def _toggle_midi(self):
        """Toggle MIDI connection."""
        if self.midi_handler:
            if hasattr(self, '_midi_connected') and self._midi_connected:
                self.midi_handler.stop()
                self.midi_button.setText("Start MIDI")
                self._midi_connected = False
                print("MIDI disconnected")
            else:
                if self.midi_handler.start():
                    self.midi_button.setText("Stop MIDI")
                    self._midi_connected = True
                    print("✓ MIDI connected")
                else:
                    print("Failed to connect MIDI")
    
    def _cleanup_expired_notes(self):
        """Clean up expired notes."""
        current_time = time.time()
        expired_notes = [
            note for note, info in self.active_notes.items()
            if current_time - info['timestamp'] > 60  # 60 second timeout
        ]
        
        for note in expired_notes:
            del self.active_notes[note]
        
        if expired_notes:
            self._update_color()
            self._update_notes_display()
            print(f"Cleaned up {len(expired_notes)} expired notes")
    
    def _clear_all_notes(self):
        """Clear all active notes."""
        self.active_notes.clear()
        self._update_color()
        self._update_notes_display()
        print("All notes cleared")
    
    def closeEvent(self, event):
        """Handle application closure."""
        print("Shutting down perfect morphing application...")
        
        try:
            if self.midi_handler:
                self.midi_handler.stop()
                print("MIDI handler stopped")
        except Exception as e:
            print(f"Error stopping MIDI: {e}")
        
        try:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
                print("Audio analyzer stopped")
        except Exception as e:
            print(f"Error stopping audio: {e}")
        
        try:
            self.cleanup_timer.stop()
        except Exception as e:
            print(f"Error stopping cleanup timer: {e}")
        
        print("Perfect morphing application shutdown complete")
        event.accept()

# Main function
def main():
    print("=== Perfect MIDI Morphing Visualizer ===")
    print("Features:")
    print("• Perfect mesh morphing with identical vertex counts")
    print("• MIDI input with velocity-responsive colors")
    print("• Audio analysis with onset detection")
    print("• Real-time color visualization")
    print("• FIXED: Safe color handling - no more crashes!")
    print("")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Perfect MIDI Morphing Visualizer")
    
    try:
        window = PerfectMorphingWindow()
        window.resize(1200, 800)
        window.show()
        
        print("🎵 Perfect MIDI Morphing Visualizer Ready!")
        print("\nControls:")
        print("• Adjust morph slider to blend between shapes")
        print("• Enable audio analysis for onset detection")
        print("• Connect MIDI device for note input")
        print("• Play MIDI notes to see color changes")
        print("• All colors are now SAFE and won't crash!")
        print("")
        
        return app.exec()
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
