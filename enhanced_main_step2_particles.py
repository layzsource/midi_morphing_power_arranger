#!/usr/bin/env python3
"""
Enhanced MIDI Morphing Visualizer - Step 2: Advanced Particle Physics
Building on Step 1 (Advanced Audio Analysis), now adding:
- Full particle physics simulation with gravity, drag, forces
- Multiple particle types (spark, burst, trail, bloom, explosion)
- MIDI-triggered particle emission with note-to-color mapping
- Audio-responsive particle effects
- Performance-optimized rendering
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
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Core dependencies
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox,
        QMenuBar, QMenu, QHBoxLayout, QGroupBox, QGridLayout, QTabWidget,
        QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar, QFormLayout
    )
    from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject, QThread
    from PySide6.QtGui import QAction, QFont, QColor, QPalette
    from pyvistaqt import QtInteractor
    import pyvista as pv
    print("✅ Core GUI dependencies available")
except ImportError as e:
    print(f"❌ Missing core dependencies: {e}")
    sys.exit(1)

# Audio backend detection
AUDIO_BACKENDS = {}

try:
    import sounddevice as sd
    AUDIO_BACKENDS['sounddevice'] = True
    print("✅ SoundDevice backend available")
except ImportError:
    AUDIO_BACKENDS['sounddevice'] = False
    print("⚠️ SoundDevice backend not available")

try:
    import pyaudio
    AUDIO_BACKENDS['pyaudio'] = True
    print("✅ PyAudio backend available")
except ImportError:
    AUDIO_BACKENDS['pyaudio'] = False
    print("⚠️ PyAudio backend not available")

try:
    import librosa
    import scipy.signal
    ADVANCED_AUDIO = True
    print("✅ Advanced audio analysis (librosa) available")
except ImportError:
    ADVANCED_AUDIO = False
    print("⚠️ Advanced audio analysis not available")

try:
    import pygame.midi
    MIDI_AVAILABLE = True
    print("✅ MIDI support available")
except ImportError:
    MIDI_AVAILABLE = False
    print("⚠️ MIDI support not available")

try:
    import psutil
    PERFORMANCE_MONITORING = True
    print("✅ Performance monitoring available")
except ImportError:
    PERFORMANCE_MONITORING = False
    print("⚠️ Performance monitoring not available")

# =============================================================================
# Enhanced Configuration for Step 2
# =============================================================================

class AdvancedConfig:
    """Enhanced configuration with all advanced features."""
    
    def __init__(self):
        # Audio backends
        self.PREFERRED_AUDIO_BACKEND = 'sounddevice'
        self.AUDIO_FALLBACK_ENABLED = True
        
        # Basic audio settings
        self.AUDIO_SAMPLE_RATE = 44100
        self.AUDIO_CHUNK_SIZE = 1024
        self.AUDIO_CHANNELS = 1
        self.AUDIO_BUFFER_SIZE = 8192
        self.AUDIO_FFT_SIZE = 2048
        self.AUDIO_HOP_LENGTH = 512
        
        # Spectral analysis
        self.ENABLE_SPECTRAL_CENTROID = True
        self.ENABLE_SPECTRAL_ROLLOFF = True
        self.ENABLE_SPECTRAL_BANDWIDTH = True
        self.ENABLE_SPECTRAL_FLUX = True
        self.ENABLE_ZERO_CROSSING_RATE = True
        
        # Advanced features
        self.ENABLE_MFCC = True
        self.ENABLE_MEL_SPECTROGRAM = True
        self.ENABLE_CHROMA = True
        self.ENABLE_TEMPO_TRACKING = True
        self.ENABLE_BEAT_DETECTION = True
        
        # Frequency analysis
        self.FREQ_MIN = 80
        self.FREQ_MAX = 8000
        
        # Particle system - ENHANCED FOR STEP 2
        self.ENABLE_PARTICLES = True
        self.MAX_PARTICLES = 1000
        self.PARTICLE_LIFETIME = 2.0
        self.PARTICLE_PHYSICS_ENABLED = True
        self.PARTICLE_GRAVITY = [0.0, -9.81, 0.0]
        self.PARTICLE_DRAG = 0.98
        self.PARTICLE_SIZE_RANGE = [0.5, 2.0]
        self.PARTICLE_SPEED_RANGE = [2.0, 15.0]
        self.PARTICLE_EMISSION_RATE = 50.0
        self.PARTICLE_COLOR_VARIATION = 0.3
        self.PARTICLE_PERFORMANCE_MODE = False
        
        # Scene management
        self.MAX_SCENE_OBJECTS = 8
        self.SCENE_PHYSICS_ENABLED = True
        self.SCENE_RECORDING_ENABLED = True

# =============================================================================
# Advanced Particle Physics System - Step 2 Core Feature
# =============================================================================

class ParticleType(Enum):
    """Types of particle effects."""
    SPARK = "spark"
    BURST = "burst"
    TRAIL = "trail"
    BLOOM = "bloom"
    SHOCKWAVE = "shockwave"
    EXPLOSION = "explosion"
    FOUNTAIN = "fountain"
    SPIRAL = "spiral"

@dataclass
class Particle:
    """Individual particle with full physics properties."""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(3))
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    size: float = 1.0
    opacity: float = 1.0
    life_remaining: float = 1.0
    max_life: float = 1.0
    mass: float = 1.0
    drag: float = 0.98
    note: int = 60
    velocity_midi: float = 1.0
    particle_type: ParticleType = ParticleType.SPARK
    spawn_time: float = field(default_factory=time.time)
    
    def update(self, delta_time: float, gravity: np.ndarray = None) -> bool:
        """Update particle physics and return False if particle should be removed."""
        if self.life_remaining <= 0:
            return False
        
        # Apply gravity if provided
        if gravity is not None:
            self.acceleration += gravity * self.mass
        
        # Update physics
        self.velocity += self.acceleration * delta_time
        self.velocity *= self.drag  # Apply drag
        self.position += self.velocity * delta_time
        
        # Update life and derived properties
        self.life_remaining -= delta_time
        life_ratio = self.life_remaining / self.max_life
        
        # Particle type specific behavior
        if self.particle_type == ParticleType.EXPLOSION:
            # Explosions get bigger then fade
            self.size = (1.0 - life_ratio) * 3.0 + 0.5
            self.opacity = life_ratio * 0.9
        elif self.particle_type == ParticleType.TRAIL:
            # Trails maintain size but fade quickly
            self.opacity = life_ratio * life_ratio * 0.8  # Quadratic fade
        elif self.particle_type == ParticleType.BLOOM:
            # Blooms grow slowly and fade gently
            self.size = (1.0 - life_ratio * 0.5) * 2.0
            self.opacity = life_ratio * 0.7
        else:
            # Default behavior for sparks, bursts, etc.
            self.opacity = life_ratio * 0.8 + 0.2  # Keep some minimum opacity
            self.size = max(0.1, self.size * (0.8 + life_ratio * 0.4))
        
        # Reset acceleration for next frame
        self.acceleration = np.zeros(3)
        
        return self.life_remaining > 0

@dataclass
class ParticleEmitter:
    """Particle emitter configuration for different effects."""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    direction: np.ndarray = field(default_factory=lambda: np.array([0, 1, 0]))
    spread_angle: float = 30.0  # degrees
    particle_type: ParticleType = ParticleType.SPARK
    emission_rate: float = 50.0  # particles per second
    particle_life: float = 2.0
    initial_speed: float = 5.0
    speed_variation: float = 0.3
    size_range: Tuple[float, float] = (0.5, 2.0)
    color_base: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    color_variation: float = 0.2
    gravity_scale: float = 1.0
    drag_coefficient: float = 0.98
    enabled: bool = True
    last_emission: float = field(default_factory=time.time)
    burst_count: int = 0  # For burst emissions
    continuous: bool = True  # Continuous vs burst emission

class AdvancedParticleSystem:
    """
    Advanced particle system with full physics simulation.
    This is the core Step 2 enhancement.
    """
    
    def __init__(self, plotter, config: AdvancedConfig):
        self.plotter = plotter
        self.config = config
        
        # Particle storage
        self.active_particles: List[Particle] = []
        self.particle_pools: Dict[ParticleType, List[Particle]] = defaultdict(list)
        self.particle_actors: List[Any] = []  # PyVista actors for rendering
        
        # Emitters
        self.active_emitters: Dict[str, ParticleEmitter] = {}
        self.note_emitters: Dict[int, str] = {}  # Note to emitter ID mapping
        
        # Physics settings
        self.gravity = np.array(config.PARTICLE_GRAVITY)
        self.max_particles = config.MAX_PARTICLES
        self.render_particles = config.ENABLE_PARTICLES
        self.physics_enabled = config.PARTICLE_PHYSICS_ENABLED
        
        # Rendering settings
        self.particle_size_scale = 1.0
        self.opacity_scale = 1.0
        self.performance_mode = config.PARTICLE_PERFORMANCE_MODE
        
        # Performance monitoring
        self.update_times = deque(maxlen=60)
        self.particle_count_history = deque(maxlen=300)  # 5 seconds at 60fps
        self.emission_count = 0
        self.cleanup_count = 0
        
        # Audio responsiveness
        self.audio_amplitude = 0.0
        self.last_onset_time = 0.0
        self.beat_strength = 0.0
        
        print("🎆 Advanced particle system initialized")
    
    def emit_note_particles(self, note: int, velocity: float, position: np.ndarray = None, 
                          particle_type: ParticleType = None) -> str:
        """
        Emit particles when MIDI note is triggered.
        Returns emitter ID for tracking.
        """
        if not self.render_particles:
            return ""
        
        # Generate position based on note if not provided
        if position is None:
            position = self._get_note_position(note, velocity)
        
        # Determine particle type based on note characteristics
        if particle_type is None:
            particle_type = self._get_particle_type_for_note(note, velocity)
        
        # Generate color from note
        color = self._get_note_color(note, velocity)
        
        # Create emitter ID
        emitter_id = f"note_{note}_{time.time()}"
        
        # Create particles based on velocity and type
        num_particles = self._calculate_particle_count(velocity, particle_type)
        
        # Create emitter
        emitter = self._create_emitter(position, color, velocity, particle_type)
        self.active_emitters[emitter_id] = emitter
        self.note_emitters[note] = emitter_id
        
        # Emit initial burst
        self._emit_particle_burst(emitter, num_particles)
        
        self.emission_count += num_particles
        print(f"🎆 Created {num_particles} {particle_type.value} particles for note {note}")
        
        return emitter_id
    
    def emit_audio_responsive_particles(self, amplitude: float, onset_detected: bool = False):
        """Emit particles based on audio analysis."""
        if not self.render_particles:
            return
        
        self.audio_amplitude = amplitude
        
        # Onset-triggered particle burst
        if onset_detected:
            current_time = time.time()
            if current_time - self.last_onset_time > 0.1:  # Debounce onsets
                self.last_onset_time = current_time
                
                # Create onset burst at center
                center_pos = np.array([0.0, 0.0, 0.0])
                onset_color = np.array([1.0, 1.0, 1.0])  # White for onsets
                
                # Create burst emitter
                emitter = ParticleEmitter(
                    position=center_pos,
                    particle_type=ParticleType.EXPLOSION,
                    emission_rate=100.0,
                    initial_speed=8.0 + amplitude * 10.0,
                    spread_angle=180.0,
                    color_base=onset_color,
                    particle_life=1.5,
                    continuous=False
                )
                
                burst_count = int(20 + amplitude * 50)
                self._emit_particle_burst(emitter, burst_count)
                print(f"🎯 Onset burst: {burst_count} particles")
    
    def emit_beat_particles(self, beat_strength: float):
        """Emit particles synchronized to beat detection."""
        if not self.render_particles:
            return
        
        self.beat_strength = beat_strength
        
        # Create rhythmic particle ring
        num_particles = int(5 + beat_strength * 15)
        for i in range(num_particles):
            angle = (i / num_particles) * 2 * np.pi
            radius = 3.0 + beat_strength * 2.0
            
            position = np.array([
                np.cos(angle) * radius,
                0.0,
                np.sin(angle) * radius
            ])
            
            # Beat particles move inward
            velocity = -position * 0.5 * beat_strength
            velocity[1] = 2.0 + beat_strength * 3.0  # Add upward component
            
            color = np.array([1.0, 0.5, 0.0])  # Orange for beats
            
            particle = Particle(
                position=position,
                velocity=velocity,
                color=color,
                size=1.0 + beat_strength,
                life_remaining=2.0,
                max_life=2.0,
                particle_type=ParticleType.BURST,
                drag=0.95
            )
            
            self.active_particles.append(particle)
        
        print(f"🥁 Beat particles: {num_particles} (strength: {beat_strength:.2f})")
    
    def _get_note_position(self, note: int, velocity: float) -> np.ndarray:
        """Generate position based on note characteristics."""
        # Map note to position in 3D space
        octave = note // 12
        note_in_octave = note % 12
        
        # Create circular arrangement based on note
        angle = (note_in_octave / 12.0) * 2 * np.pi
        radius = 2.0 + velocity * 3.0 + (octave - 4) * 0.5
        
        height = (octave - 4) * 1.0 + velocity * 2.0
        
        return np.array([
            np.cos(angle) * radius,
            height,
            np.sin(angle) * radius
        ])
    
    def _get_particle_type_for_note(self, note: int, velocity: float) -> ParticleType:
        """Determine particle type based on note characteristics."""
        if velocity > 0.9:
            return ParticleType.EXPLOSION
        elif velocity > 0.7:
            return ParticleType.BURST
        elif note < 48:  # Low notes
            return ParticleType.BLOOM
        elif note > 84:  # High notes
            return ParticleType.SPARK
        elif velocity < 0.3:
            return ParticleType.TRAIL
        else:
            return ParticleType.FOUNTAIN
    
    def _get_note_color(self, note: int, velocity: float) -> np.ndarray:
        """Generate color based on note and velocity."""
        # Map note to hue (chromatic circle)
        hue = (note % 12) / 12.0
        
        # Velocity affects saturation and brightness
        saturation = 0.6 + velocity * 0.4
        brightness = 0.5 + velocity * 0.5
        
        return np.array(colorsys.hsv_to_rgb(hue, saturation, brightness))
    
    def _calculate_particle_count(self, velocity: float, particle_type: ParticleType) -> int:
        """Calculate number of particles to emit based on velocity and type."""
        base_count = {
            ParticleType.SPARK: 10,
            ParticleType.BURST: 25,
            ParticleType.TRAIL: 5,
            ParticleType.BLOOM: 35,
            ParticleType.EXPLOSION: 60,
            ParticleType.FOUNTAIN: 20,
            ParticleType.SPIRAL: 15,
            ParticleType.SHOCKWAVE: 40
        }
        
        count = base_count.get(particle_type, 15)
        count = int(count * (0.5 + velocity * 1.5))
        
        # Performance limiting
        if self.performance_mode:
            count = min(count, 20)
        
        return min(count, self.max_particles - len(self.active_particles))
    
    def _create_emitter(self, position: np.ndarray, color: np.ndarray, 
                       velocity: float, particle_type: ParticleType) -> ParticleEmitter:
        """Create particle emitter with appropriate settings."""
        
        # Type-specific emitter settings
        if particle_type == ParticleType.EXPLOSION:
            return ParticleEmitter(
                position=position,
                particle_type=particle_type,
                emission_rate=200.0,
                initial_speed=5.0 + velocity * 15.0,
                spread_angle=180.0,
                color_base=color,
                particle_life=1.0 + velocity,
                size_range=(0.8, 2.5),
                continuous=False
            )
        elif particle_type == ParticleType.FOUNTAIN:
            return ParticleEmitter(
                position=position,
                direction=np.array([0, 1, 0]),
                particle_type=particle_type,
                emission_rate=30.0,
                initial_speed=3.0 + velocity * 8.0,
                spread_angle=45.0,
                color_base=color,
                particle_life=2.0 + velocity,
                continuous=True
            )
        elif particle_type == ParticleType.SPIRAL:
            return ParticleEmitter(
                position=position,
                particle_type=particle_type,
                emission_rate=40.0,
                initial_speed=4.0 + velocity * 6.0,
                spread_angle=90.0,
                color_base=color,
                particle_life=2.5,
                continuous=True
            )
        else:
            # Default emitter
            return ParticleEmitter(
                position=position,
                particle_type=particle_type,
                emission_rate=50.0,
                initial_speed=4.0 + velocity * 8.0,
                spread_angle=60.0,
                color_base=color,
                particle_life=1.5 + velocity,
                continuous=False
            )
    
    def _emit_particle_burst(self, emitter: ParticleEmitter, count: int):
        """Emit a burst of particles from an emitter."""
        for _ in range(count):
            if len(self.active_particles) >= self.max_particles:
                break
            
            particle = self._create_single_particle(emitter)
            self.active_particles.append(particle)
    
    def _create_single_particle(self, emitter: ParticleEmitter) -> Particle:
        """Create a single particle from an emitter."""
        # Random direction within spread angle
        if emitter.particle_type == ParticleType.SPIRAL:
            # Spiral particles follow a helical path
            angle = np.random.uniform(0, 2 * np.pi)
            spiral_factor = np.random.uniform(0.5, 1.5)
            direction = np.array([
                np.cos(angle) * spiral_factor,
                1.0,
                np.sin(angle) * spiral_factor
            ])
        else:
            # Standard random direction within cone
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, np.radians(emitter.spread_angle))
            
            direction = np.array([
                np.sin(phi) * np.cos(theta),
                np.cos(phi),
                np.sin(phi) * np.sin(theta)
            ])
            
            # Apply emitter direction
            # Simple rotation (could be enhanced with proper rotation matrices)
            direction = direction + emitter.direction * 0.5
        
        # Normalize and apply speed
        direction = direction / np.linalg.norm(direction)
        speed = emitter.initial_speed * (1.0 + np.random.uniform(-emitter.speed_variation, 
                                                                emitter.speed_variation))
        velocity = direction * speed
        
        # Add some randomness to position
        position_offset = np.random.uniform(-0.1, 0.1, 3)
        position = emitter.position + position_offset
        
        # Color variation
        color = emitter.color_base.copy()
        if emitter.color_variation > 0:
            color += np.random.uniform(-emitter.color_variation, 
                                     emitter.color_variation, 3)
            color = np.clip(color, 0.0, 1.0)
        
        # Size variation
        size = np.random.uniform(*emitter.size_range)
        
        return Particle(
            position=position,
            velocity=velocity,
            acceleration=np.zeros(3),
            color=color,
            size=size,
            opacity=1.0,
            life_remaining=emitter.particle_life,
            max_life=emitter.particle_life,
            mass=np.random.uniform(0.8, 1.2),
            drag=emitter.drag_coefficient,
            particle_type=emitter.particle_type
        )
    
    def update(self, delta_time: float):
        """Update all particles and emitters."""
        if not self.render_particles:
            return
        
        start_time = time.time()
        
        # Update particles
        active_particles = []
        for particle in self.active_particles:
            if particle.update(delta_time, self.gravity if self.physics_enabled else None):
                active_particles.append(particle)
            else:
                self.cleanup_count += 1
        
        self.active_particles = active_particles
        
        # Update continuous emitters
        self._update_continuous_emitters(delta_time)
        
        # Update rendering
        self._update_particle_rendering()
        
        # Performance tracking
        update_time = time.time() - start_time
        self.update_times.append(update_time)
        self.particle_count_history.append(len(self.active_particles))
        
        # Performance optimization
        if self.performance_mode and len(self.active_particles) > self.max_particles * 0.8:
            self._optimize_performance()
    
    def _update_continuous_emitters(self, delta_time: float):
        """Update continuous particle emitters."""
        current_time = time.time()
        
        for emitter_id, emitter in list(self.active_emitters.items()):
            if not emitter.enabled or not emitter.continuous:
                continue
            
            # Calculate particles to emit this frame
            time_since_last = current_time - emitter.last_emission
            particles_to_emit = int(emitter.emission_rate * time_since_last)
            
            if particles_to_emit > 0:
                particles_to_emit = min(particles_to_emit, 10)  # Limit per frame
                self._emit_particle_burst(emitter, particles_to_emit)
                emitter.last_emission = current_time
    
    def _update_particle_rendering(self):
        """Update particle visualization."""
        try:
            # Clear old particle actors
            for actor in self.particle_actors:
                self.plotter.remove_actor(actor)
            self.particle_actors.clear()
            
            if not self.active_particles:
                return
            
            # Group particles by type for optimized rendering
            particles_by_type = defaultdict(list)
            for particle in self.active_particles:
                particles_by_type[particle.particle_type].append(particle)
            
            # Render each particle type
            for particle_type, particles in particles_by_type.items():
                self._render_particle_group(particle_type, particles)
                
        except Exception as e:
            print(f"Particle rendering error: {e}")
    
    def _render_particle_group(self, particle_type: ParticleType, particles: List[Particle]):
        """Render a group of particles of the same type."""
        if not particles:
            return
        
        try:
            # Extract particle data
            positions = np.array([p.position for p in particles])
            colors = np.array([p.color for p in particles])
            sizes = np.array([p.size for p in particles])
            opacities = np.array([p.opacity for p in particles])
            
            # Create point cloud
            point_cloud = pv.PolyData(positions)
            
            # Add particle properties
            point_cloud['colors'] = (colors * 255).astype(np.uint8)
            point_cloud['sizes'] = sizes * self.particle_size_scale
            point_cloud['opacities'] = opacities * self.opacity_scale
            
            # Particle type specific rendering
            if particle_type == ParticleType.EXPLOSION:
                # Larger, more dramatic rendering
                actor = self.plotter.add_mesh(
                    point_cloud,
                    style='points',
                    point_size=15,
                    opacity=0.9,
                    render_points_as_spheres=True
                )
            elif particle_type == ParticleType.TRAIL:
                # Smaller, more subtle
                actor = self.plotter.add_mesh(
                    point_cloud,
                    style='points',
                    point_size=5,
                    opacity=0.6,
                    render_points_as_spheres=False
                )
            elif particle_type == ParticleType.SPARK:
                # Sharp, bright points
                actor = self.plotter.add_mesh(
                    point_cloud,
                    style='points',
                    point_size=8,
                    opacity=0.8,
                    render_points_as_spheres=False
                )
            else:
                # Default rendering
                actor = self.plotter.add_mesh(
                    point_cloud,
                    style='points',
                    point_size=10,
                    opacity=0.7,
                    render_points_as_spheres=True
                )
            
            self.particle_actors.append(actor)
            
        except Exception as e:
            print(f"Error rendering {particle_type.value} particles: {e}")
    
    def _optimize_performance(self):
        """Optimize performance when particle count is high."""
        # Remove oldest particles first
        if len(self.active_particles) > self.max_particles:
            self.active_particles.sort(key=lambda p: p.spawn_time)
            excess = len(self.active_particles) - self.max_particles
            self.active_particles = self.active_particles[excess:]
            print(f"⚡ Performance optimization: removed {excess} old particles")
    
    def clear_all_particles(self):
        """Clear all active particles and emitters."""
        self.active_particles.clear()
        self.active_emitters.clear()
        self.note_emitters.clear()
        
        # Clear visual actors
        for actor in self.particle_actors:
            self.plotter.remove_actor(actor)
        self.particle_actors.clear()
        
        print("🧹 All particles cleared")
    
    def set_performance_mode(self, enabled: bool):
        """Enable/disable performance mode."""
        self.performance_mode = enabled
        if enabled:
            self.max_particles = 500
            print("⚡ Particle performance mode enabled")
        else:
            self.max_particles = self.config.MAX_PARTICLES
            print("🎆 Full particle quality mode enabled")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        if not self.update_times:
            return {}
        
        avg_update_time = np.mean(self.update_times)
        max_update_time = np.max(self.update_times)
        avg_particle_count = np.mean(self.particle_count_history) if self.particle_count_history else 0
        
        return {
            'active_particles': len(self.active_particles),
            'active_emitters': len(self.active_emitters),
            'avg_update_time_ms': avg_update_time * 1000,
            'max_update_time_ms': max_update_time * 1000,
            'avg_particle_count': avg_particle_count,
            'performance_mode': self.performance_mode,
            'total_emissions': self.emission_count,
            'total_cleanups': self.cleanup_count,
            'total_particle_actors': len(self.particle_actors)
        }

# =============================================================================
# Audio Backend and Analysis System (From Step 1 - Maintained)
# =============================================================================

class AudioBackend(Enum):
    SOUNDDEVICE = "sounddevice"
    PYAUDIO = "pyaudio"

class AdvancedAudioAnalyzer(QObject):
    """
    Comprehensive audio analysis with multiple backends and advanced features.
    (Maintained from Step 1)
    """
    
    # Signals for all audio features
    amplitude_signal = Signal(float)
    spectral_centroid_signal = Signal(float)
    spectral_rolloff_signal = Signal(float)
    spectral_bandwidth_signal = Signal(float)
    spectral_flux_signal = Signal(float)
    zero_crossing_rate_signal = Signal(float)
    onset_detected_signal = Signal(float)
    beat_detected_signal = Signal(float, float)  # beat_time, tempo
    tempo_signal = Signal(float)
    mfcc_signal = Signal(np.ndarray)
    mel_spectrogram_signal = Signal(np.ndarray)
    chroma_signal = Signal(np.ndarray)
    
    def __init__(self, config: AdvancedConfig):
        super().__init__()
        self.config = config
        self.current_backend = None
        self.audio_stream = None
        self.running = False
        self.thread = None
        
        # Audio buffers
        self.audio_queue = queue.Queue()
        self.audio_buffer = np.zeros(config.AUDIO_BUFFER_SIZE)
        self.previous_frame = np.zeros(config.AUDIO_FFT_SIZE // 2 + 1)
        
        # Feature tracking
        self.previous_features = {}
        self.onset_history = deque(maxlen=100)
        
        # Performance monitoring
        self.processing_times = deque(maxlen=100)
        self.is_active = False
        
        # Initialize backend
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Initialize the best available audio backend."""
        preferred = self.config.PREFERRED_AUDIO_BACKEND
        
        if preferred == 'sounddevice' and AUDIO_BACKENDS['sounddevice']:
            self.current_backend = AudioBackend.SOUNDDEVICE
            print("🎵 Using SoundDevice backend")
        elif preferred == 'pyaudio' and AUDIO_BACKENDS['pyaudio']:
            self.current_backend = AudioBackend.PYAUDIO
            print("🎵 Using PyAudio backend")
        elif self.config.AUDIO_FALLBACK_ENABLED:
            # Try fallback
            if AUDIO_BACKENDS['sounddevice']:
                self.current_backend = AudioBackend.SOUNDDEVICE
                print("🎵 Falling back to SoundDevice backend")
            elif AUDIO_BACKENDS['pyaudio']:
                self.current_backend = AudioBackend.PYAUDIO
                print("🎵 Falling back to PyAudio backend")
            else:
                print("❌ No audio backends available")
                return False
        else:
            print("❌ Preferred audio backend not available and fallback disabled")
            return False
        
        return True
    
    def start(self):
        """Start audio analysis."""
        if self.is_active:
            return True
            
        try:
            if self.current_backend == AudioBackend.SOUNDDEVICE:
                return self._start_sounddevice()
            elif self.current_backend == AudioBackend.PYAUDIO:
                return self._start_pyaudio()
            else:
                return False
        except Exception as e:
            print(f"❌ Failed to start audio analysis: {e}")
            return False
    
    def _start_sounddevice(self):
        """Start SoundDevice backend."""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"SoundDevice status: {status}")
                if not self.audio_queue.full():
                    self.audio_queue.put(indata[:, 0].copy())  # Take first channel
            
            self.audio_stream = sd.InputStream(
                samplerate=self.config.AUDIO_SAMPLE_RATE,
                channels=self.config.AUDIO_CHANNELS,
                blocksize=self.config.AUDIO_CHUNK_SIZE,
                callback=audio_callback,
                dtype=np.float32
            )
            
            self.audio_stream.start()
            self._start_analysis_thread()
            
            print("✅ SoundDevice audio analysis started")
            return True
            
        except Exception as e:
            print(f"❌ SoundDevice startup failed: {e}")
            return False
    
    def _start_pyaudio(self):
        """Start PyAudio backend."""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            
            def audio_callback(in_data, frame_count, time_info, status):
                try:
                    if status:
                        print(f"PyAudio status: {status}")
                    
                    audio_data = np.frombuffer(in_data, dtype=np.float32)
                    if not self.audio_queue.full():
                        self.audio_queue.put(audio_data.copy())
                    
                    return (None, pyaudio.paContinue)
                except Exception as e:
                    print(f"PyAudio callback error: {e}")
                    return (None, pyaudio.paAbort)
            
            # Find best input device
            device_index = self._find_best_input_device()
            
            self.audio_stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=self.config.AUDIO_CHANNELS,
                rate=self.config.AUDIO_SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.config.AUDIO_CHUNK_SIZE,
                stream_callback=audio_callback
            )
            
            self.audio_stream.start_stream()
            self._start_analysis_thread()
            
            print("✅ PyAudio audio analysis started")
            return True
            
        except Exception as e:
            print(f"❌ PyAudio startup failed: {e}")
            return False
    
    def _find_best_input_device(self):
        """Find the best input device for PyAudio."""
        try:
            # Try default first
            default_device = self.pyaudio_instance.get_default_input_device_info()
            if default_device['maxInputChannels'] > 0:
                print(f"Using default audio input: {default_device['name']}")
                return default_device['index']
        except:
            pass
        
        # Find first available input device
        for i in range(self.pyaudio_instance.get_device_count()):
            device_info = self.pyaudio_instance.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Using audio input: {device_info['name']}")
                return i
        
        print("❌ No audio input devices found")
        return None
    
    def _start_analysis_thread(self):
        """Start the audio analysis thread."""
        self.running = True
        self.is_active = True
        self.thread = threading.Thread(target=self._analysis_loop, daemon=True)
        self.thread.start()
    
    def _analysis_loop(self):
        """Main audio analysis loop with comprehensive feature extraction."""
        while self.running:
            try:
                # Get audio data
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                start_time = time.time()
                
                # Update buffer
                self._update_buffer(audio_chunk)
                
                # Extract all features
                features = self._extract_comprehensive_features()
                
                # Emit signals
                self._emit_feature_signals(features)
                
                # Performance tracking
                processing_time = time.time() - start_time
                self.processing_times.append(processing_time)
                
            except Exception as e:
                print(f"Audio analysis error: {e}")
    
    def _update_buffer(self, new_chunk):
        """Update the audio buffer with new data."""
        try:
            chunk_size = len(new_chunk)
            
            # Shift buffer and add new data
            self.audio_buffer[:-chunk_size] = self.audio_buffer[chunk_size:]
            self.audio_buffer[-chunk_size:] = new_chunk
            
        except Exception as e:
            print(f"Buffer update error: {e}")
    
    def _extract_comprehensive_features(self):
        """Extract all audio features."""
        features = {}
        
        try:
            # Skip if buffer is too quiet
            if np.max(np.abs(self.audio_buffer)) < 1e-6:
                return {}
            
            # Basic amplitude features
            features['rms'] = np.sqrt(np.mean(self.audio_buffer ** 2))
            features['peak_amplitude'] = np.max(np.abs(self.audio_buffer))
            
            # Zero-crossing rate
            if self.config.ENABLE_ZERO_CROSSING_RATE:
                features['zero_crossing_rate'] = self._compute_zero_crossing_rate()
            
            # Spectral analysis
            fft = np.fft.rfft(self.audio_buffer)
            magnitude_spectrum = np.abs(fft)
            power_spectrum = magnitude_spectrum ** 2
            freqs = np.fft.rfftfreq(len(self.audio_buffer), 1/self.config.AUDIO_SAMPLE_RATE)
            
            # Filter to frequency range
            freq_mask = (freqs >= self.config.FREQ_MIN) & (freqs <= self.config.FREQ_MAX)
            
            if np.any(freq_mask):
                filtered_power = power_spectrum[freq_mask]
                filtered_freqs = freqs[freq_mask]
                
                # Spectral centroid
                if self.config.ENABLE_SPECTRAL_CENTROID:
                    features['spectral_centroid'] = self._compute_spectral_centroid(
                        filtered_freqs, filtered_power)
                
                # Spectral rolloff
                if self.config.ENABLE_SPECTRAL_ROLLOFF:
                    features['spectral_rolloff'] = self._compute_spectral_rolloff(
                        filtered_freqs, filtered_power)
                
                # Spectral bandwidth
                if self.config.ENABLE_SPECTRAL_BANDWIDTH:
                    features['spectral_bandwidth'] = self._compute_spectral_bandwidth(
                        filtered_freqs, filtered_power, features.get('spectral_centroid', 0))
                
                # Spectral flux
                if self.config.ENABLE_SPECTRAL_FLUX:
                    features['spectral_flux'] = self._compute_spectral_flux(magnitude_spectrum)
            
            # Advanced features (requires librosa)
            if ADVANCED_AUDIO:
                # MFCC
                if self.config.ENABLE_MFCC:
                    features['mfcc'] = self._compute_mfcc()
                
                # Mel-spectrogram
                if self.config.ENABLE_MEL_SPECTROGRAM:
                    features['mel_spectrogram'] = self._compute_mel_spectrogram()
                
                # Chroma features
                if self.config.ENABLE_CHROMA:
                    features['chroma'] = self._compute_chroma()
                
                # Onset detection
                features['onset_detected'] = self._detect_onsets()
                
                # Tempo and beat tracking
                if self.config.ENABLE_TEMPO_TRACKING:
                    tempo_info = self._track_tempo_and_beats()
                    features.update(tempo_info)
            
            features['timestamp'] = time.time()
            return features
            
        except Exception as e:
            print(f"Feature extraction error: {e}")
            return {}
    
    def _compute_zero_crossing_rate(self):
        """Compute zero-crossing rate."""
        if ADVANCED_AUDIO:
            return np.mean(librosa.feature.zero_crossing_rate(self.audio_buffer)[0])
        else:
            # Simple zero-crossing rate calculation
            zero_crossings = np.sum(np.diff(np.sign(self.audio_buffer)) != 0)
            return zero_crossings / len(self.audio_buffer)
    
    def _compute_spectral_centroid(self, freqs, power):
        """Compute spectral centroid."""
        if np.sum(power) > 0:
            return np.sum(freqs * power) / np.sum(power)
        return 0.0
    
    def _compute_spectral_rolloff(self, freqs, power):
        """Compute spectral rolloff (85% energy)."""
        cumsum = np.cumsum(power)
        total_energy = cumsum[-1]
        if total_energy > 0:
            rolloff_idx = np.where(cumsum >= 0.85 * total_energy)[0]
            if len(rolloff_idx) > 0:
                return freqs[rolloff_idx[0]]
        return freqs[-1] if len(freqs) > 0 else 0.0
    
    def _compute_spectral_bandwidth(self, freqs, power, centroid):
        """Compute spectral bandwidth."""
        if centroid > 0 and np.sum(power) > 0:
            return np.sqrt(np.sum(((freqs - centroid) ** 2) * power) / np.sum(power))
        return 0.0
    
    def _compute_spectral_flux(self, magnitude_spectrum):
        """Compute spectral flux (change in spectrum)."""
        flux = np.sum((magnitude_spectrum - self.previous_frame) ** 2)
        self.previous_frame = magnitude_spectrum.copy()
        return flux
    
    def _compute_mfcc(self):
        """Compute MFCC features."""
        try:
            mfccs = librosa.feature.mfcc(
                y=self.audio_buffer,
                sr=self.config.AUDIO_SAMPLE_RATE,
                n_mfcc=13,  # Standard 13 coefficients
                n_fft=self.config.AUDIO_FFT_SIZE,
                hop_length=self.config.AUDIO_HOP_LENGTH
            )
            return np.mean(mfccs, axis=1)  # Average over time
        except Exception as e:
            print(f"MFCC computation error: {e}")
            return np.zeros(13)
    
    def _compute_mel_spectrogram(self):
        """Compute mel-spectrogram."""
        try:
            mel_spec = librosa.feature.melspectrogram(
                y=self.audio_buffer,
                sr=self.config.AUDIO_SAMPLE_RATE,
                n_mels=128,
                fmin=0,
                fmax=None
            )
            return np.mean(mel_spec, axis=1)  # Average over time
        except Exception as e:
            print(f"Mel-spectrogram computation error: {e}")
            return np.zeros(128)
    
    def _compute_chroma(self):
        """Compute chroma features."""
        try:
            chroma = librosa.feature.chroma_stft(
                y=self.audio_buffer,
                sr=self.config.AUDIO_SAMPLE_RATE
            )
            return np.mean(chroma, axis=1)  # Average over time
        except Exception as e:
            print(f"Chroma computation error: {e}")
            return np.zeros(12)
    
    def _detect_onsets(self):
        """Detect onset events."""
        try:
            onset_frames = librosa.onset.onset_detect(
                y=self.audio_buffer,
                sr=self.config.AUDIO_SAMPLE_RATE,
                units='time',
                hop_length=self.config.AUDIO_HOP_LENGTH
            )
            
            # Track onset history for adaptive threshold
            onset_detected = len(onset_frames) > 0
            self.onset_history.append(onset_detected)
            
            return onset_detected
        except Exception as e:
            print(f"Onset detection error: {e}")
            return False
    
    def _track_tempo_and_beats(self):
        """Track tempo and beat positions."""
        tempo_info = {}
        try:
            # Tempo estimation
            tempo, beats = librosa.beat.beat_track(
                y=self.audio_buffer,
                sr=self.config.AUDIO_SAMPLE_RATE,
                trim=False
            )
            
            tempo_info['tempo'] = float(tempo) if tempo > 0 else 0.0
            tempo_info['beat_detected'] = len(beats) > 0
            tempo_info['beat_strength'] = np.mean(beats) if len(beats) > 0 else 0.0
            
        except Exception as e:
            print(f"Tempo tracking error: {e}")
            tempo_info = {'tempo': 0.0, 'beat_detected': False, 'beat_strength': 0.0}
        
        return tempo_info
    
    def _emit_feature_signals(self, features):
        """Emit all feature signals."""
        try:
            if 'rms' in features:
                self.amplitude_signal.emit(features['rms'])
            
            if 'spectral_centroid' in features:
                self.spectral_centroid_signal.emit(features['spectral_centroid'])
            
            if 'spectral_rolloff' in features:
                self.spectral_rolloff_signal.emit(features['spectral_rolloff'])
            
            if 'spectral_bandwidth' in features:
                self.spectral_bandwidth_signal.emit(features['spectral_bandwidth'])
            
            if 'spectral_flux' in features:
                self.spectral_flux_signal.emit(features['spectral_flux'])
            
            if 'zero_crossing_rate' in features:
                self.zero_crossing_rate_signal.emit(features['zero_crossing_rate'])
            
            if 'onset_detected' in features and features['onset_detected']:
                self.onset_detected_signal.emit(time.time())
            
            if 'tempo' in features and features['tempo'] > 0:
                self.tempo_signal.emit(features['tempo'])
            
            if 'beat_detected' in features and features['beat_detected']:
                beat_strength = features.get('beat_strength', 1.0)
                self.beat_detected_signal.emit(time.time(), beat_strength)
            
            if 'mfcc' in features:
                self.mfcc_signal.emit(features['mfcc'])
            
            if 'mel_spectrogram' in features:
                self.mel_spectrogram_signal.emit(features['mel_spectrogram'])
            
            if 'chroma' in features:
                self.chroma_signal.emit(features['chroma'])
                
        except Exception as e:
            print(f"Signal emission error: {e}")
    
    def stop(self):
        """Stop audio analysis."""
        self.running = False
        self.is_active = False
        
        if self.audio_stream:
            if self.current_backend == AudioBackend.SOUNDDEVICE:
                self.audio_stream.stop()
                self.audio_stream.close()
            elif self.current_backend == AudioBackend.PYAUDIO:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                if hasattr(self, 'pyaudio_instance'):
                    self.pyaudio_instance.terminate()
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        print("🔇 Advanced audio analysis stopped")

# =============================================================================
# Simple Scene Manager (For Step 2 - Will be enhanced in Step 3)
# =============================================================================

class SimpleSceneManager:
    """Simple scene manager for Step 2 - will be enhanced in Step 3."""
    
    def __init__(self, plotter, config: AdvancedConfig):
        self.plotter = plotter
        self.config = config
        self.objects = {}
        self.physics_enabled = config.SCENE_PHYSICS_ENABLED
        print("🎭 Simple scene manager initialized")
        
        # Create a simple test sphere
        self._create_test_scene()
    
    def _create_test_scene(self):
        """Create a simple test scene."""
        sphere = pv.Sphere(radius=1.0)
        self.test_actor = self.plotter.add_mesh(
            sphere,
            color='lightblue',
            opacity=0.8
        )
        print("✨ Test sphere created")
    
    def handle_midi_note(self, note: int, velocity: float, note_on: bool = True, channel: int = 0):
        """Handle MIDI note events."""
        if note_on:
            # Change sphere color based on note
            hue = (note % 12) / 12.0
            color = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            if hasattr(self, 'test_actor'):
                self.test_actor.GetProperty().SetColor(color)
            print(f"🎵 Note {note} ON (velocity: {velocity:.2f}) - Color: {color}")
        else:
            print(f"🎵 Note {note} OFF")
    
    def update_physics(self, delta_time: float):
        """Mock physics update."""
        pass
    
    def set_global_morph_blend(self, blend: float):
        """Mock morph blend."""
        print(f"🔄 Global morph blend: {blend:.2f}")
    
    def get_scene_summary(self) -> Dict:
        """Get scene summary."""
        return {
            'total_objects': 1,
            'active_objects': 1,
            'total_active_notes': 0,
            'physics_enabled': self.physics_enabled,
            'recording_enabled': False,
            'global_morph_blend': 0.0
        }

# =============================================================================
# Performance Monitor (From Step 1 - Maintained)
# =============================================================================

class SimplePerformanceMonitor(QObject):
    """Performance monitor from Step 1."""
    
    performance_update_signal = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self.monitoring = False
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_performance)
        self.timer.setInterval(1000)
        self.last_frame_time = time.time()
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring = True
        self.timer.start()
        print("📊 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring = False
        self.timer.stop()
        print("📊 Performance monitoring stopped")
    
    def record_frame(self):
        """Record a frame for FPS calculation."""
        pass
    
    def _update_performance(self):
        """Mock performance update."""
        performance_data = {
            'fps': 60.0,
            'memory_mb': 150.0,
            'cpu_percent': 25.0,
            'timestamp': time.time()
        }
        self.performance_update_signal.emit(performance_data)

# =============================================================================
# Enhanced Main Window - Step 2: Particle Physics Integration
# =============================================================================

class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with Step 2: Advanced Particle Physics."""
    
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.config = AdvancedConfig()
        
        # Core components
        self.audio_analyzer = None
        self.particle_system = None
        self.scene_manager = None
        self.performance_monitor = None
        
        # MIDI
        self.midi_input = None
        self.midi_thread = None
        
        # UI components
        self.plotter_widget = None
        self.plotter = None
        self.status_widgets = {}
        
        # Performance tracking
        self.last_frame_time = time.time()
        
        self._setup_ui()
        self._initialize_systems()
        self._setup_connections()
        self._start_systems()
        
        print("🚀 Enhanced MIDI Morphing Visualizer - Step 2: Particle Physics!")
    
    def _setup_ui(self):
        """Setup enhanced user interface."""
        self.setWindowTitle("Enhanced MIDI Morphing Visualizer - Step 2: Particle Physics")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget with 3D visualization
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # 3D Visualization - Fixed QtInteractor usage
        self.plotter_widget = QtInteractor(central_widget)
        self.plotter = self.plotter_widget
        self.plotter.background_color = 'black'
        
        main_layout.addWidget(self.plotter_widget, stretch=1)
        
        # Control panel - ENHANCED FOR STEP 2
        control_panel = self._create_enhanced_control_panel()
        main_layout.addWidget(control_panel)
        
        # Status bar
        self._setup_status_bar()
        
        # Menu bar
        self._setup_menu_bar()
        
        print("✅ Enhanced UI setup complete with particle controls")
    
    def _create_enhanced_control_panel(self):
        """Create enhanced control panel with particle controls."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # Global morph control
        morph_group = QGroupBox("Global Morphing")
        morph_layout = QVBoxLayout(morph_group)
        
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        self.morph_slider.valueChanged.connect(self._on_morph_changed)
        
        self.morph_label = QLabel("Morph: 0%")
        
        morph_layout.addWidget(self.morph_label)
        morph_layout.addWidget(self.morph_slider)
        
        layout.addWidget(morph_group)
        
        # Audio backend selection
        audio_group = QGroupBox("Audio Backend")
        audio_layout = QVBoxLayout(audio_group)
        
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["SoundDevice", "PyAudio", "Auto"])
        self.backend_combo.currentTextChanged.connect(self._on_backend_changed)
        
        audio_layout.addWidget(self.backend_combo)
        
        layout.addWidget(audio_group)
        
        # ENHANCED PARTICLE CONTROLS FOR STEP 2
        particle_group = QGroupBox("Particle Physics System")
        particle_layout = QVBoxLayout(particle_group)
        
        self.particles_enabled = QCheckBox("Enable Particles")
        self.particles_enabled.setChecked(True)
        self.particles_enabled.toggled.connect(self._on_particles_toggled)
        
        self.particle_count_label = QLabel("Particles: 0")
        
        # Particle type selector
        particle_type_layout = QHBoxLayout()
        particle_type_layout.addWidget(QLabel("Type:"))
        self.particle_type_combo = QComboBox()
        self.particle_type_combo.addItems([
            "Auto", "Spark", "Burst", "Trail", "Bloom", 
            "Explosion", "Fountain", "Spiral"
        ])
        particle_type_layout.addWidget(self.particle_type_combo)
        
        # Performance mode toggle
        self.performance_mode = QCheckBox("Performance Mode")
        self.performance_mode.toggled.connect(self._on_performance_mode_toggled)
        
        # Gravity control
        gravity_layout = QHBoxLayout()
        gravity_layout.addWidget(QLabel("Gravity:"))
        self.gravity_slider = QSlider(Qt.Horizontal)
        self.gravity_slider.setRange(-20, 5)
        self.gravity_slider.setValue(-10)  # Default -9.81
        self.gravity_slider.valueChanged.connect(self._on_gravity_changed)
        self.gravity_label = QLabel("-9.8")
        gravity_layout.addWidget(self.gravity_slider)
        gravity_layout.addWidget(self.gravity_label)
        
        particle_layout.addWidget(self.particles_enabled)
        particle_layout.addWidget(self.particle_count_label)
        particle_layout.addLayout(particle_type_layout)
        particle_layout.addWidget(self.performance_mode)
        particle_layout.addLayout(gravity_layout)
        
        layout.addWidget(particle_group)
        
        # Performance controls
        perf_group = QGroupBox("Performance")
        perf_layout = QVBoxLayout(perf_group)
        
        self.performance_enabled = QCheckBox("Monitor Performance")
        self.performance_enabled.setChecked(True)
        self.performance_enabled.toggled.connect(self._on_performance_toggled)
        
        self.fps_label = QLabel("FPS: --")
        self.memory_label = QLabel("Memory: -- MB")
        
        perf_layout.addWidget(self.performance_enabled)
        perf_layout.addWidget(self.fps_label)
        perf_layout.addWidget(self.memory_label)
        
        layout.addWidget(perf_group)
        
        # ENHANCED TEST CONTROLS FOR STEP 2
        test_group = QGroupBox("Test Controls")
        test_layout = QVBoxLayout(test_group)
        
        self.test_note_btn = QPushButton("Test MIDI Note")
        self.test_note_btn.clicked.connect(self._test_midi_note)
        
        self.test_particle_btn = QPushButton("Test Particles")
        self.test_particle_btn.clicked.connect(self._test_particles)
        
        self.test_explosion_btn = QPushButton("Test Explosion")
        self.test_explosion_btn.clicked.connect(self._test_explosion)
        
        self.test_fountain_btn = QPushButton("Test Fountain")
        self.test_fountain_btn.clicked.connect(self._test_fountain)
        
        self.clear_particles_btn = QPushButton("Clear All Particles")
        self.clear_particles_btn.clicked.connect(self._clear_particles)
        
        test_layout.addWidget(self.test_note_btn)
        test_layout.addWidget(self.test_particle_btn)
        test_layout.addWidget(self.test_explosion_btn)
        test_layout.addWidget(self.test_fountain_btn)
        test_layout.addWidget(self.clear_particles_btn)
        
        return panel
    
    def _setup_status_bar(self):
        """Setup comprehensive status bar."""
        status_bar = self.statusBar()
        
        # MIDI status
        self.status_widgets['midi'] = QLabel("MIDI: Disconnected")
        status_bar.addWidget(self.status_widgets['midi'])
        
        # Audio status
        self.status_widgets['audio'] = QLabel("Audio: Stopped")
        status_bar.addWidget(self.status_widgets['audio'])
        
        # Scene status
        self.status_widgets['scene'] = QLabel("Scene: Ready")
        status_bar.addWidget(self.status_widgets['scene'])
        
        # Particle status - NEW FOR STEP 2
        self.status_widgets['particles'] = QLabel("Particles: 0/0")
        status_bar.addWidget(self.status_widgets['particles'])
        
        # Performance status
        self.status_widgets['performance'] = QLabel("Performance: OK")
        status_bar.addPermanentWidget(self.status_widgets['performance'])
    
    def _setup_menu_bar(self):
        """Setup comprehensive menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Audio menu
        audio_menu = menubar.addMenu('Audio')
        restart_audio_action = QAction('Restart Audio Analysis', self)
        restart_audio_action.triggered.connect(self._restart_audio)
        audio_menu.addAction(restart_audio_action)
        
        # Particle menu - NEW FOR STEP 2
        particle_menu = menubar.addMenu('Particles')
        
        clear_particles_action = QAction('Clear All Particles', self)
        clear_particles_action.triggered.connect(self._clear_particles)
        particle_menu.addAction(clear_particles_action)
        
        performance_mode_action = QAction('Toggle Performance Mode', self)
        performance_mode_action.triggered.connect(self._toggle_performance_mode)
        particle_menu.addAction(performance_mode_action)
        
        # Scene menu
        scene_menu = menubar.addMenu('Scene')
        reset_scene_action = QAction('Reset Scene', self)
        reset_scene_action.triggered.connect(self._reset_scene)
        scene_menu.addAction(reset_scene_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _initialize_systems(self):
        """Initialize all enhanced systems."""
        print("🔧 Initializing enhanced systems with particle physics...")
        
        # Initialize audio analyzer (from Step 1)
        self.audio_analyzer = AdvancedAudioAnalyzer(self.config)
        
        # Initialize scene manager (simple for now, enhanced in Step 3)
        self.scene_manager = SimpleSceneManager(self.plotter, self.config)
        
        # Initialize ADVANCED PARTICLE SYSTEM - STEP 2 CORE FEATURE
        self.particle_system = AdvancedParticleSystem(self.plotter, self.config)
        
        # Initialize performance monitor
        self.performance_monitor = SimplePerformanceMonitor()
        
        # Initialize MIDI if available
        if MIDI_AVAILABLE:
            self._initialize_midi()
        
        print("✅ All enhanced systems initialized with particle physics")
    
    def _initialize_midi(self):
        """Initialize MIDI system."""
        try:
            pygame.midi.init()
            device_count = pygame.midi.get_count()
            
            if device_count > 0:
                # Find first input device
                for i in range(device_count):
                    info = pygame.midi.get_device_info(i)
                    if info[2]:  # is_input
                        self.midi_input = pygame.midi.Input(i)
                        print(f"🎹 MIDI device connected: {info[1].decode()}")
                        self.status_widgets['midi'].setText(f"MIDI: {info[1].decode()}")
                        break
            else:
                print("🎹 No MIDI devices found")
                self.status_widgets['midi'].setText("MIDI: No devices")
                
        except Exception as e:
            print(f"🎹 MIDI initialization failed: {e}")
            self.status_widgets['midi'].setText("MIDI: Error")
    
    def _setup_connections(self):
        """Setup signal connections between systems."""
        print("🔗 Setting up system connections with particle integration...")
        
        # Audio analyzer connections - ENHANCED FOR STEP 2
        if self.audio_analyzer:
            self.audio_analyzer.amplitude_signal.connect(self._on_amplitude_changed)
            self.audio_analyzer.spectral_centroid_signal.connect(self._on_spectral_centroid)
            self.audio_analyzer.spectral_rolloff_signal.connect(self._on_spectral_rolloff)
            self.audio_analyzer.spectral_bandwidth_signal.connect(self._on_spectral_bandwidth)
            self.audio_analyzer.spectral_flux_signal.connect(self._on_spectral_flux)
            self.audio_analyzer.zero_crossing_rate_signal.connect(self._on_zero_crossing_rate)
            self.audio_analyzer.onset_detected_signal.connect(self._on_onset_detected)
            self.audio_analyzer.beat_detected_signal.connect(self._on_beat_detected)
            self.audio_analyzer.tempo_signal.connect(self._on_tempo_changed)
            self.audio_analyzer.mfcc_signal.connect(self._on_mfcc_features)
            self.audio_analyzer.mel_spectrogram_signal.connect(self._on_mel_spectrogram)
            self.audio_analyzer.chroma_signal.connect(self._on_chroma_features)
        
        # Performance monitor connections
        if self.performance_monitor:
            self.performance_monitor.performance_update_signal.connect(self._on_performance_update)
        
        # Setup update timer for main loop
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._main_update_loop)
        self.update_timer.setInterval(16)  # ~60 FPS
        
        # Setup MIDI polling timer
        if self.midi_input:
            self.midi_timer = QTimer()
            self.midi_timer.timeout.connect(self._poll_midi)
            self.midi_timer.setInterval(5)  # 5ms for responsive MIDI
        
        print("✅ System connections established with particle integration")
    
    def _start_systems(self):
        """Start all systems."""
        print("🚀 Starting enhanced systems with particle physics...")
        
        # Start audio analysis
        if self.audio_analyzer:
            if self.audio_analyzer.start():
                self.status_widgets['audio'].setText("Audio: Advanced Analysis + Particles")
                print("✅ Advanced audio analysis started with particle integration")
            else:
                self.status_widgets['audio'].setText("Audio: Failed to start")
                print("❌ Advanced audio analysis failed to start")
        
        # Start performance monitoring
        if self.performance_monitor:
            self.performance_monitor.start_monitoring()
        
        # Start main update loop
        self.update_timer.start()
        
        # Start MIDI polling
        if self.midi_input:
            self.midi_timer.start()
        
        print("🎉 All systems started successfully with particle physics!")
    
    def _main_update_loop(self):
        """Main update loop with particle system integration."""
        try:
            current_time = time.time()
            delta_time = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Update scene physics
            if self.scene_manager:
                self.scene_manager.update_physics(delta_time)
            
            # UPDATE PARTICLE SYSTEM - STEP 2 CORE FEATURE
            if self.particle_system:
                self.particle_system.update(delta_time)
                
                # Update particle count display
                particle_count = len(self.particle_system.active_particles)
                emitter_count = len(self.particle_system.active_emitters)
                self.particle_count_label.setText(f"Particles: {particle_count}")
                self.status_widgets['particles'].setText(f"Particles: {particle_count}/{emitter_count}")
            
            # Update scene status
            if self.scene_manager:
                summary = self.scene_manager.get_scene_summary()
                self.status_widgets['scene'].setText(f"Scene: {summary['total_objects']} objects")
            
            # Record frame for performance monitoring
            if self.performance_monitor:
                self.performance_monitor.record_frame()
            
        except Exception as e:
            print(f"Main update loop error: {e}")
    
    def _poll_midi(self):
        """Poll MIDI input for events."""
        if not self.midi_input:
            return
        
        try:
            if self.midi_input.poll():
                events = self.midi_input.read(10)
                
                for event_data in events:
                    event = event_data[0]
                    status = event[0]
                    
                    # Note On (144-159)
                    if 144 <= status <= 159:
                        channel = status - 144
                        note = event[1]
                        velocity = event[2] / 127.0
                        
                        if velocity > 0:
                            self._handle_midi_note_on(note, velocity, channel)
                        else:
                            self._handle_midi_note_off(note, channel)
                    
                    # Note Off (128-143)
                    elif 128 <= status <= 143:
                        channel = status - 128
                        note = event[1]
                        self._handle_midi_note_off(note, channel)
                    
                    # Control Change (176-191)
                    elif 176 <= status <= 191:
                        channel = status - 176
                        controller = event[1]
                        value = event[2] / 127.0
                        self._handle_midi_control_change(controller, value, channel)
                        
        except Exception as e:
            print(f"MIDI polling error: {e}")
    
    def _handle_midi_note_on(self, note: int, velocity: float, channel: int = 0):
        """Handle MIDI note on with PARTICLE INTEGRATION."""
        try:
            print(f"🎵 MIDI Note ON: {note} vel:{velocity:.2f} ch:{channel}")
            
            # Scene manager handles visual objects
            if self.scene_manager:
                self.scene_manager.handle_midi_note(note, velocity, True, channel)
            
            # PARTICLE SYSTEM CREATES PARTICLES - STEP 2 CORE FEATURE
            if self.particle_system and self.particles_enabled.isChecked():
                # Get selected particle type
                particle_type_name = self.particle_type_combo.currentText()
                if particle_type_name == "Auto":
                    particle_type = None  # Let system choose
                else:
                    particle_type = ParticleType(particle_type_name.lower())
                
                self.particle_system.emit_note_particles(note, velocity, None, particle_type)
            
        except Exception as e:
            print(f"Error handling MIDI note on: {e}")
    
    def _handle_midi_note_off(self, note: int, channel: int = 0):
        """Handle MIDI note off."""
        try:
            print(f"🎵 MIDI Note OFF: {note} ch:{channel}")
            
            # Scene manager handles note off
            if self.scene_manager:
                self.scene_manager.handle_midi_note(note, 0.0, False, channel)
                
        except Exception as e:
            print(f"Error handling MIDI note off: {e}")
    
    def _handle_midi_control_change(self, controller: int, value: float, channel: int = 0):
        """Handle MIDI control change messages."""
        try:
            print(f"🎛️ MIDI CC: {controller} val:{value:.2f} ch:{channel}")
            
            # Modulation wheel (CC1) controls global morph
            if controller == 1:
                morph_value = int(value * 100)
                self.morph_slider.setValue(morph_value)
            
            # CC74 controls particle gravity
            elif controller == 74:
                gravity_value = -20 + value * 25  # Range -20 to 5
                self.gravity_slider.setValue(int(gravity_value))
                
        except Exception as e:
            print(f"Error handling MIDI control change: {e}")
    
    # Audio feature signal handlers - ENHANCED WITH PARTICLE INTEGRATION
    def _on_amplitude_changed(self, amplitude: float):
        """Handle amplitude changes with particle integration."""
        # Use amplitude to control global brightness
        if hasattr(self.scene_manager, 'test_actor'):
            current_opacity = amplitude * 2.0  # Scale amplitude
            current_opacity = max(0.2, min(1.0, current_opacity))  # Clamp
            self.scene_manager.test_actor.GetProperty().SetOpacity(current_opacity)
        
        # PARTICLE INTEGRATION - Feed amplitude to particle system
        if self.particle_system:
            self.particle_system.emit_audio_responsive_particles(amplitude)
        
        print(f"🔊 Amplitude: {amplitude:.3f}")
    
    def _on_spectral_centroid(self, centroid: float):
        """Handle spectral centroid changes."""
        # Use centroid for color temperature
        normalized_centroid = (centroid - self.config.FREQ_MIN) / (self.config.FREQ_MAX - self.config.FREQ_MIN)
        normalized_centroid = max(0.0, min(1.0, normalized_centroid))
        
        # Map to color temperature (blue = low, red = high)
        if hasattr(self.scene_manager, 'test_actor'):
            color = [1.0, 1.0 - normalized_centroid, 1.0 - normalized_centroid]
            self.scene_manager.test_actor.GetProperty().SetColor(color)
        print(f"🎼 Spectral Centroid: {centroid:.1f} Hz")
    
    def _on_spectral_rolloff(self, rolloff: float):
        """Handle spectral rolloff changes."""
        print(f"📊 Spectral Rolloff: {rolloff:.1f} Hz")
    
    def _on_spectral_bandwidth(self, bandwidth: float):
        """Handle spectral bandwidth changes."""
        print(f"📏 Spectral Bandwidth: {bandwidth:.1f} Hz")
    
    def _on_spectral_flux(self, flux: float):
        """Handle spectral flux changes."""
        print(f"🌊 Spectral Flux: {flux:.3f}")
    
    def _on_zero_crossing_rate(self, zcr: float):
        """Handle zero-crossing rate changes."""
        print(f"⚡ Zero Crossing Rate: {zcr:.3f}")
    
    def _on_onset_detected(self, timestamp: float):
        """Handle onset detection with PARTICLE INTEGRATION."""
        print(f"🎯 Audio onset detected at {timestamp}")
        
        # Create visual flash effect
        if hasattr(self.scene_manager, 'test_actor'):
            self.scene_manager.test_actor.GetProperty().SetColor([1.0, 1.0, 1.0])
            QTimer.singleShot(100, lambda: self._reset_sphere_color())
        
        # PARTICLE INTEGRATION - Trigger onset particles
        if self.particle_system and self.particles_enabled.isChecked():
            self.particle_system.emit_audio_responsive_particles(0.8, onset_detected=True)
    
    def _reset_sphere_color(self):
        """Reset sphere to default color."""
        if hasattr(self.scene_manager, 'test_actor'):
            self.scene_manager.test_actor.GetProperty().SetColor([0.5, 0.8, 1.0])
    
    def _on_beat_detected(self, timestamp: float, strength: float):
        """Handle beat detection with PARTICLE INTEGRATION."""
        print(f"🥁 Beat detected: {timestamp} strength:{strength:.2f}")
        
        # PARTICLE INTEGRATION - Create beat-synchronized particles
        if self.particle_system and self.particles_enabled.isChecked():
            self.particle_system.emit_beat_particles(strength)
    
    def _on_tempo_changed(self, tempo: float):
        """Handle tempo changes."""
        print(f"🎼 Tempo: {tempo:.1f} BPM")
    
    def _on_mfcc_features(self, mfcc: np.ndarray):
        """Handle MFCC features."""
        if len(mfcc) > 0:
            print(f"🎚️ MFCC[0]: {mfcc[0]:.3f}")
    
    def _on_mel_spectrogram(self, mel_spec: np.ndarray):
        """Handle mel-spectrogram features."""
        if len(mel_spec) > 0:
            max_mel = np.max(mel_spec)
            print(f"🌈 Mel-spec peak: {max_mel:.3f}")
    
    def _on_chroma_features(self, chroma: np.ndarray):
        """Handle chroma features."""
        if len(chroma) > 0:
            dominant_chroma = np.argmax(chroma)
            print(f"🎵 Dominant chroma: {dominant_chroma} ({chroma[dominant_chroma]:.3f})")
    
    def _on_performance_update(self, performance_data: dict):
        """Handle performance monitoring updates."""
        try:
            fps = performance_data.get('fps', 0)
            memory = performance_data.get('memory_mb', 0)
            
            # Update labels
            self.fps_label.setText(f"FPS: {fps:.1f}")
            self.memory_label.setText(f"Memory: {memory:.1f} MB")
            
            # Update status bar based on performance
            if fps < 30:
                self.status_widgets['performance'].setText("Performance: LOW FPS")
                self.status_widgets['performance'].setStyleSheet("color: red;")
            elif memory > 1000:
                self.status_widgets['performance'].setText("Performance: HIGH MEMORY")
                self.status_widgets['performance'].setStyleSheet("color: orange;")
            else:
                self.status_widgets['performance'].setText("Performance: OK")
                self.status_widgets['performance'].setStyleSheet("color: green;")
                
        except Exception as e:
            print(f"Performance update error: {e}")
    
    # UI Event Handlers - ENHANCED FOR STEP 2
    def _on_morph_changed(self, value: int):
        """Handle morph slider changes."""
        morph_blend = value / 100.0
        self.morph_label.setText(f"Morph: {value}%")
        
        if self.scene_manager:
            self.scene_manager.set_global_morph_blend(morph_blend)
    
    def _on_backend_changed(self, backend_name: str):
        """Handle audio backend changes."""
        backend_map = {
            "SoundDevice": "sounddevice",
            "PyAudio": "pyaudio",
            "Auto": "sounddevice"
        }
        
        if backend_name in backend_map:
            self.config.PREFERRED_AUDIO_BACKEND = backend_map[backend_name]
            print(f"🎵 Audio backend changed to: {backend_name}")
            self._restart_audio()
    
    def _on_particles_toggled(self, enabled: bool):
        """Handle particle system toggle."""
        if self.particle_system:
            self.particle_system.render_particles = enabled
            print(f"🎆 Particles {'enabled' if enabled else 'disabled'}")
    
    def _on_performance_mode_toggled(self, enabled: bool):
        """Handle particle performance mode toggle."""
        if self.particle_system:
            self.particle_system.set_performance_mode(enabled)
    
    def _on_gravity_changed(self, value: int):
        """Handle gravity slider changes."""
        gravity_value = value / 1.0  # Convert to float
        self.gravity_label.setText(f"{gravity_value:.1f}")
        
        if self.particle_system:
            self.particle_system.gravity[1] = gravity_value
            print(f"🌍 Gravity changed to: {gravity_value:.1f}")
    
    def _on_performance_toggled(self, enabled: bool):
        """Handle performance monitoring toggle."""
        if self.performance_monitor:
            if enabled:
                self.performance_monitor.start_monitoring()
            else:
                self.performance_monitor.stop_monitoring()
    
    # Test Functions - ENHANCED FOR STEP 2
    def _test_midi_note(self):
        """Test MIDI note functionality with particles."""
        import random
        note = random.randint(60, 72)
        velocity = random.uniform(0.3, 1.0)
        self._handle_midi_note_on(note, velocity, 0)
        
        # Schedule note off after 1 second
        QTimer.singleShot(1000, lambda: self._handle_midi_note_off(note, 0))
    
    def _test_particles(self):
        """Test basic particle functionality."""
        if self.particle_system:
            import random
            for _ in range(3):
                note = random.randint(60, 72)
                velocity = random.uniform(0.5, 1.0)
                self.particle_system.emit_note_particles(note, velocity)
    
    def _test_explosion(self):
        """Test explosion particle effect."""
        if self.particle_system:
            center_pos = np.array([0.0, 2.0, 0.0])
            self.particle_system.emit_note_particles(
                60, 1.0, center_pos, ParticleType.EXPLOSION
            )
            print("💥 Explosion test triggered!")
    
    def _test_fountain(self):
        """Test fountain particle effect."""
        if self.particle_system:
            fountain_pos = np.array([2.0, -1.0, 2.0])
            self.particle_system.emit_note_particles(
                72, 0.8, fountain_pos, ParticleType.FOUNTAIN
            )
            print("⛲ Fountain test triggered!")
    
    def _clear_particles(self):
        """Clear all particles."""
        if self.particle_system:
            self.particle_system.clear_all_particles()
            print("🧹 All particles cleared")
    
    # Menu Actions - ENHANCED FOR STEP 2
    def _restart_audio(self):
        """Restart audio analysis system."""
        try:
            if self.audio_analyzer:
                print("🔄 Restarting advanced audio analysis...")
                self.audio_analyzer.stop()
                
                self.audio_analyzer = AdvancedAudioAnalyzer(self.config)
                
                # Reconnect signals
                self.audio_analyzer.amplitude_signal.connect(self._on_amplitude_changed)
                self.audio_analyzer.spectral_centroid_signal.connect(self._on_spectral_centroid)
                self.audio_analyzer.spectral_rolloff_signal.connect(self._on_spectral_rolloff)
                self.audio_analyzer.spectral_bandwidth_signal.connect(self._on_spectral_bandwidth)
                self.audio_analyzer.spectral_flux_signal.connect(self._on_spectral_flux)
                self.audio_analyzer.zero_crossing_rate_signal.connect(self._on_zero_crossing_rate)
                self.audio_analyzer.onset_detected_signal.connect(self._on_onset_detected)
                self.audio_analyzer.beat_detected_signal.connect(self._on_beat_detected)
                self.audio_analyzer.tempo_signal.connect(self._on_tempo_changed)
                self.audio_analyzer.mfcc_signal.connect(self._on_mfcc_features)
                self.audio_analyzer.mel_spectrogram_signal.connect(self._on_mel_spectrogram)
                self.audio_analyzer.chroma_signal.connect(self._on_chroma_features)
                
                if self.audio_analyzer.start():
                    self.status_widgets['audio'].setText("Audio: Advanced Analysis + Particles")
                    print("✅ Advanced audio analysis restarted")
                else:
                    self.status_widgets['audio'].setText("Audio: Restart Failed")
                    print("❌ Advanced audio restart failed")
                    
        except Exception as e:
            print(f"Audio restart error: {e}")
    
    def _reset_scene(self):
        """Reset the entire scene."""
        print("🎭 Resetting scene...")
        if hasattr(self.scene_manager, 'test_actor'):
            self.scene_manager.test_actor.GetProperty().SetColor([0.5, 0.8, 1.0])
            self.scene_manager.test_actor.GetProperty().SetOpacity(0.8)
        
        # Also clear particles
        self._clear_particles()
    
    def _toggle_performance_mode(self):
        """Toggle particle performance mode."""
        current_state = self.performance_mode.isChecked()
        self.performance_mode.setChecked(not current_state)
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Enhanced MIDI Morphing Visualizer</h2>
        <p><b>Version:</b> 2.0 - Step 2: Advanced Particle Physics</p>
        
        <h3>🎆 Step 2 Completed - Particle Physics Features:</h3>
        <ul>
        <li>✅ Full physics simulation (gravity, drag, forces)</li>
        <li>✅ Multiple particle types (spark, burst, trail, bloom, explosion, fountain, spiral)</li>
        <li>✅ MIDI-triggered particle emission with note-to-color mapping</li>
        <li>✅ Audio-responsive particle effects (onset & beat detection)</li>
        <li>✅ Performance-optimized rendering with performance mode</li>
        <li>✅ Real-time particle count and emitter management</li>
        <li>✅ Gravity control and particle type selection</li>
        <li>✅ Advanced particle behaviors per type</li>
        </ul>
        
        <h3>🎵 Maintained from Step 1:</h3>
        <ul>
        <li>✅ Multiple audio backends (SoundDevice + PyAudio)</li>
        <li>✅ Real-time spectral analysis with visual feedback</li>
        <li>✅ Advanced onset detection and beat tracking</li>
        <li>✅ MFCC, mel-spectrogram, and chroma analysis</li>
        </ul>
        
        <h3>🎮 Try These Particle Features:</h3>
        <ul>
        <li>🎹 Play MIDI notes (watch particles spawn with colors)</li>
        <li>🎤 Make sounds near microphone (onset particles)</li>
        <li>🥁 Play rhythmic music (beat-synchronized particles)</li>
        <li>💥 Test explosion and fountain effects</li>
        <li>🎛️ Adjust gravity and particle types</li>
        <li>⚡ Toggle performance mode for optimization</li>
        </ul>
        
        <p><b>Next:</b> Step 3 will add enhanced scene management with multiple objects and morphing!</p>
        """
        
        QMessageBox.about(self, "About - Step 2 Complete", about_text)
    
    def closeEvent(self, event):
        """Handle application shutdown."""
        print("🛑 Shutting down enhanced systems with particle physics...")
        
        # Stop all systems
        if self.audio_analyzer:
            self.audio_analyzer.stop()
        
        if self.performance_monitor:
            self.performance_monitor.stop_monitoring()
        
        if hasattr(self, 'update_timer'):
            self.update_timer.stop()
        
        if hasattr(self, 'midi_timer'):
            self.midi_timer.stop()
        
        if self.midi_input:
            self.midi_input.close()
            pygame.midi.quit()
        
        # Clear particles
        if self.particle_system:
            self.particle_system.clear_all_particles()
        
        print("👋 Enhanced MIDI Morphing Visualizer shutdown complete")
        event.accept()

# =============================================================================
# Application Entry Point
# =============================================================================

def main():
    """Main application entry point."""
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced MIDI Morphing Visualizer - Step 2")
        app.setApplicationVersion("2.0")
        
        # Create and show main window
        window = EnhancedMainWindow()
        window.show()
        
        print("\n" + "="*80)
        print("🎉 ENHANCED MIDI MORPHING VISUALIZER - STEP 2: PARTICLE PHYSICS")
        print("="*80)
        print("\n🎆 STEP 2 COMPLETED - ADVANCED PARTICLE PHYSICS SYSTEM:")
        print("✅ Full physics simulation (gravity, drag, forces)")
        print("✅ Multiple particle types (spark, burst, trail, bloom, explosion, fountain, spiral)")
        print("✅ MIDI-triggered particle emission with note-to-color mapping")
        print("✅ Audio-responsive particle effects (onset & beat detection)")
        print("✅ Performance-optimized rendering with performance mode")
        print("✅ Real-time particle count and emitter management")
        print("✅ Gravity control and particle type selection")
        print("✅ Advanced particle behaviors per type")
        print("\n🎵 MAINTAINED FROM STEP 1:")
        print("✅ Multiple audio backends (SoundDevice + PyAudio)")
        print("✅ Real-time spectral analysis with visual feedback")
        print("✅ Advanced onset detection and beat tracking")
        print("✅ MFCC, mel-spectrogram, and chroma analysis")
        print("\n🎮 TRY THESE PARTICLE FEATURES:")
        print("   🎹 Play MIDI notes (watch particles spawn with colors)")
        print("   🎤 Make sounds near microphone (onset particles)")
        print("   🥁 Play rhythmic music (beat-synchronized particles)")
        print("   💥 Use 'Test Explosion' and 'Test Fountain' buttons")
        print("   🎛️ Adjust gravity slider and try different particle types")
        print("   ⚡ Toggle performance mode for optimization")
        print("   🧹 Use 'Clear All Particles' to reset")
        print("\n🚀 NEXT STEP: Enhanced scene management with multiple objects!")
        print("="*80)
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
