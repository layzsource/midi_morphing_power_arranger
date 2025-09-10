import sys
import logging
import time
import threading
import colorsys
import numpy as np
import queue
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox
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
    """Audio analysis - only starts when explicitly enabled."""
    
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
        
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.chunk_size = config.AUDIO_CHUNK_SIZE
        self.buffer_size = self.sample_rate * 2
        self.audio_buffer = np.zeros(self.buffer_size)
        self.is_active = False  # Track if actually running
        
    def start(self):
        if not AUDIO_AVAILABLE or self.is_active:
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
            self.is_active = True
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            print("Audio analysis started")
            return True
            
        except Exception as e:
            print(f"Failed to start audio analysis: {e}")
            return False
    
    def stop(self):
        """Stop audio analysis completely."""
        self.running = False
        self.is_active = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        if self.audio:
            self.audio.terminate()
            self.audio = None
        print("Audio analysis stopped")
    
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

class FixedLightingMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI Morphing Interface - True Color Lighting")
        
        # Load settings
        self.settings = QSettings("MorphingVisualizer", "Config")
        self.config.load_from_settings(self.settings)
        
        # Initialize state
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "icosahedron"
        self.active_notes = {}
        self.default_color = np.array([0.8, 0.8, 0.8])
        
        # Audio state
        self.audio_enabled = False
        self.audio_color_influence = 0.0
        self.audio_morph_influence = 0.0
        
        # Setup components
        self.midi_handler = MidiHandler()
        self.audio_analyzer = AudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        
        self._setup_ui()
        self._initialize_visualization()
        self._setup_midi()
        # DO NOT setup audio automatically
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_elements)
        self.cleanup_timer.start(5000)
    
    def _setup_ui(self):
        """Setup UI."""
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
        self.layout.addWidget(QLabel("Morph Blend (CC#1):"))
        self.layout.addWidget(self.morph_slider)
        
        # Audio controls - DISABLED by default
        self.audio_enabled_check = QCheckBox("Enable Audio Analysis")
        self.audio_enabled_check.setChecked(False)
        self.audio_enabled_check.toggled.connect(self._toggle_audio)
        self.layout.addWidget(self.audio_enabled_check)
        
        # MIDI controls
        self.midi_button = QPushButton("Reconnect MIDI")
        self.midi_button.clicked.connect(self._reconnect_midi)
        self.layout.addWidget(self.midi_button)
        
        # Status displays
        self.notes_label = QLabel("Active Notes: None")
        self.layout.addWidget(self.notes_label)
        
        self.audio_label = QLabel("Audio: Disabled")
        self.layout.addWidget(self.audio_label)
        
        # Clear button
        self.clear_all_button = QPushButton("Clear All Notes")
        self.clear_all_button.clicked.connect(self._clear_all)
        self.layout.addWidget(self.clear_all_button)

    def _initialize_visualization(self):
        """Initialize 3D visualization - SINGLE OBJECT ONLY."""
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
        
        # Add ONLY the main morphing object
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh, 
            color=self.default_color,
            smooth_shading=True
        )
        
        self.plotter_widget.reset_camera()
        
        # Connect signals
        self.morph_slider.valueChanged.connect(self.on_morph_slider_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_shape_change)
        
        self.status_bar.showMessage("Ready - MIDI notes change object color directly")
    
    def _setup_midi(self):
        """Setup MIDI only."""
        if not MIDI_AVAILABLE:
            return
        
        self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
        self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
        self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        if self.midi_handler.start(self.config.MIDI_PORT):
            print("MIDI connected - audio analysis disabled")
    
    def _toggle_audio(self, enabled):
        """Toggle audio analysis - only starts when user enables it."""
        self.audio_enabled = enabled
        
        if enabled and self.audio_analyzer:
            if self.audio_analyzer.start():
                # Connect signals only when starting
                self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
                self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
                self.audio_label.setText("Audio: Active")
                print("Audio analysis enabled by user")
            else:
                self.audio_enabled_check.setChecked(False)
                self.audio_label.setText("Audio: Failed to start")
        else:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
            self.audio_label.setText("Audio: Disabled")
            print("Audio analysis disabled")
    
    def _on_midi_note_on(self, note, velocity):
        """Handle MIDI note - change MAIN OBJECT color only."""
        try:
            # Calculate color for this note
            hue = note / 127.0
            rgb_color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            
            # Store active note
            self.active_notes[note] = {
                'color': rgb_color,
                'velocity': velocity,
                'timestamp': time.time()
            }
            
            # Update MAIN OBJECT color immediately
            self._update_main_object_color()
            self._update_displays()
            
            print(f"Note ON: {note} - Main object color changed")
                
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note):
        """Handle MIDI note off - update main object color."""
        try:
            if note in self.active_notes:
                del self.active_notes[note]
            
            # Update main object color
            self._update_main_object_color()
            self._update_displays()
            
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value):
        """Handle MIDI CC."""
        if cc_number == 1:  # Mod wheel
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
    
    def _on_audio_onset(self, amplitude):
        """Handle audio onset - flash main object."""
        try:
            if not self.audio_enabled:
                return
                
            # Flash the main object white briefly
            self.audio_color_influence = min(amplitude * 3, 1.0)
            self._update_main_object_color()
            
            # Fade out flash
            QTimer.singleShot(150, self._fade_audio_influence)
            
        except Exception as e:
            print(f"Error handling audio onset: {e}")
    
    def _on_audio_amplitude(self, amplitude):
        """Handle audio amplitude for morphing."""
        try:
            if amplitude > 0.1:
                self.audio_morph_influence = min(amplitude * 0.2, 0.2)
                base_morph = self.morph_slider.value() / 100.0
                combined_morph = np.clip(base_morph + self.audio_morph_influence, 0, 1)
                self._apply_morphing(combined_morph)
            
            self.audio_label.setText(f"Audio: Amplitude {amplitude:.3f}")
            
        except Exception as e:
            print(f"Error handling audio amplitude: {e}")
    
    def _fade_audio_influence(self):
        """Fade out audio color influence."""
        self.audio_color_influence *= 0.5
        if self.audio_color_influence > 0.01:
            self._update_main_object_color()
            QTimer.singleShot(100, self._fade_audio_influence)
        else:
            self.audio_color_influence = 0.0
    
    def _update_main_object_color(self):
        """Update ONLY the main morphing object's color - NO ADDITIONAL OBJECTS."""
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
            
            # Apply audio flash if present
            if self.audio_color_influence > 0:
                flash_color = np.array([1.0, 1.0, 1.0])  # White flash
                final_color = (1 - self.audio_color_influence) * base_color + self.audio_color_influence * flash_color
            else:
                final_color = base_color
            
            # Update the single main object
            self.plotter_widget.remove_actor(self.actor)
            self.actor = self.plotter_widget.add_mesh(
                self.current_mesh,
                color=final_color,
                smooth_shading=True
            )
            
            self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error updating main object color: {e}")
    
    def _apply_morphing(self, alpha):
        """Apply morphing to main object."""
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
    
    def _cleanup_expired_elements(self):
        """Clean up old notes."""
        current_time = time.time()
        
        expired_notes = [note for note, info in self.active_notes.items() 
                        if current_time - info['timestamp'] > 60]
        
        for note in expired_notes:
            del self.active_notes[note]
        
        if expired_notes:
            self._update_main_object_color()
            self._update_displays()
    
    def _clear_all(self):
        """Clear all notes."""
        self.active_notes.clear()
        self._update_main_object_color()
        self._update_displays()
    
    def _update_displays(self):
        """Update status displays."""
        if self.active_notes:
            note_names = [f"Note {note}" for note in sorted(self.active_notes.keys())]
            self.notes_label.setText(f"Active Notes: {', '.join(note_names)}")
        else:
            self.notes_label.setText("Active Notes: None")
    
    def _reconnect_midi(self):
        """Reconnect MIDI."""
        self.midi_handler.stop()
        if self.midi_handler.start(self.config.MIDI_PORT):
            self.status_bar.showMessage("MIDI reconnected")
    
    def on_morph_slider_change(self, value):
        """Handle morph slider."""
        alpha = value / 100.0
        self._apply_morphing(alpha)
        self._update_main_object_color()
    
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
        
        self.cleanup_timer.stop()
        event.accept()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    window = FixedLightingMainWindow()
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())
