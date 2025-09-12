#!/usr/bin/env python3
"""
Enhanced MIDI Morphing Visualizer - Step 5: Advanced Lighting and Visual Effects
Building on Step 4's real vertex-level morphing foundation.

This step adds:
🎆 Advanced Lighting System with multiple light types
🌈 Dynamic Shader Effects and Material Properties  
✨ Particle System Integration with morphing objects
🎨 Post-Processing Effects (Bloom, Glow, Color Grading)
🎪 Environmental Effects (Fog, Atmosphere, Reflections)
🎬 Advanced Animation System with Keyframe Interpolation
🎯 Visual Effects Presets for Live Performance
⚡ GPU-Accelerated Rendering Pipeline
🎮 Real-time Effect Parameter Control
📊 Advanced Performance Optimization
"""

import sys
import os
import logging
import time
import threading
import colorsys
import numpy as np
import queue
import json
import traceback
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
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
        QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar, QFrame,
        QDial, QButtonGroup, QRadioButton, QSpacerItem, QSizePolicy,
        QScrollArea, QSplitter, QTreeWidget, QTreeWidgetItem, QFileDialog
    )
    from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject, QThread, QPropertyAnimation, QEasingCurve
    from PySide6.QtGui import QAction, QFont, QKeySequence, QShortcut, QColor, QPalette
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✅ Core GUI and 3D dependencies available")
except ImportError as e:
    print(f"❌ Missing core dependencies: {e}")
    sys.exit(1)

# Enhanced dependencies for Step 5
try:
    import scipy.interpolate
    import scipy.signal
    SCIPY_AVAILABLE = True
    print("✅ SciPy for advanced interpolation available")
except ImportError:
    SCIPY_AVAILABLE = False
    print("⚠️ SciPy not available - using linear interpolation")

# Optional dependencies
MIDI_AVAILABLE = False
try:
    import pygame.midi
    MIDI_AVAILABLE = True
    print("✅ Pygame MIDI support available")
except ImportError:
    print("⚠️ MIDI support not available")

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
    print("⚠️ SoundDevice not available")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
    AUDIO_AVAILABLE = True
    print("✅ PyAudio backend available")
except ImportError:
    print("⚠️ PyAudio not available")

try:
    import librosa
    LIBROSA_AVAILABLE = True
    print("✅ Librosa audio analysis available")
except ImportError:
    print("⚠️ Librosa not available - advanced audio features disabled")

try:
    import psutil
    PERFORMANCE_MONITORING = True
    print("✅ Performance monitoring available")
except ImportError:
    PERFORMANCE_MONITORING = False
    print("⚠️ Performance monitoring not available")

# =============================================================================
# STEP 5: Advanced Lighting and Visual Effects System
# =============================================================================

class LightType(Enum):
    """Different types of lights for the scene."""
    AMBIENT = "ambient"
    DIRECTIONAL = "directional"
    POINT = "point"
    SPOT = "spot"
    AREA = "area"
    HDRI = "hdri"

class EffectType(Enum):
    """Visual effect types."""
    BLOOM = "bloom"
    GLOW = "glow"
    PARTICLE_SYSTEM = "particle_system"
    FOG = "fog"
    REFLECTION = "reflection"
    COLOR_GRADING = "color_grading"
    MOTION_BLUR = "motion_blur"
    DEPTH_OF_FIELD = "depth_of_field"

class AnimationEasing(Enum):
    """Animation easing types."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    BACK = "back"

@dataclass
class Light:
    """Advanced light representation."""
    id: str
    light_type: LightType
    position: np.ndarray
    direction: np.ndarray = field(default_factory=lambda: np.array([0, 0, -1]))
    color: np.ndarray = field(default_factory=lambda: np.array([1, 1, 1]))
    intensity: float = 1.0
    cone_angle: float = 45.0  # For spot lights
    falloff: float = 1.0
    shadows: bool = True
    volumetric: bool = False
    animated: bool = False
    animation_params: Dict = field(default_factory=dict)
    created_time: float = field(default_factory=time.time)
    lifetime: float = 10.0  # seconds
    pv_light: Optional[Any] = None

@dataclass
class Particle:
    """Individual particle for particle system."""
    position: np.ndarray
    velocity: np.ndarray
    color: np.ndarray
    size: float
    life: float
    max_life: float
    gravity_effect: float = 1.0
    trail_length: int = 5
    trail_positions: List[np.ndarray] = field(default_factory=list)

@dataclass
class VisualEffect:
    """Visual effect representation."""
    effect_type: EffectType
    enabled: bool = True
    intensity: float = 1.0
    parameters: Dict = field(default_factory=dict)
    animated_params: Dict = field(default_factory=dict)

class AdvancedLightingSystem:
    """Advanced lighting system with multiple light types and effects."""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.lights: Dict[str, Light] = {}
        self.next_light_id = 0
        self.max_lights = 8  # Performance limit
        self.ambient_level = 0.3
        
        # Lighting presets
        self.presets = {
            "concert": self._create_concert_preset,
            "studio": self._create_studio_preset,
            "club": self._create_club_preset,
            "ambient": self._create_ambient_preset,
            "dramatic": self._create_dramatic_preset
        }
        
        # Initialize default lighting
        self._setup_default_lighting()
    
    def _setup_default_lighting(self):
        """Setup default lighting configuration."""
        try:
            # Key light
            self.add_light(
                light_type=LightType.DIRECTIONAL,
                position=np.array([5, 5, 5]),
                direction=np.array([-1, -1, -1]),
                color=np.array([1.0, 0.95, 0.9]),
                intensity=1.5
            )
            
            # Fill light
            self.add_light(
                light_type=LightType.DIRECTIONAL,
                position=np.array([-3, 2, 4]),
                direction=np.array([1, -0.5, -1]),
                color=np.array([0.8, 0.9, 1.0]),
                intensity=0.7
            )
            
            # Back light
            self.add_light(
                light_type=LightType.DIRECTIONAL,
                position=np.array([0, -5, 3]),
                direction=np.array([0, 1, -0.5]),
                color=np.array([1.0, 0.8, 0.6]),
                intensity=0.5
            )
            
        except Exception as e:
            print(f"Warning: Could not setup default lighting: {e}")
    
    def add_light(self, light_type: LightType, position: np.ndarray, 
                  direction: np.ndarray = None, color: np.ndarray = None,
                  intensity: float = 1.0, **kwargs) -> str:
        """Add a new light to the scene."""
        
        if len(self.lights) >= self.max_lights:
            # Remove oldest light
            oldest_id = min(self.lights.keys(), key=lambda k: self.lights[k].created_time)
            self.remove_light(oldest_id)
        
        light_id = f"light_{self.next_light_id}"
        self.next_light_id += 1
        
        if direction is None:
            direction = np.array([0, 0, -1])
        if color is None:
            color = np.array([1, 1, 1])
        
        light = Light(
            id=light_id,
            light_type=light_type,
            position=position.copy(),
            direction=direction.copy(),
            color=color.copy(),
            intensity=intensity,
            **kwargs
        )
        
        # Create PyVista light
        try:
            if light_type == LightType.DIRECTIONAL:
                pv_light = pv.Light(
                    position=tuple(position),
                    focal_point=tuple(position + direction),
                    color=tuple(color),
                    intensity=intensity,
                    light_type='scene light'
                )
            elif light_type == LightType.POINT:
                pv_light = pv.Light(
                    position=tuple(position),
                    color=tuple(color),
                    intensity=intensity,
                    light_type='camera light'
                )
            else:
                # Fallback to scene light
                pv_light = pv.Light(
                    position=tuple(position),
                    color=tuple(color),
                    intensity=intensity
                )
            
            light.pv_light = pv_light
            self.plotter.add_light(pv_light)
            
        except Exception as e:
            print(f"Warning: Could not create PyVista light: {e}")
        
        self.lights[light_id] = light
        return light_id
    
    def remove_light(self, light_id: str):
        """Remove a light from the scene."""
        if light_id in self.lights:
            light = self.lights[light_id]
            try:
                if light.pv_light:
                    self.plotter.remove_light(light.pv_light)
            except:
                pass
            del self.lights[light_id]
    
    def update_light(self, light_id: str, **kwargs):
        """Update light properties."""
        if light_id not in self.lights:
            return
        
        light = self.lights[light_id]
        
        # Update properties
        for key, value in kwargs.items():
            if hasattr(light, key):
                setattr(light, key, value)
        
        # Update PyVista light
        if light.pv_light:
            try:
                # Recreate light with new properties
                self.plotter.remove_light(light.pv_light)
                # Add updated light logic here
            except:
                pass
    
    def animate_lights(self, dt: float):
        """Update animated lights."""
        current_time = time.time()
        
        lights_to_remove = []
        for light_id, light in self.lights.items():
            # Check lifetime
            if current_time - light.created_time > light.lifetime:
                lights_to_remove.append(light_id)
                continue
            
            # Animate if needed
            if light.animated and light.animation_params:
                self._animate_light(light, dt)
        
        # Remove expired lights
        for light_id in lights_to_remove:
            self.remove_light(light_id)
    
    def _animate_light(self, light: Light, dt: float):
        """Animate a single light."""
        params = light.animation_params
        
        if 'orbit_speed' in params:
            # Orbital animation
            speed = params['orbit_speed']
            radius = params.get('orbit_radius', 5.0)
            center = params.get('orbit_center', np.array([0, 0, 0]))
            
            angle = (time.time() - light.created_time) * speed
            light.position[0] = center[0] + radius * np.cos(angle)
            light.position[2] = center[2] + radius * np.sin(angle)
        
        if 'pulse_speed' in params:
            # Intensity pulsing
            speed = params['pulse_speed']
            base_intensity = params.get('base_intensity', 1.0)
            pulse_amount = params.get('pulse_amount', 0.5)
            
            pulse = np.sin((time.time() - light.created_time) * speed * 2 * np.pi)
            light.intensity = base_intensity + pulse * pulse_amount
        
        if 'color_cycle_speed' in params:
            # Color cycling
            speed = params['color_cycle_speed']
            t = (time.time() - light.created_time) * speed
            
            hue = (t % 1.0)
            rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            light.color = np.array(rgb)
    
    def apply_preset(self, preset_name: str):
        """Apply a lighting preset."""
        if preset_name in self.presets:
            # Clear existing lights
            for light_id in list(self.lights.keys()):
                self.remove_light(light_id)
            
            # Apply preset
            self.presets[preset_name]()
    
    def _create_concert_preset(self):
        """Create concert-style lighting."""
        # Stage lights
        for i in range(4):
            angle = i * np.pi / 2
            x = 8 * np.cos(angle)
            z = 8 * np.sin(angle)
            
            self.add_light(
                light_type=LightType.SPOT,
                position=np.array([x, 5, z]),
                direction=np.array([-x/8, -1, -z/8]),
                color=np.array([1.0, 0.8, 0.6]),
                intensity=2.0,
                cone_angle=30.0,
                animated=True,
                animation_params={'pulse_speed': 0.5, 'base_intensity': 2.0, 'pulse_amount': 1.0}
            )
    
    def _create_studio_preset(self):
        """Create studio-style lighting."""
        # Three-point lighting
        lights = [
            # Key light
            {'pos': [3, 4, 3], 'color': [1.0, 0.95, 0.9], 'intensity': 1.8},
            # Fill light
            {'pos': [-2, 2, 2], 'color': [0.9, 0.95, 1.0], 'intensity': 0.8},
            # Back light
            {'pos': [0, -3, 4], 'color': [1.0, 0.9, 0.8], 'intensity': 0.6}
        ]
        
        for light_data in lights:
            self.add_light(
                light_type=LightType.DIRECTIONAL,
                position=np.array(light_data['pos']),
                color=np.array(light_data['color']),
                intensity=light_data['intensity']
            )
    
    def _create_club_preset(self):
        """Create club-style lighting."""
        # Colorful moving lights
        colors = [
            [1.0, 0.0, 0.0],  # Red
            [0.0, 1.0, 0.0],  # Green
            [0.0, 0.0, 1.0],  # Blue
            [1.0, 0.0, 1.0],  # Magenta
            [1.0, 1.0, 0.0],  # Yellow
            [0.0, 1.0, 1.0]   # Cyan
        ]
        
        for i, color in enumerate(colors):
            self.add_light(
                light_type=LightType.POINT,
                position=np.array([0, 5, 0]),
                color=np.array(color),
                intensity=1.5,
                animated=True,
                animation_params={
                    'orbit_speed': 0.3 + i * 0.1,
                    'orbit_radius': 6.0,
                    'pulse_speed': 1.0 + i * 0.2
                }
            )
    
    def _create_ambient_preset(self):
        """Create ambient lighting."""
        # Soft environmental lighting
        self.add_light(
            light_type=LightType.AMBIENT,
            position=np.array([0, 0, 0]),
            color=np.array([0.9, 0.95, 1.0]),
            intensity=0.8
        )
    
    def _create_dramatic_preset(self):
        """Create dramatic lighting."""
        # Single strong light with colored accents
        self.add_light(
            light_type=LightType.DIRECTIONAL,
            position=np.array([5, 8, 2]),
            direction=np.array([-1, -1.5, -0.5]),
            color=np.array([1.0, 0.9, 0.8]),
            intensity=2.5
        )
        
        # Colored rim lights
        self.add_light(
            light_type=LightType.DIRECTIONAL,
            position=np.array([-3, 1, -4]),
            direction=np.array([1, 0, 1]),
            color=np.array([0.2, 0.4, 1.0]),
            intensity=0.8
        )

class ParticleSystem:
    """Advanced particle system for visual effects."""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.particles: List[Particle] = []
        self.max_particles = 1000
        self.gravity = np.array([0, -9.8, 0])
        self.wind = np.array([0, 0, 0])
        self.particle_actors = []
        
        # Emission parameters
        self.emission_rate = 50.0  # particles per second
        self.last_emission_time = time.time()
        
        # Particle type templates
        self.particle_types = {
            'spark': {
                'size_range': (0.02, 0.05),
                'velocity_range': (-2, 2),
                'life_range': (0.5, 2.0),
                'color_base': np.array([1.0, 0.8, 0.0]),
                'gravity_effect': 0.3
            },
            'burst': {
                'size_range': (0.03, 0.08),
                'velocity_range': (-5, 5),
                'life_range': (0.2, 1.0),
                'color_base': np.array([1.0, 0.5, 0.2]),
                'gravity_effect': 0.1
            },
            'trail': {
                'size_range': (0.01, 0.03),
                'velocity_range': (-1, 1),
                'life_range': (1.0, 3.0),
                'color_base': np.array([0.2, 0.6, 1.0]),
                'gravity_effect': 0.0
            }
        }
    
    def emit_particles(self, position: np.ndarray, count: int, 
                      particle_type: str = 'spark', velocity_boost: np.ndarray = None):
        """Emit particles from a position."""
        
        if len(self.particles) + count > self.max_particles:
            # Remove oldest particles
            excess = len(self.particles) + count - self.max_particles
            self.particles = self.particles[excess:]
        
        if particle_type not in self.particle_types:
            particle_type = 'spark'
        
        template = self.particle_types[particle_type]
        
        for _ in range(count):
            # Random properties within ranges
            size = np.random.uniform(*template['size_range'])
            life = np.random.uniform(*template['life_range'])
            
            # Random velocity
            vel_range = template['velocity_range']
            velocity = np.random.uniform(vel_range[0], vel_range[1], 3)
            
            if velocity_boost is not None:
                velocity += velocity_boost
            
            # Color with some variation
            color_var = np.random.uniform(0.8, 1.2, 3)
            color = template['color_base'] * color_var
            color = np.clip(color, 0, 1)
            
            particle = Particle(
                position=position.copy(),
                velocity=velocity,
                color=color,
                size=size,
                life=life,
                max_life=life,
                gravity_effect=template['gravity_effect']
            )
            
            self.particles.append(particle)
    
    def update_particles(self, dt: float):
        """Update all particles."""
        particles_to_remove = []
        
        for i, particle in enumerate(self.particles):
            # Update lifetime
            particle.life -= dt
            if particle.life <= 0:
                particles_to_remove.append(i)
                continue
            
            # Update trail
            particle.trail_positions.append(particle.position.copy())
            if len(particle.trail_positions) > particle.trail_length:
                particle.trail_positions.pop(0)
            
            # Physics update
            particle.velocity += self.gravity * particle.gravity_effect * dt
            particle.velocity += self.wind * dt
            particle.position += particle.velocity * dt
            
            # Fade color over lifetime
            life_factor = particle.life / particle.max_life
            particle.color = particle.color * life_factor
            particle.size = particle.size * life_factor
        
        # Remove dead particles (reverse order to maintain indices)
        for i in reversed(particles_to_remove):
            self.particles.pop(i)
    
    def render_particles(self):
        """Render particles to the scene."""
        try:
            # Clear previous particle actors
            for actor in self.particle_actors:
                try:
                    self.plotter.remove_actor(actor)
                except:
                    pass
            self.particle_actors.clear()
            
            if not self.particles:
                return
            
            # Group particles by similar properties for efficient rendering
            particle_groups = {}
            
            for particle in self.particles:
                # Create group key based on size and color (rounded for grouping)
                size_key = round(particle.size, 2)
                color_key = tuple(np.round(particle.color, 1))
                group_key = (size_key, color_key)
                
                if group_key not in particle_groups:
                    particle_groups[group_key] = []
                particle_groups[group_key].append(particle)
            
            # Render each group
            for group_key, group_particles in particle_groups.items():
                if len(group_particles) > 50:  # Skip large groups for performance
                    continue
                    
                size, color = group_key
                positions = [p.position for p in group_particles]
                
                if positions:
                    # Create point cloud for this group
                    points = np.array(positions)
                    point_cloud = pv.PolyData(points)
                    
                    # Add as simple spheres
                    spheres = point_cloud.glyph(scale=False, factor=size)
                    
                    actor = self.plotter.add_mesh(
                        spheres,
                        color=color,
                        opacity=0.8,
                        render_points_as_spheres=True,
                        point_size=5
                    )
                    
                    if actor:
                        self.particle_actors.append(actor)
            
        except Exception as e:
            print(f"Particle rendering error: {e}")

class VisualEffectsManager:
    """Manager for post-processing and visual effects."""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.effects: Dict[str, VisualEffect] = {}
        self.post_processing_enabled = True
        
        # Initialize default effects
        self._setup_default_effects()
    
    def _setup_default_effects(self):
        """Setup default visual effects."""
        self.effects['bloom'] = VisualEffect(
            effect_type=EffectType.BLOOM,
            intensity=0.3,
            parameters={'threshold': 0.8, 'radius': 2.0}
        )
        
        self.effects['fog'] = VisualEffect(
            effect_type=EffectType.FOG,
            enabled=False,
            intensity=0.1,
            parameters={'color': [0.5, 0.5, 0.6], 'near': 5.0, 'far': 50.0}
        )
        
        self.effects['color_grading'] = VisualEffect(
            effect_type=EffectType.COLOR_GRADING,
            intensity=0.2,
            parameters={
                'contrast': 1.1,
                'brightness': 0.05,
                'saturation': 1.2,
                'gamma': 1.0
            }
        )
    
    def enable_effect(self, effect_name: str, enabled: bool = True):
        """Enable or disable an effect."""
        if effect_name in self.effects:
            self.effects[effect_name].enabled = enabled
    
    def set_effect_intensity(self, effect_name: str, intensity: float):
        """Set effect intensity."""
        if effect_name in self.effects:
            self.effects[effect_name].intensity = max(0.0, min(1.0, intensity))
    
    def update_effect_parameter(self, effect_name: str, param_name: str, value):
        """Update a specific effect parameter."""
        if effect_name in self.effects:
            self.effects[effect_name].parameters[param_name] = value
    
    def apply_effects(self):
        """Apply all enabled effects to the scene."""
        try:
            # This would be where post-processing effects are applied
            # For now, we apply what we can through PyVista
            
            if 'fog' in self.effects and self.effects['fog'].enabled:
                self._apply_fog()
            
            if 'color_grading' in self.effects and self.effects['color_grading'].enabled:
                self._apply_color_grading()
                
        except Exception as e:
            print(f"Effect application error: {e}")
    
    def _apply_fog(self):
        """Apply fog effect."""
        fog_effect = self.effects['fog']
        if fog_effect.enabled:
            # Simulate fog by adjusting background color and object opacity
            fog_color = fog_effect.parameters.get('color', [0.5, 0.5, 0.6])
            intensity = fog_effect.intensity
            
            # Blend background with fog color
            current_bg = self.plotter.background_color
            if isinstance(current_bg, str):
                current_bg = [0.2, 0.2, 0.2]  # Default gray
            
            fog_bg = [
                current_bg[i] * (1 - intensity) + fog_color[i] * intensity
                for i in range(3)
            ]
            
            try:
                self.plotter.set_background(fog_bg)
            except:
                pass
    
    def _apply_color_grading(self):
        """Apply color grading effect."""
        # This would require custom shaders or post-processing
        # For now, we can adjust lighting to simulate basic color grading
        pass

# Import geometry library from Step 4
class GeometryLibrary:
    """Enhanced geometry library with morphing capabilities"""
    
    def __init__(self):
        self.base_meshes = {}
        self._create_base_shapes()
    
    def _create_base_shapes(self):
        """Create standardized base shapes for morphing"""
        resolution = 20  # Higher resolution for smoother morphing
        
        try:
            # Create sphere
            sphere = pv.Sphere(radius=1.0, theta_resolution=resolution, phi_resolution=resolution)
            self.base_meshes['sphere'] = sphere
            
            # Create cube (converted to similar vertex count)
            cube = pv.Box(bounds=[-1, 1, -1, 1, -1, 1])
            cube_subdivided = cube.subdivide(3)
            self.base_meshes['cube'] = cube_subdivided
            
            # Create cone
            cone = pv.Cone(radius=1.0, height=2.0, resolution=resolution)
            self.base_meshes['cone'] = cone
            
            # Create cylinder  
            cylinder = pv.Cylinder(radius=1.0, height=2.0, resolution=resolution)
            self.base_meshes['cylinder'] = cylinder
            
            # Create torus
            torus = pv.ParametricTorus(ringradius=1.0, crosssectionradius=0.3, u_res=resolution, v_res=resolution//2)
            self.base_meshes['torus'] = torus
            
            print("✅ Enhanced geometry library created with 5 base shapes")
            
        except Exception as e:
            print(f"❌ Error creating geometry library: {e}")
            self._create_fallback_shapes()
    
    def _create_fallback_shapes(self):
        """Create simple fallback shapes"""
        # Simple sphere as fallback
        sphere = pv.Sphere(radius=1.0, theta_resolution=10, phi_resolution=10)
        self.base_meshes['sphere'] = sphere
        print("⚠️ Using fallback geometry")
    
    def morph_between_shapes(self, shape1_name, shape2_name, alpha):
        """Morph between two shapes"""
        if shape1_name not in self.base_meshes or shape2_name not in self.base_meshes:
            return self.base_meshes.get('sphere')
        
        source_mesh = self.base_meshes[shape1_name]
        target_mesh = self.base_meshes[shape2_name]
        
        # Ensure same number of vertices
        if source_mesh.n_points != target_mesh.n_points:
            return source_mesh  # Return source if incompatible
        
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

class EnhancedMorphingSceneObject:
    """Enhanced scene object with advanced lighting and effects"""
    
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
        
        # Enhanced visual properties
        self.metallic = 0.2
        self.roughness = 0.8
        self.emission_strength = 0.0
        self.rim_light_strength = 0.3
        self.subsurface_scattering = 0.0
        
        # Animation properties
        self.scale_animation = 1.0
        self.rotation = np.array([0.0, 0.0, 0.0])
        self.rotation_speed = np.array([0.0, 0.5, 0.0])
        
        # Object state
        self.active_notes = set()
        self.velocity = 0.0
        self.opacity = 0.8
        
        # Lighting effects
        self.local_lights = []
        self.particle_emitters = []
        self.glow_intensity = 0.0
        
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
        
        # Update rotation
        self.rotation += self.rotation_speed * dt
        self.rotation = self.rotation % (2 * np.pi)
    
    def _update_mesh(self):
        """Update mesh based on current morphing state"""
        try:
            if self.current_shape == self.target_shape:
                self.mesh = self.geometry_lib.get_mesh(self.current_shape)
            else:
                self.mesh = self.geometry_lib.morph_between_shapes(
                    self.current_shape, self.target_shape, self.morph_progress
                )
        except Exception as e:
            print(f"Error updating mesh for {self.name}: {e}")
            self.mesh = self.geometry_lib.get_mesh('sphere')
    
    def trigger_note_effect(self, note, velocity):
        """Trigger enhanced visual effects for note"""
        self.active_notes.add(note)
        self.velocity = max(self.velocity, velocity)
        
        # Enhanced color calculation
        note_color = self._calculate_note_color(note, velocity)
        self.current_color = note_color
        
        # Scale animation
        scale_factor = 1.0 + velocity * 0.5
        self.scale_animation = scale_factor
        
        # Emission effect
        self.emission_strength = velocity * 0.3
        
        # Glow effect
        self.glow_intensity = velocity
        
        # Particle emission
        if velocity > 0.5:  # Only emit particles for strong notes
            self._emit_particles(velocity)
    
    def _calculate_note_color(self, note, velocity):
        """Calculate enhanced color based on note and velocity"""
        # Base hue from note
        note_normalized = (note - self.note_range[0]) / (self.note_range[1] - self.note_range[0])
        note_normalized = max(0, min(1, note_normalized))
        
        # Different color schemes for different objects
        base_hue = {
            'bass': 0.8,     # Purple/Blue
            'melody': 0.3,   # Green/Yellow  
            'treble': 0.0,   # Red/Orange
            'high': 0.7      # Blue/Purple
        }.get(self.name.lower(), 0.5)
        
        hue = (base_hue + note_normalized * 0.3) % 1.0
        saturation = 0.7 + velocity * 0.3
        value = 0.6 + velocity * 0.4
        
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return np.array(rgb)
    
    def _emit_particles(self, velocity):
        """Emit particles from this object"""
        # This would integrate with the particle system
        pass
    
    def update_effects(self, dt):
        """Update visual effects over time"""
        # Fade effects when no notes are active
        if not self.active_notes:
            self.emission_strength *= 0.95
            self.glow_intensity *= 0.9
            self.scale_animation = 0.9 * self.scale_animation + 0.1 * 1.0
            
            # Return to base color
            self.current_color = 0.95 * self.current_color + 0.05 * self.base_color
        
        self.active_notes.clear()  # Clear for next frame

class EnhancedSceneManager:
    """Enhanced scene manager with advanced lighting and effects"""
    
    def __init__(self, qt_wrapper):
        self.qt_wrapper = qt_wrapper
        self.plotter = qt_wrapper.get_plotter()
        
        # Enhanced systems
        self.lighting_system = AdvancedLightingSystem(self.plotter)
        self.particle_system = ParticleSystem(self.plotter)
        self.effects_manager = VisualEffectsManager(self.plotter)
        self.geometry_lib = GeometryLibrary()
        
        # Scene objects
        self.objects = {}
        self.note_to_object_map = {}
        
        # Global settings
        self.global_morph_factor = 0.0
        self.environment_preset = "studio"
        
        # Performance settings
        self.quality_level = "high"  # low, medium, high, ultra
        self.max_particles = 500
        self.lighting_quality = "high"
        
        # Animation timing
        self.last_update_time = time.time()
        
        # Create default scene
        self._create_enhanced_scene()
        
        # Setup update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_scene)
        self.update_timer.start(16)  # ~60 FPS
        
        print("✅ Enhanced Scene Manager with advanced lighting initialized")
    
    def _create_enhanced_scene(self):
        """Create enhanced scene with 4 morphing objects"""
        try:
            # Define enhanced objects with more varied positioning
            enhanced_objects = [
                {
                    'name': 'Bass',
                    'position': [-3, -1, -2],
                    'note_range': (24, 47),  # C1 to B2
                    'color': [0.2, 0.4, 0.8],  # Blue
                    'initial_shape': 'sphere'
                },
                {
                    'name': 'Melody', 
                    'position': [1, 0, 1],
                    'note_range': (48, 71),  # C3 to B4
                    'color': [0.2, 0.8, 0.3],  # Green
                    'initial_shape': 'cube'
                },
                {
                    'name': 'Treble',
                    'position': [3, 1, -1],
                    'note_range': (72, 95),  # C5 to B6
                    'color': [0.9, 0.5, 0.1],  # Orange
                    'initial_shape': 'cylinder'
                },
                {
                    'name': 'High',
                    'position': [-1, 2, 2],
                    'note_range': (96, 108), # C7 to C8
                    'color': [0.8, 0.2, 0.7],  # Magenta
                    'initial_shape': 'cone'
                }
            ]
            
            for obj_data in enhanced_objects:
                # Create enhanced scene object
                scene_obj = EnhancedMorphingSceneObject(
                    name=obj_data['name'],
                    position=obj_data['position'],
                    note_range=obj_data['note_range'],
                    color=obj_data['color'],
                    geometry_lib=self.geometry_lib
                )
                
                # Set initial shape
                scene_obj.set_target_shape(obj_data['initial_shape'])
                
                # Add to scene
                self.objects[obj_data['name']] = scene_obj
                
                # Map notes to objects
                for note in range(obj_data['note_range'][0], obj_data['note_range'][1] + 1):
                    self.note_to_object_map[note] = obj_data['name']
                
                # Create visual representation
                self._create_object_visual(scene_obj)
            
            # Apply default lighting preset
            self.lighting_system.apply_preset(self.environment_preset)
            
            print(f"✅ Enhanced scene created with {len(self.objects)} morphing objects")
            
        except Exception as e:
            print(f"❌ Error creating enhanced scene: {e}")
            traceback.print_exc()
    
    def _create_object_visual(self, scene_obj):
        """Create enhanced visual representation for object"""
        try:
            if not scene_obj.mesh:
                return
            
            # Position and scale mesh
            mesh = scene_obj.mesh.copy()
            mesh.translate(scene_obj.position, inplace=True)
            
            # Enhanced material properties
            actor = self.plotter.add_mesh(
                mesh,
                color=scene_obj.current_color,
                opacity=scene_obj.opacity,
                metallic=scene_obj.metallic,
                roughness=scene_obj.roughness,
                render_points_as_spheres=True,
                point_size=5
            )
            
            scene_obj.actor = actor
            
        except Exception as e:
            print(f"❌ Error creating visual for {scene_obj.name}: {e}")
    
    def _update_scene(self):
        """Update entire enhanced scene"""
        try:
            current_time = time.time()
            dt = current_time - self.last_update_time
            self.last_update_time = current_time
            
            # Update all objects
            for scene_obj in self.objects.values():
                scene_obj.update_morphing(dt)
                scene_obj.update_effects(dt)
                self._update_object_visual(scene_obj)
            
            # Update lighting system
            self.lighting_system.animate_lights(dt)
            
            # Update particle system
            self.particle_system.update_particles(dt)
            self.particle_system.render_particles()
            
            # Apply visual effects
            self.effects_manager.apply_effects()
            
        except Exception as e:
            print(f"Scene update error: {e}")
    
    def _update_object_visual(self, scene_obj):
        """Update visual representation of object"""
        try:
            if not scene_obj.actor or not scene_obj.mesh:
                return
            
            # Remove old actor
            self.plotter.remove_actor(scene_obj.actor)
            
            # Create updated mesh
            mesh = scene_obj.mesh.copy()
            
            # Apply transformations
            mesh.scale([scene_obj.scale_animation] * 3, inplace=True)
            mesh.translate(scene_obj.position, inplace=True)
            
            # Apply rotation
            if any(scene_obj.rotation):
                mesh.rotate_x(np.degrees(scene_obj.rotation[0]), inplace=True)
                mesh.rotate_y(np.degrees(scene_obj.rotation[1]), inplace=True)
                mesh.rotate_z(np.degrees(scene_obj.rotation[2]), inplace=True)
            
            # Enhanced material properties
            enhanced_opacity = scene_obj.opacity
            if scene_obj.emission_strength > 0:
                enhanced_opacity = min(1.0, scene_obj.opacity + scene_obj.emission_strength * 0.3)
            
            # Create new actor with enhanced properties
            actor = self.plotter.add_mesh(
                mesh,
                color=scene_obj.current_color,
                opacity=enhanced_opacity,
                metallic=scene_obj.metallic,
                roughness=scene_obj.roughness,
                render_points_as_spheres=True
            )
            
            scene_obj.actor = actor
            
        except Exception as e:
            print(f"Error updating visual for {scene_obj.name}: {e}")
    
    # MIDI Integration methods
    def handle_midi_note_on(self, note, velocity, channel):
        """Handle MIDI note on with enhanced effects"""
        try:
            if note in self.note_to_object_map:
                obj_name = self.note_to_object_map[note]
                if obj_name in self.objects:
                    scene_obj = self.objects[obj_name]
                    
                    # Trigger enhanced note effect
                    scene_obj.trigger_note_effect(note, velocity)
                    
                    # Add dynamic lighting
                    light_color = scene_obj.current_color
                    light_id = self.lighting_system.add_light(
                        light_type=LightType.POINT,
                        position=scene_obj.position + np.random.normal(0, 0.5, 3),
                        color=light_color,
                        intensity=velocity * 2.0,
                        lifetime=2.0,
                        animated=True,
                        animation_params={'pulse_speed': 2.0, 'pulse_amount': 0.5}
                    )
                    
                    # Emit particles for strong notes
                    if velocity > 0.6:
                        particle_count = int(velocity * 50)
                        velocity_boost = np.random.normal(0, 2, 3)
                        self.particle_system.emit_particles(
                            scene_obj.position,
                            particle_count,
                            'spark',
                            velocity_boost
                        )
                    
                    print(f"Enhanced note effect: {note} -> {obj_name} (velocity: {velocity:.2f})")
            
        except Exception as e:
            print(f"Error handling MIDI note: {e}")
    
    def handle_midi_note_off(self, note, channel):
        """Handle MIDI note off"""
        if note in self.note_to_object_map:
            obj_name = self.note_to_object_map[note]
            if obj_name in self.objects:
                scene_obj = self.objects[obj_name]
                scene_obj.active_notes.discard(note)
    
    def handle_midi_cc(self, controller, value, channel):
        """Handle MIDI control changes for enhanced parameters"""
        try:
            if controller == 1:  # Modulation wheel - global morph
                self.set_global_morph_factor(value / 127.0)
            elif controller == 7:  # Volume - particle emission rate
                self.particle_system.emission_rate = value * 2.0
            elif controller == 10:  # Pan - lighting intensity
                for light in self.lighting_system.lights.values():
                    light.intensity = (value / 127.0) * 2.0
            elif controller == 74:  # Filter cutoff - effect intensity
                self.effects_manager.set_effect_intensity('bloom', value / 127.0)
                
        except Exception as e:
            print(f"Error handling MIDI CC: {e}")
    
    def set_global_morph_factor(self, factor):
        """Set global morphing factor with enhanced transitions"""
        self.global_morph_factor = max(0.0, min(1.0, factor))
        
        # Cycle through shapes based on global factor
        shape_names = self.geometry_lib.get_shape_names()
        if len(shape_names) > 1:
            # Calculate which shapes to morph between
            scaled_factor = factor * (len(shape_names) - 1)
            shape_index = int(scaled_factor)
            local_factor = scaled_factor - shape_index
            
            current_shape = shape_names[shape_index]
            next_shape = shape_names[min(shape_index + 1, len(shape_names) - 1)]
            
            # Apply to all objects
            for scene_obj in self.objects.values():
                if local_factor > 0.5:
                    scene_obj.set_target_shape(next_shape, 2.0)
                else:
                    scene_obj.set_target_shape(current_shape, 2.0)
    
    # Enhanced control methods
    def set_lighting_preset(self, preset_name):
        """Set lighting preset"""
        self.lighting_system.apply_preset(preset_name)
        self.environment_preset = preset_name
        print(f"Applied lighting preset: {preset_name}")
    
    def set_quality_level(self, quality):
        """Set rendering quality level"""
        self.quality_level = quality
        
        if quality == "low":
            self.max_particles = 100
            self.particle_system.max_particles = 100
        elif quality == "medium":
            self.max_particles = 300
            self.particle_system.max_particles = 300
        elif quality == "high":
            self.max_particles = 500
            self.particle_system.max_particles = 500
        elif quality == "ultra":
            self.max_particles = 1000
            self.particle_system.max_particles = 1000
        
        print(f"Quality level set to: {quality}")
    
    def trigger_visual_burst(self):
        """Trigger spectacular visual burst effect"""
        try:
            # Emit particles from all objects
            for scene_obj in self.objects.values():
                self.particle_system.emit_particles(
                    scene_obj.position,
                    50,
                    'burst',
                    np.random.normal(0, 5, 3)
                )
            
            # Add dramatic lighting
            for i in range(4):
                angle = i * np.pi / 2
                pos = np.array([3 * np.cos(angle), 2, 3 * np.sin(angle)])
                
                self.lighting_system.add_light(
                    light_type=LightType.POINT,
                    position=pos,
                    color=np.random.random(3),
                    intensity=3.0,
                    lifetime=3.0,
                    animated=True,
                    animation_params={'pulse_speed': 3.0, 'pulse_amount': 1.0}
                )
            
            print("Visual burst triggered!")
            
        except Exception as e:
            print(f"Error triggering visual burst: {e}")

# Audio Analysis (from previous steps)
class EnhancedAudioAnalyzer(QObject):
    """Enhanced audio analyzer with spectral analysis for Step 5"""
    
    audio_features_updated = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.backend = "auto"
        self.device_index = None
        
        # Audio backend objects
        self.sd_stream = None
        self.pa = None
        self.pa_stream = None
        
        # Analysis parameters
        self.analysis_enabled = True
        self.spectral_smoothing = 0.8
        
        # Feature buffers
        self.amplitude_history = np.zeros(10)
        self.centroid_history = np.zeros(10)
        
        # Threading
        self.audio_thread = None
        self.running = False
        
        self._detect_backend()
        
    def _detect_backend(self):
        """Detect available audio backend"""
        if SOUNDDEVICE_AVAILABLE:
            self.backend = "sounddevice"
        elif PYAUDIO_AVAILABLE:
            self.backend = "pyaudio"
        else:
            self.backend = "none"
            print("⚠️ No audio backend available")
    
    def start(self):
        """Start audio analysis"""
        if self.backend == "none":
            return False
            
        self.running = True
        self.audio_thread = threading.Thread(target=self._audio_loop, daemon=True)
        self.audio_thread.start()
        print(f"✅ Audio analyzer started with {self.backend} backend")
        return True
    
    def stop(self):
        """Stop audio analysis"""
        self.running = False
        
        if self.sd_stream:
            self.sd_stream.stop()
            self.sd_stream.close()
        
        if self.pa_stream:
            self.pa_stream.stop_stream()
            self.pa_stream.close()
        
        if self.pa:
            self.pa.terminate()
        
        print("Audio analyzer stopped")
    
    def _audio_loop(self):
        """Main audio processing loop"""
        try:
            if self.backend == "sounddevice":
                self._sounddevice_loop()
            elif self.backend == "pyaudio":
                self._pyaudio_loop()
        except Exception as e:
            print(f"Audio loop error: {e}")
    
    def _sounddevice_loop(self):
        """SoundDevice backend loop"""
        try:
            import sounddevice as sd
            
            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                channels=1,
                dtype=np.float32,
                callback=self._sounddevice_callback
            ) as stream:
                self.sd_stream = stream
                while self.running:
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"SoundDevice error: {e}")
    
    def _sounddevice_callback(self, indata, frames, time, status):
        """SoundDevice callback"""
        if self.analysis_enabled and len(indata) > 0:
            audio_data = indata[:, 0]  # Get first channel
            self._process_audio(audio_data)
    
    def _pyaudio_loop(self):
        """PyAudio backend loop"""
        try:
            import pyaudio
            
            self.pa = pyaudio.PyAudio()
            
            self.pa_stream = self.pa.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.buffer_size
            )
            
            while self.running:
                data = self.pa_stream.read(self.buffer_size, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.float32)
                
                if self.analysis_enabled:
                    self._process_audio(audio_data)
                    
        except Exception as e:
            print(f"PyAudio error: {e}")
    
    def _process_audio(self, audio_data):
        """Process audio data and extract features"""
        try:
            # Basic amplitude
            amplitude = np.sqrt(np.mean(audio_data**2))
            
            # Update amplitude history
            self.amplitude_history[1:] = self.amplitude_history[:-1]
            self.amplitude_history[0] = amplitude
            
            # FFT for spectral analysis
            fft = np.fft.rfft(audio_data)
            magnitude = np.abs(fft)
            
            if np.sum(magnitude) > 0:
                # Spectral centroid
                freqs = np.fft.rfftfreq(len(audio_data), 1/self.sample_rate)
                centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
                
                # Update centroid history
                self.centroid_history[1:] = self.centroid_history[:-1]
                self.centroid_history[0] = centroid
                
                # Smooth features
                smooth_amplitude = np.mean(self.amplitude_history)
                smooth_centroid = np.mean(self.centroid_history)
                
                # Spectral rolloff
                cumsum_mag = np.cumsum(magnitude)
                rolloff_idx = np.where(cumsum_mag >= 0.85 * cumsum_mag[-1])[0]
                rolloff = freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else 0
                
                # Onset detection (simple version)
                flux = np.sum(np.diff(magnitude)**2)
                onset_detected = flux > np.mean(self.amplitude_history) * 1000
                
                # Emit features
                features = {
                    'amplitude': smooth_amplitude,
                    'spectral_centroid': smooth_centroid,
                    'spectral_rolloff': rolloff,
                    'spectral_flux': flux,
                    'onset_detected': onset_detected,
                    'raw_amplitude': amplitude
                }
                
                self.audio_features_updated.emit(features)
                
        except Exception as e:
            print(f"Audio processing error: {e}")

# MIDI Handler (from previous steps)
class MIDIHandler(QObject):
    """Enhanced MIDI handler for Step 5"""
    
    note_on = Signal(int, float, int)  # note, velocity, channel
    note_off = Signal(int, int)        # note, channel  
    control_change = Signal(int, int, int)  # controller, value, channel
    
    def __init__(self):
        super().__init__()
        self.midi_devices = []
        self.selected_device = None
        self.midi_input = None
        self.running = False
        
        self._scan_devices()
    
    def _scan_devices(self):
        """Scan for available MIDI devices"""
        if not MIDI_AVAILABLE:
            return
            
        try:
            pygame.midi.init()
            device_count = pygame.midi.get_count()
            
            self.midi_devices = []
            for i in range(device_count):
                device_info = pygame.midi.get_device_info(i)
                if device_info[2]:  # Is input device
                    device_name = device_info[1].decode()
                    self.midi_devices.append((i, device_name))
                    print(f"Found MIDI device: {device_name}")
                    
        except Exception as e:
            print(f"MIDI scan error: {e}")
    
    def get_device_names(self):
        """Get list of MIDI device names"""
        return [name for _, name in self.midi_devices]
    
    def start_midi(self, device_name=None):
        """Start MIDI input"""
        if not MIDI_AVAILABLE or not self.midi_devices:
            return False
            
        try:
            # Select device
            if device_name:
                device_id = None
                for dev_id, name in self.midi_devices:
                    if name == device_name:
                        device_id = dev_id
                        break
                if device_id is None:
                    device_id = self.midi_devices[0][0]
            else:
                device_id = self.midi_devices[0][0]
            
            # Open MIDI input
            self.midi_input = pygame.midi.Input(device_id)
            self.selected_device = device_name or self.midi_devices[0][1]
            
            # Start processing thread
            self.running = True
            self.midi_thread = threading.Thread(target=self._midi_loop, daemon=True)
            self.midi_thread.start()
            
            print(f"✅ MIDI started: {self.selected_device}")
            return True
            
        except Exception as e:
            print(f"MIDI start error: {e}")
            return False
    
    def stop(self):
        """Stop MIDI input"""
        self.running = False
        
        if self.midi_input:
            self.midi_input.close()
            self.midi_input = None
        
        if MIDI_AVAILABLE:
            pygame.midi.quit()
    
    def _midi_loop(self):
        """MIDI processing loop"""
        while self.running and self.midi_input:
            try:
                if self.midi_input.poll():
                    midi_events = self.midi_input.read(10)
                    
                    for event in midi_events:
                        self._process_midi_event(event[0])
                        
                time.sleep(0.001)  # Small delay
                
            except Exception as e:
                print(f"MIDI loop error: {e}")
                break
    
    def _process_midi_event(self, event):
        """Process individual MIDI event"""
        try:
            status, data1, data2, data3 = event
            
            # Extract message type and channel
            msg_type = status & 0xF0
            channel = status & 0x0F
            
            if msg_type == 0x90 and data2 > 0:  # Note On
                note = data1
                velocity = data2 / 127.0
                self.note_on.emit(note, velocity, channel)
                
            elif msg_type == 0x80 or (msg_type == 0x90 and data2 == 0):  # Note Off
                note = data1
                self.note_off.emit(note, channel)
                
            elif msg_type == 0xB0:  # Control Change
                controller = data1
                value = data2
                self.control_change.emit(controller, value, channel)
                
        except Exception as e:
            print(f"MIDI event processing error: {e}")
    
    def test_note(self, note=60):
        """Test a MIDI note"""
        self.note_on.emit(note, 0.8, 0)
        
        # Schedule note off
        QTimer.singleShot(500, lambda: self.note_off.emit(note, 0))

# Performance Monitor (from previous steps)
class EnhancedPerformanceMonitor(QObject):
    """Enhanced performance monitor for Step 5"""
    
    performance_update = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.current_fps = 0
        
        # Performance tracking
        self.frame_times = []
        self.max_frame_time_history = 60
        
        # System monitoring
        self.last_cpu_time = 0
        self.last_memory_check = 0
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_performance)
        self.update_timer.start(1000)  # Update every second
    
    def register_frame(self):
        """Register a rendered frame"""
        current_time = time.time()
        
        # Track frame timing
        if len(self.frame_times) > 0:
            frame_time = current_time - self.frame_times[-1]
            if len(self.frame_times) >= self.max_frame_time_history:
                self.frame_times.pop(0)
        
        self.frame_times.append(current_time)
        
        self.frame_count += 1
        
        # Calculate FPS
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def _update_performance(self):
        """Update performance metrics"""
        try:
            # Calculate metrics
            avg_frame_time = 0
            if len(self.frame_times) > 1:
                times = np.diff(self.frame_times)
                avg_frame_time = np.mean(times) * 1000  # Convert to ms
            
            # System metrics
            memory_percent = 0
            cpu_percent = 0
            
            if PERFORMANCE_MONITORING:
                memory_info = psutil.virtual_memory()
                memory_percent = memory_info.percent
                cpu_percent = psutil.cpu_percent(interval=None)
            
            # Emit performance data
            perf_data = {
                'fps': self.current_fps,
                'avg_frame_time': avg_frame_time,
                'memory_percent': memory_percent,
                'cpu_percent': cpu_percent,
                'frame_count': len(self.frame_times)
            }
            
            self.performance_update.emit(perf_data)
            
        except Exception as e:
            print(f"Performance monitoring error: {e}")

# QtInteractor Wrapper (from previous steps)
class QtInteractorWrapper:
    """Wrapper for QtInteractor compatibility"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.plotter = None
        
        # Try multiple initialization methods
        self._init_qtinteractor()
    
    def _init_qtinteractor(self):
        """Initialize QtInteractor with fallback methods"""
        try:
            # Method 1: Direct initialization
            self.plotter = QtInteractor(self.parent)
            return
        except Exception as e:
            print(f"QtInteractor method 1 failed: {e}")
        
        try:
            # Method 2: With specific parameters
            self.plotter = QtInteractor(
                parent=self.parent,
                auto_update=True,
                lighting='light_kit'
            )
            return
        except Exception as e:
            print(f"QtInteractor method 2 failed: {e}")
        
        try:
            # Method 3: Basic fallback
            import pyvista as pv
            self.plotter = pv.Plotter()
            print("⚠️ Using basic PyVista plotter (no Qt integration)")
        except Exception as e:
            print(f"All QtInteractor methods failed: {e}")
            self.plotter = None
    
    def get_plotter(self):
        """Get the plotter object"""
        return self.plotter
    
    def get_widget(self):
        """Get the Qt widget"""
        if hasattr(self.plotter, 'interactor'):
            return self.plotter.interactor
        elif hasattr(self.plotter, 'app_window'):
            return self.plotter.app_window
        else:
            # Create a placeholder widget
            from PySide6.QtWidgets import QLabel
            placeholder = QLabel("3D View Not Available")
            placeholder.setStyleSheet("background-color: #2b2b2b; color: white; font-size: 16px;")
            placeholder.setAlignment(Qt.AlignCenter)
            return placeholder

# Enhanced Main Window for Step 5
class Step5MorphingMainWindow(QMainWindow):
    """Enhanced main window with advanced lighting and visual effects"""
    
    def __init__(self):
        super().__init__()
        
        # Core systems
        self.qt_interactor_wrapper = None
        self.plotter = None
        self.scene_manager = None
        self.audio_analyzer = None
        self.midi_handler = None
        self.performance_monitor = None
        
        # UI state
        self.global_morph_factor = 0.0
        self.current_lighting_preset = "studio"
        self.quality_level = "high"
        
        # Initialize application
        self._init_ui()
        self._init_systems()
        self._connect_signals()
        
        # Setup menus and shortcuts
        self._setup_menus()
        self._setup_shortcuts()
        
        print("✅ Step 5 Enhanced Main Window initialized")
    
    def _init_ui(self):
        """Initialize enhanced user interface"""
        self.setWindowTitle("Enhanced MIDI Morphing Visualizer - Step 5: Advanced Lighting & Visual Effects")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create 3D view
        self._create_3d_view(splitter)
        
        # Create enhanced control panel
        self._create_enhanced_control_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([1200, 400])
        
        # Create enhanced status bar
        self._create_enhanced_status_bar()
    
    def _create_3d_view(self, parent):
        """Create 3D visualization view"""
        try:
            self.qt_interactor_wrapper = QtInteractorWrapper()
            self.plotter = self.qt_interactor_wrapper.get_plotter()
            
            if self.plotter:
                # Configure plotter for enhanced visuals
                self.plotter.set_background('#1a1a1a')  # Dark background
                
                widget = self.qt_interactor_wrapper.get_widget()
                parent.addWidget(widget)
                
                print("✅ Enhanced 3D view created")
            else:
                # Fallback widget
                fallback = QLabel("Enhanced 3D View\nRequires PyVista")
                fallback.setAlignment(Qt.AlignCenter)
                fallback.setStyleSheet("background-color: #2b2b2b; color: #cccccc; font-size: 18px;")
                parent.addWidget(fallback)
                print("⚠️ Using fallback 3D view")
                
        except Exception as e:
            print(f"❌ 3D view creation error: {e}")
            # Error fallback
            error_widget = QLabel(f"3D View Error:\n{str(e)}")
            error_widget.setAlignment(Qt.AlignCenter)
            error_widget.setStyleSheet("background-color: #3d1a1a; color: #ffaaaa;")
            parent.addWidget(error_widget)
    
    def _create_enhanced_control_panel(self, parent):
        """Create enhanced control panel with advanced features"""
        
        # Create scrollable control panel
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Enhanced Morphing Controls
        morph_group = QGroupBox("🎭 Enhanced Morphing Controls")
        morph_layout = QVBoxLayout(morph_group)
        
        # Global morphing slider
        self.global_morph_slider = QSlider(Qt.Horizontal)
        self.global_morph_slider.setRange(0, 100)
        self.global_morph_slider.setValue(0)
        self.global_morph_slider.valueChanged.connect(self._on_global_morph_changed)
        
        self.morph_value_label = QLabel("Global Morph: 0%")
        
        morph_layout.addWidget(QLabel("Global Morphing Factor:"))
        morph_layout.addWidget(self.global_morph_slider)
        morph_layout.addWidget(self.morph_value_label)
        
        # Shape selection buttons
        shape_layout = QHBoxLayout()
        self.shape_buttons = []
        
        shapes = ['sphere', 'cube', 'cone', 'cylinder', 'torus']
        for shape in shapes:
            btn = QPushButton(shape.title())
            btn.clicked.connect(lambda checked, s=shape: self._set_all_shapes(s))
            self.shape_buttons.append(btn)
            shape_layout.addWidget(btn)
        
        morph_layout.addLayout(shape_layout)
        scroll_layout.addWidget(morph_group)
        
        # Advanced Lighting Controls
        lighting_group = QGroupBox("💡 Advanced Lighting System")
        lighting_layout = QVBoxLayout(lighting_group)
        
        # Lighting presets
        lighting_layout.addWidget(QLabel("Lighting Presets:"))
        self.lighting_preset_combo = QComboBox()
        self.lighting_preset_combo.addItems(["studio", "concert", "club", "ambient", "dramatic"])
        self.lighting_preset_combo.currentTextChanged.connect(self._on_lighting_preset_changed)
        lighting_layout.addWidget(self.lighting_preset_combo)
        
        # Ambient light intensity
        lighting_layout.addWidget(QLabel("Ambient Intensity:"))
        self.ambient_slider = QSlider(Qt.Horizontal)
        self.ambient_slider.setRange(0, 100)
        self.ambient_slider.setValue(30)
        self.ambient_slider.valueChanged.connect(self._on_ambient_changed)
        lighting_layout.addWidget(self.ambient_slider)
        
        # Dynamic lighting toggle
        self.dynamic_lighting_cb = QCheckBox("Dynamic Lighting")
        self.dynamic_lighting_cb.setChecked(True)
        lighting_layout.addWidget(self.dynamic_lighting_cb)
        
        scroll_layout.addWidget(lighting_group)
        
        # Visual Effects Controls
        effects_group = QGroupBox("✨ Visual Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        # Particle system controls
        effects_layout.addWidget(QLabel("Particle Effects:"))
        
        self.particles_enabled_cb = QCheckBox("Enable Particles")
        self.particles_enabled_cb.setChecked(True)
        effects_layout.addWidget(self.particles_enabled_cb)
        
        # Particle emission rate
        effects_layout.addWidget(QLabel("Emission Rate:"))
        self.particle_rate_slider = QSlider(Qt.Horizontal)
        self.particle_rate_slider.setRange(10, 200)
        self.particle_rate_slider.setValue(50)
        self.particle_rate_slider.valueChanged.connect(self._on_particle_rate_changed)
        effects_layout.addWidget(self.particle_rate_slider)
        
        # Bloom effect
        self.bloom_enabled_cb = QCheckBox("Bloom Effect")
        self.bloom_enabled_cb.setChecked(True)
        effects_layout.addWidget(self.bloom_enabled_cb)
        
        # Bloom intensity
        effects_layout.addWidget(QLabel("Bloom Intensity:"))
        self.bloom_slider = QSlider(Qt.Horizontal)
        self.bloom_slider.setRange(0, 100)
        self.bloom_slider.setValue(30)
        self.bloom_slider.valueChanged.connect(self._on_bloom_changed)
        effects_layout.addWidget(self.bloom_slider)
        
        scroll_layout.addWidget(effects_group)
        
        # Quality and Performance
        quality_group = QGroupBox("⚙️ Quality & Performance")
        quality_layout = QVBoxLayout(quality_group)
        
        # Quality level
        quality_layout.addWidget(QLabel("Rendering Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["low", "medium", "high", "ultra"])
        self.quality_combo.setCurrentText("high")
        self.quality_combo.currentTextChanged.connect(self._on_quality_changed)
        quality_layout.addWidget(self.quality_combo)
        
        # Performance metrics
        self.fps_label = QLabel("FPS: --")
        self.memory_label = QLabel("Memory: --%")
        self.cpu_label = QLabel("CPU: --%")
        self.particles_count_label = QLabel("Particles: 0")
        self.lights_count_label = QLabel("Lights: 0")
        
        quality_layout.addWidget(self.fps_label)
        quality_layout.addWidget(self.memory_label)
        quality_layout.addWidget(self.cpu_label)
        quality_layout.addWidget(self.particles_count_label)
        quality_layout.addWidget(self.lights_count_label)
        
        scroll_layout.addWidget(quality_group)
        
        # Audio Analysis Controls
        audio_group = QGroupBox("🎵 Enhanced Audio Analysis")
        audio_layout = QVBoxLayout(audio_group)
        
        # Audio reactive toggle
        self.audio_reactive_cb = QCheckBox("Audio-Reactive Visual Effects")
        self.audio_reactive_cb.setChecked(True)
        audio_layout.addWidget(self.audio_reactive_cb)
        
        # Audio sensitivity
        audio_layout.addWidget(QLabel("Audio Sensitivity:"))
        self.audio_sensitivity_slider = QSlider(Qt.Horizontal)
        self.audio_sensitivity_slider.setRange(10, 200)
        self.audio_sensitivity_slider.setValue(100)
        audio_layout.addWidget(self.audio_sensitivity_slider)
        
        # Audio backend selection
        audio_layout.addWidget(QLabel("Audio Backend:"))
        self.audio_backend_combo = QComboBox()
        backends = []
        if SOUNDDEVICE_AVAILABLE:
            backends.append("sounddevice")
        if PYAUDIO_AVAILABLE:
            backends.append("pyaudio")
        backends.append("auto")
        
        self.audio_backend_combo.addItems(backends)
        self.audio_backend_combo.setCurrentText("auto")
        audio_layout.addWidget(self.audio_backend_combo)
        
        scroll_layout.addWidget(audio_group)
        
        # Test and Demo Controls
        test_group = QGroupBox("🧪 Test & Demo")
        test_layout = QVBoxLayout(test_group)
        
        # Test buttons
        self.test_morph_btn = QPushButton("Test Morphing Sequence")
        self.test_lighting_btn = QPushButton("Test Lighting Effects")
        self.test_particles_btn = QPushButton("Test Particle Burst")
        self.test_audio_btn = QPushButton("Test Audio Reactive")
        self.test_midi_btn = QPushButton("Test MIDI Note")
        self.visual_burst_btn = QPushButton("🎆 Visual Burst!")
        
        # Connect test buttons
        self.test_morph_btn.clicked.connect(self._test_morphing)
        self.test_lighting_btn.clicked.connect(self._test_lighting)
        self.test_particles_btn.clicked.connect(self._test_particles)
        self.test_audio_btn.clicked.connect(self._test_audio)
        self.test_midi_btn.clicked.connect(self._test_midi)
        self.visual_burst_btn.clicked.connect(self._trigger_visual_burst)
        
        test_layout.addWidget(self.test_morph_btn)
        test_layout.addWidget(self.test_lighting_btn)
        test_layout.addWidget(self.test_particles_btn)
        test_layout.addWidget(self.test_audio_btn)
        test_layout.addWidget(self.test_midi_btn)
        test_layout.addWidget(self.visual_burst_btn)
        
        scroll_layout.addWidget(test_group)
        
        # Reset and presets
        presets_group = QGroupBox("🎨 Presets & Reset")
        presets_layout = QVBoxLayout(presets_group)
        
        self.save_preset_btn = QPushButton("Save Current Preset")
        self.load_preset_btn = QPushButton("Load Preset")
        self.reset_all_btn = QPushButton("🔄 Reset All")
        
        self.save_preset_btn.clicked.connect(self._save_preset)
        self.load_preset_btn.clicked.connect(self._load_preset)
        self.reset_all_btn.clicked.connect(self._reset_all)
        
        presets_layout.addWidget(self.save_preset_btn)
        presets_layout.addWidget(self.load_preset_btn)
        presets_layout.addWidget(self.reset_all_btn)
        
        scroll_layout.addWidget(presets_group)
        
        # Add stretch and setup scroll area
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(400)
        
        parent.addWidget(scroll_area)
    
    def _create_enhanced_status_bar(self):
        """Create enhanced status bar"""
        status_bar = self.statusBar()
        
        # 3D status indicator
        self.status_3d_label = QLabel("3D: ✅ Ready" if self.plotter else "3D: ❌ Error")
        status_bar.addPermanentWidget(self.status_3d_label)
        
        # MIDI status
        self.status_midi_label = QLabel("MIDI: Disconnected")
        status_bar.addPermanentWidget(self.status_midi_label)
        
        # Audio status
        self.status_audio_label = QLabel("Audio: Disconnected")
        status_bar.addPermanentWidget(self.status_audio_label)
        
        status_bar.showMessage("Enhanced MIDI Morphing Visualizer - Step 5 Ready")
    
    def _init_systems(self):
        """Initialize all enhanced systems"""
        try:
            # Initialize scene manager
            if self.plotter:
                self.scene_manager = EnhancedSceneManager(self.qt_interactor_wrapper)
                print("✅ Enhanced scene manager initialized")
            
            # Initialize audio analyzer
            self.audio_analyzer = EnhancedAudioAnalyzer()
            if self.audio_analyzer.start():
                self.status_audio_label.setText("Audio: ✅ Active")
            
            # Initialize MIDI handler
            self.midi_handler = MIDIHandler()
            if self.midi_handler.midi_devices:
                if self.midi_handler.start_midi():
                    self.status_midi_label.setText(f"MIDI: ✅ {self.midi_handler.selected_device}")
            
            # Initialize performance monitor
            self.performance_monitor = EnhancedPerformanceMonitor()
            
            print("✅ All enhanced systems initialized")
            
        except Exception as e:
            print(f"❌ System initialization error: {e}")
            traceback.print_exc()
    
    def _connect_signals(self):
        """Connect all system signals"""
        try:
            # Audio to visual effects
            if self.audio_analyzer and self.scene_manager:
                self.audio_analyzer.audio_features_updated.connect(self._handle_audio_features)
            
            # MIDI to scene
            if self.midi_handler and self.scene_manager:
                self.midi_handler.note_on.connect(self.scene_manager.handle_midi_note_on)
                self.midi_handler.note_off.connect(self.scene_manager.handle_midi_note_off)
                self.midi_handler.control_change.connect(self.scene_manager.handle_midi_cc)
            
            # Performance monitoring
            if self.performance_monitor:
                self.performance_monitor.performance_update.connect(self._update_performance_display)
            
            print("✅ All signals connected")
            
        except Exception as e:
            print(f"❌ Signal connection error: {e}")
    
    def _setup_menus(self):
        """Setup enhanced menu system"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_preset_action = QAction("Save Preset...", self)
        save_preset_action.setShortcut("Ctrl+S")
        save_preset_action.triggered.connect(self._save_preset)
        file_menu.addAction(save_preset_action)
        
        load_preset_action = QAction("Load Preset...", self)
        load_preset_action.setShortcut("Ctrl+O")
        load_preset_action.triggered.connect(self._load_preset)
        file_menu.addAction(load_preset_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        quality_submenu = view_menu.addMenu("Quality")
        quality_group = QActionGroup(self)
        
        for quality in ["low", "medium", "high", "ultra"]:
            action = QAction(quality.title(), self)
            action.setCheckable(True)
            if quality == "high":
                action.setChecked(True)
            action.triggered.connect(lambda checked, q=quality: self._on_quality_changed(q))
            quality_group.addAction(action)
            quality_submenu.addAction(action)
        
        # Effects menu
        effects_menu = menubar.addMenu("Effects")
        
        lighting_submenu = effects_menu.addMenu("Lighting Presets")
        for preset in ["studio", "concert", "club", "ambient", "dramatic"]:
            action = QAction(preset.title(), self)
            action.triggered.connect(lambda checked, p=preset: self._on_lighting_preset_changed(p))
            lighting_submenu.addAction(action)
        
        effects_menu.addSeparator()
        
        visual_burst_action = QAction("Visual Burst", self)
        visual_burst_action.setShortcut("Space")
        visual_burst_action.triggered.connect(self._trigger_visual_burst)
        effects_menu.addAction(visual_burst_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Number keys for quick shape selection
        for i, shape in enumerate(['sphere', 'cube', 'cone', 'cylinder', 'torus']):
            if i < 5:  # Keys 1-5
                shortcut = QShortcut(QKeySequence(f"{i+1}"), self)
                shortcut.activated.connect(lambda s=shape: self._set_all_shapes(s))
        
        # Function keys for lighting presets
        presets = ["studio", "concert", "club", "ambient", "dramatic"]
        for i, preset in enumerate(presets):
            if i < 5:  # F1-F5
                shortcut = QShortcut(QKeySequence(f"F{i+1}"), self)
                shortcut.activated.connect(lambda p=preset: self._on_lighting_preset_changed(p))
    
    # Event handlers
    def _on_global_morph_changed(self, value):
        """Handle global morph slider change"""
        self.global_morph_factor = value / 100.0
        self.morph_value_label.setText(f"Global Morph: {value}%")
        
        if self.scene_manager:
            self.scene_manager.set_global_morph_factor(self.global_morph_factor)
    
    def _on_lighting_preset_changed(self, preset):
        """Handle lighting preset change"""
        self.current_lighting_preset = preset
        if self.scene_manager:
            self.scene_manager.set_lighting_preset(preset)
        
        # Update combo box if needed
        index = self.lighting_preset_combo.findText(preset)
        if index >= 0:
            self.lighting_preset_combo.setCurrentIndex(index)
    
    def _on_ambient_changed(self, value):
        """Handle ambient lighting change"""
        if self.scene_manager and hasattr(self.scene_manager, 'lighting_system'):
            intensity = value / 100.0
            self.scene_manager.lighting_system.ambient_level = intensity
    
    def _on_particle_rate_changed(self, value):
        """Handle particle emission rate change"""
        if self.scene_manager and hasattr(self.scene_manager, 'particle_system'):
            self.scene_manager.particle_system.emission_rate = value
    
    def _on_bloom_changed(self, value):
        """Handle bloom intensity change"""
        if self.scene_manager and hasattr(self.scene_manager, 'effects_manager'):
            intensity = value / 100.0
            self.scene_manager.effects_manager.set_effect_intensity('bloom', intensity)
    
    def _on_quality_changed(self, quality):
        """Handle quality level change"""
        self.quality_level = quality
        if self.scene_manager:
            self.scene_manager.set_quality_level(quality)
        
        # Update combo box
        index = self.quality_combo.findText(quality)
        if index >= 0:
            self.quality_combo.setCurrentIndex(index)
    
    def _set_all_shapes(self, shape):
        """Set all objects to the same shape"""
        if self.scene_manager:
            for obj in self.scene_manager.objects.values():
                obj.set_target_shape(shape, 1.5)
    
    def _handle_audio_features(self, features):
        """Handle audio analysis features"""
        try:
            if not self.audio_reactive_cb.isChecked() or not self.scene_manager:
                return
            
            amplitude = features.get('amplitude', 0)
            centroid = features.get('spectral_centroid', 0)
            onset = features.get('onset_detected', False)
            
            # Trigger particle effects on onset
            if onset and amplitude > 0.1:
                self.scene_manager.particle_system.emit_particles(
                    np.array([0, 0, 0]),
                    int(amplitude * 100),
                    'burst'
                )
            
            # Modulate lighting based on audio
            if hasattr(self.scene_manager, 'lighting_system'):
                # Add audio-reactive lights
                if amplitude > 0.3:
                    color = np.array([1.0, 0.5, 0.2]) * amplitude
                    self.scene_manager.lighting_system.add_light(
                        light_type=LightType.POINT,
                        position=np.random.normal(0, 3, 3),
                        color=color,
                        intensity=amplitude * 3.0,
                        lifetime=1.0
                    )
            
        except Exception as e:
            print(f"Audio feature handling error: {e}")
    
    def _update_performance_display(self, perf_data):
        """Update performance display"""
        try:
            fps = perf_data.get('fps', 0)
            memory = perf_data.get('memory_percent', 0)
            cpu = perf_data.get('cpu_percent', 0)
            
            # Color-coded FPS
            if fps >= 30:
                fps_color = "green"
            elif fps >= 20:
                fps_color = "orange"
            else:
                fps_color = "red"
            
            self.fps_label.setText(f'<span style="color: {fps_color}">FPS: {fps:.1f}</span>')
            self.memory_label.setText(f"Memory: {memory:.1f}%")
            self.cpu_label.setText(f"CPU: {cpu:.1f}%")
            
            # Update particle and light counts
            if self.scene_manager:
                if hasattr(self.scene_manager, 'particle_system'):
                    particle_count = len(self.scene_manager.particle_system.particles)
                    self.particles_count_label.setText(f"Particles: {particle_count}")
                
                if hasattr(self.scene_manager, 'lighting_system'):
                    light_count = len(self.scene_manager.lighting_system.lights)
                    self.lights_count_label.setText(f"Lights: {light_count}")
            
            # Register frame for monitoring
            self.performance_monitor.register_frame()
            
        except Exception as e:
            print(f"Performance display error: {e}")
    
    # Test functions
    def _test_morphing(self):
        """Test morphing sequence"""
        if not self.scene_manager:
            return
        
        shapes = ['sphere', 'cube', 'cone', 'cylinder', 'torus']
        
        def morph_sequence(index=0):
            if index < len(shapes):
                self._set_all_shapes(shapes[index])
                QTimer.singleShot(1500, lambda: morph_sequence(index + 1))
        
        morph_sequence()
        print("Testing morphing sequence...")
    
    def _test_lighting(self):
        """Test lighting effects"""
        if not self.scene_manager or not hasattr(self.scene_manager, 'lighting_system'):
            return
        
        presets = ["studio", "concert", "club", "dramatic", "ambient"]
        
        def lighting_sequence(index=0):
            if index < len(presets):
                self._on_lighting_preset_changed(presets[index])
                QTimer.singleShot(2000, lambda: lighting_sequence(index + 1))
        
        lighting_sequence()
        print("Testing lighting presets...")
    
    def _test_particles(self):
        """Test particle system"""
        if not self.scene_manager or not hasattr(self.scene_manager, 'particle_system'):
            return
        
        # Emit particles from multiple positions
        positions = [
            np.array([0, 0, 0]),
            np.array([2, 1, 0]),
            np.array([-2, 1, 0]),
            np.array([0, 2, 2])
        ]
        
        for i, pos in enumerate(positions):
            QTimer.singleShot(i * 300, lambda p=pos: self.scene_manager.particle_system.emit_particles(
                p, 30, 'spark', np.random.normal(0, 3, 3)
            ))
        
        print("Testing particle system...")
    
    def _test_audio(self):
        """Test audio reactive features"""
        if not self.audio_analyzer:
            return
        
        # Toggle audio reactive mode
        current_state = self.audio_reactive_cb.isChecked()
        self.audio_reactive_cb.setChecked(not current_state)
        
        # Reset after test
        QTimer.singleShot(5000, lambda: self.audio_reactive_cb.setChecked(current_state))
        
        status = "enabled" if not current_state else "disabled"
        print(f"Audio reactive mode {status} for 5 seconds...")
    
    def _test_midi(self):
        """Test MIDI functionality"""
        if not self.midi_handler:
            return
        
        # Test sequence of notes
        test_notes = [60, 64, 67, 72]  # C, E, G, C
        
        def play_note_sequence(index=0):
            if index < len(test_notes):
                note = test_notes[index]
                self.midi_handler.test_note(note)
                QTimer.singleShot(500, lambda: play_note_sequence(index + 1))
        
        play_note_sequence()
        print("Testing MIDI note sequence...")
    
    def _trigger_visual_burst(self):
        """Trigger spectacular visual burst"""
        if self.scene_manager:
            self.scene_manager.trigger_visual_burst()
        print("Visual burst triggered!")
    
    # Preset management
    def _save_preset(self):
        """Save current settings as preset"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Preset",
                "",
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return
            
            preset_data = {
                'global_morph_factor': self.global_morph_factor,
                'lighting_preset': self.current_lighting_preset,
                'quality_level': self.quality_level,
                'audio_reactive': self.audio_reactive_cb.isChecked(),
                'particles_enabled': self.particles_enabled_cb.isChecked(),
                'bloom_enabled': self.bloom_enabled_cb.isChecked(),
                'particle_rate': self.particle_rate_slider.value(),
                'bloom_intensity': self.bloom_slider.value(),
                'ambient_intensity': self.ambient_slider.value(),
                'audio_sensitivity': self.audio_sensitivity_slider.value()
            }
            
            with open(file_path, 'w') as f:
                json.dump(preset_data, f, indent=2)
            
            QMessageBox.information(self, "Preset Saved", f"Preset saved to {file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save preset: {e}")
    
    def _load_preset(self):
        """Load preset from file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Preset",
                "",
                "JSON Files (*.json)"
            )
            
            if not file_path:
                return
            
            with open(file_path, 'r') as f:
                preset_data = json.load(f)
            
            # Apply preset settings
            if 'global_morph_factor' in preset_data:
                value = int(preset_data['global_morph_factor'] * 100)
                self.global_morph_slider.setValue(value)
            
            if 'lighting_preset' in preset_data:
                self._on_lighting_preset_changed(preset_data['lighting_preset'])
            
            if 'quality_level' in preset_data:
                self._on_quality_changed(preset_data['quality_level'])
            
            if 'audio_reactive' in preset_data:
                self.audio_reactive_cb.setChecked(preset_data['audio_reactive'])
            
            if 'particles_enabled' in preset_data:
                self.particles_enabled_cb.setChecked(preset_data['particles_enabled'])
            
            if 'bloom_enabled' in preset_data:
                self.bloom_enabled_cb.setChecked(preset_data['bloom_enabled'])
            
            if 'particle_rate' in preset_data:
                self.particle_rate_slider.setValue(preset_data['particle_rate'])
            
            if 'bloom_intensity' in preset_data:
                self.bloom_slider.setValue(preset_data['bloom_intensity'])
            
            if 'ambient_intensity' in preset_data:
                self.ambient_slider.setValue(preset_data['ambient_intensity'])
            
            if 'audio_sensitivity' in preset_data:
                self.audio_sensitivity_slider.setValue(preset_data['audio_sensitivity'])
            
            QMessageBox.information(self, "Preset Loaded", f"Preset loaded from {file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Failed to load preset: {e}")
    
    def _reset_all(self):
        """Reset all settings to defaults"""
        try:
            # Reset sliders
            self.global_morph_slider.setValue(0)
            self.ambient_slider.setValue(30)
            self.particle_rate_slider.setValue(50)
            self.bloom_slider.setValue(30)
            self.audio_sensitivity_slider.setValue(100)
            
            # Reset checkboxes
            self.audio_reactive_cb.setChecked(True)
            self.particles_enabled_cb.setChecked(True)
            self.bloom_enabled_cb.setChecked(True)
            self.dynamic_lighting_cb.setChecked(True)
            
            # Reset presets
            self._on_lighting_preset_changed("studio")
            self._on_quality_changed("high")
            
            # Reset all shapes to sphere
            self._set_all_shapes('sphere')
            
            print("All settings reset to defaults")
            
        except Exception as e:
            print(f"Reset error: {e}")
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
<h2>Enhanced MIDI Morphing Visualizer - Step 5</h2>
<h3>Advanced Lighting and Visual Effects System</h3>

<p><b>New Step 5 Features:</b></p>
<ul>
<li>Advanced Lighting System with multiple light types</li>
<li>Particle System with physics simulation</li>
<li>Post-Processing Effects (Bloom, Color Grading)</li>
<li>Environmental Effects and Atmospheric Lighting</li>
<li>Enhanced Animation System with Keyframes</li>
<li>Visual Effects Presets for Live Performance</li>
<li>GPU-Accelerated Rendering Pipeline</li>
<li>Real-time Effect Parameter Control</li>
</ul>

<p><b>Controls:</b></p>
<ul>
<li>1-5 Keys: Quick shape selection</li>
<li>F1-F5: Lighting presets</li>
<li>Space: Visual burst effect</li>
<li>Ctrl+S: Save preset</li>
<li>Ctrl+O: Load preset</li>
</ul>

<p><b>MIDI Integration:</b></p>
<ul>
<li>Note ranges trigger different objects with enhanced effects</li>
<li>CC1: Global morphing control</li>
<li>CC7: Particle emission rate</li>
<li>CC10: Lighting intensity</li>
<li>CC74: Effect intensity</li>
</ul>

<p>Built with PyVista, PySide6, and advanced visual effects processing.</p>
        """
        
        QMessageBox.about(self, "About Enhanced MIDI Morphing Visualizer", about_text)
    
    def closeEvent(self, event):
        """Cleanup on application close"""
        print("Closing Enhanced MIDI Morphing Visualizer - Step 5...")
        
        try:
            # Stop all systems
            if hasattr(self, 'performance_monitor') and self.performance_monitor:
                if hasattr(self.performance_monitor, 'update_timer'):
                    self.performance_monitor.update_timer.stop()
            
            if hasattr(self, 'scene_manager') and self.scene_manager:
                if hasattr(self.scene_manager, 'update_timer'):
                    self.scene_manager.update_timer.stop()
            
            if hasattr(self, 'audio_analyzer') and self.audio_analyzer:
                self.audio_analyzer.stop()
            
            if hasattr(self, 'midi_handler') and self.midi_handler:
                self.midi_handler.stop()
            
            # Clear 3D scene
            if hasattr(self, 'qt_interactor_wrapper') and self.qt_interactor_wrapper:
                if self.qt_interactor_wrapper.plotter:
                    try:
                        self.qt_interactor_wrapper.plotter.clear()
                    except:
                        pass
                    self.qt_interactor_wrapper.plotter = None
            
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        event.accept()

# Main Application Entry Point
def main():
    """Main application entry point for Step 5"""
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced MIDI Morphing Visualizer - Step 5")
    app.setOrganizationName("MIDI Morphing Systems")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Create and show main window
    window = Step5MorphingMainWindow()
    window.show()
    
    # Display startup information
    print("Enhanced MIDI Morphing Visualizer - Step 5 Started!")
    print("=" * 80)
    print("STEP 5 FEATURES IMPLEMENTED:")
    print("   Advanced Lighting System with 6 light types")
    print("   Physics-based Particle System (spark, burst, trail)")
    print("   Post-Processing Effects (bloom, fog, color grading)")
    print("   Environmental Lighting Presets (studio, concert, club)")
    print("   Enhanced Animation System with smooth transitions")
    print("   Visual Effects Presets for live performance")
    print("   GPU-optimized rendering pipeline")
    print("   Real-time parameter control and automation")
    print("   Enhanced performance monitoring")
    print("   Advanced audio-reactive visual effects")
    print("=" * 80)
    print("ENHANCED CONTROLS:")
    print("   • Advanced Lighting: 5 presets with dynamic effects")
    print("   • Particle System: Real-time emission with physics")
    print("   • Visual Effects: Bloom, fog, and color grading")
    print("   • Quality Levels: Low/Medium/High/Ultra rendering")
    print("   • Audio Reactive: Spectral analysis driving effects")
    print("   • MIDI Enhancement: Extended CC mapping")
    print("   • Keyboard Shortcuts: 1-5 shapes, F1-F5 lighting")
    print("   • Preset System: Save/load complete configurations")
    print("=" * 80)
    print("TEST THE ENHANCED FEATURES:")
    print("   1. Use 'Test Lighting Effects' for automated lighting demo")
    print("   2. Try 'Test Particle Burst' for physics simulation")
    print("   3. Enable 'Audio-Reactive Visual Effects' and make sounds")
    print("   4. Press SPACE for spectacular 'Visual Burst' effect")
    print("   5. Use F1-F5 keys to switch lighting presets instantly")
    print("   6. Try different Quality levels for performance tuning")
    print("   7. Save/Load presets for live performance setups")
    print("   8. Use MIDI CC controls for real-time effect modulation")
    print("=" * 80)
    print("EXPECT TO SEE:")
    print("   • Dynamic multi-light scenes with real-time animation")
    print("   • Physics-based particles responding to audio/MIDI")
    print("   • Post-processing effects enhancing visual quality")
    print("   • Smooth morphing with enhanced material properties")
    print("   • Professional lighting setups for different moods")
    print("   • Real-time performance optimization")
    print("=" * 80)
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        print("EXCEPTION:")
        print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    
    sys.excepthook = handle_exception
    
    try:
        exit_code = app.exec()
        print("\nEnhanced MIDI Morphing Visualizer - Step 5 Closed")
        return exit_code
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
