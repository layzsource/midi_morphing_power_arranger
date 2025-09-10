#!/usr/bin/env python3
"""
Complete MIDI Morphing Visualizer - Full Featured Version
Combines working morphing with all advanced features:
- Scene Manager with multiple objects
- Note range mapping
- Performance monitoring
- Configuration dialogs
- Advanced audio analysis
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

# Configure logging
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

# =============================================================================
# Configuration Classes
# =============================================================================

class MidiConstants:
    """MIDI protocol constants."""
    NOTE_OFF_START = 128
    NOTE_OFF_END = 143
    NOTE_ON_START = 144
    NOTE_ON_END = 159
    CC_START = 176
    CC_END = 191
    MIN_VALUE = 0
    MAX_VALUE = 127
    MODWHEEL_CC = 1

class Config:
    """Comprehensive configuration class."""
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
        self.AUDIO_FFT_SIZE = 2048
        self.AUDIO_HOP_LENGTH = 512
        self.AUDIO_FREQUENCY_RANGE = (80, 8000)
        self.AUDIO_SPECTRAL_ROLLOFF = 0.85
        self.AUDIO_COLOR_STRENGTH = 1.0
        self.AUDIO_MORPH_STRENGTH = 0.2
        
        # MIDI settings
        self.VELOCITY_SENSITIVITY = 1.0
        self.NOTE_MIN = 0
        self.NOTE_MAX = 127
        self.MORPH_CC = 1
        self.NOTE_TIMEOUT = 60
        self.MIDI_CHANNEL = 0
        self.MIDI_AUTO_RECONNECT = True
        
        # Visualization settings
        self.COLOR_SATURATION = 0.8
        self.COLOR_BRIGHTNESS = 1.0
        self.MORPH_SPEED = 1.0
        self.COLOR_TRANSITION_SPEED = 0.5
        self.FLASH_DURATION = 150
        self.SMOOTH_SHADING = True
        self.WIREFRAME_MODE = False
        self.AUTO_ROTATE = False
        self.ROTATION_SPEED = 1.0
        self.DEFAULT_COLOR = [0.8, 0.8, 0.8]
        
        # Performance settings
        self.TARGET_FPS = 60
        self.VSYNC = True
        self.RENDER_QUALITY = "High"
        self.MEMORY_LIMIT = 1000
        self.CLEANUP_INTERVAL = 5
        self.FPS_WARNING = 30
        self.MEMORY_WARNING = 80
        self.CPU_WARNING = 85
        self.ENABLE_PROFILING = True
        self.VERBOSE_LOGGING = False
        self.SHOW_DEBUG_INFO = False
        
        # OSC settings
        self.OSC_IP = "127.0.0.1"
        self.OSC_PORT = 5005
        self.ENABLE_OSC = False

# =============================================================================
# Geometry and Mesh Functions (Working Version)
# =============================================================================

def create_perfectly_matched_meshes(resolution=25):
    """Create meshes with identical vertex counts for perfect morphing."""
    try:
        print(f"Creating perfectly matched meshes with resolution {resolution}...")
        
        # Create base sphere as reference
        sphere = pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution)
        target_points = sphere.n_points
        print(f"Target vertex count: {target_points}")
        
        meshes = {'sphere': sphere}
        
        # Create other shapes and force vertex count match
        shapes_to_create = ['cube', 'cone', 'cylinder']
        
        for shape_name in shapes_to_create:
            try:
                if shape_name == 'cube':
                    base_mesh = pv.Cube()
                elif shape_name == 'cone':
                    base_mesh = pv.Cone(resolution=resolution)
                elif shape_name == 'cylinder':
                    base_mesh = pv.Cylinder(resolution=resolution)
                else:
                    continue
                
                matched_mesh = force_vertex_count_match(base_mesh, target_points)
                if matched_mesh is not None:
                    meshes[shape_name] = matched_mesh
                    print(f"✓ {shape_name}: {matched_mesh.n_points} vertices")
                    
            except Exception as e:
            print(f"Error handling audio amplitude: {e}")
                print(f"✗ Error creating {shape_name}: {e}")
        
        # Create torus by deforming sphere
        try:
            torus = create_torus_from_sphere(sphere)
            if torus.n_points == target_points:
                meshes['torus'] = torus
                print(f"✓ torus: {torus.n_points} vertices")
        except Exception as e:
            print(f"✗ Error creating torus: {e}")
        
        # Create icosahedron
        try:
            icosahedron = create_icosahedron_from_sphere(sphere)
            if icosahedron.n_points == target_points:
                meshes['icosahedron'] = icosahedron
                print(f"✓ icosahedron: {icosahedron.n_points} vertices")
        except Exception as e:
            print(f"✗ Error creating icosahedron: {e}")
        
        # Final verification
        vertex_counts = [mesh.n_points for mesh in meshes.values()]
        if len(set(vertex_counts)) == 1:
            print(f"✅ SUCCESS: All {len(meshes)} meshes have IDENTICAL vertex counts: {vertex_counts[0]}")
        else:
            print(f"⚠ Mixed vertex counts, keeping matched ones only")
            matched_meshes = {name: mesh for name, mesh in meshes.items() 
                            if mesh.n_points == target_points}
            meshes = matched_meshes
        
        return meshes
        
    except Exception as e:
        print(f"Error in mesh creation: {e}")
        return {'sphere': pv.Sphere()}

def force_vertex_count_match(mesh, target_count):
    """Force a mesh to have exactly target_count vertices."""
    try:
        current_count = mesh.n_points
        
        if current_count == target_count:
            return mesh
        
        # Ensure triangulation
        if hasattr(mesh, 'triangulate'):
            mesh = mesh.triangulate()
        
        # Subdivide if needed
        if current_count < target_count:
            while mesh.n_points < target_count * 0.9:
                try:
                    mesh = mesh.subdivide(1)
                    if mesh.n_points >= target_count * 2:
                        break
                except Exception as e:
                    print(f"Subdivision failed: {e}")
                    break
        
        # Decimate if needed
        if mesh.n_points > target_count:
            ratio = target_count / mesh.n_points
            try:
                mesh = mesh.decimate(1 - ratio)
            except Exception as e:
                print(f"Decimation failed: {e}")
                return None
        
        # Accept close matches
        if abs(mesh.n_points - target_count) / target_count < 0.1:
            return mesh
        
        return None
        
    except Exception as e:
        print(f"Force vertex match failed: {e}")
        return None

def create_torus_from_sphere(sphere):
    """Create torus by deforming sphere points."""
    points = sphere.points.copy()
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    
    major_radius = 0.7
    minor_radius = 0.3
    
    new_r = major_radius + minor_radius * np.cos(z * np.pi * 2)
    new_z = minor_radius * np.sin(z * np.pi * 2)
    
    torus_points = np.column_stack([
        new_r * np.cos(theta),
        new_r * np.sin(theta),
        new_z
    ])
    
    torus = sphere.copy()
    torus.points = torus_points
    return torus

def create_icosahedron_from_sphere(sphere):
    """Create icosahedron by projecting sphere to icosahedral faces."""
    points = sphere.points.copy()
    
    # Simple icosahedral approximation by quantizing directions
    normals = points / np.linalg.norm(points, axis=1)[:, np.newaxis]
    quantized = np.round(normals * 4) / 4
    quantized = quantized / np.linalg.norm(quantized, axis=1)[:, np.newaxis]
    
    icosahedron = sphere.copy()
    icosahedron.points = quantized
    return icosahedron

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
        if note_on:
            range_span = self.note_range.max_note - self.note_range.min_note
            normalized_note = (note - self.note_range.min_note) / range_span if range_span > 0 else 0.5
            
            hue = normalized_note
            saturation = 0.8 + (velocity * 0.2)
            brightness = 0.6 + (velocity * 0.4)
            
            color = colorsys.hsv_to_rgb(hue, saturation, brightness)
            
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
        if not self.active_notes:
            self.color = np.array([0.5, 0.5, 0.5])
            self.opacity = 0.3
            return
        
        if len(self.active_notes) == 1:
            note_info = next(iter(self.active_notes.values()))
            self.color = np.array(note_info['color'])
            self.opacity = 0.7 + (note_info['velocity'] * 0.3)
        else:
            total_color = np.array([0.0, 0.0, 0.0])
            total_weight = 0.0
            
            for note_info in self.active_notes.values():
                weight = note_info['velocity']
                color = np.array(note_info['color'])
                total_color += color * weight
                total_weight += weight
            
            if total_weight > 0:
                self.color = total_color / total_weight
                self.opacity = min(0.7 + (total_weight / len(self.active_notes) * 0.3), 1.0)

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
        mappings = [
            {
                'id': 'bass',
                'note_range': NoteRange(21, 47, "Bass (C1-B2)"),
                'shape_type': 'sphere',
                'position': np.array([-2.0, 0.0, 0.0]),
                'scale': 1.5,
                'depth_layer': 1
            },
            {
                'id': 'melody',
                'note_range': NoteRange(48, 72, "Melody (C3-C5)"),
                'shape_type': 'icosahedron' if 'icosahedron' in self.initial_meshes else 'cube',
                'position': np.array([0.0, 0.0, 0.0]),
                'scale': 1.0,
                'depth_layer': 2
            },
            {
                'id': 'treble',
                'note_range': NoteRange(73, 96, "Treble (C#5-C7)"),
                'shape_type': 'cube',
                'position': np.array([2.0, 0.0, 0.0]),
                'scale': 0.7,
                'depth_layer': 3
            },
            {
                'id': 'sparkle',
                'note_range': NoteRange(97, 127, "High (C#7-G9)"),
                'shape_type': 'cone',
                'position': np.array([0.0, 2.0, 0.0]),
                'scale': 0.5,
                'depth_layer': 4,
                'blend_mode': LayerBlendMode.ADDITIVE
            }
        ]
        
        for mapping in mappings:
            # Only create if the shape type exists
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
        if obj_id not in self.objects or obj_id not in self.actors:
            return
        
        visual_obj = self.objects[obj_id]
        actor = self.actors[obj_id]
        mesh = self.meshes[obj_id]
        
        self.plotter_widget.remove_actor(actor)
        
        actor_props = {
            'color': visual_obj.color,
            'opacity': visual_obj.opacity,
            'smooth_shading': True
        }
        
        if visual_obj.blend_mode == LayerBlendMode.ADDITIVE:
            actor_props['opacity'] *= 0.8
        
        new_actor = self.plotter_widget.add_mesh(mesh, **actor_props)
        self.actors[obj_id] = new_actor
    
    def apply_global_morphing(self, target_shape: str, alpha: float):
        """Apply morphing to all objects in the scene."""
        for obj_id, visual_obj in self.objects.items():
            if obj_id in self.meshes and target_shape in self.initial_meshes:
                try:
                    # Get current shape type
                    current_shape = visual_obj.shape_type
                    
                    # Blend between current and target
                    blended_points = blend_meshes(
                        self.initial_meshes,
                        current_shape,
                        target_shape,
                        alpha
                    )
                    
                    # Apply scale and position
                    transformed_points = blended_points * visual_obj.scale + visual_obj.position
                    
                    # Update mesh
                    self.meshes[obj_id].points = transformed_points
                    
                    # Update morph amount
                    visual_obj.morph_amount = alpha
                    visual_obj.current_morph_target = target_shape
                    
                except Exception as e:
                    print(f"Error morphing object {obj_id}: {e}")
        
        # Trigger render
        if self.plotter_widget:
            self.plotter_widget.render()
    
    def cleanup_expired_notes(self, timeout: float = 60.0):
        current_time = time.time()
        for visual_obj in self.objects.values():
            expired_notes = [
                note for note, info in visual_obj.active_notes.items()
                if current_time - info['timestamp'] > timeout
            ]
            
            for note in expired_notes:
                del visual_obj.active_notes[note]
            
            if expired_notes:
                visual_obj._update_composite_properties()
        
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
# MIDI Handler (Enhanced)
# =============================================================================

class EnhancedMidiHandler(QObject):
    note_on_signal = Signal(int, float, int)  # note, velocity, channel
    note_off_signal = Signal(int, int)        # note, channel
    cc_signal = Signal(int, float, int)       # cc, value, channel
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.midi_input = None
        self.running = False
        self.thread = None
        self.midi_initialized = False
        
    def start(self, device_name=None):
        if not MIDI_AVAILABLE:
            return False
            
        try:
            if not self.midi_initialized:
                pygame.midi.init()
                self.midi_initialized = True
            
            device_id = self._find_device(device_name or self.config.MIDI_PORT)
            if device_id is None:
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
                
                if is_input:
                    if preferred_name and preferred_name.lower() in name.lower():
                        return i
                    elif not preferred_name:
                        return i
            
            return None
        except Exception as e:
            print(f"Error finding MIDI device: {e}")
            return None
    
    def _midi_loop(self):
        while self.running and self.midi_input:
            try:
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
    
    def _process_midi_event(self, midi_data):
        if len(midi_data) < 3:
            return
            
        status, data1, data2 = midi_data[:3]
        channel = status & 0x0F
        
        # Check channel filter
        if self.config.MIDI_CHANNEL > 0 and channel != (self.config.MIDI_CHANNEL - 1):
            return
        
        if MidiConstants.NOTE_ON_START <= status <= MidiConstants.NOTE_ON_END:
            if data2 > 0:
                velocity = (data2 / MidiConstants.MAX_VALUE) * self.config.VELOCITY_SENSITIVITY
                self.note_on_signal.emit(data1, min(velocity, 1.0), channel)
            else:
                self.note_off_signal.emit(data1, channel)
        elif MidiConstants.NOTE_OFF_START <= status <= MidiConstants.NOTE_OFF_END:
            self.note_off_signal.emit(data1, channel)
        elif MidiConstants.CC_START <= status <= MidiConstants.CC_END:
            cc_value = data2 / MidiConstants.MAX_VALUE
            self.cc_signal.emit(data1, cc_value, channel)
    
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
        print("Stopping enhanced MIDI handler...")
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        self._cleanup_midi()
        print("Enhanced MIDI handler stopped")

# =============================================================================
# Audio Analysis (Simplified for now)
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
            self.previous_energy = 0.0
    
    def start(self):
        if not AUDIO_AVAILABLE or self.is_active:
            return False
            
        try:
            self.audio = pyaudio.PyAudio()
            
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
