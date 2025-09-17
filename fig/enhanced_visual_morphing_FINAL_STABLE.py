#!/usr/bin/env python3
"""
Enhanced Visual Morphing Demo - Extended Shape Library + Effects
Building on the perfect visual foundation with more shapes and enhanced effects
"""

import sys
import math
import logging
import numpy as np
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox,
    QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import rtmidi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedMorphWidget(QOpenGLWidget):
    """Enhanced morphing visualization with extended shape library"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.morph_factor = 0.0
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.rotation = 0.0
        self.particles = []

        # Enhanced visual settings
        self.particle_trails = True
        self.color_mode = 'rainbow'
        self.particle_size = 6.0
        self.shape_resolution = 800

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60 FPS

    def initializeGL(self):
        """Initialize OpenGL with enhanced settings"""
        glClearColor(0.02, 0.02, 0.08, 1.0)  # Deep space background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPointSize(2.0)
        logger.info("✅ Enhanced OpenGL initialized")

    def resizeGL(self, width, height):
        """Handle resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = width / height if height > 0 else 1
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render enhanced morphing visualization"""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Dynamic camera setup
            glTranslatef(0.0, 0.0, -6.0)
            glRotatef(self.rotation * 0.8, 1.0, 1.0, 0.0)
            glRotatef(self.rotation * 0.3, 0.0, 1.0, 0.0)

            # Generate and render morphed shape
            vertices = self.generate_morphed_shape()
            self.render_morphed_shape(vertices)

            # Render enhanced particles
            self.render_enhanced_particles()

        except Exception as e:
            logger.error(f"Render error: {e}")

    def generate_morphed_shape(self):
        """Generate vertices for morphed shape with extended library"""
        vertices_a = self.generate_shape(self.shape_a)
        vertices_b = self.generate_shape(self.shape_b)

        # Ensure same number of vertices
        min_len = min(len(vertices_a), len(vertices_b))
        vertices_a = vertices_a[:min_len]
        vertices_b = vertices_b[:min_len]

        # Smooth morphing with easing
        ease_factor = self.ease_in_out(self.morph_factor)

        morphed = []
        for i in range(min_len):
            va = vertices_a[i]
            vb = vertices_b[i]

            # Enhanced morphing with rotation
            mx = va[0] * (1 - ease_factor) + vb[0] * ease_factor
            my = va[1] * (1 - ease_factor) + vb[1] * ease_factor
            mz = va[2] * (1 - ease_factor) + vb[2] * ease_factor

            morphed.append([mx, my, mz])

        return morphed

    def ease_in_out(self, t):
        """Smooth easing function for morphing"""
        return t * t * (3.0 - 2.0 * t)

    def generate_shape(self, shape_name):
        """Generate vertices for extended shape library"""
        vertices = []
        num_points = self.shape_resolution

        if shape_name == 'sphere':
            # Create perfect sphere with even distribution using Fibonacci spiral
            # This ensures no gaps or lines missing from the sphere

            golden_ratio = (1 + math.sqrt(5)) / 2  # φ (phi)

            for i in range(num_points):
                # Fibonacci spiral distribution for even sphere coverage
                y = 1 - (2 * i / (num_points - 1))  # y from 1 to -1
                radius = math.sqrt(1 - y * y)       # radius at y

                theta = 2 * math.pi * i / golden_ratio  # Golden angle

                x = radius * math.cos(theta)
                z = radius * math.sin(theta)

                vertices.append([x, y, z])

        elif shape_name == 'cube':
            # Create a perfect cube with precise geometry
            # Use a systematic approach to ensure equal face distribution

            # Calculate optimal grid size for even distribution
            total_faces = 6
            points_per_face = num_points // total_faces

            # Use perfect square grid for each face
            grid_size = max(3, int(math.sqrt(points_per_face)))  # Minimum 3x3 grid

            for face in range(6):
                # Generate grid points for this face
                for row in range(grid_size):
                    for col in range(grid_size):
                        # Create perfectly spaced coordinates from -1 to 1
                        if grid_size == 1:
                            u = v = 0.0
                        else:
                            u = -1.0 + (2.0 * col) / (grid_size - 1)
                            v = -1.0 + (2.0 * row) / (grid_size - 1)

                        # Map to cube faces with exact coordinates
                        if face == 0:    # Front face (z = +1)
                            vertices.append([u, v, 1.0])
                        elif face == 1:  # Back face (z = -1)
                            vertices.append([u, v, -1.0])
                        elif face == 2:  # Right face (x = +1)
                            vertices.append([1.0, u, v])
                        elif face == 3:  # Left face (x = -1)
                            vertices.append([-1.0, u, v])
                        elif face == 4:  # Top face (y = +1)
                            vertices.append([u, 1.0, v])
                        else:            # Bottom face (y = -1)
                            vertices.append([u, -1.0, v])

                        # Stop when we have enough points
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

        elif shape_name == 'helix':
            for i in range(num_points):
                t = (i / num_points) * 8 * math.pi
                r = 0.8 + 0.2 * math.sin(t * 3)

                x = r * math.cos(t)
                y = (i / num_points) * 4 - 2
                z = r * math.sin(t)
                vertices.append([x, y, z])

        elif shape_name == 'klein_bottle':
            for i in range(num_points):
                u = (i / num_points) * 2 * math.pi
                v = ((i * 7) % num_points) / num_points * 2 * math.pi

                # Klein bottle parametric equations
                x = (2 + math.cos(v/2) * math.sin(u) - math.sin(v/2) * math.sin(2*u)) * math.cos(v)
                y = (2 + math.cos(v/2) * math.sin(u) - math.sin(v/2) * math.sin(2*u)) * math.sin(v)
                z = math.sin(v/2) * math.sin(u) + math.cos(v/2) * math.sin(2*u)
                vertices.append([x/3, y/3, z/3])

        elif shape_name == 'mobius':
            for i in range(num_points):
                u = (i / num_points) * 2 * math.pi
                v = ((i * 11) % num_points) / num_points * 0.4 - 0.2

                # Möbius strip equations
                x = (1 + v * math.cos(u/2)) * math.cos(u)
                y = (1 + v * math.cos(u/2)) * math.sin(u)
                z = v * math.sin(u/2)
                vertices.append([x, y, z])

        elif shape_name == 'heart':
            for i in range(num_points):
                t = (i / num_points) * 2 * math.pi

                # 3D heart shape
                x = 16 * math.sin(t)**3
                y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
                z = 5 * math.sin(t * 3) * math.cos(t * 2)
                vertices.append([x/20, y/20, z/20])

        elif shape_name == 'star':
            for i in range(num_points):
                theta = (i / num_points) * 2 * math.pi * 5
                phi = ((i * 7) % num_points) / num_points * math.pi

                # 5-pointed star with depth
                r = 1.0 if (i // (num_points // 10)) % 2 == 0 else 0.5
                x = r * math.sin(phi) * math.cos(theta)
                y = r * math.cos(phi)
                z = r * math.sin(phi) * math.sin(theta)
                vertices.append([x, y, z])

        elif shape_name == 'spiral':
            for i in range(num_points):
                t = (i / num_points) * 8 * math.pi
                r = (i / num_points) * 1.5

                x = r * math.cos(t)
                y = (i / num_points) * 3 - 1.5
                z = r * math.sin(t)
                vertices.append([x, y, z])

        elif shape_name == 'pyramid':
            # Create a square-based pyramid with proper geometry
            base_points = num_points // 5  # 80% for base, 20% for sides

            # Square base points
            base_size = int(math.sqrt(base_points))
            for i in range(base_size):
                for j in range(base_size):
                    if base_size > 1:
                        x = (i / (base_size - 1)) * 2 - 1
                        z = (j / (base_size - 1)) * 2 - 1
                    else:
                        x = z = 0
                    vertices.append([x, -1, z])  # Base at y = -1

            # Pyramid sides connecting to apex
            remaining_points = num_points - (base_size * base_size)
            for i in range(remaining_points):
                # Distribute points on the 4 triangular faces
                face = i % 4
                t = (i // 4) / max(1, remaining_points // 4 - 1)  # Parameter along edge

                if face == 0:  # Front face
                    base_x, base_z = 2 * t - 1, -1
                elif face == 1:  # Right face
                    base_x, base_z = 1, 2 * t - 1
                elif face == 2:  # Back face
                    base_x, base_z = 1 - 2 * t, 1
                else:  # Left face
                    base_x, base_z = -1, 1 - 2 * t

                # Linear interpolation from base to apex
                height_factor = (i % (remaining_points // 4)) / max(1, remaining_points // 4 - 1)
                x = base_x * (1 - height_factor)
                y = -1 + 2 * height_factor  # From base (-1) to apex (1)
                z = base_z * (1 - height_factor)
                vertices.append([x, y, z])

        else:  # Default fallback
            return self.generate_shape('sphere')

        return vertices

    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color space for proper rainbow colors"""
        # Normalize hue to 0-1 range
        h = h % 1.0

        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)

        if i == 0:
            return v, t, p
        elif i == 1:
            return q, v, p
        elif i == 2:
            return p, v, t
        elif i == 3:
            return p, q, v
        elif i == 4:
            return t, p, v
        else:
            return v, p, q

    def render_morphed_shape(self, vertices):
        """Render the morphed shape with enhanced effects"""
        if not vertices:
            return

        if self.color_mode == 'rainbow':
            # Proper rainbow color using HSV to RGB conversion
            hue = self.morph_factor  # 0.0 to 1.0 range for full spectrum
            saturation = 1.0  # Full saturation for vivid colors
            value = 0.9  # Bright but not oversaturated

            r, g, b = self.hsv_to_rgb(hue, saturation, value)
            glColor3f(r, g, b)
        elif self.color_mode == 'blue_white':
            # Blue to white gradient
            intensity = 0.6 + 0.4 * self.morph_factor
            glColor3f(intensity * 0.7, intensity * 0.9, intensity)
        else:
            # Default cyan
            glColor3f(0.3, 0.8, 1.0)

        glPointSize(2.5)
        glBegin(GL_POINTS)
        for vertex in vertices:
            glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

    def render_enhanced_particles(self):
        """Render particles with enhanced effects"""
        if not self.particles:
            return

        glPointSize(self.particle_size)

        for particle in self.particles:
            if particle['life'] > 0:
                # Color based on life and velocity
                life_factor = particle['life']
                velocity_factor = min(1.0, np.linalg.norm([particle['vx'], particle['vy'], particle['vz']]) * 10)

                r = 1.0 * life_factor
                g = 0.8 * life_factor * velocity_factor
                b = 0.2 + 0.6 * velocity_factor
                alpha = life_factor * 0.8

                glColor4f(r, g, b, alpha)

                glBegin(GL_POINTS)
                glVertex3f(particle['x'], particle['y'], particle['z'])
                glEnd()

                # Particle trails if enabled
                if self.particle_trails and 'trail' in particle:
                    glPointSize(1.0)
                    glColor4f(r * 0.5, g * 0.5, b * 0.5, alpha * 0.3)

                    glBegin(GL_POINTS)
                    for trail_point in particle['trail']:
                        glVertex3f(trail_point[0], trail_point[1], trail_point[2])
                    glEnd()

    def update_animation(self):
        """Update animation with enhanced effects"""
        self.rotation += 0.8

        # Update particles with trails
        for particle in self.particles[:]:
            particle['life'] -= 0.015

            # Update position
            old_pos = [particle['x'], particle['y'], particle['z']]
            particle['x'] += particle['vx'] * 0.02
            particle['y'] += particle['vy'] * 0.02
            particle['z'] += particle['vz'] * 0.02

            # Add gravity
            particle['vy'] -= 0.001

            # Add trail point
            if self.particle_trails:
                if 'trail' not in particle:
                    particle['trail'] = []
                particle['trail'].append(old_pos)
                if len(particle['trail']) > 10:
                    particle['trail'].pop(0)

            if particle['life'] <= 0:
                self.particles.remove(particle)

        self.update()

    def set_morph_factor(self, factor):
        """Set morphing factor"""
        self.morph_factor = factor

    def set_shapes(self, shape_a, shape_b):
        """Set the shapes to morph between"""
        self.shape_a = shape_a
        self.shape_b = shape_b

    def set_visual_settings(self, trails=True, color_mode='rainbow', particle_size=6.0, resolution=800):
        """Configure visual settings"""
        self.particle_trails = trails
        self.color_mode = color_mode
        self.particle_size = particle_size
        self.shape_resolution = resolution

    def add_particle_burst(self, note, velocity, burst_type='normal'):
        """Add enhanced particle burst"""
        x_pos = (note - 60) / 30.0

        # Enhanced particle count based on velocity
        base_count = max(2, velocity // 6)
        if burst_type == 'explosion':
            base_count *= 3
        elif burst_type == 'stream':
            base_count = max(15, base_count)

        for _ in range(base_count):
            if burst_type == 'explosion':
                # Explosive burst
                speed = 0.2 + (velocity / 127.0) * 0.3
                vx = (np.random.random() - 0.5) * speed
                vy = np.random.random() * speed
                vz = (np.random.random() - 0.5) * speed
            elif burst_type == 'stream':
                # Upward stream
                vx = (np.random.random() - 0.5) * 0.05
                vy = 0.1 + np.random.random() * 0.15
                vz = (np.random.random() - 0.5) * 0.05
            else:
                # Normal burst
                vx = (np.random.random() - 0.5) * 0.15
                vy = np.random.random() * 0.2
                vz = (np.random.random() - 0.5) * 0.15

            particle = {
                'x': x_pos + (np.random.random() - 0.5) * 0.3,
                'y': (np.random.random() - 0.5) * 0.2,
                'z': (np.random.random() - 0.5) * 0.3,
                'vx': vx,
                'vy': vy,
                'vz': vz,
                'life': 1.5 + np.random.random() * 1.5,
                'trail': []
            }
            self.particles.append(particle)

        logger.info(f"🎆 Enhanced burst: {len(self.particles)} total particles")

class EnhancedMorphingDemo(QMainWindow):
    """Enhanced morphing demo with extended features"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌟 Enhanced Visual Morphing - Extended Shape Library")
        self.setGeometry(100, 100, 1200, 800)

        self.manual_control = False
        self._setup_ui()
        self._setup_midi()

        logger.info("🌟 Enhanced Visual Morphing Demo Ready!")

    def _setup_ui(self):
        """Set up enhanced UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Enhanced morphing visualization (75%)
        self.morph_widget = EnhancedMorphWidget()
        layout.addWidget(self.morph_widget, 75)

        # Enhanced controls (25%)
        controls = self._create_enhanced_controls()
        layout.addWidget(controls, 25)

    def _create_enhanced_controls(self):
        """Create enhanced control panel"""
        controls_frame = QFrame()
        controls_frame.setMaximumWidth(350)
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
        """)

        layout = QVBoxLayout(controls_frame)

        # Enhanced title
        title = QLabel("🌟 ENHANCED MORPHING")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db; padding: 10px;")
        layout.addWidget(title)

        # Extended shape selection
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

        # Enhanced morph control
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

        # Visual effects control
        effects_group = QGroupBox("✨ Visual Effects")
        effects_layout = QVBoxLayout(effects_group)

        self.trails_cb = QCheckBox("Particle Trails")
        self.trails_cb.setChecked(True)
        self.trails_cb.stateChanged.connect(self._update_effects)
        effects_layout.addWidget(self.trails_cb)

        effects_layout.addWidget(QLabel("Color Mode:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(['rainbow', 'blue_white', 'cyan'])
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

        # Particle control
        particle_group = QGroupBox("🎆 Particle Effects")
        particle_layout = QVBoxLayout(particle_group)

        self.explosion_btn = QPushButton("💥 Explosion")
        self.explosion_btn.clicked.connect(lambda: self._create_demo_particles('explosion'))
        particle_layout.addWidget(self.explosion_btn)

        self.stream_btn = QPushButton("🌊 Stream")
        self.stream_btn.clicked.connect(lambda: self._create_demo_particles('stream'))
        particle_layout.addWidget(self.stream_btn)

        layout.addWidget(particle_group)

        # Enhanced status
        status_group = QGroupBox("📊 Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("🌟 Enhanced System Active")
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        self.particle_label = QLabel("Particles: 0")
        self.particle_label.setStyleSheet("color: #f39c12;")
        status_layout.addWidget(self.particle_label)

        layout.addWidget(status_group)

        layout.addStretch()
        return controls_frame

    def _setup_midi(self):
        """Set up MIDI with enhanced particle effects"""
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
                logger.info(f"✅ Enhanced MIDI: {ports[target_port]}")
            else:
                self.status_label.setText("⚠️ No MIDI - Demo Mode")

        except Exception as e:
            logger.error(f"MIDI error: {e}")
            self.status_label.setText("❌ MIDI Error")

    def _enhanced_midi_callback(self, event, data=None):
        """Enhanced MIDI callback with multiple particle types"""
        message, deltatime = event

        if len(message) >= 3:
            status = message[0]

            if (status & 0xF0) in [0x90, 0x80]:  # Note events
                note = message[1]
                velocity = message[2]

                if velocity > 0:
                    # Different particle types based on velocity and note
                    if velocity > 100:
                        burst_type = 'explosion'
                    elif velocity < 40:
                        burst_type = 'stream'
                    else:
                        burst_type = 'normal'

                    self.morph_widget.add_particle_burst(note, velocity, burst_type)
                    self.status_label.setText(f"🎵 Note: {note} ({burst_type})")

            elif (status & 0xF0) == 0xB0:  # CC events
                cc = message[1]
                value = message[2]

                if cc == 1 and not self.manual_control:
                    morph_value = int(value * 100 / 127)
                    self.morph_slider.blockSignals(True)
                    self.morph_slider.setValue(morph_value)
                    self.morph_slider.blockSignals(False)
                    self._update_morph_display(morph_value)

    def _update_shapes(self):
        """Update shapes with logging"""
        shape_a = self.shape_a_combo.currentText()
        shape_b = self.shape_b_combo.currentText()
        self.morph_widget.set_shapes(shape_a, shape_b)
        logger.info(f"🎨 Enhanced shapes: {shape_a} → {shape_b}")

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
        logger.info(f"✨ Effects updated: trails={trails}, color={color_mode}, res={resolution}")

    def _on_morph_changed(self, value):
        """Handle enhanced morph changes"""
        self.manual_control = True
        self._update_morph_display(value)

    def _update_morph_display(self, value):
        """Update enhanced morph display"""
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
        self.particle_label.setText(f"Particles: {len(self.morph_widget.particles)}")

    def _create_demo_particles(self, burst_type):
        """Create demo particle effects"""
        self.morph_widget.add_particle_burst(60, 100, burst_type)
        logger.info(f"🎆 Demo {burst_type} particles created")

def main():
    """Launch enhanced visual morphing demo"""
    app = QApplication(sys.argv)

    window = EnhancedMorphingDemo()
    window.show()

    logger.info("🌟 Enhanced Visual Morphing Demo Started!")
    logger.info("✨ New features:")
    logger.info("   • 10 morphing shapes (sphere, cube, torus, helix, Klein bottle, etc.)")
    logger.info("   • Rainbow and gradient color modes")
    logger.info("   • Particle trails and enhanced effects")
    logger.info("   • Adjustable resolution (200-2000 points)")
    logger.info("   • Multiple particle burst types")
    logger.info("   • Enhanced MIDI responsiveness")

    return app.exec()

if __name__ == "__main__":
    main()