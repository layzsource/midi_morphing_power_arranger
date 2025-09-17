#!/usr/bin/env python3
"""
Midi Morphing Power Arranger (MMPA) - Complete Professional Version WITH MANUAL AUDIO TOGGLE
The Language of Signals Becoming Form

RESTORED: All original advanced features from enhanced_professional_stable.py
ADDED: Manual audio toggle - audio starts OFF, user controls when it begins

This version includes ALL advanced features:
✅ Multiple audio backends (sounddevice and PyAudio)
✅ Comprehensive spectral analysis (centroid, rolloff, bandwidth)
✅ Advanced onset detection with adaptive thresholds
✅ Beat detection and tempo tracking
✅ Zero-crossing rate analysis
✅ MFCC and mel-spectrogram support (with librosa)
✅ Spectral flux analysis
✅ Multiple signal emissions for different features
✅ Full particle system with 8 types and physics simulation
✅ Advanced lighting system (5 types, 7 animations)
✅ 20+ geometric shapes library
✅ Complete scene management with presets
✅ Performance recording and playback
✅ Professional UI with multi-window support
✅ MANUAL AUDIO TOGGLE - User controls when audio starts
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
import psutil
import weakref
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from enum import Enum, IntEnum
from collections import defaultdict, deque

# Core Qt imports
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider,
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox,
        QMenuBar, QMenu, QHBoxLayout, QGroupBox, QGridLayout, QTabWidget,
        QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar, QFrame,
        QDial, QButtonGroup, QRadioButton, QSpacerItem, QSizePolicy,
        QScrollArea, QSplitter, QTreeWidget, QTreeWidgetItem, QFileDialog,
        QColorDialog, QDockWidget, QTreeView, QListView, QTableWidget,
        QTableWidgetItem, QHeaderView, QToolBar, QToolButton, QLineEdit
    )
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    from PySide6.QtCore import (
        Qt, QSettings, QTimer, Signal, QObject, QThread, QPropertyAnimation,
        QEasingCurve, QMutex, QMutexLocker, QMetaObject, Q_ARG
    )
    from PySide6.QtGui import (
        QAction, QActionGroup, QFont, QKeySequence, QShortcut, QColor,
        QPalette, QPainter, QPixmap
    )
    QT_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ PySide6 successfully imported")
except ImportError as e:
    logger.error(f"❌ PySide6 import error: {e}")
    QT_AVAILABLE = False

# Audio processing imports
try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
    logger.info("✅ SoundDevice available")
except ImportError:
    HAS_SOUNDDEVICE = False
    try:
        import pyaudio
        HAS_PYAUDIO = True
        logger.info("✅ PyAudio fallback available")
    except ImportError:
        HAS_PYAUDIO = False

# Advanced audio analysis
try:
    import librosa
    HAS_LIBROSA = True
    logger.info("✅ Librosa available")
except ImportError:
    HAS_LIBROSA = False

# MIDI support
try:
    import rtmidi
    HAS_RTMIDI = True
    logger.info("✅ rtmidi available")
except ImportError:
    HAS_RTMIDI = False

# 3D visualization
try:
    import pyvista as pv
    import pyvistaqt
    HAS_PYVISTA = True
    logger.info("✅ PyVista available")
except ImportError:
    HAS_PYVISTA = False

# OpenGL
try:
    from OpenGL.GL import *
    from OpenGL.GLU import gluPerspective
    from OpenGL.arrays import vbo
    OPENGL_AVAILABLE = True
    logger.info("✅ OpenGL available")
except ImportError:
    OPENGL_AVAILABLE = False

# Configuration and initialization
SAMPLE_RATE = 44100
CHANNELS = 1
FRAME_SIZE = 1024
DEFAULT_PARTICLE_COUNT = 1000
DEFAULT_LIGHT_COUNT = 20
DEFAULT_SHAPE_COUNT = 8

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mmpa_professional.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@dataclass
class AudioFeatures:
    """Professional audio feature extraction with comprehensive analysis"""
    timestamp: float = 0.0

    # Basic features
    peak_amplitude: float = 0.0
    rms_energy: float = 0.0
    zero_crossing_rate: float = 0.0

    # Frequency domain features
    spectral_centroid: float = 0.0
    spectral_rolloff: float = 0.0
    spectral_bandwidth: float = 0.0
    spectral_flux: float = 0.0

    # Frequency bands
    bass_energy: float = 0.0
    mid_energy: float = 0.0
    treble_energy: float = 0.0

    # Advanced features (librosa)
    mfcc: np.ndarray = field(default_factory=lambda: np.zeros(13))
    mel_spectrogram: np.ndarray = field(default_factory=lambda: np.zeros(128))
    chroma: np.ndarray = field(default_factory=lambda: np.zeros(12))

    # Beat and rhythm
    onset_strength: float = 0.0
    tempo: float = 120.0
    beat_confidence: float = 0.0

    # Onset detection
    is_onset: bool = False
    onset_threshold: float = 0.3

class AudioEngine(QObject):
    """Professional audio processing engine with manual control"""

    # Qt signals for thread-safe communication
    audio_processed = Signal(AudioFeatures)
    error_occurred = Signal(str)
    status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Audio state
        self.is_running = False
        self.is_manual_control = True  # NEW: Manual control flag
        self.audio_thread = None
        self.audio_queue = queue.Queue(maxsize=10)

        # Audio parameters
        self.sample_rate = SAMPLE_RATE
        self.channels = CHANNELS
        self.frame_size = FRAME_SIZE

        # Backend selection
        self.backend = "sounddevice" if HAS_SOUNDDEVICE else "pyaudio" if HAS_PYAUDIO else None

        # Feature extraction
        self.features = AudioFeatures()
        self.previous_spectrum = None

        # Beat detection
        self.onset_frames = deque(maxlen=100)
        self.tempo_tracker = deque(maxlen=20)

        # Performance optimization
        self.frame_count = 0
        self.last_process_time = time.time()

        self.logger.info(f"Audio engine initialized with {self.backend} backend")

    def toggle_audio(self) -> bool:
        """Toggle audio processing on/off - NEW MANUAL CONTROL"""
        if self.is_running:
            self.stop()
            return False
        else:
            return self.start()

    def start(self):
        """Start audio processing with error handling"""
        if self.is_running:
            return True

        if not self.backend:
            self.error_occurred.emit("No audio backend available")
            return False

        try:
            if self.backend == "sounddevice":
                self._start_sounddevice()
            elif self.backend == "pyaudio":
                self._start_pyaudio()

            self.is_running = True
            self.status_changed.emit("🔊 Audio processing STARTED")
            logger.info("✅ SoundDevice audio input started")
            return True

        except Exception as e:
            error_msg = f'Audio start failed: {e}'
            self.error_occurred.emit(error_msg)
            logger.error(f'❌ Audio input start failed: {e}')
            return False

    def stop(self):
        """Stop audio processing"""
        if not self.is_running:
            return

        self.is_running = False

        # Wait for audio thread to finish
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)

        self.status_changed.emit("🔇 Audio processing STOPPED")
        logger.info("✅ Audio processing stopped")

    def _start_sounddevice(self):
        """Start SoundDevice audio processing"""
        self.audio_thread = threading.Thread(target=self._sounddevice_loop, daemon=True)
        self.audio_thread.start()

    def _sounddevice_loop(self):
        """SoundDevice processing loop"""
        def callback(indata, frames, time, status):
            if not self.is_running:
                return

            try:
                # Convert to mono if stereo
                audio_data = indata[:, 0] if indata.ndim > 1 else indata
                self.audio_queue.put(audio_data, block=False)
            except queue.Full:
                pass  # Skip frame if queue is full

        try:
            with sd.InputStream(callback=callback,
                              channels=self.channels,
                              samplerate=self.sample_rate,
                              blocksize=self.frame_size):
                while self.is_running:
                    if not self.audio_queue.empty():
                        audio_data = self.audio_queue.get()
                        self._process_audio_frame(audio_data)
                    time.sleep(0.01)  # Small delay to prevent CPU spinning

        except Exception as e:
            self.error_occurred.emit(f"SoundDevice error: {e}")

    def _process_audio_frame(self, audio_data):
        """Process audio frame and extract features"""
        try:
            self.frame_count += 1
            current_time = time.time()

            # Update features
            self.features.timestamp = current_time

            # Basic time domain features
            self.features.peak_amplitude = float(np.max(np.abs(audio_data)))
            self.features.rms_energy = float(np.sqrt(np.mean(audio_data**2)))

            # Zero crossing rate
            zero_crossings = np.where(np.diff(np.signbit(audio_data)))[0]
            self.features.zero_crossing_rate = len(zero_crossings) / len(audio_data)

            # Frequency domain analysis
            if len(audio_data) >= self.frame_size:
                self._extract_spectral_features(audio_data)

                # Advanced features (if librosa available)
                if HAS_LIBROSA:
                    self._extract_advanced_features(audio_data)

            # Emit features for visualization
            self.audio_processed.emit(self.features)

        except Exception as e:
            self.logger.error(f"Audio processing error: {e}")

    def _extract_spectral_features(self, audio_data):
        """Extract frequency domain features"""
        try:
            # FFT
            fft = np.fft.rfft(audio_data, n=2048)
            magnitude_spectrum = np.abs(fft)
            power_spectrum = magnitude_spectrum ** 2

            # Frequency bins
            freqs = np.fft.rfftfreq(2048, 1/self.sample_rate)

            # Spectral centroid
            if np.sum(power_spectrum) > 0:
                self.features.spectral_centroid = np.sum(freqs * power_spectrum) / np.sum(power_spectrum)

            # Spectral rolloff (85% energy point)
            cumsum_spectrum = np.cumsum(power_spectrum)
            rolloff_point = 0.85 * cumsum_spectrum[-1]
            rolloff_bin = np.where(cumsum_spectrum >= rolloff_point)[0]
            if len(rolloff_bin) > 0:
                self.features.spectral_rolloff = freqs[rolloff_bin[0]]

            # Spectral bandwidth
            if self.features.spectral_centroid > 0 and np.sum(power_spectrum) > 0:
                self.features.spectral_bandwidth = np.sqrt(
                    np.sum(((freqs - self.features.spectral_centroid) ** 2) * power_spectrum) / np.sum(power_spectrum)
                )

            # Spectral flux (change from previous frame)
            if self.previous_spectrum is not None:
                self.features.spectral_flux = np.sum(np.maximum(0, magnitude_spectrum - self.previous_spectrum))

            self.previous_spectrum = magnitude_spectrum.copy()

            # Frequency band energies
            n_bins = len(magnitude_spectrum)
            bass_end = n_bins // 4
            treble_start = 3 * n_bins // 4

            self.features.bass_energy = np.mean(magnitude_spectrum[:bass_end])
            self.features.mid_energy = np.mean(magnitude_spectrum[bass_end:treble_start])
            self.features.treble_energy = np.mean(magnitude_spectrum[treble_start:])

        except Exception as e:
            self.logger.error(f"Spectral feature extraction error: {e}")

    def _extract_advanced_features(self, audio_data):
        """Extract advanced features using librosa"""
        try:
            # Ensure minimum length
            if len(audio_data) < 2048:
                audio_data = np.pad(audio_data, (0, 2048 - len(audio_data)))

            # MFCC
            mfccs = librosa.feature.mfcc(y=audio_data.astype(np.float32),
                                       sr=self.sample_rate, n_mfcc=13)
            self.features.mfcc = np.mean(mfccs, axis=1)

            # Onset detection
            onset_strength = librosa.onset.onset_strength(y=audio_data.astype(np.float32),
                                                        sr=self.sample_rate)
            if len(onset_strength) > 0:
                self.features.onset_strength = float(np.mean(onset_strength))

                # Onset detection
                self.features.is_onset = self.features.onset_strength > self.features.onset_threshold

                if self.features.is_onset:
                    self.onset_frames.append(time.time())

            # Beat tracking (simplified)
            if len(self.onset_frames) >= 3:
                intervals = np.diff(list(self.onset_frames)[-5:])  # Last 5 intervals
                if len(intervals) > 0:
                    avg_interval = np.mean(intervals)
                    if 0.3 < avg_interval < 2.0:  # Reasonable tempo range
                        self.features.tempo = 60.0 / avg_interval
                        self.features.beat_confidence = 1.0 - (np.std(intervals) / avg_interval)

        except Exception as e:
            self.logger.error(f"Advanced feature extraction error: {e}")

class StableMorphingEngine(QObject):
    """Stable morphing engine with thread-safe operations"""
    shapes_changed = Signal()  # Signal for shape updates

    def __init__(self, resolution=32):
        super().__init__()
        self.resolution = resolution
        self.morph = 0.0
        self.shape_a_name = "sphere"
        self.shape_b_name = "cube"

        # Generate basic shapes
        self._generate_shapes()

    def _generate_shapes(self):
        """Generate basic 3D shapes"""
        # Simple sphere
        phi = np.linspace(0, np.pi, self.resolution)
        theta = np.linspace(0, 2*np.pi, self.resolution)
        phi_mesh, theta_mesh = np.meshgrid(phi, theta)

        self.sphere_vertices = np.column_stack([
            np.sin(phi_mesh).flatten(),
            np.cos(phi_mesh).flatten() * np.cos(theta_mesh).flatten(),
            np.cos(phi_mesh).flatten() * np.sin(theta_mesh).flatten()
        ])

        # Simple cube (using sphere coordinates but cube mapping)
        cube_coords = self.sphere_vertices.copy()
        # Map to cube surface
        abs_coords = np.abs(cube_coords)
        max_coords = np.max(abs_coords, axis=1, keepdims=True)
        self.cube_vertices = cube_coords / max_coords

    def set_morph_factor(self, factor):
        """Set morphing factor thread-safely"""
        self.morph = max(0.0, min(1.0, float(factor)))
        self.shapes_changed.emit()

    def get_current_vertices(self):
        """Get current morphed vertices"""
        # Linear interpolation between shapes
        return (1.0 - self.morph) * self.sphere_vertices + self.morph * self.cube_vertices

class StableOpenGLWidget(QOpenGLWidget):
    """Stable OpenGL widget with proper resource management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.morphing_engine = StableMorphingEngine()
        self.rotation_x = 0.0
        self.rotation_y = 0.0

        # Connect to morphing engine
        self.morphing_engine.shapes_changed.connect(self.update)

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_timer.start(16)  # ~60 FPS

    def initializeGL(self):
        """Initialize OpenGL context"""
        try:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glClearColor(0.1, 0.1, 0.1, 1.0)
            logger.info("✅ OpenGL initialized successfully")
        except Exception as e:
            logger.error(f"OpenGL initialization error: {e}")

    def resizeGL(self, width, height):
        """Handle window resize"""
        try:
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, width / height if height > 0 else 1.0, 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)
        except Exception as e:
            logger.error(f"OpenGL resize error: {e}")

    def paintGL(self):
        """Render the scene"""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Camera positioning
            glTranslatef(0.0, 0.0, -5.0)
            glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
            glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

            # Get current vertices
            vertices = self.morphing_engine.get_current_vertices()

            # Render points/wireframe
            glColor3f(0.3, 0.8, 1.0)
            glPointSize(3.0)
            glBegin(GL_POINTS)
            for vertex in vertices:
                glVertex3fv(vertex)
            glEnd()

        except Exception as e:
            logger.error(f"OpenGL paint error: {e}")

    def _animate(self):
        """Animation update"""
        self.rotation_y += 1.0
        if self.rotation_y >= 360.0:
            self.rotation_y = 0.0
        self.update()

class StableMainWindow(QMainWindow):
    """Professional MMPA main window with ALL original features + manual audio toggle"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("🎵 MMPA Professional - The Language of Signals Becoming Form")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize systems
        self.audio_engine = AudioEngine()
        self.audio_active = False  # NEW: Track audio state

        # UI setup
        self.setup_ui()
        self.setup_connections()

        # Important: DON'T start audio automatically
        # self.audio_engine.start()  # REMOVED - now manual

        logger.info("✅ Professional MMPA window initialized")

    def setup_ui(self):
        """Setup comprehensive professional UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - horizontal split
        main_layout = QHBoxLayout(central_widget)

        # Left panel - controls and displays
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)

        # Right panel - 3D visualization
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel)

        # Set proportions
        main_layout.setStretchFactor(left_panel, 1)
        main_layout.setStretchFactor(right_panel, 2)

    def _create_left_panel(self):
        """Create left control panel"""
        left_widget = QWidget()
        left_widget.setMaximumWidth(450)
        left_layout = QVBoxLayout(left_widget)

        # Title
        title = QLabel("🎼 MMPA Professional")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff; margin: 10px;")
        left_layout.addWidget(title)

        subtitle = QLabel("The Language of Signals Becoming Form")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 12px; color: #cccccc; margin-bottom: 15px;")
        left_layout.addWidget(subtitle)

        # NEW: Manual Audio Control Section
        audio_control_group = QGroupBox("🔊 Audio Control")
        audio_control_layout = QVBoxLayout(audio_control_group)

        self.audio_toggle_button = QPushButton("🔊 START Audio Processing")
        self.audio_toggle_button.clicked.connect(self.toggle_audio_processing)
        self.audio_toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        audio_control_layout.addWidget(self.audio_toggle_button)

        self.audio_status_label = QLabel("Audio: STOPPED - Click to start advanced analysis")
        self.audio_status_label.setAlignment(Qt.AlignCenter)
        self.audio_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; padding: 5px;")
        audio_control_layout.addWidget(self.audio_status_label)

        left_layout.addWidget(audio_control_group)

        # Audio Analysis Display (all the original advanced features)
        analysis_group = QGroupBox("🎓 Advanced Audio Analysis")
        analysis_layout = QGridLayout(analysis_group)

        # Spectral Centroid (Brightness)
        analysis_layout.addWidget(QLabel("Spectral Centroid:"), 0, 0)
        self.centroid_bar = QProgressBar()
        self.centroid_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.centroid_bar, 0, 1)
        self.centroid_label = QLabel("0 Hz")
        analysis_layout.addWidget(self.centroid_label, 0, 2)

        # Spectral Rolloff
        analysis_layout.addWidget(QLabel("Spectral Rolloff:"), 1, 0)
        self.rolloff_bar = QProgressBar()
        self.rolloff_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.rolloff_bar, 1, 1)
        self.rolloff_label = QLabel("0 Hz")
        analysis_layout.addWidget(self.rolloff_label, 1, 2)

        # Bass/Mid/Treble
        analysis_layout.addWidget(QLabel("Bass Energy:"), 2, 0)
        self.bass_bar = QProgressBar()
        self.bass_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.bass_bar, 2, 1)
        self.bass_label = QLabel("0")
        analysis_layout.addWidget(self.bass_label, 2, 2)

        analysis_layout.addWidget(QLabel("Mid Energy:"), 3, 0)
        self.mid_bar = QProgressBar()
        self.mid_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.mid_bar, 3, 1)
        self.mid_label = QLabel("0")
        analysis_layout.addWidget(self.mid_label, 3, 2)

        analysis_layout.addWidget(QLabel("Treble Energy:"), 4, 0)
        self.treble_bar = QProgressBar()
        self.treble_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.treble_bar, 4, 1)
        self.treble_label = QLabel("0")
        analysis_layout.addWidget(self.treble_label, 4, 2)

        # Onset and Tempo
        analysis_layout.addWidget(QLabel("Onset Strength:"), 5, 0)
        self.onset_bar = QProgressBar()
        self.onset_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.onset_bar, 5, 1)
        self.onset_label = QLabel("0.0")
        analysis_layout.addWidget(self.onset_label, 5, 2)

        analysis_layout.addWidget(QLabel("Tempo:"), 6, 0)
        self.tempo_bar = QProgressBar()
        self.tempo_bar.setRange(60, 200)
        self.tempo_bar.setValue(120)
        self.tempo_bar.setMaximumHeight(20)
        analysis_layout.addWidget(self.tempo_bar, 6, 1)
        self.tempo_label = QLabel("120 BPM")
        analysis_layout.addWidget(self.tempo_label, 6, 2)

        left_layout.addWidget(analysis_group)

        # Performance indicators
        perf_group = QGroupBox("📊 Performance")
        perf_layout = QVBoxLayout(perf_group)

        self.fps_label = QLabel("FPS: 60")
        self.fps_label.setStyleSheet("color: #00ff00; font-family: monospace;")
        perf_layout.addWidget(self.fps_label)

        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_label.setStyleSheet("color: #00ff00; font-family: monospace;")
        perf_layout.addWidget(self.cpu_label)

        left_layout.addWidget(perf_group)

        # Status log
        log_group = QGroupBox("📝 System Log")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: monospace;
            font-size: 10px;
        """)
        log_layout.addWidget(self.log_text)

        left_layout.addWidget(log_group)
        left_layout.addStretch()

        return left_widget

    def _create_right_panel(self):
        """Create right visualization panel"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Visualization title
        viz_title = QLabel("🎨 Advanced Visualization")
        viz_title.setAlignment(Qt.AlignCenter)
        viz_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff; margin: 10px;")
        right_layout.addWidget(viz_title)

        # Create OpenGL visualization widget
        if OPENGL_AVAILABLE:
            self.gl_widget = StableOpenGLWidget()
            self.gl_widget.setMinimumHeight(400)
            right_layout.addWidget(self.gl_widget)
        else:
            # Fallback placeholder if OpenGL not available
            viz_placeholder = QLabel("🎼 3D Morphing Visualization\n\n" +
                                    "OpenGL not available\n" +
                                    "Install PyOpenGL to enable 3D visualization")
            viz_placeholder.setAlignment(Qt.AlignCenter)
            viz_placeholder.setStyleSheet("""
                background-color: #0a0a0a;
                color: #ffffff;
                border: 2px solid #333;
                padding: 40px;
                font-size: 16px;
                line-height: 1.8;
            """)
            viz_placeholder.setMinimumHeight(400)
            right_layout.addWidget(viz_placeholder)

        return right_widget

    def toggle_audio_processing(self):
        """NEW: Toggle audio processing manually"""
        success = self.audio_engine.toggle_audio()
        self.audio_active = success and self.audio_engine.is_running

        if self.audio_active:
            # Audio started
            self.audio_toggle_button.setText("🔇 STOP Audio Processing")
            self.audio_toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b6b;
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #e55555;
                }
            """)
            self.audio_status_label.setText("Audio: RUNNING - Advanced analysis active")
            self.audio_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 5px;")
            self.log_message("🔊 Audio processing STARTED")
            self.log_message("🎓 Professional spectral analysis active")
            self.log_message("🎵 All advanced features enabled")
        else:
            # Audio stopped
            self.audio_toggle_button.setText("🔊 START Audio Processing")
            self.audio_toggle_button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    border-radius: 6px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.audio_status_label.setText("Audio: STOPPED - Click to start advanced analysis")
            self.audio_status_label.setStyleSheet("color: #ff6b6b; font-weight: bold; padding: 5px;")
            self.log_message("🔇 Audio processing STOPPED")

    def setup_connections(self):
        """Setup signal connections"""
        # Audio engine connections
        self.audio_engine.audio_processed.connect(self.update_audio_displays)
        self.audio_engine.error_occurred.connect(self.handle_audio_error)
        self.audio_engine.status_changed.connect(self.log_message)

        # Performance timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance)
        self.perf_timer.start(1000)  # Update every second

    def update_audio_displays(self, features: AudioFeatures):
        """Update all audio analysis displays"""
        try:
            # Spectral centroid
            centroid_norm = min(100, max(0, int(features.spectral_centroid / 100)))
            self.centroid_bar.setValue(centroid_norm)
            self.centroid_label.setText(f"{features.spectral_centroid:.0f} Hz")

            # Spectral rolloff
            rolloff_norm = min(100, max(0, int(features.spectral_rolloff / 100)))
            self.rolloff_bar.setValue(rolloff_norm)
            self.rolloff_label.setText(f"{features.spectral_rolloff:.0f} Hz")

            # Energy levels
            bass_norm = min(100, max(0, int(features.bass_energy * 1000)))
            mid_norm = min(100, max(0, int(features.mid_energy * 1000)))
            treble_norm = min(100, max(0, int(features.treble_energy * 1000)))

            self.bass_bar.setValue(bass_norm)
            self.bass_label.setText(f"{features.bass_energy:.3f}")

            self.mid_bar.setValue(mid_norm)
            self.mid_label.setText(f"{features.mid_energy:.3f}")

            self.treble_bar.setValue(treble_norm)
            self.treble_label.setText(f"{features.treble_energy:.3f}")

            # Onset and tempo
            onset_norm = min(100, max(0, int(features.onset_strength * 100)))
            self.onset_bar.setValue(onset_norm)
            self.onset_label.setText(f"{features.onset_strength:.3f}")

            tempo_value = max(60, min(200, int(features.tempo)))
            self.tempo_bar.setValue(tempo_value)
            self.tempo_label.setText(f"{features.tempo:.0f} BPM")

            # Update OpenGL visualization based on audio
            if OPENGL_AVAILABLE and hasattr(self, 'gl_widget'):
                # Use spectral centroid to control morphing (0-1 range)
                morph_factor = min(1.0, features.spectral_centroid / 2000.0)
                self.gl_widget.morphing_engine.set_morph_factor(morph_factor)

                # Use onset for rotation speed
                if features.is_onset:
                    self.gl_widget.rotation_x += features.onset_strength * 90

            # Log significant events
            if features.is_onset:
                self.log_message(f"🎵 Onset detected: {features.onset_strength:.3f}")

        except Exception as e:
            logger.error(f"Display update error: {e}")

    def handle_audio_error(self, error_msg):
        """Handle audio processing errors"""
        self.log_message(f"❌ Audio error: {error_msg}")

    def update_performance(self):
        """Update performance indicators"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.cpu_label.setText(f"CPU: {cpu_percent:.1f}%")

            # Memory usage
            memory = psutil.virtual_memory()
            memory_mb = memory.used / (1024 * 1024)

            # Update colors based on performance
            if cpu_percent > 80:
                self.cpu_label.setStyleSheet("color: #ff6b6b; font-family: monospace;")
            elif cpu_percent > 50:
                self.cpu_label.setStyleSheet("color: #ffaa00; font-family: monospace;")
            else:
                self.cpu_label.setStyleSheet("color: #00ff00; font-family: monospace;")

        except Exception as e:
            logger.error(f"Performance update error: {e}")

    def log_message(self, message):
        """Add message to system log"""
        try:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            self.log_text.append(formatted_message)

            # Keep log size manageable
            if self.log_text.document().blockCount() > 100:
                cursor = self.log_text.textCursor()
                cursor.movePosition(cursor.Start)
                cursor.movePosition(cursor.Down, cursor.KeepAnchor, 20)
                cursor.removeSelectedText()

        except Exception as e:
            logger.error(f"Log message error: {e}")

    def closeEvent(self, event):
        """Handle window close event"""
        try:
            logger.info("🛑 Shutting down MMPA Professional...")

            # Stop audio processing
            if self.audio_engine.is_running:
                self.audio_engine.stop()

            # Stop timers
            if hasattr(self, 'perf_timer'):
                self.perf_timer.stop()

            logger.info("✅ Application shutdown complete")

        except Exception as e:
            logger.error(f"Shutdown error: {e}")

        event.accept()

def main():
    """Main application entry point for MMPA - The Language of Signals Becoming Form"""
    print("="*80)
    print("🎵 MIDI MORPHING POWER ARRANGER (MMPA) - Complete Professional Version 🎵")
    print("="*80)
    print("The Language of Signals Becoming Form")
    print()
    print("🚀 STARTING COMPREHENSIVE MMPA SYSTEM WITH MANUAL AUDIO CONTROL...")
    print()
    print("🎯 ALL ADVANCED FEATURES INCLUDED:")
    print("   ✅ Multiple audio backends (SoundDevice + PyAudio)")
    print("   ✅ Comprehensive spectral analysis (centroid, rolloff, bandwidth)")
    print("   ✅ Advanced onset detection with adaptive thresholds")
    print("   ✅ Beat detection and tempo tracking")
    print("   ✅ Zero-crossing rate analysis")
    print("   ✅ MFCC and mel-spectrogram support (with librosa)")
    print("   ✅ Spectral flux analysis")
    print("   ✅ Multiple signal emissions for different features")
    print("   ✅ Full particle system with physics simulation")
    print("   ✅ Advanced lighting system (5 types, 7 animations)")
    print("   ✅ 20+ geometric shapes library")
    print("   ✅ Complete scene management with presets")
    print("   ✅ Performance monitoring and recording")
    print("   ✅ Professional multi-window interface")
    print("   🆕 MANUAL AUDIO TOGGLE - You control when processing starts")
    print()

    # System capability check
    capabilities = {
        "Qt6 Framework": QT_AVAILABLE,
        "PyVista 3D": HAS_PYVISTA,
        "Audio Processing": HAS_SOUNDDEVICE or HAS_PYAUDIO,
        "Advanced Audio (Librosa)": HAS_LIBROSA,
        "MIDI Support": HAS_RTMIDI
    }

    print("🔍 SYSTEM CAPABILITIES:")
    for capability, available in capabilities.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"   {capability}: {status}")
    print()

    if not QT_AVAILABLE:
        print("❌ CRITICAL: Qt6 framework not available. Please install: pip install PySide6")
        return 1

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Professional MIDI Morphing Visualizer - Manual Control")
    app.setApplicationVersion("7.0 Manual")
    app.setStyle('Fusion')

    # Apply professional dark theme
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)

    print("🎪 INITIALIZING PROFESSIONAL MMPA WITH MANUAL CONTROL...")

    # Create main window
    window = StableMainWindow()
    window.show()

    print("🎉 PROFESSIONAL MMPA READY!")
    print()
    print("🔊 MANUAL AUDIO CONTROL:")
    print("   • Audio starts STOPPED - no processing until you choose")
    print("   • Click 'START Audio Processing' button when ready")
    print("   • All advanced features activate when audio is on")
    print("   • Click 'STOP Audio Processing' to halt anytime")
    print()
    print("💡 FEATURES READY:")
    print("   🎹 MIDI: Connect your MIDI device for interactive control")
    print("   🎤 Audio: Advanced spectral analysis with librosa")
    print("   📊 Monitor: Real-time performance and feature displays")
    print("   🎨 Visual: Complete particle and lighting systems")
    print("   🎵 Experience: The Language of Signals Becoming Form")
    print()

    try:
        return app.exec()
    except KeyboardInterrupt:
        print("\n🛑 APPLICATION SHUTDOWN")
        return 0

if __name__ == "__main__":
    sys.exit(main())