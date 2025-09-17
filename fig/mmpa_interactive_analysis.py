#!/usr/bin/env python3
"""
MMPA Interactive Analysis Mode
Revolutionary pause, freeze, inspect, and analyze capabilities

Transform MMPA from real-time visualization into interactive analytical instrument
"""

import numpy as np
import time
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QKeyEvent, QMouseEvent, QPainter, QFont, QColor
from PySide6.QtWidgets import QWidget
import logging

logger = logging.getLogger(__name__)

class AnalysisMode(Enum):
    """Analysis mode states"""
    LIVE = "live"              # Normal real-time operation
    PAUSED = "paused"          # Freeze current frame, continue analysis
    FROZEN = "frozen"          # Complete freeze, no new data
    INSPECTION = "inspection"   # Detailed analysis mode
    LABELING = "labeling"      # Interactive tagging mode

class InteractionMode(Enum):
    """Mouse interaction modes"""
    NORMAL = "normal"          # Standard camera controls
    MEASURE = "measure"        # Frequency/time measurement
    SELECT = "select"          # Element selection
    LABEL = "label"           # Label placement

@dataclass
class FrozenMoment:
    """Captured moment for analysis"""
    timestamp: float
    signal_data: np.ndarray
    frequency_spectrum: np.ndarray
    frequencies: np.ndarray
    visual_state: Dict[str, Any]
    audio_features: Dict[str, Any]
    genre_info: Dict[str, Any]
    morph_parameters: Dict[str, float]

@dataclass
class Annotation:
    """User annotation/label"""
    id: str
    position: Tuple[float, float, float]  # 3D position
    frequency: Optional[float]
    timestamp: float
    label_type: str
    text: str
    color: Tuple[float, float, float]
    metadata: Dict[str, Any]

@dataclass
class MeasurementResult:
    """Analysis measurement result"""
    measurement_type: str
    position: Tuple[float, float]
    frequency: Optional[float]
    amplitude: Optional[float]
    value: float
    units: str
    timestamp: float

class FrequencyAnalyzer:
    """Advanced frequency analysis tools"""

    def __init__(self, sample_rate: float = 44100):
        self.sample_rate = sample_rate
        self.frequency_bands = self._create_frequency_bands()

    def _create_frequency_bands(self) -> Dict[str, Tuple[float, float]]:
        """Create frequency band definitions"""
        return {
            'sub_bass': (20, 60),
            'bass': (60, 200),
            'low_mid': (200, 500),
            'mid': (500, 2000),
            'high_mid': (2000, 6000),
            'treble': (6000, 20000)
        }

    def isolate_frequency_band(self, signal: np.ndarray, band_name: str) -> np.ndarray:
        """Isolate specific frequency band"""
        if band_name not in self.frequency_bands:
            return signal

        low_freq, high_freq = self.frequency_bands[band_name]

        # Create bandpass filter
        from scipy.signal import butter, filtfilt
        nyquist = self.sample_rate / 2
        low = low_freq / nyquist
        high = high_freq / nyquist

        # Ensure frequencies are in valid range
        low = max(0.01, min(0.99, low))
        high = max(0.01, min(0.99, high))

        if high <= low:
            return np.zeros_like(signal)

        try:
            b, a = butter(4, [low, high], btype='band')
            filtered_signal = filtfilt(b, a, signal)
            return filtered_signal
        except Exception as e:
            logger.error(f"Frequency isolation error: {e}")
            return signal

    def analyze_harmonic_content(self, signal: np.ndarray, fundamental_freq: float) -> Dict[str, float]:
        """Analyze harmonic vs inharmonic content"""
        spectrum = np.abs(np.fft.fft(signal))
        freqs = np.fft.fftfreq(len(signal), 1/self.sample_rate)

        # Find harmonics (2f, 3f, 4f, 5f, 6f)
        harmonics = [2, 3, 4, 5, 6]
        harmonic_energy = 0
        total_energy = np.sum(spectrum**2)

        for harmonic in harmonics:
            harmonic_freq = fundamental_freq * harmonic
            # Find closest frequency bin
            idx = np.argmin(np.abs(freqs - harmonic_freq))
            # Sum energy in small window around harmonic
            window = 5
            start_idx = max(0, idx - window)
            end_idx = min(len(spectrum), idx + window + 1)
            harmonic_energy += np.sum(spectrum[start_idx:end_idx]**2)

        harmonic_ratio = harmonic_energy / total_energy if total_energy > 0 else 0
        inharmonic_ratio = 1.0 - harmonic_ratio

        return {
            'harmonic_ratio': float(harmonic_ratio),
            'inharmonic_ratio': float(inharmonic_ratio),
            'total_energy': float(total_energy),
            'harmonic_energy': float(harmonic_energy)
        }

    def detect_dissonance_level(self, spectrum: np.ndarray, freqs: np.ndarray) -> float:
        """Calculate sensory dissonance using Plomp-Levelt curves"""
        # Simplified dissonance calculation
        # Based on frequency ratios and amplitude interactions

        # Find peaks in spectrum
        peak_indices = []
        for i in range(1, len(spectrum) - 1):
            if spectrum[i] > spectrum[i-1] and spectrum[i] > spectrum[i+1] and spectrum[i] > 0.1 * np.max(spectrum):
                peak_indices.append(i)

        if len(peak_indices) < 2:
            return 0.0

        # Calculate dissonance between peak pairs
        total_dissonance = 0
        for i, idx1 in enumerate(peak_indices):
            for j, idx2 in enumerate(peak_indices[i+1:], i+1):
                f1, f2 = freqs[idx1], freqs[idx2]
                a1, a2 = spectrum[idx1], spectrum[idx2]

                if f1 > 0 and f2 > 0:
                    # Frequency ratio
                    ratio = f2 / f1 if f2 > f1 else f1 / f2

                    # Plomp-Levelt dissonance curve approximation
                    if ratio < 1.2:  # Very close frequencies
                        dissonance = 1.0 - (ratio - 1.0) * 5.0
                    elif ratio < 2.0:  # Moderate intervals
                        dissonance = 0.5 * (2.0 - ratio)
                    else:  # Wide intervals
                        dissonance = 0.1

                    # Weight by amplitudes
                    weight = min(a1, a2) / max(a1, a2) if max(a1, a2) > 0 else 0
                    total_dissonance += dissonance * weight

        return min(1.0, total_dissonance / len(peak_indices))

class LabelingSystem:
    """Interactive labeling and annotation system"""

    def __init__(self):
        self.annotations: List[Annotation] = []
        self.label_types = {
            'frequency': {'color': (1.0, 0.8, 0.2), 'shape': 'circle'},
            'harmonic': {'color': (0.8, 1.0, 0.2), 'shape': 'diamond'},
            'dissonance': {'color': (1.0, 0.2, 0.2), 'shape': 'triangle'},
            'consonance': {'color': (0.2, 1.0, 0.2), 'shape': 'square'},
            'pattern': {'color': (0.2, 0.8, 1.0), 'shape': 'star'},
            'custom': {'color': (1.0, 1.0, 1.0), 'shape': 'circle'}
        }
        self.current_label_type = 'frequency'

    def add_annotation(self, position: Tuple[float, float, float], text: str,
                      frequency: Optional[float] = None, metadata: Optional[Dict] = None) -> str:
        """Add new annotation"""
        annotation_id = f"label_{len(self.annotations)}_{int(time.time())}"

        annotation = Annotation(
            id=annotation_id,
            position=position,
            frequency=frequency,
            timestamp=time.time(),
            label_type=self.current_label_type,
            text=text,
            color=self.label_types[self.current_label_type]['color'],
            metadata=metadata or {}
        )

        self.annotations.append(annotation)
        logger.info(f"Added annotation: {text} at {position}")
        return annotation_id

    def remove_annotation(self, annotation_id: str) -> bool:
        """Remove annotation by ID"""
        for i, annotation in enumerate(self.annotations):
            if annotation.id == annotation_id:
                del self.annotations[i]
                logger.info(f"Removed annotation: {annotation_id}")
                return True
        return False

    def get_annotations_near(self, position: Tuple[float, float, float], radius: float = 0.1) -> List[Annotation]:
        """Get annotations near a position"""
        nearby = []
        px, py, pz = position

        for annotation in self.annotations:
            ax, ay, az = annotation.position
            distance = np.sqrt((px - ax)**2 + (py - ay)**2 + (pz - az)**2)
            if distance <= radius:
                nearby.append(annotation)

        return nearby

    def export_annotations(self) -> List[Dict]:
        """Export annotations to JSON-serializable format"""
        return [
            {
                'id': ann.id,
                'position': ann.position,
                'frequency': ann.frequency,
                'timestamp': ann.timestamp,
                'label_type': ann.label_type,
                'text': ann.text,
                'color': ann.color,
                'metadata': ann.metadata
            }
            for ann in self.annotations
        ]

class AnalysisStateManager(QObject):
    """Manages analysis mode state and transitions"""

    # Signals
    mode_changed = Signal(AnalysisMode)
    moment_frozen = Signal(FrozenMoment)
    annotation_added = Signal(Annotation)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = AnalysisMode.LIVE
        self.interaction_mode = InteractionMode.NORMAL
        self.frozen_moment: Optional[FrozenMoment] = None
        self.frequency_analyzer = FrequencyAnalyzer()
        self.labeling_system = LabelingSystem()
        self.measurements: List[MeasurementResult] = []

        # Analysis settings
        self.zoom_level = 1.0
        self.selected_frequency_band = 'full'
        self.show_frequency_grid = False
        self.show_harmonic_overlay = False

        logger.info("🔬 Analysis State Manager initialized")

    def set_mode(self, new_mode: AnalysisMode):
        """Change analysis mode"""
        if new_mode != self.current_mode:
            old_mode = self.current_mode
            self.current_mode = new_mode
            self.mode_changed.emit(new_mode)
            logger.info(f"Analysis mode: {old_mode} → {new_mode}")

    def freeze_current_moment(self, signal_data: np.ndarray, visual_state: Dict[str, Any],
                            audio_features: Dict[str, Any], genre_info: Dict[str, Any],
                            morph_parameters: Dict[str, float]) -> FrozenMoment:
        """Capture current moment for analysis"""

        # Calculate frequency spectrum
        windowed_signal = signal_data * np.hanning(len(signal_data))
        spectrum = np.abs(np.fft.fft(windowed_signal))
        frequencies = np.fft.fftfreq(len(windowed_signal), 1/44100)

        # Create frozen moment
        self.frozen_moment = FrozenMoment(
            timestamp=time.time(),
            signal_data=signal_data.copy(),
            frequency_spectrum=spectrum[:len(spectrum)//2].copy(),
            frequencies=frequencies[:len(frequencies)//2].copy(),
            visual_state=visual_state.copy(),
            audio_features=audio_features.copy(),
            genre_info=genre_info.copy(),
            morph_parameters=morph_parameters.copy()
        )

        self.moment_frozen.emit(self.frozen_moment)
        logger.info(f"🧊 Moment frozen for analysis - {len(signal_data)} samples")
        return self.frozen_moment

    def analyze_frozen_moment(self) -> Dict[str, Any]:
        """Perform deep analysis on frozen moment"""
        if not self.frozen_moment:
            return {}

        analysis = {
            'timestamp': self.frozen_moment.timestamp,
            'signal_length': len(self.frozen_moment.signal_data),
            'dominant_frequency': float(self.frozen_moment.frequencies[np.argmax(self.frozen_moment.frequency_spectrum)]),
            'total_energy': float(np.sum(self.frozen_moment.frequency_spectrum**2)),
            'spectral_centroid': float(np.sum(self.frozen_moment.frequencies * self.frozen_moment.frequency_spectrum) /
                                     np.sum(self.frozen_moment.frequency_spectrum)),
        }

        # Harmonic analysis
        if analysis['dominant_frequency'] > 0:
            harmonic_analysis = self.frequency_analyzer.analyze_harmonic_content(
                self.frozen_moment.signal_data, analysis['dominant_frequency']
            )
            analysis.update(harmonic_analysis)

        # Dissonance analysis
        dissonance = self.frequency_analyzer.detect_dissonance_level(
            self.frozen_moment.frequency_spectrum, self.frozen_moment.frequencies
        )
        analysis['dissonance_level'] = dissonance

        # Frequency band analysis
        band_energies = {}
        for band_name in self.frequency_analyzer.frequency_bands:
            band_signal = self.frequency_analyzer.isolate_frequency_band(
                self.frozen_moment.signal_data, band_name
            )
            band_energies[band_name] = float(np.sum(band_signal**2))

        analysis['frequency_bands'] = band_energies

        return analysis

    def add_measurement(self, measurement_type: str, position: Tuple[float, float],
                       frequency: Optional[float] = None, amplitude: Optional[float] = None,
                       value: float = 0.0, units: str = "") -> str:
        """Add measurement result"""
        measurement = MeasurementResult(
            measurement_type=measurement_type,
            position=position,
            frequency=frequency,
            amplitude=amplitude,
            value=value,
            units=units,
            timestamp=time.time()
        )

        self.measurements.append(measurement)
        logger.info(f"📏 Added measurement: {measurement_type} = {value} {units}")
        return f"measurement_{len(self.measurements)}"

    def get_frequency_at_position(self, x_position: float, viewport_width: float) -> float:
        """Convert screen x position to frequency"""
        if not self.frozen_moment:
            return 0.0

        # Map x position (0-1) to frequency range
        max_freq = self.frozen_moment.frequencies[-1]
        frequency = x_position * max_freq / viewport_width
        return max(0, min(max_freq, frequency))

    def get_amplitude_at_frequency(self, target_frequency: float) -> float:
        """Get amplitude at specific frequency"""
        if not self.frozen_moment:
            return 0.0

        # Find closest frequency bin
        idx = np.argmin(np.abs(self.frozen_moment.frequencies - target_frequency))
        return float(self.frozen_moment.frequency_spectrum[idx])

    def export_analysis_session(self) -> Dict[str, Any]:
        """Export complete analysis session"""
        session_data = {
            'timestamp': time.time(),
            'current_mode': self.current_mode.value,
            'zoom_level': self.zoom_level,
            'selected_band': self.selected_frequency_band,
            'annotations': self.labeling_system.export_annotations(),
            'measurements': [
                {
                    'type': m.measurement_type,
                    'position': m.position,
                    'frequency': m.frequency,
                    'amplitude': m.amplitude,
                    'value': m.value,
                    'units': m.units,
                    'timestamp': m.timestamp
                }
                for m in self.measurements
            ]
        }

        if self.frozen_moment:
            session_data['frozen_moment'] = {
                'timestamp': self.frozen_moment.timestamp,
                'audio_features': self.frozen_moment.audio_features,
                'genre_info': self.frozen_moment.genre_info,
                'morph_parameters': self.frozen_moment.morph_parameters,
                'analysis_results': self.analyze_frozen_moment()
            }

        return session_data

# Key binding constants
class AnalysisKeys:
    """Keyboard shortcuts for analysis mode"""
    PAUSE_RESUME = Qt.Key_Space
    FREEZE = Qt.Key_F
    INSPECTION = Qt.Key_I
    LABELING = Qt.Key_L
    ESCAPE = Qt.Key_Escape
    ZOOM_IN = Qt.Key_Plus
    ZOOM_OUT = Qt.Key_Minus
    TOGGLE_GRID = Qt.Key_G
    TOGGLE_HARMONICS = Qt.Key_H
    EXPORT = Qt.Key_E

# Test the analysis system
def test_analysis_system():
    """Test the interactive analysis system"""
    print("🧪 Testing MMPA Interactive Analysis System")
    print("=" * 50)

    # Create test signal
    sample_rate = 44100
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Complex test signal with harmonics and noise
    fundamental = 220  # A3
    test_signal = (np.sin(2 * np.pi * fundamental * t) +
                  0.5 * np.sin(2 * np.pi * fundamental * 2 * t) +  # 2nd harmonic
                  0.3 * np.sin(2 * np.pi * fundamental * 3 * t) +  # 3rd harmonic
                  0.1 * np.random.normal(0, 1, len(t)))  # Noise

    # Initialize analysis system
    analyzer = FrequencyAnalyzer(sample_rate)
    state_manager = AnalysisStateManager()

    print("✅ Analysis system initialized")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Test signal: {len(test_signal)} samples")
    print(f"Fundamental frequency: {fundamental} Hz")

    # Test frequency band isolation
    print("\n🎵 Testing frequency band isolation...")
    for band_name in analyzer.frequency_bands:
        isolated = analyzer.isolate_frequency_band(test_signal, band_name)
        energy = np.sum(isolated**2)
        print(f"  {band_name}: {energy:.3f} energy")

    # Test harmonic analysis
    print("\n🎼 Testing harmonic analysis...")
    harmonic_results = analyzer.analyze_harmonic_content(test_signal, fundamental)
    for key, value in harmonic_results.items():
        print(f"  {key}: {value:.3f}")

    # Test dissonance detection
    print("\n🎭 Testing dissonance analysis...")
    spectrum = np.abs(np.fft.fft(test_signal))
    frequencies = np.fft.fftfreq(len(test_signal), 1/sample_rate)
    dissonance = analyzer.detect_dissonance_level(spectrum[:len(spectrum)//2],
                                                frequencies[:len(frequencies)//2])
    print(f"  Dissonance level: {dissonance:.3f}")

    # Test moment freezing
    print("\n🧊 Testing moment freezing...")
    visual_state = {'shape_a': 'sphere', 'shape_b': 'cube', 'morph_factor': 0.5}
    audio_features = {'rms': 0.3, 'spectral_centroid': 1500}
    genre_info = {'genre': 'test', 'confidence': 0.8}
    morph_params = {'rotation': 45, 'scale': 1.2}

    frozen_moment = state_manager.freeze_current_moment(
        test_signal, visual_state, audio_features, genre_info, morph_params
    )

    print(f"  Frozen moment timestamp: {frozen_moment.timestamp}")
    print(f"  Signal samples: {len(frozen_moment.signal_data)}")
    print(f"  Spectrum bins: {len(frozen_moment.frequency_spectrum)}")

    # Test analysis
    print("\n📊 Testing frozen moment analysis...")
    analysis_results = state_manager.analyze_frozen_moment()
    for key, value in analysis_results.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value:.3f}")
        else:
            print(f"  {key}: {value:.3f}")

    # Test labeling system
    print("\n🏷️ Testing labeling system...")
    labeling = state_manager.labeling_system

    # Add test annotations
    labeling.add_annotation((0.5, 0.5, 0.0), "Fundamental frequency", frequency=fundamental)
    labeling.add_annotation((0.3, 0.7, 0.0), "Second harmonic", frequency=fundamental*2)
    labeling.add_annotation((0.8, 0.2, 0.0), "Noise component")

    print(f"  Added {len(labeling.annotations)} annotations")
    for ann in labeling.annotations:
        print(f"    {ann.text} at {ann.position}")

    # Test export
    print("\n💾 Testing export functionality...")
    export_data = state_manager.export_analysis_session()
    print(f"  Export data keys: {list(export_data.keys())}")
    print(f"  Annotations exported: {len(export_data['annotations'])}")
    print(f"  Measurements exported: {len(export_data['measurements'])}")

    print("\n✅ Interactive Analysis System Test Complete!")
    print("🚀 Ready for integration with MMPA visualization")

if __name__ == "__main__":
    test_analysis_system()