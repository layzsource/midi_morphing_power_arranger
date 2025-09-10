"""
main_window.py - Enhanced Main Window with Advanced Particle and Morphing Systems
This integrates Option 2: Full PySide6 Integration with advanced features
"""

import sys
import os
import logging
import time
import numpy as np
import colorsys
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Core imports from the original
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, 
    QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox,
    QMenuBar, QMenu, QHBoxLayout, QGroupBox, QGridLayout, QTabWidget,
    QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar, QDockWidget
)
from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QAction, QFont, QShortcut, QKeySequence
from pyvistaqt import QtInteractor
import pyvista as pv

# Import the fixed main window base
try:
    from main_fixed_window import PerformanceAwareMainWindow
except ImportError:
    # If main_fixed_window is not available, we'll create our own base
    print("Note: main_fixed_window not found, using standalone implementation")
    PerformanceAwareMainWindow = QMainWindow

# Import configuration and other modules
try:
    from config import Config
    from profiler import PerformanceProfiler
except ImportError:
    print("Note: Some modules not found, using basic implementations")
    Config = None
    PerformanceProfiler = None

# Check for optional dependencies
try:
    import pygame.midi
    MIDI_AVAILABLE = True
except ImportError:
    MIDI_AVAILABLE = False
    print("⚠ MIDI support not available")

# =============================================================================
# Advanced Particle System
# =============================================================================

class ParticleType(Enum):
    BURST = "burst"
    SPARK = "spark"
    GALAXY = "galaxy"
    FLUID = "fluid"
    BLOOM = "bloom"
    CRYSTAL = "crystal"

@dataclass
class Particle:
    position: np.ndarray
    velocity: np.ndarray
    color: Tuple[float, float, float]
    size: float
    lifetime: float
    max_lifetime: float
    particle_type: ParticleType
    gravity_factor: float = 1.0

class AdvancedParticleSystem:
    """Advanced particle system with multiple effects and physics."""
    
    def __init__(self, plotter, max_particles=5000):
        self.plotter = plotter
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.mesh = None
        self.physics_enabled = True
        self.morph_amount = 0.5
        self.particle_intensity = 1.0
        self.color_shift = 0.0
        self.enabled = True
        
    def emit_note_particles(self, note: int, velocity: float, position: Optional[np.ndarray] = None):
        """Emit particles based on MIDI note with advanced patterns."""
        if not self.enabled:
            return
            
        if position is None:
            # Create position based on note
            angle = (note % 12) * np.pi / 6  # 12 notes in a circle
            radius = 2 + (note // 12)  # Octave determines radius
            position = np.array([
                np.cos(angle) * radius,
                0,
                np.sin(angle) * radius
            ])
        
        # Determine particle type and count based on velocity
        if velocity > 0.8:
            p_type = ParticleType.BURST
            count = int(velocity * 60 * self.particle_intensity)
        elif velocity > 0.6:
            p_type = ParticleType.SPARK
            count = int(velocity * 40 * self.particle_intensity)
        elif velocity > 0.4:
            p_type = ParticleType.GALAXY
            count = int(velocity * 30 * self.particle_intensity)
        else:
            p_type = ParticleType.BLOOM
            count = int(velocity * 20 * self.particle_intensity)
        
        # Calculate color from note with color shift
        hue = ((note % 12) / 12.0 + self.color_shift) % 1.0
        rgb = colorsys.hsv_to_rgb(hue, 0.8 + velocity * 0.2, 0.5 + velocity * 0.5)
        
        for i in range(count):
            particle = self._create_particle(p_type, position, velocity, rgb)
            self.particles.append(particle)
        
        # Limit particles
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]
    
    def _create_particle(self, p_type: ParticleType, position: np.ndarray, 
                        velocity: float, color: Tuple[float, float, float]) -> Particle:
        """Create a particle with specific type characteristics."""
        
        if p_type == ParticleType.BURST:
            # Explosive radial pattern
            angle_h = np.random.uniform(0, 2 * np.pi)
            angle_v = np.random.uniform(-np.pi/4, np.pi/4)
            speed = np.random.uniform(3, 6) * velocity
            vel = np.array([
                np.cos(angle_h) * np.cos(angle_v) * speed,
                np.sin(angle_v) * speed + 2,
                np.sin(angle_h) * np.cos(angle_v) * speed
            ])
            size = np.random.uniform(0.1, 0.3) * velocity
            lifetime = np.random.uniform(1, 2)
            gravity = 0.5
            
        elif p_type == ParticleType.SPARK:
            # Quick sparks with trails
            vel = np.random.randn(3) * 3 * velocity
            vel[1] += 3  # Upward bias
            size = np.random.uniform(0.05, 0.15) * velocity
            lifetime = np.random.uniform(0.5, 1.5)
            gravity = 0.3
            
        elif p_type == ParticleType.GALAXY:
            # Spiral galaxy pattern
            angle = np.random.uniform(0, 2 * np.pi)
            radius = np.random.uniform(1, 4)
            spiral = angle + radius * 0.5
            vel = np.array([
                np.cos(spiral) * radius * 0.5,
                np.random.uniform(-0.5, 0.5),
                np.sin(spiral) * radius * 0.5
            ])
            size = np.random.uniform(0.05, 0.2)
            lifetime = np.random.uniform(2, 4)
            gravity = 0.1
            
        elif p_type == ParticleType.BLOOM:
            # Slow blooming effect
            angle = np.random.uniform(0, 2 * np.pi)
            vel = np.array([
                np.cos(angle) * 0.5,
                np.random.uniform(0, 1),
                np.sin(angle) * 0.5
            ])
            size = np.random.uniform(0.1, 0.4) * velocity
            lifetime = np.random.uniform(2, 3)
            gravity = 0.05
            
        else:  # CRYSTAL or FLUID
            vel = np.random.randn(3) * velocity
            size = np.random.uniform(0.1, 0.2) * velocity
            lifetime = np.random.uniform(1, 3)
            gravity = 0.2
        
        return Particle(
            position=position.copy() + np.random.randn(3) * 0.2,
            velocity=vel,
            color=color,
            size=size,
            lifetime=lifetime,
            max_lifetime=lifetime,
            particle_type=p_type,
            gravity_factor=gravity
        )
    
    def emit_special_effect(self, effect_name: str, position: np.ndarray, intensity: float = 1.0):
        """Emit special particle effects."""
        if effect_name == "explosion":
            # Create explosion effect
            for i in range(int(100 * intensity)):
                angle_h = np.random.uniform(0, 2 * np.pi)
                angle_v = np.random.uniform(-np.pi/2, np.pi/2)
                speed = np.random.uniform(2, 8)
                vel = np.array([
                    np.cos(angle_h) * np.cos(angle_v) * speed,
                    np.sin(angle_v) * speed,
                    np.sin(angle_h) * np.cos(angle_v) * speed
                ])
                
                hue = np.random.uniform(0, 0.15)  # Red-orange colors
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                
                particle = Particle(
                    position=position.copy() + np.random.randn(3) * 0.5,
                    velocity=vel,
                    color=rgb,
                    size=np.random.uniform(0.1, 0.4),
                    lifetime=np.random.uniform(0.5, 2),
                    max_lifetime=np.random.uniform(0.5, 2),
                    particle_type=ParticleType.BURST,
                    gravity_factor=0.3
                )
                self.particles.append(particle)
        
        elif effect_name == "fountain":
            # Create fountain effect
            for i in range(int(50 * intensity)):
                angle = np.random.uniform(0, 2 * np.pi)
                speed = np.random.uniform(3, 5)
                vel = np.array([
                    np.cos(angle) * speed * 0.3,
                    speed,
                    np.sin(angle) * speed * 0.3
                ])
                
                hue = 0.6  # Blue colors
                rgb = colorsys.hsv_to_rgb(hue, 0.8, 0.9)
                
                particle = Particle(
                    position=position.copy(),
                    velocity=vel,
                    color=rgb,
                    size=np.random.uniform(0.05, 0.15),
                    lifetime=np.random.uniform(1, 3),
                    max_lifetime=np.random.uniform(1, 3),
                    particle_type=ParticleType.FLUID,
                    gravity_factor=1.0
                )
                self.particles.append(particle)
    
    def update(self, dt: float):
        """Update particle physics and rendering."""
        if not self.particles:
            return
        
        # Update particles
        alive_particles = []
        for p in self.particles:
            p.lifetime -= dt
            
            if p.lifetime > 0:
                # Apply physics
                if self.physics_enabled:
                    # Gravity
                    p.velocity[1] -= 9.8 * dt * p.gravity_factor
                    
                    # Air resistance
                    p.velocity *= (1 - dt * 0.5)
                    
                    # Update position
                    p.position += p.velocity * dt
                    
                    # Morph effect - creates swirling patterns
                    if self.morph_amount > 0:
                        swirl = np.array([
                            np.sin(p.position[1] * 0.5) * self.morph_amount,
                            0,
                            np.cos(p.position[1] * 0.5) * self.morph_amount
                        ])
                        p.position += swirl * dt
                
                # Ground collision
                if p.position[1] < -5:
                    p.position[1] = -5
                    p.velocity[1] *= -0.5  # Bounce with damping
                    p.velocity[0] *= 0.7
                    p.velocity[2] *= 0.7
                
                alive_particles.append(p)
        
        self.particles = alive_particles
        self._update_mesh()
    
    def _update_mesh(self):
        """Update the particle mesh for rendering."""
        if not self.particles or not self.enabled:
            if self.mesh:
                self.plotter.remove_actor(self.mesh)
                self.mesh = None
            return
        
        # Create point cloud
        points = np.array([p.position for p in self.particles])
        colors = np.array([p.color for p in self.particles])
        sizes = np.array([p.size * (p.lifetime / p.max_lifetime) for p in self.particles])
        
        # Create polydata
        point_cloud = pv.PolyData(points)
        point_cloud["colors"] = colors
        point_cloud["sizes"] = sizes * 100  # Scale for visibility
        
        # Remove old mesh
        if self.mesh:
            self.plotter.remove_actor(self.mesh)
        
        # Add new mesh with improved rendering
        self.mesh = self.plotter.add_points(
            point_cloud,
            scalars="colors",
            rgb=True,
            point_size=10,
            render_points_as_spheres=True,
            opacity=0.9
        )
    
    def clear_all_particles(self):
        """Clear all particles."""
        self.particles.clear()
        if self.mesh:
            self.plotter.remove_actor(self.mesh)
            self.mesh = None
    
    def get_particle_count(self) -> int:
        """Get current particle count."""
        return len(self.particles)

# =============================================================================
# Advanced Morphing System
# =============================================================================

class MorphingMode(Enum):
    SPHERE_TO_CUBE = "sphere_cube"
    TORUS_WAVE = "torus_wave"
    DNA_HELIX = "dna_helix"
    CRYSTAL = "crystal"
    FLUID = "fluid"
    TERRAIN = "terrain"
    GALAXY = "galaxy"

class AdvancedMorphingSystem:
    """Advanced morphing system with multiple modes and smooth transitions."""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.mode = MorphingMode.SPHERE_TO_CUBE
        self.morph_value = 0.0
        self.target_morph = 0.0
        self.mesh = None
        self.wireframe = False
        self.original_points = None
        self.target_points = None
        self.current_points = None
        self.auto_morph = False
        self.morph_speed = 0.5
        
    def create_morph_geometry(self, mode: MorphingMode):
        """Create geometry for morphing based on mode."""
        self.mode = mode
        
        if mode == MorphingMode.SPHERE_TO_CUBE:
            # Create sphere and cube with matching point counts
            sphere = pv.Sphere(radius=3, theta_resolution=30, phi_resolution=30)
            cube = pv.Box(bounds=(-3, 3, -3, 3, -3, 3))
            # Resample cube to match sphere point count
            cube = cube.sample(sphere)
            self.original_points = np.array(sphere.points)
            self.target_points = np.array(cube.points[:len(self.original_points)])
            
        elif mode == MorphingMode.TORUS_WAVE:
            # Create torus with wave distortion
            torus = pv.ParametricTorus(ringradius=3, crosssectionradius=1)
            self.original_points = np.array(torus.points)
            # Create wave-distorted version
            self.target_points = self.original_points.copy()
            for i, point in enumerate(self.target_points):
                wave = np.sin(point[0] * 2) * np.cos(point[2] * 2) * 0.8
                self.target_points[i][1] += wave
                self.target_points[i][0] *= (1 + wave * 0.2)
                
        elif mode == MorphingMode.DNA_HELIX:
            # Create DNA double helix
            t = np.linspace(0, 6 * np.pi, 300)
            # First strand
            x1 = np.cos(t) * 2
            y1 = t / 2 - 3
            z1 = np.sin(t) * 2
            # Second strand
            x2 = np.cos(t + np.pi) * 2
            y2 = t / 2 - 3
            z2 = np.sin(t + np.pi) * 2
            
            points1 = np.column_stack([x1, y1, z1])
            points2 = np.column_stack([x2, y2, z2])
            self.original_points = np.vstack([points1, points2])
            
            # Create twisted version as target
            self.target_points = self.original_points.copy()
            for i, point in enumerate(self.target_points):
                twist = np.sin(point[1] * 0.5) * 0.5
                rotation = point[1] * 0.2
                x_rot = point[0] * np.cos(rotation) - point[2] * np.sin(rotation)
                z_rot = point[0] * np.sin(rotation) + point[2] * np.cos(rotation)
                self.target_points[i][0] = x_rot * (1 + twist)
                self.target_points[i][2] = z_rot * (1 + twist)
                
        elif mode == MorphingMode.CRYSTAL:
            # Create crystalline structures
            octahedron = pv.Octahedron(radius=3)
            icosahedron = pv.Icosahedron(radius=3)
            # Subdivide for more points
            octahedron = octahedron.subdivide(2)
            icosahedron = icosahedron.subdivide(2)
            self.original_points = np.array(octahedron.points)
            # Sample icosahedron to match point count
            icosahedron = icosahedron.sample(octahedron)
            self.target_points = np.array(icosahedron.points[:len(self.original_points)])
            
        elif mode == MorphingMode.FLUID:
            # Create fluid-like organic shapes
            sphere = pv.Sphere(radius=3, theta_resolution=50, phi_resolution=50)
            self.original_points = np.array(sphere.points)
            # Create organic distortion
            self.target_points = self.original_points.copy()
            for i, point in enumerate(self.target_points):
                # Multi-frequency noise for organic look
                noise1 = np.sin(point[0] * 2) * np.cos(point[1] * 2) * np.sin(point[2] * 2)
                noise2 = np.sin(point[0] * 4) * np.cos(point[1] * 4) * 0.3
                noise3 = np.sin(point[0] * 8) * np.cos(point[2] * 8) * 0.1
                total_noise = (noise1 + noise2 + noise3) * 0.5
                self.target_points[i] *= (1 + total_noise)
                
        elif mode == MorphingMode.TERRAIN:
            # Create terrain-like surface
            grid = pv.Plane(center=(0, 0, 0), direction=(0, 1, 0), 
                           i_size=10, j_size=10, i_resolution=50, j_resolution=50)
            self.original_points = np.array(grid.points)
            # Create mountainous terrain
            self.target_points = self.original_points.copy()
            for i, point in enumerate(self.target_points):
                # Fractal-like noise for terrain
                height = 0
                freq = 1
                amp = 2
                for octave in range(4):
                    height += np.sin(point[0] * freq) * np.cos(point[2] * freq) * amp
                    freq *= 2
                    amp *= 0.5
                self.target_points[i][1] = height
                
        elif mode == MorphingMode.GALAXY:
            # Create spiral galaxy
            num_arms = 3
            points_per_arm = 200
            all_points = []
            
            for arm in range(num_arms):
                arm_angle = (2 * np.pi / num_arms) * arm
                for i in range(points_per_arm):
                    # Logarithmic spiral
                    t = i / points_per_arm * 4 * np.pi
                    radius = np.exp(t * 0.15)
                    angle = t + arm_angle
                    
                    # Add some randomness for star distribution
                    radius += np.random.normal(0, radius * 0.1)
                    angle += np.random.normal(0, 0.1)
                    
                    x = radius * np.cos(angle)
                    z = radius * np.sin(angle)
                    y = np.random.normal(0, 0.2)
                    
                    all_points.append([x, y, z])
            
            self.original_points = np.array(all_points)
            # Create rotating version as target
            self.target_points = self.original_points.copy()
            rotation_angle = np.pi / 4
            for i, point in enumerate(self.target_points):
                x_rot = point[0] * np.cos(rotation_angle) - point[2] * np.sin(rotation_angle)
                z_rot = point[0] * np.sin(rotation_angle) + point[2] * np.cos(rotation_angle)
                self.target_points[i][0] = x_rot
                self.target_points[i][2] = z_rot
                self.target_points[i][1] = point[1] + np.sin(np.linalg.norm([x_rot, z_rot]) * 0.5) * 0.5
        
        # Initialize current points
        self.current_points = self.original_points.copy()
        self.update_morph(self.morph_value)
    
    def update_morph(self, value: float):
        """Update morph with smooth interpolation."""
        self.target_morph = np.clip(value, 0, 1)
    
    def animate_morph(self, dt: float):
        """Animate morphing with smooth transitions."""
        if self.auto_morph:
            # Auto-oscillate morphing
            self.target_morph = (np.sin(time.time() * self.morph_speed) + 1) / 2
        
        # Smooth interpolation towards target
        morph_diff = self.target_morph - self.morph_value
        self.morph_value += morph_diff * dt * 5  # Smooth factor
        
        if self.original_points is None or self.target_points is None:
            return
        
        # Interpolate between original and target with easing
        t = self._ease_in_out_cubic(self.morph_value)
        self.current_points = (1 - t) * self.original_points + t * self.target_points
        
        # Add dynamic wave effect
        wave_time = time.time() * 2
        for i in range(len(self.current_points)):
            wave = np.sin(wave_time + i * 0.01) * 0.05
            self.current_points[i][1] += wave
        
        self._update_mesh()
    
    def _ease_in_out_cubic(self, t: float) -> float:
        """Cubic easing function for smooth transitions."""
        if t < 0.5:
            return 4 * t * t * t
        else:
            return 1 - pow(-2 * t + 2, 3) / 2
    
    def _update_mesh(self):
        """Update the morphing mesh."""
        if self.current_points is None or len(self.current_points) < 4:
            return
        
        # Create point cloud
        point_cloud = pv.PolyData(self.current_points)
        
        # Create mesh from points
        try:
            if self.mode in [MorphingMode.DNA_HELIX, MorphingMode.GALAXY]:
                # For sparse points, use sphere glyphs
                mesh = point_cloud.glyph(geom=pv.Sphere(radius=0.1))
            else:
                # For dense points, create surface
                mesh = point_cloud.delaunay_3d().extract_surface()
        except:
            # Fallback to point cloud
            mesh = point_cloud
        
        # Calculate color based on morph value
        hue = self.morph_value * 0.3  # Color shifts from cyan to purple
        rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
        
        # Remove old mesh
        if self.mesh:
            self.plotter.remove_actor(self.mesh)
        
        # Add new mesh with enhanced rendering
        self.mesh = self.plotter.add_mesh(
            mesh,
            color=rgb,
            opacity=0.8,
            show_edges=self.wireframe,
            edge_color='white' if self.wireframe else None,
            smooth_shading=True,
            specular=0.5,
            specular_power=20
        )
    
    def morph_from_midi(self, note: int, velocity: float):
        """Apply morphing based on MIDI input."""
        # Map note to morph amount (2 octaves = full morph)
        morph_amount = (note % 24) / 24.0
        # Scale by velocity for dynamics
        morph_amount *= velocity
        # Add some momentum
        morph_amount = self.morph_value * 0.7 + morph_amount * 0.3
        self.update_morph(morph_amount)
    
    def toggle_wireframe(self):
        """Toggle wireframe rendering."""
        self.wireframe = not self.wireframe
        self._update_mesh()
    
    def toggle_auto_morph(self):
        """Toggle automatic morphing animation."""
        self.auto_morph = not self.auto_morph

# =============================================================================
# Enhanced Main Window
# =============================================================================

class EnhancedMainWindow(PerformanceAwareMainWindow):
    """Main window with integrated advanced particle and morphing systems."""
    
    def __init__(self):
        # Initialize the base class first
        super().__init__()
        
        # Add advanced features
        self.setup_advanced_features()
        
        # Start animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_frame)
        self.animation_timer.start(16)  # ~60 FPS
        
        self.last_frame_time = time.time()
        
        print("✨ Enhanced main window with advanced features initialized!")
    
    def setup_advanced_features(self):
        """Set up advanced particle and morphing systems."""
        try:
            # Initialize advanced particle system
            self.adv_particles = AdvancedParticleSystem(self.plotter_widget)
            
            # Initialize advanced morphing
            self.adv_morphing = AdvancedMorphingSystem(self.plotter_widget)
            self.adv_morphing.create_morph_geometry(MorphingMode.SPHERE_TO_CUBE)
            
            # Add UI controls
            self.add_advanced_controls()
            
            # Add keyboard shortcuts
            self.setup_keyboard_shortcuts()
            
            # Override MIDI handler if available
            if hasattr(self, 'midi_handler') and self.midi_handler:
                # Connect to enhanced MIDI processing
                self.midi_handler.note_on_signal.connect(self.handle_midi_note_advanced)
                self.midi_handler.note_off_signal.connect(self.handle_midi_off_advanced)
            
            print("✅ Advanced features initialized successfully!")
            
        except Exception as e:
            print(f"⚠ Could not initialize all advanced features: {e}")
            import traceback
            traceback.print_exc()
    
    def add_advanced_controls(self):
        """Add advanced feature controls to UI."""
        # Create a dock widget for advanced controls
        dock = QDockWidget("Advanced Features", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # === Morphing Controls ===
        morph_group = QGroupBox("Advanced Morphing")
        morph_layout = QVBoxLayout(morph_group)
        
        # Morphing mode selector
        morph_label = QLabel("Morphing Mode:")
        morph_layout.addWidget(morph_label)
        
        self.morph_combo = QComboBox()
        self.morph_combo.addItems([
            "Sphere to Cube",
            "Torus Wave",
            "DNA Helix",
            "Crystal",
            "Fluid",
            "Terrain",
            "Galaxy"
        ])
        self.morph_combo.currentIndexChanged.connect(self.on_morph_mode_changed)
        morph_layout.addWidget(self.morph_combo)
        
        # Morph amount slider
        morph_amount_label = QLabel("Morph Amount:")
        morph_layout.addWidget(morph_amount_label)
        
        self.adv_morph_slider = QSlider(Qt.Horizontal)
        self.adv_morph_slider.setRange(0, 100)
        self.adv_morph_slider.setValue(0)
        self.adv_morph_slider.valueChanged.connect(self.on_adv_morph_changed)
        morph_layout.addWidget(self.adv_morph_slider)
        
        # Morph speed slider
        morph_speed_label = QLabel("Animation Speed:")
        morph_layout.addWidget(morph_speed_label)
        
        self.morph_speed_slider = QSlider(Qt.Horizontal)
        self.morph_speed_slider.setRange(10, 200)
        self.morph_speed_slider.setValue(50)
        self.morph_speed_slider.valueChanged.connect(self.on_morph_speed_changed)
        morph_layout.addWidget(self.morph_speed_slider)
        
        # Auto morph checkbox
        self.auto_morph_check = QCheckBox("Auto-Animate Morphing")
        self.auto_morph_check.stateChanged.connect(self.toggle_auto_morph)
        morph_layout.addWidget(self.auto_morph_check)
        
        # Wireframe checkbox
        self.wireframe_check = QCheckBox("Wireframe Mode")
        self.wireframe_check.stateChanged.connect(self.toggle_wireframe)
        morph_layout.addWidget(self.wireframe_check)
        
        layout.addWidget(morph_group)
        
        # === Particle Controls ===
        particle_group = QGroupBox("Particle Effects")
        particle_layout = QVBoxLayout(particle_group)
        
        # Particle enable checkbox
        self.particles_enabled_check = QCheckBox("Enable Particles")
        self.particles_enabled_check.setChecked(True)
        self.particles_enabled_check.stateChanged.connect(self.toggle_particles)
        particle_layout.addWidget(self.particles_enabled_check)
        
        # Physics checkbox
        self.physics_check = QCheckBox("Enable Physics")
        self.physics_check.setChecked(True)
        self.physics_check.stateChanged.connect(self.toggle_physics)
        particle_layout.addWidget(self.physics_check)
        
        # Particle intensity
        particle_label = QLabel("Particle Intensity:")
        particle_layout.addWidget(particle_label)
        
        self.particle_slider = QSlider(Qt.Horizontal)
        self.particle_slider.setRange(0, 200)
        self.particle_slider.setValue(100)
        self.particle_slider.valueChanged.connect(self.on_particle_intensity_changed)
        particle_layout.addWidget(self.particle_slider)
        
        # Color shift slider
        color_label = QLabel("Color Shift:")
        particle_layout.addWidget(color_label)
        
        self.color_shift_slider = QSlider(Qt.Horizontal)
        self.color_shift_slider.setRange(0, 100)
        self.color_shift_slider.setValue(0)
        self.color_shift_slider.valueChanged.connect(self.on_color_shift_changed)
        particle_layout.addWidget(self.color_shift_slider)
        
        # Particle count label
        self.particle_count_label = QLabel("Particles: 0")
        particle_layout.addWidget(self.particle_count_label)
        
        # Clear particles button
        clear_btn = QPushButton("Clear All Particles")
        clear_btn.clicked.connect(self.clear_particles)
        particle_layout.addWidget(clear_btn)
        
        layout.addWidget(particle_group)
        
        # === Effect Presets ===
        preset_group = QGroupBox("Effect Presets")
        preset_layout = QGridLayout(preset_group)
        
        # Preset buttons
        presets = [
            ("Ambient", self.preset_ambient),
            ("Aggressive", self.preset_aggressive),
            ("Psychedelic", self.preset_psychedelic),
            ("Minimal", self.preset_minimal),
            ("Galaxy", self.preset_galaxy),
            ("Underwater", self.preset_underwater)
        ]
        
        for i, (name, callback) in enumerate(presets):
            btn = QPushButton(name)
            btn.clicked.connect(callback)
            preset_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(preset_group)
        
        # === Special Effects ===
        effects_group = QGroupBox("Special Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        # Effect buttons
        explosion_btn = QPushButton("Trigger Explosion")
        explosion_btn.clicked.connect(self.trigger_explosion)
        effects_layout.addWidget(explosion_btn)
        
        fountain_btn = QPushButton("Trigger Fountain")
        fountain_btn.clicked.connect(self.trigger_fountain)
        effects_layout.addWidget(fountain_btn)
        
        layout.addWidget(effects_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
        # Set the widget for the dock
        dock.setWidget(container)
        
        # Add dock to main window
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
    
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts for advanced features."""
        # Particle shortcuts
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.toggle_particles)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.trigger_explosion)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.trigger_fountain)
        QShortcut(QKeySequence("Ctrl+Shift+C"), self).activated.connect(self.clear_particles)
        
        # Morphing shortcuts
        QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(self.toggle_auto_morph)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.toggle_wireframe)
        
        # Preset shortcuts
        QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(self.preset_ambient)
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(self.preset_aggressive)
        QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(self.preset_psychedelic)
        QShortcut(QKeySequence("Ctrl+4"), self).activated.connect(self.preset_minimal)
    
    # === Callback Methods ===
    
    def on_morph_mode_changed(self, index):
        """Handle morphing mode change."""
        modes = list(MorphingMode)
        if index < len(modes):
            self.adv_morphing.create_morph_geometry(modes[index])
            print(f"Morphing mode changed to: {modes[index].value}")
    
    def on_adv_morph_changed(self, value):
        """Handle advanced morph slider change."""
        self.adv_morphing.update_morph(value / 100.0)
    
    def on_morph_speed_changed(self, value):
        """Handle morph speed change."""
        self.adv_morphing.morph_speed = value / 100.0
    
    def toggle_auto_morph(self):
        """Toggle automatic morphing."""
        self.adv_morphing.toggle_auto_morph()
        self.auto_morph_check.setChecked(self.adv_morphing.auto_morph)
        print(f"Auto-morph: {'ON' if self.adv_morphing.auto_morph else 'OFF'}")
    
    def toggle_wireframe(self):
        """Toggle wireframe rendering."""
        self.adv_morphing.toggle_wireframe()
        self.wireframe_check.setChecked(self.adv_morphing.wireframe)
        print(f"Wireframe: {'ON' if self.adv_morphing.wireframe else 'OFF'}")
    
    def toggle_particles(self):
        """Toggle particle effects."""
        self.adv_particles.enabled = self.particles_enabled_check.isChecked()
        if not self.adv_particles.enabled:
            self.adv_particles.clear_all_particles()
        print(f"Particles: {'ON' if self.adv_particles.enabled else 'OFF'}")
    
    def toggle_physics(self):
        """Toggle particle physics."""
        self.adv_particles.physics_enabled = self.physics_check.isChecked()
        print(f"Physics: {'ON' if self.adv_particles.physics_enabled else 'OFF'}")
    
    def on_particle_intensity_changed(self, value):
        """Handle particle intensity change."""
        self.adv_particles.particle_intensity = value / 100.0
    
    def on_color_shift_changed(self, value):
        """Handle color shift change."""
        self.adv_particles.color_shift = value / 100.0
    
    def clear_particles(self):
        """Clear all particles."""
        self.adv_particles.clear_all_particles()
        print("All particles cleared")
    
    def trigger_explosion(self):
        """Trigger explosion effect."""
        position = np.array([0, 0, 0])
        self.adv_particles.emit_special_effect("explosion", position, 1.0)
        print("💥 Explosion triggered!")
    
    def trigger_fountain(self):
        """Trigger fountain effect."""
        position = np.array([0, -3, 0])
        self.adv_particles.emit_special_effect("fountain", position, 1.0)
        print("⛲ Fountain triggered!")
    
    # === Presets ===
    
    def preset_ambient(self):
        """Apply ambient preset."""
        self.morph_combo.setCurrentIndex(0)  # Sphere to Cube
        self.particle_slider.setValue(50)
        self.color_shift_slider.setValue(30)
        self.morph_speed_slider.setValue(30)
        self.auto_morph_check.setChecked(True)
        print("🌊 Ambient preset applied")
    
    def preset_aggressive(self):
        """Apply aggressive preset."""
        self.morph_combo.setCurrentIndex(3)  # Crystal
        self.particle_slider.setValue(150)
        self.color_shift_slider.setValue(0)
        self.morph_speed_slider.setValue(100)
        self.auto_morph_check.setChecked(False)
        print("🔥 Aggressive preset applied")
    
    def preset_psychedelic(self):
        """Apply psychedelic preset."""
        self.morph_combo.setCurrentIndex(4)  # Fluid
        self.particle_slider.setValue(100)
        self.color_shift_slider.setValue(75)
        self.morph_speed_slider.setValue(60)
        self.auto_morph_check.setChecked(True)
        print("🌈 Psychedelic preset applied")
    
    def preset_minimal(self):
        """Apply minimal preset."""
        self.morph_combo.setCurrentIndex(0)  # Sphere to Cube
        self.particle_slider.setValue(20)
        self.color_shift_slider.setValue(0)
        self.morph_speed_slider.setValue(20)
        self.auto_morph_check.setChecked(False)
        self.wireframe_check.setChecked(True)
        print("⚪ Minimal preset applied")
    
    def preset_galaxy(self):
        """Apply galaxy preset."""
        self.morph_combo.setCurrentIndex(6)  # Galaxy
        self.particle_slider.setValue(120)
        self.color_shift_slider.setValue(60)
        self.morph_speed_slider.setValue(40)
        self.auto_morph_check.setChecked(True)
        print("🌌 Galaxy preset applied")
    
    def preset_underwater(self):
        """Apply underwater preset."""
        self.morph_combo.setCurrentIndex(4)  # Fluid
        self.particle_slider.setValue(80)
        self.color_shift_slider.setValue(55)  # Blue-green
        self.morph_speed_slider.setValue(25)
        self.auto_morph_check.setChecked(True)
        self.physics_check.setChecked(True)
        print("🌊 Underwater preset applied")
    
    # === MIDI Handling ===
    
    def handle_midi_note_advanced(self, note, velocity):
        """Enhanced MIDI note handler with advanced features."""
        # Call base handler if it exists
        if hasattr(super(), 'handle_midi_note'):
            super().handle_midi_note(note, velocity)
        
        # Emit particles based on note
        self.adv_particles.emit_note_particles(note, velocity)
        
        # Apply morphing based on note
        self.adv_morphing.morph_from_midi(note, velocity)
        
        # Update status
        octave = note // 12
        note_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][note % 12]
        self.statusBar().showMessage(f"Note: {note_name}{octave} (vel: {int(velocity*127)})", 2000)
    
    def handle_midi_off_advanced(self, note):
        """Handle MIDI note off."""
        # Call base handler if it exists
        if hasattr(super(), 'handle_midi_off'):
            super().handle_midi_off(note)
    
    # === Animation Loop ===
    
    def animate_frame(self):
        """Main animation loop for advanced features."""
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Limit dt to prevent large jumps
        dt = min(dt, 0.1)
        
        # Update particle system
        if hasattr(self, 'adv_particles'):
            self.adv_particles.update(dt)
            # Update particle count
            count = self.adv_particles.get_particle_count()
            self.particle_count_label.setText(f"Particles: {count}")
        
        # Update morphing animation
        if hasattr(self, 'adv_morphing'):
            self.adv_morphing.animate_morph(dt)
        
        # Update render
        self.plotter_widget.update()
    
    # === Keyboard Testing (for development without MIDI) ===
    
    def keyPressEvent(self, event):
        """Handle keyboard input for testing without MIDI device."""
        # Map keyboard keys to MIDI notes
        key_to_note = {
            Qt.Key_A: 60,  # C4
            Qt.Key_W: 61,  # C#4
            Qt.Key_S: 62,  # D4
            Qt.Key_E: 63,  # D#4
            Qt.Key_D: 64,  # E4
            Qt.Key_F: 65,  # F4
            Qt.Key_T: 66,  # F#4
            Qt.Key_G: 67,  # G4
            Qt.Key_Y: 68,  # G#4
            Qt.Key_H: 69,  # A4
            Qt.Key_U: 70,  # A#4
            Qt.Key_J: 71,  # B4
            Qt.Key_K: 72,  # C5
            Qt.Key_O: 73,  # C#5
            Qt.Key_L: 74,  # D5
        }
        
        if event.key() in key_to_note and not event.isAutoRepeat():
            note = key_to_note[event.key()]
            velocity = 0.5 + np.random.random() * 0.5  # Random velocity
            self.handle_midi_note_advanced(note, velocity)
        
        # Call base implementation
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Handle keyboard release for testing."""
        key_to_note = {
            Qt.Key_A: 60, Qt.Key_W: 61, Qt.Key_S: 62, Qt.Key_E: 63,
            Qt.Key_D: 64, Qt.Key_F: 65, Qt.Key_T: 66, Qt.Key_G: 67,
            Qt.Key_Y: 68, Qt.Key_H: 69, Qt.Key_U: 70, Qt.Key_J: 71,
            Qt.Key_K: 72, Qt.Key_O: 73, Qt.Key_L: 74
        }
        
        if event.key() in key_to_note and not event.isAutoRepeat():
            note = key_to_note[event.key()]
            self.handle_midi_off_advanced(note)
        
        # Call base implementation
        super().keyReleaseEvent(event)

# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Main application entry point."""
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced MIDI Visualizer")
    app.setOrganizationName("MIDI Morphing")
    
    # Create and show main window
    window = EnhancedMainWindow()
    window.setWindowTitle("🎹 Enhanced MIDI Morphing Visualizer")
    window.resize(1200, 800)
    window.show()
    
    # Print instructions
    print("\n" + "="*60)
    print("🎹 ENHANCED MIDI MORPHING VISUALIZER")
    print("="*60)
    print("\nFEATURES:")
    print("✨ Advanced particle system with physics")
    print("🎭 Multiple morphing modes (7 different styles)")
    print("🎨 Dynamic color shifting")
    print("⚡ Special effects (explosions, fountains)")
    print("🎵 MIDI-reactive visualization")
    print("\nCONTROLS:")
    print("📎 Connect MIDI device or use keyboard (A-L keys)")
    print("⌨️ Keyboard shortcuts:")
    print("  • Ctrl+P: Toggle particles")
    print("  • Ctrl+E: Explosion effect")
    print("  • Ctrl+F: Fountain effect")
    print("  • Ctrl+M: Toggle auto-morph")
    print("  • Ctrl+W: Toggle wireframe")
    print("  • Ctrl+1-4: Apply presets")
    print("\nKEYBOARD PIANO:")
    print("  A W S E D F T G Y H U J K O L")
    print("  C C# D D# E F F# G G# A A# B C C# D")
    print("\nEnjoy creating amazing visuals! 🎉")
    print("="*60 + "\n")
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())

# Export the enhanced main window class
MainWindow = EnhancedMainWindow
__all__ = ['MainWindow', 'EnhancedMainWindow']
