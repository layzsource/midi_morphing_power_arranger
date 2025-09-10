#!/usr/bin/env python3
"""
Standalone MIDI Morphing Visualizer - Working Version
Run this file directly: python standalone_app.py
"""

import sys
import os
import logging
import time
import threading
import colorsys
import numpy as np
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check core dependencies first
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox
    )
    from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✓ Core GUI dependencies available")
except ImportError as e:
    print(f"✗ Missing core dependencies: {e}")
    print("Install with: pip install PySide6 pyvista pyvistaqt")
    sys.exit(1)

# Simple Config class (embedded)
class SimpleConfig:
    def __init__(self):
        self.MESH_RESOLUTION = 50
        self.MIDI_PORT = None
        self.AUDIO_SAMPLE_RATE = 44100
        self.AUDIO_CHUNK_SIZE = 512
        self.AUDIO_ONSET_THRESHOLD = 1.5
        self.AUDIO_ENABLED = True
        self.AUDIO_DEVICE_INDEX = None
        self.AUDIO_CHANNELS = 1
        self.DEFAULT_COLOR = [0.8, 0.8, 0.8]

# Check optional dependencies
MIDI_AVAILABLE = False
try:
    import pygame
    import pygame.midi
    MIDI_AVAILABLE = True
    print("✓ Pygame MIDI support available")
except ImportError:
    print("⚠ MIDI support not available (install pygame for MIDI)")

AUDIO_AVAILABLE = False
try:
    import pyaudio
    AUDIO_AVAILABLE = True
    print("✓ PyAudio available")
except ImportError:
    print("⚠ Audio analysis not available (install pyaudio for audio)")

# Simple geometry functions (embedded)
def create_simple_meshes(resolution=50):
    """Create basic meshes."""
    try:
        meshes = {
            'sphere': pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution),
            'cube': pv.Cube(),
            'cone': pv.Cone(height=2.0, radius=1.0, resolution=resolution),
            'icosahedron': pv.Icosahedron(),
            'torus': pv.Torus(r_minor=0.3, r_major=0.7)
        }
        
        # Ensure all meshes have compatible vertex counts
        sphere_points = meshes['sphere'].n_points
        print(f"Created meshes with {sphere_points} vertices each")
        
        # Simple resampling for compatibility
        for name, mesh in meshes.items():
            if mesh.n_points != sphere_points and name != 'sphere':
                # Simple decimation/subdivision for compatibility
                if mesh.n_points > sphere_points:
                    ratio = sphere_points / mesh.n_points
                    if ratio < 1.0:
                        meshes[name] = mesh.decimate(1 - ratio)
                elif mesh.n_points < sphere_points:
                    # Use subdivision
                    subdivided = mesh.copy()
                    while subdivided.n_points < sphere_points * 0.8:
                        subdivided = subdivided.subdivide(1)
                    meshes[name] = subdivided
        
        return meshes
        
    except Exception as e:
        print(f"Error creating meshes: {e}")
        # Fallback to basic shapes
        return {
            'sphere': pv.Sphere(),
            'cube': pv.Cube(),
            'cone': pv.Cone(),
            'icosahedron': pv.Icosahedron(),
            'torus': pv.Torus()
        }

def blend_meshes_simple(meshes, source_key, target_key, alpha):
    """Simple mesh blending."""
    if source_key not in meshes or target_key not in meshes:
        print(f"Warning: Mesh keys not found: {source_key}, {target_key}")
        return meshes[source_key].points if source_key in meshes else None
    
    source_mesh = meshes[source_key]
    target_mesh = meshes[target_key]
    
    # Check vertex compatibility
    if source_mesh.n_points != target_mesh.n_points:
        print(f"Warning: Vertex count mismatch - using source mesh only")
        return source_mesh.points
    
    # Linear interpolation
    source_points = source_mesh.points
    target_points = target_mesh.points
    return (1 - alpha) * source_points + alpha * target_points

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
        self.is_active = False
        
        if AUDIO_AVAILABLE:
            self.sample_rate = config.AUDIO_SAMPLE_RATE
            self.chunk_size = config.AUDIO_CHUNK_SIZE
            self.audio_queue = queue.Queue()
            self.previous_energy = 0.0
    
    def start(self):
        if not AUDIO_AVAILABLE or self.is_active:
            return False
            
        try:
            self.audio = pyaudio.PyAudio()
            
            # Find default input device
            try:
                default_device = self.audio.get_default_input_device_info()
                device_index = default_device['index']
                print(f"Using audio device: {default_device['name']}")
            except Exception:
                device_index = None
                print("Using default audio device")
            
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.stream.start_stream()
            
            self.running = True
            self.is_active = True
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            print("✓ Audio analysis started")
            return True
            
        except Exception as e:
            print(f"✗ Failed to start audio analysis: {e}")
            return False
    
    def stop(self):
        self.running = False
        self.is_active = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("Audio analysis stopped")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        try:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            if not self.audio_queue.full():
                self.audio_queue.put(audio_data.copy())
            return (None, pyaudio.paContinue)
        except Exception:
            return (None, pyaudio.paAbort)
    
    def _analysis_loop(self):
        while self.running:
            try:
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Simple RMS calculation
                rms = np.sqrt(np.mean(audio_chunk ** 2))
                if rms > 0.001:  # Only emit if above noise floor
                    self.amplitude_signal.emit(rms)
                
                # Simple onset detection
                current_energy = np.sum(audio_chunk ** 2)
                if self.previous_energy > 0:
                    energy_ratio = current_energy / max(self.previous_energy, 1e-10)
                    if energy_ratio > self.config.AUDIO_ONSET_THRESHOLD:
                        self.onset_detected_signal.emit(rms)
                
                self.previous_energy = current_energy * 0.1 + self.previous_energy * 0.9
                
            except Exception as e:
                print(f"Audio analysis error: {e}")
                break

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
        self.midi_initialized = False
        
    def start(self, device_name=None):
        if not MIDI_AVAILABLE:
            print("MIDI not available")
            return False
            
        try:
            if not self.midi_initialized:
                pygame.midi.init()
                self.midi_initialized = True
            
            device_id = self._find_device(device_name)
            if device_id is None:
                print("No MIDI input devices found")
                return False
            
            self.midi_input = pygame.midi.Input(device_id)
            device_info = pygame.midi.get_device_info(device_id)
            device_name = device_info[1].decode() if isinstance(device_info[1], bytes) else str(device_info[1])
            print(f"✓ Connected to MIDI device: {device_name}")
            
            self.running = True
            self.thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"✗ Failed to start MIDI: {e}")
            self._cleanup_midi()
            return False
    
    def _find_device(self, preferred_name=None):
        try:
            device_count = pygame.midi.get_count()
            print(f"Found {device_count} MIDI devices")
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                is_input = info[2]
                
                print(f"  Device {i}: {name} ({'input' if is_input else 'output'})")
                
                if is_input:
                    if preferred_name and preferred_name.lower() in name.lower():
                        return i
                    elif not preferred_name:
                        return i  # Return first available input
            
            return None
        except Exception as e:
            print(f"Error finding MIDI device: {e}")
            return None
    
    def _midi_loop(self):
        while self.running and self.midi_input:
            try:
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    
                    for event in midi_events:
                        self._process_midi_event(event[0])
                
                time.sleep(0.001)
                
            except Exception as e:
                print(f"MIDI polling error: {e}")
                break
    
    def _process_midi_event(self, midi_data):
        if len(midi_data) < 3:
            return
            
        status, data1, data2 = midi_data[:3]
        
        if 144 <= status <= 159:  # Note On
            if data2 > 0:
                velocity = data2 / 127.0
                self.note_on_signal.emit(data1, velocity)
            else:
                self.note_off_signal.emit(data1)
        elif 128 <= status <= 143:  # Note Off
            self.note_off_signal.emit(data1)
        elif 176 <= status <= 191:  # Control Change
            cc_value = data2 / 127.0
            self.cc_signal.emit(data1, cc_value)
    
    def _cleanup_midi(self):
        try:
            if self.midi_input:
                self.midi_input.close()
                self.midi_input = None
        except Exception as e:
            print(f"Error closing MIDI input: {e}")
        
        try:
            if self.midi_initialized:
                pygame.midi.quit()
                self.midi_initialized = False
        except Exception as e:
            print(f"Error quitting pygame.midi: {e}")
    
    def stop(self):
        print("Stopping MIDI handler...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        self._cleanup_midi()

# Main Application Window
class MorphingVisualizerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = SimpleConfig()
        self.setWindowTitle("MIDI Morphing Visualizer - Standalone")
        
        # Initialize state
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "cube"
        self.active_notes = {}
        self.default_color = np.array(self.config.DEFAULT_COLOR)
        
        # Audio state
        self.audio_enabled = False
        self.audio_color_influence = 0.0
        
        # Setup components
        self.midi_handler = SimpleMidiHandler() if MIDI_AVAILABLE else None
        self.audio_analyzer = SimpleAudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        
        # Initialize visualization
        print("Initializing 3D visualization...")
        self._initialize_visualization()
        self._setup_ui()
        self._setup_connections()
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_elements)
        self.cleanup_timer.start(5000)  # Every 5 seconds
        
        print("✓ Application initialized successfully")
    
    def _initialize_visualization(self):
        try:
            print("Creating meshes...")
            self.initial_meshes = create_simple_meshes(self.config.MESH_RESOLUTION)
            print(f"✓ Created {len(self.initial_meshes)} meshes")
            
            # Verify we have at least basic shapes
            if len(self.initial_meshes) < 2:
                raise Exception("Not enough meshes created")
                
        except Exception as e:
            print(f"✗ Error creating meshes: {e}")
            print("Using minimal fallback meshes...")
            
            # Ultra-minimal fallback
            try:
                self.initial_meshes = {
                    'sphere': pv.Sphere(),
                    'cube': pv.Cube()
                }
                
                # Add cylinder if available
                try:
                    self.initial_meshes['cylinder'] = pv.Cylinder()
                except:
                    pass
                
                # Add cone if available
                try:
                    self.initial_meshes['cone'] = pv.Cone()
                except:
                    pass
                
                print(f"✓ Fallback: Created {len(self.initial_meshes)} basic meshes")
                
            except Exception as e2:
                print(f"✗ Even fallback mesh creation failed: {e2}")
                # Absolute minimal - just sphere
                self.initial_meshes = {'sphere': pv.Sphere()}
                print("✓ Using single sphere mesh only")
    
    def _setup_ui(self):
        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 3D Visualization
        print("Setting up 3D plotter...")
        self.plotter_widget = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter_widget)

        # Add initial mesh
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh,
            color=self.default_color,
            smooth_shading=True
        )
        self.plotter_widget.reset_camera()

        # Controls
        self.layout.addWidget(QLabel("Target Shape:"))
        self.target_shape_combo = QComboBox()
        self.target_shape_combo.addItems(sorted(list(self.initial_meshes.keys())))
        self.target_shape_combo.setCurrentText(self.target_mesh_key)
        self.layout.addWidget(self.target_shape_combo)

        self.layout.addWidget(QLabel("Morph Amount:"))
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setMinimum(0)
        self.morph_slider.setMaximum(100)
        self.morph_slider.setValue(0)
        self.layout.addWidget(self.morph_slider)
        
        # Audio controls
        if AUDIO_AVAILABLE:
            self.audio_check = QCheckBox("Enable Audio Analysis")
            self.layout.addWidget(self.audio_check)
        
        # MIDI controls
        if MIDI_AVAILABLE:
            self.midi_button = QPushButton("Connect MIDI")
            self.layout.addWidget(self.midi_button)
        
        # Status displays
        self.notes_label = QLabel("Active Notes: None")
        self.layout.addWidget(self.notes_label)
        
        self.audio_label = QLabel("Audio: Disabled")
        self.layout.addWidget(self.audio_label)
        
        # Clear button
        self.clear_button = QPushButton("Clear All Notes")
        self.layout.addWidget(self.clear_button)
        
        self.status_bar.showMessage("Ready - Use MIDI controller or morph slider to interact")
    
    def _setup_connections(self):
        # UI connections
        self.morph_slider.valueChanged.connect(self._on_morph_change)
        self.target_shape_combo.currentTextChanged.connect(self._on_target_change)
        self.clear_button.clicked.connect(self._clear_all_notes)
        
        # Audio connections
        if AUDIO_AVAILABLE and self.audio_analyzer:
            self.audio_check.toggled.connect(self._toggle_audio)
            self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
            self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
        
        # MIDI connections
        if MIDI_AVAILABLE and self.midi_handler:
            self.midi_button.clicked.connect(self._toggle_midi)
            self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
            self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
            self.midi_handler.cc_signal.connect(self._on_midi_cc)
    
    def _on_morph_change(self, value):
        alpha = value / 100.0
        try:
            blended_points = blend_meshes_simple(
                self.initial_meshes, 
                self.current_mesh_key, 
                self.target_mesh_key, 
                alpha
            )
            
            if blended_points is not None:
                self.current_mesh.points = blended_points
                self._update_visualization()
                
        except Exception as e:
            print(f"Error in morphing: {e}")
    
    def _on_target_change(self, target_key):
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            self._on_morph_change(self.morph_slider.value())
    
    def _toggle_audio(self, enabled):
        if enabled and self.audio_analyzer:
            if self.audio_analyzer.start():
                self.audio_enabled = True
                self.audio_label.setText("Audio: Active")
            else:
                self.audio_check.setChecked(False)
                self.audio_label.setText("Audio: Failed to start")
        else:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
            self.audio_enabled = False
            self.audio_label.setText("Audio: Disabled")
    
    def _toggle_midi(self):
        if self.midi_handler:
            if not self.midi_handler.running:
                if self.midi_handler.start():
                    self.midi_button.setText("Disconnect MIDI")
                    self.status_bar.showMessage("MIDI connected", 3000)
                else:
                    self.status_bar.showMessage("MIDI connection failed", 3000)
            else:
                self.midi_handler.stop()
                self.midi_button.setText("Connect MIDI")
                self.status_bar.showMessage("MIDI disconnected", 3000)
    
    def _on_midi_note_on(self, note, velocity):
        try:
            # Map note to color
            hue = note / 127.0
            rgb_color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            
            self.active_notes[note] = {
                'color': np.array(rgb_color),
                'velocity': velocity,
                'timestamp': time.time()
            }
            
            self._update_color()
            self._update_status()
            print(f"Note ON: {note} (velocity: {velocity:.2f})")
            
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note):
        try:
            if note in self.active_notes:
                del self.active_notes[note]
            
            self._update_color()
            self._update_status()
            print(f"Note OFF: {note}")
            
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value):
        if cc_number == 1:  # Mod wheel controls morphing
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
            print(f"CC1 (Mod Wheel): {value:.2f}")
    
    def _on_audio_onset(self, amplitude):
        try:
            # Flash white on audio onset
            self.audio_color_influence = min(amplitude * 5, 1.0)
            self._update_color()
            
            # Fade out after 200ms
            QTimer.singleShot(200, self._fade_audio_flash)
            
        except Exception as e:
            print(f"Error handling audio onset: {e}")
    
    def _on_audio_amplitude(self, amplitude):
        self.audio_label.setText(f"Audio: {amplitude:.3f}")
    
    def _fade_audio_flash(self):
        self.audio_color_influence *= 0.3
        if self.audio_color_influence > 0.01:
            self._update_color()
            QTimer.singleShot(50, self._fade_audio_flash)
        else:
            self.audio_color_influence = 0.0
    
    def _update_color(self):
        try:
            # Calculate color from active notes
            if self.active_notes:
                if len(self.active_notes) == 1:
                    # Single note
                    note_info = next(iter(self.active_notes.values()))
                    base_color = note_info['color']
                else:
                    # Multiple notes - blend colors
                    total_color = np.array([0.0, 0.0, 0.0])
                    total_weight = 0.0
                    
                    for note_info in self.active_notes.values():
                        weight = note_info['velocity']
                        total_color += note_info['color'] * weight
                        total_weight += weight
                    
                    base_color = total_color / total_weight if total_weight > 0 else self.default_color
            else:
                base_color = self.default_color
            
            # Apply audio flash
            if self.audio_color_influence > 0:
                flash_color = np.array([1.0, 1.0, 1.0])  # White
                final_color = (1 - self.audio_color_influence) * base_color + self.audio_color_influence * flash_color
            else:
                final_color = base_color
            
            # Update visualization
            self.plotter_widget.remove_actor(self.actor)
            self.actor = self.plotter_widget.add_mesh(
                self.current_mesh,
                color=final_color,
                smooth_shading=True
            )
            self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error updating color: {e}")
    
    def _update_visualization(self):
        """Update the 3D visualization without changing color."""
        try:
            # Get current color
            current_color = self.default_color
            if self.active_notes:
                if len(self.active_notes) == 1:
                    note_info = next(iter(self.active_notes.values()))
                    current_color = note_info['color']
                else:
                    total_color = np.array([0.0, 0.0, 0.0])
                    total_weight = 0.0
                    for note_info in self.active_notes.values():
                        weight = note_info['velocity']
                        total_color += note_info['color'] * weight
                        total_weight += weight
                    current_color = total_color / total_weight if total_weight > 0 else self.default_color
            
            # Update mesh with current color
            self.plotter_widget.remove_actor(self.actor)
            self.actor = self.plotter_widget.add_mesh(
                self.current_mesh,
                color=current_color,
                smooth_shading=True
            )
            self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error updating visualization: {e}")
    
    def _update_status(self):
        if self.active_notes:
            note_list = [f"Note {note}" for note in sorted(self.active_notes.keys())]
            self.notes_label.setText(f"Active Notes: {', '.join(note_list)}")
        else:
            self.notes_label.setText("Active Notes: None")
    
    def _clear_all_notes(self):
        self.active_notes.clear()
        self._update_color()
        self._update_status()
    
    def _cleanup_expired_elements(self):
        """Remove notes that haven't been updated in 60 seconds."""
        current_time = time.time()
        expired_notes = [
            note for note, info in self.active_notes.items()
            if current_time - info['timestamp'] > 60
        ]
        
        for note in expired_notes:
            del self.active_notes[note]
        
        if expired_notes:
            self._update_color()
            self._update_status()
    
    def closeEvent(self, event):
        print("Shutting down...")
        
        if self.midi_handler:
            self.midi_handler.stop()
        
        if self.audio_analyzer:
            self.audio_analyzer.stop()
        
        self.cleanup_timer.stop()
        
        print("Shutdown complete")
        event.accept()

def main():
    print("=== MIDI Morphing Visualizer - Standalone ===")
    
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer")
    
    try:
        window = MorphingVisualizerWindow()
        window.resize(1200, 800)
        window.show()
        
        print("Application started successfully!")
        print("\nUsage:")
        print("- Use the morph slider to blend between shapes")
        print("- Connect MIDI device and play notes for colors")
        print("- Enable audio analysis for sound-reactive effects")
        print("- CC1 (mod wheel) controls morphing amount")
        
        return app.exec()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
