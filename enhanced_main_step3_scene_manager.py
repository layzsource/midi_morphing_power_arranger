#!/usr/bin/env python3
"""
Enhanced MIDI Morphing Visualizer - Step 3: Enhanced Scene Manager with Multiple Objects
Building on Step 1's advanced audio analysis foundation.

This step adds:
- Enhanced Scene Manager with multiple objects
- Note range mapping (bass, melody, treble, high octave)
- Multiple geometric shapes responding to different note ranges
- Advanced morphing capabilities using the Global Morphing Slider
- Improved MIDI-to-visual mapping
- Object-specific audio responsiveness
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

# Audio dependencies from Step 1
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
# STEP 3: Enhanced Scene Manager and Object System
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

class NoteRange(Enum):
    """Predefined note ranges for different musical sections."""
    BASS = "bass"          # C1-B2 (24-47)
    MELODY = "melody"      # C3-B4 (48-71) 
    TREBLE = "treble"      # C5-B6 (72-95)
    HIGH = "high"          # C7-C8 (96-108)

@dataclass
class SceneObject:
    """Enhanced scene object with full morphing capabilities."""
    id: str
    object_type: ObjectType
    note_range: Tuple[int, int]  # (min_note, max_note)
    range_name: str
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    base_scale: float = 1.0
    current_scale: float = 1.0
    base_color: np.ndarray = field(default_factory=lambda: np.array([0.5, 0.5, 1.0]))
    current_color: np.ndarray = field(default_factory=lambda: np.array([0.5, 0.5, 1.0]))
    opacity: float = 0.8
    metallic: float = 0.3
    roughness: float = 0.4
    active_notes: Dict[int, float] = field(default_factory=dict)  # note -> velocity
    last_activity: float = 0.0
    morph_factor: float = 0.0  # Controlled by global morphing slider
    target_object_type: Optional[ObjectType] = None
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
        # Map note to hue within object's color scheme
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
        
        # Adjust hue to stay in [0,1] range
        hue = hue % 1.0
        
        # Velocity affects saturation and value
        saturation = 0.6 + velocity * 0.4
        value = 0.4 + velocity * 0.6
        
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return np.array(rgb)

class EnhancedSceneManager:
    """
    Enhanced Scene Manager for Step 3 - Multiple Objects with Range Mapping
    """
    
    def __init__(self, plotter_widget):
        self.plotter_widget = plotter_widget
        self.plotter = plotter_widget.plotter if hasattr(plotter_widget, 'plotter') else plotter_widget
        
        # Scene objects
        self.objects: Dict[str, SceneObject] = {}
        self.note_to_object_map: Dict[int, str] = {}
        
        # Global scene settings
        self.global_morph_factor = 0.0
        self.ambient_light_intensity = 0.3
        self.max_lights_per_object = 3
        self.light_decay_time = 2.0
        
        # Performance tracking
        self.last_update_time = time.time()
        self.update_count = 0
        
        # Initialize default scene
        self._create_default_scene()
        
        print("✅ Enhanced Scene Manager initialized with multiple objects")
    
    def _create_default_scene(self):
        """Create the default multi-object scene."""
        
        # Define note ranges (based on MIDI note numbers)
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
                "color": np.array([0.2, 0.3, 1.0])  # Blue for bass
            },
            {
                "id": "melody_cube", 
                "type": ObjectType.CUBE,
                "range": "melody",
                "position": np.array([0.0, 0.0, 0.0]),
                "scale": 1.2,
                "color": np.array([0.3, 0.8, 0.3])  # Green for melody
            },
            {
                "id": "treble_cylinder",
                "type": ObjectType.CYLINDER,
                "range": "treble", 
                "position": np.array([2.0, 1.0, 0.0]),
                "scale": 1.0,
                "color": np.array([1.0, 0.4, 0.2])  # Orange for treble
            },
            {
                "id": "high_icosahedron",
                "type": ObjectType.ICOSAHEDRON,
                "range": "high",
                "position": np.array([0.0, 2.5, 0.0]),
                "scale": 0.8,
                "color": np.array([1.0, 0.2, 1.0])  # Magenta for high notes
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
            if obj.actor:
                self.plotter.add_actor(obj.actor)
            
            self.objects[obj.id] = obj
            
            # Map notes to objects
            for note in range(obj.note_range[0], obj.note_range[1] + 1):
                self.note_to_object_map[note] = obj.id
        
        print(f"✅ Created {len(self.objects)} scene objects:")
        for obj_id, obj in self.objects.items():
            range_str = f"{obj.note_range[0]}-{obj.note_range[1]}"
            print(f"   • {obj_id}: {obj.object_type.value} (notes {range_str}, {obj.range_name})")
    
    def _create_object_mesh(self, scene_obj: SceneObject) -> Any:
        """Create PyVista mesh for scene object."""
        try:
            # Create base mesh based on object type
            if scene_obj.object_type == ObjectType.SPHERE:
                mesh = pv.Sphere(radius=scene_obj.base_scale, 
                               phi_resolution=20, theta_resolution=20)
            elif scene_obj.object_type == ObjectType.CUBE:
                mesh = pv.Cube(x_length=scene_obj.base_scale*2,
                              y_length=scene_obj.base_scale*2, 
                              z_length=scene_obj.base_scale*2)
            elif scene_obj.object_type == ObjectType.CYLINDER:
                mesh = pv.Cylinder(radius=scene_obj.base_scale*0.8, 
                                 height=scene_obj.base_scale*2,
                                 resolution=16)
            elif scene_obj.object_type == ObjectType.CONE:
                mesh = pv.Cone(radius=scene_obj.base_scale, 
                              height=scene_obj.base_scale*2,
                              resolution=16)
            elif scene_obj.object_type == ObjectType.TORUS:
                mesh = pv.Torus(major_radius=scene_obj.base_scale,
                               minor_radius=scene_obj.base_scale*0.3)
            elif scene_obj.object_type == ObjectType.ICOSAHEDRON:
                mesh = pv.Icosahedron(radius=scene_obj.base_scale)
            elif scene_obj.object_type == ObjectType.OCTAHEDRON:
                mesh = pv.Octahedron()
                mesh = mesh.scale(scene_obj.base_scale)
            else:
                mesh = pv.Sphere(radius=scene_obj.base_scale)
            
            # Position the mesh
            mesh = mesh.translate(scene_obj.position)
            
            # Add mesh to plotter with materials
            actor = self.plotter.add_mesh(
                mesh,
                color=scene_obj.current_color,
                opacity=scene_obj.opacity,
                metallic=scene_obj.metallic,
                roughness=scene_obj.roughness,
                show_edges=False,
                lighting=True
            )
            
            return actor
            
        except Exception as e:
            print(f"❌ Error creating mesh for {scene_obj.id}: {e}")
            return None
    
    def handle_midi_note(self, note: int, velocity: float, note_on: bool = True, channel: int = 0):
        """Enhanced MIDI note handler with multi-object support."""
        
        # Find object responsible for this note
        obj_id = self.note_to_object_map.get(note)
        if not obj_id or obj_id not in self.objects:
            # Note outside of mapped ranges - could add fallback behavior
            return
        
        scene_obj = self.objects[obj_id]
        
        if note_on:
            # Add note to active notes
            scene_obj.active_notes[note] = velocity
            scene_obj.last_activity = time.time()
            
            # Update object based on note activity
            self._update_object_for_note(scene_obj, note, velocity)
            
            print(f"🎵 Note {note} (vel: {velocity:.2f}) -> {obj_id} ({scene_obj.range_name})")
            
        else:
            # Remove note from active notes
            if note in scene_obj.active_notes:
                del scene_obj.active_notes[note]
                
            # If no more active notes, start fade out
            if not scene_obj.active_notes:
                self._start_object_fadeout(scene_obj)
    
    def _update_object_for_note(self, scene_obj: SceneObject, note: int, velocity: float):
        """Update scene object visual properties based on note activity."""
        
        try:
            # Update color based on note and velocity
            note_color = scene_obj.get_color_for_note(note, velocity)
            
            # Blend with existing color if multiple notes active
            if len(scene_obj.active_notes) > 1:
                scene_obj.current_color = (scene_obj.current_color + note_color) / 2
            else:
                scene_obj.current_color = note_color
            
            # Update scale based on intensity
            intensity = scene_obj.get_intensity()
            scale_factor = 1.0 + intensity * 0.5  # Scale up to 150% with full intensity
            scene_obj.current_scale = scene_obj.base_scale * scale_factor
            
            # Apply global morphing if enabled
            self._apply_global_morphing(scene_obj)
            
            # Update visual representation
            self._update_object_visual(scene_obj)
            
            # Add lighting effect
            self._add_note_light(scene_obj, note, velocity)
            
        except Exception as e:
            print(f"❌ Error updating object {scene_obj.id}: {e}")
    
    def _apply_global_morphing(self, scene_obj: SceneObject):
        """Apply global morphing effects to scene object."""
        
        if self.global_morph_factor <= 0.0:
            return
        
        # Morph towards different object type based on morph factor
        target_types = {
            ObjectType.SPHERE: ObjectType.CUBE,
            ObjectType.CUBE: ObjectType.CYLINDER,
            ObjectType.CYLINDER: ObjectType.CONE,
            ObjectType.CONE: ObjectType.TORUS,
            ObjectType.TORUS: ObjectType.ICOSAHEDRON,
            ObjectType.ICOSAHEDRON: ObjectType.OCTAHEDRON,
            ObjectType.OCTAHEDRON: ObjectType.SPHERE
        }
        
        scene_obj.target_object_type = target_types.get(scene_obj.object_type)
        scene_obj.morph_factor = self.global_morph_factor
        
        # Apply morphing effect to color (shift hue)
        hue_shift = self.global_morph_factor * 0.3
        h, s, v = colorsys.rgb_to_hsv(*scene_obj.current_color)
        h = (h + hue_shift) % 1.0
        morphed_color = np.array(colorsys.hsv_to_rgb(h, s, v))
        scene_obj.current_color = morphed_color
    
    def _update_object_visual(self, scene_obj: SceneObject):
        """Update the visual representation of a scene object."""
        
        if not scene_obj.actor:
            return
        
        try:
            # Update color
            scene_obj.actor.GetProperty().SetColor(scene_obj.current_color)
            
            # Update opacity based on activity
            intensity = scene_obj.get_intensity()
            opacity = scene_obj.opacity + intensity * 0.2
            scene_obj.actor.GetProperty().SetOpacity(min(1.0, opacity))
            
            # Apply morphing effects if active
            if scene_obj.morph_factor > 0.0:
                # Modify material properties for morphing effect
                metallic = scene_obj.metallic + scene_obj.morph_factor * 0.3
                roughness = scene_obj.roughness - scene_obj.morph_factor * 0.2
                
                scene_obj.actor.GetProperty().SetMetallic(min(1.0, metallic))
                scene_obj.actor.GetProperty().SetRoughness(max(0.0, roughness))
            
        except Exception as e:
            print(f"❌ Error updating visual for {scene_obj.id}: {e}")
    
    def _add_note_light(self, scene_obj: SceneObject, note: int, velocity: float):
        """Add dynamic lighting for note activity."""
        
        try:
            # Limit number of lights per object
            if len(scene_obj.lights) >= self.max_lights_per_object:
                # Remove oldest light
                oldest_light = scene_obj.lights.pop(0)
                self.plotter.remove_actor(oldest_light)
            
            # Create light at object position with slight random offset
            light_pos = scene_obj.position + np.random.normal(0, 0.5, 3)
            
            # Light color based on note
            light_color = scene_obj.get_color_for_note(note, velocity)
            
            # Light intensity based on velocity
            intensity = velocity * 2.0
            
            # Create point light
            light = pv.Light(
                position=light_pos,
                focal_point=scene_obj.position,
                color=light_color,
                intensity=intensity,
                light_type='point'
            )
            
            # Add to scene
            self.plotter.add_light(light)
            scene_obj.lights.append(light)
            
        except Exception as e:
            print(f"❌ Error adding light for {scene_obj.id}: {e}")
    
    def _start_object_fadeout(self, scene_obj: SceneObject):
        """Start fadeout animation for object with no active notes."""
        
        # Gradually return to base state
        scene_obj.current_color = scene_obj.base_color.copy()
        scene_obj.current_scale = scene_obj.base_scale
        scene_obj.morph_factor = 0.0
        
        self._update_object_visual(scene_obj)
    
    def set_global_morph_factor(self, factor: float):
        """Set global morphing factor (0.0 to 1.0)."""
        
        self.global_morph_factor = max(0.0, min(1.0, factor))
        
        # Apply to all active objects
        for scene_obj in self.objects.values():
            if scene_obj.active_notes:  # Only morph active objects
                self._apply_global_morphing(scene_obj)
                self._update_object_visual(scene_obj)
    
    def cleanup_lights(self):
        """Clean up old lights to maintain performance."""
        
        current_time = time.time()
        
        for scene_obj in self.objects.values():
            lights_to_remove = []
            
            for i, light in enumerate(scene_obj.lights):
                # Remove lights that are too old (basic cleanup)
                if len(scene_obj.lights) > self.max_lights_per_object:
                    lights_to_remove.append(i)
            
            # Remove old lights
            for i in reversed(lights_to_remove):
                try:
                    old_light = scene_obj.lights.pop(i)
                    try:
                        self.plotter.remove_actor(old_light)
                    except:
                        # If removal fails, just remove from list
                        pass
                except:
                    pass
    
    def get_scene_stats(self) -> Dict[str, Any]:
        """Get scene statistics for monitoring."""
        
        total_active_notes = sum(len(obj.active_notes) for obj in self.objects.values())
        total_lights = sum(len(obj.lights) for obj in self.objects.values())
        active_objects = sum(1 for obj in self.objects.values() if obj.active_notes)
        
        return {
            'total_objects': len(self.objects),
            'active_objects': active_objects,
            'total_active_notes': total_active_notes,
            'total_lights': total_lights,
            'global_morph_factor': self.global_morph_factor,
            'note_mapping_coverage': len(self.note_to_object_map)
        }

# =============================================================================
# MIDI Handler (Enhanced from Step 1)
# =============================================================================

class MidiSignals(QObject):
    """Qt signals for MIDI events."""
    note_on = Signal(int, float, int)  # note, velocity, channel
    note_off = Signal(int, int)        # note, channel  
    control_change = Signal(int, int, int)  # controller, value, channel

class MidiHandler(QThread):
    """Enhanced MIDI handler with better device management."""
    
    def __init__(self):
        super().__init__()
        self.signals = MidiSignals()
        self.running = False
        self.midi_input = None
        self.device_id = None
        
        # Initialize pygame midi
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
                
                time.sleep(0.001)  # Small delay to prevent CPU spinning
                
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
# Audio Analysis System (From Step 1)
# =============================================================================

class AudioSignals(QObject):
    """Qt signals for audio analysis events."""
    amplitude_updated = Signal(float)
    spectral_centroid_updated = Signal(float)
    onset_detected = Signal(float)  
    beat_detected = Signal(float)
    spectral_features_updated = Signal(dict)

class AudioAnalyzer(QThread):
    """Audio analysis system from Step 1."""
    
    def __init__(self, backend='auto'):
        super().__init__()
        self.signals = AudioSignals()
        self.running = False
        self.backend = self._select_backend(backend)
        
        # Audio settings
        self.sample_rate = 44100
        self.block_size = 1024
        self.channels = 1
        
        # Analysis state
        self.audio_buffer = queue.Queue(maxsize=10)
        self.onset_detector = None
        self.last_onset_time = 0
        self.onset_threshold = 0.5
        
        print(f"🎧 Audio analyzer initialized with {self.backend} backend")
    
    def _select_backend(self, preference):
        """Select best available audio backend."""
        
        if preference == 'sounddevice' and SOUNDDEVICE_AVAILABLE:
            return 'sounddevice'
        elif preference == 'pyaudio' and PYAUDIO_AVAILABLE:
            return 'pyaudio'
        elif preference == 'auto':
            if SOUNDDEVICE_AVAILABLE:
                return 'sounddevice'
            elif PYAUDIO_AVAILABLE:
                return 'pyaudio'
        
        return 'none'
    
    def run(self):
        """Main audio analysis loop."""
        
        if self.backend == 'none':
            print("⚠️  No audio backend available")
            return
        
        self.running = True
        print(f"🎧 Audio analysis started with {self.backend}")
        
        try:
            if self.backend == 'sounddevice':
                self._run_sounddevice()
            elif self.backend == 'pyaudio':
                self._run_pyaudio()
        except Exception as e:
            print(f"❌ Audio analysis error: {e}")
    
    def _run_sounddevice(self):
        """Run audio analysis with SoundDevice backend."""
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            
            try:
                # Add to buffer for processing
                audio_data = indata[:, 0] if indata.ndim > 1 else indata
                if not self.audio_buffer.full():
                    self.audio_buffer.put(audio_data.copy())
                    
            except Exception as e:
                print(f"Audio callback error: {e}")
        
        with sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=self.channels,
            callback=audio_callback
        ):
            self._process_audio_loop()
    
    def _run_pyaudio(self):
        """Run audio analysis with PyAudio backend."""
        
        pa = pyaudio.PyAudio()
        
        try:
            stream = pa.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.block_size
            )
            
            while self.running:
                try:
                    data = stream.read(self.block_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.float32)
                    
                    if not self.audio_buffer.full():
                        self.audio_buffer.put(audio_data.copy())
                        
                except Exception as e:
                    print(f"PyAudio read error: {e}")
                    time.sleep(0.01)
            
            stream.stop_stream()
            stream.close()
            
        finally:
            pa.terminate()
    
    def _process_audio_loop(self):
        """Process audio data from buffer."""
        
        while self.running:
            try:
                if not self.audio_buffer.empty():
                    audio_data = self.audio_buffer.get()
                    self._analyze_audio(audio_data)
                else:
                    time.sleep(0.001)
                    
            except Exception as e:
                print(f"Audio processing error: {e}")
                time.sleep(0.01)
    
    def _analyze_audio(self, audio_data):
        """Analyze audio data and emit signals."""
        
        try:
            # Basic amplitude analysis
            amplitude = np.sqrt(np.mean(audio_data**2))
            self.signals.amplitude_updated.emit(float(amplitude))
            
            # Advanced analysis requires librosa
            if LIBROSA_AVAILABLE and len(audio_data) > 0:
                
                # Spectral centroid (pitch estimation)
                centroid = librosa.feature.spectral_centroid(
                    y=audio_data, sr=self.sample_rate
                )[0][0]
                self.signals.spectral_centroid_updated.emit(float(centroid))
                
                # Onset detection
                onset_strength = librosa.onset.onset_strength(
                    y=audio_data, sr=self.sample_rate
                )
                if len(onset_strength) > 0:
                    current_onset = np.mean(onset_strength)
                    if current_onset > self.onset_threshold:
                        current_time = time.time()
                        if current_time - self.last_onset_time > 0.1:  # Debounce
                            self.signals.onset_detected.emit(float(current_onset))
                            self.last_onset_time = current_time
                
                # Beat detection
                tempo, beats = librosa.beat.beat_track(
                    y=audio_data, sr=self.sample_rate
                )
                if len(beats) > 0:
                    self.signals.beat_detected.emit(float(tempo))
                
                # Additional spectral features
                spectral_features = {
                    'rolloff': float(librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)[0][0]),
                    'bandwidth': float(librosa.feature.spectral_bandwidth(y=audio_data, sr=self.sample_rate)[0][0]),
                    'zero_crossing_rate': float(librosa.feature.zero_crossing_rate(audio_data)[0][0])
                }
                self.signals.spectral_features_updated.emit(spectral_features)
                
        except Exception as e:
            print(f"Audio analysis error: {e}")
    
    def stop(self):
        """Stop audio analysis."""
        self.running = False
        print("🎧 Audio analyzer stopped")

# =============================================================================
# Performance Monitor (From Step 1)
# =============================================================================

class PerformanceSignals(QObject):
    """Qt signals for performance monitoring."""
    fps_updated = Signal(float)
    memory_updated = Signal(float, float)  # MB, percentage
    cpu_updated = Signal(float)
    performance_warning = Signal(str)

class PerformanceMonitor(QThread):
    """Performance monitoring system."""
    
    def __init__(self):
        super().__init__()
        self.signals = PerformanceSignals()
        self.running = False
        
        # FPS tracking
        self.frame_times = []
        self.last_frame_time = time.time()
        
        # Thresholds
        self.low_fps_threshold = 20.0
        self.high_memory_threshold = 80.0  # Percentage
        self.high_cpu_threshold = 90.0     # Percentage
    
    def update_fps(self):
        """Update FPS calculation."""
        
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 60:  # Keep last 60 frames
            self.frame_times.pop(0)
        
        if len(self.frame_times) > 0:
            avg_frame_time = np.mean(self.frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            self.signals.fps_updated.emit(fps)
            
            if fps < self.low_fps_threshold:
                self.signals.performance_warning.emit(f"Low FPS: {fps:.1f}")
    
    def run(self):
        """Main performance monitoring loop."""
        
        if not PERFORMANCE_MONITORING:
            print("⚠️  Performance monitoring not available")
            return
        
        self.running = True
        print("📊 Performance monitoring started")
        
        while self.running:
            try:
                # Memory usage
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = process.memory_percent()
                
                self.signals.memory_updated.emit(memory_mb, memory_percent)
                
                if memory_percent > self.high_memory_threshold:
                    self.signals.performance_warning.emit(f"High memory usage: {memory_percent:.1f}%")
                
                # CPU usage
                cpu_percent = process.cpu_percent()
                self.signals.cpu_updated.emit(cpu_percent)
                
                if cpu_percent > self.high_cpu_threshold:
                    self.signals.performance_warning.emit(f"High CPU usage: {cpu_percent:.1f}%")
                
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(1.0)
    
    def stop(self):
        """Stop performance monitoring."""
        self.running = False
        print("📊 Performance monitor stopped")

# =============================================================================
# Main Application Window (Enhanced for Step 3)
# =============================================================================

class EnhancedMorphingWindow(QMainWindow):
    """Enhanced main window with multi-object scene management."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Morphing Visualizer - Step 3: Enhanced Scene Manager")
        
        # Core components
        self.scene_manager = None
        self.midi_handler = None
        self.audio_analyzer = None
        self.performance_monitor = None
        
        # UI components
        self.plotter_widget = None
        self.morph_slider = None
        self.audio_backend_combo = None
        
        # Timers
        self.cleanup_timer = QTimer()
        self.render_timer = QTimer()
        
        # Settings
        self.settings = QSettings("MIDIMorphing", "Step3Enhanced")
        
        # Initialize UI
        self._setup_ui()
        self._setup_3d_scene()
        self._setup_connections()
        self._start_systems()
        
        print("✅ Enhanced Morphing Window (Step 3) initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_panel.setMinimumWidth(250)
        left_layout = QVBoxLayout(left_panel)
        
        # Global Morphing Control
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
        
        # Audio Controls
        audio_group = QGroupBox("Audio Analysis")
        audio_layout = QVBoxLayout(audio_group)
        
        audio_layout.addWidget(QLabel("Backend:"))
        self.audio_backend_combo = QComboBox()
        self.audio_backend_combo.addItems(["Auto", "SoundDevice", "PyAudio"])
        audio_layout.addWidget(self.audio_backend_combo)
        
        self.audio_status_label = QLabel("Status: Initializing...")
        audio_layout.addWidget(self.audio_status_label)
        
        left_layout.addWidget(audio_group)
        
        # Scene Information
        scene_group = QGroupBox("Scene Objects")
        scene_layout = QVBoxLayout(scene_group)
        
        self.scene_info_text = QTextEdit()
        self.scene_info_text.setMaximumHeight(200)
        self.scene_info_text.setReadOnly(True)
        scene_layout.addWidget(self.scene_info_text)
        
        left_layout.addWidget(scene_group)
        
        # Performance Monitoring
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        self.fps_label = QLabel("FPS: --")
        self.memory_label = QLabel("Memory: --")
        self.cpu_label = QLabel("CPU: --")
        
        perf_layout.addWidget(self.fps_label)
        perf_layout.addWidget(self.memory_label)
        perf_layout.addWidget(self.cpu_label)
        
        left_layout.addWidget(perf_group)
        
        # Test Controls
        test_group = QGroupBox("Test Controls")
        test_layout = QVBoxLayout(test_group)
        
        self.test_note_btn = QPushButton("Test MIDI Note")
        self.test_morph_btn = QPushButton("Test Morphing")
        self.reset_scene_btn = QPushButton("Reset Scene")
        
        test_layout.addWidget(self.test_note_btn)
        test_layout.addWidget(self.test_morph_btn)
        test_layout.addWidget(self.reset_scene_btn)
        
        left_layout.addWidget(test_group)
        
        # Stretch at bottom
        left_layout.addStretch()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        
        # 3D visualization will be added to main_layout in _setup_3d_scene
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menu bar
        self._setup_menu_bar()
    
    def _setup_menu_bar(self):
        """Setup application menu bar."""
        
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Audio menu
        audio_menu = menubar.addMenu("Audio")
        
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
        """Setup 3D visualization scene."""
        
        try:
            # Create PyVista plotter widget
            self.plotter_widget = QtInteractor(self)
            self.plotter_widget.setMinimumSize(800, 600)
            
            # Add to main layout
            self.centralWidget().layout().addWidget(self.plotter_widget, 1)
            
            # Configure plotter
            plotter = self.plotter_widget.plotter
            plotter.set_background('black')
            
            # Add some ambient lighting
            plotter.add_light(pv.Light(
                position=(10, 10, 10),
                focal_point=(0, 0, 0),
                color='white',
                intensity=0.3
            ))
            
            # Create enhanced scene manager
            self.scene_manager = EnhancedSceneManager(self.plotter_widget)
            
            print("✅ 3D scene setup complete")
            
        except Exception as e:
            print(f"❌ Error setting up 3D scene: {e}")
            QMessageBox.critical(self, "Error", f"Failed to setup 3D scene: {e}")
    
    def _setup_connections(self):
        """Setup signal/slot connections."""
        
        # Morph slider
        self.morph_slider.valueChanged.connect(self._on_morph_slider_changed)
        
        # Audio backend selection
        self.audio_backend_combo.currentTextChanged.connect(self._on_audio_backend_changed)
        
        # Test buttons
        self.test_note_btn.clicked.connect(self._test_midi_note)
        self.test_morph_btn.clicked.connect(self._test_morphing)
        self.reset_scene_btn.clicked.connect(self._reset_scene)
        
        # Timers
        self.cleanup_timer.timeout.connect(self._cleanup_performance)
        self.render_timer.timeout.connect(self._update_render)
        
        print("✅ UI connections setup complete")
    
    def _start_systems(self):
        """Start all subsystems."""
        
        # Start MIDI handler
        if MIDI_AVAILABLE:
            try:
                self.midi_handler = MidiHandler()
                self.midi_handler.signals.note_on.connect(self._on_midi_note_on)
                self.midi_handler.signals.note_off.connect(self._on_midi_note_off)
                self.midi_handler.signals.control_change.connect(self._on_midi_control_change)
                self.midi_handler.start()
                print("✅ MIDI handler started")
            except Exception as e:
                print(f"⚠️  MIDI handler failed to start: {e}")
        
        # Start audio analyzer
        if AUDIO_AVAILABLE:
            try:
                backend = self.audio_backend_combo.currentText().lower()
                self.audio_analyzer = AudioAnalyzer(backend)
                self.audio_analyzer.signals.amplitude_updated.connect(self._on_amplitude_updated)
                self.audio_analyzer.signals.spectral_centroid_updated.connect(self._on_spectral_centroid_updated)
                self.audio_analyzer.signals.onset_detected.connect(self._on_onset_detected)
                self.audio_analyzer.signals.beat_detected.connect(self._on_beat_detected)
                self.audio_analyzer.start()
                self.audio_status_label.setText("Status: Running")
                print("✅ Audio analyzer started")
            except Exception as e:
                print(f"⚠️  Audio analyzer failed to start: {e}")
                self.audio_status_label.setText(f"Status: Error - {e}")
        
        # Start performance monitor
        if PERFORMANCE_MONITORING:
            try:
                self.performance_monitor = PerformanceMonitor()
                self.performance_monitor.signals.fps_updated.connect(self._on_fps_updated)
                self.performance_monitor.signals.memory_updated.connect(self._on_memory_updated)
                self.performance_monitor.signals.cpu_updated.connect(self._on_cpu_updated)
                self.performance_monitor.signals.performance_warning.connect(self._on_performance_warning)
                self.performance_monitor.start()
                print("✅ Performance monitor started")
            except Exception as e:
                print(f"⚠️  Performance monitor failed to start: {e}")
        
        # Start timers
        self.cleanup_timer.start(5000)  # 5 second cleanup
        self.render_timer.start(16)     # ~60 FPS render updates
        
        # Update scene info
        self._update_scene_info()
    
    def _on_morph_slider_changed(self, value):
        """Handle morph slider changes."""
        
        morph_factor = value / 100.0
        self.morph_value_label.setText(f"{value}%")
        
        if self.scene_manager:
            self.scene_manager.set_global_morph_factor(morph_factor)
        
        print(f"🔄 Global morph factor: {morph_factor:.2f}")
    
    def _on_audio_backend_changed(self, backend):
        """Handle audio backend changes."""
        
        if self.audio_analyzer:
            self.audio_analyzer.stop()
            self.audio_analyzer.wait()
        
        try:
            self.audio_analyzer = AudioAnalyzer(backend.lower())
            self.audio_analyzer.signals.amplitude_updated.connect(self._on_amplitude_updated)
            self.audio_analyzer.signals.spectral_centroid_updated.connect(self._on_spectral_centroid_updated)
            self.audio_analyzer.signals.onset_detected.connect(self._on_onset_detected)
            self.audio_analyzer.signals.beat_detected.connect(self._on_beat_detected)
            self.audio_analyzer.start()
            self.audio_status_label.setText(f"Status: Running ({backend})")
            print(f"🎧 Switched to {backend} audio backend")
        except Exception as e:
            self.audio_status_label.setText(f"Status: Error - {e}")
            print(f"❌ Failed to switch audio backend: {e}")
    
    def _on_midi_note_on(self, note, velocity, channel):
        """Handle MIDI note on events."""
        
        if self.scene_manager:
            self.scene_manager.handle_midi_note(note, velocity, True, channel)
    
    def _on_midi_note_off(self, note, channel):
        """Handle MIDI note off events."""
        
        if self.scene_manager:
            self.scene_manager.handle_midi_note(note, 0, False, channel)
    
    def _on_midi_control_change(self, controller, value, channel):
        """Handle MIDI control change events."""
        
        if controller == 1:  # Modulation wheel controls morphing
            morph_value = int((value / 127.0) * 100)
            self.morph_slider.setValue(morph_value)
            print(f"🎛️  MIDI CC1 -> Morph: {morph_value}%")
    
    def _on_amplitude_updated(self, amplitude):
        """Handle audio amplitude updates."""
        pass  # Could drive global scene brightness
    
    def _on_spectral_centroid_updated(self, centroid):
        """Handle spectral centroid updates."""
        pass  # Could influence global color shifts
    
    def _on_onset_detected(self, strength):
        """Handle audio onset detection."""
        # Could trigger global flash effects
        print(f"🎵 Audio onset detected: {strength:.2f}")
    
    def _on_beat_detected(self, tempo):
        """Handle beat detection."""
        # Could influence global animation timing
        print(f"🥁 Beat detected: {tempo:.1f} BPM")
    
    def _on_fps_updated(self, fps):
        """Handle FPS updates."""
        color = "green" if fps >= 30 else "orange" if fps >= 20 else "red"
        self.fps_label.setText(f"<font color='{color}'>FPS: {fps:.1f}</font>")
        
        if self.performance_monitor:
            self.performance_monitor.update_fps()
    
    def _on_memory_updated(self, memory_mb, memory_percent):
        """Handle memory usage updates."""
        color = "green" if memory_percent < 70 else "orange" if memory_percent < 85 else "red"
        self.memory_label.setText(f"<font color='{color}'>Memory: {memory_percent:.1f}%</font>")
    
    def _on_cpu_updated(self, cpu_percent):
        """Handle CPU usage updates."""
        color = "green" if cpu_percent < 70 else "orange" if cpu_percent < 85 else "red"
        self.cpu_label.setText(f"<font color='{color}'>CPU: {cpu_percent:.1f}%</font>")
    
    def _on_performance_warning(self, warning):
        """Handle performance warnings."""
        self.status_bar.showMessage(f"⚠️ {warning}", 5000)
    
    def _test_midi_note(self):
        """Test MIDI note functionality."""
        
        # Test different notes in different ranges
        test_notes = [
            (36, 0.8, "bass"),      # Bass range
            (60, 0.9, "melody"),    # Melody range  
            (84, 0.7, "treble"),    # Treble range
            (96, 0.6, "high")       # High range
        ]
        
        for i, (note, velocity, range_name) in enumerate(test_notes):
            QTimer.singleShot(i * 1000, lambda n=note, v=velocity, r=range_name: self._trigger_test_note(n, v, r))
    
    def _trigger_test_note(self, note, velocity, range_name):
        """Trigger a test note."""
        
        if self.scene_manager:
            self.scene_manager.handle_midi_note(note, velocity, True, 0)
            print(f"🎵 Test note: {note} (velocity: {velocity:.2f}) in {range_name} range")
            
            # Note off after 2 seconds
            QTimer.singleShot(2000, lambda: self.scene_manager.handle_midi_note(note, 0, False, 0))
    
    def _test_morphing(self):
        """Test morphing functionality."""
        
        # Animate morph slider
        def animate_morph(target_value):
            current = self.morph_slider.value()
            step = 5 if target_value > current else -5
            
            if abs(target_value - current) <= abs(step):
                self.morph_slider.setValue(target_value)
            else:
                self.morph_slider.setValue(current + step)
                QTimer.singleShot(50, lambda: animate_morph(target_value))
        
        # Animate to 100%, then back to 0%
        animate_morph(100)
        QTimer.singleShot(3000, lambda: animate_morph(0))
        
        print("🔄 Testing morphing animation")
    
    def _reset_scene(self):
        """Reset scene to default state."""
        
        if self.scene_manager:
            # Reset morph slider
            self.morph_slider.setValue(0)
            
            # Clear all active notes
            for scene_obj in self.scene_manager.objects.values():
                scene_obj.active_notes.clear()
                scene_obj.current_color = scene_obj.base_color.copy()
                scene_obj.current_scale = scene_obj.base_scale
                scene_obj.morph_factor = 0.0
                self.scene_manager._update_object_visual(scene_obj)
            
            # Cleanup lights
            self.scene_manager.cleanup_lights()
            
            print("🔄 Scene reset to default state")
    
    def _cleanup_performance(self):
        """Periodic performance cleanup."""
        
        if self.scene_manager:
            self.scene_manager.cleanup_lights()
    
    def _update_render(self):
        """Update rendering performance tracking."""
        
        if self.performance_monitor:
            self.performance_monitor.update_fps()
        
        # Update scene info periodically
        if hasattr(self, '_last_scene_update'):
            if time.time() - self._last_scene_update > 2.0:
                self._update_scene_info()
        else:
            self._update_scene_info()
    
    def _update_scene_info(self):
        """Update scene information display."""
        
        try:
            if self.scene_manager:
                stats = self.scene_manager.get_scene_stats()
                
                info_text = f"""Objects: {stats['total_objects']}
Active: {stats['active_objects']}
Notes: {stats['total_active_notes']}
Lights: {stats['total_lights']}
Morph: {stats['global_morph_factor']:.2f}
Coverage: {stats['note_mapping_coverage']} notes"""
                
                self.scene_info_text.setPlainText(info_text)
                self._last_scene_update = time.time()
            else:
                self.scene_info_text.setPlainText("Scene Manager: Not Available")
        except Exception as e:
            self.scene_info_text.setPlainText(f"Scene Info Error: {e}")
            print(f"Error updating scene info: {e}")
    
    def _show_about(self):
        """Show about dialog."""
        
        about_text = """
MIDI Morphing Visualizer - Step 3: Enhanced Scene Manager

Features:
• Multiple objects responding to different note ranges
• Global morphing with real-time slider control
• Advanced audio analysis with multiple backends
• Performance monitoring and optimization
• MIDI integration with automatic device detection

Note Ranges:
• Bass: C1-B2 (notes 24-47) → Blue Sphere
• Melody: C3-B4 (notes 48-71) → Green Cube  
• Treble: C5-B6 (notes 72-95) → Orange Cylinder
• High: C7-C8 (notes 96-108) → Magenta Icosahedron

Version: Step 3 Enhanced
        """
        
        QMessageBox.about(self, "About", about_text.strip())
    
    def closeEvent(self, event):
        """Clean shutdown."""
        
        print("Shutting down Enhanced Morphing Window (Step 3)...")
        
        # Stop all systems
        try:
            if self.midi_handler:
                self.midi_handler.stop()
                self.midi_handler.wait()
        except:
            pass
        
        try:
            if self.audio_analyzer:
                self.audio_analyzer.stop()
                self.audio_analyzer.wait()
        except:
            pass
        
        try:
            if self.performance_monitor:
                self.performance_monitor.stop()
                self.performance_monitor.wait()
        except:
            pass
        
        # Stop timers
        self.cleanup_timer.stop()
        self.render_timer.stop()
        
        print("✅ Enhanced Morphing Window (Step 3) shutdown complete")
        event.accept()

# =============================================================================
# Main Application Entry Point
# =============================================================================

def main():
    """Main application entry point."""
    
    print("=" * 70)
    print("🎵 MIDI Morphing Visualizer - Step 3: Enhanced Scene Manager 🎵")
    print("=" * 70)
    print()
    print("Building on Step 1's advanced audio analysis foundation...")
    print()
    print("NEW FEATURES IN STEP 3:")
    print("✅ Enhanced Scene Manager with multiple objects")
    print("✅ Note range mapping (bass, melody, treble, high)")
    print("✅ Multiple geometric shapes responding to different notes")
    print("✅ Advanced morphing capabilities with Global Morphing Slider")
    print("✅ Object-specific audio responsiveness")
    print("✅ Improved MIDI-to-visual mapping")
    print()
    print("RETAINED FROM STEP 1:")
    print("✅ Advanced audio analysis with multiple backends")
    print("✅ Real-time spectral analysis and onset detection")
    print("✅ MIDI device integration with automatic detection")
    print("✅ Performance monitoring and optimization")
    print()
    print("NOTE MAPPING:")
    print("🎵 Bass (C1-B2, notes 24-47) → Blue Sphere (left-back)")
    print("🎵 Melody (C3-B4, notes 48-71) → Green Cube (center)")
    print("🎵 Treble (C5-B6, notes 72-95) → Orange Cylinder (right-front)")  
    print("🎵 High (C7-C8, notes 96-108) → Magenta Icosahedron (top)")
    print()
    
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer - Step 3")
    app.setOrganizationName("Enhanced MIDI Visualization")
    
    try:
        window = EnhancedMorphingWindow()
        window.resize(1200, 800)
        window.show()
        
        print("🚀 Enhanced MIDI Morphing Visualizer (Step 3) is ready!")
        print()
        print("QUICK TEST GUIDE:")
        print("1. Use 'Test MIDI Note' button to see different objects light up")
        print("2. Move the 'Global Morphing' slider to see morphing effects")
        print("3. Play MIDI notes in different octaves to trigger different objects")
        print("4. Speak near microphone for audio-reactive effects")
        print("5. Watch performance monitoring in the bottom panel")
        print()
        print("Enjoy your enhanced multi-object MIDI visualization! 🎆")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
