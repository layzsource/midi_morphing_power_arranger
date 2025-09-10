import sys
import logging
import time
import threading
import colorsys
import numpy as np
import queue
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMenuBar,
    QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject
from PySide6.QtGui import QAction
from pyvistaqt import QtInteractor
import pyvista as pv

from config import Config
from geometry import create_initial_meshes, blend_meshes
from performance_monitoring import PerformanceProfiler, PerformanceDialog, performance_monitor
from config_dialog import ConfigurationDialog
from scene_manager import SceneManager
from scene_config_dialog import SceneConfigurationDialog

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
        self.is_active = False
    
    @performance_monitor
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
    
    @performance_monitor
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
    
    @performance_monitor
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
        self.midi_initialized = False
        
    @performance_monitor
    def start(self, device_name=None):
        if not MIDI_AVAILABLE:
            return False
            
        try:
            # Initialize pygame.midi if not already done
            if not self.midi_initialized:
                pygame.midi.init()
                self.midi_initialized = True
            
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
            self._cleanup_midi()
            return False
    
    def _find_device(self, preferred_name=None):
        try:
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
        except Exception as e:
            print(f"Error finding MIDI device: {e}")
            return None
    
    @performance_monitor
    def _midi_loop(self):
        while self.running and self.midi_input:
            try:
                # Check if pygame.midi is still initialized
                if not self.midi_initialized:
                    break
                    
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    
                    for event in midi_events:
                        self._process_midi_event(event[0])
                
                time.sleep(0.001)
                
            except Exception as e:
                print(f"MIDI polling error: {e}")
                break
        
        print("MIDI loop ended")
    
    @performance_monitor
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
        """Safely cleanup MIDI resources."""
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
        """Stop MIDI handler safely."""
        print("Stopping MIDI handler...")
        self.running = False
        
        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        # Cleanup MIDI resources
        self._cleanup_midi()
        print("MIDI handler stopped")

class PerformanceAwareMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI Morphing Interface - Performance Monitored")
        
        # Initialize performance profiler FIRST
        self.profiler = PerformanceProfiler(self.config)
        
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
        
        # Performance monitoring dialog
        self.performance_dialog = None
        self.config_dialog = None
        self.scene_config_dialog = None
        
        # Scene manager for multi-object compositions
        self.scene_manager = None
        
        # Setup components
        self.midi_handler = MidiHandler()
        self.audio_analyzer = AudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        
        # Give components access to profiler for monitoring
        if hasattr(self.midi_handler, 'profiler'):
            self.midi_handler.profiler = self.profiler
        if self.audio_analyzer and hasattr(self.audio_analyzer, 'profiler'):
            self.audio_analyzer.profiler = self.profiler
        
        # Initialize visualization and scene manager BEFORE UI setup
        self._initialize_visualization()
        
        self._setup_ui()
        self._setup_menu()
        self._setup_midi()
        self._setup_performance_monitoring()
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_elements)
        self.cleanup_timer.start(5000)
        
        # Frame timing for FPS calculation
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._frame_update)
        self.render_timer.start(16)  # ~60 FPS target
    
    def _show_scene_config_dialog(self):
        """Show scene configuration dialog."""
        if not self.scene_manager:
            QMessageBox.warning(self, "Scene Manager", "Scene manager not initialized. Please restart the application.")
            return
        
        if self.scene_config_dialog is None:
            self.scene_config_dialog = SceneConfigurationDialog(self.scene_manager, self)
            self.scene_config_dialog.scene_updated.connect(self._on_scene_updated)
        
        self.scene_config_dialog.show()
        self.scene_config_dialog.raise_()
        self.scene_config_dialog.activateWindow()
    
    def _on_scene_updated(self):
        """Handle scene configuration updates."""
        try:
            # Update display
            self._update_scene_display()
            
            # Update target shape combo with available shapes
            current_text = self.target_shape_combo.currentText()
            self.target_shape_combo.clear()
            self.target_shape_combo.addItems(sorted(list(self.initial_meshes.keys())))
            
            # Restore selection if possible
            index = self.target_shape_combo.findText(current_text)
            if index >= 0:
                self.target_shape_combo.setCurrentIndex(index)
            
            self.status_bar.showMessage("Scene configuration updated", 3000)
            
        except Exception as e:
            print(f"Error updating scene: {e}")
            self.status_bar.showMessage(f"Error updating scene: {e}", 5000)
    
    @performance_monitor
    def _initialize_visualization(self):
        """Initialize 3D visualization with scene manager."""
        # Create meshes first
        self.initial_meshes = create_initial_meshes(self.config.MESH_RESOLUTION)
        logger.info(f"Created {len(self.initial_meshes)} meshes")
        
        # Initialize scene manager (this must happen before UI setup)
        self.scene_manager = SceneManager(self.initial_meshes, None)  # Plotter will be set later
        print("Scene manager initialized")
    
    def _finalize_visualization_setup(self):
        """Finalize visualization setup after UI is ready."""
        # Now we can set the plotter widget
        self.scene_manager.plotter_widget = self.plotter_widget
        
        # Clear any default objects and recreate with proper plotter
        for obj_id in list(self.scene_manager.objects.keys()):
            self.scene_manager.remove_object(obj_id)
        
        # Recreate default scene
        self.scene_manager._setup_default_mappings()
        
        # Reset camera
        self.plotter_widget.reset_camera()
        
        self.status_bar.showMessage("Ready - Multi-object scene with note range mapping active")
    
    def _setup_menu(self):
        """Setup application menu with performance options."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Configuration submenu
        config_action = QAction("Settings...", self)
        config_action.triggered.connect(self._show_config_dialog)
        config_action.setShortcut("Ctrl+,")
        file_menu.addAction(config_action)
        
        file_menu.addSeparator()
        
        export_perf_action = QAction("Export Performance Data", self)
        export_perf_action.triggered.connect(self._export_performance_data)
        file_menu.addAction(export_perf_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Scene configuration
        scene_config_action = QAction("Scene Configuration...", self)
        scene_config_action.triggered.connect(self._show_scene_config_dialog)
        scene_config_action.setShortcut("Ctrl+Shift+S")
        view_menu.addAction(scene_config_action)
        
        view_menu.addSeparator()
        
        # Performance menu
        perf_menu = menubar.addMenu("Performance")
        
        show_monitor_action = QAction("Show Performance Monitor", self)
        show_monitor_action.triggered.connect(self._show_performance_dialog)
        perf_menu.addAction(show_monitor_action)
        
        perf_menu.addSeparator()
        
        enable_monitoring_action = QAction("Enable Performance Monitoring", self)
        enable_monitoring_action.setCheckable(True)
        enable_monitoring_action.setChecked(self.profiler.enabled)
        enable_monitoring_action.toggled.connect(self._toggle_performance_monitoring)
        perf_menu.addAction(enable_monitoring_action)
        
        reset_stats_action = QAction("Reset Performance Statistics", self)
        reset_stats_action.triggered.connect(self._reset_performance_stats)
        perf_menu.addAction(reset_stats_action)
    
    @performance_monitor
    def _setup_ui(self):
        """Setup UI with performance monitoring."""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Status bar with performance info
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Loading...")
        
        # Performance indicator in status bar
        self.fps_label = QLabel("FPS: --")
        self.memory_label = QLabel("Memory: --")
        self.status_bar.addPermanentWidget(self.fps_label)
        self.status_bar.addPermanentWidget(self.memory_label)

        # Initialize plotter
        self.plotter_widget = QtInteractor(self.central_widget)
        self.layout.addWidget(self.plotter_widget)

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
        
        # Audio controls
        self.audio_enabled_check = QCheckBox("Enable Audio Analysis")
        self.audio_enabled_check.setChecked(False)
        self.audio_enabled_check.toggled.connect(self._toggle_audio)
        self.layout.addWidget(self.audio_enabled_check)
        
        # MIDI controls
        self.midi_button = QPushButton("Reconnect MIDI")
        self.midi_button.clicked.connect(self._reconnect_midi)
        self.layout.addWidget(self.midi_button)
        
        # Scene configuration button
        self.scene_config_button = QPushButton("Scene Configuration")
        self.scene_config_button.clicked.connect(self._show_scene_config_dialog)
        self.layout.addWidget(self.scene_config_button)
        
        # Configuration button
        self.config_button = QPushButton("Settings")
        self.config_button.clicked.connect(self._show_config_dialog)
        self.layout.addWidget(self.config_button)
        
        # Performance button
        self.performance_button = QPushButton("Show Performance Monitor")
        self.performance_button.clicked.connect(self._show_performance_dialog)
        self.layout.addWidget(self.performance_button)
        
        # Status displays
        self.notes_label = QLabel("Active Notes: None")
        self.layout.addWidget(self.notes_label)
        
        self.audio_label = QLabel("Audio: Disabled")
        self.layout.addWidget(self.audio_label)
        
        # Clear button
        self.clear_all_button = QPushButton("Clear All Notes")
        self.clear_all_button.clicked.connect(self._clear_all)
        self.layout.addWidget(self.clear_all_button)
        
        # Finalize visualization setup now that UI is ready
        self._finalize_visualization_setup()
        
        # Connect UI signals
        self.morph_slider.valueChanged.connect(self.on_morph_slider_change)
        self.target_shape_combo.currentTextChanged.connect(self.on_target_shape_change)

    def _setup_performance_monitoring(self):
        """Setup performance monitoring system."""
        # Connect profiler signals to status bar updates
        self.profiler.fps_updated.connect(self._update_fps_status)
        self.profiler.memory_updated.connect(self._update_memory_status)
        self.profiler.performance_warning.connect(self._show_performance_warning)
        
        # Start monitoring
        self.profiler.start_monitoring()
    
    def _setup_midi(self):
        """Setup MIDI with performance monitoring."""
        if not MIDI_AVAILABLE:
            return
        
        # Give MIDI handler access to profiler
        self.midi_handler.profiler = self.profiler
        
        self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
        self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
        self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        if self.midi_handler.start(self.config.MIDI_PORT):
            print("MIDI connected with performance monitoring")
    
    def _frame_update(self):
        """Called every frame for FPS monitoring."""
        self.profiler.start_frame()
        # Any per-frame processing would go here
        self.profiler.end_frame()
    
    @performance_monitor
    def _toggle_audio(self, enabled):
        """Toggle audio analysis with performance monitoring."""
        self.audio_enabled = enabled
        
        if enabled and self.audio_analyzer:
            # Give audio analyzer access to profiler
            self.audio_analyzer.profiler = self.profiler
            
            if self.audio_analyzer.start():
                self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
                self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
                self.audio_label.setText("Audio: Active")
                print("Audio analysis enabled with performance monitoring")
            else:
                self.audio_enabled_check.setChecked(False)
                self.audio_label.setText("Audio: Failed to start")
        else:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
            self.audio_label.setText("Audio: Disabled")
    
    @performance_monitor
    def _on_midi_note_on(self, note, velocity):
        """Handle MIDI note with scene manager."""
        try:
            if self.scene_manager:
                # Route to scene manager for multi-object handling
                affected_objects = self.scene_manager.handle_midi_note(note, velocity, True)
                
                if affected_objects:
                    print(f"Note ON: {note} -> Objects: {', '.join(affected_objects)}")
                    self._update_scene_display()
                else:
                    print(f"Note ON: {note} - No objects in range")
            else:
                # Fallback to single object mode
                self._handle_single_object_note_on(note, velocity)
                
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    @performance_monitor
    def _on_midi_note_off(self, note):
        """Handle MIDI note off with scene manager."""
        try:
            if self.scene_manager:
                # Route to scene manager
                affected_objects = self.scene_manager.handle_midi_note(note, 0, False)
                
                if affected_objects:
                    print(f"Note OFF: {note} -> Objects: {', '.join(affected_objects)}")
                    self._update_scene_display()
            else:
                # Fallback to single object mode
                self._handle_single_object_note_off(note)
            
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _handle_single_object_note_on(self, note, velocity):
        """Fallback single object note handling."""
        hue = note / 127.0
        rgb_color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        
        self.active_notes[note] = {
            'color': rgb_color,
            'velocity': velocity,
            'timestamp': time.time()
        }
        
        self._update_main_object_color()
        self._update_displays()
    
    def _handle_single_object_note_off(self, note):
        """Fallback single object note off handling."""
        if note in self.active_notes:
            del self.active_notes[note]
        
        self._update_main_object_color()
        self._update_displays()
    
    def _update_scene_display(self):
        """Update the scene display information."""
        if self.scene_manager:
            summary = self.scene_manager.get_scene_summary()
            active_objects = summary['active_objects']
            total_notes = summary['total_active_notes']
            
            if total_notes > 0:
                note_info = []
                for obj_id, obj_info in summary['objects'].items():
                    if obj_info['active_notes'] > 0:
                        note_info.append(f"{obj_id}({obj_info['active_notes']})")
                
                self.notes_label.setText(f"Active: {', '.join(note_info)} | Total Notes: {total_notes}")
            else:
                self.notes_label.setText("Active Notes: None")
        else:
            self._update_displays()
    
    @performance_monitor
    def _on_midi_cc(self, cc_number, value):
        """Handle MIDI CC with performance monitoring."""
        if cc_number == 1:  # Mod wheel
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
    
    @performance_monitor
    def _on_audio_onset(self, amplitude):
        """Handle audio onset with performance monitoring."""
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
    
    @performance_monitor
    def _on_audio_amplitude(self, amplitude):
        """Handle audio amplitude with performance monitoring."""
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
    
    @performance_monitor
    def _update_main_object_color(self):
        """Update main object color with performance monitoring."""
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
            
            # Update the single main object (fallback mode only)
            if hasattr(self, 'actor') and hasattr(self, 'current_mesh'):
                self.plotter_widget.remove_actor(self.actor)
                self.actor = self.plotter_widget.add_mesh(
                    self.current_mesh,
                    color=final_color,
                    smooth_shading=True
                )
                
                self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error updating main object color: {e}")
    
    @performance_monitor
    def _apply_morphing(self, alpha):
        """Apply morphing with performance monitoring."""
        try:
            if self.scene_manager:
                # Apply morphing to all objects in the scene
                for obj_id, visual_obj in self.scene_manager.objects.items():
                    if hasattr(visual_obj, 'mesh') and hasattr(visual_obj, 'shape_type'):
                        # Get the current and target mesh keys
                        current_key = visual_obj.shape_type
                        target_key = getattr(visual_obj, 'current_morph_target', self.target_mesh_key)
                        
                        # Ensure both meshes exist
                        if current_key in self.initial_meshes and target_key in self.initial_meshes:
                            # Blend the meshes
                            blended_points = blend_meshes(
                                self.initial_meshes, 
                                current_key, 
                                target_key, 
                                alpha
                            )
                            
                            # Update the visual object's mesh
                            visual_obj.mesh.points = blended_points
                            
                            # Update morph amount for reference
                            visual_obj.morph_amount = alpha
                
                # Trigger scene rendering
                self.scene_manager.render_frame()
                
            elif hasattr(self, 'current_mesh') and hasattr(self, 'current_mesh_key'):
                # Fallback single object mode
                blended_points = blend_meshes(
                    self.initial_meshes, 
                    self.current_mesh_key, 
                    self.target_mesh_key, 
                    alpha
                )
                self.current_mesh.points = blended_points
                
                # Re-render the main object if actor exists
                if hasattr(self, 'actor'):
                    # Get current color to preserve it
                    current_color = self.default_color
                    if self.active_notes:
                        # Calculate current color from active notes
                        if len(self.active_notes) == 1:
                            note_info = next(iter(self.active_notes.values()))
                            current_color = np.array(note_info['color'])
                        else:
                            # Blend multiple colors
                            total_color = np.array([0.0, 0.0, 0.0])
                            total_weight = 0.0
                            for note_info in self.active_notes.values():
                                weight = note_info['velocity']
                                color = np.array(note_info['color'])
                                total_color += color * weight
                                total_weight += weight
                            current_color = total_color / total_weight if total_weight > 0 else self.default_color
                    
                    # Remove old actor and add new one with morphed mesh
                    self.plotter_widget.remove_actor(self.actor)
                    self.actor = self.plotter_widget.add_mesh(
                        self.current_mesh,
                        color=current_color,
                        smooth_shading=True
                    )
                    
                    # Render the updated scene
                    self.plotter_widget.render()
            
        except Exception as e:
            print(f"Error applying morphing: {e}")
            import traceback
            traceback.print_exc()
    
    def _cleanup_expired_elements(self):
        """Clean up expired notes from scene manager."""
        if self.scene_manager:
            self.scene_manager.cleanup_expired_notes(60.0)
            self._update_scene_display()
        else:
            # Fallback cleanup for single object mode
            current_time = time.time()
            expired_notes = [note for note, info in self.active_notes.items() 
                            if current_time - info['timestamp'] > 60]
            
            for note in expired_notes:
                del self.active_notes[note]
            
            if expired_notes:
                self._update_main_object_color()
                self._update_displays()
    
    def _clear_all(self):
        """Clear all notes from scene manager."""
        if self.scene_manager:
            self.scene_manager.clear_all_notes()
            self._update_scene_display()
        else:
            # Fallback for single object mode
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
        """Reconnect MIDI safely."""
        print("Reconnecting MIDI...")
        self.midi_handler.stop()
        
        # Give it a moment to cleanup
        QTimer.singleShot(100, self._do_midi_reconnect)
    
    def _do_midi_reconnect(self):
        """Perform the actual MIDI reconnection."""
        if self.midi_handler.start(self.config.MIDI_PORT):
            self.status_bar.showMessage("MIDI reconnected successfully", 3000)
            print("MIDI reconnected successfully")
        else:
            self.status_bar.showMessage("MIDI reconnection failed", 3000)
            print("MIDI reconnection failed")
    
    @performance_monitor
    def on_morph_slider_change(self, value):
        """Handle morph slider - affects all objects in scene."""
        alpha = value / 100.0
        
        if self.scene_manager:
            # Apply morphing to all objects that support it
            for obj_id, visual_obj in self.scene_manager.objects.items():
                if hasattr(visual_obj, 'morph_amount'):
                    visual_obj.morph_amount = alpha
            
            # Trigger scene update
            self.scene_manager.render_frame()
        else:
            # Fallback single object morphing
            self._apply_morphing(alpha)
            self._update_main_object_color()
    
    def on_target_shape_change(self, target_key):
        """Handle target shape change."""
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            
            if self.scene_manager:
                # Set target shape for all objects
                for visual_obj in self.scene_manager.objects.values():
                    visual_obj.current_morph_target = target_key
                
                # Apply current morph amount
                self.on_morph_slider_change(self.morph_slider.value())
            else:
                # Fallback single object
                self.on_morph_slider_change(self.morph_slider.value())
    
    # Configuration dialog methods
    def _show_config_dialog(self):
        """Show configuration dialog."""
        if self.config_dialog is None:
            self.config_dialog = ConfigurationDialog(self.config, self)
            self.config_dialog.settings_changed.connect(self._on_settings_changed)
        
        self.config_dialog.show()
        self.config_dialog.raise_()
        self.config_dialog.activateWindow()
    
    def _on_settings_changed(self):
        """Handle settings changes from configuration dialog."""
        try:
            # Update performance monitoring thresholds
            if hasattr(self.config, 'FPS_WARNING'):
                self.profiler.fps_warning_threshold = self.config.FPS_WARNING
            if hasattr(self.config, 'MEMORY_WARNING'):
                self.profiler.memory_warning_threshold = self.config.MEMORY_WARNING
            if hasattr(self.config, 'CPU_WARNING'):
                self.profiler.cpu_warning_threshold = self.config.CPU_WARNING
            
            # Update cleanup interval
            if hasattr(self.config, 'CLEANUP_INTERVAL'):
                self.cleanup_timer.setInterval(self.config.CLEANUP_INTERVAL * 1000)
            
            # Update render timer for FPS target
            if hasattr(self.config, 'TARGET_FPS'):
                target_interval = int(1000 / self.config.TARGET_FPS)
                self.render_timer.setInterval(target_interval)
            
            # Update mesh resolution if changed
            if hasattr(self.config, 'MESH_RESOLUTION'):
                old_resolution = getattr(self, '_last_mesh_resolution', 50)
                if old_resolution != self.config.MESH_RESOLUTION:
                    self._recreate_meshes()
                    self._last_mesh_resolution = self.config.MESH_RESOLUTION
            
            # Update default color
            if hasattr(self.config, 'DEFAULT_COLOR'):
                self.default_color = np.array(self.config.DEFAULT_COLOR)
                if not self.scene_manager:
                    self._update_main_object_color()
            
            # Apply audio settings if analyzer is active
            if self.audio_analyzer and self.audio_analyzer.is_active:
                if hasattr(self.config, 'AUDIO_ONSET_THRESHOLD'):
                    # Note: Would need to restart audio analyzer for sample rate changes
                    pass
            
            # Update MIDI settings
            if hasattr(self.config, 'MIDI_AUTO_RECONNECT') and self.config.MIDI_AUTO_RECONNECT:
                if not self.midi_handler.running:
                    self._reconnect_midi()
            
            # Save settings to persistent storage
            self.config.save_to_settings(self.settings)
            
            self.status_bar.showMessage("Settings updated successfully", 3000)
            
        except Exception as e:
            print(f"Error applying settings: {e}")
            self.status_bar.showMessage(f"Error updating settings: {e}", 5000)
    
    def _recreate_meshes(self):
        """Recreate meshes with new resolution."""
        try:
            # Store current state
            current_morph = self.morph_slider.value() / 100.0
            
            # Recreate meshes with new resolution
            old_meshes = self.initial_meshes
            self.initial_meshes = create_initial_meshes(self.config.MESH_RESOLUTION)
            
            if self.scene_manager:
                # Update scene manager with new meshes
                self.scene_manager.initial_meshes = self.initial_meshes
                
                # Recreate all objects with new resolution
                for obj_id, visual_obj in list(self.scene_manager.objects.items()):
                    # Store object configuration
                    config = {
                        'note_range': visual_obj.note_range,
                        'shape_type': visual_obj.shape_type,
                        'position': visual_obj.position.copy(),
                        'scale': visual_obj.scale,
                        'depth_layer': visual_obj.depth_layer,
                        'blend_mode': visual_obj.blend_mode
                    }
                    
                    # Remove and recreate
                    self.scene_manager.remove_object(obj_id)
                    self.scene_manager.add_object(
                        id=obj_id,
                        note_range=config['note_range'],
                        shape_type=config['shape_type'],
                        position=config['position'],
                        scale=config['scale'],
                        depth_layer=config['depth_layer'],
                        blend_mode=config['blend_mode']
                    )
            else:
                # Fallback single object recreation
                if hasattr(self, 'current_mesh_key'):
                    self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
                    
                    # Apply current morphing
                    self._apply_morphing(current_morph)
                    
                    # Update visualization
                    self._update_main_object_color()
            
            print(f"Meshes recreated with resolution: {self.config.MESH_RESOLUTION}")
            
        except Exception as e:
            print(f"Error recreating meshes: {e}")
    
    # Performance monitoring UI methods
    def _show_performance_dialog(self):
        """Show performance monitoring dialog."""
        if self.performance_dialog is None:
            self.performance_dialog = PerformanceDialog(self.profiler, self)
        
        self.performance_dialog.show()
        self.performance_dialog.raise_()
        self.performance_dialog.activateWindow()
    
    def _toggle_performance_monitoring(self, enabled):
        """Toggle performance monitoring."""
        self.profiler.enabled = enabled
        if enabled and not self.profiler.monitoring_active:
            self.profiler.start_monitoring()
        elif not enabled:
            self.profiler.stop_monitoring()
        
        status = "enabled" if enabled else "disabled"
        self.status_bar.showMessage(f"Performance monitoring {status}")
    
    def _reset_performance_stats(self):
        """Reset performance statistics."""
        reply = QMessageBox.question(self, "Reset Performance Statistics", 
                                   "Are you sure you want to reset all performance statistics?")
        
        if reply == QMessageBox.Yes:
            self.profiler.fps_history.clear()
            self.profiler.memory_history.clear()
            self.profiler.cpu_history.clear()
            self.profiler.function_timings.clear()
            self.profiler.session_start_time = time.time()
            self.profiler.total_frames_rendered = 0
            self.profiler.performance_warnings_count = 0
            self.status_bar.showMessage("Performance statistics reset")
    
    def _export_performance_data(self):
        """Export performance data."""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Performance Data", 
            f"performance_data_{int(time.time())}.json",
            "JSON Files (*.json)"
        )
        
        if filename:
            if self.profiler.export_performance_data(filename):
                QMessageBox.information(self, "Export Successful", 
                                      f"Performance data exported to:\n{filename}")
            else:
                QMessageBox.warning(self, "Export Failed", 
                                  "Failed to export performance data.")
    
    def _update_fps_status(self, fps):
        """Update FPS in status bar."""
        color = "green" if fps >= 30 else "orange" if fps >= 20 else "red"
        self.fps_label.setText(f"<font color='{color}'>FPS: {fps:.1f}</font>")
    
    def _update_memory_status(self, memory_mb, memory_percent):
        """Update memory usage in status bar."""
        color = "green" if memory_percent < 70 else "orange" if memory_percent < 85 else "red"
        self.memory_label.setText(f"<font color='{color}'>Mem: {memory_percent:.1f}%</font>")
    
    def _show_performance_warning(self, warning):
        """Show performance warning in status bar."""
        self.status_bar.showMessage(f"⚠️ {warning}", 5000)  # Show for 5 seconds
    
    def closeEvent(self, event):
        """Clean shutdown with performance monitoring cleanup."""
        print("Shutting down application...")
        
        # Stop all systems gracefully
        try:
            if self.midi_handler:
                print("Stopping MIDI handler...")
                self.midi_handler.stop()
        except Exception as e:
            print(f"Error stopping MIDI handler: {e}")
        
        try:
            if self.audio_analyzer:
                print("Stopping audio analyzer...")
                self.audio_analyzer.stop()
        except Exception as e:
            print(f"Error stopping audio analyzer: {e}")
        
        try:
            # Stop performance monitoring
            print("Stopping performance monitoring...")
            self.profiler.stop_monitoring()
        except Exception as e:
            print(f"Error stopping performance monitoring: {e}")
        
        try:
            # Stop timers
            self.cleanup_timer.stop()
            self.render_timer.stop()
        except Exception as e:
            print(f"Error stopping timers: {e}")
        
        try:
            # Close dialogs if open
            if self.performance_dialog:
                self.performance_dialog.close()
            
            if self.config_dialog:
                self.config_dialog.close()
            
            if self.scene_config_dialog:
                self.scene_config_dialog.close()
        except Exception as e:
            print(f"Error closing dialogs: {e}")
        
        print("Application shutdown complete")
        event.accept()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    app = QApplication(sys.argv)
    
    window = PerformanceAwareMainWindow()
    window.resize(1000, 700)
    window.show()
    
    sys.exit(app.exec())
