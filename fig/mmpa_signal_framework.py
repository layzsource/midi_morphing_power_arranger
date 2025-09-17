#!/usr/bin/env python3
"""
MMPA Universal Signal Framework
The foundation for transforming any signal into morphing visual forms

This implements the core MMPA loop: Signal → Analysis → Mapping → Form → Feedback
"""

import numpy as np
import time
import threading
import queue
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SignalType(Enum):
    """Universal signal types supported by MMPA"""
    MIDI = "midi"
    AUDIO = "audio"
    SENSOR = "sensor"
    DATA_STREAM = "data_stream"
    SEISMIC = "seismic"
    NEURAL = "neural"
    ROBOTIC = "robotic"
    FLUID = "fluid"

@dataclass
class SignalFeatures:
    """Universal signal features extracted from any signal type"""
    # Core features (all signals have these)
    timestamp: float
    intensity: float  # 0.0 to 1.0
    frequency: float  # Dominant frequency or rate

    # Pattern features
    rhythm_strength: float = 0.0  # How rhythmic/periodic
    complexity: float = 0.0       # How complex/chaotic
    change_rate: float = 0.0      # How fast it's changing

    # Advanced features
    spectral_centroid: float = 0.0  # Brightness/timbre
    spectral_rolloff: float = 0.0   # Energy distribution
    zero_crossing_rate: float = 0.0 # Texture measure

    # Multi-dimensional data
    frequency_bands: List[float] = field(default_factory=list)  # Spectrum
    harmonics: List[float] = field(default_factory=list)        # Harmonic content
    patterns: List[float] = field(default_factory=list)         # Detected patterns

    # Signal-specific metadata
    raw_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SignalEvent:
    """Discrete events extracted from continuous signals"""
    event_type: str           # "onset", "peak", "pattern", "change"
    timestamp: float
    intensity: float
    duration: float = 0.0
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # Spatial location if applicable
    metadata: Dict[str, Any] = field(default_factory=dict)

class SignalProcessor(ABC):
    """
    Universal base class for all signal processors in MMPA

    Each signal type (MIDI, Audio, Sensor, etc.) implements this interface
    to provide consistent signal analysis and feature extraction.
    """

    def __init__(self, signal_type: SignalType, sample_rate: float = 44100.0):
        self.signal_type = signal_type
        self.sample_rate = sample_rate
        self.is_active = False
        self.features_history = []
        self.events_history = []
        self.analysis_callbacks = []

        # Feature extraction settings
        self.feature_window_size = 1024
        self.hop_length = 512
        self.history_length = 100  # Keep last 100 feature frames

        # Real-time processing
        self.processing_thread = None
        self.signal_queue = queue.Queue()

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize signal input hardware/connections"""
        pass

    @abstractmethod
    def process_signal(self, raw_signal: Any) -> SignalFeatures:
        """
        Process raw signal input and extract universal features

        Args:
            raw_signal: Raw signal data (format depends on signal type)

        Returns:
            SignalFeatures: Standardized feature representation
        """
        pass

    @abstractmethod
    def detect_events(self, features: SignalFeatures) -> List[SignalEvent]:
        """
        Detect discrete events from signal features

        Args:
            features: Extracted signal features

        Returns:
            List of detected events
        """
        pass

    def start_processing(self):
        """Start real-time signal processing"""
        if self.is_active:
            return

        if not self.initialize():
            logger.error(f"Failed to initialize {self.signal_type.value} processor")
            return

        self.is_active = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()

        logger.info(f"✅ Started {self.signal_type.value} signal processor")

    def stop_processing(self):
        """Stop real-time signal processing"""
        self.is_active = False
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
        logger.info(f"⏹️ Stopped {self.signal_type.value} signal processor")

    def _processing_loop(self):
        """Main processing loop (runs in separate thread)"""
        while self.is_active:
            try:
                # Get raw signal (implementation-specific)
                raw_signal = self._get_raw_signal()
                if raw_signal is None:
                    time.sleep(0.001)  # 1ms sleep if no data
                    continue

                # Extract features
                features = self.process_signal(raw_signal)

                # Detect events
                events = self.detect_events(features)

                # Store in history
                self._update_history(features, events)

                # Notify listeners
                self._notify_callbacks(features, events)

            except Exception as e:
                logger.error(f"Signal processing error: {e}")
                time.sleep(0.01)

    @abstractmethod
    def _get_raw_signal(self) -> Optional[Any]:
        """Get raw signal data (implementation-specific)"""
        pass

    def _update_history(self, features: SignalFeatures, events: List[SignalEvent]):
        """Update feature and event history"""
        self.features_history.append(features)
        self.events_history.extend(events)

        # Trim history to prevent memory growth
        if len(self.features_history) > self.history_length:
            self.features_history.pop(0)

        # Keep events from last 10 seconds
        current_time = time.time()
        self.events_history = [e for e in self.events_history
                              if current_time - e.timestamp < 10.0]

    def _notify_callbacks(self, features: SignalFeatures, events: List[SignalEvent]):
        """Notify registered callbacks of new analysis"""
        for callback in self.analysis_callbacks:
            try:
                callback(self.signal_type, features, events)
            except Exception as e:
                logger.error(f"Callback error: {e}")

    def register_callback(self, callback: Callable[[SignalType, SignalFeatures, List[SignalEvent]], None]):
        """Register callback for real-time signal analysis"""
        self.analysis_callbacks.append(callback)

    def get_recent_features(self, count: int = 10) -> List[SignalFeatures]:
        """Get recent feature history"""
        return self.features_history[-count:] if self.features_history else []

    def get_recent_events(self, time_window: float = 5.0) -> List[SignalEvent]:
        """Get recent events within time window"""
        current_time = time.time()
        return [e for e in self.events_history
                if current_time - e.timestamp <= time_window]

class SignalAnalyzer:
    """
    Utility class for advanced signal analysis
    Provides common analysis functions used by all signal processors
    """

    @staticmethod
    def compute_spectral_features(signal: np.ndarray, sample_rate: float) -> Dict[str, float]:
        """Compute spectral features from signal"""
        # FFT analysis
        fft = np.fft.fft(signal)
        magnitude = np.abs(fft)
        frequencies = np.fft.fftfreq(len(signal), 1/sample_rate)

        # Spectral centroid (brightness)
        spectral_centroid = np.sum(frequencies[:len(frequencies)//2] * magnitude[:len(magnitude)//2]) / np.sum(magnitude[:len(magnitude)//2])

        # Spectral rolloff (energy distribution)
        cumsum = np.cumsum(magnitude[:len(magnitude)//2])
        rolloff_threshold = 0.85 * cumsum[-1]
        spectral_rolloff = frequencies[np.where(cumsum >= rolloff_threshold)[0][0]]

        # Zero crossing rate
        zero_crossings = np.where(np.diff(np.signbit(signal)))[0]
        zero_crossing_rate = len(zero_crossings) / len(signal) * sample_rate

        return {
            'spectral_centroid': float(spectral_centroid) if not np.isnan(spectral_centroid) else 0.0,
            'spectral_rolloff': float(spectral_rolloff) if not np.isnan(spectral_rolloff) else 0.0,
            'zero_crossing_rate': float(zero_crossing_rate)
        }

    @staticmethod
    def detect_rhythm(features_history: List[SignalFeatures]) -> float:
        """Detect rhythmic patterns in feature history"""
        if len(features_history) < 10:
            return 0.0

        # Extract intensity over time
        intensities = [f.intensity for f in features_history[-50:]]  # Last 50 frames

        # Simple autocorrelation-based rhythm detection
        if len(intensities) < 20:
            return 0.0

        autocorr = np.correlate(intensities, intensities, mode='full')
        autocorr = autocorr[len(autocorr)//2:]

        # Find peaks in autocorrelation (indicating periodicity)
        if len(autocorr) > 5:
            peak_strength = np.max(autocorr[2:min(len(autocorr), 20)]) / autocorr[0]
            return min(1.0, max(0.0, peak_strength - 0.5) * 2)

        return 0.0

    @staticmethod
    def compute_complexity(signal: np.ndarray) -> float:
        """Compute signal complexity (entropy-based measure)"""
        if len(signal) < 10:
            return 0.0

        # Histogram-based entropy
        hist, _ = np.histogram(signal, bins=50, density=True)
        hist = hist[hist > 0]  # Remove zero bins

        if len(hist) == 0:
            return 0.0

        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        normalized_entropy = entropy / np.log2(len(hist))  # Normalize to 0-1

        return min(1.0, max(0.0, normalized_entropy))

class SignalToFormMapper:
    """
    Universal mapper from signal features to visual form parameters

    This is the core of the MMPA transformation engine:
    Signal Features → Form Parameters (geometry, color, motion, particles)
    """

    def __init__(self):
        self.mapping_rules = {}
        self.adaptation_rate = 0.1
        self.mapping_history = []

        # Initialize default mappings
        self._setup_default_mappings()

    def _setup_default_mappings(self):
        """Setup default signal-to-form mappings"""
        self.mapping_rules = {
            # Intensity → Visual properties
            'intensity_to_brightness': lambda features: features.intensity,
            'intensity_to_particle_count': lambda features: int(features.intensity * 50),
            'intensity_to_scale': lambda features: 0.5 + features.intensity * 0.5,

            # Frequency → Geometric properties
            'frequency_to_hue': lambda features: (features.frequency / 1000.0) % 1.0,
            'frequency_to_morph_factor': lambda features: (features.frequency / 500.0) % 1.0,
            'frequency_to_rotation_speed': lambda features: features.frequency / 100.0,

            # Complexity → Motion properties
            'complexity_to_chaos': lambda features: features.complexity,
            'complexity_to_variation': lambda features: features.complexity * 0.5,

            # Rhythm → Animation properties
            'rhythm_to_pulse_rate': lambda features: features.rhythm_strength * 10.0,
            'rhythm_to_sync_strength': lambda features: features.rhythm_strength,

            # Spectral features → Advanced properties
            'spectral_centroid_to_shimmer': lambda features: features.spectral_centroid / 2000.0,
            'spectral_rolloff_to_spread': lambda features: features.spectral_rolloff / 4000.0,
        }

    def map_features_to_form(self, features: SignalFeatures) -> Dict[str, float]:
        """
        Map signal features to form parameters

        Returns:
            Dictionary of form parameters for visual rendering
        """
        form_params = {}

        for param_name, mapping_func in self.mapping_rules.items():
            try:
                value = mapping_func(features)
                # Ensure all values are in reasonable ranges
                if isinstance(value, (int, float)):
                    form_params[param_name] = max(0.0, min(10.0, float(value)))
                else:
                    form_params[param_name] = value
            except Exception as e:
                logger.error(f"Mapping error for {param_name}: {e}")
                form_params[param_name] = 0.0

        # Store mapping for adaptation
        self.mapping_history.append((features, form_params))
        if len(self.mapping_history) > 100:
            self.mapping_history.pop(0)

        return form_params

    def add_custom_mapping(self, name: str, mapping_func: Callable[[SignalFeatures], float]):
        """Add custom signal-to-form mapping"""
        self.mapping_rules[name] = mapping_func
        logger.info(f"✅ Added custom mapping: {name}")

    def adapt_mappings(self, feedback_score: float):
        """
        Adapt mappings based on feedback (for learning systems)

        Args:
            feedback_score: 0.0 (poor) to 1.0 (excellent) feedback on current mapping
        """
        # Simple adaptation: adjust mapping sensitivity based on feedback
        if feedback_score < 0.3:
            # Poor feedback - reduce sensitivity
            for name, func in self.mapping_rules.items():
                if 'intensity' in name or 'frequency' in name:
                    # Create dampened version of mapping
                    original_func = func
                    self.mapping_rules[name] = lambda f, orig=original_func: orig(f) * 0.8
        elif feedback_score > 0.8:
            # Great feedback - increase sensitivity
            for name, func in self.mapping_rules.items():
                if 'intensity' in name or 'frequency' in name:
                    original_func = func
                    self.mapping_rules[name] = lambda f, orig=original_func: orig(f) * 1.1

class MMPASignalEngine:
    """
    Main MMPA Signal Engine
    Coordinates multiple signal processors and the signal-to-form mapping
    """

    def __init__(self):
        self.signal_processors: Dict[SignalType, SignalProcessor] = {}
        self.signal_mapper = SignalToFormMapper()
        self.form_callbacks = []
        self.is_running = False

        # Combined signal state
        self.current_features = {}
        self.current_events = []

        logger.info("🎵 MMPA Signal Engine initialized")

    def register_processor(self, processor: SignalProcessor):
        """Register a signal processor"""
        self.signal_processors[processor.signal_type] = processor
        processor.register_callback(self._on_signal_analysis)
        logger.info(f"✅ Registered {processor.signal_type.value} processor")

    def start_engine(self):
        """Start all registered signal processors"""
        if self.is_running:
            return

        self.is_running = True

        for processor in self.signal_processors.values():
            processor.start_processing()

        logger.info("🚀 MMPA Signal Engine started")

    def stop_engine(self):
        """Stop all signal processors"""
        self.is_running = False

        for processor in self.signal_processors.values():
            processor.stop_processing()

        logger.info("⏹️ MMPA Signal Engine stopped")

    def _on_signal_analysis(self, signal_type: SignalType, features: SignalFeatures, events: List[SignalEvent]):
        """Handle signal analysis from any processor"""
        # Store current signal state
        self.current_features[signal_type] = features
        self.current_events.extend(events)

        # Map to form parameters
        form_params = self.signal_mapper.map_features_to_form(features)

        # Notify form generation callbacks
        for callback in self.form_callbacks:
            try:
                callback(signal_type, features, events, form_params)
            except Exception as e:
                logger.error(f"Form callback error: {e}")

    def register_form_callback(self, callback: Callable[[SignalType, SignalFeatures, List[SignalEvent], Dict[str, float]], None]):
        """Register callback for form generation"""
        self.form_callbacks.append(callback)

    def get_combined_features(self) -> Dict[SignalType, SignalFeatures]:
        """Get current features from all active signal types"""
        return self.current_features.copy()

    def get_recent_events(self, time_window: float = 2.0) -> List[SignalEvent]:
        """Get recent events from all signal types"""
        current_time = time.time()
        return [e for e in self.current_events
                if current_time - e.timestamp <= time_window]

# Export main classes for use in enhanced visual morphing system
__all__ = [
    'SignalType', 'SignalFeatures', 'SignalEvent', 'SignalProcessor',
    'SignalAnalyzer', 'SignalToFormMapper', 'MMPASignalEngine'
]

if __name__ == "__main__":
    # Demo the framework
    print("🎵 MMPA Universal Signal Framework Demo")
    print("Signal → Analysis → Mapping → Form → Feedback")
    print("\nFramework ready for integration with enhanced visual morphing system!")