#!/usr/bin/env python3
"""
MMPA Light Version - Optimized for Everyday Use
===============================================

Lightweight audio-visual morphing system with:
- Basic geometric morphing (6 core shapes)
- MIDI integration (MPK Mini support)
- Simplified audio processing
- Performance-optimized for low-end systems
- Essential controls only

Target: 30 FPS on basic hardware
CPU Load: Minimal
"""

import sys
import math
import logging
import numpy as np
import time
from typing import Dict, List, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox,
    QCheckBox, QSpinBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

# Import MMPA framework (light components only)
from mmpa_signal_framework import MMPASignalEngine, SignalType, SignalFeatures
from mmpa_midi_processor import MIDISignalProcessor

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduced logging
logger = logging.getLogger(__name__)

class LightMorphWidget(QOpenGLWidget):
    """Lightweight morphing widget - optimized for performance"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Basic morphing settings
        self.morph_factor = 0.0
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.rotation = 0.0

        # Performance-optimized settings
        self.shape_resolution = 200  # Lower resolution for performance
        self.color_mode = 'rainbow'

        # MIDI-only processing (no heavy audio intelligence)
        self.mmpa_engine = MMPASignalEngine()
        midi_processor = MIDISignalProcessor("MPK")
        self.mmpa_engine.register_processor(midi_processor)
        self.mmpa_engine.register_form_callback(self._on_signal_to_form)
        self.mmpa_engine.start_engine()

        # Performance timer (30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)  # 30 FPS for performance

        logger.warning("⚡ MMPA Light Version initialized")

    def _on_signal_to_form(self, signal_type, features, events, form_params):
        """Lightweight signal processing"""
        if 'morph_factor' in form_params:
            self.morph_factor = form_params['morph_factor']

    def initializeGL(self):
        """Basic OpenGL setup"""
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        """Handle resize"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height if height > 0 else 1
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Lightweight rendering"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0.0, 0.0, -6.0)
        glRotatef(self.rotation, 1.0, 1.0, 0.0)

        # Simple morphing between two shapes
        vertices = self.generate_morphed_shape()
        self.render_shape(vertices)

    def generate_morphed_shape(self):
        """Generate basic morphed shape"""
        vertices_a = self.generate_shape(self.shape_a)
        vertices_b = self.generate_shape(self.shape_b)

        min_len = min(len(vertices_a), len(vertices_b))
        vertices_a = vertices_a[:min_len]
        vertices_b = vertices_b[:min_len]

        morphed = []
        for i in range(min_len):
            va, vb = vertices_a[i], vertices_b[i]
            mx = va[0] * (1 - self.morph_factor) + vb[0] * self.morph_factor
            my = va[1] * (1 - self.morph_factor) + vb[1] * self.morph_factor
            mz = va[2] * (1 - self.morph_factor) + vb[2] * self.morph_factor
            morphed.append([mx, my, mz])

        return morphed

    def generate_shape(self, shape_name):
        """Generate basic shapes (6 core shapes only)"""
        vertices = []
        num_points = self.shape_resolution

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
                face = i % 6
                u = (i // 6) / max(1, num_points // 6) * 2 - 1
                v = ((i * 3) % (num_points // 6)) / max(1, num_points // 6) * 2 - 1

                if face == 0:    vertices.append([u, v, 1.0])
                elif face == 1:  vertices.append([u, v, -1.0])
                elif face == 2:  vertices.append([1.0, u, v])
                elif face == 3:  vertices.append([-1.0, u, v])
                elif face == 4:  vertices.append([u, 1.0, v])
                else:            vertices.append([u, -1.0, v])

        elif shape_name == 'torus':
            for i in range(num_points):
                theta = (i / num_points) * 2 * math.pi * 4
                phi = ((i * 13) % num_points) / num_points * 2 * math.pi
                R, r = 1.0, 0.4
                x = (R + r * math.cos(phi)) * math.cos(theta)
                y = r * math.sin(phi)
                z = (R + r * math.cos(phi)) * math.sin(theta)
                vertices.append([x, y, z])

        elif shape_name == 'pyramid':
            # Simple pyramid
            for i in range(num_points):
                if i < num_points // 2:
                    # Base
                    angle = (i / (num_points // 2)) * 2 * math.pi
                    x = math.cos(angle)
                    z = math.sin(angle)
                    vertices.append([x, -1.0, z])
                else:
                    # Sides to apex
                    vertices.append([0.0, 1.0, 0.0])

        elif shape_name == 'spiral':
            for i in range(num_points):
                t = (i / num_points) * 6 * math.pi
                radius = 0.5 + 0.5 * (i / num_points)
                x = radius * math.cos(t)
                y = (i / num_points) * 2 - 1
                z = radius * math.sin(t)
                vertices.append([x, y, z])

        elif shape_name == 'star':
            for i in range(num_points):
                theta = (i / num_points) * 2 * math.pi
                phi = ((i * 5) % num_points) / num_points * math.pi
                radius = 0.5 + 0.5 * math.sin(phi * 5)
                x = radius * math.sin(phi) * math.cos(theta)
                y = radius * math.cos(phi)
                z = radius * math.sin(phi) * math.sin(theta)
                vertices.append([x, y, z])
        else:
            return self.generate_shape('sphere')

        return vertices[:num_points]

    def render_shape(self, vertices):
        """Simple shape rendering"""
        if not vertices:
            return

        # Simple rainbow coloring
        hue = self.morph_factor
        r = 0.5 + 0.5 * math.sin(hue * math.pi * 2)
        g = 0.5 + 0.5 * math.sin((hue + 0.33) * math.pi * 2)
        b = 0.5 + 0.5 * math.sin((hue + 0.67) * math.pi * 2)
        glColor3f(r, g, b)

        glPointSize(3.0)
        glBegin(GL_POINTS)
        for vertex in vertices:
            glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

    def update_animation(self):
        """Simple animation update"""
        self.rotation += 1.0
        self.update()

    def set_shapes(self, shape_a, shape_b):
        """Set morphing shapes"""
        self.shape_a = shape_a
        self.shape_b = shape_b

class MMPALightDemo(QMainWindow):
    """MMPA Light Version - Simplified UI"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ MMPA Light - Audio-Visual Morphing (Performance Optimized)")
        self.setGeometry(100, 100, 1000, 700)

        self._setup_ui()
        logger.warning("⚡ MMPA Light Version Ready!")

    def _setup_ui(self):
        """Setup simplified UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Morphing visualization (80%)
        self.morph_widget = LightMorphWidget()
        layout.addWidget(self.morph_widget, 80)

        # Simple controls (20%)
        controls = self._create_controls()
        layout.addWidget(controls, 20)

    def _create_controls(self):
        """Create simplified control panel"""
        controls_frame = QFrame()
        controls_frame.setMaximumWidth(250)
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
            }
        """)

        layout = QVBoxLayout(controls_frame)

        # Basic shape selection
        shape_group = QGroupBox("🔷 Basic Shapes")
        shape_layout = QVBoxLayout(shape_group)

        shapes = ['sphere', 'cube', 'torus', 'pyramid', 'spiral', 'star']

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

        # MIDI controls
        midi_group = QGroupBox("🎹 MIDI Control")
        midi_layout = QVBoxLayout(midi_group)

        midi_layout.addWidget(QLabel("Connect MPK Mini and play!"))
        self.midi_status = QLabel("Status: Ready")
        self.midi_status.setStyleSheet("color: #2ecc71;")
        midi_layout.addWidget(self.midi_status)

        layout.addWidget(midi_group)

        # Performance info
        perf_group = QGroupBox("⚡ Performance")
        perf_layout = QVBoxLayout(perf_group)

        perf_layout.addWidget(QLabel("Target: 30 FPS"))
        perf_layout.addWidget(QLabel("Resolution: 200 points"))
        perf_layout.addWidget(QLabel("CPU: Minimal"))

        layout.addWidget(perf_group)

        layout.addStretch()
        return controls_frame

    def _update_shapes(self):
        """Update morphing shapes"""
        shape_a = self.shape_a_combo.currentText()
        shape_b = self.shape_b_combo.currentText()
        self.morph_widget.set_shapes(shape_a, shape_b)

def main():
    """Run MMPA Light Version"""
    app = QApplication(sys.argv)
    window = MMPALightDemo()
    window.show()

    print("🚀 MMPA Light Version")
    print("====================")
    print("✅ Optimized for everyday use")
    print("✅ 30 FPS performance target")
    print("✅ Basic shapes + MIDI control")
    print("✅ Minimal CPU usage")
    print("\n🎹 Connect MPK Mini and start playing!")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()