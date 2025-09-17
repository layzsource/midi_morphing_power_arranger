#!/usr/bin/env python3
"""
Minimal Working MIDI Morphing System
Simple, functional morphing without the complex broken foundation
"""

import sys
import math
import logging
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import rtmidi

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleShape:
    """Simple shape generator with consistent vertex counts"""

    def __init__(self, resolution=32):
        self.resolution = resolution
        self.vertex_count = resolution * resolution

    def generate_sphere(self):
        """Generate sphere with consistent vertex count"""
        vertices = []
        for i in range(self.resolution):
            theta = math.pi * i / (self.resolution - 1)
            for j in range(self.resolution):
                phi = 2 * math.pi * j / (self.resolution - 1)
                x = math.sin(theta) * math.cos(phi)
                y = math.cos(theta)
                z = math.sin(theta) * math.sin(phi)
                vertices.append([x, y, z])
        return np.array(vertices, dtype=np.float32)

    def generate_cube(self):
        """Generate cube vertices"""
        vertices = []
        # Generate cube surface points
        for i in range(self.resolution):
            for j in range(self.resolution):
                # Map to [-1, 1] range
                u = 2.0 * i / (self.resolution - 1) - 1.0
                v = 2.0 * j / (self.resolution - 1) - 1.0

                # Add points on each face of the cube
                if len(vertices) < self.vertex_count:
                    face = len(vertices) % 6
                    if face == 0:    # Front
                        vertices.append([u, v, 1.0])
                    elif face == 1:  # Back
                        vertices.append([u, v, -1.0])
                    elif face == 2:  # Right
                        vertices.append([1.0, u, v])
                    elif face == 3:  # Left
                        vertices.append([-1.0, u, v])
                    elif face == 4:  # Top
                        vertices.append([u, 1.0, v])
                    else:            # Bottom
                        vertices.append([u, -1.0, v])

        # Ensure exact vertex count
        while len(vertices) < self.vertex_count:
            vertices.append(vertices[-1])
        return np.array(vertices[:self.vertex_count], dtype=np.float32)

    def generate_torus(self):
        """Generate torus vertices"""
        vertices = []
        major_r = 1.0
        minor_r = 0.3

        for i in range(self.resolution):
            theta = 2 * math.pi * i / self.resolution
            for j in range(self.resolution):
                phi = 2 * math.pi * j / self.resolution
                x = (major_r + minor_r * math.cos(phi)) * math.cos(theta)
                y = minor_r * math.sin(phi)
                z = (major_r + minor_r * math.cos(phi)) * math.sin(theta)
                vertices.append([x, y, z])

        # Ensure exact vertex count
        while len(vertices) < self.vertex_count:
            vertices.append(vertices[-1])
        return np.array(vertices[:self.vertex_count], dtype=np.float32)

class SimpleMorphEngine:
    """Simple morphing engine with consistent vertex handling"""

    def __init__(self, resolution=32):
        self.shape_gen = SimpleShape(resolution)
        self.morph_factor = 0.0
        self.current_shape_a = 'sphere'
        self.current_shape_b = 'cube'

        # Generate shapes
        self.shapes = {
            'sphere': self.shape_gen.generate_sphere(),
            'cube': self.shape_gen.generate_cube(),
            'torus': self.shape_gen.generate_torus()
        }

        logger.info(f"Generated shapes with {self.shape_gen.vertex_count} vertices each")

    def get_morphed_vertices(self):
        """Get morphed vertices between current shapes"""
        shape_a = self.shapes.get(self.current_shape_a, self.shapes['sphere'])
        shape_b = self.shapes.get(self.current_shape_b, self.shapes['cube'])

        # Simple linear interpolation
        morphed = (1.0 - self.morph_factor) * shape_a + self.morph_factor * shape_b
        return morphed

class SimpleGLWidget(QOpenGLWidget):
    """Simple OpenGL widget for rendering morphed shapes"""

    def __init__(self, morph_engine):
        super().__init__()
        self.morph_engine = morph_engine
        self.rotation = 0.0

        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_rotation)
        self.timer.start(16)  # ~60 FPS

    def _update_rotation(self):
        self.rotation += 1.0
        self.update()

    def initializeGL(self):
        """Initialize OpenGL settings"""
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glPointSize(2.0)

    def resizeGL(self, width, height):
        """Handle window resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Simple perspective
        glFrustum(-1.0, 1.0, -1.0, 1.0, 2.0, 10.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the morphed shape"""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Set up camera
            glTranslatef(0.0, 0.0, -5.0)
            glRotatef(self.rotation, 1.0, 1.0, 0.0)

            # Get morphed vertices
            vertices = self.morph_engine.get_morphed_vertices()

            # Render as points
            glColor3f(1.0, 0.8, 0.2)  # Golden color
            glBegin(GL_POINTS)
            for vertex in vertices:
                glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()

        except Exception as e:
            logger.error(f"Render error: {e}")

class SimpleMIDI:
    """Simple MIDI handler for testing"""

    def __init__(self, note_callback=None, cc_callback=None):
        self.note_callback = note_callback
        self.cc_callback = cc_callback
        self.midi_in = None

        try:
            self.midi_in = rtmidi.MidiIn()
            ports = self.midi_in.get_ports()

            # Find MPK mini or any MIDI device
            for i, port in enumerate(ports):
                logger.info(f"MIDI port {i}: {port}")
                if 'MPK' in port or 'mini' in port:
                    self.midi_in.open_port(i)
                    self.midi_in.set_callback(self._midi_callback)
                    logger.info(f"Connected to: {port}")
                    return

            # If no MPK found, use first available port
            if ports:
                self.midi_in.open_port(0)
                self.midi_in.set_callback(self._midi_callback)
                logger.info(f"Connected to: {ports[0]}")

        except Exception as e:
            logger.error(f"MIDI init error: {e}")

    def _midi_callback(self, event, data=None):
        """Handle MIDI messages"""
        message, deltatime = event

        if len(message) >= 3:
            status = message[0]

            # Note events
            if (status & 0xF0) in [0x90, 0x80]:  # Note on/off
                note = message[1]
                velocity = message[2]
                if self.note_callback and velocity > 0:  # Note on
                    self.note_callback(note, velocity)
                    logger.info(f"Note: {note}, Velocity: {velocity}")

            # CC events
            elif (status & 0xF0) == 0xB0:  # Control change
                cc = message[1]
                value = message[2]
                if self.cc_callback:
                    self.cc_callback(cc, value)
                if cc == 1:  # Mod wheel
                    logger.info(f"CC1 (Mod): {value}")

class SimpleMainWindow(QMainWindow):
    """Simple main window with working morphing"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Working Morphing System")
        self.setGeometry(100, 100, 1000, 700)

        # Initialize systems
        self.morph_engine = SimpleMorphEngine(resolution=32)
        self.manual_control = False

        self._setup_ui()
        self._setup_midi()

        logger.info("Simple morphing system initialized!")

    def _setup_ui(self):
        """Set up the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # OpenGL widget (70% of space)
        self.gl_widget = SimpleGLWidget(self.morph_engine)
        layout.addWidget(self.gl_widget, 7)

        # Controls panel (30% of space)
        controls = self._create_controls()
        layout.addWidget(controls, 3)

    def _create_controls(self):
        """Create control panel"""
        controls_frame = QFrame()
        controls_frame.setMaximumWidth(300)
        controls_frame.setStyleSheet("background-color: #2a2a2a; color: white; padding: 10px;")

        layout = QVBoxLayout(controls_frame)

        # Title
        title = QLabel("SIMPLE MORPHING")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Shape selection
        shape_group = QGroupBox("Shape Selection")
        shape_layout = QVBoxLayout(shape_group)

        # Shape A
        shape_layout.addWidget(QLabel("Shape A:"))
        self.shape_a_combo = QComboBox()
        self.shape_a_combo.addItems(['sphere', 'cube', 'torus'])
        self.shape_a_combo.currentTextChanged.connect(self._on_shape_a_changed)
        shape_layout.addWidget(self.shape_a_combo)

        # Shape B
        shape_layout.addWidget(QLabel("Shape B:"))
        self.shape_b_combo = QComboBox()
        self.shape_b_combo.addItems(['sphere', 'cube', 'torus'])
        self.shape_b_combo.setCurrentText('cube')
        self.shape_b_combo.currentTextChanged.connect(self._on_shape_b_changed)
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

        self.morph_label = QLabel("0%")
        self.morph_label.setAlignment(Qt.AlignCenter)
        morph_layout.addWidget(self.morph_label)

        # Reset button
        reset_btn = QPushButton("Enable MIDI Control")
        reset_btn.clicked.connect(self._reset_manual_control)
        morph_layout.addWidget(reset_btn)

        layout.addWidget(morph_group)

        # Status
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_group)

        layout.addStretch()

        return controls_frame

    def _setup_midi(self):
        """Set up MIDI handling"""
        self.midi = SimpleMIDI(
            note_callback=self._on_midi_note,
            cc_callback=self._on_midi_cc
        )

    def _on_shape_a_changed(self, shape):
        """Handle shape A selection"""
        self.morph_engine.current_shape_a = shape
        logger.info(f"Shape A: {shape}")

    def _on_shape_b_changed(self, shape):
        """Handle shape B selection"""
        self.morph_engine.current_shape_b = shape
        logger.info(f"Shape B: {shape}")

    def _on_morph_changed(self, value):
        """Handle morph slider change"""
        self.manual_control = True
        morph_factor = value / 100.0
        self.morph_engine.morph_factor = morph_factor
        self.morph_label.setText(f"{value}%")
        self.status_label.setText("Manual Control Active")
        logger.info(f"Manual morph: {morph_factor:.2f}")

    def _reset_manual_control(self):
        """Reset to allow MIDI control"""
        self.manual_control = False
        self.status_label.setText("MIDI Control Enabled")
        logger.info("MIDI control restored")

    def _on_midi_note(self, note, velocity):
        """Handle MIDI note events"""
        logger.info(f"🎵 MIDI Note: {note}, Velocity: {velocity}")
        self.status_label.setText(f"Note: {note} ({velocity})")
        # TODO: Add particle effects here

    def _on_midi_cc(self, cc, value):
        """Handle MIDI CC events"""
        if cc == 1 and not self.manual_control:  # Mod wheel
            morph_factor = value / 127.0
            self.morph_engine.morph_factor = morph_factor

            # Update slider without triggering manual mode
            self.morph_slider.blockSignals(True)
            self.morph_slider.setValue(int(value * 100 / 127))
            self.morph_label.setText(f"{int(value * 100 / 127)}%")
            self.morph_slider.blockSignals(False)

            self.status_label.setText(f"MIDI Morph: {int(value * 100 / 127)}%")

def main():
    app = QApplication(sys.argv)

    # Create and show main window
    window = SimpleMainWindow()
    window.show()

    logger.info("🎯 Simple morphing system started!")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()