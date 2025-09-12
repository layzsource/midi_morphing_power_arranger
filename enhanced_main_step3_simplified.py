#!/usr/bin/env python3
"""
Enhanced MIDI Morphing Visualizer - Step 3: Simplified Fallback Version
This version works without 3D visualization for testing the enhanced scene manager logic.

Features:
- Enhanced Scene Manager with multiple objects (logic only)
- Note range mapping (bass, melody, treble, high)
- MIDI-to-object mapping
- Audio analysis from Step 1
- Performance monitoring
- Test functionality without 3D requirements
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
# Enhanced Scene Manager (Logic Only - No 3D Dependencies)
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
    """Enhanced scene object (logic only)."""
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
    active_notes: Dict[int, float] = field(default_factory=dict)  # note -> velocity
    last_activity: float = 0.0
    morph_factor: float = 0.0
    
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

class SimplifiedSceneManager:
    """
    Simplified Scene Manager for Step 3 - Logic Only (No 3D Dependencies)
    """
    
    def __init__(self):
        # Scene objects
        self.objects: Dict[str, SceneObject] = {}
        self.note_to_object_map: Dict[int, str] = {}
        
        # Global scene settings
        self.global_morph_factor = 0.0
        self.max_lights_per_object = 3
        
        # Performance tracking
        self.last_update_time = time.time()
        self.update_count = 0
        
        # Initialize default scene
        self._create_default_scene()
        
        print("✅ Simplified Scene Manager initialized with multiple objects")
    
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
            
            self.objects[obj.id] = obj
            
            # Map notes to objects
            for note in range(obj.note_range[0], obj.note_range[1] + 1):
                self.note_to_object_map[note] = obj.id
        
        print(f"✅ Created {len(self.objects)} scene objects:")
        for obj_id, obj in self.objects.items():
            range_str = f"{obj.note_range[0]}-{obj.note_range[1]}"
            print(f"   • {obj_id}: {obj.object_type.value} (notes {range_str}, {obj.range_name})")
    
    def handle_midi_note(self, note: int, velocity: float, note_on: bool = True, channel: int = 0):
        """Enhanced MIDI note handler with multi-object support."""
        
        # Find object responsible for this note
        obj_id = self.note_to_object_map.get(note)
        if not obj_id or obj_id not in self.objects:
            print(f"🎵 Note {note} outside mapped ranges")
            return
        
        scene_obj = self.objects[obj_id]
        
        if note_on:
            # Add note to active notes
            scene_obj.active_notes[note] = velocity
            scene_obj.last_activity = time.time()
            
            # Update object based on note activity
            self._update_object_for_note(scene_obj, note, velocity)
            
            print(f"🎵 Note {note} (vel: {velocity:.2f}) -> {obj_id} ({scene_obj.range_name}) [Intensity: {scene_obj.get_intensity():.2f}]")
            
        else:
            # Remove note from active notes
            if note in scene_obj.active_notes:
                del scene_obj.active_notes[note]
                print(f"🎵 Note {note} OFF -> {obj_id} ({scene_obj.range_name}) [Remaining: {len(scene_obj.active_notes)} notes]")
                
            # If no more active notes, start fade out
            if not scene_obj.active_notes:
                self._start_object_fadeout(scene_obj)
    
    def _update_object_for_note(self, scene_obj: SceneObject, note: int, velocity: float):
        """Update scene object properties based on note activity."""
        
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
            
            print(f"   Updated {scene_obj.id}: scale={scene_obj.current_scale:.2f}, color=RGB({scene_obj.current_color[0]:.2f},{scene_obj.current_color[1]:.2f},{scene_obj.current_color[2]:.2f})")
            
        except Exception as e:
            print(f"❌ Error updating object {scene_obj.id}: {e}")
    
    def _apply_global_morphing(self, scene_obj: SceneObject):
        """Apply global morphing effects to scene object."""
        
        if self.global_morph_factor <= 0.0:
            return
        
        scene_obj.morph_factor = self.global_morph_factor
        
        # Apply morphing effect to color (shift hue)
        hue_shift = self.global_morph_factor * 0.3
        h, s, v = colorsys.rgb_to_hsv(*scene_obj.current_color)
        h = (h + hue_shift) % 1.0
        morphed_color = np.array(colorsys.hsv_to_rgb(h, s, v))
        scene_obj.current_color = morphed_color
        
        print(f"   Morphing {scene_obj.id}: factor={self.global_morph_factor:.2f}")
    
    def _start_object_fadeout(self, scene_obj: SceneObject):
        """Start fadeout animation for object with no active notes."""
        
        # Gradually return to base state
        scene_obj.current_color = scene_obj.base_color.copy()
        scene_obj.current_scale = scene_obj.base_scale
        scene_obj.morph_factor = 0.0
        
        print(f"   {scene_obj.id} fading out to base state")
    
    def set_global_morph_factor(self, factor: float):
        """Set global morphing factor (0.0 to 1.0)."""
        
        self.global_morph_factor = max(0.0, min(1.0, factor))
        
        # Apply to all active objects
        for scene_obj in self.objects.values():
            if scene_obj.active_notes:  # Only morph active objects
                self._apply_global_morphing(scene_obj)
        
        print(f"🔄 Global morph factor set to: {self.global_morph_factor:.2f}")
    
    def get_scene_stats(self) -> Dict[str, Any]:
        """Get scene statistics for monitoring."""
        
        total_active_notes = sum(len(obj.active_notes) for obj in self.objects.values())
        active_objects = sum(1 for obj in self.objects.values() if obj.active_notes)
        
        return {
            'total_objects': len(self.objects),
            'active_objects': active_objects,
            'total_active_notes': total_active_notes,
            'total_lights': 0,  # No lights in simplified version
            'global_morph_factor': self.global_morph_factor,
            'note_mapping_coverage': len(self.note_to_object_map)
        }

# =============================================================================
# MIDI Handler (Same as Step 1)
# =============================================================================

class MidiSignals(QObject):
    """Qt signals for MIDI events."""
    note_on = Signal(int, float, int)  # note, velocity, channel
    note_off = Signal(int, int)        # note, channel  
    control_change = Signal(int, int, int)  # controller, value, channel

class MidiHandler(QThread):
    """MIDI handler."""
    
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
# Simple Performance Monitor
# =============================================================================

class SimplePerformanceSignals(QObject):
    """Qt signals for performance monitoring."""
    fps_updated = Signal(float)
    memory_updated = Signal(float, float)
    performance_warning = Signal(str)

class SimplePerformanceMonitor(QThread):
    """Simple performance monitoring."""
    
    def __init__(self):
        super().__init__()
        self.signals = SimplePerformanceSignals()
        self.running = False
        self.frame_count = 0
        self.last_time = time.time()
    
    def update_frame(self):
        """Call this every frame."""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_time >= 1.0:
            fps = self.frame_count / (current_time - self.last_time)
            self.signals.fps_updated.emit(fps)
            self.frame_count = 0
            self.last_time = current_time
    
    def run(self):
        """Monitor system resources."""
        if not PERFORMANCE_MONITORING:
            return
        
        self.running = True
        
        while self.running:
            try:
                process = psutil.Process()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                memory_percent = process.memory_percent()
                
                self.signals.memory_updated.emit(memory_mb, memory_percent)
                
                if memory_percent > 80:
                    self.signals.performance_warning.emit(f"High memory: {memory_percent:.1f}%")
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(1.0)
    
    def stop(self):
        """Stop monitoring."""
        self.running = False

# =============================================================================
# Main Application Window (Simplified)
# =============================================================================

class SimplifiedMorphingWindow(QMainWindow):
    """Simplified main window without 3D dependencies."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Morphing Visualizer - Step 3: Simplified (No 3D)")
        
        # Core components
        self.scene_manager = None
        self.midi_handler = None
        self.performance_monitor = None
        
        # UI components
        self.morph_slider = None
        
        # Timers
        self.update_timer = QTimer()
        
        # Initialize
        self._setup_ui()
        self._setup_scene_manager()
        self._setup_connections()
        self._start_systems()
        
        print("✅ Simplified Morphing Window (Step 3) initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel for controls
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
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
        
        perf_layout.addWidget(self.fps_label)
        perf_layout.addWidget(self.memory_label)
        
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
        
        left_layout.addStretch()
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        
        # Right panel - simulation display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 3D Scene Placeholder
        scene_placeholder = QLabel("3D Scene Manager - Logic Only\n\nObjects are managed in memory.\nWatch console for MIDI note activity.\n\nUse Test buttons to see object responses.")
        scene_placeholder.setMinimumSize(600, 400)
        scene_placeholder.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #00ff00;
                border: 2px solid #333333;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                padding: 20px;
                text-align: center;
            }
        """)
        scene_placeholder.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(scene_placeholder)
        
        # Real-time object status display
        status_group = QGroupBox("Object Status")
        status_layout = QVBoxLayout(status_group)
        
        self.object_status_text = QTextEdit()
        self.object_status_text.setMaximumHeight(150)
        self.object_status_text.setReadOnly(True)
        self.object_status_text.setStyleSheet("""
            QTextEdit {
                background-color: #0a0a0a;
                color: #00cc00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        status_layout.addWidget(self.object_status_text)
        
        right_layout.addWidget(status_group)
        
        main_layout.addWidget(right_panel, 1)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Simplified Step 3 (No 3D Dependencies)")
    
    def _setup_scene_manager(self):
        """Setup simplified scene manager."""
        
        try:
            self.scene_manager = SimplifiedSceneManager()
            print("✅ Simplified scene manager setup complete")
        except Exception as e:
            print(f"❌ Error setting up scene manager: {e}")
    
    def _setup_connections(self):
        """Setup signal/slot connections."""
        
        # Morph slider
        self.morph_slider.valueChanged.connect(self._on_morph_slider_changed)
        
        # Test buttons
        self.test_note_btn.clicked.connect(self._test_midi_note)
        self.test_morph_btn.clicked.connect(self._test_morphing)
        self.reset_scene_btn.clicked.connect(self._reset_scene)
        
        # Update timer
        self.update_timer.timeout.connect(self._update_display)
        
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
        
        # Start performance monitor
        if PERFORMANCE_MONITORING:
            try:
                self.performance_monitor = SimplePerformanceMonitor()
                self.performance_monitor.signals.fps_updated.connect(self._on_fps_updated)
                self.performance_monitor.signals.memory_updated.connect(self._on_memory_updated)
                self.performance_monitor.signals.performance_warning.connect(self._on_performance_warning)
                self.performance_monitor.start()
                print("✅ Performance monitor started")
            except Exception as e:
                print(f"⚠️  Performance monitor failed to start: {e}")
        
        # Start update timer
        self.update_timer.start(100)  # Update every 100ms
        
        # Initial display update
        self._update_scene_info()
        self._update_object_status()
    
    def _on_morph_slider_changed(self, value):
        """Handle morph slider changes."""
        
        morph_factor = value / 100.0
        self.morph_value_label.setText(f"{value}%")
        
        if self.scene_manager:
            self.scene_manager.set_global_morph_factor(morph_factor)
        
        print(f"🔄 Global morph factor: {morph_factor:.2f}")
    
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
    
    def _on_fps_updated(self, fps):
        """Handle FPS updates."""
        color = "green" if fps >= 30 else "orange" if fps >= 20 else "red"
        self.fps_label.setText(f"<font color='{color}'>FPS: {fps:.1f}</font>")
    
    def _on_memory_updated(self, memory_mb, memory_percent):
        """Handle memory usage updates."""
        color = "green" if memory_percent < 70 else "orange" if memory_percent < 85 else "red"
        self.memory_label.setText(f"<font color='{color}'>Memory: {memory_percent:.1f}%</font>")
    
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
            print(f"🧪 Test note: {note} (velocity: {velocity:.2f}) in {range_name} range")
            
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
        
        print("🧪 Testing morphing animation")
    
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
            
            print("🔄 Scene reset to default state")
    
    def _update_display(self):
        """Update display elements."""
        
        # Update FPS counter
        if self.performance_monitor:
            self.performance_monitor.update_frame()
        
        # Update scene info
        self._update_scene_info()
        self._update_object_status()
    
    def _update_scene_info(self):
        """Update scene information display."""
        
        try:
            if self.scene_manager:
                stats = self.scene_manager.get_scene_stats()
                
                info_text = f"""Objects: {stats['total_objects']}
Active: {stats['active_objects']}
Notes: {stats['total_active_notes']}
Morph: {stats['global_morph_factor']:.2f}
Coverage: {stats['note_mapping_coverage']} notes"""
                
                self.scene_info_text.setPlainText(info_text)
            else:
                self.scene_info_text.setPlainText("Scene Manager: Not Available")
        except Exception as e:
            self.scene_info_text.setPlainText(f"Scene Info Error: {e}")
    
    def _update_object_status(self):
        """Update object status display."""
        
        try:
            if not self.scene_manager:
                self.object_status_text.setPlainText("Scene Manager not available")
                return
            
            status_lines = []
            status_lines.append("=== OBJECT STATUS ===")
            
            for obj_id, obj in self.scene_manager.objects.items():
                active_notes = len(obj.active_notes)
                intensity = obj.get_intensity()
                
                if active_notes > 0:
                    note_list = ", ".join(str(n) for n in obj.active_notes.keys())
                    status_lines.append(f"{obj_id.upper()}: {active_notes} notes [{note_list}]")
                    status_lines.append(f"  Intensity: {intensity:.2f} | Scale: {obj.current_scale:.2f}")
                    status_lines.append(f"  Color: RGB({obj.current_color[0]:.2f}, {obj.current_color[1]:.2f}, {obj.current_color[2]:.2f})")
                    if obj.morph_factor > 0:
                        status_lines.append(f"  Morph: {obj.morph_factor:.2f}")
                else:
                    status_lines.append(f"{obj_id.upper()}: IDLE")
                
                status_lines.append("")
            
            self.object_status_text.setPlainText("\n".join(status_lines))
            
        except Exception as e:
            self.object_status_text.setPlainText(f"Status update error: {e}")
    
    def closeEvent(self, event):
        """Clean shutdown."""
        
        print("Shutting down Simplified Morphing Window (Step 3)...")
        
        # Stop all systems
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
        
        # Stop timers
        self.update_timer.stop()
        
        print("✅ Simplified Morphing Window (Step 3) shutdown complete")
        event.accept()

# =============================================================================
# Main Application Entry Point
# =============================================================================

def main():
    """Main application entry point."""
    
    print("=" * 80)
    print("🎵 MIDI Morphing Visualizer - Step 3: Simplified (No 3D Dependencies) 🎵")
    print("=" * 80)
    print()
    print("This version demonstrates the Step 3 Enhanced Scene Manager")
    print("without requiring 3D visualization dependencies.")
    print()
    print("FEATURES:")
    print("✅ Enhanced Scene Manager with multiple objects (logic only)")
    print("✅ Note range mapping (bass, melody, treble, high)")
    print("✅ MIDI-to-object mapping and routing")
    print("✅ Global morphing capabilities")
    print("✅ Real-time object state tracking")
    print("✅ Performance monitoring")
    print("✅ Test functionality")
    print()
    print("NOTE MAPPING:")
    print("🎵 Bass (C1-B2, notes 24-47) → Bass Sphere")
    print("🎵 Melody (C3-B4, notes 48-71) → Melody Cube")
    print("🎵 Treble (C5-B6, notes 72-95) → Treble Cylinder")  
    print("🎵 High (C7-C8, notes 96-108) → High Icosahedron")
    print()
    
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer - Step 3 Simplified")
    app.setOrganizationName("Enhanced MIDI Visualization")
    
    try:
        window = SimplifiedMorphingWindow()
        window.resize(1000, 700)
        window.show()
        
        print("🚀 Simplified MIDI Morphing Visualizer (Step 3) is ready!")
        print()
        print("QUICK TEST GUIDE:")
        print("1. Use 'Test MIDI Note' button to see object responses")
        print("2. Move the 'Global Morphing' slider to see morphing effects")
        print("3. Play MIDI notes in different octaves to trigger different objects")
        print("4. Watch the 'Object Status' panel for real-time updates")
        print("5. Monitor performance in the bottom panel")
        print()
        print("All object activity is logged to console and status display.")
        print("This demonstrates the Step 3 logic without 3D dependencies! 🎆")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
