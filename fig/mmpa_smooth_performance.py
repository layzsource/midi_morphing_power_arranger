#!/usr/bin/env python3
"""
MMPA Smooth Performance Version
Optimized for buttery smooth 60fps audio-reactive visualization
"""

import sys
import math
import time
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

# Lightweight logging
logging.basicConfig(level=logging.WARNING)  # Reduced logging
logger = logging.getLogger(__name__)

class SmoothAudioProcessor:
    """Lightweight audio processor focused on performance"""

    def __init__(self):
        self.sample_rate = 44100
        self.buffer_size = 1024
        self.audio_stream = None

        # Simple audio features (no ML)
        self.amplitude = 0.0
        self.bass_energy = 0.0
        self.mid_energy = 0.0
        self.treble_energy = 0.0

        # Smoothing for stable visuals
        self.smoothing_factor = 0.3

        logger.info("🎵 Lightweight Audio Processor initialized")

    def process_audio(self, data):
        """Process audio with simple, fast analysis"""
        if data is None or len(data) == 0:
            return

        # Simple RMS amplitude
        rms = np.sqrt(np.mean(data**2))

        # Simple frequency analysis using FFT
        fft = np.fft.rfft(data)
        freqs = np.fft.rfftfreq(len(data), 1/self.sample_rate)
        magnitudes = np.abs(fft)

        # Basic frequency bands
        bass_mask = (freqs >= 20) & (freqs <= 200)
        mid_mask = (freqs >= 200) & (freqs <= 2000)
        treble_mask = (freqs >= 2000) & (freqs <= 8000)

        bass = np.mean(magnitudes[bass_mask]) if np.any(bass_mask) else 0
        mid = np.mean(magnitudes[mid_mask]) if np.any(mid_mask) else 0
        treble = np.mean(magnitudes[treble_mask]) if np.any(treble_mask) else 0

        # Smooth the values for stable visuals
        self.amplitude = self._smooth(self.amplitude, rms)
        self.bass_energy = self._smooth(self.bass_energy, bass)
        self.mid_energy = self._smooth(self.mid_energy, mid)
        self.treble_energy = self._smooth(self.treble_energy, treble)

    def _smooth(self, old_value, new_value):
        """Apply smoothing to prevent jitter"""
        return old_value * (1 - self.smoothing_factor) + new_value * self.smoothing_factor


class SmoothMorphWidget(QOpenGLWidget):
    """Ultra-smooth morphing widget optimized for performance"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Core parameters
        self.morph_factor = 0.0
        self.rotation = 0.0
        self.particles = []

        # Audio-reactive parameters
        self.audio_processor = SmoothAudioProcessor()
        self.amplitude = 0.0
        self.bass = 0.0
        self.mid = 0.0
        self.treble = 0.0

        # Color system (simplified)
        self.base_hue = 0.5
        self.saturation = 0.8
        self.brightness = 1.0

        # Performance settings
        self.max_particles = 200  # Reduced from 800
        self.target_fps = 30      # Reduced from 60 for stability

        # Animation timing
        self.last_time = time.time()

        logger.info("🎨 Smooth Morph Widget initialized")

    def initializeGL(self):
        """Initialize OpenGL with minimal overhead"""
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPointSize(3.0)

    def resizeGL(self, width, height):
        """Handle resize efficiently"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = width / height if height > 0 else 1
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Smooth, efficient rendering"""
        try:
            # Update timing
            current_time = time.time()
            dt = current_time - self.last_time
            self.last_time = current_time

            # Update animation
            self.rotation += 30.0 * dt  # 30 degrees per second
            self.morph_factor = 0.5 + 0.3 * math.sin(current_time * 2)

            # Clear and setup
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Simple camera
            glTranslatef(0.0, 0.0, -4.0)
            glRotatef(self.rotation * 0.5, 1.0, 1.0, 0.0)

            # Generate audio-reactive color
            hue = (self.base_hue + self.treble * 0.3) % 1.0
            color_intensity = 0.5 + self.amplitude * 0.5

            # Render simple morphing shape
            self._render_smooth_morph(color_intensity, hue)

            # Render lightweight particles
            self._update_particles()
            self._render_particles()

        except Exception as e:
            logger.error(f"Render error: {e}")

    def _render_smooth_morph(self, intensity, hue):
        """Render smooth morphing geometry"""
        # Convert HSV to RGB
        h = hue * 6.0
        c = intensity * self.saturation
        x = c * (1 - abs((h % 2) - 1))

        if h < 1:
            r, g, b = c, x, 0
        elif h < 2:
            r, g, b = x, c, 0
        elif h < 3:
            r, g, b = 0, c, x
        elif h < 4:
            r, g, b = 0, x, c
        elif h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x

        glColor3f(r, g, b)

        # Simple sphere with audio-reactive deformation
        glBegin(GL_TRIANGLES)

        segments = 16  # Reduced complexity
        for i in range(segments):
            for j in range(segments):
                # Sphere coordinates with audio deformation
                u1, v1 = i / segments * 2 * math.pi, j / segments * math.pi
                u2, v2 = (i + 1) / segments * 2 * math.pi, (j + 1) / segments * math.pi

                # Audio-reactive radius
                base_radius = 1.0 + self.amplitude * 0.3

                # Vertices
                x1 = base_radius * math.sin(v1) * math.cos(u1)
                y1 = base_radius * math.sin(v1) * math.sin(u1)
                z1 = base_radius * math.cos(v1)

                x2 = base_radius * math.sin(v1) * math.cos(u2)
                y2 = base_radius * math.sin(v1) * math.sin(u2)
                z2 = base_radius * math.cos(v1)

                x3 = base_radius * math.sin(v2) * math.cos(u1)
                y3 = base_radius * math.sin(v2) * math.sin(u1)
                z3 = base_radius * math.cos(v2)

                # Triangle 1
                glVertex3f(x1, y1, z1)
                glVertex3f(x2, y2, z2)
                glVertex3f(x3, y3, z3)

        glEnd()

    def _update_particles(self):
        """Update particle system efficiently"""
        current_time = time.time()

        # Remove old particles
        self.particles = [p for p in self.particles if current_time - p['birth_time'] < 2.0]

        # Add new particles based on audio
        if self.amplitude > 0.1 and len(self.particles) < self.max_particles:
            for _ in range(int(self.amplitude * 3)):  # Fewer particles
                particle = {
                    'x': (np.random.random() - 0.5) * 2,
                    'y': (np.random.random() - 0.5) * 2,
                    'z': (np.random.random() - 0.5) * 2,
                    'vx': (np.random.random() - 0.5) * 0.02,
                    'vy': (np.random.random() - 0.5) * 0.02,
                    'vz': (np.random.random() - 0.5) * 0.02,
                    'birth_time': current_time,
                    'hue': np.random.random()
                }
                self.particles.append(particle)

        # Update particle positions
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['z'] += particle['vz']

    def _render_particles(self):
        """Render particles efficiently"""
        glBegin(GL_POINTS)

        current_time = time.time()
        for particle in self.particles:
            # Age-based alpha
            age = current_time - particle['birth_time']
            alpha = max(0, 1.0 - age / 2.0)

            # Color based on audio
            hue = (particle['hue'] + self.bass * 0.1) % 1.0
            intensity = 0.5 + self.mid * 0.5

            # Simple HSV to RGB
            h = hue * 6.0
            c = intensity
            x = c * (1 - abs((h % 2) - 1))

            if h < 1:
                r, g, b = c, x, 0
            elif h < 2:
                r, g, b = x, c, 0
            elif h < 3:
                r, g, b = 0, c, x
            elif h < 4:
                r, g, b = 0, x, c
            elif h < 5:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x

            glColor4f(r, g, b, alpha)
            glVertex3f(particle['x'], particle['y'], particle['z'])

        glEnd()

    def update_audio_data(self, amplitude, bass, mid, treble):
        """Update audio parameters smoothly"""
        self.amplitude = amplitude
        self.bass = bass
        self.mid = mid
        self.treble = treble


class SmoothMMPAWindow(QMainWindow):
    """Lightweight MMPA window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MMPA - Smooth Performance Edition")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Controls
        controls = QHBoxLayout()

        # Simple controls
        self.amplitude_slider = QSlider(Qt.Horizontal)
        self.amplitude_slider.setRange(0, 100)
        self.amplitude_slider.setValue(50)

        controls.addWidget(QLabel("Volume:"))
        controls.addWidget(self.amplitude_slider)

        # Visualization widget
        self.vis_widget = SmoothMorphWidget()

        # Add to layout
        control_frame = QFrame()
        control_frame.setLayout(controls)
        control_frame.setMaximumHeight(50)

        layout.addWidget(control_frame)
        layout.addWidget(self.vis_widget)

        # Update timer - 30 FPS for smooth performance
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_visualization)
        self.timer.start(33)  # ~30 FPS

        # Connect slider
        self.amplitude_slider.valueChanged.connect(self._on_amplitude_change)

        logger.info("🚀 Smooth MMPA Window initialized")

    def _update_visualization(self):
        """Update visualization smoothly"""
        # Simulate audio input (replace with real audio)
        t = time.time()
        amplitude = 0.3 + 0.2 * math.sin(t * 2) + (self.amplitude_slider.value() / 100.0) * 0.3
        bass = 0.2 + 0.3 * math.sin(t * 0.5)
        mid = 0.3 + 0.2 * math.cos(t * 1.5)
        treble = 0.1 + 0.3 * math.sin(t * 3)

        self.vis_widget.update_audio_data(amplitude, bass, mid, treble)
        self.vis_widget.update()

    def _on_amplitude_change(self, value):
        """Handle amplitude slider change"""
        pass  # Audio reactivity handled in timer


def main():
    app = QApplication(sys.argv)

    print("🚀 Starting MMPA Smooth Performance Edition")
    print("🎯 Optimized for 30fps smooth visualization")
    print("⚡ Lightweight audio processing")
    print("🎨 Simple but beautiful morphing shapes")

    window = SmoothMMPAWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    main()