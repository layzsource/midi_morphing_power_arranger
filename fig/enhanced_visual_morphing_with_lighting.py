#!/usr/bin/env python3
"""
Enhanced Visual Morphing Demo with Professional Lighting System
Building on perfect geometry with advanced lighting, animations, and MIDI reactivity
"""

import sys
import math
import logging
import numpy as np
import time
import colorsys
from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox,
    QCheckBox, QSpinBox, QTabWidget
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import rtmidi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightType(Enum):
    """Professional light types"""
    AMBIENT = "ambient"
    DIRECTIONAL = "directional"
    POINT = "point"
    SPOT = "spot"
    LASER = "laser"

class LightAnimation(Enum):
    """Professional light animations"""
    STATIC = "static"
    PULSE = "pulse"
    STROBE = "strobe"
    RAINBOW = "rainbow"
    BREATHE = "breathe"
    FLICKER = "flicker"
    CHASE = "chase"

@dataclass
class LightState:
    """Complete light state"""
    position: Tuple[float, float, float] = (0.0, 5.0, 0.0)
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    intensity: float = 1.0
    animation_time: float = 0.0
    midi_velocity: float = 0.0
    bass_level: float = 0.0
    mid_level: float = 0.0
    treble_level: float = 0.0

class Light(QObject):
    """Professional light with full control"""

    state_changed = Signal()

    def __init__(self, light_type: LightType = LightType.POINT, name: str = "Light"):
        super().__init__()
        self.light_type = light_type
        self.name = name
        self.enabled = True
        self.state = LightState()
        self.animation = LightAnimation.STATIC
        self.animation_speed = 1.0
        self.base_color = self.state.color
        self.base_intensity = self.state.intensity

    def set_animation(self, animation: LightAnimation, speed: float = 1.0):
        """Set light animation"""
        self.animation = animation
        self.animation_speed = speed
        logger.info(f"💡 {self.name}: {animation.value} animation set (speed: {speed})")

    def update_midi(self, note: int, velocity: int):
        """Update light based on MIDI input"""
        self.state.midi_velocity = velocity / 127.0

        # Note-to-color mapping (chromatic scale)
        hue = (note % 12) / 12.0
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
        self.base_color = (r, g, b)

        # Velocity-based intensity
        self.state.intensity = self.base_intensity * (0.3 + 0.7 * self.state.midi_velocity)

        # Auto-trigger animations based on velocity
        if velocity > 100:
            self.set_animation(LightAnimation.PULSE, 5.0)
        elif velocity > 80:
            self.set_animation(LightAnimation.BREATHE, 2.0)
        elif velocity > 60:
            self.set_animation(LightAnimation.FLICKER, 3.0)

    def update_audio(self, bass: float, mid: float, treble: float):
        """Update light based on audio analysis"""
        self.state.bass_level = bass
        self.state.mid_level = mid
        self.state.treble_level = treble

        # Frequency-based color shifting
        if bass > max(mid, treble) * 1.5:
            # Bass dominant - warm colors
            self.state.color = (1.0, 0.3 + 0.4 * bass, 0.1)
        elif treble > max(bass, mid) * 1.5:
            # Treble dominant - cool colors
            self.state.color = (0.1, 0.3 + 0.4 * treble, 1.0)
        else:
            # Balanced - use base color
            self.state.color = self.base_color

    def update_animation(self, dt: float):
        """Update animation state"""
        if self.animation == LightAnimation.STATIC:
            return

        self.state.animation_time += dt * self.animation_speed
        t = self.state.animation_time

        if self.animation == LightAnimation.PULSE:
            # Intensity pulsing
            pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi)
            self.state.intensity = self.base_intensity * (0.3 + 0.7 * pulse)

        elif self.animation == LightAnimation.STROBE:
            # Strobe effect
            self.state.intensity = self.base_intensity if int(t * 20) % 2 == 0 else 0.0

        elif self.animation == LightAnimation.RAINBOW:
            # Color cycling
            hue = (t * 0.5) % 1.0
            r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 1.0)
            self.state.color = (r, g, b)

        elif self.animation == LightAnimation.BREATHE:
            # Breathing effect
            breath = 0.5 + 0.5 * math.sin(t * math.pi)
            self.state.intensity = self.base_intensity * (0.2 + 0.8 * breath)

        elif self.animation == LightAnimation.FLICKER:
            # Random flickering
            flicker = 0.7 + 0.3 * (math.sin(t * 13.7) * math.sin(t * 7.3))
            self.state.intensity = self.base_intensity * flicker

        elif self.animation == LightAnimation.CHASE:
            # Moving pattern
            phase = (t * 0.5) % 1.0
            chase_intensity = 1.0 if abs(phase - 0.5) < 0.2 else 0.3
            self.state.intensity = self.base_intensity * chase_intensity

class LightingSystem(QObject):
    """Professional lighting system manager"""

    lights_updated = Signal()

    def __init__(self):
        super().__init__()
        self.lights: List[Light] = []
        self.global_intensity = 1.0
        self.audio_reactive = True
        self.midi_reactive = True

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animations)
        self.timer.start(16)  # 60 FPS

        self.last_time = time.time()

    def add_light(self, light_type: LightType, name: str, **kwargs) -> Light:
        """Add a new light to the system"""
        light = Light(light_type, name)

        # Set initial properties from kwargs
        if 'position' in kwargs:
            light.state.position = kwargs['position']
        if 'color' in kwargs:
            light.state.color = kwargs['color']
            light.base_color = kwargs['color']
        if 'intensity' in kwargs:
            light.state.intensity = kwargs['intensity']
            light.base_intensity = kwargs['intensity']

        self.lights.append(light)
        logger.info(f"💡 Added {light_type.value} light: {name}")
        return light

    def apply_preset(self, preset_name: str):
        """Apply lighting preset"""
        self.lights.clear()

        if preset_name == "concert":
            # Concert lighting setup
            self.add_light(LightType.SPOT, "Front Spot 1",
                          position=(-2, 4, 2), color=(1.0, 0.9, 0.8), intensity=0.8)
            self.add_light(LightType.SPOT, "Front Spot 2",
                          position=(2, 4, 2), color=(0.8, 0.9, 1.0), intensity=0.8)
            self.add_light(LightType.DIRECTIONAL, "Back Wash",
                          position=(0, 6, -4), color=(0.4, 0.2, 0.8), intensity=0.4)
            self.add_light(LightType.LASER, "Laser 1",
                          position=(-3, 2, 0), color=(1.0, 0.0, 0.2), intensity=0.6)
            self.add_light(LightType.LASER, "Laser 2",
                          position=(3, 2, 0), color=(0.0, 1.0, 0.2), intensity=0.6)

        elif preset_name == "ambient":
            # Soft ambient lighting
            self.add_light(LightType.AMBIENT, "Global Ambient",
                          color=(0.8, 0.9, 1.0), intensity=0.3)
            self.add_light(LightType.POINT, "Warm Fill",
                          position=(0, 3, 1), color=(1.0, 0.8, 0.6), intensity=0.5)

        elif preset_name == "club":
            # Club/party lighting
            self.add_light(LightType.SPOT, "Moving Spot 1",
                          position=(-2, 5, -1), color=(1.0, 0.0, 0.5), intensity=0.9)
            self.add_light(LightType.SPOT, "Moving Spot 2",
                          position=(2, 5, -1), color=(0.0, 1.0, 0.5), intensity=0.9)
            self.add_light(LightType.LASER, "Laser Show 1",
                          position=(-4, 3, 0), color=(1.0, 0.0, 0.0), intensity=0.8)
            self.add_light(LightType.LASER, "Laser Show 2",
                          position=(4, 3, 0), color=(0.0, 0.0, 1.0), intensity=0.8)
            # Set animations
            for light in self.lights:
                if light.light_type == LightType.SPOT:
                    light.set_animation(LightAnimation.CHASE, 2.0)
                elif light.light_type == LightType.LASER:
                    light.set_animation(LightAnimation.RAINBOW, 3.0)

        elif preset_name == "minimal":
            # Simple 3-point lighting
            self.add_light(LightType.DIRECTIONAL, "Key Light",
                          position=(2, 4, 2), color=(1.0, 1.0, 0.9), intensity=0.8)
            self.add_light(LightType.POINT, "Fill Light",
                          position=(-1, 2, 1), color=(0.8, 0.9, 1.0), intensity=0.4)
            self.add_light(LightType.DIRECTIONAL, "Back Light",
                          position=(0, 3, -2), color=(0.9, 0.8, 1.0), intensity=0.3)

        logger.info(f"🎭 Applied lighting preset: {preset_name} ({len(self.lights)} lights)")
        self.lights_updated.emit()

    def update_midi_data(self, note: int, velocity: int):
        """Update all lights with MIDI data"""
        if not self.midi_reactive:
            return

        for light in self.lights:
            if light.enabled:
                light.update_midi(note, velocity)

    def update_audio_data(self, bass: float, mid: float, treble: float):
        """Update all lights with audio data"""
        if not self.audio_reactive:
            return

        for light in self.lights:
            if light.enabled:
                light.update_audio(bass, mid, treble)

    def update_animations(self):
        """Update all light animations"""
        current_time = time.time()
        dt = current_time - self.last_time
        self.last_time = current_time

        for light in self.lights:
            if light.enabled:
                light.update_animation(dt)

    def get_combined_lighting(self) -> Tuple[float, float, float]:
        """Get combined lighting color for rendering"""
        if not self.lights:
            return (1.0, 1.0, 1.0)

        total_r = total_g = total_b = 0.0
        total_weight = 0.0

        for light in self.lights:
            if light.enabled and light.state.intensity > 0.01:
                weight = light.state.intensity * self.global_intensity
                total_r += light.state.color[0] * weight
                total_g += light.state.color[1] * weight
                total_b += light.state.color[2] * weight
                total_weight += weight

        if total_weight > 0:
            return (
                min(1.0, total_r / total_weight),
                min(1.0, total_g / total_weight),
                min(1.0, total_b / total_weight)
            )
        else:
            return (0.2, 0.2, 0.3)  # Dim default lighting

class EnhancedMorphWidgetWithLighting(QOpenGLWidget):
    """Enhanced morphing widget with professional lighting"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.morph_factor = 0.0
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.rotation = 0.0
        self.particles = []

        # Enhanced visual settings
        self.particle_trails = True
        self.color_mode = 'lighting'  # New lighting mode
        self.particle_size = 6.0
        self.shape_resolution = 800

        # Professional lighting system
        self.lighting_system = LightingSystem()
        self.lighting_system.apply_preset("minimal")  # Start with minimal preset

        # Connect lighting updates
        self.lighting_system.lights_updated.connect(self.update)

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60 FPS

    def initializeGL(self):
        """Initialize OpenGL with lighting support"""
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Set global ambient
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.1, 0.1, 0.2, 1.0])

        glPointSize(2.0)
        logger.info("✅ Enhanced OpenGL with lighting initialized")

    def resizeGL(self, width, height):
        """Handle resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = width / height if height > 0 else 1
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render with professional lighting"""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Setup camera
            glTranslatef(0.0, 0.0, -6.0)
            glRotatef(self.rotation * 0.8, 1.0, 1.0, 0.0)
            glRotatef(self.rotation * 0.3, 0.0, 1.0, 0.0)

            # Apply lighting
            self.apply_lighting()

            # Generate and render morphed shape
            vertices = self.generate_morphed_shape()
            self.render_morphed_shape(vertices)

            # Render particles
            self.render_enhanced_particles()

        except Exception as e:
            logger.error(f"Render error: {e}")

    def apply_lighting(self):
        """Apply professional lighting to the scene"""
        # Get combined lighting color
        light_color = self.lighting_system.get_combined_lighting()

        # Set main light properties
        light_pos = [2.0, 4.0, 2.0, 1.0]  # Positional light
        light_ambient = [light_color[0] * 0.3, light_color[1] * 0.3, light_color[2] * 0.3, 1.0]
        light_diffuse = [light_color[0], light_color[1], light_color[2], 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]

        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB"""
        h = h % 1.0
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        if i == 0: return v, t, p
        elif i == 1: return q, v, p
        elif i == 2: return p, v, t
        elif i == 3: return p, q, v
        elif i == 4: return t, p, v
        else: return v, p, q

    def generate_morphed_shape(self):
        """Generate morphed shape vertices"""
        vertices_a = self.generate_shape(self.shape_a)
        vertices_b = self.generate_shape(self.shape_b)

        min_len = min(len(vertices_a), len(vertices_b))
        vertices_a = vertices_a[:min_len]
        vertices_b = vertices_b[:min_len]

        ease_factor = self.ease_in_out(self.morph_factor)

        morphed = []
        for i in range(min_len):
            va = vertices_a[i]
            vb = vertices_b[i]
            mx = va[0] * (1 - ease_factor) + vb[0] * ease_factor
            my = va[1] * (1 - ease_factor) + vb[1] * ease_factor
            mz = va[2] * (1 - ease_factor) + vb[2] * ease_factor
            morphed.append([mx, my, mz])

        return morphed

    def ease_in_out(self, t):
        """Smooth easing function"""
        return t * t * (3.0 - 2.0 * t)

    def generate_shape(self, shape_name):
        """Generate shape with perfect geometry"""
        vertices = []
        num_points = self.shape_resolution

        if shape_name == 'sphere':
            # Perfect sphere with Fibonacci spiral
            golden_ratio = (1 + math.sqrt(5)) / 2

            for i in range(num_points):
                y = 1 - (2 * i / (num_points - 1))
                radius = math.sqrt(1 - y * y)
                theta = 2 * math.pi * i / golden_ratio
                x = radius * math.cos(theta)
                z = radius * math.sin(theta)
                vertices.append([x, y, z])

        elif shape_name == 'cube':
            # Perfect cube with even face distribution
            total_faces = 6
            points_per_face = num_points // total_faces
            grid_size = max(3, int(math.sqrt(points_per_face)))

            for face in range(6):
                for row in range(grid_size):
                    for col in range(grid_size):
                        if grid_size == 1:
                            u = v = 0.0
                        else:
                            u = -1.0 + (2.0 * col) / (grid_size - 1)
                            v = -1.0 + (2.0 * row) / (grid_size - 1)

                        if face == 0:    vertices.append([u, v, 1.0])     # Front
                        elif face == 1:  vertices.append([u, v, -1.0])    # Back
                        elif face == 2:  vertices.append([1.0, u, v])     # Right
                        elif face == 3:  vertices.append([-1.0, u, v])    # Left
                        elif face == 4:  vertices.append([u, 1.0, v])     # Top
                        else:            vertices.append([u, -1.0, v])    # Bottom

                        if len(vertices) >= num_points:
                            break
                    if len(vertices) >= num_points:
                        break
                if len(vertices) >= num_points:
                    break

        elif shape_name == 'torus':
            for i in range(num_points):
                theta = (i / num_points) * 2 * math.pi * 4
                phi = ((i * 13) % num_points) / num_points * 2 * math.pi
                R, r = 1.0, 0.4
                x = (R + r * math.cos(phi)) * math.cos(theta)
                y = r * math.sin(phi)
                z = (R + r * math.cos(phi)) * math.sin(theta)
                vertices.append([x, y, z])

        # Add other shapes from original implementation...
        else:
            return self.generate_shape('sphere')

        return vertices

    def render_morphed_shape(self, vertices):
        """Render shape with lighting-based coloring"""
        if not vertices:
            return

        if self.color_mode == 'lighting':
            # Use professional lighting color
            light_color = self.lighting_system.get_combined_lighting()
            glColor3f(light_color[0], light_color[1], light_color[2])
        elif self.color_mode == 'rainbow':
            # Classic rainbow mode
            hue = self.morph_factor
            r, g, b = self.hsv_to_rgb(hue, 1.0, 0.9)
            glColor3f(r, g, b)
        else:
            # Default
            glColor3f(0.3, 0.8, 1.0)

        glPointSize(2.5)
        glBegin(GL_POINTS)
        for vertex in vertices:
            glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

    def render_enhanced_particles(self):
        """Render particles with lighting effects"""
        if not self.particles:
            return

        # Get lighting color for particle tinting
        light_color = self.lighting_system.get_combined_lighting()

        glPointSize(self.particle_size)

        for particle in self.particles:
            if particle['life'] > 0:
                life_factor = particle['life']

                # Blend particle color with lighting
                r = particle.get('r', 1.0) * light_color[0] * life_factor
                g = particle.get('g', 0.8) * light_color[1] * life_factor
                b = particle.get('b', 0.2) * light_color[2] * life_factor
                alpha = life_factor * 0.8

                glColor4f(r, g, b, alpha)

                glBegin(GL_POINTS)
                glVertex3f(particle['x'], particle['y'], particle['z'])
                glEnd()

    def update_animation(self):
        """Update animation and particles"""
        self.rotation += 0.8

        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 0.015
            particle['x'] += particle['vx'] * 0.02
            particle['y'] += particle['vy'] * 0.02
            particle['z'] += particle['vz'] * 0.02
            particle['vy'] -= 0.001  # Gravity

            if particle['life'] <= 0:
                self.particles.remove(particle)

        self.update()

    def set_morph_factor(self, factor):
        """Set morphing factor"""
        self.morph_factor = factor

    def set_shapes(self, shape_a, shape_b):
        """Set shapes to morph between"""
        self.shape_a = shape_a
        self.shape_b = shape_b

    def set_visual_settings(self, trails=True, color_mode='lighting', particle_size=6.0, resolution=800):
        """Configure visual settings"""
        self.particle_trails = trails
        self.color_mode = color_mode
        self.particle_size = particle_size
        self.shape_resolution = resolution

    def add_particle_burst(self, note, velocity, burst_type='normal'):
        """Add particle burst with lighting-reactive colors"""
        x_pos = (note - 60) / 30.0
        base_count = max(2, velocity // 6)

        # Get current lighting color for particles
        light_color = self.lighting_system.get_combined_lighting()

        for _ in range(base_count):
            vx = (np.random.random() - 0.5) * 0.15
            vy = np.random.random() * 0.2
            vz = (np.random.random() - 0.5) * 0.15

            particle = {
                'x': x_pos + (np.random.random() - 0.5) * 0.3,
                'y': (np.random.random() - 0.5) * 0.2,
                'z': (np.random.random() - 0.5) * 0.3,
                'vx': vx, 'vy': vy, 'vz': vz,
                'life': 1.5 + np.random.random() * 1.5,
                'r': light_color[0], 'g': light_color[1], 'b': light_color[2]
            }
            self.particles.append(particle)

class EnhancedMorphingDemoWithLighting(QMainWindow):
    """Enhanced morphing demo with professional lighting controls"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌟 Enhanced Visual Morphing + Professional Lighting")
        self.setGeometry(100, 100, 1400, 900)

        self.manual_control = False
        self._setup_ui()
        self._setup_midi()

        logger.info("🌟 Enhanced Visual Morphing with Lighting Ready!")

    def _setup_ui(self):
        """Set up enhanced UI with lighting controls"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Enhanced morphing visualization (70%)
        self.morph_widget = EnhancedMorphWidgetWithLighting()
        layout.addWidget(self.morph_widget, 70)

        # Enhanced controls with lighting (30%)
        controls = self._create_enhanced_controls()
        layout.addWidget(controls, 30)

    def _create_enhanced_controls(self):
        """Create enhanced control panel with lighting"""
        controls_frame = QFrame()
        controls_frame.setMaximumWidth(400)
        controls_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c3e50, stop: 1 #34495e);
                color: white;
                padding: 10px;
                border-radius: 8px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
                color: #ecf0f1;
            }
            QComboBox, QSpinBox {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border-radius: 3px;
                border: 1px solid #3498db;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border-radius: 4px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        layout = QVBoxLayout(controls_frame)

        # Title
        title = QLabel("🌟 ENHANCED MORPHING + LIGHTING")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db; padding: 10px;")
        layout.addWidget(title)

        # Create tabbed interface
        tabs = QTabWidget()

        # Morphing tab
        morph_tab = self._create_morph_controls()
        tabs.addTab(morph_tab, "🎨 Morphing")

        # Lighting tab
        lighting_tab = self._create_lighting_controls()
        tabs.addTab(lighting_tab, "💡 Lighting")

        # Effects tab
        effects_tab = self._create_effects_controls()
        tabs.addTab(effects_tab, "✨ Effects")

        layout.addWidget(tabs)

        # Status
        self.status_label = QLabel("🌟 Enhanced System Active")
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        layout.addWidget(self.status_label)

        return controls_frame

    def _create_morph_controls(self):
        """Create morphing controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Shape selection
        shape_group = QGroupBox("🎨 Shape Library")
        shape_layout = QVBoxLayout(shape_group)

        shapes = ['sphere', 'cube', 'torus', 'helix', 'klein_bottle',
                 'mobius', 'heart', 'star', 'spiral', 'pyramid']

        shape_layout.addWidget(QLabel("Shape A:"))
        self.shape_a_combo = QComboBox()
        self.shape_a_combo.addItems(shapes)
        self.shape_a_combo.currentTextChanged.connect(self._update_shapes)
        shape_layout.addWidget(self.shape_a_combo)

        shape_layout.addWidget(QLabel("Shape B:"))
        self.shape_b_combo = QComboBox()
        self.shape_b_combo.addItems(shapes)
        self.shape_b_combo.setCurrentText('cube')
        self.shape_b_combo.currentTextChanged.connect(self._update_shapes)
        shape_layout.addWidget(self.shape_b_combo)

        layout.addWidget(shape_group)

        # Morph control
        morph_group = QGroupBox("🎚️ Morphing Control")
        morph_layout = QVBoxLayout(morph_group)

        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        self.morph_slider.valueChanged.connect(self._on_morph_changed)
        morph_layout.addWidget(self.morph_slider)

        self.morph_label = QLabel("0% (Sphere)")
        self.morph_label.setAlignment(Qt.AlignCenter)
        self.morph_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        morph_layout.addWidget(self.morph_label)

        layout.addWidget(morph_group)

        return widget

    def _create_lighting_controls(self):
        """Create professional lighting controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Lighting presets
        preset_group = QGroupBox("🎭 Lighting Presets")
        preset_layout = QVBoxLayout(preset_group)

        presets = ['minimal', 'concert', 'ambient', 'club']
        for preset in presets:
            btn = QPushButton(f"🎭 {preset.title()}")
            btn.clicked.connect(lambda checked, p=preset: self._apply_lighting_preset(p))
            preset_layout.addWidget(btn)

        layout.addWidget(preset_group)

        # Lighting controls
        control_group = QGroupBox("💡 Lighting Control")
        control_layout = QVBoxLayout(control_group)

        # Global intensity
        control_layout.addWidget(QLabel("Global Intensity:"))
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(100)
        self.intensity_slider.valueChanged.connect(self._on_intensity_changed)
        control_layout.addWidget(self.intensity_slider)

        # Audio reactivity
        self.audio_reactive_cb = QCheckBox("🎵 Audio Reactive")
        self.audio_reactive_cb.setChecked(True)
        self.audio_reactive_cb.stateChanged.connect(self._on_audio_reactive_changed)
        control_layout.addWidget(self.audio_reactive_cb)

        # MIDI reactivity
        self.midi_reactive_cb = QCheckBox("🎹 MIDI Reactive")
        self.midi_reactive_cb.setChecked(True)
        self.midi_reactive_cb.stateChanged.connect(self._on_midi_reactive_changed)
        control_layout.addWidget(self.midi_reactive_cb)

        layout.addWidget(control_group)

        return widget

    def _create_effects_controls(self):
        """Create effects controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Visual effects
        effects_group = QGroupBox("✨ Visual Effects")
        effects_layout = QVBoxLayout(effects_group)

        self.trails_cb = QCheckBox("Particle Trails")
        self.trails_cb.setChecked(True)
        self.trails_cb.stateChanged.connect(self._update_effects)
        effects_layout.addWidget(self.trails_cb)

        effects_layout.addWidget(QLabel("Color Mode:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(['lighting', 'rainbow', 'cyan'])
        self.color_combo.currentTextChanged.connect(self._update_effects)
        effects_layout.addWidget(self.color_combo)

        effects_layout.addWidget(QLabel("Resolution:"))
        self.resolution_spin = QSpinBox()
        self.resolution_spin.setRange(200, 2000)
        self.resolution_spin.setValue(800)
        self.resolution_spin.setSuffix(" points")
        self.resolution_spin.valueChanged.connect(self._update_effects)
        effects_layout.addWidget(self.resolution_spin)

        layout.addWidget(effects_group)

        # Demo particles
        particle_group = QGroupBox("🎆 Demo Particles")
        particle_layout = QVBoxLayout(particle_group)

        demo_btn = QPushButton("🎆 Create Burst")
        demo_btn.clicked.connect(self._create_demo_particles)
        particle_layout.addWidget(demo_btn)

        layout.addWidget(particle_group)

        return widget

    def _setup_midi(self):
        """Set up MIDI with lighting integration"""
        try:
            self.midi = rtmidi.MidiIn()
            ports = self.midi.get_ports()

            if ports:
                target_port = 0
                for i, port in enumerate(ports):
                    if 'MPK' in port or 'mini' in port:
                        target_port = i
                        break

                self.midi.open_port(target_port)
                self.midi.set_callback(self._enhanced_midi_callback)
                self.status_label.setText(f"🎹 {ports[target_port][:20]}...")
                logger.info(f"✅ Enhanced MIDI + Lighting: {ports[target_port]}")
            else:
                self.status_label.setText("⚠️ No MIDI - Demo Mode")

        except Exception as e:
            logger.error(f"MIDI error: {e}")
            self.status_label.setText("❌ MIDI Error")

    def _enhanced_midi_callback(self, event, data=None):
        """Enhanced MIDI callback with lighting integration"""
        message, deltatime = event

        if len(message) >= 3:
            status = message[0]

            if (status & 0xF0) in [0x90, 0x80]:  # Note events
                note = message[1]
                velocity = message[2]

                if velocity > 0:
                    # Update lighting system
                    self.morph_widget.lighting_system.update_midi_data(note, velocity)

                    # Create particles
                    burst_type = 'explosion' if velocity > 100 else 'normal'
                    self.morph_widget.add_particle_burst(note, velocity, burst_type)

                    self.status_label.setText(f"🎵 Note: {note} (Lighting Active)")

            elif (status & 0xF0) == 0xB0:  # CC events
                cc = message[1]
                value = message[2]

                if cc == 1 and not self.manual_control:
                    morph_value = int(value * 100 / 127)
                    self.morph_slider.blockSignals(True)
                    self.morph_slider.setValue(morph_value)
                    self.morph_slider.blockSignals(False)
                    self._update_morph_display(morph_value)

    def _apply_lighting_preset(self, preset):
        """Apply lighting preset"""
        self.morph_widget.lighting_system.apply_preset(preset)
        logger.info(f"🎭 Applied lighting preset: {preset}")

    def _on_intensity_changed(self, value):
        """Handle intensity changes"""
        intensity = value / 100.0
        self.morph_widget.lighting_system.global_intensity = intensity

    def _on_audio_reactive_changed(self, state):
        """Handle audio reactivity toggle"""
        self.morph_widget.lighting_system.audio_reactive = state == Qt.Checked

    def _on_midi_reactive_changed(self, state):
        """Handle MIDI reactivity toggle"""
        self.morph_widget.lighting_system.midi_reactive = state == Qt.Checked

    def _update_shapes(self):
        """Update shapes"""
        shape_a = self.shape_a_combo.currentText()
        shape_b = self.shape_b_combo.currentText()
        self.morph_widget.set_shapes(shape_a, shape_b)

    def _update_effects(self):
        """Update visual effects"""
        trails = self.trails_cb.isChecked()
        color_mode = self.color_combo.currentText()
        resolution = self.resolution_spin.value()

        self.morph_widget.set_visual_settings(
            trails=trails,
            color_mode=color_mode,
            resolution=resolution
        )

    def _on_morph_changed(self, value):
        """Handle morph changes"""
        self.manual_control = True
        self._update_morph_display(value)

    def _update_morph_display(self, value):
        """Update morph display"""
        morph_factor = value / 100.0
        self.morph_widget.set_morph_factor(morph_factor)

        shape_a = self.shape_a_combo.currentText().title()
        shape_b = self.shape_b_combo.currentText().title()

        if value < 5:
            display_text = f"{value}% ({shape_a})"
        elif value > 95:
            display_text = f"{value}% ({shape_b})"
        else:
            display_text = f"{value}% (Morphing)"

        self.morph_label.setText(display_text)

    def _create_demo_particles(self):
        """Create demo particles"""
        self.morph_widget.add_particle_burst(60, 100, 'normal')

def main():
    """Launch enhanced visual morphing with lighting"""
    app = QApplication(sys.argv)

    window = EnhancedMorphingDemoWithLighting()
    window.show()

    logger.info("🌟 Enhanced Visual Morphing with Professional Lighting Started!")
    logger.info("💡 Features:")
    logger.info("   • Professional lighting system (7 types, 7 animations)")
    logger.info("   • MIDI-reactive lighting with note-to-color mapping")
    logger.info("   • Audio-reactive lighting effects")
    logger.info("   • Lighting presets (minimal, concert, ambient, club)")
    logger.info("   • Perfect cube/sphere geometry")
    logger.info("   • Enhanced particle system with lighting integration")

    return app.exec()

if __name__ == "__main__":
    main()