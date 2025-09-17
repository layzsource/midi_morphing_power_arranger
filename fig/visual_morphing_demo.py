#!/usr/bin/env python3
"""
Visual Morphing Demo - Guaranteed Visible Morphing
This ensures you can see the morphing shapes clearly with working visual feedback
"""

import sys
import math
import logging
import numpy as np
import time
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QBrush
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import rtmidi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVisualMorphWidget(QOpenGLWidget):
    """Simple morphing visualization that guarantees visible output"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.morph_factor = 0.0
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.rotation = 0.0
        self.particles = []

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60 FPS

    def initializeGL(self):
        """Initialize OpenGL with guaranteed settings"""
        glClearColor(0.05, 0.05, 0.15, 1.0)  # Dark blue background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(3.0)
        logger.info("✅ OpenGL initialized for visual morphing")

    def resizeGL(self, width, height):
        """Handle resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        # Simple perspective projection
        aspect = width / height if height > 0 else 1
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 10.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the morphing shapes"""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Set up camera
            glTranslatef(0.0, 0.0, -5.0)
            glRotatef(self.rotation, 1.0, 1.0, 0.0)

            # Generate and render morphed shape
            vertices = self.generate_morphed_shape()

            # Render morphed shape
            glColor3f(0.8, 0.9, 1.0)  # Light blue
            glBegin(GL_POINTS)
            for vertex in vertices:
                glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()

            # Render particles
            self.render_particles()

        except Exception as e:
            logger.error(f"Render error: {e}")

    def generate_morphed_shape(self):
        """Generate vertices for morphed shape"""
        # Create base shapes
        vertices_a = self.generate_shape(self.shape_a)
        vertices_b = self.generate_shape(self.shape_b)

        # Morph between them
        morphed = []
        for i in range(min(len(vertices_a), len(vertices_b))):
            va = vertices_a[i]
            vb = vertices_b[i]

            # Linear interpolation
            mx = va[0] * (1 - self.morph_factor) + vb[0] * self.morph_factor
            my = va[1] * (1 - self.morph_factor) + vb[1] * self.morph_factor
            mz = va[2] * (1 - self.morph_factor) + vb[2] * self.morph_factor

            morphed.append([mx, my, mz])

        return morphed

    def generate_shape(self, shape_name):
        """Generate vertices for a specific shape"""
        vertices = []
        num_points = 500  # Consistent number of points

        if shape_name == 'sphere':
            for i in range(num_points):
                theta = (i / num_points) * 2 * math.pi
                phi = ((i * 7) % num_points) / num_points * math.pi

                x = math.sin(phi) * math.cos(theta)
                y = math.cos(phi)
                z = math.sin(phi) * math.sin(theta)
                vertices.append([x, y, z])

        elif shape_name == 'cube':
            for i in range(num_points):
                # Distribute points on cube faces
                face = i % 6
                u = ((i // 6) % 10) / 10 * 2 - 1
                v = ((i // 60) % 10) / 10 * 2 - 1

                if face == 0:    # Front
                    vertices.append([u, v, 1])
                elif face == 1:  # Back
                    vertices.append([u, v, -1])
                elif face == 2:  # Right
                    vertices.append([1, u, v])
                elif face == 3:  # Left
                    vertices.append([-1, u, v])
                elif face == 4:  # Top
                    vertices.append([u, 1, v])
                else:            # Bottom
                    vertices.append([u, -1, v])

        elif shape_name == 'torus':
            for i in range(num_points):
                theta = (i / num_points) * 2 * math.pi * 3
                phi = ((i * 13) % num_points) / num_points * 2 * math.pi

                R = 1.0  # Major radius
                r = 0.3  # Minor radius

                x = (R + r * math.cos(phi)) * math.cos(theta)
                y = r * math.sin(phi)
                z = (R + r * math.cos(phi)) * math.sin(theta)
                vertices.append([x, y, z])

        elif shape_name == 'cylinder':
            for i in range(num_points):
                if i < num_points // 2:
                    # Curved surface
                    theta = (i / (num_points // 2)) * 2 * math.pi
                    height = ((i * 7) % (num_points // 2)) / (num_points // 2) * 2 - 1

                    x = math.cos(theta)
                    y = height
                    z = math.sin(theta)
                else:
                    # End caps
                    idx = i - num_points // 2
                    theta = (idx / (num_points // 2)) * 2 * math.pi
                    r = (idx % 10) / 10

                    x = r * math.cos(theta)
                    y = 1 if idx < (num_points // 4) else -1
                    z = r * math.sin(theta)

                vertices.append([x, y, z])

        else:  # Default to sphere
            return self.generate_shape('sphere')

        return vertices

    def render_particles(self):
        """Render particle effects"""
        glColor3f(1.0, 0.8, 0.2)  # Golden particles
        glPointSize(6.0)

        glBegin(GL_POINTS)
        for particle in self.particles:
            if particle['life'] > 0:
                glVertex3f(particle['x'], particle['y'], particle['z'])
        glEnd()

    def update_animation(self):
        """Update animation state"""
        self.rotation += 1.0

        # Update particles
        for particle in self.particles[:]:
            particle['life'] -= 0.02
            particle['x'] += particle['vx'] * 0.02
            particle['y'] += particle['vy'] * 0.02
            particle['z'] += particle['vz'] * 0.02

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

    def add_particle_burst(self, note, velocity):
        """Add particle burst for MIDI note"""
        # Position based on note
        x_pos = (note - 60) / 60.0  # Center around middle C

        # Create particles
        for _ in range(max(1, velocity // 8)):
            particle = {
                'x': x_pos,
                'y': 0,
                'z': 0,
                'vx': (np.random.random() - 0.5) * 0.1,
                'vy': np.random.random() * 0.15,
                'vz': (np.random.random() - 0.5) * 0.1,
                'life': 1.0 + np.random.random()
            }
            self.particles.append(particle)

        logger.info(f"🎆 Particle burst: {len(self.particles)} total particles")

class VisualMorphingDemo(QMainWindow):
    """Main window with guaranteed visual morphing"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎨 Visual Morphing Demo - Guaranteed Visible!")
        self.setGeometry(100, 100, 1000, 700)

        self.manual_control = False
        self._setup_ui()
        self._setup_midi()

        logger.info("🎨 Visual Morphing Demo Ready!")

    def _setup_ui(self):
        """Set up UI with visual morphing widget"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Morphing visualization (70%)
        self.morph_widget = SimpleVisualMorphWidget()
        layout.addWidget(self.morph_widget, 7)

        # Controls (30%)
        controls = self._create_controls()
        layout.addWidget(controls, 3)

    def _create_controls(self):
        """Create control panel"""
        controls_frame = QFrame()
        controls_frame.setMaximumWidth(300)
        controls_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QComboBox {
                background-color: #34495e;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: white;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #66e, stop: 1 #bbf);
                border: 1px solid #777;
                height: 10px;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(controls_frame)

        # Title
        title = QLabel("🎨 VISUAL MORPHING")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Shape selection
        shape_group = QGroupBox("Shape Selection")
        shape_layout = QVBoxLayout(shape_group)

        # Shape A
        shape_layout.addWidget(QLabel("Shape A:"))
        self.shape_a_combo = QComboBox()
        self.shape_a_combo.addItems(['sphere', 'cube', 'torus', 'cylinder'])
        self.shape_a_combo.currentTextChanged.connect(self._update_shapes)
        shape_layout.addWidget(self.shape_a_combo)

        # Shape B
        shape_layout.addWidget(QLabel("Shape B:"))
        self.shape_b_combo = QComboBox()
        self.shape_b_combo.addItems(['sphere', 'cube', 'torus', 'cylinder'])
        self.shape_b_combo.setCurrentText('cube')
        self.shape_b_combo.currentTextChanged.connect(self._update_shapes)
        shape_layout.addWidget(self.shape_b_combo)

        layout.addWidget(shape_group)

        # Morph control
        morph_group = QGroupBox("Morph Control")
        morph_layout = QVBoxLayout(morph_group)

        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        self.morph_slider.valueChanged.connect(self._on_morph_changed)
        morph_layout.addWidget(self.morph_slider)

        self.morph_label = QLabel("0% (Sphere)")
        self.morph_label.setAlignment(Qt.AlignCenter)
        morph_layout.addWidget(self.morph_label)

        # Demo button
        demo_btn = QPushButton("🎭 Auto Demo")
        demo_btn.clicked.connect(self._start_demo)
        morph_layout.addWidget(demo_btn)

        layout.addWidget(morph_group)

        # Status
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("🎯 Visual Rendering Active")
        self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        status_layout.addWidget(self.status_label)

        self.particle_label = QLabel("Particles: 0")
        status_layout.addWidget(self.particle_label)

        layout.addWidget(status_group)

        # Instructions
        instructions = QLabel("""
🎮 CONTROLS:
• Use sliders to morph shapes
• Play MIDI for particle bursts
• Change shapes in dropdowns
• Watch the morphing happen!
        """)
        instructions.setStyleSheet("font-size: 10px; color: #bdc3c7;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        layout.addStretch()

        return controls_frame

    def _setup_midi(self):
        """Set up MIDI handling"""
        try:
            self.midi = rtmidi.MidiIn()
            ports = self.midi.get_ports()

            if ports:
                # Connect to MPK Mini or first available
                target_port = 0
                for i, port in enumerate(ports):
                    if 'MPK' in port or 'mini' in port:
                        target_port = i
                        break

                self.midi.open_port(target_port)
                self.midi.set_callback(self._midi_callback)
                self.status_label.setText(f"🎹 MIDI: {ports[target_port][:15]}...")
                logger.info(f"✅ MIDI connected: {ports[target_port]}")
            else:
                self.status_label.setText("⚠️ No MIDI - Use sliders")

        except Exception as e:
            logger.error(f"MIDI error: {e}")
            self.status_label.setText("❌ MIDI Error - Use sliders")

    def _midi_callback(self, event, data=None):
        """Handle MIDI events"""
        message, deltatime = event

        if len(message) >= 3:
            status = message[0]

            # Note events
            if (status & 0xF0) in [0x90, 0x80]:  # Note on/off
                note = message[1]
                velocity = message[2]

                if velocity > 0:  # Note on
                    self.morph_widget.add_particle_burst(note, velocity)
                    self.status_label.setText(f"🎵 Note: {note} (V:{velocity})")
                    logger.info(f"🎵 MIDI Note: {note}, Velocity: {velocity}")

            # CC events
            elif (status & 0xF0) == 0xB0:  # Control change
                cc = message[1]
                value = message[2]

                if cc == 1 and not self.manual_control:  # Mod wheel
                    morph_value = int(value * 100 / 127)
                    self.morph_slider.blockSignals(True)
                    self.morph_slider.setValue(morph_value)
                    self.morph_slider.blockSignals(False)

                    self._update_morph_display(morph_value)
                    self.status_label.setText(f"🎹 MIDI Morph: {morph_value}%")

    def _on_morph_changed(self, value):
        """Handle morph slider changes"""
        self.manual_control = True
        self._update_morph_display(value)
        self.status_label.setText(f"🎮 Manual: {value}%")

    def _update_morph_display(self, value):
        """Update morph display"""
        morph_factor = value / 100.0
        self.morph_widget.set_morph_factor(morph_factor)

        shape_a = self.shape_a_combo.currentText()
        shape_b = self.shape_b_combo.currentText()

        if value < 10:
            display_text = f"{value}% ({shape_a.title()})"
        elif value > 90:
            display_text = f"{value}% ({shape_b.title()})"
        else:
            display_text = f"{value}% (Morphing)"

        self.morph_label.setText(display_text)

        # Update particle count
        particle_count = len(self.morph_widget.particles)
        self.particle_label.setText(f"Particles: {particle_count}")

    def _update_shapes(self):
        """Update the shapes being morphed"""
        shape_a = self.shape_a_combo.currentText()
        shape_b = self.shape_b_combo.currentText()
        self.morph_widget.set_shapes(shape_a, shape_b)
        logger.info(f"🎨 Shapes updated: {shape_a} → {shape_b}")

    def _start_demo(self):
        """Start automatic demo"""
        self.manual_control = False

        # Create demo animation
        self.demo_timer = QTimer()
        self.demo_step = 0

        def demo_step():
            self.demo_step += 1
            value = int(50 + 45 * math.sin(self.demo_step * 0.1))

            self.morph_slider.blockSignals(True)
            self.morph_slider.setValue(value)
            self.morph_slider.blockSignals(False)

            self._update_morph_display(value)
            self.status_label.setText(f"🎭 Demo Mode: {value}%")

            # Add random particles
            if self.demo_step % 30 == 0:
                note = 60 + (self.demo_step % 24)
                velocity = 80 + int(20 * math.sin(self.demo_step * 0.2))
                self.morph_widget.add_particle_burst(note, velocity)

        self.demo_timer.timeout.connect(demo_step)
        self.demo_timer.start(100)  # 10 FPS demo

        logger.info("🎭 Demo mode started")

def main():
    """Launch visual morphing demo"""
    app = QApplication(sys.argv)

    # Create and show the demo window
    window = VisualMorphingDemo()
    window.show()

    logger.info("🎨 Visual Morphing Demo Started!")
    logger.info("✅ You should now see:")
    logger.info("   • Rotating morphing shapes (blue points)")
    logger.info("   • Morphing controls on the right")
    logger.info("   • Particle effects when playing MIDI")
    logger.info("   • Real-time visual feedback")

    return app.exec()

if __name__ == "__main__":
    main()