#!/usr/bin/env python3
"""
Enhanced Visual Morphing with MMPA Universal Signal Framework
Building our perfect stable system into the professional MMPA universal signal-to-form engine

This integrates:
- Our stable 10-shape enhanced visual morphing system
- MMPA universal signal processing framework
- Advanced signal-to-form mapping capabilities
- Foundation for any signal type (MIDI, Audio, Sensors, etc.)
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

# Set up logging first (reduced verbosity for performance)
logging.basicConfig(level=logging.WARNING)  # Changed from INFO to WARNING
logger = logging.getLogger(__name__)

# Import our MMPA framework
from mmpa_signal_framework import (
    MMPASignalEngine, SignalType, SignalFeatures, SignalEvent, SignalToFormMapper
)
from mmpa_midi_processor import MIDISignalProcessor
from mmpa_audio_processor import AudioSignalProcessor

# Import performance profiler
try:
    from mmpa_performance_profiler import MMPAPerformanceProfiler
    PROFILER_AVAILABLE = True
except ImportError:
    PROFILER_AVAILABLE = False
    print("⚠️ Performance profiler not available")

# Import revolutionary cinematic rendering engine
try:
    from mmpa_cinematic_rendering import CinematicRenderer, HDRFramebuffer, BloomRenderer
    CINEMATIC_RENDERING_AVAILABLE = True
    logger.info("🎬 Cinematic Rendering Engine imported successfully")
except ImportError as e:
    CINEMATIC_RENDERING_AVAILABLE = False
    logger.warning(f"⚠️ Cinematic Rendering Engine not available: {e}")

# Import our revolutionary procedural geometry engine
try:
    from mmpa_procedural_geometry import ProceduralGeometryEngine
    PROCEDURAL_GEOMETRY_AVAILABLE = True
    logger.info("🔥 Procedural Geometry Engine imported successfully")
except ImportError as e:
    PROCEDURAL_GEOMETRY_AVAILABLE = False
    logger.warning(f"⚠️ Procedural Geometry Engine not available: {e}")

# Import revolutionary interactive analysis system
try:
    from mmpa_interactive_analysis import (
        AnalysisStateManager, AnalysisMode, InteractionMode, AnalysisKeys
    )
    INTERACTIVE_ANALYSIS_AVAILABLE = True
    logger.info("🔬 Interactive Analysis System imported successfully")
except ImportError as e:
    INTERACTIVE_ANALYSIS_AVAILABLE = False
    logger.warning(f"⚠️ Interactive Analysis System not available: {e}")

class MMPAMorphWidget(QOpenGLWidget):
    """Enhanced morphing widget powered by MMPA Universal Signal Framework"""

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
        self.shape_resolution = 25   # EMERGENCY: Ultra-low resolution

        # MMPA Integration
        self.mmpa_engine = MMPASignalEngine()
        self.current_form_params = {}
        self.signal_history = []
        self.audio_amplitude = 0.0  # Track current audio amplitude for dynamic scaling

        # Smooth color transition system
        self.current_color = (0.5, 0.8, 1.0)  # Current HSV color
        self.target_color = (0.5, 0.8, 1.0)   # Target HSV color
        self.color_transition_speed = 0.003    # Much slower color transitions for stability

        # Performance controls
        self.performance_mode = False          # Performance mode toggle
        self.target_fps = 10                   # EMERGENCY: Ultra-low FPS
        self.musical_intelligence_frequency = 200 # EMERGENCY: Process every 200 frames
        self.frame_count = 0                   # Frame counter for throttling

        # Musical Intelligence Integration
        self.current_genre = 'unknown'
        self.current_key = 'C major'
        self.current_chord = 'unknown'
        self.genre_visual_styles = self._setup_genre_visual_styles()
        self.key_color_palettes = self._setup_key_color_palettes()

        # Stability controls to prevent rapid switching
        self.genre_stability_counter = 0
        self.genre_stability_threshold = 50  # EMERGENCY: Much higher stability threshold
        self.pending_genre = 'unknown'
        self.key_stability_counter = 0
        self.key_stability_threshold = 30   # EMERGENCY: Much higher stability threshold
        self.pending_key = 'C major'

        # Cinematic Rendering System
        self.cinematic_engine = None
        self.use_cinematic_rendering = False  # Disabled for performance

        # Revolutionary Procedural Geometry Integration (DISABLED FOR PERFORMANCE)
        self.procedural_engine = None
        # Disabled procedural geometry engine for performance
        # if PROCEDURAL_GEOMETRY_AVAILABLE:
        #     self.procedural_engine = ProceduralGeometryEngine()
        #     logger.info("🚀 Procedural Geometry Engine initialized - infinite shapes available!")

        # Revolutionary Interactive Analysis Integration
        self.analysis_manager = None
        if INTERACTIVE_ANALYSIS_AVAILABLE:
            self.analysis_manager = AnalysisStateManager(self)
            self.analysis_manager.mode_changed.connect(self._on_analysis_mode_changed)
            self.analysis_manager.moment_frozen.connect(self._on_moment_frozen)
            logger.info("🔬 Interactive Analysis System initialized - pause/freeze/analyze capabilities active!")

        # Setup MMPA signal processors
        self._setup_mmpa_processors()

        # Animation timer (adjustable FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self._set_target_fps(self.target_fps)

        logger.info("🎵 MMPA Morph Widget initialized")

        # Performance profiling
        self.profiler = None
        self.show_performance_stats = False
        # EMERGENCY: Disable profiler for performance
        # if PROFILER_AVAILABLE:
        #     self.profiler = MMPAPerformanceProfiler()
        #     self.profiler.start_monitoring()
        #     logger.warning("📊 Performance profiling enabled - Ctrl+P to toggle stats")

        # Enable keyboard focus for analysis controls
        self.setFocusPolicy(Qt.StrongFocus)

    def _set_target_fps(self, fps):
        """Set target FPS and update timer"""
        self.target_fps = fps
        interval = int(1000 / fps)  # Convert to milliseconds
        self.timer.start(interval)
        logger.info(f"⚡ Set target FPS: {fps} (interval: {interval}ms)")

    def set_performance_mode(self, enabled):
        """Toggle performance mode"""
        self.performance_mode = enabled
        if enabled:
            # Performance mode: reduce quality for better FPS
            self._set_target_fps(30)  # Lower FPS
            self.musical_intelligence_frequency = 30  # Process every 30 frames (1fps)
            self.shape_resolution = max(10, self.shape_resolution // 5)  # EMERGENCY: Minimal resolution
            logger.info("⚡ Performance mode ENABLED")
        else:
            # Quality mode: restore full quality
            self._set_target_fps(60)  # Higher FPS
            self.musical_intelligence_frequency = 10  # Process every 10 frames (6fps)
            self.shape_resolution = min(50, self.shape_resolution * 2)   # EMERGENCY: Severely capped
            logger.info("✨ Quality mode ENABLED")

    def _setup_mmpa_processors(self):
        """Setup MMPA signal processors"""
        # MIDI Signal Processor
        midi_processor = MIDISignalProcessor("MPK")
        self.mmpa_engine.register_processor(midi_processor)

        # Enhanced Audio Signal Processor with musical intelligence
        # Try BlackHole first, fall back to default microphone input
        audio_processor = AudioSignalProcessor(device_name="BlackHole")
        self.mmpa_engine.register_processor(audio_processor)

        # Register form generation callback
        self.mmpa_engine.register_form_callback(self._on_signal_to_form)

        # Start the MMPA engine
        self.mmpa_engine.start_engine()

        logger.info("🚀 MMPA Signal Engine integrated with Audio Intelligence")

    def _on_signal_to_form(self, signal_type: SignalType, features: SignalFeatures,
                          events: List[SignalEvent], form_params: Dict[str, float]):
        """Handle signal-to-form transformation from MMPA engine with performance throttling"""

        # Increment frame counter
        self.frame_count += 1

        # Throttle musical intelligence processing based on performance settings
        should_process_intelligence = (self.frame_count % self.musical_intelligence_frequency == 0)

        # Store current form parameters
        self.current_form_params = form_params

        # EMERGENCY: Disable signal history storage for performance
        # Heavy signal history storage disabled to reduce CPU load
        pass

        # Keep last 100 signal frames
        if len(self.signal_history) > 100:
            self.signal_history.pop(0)

        # Apply MMPA mappings to visual system
        self._apply_mmpa_mappings(signal_type, features, events, form_params)

        # Apply advanced musical intelligence mappings (with throttling)
        self._apply_musical_intelligence_mappings(signal_type, features, should_process_intelligence)

    def _apply_mmpa_mappings(self, signal_type: SignalType, features: SignalFeatures,
                            events: List[SignalEvent], form_params: Dict[str, float]):
        """Apply MMPA signal mappings to visual parameters"""

        # Morphing control from frequency mapping
        if 'frequency_to_morph_factor' in form_params:
            self.morph_factor = form_params['frequency_to_morph_factor']

        # Enhanced Musical Intelligence Color Control
        if self.color_mode == 'mmpa_reactive':
            if 'intensity_to_brightness' in form_params:
                # Use signal intensity to control color brightness
                brightness = form_params['intensity_to_brightness']

                # Musical Intelligence-Based Color Mapping
                raw_data = features.raw_data if hasattr(features, 'raw_data') else {}

                # Genre-based color schemes
                genre = raw_data.get('genre', 'unknown')
                if genre != 'unknown':
                    genre_hue = self._get_genre_color(genre)
                    hue = genre_hue
                elif 'frequency_to_hue' in form_params:
                    # Fallback to frequency mapping
                    hue = form_params['frequency_to_hue']
                else:
                    hue = 0.5

                # Key signature color modulation
                key_signature = raw_data.get('key_signature', 'unknown')
                if key_signature != 'unknown':
                    key_confidence = raw_data.get('key_confidence', 0)
                    if key_confidence > 0.4:
                        key_hue_shift = self._get_key_color_shift(key_signature)
                        hue = (hue + key_hue_shift) % 1.0

                # Chord quality affects saturation
                chord_quality = raw_data.get('chord_quality', '')
                saturation = 0.8
                if chord_quality == 'minor':
                    saturation = 0.6  # Softer saturation for minor chords
                elif chord_quality == 'diminished':
                    saturation = 1.0  # High saturation for tension
                elif chord_quality == 'augmented':
                    saturation = 0.9  # Bright saturation for augmented

                # Harmonic tension affects color intensity
                harmonic_tension = raw_data.get('harmonic_tension', 0)
                if harmonic_tension > 0.5:
                    brightness = min(brightness * (1.0 + harmonic_tension * 0.3), 1.0)

                # Store enhanced color
                self.mmpa_color = (hue, saturation, brightness)

        # Enhanced Particle generation from advanced musical events
        for event in events:
            if event.event_type == "note_onset" or event.event_type == "note":
                self._create_mmpa_particle_burst(event, form_params)
            elif event.event_type == "peak" or event.event_type == "volume_peak":
                self._create_mmpa_peak_effect(event, form_params)
            elif event.event_type == "pattern" or event.event_type == "rhythm_pattern":
                self._create_mmpa_pattern_effect(event, form_params)
            elif event.event_type == "beat":
                self._create_beat_effect(event, form_params)
            elif event.event_type == "harmony":
                self._create_harmony_effect(event, form_params)
            # Advanced Musical Intelligence Event Handlers
            elif event.event_type == "tempo":
                self._create_tempo_change_effect(event, form_params)
            elif event.event_type == "texture_change":
                self._create_texture_change_effect(event, form_params)
            elif event.event_type.startswith("freq_emphasis_"):
                self._create_frequency_emphasis_effect(event, form_params)
            elif event.event_type == "chord_change":
                self._create_chord_change_effect(event, form_params)
            elif event.event_type == "key_change":
                self._create_key_change_effect(event, form_params)

        # Scale and motion from complexity
        if 'complexity_to_chaos' in form_params:
            chaos_factor = form_params['complexity_to_chaos']
            # Apply chaos to particle movement
            for particle in self.particles:
                if 'chaos_factor' not in particle:
                    particle['chaos_factor'] = chaos_factor

        # Rotation speed from rhythm
        if 'rhythm_to_pulse_rate' in form_params:
            pulse_rate = form_params['rhythm_to_pulse_rate']
            # Modulate rotation speed
            self.rotation_speed = 0.8 + pulse_rate * 0.5

    def _create_mmpa_particle_burst(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create particle burst based on MMPA signal event"""

        # Use event intensity and form parameters
        particle_count = max(1, int(event.intensity * 5))  # Reduced from 30 to 5
        if 'intensity_to_particle_count' in form_params:
            particle_count = int(form_params['intensity_to_particle_count'])

        # Position from event metadata
        x_pos = 0.0
        if 'note' in event.metadata:
            note = event.metadata['note']
            x_pos = (note - 60) / 30.0  # MIDI note to position

        # Create particles with MMPA-enhanced properties
        for _ in range(particle_count):
            # Velocity influenced by signal complexity
            chaos = form_params.get('complexity_to_chaos', 0.0)
            speed_factor = 0.15 + chaos * 0.1

            vx = (np.random.random() - 0.5) * speed_factor
            vy = np.random.random() * 0.2
            vz = (np.random.random() - 0.5) * speed_factor

            # Color from signal features
            if hasattr(self, 'mmpa_color'):
                hue, sat, val = self.mmpa_color
                r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
            else:
                r, g, b = 1.0, 0.8, 0.2

            particle = {
                'x': x_pos + (np.random.random() - 0.5) * 0.3,
                'y': (np.random.random() - 0.5) * 0.2,
                'z': (np.random.random() - 0.5) * 0.3,
                'vx': vx, 'vy': vy, 'vz': vz,
                'life': 1.5 + np.random.random() * 1.5,
                'r': r, 'g': g, 'b': b,
                'chaos_factor': chaos,
                'signal_intensity': event.intensity
            }
            self.particles.append(particle)

    def _create_mmpa_peak_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create special effect for peak events"""
        # Burst of bright particles for intensity peaks
        for _ in range(20):
            vx = (np.random.random() - 0.5) * 0.3
            vy = np.random.random() * 0.4
            vz = (np.random.random() - 0.5) * 0.3

            particle = {
                'x': 0.0, 'y': 0.0, 'z': 0.0,
                'vx': vx, 'vy': vy, 'vz': vz,
                'life': 2.0,
                'r': 1.0, 'g': 1.0, 'b': 0.8,  # Bright white/yellow
                'peak_effect': True
            }
            self.particles.append(particle)

    def _create_mmpa_pattern_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create special effect for pattern events"""
        pattern_type = event.metadata.get('pattern_type', 'unknown')

        if pattern_type == 'sequence':
            # Flowing particles for melodic sequences
            for i in range(10):
                particle = {
                    'x': -1.0 + i * 0.2,
                    'y': 0.5,
                    'z': 0.0,
                    'vx': 0.1, 'vy': 0.0, 'vz': 0.0,
                    'life': 3.0,
                    'r': 0.2, 'g': 0.8, 'b': 1.0,  # Blue flow
                    'sequence_effect': True
                }
                self.particles.append(particle)

    def _create_beat_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create beat-synchronized effects"""
        bpm = event.metadata.get('bpm', 120)
        intensity = event.intensity

        # Beat ring effect
        for i in range(int(intensity * 15)):
            angle = (i / 15) * 2 * math.pi
            radius = 1.0 + intensity * 0.5

            particle = {
                'x': radius * math.cos(angle),
                'y': 0.0,
                'z': radius * math.sin(angle),
                'vx': 0.1 * math.cos(angle),
                'vy': 0.0,
                'vz': 0.1 * math.sin(angle),
                'life': 1.0,
                'r': 1.0, 'g': 0.2, 'b': 0.2,  # Red beat particles
                'beat_effect': True
            }
            self.particles.append(particle)

    def _create_harmony_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create harmony-based visual effects"""
        peak_count = event.metadata.get('peak_count', 3)
        notes = event.metadata.get('notes', [])

        # Create layered harmony particles
        for i, note in enumerate(notes[:5]):  # Up to 5 harmony notes
            if note != 'N/A':
                # Position based on note
                note_position = (i - 2) * 0.4  # Spread across space

                for _ in range(5):
                    particle = {
                        'x': note_position + (np.random.random() - 0.5) * 0.2,
                        'y': (np.random.random() - 0.5) * 0.3,
                        'z': (np.random.random() - 0.5) * 0.2,
                        'vx': 0.0,
                        'vy': np.random.random() * 0.1,
                        'vz': 0.0,
                        'life': 2.5,
                        'r': 0.6, 'g': 0.8, 'b': 1.0,  # Blue harmony
                        'harmony_note': note
                    }
                    self.particles.append(particle)

    def _create_tempo_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create tempo-based visual effects"""
        bpm = event.metadata.get('bpm', 120)
        intensity = event.intensity

        # Tempo visualization with pulsing
        if bpm > 100:  # Fast tempo
            # Quick burst
            for _ in range(int(intensity * 20)):
                particle = {
                    'x': (np.random.random() - 0.5) * 1.5,
                    'y': (np.random.random() - 0.5) * 1.5,
                    'z': (np.random.random() - 0.5) * 1.5,
                    'vx': (np.random.random() - 0.5) * 0.3,
                    'vy': (np.random.random() - 0.5) * 0.3,
                    'vz': (np.random.random() - 0.5) * 0.3,
                    'life': 0.8,
                    'r': 1.0, 'g': 1.0, 'b': 0.0,  # Yellow fast tempo
                    'tempo_effect': True
                }
                self.particles.append(particle)
        else:  # Slow tempo
            # Gentle drift
            for _ in range(int(intensity * 8)):
                particle = {
                    'x': (np.random.random() - 0.5) * 2.0,
                    'y': (np.random.random() - 0.5) * 2.0,
                    'z': (np.random.random() - 0.5) * 2.0,
                    'vx': (np.random.random() - 0.5) * 0.05,
                    'vy': (np.random.random() - 0.5) * 0.05,
                    'vz': (np.random.random() - 0.5) * 0.05,
                    'life': 3.0,
                    'r': 0.5, 'g': 0.5, 'b': 1.0,  # Blue slow tempo
                    'tempo_effect': True
                }
                self.particles.append(particle)

    def _create_frequency_emphasis_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create effects for frequency band emphasis"""
        band = event.metadata.get('band', 'unknown')
        energy = event.metadata.get('energy', 0.5)

        # Color and position based on frequency band
        band_colors = {
            'bass': (1.0, 0.3, 0.0),      # Red-orange
            'low_mid': (1.0, 0.6, 0.0),   # Orange
            'mid': (1.0, 1.0, 0.0),       # Yellow
            'high_mid': (0.0, 1.0, 0.5),  # Green
            'treble': (0.0, 0.5, 1.0),    # Blue
            'ultra': (0.8, 0.0, 1.0)      # Purple
        }

        band_positions = {
            'bass': -1.5,
            'low_mid': -0.9,
            'mid': -0.3,
            'high_mid': 0.3,
            'treble': 0.9,
            'ultra': 1.5
        }

        if band in band_colors:
            r, g, b = band_colors[band]
            y_pos = band_positions[band]

            # Create emphasis particles
            particle_count = int(energy * 3)  # Reduced from 15 to 3
            for _ in range(particle_count):
                particle = {
                    'x': (np.random.random() - 0.5) * 0.5,
                    'y': y_pos + (np.random.random() - 0.5) * 0.3,
                    'z': (np.random.random() - 0.5) * 0.5,
                    'vx': (np.random.random() - 0.5) * 0.1,
                    'vy': 0.0,
                    'vz': (np.random.random() - 0.5) * 0.1,
                    'life': 1.5,
                    'r': r, 'g': g, 'b': b,
                    'freq_emphasis': band
                }
                self.particles.append(particle)

    def _setup_genre_visual_styles(self) -> Dict[str, Dict[str, Any]]:
        """Setup visual styles for different musical genres"""
        return {
            'rock': {
                'color_scheme': 'high_contrast',
                'particle_intensity': 1.2,
                'morph_speed': 1.5,
                'chaos_factor': 0.8,
                'preferred_shapes': ['cube', 'pyramid'],
                'particle_size_multiplier': 1.3
            },
            'jazz': {
                'color_scheme': 'smooth_gradients',
                'particle_intensity': 0.8,
                'morph_speed': 0.7,
                'chaos_factor': 0.9,
                'preferred_shapes': ['sphere', 'torus'],
                'particle_size_multiplier': 0.9
            },
            'classical': {
                'color_scheme': 'elegant_pastels',
                'particle_intensity': 0.6,
                'morph_speed': 0.5,
                'chaos_factor': 0.3,
                'preferred_shapes': ['sphere', 'dodecahedron'],
                'particle_size_multiplier': 0.8
            },
            'electronic': {
                'color_scheme': 'neon_bright',
                'particle_intensity': 1.5,
                'morph_speed': 2.0,
                'chaos_factor': 1.2,
                'preferred_shapes': ['cube', 'octahedron'],
                'particle_size_multiplier': 1.5
            },
            'pop': {
                'color_scheme': 'vibrant_rainbow',
                'particle_intensity': 1.0,
                'morph_speed': 1.0,
                'chaos_factor': 0.6,
                'preferred_shapes': ['sphere', 'cube'],
                'particle_size_multiplier': 1.0
            },
            'blues': {
                'color_scheme': 'blue_spectrum',
                'particle_intensity': 0.7,
                'morph_speed': 0.8,
                'chaos_factor': 0.5,
                'preferred_shapes': ['torus', 'sphere'],
                'particle_size_multiplier': 0.9
            },
            'folk': {
                'color_scheme': 'earth_tones',
                'particle_intensity': 0.5,
                'morph_speed': 0.6,
                'chaos_factor': 0.2,
                'preferred_shapes': ['sphere', 'torus'],
                'particle_size_multiplier': 0.7
            },
            'reggae': {
                'color_scheme': 'rasta_colors',
                'particle_intensity': 0.9,
                'morph_speed': 0.9,
                'chaos_factor': 0.4,
                'preferred_shapes': ['torus', 'sphere'],
                'particle_size_multiplier': 1.1
            }
        }

    def _setup_key_color_palettes(self) -> Dict[str, tuple]:
        """Setup color palettes for different musical keys"""
        return {
            # Major keys - brighter, warmer colors
            'C major': (0.0, 0.8, 1.0),      # Pure red
            'G major': (0.1, 0.9, 1.0),      # Orange-red
            'D major': (0.15, 0.9, 1.0),     # Orange
            'A major': (0.2, 0.8, 1.0),      # Yellow-orange
            'E major': (0.25, 0.9, 1.0),     # Yellow
            'B major': (0.3, 0.8, 1.0),      # Yellow-green
            'F# major': (0.4, 0.9, 1.0),     # Green
            'C# major': (0.5, 0.8, 1.0),     # Cyan
            'F major': (0.55, 0.9, 1.0),     # Light blue
            'Bb major': (0.6, 0.8, 1.0),     # Blue
            'Eb major': (0.7, 0.9, 1.0),     # Purple-blue
            'Ab major': (0.8, 0.8, 1.0),     # Purple

            # Minor keys - darker, more subdued colors
            'A minor': (0.0, 0.6, 0.7),      # Dark red
            'E minor': (0.1, 0.7, 0.8),      # Dark orange
            'B minor': (0.15, 0.6, 0.7),     # Dark orange-brown
            'F# minor': (0.2, 0.7, 0.8),     # Dark yellow
            'C# minor': (0.25, 0.6, 0.7),    # Olive
            'G# minor': (0.3, 0.7, 0.8),     # Dark green
            'D# minor': (0.4, 0.6, 0.7),     # Teal
            'A# minor': (0.5, 0.7, 0.8),     # Dark cyan
            'D minor': (0.55, 0.6, 0.7),     # Dark blue
            'G minor': (0.6, 0.7, 0.8),      # Navy
            'C minor': (0.7, 0.6, 0.7),      # Dark purple
            'F minor': (0.8, 0.7, 0.8),      # Dark magenta
        }

    def _apply_musical_intelligence_mappings(self, signal_type: SignalType, features: SignalFeatures, should_process_intelligence: bool):
        """Apply advanced musical intelligence to visual parameters with performance throttling"""
        if signal_type != SignalType.AUDIO:
            return

        raw_data = features.raw_data

        # Only process intensive musical intelligence if throttling allows it
        if should_process_intelligence:
            # Genre-based visual styling with stability control
            genre = raw_data.get('genre', 'unknown')
            if genre != 'unknown':
                # Check if this is the same genre we're tracking
                if genre == self.pending_genre:
                    self.genre_stability_counter += 1
                    # Apply genre change only after stability threshold is met
                    if self.genre_stability_counter >= self.genre_stability_threshold and genre != self.current_genre:
                        self.current_genre = genre
                        self._apply_genre_visual_style(genre)
                        # Reset counter after successful application
                        self.genre_stability_counter = 0
                else:
                    # New genre detected, start tracking it
                    self.pending_genre = genre
                    self.genre_stability_counter = 1

            # Key signature-based color palette with stability control
            key_signature = raw_data.get('key_signature', 'C major')
            if key_signature == self.pending_key:
                self.key_stability_counter += 1
                # Apply key change only after stability threshold is met
                if self.key_stability_counter >= self.key_stability_threshold and key_signature != self.current_key:
                    self.current_key = key_signature
                    self._apply_key_color_palette(key_signature)
                    # Reset counter after successful application
                    self.key_stability_counter = 0
            else:
                # New key detected, start tracking it
                self.pending_key = key_signature
                self.key_stability_counter = 1

            # Chord progression-based form transformation
            chord = raw_data.get('chord', 'unknown')
            if chord != 'unknown' and chord != self.current_chord:
                self.current_chord = chord
                self._apply_chord_transformation(chord, raw_data)

        # Advanced pattern-based effects
        self._apply_advanced_pattern_effects(features, raw_data)

    def _apply_genre_visual_style(self, genre: str):
        """Apply visual style based on detected genre"""
        style = self.genre_visual_styles.get(genre, self.genre_visual_styles['pop'])

        # Update particle system parameters
        self.particle_size = 6.0 * style['particle_size_multiplier']

        # Update shape preferences
        preferred_shapes = style['preferred_shapes']
        if len(preferred_shapes) >= 2:
            self.shape_a = preferred_shapes[0]
            self.shape_b = preferred_shapes[1]

        # Update animation speed
        self.rotation_speed = 0.8 * style['morph_speed']

        # Reduced logging for performance - only log major changes
        if hasattr(self, 'last_logged_genre') and self.last_logged_genre != genre:
            logger.warning(f"🎭 Applied {genre} visual style")  # Changed to warning level
            self.last_logged_genre = genre

    def _apply_key_color_palette(self, key_signature: str):
        """Apply color palette based on detected key signature with smooth transition"""
        if key_signature in self.key_color_palettes:
            hue, sat, val = self.key_color_palettes[key_signature]
            # Set target color for smooth transition instead of instant change
            self.target_color = (hue, sat, val)
            # Reduced logging for performance - only log major changes
            if hasattr(self, 'last_logged_key') and self.last_logged_key != key_signature:
                logger.warning(f"🎨 Transitioning to {key_signature} color palette")  # Changed to warning level
                self.last_logged_key = key_signature

    def _apply_chord_transformation(self, chord: str, raw_data: Dict):
        """Apply form transformation based on chord detection"""
        # Major chords - more rounded shapes
        if 'm' not in chord and '°' not in chord:
            # Major chord - smoother morphing
            if hasattr(self, 'current_morph_style'):
                self.current_morph_style = 'smooth'

        # Minor chords - more angular shapes
        elif 'm' in chord:
            # Minor chord - more angular morphing
            if hasattr(self, 'current_morph_style'):
                self.current_morph_style = 'angular'

        # Harmonic tension influences chaos
        harmonic_tension = raw_data.get('harmonic_tension', 0.0)
        if harmonic_tension > 0.5:
            # High tension - add visual chaos
            for particle in self.particles:
                if 'tension_factor' not in particle:
                    particle['tension_factor'] = harmonic_tension

    def _apply_advanced_pattern_effects(self, features: SignalFeatures, raw_data: Dict):
        """Apply effects based on advanced musical patterns"""
        patterns = features.patterns

        if len(patterns) >= 8:
            # Use advanced pattern data
            rhythmic_complexity = patterns[0]
            groove_factor = patterns[1]
            melody_stability = patterns[2]
            harmonic_richness = patterns[7]

            # Groove factor influences particle movement
            if groove_factor > 0.5:
                self._create_groove_particles(groove_factor)

            # Harmonic richness influences particle count
            if harmonic_richness > 0.3:
                self._create_harmony_particles(harmonic_richness)

            # Melody stability influences color consistency
            if melody_stability > 0.7:
                # Stable melody - consistent colors
                if hasattr(self, 'mmpa_color'):
                    # Keep color stable
                    pass

    def _create_groove_particles(self, groove_factor: float):
        """Create special particles for groove patterns"""
        if np.random.random() < groove_factor * 0.1:  # Occasional groove bursts
            for _ in range(int(groove_factor * 10)):
                particle = {
                    'x': (np.random.random() - 0.5) * 2.0,
                    'y': (np.random.random() - 0.5) * 0.5,
                    'z': (np.random.random() - 0.5) * 2.0,
                    'vx': (np.random.random() - 0.5) * 0.1,
                    'vy': np.random.random() * 0.05,
                    'vz': (np.random.random() - 0.5) * 0.1,
                    'life': 2.0,
                    'r': 1.0, 'g': 0.6, 'b': 0.0,  # Golden groove particles
                    'groove_effect': True
                }
                self.particles.append(particle)

    def _create_harmony_particles(self, harmonic_richness: float):
        """Create particles representing harmonic content"""
        if np.random.random() < harmonic_richness * 0.05:  # Rich harmony bursts
            particle_count = int(harmonic_richness * 4)  # Reduced from 20 to 4
            for i in range(particle_count):
                # Arrange particles in harmonic formations
                angle = (i / particle_count) * 2 * math.pi
                radius = 0.8 + harmonic_richness * 0.5

                particle = {
                    'x': radius * math.cos(angle),
                    'y': (np.random.random() - 0.5) * 0.3,
                    'z': radius * math.sin(angle),
                    'vx': -0.1 * math.cos(angle),
                    'vy': 0.0,
                    'vz': -0.1 * math.sin(angle),
                    'life': 3.0,
                    'r': 0.8, 'g': 0.4, 'b': 1.0,  # Purple harmony particles
                    'harmony_effect': True
                }
                self.particles.append(particle)

    def _get_genre_color(self, genre: str) -> float:
        """Get color hue for a specific music genre"""
        genre_colors = {
            'rock': 0.0,        # Red - energetic
            'jazz': 0.6,        # Blue - sophisticated
            'classical': 0.75,  # Purple - elegant
            'electronic': 0.5,  # Cyan - modern
            'folk': 0.25,       # Green - natural
            'pop': 0.9,         # Pink - bright
            'blues': 0.65,      # Deep blue - soulful
            'reggae': 0.3,      # Yellow-green - relaxed
            'country': 0.15,    # Orange - warm
            'metal': 0.0,       # Red - intense
            'ambient': 0.55,    # Light blue - ethereal
            'hip_hop': 0.8      # Magenta - urban
        }
        return genre_colors.get(genre, 0.5)  # Default to cyan

    def _get_key_color_shift(self, key_signature: str) -> float:
        """Get color shift for key signature"""
        # Map musical keys to color wheel positions
        key_shifts = {
            'C major': 0.0, 'G major': 0.1, 'D major': 0.2, 'A major': 0.3,
            'E major': 0.4, 'B major': 0.5, 'F# major': 0.6, 'C# major': 0.7,
            'F major': 0.9, 'Bb major': 0.8, 'Eb major': 0.7, 'Ab major': 0.6,
            'A minor': 0.85, 'E minor': 0.75, 'B minor': 0.65, 'F# minor': 0.55,
            'C# minor': 0.45, 'G# minor': 0.35, 'D# minor': 0.25, 'A# minor': 0.15,
            'D minor': 0.05, 'G minor': 0.95, 'C minor': 0.15, 'F minor': 0.25
        }
        return key_shifts.get(key_signature, 0.0)

    def _create_tempo_change_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create visual effect for tempo changes"""
        bpm = event.metadata.get('bpm', 120)
        # Adjust animation speed based on tempo
        tempo_factor = min(bpm / 120.0, 2.0)  # Cap at 2x speed
        self.rotation_speed = 0.5 * tempo_factor

        # Create tempo indication particles
        if bpm > 140:  # Fast tempo
            # Rapid, small particles
            for _ in range(int(bpm / 20)):
                self._create_tempo_particle(size=0.5, speed=0.3)
        elif bpm < 80:  # Slow tempo
            # Large, slow particles
            for _ in range(3):
                self._create_tempo_particle(size=2.0, speed=0.1)

    def _create_tempo_particle(self, size: float, speed: float):
        """Create a single tempo indicator particle"""
        particle = {
            'x': (np.random.random() - 0.5) * 1.5,
            'y': (np.random.random() - 0.5) * 0.5,
            'z': (np.random.random() - 0.5) * 1.5,
            'vx': (np.random.random() - 0.5) * speed,
            'vy': 0.0,
            'vz': (np.random.random() - 0.5) * speed,
            'life': 2.0,
            'r': 1.0, 'g': 1.0, 'b': 0.3,  # Yellow tempo particles
            'size': size
        }
        self.particles.append(particle)

    def _create_texture_change_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create visual effect for texture/complexity changes"""
        entropy = event.metadata.get('entropy', 0)
        # More complex textures = more chaotic particle movement
        chaos_level = min(entropy / 5.0, 1.0)

        # Create swirling particle patterns for texture changes
        particle_count = int(chaos_level * 5)  # Reduced from 30 to 5
        for i in range(particle_count):
            angle = (i / particle_count) * 2 * math.pi
            radius = 0.5 + chaos_level * 0.8

            particle = {
                'x': radius * math.cos(angle),
                'y': (np.random.random() - 0.5) * chaos_level,
                'z': radius * math.sin(angle),
                'vx': -0.2 * math.sin(angle) * chaos_level,
                'vy': (np.random.random() - 0.5) * 0.1,
                'vz': 0.2 * math.cos(angle) * chaos_level,
                'life': 2.5,
                'r': chaos_level, 'g': 0.5, 'b': 1.0 - chaos_level,
                'texture_effect': True
            }
            self.particles.append(particle)

    def _create_frequency_emphasis_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create visual effect for frequency band emphasis"""
        band_name = event.metadata.get('band', 'unknown')
        band_energy = event.metadata.get('energy', 0.5)

        # Different colors and positions for different frequency bands
        band_effects = {
            'bass': {'color': (1.0, 0.2, 0.2), 'y_pos': -1.0, 'size': 3.0},
            'low_mid': {'color': (1.0, 0.6, 0.2), 'y_pos': -0.5, 'size': 2.5},
            'mid': {'color': (1.0, 1.0, 0.2), 'y_pos': 0.0, 'size': 2.0},
            'high_mid': {'color': (0.6, 1.0, 0.2), 'y_pos': 0.5, 'size': 1.5},
            'treble': {'color': (0.2, 1.0, 0.6), 'y_pos': 1.0, 'size': 1.0},
            'ultra': {'color': (0.2, 0.6, 1.0), 'y_pos': 1.5, 'size': 0.8}
        }

        if band_name in band_effects:
            effect = band_effects[band_name]
            particle_count = int(band_energy * 3)  # Reduced from 15 to 3

            for _ in range(particle_count):
                particle = {
                    'x': (np.random.random() - 0.5) * 2.0,
                    'y': effect['y_pos'] + (np.random.random() - 0.5) * 0.3,
                    'z': (np.random.random() - 0.5) * 2.0,
                    'vx': (np.random.random() - 0.5) * 0.1,
                    'vy': 0.0,
                    'vz': (np.random.random() - 0.5) * 0.1,
                    'life': 1.5,
                    'r': effect['color'][0],
                    'g': effect['color'][1],
                    'b': effect['color'][2],
                    'size': effect['size'] * band_energy,
                    'freq_band': band_name
                }
                self.particles.append(particle)

    def _create_chord_change_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create visual effect for chord changes"""
        # Create harmonic burst pattern
        for i in range(8):  # 8 particles in harmonic formation
            angle = (i / 8.0) * 2 * math.pi
            radius = 1.2

            particle = {
                'x': radius * math.cos(angle),
                'y': 0.0,
                'z': radius * math.sin(angle),
                'vx': 0.05 * math.cos(angle),
                'vy': 0.0,
                'vz': 0.05 * math.sin(angle),
                'life': 3.0,
                'r': 0.9, 'g': 0.7, 'b': 1.0,  # Lavender for chord changes
                'chord_effect': True
            }
            self.particles.append(particle)

    def _create_key_change_effect(self, event: SignalEvent, form_params: Dict[str, float]):
        """Create visual effect for key signature changes"""
        # Major key change = upward spiral, minor = downward spiral
        key_type = 'major' if 'major' in event.metadata.get('key', '') else 'minor'
        direction = 1 if key_type == 'major' else -1

        # Create spiraling particle effect
        for i in range(20):
            t = i / 20.0
            angle = t * 4 * math.pi  # Two full rotations
            radius = 0.3 + t * 0.8
            y_pos = direction * t * 1.5

            particle = {
                'x': radius * math.cos(angle),
                'y': y_pos,
                'z': radius * math.sin(angle),
                'vx': -0.1 * math.sin(angle),
                'vy': direction * 0.05,
                'vz': 0.1 * math.cos(angle),
                'life': 4.0,
                'r': 1.0 if key_type == 'major' else 0.7,
                'g': 0.8,
                'b': 0.7 if key_type == 'major' else 1.0,
                'key_effect': True
            }
            self.particles.append(particle)

    # Include all the perfect geometry methods from our stable system
    def initializeGL(self):
        """Initialize OpenGL with enhanced settings and cinematic rendering"""
        glClearColor(0.02, 0.02, 0.08, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPointSize(2.0)

        # Initialize cinematic rendering engine
        if CINEMATIC_RENDERING_AVAILABLE and self.use_cinematic_rendering:
            try:
                self.cinematic_engine = CinematicRenderer(self.width(), self.height())
                logger.info("🎬 Cinematic HDR+Bloom+PBR rendering engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize cinematic rendering: {e}")
                self.cinematic_engine = None

        logger.info("✅ Enhanced OpenGL initialized")

    def resizeGL(self, width, height):
        """Handle resize with cinematic engine support"""
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height if height > 0 else 1
        glFrustum(-aspect, aspect, -1.0, 1.0, 2.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

        # Resize cinematic engine framebuffers
        if self.cinematic_engine:
            self.cinematic_engine.resize(width, height)

    def paintGL(self):
        """Render enhanced multi-layer morphing visualization"""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            # Dynamic camera setup
            rotation_speed = getattr(self, 'rotation_speed', 0.8)
            glTranslatef(0.0, 0.0, -6.0)
            glRotatef(self.rotation * rotation_speed, 1.0, 1.0, 0.0)
            glRotatef(self.rotation * 0.3, 0.0, 1.0, 0.0)

            # SIMPLIFIED RENDERING FOR PERFORMANCE
            # Render single shape instead of multi-layer
            self._render_simple_shape()

            # Render basic particles (reduced complexity)
            self._render_basic_particles()

        except Exception as e:
            logger.error(f"Render error: {e}")

    def _render_simple_shape(self):
        """Render single simple shape for performance"""
        # Apply current color
        h, s, v = self.current_color
        glColor3f(h, s, v)

        # Simple sphere with minimal vertices
        glBegin(GL_TRIANGLES)
        for i in range(12):  # Ultra-low resolution: 12 triangles only
            angle = i * math.pi * 2 / 12
            next_angle = (i + 1) * math.pi * 2 / 12

            # Simple triangle fan
            glVertex3f(0, 0, 0)  # Center
            glVertex3f(math.cos(angle), math.sin(angle), 0)
            glVertex3f(math.cos(next_angle), math.sin(next_angle), 0)
        glEnd()

    def _render_basic_particles(self):
        """Render basic particles with minimal complexity"""
        if not hasattr(self, 'particles') or len(self.particles) == 0:
            return

        glPointSize(2.0)
        glBegin(GL_POINTS)

        # Only render first 20 particles for performance
        for particle in self.particles[:20]:
            glColor3f(0.8, 0.8, 1.0)  # Simple blue color
            glVertex3f(particle['x'], particle['y'], particle['z'])

        glEnd()

    def render_multi_layer_morphing(self):
        """Render multiple morphing layers at different scales and speeds"""
        # Store current state
        current_morph = self.morph_factor

        # Layer 1: Main shape (full size)
        glPushMatrix()
        vertices = self.generate_morphed_shape()
        self.render_morphed_shape(vertices)
        glPopMatrix()

        # Layer 2: Secondary shape (70% size, different rotation)
        glPushMatrix()
        glRotatef(self.rotation * 0.5, 0.0, 0.0, 1.0)  # Different rotation axis
        glScalef(0.7, 0.7, 0.7)

        # Use a different morph phase for variety
        self.morph_factor = (current_morph + 0.3) % 1.0
        vertices2 = self.generate_morphed_shape()

        # Semi-transparent rendering for layering effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Store original render method behavior
        original_amplitude = self.audio_amplitude
        self.audio_amplitude *= 0.6  # Reduced pulse for secondary layer

        self.render_morphed_shape(vertices2)

        # Restore original amplitude
        self.audio_amplitude = original_amplitude
        glPopMatrix()

        # Layer 3: Tertiary shape (40% size, counter-rotation)
        glPushMatrix()
        glRotatef(-self.rotation * 0.8, 1.0, 0.0, 0.0)  # Counter-rotation
        glScalef(0.4, 0.4, 0.4)

        # Another different morph phase
        self.morph_factor = (current_morph + 0.6) % 1.0
        vertices3 = self.generate_morphed_shape()

        # Even more transparent for innermost layer
        self.audio_amplitude *= 0.3  # Minimal pulse for tertiary layer

        self.render_morphed_shape(vertices3)

        # Restore original amplitude and morph factor
        self.audio_amplitude = original_amplitude
        self.morph_factor = current_morph

        glDisable(GL_BLEND)
        glPopMatrix()

    def hsv_to_rgb(self, h, s, v):
        """Convert HSV to RGB color space for proper rainbow colors"""
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
        """Generate vertices for morphed shape with extended library"""
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
        """Smooth easing function for morphing"""
        return t * t * (3.0 - 2.0 * t)

    def generate_shape(self, shape_name):
        """Generate vertices for extended shape library with perfect geometry"""
        vertices = []
        num_points = self.shape_resolution

        if shape_name == 'sphere':
            # Perfect sphere with Fibonacci spiral distribution
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

                        if face == 0:    vertices.append([u, v, 1.0])
                        elif face == 1:  vertices.append([u, v, -1.0])
                        elif face == 2:  vertices.append([1.0, u, v])
                        elif face == 3:  vertices.append([-1.0, u, v])
                        elif face == 4:  vertices.append([u, 1.0, v])
                        else:            vertices.append([u, -1.0, v])

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

        elif shape_name == 'dodecahedron':
            # Perfect dodecahedron with 12 pentagonal faces
            phi = (1 + math.sqrt(5)) / 2  # Golden ratio
            vertices_base = [
                # Cube vertices
                [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
                [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1],
                # Rectangle vertices
                [0, 1/phi, phi], [0, 1/phi, -phi], [0, -1/phi, phi], [0, -1/phi, -phi],
                [1/phi, phi, 0], [1/phi, -phi, 0], [-1/phi, phi, 0], [-1/phi, -phi, 0],
                [phi, 0, 1/phi], [phi, 0, -1/phi], [-phi, 0, 1/phi], [-phi, 0, -1/phi]
            ]
            # Normalize and distribute points
            for i in range(num_points):
                base_idx = i % len(vertices_base)
                vertex = vertices_base[base_idx]
                # Normalize
                length = math.sqrt(sum(x*x for x in vertex))
                if length > 0:
                    normalized = [x/length for x in vertex]
                    vertices.append(normalized)

        elif shape_name == 'icosahedron':
            # Perfect icosahedron with 20 triangular faces
            phi = (1 + math.sqrt(5)) / 2  # Golden ratio
            vertices_base = [
                # Rectangle in xy-plane
                [0, 1, phi], [0, 1, -phi], [0, -1, phi], [0, -1, -phi],
                # Rectangle in xz-plane
                [1, phi, 0], [1, -phi, 0], [-1, phi, 0], [-1, -phi, 0],
                # Rectangle in yz-plane
                [phi, 0, 1], [phi, 0, -1], [-phi, 0, 1], [-phi, 0, -1]
            ]
            # Normalize and distribute points
            for i in range(num_points):
                base_idx = i % len(vertices_base)
                vertex = vertices_base[base_idx]
                # Normalize
                length = math.sqrt(sum(x*x for x in vertex))
                if length > 0:
                    normalized = [x/length for x in vertex]
                    vertices.append(normalized)

        elif shape_name == 'klein_bottle':
            # Klein bottle parametric surface
            for i in range(num_points):
                u = (i / num_points) * 2 * math.pi
                v = ((i * 7) % num_points) / num_points * 2 * math.pi

                if u < math.pi:
                    x = 6 * math.cos(u) * (1 + math.sin(u)) + 4 * (1 - math.cos(u) / 2) * math.cos(u) * math.cos(v)
                    y = 16 * math.sin(u) + 4 * (1 - math.cos(u) / 2) * math.sin(u) * math.cos(v)
                else:
                    x = 6 * math.cos(u) * (1 + math.sin(u)) + 4 * (1 - math.cos(u) / 2) * math.cos(v + math.pi)
                    y = 16 * math.sin(u)
                z = 4 * (1 - math.cos(u) / 2) * math.sin(v)

                # Scale down to fit
                scale = 0.1
                vertices.append([x * scale, y * scale, z * scale])

        elif shape_name == 'mobius_strip':
            # Möbius strip parametric surface
            for i in range(num_points):
                u = (i / num_points) * 2 * math.pi
                v = ((i * 3) % num_points) / num_points * 2 - 1  # v from -1 to 1

                x = (1 + v/2 * math.cos(u/2)) * math.cos(u)
                y = (1 + v/2 * math.cos(u/2)) * math.sin(u)
                z = v/2 * math.sin(u/2)

                vertices.append([x, y, z])

        elif shape_name == 'helix':
            # 3D helix/spiral
            for i in range(num_points):
                t = (i / num_points) * 8 * math.pi  # Multiple turns
                radius = 0.8
                x = radius * math.cos(t)
                y = (i / num_points) * 4 - 2  # Height from -2 to 2
                z = radius * math.sin(t)
                vertices.append([x, y, z])

        elif shape_name == 'octahedron':
            # Perfect octahedron (8 triangular faces)
            vertices_base = [
                [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]
            ]
            # Distribute points evenly
            for i in range(num_points):
                base_idx = i % len(vertices_base)
                vertices.append(vertices_base[base_idx])

        # Revolutionary Procedural Geometry Integration (DISABLED FOR PERFORMANCE)
        # elif self.procedural_engine and shape_name in ['l_system_tree', 'mandelbrot_3d', 'perlin_terrain',
        #                                                'voronoi_cells', 'dna_helix', 'crystal_lattice',
        #                                                'mathematical_surface']:
        # Disabled procedural geometry for performance - fallback to simple sphere
        elif shape_name in ['l_system_tree', 'mandelbrot_3d', 'perlin_terrain',
                           'voronoi_cells', 'dna_helix', 'crystal_lattice',
                           'mathematical_surface']:
            # Fallback to simple sphere for procedural shapes (performance)
            for i in range(num_points):
                u = (i / num_points) * 2 * math.pi
                v = ((i // int(math.sqrt(num_points))) / int(math.sqrt(num_points))) * math.pi
                x = math.sin(v) * math.cos(u)
                y = math.sin(v) * math.sin(u)
                z = math.cos(v)
                vertices.append((x, y, z))

        # Add all other shapes from our stable system...
        else:
            return self.generate_shape('sphere')

        return vertices

    def render_morphed_shape(self, vertices):
        """Render the morphed shape with enhanced effects and dynamic scaling"""
        if not vertices:
            return

        # Calculate dynamic scale factor based on audio amplitude
        base_scale = 1.0
        pulse_scale = 0.2 + (self.audio_amplitude * 0.8)  # Scale from 0.2 to 1.0
        breathing_effect = 0.1 * math.sin(time.time() * 3)  # Gentle breathing
        total_scale = base_scale * pulse_scale + breathing_effect

        if self.color_mode == 'rainbow':
            hue = self.morph_factor
            r, g, b = self.hsv_to_rgb(hue, 1.0, 0.9)
            glColor3f(r, g, b)
        elif self.color_mode == 'mmpa_reactive':
            if hasattr(self, 'mmpa_color'):
                hue, sat, val = self.mmpa_color
                r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
                glColor3f(r, g, b)
            else:
                glColor3f(0.3, 0.8, 1.0)
        else:
            glColor3f(0.3, 0.8, 1.0)

        # Dynamic point size based on amplitude
        dynamic_point_size = 2.5 + (self.audio_amplitude * 3.0)
        glPointSize(dynamic_point_size)

        glBegin(GL_POINTS)
        for vertex in vertices:
            # Apply dynamic scaling to each vertex
            scaled_x = vertex[0] * total_scale
            scaled_y = vertex[1] * total_scale
            scaled_z = vertex[2] * total_scale
            glVertex3f(scaled_x, scaled_y, scaled_z)
        glEnd()

    def render_enhanced_particles(self):
        """Render particles with enhanced effects and trails"""
        if not self.particles:
            return

        # Enable better blending for particles
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for glow

        # Render trails first (behind particles)
        if self.particle_trails:
            self._render_particle_trails()

        # Fixed particle rendering - can't change point size inside glBegin/glEnd
        glPointSize(self.particle_size)  # Set base point size

        glBegin(GL_POINTS)

        for particle in self.particles:
            if particle['life'] > 0:
                life_factor = min(particle['life'], 1.0)

                # Enhanced color calculations
                r = particle.get('r', 1.0) * life_factor
                g = particle.get('g', 0.8) * life_factor
                b = particle.get('b', 0.2) * life_factor
                alpha = life_factor * 0.9

                # Special effects for different particle types
                if particle.get('peak_effect'):
                    # Bright pulsing for peaks
                    pulse = 0.7 + 0.3 * math.sin(time.time() * 15)
                    r *= pulse * 1.5
                    g *= pulse * 1.5
                    b *= pulse * 1.5

                elif particle.get('harmony_effect'):
                    # Gentle pulsing for harmony
                    pulse = 0.8 + 0.2 * math.sin(time.time() * 8)
                    r *= pulse
                    g *= pulse
                    b *= pulse

                elif particle.get('chord_effect'):
                    # Rich colors for chords
                    r = min(r * 1.2, 1.0)
                    alpha *= 1.1

                glColor4f(r, g, b, alpha)
                glVertex3f(particle['x'], particle['y'], particle['z'])

        glEnd()

        # Reset blending
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def _render_particle_trails(self):
        """Render particle trails with fading effect"""
        glLineWidth(1.0)

        for particle in self.particles:
            if 'trail' in particle and len(particle['trail']) > 1:
                trail = particle['trail']
                life_factor = min(particle['life'], 1.0)

                # Base colors from particle
                base_r = particle.get('r', 1.0)
                base_g = particle.get('g', 0.8)
                base_b = particle.get('b', 0.2)

                # Render trail as line strip with fading
                glBegin(GL_LINE_STRIP)
                for i, pos in enumerate(trail):
                    # Fade from oldest (transparent) to newest (more opaque)
                    trail_factor = (i / len(trail)) * life_factor * 0.5
                    glColor4f(base_r * trail_factor, base_g * trail_factor,
                             base_b * trail_factor, trail_factor)
                    glVertex3f(pos[0], pos[1], pos[2])
                glEnd()

    def update_animation(self):
        """Update animation with enhanced physics and trail effects"""
        self.rotation += getattr(self, 'rotation_speed', 0.8)

        # Smooth color transitions
        self._update_color_transition()

        # Update particles with enhanced physics
        for particle in self.particles[:]:
            particle['life'] -= 0.015

            # Store previous position for trails
            if 'trail' not in particle:
                particle['trail'] = []

            # Add current position to trail
            if self.particle_trails:
                particle['trail'].append([particle['x'], particle['y'], particle['z']])
                # Limit trail length to prevent memory issues
                if len(particle['trail']) > 15:
                    particle['trail'].pop(0)

            # Enhanced gravity with center attraction
            center_x, center_y, center_z = 0.0, 0.0, 0.0
            dx = center_x - particle['x']
            dy = center_y - particle['y']
            dz = center_z - particle['z']
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)

            if distance > 0.1:  # Avoid division by zero
                # Gravitational attraction to center
                gravity_strength = 0.002
                gravity_force = gravity_strength / (distance * distance + 0.1)
                particle['vx'] += dx * gravity_force
                particle['vy'] += dy * gravity_force
                particle['vz'] += dz * gravity_force

            # Apply movement with enhanced chaos
            chaos = particle.get('chaos_factor', 0.0)
            chaos_x = (np.random.random() - 0.5) * chaos * 0.001
            chaos_y = (np.random.random() - 0.5) * chaos * 0.001
            chaos_z = (np.random.random() - 0.5) * chaos * 0.001

            particle['x'] += particle['vx'] * 0.02 + chaos_x
            particle['y'] += particle['vy'] * 0.02 + chaos_y
            particle['z'] += particle['vz'] * 0.02 + chaos_z

            # Add downward gravity
            particle['vy'] -= 0.002

            # Velocity damping for more realistic motion
            damping = 0.98
            particle['vx'] *= damping
            particle['vy'] *= damping
            particle['vz'] *= damping

            if particle['life'] <= 0:
                self.particles.remove(particle)

        self.update()

    def _update_color_transition(self):
        """Smoothly interpolate between current and target colors"""
        if self.current_color != self.target_color:
            # Linear interpolation for each HSV component
            curr_h, curr_s, curr_v = self.current_color
            targ_h, targ_s, targ_v = self.target_color

            # Handle hue wrap-around (shortest path on color wheel)
            hue_diff = targ_h - curr_h
            if hue_diff > 0.5:
                hue_diff -= 1.0
            elif hue_diff < -0.5:
                hue_diff += 1.0

            # Interpolate each component
            new_h = (curr_h + hue_diff * self.color_transition_speed) % 1.0
            new_s = curr_s + (targ_s - curr_s) * self.color_transition_speed
            new_v = curr_v + (targ_v - curr_v) * self.color_transition_speed

            self.current_color = (new_h, new_s, new_v)

            # Update mmpa_color for the rendering system
            self.mmpa_color = self.current_color

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

    # ========================================
    # REVOLUTIONARY INTERACTIVE ANALYSIS MODE
    # ========================================

    def keyPressEvent(self, event):
        """Handle keyboard input for analysis mode"""
        if not INTERACTIVE_ANALYSIS_AVAILABLE or not self.analysis_manager:
            super().keyPressEvent(event)
            return

        key = event.key()

        try:
            if key == AnalysisKeys.PAUSE_RESUME:
                self._toggle_pause_resume()
                event.accept()
            elif key == AnalysisKeys.FREEZE:
                self._freeze_current_moment()
                event.accept()
            elif key == AnalysisKeys.INSPECTION:
                self._enter_inspection_mode()
                event.accept()
            elif key == AnalysisKeys.LABELING:
                self._enter_labeling_mode()
                event.accept()
            elif key == AnalysisKeys.ESCAPE:
                self._return_to_live_mode()
                event.accept()
            elif key == AnalysisKeys.TOGGLE_GRID:
                self._toggle_analysis_grid()
                event.accept()
            elif key == AnalysisKeys.EXPORT:
                self._export_analysis()
                event.accept()
            elif key == Qt.Key_H:  # Help key
                self._toggle_help()
                event.accept()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            logger.error(f"Keyboard event error: {e}")
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse input for analysis interactions"""
        if (INTERACTIVE_ANALYSIS_AVAILABLE and self.analysis_manager and
            self.analysis_manager.current_mode in [AnalysisMode.INSPECTION, AnalysisMode.LABELING]):

            try:
                # Get mouse position in widget coordinates
                x = event.pos().x() / self.width()
                y = 1.0 - (event.pos().y() / self.height())  # Flip Y coordinate

                if event.button() == Qt.LeftButton:
                    self._handle_analysis_click(x, y)
                elif event.button() == Qt.RightButton:
                    self._handle_analysis_right_click(x, y)

                event.accept()
                return
            except Exception as e:
                logger.error(f"Mouse event error: {e}")

        super().mousePressEvent(event)

    def _toggle_pause_resume(self):
        """Toggle between live and paused modes"""
        current_mode = self.analysis_manager.current_mode

        if current_mode == AnalysisMode.LIVE:
            self.analysis_manager.set_mode(AnalysisMode.PAUSED)
            pass  # Reduced logging for performance
        elif current_mode == AnalysisMode.PAUSED:
            self.analysis_manager.set_mode(AnalysisMode.LIVE)
            pass  # Reduced logging for performance

    def _freeze_current_moment(self):
        """Freeze current moment for detailed analysis"""
        if not hasattr(self, 'mmpa_engine') or not hasattr(self.mmpa_engine, 'get_latest_signal'):
            logger.warning("No signal data available for freezing")
            return

        try:
            # Get current signal and analysis data
            latest_signal = getattr(self.mmpa_engine, 'latest_raw_signal', np.zeros(1024))

            visual_state = {
                'shape_a': self.shape_a,
                'shape_b': self.shape_b,
                'morph_factor': self.morph_factor,
                'rotation': self.rotation,
                'color_mode': self.color_mode,
                'particle_trails': self.particle_trails
            }

            audio_features = {
                'amplitude': self.audio_amplitude,
                'rms_energy': getattr(self, 'current_rms', 0.0),
                'spectral_centroid': getattr(self, 'current_centroid', 0.0)
            }

            genre_info = {
                'genre': self.current_genre,
                'key': self.current_key,
                'chord': self.current_chord
            }

            morph_params = {
                'rotation': self.rotation,
                'morph_factor': self.morph_factor,
                'particle_count': len(self.particles)
            }

            # Freeze the moment
            frozen_moment = self.analysis_manager.freeze_current_moment(
                latest_signal, visual_state, audio_features, genre_info, morph_params
            )

            self.analysis_manager.set_mode(AnalysisMode.FROZEN)
            pass  # Reduced logging for performance

        except Exception as e:
            logger.error(f"Freeze moment error: {e}")

    def _enter_inspection_mode(self):
        """Enter detailed inspection mode"""
        self.analysis_manager.set_mode(AnalysisMode.INSPECTION)
        pass  # Reduced logging for performance

    def _enter_labeling_mode(self):
        """Enter interactive labeling mode"""
        self.analysis_manager.set_mode(AnalysisMode.LABELING)
        pass  # Reduced logging for performance

    def _return_to_live_mode(self):
        """Return to live visualization mode"""
        self.analysis_manager.set_mode(AnalysisMode.LIVE)
        pass  # Reduced logging for performance

    def _toggle_analysis_grid(self):
        """Toggle analysis grid overlay"""
        if hasattr(self.analysis_manager, 'show_frequency_grid'):
            self.analysis_manager.show_frequency_grid = not self.analysis_manager.show_frequency_grid
            state = "ON" if self.analysis_manager.show_frequency_grid else "OFF"
            pass  # Reduced logging for performance

    def _toggle_help(self):
        """Toggle help overlay"""
        if not hasattr(self, 'show_help'):
            self.show_help = False
        self.show_help = not self.show_help
        state = "ON" if self.show_help else "OFF"
        pass  # Reduced logging for performance

    def _export_analysis(self):
        """Export current analysis session"""
        try:
            export_data = self.analysis_manager.export_analysis_session()
            timestamp = int(time.time())
            filename = f"mmpa_analysis_{timestamp}.json"

            with open(filename, 'w') as f:
                import json
                json.dump(export_data, f, indent=2)

            logger.info(f"💾 Analysis exported to {filename}")

        except Exception as e:
            logger.error(f"Export error: {e}")

    def _handle_analysis_click(self, x: float, y: float):
        """Handle left click in analysis mode"""
        if self.analysis_manager.current_mode == AnalysisMode.INSPECTION:
            # Get frequency at click position
            frequency = self.analysis_manager.get_frequency_at_position(x, self.width())
            amplitude = self.analysis_manager.get_amplitude_at_frequency(frequency)

            # Add measurement
            measurement_id = self.analysis_manager.add_measurement(
                "frequency_point", (x, y), frequency=frequency,
                amplitude=amplitude, value=frequency, units="Hz"
            )

            pass  # Reduced logging for performance

        elif self.analysis_manager.current_mode == AnalysisMode.LABELING:
            # Add annotation
            frequency = self.analysis_manager.get_frequency_at_position(x, self.width())
            label_text = f"Point_{len(self.analysis_manager.labeling_system.annotations)}"

            annotation_id = self.analysis_manager.labeling_system.add_annotation(
                (x, y, 0.0), label_text, frequency=frequency
            )

            pass  # Reduced logging for performance

    def _handle_analysis_right_click(self, x: float, y: float):
        """Handle right click in analysis mode"""
        # Check for nearby annotations
        nearby_annotations = self.analysis_manager.labeling_system.get_annotations_near((x, y, 0.0), 0.05)

        if nearby_annotations:
            # Remove nearest annotation
            nearest = nearby_annotations[0]
            self.analysis_manager.labeling_system.remove_annotation(nearest.id)
            pass  # Reduced logging for performance

    def _on_analysis_mode_changed(self, new_mode: AnalysisMode):
        """Handle analysis mode changes"""
        # Update visual indicators based on mode
        if new_mode == AnalysisMode.PAUSED:
            # Could change background color, add overlay, etc.
            pass
        elif new_mode == AnalysisMode.FROZEN:
            # Stop animation timer
            if hasattr(self, 'timer'):
                self.timer.stop()
        elif new_mode == AnalysisMode.LIVE:
            # Resume animation timer
            if hasattr(self, 'timer') and not self.timer.isActive():
                self.timer.start()

    def _on_moment_frozen(self, frozen_moment):
        """Handle moment frozen signal"""
        # Perform analysis on frozen moment
        if hasattr(self.analysis_manager, 'analyze_frozen_moment'):
            analysis_results = self.analysis_manager.analyze_frozen_moment()

            # Reduced logging for performance - analysis results available via UI
            pass

            # Display frequency band analysis
            freq_bands = analysis_results.get('frequency_bands', {})
            strongest_band = max(freq_bands, key=freq_bands.get) if freq_bands else 'none'
            pass  # Reduced logging for performance

    # REMOVED DUPLICATE PAINTGL METHOD FOR PERFORMANCE - Using first paintGL only

    # REMOVED _render_cinematic FOR PERFORMANCE

    def _render_classic(self):
        """Fallback classic OpenGL rendering"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Dynamic camera setup
        rotation_speed = getattr(self, 'rotation_speed', 0.8)
        glTranslatef(0.0, 0.0, -6.0)
        glRotatef(self.rotation * rotation_speed, 1.0, 1.0, 0.0)
        glRotatef(self.rotation * 0.3, 0.0, 1.0, 0.0)

        # Render multiple morphing layers for enhanced visual depth
        self.render_multi_layer_morphing()

        # Render enhanced particles
        self.render_enhanced_particles()

    def _render_scene_with_pbr(self):
        """Render scene using PBR materials"""
        # Set audio-reactive PBR parameters
        metallic = min(0.8, self.audio_amplitude * 1.5)
        roughness = 0.3 + (1.0 - self.audio_amplitude) * 0.4

        # Apply genre-specific material properties
        if self.current_genre in ['metal', 'rock']:
            metallic = min(1.0, metallic + 0.3)
        elif self.current_genre in ['jazz', 'classical']:
            roughness = max(0.1, roughness - 0.2)

        # Set emissive for bloom effect
        emissive_strength = self.audio_amplitude * 2.0
        emissive_color = self.current_color

        # Render morphing layers with PBR
        self.cinematic_engine.set_material_properties(
            albedo=self.current_color,
            metallic=metallic,
            roughness=roughness,
            ao=1.0,
            emissive=emissive_color,
            emissive_strength=emissive_strength
        )

        # Render multiple morphing layers
        self.render_multi_layer_morphing()

        # Render enhanced particles
        self.render_enhanced_particles()

    def _get_genre_id(self, genre_name: str) -> int:
        """Convert genre name to numeric ID for shader"""
        genre_map = {
            'rock': 0, 'pop': 1, 'jazz': 2, 'classical': 3, 'electronic': 4,
            'hip_hop': 5, 'country': 6, 'blues': 7, 'reggae': 8, 'folk': 9,
            'metal': 10, 'r&b': 11, 'punk': 12, 'funk': 13, 'ambient': 14, 'techno': 15
        }
        return genre_map.get(genre_name.lower(), 0)

    def _render_analysis_overlays(self):
        """Render analysis mode visual overlays"""
        try:
            # Set up 2D rendering for overlays
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, self.width(), 0, self.height(), -1, 1)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()

            # Disable depth testing for overlays
            glDisable(GL_DEPTH_TEST)

            # Render mode indicator
            self._render_mode_indicator()

            # Render annotations if in labeling mode
            if self.analysis_manager.current_mode in [AnalysisMode.LABELING, AnalysisMode.INSPECTION]:
                self._render_annotations()

            # Render frequency grid if enabled
            if getattr(self.analysis_manager, 'show_frequency_grid', False):
                self._render_frequency_grid()

            # Render mouse cursor info in analysis modes
            if self.analysis_manager.current_mode in [AnalysisMode.INSPECTION, AnalysisMode.LABELING]:
                self._render_mouse_cursor_info()

            # Render help overlay if enabled
            self._render_help_overlay()

            # Restore 3D rendering
            glEnable(GL_DEPTH_TEST)
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)

        except Exception as e:
            logger.error(f"Analysis overlay render error: {e}")

    def _render_mode_indicator(self):
        """Render professional analysis mode indicator with text and animations"""
        mode_info = {
            AnalysisMode.PAUSED: {
                'color': (1.0, 1.0, 0.0), 'text': '⏸️ PAUSED',
                'desc': 'Visualization paused - Press SPACE to resume'
            },
            AnalysisMode.FROZEN: {
                'color': (0.0, 1.0, 1.0), 'text': '🧊 FROZEN',
                'desc': 'Moment frozen for analysis - Press I to inspect, L to label'
            },
            AnalysisMode.INSPECTION: {
                'color': (1.0, 0.5, 0.0), 'text': '🔍 INSPECTION',
                'desc': 'Click anywhere to measure frequency and amplitude'
            },
            AnalysisMode.LABELING: {
                'color': (1.0, 0.0, 1.0), 'text': '🏷️ LABELING',
                'desc': 'Click to add labels, Right-click to remove'
            }
        }

        mode = self.analysis_manager.current_mode
        if mode not in mode_info:
            return

        info = mode_info[mode]
        r, g, b = info['color']

        # Pulsing effect for attention
        pulse = 0.7 + 0.3 * math.sin(time.time() * 3)
        alpha = pulse

        # Background panel with rounded corners effect
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Main panel background
        glColor4f(0.0, 0.0, 0.0, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(10, self.height() - 90)
        glVertex2f(450, self.height() - 90)
        glVertex2f(450, self.height() - 10)
        glVertex2f(10, self.height() - 10)
        glEnd()

        # Colored accent bar
        glColor4f(r * alpha, g * alpha, b * alpha, alpha)
        glBegin(GL_QUADS)
        glVertex2f(10, self.height() - 90)
        glVertex2f(450, self.height() - 90)
        glVertex2f(450, self.height() - 75)
        glVertex2f(10, self.height() - 75)
        glEnd()

        # Analysis stats if frozen
        if mode == AnalysisMode.FROZEN and hasattr(self.analysis_manager, 'frozen_moment'):
            self._render_analysis_stats()

        glDisable(GL_BLEND)

    def _render_analysis_stats(self):
        """Render real-time analysis statistics for frozen moments"""
        if not self.analysis_manager.frozen_moment:
            return

        try:
            analysis = self.analysis_manager.analyze_frozen_moment()

            # Position for stats display
            start_y = self.height() - 120
            line_height = 15

            glColor3f(1.0, 1.0, 1.0)  # White text

            # Display key analysis results
            stats = [
                f"🎵 Frequency: {analysis.get('dominant_frequency', 0):.1f} Hz",
                f"🎼 Harmonic Ratio: {analysis.get('harmonic_ratio', 0):.2f}",
                f"🎭 Dissonance: {analysis.get('dissonance_level', 0):.2f}",
                f"⚡ Energy: {analysis.get('total_energy', 0):.0f}",
            ]

            # Find strongest frequency band
            freq_bands = analysis.get('frequency_bands', {})
            if freq_bands:
                strongest_band = max(freq_bands, key=freq_bands.get)
                stats.append(f"📊 Peak Band: {strongest_band}")

        except Exception as e:
            logger.error(f"Stats render error: {e}")

    def _render_annotations(self):
        """Render enhanced user annotations with labels and connections"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        for i, annotation in enumerate(self.analysis_manager.labeling_system.annotations):
            x = annotation.position[0] * self.width()
            y = annotation.position[1] * self.height()

            r, g, b = annotation.color

            # Pulsing effect for visibility
            pulse = 0.8 + 0.2 * math.sin(time.time() * 4 + i)

            # Render annotation marker with glow effect
            for size in [12.0, 8.0, 4.0]:  # Multiple sizes for glow
                alpha = (12.0 - size + 4.0) / 12.0 * pulse * 0.7
                glColor4f(r, g, b, alpha)
                glPointSize(size)
                glBegin(GL_POINTS)
                glVertex2f(x, y)
                glEnd()

            # Render frequency line if available
            if annotation.frequency and annotation.frequency > 0:
                # Draw line from annotation to frequency axis
                glColor4f(r, g, b, 0.3)
                glBegin(GL_LINES)
                glVertex2f(x, y)
                glVertex2f(x, 30)  # Bottom of screen
                glEnd()

                # Frequency label at bottom
                glColor4f(r, g, b, 0.8)

        glDisable(GL_BLEND)

    def _render_frequency_grid(self):
        """Render professional frequency analysis grid with labels"""
        if not self.analysis_manager.frozen_moment:
            return

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Get frequency range for labeling
        max_freq = self.analysis_manager.frozen_moment.frequencies[-1]

        # Major grid lines (frequency bands)
        glColor4f(0.4, 0.4, 0.4, 0.8)
        glBegin(GL_LINES)

        # Frequency band divisions (more musical)
        freq_divisions = [50, 100, 250, 500, 1000, 2500, 5000, 10000, 15000]
        for freq in freq_divisions:
            if freq < max_freq:
                x = (freq / max_freq) * self.width()
                glVertex2f(x, 0)
                glVertex2f(x, self.height())

        glEnd()

        # Minor grid lines
        glColor4f(0.2, 0.2, 0.2, 0.5)
        glBegin(GL_LINES)

        # Horizontal amplitude levels
        for i in range(1, 8):
            y = (i / 8.0) * self.height()
            glVertex2f(0, y)
            glVertex2f(self.width(), y)

        glEnd()

        # Frequency band labels
        glColor4f(0.8, 0.8, 0.8, 0.9)
        for freq in freq_divisions[:6]:  # Don't overcrowd
            if freq < max_freq:
                x = (freq / max_freq) * self.width()
                # Would render text here with proper text rendering

        glDisable(GL_BLEND)

    def mouseMoveEvent(self, event):
        """Enhanced mouse move with real-time frequency feedback"""
        if (INTERACTIVE_ANALYSIS_AVAILABLE and self.analysis_manager and
            self.analysis_manager.current_mode in [AnalysisMode.INSPECTION, AnalysisMode.LABELING]):

            try:
                # Store mouse position for rendering cursor info
                self.mouse_x = event.pos().x() / self.width()
                self.mouse_y = 1.0 - (event.pos().y() / self.height())
                self.mouse_frequency = self.analysis_manager.get_frequency_at_position(
                    self.mouse_x, self.width()
                ) if hasattr(self.analysis_manager, 'get_frequency_at_position') else 0.0

                # Force redraw to show cursor info
                self.update()

            except Exception as e:
                logger.error(f"Mouse move error: {e}")

        super().mouseMoveEvent(event)

    def _render_mouse_cursor_info(self):
        """Render real-time cursor information"""
        if not hasattr(self, 'mouse_x'):
            return

        mouse_x_px = self.mouse_x * self.width()
        mouse_y_px = self.mouse_y * self.height()

        # Cursor crosshairs
        glColor4f(1.0, 1.0, 1.0, 0.6)
        glBegin(GL_LINES)
        # Vertical line
        glVertex2f(mouse_x_px, 0)
        glVertex2f(mouse_x_px, self.height())
        # Horizontal line
        glVertex2f(0, mouse_y_px)
        glVertex2f(self.width(), mouse_y_px)
        glEnd()

        # Frequency info box
        if hasattr(self, 'mouse_frequency') and self.mouse_frequency > 0:
            # Background for text
            box_width = 120
            box_height = 40
            box_x = mouse_x_px + 10
            box_y = mouse_y_px - 30

            # Keep box on screen
            if box_x + box_width > self.width():
                box_x = mouse_x_px - box_width - 10
            if box_y < 0:
                box_y = mouse_y_px + 10

            # Semi-transparent background
            glColor4f(0.0, 0.0, 0.0, 0.8)
            glBegin(GL_QUADS)
            glVertex2f(box_x, box_y)
            glVertex2f(box_x + box_width, box_y)
            glVertex2f(box_x + box_width, box_y + box_height)
            glVertex2f(box_x, box_y + box_height)
            glEnd()

            # Border
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glBegin(GL_LINE_LOOP)
            glVertex2f(box_x, box_y)
            glVertex2f(box_x + box_width, box_y)
            glVertex2f(box_x + box_width, box_y + box_height)
            glVertex2f(box_x, box_y + box_height)
            glEnd()

    def _render_help_overlay(self):
        """Render keyboard shortcuts help overlay"""
        if not hasattr(self, 'show_help') or not self.show_help:
            return

        # Help panel background
        panel_width = 400
        panel_height = 300
        panel_x = (self.width() - panel_width) / 2
        panel_y = (self.height() - panel_height) / 2

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Background
        glColor4f(0.0, 0.0, 0.0, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()

        # Border
        glColor4f(0.5, 0.8, 1.0, 1.0)
        glBegin(GL_LINE_LOOP)
        glVertex2f(panel_x, panel_y)
        glVertex2f(panel_x + panel_width, panel_y)
        glVertex2f(panel_x + panel_width, panel_y + panel_height)
        glVertex2f(panel_x, panel_y + panel_height)
        glEnd()

        glDisable(GL_BLEND)

        # Help content would be rendered here with proper text rendering

class MMPAEnhancedMorphingDemo(QMainWindow):
    """Enhanced morphing demo with MMPA Universal Signal Framework"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 MMPA Enhanced Visual Morphing - Universal Signal-to-Form Engine")
        self.setGeometry(100, 100, 1400, 900)

        self.manual_control = False
        self._setup_ui()

        logger.info("🎵 MMPA Enhanced Visual Morphing Ready!")

    def _setup_ui(self):
        """Set up enhanced UI with MMPA integration"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Enhanced morphing visualization (70%)
        self.morph_widget = MMPAMorphWidget()
        layout.addWidget(self.morph_widget, 70)

        # Enhanced controls with MMPA (30%)
        controls = self._create_mmpa_controls()
        layout.addWidget(controls, 30)

    def _create_mmpa_controls(self):
        """Create MMPA-enhanced control panel"""
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
        """)

        layout = QVBoxLayout(controls_frame)

        # Title
        title = QLabel("🎵 MMPA ENHANCED MORPHING")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3498db; padding: 10px;")
        layout.addWidget(title)

        # Create tabbed interface
        tabs = QTabWidget()

        # Morphing tab
        morph_tab = self._create_morph_controls()
        tabs.addTab(morph_tab, "🎨 Morphing")

        # MMPA Signal tab
        mmpa_tab = self._create_mmpa_controls_tab()
        tabs.addTab(mmpa_tab, "🎵 MMPA Signals")

        # Effects tab
        effects_tab = self._create_effects_controls()
        tabs.addTab(effects_tab, "✨ Effects")

        layout.addWidget(tabs)

        # Status
        self.status_label = QLabel("🎵 MMPA Signal Engine Active")
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

        # Base shapes
        shapes = ['sphere', 'cube', 'torus', 'dodecahedron', 'icosahedron',
                 'klein_bottle', 'mobius_strip', 'helix', 'octahedron']

        # Add revolutionary procedural shapes if available
        if PROCEDURAL_GEOMETRY_AVAILABLE:
            procedural_shapes = ['l_system_tree', 'mandelbrot_3d', 'perlin_terrain',
                               'voronoi_cells', 'dna_helix', 'crystal_lattice',
                               'mathematical_surface']
            shapes.extend(procedural_shapes)
            logger.info(f"🔥 Added {len(procedural_shapes)} procedural shapes to UI")

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

        self.morph_label = QLabel("0% (Sphere) - MMPA Controlled")
        self.morph_label.setAlignment(Qt.AlignCenter)
        self.morph_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        morph_layout.addWidget(self.morph_label)

        layout.addWidget(morph_group)

        return widget

    def _create_mmpa_controls_tab(self):
        """Create MMPA signal analysis controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Signal sources
        sources_group = QGroupBox("📡 Signal Sources")
        sources_layout = QVBoxLayout(sources_group)

        # MIDI status
        self.midi_status = QLabel("🎹 MIDI: Connected (MPK Mini)")
        self.midi_status.setStyleSheet("color: #2ecc71;")
        sources_layout.addWidget(self.midi_status)

        # Audio status (future)
        self.audio_status = QLabel("🎤 Audio: Available for integration")
        self.audio_status.setStyleSheet("color: #f39c12;")
        sources_layout.addWidget(self.audio_status)

        # Sensor status (future)
        self.sensor_status = QLabel("📊 Sensors: Framework ready")
        self.sensor_status.setStyleSheet("color: #9b59b6;")
        sources_layout.addWidget(self.sensor_status)

        layout.addWidget(sources_group)

        # Signal analysis controls
        analysis_group = QGroupBox("🔬 Signal Analysis")
        analysis_layout = QVBoxLayout(analysis_group)

        # Button to open separate analysis window
        self.analysis_window_btn = QPushButton("📊 Open Musical Intelligence Window")
        self.analysis_window_btn.clicked.connect(self._open_analysis_window)
        analysis_layout.addWidget(self.analysis_window_btn)

        # Compact status display
        self.compact_analysis = QLabel("Musical Intelligence: Ready")
        self.compact_analysis.setStyleSheet("background-color: #1e1e1e; color: #00ff00; padding: 10px; font-family: monospace;")
        self.compact_analysis.setWordWrap(True)
        analysis_layout.addWidget(self.compact_analysis)

        layout.addWidget(analysis_group)

        # Initialize separate analysis window (but don't show it yet)
        self.analysis_window = None

        # Audio device selection
        audio_group = QGroupBox("🎤 Audio Settings")
        audio_layout = QVBoxLayout(audio_group)

        audio_layout.addWidget(QLabel("Audio Device:"))
        self.audio_device_combo = QComboBox()
        self.audio_device_combo.addItems(['BlackHole (System Audio)', 'Default Microphone', 'Refresh Devices'])
        self.audio_device_combo.currentTextChanged.connect(self._update_audio_device)
        audio_layout.addWidget(self.audio_device_combo)

        # Audio level indicator
        audio_layout.addWidget(QLabel("Audio Level:"))
        self.audio_level_bar = QProgressBar()
        self.audio_level_bar.setRange(0, 100)
        self.audio_level_bar.setValue(0)
        audio_layout.addWidget(self.audio_level_bar)

        layout.addWidget(audio_group)

        # Performance Controls
        performance_group = QGroupBox("⚡ Performance Settings")
        performance_layout = QVBoxLayout(performance_group)

        # Performance mode toggle
        self.performance_mode_cb = QCheckBox("Performance Mode (Lower Quality, Higher FPS)")
        self.performance_mode_cb.stateChanged.connect(self._toggle_performance_mode)
        performance_layout.addWidget(self.performance_mode_cb)

        # FPS control
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Target FPS:"))
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(['30', '45', '60'])
        self.fps_combo.setCurrentText('60')
        self.fps_combo.currentTextChanged.connect(self._update_target_fps)
        fps_layout.addWidget(self.fps_combo)
        performance_layout.addLayout(fps_layout)

        # Musical intelligence frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Musical Intelligence Frequency:"))
        self.intelligence_freq_combo = QComboBox()
        self.intelligence_freq_combo.addItems(['High (6fps)', 'Medium (3fps)', 'Low (1fps)'])
        self.intelligence_freq_combo.setCurrentText('High (6fps)')
        self.intelligence_freq_combo.currentTextChanged.connect(self._update_intelligence_frequency)
        freq_layout.addWidget(self.intelligence_freq_combo)
        performance_layout.addLayout(freq_layout)

        layout.addWidget(performance_group)

        # Performance Recording
        recording_group = QGroupBox("🎬 Performance Recording")
        recording_layout = QVBoxLayout(recording_group)

        # Recording controls
        self.record_btn = QPushButton("🔴 Start Recording")
        self.record_btn.clicked.connect(self._toggle_recording)
        recording_layout.addWidget(self.record_btn)

        # Recording status
        self.recording_status = QLabel("Ready to record")
        self.recording_status.setStyleSheet("padding: 5px; background-color: #2d2d2d; color: #ffffff;")
        recording_layout.addWidget(self.recording_status)

        # Recording options
        recording_layout.addWidget(QLabel("Include:"))
        self.record_musical_data = QCheckBox("Musical Intelligence Data")
        self.record_musical_data.setChecked(True)
        recording_layout.addWidget(self.record_musical_data)

        layout.addWidget(recording_group)

        # Visual Presets
        preset_group = QGroupBox("🎨 Visual Presets")
        preset_layout = QVBoxLayout(preset_group)

        # Preset selection
        preset_layout.addWidget(QLabel("Load Preset:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Default", "Jazz Club", "Classical Concert", "Electronic Dance",
            "Rock Show", "Ambient Chill", "Blues Bar"
        ])
        self.preset_combo.currentTextChanged.connect(self._load_preset)
        preset_layout.addWidget(self.preset_combo)

        # Preset controls
        preset_controls = QHBoxLayout()
        self.save_preset_btn = QPushButton("💾 Save Current")
        self.save_preset_btn.clicked.connect(self._save_current_preset)
        preset_controls.addWidget(self.save_preset_btn)

        preset_layout.addLayout(preset_controls)

        layout.addWidget(preset_group)

        # Initialize systems
        self.is_recording = False
        self.recording_data = []
        self.recording_start_time = None
        self._init_presets()

        # REMOVED ANALYSIS TIMER FOR PERFORMANCE - Will update analysis with main timer

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
        self.color_combo.addItems(['rainbow', 'mmpa_reactive', 'blue_white', 'cyan'])
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

        return widget

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
        """Handle manual morph changes"""
        self.manual_control = True
        morph_factor = value / 100.0
        self.morph_widget.set_morph_factor(morph_factor)
        self.morph_label.setText(f"{value}% (Manual Override)")

    def _update_signal_analysis(self):
        """Update signal analysis display"""
        if not hasattr(self.morph_widget, 'mmpa_engine'):
            return

        # Get recent signal features
        combined_features = self.morph_widget.mmpa_engine.get_combined_features()
        recent_events = self.morph_widget.mmpa_engine.get_recent_events(2.0)

        analysis_text = "=== MMPA Signal Analysis ===\n"

        for signal_type, features in combined_features.items():
            analysis_text += f"\n{signal_type.value.upper()}:\n"
            analysis_text += f"  Intensity: {features.intensity:.3f}\n"
            analysis_text += f"  Frequency: {features.frequency:.1f} Hz\n"
            analysis_text += f"  Complexity: {features.complexity:.3f}\n"
            analysis_text += f"  Rhythm: {features.rhythm_strength:.3f}\n"

            # Enhanced Musical Intelligence Display
            if hasattr(features, 'raw_data') and features.raw_data:
                raw_data = features.raw_data

                # Musical Analysis Section
                if any(key in raw_data for key in ['chord', 'key_signature', 'genre', 'bpm']):
                    analysis_text += "\n  🎵 MUSICAL INTELLIGENCE:\n"

                    # Tempo & Rhythm
                    bpm = raw_data.get('bpm', 0)
                    pattern = raw_data.get('rhythm_pattern', 'unknown')
                    if bpm > 0:
                        analysis_text += f"    ♩ Tempo: {bpm:.1f} BPM ({pattern})\n"

                    # Harmonic Analysis
                    chord = raw_data.get('chord', 'unknown')
                    chord_quality = raw_data.get('chord_quality', '')
                    if chord != 'unknown':
                        analysis_text += f"    🎹 Chord: {chord}"
                        if chord_quality:
                            analysis_text += f" ({chord_quality})"
                        analysis_text += "\n"

                    progression = raw_data.get('chord_progression', 'unknown')
                    prog_confidence = raw_data.get('progression_confidence', 0)
                    if progression != 'unknown' and prog_confidence > 0.4:
                        analysis_text += f"    🎼 Progression: {progression} ({prog_confidence:.1%})\n"

                    # Key Signature
                    key = raw_data.get('key_signature', 'unknown')
                    key_confidence = raw_data.get('key_confidence', 0)
                    if key != 'unknown' and key_confidence > 0.3:
                        analysis_text += f"    🔑 Key: {key} ({key_confidence:.1%})\n"

                    # Genre Classification
                    genre = raw_data.get('genre', 'unknown')
                    genre_confidence = raw_data.get('genre_confidence', 0)
                    if genre != 'unknown' and genre_confidence > 0.3:
                        analysis_text += f"    🎸 Genre: {genre} ({genre_confidence:.1%})\n"

                    # Musical Complexity
                    musical_complexity = raw_data.get('musical_complexity', 0)
                    if musical_complexity > 0:
                        complexity_desc = "simple" if musical_complexity < 0.3 else "moderate" if musical_complexity < 0.6 else "complex"
                        analysis_text += f"    📊 Musical Complexity: {complexity_desc} ({musical_complexity:.2f})\n"

                    # Harmonic Tension
                    tension = raw_data.get('harmonic_tension', 0)
                    if tension > 0:
                        tension_desc = "consonant" if tension < 0.3 else "moderate" if tension < 0.6 else "dissonant"
                        analysis_text += f"    ⚡ Harmonic Tension: {tension_desc} ({tension:.2f})\n"

        if recent_events:
            analysis_text += f"\nRECENT EVENTS ({len(recent_events)}):\n"
            for event in recent_events[-5:]:  # Last 5 events
                # Enhanced event display with musical context
                event_desc = event.event_type
                if hasattr(event, 'metadata') and event.metadata:
                    if event.event_type == "note" and 'note' in event.metadata:
                        event_desc += f" ({event.metadata['note']})"
                    elif event.event_type == "beat" and 'pattern' in event.metadata:
                        pattern = event.metadata['pattern']
                        if pattern != 'unknown':
                            event_desc += f" ({pattern})"
                    elif event.event_type == "tempo" and 'bpm' in event.metadata:
                        event_desc += f" ({event.metadata['bpm']:.0f} BPM)"
                analysis_text += f"  {event_desc}: {event.intensity:.2f}\n"

        # Show current form parameters
        if hasattr(self.morph_widget, 'current_form_params'):
            form_params = self.morph_widget.current_form_params
            if form_params:
                analysis_text += "\nFORM PARAMETERS:\n"
                for param, value in list(form_params.items())[:5]:  # Show first 5
                    analysis_text += f"  {param}: {value:.3f}\n"

        # Update compact status display
        if combined_features:
            # Show brief status in main window
            status_parts = []
            for signal_type, features in combined_features.items():
                if hasattr(features, 'raw_data') and features.raw_data:
                    raw_data = features.raw_data
                    genre = raw_data.get('genre', 'unknown')
                    key = raw_data.get('key_signature', 'unknown')
                    bpm = raw_data.get('bpm', 0)

                    if genre != 'unknown':
                        status_parts.append(f"Genre: {genre}")
                    if key != 'unknown':
                        status_parts.append(f"Key: {key}")
                    if bpm > 0:
                        status_parts.append(f"BPM: {bpm:.0f}")

            if status_parts:
                self.compact_analysis.setText(" | ".join(status_parts))
            else:
                self.compact_analysis.setText("Musical Intelligence: Active - No music detected")
        else:
            self.compact_analysis.setText("Musical Intelligence: Ready")

        # Update separate analysis window if it exists
        if self.analysis_window and self.analysis_window.isVisible():
            self.analysis_window.update_analysis(analysis_text)

        # Update audio level indicator
        self._update_audio_level_display(combined_features)

        # Record frame data if recording is active
        if hasattr(self, 'is_recording') and self.is_recording:
            self._record_frame_data(combined_features, recent_events)

    def _update_audio_level_display(self, combined_features):
        """Update audio level progress bar and amplitude tracking"""
        if SignalType.AUDIO in combined_features:
            audio_features = combined_features[SignalType.AUDIO]
            level = min(audio_features.intensity * 100, 100)
            self.audio_level_bar.setValue(int(level))

            # Update morph widget amplitude for dynamic scaling
            if hasattr(self, 'morph_widget'):
                self.morph_widget.audio_amplitude = audio_features.intensity

            # Color coding for level
            if level > 80:
                self.audio_level_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif level > 50:
                self.audio_level_bar.setStyleSheet("QProgressBar::chunk { background-color: yellow; }")
            else:
                self.audio_level_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        else:
            self.audio_level_bar.setValue(0)
            if hasattr(self, 'morph_widget'):
                self.morph_widget.audio_amplitude = 0.0

    def _update_audio_device(self, device_name):
        """Handle audio device selection changes"""
        if device_name == "Refresh Devices":
            # TODO: Refresh available audio devices
            logger.info("🔄 Refreshing audio devices...")
        else:
            logger.info(f"🎤 Audio device selected: {device_name}")

    def _toggle_performance_mode(self, state):
        """Toggle performance mode on/off"""
        enabled = state == 2  # Qt.Checked
        self.morph_widget.set_performance_mode(enabled)

    def _update_target_fps(self, fps_text):
        """Update target FPS"""
        try:
            fps = int(fps_text)
            self.morph_widget._set_target_fps(fps)
        except ValueError:
            logger.error(f"Invalid FPS value: {fps_text}")

    def _update_intelligence_frequency(self, freq_text):
        """Update musical intelligence processing frequency"""
        freq_map = {
            'High (6fps)': 10,   # Process every 10 frames at 60fps = 6fps
            'Medium (3fps)': 20, # Process every 20 frames at 60fps = 3fps
            'Low (1fps)': 60     # Process every 60 frames at 60fps = 1fps
        }

        if freq_text in freq_map:
            self.morph_widget.musical_intelligence_frequency = freq_map[freq_text]
            logger.info(f"🎵 Musical intelligence frequency set to: {freq_text}")

    def _toggle_recording(self):
        """Toggle performance recording on/off"""
        if not self.is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Start recording performance data"""
        self.is_recording = True
        self.recording_start_time = time.time()
        self.recording_data = []

        # Update UI
        self.record_btn.setText("⏹️ Stop Recording")
        self.record_btn.setStyleSheet("background-color: #ff4444; color: white;")
        self.recording_status.setText("🔴 RECORDING...")
        self.recording_status.setStyleSheet("padding: 5px; background-color: #ff4444; color: white;")

        logger.info("🎬 Performance recording started")

    def _stop_recording(self):
        """Stop recording and save data"""
        if not self.is_recording:
            return

        self.is_recording = False
        recording_duration = time.time() - self.recording_start_time

        # Update UI
        self.record_btn.setText("🔴 Start Recording")
        self.record_btn.setStyleSheet("")
        self.recording_status.setText(f"Saved recording ({recording_duration:.1f}s)")
        self.recording_status.setStyleSheet("padding: 5px; background-color: #2d2d2d; color: #00ff00;")

        # Save recording data
        self._save_recording_data(recording_duration)

    def _save_recording_data(self, duration):
        """Save recorded performance data to file"""
        import json
        import os
        from datetime import datetime

        # Create recordings directory
        recordings_dir = "recordings"
        os.makedirs(recordings_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mmpa_performance_{timestamp}.json"
        filepath = os.path.join(recordings_dir, filename)

        # Prepare recording metadata
        recording_metadata = {
            "recording_info": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": duration,
                "total_data_points": len(self.recording_data),
                "includes_musical_data": self.record_musical_data.isChecked()
            },
            "data": self.recording_data
        }

        # Save to file
        try:
            with open(filepath, 'w') as f:
                json.dump(recording_metadata, f, indent=2)

            logger.info(f"📁 Recording saved: {filepath}")
            self.recording_status.setText(f"Saved: {filename}")

        except Exception as e:
            logger.error(f"❌ Failed to save recording: {e}")
            self.recording_status.setText("❌ Save failed")

    def _init_presets(self):
        """Initialize preset system with default presets"""
        self.default_presets = {
            "Jazz Club": {
                "color_mode": "mmpa_reactive",
                "shapes": ["sphere", "torus"],
                "particle_trails": True,
                "resolution": 800,
                "description": "Smooth, sophisticated visuals for jazz"
            },
            "Classical Concert": {
                "color_mode": "rainbow",
                "shapes": ["sphere", "helix"],
                "particle_trails": True,
                "resolution": 1200,
                "description": "Elegant, flowing visuals for classical music"
            },
            "Electronic Dance": {
                "color_mode": "mmpa_reactive",
                "shapes": ["cube", "star"],
                "particle_trails": False,
                "resolution": 600,
                "description": "High-energy, geometric visuals for electronic music"
            },
            "Rock Show": {
                "color_mode": "mmpa_reactive",
                "shapes": ["star", "pyramid"],
                "particle_trails": True,
                "resolution": 1000,
                "description": "Bold, dynamic visuals for rock music"
            },
            "Ambient Chill": {
                "color_mode": "blue_white",
                "shapes": ["sphere", "mobius"],
                "particle_trails": True,
                "resolution": 400,
                "description": "Calm, flowing visuals for ambient music"
            },
            "Blues Bar": {
                "color_mode": "mmpa_reactive",
                "shapes": ["sphere", "torus"],
                "particle_trails": True,
                "resolution": 600,
                "description": "Soulful, warm visuals for blues"
            }
        }

    def _load_preset(self, preset_name):
        """Load a visual preset"""
        if preset_name == "Default":
            return

        if preset_name in self.default_presets:
            preset = self.default_presets[preset_name]
            self._apply_preset(preset)
            logger.info(f"🎨 Loaded preset: {preset_name}")

    def _apply_preset(self, preset):
        """Apply preset settings to the visual system"""
        try:
            # Apply visual settings
            if hasattr(self, 'color_combo'):
                color_mode = preset.get('color_mode', 'rainbow')
                index = self.color_combo.findText(color_mode)
                if index >= 0:
                    self.color_combo.setCurrentIndex(index)

            # Apply shape settings
            shapes = preset.get('shapes', ['sphere', 'cube'])
            if hasattr(self, 'shape_a_combo') and len(shapes) >= 2:
                a_index = self.shape_a_combo.findText(shapes[0])
                b_index = self.shape_b_combo.findText(shapes[1])
                if a_index >= 0:
                    self.shape_a_combo.setCurrentIndex(a_index)
                if b_index >= 0:
                    self.shape_b_combo.setCurrentIndex(b_index)

            # Apply trails setting
            if hasattr(self, 'trails_cb'):
                self.trails_cb.setChecked(preset.get('particle_trails', True))

            # Apply resolution
            if hasattr(self, 'resolution_spin'):
                resolution = preset.get('resolution', 800)
                self.resolution_spin.setValue(resolution)

            # Trigger updates
            if hasattr(self, '_update_shapes'):
                self._update_shapes()
            if hasattr(self, '_update_effects'):
                self._update_effects()

        except Exception as e:
            logger.error(f"❌ Failed to apply preset: {e}")

    def _save_current_preset(self):
        """Save current settings as a preset"""
        from PySide6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, 'Save Preset', 'Enter preset name:')
        if ok and name:
            preset = self._get_current_settings()
            logger.info(f"💾 Saved preset: {name} - {preset}")

    def _get_current_settings(self):
        """Get current visual settings as a preset"""
        settings = {}

        if hasattr(self, 'color_combo'):
            settings['color_mode'] = self.color_combo.currentText()
        if hasattr(self, 'shape_a_combo') and hasattr(self, 'shape_b_combo'):
            settings['shapes'] = [self.shape_a_combo.currentText(), self.shape_b_combo.currentText()]
        if hasattr(self, 'trails_cb'):
            settings['particle_trails'] = self.trails_cb.isChecked()
        if hasattr(self, 'resolution_spin'):
            settings['resolution'] = self.resolution_spin.value()

        settings['description'] = "Custom user preset"
        return settings

    def _record_frame_data(self, combined_features, recent_events):
        """Record current frame data if recording is active"""
        if not hasattr(self, 'is_recording') or not self.is_recording:
            return

        current_time = time.time()
        relative_time = current_time - self.recording_start_time

        frame_data = {
            "timestamp": relative_time,
            "real_time": current_time
        }

        # Record musical intelligence data if enabled
        if self.record_musical_data.isChecked():
            musical_data = {}
            for signal_type, features in combined_features.items():
                if hasattr(features, 'raw_data') and features.raw_data:
                    raw_data = features.raw_data
                    musical_data[signal_type.value] = {
                        "genre": raw_data.get('genre', 'unknown'),
                        "genre_confidence": raw_data.get('genre_confidence', 0),
                        "key_signature": raw_data.get('key_signature', 'unknown'),
                        "key_confidence": raw_data.get('key_confidence', 0),
                        "chord": raw_data.get('chord', 'unknown'),
                        "chord_quality": raw_data.get('chord_quality', ''),
                        "bpm": raw_data.get('bpm', 0),
                        "rhythm_pattern": raw_data.get('rhythm_pattern', 'unknown'),
                        "harmonic_tension": raw_data.get('harmonic_tension', 0),
                        "musical_complexity": raw_data.get('musical_complexity', 0),
                        "intensity": features.intensity,
                        "frequency": features.frequency,
                        "rhythm_strength": features.rhythm_strength
                    }

            frame_data["musical_intelligence"] = musical_data

        # Record recent events
        if recent_events:
            frame_data["events"] = [
                {
                    "type": event.event_type,
                    "intensity": event.intensity,
                    "metadata": event.metadata if hasattr(event, 'metadata') else {}
                }
                for event in recent_events[-5:]  # Last 5 events
            ]

        self.recording_data.append(frame_data)

    def _open_analysis_window(self):
        """Open separate musical intelligence analysis window"""
        if self.analysis_window is None:
            self.analysis_window = MusicalIntelligenceWindow()

        self.analysis_window.show()
        self.analysis_window.raise_()
        self.analysis_window.activateWindow()
        logger.info("📊 Musical Intelligence window opened")

    def _open_timeline_editor(self):
        """Open timeline editor window"""
        if not hasattr(self, 'timeline_editor_window') or self.timeline_editor_window is None:
            self.timeline_editor_window = TimelineEditorWindow(self)

        self.timeline_editor_window.show()
        self.timeline_editor_window.raise_()
        self.timeline_editor_window.activateWindow()
        logger.info("📝 Timeline editor opened")


class TimelineEditorWindow(QMainWindow):
    """Timeline editor for creating automated visual sequences"""

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("⏰ Timeline Editor")
        self.setGeometry(200, 200, 600, 400)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("⏰ Visual Timeline Editor")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px; background-color: #2d2d2d; color: #ffffff;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Timeline list
        self.timeline_list = QTextEdit()
        self.timeline_list.setPlainText("# Timeline Events (time_in_seconds: action)\n\n0.0: preset Jazz Club\n5.0: shapes sphere torus\n10.0: color rainbow\n15.0: preset Electronic Dance\n20.0: shapes cube star\n25.0: preset Classical Concert")
        layout.addWidget(self.timeline_list)

        # Controls
        controls = QHBoxLayout()

        load_btn = QPushButton("📂 Load Timeline")
        load_btn.clicked.connect(self._load_timeline)
        controls.addWidget(load_btn)

        save_btn = QPushButton("💾 Save Timeline")
        save_btn.clicked.connect(self._save_timeline)
        controls.addWidget(save_btn)

        apply_btn = QPushButton("✅ Apply to Main")
        apply_btn.clicked.connect(self._apply_timeline)
        controls.addWidget(apply_btn)

        layout.addLayout(controls)

        self.statusBar().showMessage("Timeline Editor Ready")

    def _load_timeline(self):
        """Load timeline from file"""
        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(self, "Load Timeline", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                self.timeline_list.setPlainText(content)
                self.statusBar().showMessage(f"Loaded: {filename}")
            except Exception as e:
                self.statusBar().showMessage(f"Error loading: {e}")

    def _save_timeline(self):
        """Save timeline to file"""
        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(self, "Save Timeline", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.timeline_list.toPlainText())
                self.statusBar().showMessage(f"Saved: {filename}")
            except Exception as e:
                self.statusBar().showMessage(f"Error saving: {e}")

    def _apply_timeline(self):
        """Apply timeline to main system"""
        try:
            timeline_data = []
            content = self.timeline_list.toPlainText()

            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    if ':' in line:
                        time_str, action = line.split(':', 1)
                        time_val = float(time_str.strip())
                        action = action.strip()

                        # Parse action
                        if action.startswith('preset '):
                            preset_name = action[7:]
                            timeline_data.append({
                                'time': time_val,
                                'type': 'preset_change',
                                'data': {'preset': preset_name}
                            })
                        elif action.startswith('shapes '):
                            shapes = action[7:].split()
                            if len(shapes) >= 2:
                                timeline_data.append({
                                    'time': time_val,
                                    'type': 'shape_change',
                                    'data': {'shapes': shapes[:2]}
                                })
                        elif action.startswith('color '):
                            color_mode = action[6:]
                            timeline_data.append({
                                'time': time_val,
                                'type': 'color_change',
                                'data': {'color_mode': color_mode}
                            })

            # Apply to parent
            self.parent.timeline_data = timeline_data
            duration = timeline_data[-1]['time'] if timeline_data else 0
            self.parent.timeline_status.setText(f"Custom timeline loaded ({duration}s)")

            self.statusBar().showMessage(f"Applied timeline with {len(timeline_data)} events")
            logger.info(f"📝 Applied custom timeline: {len(timeline_data)} events")

        except Exception as e:
            self.statusBar().showMessage(f"Error parsing timeline: {e}")
            logger.error(f"❌ Timeline parsing error: {e}")


class MusicalIntelligenceWindow(QMainWindow):
    """Separate window for detailed musical intelligence analysis"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 Musical Intelligence Analysis")
        self.setGeometry(100, 100, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("🎵 Real-Time Musical Intelligence Analysis")
        header.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px; background-color: #2d2d2d; color: #ffffff;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Tabbed analysis display
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Main analysis tab
        self.main_analysis = QTextEdit()
        self.main_analysis.setReadOnly(True)
        self.main_analysis.setStyleSheet("""
            background-color: #1e1e1e;
            color: #00ff00;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        """)
        self.tab_widget.addTab(self.main_analysis, "📊 Full Analysis")

        # Genre/Key tab
        self.genre_key_display = QTextEdit()
        self.genre_key_display.setReadOnly(True)
        self.genre_key_display.setStyleSheet(self.main_analysis.styleSheet())
        self.tab_widget.addTab(self.genre_key_display, "🎭 Genre & Key")

        # Events tab
        self.events_display = QTextEdit()
        self.events_display.setReadOnly(True)
        self.events_display.setStyleSheet(self.main_analysis.styleSheet())
        self.tab_widget.addTab(self.events_display, "⚡ Events")

        # Always on top option
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        # Status bar
        self.statusBar().showMessage("Musical Intelligence Analysis Ready")

    def update_analysis(self, analysis_text: str):
        """Update the analysis display with new data"""
        # Update main analysis
        self.main_analysis.setText(analysis_text)

        # Extract specific sections for other tabs
        self._update_specialized_tabs(analysis_text)

        # Auto-scroll to bottom
        cursor = self.main_analysis.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.main_analysis.setTextCursor(cursor)

        # Update status
        self.statusBar().showMessage(f"Updated: {time.strftime('%H:%M:%S')}")

    def _update_specialized_tabs(self, analysis_text: str):
        """Extract and display specialized information"""
        lines = analysis_text.split('\n')

        # Extract genre and key information
        genre_key_info = []
        events_info = []

        current_section = None
        for line in lines:
            if "MUSICAL INTELLIGENCE:" in line:
                current_section = "musical"
            elif "RECENT EVENTS" in line:
                current_section = "events"
            elif current_section == "musical" and any(keyword in line for keyword in ["Genre:", "Key:", "Tempo:", "Chord:", "Progression:"]):
                genre_key_info.append(line)
            elif current_section == "events":
                events_info.append(line)

        # Update tabs
        self.genre_key_display.setText("\n".join(genre_key_info) if genre_key_info else "No musical intelligence data available")
        self.events_display.setText("\n".join(events_info) if events_info else "No recent events")


def main():
    """Launch MMPA Enhanced Visual Morphing"""
    app = QApplication(sys.argv)

    window = MMPAEnhancedMorphingDemo()
    window.show()

    logger.info("🎵 MMPA Enhanced Visual Morphing Started!")
    logger.info("🚀 Universal Signal-to-Form Engine Active")
    logger.info("📡 Features:")
    logger.info("   • MMPA Universal Signal Framework")
    logger.info("   • Signal → Analysis → Mapping → Form → Feedback loop")
    logger.info("   • MIDI Signal Processor (MPK Mini)")
    logger.info("   • 10 perfect morphing shapes")
    logger.info("   • Advanced signal-to-form mapping")
    logger.info("   • Framework ready for any signal type")
    logger.info("   • Real-time signal analysis display")

    return app.exec()

if __name__ == "__main__":
    main()