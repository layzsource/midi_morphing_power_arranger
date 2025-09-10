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
    import librosa
    AUDIO_AVAILABLE = True
    print("Audio analysis available")
except ImportError:
    AUDIO_AVAILABLE = False
    print("Audio libraries not available - audio analysis disabled")

logger = logging.getLogger(__name__)

class AudioAnalyzer(QObject):
    """Real-time audio analysis using PyAudio."""
    
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
        """Start audio analysis."""
        if not AUDIO_AVAILABLE:
            return False
            
        try:
            self.audio = pyaudio.PyAudio()
            device_index = self._find_input_device()
            if device_index is None:
                print("No audio input devices found")
                return False
            
            device_info = self.audio.get_device_info_by_index(device_index)
            print(f"Using audio device: {device_info['name']}")
            
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
            
            print("Audio analysis started")
            return True
            
        except Exception as e:
            print(f"Failed to start audio analysis: {e}")
            return False
    
    def _find_input_device(self):
        """Find audio input device."""
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
        """PyAudio callback."""
        try:
            if status:
                print(f"Audio stream status: {status}")
            
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            
            if not self.audio_queue.full():
                self.audio_queue.put(audio_data.copy())
            
            return (None, pyaudio.paContinue)
            
        except Exception as e:
            print(f"Audio callback error: {e}")
            return (None, pyaudio.paAbort)
    
    def _analysis_loop(self):
        """Main audio analysis loop."""
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
        """Update audio buffer."""
        try:
            shift_amount = len(new_chunk)
            self.audio_buffer[:-shift_amount] = self.audio_buffer[shift_amount:]
            self.audio_buffer[-shift_amount:] = new_chunk
        except Exception as e:
            print(f"Buffer update error: {e}")
    
    def _analyze_audio(self):
        """Analyze audio buffer."""
        try:
            if np.max(np.abs(self.audio_buffer)) < 1e-6:
                return
            
            rms = np.sqrt(np.mean(self.audio_buffer ** 2))
            self.amplitude_signal.emit(rms)
            
            # Onset detection
            current_energy = np.sum(self.audio_buffer ** 2)
            if hasattr(self, 'previous_energy'):
                energy_ratio = current_energy / max(self.previous_energy, 1e-10)
                if energy_ratio > self.config.AUDIO_ONSET_THRESHOLD:
                    self.onset_detected_signal.emit(rms)
            
            self.previous_energy = current_energy
            
            # Pitch detection
            try:
                recent_data = self.audio_buffer[-self.chunk_size * 4:]
                pitch_freq = self._detect_pitch(recent_data)
                if pitch_freq > 0:
                    confidence = min(rms * 10, 1.0)
                    self.pitch_detected_signal.emit(pitch_freq, confidence)
            except Exception:
                pass
                
        except Exception as e:
            print(f"Audio analysis failed: {e}")
    
    def _detect_pitch(self, audio_data):
        """Simple pitch detection using autocorrelation."""
        try:
            windowed = audio_data * np.hanning(len(audio_data))
            correlation = np.correlate(windowed, windowed, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            min_period = int(self.sample_rate / 800)
            max_period = int(self.sample_rate / 80)
            
            if max_period >= len(correlation):
                return 0
            
            search_range = correlation[min_period:max_period]
            if len(search_range) == 0:
                return 0
                
            peak_index = np.argmax(search_range) + min_period
            
            if peak_index > 0:
                frequency = self.sample_rate / peak_index
                if 80 <= frequency <= 800:
                    return frequency
            
            return 0
        except Exception:
            return 0
    
    def stop(self):
        """Stop audio analysis."""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("Audio analysis stopped")

class MidiHandler(QObject):
    """Handles MIDI input using pygame."""
    
    note_on_signal = Signal(int, float)
    note_off_signal = Signal(int)
    cc_signal = Signal(int, float)
    
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
            device_id = self._find_device(device_name)
            if device_id is None:
                print("No MIDI input devices found")
                return False
            
            self.midi_input = pygame.midi.Input(device_id)
            device_info = pygame.midi.get_device_info(device_id)
            device_name = device_info[1].decode() if isinstance(device_info[1], bytes) else str(device_info[1])
            print(f"Connected to MIDI device: {device_name}")
            
            self.running = True
            self.thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.thread.start()
            
            return True
            
        except Exception as e:
            print(f"Failed to start MIDI: {e}")
            return False
    
    def _find_device(self, preferred_name=None):
        """Find MIDI device."""
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
        """MIDI polling loop."""
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
        """Process MIDI event."""
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
        """Stop MIDI input."""
        self.running = False
        if self.midi_input:
            self.midi_input.close()
            pygame.midi.quit()
        print("MIDI stopped")

class DynamicLightingMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI + Audio + Dynamic Lighting Interface")
        
        # Load settings
        self.settings = QSettings("MorphingVisualizer", "Config")
        self.config.load_from_settings(self.settings)
        
        # Initialize state
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "icosahedron"
        self.active_notes = {}
        self.light_sources = {}  # Dynamic light sources
        self.default_color = np.array([0.8, 0.8, 0.8])  # Light gray for better lighting effects
        
        # Lighting state
        self.base_lighting = True
        self.dynamic_lighting_enabled = True
        self.max_lights = 8
        
        # Audio state
        self.audio_color_influence = 0.0
        self.audio_morph_influence = 0.0
        self.current_audio_amplitude = 0.0
        
        # Setup components
        self.midi_handler = MidiHandler()
        self.audio_analyzer = AudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        
        self._setup_ui()
        self._initialize_visualization()
        self._setup_midi()
        self._setup_audio()
        
        # Light animation timer
        self.light_animation_timer = QTimer()
        self.light_animation_timer.timeout.connect(self._update_light_animation)
        self.light_animation_timer.start(50)  # 20 FPS for smooth lighting
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_lights)
        self.cleanup_timer.start(2000)
    
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
        self.layout.addWidget(QLabel("Morph Blend:"))
        self.layout.addWidget(self.morph_slider)
        
        # Lighting controls
        self.lighting_enabled_check = QCheckBox("Enable Dynamic Lighting")
        self.lighting_enabled_check.setChecked(True)
        self.lighting_enabled_check.toggled.connect(self._toggle_lighting)
        self.layout.addWidget(self.lighting_enabled_check)
        
        self.max_lights_spin = QSpinBox()
        self.max_lights_spin.setRange(1, 16)
        self.max_lights_spin.setValue(8)
        self.max_lights_spin.valueChanged.connect(self._update_max_lights)
        self.layout.addWidget(QLabel("Max Dynamic Lights:"))
        self.layout.addWidget(self.max_lights_spin)
        
        # Audio controls
        self.audio_enabled_check = QCheckBox("Enable Audio Analysis")
        self.audio_enabled_check.setChecked(True)
        self.audio_enabled_check.toggled.connect(self._toggle_audio)
        self.layout.addWidget(self.audio_enabled_check)
        
        # MIDI controls
        self.midi_button = QPushButton("Reconnect MIDI")
        self.midi_button.clicked.connect(self._reconnect_midi)
        self.layout.addWidget(self.midi_button)
        
        # Status displays
        self.notes_label = QLabel("Active Notes: None")
        self.layout.addWidget(self.notes_label)
        
        self.lights_label = QLabel("Active Lights: 0")
        self.layout.addWidget(self.lights_label)
        
        self.audio_label = QLabel("Audio: Waiting for input...")
        self.layout.addWidget(self.audio_label)
        
        # Clear controls
        self.clear_all_button = QPushButton("Clear All Notes & Lights")
        self.clear_all_button.clicked.connect(self._clear_all)
        self.layout.addWidget(self.clear_all_button)

    def _initialize_visualization(self):
        """Initialize the 3D visualization with lighting setup."""
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
        
        # Enable lighting in the plotter
        self.plotter_widget.enable_lightkit()
        
        # Add the mesh with lighting-responsive material properties
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh, 
            color=self.default_color,
            smooth_shading=True,
            ambient=0.3,     # How much ambient light affects the surface
            diffuse=0.7,     # How much directional light affects the surface
            specular=0.4,    # Reflective highlights
            specular_power=20  # Sharpness of highlights
        )
        
        # Set up base lighting environment
        self._setup_base_lighting()
        
        self.plotter_widget.reset_camera()
        
        # Connect signals
        self.morph_slider.valueChanged.connect(self.on_morph_slider_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_shape_change)
        
        self.status_bar.showMessage("Ready - Dynamic lighting active")
    
    def _setup_base_lighting(self):
        """Setup base ambient lighting."""
        # Clear existing lights
        self.plotter_widget.remove_all_lights()
        
        # Add soft ambient light
        ambient_light = pv.Light(
            position=(0, 0, 10),
            focal_point=(0, 0, 0),
            color=(1, 1, 1),
            intensity=0.4,
            positional=True
        )
        self.plotter_widget.add_light(ambient_light)
        
        # Add key light
        key_light = pv.Light(
            position=(5, 5, 5),
            focal_point=(0, 0, 0),
            color=(1, 1, 1),
            intensity=0.6,
            positional=True
        )
        self.plotter_widget.add_light(key_light)
    
    def _setup_midi(self):
        """Setup MIDI connections."""
        if not MIDI_AVAILABLE:
            return
        
        self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
        self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
        self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        if self.midi_handler.start(self.config.MIDI_PORT):
            print("MIDI connected")
        else:
            print("MIDI connection failed")
    
    def _setup_audio(self):
        """Setup audio analysis."""
        if not AUDIO_AVAILABLE or not self.audio_analyzer:
            return
        
        self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
        self.audio_analyzer.pitch_detected_signal.connect(self._on_audio_pitch)
        self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
        
        if self.audio_analyzer.start():
            print("Audio analysis started")
    
    def _toggle_lighting(self, enabled):
        """Toggle dynamic lighting on/off."""
        self.dynamic_lighting_enabled = enabled
        if not enabled:
            # Clear all dynamic lights
            self.light_sources.clear()
            self._setup_base_lighting()
            self._update_object_appearance()
    
    def _toggle_audio(self, enabled):
        """Toggle audio analysis."""
        if not self.audio_analyzer:
            return
            
        if enabled:
            self.audio_analyzer.start()
        else:
            self.audio_analyzer.stop()
            self.audio_color_influence = 0.0
            self.audio_morph_influence = 0.0
    
    def _update_max_lights(self, value):
        """Update maximum number of dynamic lights."""
        self.max_lights = value
        
        # Remove excess lights if necessary
        while len(self.light_sources) > self.max_lights:
            oldest_light = min(self.light_sources.keys())
            self._remove_light_source(oldest_light)
    
    def _on_midi_note_on(self, note, velocity):
        """Handle MIDI note on - create dynamic light."""
        try:
            # Remove existing light for this note
            if note in self.light_sources:
                self._remove_light_source(note)
            
            # Create new dynamic light
            self._create_light_source(note, velocity, 'midi')
            
            # Also update base color for immediate feedback
            hue = note / 127.0
            rgb_color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            
            self.active_notes[note] = {
                'color': rgb_color,
                'velocity': velocity,
                'timestamp': time.time()
            }
            
            self._update_object_appearance()
            self._update_displays()
            
            print(f"Note ON: {note} - Dynamic light created")
                
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note):
        """Handle MIDI note off - remove dynamic light."""
        try:
            if note in self.light_sources:
                self._remove_light_source(note)
            
            if note in self.active_notes:
                del self.active_notes[note]
            
            self._update_object_appearance()
            self._update_displays()
            
            print(f"Note OFF: {note} - Light removed")
                
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value):
        """Handle MIDI control change."""
        if cc_number == 1:  # Mod wheel
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
    
    def _on_audio_onset(self, amplitude):
        """Handle audio onset - create temporary light flash."""
        try:
            if not self.dynamic_lighting_enabled:
                return
                
            # Create temporary white light for onset
            temp_note = -int(time.time() * 1000) % 1000  # Negative number for audio
            self._create_light_source(temp_note, amplitude, 'audio_onset', duration=0.5)
            
            # Also create color flash effect
            self.audio_color_influence = min(amplitude * 3, 1.0)
            self._update_object_appearance()
            
            # Fade out flash
            QTimer.singleShot(100, self._fade_audio_influence)
            
        except Exception as e:
            print(f"Error handling audio onset: {e}")
    
    def _on_audio_pitch(self, frequency, confidence):
        """Handle audio pitch detection."""
        try:
            if confidence > 0.4 and self.dynamic_lighting_enabled:
                # Map frequency to note-like value
                note_equiv = int(np.clip((frequency - 80) / (800 - 80) * 127, 0, 127))
                temp_note = -(note_equiv + 1000)  # Negative for audio
                
                # Create temporary colored light
                self._create_light_source(temp_note, confidence, 'audio_pitch', duration=1.0)
                
            self.audio_label.setText(f"Audio: {frequency:.1f}Hz (conf: {confidence:.2f})")
            
        except Exception as e:
            print(f"Error handling audio pitch: {e}")
    
    def _on_audio_amplitude(self, amplitude):
        """Handle audio amplitude for morphing."""
        try:
            self.current_audio_amplitude = amplitude
            
            if amplitude > 0.1:
                self.audio_morph_influence = min(amplitude * 0.2, 0.2)
                base_morph = self.morph_slider.value() / 100.0
                combined_morph = np.clip(base_morph + self.audio_morph_influence, 0, 1)
                self._apply_morphing(combined_morph)
            
        except Exception as e:
            print(f"Error handling audio amplitude: {e}")
    
    def _create_light_source(self, identifier, intensity, source_type, duration=None):
        """Create a dynamic light source."""
        try:
            if not self.dynamic_lighting_enabled:
                return
                
            # Remove oldest light if at maximum
            if len(self.light_sources) >= self.max_lights:
                oldest_id = min(self.light_sources.keys())
                self._remove_light_source(oldest_id)
            
            # Determine light properties based on source
            if source_type == 'midi':
                hue = abs(identifier) / 127.0
                color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
                position = self._get_light_position_for_note(identifier)
                light_intensity = intensity * 2.0
            elif source_type == 'audio_onset':
                color = (1.0, 1.0, 1.0)  # White flash
                position = (np.random.uniform(-3, 3), np.random.uniform(-3, 3), np.random.uniform(2, 4))
                light_intensity = intensity * 3.0
            elif source_type == 'audio_pitch':
                hue = (abs(identifier) % 127) / 127.0
                color = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                position = (np.random.uniform(-2, 2), np.random.uniform(-2, 2), np.random.uniform(1, 3))
                light_intensity = intensity * 1.5
            else:
                color = (1.0, 1.0, 1.0)
                position = (0, 0, 3)
                light_intensity = intensity
            
            # Create PyVista light
            light = pv.Light(
                position=position,
                focal_point=(0, 0, 0),
                color=color,
                intensity=light_intensity,
                cone_angle=45,
                positional=True
            )
            
            # Store light info
            self.light_sources[identifier] = {
                'light': light,
                'color': color,
                'intensity': light_intensity,
                'position': position,
                'timestamp': time.time(),
                'source_type': source_type,
                'duration': duration,
                'animation_phase': 0.0
            }
            
            # Add to plotter
            self.plotter_widget.add_light(light)
            
        except Exception as e:
            print(f"Error creating light source: {e}")
    
    def _get_light_position_for_note(self, note):
        """Get consistent light position for a MIDI note."""
        # Use note number to generate consistent position
        angle = (abs(note) / 127.0) * 2 * np.pi
        height = np.interp(abs(note), [0, 127], [-1, 2])
        radius = 3.0
        
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = height
        
        return (x, y, z)
    
    def _remove_light_source(self, identifier):
        """Remove a dynamic light source."""
        if identifier in self.light_sources:
            light_info = self.light_sources.pop(identifier)
            try:
                # Remove light from plotter
                if hasattr(self.plotter_widget, 'renderer'):
                    self.plotter_widget.renderer.RemoveLight(light_info['light'].GetLightObject())
            except Exception as e:
                print(f"Error removing light: {e}")
    
    def _update_light_animation(self):
        """Update animated lighting effects."""
        try:
            if not self.dynamic_lighting_enabled:
                return
                
            current_time = time.time()
            lights_to_remove = []
            
            for identifier, light_info in self.light_sources.items():
                # Update animation phase
                light_info['animation_phase'] += 0.1
                
                # Check for expiration
                if light_info['duration'] and (current_time - light_info['timestamp']) > light_info['duration']:
                    lights_to_remove.append(identifier)
                    continue
                
                # Animate light properties
                if light_info['source_type'] == 'audio_onset':
                    # Fade out onset lights
                    age = current_time - light_info['timestamp']
                    fade_factor = max(0, 1 - (age / light_info['duration'])) if light_info['duration'] else 1
                    
                    # Update light intensity (this is a simplified approach)
                    base_intensity = light_info['intensity']
                    current_intensity = base_intensity * fade_factor
                    
                elif light_info['source_type'] == 'midi':
                    # Subtle pulsing for MIDI lights
                    pulse = 0.8 + 0.2 * np.sin(light_info['animation_phase'])
                    current_intensity = light_info['intensity'] * pulse
                
            # Remove expired lights
            for identifier in lights_to_remove:
                self._remove_light_source(identifier)
            
            # Update displays if lights changed
            if lights_to_remove:
                self._update_displays()
            
        except Exception as e:
            print(f"Error in light animation: {e}")
    
    def _cleanup_expired_lights(self):
        """Clean up old lights and notes."""
        current_time = time.time()
        
        # Clean up old MIDI notes
        expired_notes = [note for note, info in self.active_notes.items() 
                        if current_time - info['timestamp'] > 60]
        
        for note in expired_notes:
            del self.active_notes[note]
            if note in self.light_sources:
                self._remove_light_source(note)
        
        # Clean up audio lights without duration
        expired_lights = [lid for lid, info in self.light_sources.items() 
                         if not info['duration'] and current_time - info['timestamp'] > 30]
        
        for lid in expired_lights:
            self._remove_light_source(lid)
        
        if expired_notes or expired_lights:
            self._update_object_appearance()
            self._update_displays()
    
    def _fade_audio_influence(self):
        """Fade out audio color influence."""
        self.audio_color_influence *= 0.7
        if self.audio_color_influence > 0.01:
            self._update_object_appearance()
            QTimer.singleShot(50, self._fade_audio_influence)
        else:
            self.audio_color_influence = 0.0
    
    def _update_object_appearance(self):
        """Update the main object's appearance based on all influences."""
        try:
            # Calculate base color from MIDI notes
            if self.active_notes:
                if len(self.active_notes) == 1:
                    note_info = next(iter(self.active_notes.values()))
                    base_color = np.array(note_info['color'])
                else:
                    # Blend multiple MIDI notes
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
                if hasattr(self, 'current_audio_hue'):
                    audio_color = np.array(colorsys.hsv_to_rgb(self.current_audio_hue, 1.0, 1.0))
                else:
                    audio_color = np.array([1.0, 1.0, 1.0])  # White flash
                
                final_color = (1 - self.audio_color_influence) * base_color + self.audio_color_influence * audio_color
            else:
                final_color = base_color
            
            # Update the mesh actor
            self.plotter_widget.remove_actor(self.actor)
            self.actor = self.plotter_widget.add_mesh(
                self.current_mesh,
                color=final_color,
                smooth_shading=True,
                ambient=0.3,
                diffuse=0.7,
                specular=0.4,
                specular_power=20
            )
            
            self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error updating object appearance: {e}")
    
    def _apply_morphing(self, alpha):
        """Apply morphing with given alpha value."""
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
        """Clear all notes and lights."""
        self.active_notes.clear()
        
        # Clear all dynamic lights
        for identifier in list(self.light_sources.keys()):
            self._remove_light_source(identifier)
        
        # Reset to base lighting
        self._setup_base_lighting()
        
        self._update_object_appearance()
        self._update_displays()
    
    def _update_displays(self):
        """Update all status displays."""
        # Update notes display
        if self.active_notes:
            note_names = [f"Note {note}" for note in sorted(self.active_notes.keys())]
            self.notes_label.setText(f"Active Notes: {', '.join(note_names)}")
        else:
            self.notes_label.setText("Active Notes: None")
        
        # Update lights display
        midi_lights = len([lid for lid, info in self.light_sources.items() if info['source_type'] == 'midi'])
        audio_lights = len([lid for lid, info in self.light_sources.items() if info['source_type'] != 'midi'])
        self.lights_label.setText(f"Active Lights: {midi_lights} MIDI, {audio_lights} Audio")
    
    def _reconnect_midi(self):
        """Reconnect MIDI."""
        self.midi_handler.stop()
        if self.midi_handler.start(self.config.MIDI_PORT):
            self.status_bar.showMessage("MIDI reconnected")
        else:
            self.status_bar.showMessage("MIDI reconnection failed")
    
    def on_morph_slider_change(self, value):
        """Handle manual morph slider changes."""
        alpha = value / 100.0
        self._apply_morphing(alpha)
        self._update_object_appearance()
    
    def on_target_shape_change(self, target_key):
        """Handle target shape changes."""
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            self.on_morph_slider_change(self.morph_slider.value())
    
    def closeEvent(self, event):
        """Clean shutdown."""
        if self.midi_handler:
            self.midi_handler.stop()
        if self.audio_analyzer:
            self.audio_analyzer.stop()
        
        self.light_animation_timer.stop()
        self.cleanup_timer.stop()
        event.accept()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    window = DynamicLightingMainWindow()
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())
