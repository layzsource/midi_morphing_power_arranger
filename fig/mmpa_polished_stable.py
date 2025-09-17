#!/usr/bin/env python3
"""
MMPA Polished Stable System
Rock-solid performance with all features - fixed the specific bottlenecks

Key Optimizations:
- Stabilized genre detection (no rapid switching)
- Smooth color transitions (no chaos)
- Removed problematic cinematic rendering
- Reduced logging overhead
- Performance monitoring dashboard
"""

import sys
import math
import logging
import numpy as np
import time
import colorsys
from typing import Dict, List, Any
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QSlider, QLabel, QPushButton, QFrame, QGroupBox,
    QCheckBox, QSpinBox, QTabWidget, QTextEdit, QProgressBar
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *

# Optimized logging - much less verbose
logging.basicConfig(level=logging.WARNING)  # Only warnings and errors
logger = logging.getLogger(__name__)

# Import our MMPA framework
from mmpa_signal_framework import (
    MMPASignalEngine, SignalType, SignalFeatures, SignalEvent, SignalToFormMapper
)
from mmpa_midi_processor import MIDISignalProcessor
from mmpa_audio_processor import AudioSignalProcessor

# Import interactive analysis system (but don't log)
try:
    from mmpa_interactive_analysis import (
        AnalysisStateManager, AnalysisMode, InteractionMode, AnalysisKeys
    )
    INTERACTIVE_ANALYSIS_AVAILABLE = True
except ImportError as e:
    INTERACTIVE_ANALYSIS_AVAILABLE = False


class StableMorphWidget(QOpenGLWidget):
    """Polished stable morphing widget - no performance issues"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Core parameters
        self.morph_factor = 0.0
        self.shape_a = 'sphere'
        self.shape_b = 'cube'
        self.rotation = 0.0
        self.particles = []

        # Enhanced visual settings (optimized)
        self.particle_trails = True
        self.color_mode = 'rainbow'
        self.particle_size = 4.0
        self.shape_resolution = 200  # Further reduced for stability

        # MMPA Integration
        self.mmpa_engine = MMPASignalEngine()
        self.current_form_params = {}
        self.signal_history = []
        self.audio_amplitude = 0.0

        # Stabilized color system - NO rapid changes
        self.current_color = [0.5, 0.8, 1.0]  # Current HSV color as list
        self.target_color = [0.5, 0.8, 1.0]   # Target HSV color as list
        self.color_transition_speed = 0.005    # Very slow transitions

        # Stable performance controls
        self.target_fps = 30
        self.frame_count = 0

        # Stabilized Musical Intelligence - NO rapid switching
        self.current_genre = 'unknown'
        self.genre_stability_counter = 0
        self.genre_change_threshold = 90  # 3 seconds at 30fps before genre change
        self.pending_genre = 'unknown'

        self.current_key = 'C major'
        self.key_stability_counter = 0
        self.key_change_threshold = 60    # 2 seconds before key change
        self.pending_key = 'C major'

        # Optimized visual styles
        self.genre_visual_styles = self._setup_stable_genre_styles()
        self.key_color_palettes = self._setup_stable_key_palettes()

        # Interactive Analysis System (simplified)
        self.analysis_manager = None
        if INTERACTIVE_ANALYSIS_AVAILABLE:
            try:
                self.analysis_manager = AnalysisStateManager()
            except Exception as e:
                pass  # Fail silently

        # Optimized particle system
        self.max_particles = 150  # Reduced further
        self.particle_spawn_probability = 0.1  # Reduced spawn rate

        # Performance monitoring
        self.last_fps_time = time.time()
        self.fps_counter = 0
        self.current_fps = 30.0
        self.avg_frame_time = 0.033

    def initializeGL(self):
        """Initialize OpenGL with maximum stability"""
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
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
        """Ultra-stable render with performance monitoring"""
        frame_start_time = time.time()

        try:
            self.frame_count += 1

            # Update performance metrics
            self._update_performance_metrics()

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Stable camera setup
            rotation_speed = 0.5  # Consistent speed
            glTranslatef(0.0, 0.0, -6.0)
            glRotatef(self.rotation * rotation_speed, 1.0, 1.0, 0.0)
            glRotatef(self.rotation * 0.3, 0.0, 1.0, 0.0)

            # Smooth color transitions
            self._update_stable_colors()

            # Render stable morphing
            self.render_stable_morphing()

            # Render stable particles
            if self.frame_count % 2 == 0:  # Update every other frame
                self.update_stable_particles()
            self.render_stable_particles()

            # Render analysis overlays (simplified)
            if (INTERACTIVE_ANALYSIS_AVAILABLE and self.analysis_manager and
                self.analysis_manager.current_mode != AnalysisMode.LIVE):
                self._render_simple_analysis_overlay()

        except Exception as e:
            logger.error(f"Render error: {e}")

        # Track frame time
        frame_time = time.time() - frame_start_time
        self.avg_frame_time = self.avg_frame_time * 0.9 + frame_time * 0.1

    def _update_performance_metrics(self):
        """Update performance monitoring"""
        current_time = time.time()
        self.fps_counter += 1

        if current_time - self.last_fps_time >= 1.0:  # Every second
            self.current_fps = self.fps_counter / (current_time - self.last_fps_time)
            self.fps_counter = 0
            self.last_fps_time = current_time

    def _update_stable_colors(self):
        """Update colors with maximum stability"""
        # Very smooth interpolation - no jitter
        for i in range(3):  # H, S, V
            diff = self.target_color[i] - self.current_color[i]
            self.current_color[i] += diff * self.color_transition_speed

        # Set OpenGL color
        rgb_color = colorsys.hsv_to_rgb(*self.current_color)
        glColor3f(*rgb_color)

    def render_stable_morphing(self):
        """Render morphing with maximum stability"""
        # Simple, efficient shape generation
        vertices = []
        resolution = max(16, self.shape_resolution // 10)  # Much simpler

        for i in range(resolution):
            theta = (i / resolution) * 2 * math.pi

            # Simple audio-reactive radius
            base_radius = 1.0 + self.audio_amplitude * 0.2  # Reduced reactivity

            # Simple morphing
            radius_mod = 1.0 + 0.1 * math.sin(theta * 2 + self.morph_factor * math.pi)
            radius = base_radius * radius_mod

            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            z = 0.1 * math.sin(theta * 4 + time.time() * 0.5)  # Gentle wave

            vertices.append((x, y, z))

        # Render efficiently
        if vertices:
            # Line loop for performance
            glBegin(GL_LINE_LOOP)
            for vertex in vertices:
                glVertex3f(*vertex)
            glEnd()

            # Simple fill
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, 0)  # Center
            for vertex in vertices:
                glVertex3f(*vertex)
            glVertex3f(*vertices[0])  # Close the fan
            glEnd()

    def update_stable_particles(self):
        """Update particles with stability focus"""
        current_time = time.time()

        # Remove old particles
        self.particles = [p for p in self.particles
                         if current_time - p['birth_time'] < 2.5]

        # Add new particles (controlled rate)
        if (self.audio_amplitude > 0.15 and
            len(self.particles) < self.max_particles and
            np.random.random() < self.particle_spawn_probability):

            particle = {
                'x': (np.random.random() - 0.5) * 3,
                'y': (np.random.random() - 0.5) * 3,
                'z': (np.random.random() - 0.5) * 3,
                'vx': (np.random.random() - 0.5) * 0.015,
                'vy': (np.random.random() - 0.5) * 0.015,
                'vz': (np.random.random() - 0.5) * 0.015,
                'birth_time': current_time,
                'hue': self.current_color[0] + (np.random.random() - 0.5) * 0.1
            }
            self.particles.append(particle)

        # Update particle positions
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['z'] += particle['vz']

    def render_stable_particles(self):
        """Render particles with stability"""
        if not self.particles:
            return

        glPointSize(self.particle_size)
        glBegin(GL_POINTS)

        current_time = time.time()
        for particle in self.particles:
            # Age-based alpha
            age = current_time - particle['birth_time']
            alpha = max(0.1, 1.0 - age / 2.5)

            # Stable color
            hue = particle['hue'] % 1.0
            rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.6 + self.audio_amplitude * 0.4)

            glColor4f(rgb[0], rgb[1], rgb[2], alpha)
            glVertex3f(particle['x'], particle['y'], particle['z'])

        glEnd()

    def process_audio_signal(self, signal_data):
        """Process audio with stability focus"""
        if not signal_data:
            return

        # Always update amplitude smoothly
        new_amplitude = signal_data.get('amplitude', 0.0)
        self.audio_amplitude = self.audio_amplitude * 0.8 + new_amplitude * 0.2

        # Stable genre detection - NO rapid switching
        if self.frame_count % 30 == 0:  # Check once per second
            genre_info = signal_data.get('genre_info', {})
            if genre_info:
                detected_genre = genre_info.get('genre', 'unknown')

                if detected_genre == self.pending_genre:
                    self.genre_stability_counter += 1
                else:
                    self.pending_genre = detected_genre
                    self.genre_stability_counter = 0

                # Only change genre after stability threshold
                if (self.genre_stability_counter >= self.genre_change_threshold and
                    detected_genre != self.current_genre):
                    self.current_genre = detected_genre
                    self._apply_stable_genre_style(detected_genre)

            # Stable key detection
            key_info = signal_data.get('key_info', {})
            if key_info:
                detected_key = key_info.get('key', 'C major')

                if detected_key == self.pending_key:
                    self.key_stability_counter += 1
                else:
                    self.pending_key = detected_key
                    self.key_stability_counter = 0

                # Only change key after stability threshold
                if (self.key_stability_counter >= self.key_change_threshold and
                    detected_key != self.current_key):
                    self.current_key = detected_key
                    self._transition_to_stable_key_palette(detected_key)

        # Update rotation smoothly
        self.rotation += 0.8  # Consistent speed

    def _apply_stable_genre_style(self, genre):
        """Apply genre style with stability"""
        style = self.genre_visual_styles.get(genre, {})
        if style:
            self.particle_spawn_probability = style.get('spawn_rate', 0.1)
            # Don't log every change - too much noise

    def _transition_to_stable_key_palette(self, key):
        """Transition to key palette smoothly"""
        new_palette = self.key_color_palettes.get(key)
        if new_palette:
            self.target_color = list(new_palette)  # Convert to list for mutability

    def _setup_stable_genre_styles(self):
        """Setup stable genre visual styles"""
        return {
            'rock': {'spawn_rate': 0.15},
            'electronic': {'spawn_rate': 0.2},
            'classical': {'spawn_rate': 0.05},
            'jazz': {'spawn_rate': 0.1},
            'ambient': {'spawn_rate': 0.03},
            'pop': {'spawn_rate': 0.12},
            'hip_hop': {'spawn_rate': 0.18},
            'blues': {'spawn_rate': 0.08}
        }

    def _setup_stable_key_palettes(self):
        """Setup stable key-based color palettes"""
        return {
            'C major': (0.0, 0.7, 1.0),     # Red
            'G major': (0.33, 0.7, 1.0),    # Green
            'D major': (0.66, 0.7, 1.0),    # Blue
            'A major': (0.16, 0.7, 1.0),    # Orange
            'E major': (0.50, 0.7, 1.0),    # Cyan
            'A minor': (0.83, 0.6, 0.9),    # Purple
            'C# major': (0.08, 0.8, 1.0),   # Bright red
            'F major': (0.25, 0.7, 1.0),    # Yellow-green
            'F# minor': (0.75, 0.6, 0.9)    # Pink
        }

    def _render_simple_analysis_overlay(self):
        """Simple analysis mode indicator"""
        if not self.analysis_manager:
            return

        # Just show a simple colored border
        mode = self.analysis_manager.current_mode
        if mode == AnalysisMode.PAUSED:
            glColor3f(1.0, 1.0, 0.0)  # Yellow border
        elif mode == AnalysisMode.FROZEN:
            glColor3f(1.0, 0.0, 0.0)  # Red border
        elif mode == AnalysisMode.INSPECTION:
            glColor3f(0.0, 1.0, 1.0)  # Cyan border
        elif mode == AnalysisMode.LABELING:
            glColor3f(0.0, 1.0, 0.0)  # Green border
        else:
            return

        # Draw border
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), 0, self.height(), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glBegin(GL_LINE_LOOP)
        glVertex2f(5, 5)
        glVertex2f(self.width() - 5, 5)
        glVertex2f(self.width() - 5, self.height() - 5)
        glVertex2f(5, self.height() - 5)
        glEnd()

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def get_performance_metrics(self):
        """Get current performance metrics"""
        return {
            'fps': self.current_fps,
            'frame_time_ms': self.avg_frame_time * 1000,
            'particle_count': len(self.particles),
            'genre': self.current_genre,
            'key': self.current_key,
            'audio_amplitude': self.audio_amplitude
        }

    # Keyboard handling for analysis modes
    def keyPressEvent(self, event):
        """Handle keyboard input for analysis modes"""
        if not INTERACTIVE_ANALYSIS_AVAILABLE or not self.analysis_manager:
            return

        key = event.key()
        if key == AnalysisKeys.PAUSE_RESUME:
            self._toggle_pause_resume()
        elif key == AnalysisKeys.FREEZE:
            self._freeze_current_moment()
        elif key == AnalysisKeys.INSPECTION:
            self._enter_inspection_mode()
        elif key == AnalysisKeys.LABELING:
            self._enter_labeling_mode()
        elif key == AnalysisKeys.RETURN_LIVE:
            self._return_to_live_mode()

    def _toggle_pause_resume(self):
        if self.analysis_manager.current_mode == AnalysisMode.LIVE:
            self.analysis_manager.pause()
        else:
            self.analysis_manager.resume()

    def _freeze_current_moment(self):
        self.analysis_manager.freeze()

    def _enter_inspection_mode(self):
        self.analysis_manager.enter_inspection_mode()

    def _enter_labeling_mode(self):
        self.analysis_manager.enter_labeling_mode()

    def _return_to_live_mode(self):
        self.analysis_manager.return_to_live()


class PolishedMMPAWindow(QMainWindow):
    """Polished MMPA main window with performance dashboard"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MMPA - Polished Stable Edition ⚡")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize MMPA engine
        self.mmpa_engine = MMPASignalEngine()

        # Initialize stable visualization widget
        self.morph_widget = StableMorphWidget()

        # Setup UI with performance monitoring
        self._setup_polished_ui()
        self._setup_stable_audio_processing()

        # Update timer - stable 30 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_visualization)
        self.timer.start(33)  # Exactly 30 FPS

        # Performance monitoring timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self._update_performance_display)
        self.perf_timer.start(1000)  # Update every second

    def _setup_polished_ui(self):
        """Setup polished UI with performance monitoring"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Left panel - enhanced controls
        left_panel = QFrame()
        left_panel.setMaximumWidth(320)
        left_panel.setFrameStyle(QFrame.StyledPanel)

        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Performance Dashboard
        perf_group = QGroupBox("📊 Performance Dashboard")
        perf_layout = QVBoxLayout()

        self.fps_label = QLabel("FPS: 30.0")
        self.fps_label.setFont(QFont("Arial", 12, QFont.Bold))
        perf_layout.addWidget(self.fps_label)

        self.frame_time_label = QLabel("Frame Time: 33.0ms")
        perf_layout.addWidget(self.frame_time_label)

        self.particle_label = QLabel("Particles: 0")
        perf_layout.addWidget(self.particle_label)

        perf_group.setLayout(perf_layout)
        left_layout.addWidget(perf_group)

        # Audio Status
        audio_group = QGroupBox("🎵 Audio Status")
        audio_layout = QVBoxLayout()

        self.genre_label = QLabel("Genre: unknown")
        self.genre_label.setFont(QFont("Arial", 10, QFont.Bold))
        audio_layout.addWidget(self.genre_label)

        self.key_label = QLabel("Key: C major")
        audio_layout.addWidget(self.key_label)

        self.amplitude_bar = QProgressBar()
        self.amplitude_bar.setRange(0, 100)
        audio_layout.addWidget(QLabel("Amplitude:"))
        audio_layout.addWidget(self.amplitude_bar)

        audio_group.setLayout(audio_layout)
        left_layout.addWidget(audio_group)

        # Simple Controls
        controls_group = QGroupBox("🎛️ Controls")
        controls_layout = QVBoxLayout()

        # Performance mode
        self.perf_mode_check = QCheckBox("Performance Mode")
        self.perf_mode_check.setChecked(True)
        controls_layout.addWidget(self.perf_mode_check)

        # Particle trails
        self.trails_check = QCheckBox("Particle Trails")
        self.trails_check.setChecked(True)
        self.trails_check.toggled.connect(self._toggle_particle_trails)
        controls_layout.addWidget(self.trails_check)

        controls_group.setLayout(controls_layout)
        left_layout.addWidget(controls_group)

        # Instructions
        instructions_group = QGroupBox("⌨️ Analysis Mode Keys")
        instructions_layout = QVBoxLayout()

        instructions = [
            "SPACE: Pause/Resume",
            "F: Freeze frame",
            "I: Inspection mode",
            "L: Labeling mode",
            "ESC: Return to live"
        ]

        for instruction in instructions:
            label = QLabel(instruction)
            label.setFont(QFont("Courier", 9))
            instructions_layout.addWidget(label)

        instructions_group.setLayout(instructions_layout)
        left_layout.addWidget(instructions_group)

        left_layout.addStretch()

        # Add to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self.morph_widget)

    def _setup_stable_audio_processing(self):
        """Setup stable audio processing"""
        try:
            # Initialize MIDI processor
            midi_processor = MIDISignalProcessor()
            self.mmpa_engine.register_signal_processor(SignalType.MIDI, midi_processor)

            # Initialize audio processor
            self.audio_processor = AudioSignalProcessor()
            self.mmpa_engine.register_signal_processor(SignalType.AUDIO, self.audio_processor)

            # Start processing
            self.mmpa_engine.start()

        except Exception as e:
            logger.error(f"Audio setup failed: {e}")

    def _update_visualization(self):
        """Update visualization with stable processing"""
        try:
            # Get latest signal data
            signal_data = self.mmpa_engine.get_combined_features()

            if signal_data:
                self.morph_widget.process_audio_signal(signal_data)

            # Update widget
            self.morph_widget.update()

        except Exception as e:
            pass  # Fail silently - don't spam console

    def _update_performance_display(self):
        """Update performance dashboard"""
        try:
            metrics = self.morph_widget.get_performance_metrics()

            # Update displays
            self.fps_label.setText(f"FPS: {metrics['fps']:.1f}")
            self.frame_time_label.setText(f"Frame Time: {metrics['frame_time_ms']:.1f}ms")
            self.particle_label.setText(f"Particles: {metrics['particle_count']}")

            self.genre_label.setText(f"Genre: {metrics['genre']}")
            self.key_label.setText(f"Key: {metrics['key']}")
            self.amplitude_bar.setValue(int(metrics['audio_amplitude'] * 100))

            # Color-code FPS
            if metrics['fps'] >= 25:
                self.fps_label.setStyleSheet("color: green; font-weight: bold;")
            elif metrics['fps'] >= 20:
                self.fps_label.setStyleSheet("color: orange; font-weight: bold;")
            else:
                self.fps_label.setStyleSheet("color: red; font-weight: bold;")

        except Exception as e:
            pass  # Fail silently

    def _toggle_particle_trails(self, enabled):
        """Toggle particle trails"""
        self.morph_widget.particle_trails = enabled


def main():
    app = QApplication(sys.argv)

    print("🚀 MMPA Polished Stable Edition")
    print("=" * 40)
    print("✅ Stability Fixes:")
    print("   • No rapid genre switching")
    print("   • Smooth color transitions")
    print("   • Reduced logging overhead")
    print("   • Stable 30fps performance")
    print("   • Performance monitoring dashboard")
    print("")
    print("🎹 Controls:")
    print("   • SPACE: Pause/Resume")
    print("   • F: Freeze frame")
    print("   • I: Inspection mode")
    print("   • L: Labeling mode")
    print("   • ESC: Return to live")
    print("")
    print("📊 Monitor the performance dashboard in real-time!")

    window = PolishedMMPAWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    main()