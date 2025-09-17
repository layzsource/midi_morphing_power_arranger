#!/usr/bin/env python3
"""
MMPA MIDI Signal Processor
Converts MIDI input into universal MMPA signal features

This plugin transforms our existing MIDI system into the universal signal framework
"""

import numpy as np
import time
import threading
import rtmidi
from typing import Optional, List, Any, Dict
import logging

from mmpa_signal_framework import (
    SignalProcessor, SignalType, SignalFeatures, SignalEvent, SignalAnalyzer
)

logger = logging.getLogger(__name__)

class MIDISignalProcessor(SignalProcessor):
    """
    MIDI Signal Processor for MMPA Universal Framework

    Converts MIDI notes, CCs, and other MIDI data into universal SignalFeatures
    """

    def __init__(self, device_name: Optional[str] = None):
        super().__init__(SignalType.MIDI, sample_rate=1000.0)  # MIDI is event-based, not sample-based

        self.device_name = device_name
        self.midi_input = None
        self.midi_messages = []
        self.midi_lock = threading.Lock()

        # MIDI state tracking
        self.active_notes = {}  # note -> (velocity, timestamp)
        self.cc_values = {}     # cc -> value
        self.last_note_time = 0.0
        self.last_cc_time = 0.0

        # Musical analysis
        self.note_history = []  # For musical pattern detection
        self.velocity_history = []
        self.timing_history = []

        logger.info("🎹 MIDI Signal Processor initialized")

    def initialize(self) -> bool:
        """Initialize MIDI input connection"""
        try:
            self.midi_input = rtmidi.MidiIn()
            ports = self.midi_input.get_ports()

            if not ports:
                logger.warning("⚠️ No MIDI devices found")
                return False

            # Find target device
            target_port = 0
            if self.device_name:
                for i, port in enumerate(ports):
                    if self.device_name.lower() in port.lower():
                        target_port = i
                        break

            # Connect to MIDI device
            self.midi_input.open_port(target_port)
            self.midi_input.set_callback(self._midi_callback)

            logger.info(f"✅ Connected to MIDI device: {ports[target_port]}")
            return True

        except Exception as e:
            logger.error(f"❌ MIDI initialization failed: {e}")
            return False

    def _midi_callback(self, event, data=None):
        """Handle incoming MIDI messages"""
        message, deltatime = event

        with self.midi_lock:
            self.midi_messages.append({
                'message': message,
                'timestamp': time.time(),
                'deltatime': deltatime
            })

    def _get_raw_signal(self) -> Optional[Dict]:
        """Get raw MIDI messages"""
        with self.midi_lock:
            if self.midi_messages:
                return self.midi_messages.pop(0)
            return None

    def process_signal(self, raw_signal: Dict) -> SignalFeatures:
        """
        Process MIDI message and extract universal features

        Args:
            raw_signal: Dictionary with MIDI message data

        Returns:
            SignalFeatures: Universal signal features
        """
        message = raw_signal['message']
        timestamp = raw_signal['timestamp']

        # Parse MIDI message
        if len(message) >= 3:
            status = message[0]
            data1 = message[1]
            data2 = message[2]

            # Note On/Off messages
            if (status & 0xF0) in [0x90, 0x80]:  # Note events
                note = data1
                velocity = data2 if (status & 0xF0) == 0x90 else 0

                # Update active notes
                if velocity > 0:
                    self.active_notes[note] = (velocity, timestamp)
                    self.note_history.append((note, velocity, timestamp))
                    self.velocity_history.append(velocity)
                    self.last_note_time = timestamp
                else:
                    self.active_notes.pop(note, None)

            # Control Change messages
            elif (status & 0xF0) == 0xB0:
                cc = data1
                value = data2
                self.cc_values[cc] = value
                self.last_cc_time = timestamp

        # Extract universal features from current MIDI state
        return self._extract_features(timestamp)

    def _extract_features(self, timestamp: float) -> SignalFeatures:
        """Extract universal signal features from MIDI state"""

        # Core features
        intensity = self._compute_intensity()
        frequency = self._compute_dominant_frequency()

        # Pattern features
        rhythm_strength = self._compute_rhythm_strength()
        complexity = self._compute_complexity()
        change_rate = self._compute_change_rate(timestamp)

        # MIDI-specific spectral features
        spectral_features = self._compute_spectral_features()

        # Multi-dimensional data
        frequency_bands = self._compute_frequency_bands()
        harmonics = self._compute_harmonics()
        patterns = self._detect_musical_patterns()

        # Raw MIDI data for specialized processing
        raw_data = {
            'active_notes': dict(self.active_notes),
            'cc_values': dict(self.cc_values),
            'polyphony': len(self.active_notes),
            'latest_note': max(self.active_notes.keys()) if self.active_notes else 0,
            'latest_velocity': max(v[0] for v in self.active_notes.values()) if self.active_notes else 0
        }

        return SignalFeatures(
            timestamp=timestamp,
            intensity=intensity,
            frequency=frequency,
            rhythm_strength=rhythm_strength,
            complexity=complexity,
            change_rate=change_rate,
            spectral_centroid=spectral_features['spectral_centroid'],
            spectral_rolloff=spectral_features['spectral_rolloff'],
            zero_crossing_rate=spectral_features['zero_crossing_rate'],
            frequency_bands=frequency_bands,
            harmonics=harmonics,
            patterns=patterns,
            raw_data=raw_data
        )

    def _compute_intensity(self) -> float:
        """Compute overall intensity from active notes and recent activity"""
        if not self.active_notes:
            return 0.0

        # Intensity from active notes (polyphonic)
        active_intensity = sum(v[0] for v in self.active_notes.values()) / (127.0 * max(1, len(self.active_notes)))

        # Recent velocity activity
        recent_velocities = [v for v in self.velocity_history[-10:] if v > 0]
        recent_intensity = (sum(recent_velocities) / len(recent_velocities) / 127.0) if recent_velocities else 0.0

        # Combine with decay for sustained notes
        time_decay = max(0.1, 1.0 - (time.time() - self.last_note_time) / 2.0)  # 2 second decay

        return min(1.0, (active_intensity + recent_intensity) * time_decay)

    def _compute_dominant_frequency(self) -> float:
        """Compute dominant frequency from active notes"""
        if not self.active_notes:
            return 0.0

        # Convert MIDI notes to frequencies, weight by velocity
        weighted_freqs = []
        total_weight = 0

        for note, (velocity, _) in self.active_notes.items():
            # MIDI note to frequency: f = 440 * 2^((n-69)/12)
            frequency = 440.0 * (2.0 ** ((note - 69) / 12.0))
            weight = velocity / 127.0

            weighted_freqs.append(frequency * weight)
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return sum(weighted_freqs) / total_weight

    def _compute_rhythm_strength(self) -> float:
        """Compute rhythm strength from note timing patterns"""
        if len(self.note_history) < 4:
            return 0.0

        # Get recent note timings
        recent_notes = self.note_history[-20:]  # Last 20 notes
        timings = [n[2] for n in recent_notes]

        if len(timings) < 4:
            return 0.0

        # Compute inter-onset intervals
        intervals = [timings[i+1] - timings[i] for i in range(len(timings)-1)]

        if not intervals:
            return 0.0

        # Rhythm strength from interval regularity
        mean_interval = np.mean(intervals)
        interval_variance = np.var(intervals)

        if mean_interval == 0:
            return 0.0

        # More regular = higher rhythm strength
        regularity = 1.0 / (1.0 + interval_variance / (mean_interval ** 2))
        return min(1.0, regularity)

    def _compute_complexity(self) -> float:
        """Compute harmonic/melodic complexity"""
        if len(self.note_history) < 5:
            return 0.0

        # Recent notes for analysis
        recent_notes = [n[0] for n in self.note_history[-12:]]  # Last 12 notes

        # Pitch class diversity (chromatic complexity)
        pitch_classes = set(note % 12 for note in recent_notes)
        chromatic_complexity = len(pitch_classes) / 12.0

        # Interval diversity (melodic complexity)
        intervals = [abs(recent_notes[i+1] - recent_notes[i]) for i in range(len(recent_notes)-1)]
        interval_variety = len(set(intervals)) / max(1, len(intervals))

        # Polyphonic complexity
        polyphonic_complexity = min(1.0, len(self.active_notes) / 6.0)  # 6+ notes = high complexity

        return (chromatic_complexity + interval_variety + polyphonic_complexity) / 3.0

    def _compute_change_rate(self, timestamp: float) -> float:
        """Compute rate of change in MIDI activity"""
        if not self.note_history:
            return 0.0

        # Notes in last second
        recent_notes = [n for n in self.note_history if timestamp - n[2] <= 1.0]
        note_rate = len(recent_notes)  # Notes per second

        # CC change rate
        cc_change_rate = 1.0 if timestamp - self.last_cc_time <= 0.1 else 0.0

        # Normalize and combine
        normalized_note_rate = min(1.0, note_rate / 20.0)  # 20 notes/sec = max

        return (normalized_note_rate + cc_change_rate) / 2.0

    def _compute_spectral_features(self) -> Dict[str, float]:
        """Compute spectral-like features from MIDI harmony"""
        if not self.active_notes:
            return {'spectral_centroid': 0.0, 'spectral_rolloff': 0.0, 'zero_crossing_rate': 0.0}

        # Active note frequencies and weights
        frequencies = []
        weights = []

        for note, (velocity, _) in self.active_notes.items():
            freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
            frequencies.append(freq)
            weights.append(velocity / 127.0)

        if not frequencies:
            return {'spectral_centroid': 0.0, 'spectral_rolloff': 0.0, 'zero_crossing_rate': 0.0}

        frequencies = np.array(frequencies)
        weights = np.array(weights)

        # Spectral centroid (weighted mean frequency)
        spectral_centroid = np.sum(frequencies * weights) / np.sum(weights)

        # Spectral rolloff (frequency below which 85% of energy lies)
        sorted_indices = np.argsort(frequencies)
        cumulative_weights = np.cumsum(weights[sorted_indices])
        total_weight = np.sum(weights)
        rolloff_index = np.where(cumulative_weights >= 0.85 * total_weight)[0]
        spectral_rolloff = frequencies[sorted_indices[rolloff_index[0]]] if len(rolloff_index) > 0 else frequencies[-1]

        # Zero crossing rate (harmonic dissonance approximation)
        # Higher for more dissonant intervals
        zero_crossing_rate = 0.0
        if len(frequencies) > 1:
            freq_ratios = []
            for i in range(len(frequencies)):
                for j in range(i+1, len(frequencies)):
                    ratio = frequencies[j] / frequencies[i]
                    # Distance from simple ratios (octave, fifth, fourth, etc.)
                    simple_ratios = [2.0, 1.5, 1.333, 1.25, 1.2]
                    min_distance = min(abs(ratio - sr) for sr in simple_ratios)
                    freq_ratios.append(min_distance)

            zero_crossing_rate = np.mean(freq_ratios) if freq_ratios else 0.0

        return {
            'spectral_centroid': float(spectral_centroid),
            'spectral_rolloff': float(spectral_rolloff),
            'zero_crossing_rate': float(zero_crossing_rate)
        }

    def _compute_frequency_bands(self) -> List[float]:
        """Compute frequency band representation (like audio spectrum)"""
        # Define 6 frequency bands (similar to audio analysis)
        bands = [
            (80, 250),    # Bass
            (250, 500),   # Low-mid
            (500, 1000),  # Mid
            (1000, 2000), # High-mid
            (2000, 4000), # Treble
            (4000, 8000)  # Ultra
        ]

        band_energies = []

        for low_freq, high_freq in bands:
            energy = 0.0

            for note, (velocity, _) in self.active_notes.items():
                freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
                if low_freq <= freq <= high_freq:
                    energy += velocity / 127.0

            band_energies.append(energy)

        # Normalize to 0-1 range
        max_energy = max(band_energies) if band_energies else 1.0
        if max_energy > 0:
            band_energies = [e / max_energy for e in band_energies]

        return band_energies

    def _compute_harmonics(self) -> List[float]:
        """Compute harmonic content from active notes"""
        if not self.active_notes:
            return [0.0] * 8

        # Find fundamental frequency (lowest active note)
        fundamental_note = min(self.active_notes.keys())
        fundamental_freq = 440.0 * (2.0 ** ((fundamental_note - 69) / 12.0))

        harmonics = []

        # Check for harmonics (2f, 3f, 4f, etc.)
        for harmonic_num in range(1, 9):  # 8 harmonics
            target_freq = fundamental_freq * harmonic_num
            harmonic_strength = 0.0

            # Find closest active note to this harmonic
            for note, (velocity, _) in self.active_notes.items():
                note_freq = 440.0 * (2.0 ** ((note - 69) / 12.0))
                freq_ratio = note_freq / target_freq

                # If close to harmonic frequency
                if 0.9 <= freq_ratio <= 1.1:
                    harmonic_strength = max(harmonic_strength, velocity / 127.0)

            harmonics.append(harmonic_strength)

        return harmonics

    def _detect_musical_patterns(self) -> List[float]:
        """Detect musical patterns and motifs"""
        if len(self.note_history) < 8:
            return [0.0] * 4

        # Recent note sequence
        recent_notes = [n[0] for n in self.note_history[-16:]]

        patterns = []

        # Pattern 1: Ascending/descending sequences
        if len(recent_notes) >= 4:
            last_4 = recent_notes[-4:]
            ascending = all(last_4[i] <= last_4[i+1] for i in range(3))
            descending = all(last_4[i] >= last_4[i+1] for i in range(3))
            patterns.append(1.0 if ascending or descending else 0.0)
        else:
            patterns.append(0.0)

        # Pattern 2: Repetition (note appears multiple times recently)
        if recent_notes:
            most_common_note = max(set(recent_notes), key=recent_notes.count)
            repetition_strength = recent_notes.count(most_common_note) / len(recent_notes)
            patterns.append(repetition_strength)
        else:
            patterns.append(0.0)

        # Pattern 3: Scale patterns (stepwise motion)
        stepwise_motion = 0.0
        if len(recent_notes) >= 3:
            steps = [abs(recent_notes[i+1] - recent_notes[i]) for i in range(len(recent_notes)-1)]
            small_steps = sum(1 for step in steps if step <= 2)  # Half/whole steps
            stepwise_motion = small_steps / len(steps)
        patterns.append(stepwise_motion)

        # Pattern 4: Rhythmic regularity
        patterns.append(self._compute_rhythm_strength())

        return patterns

    def detect_events(self, features: SignalFeatures) -> List[SignalEvent]:
        """Detect discrete MIDI events"""
        events = []
        current_time = time.time()

        # Note onset events
        recent_notes = [n for n in self.note_history if current_time - n[2] <= 0.1]  # Last 100ms
        for note, velocity, timestamp in recent_notes:
            if current_time - timestamp <= 0.05:  # Very recent (50ms)
                events.append(SignalEvent(
                    event_type="note_onset",
                    timestamp=timestamp,
                    intensity=velocity / 127.0,
                    duration=0.0,  # Unknown duration yet
                    metadata={'note': note, 'velocity': velocity}
                ))

        # Pattern events
        if features.patterns and len(features.patterns) > 0:
            # Strong pattern detected
            if features.patterns[0] > 0.8:  # Ascending/descending pattern
                events.append(SignalEvent(
                    event_type="pattern",
                    timestamp=current_time,
                    intensity=features.patterns[0],
                    metadata={'pattern_type': 'sequence'}
                ))

            if features.patterns[1] > 0.7:  # Repetition pattern
                events.append(SignalEvent(
                    event_type="pattern",
                    timestamp=current_time,
                    intensity=features.patterns[1],
                    metadata={'pattern_type': 'repetition'}
                ))

        # Intensity events (forte/fortissimo)
        if features.intensity > 0.8:
            events.append(SignalEvent(
                event_type="peak",
                timestamp=current_time,
                intensity=features.intensity,
                metadata={'peak_type': 'intensity'}
            ))

        # Complexity events (dense harmony)
        if features.complexity > 0.7:
            events.append(SignalEvent(
                event_type="complexity",
                timestamp=current_time,
                intensity=features.complexity,
                metadata={'complexity_type': 'harmonic'}
            ))

        return events

    def stop_processing(self):
        """Stop MIDI processing and cleanup"""
        super().stop_processing()

        if self.midi_input:
            try:
                self.midi_input.close_port()
            except:
                pass

        logger.info("🎹 MIDI Signal Processor stopped")

# Demo and testing
if __name__ == "__main__":
    # Test the MIDI processor
    print("🎹 Testing MIDI Signal Processor")

    processor = MIDISignalProcessor("MPK")

    def test_callback(signal_type, features, events, form_params=None):
        print(f"Signal: {signal_type.value}")
        print(f"Intensity: {features.intensity:.2f}, Frequency: {features.frequency:.1f}Hz")
        print(f"Complexity: {features.complexity:.2f}, Rhythm: {features.rhythm_strength:.2f}")
        if events:
            print(f"Events: {[e.event_type for e in events]}")
        print("---")

    processor.register_callback(test_callback)

    if processor.initialize():
        print("✅ MIDI processor ready - play some notes!")
        processor.start_processing()

        try:
            import time
            time.sleep(30)  # Run for 30 seconds
        except KeyboardInterrupt:
            pass

        processor.stop_processing()
    else:
        print("❌ Could not initialize MIDI processor")