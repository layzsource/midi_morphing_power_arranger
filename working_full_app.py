#!/usr/bin/env python3
"""
Complete MIDI Morphing Visualizer - Full Featured Version
Working version with all advanced features and FIXED color handling.
"""

import sys
import os
import logging
import time
import threading
import colorsys
import numpy as np
import queue
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# FIXED: Import safe color utilities
from color_utils import safe_hsv_to_rgb, safe_color_array, blend_colors_safe

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core dependencies
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox,
        QMenuBar, QMenu, QHBoxLayout, QGroupBox, QGridLayout, QTabWidget,
        QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar
    )
    from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject
    from PySide6.QtGui import QAction, QFont
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✓ Core GUI dependencies available")
except ImportError as e:
    print(f"✗ Missing core dependencies: {e}")
    sys.exit(1)

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
    print("✓ Audio analysis available")
except ImportError:
    print("⚠ Audio analysis not available")

try:
    import psutil
    PERFORMANCE_MONITORING = True
    print("✓ Performance monitoring available")
except ImportError:
    PERFORMANCE_MONITORING = False
    print("⚠ Performance monitoring not available")

class Config:
    def __init__(self):
        # Core settings
        self.MESH_RESOLUTION = 25
        self.MIDI_PORT = None
        self.AUDIO_SAMPLE_RATE = 44100
        self.AUDIO_CHUNK_SIZE = 512
        self.AUDIO_ONSET_THRESHOLD = 1.5
        
        # Audio settings
        self.AUDIO_ENABLED = True
        self.AUDIO_DEVICE_INDEX = None
        self.AUDIO_CHANNELS = 1
        self.AUDIO_COLOR_STRENGTH = 1.0
        self.AUDIO_MORPH_STRENGTH = 0.2
        
        # MIDI settings
        self.VELOCITY_SENSITIVITY = 1.0
        self.NOTE_MIN = 0
        self.NOTE_MAX = 127
        self.MORPH_CC = 1
        self.NOTE_TIMEOUT = 60
        self.MIDI_CHANNEL = 0
        
        # Performance settings
        self.TARGET_FPS = 60
        self.CLEANUP_INTERVAL = 5
        self.FPS_WARNING = 30
        self.MEMORY_WARNING = 80
        self.CPU_WARNING = 85
        self.ENABLE_PROFILING = True
        self.FLASH_DURATION = 150

def create_perfectly_matched_meshes(resolution=25):
    """Create meshes with identical vertex counts for perfect morphing."""
    sphere = pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution)
    
    # Create meshes by modifying the sphere to ensure identical vertex counts
    meshes = {}
    
    # Sphere (baseline)
    meshes["sphere"] = sphere.copy()
    
    # Cube (quantize sphere points)
    cube_points = sphere.points.copy()
    for i in range(len(cube_points)):
        for j in range(3):
            cube_points[i][j] = np.sign(cube_points[i][j]) * 0.8
    
    cube = sphere.copy()
    cube.points = cube_points
    meshes["cube"] = cube
    
    # Cone (project points toward apex)
    cone_points = sphere.points.copy()
    for i in range(len(cone_points)):
        x, y, z = cone_points[i]
        height_factor = (z + 1) / 2
        scale = height_factor * 0.7 + 0.1
        cone_points[i] = [x * scale, y * scale, z]
    
    cone = sphere.copy()
    cone.points = cone_points
    meshes["cone"] = cone
    
    # Torus (project to torus surface)
    torus_points = sphere.points.copy()
    major_radius = 0.8
    minor_radius = 0.3
    
    for i in range(len(torus_points)):
        x, y, z = torus_points[i]
        
        # Convert to cylindrical coordinates
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)
        
        # Project to torus
        if r > 0:
            new_r = major_radius + minor_radius * z
            torus_points[i] = [new_r * np.cos(theta), new_r * np.sin(theta), minor_radius * (r - 0.5)]
    
    torus = sphere.copy()
    torus.points = torus_points
    meshes["torus"] = torus
    
    # Icosahedron (quantize to icosahedral directions)
    ico_points = sphere.points.copy()
    normals = ico_points / np.linalg.norm(ico_points, axis=1)[:, np.newaxis]
    quantized = np.round(normals * 3) / 3
    quantized = quantized / np.linalg.norm(quantized, axis=1)[:, np.newaxis]
    
    icosahedron = sphere.copy()
    icosahedron.points = quantized
    meshes["icosahedron"] = icosahedron
    
    # Verify all meshes have identical vertex counts
    base_count = sphere.n_points
    for name, mesh in meshes.items():
        if mesh.n_points != base_count:
            raise ValueError(f"Mesh {name} has {mesh.n_points} vertices, expected {base_count}")
    
    print(f"✓ Created {len(meshes)} perfectly matched meshes with {base_count} vertices each")
    return meshes

def blend_meshes(meshes, source_key, target_key, alpha):
    """Perfect mesh blending for identical vertex count meshes."""
    if source_key not in meshes or target_key not in meshes:
        raise ValueError(f"Mesh keys not found: {source_key}, {target_key}")
    
    source_mesh = meshes[source_key]
    target_mesh = meshes[target_key]
    
    if source_mesh.n_points != target_mesh.n_points:
        raise ValueError(f"Vertex count mismatch: {source_mesh.n_points} vs {target_mesh.n_points}")
    
    source_points = source_mesh.points
    target_points = target_mesh.points
    return (1 - alpha) * source_points + alpha * target_points

# =============================================================================
# Scene Management
# =============================================================================

class LayerBlendMode(Enum):
    NORMAL = "normal"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"

@dataclass
class NoteRange:
    min_note: int
    max_note: int
    name: str = ""
    channel: Optional[int] = None
    
    def contains(self, note: int, channel: int = None) -> bool:
        note_in_range = self.min_note <= note <= self.max_note
        channel_match = self.channel is None or self.channel == channel
        return note_in_range and channel_match

@dataclass
class VisualObject:
    id: str
    shape_type: str
    note_range: NoteRange
    position: np.ndarray
    scale: float = 1.0
    color: np.ndarray = None
    opacity: float = 1.0
    current_morph_target: str = ""
    morph_amount: float = 0.0
    active_notes: Dict[int, dict] = None
    last_activity: float = 0.0
    blend_mode: LayerBlendMode = LayerBlendMode.NORMAL
    depth_layer: int = 0
    
    def __post_init__(self):
        if self.color is None:
            self.color = np.array([0.8, 0.8, 0.8])
        if self.active_notes is None:
            self.active_notes = {}
        self.last_activity = time.time()
    
    def update_from_midi(self, note: int, velocity: float, note_on: bool = True):
        """FIXED: Update from MIDI with safe color handling."""
        if note_on:
            range_span = self.note_range.max_note - self.note_range.min_note
            normalized_note = (note - self.note_range.min_note) / range_span if range_span > 0 else 0.5
            
            hue = normalized_note
            # FIXED: Clamp saturation and brightness to valid range
            saturation = np.clip(0.8 + (velocity * 0.2), 0.0, 1.0)
            brightness = np.clip(0.6 + (velocity * 0.4), 0.0, 1.0)
            
            # FIXED: Use safe conversion
            color = safe_hsv_to_rgb(hue, saturation, brightness)
            
            self.active_notes[note] = {
                'color': color,
                'velocity': velocity,
                'timestamp': time.time()
            }
        else:
            if note in self.active_notes:
                del self.active_notes[note]
        
        self.last_activity = time.time()
        self._update_composite_properties()
    
    def _update_composite_properties(self):
        """FIXED: Update composite properties with safe color handling."""
        if not self.active_notes:
            self.color = safe_color_array([0.5, 0.5, 0.5])
            self.opacity = 0.3
            return
        
        if len(self.active_notes) == 1:
            note_info = next(iter(self.active_notes.values()))
            self.color = safe_color_array(note_info['color'])
            self.opacity = np.clip(0.7 + (note_info['velocity'] * 0.3), 0.0, 1.0)
        else:
            # FIXED: Use safe color blending
            colors = [note_info['color'] for note_info in self.active_notes.values()]
            weights = [note_info['velocity'] for note_info in self.active_notes.values()]
            
            self.color = blend_colors_safe(colors, weights)
            
            # Calculate safe opacity
            total_weight = sum(weights)
            avg_velocity = total_weight / len(self.active_notes) if len(self.active_notes) > 0 else 0.0
            self.opacity = np.clip(0.7 + (avg_velocity * 0.3), 0.0, 1.0)

class SceneManager:
    """Advanced scene manager with multiple objects and note range mapping."""
    
    def __init__(self, initial_meshes, plotter_widget):
        self.initial_meshes = initial_meshes
        self.plotter_widget = plotter_widget
        self.objects: Dict[str, VisualObject] = {}
        self.actors: Dict[str, object] = {}
        self.meshes: Dict[str, object] = {}
        
        # Setup default note range mappings
        self._setup_default_mappings()
    
    def _setup_default_mappings(self):
        """Setup default note range mappings for different octaves."""
        default_mappings = [
            {
                'id': 'bass',
                'note_range': NoteRange(24, 47, "Bass"),
                'shape_type': 'sphere',
                'position': np.array([-2.0, 0.0, 0.0]),
                'scale': 0.8
            },
            {
                'id': 'melody',
                'note_range': NoteRange(48, 71, "Melody"),
                'shape_type': 'cube',
                'position': np.array([0.0, 0.0, 0.0]),
                'scale': 0.8
            },
            {
                'id': 'treble',
                'note_range': NoteRange(72, 95, "Treble"),
                'shape_type': 'cone',
                'position': np.array([2.0, 0.0, 0.0]),
                'scale': 0.8
            },
            {
                'id': 'high',
                'note_range': NoteRange(96, 127, "High"),
                'shape_type': 'torus',
                'position': np.array([0.0, 2.0, 0.0]),
                'scale': 0.6
            }
        ]
        
        for mapping in default_mappings:
            if mapping['shape_type'] in self.initial_meshes:
                self.add_object(**mapping)
    
    def add_object(self, id: str, note_range: NoteRange, shape_type: str, 
                   position: np.ndarray = None, scale: float = 1.0, 
                   depth_layer: int = 0, blend_mode: LayerBlendMode = LayerBlendMode.NORMAL):
        
        if position is None:
            position = np.array([0.0, 0.0, 0.0])
        
        visual_obj = VisualObject(
            id=id,
            shape_type=shape_type,
            note_range=note_range,
            position=position,
            scale=scale,
            depth_layer=depth_layer,
            blend_mode=blend_mode
        )
        
        self.objects[id] = visual_obj
        
        if self.plotter_widget is not None and shape_type in self.initial_meshes:
            mesh = self.initial_meshes[shape_type].copy()
            mesh.points = mesh.points * scale + position
            
            actor_props = {
                'color': visual_obj.color,
                'opacity': visual_obj.opacity,
                'smooth_shading': True
            }
            
            if blend_mode == LayerBlendMode.ADDITIVE:
                actor_props['opacity'] = 0.7
            
            actor = self.plotter_widget.add_mesh(mesh, **actor_props)
            
            self.actors[id] = actor
            self.meshes[id] = mesh
            
            print(f"Added object '{id}' for notes {note_range.min_note}-{note_range.max_note}")
        
        return visual_obj
    
    def handle_midi_note(self, note: int, velocity: float, note_on: bool = True, channel: int = 0):
        affected_objects = []
        
        for obj_id, visual_obj in self.objects.items():
            if visual_obj.note_range.contains(note, channel):
                visual_obj.update_from_midi(note, velocity, note_on)
                affected_objects.append(obj_id)
        
        for obj_id in affected_objects:
            self._update_object_visual(obj_id)
        
        return affected_objects
    
    def _update_object_visual(self, obj_id: str):
        """FIXED: Update object visual with safe color handling."""
        if obj_id not in self.objects or obj_id not in self.actors:
            return
        
        visual_obj = self.objects[obj_id]
        actor = self.actors[obj_id]
        mesh = self.meshes[obj_id]
        
        self.plotter_widget.remove_actor(actor)
        
        # FIXED: Ensure safe color values
        safe_color = safe_color_array(visual_obj.color)
        safe_opacity = np.clip(visual_obj.opacity, 0.0, 1.0)
        
        actor_props = {
            'color': safe_color,
            'opacity': safe_opacity,
            'smooth_shading': True
        }
        
        if visual_obj.blend_mode == LayerBlendMode.ADDITIVE:
            actor_props['opacity'] *= 0.8
        
        new_actor = self.plotter_widget.add_mesh(mesh, **actor_props)
        self.actors[obj_id] = new_actor
    
    def apply_global_morphing(self, target_shape: str, alpha: float):
        """Apply morphing to all objects in the scene."""
        for obj_id, visual_obj in self.objects.items():
            if visual_obj.shape_type in self.initial_meshes and target_shape in self.initial_meshes:
                try:
                    mesh = self.meshes[obj_id]
                    blended_points = blend_meshes(
                        self.initial_meshes,
                        visual_obj.shape_type,
                        target_shape,
                        alpha
                    )
                    
                    # Apply object transformations
                    transformed_points = blended_points * visual_obj.scale + visual_obj.position
                    mesh.points = transformed_points
                    
                    visual_obj.morph_amount = alpha
                    visual_obj.current_morph_target = target_shape
                    
                except Exception as e:
                    print(f"Morphing error for object {obj_id}: {e}")
        
        self.plotter_widget.render()
    
    def cleanup_expired_notes(self, timeout: float = 60.0):
        """Clean up expired notes from all objects."""
        for visual_obj in self.objects.values():
            current_time = time.time()
            expired_notes = [
                note for note, info in visual_obj.active_notes.items()
                if current_time - info['timestamp'] > timeout
            ]
            
            for note in expired_notes:
                del visual_obj.active_notes[note]
            
            if expired_notes:
                visual_obj._update_composite_properties()
        
        # Update visuals for objects that had expired notes
        for obj_id in self.objects.keys():
            self._update_object_visual(obj_id)
    
    def clear_all_notes(self):
        for visual_obj in self.objects.values():
            visual_obj.active_notes.clear()
            visual_obj._update_composite_properties()
        
        for obj_id in self.objects.keys():
            self._update_object_visual(obj_id)
    
    def get_scene_summary(self) -> Dict:
        summary = {
            'total_objects': len(self.objects),
            'active_objects': sum(1 for obj in self.objects.values() if obj.active_notes),
            'total_active_notes': sum(len(obj.active_notes) for obj in self.objects.values()),
            'objects': {}
        }
        
        for obj_id, visual_obj in self.objects.items():
            summary['objects'][obj_id] = {
                'note_range': f"{visual_obj.note_range.min_note}-{visual_obj.note_range.max_note}",
                'active_notes': len(visual_obj.active_notes),
                'shape_type': visual_obj.shape_type,
                'blend_mode': visual_obj.blend_mode.value,
                'depth_layer': visual_obj.depth_layer
            }
        
        return summary

# =============================================================================
# Audio Analysis
# =============================================================================

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
    
    def start(self):
        if not AUDIO_AVAILABLE:
            return False
        
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.running = True
            self.is_active = True
            self.stream.start_stream()
            
            self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
            self.thread.start()
            
            print("✓ Audio analysis started")
            return True
            
        except Exception as e:
            print(f"Audio start failed: {e}")
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
        if self.is_active:
            audio_data = np.frombuffer(in_data, dtype=np.float32)
            try:
                self.audio_queue.put_nowait(audio_data)
            except queue.Full:
                pass
        return (None, pyaudio.paContinue)
    
    def _analysis_loop(self):
        previous_energy = 0.0
        
        while self.running:
            try:
                audio_chunk = self.audio_queue.get(timeout=0.1)
                
                # RMS amplitude
                rms = np.sqrt(np.mean(audio_chunk ** 2))
                self.amplitude_signal.emit(rms)
                
                # Simple onset detection
                energy = np.sum(audio_chunk ** 2)
                if previous_energy > 0:
                    ratio = energy / max(previous_energy, 1e-10)
                    if ratio > self.config.AUDIO_ONSET_THRESHOLD:
                        self.onset_detected_signal.emit(rms)
                
                previous_energy = energy * 0.1 + previous_energy * 0.9
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Audio analysis error: {e}")

# =============================================================================
# MIDI Handler
# =============================================================================

class SimpleMidiHandler(QObject):
    note_on_signal = Signal(int, float, int)  # note, velocity, channel
    note_off_signal = Signal(int, int)  # note, channel
    cc_signal = Signal(int, float, int)  # cc_number, value, channel
    
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
            
            # Find first available input device
            for i in range(pygame.midi.get_count()):
                info = pygame.midi.get_device_info(i)
                if info[2]:  # is_input
                    self.midi_input = pygame.midi.Input(i)
                    device_name = info[1].decode() if isinstance(info[1], bytes) else str(info[1])
                    print(f"✓ Connected to MIDI: {device_name}")
                    
                    self.running = True
                    self.thread = threading.Thread(target=self._midi_loop, daemon=True)
                    self.thread.start()
                    return True
            
            print("No MIDI input devices found")
            return False
            
        except Exception as e:
            print(f"MIDI start failed: {e}")
            return False
    
    def stop(self):
        self.running = False
        if self.midi_input:
            self.midi_input.close()
            self.midi_input = None
        pygame.midi.quit()
    
    def _midi_loop(self):
        while self.running and self.midi_input:
            try:
                if self.midi_input.poll():
                    events = self.midi_input.read(10)
                    for event in events:
                        self._process_midi_event(event[0])
                time.sleep(0.001)
            except Exception as e:
                print(f"MIDI loop error: {e}")
                break
    
    def _process_midi_event(self, event_data):
        status, note, velocity, _ = event_data
        channel = status & 0x0F
        
        if status & 0xF0 == 144 and velocity > 0:  # Note On
            self.note_on_signal.emit(note, velocity / 127.0, channel)
        elif status & 0xF0 == 128 or (status & 0xF0 == 144 and velocity == 0):  # Note Off
            self.note_off_signal.emit(note, channel)
        elif status & 0xF0 == 176:  # Control Change
            self.cc_signal.emit(note, velocity / 127.0, channel)

# =============================================================================
# Performance Monitoring (Simplified)
# =============================================================================

class SimpleProfiler(QObject):
    fps_updated = Signal(float)
    memory_updated = Signal(float, float)
    
    def __init__(self):
        super().__init__()
        self.enabled = PERFORMANCE_MONITORING
        self.frame_times = []
        self.max_frames = 60
        
        if self.enabled:
            self.timer = QTimer()
            self.timer.timeout.connect(self._update_stats)
            self.timer.start(1000)  # Update every second
    
    def start_frame(self):
        if self.enabled:
            self.frame_start_time = time.time()
    
    def end_frame(self):
        if self.enabled and hasattr(self, 'frame_start_time'):
            frame_time = time.time() - self.frame_start_time
            self.frame_times.append(frame_time)
            
            if len(self.frame_times) > self.max_frames:
                self.frame_times.pop(0)
    
    def _update_stats(self):
        if not self.enabled:
            return
        
        # FPS calculation
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            fps = 1.0 / max(avg_frame_time, 1e-6)
            self.fps_updated.emit(fps)
        
        # Memory usage
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_percent = process.memory_percent()
            self.memory_updated.emit(memory_mb, memory_percent)
        except:
            pass

# =============================================================================
# Main Window
# =============================================================================

class FullFeaturedMorphingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.config = Config()
        self.setWindowTitle("MIDI Morphing Visualizer - Full Featured Edition")
        
        # State
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "cube"
        self.audio_color_influence = 0.0
        
        # Initialize systems
        self.scene_manager = None
        self.midi_handler = None
        self.audio_analyzer = None
        self.profiler = SimpleProfiler()
        
        # Initialize UI and systems
        self._initialize_visualization()
        self._setup_ui()
        self._setup_systems()
        self._setup_connections()
        
        # Timers
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_notes)
        self.cleanup_timer.start(self.config.CLEANUP_INTERVAL * 1000)
        
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._on_render_frame)
        self.render_timer.start(16)  # ~60 FPS
        
        print("✓ Full-featured application ready!")
    
    def _initialize_visualization(self):
        self.initial_meshes = create_perfectly_matched_meshes(self.config.MESH_RESOLUTION)
        self.current_mesh = self.initial_meshes[self.current_mesh_key].copy()
    
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 3D Visualization
        self.plotter_widget = QtInteractor(self)
        self.plotter_widget.set_background("black")
        layout.addWidget(self.plotter_widget)
        
        # Initial scene
        self.actor = self.plotter_widget.add_mesh(
            self.current_mesh,
            color=[0.8, 0.8, 0.8],
            smooth_shading=True
        )
        
        # Controls
        controls_layout = QHBoxLayout()
        
        # Morphing controls
        left_controls = QVBoxLayout()
        
        # Target shape
        left_controls.addWidget(QLabel("Target Shape:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(["sphere", "cube", "cone", "icosahedron", "torus"])
        self.target_combo.setCurrentText("cube")
        left_controls.addWidget(self.target_combo)
        
        # Morph slider
        left_controls.addWidget(QLabel("Global Morph:"))
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0
