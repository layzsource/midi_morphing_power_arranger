#!/usr/bin/env python3
"""
Enhanced MIDI Morphing Visualizer - Step 3: Clean Fixed Version
This is a completely clean version that resolves all syntax and 3D compatibility issues.
"""

import sys
import os
import logging
import time
import threading
import colorsys
import numpy as np
import queue
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
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
        QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar, QFrame
    )
    from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject, QThread
    from PySide6.QtGui import QAction, QFont, QKeySequence, QShortcut
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✅ Core GUI dependencies available")
except ImportError as e:
    print(f"❌ Missing core dependencies: {e}")
    sys.exit(1)

# Optional dependencies
MIDI_AVAILABLE = False
try:
    import pygame.midi
    MIDI_AVAILABLE = True
    print("✅ Pygame MIDI support available")
except ImportError:
    print("⚠️  MIDI support not available")

# Audio dependencies
AUDIO_AVAILABLE = False
SOUNDDEVICE_AVAILABLE = False
PYAUDIO_AVAILABLE = False
LIBROSA_AVAILABLE = False

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
    AUDIO_AVAILABLE = True
    print("✅ SoundDevice audio backend available")
except ImportError:
    print("⚠️  SoundDevice not available")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
    AUDIO_AVAILABLE = True
    print("✅ PyAudio backend available")
except ImportError:
    print("⚠️  PyAudio not available")

try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ Librosa audio analysis available")
except ImportError:
    print("⚠️  Librosa not available - advanced audio features disabled")

try:
    import psutil
    PERFORMANCE_MONITORING = True
    print("✅ Performance monitoring available")
except ImportError:
    PERFORMANCE_MONITORING = False
    print("⚠️  Performance monitoring not available")

# =============================================================================
# QtInteractor Compatibility Wrapper
# =============================================================================

class QtInteractorWrapper:
    """Wrapper to handle QtInteractor compatibility issues."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.plotter_widget = None
        self.plotter = None
        self._initialize()
    
    def _initialize(self):
        """Initialize QtInteractor with compatibility handling."""
        try:
            # Create QtInteractor using the working pattern
            self.plotter_widget = QtInteractor(self.parent)
            # QtInteractor IS the plotter
            self.plotter = self.plotter_widget
            print("✅ QtInteractor initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize QtInteractor: {e}")
            return False
    
    def get_widget(self):
        """Get the Qt widget for adding to layouts."""
        return self.plotter_widget
    
    def get_plotter(self):
        """Get the plotter for PyVista operations."""
        return self.plotter
    
    def set_background(self, color='black'):
        """Set background color with compatibility."""
        if not self.plotter:
            return False
        try:
            if hasattr(self.plotter, 'set_background'):
                self.plotter.set_background(color)
            elif hasattr(self.plotter, 'background_color'):
                self.plotter.background_color = color
            return True
        except Exception as e:
            print(f"⚠️  Background setting failed: {e}")
            return False
    
    def add_mesh(self, mesh, **kwargs):
        """Add mesh with compatibility handling."""
        if not self.plotter:
            return None
        try:
            # Use only safe parameters
            safe_kwargs = {}
            for key, value in kwargs.items():
                if key in ['color', 'opacity', 'show_edges', 'lighting']:
                    safe_kwargs[key] = value
            
            actor = self.plotter.add_mesh(mesh, **safe_kwargs)
            return actor
        except Exception as e:
            print(f"❌ Error adding mesh: {e}")
            try:
                # Try with minimal parameters
                actor = self.plotter.add_mesh(mesh, color=kwargs.get('color', 'white'))
                return actor
            except:
                return None
    
    def add_light(self, light):
        """Add light with compatibility handling."""
        if not self.plotter:
            return False
        try:
            self.plotter.add_light(light)
            return True
        except Exception as e:
            print(f"⚠️  Could not add light: {e}")
            try:
                if hasattr(self.plotter, 'enable_lightkit'):
                    self.plotter.enable_lightkit()
                    return True
            except:
                pass
            return False
    
    def remove_actor(self, actor):
        """Remove actor with error handling."""
        if not self.plotter or not actor:
            return False
        try:
            self.plotter.remove_actor(actor)
            return True
        except:
            return False

# =============================================================================
# Scene Objects and Manager
# =============================================================================

class ObjectType(Enum):
    """Different object types for the scene."""
    SPHERE = "sphere"
    CUBE = "cube"
    CYLINDER = "cylinder"
    CONE = "cone"
    TORUS = "torus"
    ICOSAHEDRON = "icosahedron"
    OCTAHEDRON = "octahedron"

@dataclass
class SceneObject:
    """Enhanced scene object with full morphing capabilities."""
    id: str
    object_type: ObjectType
    note_range: Tuple[int, int]
    range_name: str
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    base_scale: float = 1.0
    current_scale: float = 1.0
    base_color: np.ndarray = field(default_factory=lambda: np.array([0.5, 0.5, 1.0]))
    current_color: np.ndarray = field(default_factory=lambda: np.array([0.5, 0.5, 1.0]))
    opacity: float = 0.8
    active_notes: Dict[int, float] = field(default_factory=dict)
    last_activity: float = 0.0
    morph_factor: float = 0.0
    actor: Any = None
    lights: List[Any] = field(default_factory=list)
    
    def get_intensity(self) -> float:
        """Calculate current intensity based on active notes."""
        if not self.active_notes:
            return 0.0
        return min(1.0, sum(self.active_notes.values()) / len(self.active_notes))
    
    def has_note_in_range(self, note: int) -> bool:
        """Check if note falls within this object's range."""
        return self.note_range[0] <= note <= self.note_range[1]
    
    def get_color_for_note(self, note: int, velocity: float) -> np.ndarray:
        """Get color for specific note within this object's range."""
        range_span = self.note_range[1] - self.note_range[0]
        if range_span == 0:
            note_ratio = 0.5
        else:
            note_ratio = (note - self.note_range[0]) / range_span
        
        # Different color schemes for different ranges
        if self.range_name == "bass":
            hue = 0.8 + note_ratio * 0.3  # Purple to blue
        elif self.range_name == "melody":  
            hue = 0.3 + note_ratio * 0.3   # Green to yellow
        elif self.range_name == "treble":
            hue = 0.0 + note_ratio * 0.2   # Red to orange
        else:  # high
            hue = 0.7 + note_ratio * 0.2   # Blue to purple
        
        hue = hue % 1.0
        saturation = 0.6 + velocity * 0.4
        value = 0.4 + velocity * 0.6
        
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return np.array(rgb)

class CleanSceneManager:
    """Clean Scene Manager for Step 3 with robust 3D handling."""
    
    def __init__(self, qt_wrapper):
        self.qt_wrapper = qt_wrapper
        self.plotter = qt_wrapper.get_plotter()
        
        # Scene objects
        self.objects: Dict[str, SceneObject] = {}
        self.note_to_object_map: Dict[int, str] = {}
        
        # Global scene settings
        self.global_morph_factor = 0.0
        self.max_lights_per_object = 2
        
        # Initialize default scene
        self._create_default_scene()
        print("✅ Clean Scene Manager initialized")
    
    def _create_default_scene(self):
        """Create the default multi-object scene."""
        
        # Define note ranges
        note_ranges = {
            "bass": (24, 47),     # C1-B2
            "melody": (48, 71),   # C3-B4  
            "treble": (72, 95),   # C5-B6
            "high": (96, 108)     # C7-C8
        }
        
        # Define object configurations
        object_configs = [
            {
                "id": "bass_sphere",
                "type": ObjectType.SPHERE,
                "range": "bass",
                "position": np.array([-2.0, -1.0, 0.0]),
                "scale": 1.5,
                "color": np.array([0.2, 0.3, 1.0])  # Blue
            },
            {
                "id": "melody_cube", 
                "type": ObjectType.CUBE,
                "range": "melody",
                "position": np.array([0.0, 0.0, 0.0]),
                "scale": 1.2,
                "color": np.array([0.3, 0.8, 0.3])  # Green
            },
            {
                "id": "treble_cylinder",
                "type": ObjectType.CYLINDER,
                "range": "treble", 
                "position": np.array([2.0, 1.0, 0.0]),
                "scale": 1.0,
                "color": np.array([1.0, 0.4, 0.2])  # Orange
            },
            {
                "id": "high_icosahedron",
                "type": ObjectType.ICOSAHEDRON,
                "range": "high",
                "position": np.array([0.0, 2.5, 0.0]),
                "scale": 0.8,
                "color": np.array([1.0, 0.2, 1.0])  # Magenta
            }
        ]
        
        # Create scene objects
        for config in object_configs:
            obj = SceneObject(
                id=config["id"],
                object_type=config["type"],
                note_range=note_ranges[config["range"]],
                range_name=config["range"],
                position=config["position"],
                base_scale=config["scale"],
                current_scale=config["scale"],
                base_color=config["color"],
                current_color=config["color"].copy()
            )
            
            # Create the 3D mesh
            obj.actor = self._create_object_mesh(obj)
            self.objects[obj.id] = obj
            
            # Map notes to objects
            for note in range(obj.note_range[0], obj.note_range[1] + 1):
                self.note_to_object_map[note] = obj.id
        
        print(f"✅ Created {len(self.objects)} scene objects")
        for obj_id, obj in self.objects.items():
            range_str = f"{obj.note_range[0]}-{obj.note_range[1]}"
            status = "✅" if obj.actor else "❌"
            print(f"   {status} {obj_id}: {obj.object_type.value} (notes {range_str})")
    
    def _create_object_mesh(self, scene_obj: SceneObject) -> Any:
        """Create PyVista mesh for scene object."""
        try:
            # Create base mesh with reduced resolution for compatibility
            resolution = 10
            
            if scene_obj.object_type == ObjectType.SPHERE:
                mesh = pv.Sphere(radius=scene_obj.base_scale, 
                               phi_resolution=resolution, theta_resolution=resolution)
            elif scene_obj.object_type == ObjectType.CUBE:
                mesh = pv.Cube(x_length=scene_obj.base_scale*2,
                              y_length=scene_obj.base_scale*2, 
                              z_length=scene_obj.base_scale*2)
            elif scene_obj.object_type == ObjectType.CYLINDER:
                mesh = pv.Cylinder(radius=scene_obj.base_scale*0.8, 
                                 height=scene_obj.base_scale*2,
                                 resolution=resolution)
            elif scene_obj.object_type == ObjectType.CONE:
                mesh = pv.Cone(radius=scene_obj.base_scale, 
                              height=scene_obj.base_scale*2,
                              resolution=resolution)
            elif scene_obj.object_type == ObjectType.ICOSAHEDRON:
                try:
                    mesh = pv.Icosahedron(radius=scene_obj.base_scale)
                except:
                    # Fallback to sphere
                    mesh = pv.Sphere(radius=scene_obj.base_scale,
                                   phi_resolution=resolution, theta_resolution=resolution)
            else:
                mesh = pv.Sphere(radius=scene_obj.base_scale,
                               phi_resolution=resolution, theta_resolution=resolution)
            
            # Position the mesh
            mesh = mesh.translate(scene_obj.position)
            
            # Add mesh using wrapper
            actor = self.qt_wrapper.add_mesh(
                mesh,
                color=scene_obj.current_color,
                opacity=scene_obj.opacity,
                show_edges=False,
                lighting=True
            )
            
            return actor
            
        except Exception as e:
            print(f"❌ Error creating mesh for {scene_obj.id}: {e}")
            return None
    
    def handle_midi_note(self, note: int, velocity: float, note_on: bool = True, channel: int = 0):
        """Handle MIDI note events."""
        
        obj_id = self.note_to_object_map.get(note)
        if not obj_id or obj_id not in self.objects:
            return
        
        scene_obj = self.objects[obj_id]
        
        if note_on:
            scene_obj.active_notes[note] = velocity
            scene_obj.last_activity = time.time()
            self._update_object_for_note(scene_obj, note, velocity)
            print(f"🎵 Note {note} (vel: {velocity:.2f}) -> {obj_id} ({scene_obj.range_name})")
        else:
            if note in scene_obj.active_notes:
                del scene_obj.active_notes[note]
            if not scene_obj.active_notes:
                self._start_object_fadeout(scene_obj)
    
    def _update_object_for_note(self, scene_obj: SceneObject, note: int, velocity: float):
        """Update scene object properties."""
        try:
            # Update color
            note_color = scene_obj.get_color_for_note(note, velocity)
            if len(scene_obj.active_notes) > 1:
                scene_obj.current_color = (scene_obj.current_color + note_color) / 2
            else:
                scene_obj.current_color = note_color
            
            # Update scale
            intensity = scene_obj.get_intensity()
            scale_factor = 1.0 + intensity * 0.5
            scene_obj.current_scale = scene_obj.base_scale * scale_factor
            
            # Apply global morphing
            self._apply_global_morphing(scene_obj)
            
            # Update visual
            self._update_object_visual(scene_obj)
            
        except Exception as e:
            print(f"❌ Error updating object {scene_obj.id}: {e}")
    
    def _apply_global_morphing(self, scene_obj: SceneObject):
        """Apply global morphing effects."""
        if self.global_morph_factor <= 0.0:
            return
        
        scene_obj.morph_factor = self.global_morph_factor
        
        # Apply color shift
        hue_shift = self.global_morph_factor * 0.3
        h, s, v = colorsys.rgb_to_hsv(*scene_obj.current_color)
        h = (h + hue_shift) % 1.0
        morphed_color = np.array(colorsys.hsv_to_rgb(h, s, v))
        scene_obj.current_color = morphed_color
    
    def _update_object_visual(self, scene_obj: SceneObject):
        """Update visual representation."""
        if not scene_obj.actor:
            return
        
        try:
            scene_obj.actor.GetProperty().SetColor(scene_obj.current_color)
            intensity = scene_obj.get_intensity()
            opacity = scene_obj.opacity + intensity * 0.2
            scene_obj.actor.GetProperty().SetOpacity(min(1.0, opacity))
        except Exception as e:
            print(f"❌ Error updating visual for {scene_obj.id}: {e}")
    
    def _start_object_fadeout(self, scene_obj: SceneObject):
        """Start fadeout animation."""
        scene_obj.current_color = scene_obj.base_color.copy()
        scene_obj.current_scale = scene_obj.base_scale
        scene_obj.morph_factor = 0.0
        self._update_object_visual(scene_obj)
    
    def set_global_morph_factor(self, factor: float):
        """Set global morphing factor."""
        self.global_morph_factor = max(0.0, min(1.0, factor))
        
        for scene_obj in self.objects.values():
            if scene_obj.active_notes:
                self._apply_global_morphing(scene_obj)
                self._update_object_visual(scene_obj)
    
    def cleanup_lights(self):
        """Clean up old lights."""
        for scene_obj in self.objects.values():
            while len(scene_obj.lights) > self.max_lights_per_object:
                try:
                    old_light = scene_obj.lights.pop(0)
                    self.qt_wrapper.remove_actor(old_light)
                except:
                    break
    
    def get_scene_stats(self) -> Dict[str, Any]:
        """Get scene statistics."""
        total_active_notes = sum(len(obj.active_notes) for obj in self.objects.values())
        active_objects = sum(1 for obj in self.objects.values() if obj.active_notes)
        successful_objects = sum(1 for obj in self.objects.values() if obj.actor)
        
        return {
            'total_objects': len(self.objects),
            'successful_objects': successful_objects,
            'active_objects': active_objects,
            'total_active_notes': total_active_notes,
            'total_lights': sum(len(obj.lights) for obj in self.objects.values()),
            'global_morph_factor': self.global_morph_factor,
            'note_mapping_coverage': len(self.note_to_object_map)
        }

# =============================================================================
# MIDI Handler
# =============================================================================

class MidiSignals(QObject):
    """Qt signals for MIDI events."""
    note_on = Signal(int, float, int)
    note_off = Signal(int, int)
    control_change = Signal(int, int, int)

class MidiHandler(QThread):
    """MIDI handler."""
    
    def __init__(self):
        super().__init__()
        self.signals = MidiSignals()
        self.running = False
        self.midi_input = None
        self.device_id = None
        
        if MIDI_AVAILABLE:
            try:
                pygame.midi.init()
                self._find_midi_device()
            except Exception as e:
                print(f"❌ Failed to initialize MIDI: {e}")
    
    def _find_midi_device(self):
        """Find and select MIDI input device."""
        if not MIDI_AVAILABLE:
            return
        
        try:
            device_count = pygame.midi.get_count()
            print(f"🎹 Found {device_count} MIDI devices:")
            
            for i in range(device_count):
                info = pygame.midi.get_device_info(i)
                name = info[1].decode('utf-8')
                is_input = info[2] == 1
                
                print(f"   {i}: {name} ({'Input' if is_input else 'Output'})")
                
                if is_input and self.device_id is None:
                    self.device_id = i
                    print(f"✅ Selected MIDI device: {name}")
            
            if self.device_id is not None:
                self.midi_input = pygame.midi.Input(self.device_id)
                
        except Exception as e:
            print(f"❌ Error finding MIDI device: {e}")
    
    def run(self):
        """Main MIDI processing loop."""
        if not self.midi_input:
            print("⚠️  No MIDI input available")
            return
        
        self.running = True
        print("🎹 MIDI handler started")
        
        while self.running:
            try:
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    for event in midi_events:
                        self._process_midi_event(event[0])
                time.sleep(0.001)
            except Exception as e:
                print(f"❌ MIDI processing error: {e}")
                time.sleep(0.1)
    
    def _process_midi_event(self, event_data):
        """Process individual MIDI event."""
        status, data1, data2, data3 = event_data
        channel = status & 0x0F
        message_type = status & 0xF0
        
        if message_type == 0x90:  # Note On
            note = data1
            velocity = data2 / 127.0
            if velocity > 0:
                self.signals.note_on.emit(note, velocity, channel)
            else:
                self.signals.note_off.emit(note, channel)
        elif message_type == 0x80:  # Note Off
            note = data1
            self.signals.note_off.emit(note, channel)
        elif message_type == 0xB0:  # Control Change
            controller = data1
            value = data2
            self.signals.control_change.emit(controller, value, channel)
    
    def stop(self):
        """Stop MIDI processing."""
        self.running = False
        if self.midi_input:
            try:
                self.midi_input.close()
            except:
                pass
        if MIDI_AVAILABLE:
            try:
                pygame.midi.quit()
            except:
                pass
        print("🎹 MIDI handler stopped")

# =============================================================================
# Performance Monitor (Clean - No Recursion)
# =============================================================================

class PerformanceSignals(QObject):
    """Qt signals for performance monitoring."""
    fps_updated = Signal(float)
    memory_updated = Signal(float, float)
    cpu_updated = Signal(float)
    performance_warning = Signal(str)

class CleanPerformanceMonitor(QThread):
    """Clean performance monitoring with no recursion issues."""
    
    def __init__(self):
        super().__init__()
        self.signals = PerformanceSignals()
        self.running = False
        
        # Simple FPS tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps_update_interval = 1.0
        
        # Thresholds
        self.low_fps_threshold = 20.0
        self.high_memory_threshold = 80.0
        self.high_cpu_threshold = 90.0
    
    def register_frame(self):
        """Register a frame for FPS calculation."""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= self.fps_update_interval:
            time_diff = current_time - self.last_fps_time
            fps = self.frame_count / time_diff if time_diff > 0 else 0
            
            self.signals.fps_updated.emit(fps)
            
            if fps < self.low_fps_threshold:
                self.signals.performance_warning.emit(f"Low FPS: {fps:.1f}")
            
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def run(self):
        """Main performance monitoring loop."""
        if not PERFORMANCE_MONITORING:
            print("⚠️  Performance monitoring not available")
            return
        
        self.running = True
        print("📊 Performance monitoring started")
        
        while self.running:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = process.memory_percent()
                
                self.signals.memory_updated.emit(memory_mb, memory_percent)
                
                if memory_percent > self.high_memory_threshold:
                    self.signals.performance_warning.emit(f"High memory: {memory_percent:.1f}%")
                
                cpu_percent = process.cpu_percent()
                self.signals.cpu_updated.emit(cpu_percent)
                
                if cpu_percent > self.high_cpu_threshold:
                    self.signals.performance_warning.emit(f"High CPU: {cpu_percent:.1f}%")
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(1.0)
    
    def stop(self):
        """Stop performance monitoring."""
        self.running = False
        print("📊 Performance monitor stopped")

# =============================================================================
# Main Application Window
# =============================================================================

class CleanMorphingWindow(QMainWindow):
    """Clean main window with robust 3D handling."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Morphing Visualizer - Step 3: Clean Fixed")
        
        # Core components
        self.qt_wrapper = None
        self.scene_manager = None
        self.midi_handler = None
        self.performance_monitor = None
        
        # UI components
        self.morph_slider = None
        
        # Timers
        self.cleanup_timer = QTimer()
        self.render_timer = QTimer()
        
        # Initialize
        self._setup_ui()
        self._setup_3d_scene()
        self._setup_connections()
        self._start_systems()
        
        print("✅ Clean Morphing Window initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        # Morphing control
        morph_group = QGroupBox("Global Morphing")
        morph_layout = QVBoxLayout(morph_group)
        
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        morph_layout.addWidget(QLabel("Morph Factor:"))
        morph_layout.addWidget(self.morph_slider)
        
        self.morph_value_label = QLabel("0%")
        morph_layout.addWidget(self.morph_value_label)
        
        left_layout.addWidget(morph_group)
        
        # Scene info
        scene_group = QGroupBox("Scene Objects")
        scene_layout = QVBoxLayout(scene_group)
        
        self.scene_info_text = QTextEdit()
        self.scene_info_text.setMaximumHeight(200)
        self.scene_info_text.setReadOnly(True)
        scene_layout.addWidget(self.scene_info_text)
        
        left_layout.addWidget(scene_group)
        
        # Performance
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        self.fps_label = QLabel("FPS: --")
        self.memory_label = QLabel("Memory: --")
        self.cpu_label = QLabel("CPU: --")
        
        perf_layout.addWidget(self.fps_label)
        perf_layout.addWidget(self.memory_label)
        perf_layout.addWidget(self.cpu_label)
        
        left_layout.addWidget(perf_group)
        
        # Test controls
        test_group = QGroupBox("Test Controls")
        test_layout = QVBoxLayout(test_group)
        
        self.test_note_btn = QPushButton("Test MIDI Note")
        self.test_morph_btn = QPushButton("Test Morphing")
        self.reset_scene_btn = QPushButton("Reset Scene")
        
        test_layout.addWidget(self.test_note_btn)
        test_layout.addWidget(self.test_morph_btn)
        test_layout.addWidget(self.reset_scene_btn)
        
        left_layout.addWidget(test_group)
        
        # 3D Status
        status_group = QGroupBox("3D Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_3d_label = QLabel("3D: Initializing...")
        status_layout.addWidget(self.status_3d_label)
        
        left_layout.addWidget(status_group)
        
        left_layout.addStretch()
        
        # Add to main layout
        main_layout.addWidget(left_panel)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menu bar
        self._setup_menu_bar()
    
    def _setup_menu_bar(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # Scene menu
        scene_menu = menubar.addMenu("Scene")
        reset_action = QAction("Reset Scene", self)
        reset_action.triggered.connect(self._reset_scene)
        scene_menu.addAction(reset_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_3d_scene(self):
        """Setup 3D scene with robust error handling."""
        try:
            print("🔧 Initializing 3D scene...")
            
            # Create wrapper
            self.qt_wrapper = QtInteractorWrapper(self)
            
            if not self.qt_wrapper.plotter:
                raise Exception("Failed to create QtInteractor")
            
            # Add to layout
            widget = self.qt_wrapper.get_widget()
            if widget:
                widget.setMinimumSize(800, 600)
                self.centralWidget().layout().addWidget(widget, 1)
                print("✅ 3D widget added to layout")
            else:
                raise Exception("No 3D widget available")
            
            # Configure scene
            self.qt_wrapper.set_background('black')
            
            # Add lighting
            try:
                light = pv.Light(position=[10, 10, 10], light_type='point')
                self.qt_wrapper.add_light(light)
                print("✅ Lighting added")
            except Exception as e:
                print(f"⚠️  Could not add lighting: {e}")
            
            # Create scene manager
            self.scene_manager = CleanSceneManager(self.qt_wrapper)
            
            self.status_3d_label.setText("3D: ✅ Working")
            print("✅ 3D scene setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up 3D scene: {e}")
            import traceback
            traceback.print_exc()
            
            # Create fallback
            try:
                fallback = QLabel("3D Scene Failed\n\nCheck console for details.\nMIDI will still work.")
                fallback.setMinimumSize(800, 600)
                fallback.setStyleSheet("background-color: #1a1a1a; color: #ff6666; font-size: 14px;")
                fallback.setAlignment(Qt.AlignCenter)
                self.centralWidget().layout().addWidget(fallback, 1)
                self.status_3d_label.setText("3D: ❌ Failed")
            except:
                self.status_3d_label.setText("3D: ❌ Critical Error")
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.morph_slider.valueChanged.connect(self._on_morph_slider_changed)
        self.test_note_btn.clicked.connect(self._test_midi_note)
        self.test_morph_btn.clicked.connect(self._test_morphing)
        self.reset_scene_btn.clicked.connect(self._reset_scene)
        
        self.cleanup_timer.timeout.connect(self._cleanup_performance)
        self.render_timer.timeout.connect(self._update_render)
        
        print("✅ UI connections setup complete")
    
    def _start_systems(self):
        """Start all subsystems."""
        
        # Start MIDI
        if MIDI_AVAILABLE:
            try:
                self.midi_handler = MidiHandler()
                self.midi_handler.signals.note_on.connect(self._on_midi_note_on)
                self.midi_handler.signals.note_off.connect(self._on_midi_note_off)
                self.midi_handler.signals.control_change.connect(self._on_midi_control_change)
                self.midi_handler.start()
                print("✅ MIDI handler started")
            except Exception as e:
                print(f"⚠️  MIDI handler failed: {e}")
        
        # Start performance monitor
        if PERFORMANCE_MONITORING:
            try:
                self.performance_monitor = CleanPerformanceMonitor()
                self.performance_monitor.signals.fps_updated.connect(self._on_fps_updated)
                self.performance_monitor.signals.memory_updated.connect(self._on_memory_updated)
                self.performance_monitor.signals.cpu_updated.connect(self._on_cpu_updated)
                self.performance_monitor.signals.performance_warning.connect(self._on_performance_warning)
                self.performance_monitor.start()
                print("✅ Performance monitor started")
            except Exception as e:
                print(f"⚠️  Performance monitor failed: {e}")
        
        # Start timers
        self.cleanup_timer.start(5000)  # 5 seconds
        self.render_timer.start(16)     # ~60 FPS
        
        # Update info
        self._update_scene_info()
    
    def _on_morph_slider_changed(self, value):
        """Handle morph slider changes."""
        morph_factor = value / 100.0
        self.morph_value_label.setText(f"{value}%")
        
        if self.scene_manager:
            self.scene_manager.set_global_morph_factor(morph_factor)
        
        print(f"🔄 Global morph factor: {morph_factor:.2f}")
    
    def _on_midi_note_on(self, note, velocity, channel):
        """Handle MIDI note on."""
        if self.scene_manager:
            self.scene_manager.handle_midi_note(note, velocity, True, channel)
    
    def _on_midi_note_off(self, note, channel):
        """Handle MIDI note off."""
        if self.scene_manager:
            self.scene_manager.handle_midi_note(note, 0, False, channel)
    
    def _on_midi_control_change(self, controller, value, channel):
        """Handle MIDI control change."""
        if controller == 1:  # Modulation wheel
            morph_value = int((value / 127.0) * 100)
            self.morph_slider.setValue(morph_value)
            print(f"🎛️  MIDI CC1 -> Morph: {morph_value}%")
    
    def _on_fps_updated(self, fps):
        """Handle FPS updates - NO RECURSION."""
        color = "green" if fps >= 30 else "orange" if fps >= 20 else "red"
        self.fps_label.setText(f"<font color='{color}'>FPS: {fps:.1f}</font>")
    
    def _on_memory_updated(self, memory_mb, memory_percent):
        """Handle memory updates."""
        color = "green" if memory_percent < 70 else "orange" if memory_percent < 85 else "red"
        self.memory_label.setText(f"<font color='{color}'>Memory: {memory_percent:.1f}%</font>")
    
    def _on_cpu_updated(self, cpu_percent):
        """Handle CPU updates."""
        color = "green" if cpu_percent < 70 else "orange" if cpu_percent < 85 else "red"
        self.cpu_label.setText(f"<font color='{color}'>CPU: {cpu_percent:.1f}%</font>")
    
    def _on_performance_warning(self, warning):
        """Handle performance warnings."""
        self.status_bar.showMessage(f"⚠️ {warning}", 5000)
    
    def _test_midi_note(self):
        """Test MIDI note functionality."""
        test_notes = [
            (36, 0.8, "bass"),      # Bass range
            (60, 0.9, "melody"),    # Melody range  
            (84, 0.7, "treble"),    # Treble range
            (96, 0.6, "high")       # High range
        ]
        
        for i, (note, velocity, range_name) in enumerate(test_notes):
            QTimer.singleShot(i * 1000, lambda n=note, v=velocity: self._trigger_test_note(n, v))
    
    def _trigger_test_note(self, note, velocity):
        """Trigger a test note."""
        if self.scene_manager:
            self.scene_manager.handle_midi_note(note, velocity, True, 0)
            print(f"🧪 Test note: {note} (velocity: {velocity:.2f})")
            QTimer.singleShot(2000, lambda: self.scene_manager.handle_midi_note(note, 0, False, 0))
    
    def _test_morphing(self):
        """Test morphing functionality."""
        def animate_morph(target_value):
            current = self.morph_slider.value()
            step = 5 if target_value > current else -5
            
            if abs(target_value - current) <= abs(step):
                self.morph_slider.setValue(target_value)
            else:
                self.morph_slider.setValue(current + step)
                QTimer.singleShot(50, lambda: animate_morph(target_value))
        
        animate_morph(100)
        QTimer.singleShot(3000, lambda: animate_morph(0))
        print("🧪 Testing morphing animation")
    
    def _reset_scene(self):
        """Reset scene to default state."""
        if self.scene_manager:
            self.morph_slider.setValue(0)
            
            for scene_obj in self.scene_manager.objects.values():
                scene_obj.active_notes.clear()
                scene_obj.current_color = scene_obj.base_color.copy()
                scene_obj.current_scale = scene_obj.base_scale
                scene_obj.morph_factor = 0.0
                if scene_obj.actor:
                    self.scene_manager._update_object_visual(scene_obj)
            
            self.scene_manager.cleanup_lights()
            print("🔄 Scene reset")
    
    def _cleanup_performance(self):
        """Periodic cleanup."""
        if self.scene_manager:
            self.scene_manager.cleanup_lights()
    
    def _update_render(self):
        """Update render - NO RECURSION."""
        if self.performance_monitor:
            self.performance_monitor.register_frame()
        
        # Update scene info periodically
        if hasattr(self, '_last_scene_update'):
            if time.time() - self._last_scene_update > 2.0:
                self._update_scene_info()
        else:
            self._update_scene_info()
    
    def _update_scene_info(self):
        """Update scene info display."""
        try:
            if self.scene_manager:
                stats = self.scene_manager.get_scene_stats()
                
                info_text = f"""Objects: {stats['total_objects']}
Success: {stats['successful_objects']}
Active: {stats['active_objects']}
Notes: {stats['total_active_notes']}
Morph: {stats['global_morph_factor']:.2f}
Coverage: {stats['note_mapping_coverage']} notes"""
                
                self.scene_info_text.setPlainText(info_text)
                self._last_scene_update = time.time()
            else:
                self.scene_info_text.setPlainText("Scene Manager: Not Available")
        except Exception as e:
            self.scene_info_text.setPlainText(f"Error: {e}")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
MIDI Morphing Visualizer - Step 3: Clean Fixed

This is a completely clean version that resolves:
• All syntax errors
• QtInteractor compatibility issues  
• FPS update recursion problems
• Performance monitoring stability

Features:
• Multiple objects responding to note ranges
• Global morphing with real-time control
• Robust 3D visualization with fallback
• Fixed performance monitoring
• MIDI integration

Note Ranges:
• Bass: C1-B2 → Blue Sphere
• Melody: C3-B4 → Green Cube  
• Treble: C5-B6 → Orange Cylinder
• High: C7-C8 → Magenta Icosahedron
        """
        
        QMessageBox.about(self, "About", about_text.strip())
    
    def closeEvent(self, event):
        """Clean shutdown."""
        print("Shutting down Clean Morphing Window...")
        
        try:
            if self.midi_handler:
                self.midi_handler.stop()
                self.midi_handler.wait()
        except:
            pass
        
        try:
            if self.performance_monitor:
                self.performance_monitor.stop()
                self.performance_monitor.wait()
        except:
            pass
        
        self.cleanup_timer.stop()
        self.render_timer.stop()
        
        print("✅ Clean shutdown complete")
        event.accept()

# =============================================================================
# Main Application Entry Point
# =============================================================================

def main():
    """Main application entry point."""
    
    print("=" * 70)
    print("🎵 MIDI Morphing Visualizer - Step 3: Clean Fixed 🎵")
    print("=" * 70)
    print()
    print("This is a completely clean version with all issues resolved:")
    print()
    print("🔧 ALL FIXES APPLIED:")
    print("✅ No syntax errors")
    print("✅ QtInteractor compatibility wrapper")
    print("✅ FPS recursion completely eliminated")
    print("✅ Clean performance monitoring")
    print("✅ Robust 3D handling with fallback")
    print("✅ Simplified and reliable code")
    print()
    print("🎯 FEATURES:")
    print("✅ Enhanced Scene Manager with 4 objects")
    print("✅ Note range mapping to different objects")
    print("✅ Global morphing with real-time control")
    print("✅ 3D visualization or graceful fallback")
    print("✅ MIDI integration with device detection")
    print("✅ Performance monitoring without crashes")
    print()
    print("🎵 NOTE MAPPING:")
    print("🔵 Bass (C1-B2, notes 24-47) → Blue Sphere")
    print("🟢 Melody (C3-B4, notes 48-71) → Green Cube")
    print("🟠 Treble (C5-B6, notes 72-95) → Orange Cylinder")  
    print("🟣 High (C7-C8, notes 96-108) → Magenta Icosahedron")
    print()
    
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer - Step 3 Clean")
    
    try:
        window = CleanMorphingWindow()
        window.resize(1200, 800)
        window.show()
        
        print("🚀 Clean MIDI Morphing Visualizer (Step 3) is ready!")
        print()
        print("📋 STATUS CHECK:")
        print("• Check '3D Status' - should show ✅ Working or ❌ Failed")
        print("• No syntax errors or recursion crashes")
        print("• All systems should start cleanly")
        print()
        print("🧪 TESTING:")
        print("1. 'Test MIDI Note' - cycles through all 4 ranges")
        print("2. 'Test Morphing' - animates the morph slider")
        print("3. Play MIDI notes to see objects respond")
        print("4. Use modulation wheel (CC1) to control morphing")
        print()
        print("Either 3D works perfectly or fails gracefully! 🎆")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
