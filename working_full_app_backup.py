#!/usr/bin/env python3
"""
Complete MIDI Morphing Visualizer - Full Featured Version
Working version with all advanced features and proper indentation.
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
    try:
        print(f"Creating perfectly matched meshes with resolution {resolution}...")
        
        sphere = pv.Sphere(radius=1.0, phi_resolution=resolution, theta_resolution=resolution)
        target_points = sphere.n_points
        print(f"Target vertex count: {target_points}")
        
        meshes = {'sphere': sphere}
        
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
                print(f"✗ Error creating {shape_name}: {e}")
        
        try:
            torus = create_torus_from_sphere(sphere)
            if torus.n_points == target_points:
                meshes['torus'] = torus
                print(f"✓ torus: {torus.n_points} vertices")
        except Exception as e:
            print(f"✗ Error creating torus: {e}")
        
        try:
            icosahedron = create_icosahedron_from_sphere(sphere)
            if icosahedron.n_points == target_points:
                meshes['icosahedron'] = icosahedron
                print(f"✓ icosahedron: {icosahedron.n_points} vertices")
        except Exception as e:
            print(f"✗ Error creating icosahedron: {e}")
        
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
    try:
        current_count = mesh.n_points
        
        if current_count == target_count:
            return mesh
        
        if hasattr(mesh, 'triangulate'):
            mesh = mesh.triangulate()
        
        if current_count < target_count:
            while mesh.n_points < target_count * 0.9:
                try:
                    mesh = mesh.subdivide(1)
                    if mesh.n_points >= target_count * 2:
                        break
                except Exception as e:
                    print(f"Subdivision failed: {e}")
                    break
        
        if mesh.n_points > target_count:
            ratio = target_count / mesh.n_points
            try:
                mesh = mesh.decimate(1 - ratio)
            except Exception as e:
                print(f"Decimation failed: {e}")
                return None
        
        if abs(mesh.n_points - target_count) / target_count < 0.1:
            return mesh
        
        return None
        
    except Exception as e:
        print(f"Force vertex match failed: {e}")
        return None

def create_torus_from_sphere(sphere):
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
    points = sphere.points.copy()
    
    normals = points / np.linalg.norm(points, axis=1)[:, np.newaxis]
    quantized = np.round(normals * 4) / 4
    quantized = quantized / np.linalg.norm(quantized, axis=1)[:, np.newaxis]
    
    icosahedron = sphere.copy()
    icosahedron.points = quantized
    return icosahedron

def blend_meshes(meshes, source_key, target_key, alpha):
    if source_key not in meshes or target_key not in meshes:
        raise ValueError(f"Mesh keys not found: {source_key}, {target_key}")
    
    source_mesh = meshes[source_key]
    target_mesh = meshes[target_key]
    
    if source_mesh.n_points != target_mesh.n_points:
        raise ValueError(f"Vertex count mismatch: {source_mesh.n_points} vs {target_mesh.n_points}")
    
    source_points = source_mesh.points
    target_points = target_mesh.points
    return (1 - alpha) * source_points + alpha * target_points

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
    def __init__(self, initial_meshes, plotter_widget):
        self.initial_meshes = initial_meshes
        self.plotter_widget = plotter_widget
        self.objects: Dict[str, VisualObject] = {}
        self.actors: Dict[str, object] = {}
        self.meshes: Dict[str, object] = {}
        
        self._setup_default_mappings()
    
    def _setup_default_mappings(self):
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
        for obj_id, visual_obj in self.objects.items():
            if obj_id in self.meshes and target_shape in self.initial_meshes:
                try:
                    current_shape = visual_obj.shape_type
                    
                    blended_points = blend_meshes(
                        self.initial_meshes,
                        current_shape,
                        target_shape,
                        alpha
                    )
                    
                    transformed_points = blended_points * visual_obj.scale + visual_obj.position
                    
                    self.meshes[obj_id].points = transformed_points
                    
                    visual_obj.morph_amount = alpha
                    visual_obj.current_morph_target = target_shape
                    
                except Exception as e:
                    print(f"Error morphing object {obj_id}: {e}")
        
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

class EnhancedMidiHandler(QObject):
    note_on_signal = Signal(int, float, int)
    note_off_signal = Signal(int, int)
    cc_signal = Signal(int, float, int)
    
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
        
        if self.config.MIDI_CHANNEL > 0 and channel != (self.config.MIDI_CHANNEL - 1):
            return
        
        if 144 <= status <= 159:
            if data2 > 0:
                velocity = (data2 / 127) * self.config.VELOCITY_SENSITIVITY
                self.note_on_signal.emit(data1, min(velocity, 1.0), channel)
            else:
                self.note_off_signal.emit(data1, channel)
        elif 128 <= status <= 143:
            self.note_off_signal.emit(data1, channel)
        elif 176 <= status <= 191:
            cc_value = data2 / 127
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
            print(f"✗ Failed to start audio analysis: {e}")
            return False
    
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
                
                rms = np.sqrt(np.mean(audio_chunk ** 2))
                if rms > 0.001:
                    self.amplitude_signal.emit(rms)
                
                current_energy = np.sum(audio_chunk ** 2)
                if self.previous_energy > 0:
                    energy_ratio = current_energy / max(self.previous_energy, 1e-10)
                    if energy_ratio > self.config.AUDIO_ONSET_THRESHOLD:
                        self.onset_detected_signal.emit(rms)
                
                self.previous_energy = current_energy * 0.1 + self.previous_energy * 0.9
                
            except Exception as e:
                print(f"Audio analysis error: {e}")
                break
    
    def stop(self):
        self.running = False
        self.is_active = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()
        print("Audio analysis stopped")

class PerformanceProfiler(QObject):
    fps_updated = Signal(float)
    memory_updated = Signal(float, float)
    cpu_updated = Signal(float)
    performance_warning = Signal(str)
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.enabled = config.ENABLE_PROFILING
        
        if PERFORMANCE_MONITORING:
            self.process = psutil.Process()
            self.fps_history = []
            self.frame_count = 0
            self.last_fps_time = time.time()
            
            self.monitoring_active = False
            self.monitoring_thread = None
            if self.enabled:
                self.start_monitoring()
    
    def start_monitoring(self):
        if not PERFORMANCE_MONITORING or self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        print("✓ Performance monitoring started")
    
    def _monitoring_loop(self):
        while self.monitoring_active:
            try:
                if PERFORMANCE_MONITORING:
                    memory_info = psutil.virtual_memory()
                    memory_mb = memory_info.used / (1024 * 1024)
                    memory_percent = memory_info.percent
                    
                    cpu_percent = psutil.cpu_percent(interval=None)
                    
                    self.memory_updated.emit(memory_mb, memory_percent)
                    self.cpu_updated.emit(cpu_percent)
                    
                    if memory_percent > self.config.MEMORY_WARNING:
                        self.performance_warning.emit(f"High memory usage: {memory_percent:.1f}%")
                    
                    if cpu_percent > self.config.CPU_WARNING:
                        self.performance_warning.emit(f"High CPU usage: {cpu_percent:.1f}%")
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(2.0)
    
    def record_frame(self):
        if not self.enabled:
            return
            
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            fps = self.frame_count / (current_time - self.last_fps_time)
            self.fps_history.append(fps)
            
            if len(self.fps_history) > 60:
                self.fps_history.pop(0)
            
            self.fps_updated.emit(fps)
            
            if fps < self.config.FPS_WARNING:
                self.performance_warning.emit(f"Low FPS: {fps:.1f}")
            
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def stop_monitoring(self):
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)

class FullFeaturedMorphingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("MIDI Morphing Visualizer - Full Featured")
        
        self.current_mesh_key = "sphere"
        self.target_mesh_key = "cube"
        self.audio_enabled = False
        self.audio_color_influence = 0.0
        
        self.profiler = PerformanceProfiler(self.config) if PERFORMANCE_MONITORING else None
        self.midi_handler = EnhancedMidiHandler(self.config) if MIDI_AVAILABLE else None
        self.audio_analyzer = SimpleAudioAnalyzer(self.config) if AUDIO_AVAILABLE else None
        self.scene_manager = None
        
        print("Initializing full-featured MIDI morphing visualizer...")
        self._initialize_visualization()
        self._setup_ui()
        self._setup_menu()
        self._setup_connections()
        
        if self.midi_handler:
            self.midi_handler.start()
        
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_expired_elements)
        self.cleanup_timer.start(self.config.CLEANUP_INTERVAL * 1000)
        
        self.render_timer = QTimer()
        self.render_timer.timeout.connect(self._frame_update)
        self.render_timer.start(int(1000 / self.config.TARGET_FPS))
        
        print("✅ Full-featured application initialized!")
    
    def _initialize_visualization(self):
        try:
            print("Creating meshes for full-featured version...")
            self.initial_meshes = create_perfectly_matched_meshes(self.config.MESH_RESOLUTION)
            
            if len(self.initial_meshes) >= 2:
                print(f"✓ Created {len(self.initial_meshes)} perfectly matched meshes")
            else:
                print("⚠ Limited mesh set available")
                
        except Exception as e:
            print(f"Mesh creation error: {e}")
            self.initial_meshes = {'sphere': pv.Sphere()}
    
    def _setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        if self.profiler:
            self.fps_label = QLabel("FPS: --")
            self.memory_label = QLabel("Memory: --")
            self.status_bar.addPermanentWidget(self.fps_label)
            self.status_bar.addPermanentWidget(self.memory_label)
        
        self.plotter_widget = QtInteractor(self.central_widget)
        layout.addWidget(self.plotter_widget)
        
        self.scene_manager = SceneManager(self.initial_meshes, self.plotter_widget)
        
        controls_layout = QHBoxLayout()
        
        left_controls = QVBoxLayout()
        
        left_controls.addWidget(QLabel("Global Morph Target:"))
        self.target_combo = QComboBox()
        self.target_combo.addItems(sorted(self.initial_meshes.keys()))
        if 'cube' in self.initial_meshes:
            self.target_combo.setCurrentText('cube')
        left_controls.addWidget(self.target_combo)
        
        left_controls.addWidget(QLabel("Global Morph Amount:"))
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        left_controls.addWidget(self.morph_slider)
        
        controls_layout.addLayout(left_controls)
        
        right_controls = QVBoxLayout()
        
        if AUDIO_AVAILABLE:
            self.audio_check = QCheckBox("Enable Audio Analysis")
            right_controls.addWidget(self.audio_check)
        
        if MIDI_AVAILABLE:
            self.midi_status_label = QLabel("MIDI: Connecting...")
            right_controls.addWidget(self.midi_status_label)
            
            self.midi_reconnect_button = QPushButton("Reconnect MIDI")
            right_controls.addWidget(self.midi_reconnect_button)
        
        controls_layout.addLayout(right_controls)
        layout.addLayout(controls_layout)
        
        status_layout = QHBoxLayout()
        
        scene_info = QVBoxLayout()
        self.scene_summary_label = QLabel("Scene: Multiple objects with note range mapping")
        scene_info.addWidget(self.scene_summary_label)
        
        self.active_notes_label = QLabel("Active Notes: None")
        scene_info.addWidget(self.active_notes_label)
        
        status_layout.addLayout(scene_info)
        
        if AUDIO_AVAILABLE:
            audio_info = QVBoxLayout()
            self.audio_status_label = QLabel("Audio: Disabled")
            audio_info.addWidget(self.audio_status_label)
            
            status_layout.addLayout(audio_info)
        
        layout.addLayout(status_layout)
        
        clear_button = QPushButton("Clear All Notes")
        clear_button.clicked.connect(self._clear_all_notes)
        layout.addWidget(clear_button)
        
        self.plotter_widget.reset_camera()
        
        vertex_count = list(self.initial_meshes.values())[0].n_points
        self.status_bar.showMessage(f"Full-Featured MIDI Morphing Ready - Scene Manager Active ({vertex_count} vertices per shape)")
    
    def _setup_menu(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("View")
        
        scene_config_action = QAction("Scene Configuration...", self)
        scene_config_action.triggered.connect(self._show_scene_config)
        view_menu.addAction(scene_config_action)
        
        if self.profiler:
            perf_menu = menubar.addMenu("Performance")
            
            show_monitor_action = QAction("Show Performance Monitor", self)
            show_monitor_action.triggered.connect(self._show_performance_monitor)
            perf_menu.addAction(show_monitor_action)
    
    def _setup_connections(self):
        self.morph_slider.valueChanged.connect(self._on_global_morph_change)
        self.target_combo.currentTextChanged.connect(self._on_target_change)
        
        if MIDI_AVAILABLE and self.midi_handler:
            self.midi_reconnect_button.clicked.connect(self._reconnect_midi)
            self.midi_handler.note_on_signal.connect(self._on_midi_note_on)
            self.midi_handler.note_off_signal.connect(self._on_midi_note_off)
            self.midi_handler.cc_signal.connect(self._on_midi_cc)
        
        if AUDIO_AVAILABLE and self.audio_analyzer:
            self.audio_check.toggled.connect(self._toggle_audio)
            self.audio_analyzer.onset_detected_signal.connect(self._on_audio_onset)
            self.audio_analyzer.amplitude_signal.connect(self._on_audio_amplitude)
        
        if self.profiler:
            self.profiler.fps_updated.connect(self._update_fps_display)
            self.profiler.memory_updated.connect(self._update_memory_display)
            self.profiler.cpu_updated.connect(self._update_cpu_display)
            self.profiler.performance_warning.connect(self._show_performance_warning)
    
    def _on_global_morph_change(self, value):
        alpha = value / 100.0
        target_shape = self.target_combo.currentText()
        
        if self.scene_manager and target_shape in self.initial_meshes:
            self.scene_manager.apply_global_morphing(target_shape, alpha)
            self.status_bar.showMessage(f"Global morph: → {target_shape} ({value}%)", 1000)
    
    def _on_target_change(self, target_key):
        if target_key in self.initial_meshes:
            self.target_mesh_key = target_key
            self._on_global_morph_change(self.morph_slider.value())
    
    def _toggle_audio(self, enabled):
        if enabled and self.audio_analyzer:
            if self.audio_analyzer.start():
                self.audio_enabled = True
                self.audio_status_label.setText("Audio: Active")
            else:
                self.audio_check.setChecked(False)
                self.audio_status_label.setText("Audio: Failed to start")
        else:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
            self.audio_enabled = False
            self.audio_status_label.setText("Audio: Disabled")
    
    def _reconnect_midi(self):
        if self.midi_handler:
            self.midi_handler.stop()
            QTimer.singleShot(100, self._do_midi_reconnect)
    
    def _do_midi_reconnect(self):
        if self.midi_handler and self.midi_handler.start():
            self.midi_status_label.setText("MIDI: Connected (Enhanced)")
            self.status_bar.showMessage("MIDI reconnected successfully", 3000)
        else:
            self.midi_status_label.setText("MIDI: Connection failed")
            self.status_bar.showMessage("MIDI reconnection failed", 3000)
    
    def _on_midi_note_on(self, note, velocity, channel):
        try:
            if self.scene_manager:
                affected_objects = self.scene_manager.handle_midi_note(note, velocity, True, channel)
                
                if affected_objects:
                    print(f"Note ON: {note} (vel: {velocity:.2f}, ch: {channel}) -> {', '.join(affected_objects)}")
                    self._update_scene_display()
                else:
                    print(f"Note ON: {note} - No objects in range")
            
        except Exception as e:
            print(f"Error handling note on: {e}")
    
    def _on_midi_note_off(self, note, channel):
        try:
            if self.scene_manager:
                affected_objects = self.scene_manager.handle_midi_note(note, 0, False, channel)
                
                if affected_objects:
                    print(f"Note OFF: {note} (ch: {channel}) -> {', '.join(affected_objects)}")
                    self._update_scene_display()
            
        except Exception as e:
            print(f"Error handling note off: {e}")
    
    def _on_midi_cc(self, cc_number, value, channel):
        if cc_number == self.config.MORPH_CC:
            slider_value = int(value * 100)
            self.morph_slider.setValue(slider_value)
            print(f"CC{cc_number}: {value:.2f} -> Global morph: {slider_value}%")
    
    def _on_audio_onset(self, amplitude):
        try:
            if not self.audio_enabled:
                return
            
            self.audio_color_influence = min(amplitude * self.config.AUDIO_COLOR_STRENGTH, 1.0)
            
            if self.scene_manager:
                for obj_id, visual_obj in self.scene_manager.objects.items():
                    visual_obj.opacity = min(visual_obj.opacity + self.audio_color_influence * 0.3, 1.0)
                    self.scene_manager._update_object_visual(obj_id)
            
            QTimer.singleShot(self.config.FLASH_DURATION, self._fade_audio_influence)
            
        except Exception as e:
            print(f"Error handling audio onset: {e}")
    
    def _on_audio_amplitude(self, amplitude):
        try:
            if amplitude > 0.1:
                audio_morph = min(amplitude * self.config.AUDIO_MORPH_STRENGTH, 0.2)
                base_morph = self.morph_slider.value() / 100.0
                combined_morph = np.clip(base_morph + audio_morph, 0, 1)
                
                if self.scene_manager:
                    target_shape = self.target_combo.currentText()
                    self.scene_manager.apply_global_morphing(target_shape, combined_morph)
            
            self.audio_status_label.setText(f"Audio: Amplitude {amplitude:.3f}")
            
        except Exception as e:
            print(f"Error handling audio amplitude: {e}")
    
    def _fade_audio_influence(self):
        self.audio_color_influence *= 0.3
        if self.audio_color_influence > 0.01:
            QTimer.singleShot(50, self._fade_audio_influence)
        else:
            self.audio_color_influence = 0.0
            if self.scene_manager:
                for obj_id, visual_obj in self.scene_manager.objects.items():
                    visual_obj._update_composite_properties()
                    self.scene_manager._update_object_visual(obj_id)
    
    def _update_scene_display(self):
        if self.scene_manager:
            summary = self.scene_manager.get_scene_summary()
            active_objects = summary['active_objects']
            total_notes = summary['total_active_notes']
            
            if total_notes > 0:
                note_info = []
                for obj_id, obj_info in summary['objects'].items():
                    if obj_info['active_notes'] > 0:
                        note_info.append(f"{obj_id}({obj_info['active_notes']})")
                
                self.active_notes_label.setText(f"Active: {', '.join(note_info)} | Total: {total_notes}")
                self.scene_summary_label.setText(f"Scene: {active_objects}/{summary['total_objects']} objects active")
            else:
                self.active_notes_label.setText("Active Notes: None")
                self.scene_summary_label.setText(f"Scene: {summary['total_objects']} objects ready")
    
    def _clear_all_notes(self):
        if self.scene_manager:
            self.scene_manager.clear_all_notes()
            self._update_scene_display()
    
    def _cleanup_expired_elements(self):
        if self.scene_manager:
            self.scene_manager.cleanup_expired_notes(self.config.NOTE_TIMEOUT)
            self._update_scene_display()
    
    def _frame_update(self):
        if self.profiler:
            self.profiler.record_frame()
    
    def _show_scene_config(self):
        QMessageBox.information(self, "Scene Configuration", 
                              "Scene configuration dialog not yet implemented.\n"
                              "Current scene uses default note range mappings:\n\n"
                              "• Bass (C1-B2): Left sphere\n"
                              "• Melody (C3-C5): Center icosahedron\n"
                              "• Treble (C#5-C7): Right cube\n"
                              "• High (C#7-G9): Top cone")
    
    def _show_performance_monitor(self):
        if self.profiler:
            QMessageBox.information(self, "Performance Monitor", 
                                  "Performance monitoring is active.\n"
                                  "Check the status bar for real-time FPS and memory usage.\n"
                                  "Advanced performance dialog not yet implemented.")
        else:
            QMessageBox.warning(self, "Performance Monitor", 
                              "Performance monitoring not available.\n"
                              "Install psutil for performance monitoring:\n"
                              "pip install psutil")
    
    def _update_fps_display(self, fps):
        if hasattr(self, 'fps_label'):
            color = "green" if fps >= 30 else "orange" if fps >= 20 else "red"
            self.fps_label.setText(f"<font color='{color}'>FPS: {fps:.1f}</font>")
    
    def _update_memory_display(self, memory_mb, memory_percent):
        if hasattr(self, 'memory_label'):
            color = "green" if memory_percent < 70 else "orange" if memory_percent < 85 else "red"
            self.memory_label.setText(f"<font color='{color}'>Mem: {memory_percent:.1f}%</font>")
    
    def _update_cpu_display(self, cpu_percent):
        pass
    
    def _show_performance_warning(self, warning):
        self.status_bar.showMessage(f"⚠️ {warning}", 5000)
    
    def closeEvent(self, event):
        print("Shutting down full-featured application...")
        
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
            if self.profiler:
                print("Stopping performance monitoring...")
                self.profiler.stop_monitoring()
        except Exception as e:
            print(f"Error stopping profiler: {e}")
        
        try:
            self.cleanup_timer.stop()
            self.render_timer.stop()
        except Exception as e:
            print(f"Error stopping timers: {e}")
        
        print("Full-featured application shutdown complete")
        event.accept()

def main():
    print("=== Full-Featured MIDI Morphing Visualizer ===")
    print("This version includes:")
    print("• Scene Manager with multiple objects")
    print("• Note range mapping (bass, melody, treble, high)")
    print("• Audio analysis with onset detection")
    print("• Performance monitoring and profiling")
    print("• Enhanced MIDI handling with channel filtering")
    print("• Global morphing effects")
    print("")
    
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer - Full Featured")
    
    try:
        window = FullFeaturedMorphingWindow()
        window.resize(1400, 900)
        window.show()
        
        print("🎵 Full-Featured MIDI Morphing Visualizer Ready! 🎵")
        print("\nFeatures available:")
        print("• Multiple objects respond to different note ranges")
        print("• Global morphing slider affects all objects")
        print("• Audio analysis with onset detection")
        print("• Performance monitoring in status bar")
        print("• Enhanced MIDI with channel filtering")
        print("• Menu system with configuration options")
        print("")
        print("Try playing notes in different octaves to see different objects light up!")
        
        return app.exec()
        
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
