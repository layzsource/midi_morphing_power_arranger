#!/usr/bin/env python3
"""
Enhanced MIDI Morphing Visualizer - Step 4: Complete Geometric Library with Real Morphing
CLEAN VERSION - No formatting issues

INSTALLATION:
pip install pyvistaqt PySide6 pyvista numpy librosa sounddevice pygame psutil
"""

import sys
import os
import time
import traceback
import numpy as np
import pyvista as pv
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sounddevice as sd
import pygame.midi
from collections import deque
import psutil

# Handle PyVista Qt integration
try:
    from pyvistaqt import QtInteractor
    print("✅ Using pyvistaqt.QtInteractor")
    QTINTERACTOR_AVAILABLE = True
except ImportError:
    try:
        from pyvista.plotting.qt_plotting import QtInteractor
        print("✅ Using legacy pyvista QtInteractor")
        QTINTERACTOR_AVAILABLE = True
    except ImportError:
        print("❌ QtInteractor not available")
        QTINTERACTOR_AVAILABLE = False
        QtInteractor = None

class GeometryLibrary:
    """Complete geometric library with vertex-level morphing capability"""
    
    def __init__(self, resolution=20):
        self.resolution = resolution
        self.base_meshes = {}
        self.shape_names = ['sphere', 'cube', 'cone', 'cylinder']
        self._create_initial_meshes()
    
    def _create_initial_meshes(self):
        """Create initial meshes with compatible vertex counts for morphing"""
        try:
            # Start with sphere as base
            sphere = pv.Sphere(radius=1.0, phi_resolution=self.resolution, theta_resolution=self.resolution)
            target_vertex_count = sphere.n_points
            print(f"Creating meshes with target vertex count: {target_vertex_count}")
            
            # Store sphere
            self.base_meshes['sphere'] = sphere
            
            # Create other shapes - simplified for reliability
            self.base_meshes['cube'] = self._create_simple_cube(target_vertex_count)
            self.base_meshes['cone'] = self._create_simple_cone(target_vertex_count)  
            self.base_meshes['cylinder'] = self._create_simple_cylinder(target_vertex_count)
            
            # Verify all have same vertex count
            for name, mesh in self.base_meshes.items():
                print(f"✅ {name}: {mesh.n_points} vertices")
                
        except Exception as e:
            print(f"Error creating initial meshes: {e}")
            self._create_fallback_meshes()
    
    def _create_simple_cube(self, target_count):
        """Create cube by deforming sphere"""
        sphere = self.base_meshes['sphere']
        points = sphere.points.copy()
        
        # Deform sphere into cube
        for i, point in enumerate(points):
            x, y, z = point
            # Project to cube surface
            max_coord = max(abs(x), abs(y), abs(z))
            if max_coord > 0:
                points[i] = point * (1.0 / max_coord)
        
        return pv.PolyData(points, sphere.faces)
    
    def _create_simple_cone(self, target_count):
        """Create cone by deforming sphere"""
        sphere = self.base_meshes['sphere']
        points = sphere.points.copy()
        
        # Deform sphere into cone
        for i, point in enumerate(points):
            x, y, z = point
            # Cone formula: radius decreases with height
            height_factor = (z + 1) / 2  # Normalize z to 0-1
            radius_factor = 1.0 - height_factor * 0.8
            points[i] = [x * radius_factor, y * radius_factor, z]
        
        return pv.PolyData(points, sphere.faces)
    
    def _create_simple_cylinder(self, target_count):
        """Create cylinder by deforming sphere"""
        sphere = self.base_meshes['sphere']
        points = sphere.points.copy()
        
        # Deform sphere into cylinder
        for i, point in enumerate(points):
            x, y, z = point
            # Normalize x,y to unit circle, keep z
            r = np.sqrt(x**2 + y**2)
            if r > 0:
                points[i] = [x/r, y/r, z]
        
        return pv.PolyData(points, sphere.faces)
    
    def _create_fallback_meshes(self):
        """Create fallback meshes if main creation fails"""
        sphere = pv.Sphere(radius=1.0, phi_resolution=10, theta_resolution=10)
        self.base_meshes['sphere'] = sphere
        
        for shape_name in ['cube', 'cone', 'cylinder']:
            self.base_meshes[shape_name] = sphere
    
    def blend_meshes(self, source_key, target_key, alpha):
        """Blend between two meshes - REAL MORPHING"""
        if source_key not in self.base_meshes or target_key not in self.base_meshes:
            return self.base_meshes.get('sphere')
        
        source_mesh = self.base_meshes[source_key]
        target_mesh = self.base_meshes[target_key]
        
        if source_mesh.n_points != target_mesh.n_points:
            return source_mesh
        
        # Linear interpolation between vertex positions
        source_points = source_mesh.points
        target_points = target_mesh.points
        blended_points = (1 - alpha) * source_points + alpha * target_points
        
        # Create new mesh with blended points
        return pv.PolyData(blended_points, source_mesh.faces)
    
    def get_shape_names(self):
        return list(self.base_meshes.keys())
    
    def get_mesh(self, shape_name):
        return self.base_meshes.get(shape_name)

class MorphingSceneObject:
    """Scene object with REAL vertex-level morphing"""
    
    def __init__(self, name, position, note_range, color, geometry_lib):
        self.name = name
        self.position = np.array(position)
        self.note_range = note_range
        self.base_color = np.array(color)
        self.current_color = self.base_color.copy()
        self.geometry_lib = geometry_lib
        
        # Morphing state
        self.current_shape = 'sphere'
        self.target_shape = 'sphere'
        self.morph_progress = 0.0
        self.morph_speed = 1.0
        
        # Object state
        self.active_notes = set()
        self.velocity = 0.0
        self.opacity = 0.8
        
        # 3D objects
        self.mesh = None
        self.actor = None
        
        self._update_mesh()
    
    def set_target_shape(self, target_shape, morph_speed=1.0):
        """Set target shape for morphing"""
        if target_shape in self.geometry_lib.get_shape_names():
            if target_shape != self.target_shape:
                self.current_shape = self.target_shape
                self.target_shape = target_shape
                self.morph_progress = 0.0
                self.morph_speed = morph_speed
                print(f"{self.name}: Morphing {self.current_shape} -> {target_shape}")
    
    def update_morphing(self, dt):
        """Update morphing animation"""
        if self.current_shape != self.target_shape:
            self.morph_progress += dt * self.morph_speed
            
            if self.morph_progress >= 1.0:
                self.morph_progress = 1.0
                self.current_shape = self.target_shape
                print(f"{self.name}: Morphing complete -> {self.current_shape}")
            
            self._update_mesh()
    
    def _update_mesh(self):
        """Update mesh based on current morphing state"""
        try:
            if self.current_shape == self.target_shape:
                self.mesh = self.geometry_lib.get_mesh(self.current_shape).copy()
            else:
                self.mesh = self.geometry_lib.blend_meshes(
                    self.current_shape, 
                    self.target_shape, 
                    self.morph_progress
                )
            
            if self.mesh:
                self.mesh.translate(self.position)
                
        except Exception as e:
            print(f"Error updating mesh for {self.name}: {e}")
            self.mesh = self.geometry_lib.get_mesh('sphere')
            if self.mesh:
                self.mesh = self.mesh.copy()
                self.mesh.translate(self.position)
    
    def add_note(self, note, velocity):
        """Add a MIDI note"""
        self.active_notes.add(note)
        self.velocity = max(self.velocity, velocity / 127.0)
        self._update_visual_properties()
    
    def remove_note(self, note):
        """Remove a MIDI note"""
        if note in self.active_notes:
            self.active_notes.remove(note)
        
        if not self.active_notes:
            self.velocity = 0.0
        
        self._update_visual_properties()
    
    def _update_visual_properties(self):
        """Update visual properties"""
        if self.active_notes:
            import colorsys
            avg_note = sum(self.active_notes) / len(self.active_notes)
            note_factor = (avg_note - self.note_range[0]) / (self.note_range[1] - self.note_range[0])
            note_factor = max(0.0, min(1.0, note_factor))
            
            r, g, b = self.base_color
            h, s, v = colorsys.rgb_to_hsv(r, g, b)
            h = (h + note_factor * 0.3) % 1.0
            self.current_color = np.array(colorsys.hsv_to_rgb(h, s, v))
            self.opacity = 0.6 + (self.velocity * 0.4)
        else:
            self.opacity = max(0.2, self.opacity * 0.98)
            self.current_color = self.base_color.copy()

class MorphingSceneManager(QObject):
    """Scene manager with real vertex-level morphing"""
    
    scene_updated = Signal()
    object_count_changed = Signal(int)
    
    def __init__(self, plotter):
        super().__init__()
        self.plotter = plotter
        self.objects = {}
        self.geometry_lib = GeometryLibrary(resolution=20)
        
        self.global_morph_factor = 0.0
        self.morph_sequence = ['sphere', 'cube', 'cone', 'cylinder']
        
        self._setup_scene_objects()
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_scene)
        self.update_timer.start(16)
    
    def _setup_scene_objects(self):
        """Setup morphing scene objects"""
        try:
            object_configs = [
                ("Bass Morpher", (-2, -1, 0), (24, 47), [0.2, 0.4, 1.0]),
                ("Melody Morpher", (0, 0, 0), (48, 71), [0.2, 1.0, 0.4]),
                ("Treble Morpher", (2, 1, 0), (72, 95), [1.0, 0.6, 0.2]),
                ("High Morpher", (0, 2.5, 0), (96, 108), [1.0, 0.2, 1.0])
            ]
            
            for name, position, note_range, color in object_configs:
                obj = MorphingSceneObject(name, position, note_range, color, self.geometry_lib)
                self.objects[name] = obj
            
            print(f"✅ Created {len(self.objects)} morphing objects")
            self.object_count_changed.emit(len(self.objects))
            
        except Exception as e:
            print(f"Error setting up objects: {e}")
    
    def _update_scene(self):
        """Update the morphing scene"""
        try:
            if not self.plotter:
                return
            
            dt = 0.016
            
            for obj in self.objects.values():
                obj.update_morphing(dt)
                
                if obj.mesh:
                    try:
                        if obj.actor:
                            self.plotter.remove_actor(obj.actor)
                        
                        obj.actor = self.plotter.add_mesh(
                            obj.mesh,
                            color=obj.current_color,
                            opacity=obj.opacity,
                            lighting=True
                        )
                        
                    except Exception as e:
                        print(f"Error updating visualization for {obj.name}: {e}")
            
            self.scene_updated.emit()
            
        except Exception as e:
            print(f"Scene update error: {e}")
    
    def set_global_morph_factor(self, factor):
        """Set global morphing factor"""
        self.global_morph_factor = max(0.0, min(1.0, factor))
        
        if len(self.morph_sequence) > 0:
            shape_index = int(factor * (len(self.morph_sequence) - 1))
            target_shape = self.morph_sequence[shape_index]
            
            for obj in self.objects.values():
                obj.set_target_shape(target_shape, morph_speed=2.0)
    
    def handle_midi_note_on(self, note, velocity, channel):
        """Handle MIDI note on"""
        for obj in self.objects.values():
            if obj.note_range[0] <= note <= obj.note_range[1]:
                obj.add_note(note, velocity)
                shape_index = (note - obj.note_range[0]) % len(self.morph_sequence)
                target_shape = self.morph_sequence[shape_index]
                obj.set_target_shape(target_shape)
                break
    
    def handle_midi_note_off(self, note, channel):
        """Handle MIDI note off"""
        for obj in self.objects.values():
            if obj.note_range[0] <= note <= obj.note_range[1]:
                obj.remove_note(note)
                break
    
    def handle_midi_cc(self, cc_number, value, channel):
        """Handle MIDI control change"""
        if cc_number == 1:
            self.set_global_morph_factor(value / 127.0)
    
    def reset_scene(self):
        """Reset scene"""
        for obj in self.objects.values():
            obj.active_notes.clear()
            obj.velocity = 0.0
            obj.set_target_shape('sphere')
        self.global_morph_factor = 0.0

class SimplePerformanceMonitor(QObject):
    performance_update = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_performance)
        self.update_timer.start(1000)
    
    def register_frame(self):
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def _update_performance(self):
        try:
            memory_percent = psutil.virtual_memory().percent
            cpu_percent = psutil.cpu_percent()
            
            perf_data = {
                'fps': self.current_fps,
                'memory_percent': memory_percent,
                'cpu_percent': cpu_percent
            }
            
            self.performance_update.emit(perf_data)
        except Exception as e:
            print(f"Performance error: {e}")

class SimpleAudioAnalyzer(QObject):
    audio_features_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.audio_buffer = deque(maxlen=self.buffer_size * 4)
        self.stream = None
        self.analysis_enabled = True
        
        self._init_audio_stream()
    
    def _init_audio_stream(self):
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.buffer_size,
                callback=self._audio_callback
            )
            self.stream.start()
            print("✅ Audio analyzer initialized")
        except Exception as e:
            print(f"❌ Audio error: {e}")
    
    def _audio_callback(self, indata, frames, time, status):
        if not self.analysis_enabled:
            return
        
        audio_data = indata[:, 0] if len(indata.shape) > 1 else indata
        self.audio_buffer.extend(audio_data)
        
        if len(self.audio_buffer) >= self.buffer_size:
            self._analyze_audio()
    
    def _analyze_audio(self):
        try:
            audio_data = np.array(list(self.audio_buffer)[-self.buffer_size:])
            rms = np.sqrt(np.mean(audio_data**2))
            
            features = {
                'rms': rms,
                'audio_data': audio_data
            }
            
            self.audio_features_updated.emit(features)
        except Exception as e:
            print(f"Audio analysis error: {e}")
    
    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()

class SimpleMIDIHandler(QObject):
    note_on = Signal(int, int, int)
    note_off = Signal(int, int)
    control_change = Signal(int, int, int)
    
    def __init__(self):
        super().__init__()
        self.midi_input = None
        self.polling_timer = QTimer()
        self.polling_timer.timeout.connect(self._poll_midi)
        
        self._init_midi()
    
    def _init_midi(self):
        try:
            pygame.midi.init()
            device_count = pygame.midi.get_count()
            print(f"Found {device_count} MIDI devices")
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                if info[2]:
                    try:
                        self.midi_input = pygame.midi.Input(i)
                        print(f"✅ Connected to MIDI device: {info[1].decode()}")
                        self.polling_timer.start(10)
                        break
                    except Exception as e:
                        print(f"Failed to connect to device {i}: {e}")
            
            if not self.midi_input:
                print("⚠️ No MIDI input devices found")
        except Exception as e:
            print(f"❌ MIDI error: {e}")
    
    def _poll_midi(self):
        try:
            if self.midi_input and self.midi_input.poll():
                midi_events = self.midi_input.read(10)
                for event in midi_events:
                    self._process_midi_event(event[0])
        except Exception as e:
            print(f"MIDI polling error: {e}")
    
    def _process_midi_event(self, event):
        try:
            status, note, velocity, _ = event
            channel = status & 0x0F
            message_type = status & 0xF0
            
            if message_type == 0x90:
                if velocity > 0:
                    self.note_on.emit(note, velocity, channel)
                else:
                    self.note_off.emit(note, channel)
            elif message_type == 0x80:
                self.note_off.emit(note, channel)
            elif message_type == 0xB0:
                self.control_change.emit(note, velocity, channel)
        except Exception as e:
            print(f"MIDI event error: {e}")
    
    def stop(self):
        if self.polling_timer.isActive():
            self.polling_timer.stop()
        if self.midi_input:
            self.midi_input.close()
        pygame.midi.quit()

class Step4MorphingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Step 4: Real Geometric Morphing")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize systems
        self.performance_monitor = SimplePerformanceMonitor()
        self.audio_analyzer = SimpleAudioAnalyzer()
        self.midi_handler = SimpleMIDIHandler()
        
        self.global_morph_factor = 0.0
        self.audio_reactive_enabled = True
        
        # Setup UI
        self._setup_ui()
        
        # Initialize scene manager
        if hasattr(self, 'plotter') and self.plotter:
            self.scene_manager = MorphingSceneManager(self.plotter)
        else:
            self.scene_manager = None
        
        # Connect signals
        self._connect_signals()
        
        self.statusBar().showMessage("Step 4: Real Geometric Morphing Ready!")
        print("✅ Step 4 initialized with REAL vertex morphing")
    
    def _setup_ui(self):
        """Setup UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # 3D Visualization
        if QTINTERACTOR_AVAILABLE:
            try:
                self.plotter = QtInteractor(parent=self)
                self.plotter.background_color = "black"
                self.plotter.show_axes()
                
                main_layout.addWidget(self.plotter, stretch=3)
                print("✅ 3D visualization created")
            except Exception as e:
                print(f"❌ 3D error: {e}")
                fallback_label = QLabel("3D Error\nInstall pyvistaqt")
                fallback_label.setStyleSheet("background-color: black; color: red; font-size: 16px;")
                fallback_label.setAlignment(Qt.AlignCenter)
                main_layout.addWidget(fallback_label, stretch=3)
                self.plotter = None
        else:
            fallback_label = QLabel("3D Unavailable\nInstall: pip install pyvistaqt")
            fallback_label.setStyleSheet("background-color: black; color: red; font-size: 16px;")
            fallback_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(fallback_label, stretch=3)
            self.plotter = None
        
        # Control Panel
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)
    
    def _create_control_panel(self):
        """Create control panel"""
        panel = QWidget()
        panel.setMaximumWidth(350)
        panel.setStyleSheet("""
            QWidget { 
                background-color: #2b2b2b; 
                color: white; 
                font-family: Arial;
            }
            QGroupBox { 
                font-weight: bold; 
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        
        layout = QVBoxLayout(panel)
        
        # Title
        title_label = QLabel("🎭 STEP 4: Real Morphing")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Morphing Controls
        morph_group = QGroupBox("Real Vertex-Level Morphing")
        morph_layout = QVBoxLayout(morph_group)
        
        morph_layout.addWidget(QLabel("Global Morphing Factor:"))
        self.global_morph_slider = QSlider(Qt.Horizontal)
        self.global_morph_slider.setRange(0, 100)
        self.global_morph_slider.setValue(0)
        self.global_morph_slider.valueChanged.connect(self._on_global_morph_changed)
        morph_layout.addWidget(self.global_morph_slider)
        
        self.morph_value_label = QLabel("Morph: 0% (Sphere)")
        self.morph_value_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        morph_layout.addWidget(self.morph_value_label)
        
        sequence_label = QLabel("Sequence: Sphere → Cube → Cone → Cylinder")
        sequence_label.setWordWrap(True)
        sequence_label.setStyleSheet("font-size: 10px; color: #aaa;")
        morph_layout.addWidget(sequence_label)
        
        layout.addWidget(morph_group)
        
        # Audio Reactive
        audio_group = QGroupBox("Audio-Reactive Morphing")
        audio_layout = QVBoxLayout(audio_group)
        
        self.audio_reactive_checkbox = QCheckBox("🎵 Enable Audio-Reactive")
        self.audio_reactive_checkbox.setChecked(True)
        self.audio_reactive_checkbox.toggled.connect(self._on_audio_reactive_toggled)
        audio_layout.addWidget(self.audio_reactive_checkbox)
        
        layout.addWidget(audio_group)
        
        # Shape Selection
        # Shape Selection
        shape_group = QGroupBox("Direct Shape Selection")
        shape_layout = QVBoxLayout(shape_group)
        
        shape_buttons = [
            ("Sphere", "sphere"),
            ("Cube", "cube"), 
            ("Cone", "cone"),
            ("Cylinder", "cylinder")
        ]
        
        for i, (name, shape_key) in enumerate(shape_buttons):
            if i % 2 == 0:
                button_row = QHBoxLayout()
                shape_layout.addLayout(button_row)
            
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, s=shape_key: self._morph_to_shape(s))
            button_row.addWidget(btn)
        
        layout.addWidget(shape_group)
        
        # Performance Monitor
        perf_group = QGroupBox("📊 Performance Monitor")
        perf_layout = QVBoxLayout(perf_group)
        
        self.fps_label = QLabel("FPS: --")
        self.memory_label = QLabel("Memory: --%")
        self.cpu_label = QLabel("CPU: --%")
        self.status_3d_label = QLabel("3D Status: Working" if self.plotter else "3D Status: Error")
        
        perf_layout.addWidget(self.fps_label)
        perf_layout.addWidget(self.memory_label)
        perf_layout.addWidget(self.cpu_label)
        perf_layout.addWidget(self.status_3d_label)
        
        layout.addWidget(perf_group)
        
        # Test Controls
        test_group = QGroupBox("🧪 Test Real Morphing")
        test_layout = QVBoxLayout(test_group)
        
        self.test_morph_btn = QPushButton("Test Shape Sequence")
        self.test_audio_btn = QPushButton("Test Audio-Reactive")
        self.test_midi_btn = QPushButton("Test MIDI Morphing")
        self.reset_btn = QPushButton("🔄 Reset to Sphere")
        
        self.test_morph_btn.clicked.connect(self._test_morphing)
        self.test_audio_btn.clicked.connect(self._test_audio_reactive)
        self.test_midi_btn.clicked.connect(self._test_midi_morphing)
        self.reset_btn.clicked.connect(self._reset_all)
        
        test_layout.addWidget(self.test_morph_btn)
        test_layout.addWidget(self.test_audio_btn)
        test_layout.addWidget(self.test_midi_btn)
        test_layout.addWidget(self.reset_btn)
        
        layout.addWidget(test_group)
        
        # Info
        info_group = QGroupBox("ℹ️ Step 4 Features")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QLabel("""
REAL VERTEX-LEVEL MORPHING:
• Shapes actually transform geometry
• Smooth vertex interpolation
• Multiple morph targets
• MIDI note triggering
• Audio-reactive morphing
• Real-time animation

Try the Global Morphing slider
or MIDI notes to see REAL 
shape transformations!
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 10px; padding: 5px;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        return panel
    
    def _connect_signals(self):
        """Connect signals"""
        self.performance_monitor.performance_update.connect(self._update_performance_display)
        self.audio_analyzer.audio_features_updated.connect(self._handle_audio_features)
        
        if self.scene_manager:
            self.midi_handler.note_on.connect(self.scene_manager.handle_midi_note_on)
            self.midi_handler.note_off.connect(self.scene_manager.handle_midi_note_off)
            self.midi_handler.control_change.connect(self.scene_manager.handle_midi_cc)
            self.scene_manager.scene_updated.connect(self.performance_monitor.register_frame)
    
    def _on_global_morph_changed(self, value):
        """Handle global morph slider change"""
        self.global_morph_factor = value / 100.0
        
        if self.scene_manager:
            self.scene_manager.set_global_morph_factor(self.global_morph_factor)
        
        shape_names = ['Sphere', 'Cube', 'Cone', 'Cylinder']
        shape_index = int(self.global_morph_factor * (len(shape_names) - 1))
        current_shape = shape_names[shape_index]
        
        self.morph_value_label.setText(f"Morph: {value}% ({current_shape})")
        print(f"Global morph: {self.global_morph_factor:.2f} -> {current_shape}")
    
    def _on_audio_reactive_toggled(self, checked):
        """Handle audio reactive toggle"""
        self.audio_reactive_enabled = checked
        self.audio_analyzer.analysis_enabled = checked
        status = "Enabled" if checked else "Disabled"
        print(f"Audio-reactive morphing: {status}")
        self.statusBar().showMessage(f"Audio-reactive: {status}", 2000)
    
    def _morph_to_shape(self, shape_key):
        """Morph all objects to specific shape"""
        if self.scene_manager:
            for obj in self.scene_manager.objects.values():
                obj.set_target_shape(shape_key, morph_speed=3.0)
            print(f"Morphing all objects to: {shape_key}")
            self.statusBar().showMessage(f"Morphing to {shape_key}...", 2000)
    
    def _handle_audio_features(self, features):
        """Handle audio features"""
        if not self.audio_reactive_enabled:
            return
        
        try:
            rms = features.get('rms', 0.0)
            
            if rms > 0.001:
                morph_value = min(100, int(rms * 5000))
                if morph_value > 5:
                    self.global_morph_slider.setValue(morph_value)
                
        except Exception as e:
            print(f"Error in audio reactive: {e}")
    
    def _update_performance_display(self, perf_data):
        """Update performance display"""
        fps = perf_data.get('fps', 0)
        memory_percent = perf_data.get('memory_percent', 0)
        cpu_percent = perf_data.get('cpu_percent', 0)
        
        if fps >= 30:
            fps_color = 'green'
        elif fps >= 20:
            fps_color = 'orange'
        else:
            fps_color = 'red'
        
        self.fps_label.setText(f'<span style="color: {fps_color}">FPS: {fps}</span>')
        self.memory_label.setText(f"Memory: {memory_percent:.1f}%")
        self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")
        
        self.performance_monitor.register_frame()
    
    def _test_morphing(self):
        """Test real morphing"""
        print("Testing real vertex-level morphing...")
        self.statusBar().showMessage("Testing shape sequence - watch the real morphing!", 6000)
        
        shapes = ['sphere', 'cube', 'cone', 'cylinder', 'sphere']
        
        for i, shape in enumerate(shapes):
            QTimer.singleShot(i * 1200, lambda s=shape: self._morph_to_shape(s))
    
    def _test_audio_reactive(self):
        """Test audio-reactive morphing"""
        self.audio_reactive_checkbox.setChecked(True)
        print("Audio-reactive morphing enabled - make sounds!")
        self.statusBar().showMessage("Audio-reactive test - make noise to see morphing!", 5000)
    
    def _test_midi_morphing(self):
        """Test MIDI morphing"""
        print("Testing MIDI morphing...")
        test_notes = [36, 48, 60, 72, 84, 96]
        
        for i, note in enumerate(test_notes):
            QTimer.singleShot(i * 1500, 
                lambda n=note: self.scene_manager.handle_midi_note_on(n, 100, 0) if self.scene_manager else None)
        
        self.statusBar().showMessage("Playing test MIDI notes - each triggers shape changes!", 9000)
    
    def _reset_all(self):
        """Reset everything"""
        self.global_morph_slider.setValue(0)
        self.audio_reactive_checkbox.setChecked(True)
        
        if self.scene_manager:
            self.scene_manager.reset_scene()
        
        print("Reset - all objects back to spheres")
        self.statusBar().showMessage("Reset - morphing back to spheres", 3000)
    
    def closeEvent(self, event):
        """Cleanup"""
        print("Closing Step 4 Real Morphing Visualizer...")
        
        try:
            if hasattr(self, 'audio_analyzer'):
                self.audio_analyzer.stop()
            
            if hasattr(self, 'midi_handler'):
                self.midi_handler.stop()
            
            if hasattr(self, 'performance_monitor') and hasattr(self.performance_monitor, 'update_timer'):
                self.performance_monitor.update_timer.stop()
            
            if hasattr(self, 'scene_manager') and hasattr(self.scene_manager, 'update_timer'):
                self.scene_manager.update_timer.stop()
            
            if hasattr(self, 'plotter') and self.plotter:
                try:
                    self.plotter.clear()
                except:
                    pass
                
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Step 4: Real Geometric Morphing")
    app.setOrganizationName("MIDI Morphing Systems")
    
    window = Step4MorphingWindow()
    window.show()
    
    print("🚀 Step 4: Real Geometric Morphing Started!")
    print("=" * 70)
    print("✅ STEP 4 FEATURES:")
    print("   🎭 REAL vertex-level morphing between shapes")
    print("   🔄 Smooth geometric transitions")
    print("   📐 4 shape library (Sphere, Cube, Cone, Cylinder)")
    print("   🎵 Audio-reactive morphing")
    print("   🎹 MIDI-triggered transformations")
    print("   ⚡ Real-time morphing animations")
    print("=" * 70)
    print("🎮 CONTROLS:")
    print("   • Global Morphing Slider: Morphs through shape sequence")
    print("   • Direct Shape Buttons: Instant morph to specific shapes")
    print("   • Audio-Reactive: Sound-driven morphing")
    print("   • MIDI Notes: Different ranges trigger different objects")
    print("=" * 70)
    print("🎯 TEST THE REAL MORPHING:")
    print("   1. Move 'Global Morphing Factor' slider - see REAL shapes!")
    print("   2. Click 'Test Shape Sequence' for automated morphing")
    print("   3. Try shape buttons (Sphere, Cube, Cone, Cylinder)")
    print("   4. Enable 'Audio-Reactive' and make sounds")
    print("   5. Play MIDI notes to trigger shape changes")
    print("=" * 70)
    print("🔍 EXPECT:")
    print("   • 4 objects that ACTUALLY change shape geometry")
    print("   • Smooth vertex-level morphing animations")
    print("   • Real geometric transformations in 3D")
    print("   • MIDI/audio triggering actual shape changes")
    print("=" * 70)
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print("🚨 EXCEPTION:")
        print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
    sys.excepthook = handle_exception
    
    try:
        exit_code = app.exec()
        print("\n👋 Step 4 Real Morphing Closed")
        return exit_code
    except Exception as e:
        print(f"🚨 Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
