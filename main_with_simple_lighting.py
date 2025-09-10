import sys
import logging
import time
import threading
import colorsys
import numpy as np
import queue
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QSpinBox
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

# Audio imports
try:
    import pyaudio
    AUDIO_AVAILABLE = True
    print("Audio analysis available")
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio libraries not available - audio analysis disabled")

logger = logging.getLogger(__name__)

class AudioAnalyzer(QObject):
    """Simplified audio analysis."""
    
    onset_detected_signal = Signal(float)
    pitch_detected_signal = Signal(float, float)
    amplitude_signal = Signal(float)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.audio = None
        self.stream = None
        self.running = False
        self.thread = None
        self.audio_queue = queue.Queue()
        
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.chunk_size = config.AUDIO_CHUNK_SIZE
        self.buffer_size = self.sample_rate * 2
        self.audio_buffer = np.zeros(self.buffer_size)
        
    def start(self):
        if not AUDIO_AVAILABLE:
            return False
            
        try:
            self.audio = pyaudio.PyAudio()
            device_index = self._find_input_device()
            if device_index is None:
                return False
            
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
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start audio analysis: {e}")
            return False
    
    def _find_input_device(self):
        try:
            default_device = self.audio.get_default_input_device_info()
            return default_device['index']
        except Exception:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    return i
            return None
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        try:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            if not self.audio_queue.full():
                self.audio_queue.put(audio_data.copy())
            return (None, pyaudio.paContinue)
        except Exception as e:
            return (None, pyaudio.paAbort)
    
    def _analysis_loop(self):
        while self.running:
            try:
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                self._update_buffer(audio_chunk)
                self._analyze_audio()
                
            except Exception as e:
                print(f"Audio analysis error: {e}")
    
    def _update_buffer(self, new_chunk):
        try:
            shift_amount = len(new_chunk)
            self.audio_buffer[:-shift_amount] = self.audio_buffer[shift_amount:]
            self.audio_buffer[-shift_amount:] = new_chunk
        except Exception as e:
            print(f"Buffer update error: {e}")
    
    def _analyze_audio(self):
        try:
            if np.max(np.abs(self.audio_buffer)) < 1e-6:
                return
            
            rms = np.sqrt(np.mean(self.audio_buffer ** 2))
            self.amplitude_signal.emit(rms)
            
            # Simple onset detection
            current_energy = np.sum(self.audio_buffer ** 2)
            if hasattr(self, 'previous_energy'):
                energy_ratio = current_energy / max(self.previous_energy, 1e-10)
                if energy_ratio > self.config.AUDIO_ONSET_THRESHOLD:
                    self.onset_detected_signal.emit(rms)
            
            self.previous_energy = current_energy
                
        except Exception as e:
            print(f"Audio analysis failed: {e}")
    
    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

class MidiHandler(QObject):
    note_on_signal = Signal(int, float)
    note_off_signal = Signal(int)
    cc_signal = Signal(int, float)
    
    def __init__(self):
        super().__init__()
        self.midi_input = None
        self.running = False
        self.thread = None
        
    def start(self, device_name=None):
        if not MIDI_AVAILABLE:
            return False
            
        try:
            pygame.midi.init()
            device_id = self._find_device(device_name)
            if device_id is None:
                return False
            
            self.midi_input = pygame.midi.Input(device_id)
            
            self.running = True
            self.thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start MIDI: {e}")
            return False
    
    def _find_device(self, preferred_name=None):
        device_count = pygame.midi.get_count()
        
        for i in range(device_count):
            info = pygame.midi.get_device_info(i)
            name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
            is_input = info[2]
            
            if is_input:
                if preferred_name and preferred_name.lower() in name.lower():
                    return i
                elif not preferred_name:
                    return i
        
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
    
    def stop(self):
        self.running = False
        if self.midi_input:
            self.midi_input.close()
            pygame.midi.quit()

class SimpleLightingMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI + Audio + Simple Lighting Interface")
        
        # Load settings
        self.settings = QSettings("MorphingVisualizer", "Config")
        self.config.load_from_settings(self.settings)
        
        # Initialize state
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "icosahedron"
        self.active_notes = {}
        self.light_spheres = {}  # Visual light indicators
        self.default_color = np.array([0.8, 0.8, 0.8])
        
        # Lighting state
        self.lighting_enabled = True
        self.max_lights = 8
        
        # Audio state
        self.audio_color_influence = 0.0
        self.audio_morph_influence = 0.0
        
        # Setup components
        self.midi_handler = MidiHandler()
        self.audio_analyzer = AudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        
        self._setup_ui()
        self._initialize_visualization()
        self._setup_midi()
        self._setup_audio()
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(50)  # 20 FPS
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_elements)
        self.cleanup_timer.start(3000)
    
    def _setup_ui(self):
        """Setup UI without complex lighting controls."""
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
        self.layout.addWidget(QLabel("Morph Blend:"))
        self.layout.addWidget(self.morph_slider)
        
        # Simple lighting controls
        self.lighting_enabled_check = QCheckBox("Enable Light Effects")
        self.lighting_enabled_check.setChecked(True)
        self.lighting_enabled_check.toggled.connect(self._toggle_lighting)
        self.layout.addWidget(self.lighting_enabled_check)
        
        # Audio controls
        self.audio_enabled_check = QCheckBox("Enable Audio Analysis")
        self.audio_enabled_check.setChecked(False)  # Disabled by default
        self.audio_enabled_check.toggled.connect(self._toggle_audio)
        self.layout.addWidget(self.audio_enabled_check)
        
        # MIDI controls
        self.midi_button = QPushButton("Reconnect MIDI")
        self.midi_button.clicked.connect(self._reconnect_midi)
        self.layout.addWidget(self.midi_button)
        
        # Status displays
        self.notes_label = QLabel("Active Notes: None")
        self.layout.addWidget(self.notes_label)
        
        self.lights_label = QLabel("Light Effects: 0")
        self.layout.addWidget(self.lights_label)
        
        self.audio_label = QLabel("Audio: Waiting...")
        self.layout.addWidget(self.audio_label)
        
        # Clear button
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self._clear_all)
        self.layout.addWidget(self.clear_all_button)

    def _initialize_visualization(self):
        """Initialize 3D visualization with safe lighting."""
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
        
        # Use simple lighting that won't cause shader errors
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh, 
            color=self.default_color,
            smooth_shading=True
        )
        
        self.plotter_widget.reset_camera()
        
        # Connect signals
        self.morph_slider.valueChanged.connect(self.on_morph_slider_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_shape_change)
        
        self.status_bar.showMessage("Ready - MIDI notes will create light effects")
    
    def _setup_midi(self):
        if not MIDI_AVAILABLE:
            return
        
        self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
        self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
        self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        if self.midi_handler.start(self.config.MIDI_PORT):
            print("MIDI connected")
    
    def _setup_audio(self):
        if not AUDIO_AVAILABLE or not self.audio_analyzer:
            return
        
        self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
        self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
        
        if self.audio_analyzer.start():
            print("Audio analysis started")
    
    def _toggle_lighting(self, enabled):
        self.lighting_enabled = enabled
        if not enabled:
            self._clear_all_lights()
    
    def _toggle_audio(self, enabled):
        if not self.audio_analyzer:
            return
            
        if enabled:
            self.audio_analyzer.start()
        else:
            self.audio_analyzer.stop()
            self.audio_color_influence = 0.0
    
    def _on_midi_note_on(self, note, velocity):
        """Handle MIDI note - create light effect."""
        try:
            # Remove existing light for this note
            if note in self.light_spheres:
                self._remove_light_effect(note)
            
            # Create visual light effect
            if self.lighting_enabled:
                self._create_light_effect(note, velocity, 'midi')
            
            # Update main object color
            hue = note / 127.0
            rgb_color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            
            self.active_notes[note] = {
                'color': rgb_color,
                'velocity': velocity,
                'timestamp': time.time()
            }
            
            self._update_object_color()
            self._update_displays()
            
            print(f"Note ON: {note} - Light effect created")
                
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note):
        """Handle MIDI note off."""
        try:
            if note in self.light_spheres:
                self._remove_light_effect(note)
            
            if note in self.active_notes:
                del self.active_notes[note]
            
            self._update_object_color()
            self._update_displays()
            
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value):
        if cc_number == 1:
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
    
    def _on_audio_onset(self, amplitude):
        """Handle audio onset - create flash effect."""
        try:
            if not self.lighting_enabled:
                return
                
            # Create temporary white flash effect
            temp_id = int(time.time() * 1000) % 10000
            self._create_light_effect(temp_id, amplitude, 'audio_onset')
            
            # Flash the main object
            self.audio_color_influence = min(amplitude * 2, 1.0)
            self._update_object_color()
            
            # Fade out
            QTimer.singleShot(200, self._fade_audio_influence)
            
        except Exception as e:
            print(f"Error handling audio onset: {e}")
    
    def _on_audio_amplitude(self, amplitude):
        """Handle audio amplitude."""
        try:
            if amplitude > 0.1:
                self.audio_morph_influence = min(amplitude * 0.2, 0.2)
                base_morph = self.morph_slider.value() / 100.0
                combined_morph = np.clip(base_morph + self.audio_morph_influence, 0, 1)
                self._apply_morphing(combined_morph)
            
            self.audio_label.setText(f"Audio: Amplitude {amplitude:.3f}")
            
        except Exception as e:
            print(f"Error handling audio amplitude: {e}")
    
    def _create_light_effect(self, identifier, intensity, effect_type):
        """Create a visual light effect using colored spheres."""
        try:
            if len(self.light_spheres) >= self.max_lights:
                # Remove oldest
                oldest_id = min(self.light_spheres.keys())
                self._remove_light_effect(oldest_id)
            
            # Determine properties
            if effect_type == 'midi':
                hue = abs(identifier) / 127.0
                color = colorsys.hsv_to_rgb(hue, 0.9, 1.0)
                position = self._get_position_for_note(identifier)
                radius = 0.1 + intensity * 0.2
                duration = None  # Persist until note off
            elif effect_type == 'audio_onset':
                color = (1.0, 1.0, 1.0)  # White
                position = (
                    np.random.uniform(-2, 2),
                    np.random.uniform(-2, 2),
                    np.random.uniform(1, 3)
                )
                radius = 0.2 + intensity * 0.3
                duration = 1.0  # Fade out after 1 second
            else:
                color = (0.8, 0.8, 0.8)
                position = (0, 0, 2)
                radius = 0.15
                duration = 2.0
            
            # Create glowing sphere
            sphere = pv.Sphere(radius=radius, center=position)
            
            # Add to scene with glow effect
            actor = self.plotter_widget.add_mesh(
                sphere,
                color=color,
                opacity=0.8,
                smooth_shading=True
            )
            
            # Store info
            self.light_spheres[identifier] = {
                'actor': actor,
                'sphere': sphere,
                'color': color,
                'intensity': intensity,
                'position': position,
                'timestamp': time.time(),
                'duration': duration,
                'effect_type': effect_type,
                'animation_phase': 0.0
            }
            
        except Exception as e:
            print(f"Error creating light effect: {e}")
    
    def _get_position_for_note(self, note):
        """Get position for MIDI note."""
        angle = (abs(note) / 127.0) * 2 * np.pi
        height = np.interp(abs(note), [0, 127], [-1, 2])
        radius = 2.5
        
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = height
        
        return (x, y, z)
    
    def _remove_light_effect(self, identifier):
        """Remove a light effect."""
        if identifier in self.light_spheres:
            light_info = self.light_spheres.pop(identifier)
            try:
                self.plotter_widget.remove_actor(light_info['actor'])
            except Exception as e:
                print(f"Error removing light effect: {e}")
    
    def _update_animation(self):
        """Update light animations."""
        try:
            current_time = time.time()
            effects_to_remove = []
            
            for identifier, light_info in self.light_spheres.items():
                # Update animation phase
                light_info['animation_phase'] += 0.1
                
                # Check for expiration
                if light_info['duration']:
                    age = current_time - light_info['timestamp']
                    if age > light_info['duration']:
                        effects_to_remove.append(identifier)
                        continue
                    
                    # Fade out effect
                    fade_factor = max(0, 1 - (age / light_info['duration']))
                    
                    # Update opacity (simplified approach)
                    try:
                        # Re-add with updated properties
                        self.plotter_widget.remove_actor(light_info['actor'])
                        
                        new_actor = self.plotter_widget.add_mesh(
                            light_info['sphere'],
                            color=light_info['color'],
                            opacity=0.8 * fade_factor,
                            smooth_shading=True
                        )
                        
                        light_info['actor'] = new_actor
                        
                    except Exception:
                        # If update fails, just mark for removal
                        effects_to_remove.append(identifier)
            
            # Remove expired effects
            for identifier in effects_to_remove:
                self._remove_light_effect(identifier)
            
            if effects_to_remove:
                self._update_displays()
                self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error in animation update: {e}")
    
    def _cleanup_expired_elements(self):
        """Clean up old elements."""
        current_time = time.time()
        
        # Clean up old MIDI notes
        expired_notes = [note for note, info in self.active_notes.items() 
                        if current_time - info['timestamp'] > 60]
        
        for note in expired_notes:
            del self.active_notes[note]
            if note in self.light_spheres:
                self._remove_light_effect(note)
        
        if expired_notes:
            self._update_object_color()
            self._update_displays()
    
    def _fade_audio_influence(self):
        """Fade out audio influence."""
        self.audio_color_influence *= 0.5
        if self.audio_color_influence > 0.01:
            self._update_object_color()
            QTimer.singleShot(100, self._fade_audio_influence)
        else:
            self.audio_color_influence = 0.0
    
    def _update_object_color(self):
        """Update main object color."""
        try:
            # Calculate base color from MIDI notes
            if self.active_notes:
                if len(self.active_notes) == 1:
                    note_info = next(iter(self.active_notes.values()))
                    base_color = np.array(note_info['color'])
                else:
                    total_color = np.array([0.0, 0.0, 0.0])
                    total_weight = 0.0
                    
                    for note_info in self.active_notes.values():
                        weight = note_info['velocity']
                        color = np.array(note_info['color'])
                        total_color += color * weight
                        total_weight += weight
                    
                    base_color = total_color / total_weight if total_weight > 0 else self.default_color
            else:
                base_color = self.default_color
            
            # Apply audio influence
            if self.audio_color_influence > 0:
                audio_color = np.array([1.0, 1.0, 1.0])  # White flash
                final_color = (1 - self.audio_color_influence) * base_color + self.audio_color_influence * audio_color
            else:
                final_color = base_color
            
            # Update mesh
            self.plotter_widget.remove_actor(self.actor)
            self.actor = self.plotter_widget.add_mesh(
                self.current_mesh,
                color=final_color,
                smooth_shading=True
            )
            
            self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error updating object color: {e}")
    
    def _apply_morphing(self, alpha):
        """Apply morphing."""
        try:
            blended_points = blend_meshes(
                self.initial_meshes, 
                self.current_mesh_key, 
                self.target_mesh_key, 
                alpha
            )
            self.current_mesh.points = blended_points
            
        except Exception as e:
            print(f"Error applying morphing: {e}")
    
    def _clear_all(self):
        """Clear everything."""
        self.active_notes.clear()
        self._clear_all_lights()
        self._update_object_color()
        self._update_displays()
    
    def _clear_all_lights(self):
        """Clear all light effects."""
        for identifier in list(self.light_spheres.keys()):
            self._remove_light_effect(identifier)
    
    def _update_displays(self):
        """Update status displays."""
        # Notes
        if self.active_notes:
            note_names = [f"Note {note}" for note in sorted(self.active_notes.keys())]
            self.notes_label.setText(f"Active Notes: {', '.join(note_names)}")
        else:
            self.notes_label.setText("Active Notes: None")
        
        # Lights
        midi_effects = len([lid for lid, info in self.light_spheres.items() if info['effect_type'] == 'midi'])
        audio_effects = len([lid for lid, info in self.light_spheres.items() if info['effect_type'] != 'midi'])
        self.lights_label.setText(f"Light Effects: {midi_effects} MIDI, {audio_effects} Audio")
    
    def _reconnect_midi(self):
        """Reconnect MIDI."""
        self.midi_handler.stop()
        if self.midi_handler.start(self.config.MIDI_PORT):
            self.status_bar.showMessage("MIDI reconnected")
    
    def on_morph_slider_change(self, value):
        """Handle morph slider."""
        alpha = value / 100.0
        self._apply_morphing(alpha)
        self._update_object_color()
    
    def on_target_shape_change(self, target_key):
        """Handle target shape change."""
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            self.on_morph_slider_change(self.morph_slider.value())
    
    def closeEvent(self, event):
        """Clean shutdown."""
        if self.midi_handler:
            self.midi_handler.stop()
        if self.audio_analyzer:
            self.audio_analyzer.stop()
        
        self.animation_timer.stop()
        self.cleanup_timer.stop()
        event.accept()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    window = SimpleLightingMainWindow()
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())
