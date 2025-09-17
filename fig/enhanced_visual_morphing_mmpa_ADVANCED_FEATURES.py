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

# Import our MMPA framework
from mmpa_signal_framework import (
    MMPASignalEngine, SignalType, SignalFeatures, SignalEvent, SignalToFormMapper
)
from mmpa_midi_processor import MIDISignalProcessor
from mmpa_audio_processor import AudioSignalProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.shape_resolution = 800

        # MMPA Integration
        self.mmpa_engine = MMPASignalEngine()
        self.current_form_params = {}
        self.signal_history = []

        # Musical Intelligence Integration
        self.current_genre = 'unknown'
        self.current_key = 'C major'
        self.current_chord = 'unknown'
        self.genre_visual_styles = self._setup_genre_visual_styles()
        self.key_color_palettes = self._setup_key_color_palettes()

        # Setup MMPA signal processors
        self._setup_mmpa_processors()

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60 FPS

        logger.info("🎵 MMPA Morph Widget initialized")

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
        """Handle signal-to-form transformation from MMPA engine"""

        # Store current form parameters
        self.current_form_params = form_params

        # Store signal history for analysis
        self.signal_history.append({
            'timestamp': features.timestamp,
            'signal_type': signal_type,
            'features': features,
            'events': events,
            'form_params': form_params
        })

        # Keep last 100 signal frames
        if len(self.signal_history) > 100:
            self.signal_history.pop(0)

        # Apply MMPA mappings to visual system
        self._apply_mmpa_mappings(signal_type, features, events, form_params)

        # Apply advanced musical intelligence mappings
        self._apply_musical_intelligence_mappings(signal_type, features)

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
        particle_count = max(2, int(event.intensity * 30))
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
            particle_count = int(energy * 15)
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

    def _apply_musical_intelligence_mappings(self, signal_type: SignalType, features: SignalFeatures):
        """Apply advanced musical intelligence to visual parameters"""
        if signal_type != SignalType.AUDIO:
            return

        raw_data = features.raw_data

        # Genre-based visual styling
        genre = raw_data.get('genre', 'unknown')
        if genre != 'unknown' and genre != self.current_genre:
            self.current_genre = genre
            self._apply_genre_visual_style(genre)

        # Key signature-based color palette
        key_signature = raw_data.get('key_signature', 'C major')
        if key_signature != self.current_key:
            self.current_key = key_signature
            self._apply_key_color_palette(key_signature)

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

        logger.info(f"🎭 Applied {genre} visual style")

    def _apply_key_color_palette(self, key_signature: str):
        """Apply color palette based on detected key signature"""
        if key_signature in self.key_color_palettes:
            hue, sat, val = self.key_color_palettes[key_signature]
            self.mmpa_color = (hue, sat, val)
            logger.info(f"🎨 Applied {key_signature} color palette")

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
            particle_count = int(harmonic_richness * 20)
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
        particle_count = int(chaos_level * 30)
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
            particle_count = int(band_energy * 15)

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
        """Initialize OpenGL with enhanced settings"""
        glClearColor(0.02, 0.02, 0.08, 1.0)
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
            rotation_speed = getattr(self, 'rotation_speed', 0.8)
            glTranslatef(0.0, 0.0, -6.0)
            glRotatef(self.rotation * rotation_speed, 1.0, 1.0, 0.0)
            glRotatef(self.rotation * 0.3, 0.0, 1.0, 0.0)

            # Generate and render morphed shape
            vertices = self.generate_morphed_shape()
            self.render_morphed_shape(vertices)

            # Render enhanced particles
            self.render_enhanced_particles()

        except Exception as e:
            logger.error(f"Render error: {e}")

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

        # Add all other shapes from our stable system...
        else:
            return self.generate_shape('sphere')

        return vertices

    def render_morphed_shape(self, vertices):
        """Render the morphed shape with enhanced effects"""
        if not vertices:
            return

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

        glPointSize(2.5)
        glBegin(GL_POINTS)
        for vertex in vertices:
            glVertex3f(vertex[0], vertex[1], vertex[2])
        glEnd()

    def render_enhanced_particles(self):
        """Render particles with enhanced effects"""
        if not self.particles:
            return

        # Enable better blending for particles
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for glow

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

    def update_animation(self):
        """Update animation with enhanced effects"""
        self.rotation += getattr(self, 'rotation_speed', 0.8)

        # Update particles with chaos factor
        for particle in self.particles[:]:
            particle['life'] -= 0.015

            # Apply movement with chaos
            chaos = particle.get('chaos_factor', 0.0)
            chaos_x = (np.random.random() - 0.5) * chaos * 0.001
            chaos_y = (np.random.random() - 0.5) * chaos * 0.001
            chaos_z = (np.random.random() - 0.5) * chaos * 0.001

            particle['x'] += particle['vx'] * 0.02 + chaos_x
            particle['y'] += particle['vy'] * 0.02 + chaos_y
            particle['z'] += particle['vz'] * 0.02 + chaos_z

            particle['vy'] -= 0.001  # Gravity

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

        # Start signal analysis display timer
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self._update_signal_analysis)
        self.analysis_timer.start(1000)  # Update every second

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

    def _update_audio_level_display(self, combined_features):
        """Update audio level progress bar"""
        if SignalType.AUDIO in combined_features:
            audio_features = combined_features[SignalType.AUDIO]
            level = min(audio_features.intensity * 100, 100)
            self.audio_level_bar.setValue(int(level))

            # Color coding for level
            if level > 80:
                self.audio_level_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif level > 50:
                self.audio_level_bar.setStyleSheet("QProgressBar::chunk { background-color: yellow; }")
            else:
                self.audio_level_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        else:
            self.audio_level_bar.setValue(0)

    def _update_audio_device(self, device_name):
        """Handle audio device selection changes"""
        if device_name == "Refresh Devices":
            # TODO: Refresh available audio devices
            logger.info("🔄 Refreshing audio devices...")
        else:
            logger.info(f"🎤 Audio device selected: {device_name}")

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