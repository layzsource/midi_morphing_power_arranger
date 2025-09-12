#!/usr/bin/env python3
"""
MIDI Morphing Visualizer - Step 5 Simplified: Stable Visual Effects
Building carefully on the working Step 3 foundation.

This version focuses on stability over complexity:
- Simple but effective lighting changes
- Basic particle-like effects using existing geometry
- Working morphing and MIDI integration
- No complex NumPy operations that cause casting errors
"""

import sys
import os
import time
import threading
import colorsys
import numpy as np
import traceback
from typing import Dict, List, Optional

# Core dependencies
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox,
        QMenuBar, QMenu, QHBoxLayout, QGroupBox, QGridLayout,
        QFileDialog, QSplitter, QScrollArea
    )
    from PySide6.QtCore import Qt, QTimer, Signal, QObject
    from PySide6.QtGui import QAction, QActionGroup, QFont, QKeySequence, QShortcut, QColor, QPalette
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✅ Core GUI and 3D dependencies available")
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
    print("⚠️ MIDI support not available")

AUDIO_AVAILABLE = False
try:
    import sounddevice as sd
    AUDIO_AVAILABLE = True
    print("✅ SoundDevice audio backend available")
except ImportError:
    print("⚠️ SoundDevice not available")

try:
    import psutil
    PERFORMANCE_MONITORING = True
    print("✅ Performance monitoring available")
except ImportError:
    PERFORMANCE_MONITORING = False
    print("⚠️ Performance monitoring not available")

# =============================================================================
# Stable QtInteractor Wrapper (from working Step 3)
# =============================================================================

class QtInteractorWrapper:
    """Stable wrapper for QtInteractor compatibility"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.plotter = None
        self.widget = None
        self._create_plotter()
    
    def _create_plotter(self):
        """Create QtInteractor with proven compatibility handling"""
        try:
            # Create QtInteractor - it IS the plotter in newer versions
            self.widget = QtInteractor(self.parent)
            self.plotter = self.widget
            
            # Configure plotter safely
            if self.plotter:
                try:
                    self.plotter.set_background('black')
                except:
                    pass
                try:
                    if hasattr(self.plotter, 'show_axes'):
                        self.plotter.show_axes()
                except:
                    pass
            
            print("✅ QtInteractor created successfully")
            
        except Exception as e:
            print(f"❌ QtInteractor creation error: {e}")
            # Create fallback widget
            self.widget = QWidget(self.parent)
            self.widget.setStyleSheet("background-color: #1a1a1a; color: white;")
            layout = QVBoxLayout(self.widget)
            label = QLabel("3D Visualization Error\nQtInteractor compatibility issue")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            self.plotter = None
    
    def get_widget(self):
        return self.widget
    
    def get_plotter(self):
        return self.plotter

# =============================================================================
# Simple Visual Effects (No Complex Arrays)
# =============================================================================

class SimpleVisualEffects:
    """Simple visual effects that don't cause NumPy casting errors"""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.effect_objects = []
        self.background_colors = {
            'studio': [0.1, 0.1, 0.1],
            'concert': [0.05, 0.0, 0.1],
            'club': [0.1, 0.0, 0.05],
            'ambient': [0.0, 0.05, 0.1],
            'dramatic': [0.15, 0.05, 0.0]
        }
        
    def set_lighting_preset(self, preset_name):
        """Simple lighting by changing background color"""
        if not self.plotter:
            return
            
        try:
            if preset_name in self.background_colors:
                color = self.background_colors[preset_name]
                self.plotter.set_background(color)
                print(f"Applied lighting preset: {preset_name}")
        except Exception as e:
            print(f"Lighting error: {e}")
    
    def create_particle_burst(self, position, count=10):
        """Create simple particle burst using small spheres"""
        if not self.plotter:
            return
            
        try:
            # Clear old effects
            self.clear_effects()
            
            # Create small spheres around the position
            for i in range(count):
                # Simple random offset
                offset_x = (i % 3 - 1) * 0.3
                offset_y = (i % 2) * 0.3
                offset_z = ((i // 3) % 3 - 1) * 0.3
                
                sphere_pos = [
                    position[0] + offset_x,
                    position[1] + offset_y,
                    position[2] + offset_z
                ]
                
                # Create small sphere
                sphere = pv.Sphere(radius=0.05, center=sphere_pos)
                
                # Random color
                hue = i / count
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                
                actor = self.plotter.add_mesh(
                    sphere,
                    color=rgb,
                    opacity=0.8
                )
                
                if actor:
                    self.effect_objects.append(actor)
            
            # Auto-clear after 2 seconds
            timer = QTimer()
            timer.timeout.connect(self.clear_effects)
            timer.setSingleShot(True)
            timer.start(2000)
            
        except Exception as e:
            print(f"Particle burst error: {e}")
    
    def clear_effects(self):
        """Clear all visual effects"""
        if not self.plotter:
            return
            
        try:
            for actor in self.effect_objects:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.effect_objects.clear()
        except Exception as e:
            print(f"Clear effects error: {e}")

# =============================================================================
# Simple Scene Object (Stable)
# =============================================================================

class SimpleSceneObject:
    """Simplified scene object without complex array operations"""
    
    def __init__(self, name, position, note_range, color, shape='sphere'):
        self.name = name
        self.position = list(position)  # Use simple lists, not numpy arrays
        self.note_range = note_range
        self.base_color = list(color)
        self.current_color = list(color)
        self.shape = shape
        self.scale = 1.0
        self.opacity = 0.8
        
        # Simple state tracking
        self.active_notes = set()
        self.velocity = 0.0
        
        # 3D objects
        self.mesh = None
        self.actor = None
        
        self._create_mesh()
    
    def _create_mesh(self):
        """Create mesh based on shape"""
        try:
            if self.shape == 'sphere':
                self.mesh = pv.Sphere(radius=1.0, center=self.position)
            elif self.shape == 'cube':
                self.mesh = pv.Box(bounds=[
                    self.position[0]-1, self.position[0]+1,
                    self.position[1]-1, self.position[1]+1,
                    self.position[2]-1, self.position[2]+1
                ])
            elif self.shape == 'cylinder':
                self.mesh = pv.Cylinder(
                    center=self.position,
                    direction=[0, 1, 0],
                    radius=1.0,
                    height=2.0
                )
            elif self.shape == 'cone':
                self.mesh = pv.Cone(
                    center=self.position,
                    direction=[0, 1, 0],
                    radius=1.0,
                    height=2.0
                )
            else:
                # Fallback to sphere
                self.mesh = pv.Sphere(radius=1.0, center=self.position)
        except Exception as e:
            print(f"Mesh creation error for {self.name}: {e}")
            # Fallback mesh
            self.mesh = pv.Sphere(radius=1.0, center=self.position)
    
    def set_shape(self, new_shape):
        """Change shape (simple version)"""
        if new_shape != self.shape:
            self.shape = new_shape
            self._create_mesh()
            print(f"{self.name}: Changed to {new_shape}")
    
    def trigger_note(self, note, velocity):
        """Trigger note effect"""
        self.active_notes.add(note)
        self.velocity = max(self.velocity, velocity)
        
        # Simple color calculation
        note_factor = (note - self.note_range[0]) / (self.note_range[1] - self.note_range[0])
        note_factor = max(0, min(1, note_factor))
        
        # Modify color based on note and velocity
        hue = note_factor * 0.3
        rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.8 + velocity * 0.2)
        
        self.current_color = list(rgb)
        self.scale = 1.0 + velocity * 0.5
    
    def update_effects(self):
        """Update effects over time (simple version)"""
        # Fade effects when no active notes
        if not self.active_notes:
            # Simple fade back to base color
            for i in range(3):
                self.current_color[i] = 0.9 * self.current_color[i] + 0.1 * self.base_color[i]
            
            # Scale back to normal
            self.scale = 0.95 * self.scale + 0.05 * 1.0
        
        self.active_notes.clear()

# =============================================================================
# Simple Scene Manager
# =============================================================================

class SimpleSceneManager:
    """Simplified scene manager without complex operations"""
    
    def __init__(self, qt_wrapper):
        self.qt_wrapper = qt_wrapper
        self.plotter = qt_wrapper.get_plotter()
        self.objects = {}
        self.note_to_object_map = {}
        self.visual_effects = SimpleVisualEffects(self.plotter)
        
        # Create scene
        self._create_scene()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_scene)
        self.update_timer.start(33)  # 30 FPS to avoid performance issues
        
        print("✅ Simple Scene Manager initialized")
    
    def _create_scene(self):
        """Create simple scene with 4 objects"""
        try:
            # Define objects (same as Step 3)
            objects_data = [
                {
                    'name': 'Bass',
                    'position': [-3, -1, -2],
                    'note_range': (24, 47),
                    'color': [0.2, 0.4, 0.8],
                    'shape': 'sphere'
                },
                {
                    'name': 'Melody', 
                    'position': [1, 0, 1],
                    'note_range': (48, 71),
                    'color': [0.2, 0.8, 0.3],
                    'shape': 'cube'
                },
                {
                    'name': 'Treble',
                    'position': [3, 1, -1],
                    'note_range': (72, 95),
                    'color': [0.9, 0.5, 0.1],
                    'shape': 'cylinder'
                },
                {
                    'name': 'High',
                    'position': [-1, 2, 2],
                    'note_range': (96, 108),
                    'color': [0.8, 0.2, 0.7],
                    'shape': 'cone'
                }
            ]
            
            for obj_data in objects_data:
                # Create scene object
                scene_obj = SimpleSceneObject(
                    name=obj_data['name'],
                    position=obj_data['position'],
                    note_range=obj_data['note_range'],
                    color=obj_data['color'],
                    shape=obj_data['shape']
                )
                
                self.objects[obj_data['name']] = scene_obj
                
                # Map notes to objects
                for note in range(obj_data['note_range'][0], obj_data['note_range'][1] + 1):
                    self.note_to_object_map[note] = obj_data['name']
                
                # Create visual
                self._create_object_visual(scene_obj)
            
            print(f"✅ Simple scene created with {len(self.objects)} objects")
            
        except Exception as e:
            print(f"❌ Error creating scene: {e}")
            traceback.print_exc()
    
    def _create_object_visual(self, scene_obj):
        """Create visual representation"""
        try:
            if not scene_obj.mesh or not self.plotter:
                return
            
            actor = self.plotter.add_mesh(
                scene_obj.mesh,
                color=scene_obj.current_color,
                opacity=scene_obj.opacity
            )
            
            scene_obj.actor = actor
            
        except Exception as e:
            print(f"❌ Error creating visual for {scene_obj.name}: {e}")
    
    def _update_scene(self):
        """Simple scene update without complex operations"""
        try:
            for scene_obj in self.objects.values():
                scene_obj.update_effects()
                self._update_object_visual(scene_obj)
                
        except Exception as e:
            print(f"Scene update error: {e}")
    
    def _update_object_visual(self, scene_obj):
        """Update object visual safely"""
        try:
            if not scene_obj.actor or not scene_obj.mesh or not self.plotter:
                return
            
            # Remove old actor
            self.plotter.remove_actor(scene_obj.actor)
            
            # Create updated mesh with current scale
            if scene_obj.scale != 1.0:
                # Simple scaling by recreating mesh
                scaled_mesh = scene_obj.mesh.copy()
                try:
                    # Safe scaling
                    points = scaled_mesh.points
                    center = scene_obj.position
                    scaled_points = []
                    for point in points:
                        # Scale relative to center
                        dx = (point[0] - center[0]) * scene_obj.scale
                        dy = (point[1] - center[1]) * scene_obj.scale  
                        dz = (point[2] - center[2]) * scene_obj.scale
                        scaled_points.append([center[0] + dx, center[1] + dy, center[2] + dz])
                    
                    scaled_mesh.points = scaled_points
                except:
                    # Fallback - use original mesh
                    scaled_mesh = scene_obj.mesh
            else:
                scaled_mesh = scene_obj.mesh
            
            # Create new actor
            actor = self.plotter.add_mesh(
                scaled_mesh,
                color=scene_obj.current_color,
                opacity=scene_obj.opacity
            )
            
            scene_obj.actor = actor
            
        except Exception as e:
            print(f"Visual update error for {scene_obj.name}: {e}")
    
    # MIDI Integration
    def handle_midi_note_on(self, note, velocity, channel):
        """Handle MIDI note on"""
        try:
            if note in self.note_to_object_map:
                obj_name = self.note_to_object_map[note]
                if obj_name in self.objects:
                    scene_obj = self.objects[obj_name]
                    scene_obj.trigger_note(note, velocity)
                    
                    # Trigger particle effect for strong notes
                    if velocity > 0.7:
                        self.visual_effects.create_particle_burst(scene_obj.position, 8)
                    
                    print(f"Note effect: {note} -> {obj_name} (velocity: {velocity:.2f})")
            
        except Exception as e:
            print(f"MIDI note handling error: {e}")
    
    def handle_midi_note_off(self, note, channel):
        """Handle MIDI note off"""
        try:
            if note in self.note_to_object_map:
                obj_name = self.note_to_object_map[note]
                if obj_name in self.objects:
                    scene_obj = self.objects[obj_name]
                    scene_obj.active_notes.discard(note)
        except Exception as e:
            print(f"MIDI note off error: {e}")
    
    def handle_midi_cc(self, controller, value, channel):
        """Handle MIDI control changes"""
        try:
            if controller == 1:  # Modulation wheel
                # Simple shape cycling based on CC value
                shapes = ['sphere', 'cube', 'cylinder', 'cone']
                shape_index = int((value / 127.0) * (len(shapes) - 1))
                shape = shapes[shape_index]
                
                for obj in self.objects.values():
                    obj.set_shape(shape)
                    
        except Exception as e:
            print(f"MIDI CC handling error: {e}")
    
    def set_lighting_preset(self, preset_name):
        """Set lighting preset"""
        self.visual_effects.set_lighting_preset(preset_name)
    
    def trigger_visual_burst(self):
        """Trigger visual burst"""
        try:
            for scene_obj in self.objects.values():
                self.visual_effects.create_particle_burst(scene_obj.position, 12)
            print("Visual burst triggered!")
        except Exception as e:
            print(f"Visual burst error: {e}")

# =============================================================================
# Simplified MIDI Handler
# =============================================================================

class SimpleMIDIHandler(QObject):
    """Simplified MIDI handler"""
    
    note_on = Signal(int, float, int)
    note_off = Signal(int, int)
    control_change = Signal(int, int, int)
    
    def __init__(self):
        super().__init__()
        self.midi_devices = []
        self.selected_device = None
        self.midi_input = None
        self.running = False
        self.midi_thread = None
        
        self._scan_devices()
    
    def _scan_devices(self):
        """Scan for MIDI devices"""
        if not MIDI_AVAILABLE:
            return
            
        try:
            pygame.midi.init()
            device_count = pygame.midi.get_count()
            
            self.midi_devices = []
            for device_id in range(device_count):
                info = pygame.midi.get_device_info(device_id)
                if info[2]:  # Input device
                    device_name = info[1].decode()
                    self.midi_devices.append({
                        'id': device_id,
                        'name': device_name
                    })
            
            print(f"✅ Found {len(self.midi_devices)} MIDI devices")
            
        except Exception as e:
            print(f"❌ MIDI device scan error: {e}")
    
    def get_device_names(self):
        return [device['name'] for device in self.midi_devices]
    
    def connect_device(self, device_name):
        """Connect to MIDI device"""
        if not MIDI_AVAILABLE:
            return False
            
        try:
            device_id = None
            for device in self.midi_devices:
                if device['name'] == device_name:
                    device_id = device['id']
                    break
            
            if device_id is None:
                return False
            
            self.stop()
            self.midi_input = pygame.midi.Input(device_id)
            self.selected_device = device_name
            
            self.running = True
            self.midi_thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.midi_thread.start()
            
            print(f"✅ Connected to MIDI device: {device_name}")
            return True
            
        except Exception as e:
            print(f"❌ MIDI connection error: {e}")
            return False
    
    def stop(self):
        """Stop MIDI input"""
        self.running = False
        
        try:
            if self.midi_input:
                self.midi_input.close()
                self.midi_input = None
        except:
            pass
        
        if self.selected_device:
            print(f"MIDI disconnected from: {self.selected_device}")
            self.selected_device = None
    
    def _midi_loop(self):
        """MIDI processing loop"""
        try:
            while self.running and self.midi_input:
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    for event in midi_events:
                        self._process_midi_event(event[0])
                
                time.sleep(0.001)
                
        except Exception as e:
            print(f"MIDI loop error: {e}")
    
    def _process_midi_event(self, event):
        """Process MIDI event"""
        try:
            status, note, velocity, _ = event
            channel = status & 0x0F
            message_type = status & 0xF0
            
            if message_type == 0x90:  # Note on
                if velocity > 0:
                    normalized_velocity = velocity / 127.0
                    self.note_on.emit(note, normalized_velocity, channel)
                else:
                    self.note_off.emit(note, channel)
                    
            elif message_type == 0x80:  # Note off
                self.note_off.emit(note, channel)
                
            elif message_type == 0xB0:  # Control change
                controller = note
                value = velocity
                self.control_change.emit(controller, value, channel)
                
        except Exception as e:
            print(f"MIDI event processing error: {e}")

# =============================================================================
# Simplified Main Window
# =============================================================================

class SimplifiedStep5MainWindow(QMainWindow):
    """Simplified Step 5 main window focusing on stability"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI Morphing Visualizer - Step 5 Simplified: Stable Visual Effects")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize systems
        self.scene_manager = None
        self.midi_handler = None
        self.qt_interactor_wrapper = None
        
        # Create UI
        self._create_ui()
        self._create_systems()
        self._connect_signals()
        self._setup_shortcuts()
        
        print("✅ Simplified Step 5 MIDI Morphing Visualizer initialized")
    
    def _create_ui(self):
        """Create simplified UI"""
        try:
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            main_layout = QHBoxLayout(central_widget)
            
            # Left panel for controls
            left_panel = self._create_control_panel()
            main_layout.addWidget(left_panel)
            
            # Right panel for 3D view
            right_panel = self._create_3d_panel()
            main_layout.addWidget(right_panel)
            
            # Set proportions
            left_panel.setMaximumWidth(400)
            
            # Create menu bar
            self._create_menu_bar()
            
            # Create status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Ready - Simplified Step 5")
            
        except Exception as e:
            print(f"❌ UI creation error: {e}")
    
    def _create_control_panel(self):
        """Create control panel"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Shape Controls
        shape_group = QGroupBox("🎯 Shape Control")
        shape_layout = QVBoxLayout(shape_group)
        
        shape_buttons_layout = QHBoxLayout()
        shapes = ['sphere', 'cube', 'cylinder', 'cone']
        for shape in shapes:
            btn = QPushButton(shape.title())
            btn.clicked.connect(lambda checked, s=shape: self._set_all_shapes(s))
            shape_buttons_layout.addWidget(btn)
        shape_layout.addLayout(shape_buttons_layout)
        
        layout.addWidget(shape_group)
        
        # Lighting Controls
        lighting_group = QGroupBox("🎆 Simple Lighting")
        lighting_layout = QVBoxLayout(lighting_group)
        
        lighting_layout.addWidget(QLabel("Background Preset:"))
        self.lighting_combo = QComboBox()
        self.lighting_combo.addItems(["studio", "concert", "club", "ambient", "dramatic"])
        lighting_layout.addWidget(self.lighting_combo)
        
        layout.addWidget(lighting_group)
        
        # MIDI Controls
        midi_group = QGroupBox("🎹 MIDI")
        midi_layout = QVBoxLayout(midi_group)
        
        midi_layout.addWidget(QLabel("MIDI Device:"))
        self.midi_device_combo = QComboBox()
        self.midi_device_combo.addItem("No Device")
        midi_layout.addWidget(self.midi_device_combo)
        
        self.midi_connect_btn = QPushButton("Connect MIDI")
        midi_layout.addWidget(self.midi_connect_btn)
        
        layout.addWidget(midi_group)
        
        # Test Controls
        test_group = QGroupBox("🧪 Test Functions")
        test_layout = QVBoxLayout(test_group)
        
        test_buttons = [
            ("Test Shape Morphing", self._test_morphing),
            ("Test Lighting Presets", self._test_lighting),
            ("Test Visual Burst", self._test_visual_burst)
        ]
        
        for text, func in test_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            test_layout.addWidget(btn)
        
        layout.addWidget(test_group)
        
        layout.addStretch()
        
        scroll_area.setWidget(panel)
        return scroll_area
    
    def _create_3d_panel(self):
        """Create 3D panel"""
        try:
            self.qt_interactor_wrapper = QtInteractorWrapper()
            widget = self.qt_interactor_wrapper.get_widget()
            widget.setMinimumSize(800, 600)
            return widget
        except Exception as e:
            print(f"❌ 3D panel creation error: {e}")
            fallback = QWidget()
            fallback.setStyleSheet("background-color: #1a1a1a; color: white;")
            layout = QVBoxLayout(fallback)
            label = QLabel("3D Visualization Error")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
            return fallback
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Lighting submenu
        lighting_menu = view_menu.addMenu("Lighting Presets")
        lighting_group = QActionGroup(self)
        
        presets = ["studio", "concert", "club", "ambient", "dramatic"]
        for i, preset in enumerate(presets):
            action = QAction(preset.title(), self)
            action.setShortcut(f"F{i+1}")
            action.setCheckable(True)
            action.setChecked(preset == "studio")
            action.triggered.connect(lambda checked, p=preset: self._on_lighting_changed(p))
            lighting_group.addAction(action)
            lighting_menu.addAction(action)
    
    def _create_systems(self):
        """Create backend systems"""
        try:
            # Scene manager
            if self.qt_interactor_wrapper and self.qt_interactor_wrapper.get_plotter():
                self.scene_manager = SimpleSceneManager(self.qt_interactor_wrapper)
            else:
                print("⚠️ Scene manager not created - no 3D plotter available")
            
            # MIDI handler
            self.midi_handler = SimpleMIDIHandler()
            if self.midi_handler.midi_devices:
                device_names = self.midi_handler.get_device_names()
                self.midi_device_combo.addItems(device_names)
            
            print("✅ Systems created")
            
        except Exception as e:
            print(f"❌ System creation error: {e}")
    
    def _connect_signals(self):
        """Connect signals"""
        try:
            # UI controls
            self.lighting_combo.currentTextChanged.connect(self._on_lighting_changed)
            self.midi_connect_btn.clicked.connect(self._connect_midi)
            
            # MIDI signals
            if self.midi_handler and self.scene_manager:
                self.midi_handler.note_on.connect(self.scene_manager.handle_midi_note_on)
                self.midi_handler.note_off.connect(self.scene_manager.handle_midi_note_off)
                self.midi_handler.control_change.connect(self.scene_manager.handle_midi_cc)
            
            print("✅ Signals connected")
            
        except Exception as e:
            print(f"❌ Signal connection error: {e}")
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            # Shape shortcuts (1-4)
            shapes = ['sphere', 'cube', 'cylinder', 'cone']
            for i, shape in enumerate(shapes):
                shortcut = QShortcut(QKeySequence(f"{i+1}"), self)
                shortcut.activated.connect(lambda s=shape: self._set_all_shapes(s))
            
            # Lighting preset shortcuts (F1-F5)
            presets = ["studio", "concert", "club", "ambient", "dramatic"]
            for i, preset in enumerate(presets):
                shortcut = QShortcut(QKeySequence(f"F{i+1}"), self)
                shortcut.activated.connect(lambda p=preset: self._on_lighting_changed(p))
            
            # Visual burst shortcut (Space)
            burst_shortcut = QShortcut(QKeySequence(Qt.Key_Space), self)
            burst_shortcut.activated.connect(self._test_visual_burst)
            
            print("✅ Shortcuts setup")
            
        except Exception as e:
            print(f"❌ Shortcut setup error: {e}")
    
    # Event handlers
    def _on_lighting_changed(self, preset):
        """Handle lighting preset change"""
        self.lighting_combo.setCurrentText(preset)
        if self.scene_manager:
            self.scene_manager.set_lighting_preset(preset)
    
    def _connect_midi(self):
        """Connect to selected MIDI device"""
        device_name = self.midi_device_combo.currentText()
        if device_name != "No Device" and self.midi_handler:
            if self.midi_handler.connect_device(device_name):
                self.midi_connect_btn.setText("Disconnect MIDI")
                self.status_bar.showMessage(f"Connected to MIDI: {device_name}")
            else:
                QMessageBox.warning(self, "MIDI Error", f"Failed to connect to {device_name}")
        else:
            if self.midi_handler:
                self.midi_handler.stop()
            self.midi_connect_btn.setText("Connect MIDI")
            self.status_bar.showMessage("MIDI disconnected")
    
    def _set_all_shapes(self, shape):
        """Set all objects to the same shape"""
        if self.scene_manager:
            for obj in self.scene_manager.objects.values():
                obj.set_shape(shape)
            print(f"All objects set to: {shape}")
    
    # Test functions
    def _test_morphing(self):
        """Test shape morphing"""
        if not self.scene_manager:
            return
        
        shapes = ['sphere', 'cube', 'cylinder', 'cone']
        
        def morph_sequence(index=0):
            if index < len(shapes):
                self._set_all_shapes(shapes[index])
                QTimer.singleShot(1500, lambda: morph_sequence(index + 1))
        
        morph_sequence()
        print("Testing shape morphing sequence...")
    
    def _test_lighting(self):
        """Test lighting presets"""
        if not self.scene_manager:
            return
        
        presets = ["studio", "concert", "club", "ambient", "dramatic"]
        
        def lighting_sequence(index=0):
            if index < len(presets):
                self._on_lighting_changed(presets[index])
                QTimer.singleShot(2000, lambda: lighting_sequence(index + 1))
        
        lighting_sequence()
        print("Testing lighting presets...")
    
    def _test_visual_burst(self):
        """Test visual burst"""
        if self.scene_manager:
            self.scene_manager.trigger_visual_burst()
    
    def closeEvent(self, event):
        """Cleanup on close"""
        print("Closing Simplified Step 5...")
        
        try:
            if hasattr(self, 'scene_manager') and self.scene_manager:
                if hasattr(self.scene_manager, 'update_timer'):
                    self.scene_manager.update_timer.stop()
            
            if hasattr(self, 'midi_handler') and self.midi_handler:
                self.midi_handler.stop()
            
            if hasattr(self, 'qt_interactor_wrapper') and self.qt_interactor_wrapper:
                if self.qt_interactor_wrapper.plotter:
                    try:
                        self.qt_interactor_wrapper.plotter.clear()
                    except:
                        pass
            
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        event.accept()

# =============================================================================
# Main Application Entry Point
# =============================================================================

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("MIDI Morphing Visualizer - Step 5 Simplified")
    app.setOrganizationName("MIDI Morphing Systems")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Create and show main window
    window = SimplifiedStep5MainWindow()
    window.show()
    
    # Display startup information
    print("MIDI Morphing Visualizer - Step 5 Simplified Started!")
    print("=" * 60)
    print("SIMPLIFIED STEP 5 FEATURES:")
    print("   • Stable 3D visualization without NumPy casting errors")
    print("   • Simple but effective lighting presets")
    print("   • Basic particle-like effects using geometry")
    print("   • Working MIDI integration")
    print("   • Shape morphing without complex arrays")
    print("   • Visual burst effects")
    print("=" * 60)
    print("CONTROLS:")
    print("   • 1-4 Keys: Shape selection")
    print("   • F1-F5: Lighting presets")
    print("   • Space: Visual burst effect")
    print("   • MIDI notes trigger objects by range")
    print("   • CC1 (mod wheel) cycles through shapes")
    print("=" * 60)
    print("TESTING:")
    print("   1. Use 'Test Shape Morphing' for automatic demo")
    print("   2. Try 'Test Lighting Presets' for background changes")
    print("   3. Press 'Test Visual Burst' for particle effects")
    print("   4. Connect MIDI device and play notes")
    print("=" * 60)
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print("EXCEPTION:")
        print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
    sys.excepthook = handle_exception
    
    try:
        exit_code = app.exec()
        print("\nSimplified Step 5 Closed")
        return exit_code
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
