#!/usr/bin/env python3
"""
MMPA Audio Signal Processor - SKELETON FOR NEXT SESSION
Converts audio input into universal MMPA signal features

This plugin will transform real-time audio into the universal signal framework
Ready for implementation in next session!
"""

import numpy as np
import time
import threading
from typing import Optional, List, Any, Dict, Tuple
import logging
import sounddevice as sd
from scipy import signal
from scipy.fft import fft, fftfreq
import queue

from mmpa_signal_framework import (
    SignalProcessor, SignalType, SignalFeatures, SignalEvent, SignalAnalyzer
)

logger = logging.getLogger(__name__)

# Import our revolutionary advanced genre detection system
try:
    from mmpa_advanced_genre_detector import AdvancedGenreDetector
    ADVANCED_GENRE_AVAILABLE = True
    logger.info("🚀 Advanced Genre Detection Engine imported successfully")
except ImportError as e:
    ADVANCED_GENRE_AVAILABLE = False
    logger.warning(f"⚠️ Advanced Genre Detection not available: {e}")

class AdvancedOnsetDetector:
    """Advanced onset/beat detection with tempo estimation"""

    def __init__(self, sample_rate: float):
        self.sample_rate = sample_rate
        self.onset_history = []
        self.spectral_flux_history = []
        self.energy_history = []

        # Advanced detection parameters
        self.frame_rate = 86.13  # ~512 samples at 44.1kHz
        self.adaptive_threshold = 0.1
        self.alpha = 0.98  # For exponential smoothing
        self.tempo_candidates = []
        self.current_bpm = 0.0

        # Multi-band onset detection
        self.band_flux_histories = [[] for _ in range(6)]  # 6 frequency bands

        # Pattern recognition
        self.rhythm_patterns = []
        self.beat_confidence = 0.0

    def process(self, spectrum: np.ndarray, frequency_bands: List[float]) -> float:
        """Enhanced onset detection with tempo estimation"""
        current_time = time.time()

        # Multi-band spectral flux
        band_fluxes = []
        for i, (current_energy, history) in enumerate(zip(frequency_bands, self.band_flux_histories)):
            if len(history) > 0:
                flux = max(0, current_energy - history[-1])  # Half-wave rectification
            else:
                flux = 0.0
            band_fluxes.append(flux)

            history.append(current_energy)
            if len(history) > 50:  # Keep last 50 frames
                history.pop(0)

        # Combined onset strength (weighted by frequency bands)
        weights = [2.0, 3.0, 3.0, 2.0, 1.0, 0.5]  # Emphasize mid frequencies
        onset_strength = sum(w * f for w, f in zip(weights, band_fluxes))

        # Adaptive threshold
        self.energy_history.append(onset_strength)
        if len(self.energy_history) > 100:
            self.energy_history.pop(0)

        if len(self.energy_history) >= 10:
            # Adaptive threshold based on recent energy statistics
            recent_energy = self.energy_history[-20:]
            mean_energy = np.mean(recent_energy)
            std_energy = np.std(recent_energy)
            self.adaptive_threshold = mean_energy + 1.5 * std_energy

        # Onset detection
        if onset_strength > self.adaptive_threshold and onset_strength > 0.1:
            # Check if this onset is not too close to previous one (debouncing)
            if not self.onset_history or (current_time - self.onset_history[-1]) > 0.05:  # 50ms minimum
                self.onset_history.append(current_time)

        # Keep recent onsets (last 10 seconds for tempo estimation)
        self.onset_history = [t for t in self.onset_history if current_time - t < 10.0]

        # Tempo estimation
        self.current_bpm = self._estimate_tempo()

        # Beat confidence and rhythm strength
        rhythm_strength = self._calculate_rhythm_strength()

        return rhythm_strength

    def _estimate_tempo(self) -> float:
        """Estimate current BPM from onset intervals"""
        if len(self.onset_history) < 4:
            return 0.0

        # Calculate intervals between onsets
        intervals = [self.onset_history[i] - self.onset_history[i-1]
                    for i in range(1, len(self.onset_history))]

        if not intervals:
            return 0.0

        # Look for consistent beat intervals
        tempo_candidates = []
        for interval in intervals:
            if 0.2 < interval < 2.0:  # Reasonable tempo range (30-300 BPM)
                bpm = 60.0 / interval
                tempo_candidates.append(bpm)

        if not tempo_candidates:
            return 0.0

        # Find most consistent tempo
        tempo_candidates.sort()

        # Group similar tempos and find the most common
        tempo_groups = []
        tolerance = 5.0  # BPM tolerance

        for tempo in tempo_candidates:
            added = False
            for group in tempo_groups:
                if abs(tempo - group[0]) < tolerance:
                    group.append(tempo)
                    added = True
                    break
            if not added:
                tempo_groups.append([tempo])

        # Return the average of the largest group
        if tempo_groups:
            largest_group = max(tempo_groups, key=len)
            if len(largest_group) >= 2:  # Need at least 2 consistent beats
                return np.mean(largest_group)

        return 0.0

    def _calculate_rhythm_strength(self) -> float:
        """Calculate rhythm strength based on beat consistency"""
        if len(self.onset_history) < 3:
            return 0.0

        # Calculate interval consistency
        intervals = [self.onset_history[i] - self.onset_history[i-1]
                    for i in range(1, len(self.onset_history))]

        if len(intervals) < 2:
            return 0.0

        # Measure consistency (lower std = more rhythmic)
        interval_std = np.std(intervals)
        mean_interval = np.mean(intervals)

        if mean_interval == 0:
            return 0.0

        # Coefficient of variation (normalized standard deviation)
        cv = interval_std / mean_interval

        # Convert to rhythm strength (0-1)
        rhythm_strength = 1.0 / (1.0 + cv * 5.0)

        # Boost if we have a clear tempo
        if self.current_bpm > 0:
            rhythm_strength *= 1.2

        return min(rhythm_strength, 1.0)

    def get_tempo_info(self) -> Dict[str, float]:
        """Get detailed tempo information"""
        return {
            'bpm': self.current_bpm,
            'beat_confidence': self.beat_confidence,
            'onset_count': len(self.onset_history),
            'avg_onset_interval': np.mean([self.onset_history[i] - self.onset_history[i-1]
                                          for i in range(1, len(self.onset_history))]) if len(self.onset_history) > 1 else 0.0
        }

class SpectralPeakTracker:
    """Track spectral peaks for melody and harmony detection"""

    def __init__(self, max_peaks: int = 10):
        self.max_peaks = max_peaks
        self.peak_history = []
        self.melody_line = []
        self.chord_progression = []

    def process(self, spectrum: np.ndarray, freqs: np.ndarray) -> Dict[str, Any]:
        """Extract and track spectral peaks"""
        # Find peaks in spectrum
        from scipy.signal import find_peaks

        # Find prominent peaks
        peak_indices, properties = find_peaks(
            spectrum,
            height=np.max(spectrum) * 0.1,  # At least 10% of max
            distance=10,  # Minimum distance between peaks
            prominence=np.max(spectrum) * 0.05  # Prominence threshold
        )

        # Get peak frequencies and magnitudes
        peaks = []
        for idx in peak_indices[:self.max_peaks]:
            if idx < len(freqs):
                peak_freq = freqs[idx]
                peak_mag = spectrum[idx]
                peaks.append({
                    'frequency': peak_freq,
                    'magnitude': peak_mag,
                    'note': self._freq_to_note(peak_freq)
                })

        # Sort by magnitude (strongest peaks first)
        peaks.sort(key=lambda x: x['magnitude'], reverse=True)

        # Track melody (strongest peak)
        if peaks:
            strongest_peak = peaks[0]
            self.melody_line.append(strongest_peak['frequency'])
            if len(self.melody_line) > 50:  # Keep last 50 melody points
                self.melody_line.pop(0)

            # Detect chord progression (multiple strong peaks)
            chord_freqs = [p['frequency'] for p in peaks[:4] if p['magnitude'] > np.max(spectrum) * 0.2]
            if len(chord_freqs) >= 2:
                self.chord_progression.append(chord_freqs)
                if len(self.chord_progression) > 20:
                    self.chord_progression.pop(0)

        self.peak_history.append(peaks)
        if len(self.peak_history) > 20:
            self.peak_history.pop(0)

        return {
            'peaks': peaks,
            'melody_stability': self._calculate_melody_stability(),
            'harmonic_complexity': len(peaks),
            'fundamental_freq': peaks[0]['frequency'] if peaks else 0.0
        }

    def _freq_to_note(self, freq: float) -> str:
        """Convert frequency to musical note"""
        if freq <= 0:
            return "N/A"

        A4 = 440.0
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        # Calculate semitones from A4
        semitones = 12 * np.log2(freq / A4)
        note_index = int(round(semitones)) % 12
        octave = 4 + int(round(semitones)) // 12

        return f"{note_names[note_index]}{octave}"

    def _calculate_melody_stability(self) -> float:
        """Calculate how stable the melody line is"""
        if len(self.melody_line) < 5:
            return 0.0

        # Calculate frequency variation
        recent_melody = self.melody_line[-10:]
        freq_std = np.std(recent_melody)
        mean_freq = np.mean(recent_melody)

        if mean_freq == 0:
            return 0.0

        # Normalized stability (lower variation = higher stability)
        cv = freq_std / mean_freq
        stability = 1.0 / (1.0 + cv * 2.0)
        return min(stability, 1.0)

class RhythmPatternDetector:
    """Detect and classify rhythmic patterns"""

    def __init__(self):
        self.onset_pattern_history = []
        self.pattern_templates = {
            'steady_beat': [1, 0, 1, 0, 1, 0, 1, 0],
            'syncopated': [1, 0, 0, 1, 0, 1, 0, 0],
            'triplet': [1, 0, 0, 1, 0, 0, 1, 0, 0],
            'complex': [1, 0, 1, 1, 0, 1, 0, 1]
        }
        self.current_pattern = 'unknown'
        self.pattern_confidence = 0.0

    def process(self, rhythm_strength: float, onset_detected: bool) -> Dict[str, Any]:
        """Analyze rhythmic patterns"""
        # Convert to binary onset pattern
        onset_value = 1 if onset_detected else 0
        self.onset_pattern_history.append(onset_value)

        # Keep last 16 beats for pattern analysis
        if len(self.onset_pattern_history) > 16:
            self.onset_pattern_history.pop(0)

        # Analyze pattern when we have enough data
        if len(self.onset_pattern_history) >= 8:
            self.current_pattern, self.pattern_confidence = self._classify_pattern()

        return {
            'pattern': self.current_pattern,
            'confidence': self.pattern_confidence,
            'complexity': self._calculate_pattern_complexity(),
            'groove_factor': self._calculate_groove_factor()
        }

    def _classify_pattern(self) -> Tuple[str, float]:
        """Classify the current rhythmic pattern"""
        if len(self.onset_pattern_history) < 8:
            return 'unknown', 0.0

        recent_pattern = self.onset_pattern_history[-8:]
        best_match = 'unknown'
        best_score = 0.0

        # Compare with templates
        for pattern_name, template in self.pattern_templates.items():
            template_8 = template[:8]  # Use first 8 beats
            score = self._pattern_similarity(recent_pattern, template_8)
            if score > best_score:
                best_score = score
                best_match = pattern_name

        # Confidence threshold
        confidence = best_score if best_score > 0.6 else 0.0

        return best_match, confidence

    def _pattern_similarity(self, pattern1: List[int], pattern2: List[int]) -> float:
        """Calculate similarity between two rhythm patterns"""
        if len(pattern1) != len(pattern2):
            return 0.0

        matches = sum(1 for a, b in zip(pattern1, pattern2) if a == b)
        return matches / len(pattern1)

    def _calculate_pattern_complexity(self) -> float:
        """Calculate rhythmic complexity"""
        if len(self.onset_pattern_history) < 4:
            return 0.0

        # Count transitions (changes from 0 to 1 or 1 to 0)
        transitions = sum(1 for i in range(1, len(self.onset_pattern_history))
                         if self.onset_pattern_history[i] != self.onset_pattern_history[i-1])

        # Normalize by pattern length
        complexity = transitions / (len(self.onset_pattern_history) - 1)
        return complexity

    def _calculate_groove_factor(self) -> float:
        """Calculate 'groove' - rhythmic feel and swing"""
        if len(self.onset_pattern_history) < 8:
            return 0.0

        # Look for syncopation and off-beat emphasis
        pattern = self.onset_pattern_history[-8:]

        # Count off-beat onsets (positions 1, 3, 5, 7 in 8-beat pattern)
        off_beat_onsets = sum(pattern[i] for i in [1, 3, 5, 7] if i < len(pattern))
        on_beat_onsets = sum(pattern[i] for i in [0, 2, 4, 6] if i < len(pattern))

        total_onsets = off_beat_onsets + on_beat_onsets
        if total_onsets == 0:
            return 0.0

        # Groove increases with balanced on/off beat emphasis
        if on_beat_onsets == 0:
            groove = 0.0
        else:
            ratio = off_beat_onsets / on_beat_onsets
            groove = min(ratio, 1.0)  # Cap at 1.0

        return groove

class ChordProgressionDetector:
    """Advanced chord progression detection and harmonic analysis"""

    def __init__(self):
        self.chord_history = []
        self.progression_patterns = {
            'vi-IV-I-V': ['Am', 'F', 'C', 'G'],     # Pop progression
            'I-V-vi-IV': ['C', 'G', 'Am', 'F'],    # Canon progression
            'ii-V-I': ['Dm', 'G', 'C'],            # Jazz cadence
            'I-vi-ii-V': ['C', 'Am', 'Dm', 'G'],   # Circle of fifths
            'I-bVII-IV': ['C', 'Bb', 'F']          # Rock progression
        }
        self.current_progression = 'unknown'
        self.progression_confidence = 0.0

        # Chord templates (frequency ratios for major/minor triads)
        self.chord_templates = {
            'major': [1.0, 1.25, 1.5],      # Root, major third, fifth
            'minor': [1.0, 1.2, 1.5],       # Root, minor third, fifth
            'diminished': [1.0, 1.2, 1.414], # Root, minor third, diminished fifth
            'augmented': [1.0, 1.25, 1.587]  # Root, major third, augmented fifth
        }

    def process(self, peaks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze peaks to detect chords and progressions"""
        if len(peaks) < 2:
            return {
                'chord': 'unknown',
                'quality': 'unknown',
                'progression': self.current_progression,
                'progression_confidence': self.progression_confidence,
                'harmonic_tension': 0.0
            }

        # Extract frequencies and magnitudes
        freqs = [p['frequency'] for p in peaks[:6]]  # Top 6 peaks
        mags = [p['magnitude'] for p in peaks[:6]]

        # Detect chord
        chord_info = self._detect_chord(freqs, mags)

        # Update chord history
        if chord_info['chord'] != 'unknown':
            self.chord_history.append(chord_info['chord'])
            if len(self.chord_history) > 8:  # Keep last 8 chords
                self.chord_history.pop(0)

        # Analyze progression
        if len(self.chord_history) >= 3:
            self.current_progression, self.progression_confidence = self._analyze_progression()

        # Calculate harmonic tension
        harmonic_tension = self._calculate_harmonic_tension(freqs)

        return {
            'chord': chord_info['chord'],
            'quality': chord_info['quality'],
            'inversion': chord_info.get('inversion', 0),
            'progression': self.current_progression,
            'progression_confidence': self.progression_confidence,
            'harmonic_tension': harmonic_tension,
            'chord_stability': chord_info.get('stability', 0.0)
        }

    def _detect_chord(self, freqs: List[float], mags: List[float]) -> Dict[str, Any]:
        """Detect chord from frequency peaks"""
        if len(freqs) < 2:
            return {'chord': 'unknown', 'quality': 'unknown', 'stability': 0.0}

        # Find root (lowest strong frequency)
        root_freq = freqs[0]

        # Calculate intervals from root
        intervals = []
        for freq in freqs[1:4]:  # Check next 3 frequencies
            if root_freq > 0:
                ratio = freq / root_freq
                intervals.append(ratio)

        # Match against chord templates
        best_match = 'unknown'
        best_quality = 'unknown'
        best_score = 0.0

        for quality, template in self.chord_templates.items():
            score = self._match_chord_template(intervals, template)
            if score > best_score and score > 0.6:  # Confidence threshold
                best_score = score
                best_quality = quality
                best_match = self._freq_to_chord_name(root_freq, quality)

        return {
            'chord': best_match,
            'quality': best_quality,
            'stability': best_score,
            'root_freq': root_freq
        }

    def _match_chord_template(self, intervals: List[float], template: List[float]) -> float:
        """Match interval ratios against chord template"""
        if not intervals:
            return 0.0

        matches = 0
        total_comparisons = 0

        for interval in intervals:
            for template_ratio in template[1:]:  # Skip root (1.0)
                total_comparisons += 1
                # Allow 5% tolerance for matching
                if abs(interval - template_ratio) / template_ratio < 0.05:
                    matches += 1

        return matches / total_comparisons if total_comparisons > 0 else 0.0

    def _freq_to_chord_name(self, root_freq: float, quality: str) -> str:
        """Convert root frequency to chord name"""
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        # Calculate semitones from A4 (440 Hz)
        A4 = 440.0
        semitones = 12 * np.log2(root_freq / A4)
        note_index = int(round(semitones)) % 12

        root_note = note_names[note_index]

        # Add quality suffix
        if quality == 'minor':
            return f"{root_note}m"
        elif quality == 'diminished':
            return f"{root_note}°"
        elif quality == 'augmented':
            return f"{root_note}+"
        else:
            return root_note

    def _analyze_progression(self) -> Tuple[str, float]:
        """Analyze chord progression patterns"""
        if len(self.chord_history) < 3:
            return 'unknown', 0.0

        recent_chords = self.chord_history[-4:]  # Last 4 chords

        # Match against known progressions
        best_match = 'unknown'
        best_confidence = 0.0

        for prog_name, prog_pattern in self.progression_patterns.items():
            confidence = self._match_progression(recent_chords, prog_pattern)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = prog_name

        return best_match, best_confidence

    def _match_progression(self, chords: List[str], pattern: List[str]) -> float:
        """Match chord sequence against progression pattern"""
        if len(chords) < len(pattern):
            return 0.0

        # Check different starting positions
        max_score = 0.0

        for start_pos in range(len(chords) - len(pattern) + 1):
            chord_slice = chords[start_pos:start_pos + len(pattern)]
            matches = sum(1 for a, b in zip(chord_slice, pattern) if a == b)
            score = matches / len(pattern)
            max_score = max(max_score, score)

        return max_score

    def _calculate_harmonic_tension(self, freqs: List[float]) -> float:
        """Calculate harmonic tension/dissonance level"""
        if len(freqs) < 2:
            return 0.0

        tension = 0.0
        count = 0

        # Calculate dissonance between frequency pairs
        for i in range(len(freqs)):
            for j in range(i + 1, len(freqs)):
                if freqs[i] > 0 and freqs[j] > 0:
                    ratio = freqs[j] / freqs[i]
                    # Simple dissonance model based on frequency ratios
                    dissonance = self._calculate_dissonance(ratio)
                    tension += dissonance
                    count += 1

        return tension / count if count > 0 else 0.0

    def _calculate_dissonance(self, ratio: float) -> float:
        """Calculate dissonance for a frequency ratio"""
        # Consonant intervals (low dissonance)
        consonant_ratios = [1.0, 2.0, 1.5, 1.33, 1.25, 1.2]  # Octave, fifth, fourth, major third, minor third

        min_dissonance = float('inf')
        for cons_ratio in consonant_ratios:
            # Check both directions
            dissonance = min(abs(ratio - cons_ratio), abs(ratio - 1/cons_ratio))
            min_dissonance = min(min_dissonance, dissonance)

        # Normalize to 0-1 range
        return min(min_dissonance / 0.5, 1.0)

class KeySignatureDetector:
    """Detect musical key signature using pitch class profiles"""

    def __init__(self):
        self.pitch_class_history = []
        self.current_key = 'C major'
        self.key_confidence = 0.0

        # Krumhansl-Schmuckler key profiles
        self.major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        self.minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

        self.keys = [
            'C major', 'G major', 'D major', 'A major', 'E major', 'B major',
            'F# major', 'C# major', 'F major', 'Bb major', 'Eb major', 'Ab major',
            'A minor', 'E minor', 'B minor', 'F# minor', 'C# minor', 'G# minor',
            'D# minor', 'A# minor', 'D minor', 'G minor', 'C minor', 'F minor'
        ]

    def process(self, peaks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze peaks to detect key signature"""
        if not peaks:
            return {
                'key': self.current_key,
                'confidence': self.key_confidence,
                'pitch_class_profile': [0.0] * 12
            }

        # Extract pitch classes from peaks
        pitch_classes = [0.0] * 12
        for peak in peaks[:8]:  # Use top 8 peaks
            freq = peak['frequency']
            magnitude = peak['magnitude']
            pitch_class = self._freq_to_pitch_class(freq)
            pitch_classes[pitch_class] += magnitude

        # Normalize pitch class profile
        total_energy = sum(pitch_classes)
        if total_energy > 0:
            pitch_classes = [pc / total_energy for pc in pitch_classes]

        # Add to history
        self.pitch_class_history.append(pitch_classes)
        if len(self.pitch_class_history) > 20:  # Keep last 20 profiles
            self.pitch_class_history.pop(0)

        # Analyze key when we have enough data
        if len(self.pitch_class_history) >= 5:
            self.current_key, self.key_confidence = self._detect_key()

        return {
            'key': self.current_key,
            'confidence': self.key_confidence,
            'pitch_class_profile': pitch_classes,
            'key_stability': self._calculate_key_stability()
        }

    def _freq_to_pitch_class(self, freq: float) -> int:
        """Convert frequency to pitch class (0-11)"""
        if freq <= 0:
            return 0

        # Calculate semitones from C4 (261.63 Hz)
        C4 = 261.63
        semitones = 12 * np.log2(freq / C4)
        pitch_class = int(round(semitones)) % 12
        return pitch_class

    def _detect_key(self) -> Tuple[str, float]:
        """Detect key using averaged pitch class profile"""
        # Average recent pitch class profiles
        avg_profile = [0.0] * 12
        for profile in self.pitch_class_history[-10:]:  # Last 10 profiles
            for i in range(12):
                avg_profile[i] += profile[i]

        # Normalize
        total = sum(avg_profile)
        if total > 0:
            avg_profile = [pc / total for pc in avg_profile]

        # Compare with key templates
        best_key = 'C major'
        best_correlation = -1.0

        # Test all major keys
        for i in range(12):
            rotated_major = self.major_profile[i:] + self.major_profile[:i]
            correlation = self._correlation(avg_profile, rotated_major)
            if correlation > best_correlation:
                best_correlation = correlation
                best_key = self.keys[i]

        # Test all minor keys
        for i in range(12):
            rotated_minor = self.minor_profile[i:] + self.minor_profile[:i]
            correlation = self._correlation(avg_profile, rotated_minor)
            if correlation > best_correlation:
                best_correlation = correlation
                best_key = self.keys[i + 12]

        # Confidence based on correlation strength
        confidence = max(0.0, (best_correlation + 1.0) / 2.0)  # Scale from [-1,1] to [0,1]

        return best_key, confidence

    def _correlation(self, profile1: List[float], profile2: List[float]) -> float:
        """Calculate Pearson correlation between two profiles"""
        if len(profile1) != len(profile2):
            return 0.0

        # Calculate means
        mean1 = sum(profile1) / len(profile1)
        mean2 = sum(profile2) / len(profile2)

        # Calculate correlation
        numerator = sum((p1 - mean1) * (p2 - mean2) for p1, p2 in zip(profile1, profile2))

        sum_sq1 = sum((p1 - mean1) ** 2 for p1 in profile1)
        sum_sq2 = sum((p2 - mean2) ** 2 for p2 in profile2)
        denominator = (sum_sq1 * sum_sq2) ** 0.5

        return numerator / denominator if denominator > 0 else 0.0

    def _calculate_key_stability(self) -> float:
        """Calculate how stable the detected key is over time"""
        if len(self.pitch_class_history) < 5:
            return 0.0

        # Check consistency of key detection over recent history
        recent_keys = []
        for i in range(max(1, len(self.pitch_class_history) - 5), len(self.pitch_class_history)):
            # Simulate key detection for each historical point
            profile = self.pitch_class_history[i]
            key, _ = self._detect_key_for_profile(profile)
            recent_keys.append(key)

        # Calculate stability as consistency percentage
        if not recent_keys:
            return 0.0

        most_common_key = max(set(recent_keys), key=recent_keys.count)
        stability = recent_keys.count(most_common_key) / len(recent_keys)
        return stability

    def _detect_key_for_profile(self, profile: List[float]) -> Tuple[str, float]:
        """Detect key for a single profile (helper method)"""
        best_key = 'C major'
        best_correlation = -1.0

        # Test major keys
        for i in range(12):
            rotated_major = self.major_profile[i:] + self.major_profile[:i]
            correlation = self._correlation(profile, rotated_major)
            if correlation > best_correlation:
                best_correlation = correlation
                best_key = self.keys[i]

        # Test minor keys
        for i in range(12):
            rotated_minor = self.minor_profile[i:] + self.minor_profile[:i]
            correlation = self._correlation(profile, rotated_minor)
            if correlation > best_correlation:
                best_correlation = correlation
                best_key = self.keys[i + 12]

        confidence = max(0.0, (best_correlation + 1.0) / 2.0)
        return best_key, confidence

class GenreClassifier:
    """Real-time genre classification based on audio features"""

    def __init__(self):
        self.feature_history = []
        self.genre_scores = {
            'rock': 0.0,
            'jazz': 0.0,
            'classical': 0.0,
            'electronic': 0.0,
            'folk': 0.0,
            'pop': 0.0,
            'blues': 0.0,
            'reggae': 0.0
        }
        self.current_genre = 'unknown'
        self.genre_confidence = 0.0

        # Genre feature profiles (simplified heuristics)
        self.genre_profiles = {
            'rock': {
                'tempo_range': (90, 180),
                'beat_strength': 0.7,
                'harmonic_tension': 0.3,
                'freq_emphasis': [0.6, 0.8, 0.9, 0.7, 0.4, 0.2],  # Bass/mid heavy
                'complexity': 0.4
            },
            'jazz': {
                'tempo_range': (60, 200),
                'beat_strength': 0.6,
                'harmonic_tension': 0.7,
                'freq_emphasis': [0.4, 0.6, 0.8, 0.9, 0.7, 0.3],  # Mid/high emphasis
                'complexity': 0.8
            },
            'classical': {
                'tempo_range': (40, 160),
                'beat_strength': 0.4,
                'harmonic_tension': 0.5,
                'freq_emphasis': [0.3, 0.5, 0.7, 0.8, 0.9, 0.6],  # Balanced, high emphasis
                'complexity': 0.9
            },
            'electronic': {
                'tempo_range': (120, 180),
                'beat_strength': 0.9,
                'harmonic_tension': 0.2,
                'freq_emphasis': [0.9, 0.7, 0.5, 0.6, 0.8, 0.9],  # Bass and ultra high
                'complexity': 0.3
            },
            'folk': {
                'tempo_range': (80, 140),
                'beat_strength': 0.5,
                'harmonic_tension': 0.2,
                'freq_emphasis': [0.3, 0.6, 0.8, 0.7, 0.5, 0.2],  # Mid-focused
                'complexity': 0.3
            },
            'pop': {
                'tempo_range': (90, 140),
                'beat_strength': 0.8,
                'harmonic_tension': 0.3,
                'freq_emphasis': [0.5, 0.7, 0.8, 0.6, 0.5, 0.4],  # Balanced
                'complexity': 0.4
            },
            'blues': {
                'tempo_range': (60, 120),
                'beat_strength': 0.6,
                'harmonic_tension': 0.4,
                'freq_emphasis': [0.7, 0.8, 0.7, 0.5, 0.3, 0.1],  # Low/mid emphasis
                'complexity': 0.5
            },
            'reggae': {
                'tempo_range': (80, 120),
                'beat_strength': 0.7,
                'harmonic_tension': 0.2,
                'freq_emphasis': [0.8, 0.6, 0.5, 0.7, 0.4, 0.2],  # Bass emphasis
                'complexity': 0.3
            }
        }

    def process(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Classify genre based on audio features"""

        # Extract relevant features
        feature_vector = {
            'bpm': features.get('bpm', 0),
            'beat_strength': features.get('rhythm_strength', 0),
            'harmonic_tension': features.get('harmonic_tension', 0),
            'freq_bands': features.get('frequency_bands', [0]*6),
            'complexity': features.get('complexity', 0),
            'groove': features.get('groove_factor', 0),
            'spectral_centroid': features.get('spectral_centroid', 0)
        }

        # Add to history
        self.feature_history.append(feature_vector)
        if len(self.feature_history) > 20:  # Keep last 20 feature vectors
            self.feature_history.pop(0)

        # Calculate genre scores
        if len(self.feature_history) >= 5:
            self._calculate_genre_scores()

        return {
            'genre': self.current_genre,
            'confidence': self.genre_confidence,
            'genre_scores': self.genre_scores.copy(),
            'style_indicators': self._get_style_indicators(feature_vector)
        }

    def _calculate_genre_scores(self):
        """Calculate scores for each genre based on feature history"""
        # Average recent features
        avg_features = {}
        for key in self.feature_history[0].keys():
            if key == 'freq_bands':
                avg_features[key] = [
                    sum(fv[key][i] for fv in self.feature_history[-10:]) / min(len(self.feature_history), 10)
                    for i in range(6)
                ]
            else:
                avg_features[key] = sum(fv[key] for fv in self.feature_history[-10:]) / min(len(self.feature_history), 10)

        # Score each genre
        for genre, profile in self.genre_profiles.items():
            score = 0.0
            total_weight = 0.0

            # Tempo match
            bpm = avg_features['bpm']
            if profile['tempo_range'][0] <= bpm <= profile['tempo_range'][1]:
                score += 1.0
            else:
                # Penalty for being outside range
                distance = min(abs(bpm - profile['tempo_range'][0]), abs(bpm - profile['tempo_range'][1]))
                score += max(0, 1.0 - distance / 50.0)  # 50 BPM tolerance
            total_weight += 1.0

            # Beat strength match
            beat_diff = abs(avg_features['beat_strength'] - profile['beat_strength'])
            score += max(0, 1.0 - beat_diff * 2)  # Scale factor
            total_weight += 1.0

            # Harmonic tension match
            tension_diff = abs(avg_features['harmonic_tension'] - profile['harmonic_tension'])
            score += max(0, 1.0 - tension_diff * 2)
            total_weight += 1.0

            # Frequency emphasis match
            freq_score = 0.0
            for i, (actual, expected) in enumerate(zip(avg_features['freq_bands'], profile['freq_emphasis'])):
                freq_score += max(0, 1.0 - abs(actual - expected))
            score += freq_score / 6.0
            total_weight += 1.0

            # Complexity match
            complexity_diff = abs(avg_features['complexity'] / 10.0 - profile['complexity'])  # Normalize complexity
            score += max(0, 1.0 - complexity_diff * 2)
            total_weight += 1.0

            # Normalize score
            self.genre_scores[genre] = score / total_weight if total_weight > 0 else 0.0

        # Find best genre
        if self.genre_scores:
            best_genre = max(self.genre_scores, key=self.genre_scores.get)
            self.genre_confidence = self.genre_scores[best_genre]

            # Only assign genre if confidence is reasonable
            if self.genre_confidence > 0.4:
                self.current_genre = best_genre
            else:
                self.current_genre = 'unknown'

    def _get_style_indicators(self, features: Dict[str, Any]) -> Dict[str, str]:
        """Get specific style indicators"""
        indicators = {}

        # Tempo indicator
        bpm = features['bpm']
        if bpm < 70:
            indicators['tempo'] = 'very slow'
        elif bpm < 100:
            indicators['tempo'] = 'slow'
        elif bpm < 130:
            indicators['tempo'] = 'moderate'
        elif bpm < 160:
            indicators['tempo'] = 'fast'
        else:
            indicators['tempo'] = 'very fast'

        # Rhythm indicator
        beat_strength = features['beat_strength']
        if beat_strength > 0.8:
            indicators['rhythm'] = 'strong beat'
        elif beat_strength > 0.5:
            indicators['rhythm'] = 'moderate beat'
        else:
            indicators['rhythm'] = 'weak beat'

        # Frequency character
        freq_bands = features['freq_bands']
        if len(freq_bands) >= 6:
            bass_heavy = freq_bands[0] > 0.7
            treble_heavy = freq_bands[5] > 0.7
            mid_heavy = max(freq_bands[1:4]) > 0.7

            if bass_heavy and treble_heavy:
                indicators['frequency'] = 'full spectrum'
            elif bass_heavy:
                indicators['frequency'] = 'bass heavy'
            elif treble_heavy:
                indicators['frequency'] = 'treble heavy'
            elif mid_heavy:
                indicators['frequency'] = 'mid-focused'
            else:
                indicators['frequency'] = 'balanced'

        # Harmonic character
        tension = features['harmonic_tension']
        if tension > 0.6:
            indicators['harmony'] = 'dissonant'
        elif tension > 0.3:
            indicators['harmony'] = 'moderate tension'
        else:
            indicators['harmony'] = 'consonant'

        return indicators

class AudioSignalProcessor(SignalProcessor):
    """
    Audio Signal Processor for MMPA Universal Framework

    Converts real-time audio input into universal SignalFeatures

    TODO FOR NEXT SESSION:
    1. Add audio input (pyaudio/sounddevice)
    2. Real-time FFT analysis
    3. Beat detection
    4. Audio → universal features mapping
    """

    def __init__(self, device_name: Optional[str] = None, sample_rate: float = 44100.0):
        super().__init__(SignalType.AUDIO, sample_rate=sample_rate)

        self.device_name = device_name
        self.audio_stream = None
        self.audio_queue = queue.Queue(maxsize=100)
        self.is_running = False

        # Audio analysis parameters
        self.fft_size = 2048
        self.hop_length = 512
        self.frequency_bands = 6
        self.window = np.hanning(self.fft_size)

        # Audio state tracking
        self.spectrum_history = []
        self.beat_history = []
        self.rms_history = []
        self.onset_detector = AdvancedOnsetDetector(sample_rate)
        self.peak_tracker = SpectralPeakTracker()
        self.pattern_detector = RhythmPatternDetector()
        self.chord_detector = ChordProgressionDetector()
        self.key_detector = KeySignatureDetector()

        # Initialize genre detection systems
        self.genre_classifier = GenreClassifier()  # Keep legacy system as backup
        self.advanced_genre_detector = None
        if ADVANCED_GENRE_AVAILABLE:
            self.advanced_genre_detector = AdvancedGenreDetector(sample_rate)
            logger.info("🚀 Advanced Genre Detector initialized - ML-powered classification active!")

        logger.info("🎤 Audio Signal Processor initialized")

    def initialize(self) -> bool:
        """Initialize audio input connection"""
        try:
            # List available devices for debugging
            devices = sd.query_devices()
            logger.info(f"Available audio devices: {len(devices)}")

            # Find BlackHole or use default input
            device_id = None
            device_found = False
            if self.device_name:
                for i, device in enumerate(devices):
                    if self.device_name.lower() in device['name'].lower():
                        device_id = i
                        logger.info(f"✅ Found {self.device_name}: {device['name']}")
                        device_found = True
                        break

                if not device_found:
                    logger.warning(f"⚠️ {self.device_name} not found, using default microphone input")
                    # List available devices for user reference
                    logger.info("Available audio devices:")
                    for i, device in enumerate(devices):
                        if device['max_input_channels'] > 0:
                            logger.info(f"  {i}: {device['name']}")

            # Setup audio input stream
            self.audio_stream = sd.InputStream(
                device=device_id,
                channels=1,  # Mono
                samplerate=self.sample_rate,
                blocksize=self.hop_length,
                callback=self._audio_callback,
                dtype=np.float32
            )

            self.audio_stream.start()
            self.is_running = True
            logger.info("✅ Audio stream started")
            return True

        except Exception as e:
            logger.error(f"❌ Audio initialization failed: {e}")
            return False

    def _get_raw_signal(self) -> Optional[np.ndarray]:
        """Get raw audio data from queue"""
        try:
            # Get available audio chunks
            chunks = []
            total_samples = 0

            # Collect enough samples for FFT
            while total_samples < self.fft_size and not self.audio_queue.empty():
                chunk = self.audio_queue.get_nowait()
                chunks.append(chunk)
                total_samples += len(chunk)

            if total_samples >= self.fft_size:
                # Concatenate and return FFT-sized chunk
                audio_data = np.concatenate(chunks)
                return audio_data[:self.fft_size]

            return None
        except queue.Empty:
            return None

    def process_signal(self, raw_signal: np.ndarray) -> SignalFeatures:
        """
        Process audio data and extract universal features

        Args:
            raw_signal: Audio samples array

        Returns:
            SignalFeatures: Universal signal features
        """
        timestamp = time.time()

        # Apply window and compute FFT
        windowed_signal = raw_signal * self.window
        fft_result = fft(windowed_signal)
        magnitude_spectrum = np.abs(fft_result[:self.fft_size//2])
        freqs = fftfreq(self.fft_size, 1/self.sample_rate)[:self.fft_size//2]

        # Basic features
        intensity = np.sqrt(np.mean(raw_signal**2))  # RMS

        # Dominant frequency
        peak_idx = np.argmax(magnitude_spectrum[1:]) + 1  # Skip DC
        dominant_freq = freqs[peak_idx] if peak_idx < len(freqs) else 0.0

        # Spectral features
        spectral_centroid = self._compute_spectral_centroid(magnitude_spectrum, freqs)
        spectral_rolloff = self._compute_spectral_rolloff(magnitude_spectrum, freqs)
        zero_crossing_rate = self._compute_zcr(raw_signal)

        # Frequency bands (6 bands)
        frequency_bands = self._compute_frequency_bands(magnitude_spectrum, freqs)

        # Complexity (spectral entropy)
        complexity = self._compute_spectral_entropy(magnitude_spectrum)

        # Change rate (spectral flux)
        change_rate = self._compute_spectral_flux(magnitude_spectrum)

        # Beat detection with enhanced algorithm
        rhythm_strength = self.onset_detector.process(magnitude_spectrum, frequency_bands)

        # Peak tracking for melody detection
        peak_info = self.peak_tracker.process(magnitude_spectrum, freqs)

        # Pattern detection
        onset_detected = rhythm_strength > 0.5
        pattern_info = self.pattern_detector.process(rhythm_strength, onset_detected)

        # Chord progression analysis
        chord_info = self.chord_detector.process(peak_info['peaks'])

        # Key signature detection
        key_info = self.key_detector.process(peak_info['peaks'])

        # Revolutionary Advanced Genre Classification
        genre_features = {
            'bpm': self.onset_detector.current_bpm,
            'rhythm_strength': rhythm_strength,
            'harmonic_tension': chord_info['harmonic_tension'],
            'frequency_bands': frequency_bands,
            'complexity': complexity,
            'groove_factor': pattern_info['groove_factor'],
            'spectral_centroid': spectral_centroid,
            'rhythmic_strength': rhythm_strength
        }

        # Use advanced ML-powered genre detection if available
        if self.advanced_genre_detector:
            advanced_result = self.advanced_genre_detector.process_audio(raw_signal, genre_features)

            # Convert advanced result to legacy format for compatibility
            genre_info = {
                'genre': advanced_result.get('genre', 'unknown'),
                'confidence': advanced_result.get('confidence', 0.0),
                'genre_scores': advanced_result.get('probabilities', {}),
                'style_indicators': {
                    'tempo': 'moderate',
                    'rhythm': 'moderate beat',
                    'frequency': 'balanced'
                },  # Default style indicators for compatibility
                'detection_method': 'advanced_ml',
                'legacy_available': True,
                'processing_time_ms': advanced_result.get('processing_time_ms', 0.0),
                'features_extracted': advanced_result.get('features_extracted', 0),
                'genre_stability': advanced_result.get('genre_stability', 0.0),
                'top_3_genres': advanced_result.get('top_3_genres', [])
            }
        else:
            # Fallback to legacy genre classification
            genre_info = self.genre_classifier.process(genre_features)
            genre_info.update({
                'detection_method': 'legacy_heuristic',
                'advanced_available': False
            })

        # Store spectrum for history
        self.spectrum_history.append(magnitude_spectrum)
        if len(self.spectrum_history) > 10:  # Keep last 10 frames
            self.spectrum_history.pop(0)

        # Enhanced patterns array with advanced musical analysis
        patterns = [
            pattern_info['complexity'],          # Rhythmic complexity
            pattern_info['groove_factor'],       # Groove/swing factor
            peak_info['melody_stability'],       # Melody stability
            chord_info['harmonic_tension'],      # Harmonic tension/dissonance
            chord_info.get('chord_stability', 0.0),  # Chord detection confidence
            key_info['confidence'],              # Key detection confidence
            key_info.get('key_stability', 0.0),  # Key stability over time
            min(len(peak_info['peaks']) / 8.0, 1.0)  # Harmonic richness
        ]

        # Enhanced raw data with musical intelligence
        raw_data = {
            'peak_freq': dominant_freq,
            'spectrum_peak': float(np.max(magnitude_spectrum)),
            'bpm': self.onset_detector.current_bpm,
            'tempo_info': self.onset_detector.get_tempo_info(),
            'peaks': peak_info['peaks'][:3],  # Top 3 peaks
            'rhythm_pattern': pattern_info['pattern'],
            'pattern_confidence': pattern_info['confidence'],
            'melody_note': peak_info['peaks'][0]['note'] if peak_info['peaks'] else 'N/A',

            # Advanced musical analysis
            'chord': chord_info['chord'],
            'chord_quality': chord_info['quality'],
            'chord_progression': chord_info['progression'],
            'progression_confidence': chord_info['progression_confidence'],
            'harmonic_tension': chord_info['harmonic_tension'],
            'key_signature': key_info['key'],
            'key_confidence': key_info['confidence'],
            'pitch_class_profile': key_info['pitch_class_profile'],
            'musical_complexity': sum(patterns) / len(patterns),  # Overall musical complexity

            # Genre classification
            'genre': genre_info['genre'],
            'genre_confidence': genre_info['confidence'],
            'genre_scores': genre_info['genre_scores'],
            'style_indicators': genre_info['style_indicators']
        }

        return SignalFeatures(
            timestamp=timestamp,
            intensity=float(intensity),
            frequency=float(peak_info['fundamental_freq']) if peak_info['fundamental_freq'] > 0 else float(dominant_freq),
            rhythm_strength=float(rhythm_strength),
            complexity=float(complexity),
            change_rate=float(change_rate),
            spectral_centroid=float(spectral_centroid),
            spectral_rolloff=float(spectral_rolloff),
            zero_crossing_rate=float(zero_crossing_rate),
            frequency_bands=frequency_bands,
            harmonics=self._compute_harmonics(magnitude_spectrum, freqs, dominant_freq),
            patterns=patterns,
            raw_data=raw_data
        )

    def detect_events(self, features: SignalFeatures) -> List[SignalEvent]:
        """Enhanced event detection with multiple event types"""
        events = []
        timestamp = features.timestamp
        raw_data = features.raw_data

        # Enhanced beat/onset events
        if features.rhythm_strength > 0.5:
            events.append(SignalEvent(
                timestamp=timestamp,
                event_type="beat",
                intensity=features.rhythm_strength,
                metadata={
                    "confidence": features.rhythm_strength,
                    "bpm": raw_data.get('bpm', 0),
                    "pattern": raw_data.get('rhythm_pattern', 'unknown')
                }
            ))

        # Tempo change events
        tempo_info = raw_data.get('tempo_info', {})
        if tempo_info.get('bpm', 0) > 0:
            events.append(SignalEvent(
                timestamp=timestamp,
                event_type="tempo",
                intensity=min(tempo_info.get('bpm', 0) / 200.0, 1.0),  # Normalize BPM
                metadata={
                    "bpm": tempo_info.get('bpm'),
                    "confidence": tempo_info.get('onset_count', 0) / 10.0  # Confidence based on onset count
                }
            ))

        # Musical note events (enhanced)
        melody_note = raw_data.get('melody_note', 'N/A')
        if features.frequency > 100 and features.intensity > 0.3 and melody_note != 'N/A':
            events.append(SignalEvent(
                timestamp=timestamp,
                event_type="note",
                intensity=features.intensity,
                metadata={
                    "frequency": features.frequency,
                    "note": melody_note,
                    "melody_stability": features.patterns[2] if len(features.patterns) > 2 else 0.0
                }
            ))

        # Harmonic events (chord detection)
        peaks = raw_data.get('peaks', [])
        if len(peaks) >= 3:  # Multiple strong peaks = harmony
            harmonic_intensity = min(len(peaks) / 5.0, 1.0)
            events.append(SignalEvent(
                timestamp=timestamp,
                event_type="harmony",
                intensity=harmonic_intensity,
                metadata={
                    "peak_count": len(peaks),
                    "fundamental": peaks[0]['frequency'] if peaks else 0,
                    "notes": [p.get('note', 'N/A') for p in peaks[:3]]
                }
            ))

        # Rhythmic pattern events
        pattern = raw_data.get('rhythm_pattern', 'unknown')
        pattern_confidence = raw_data.get('pattern_confidence', 0)
        if pattern != 'unknown' and pattern_confidence > 0.6:
            events.append(SignalEvent(
                timestamp=timestamp,
                event_type="rhythm_pattern",
                intensity=pattern_confidence,
                metadata={
                    "pattern": pattern,
                    "confidence": pattern_confidence,
                    "groove": features.patterns[1] if len(features.patterns) > 1 else 0.0
                }
            ))

        # Volume peaks (forte events)
        if features.intensity > 0.7:
            events.append(SignalEvent(
                timestamp=timestamp,
                event_type="volume_peak",
                intensity=features.intensity,
                metadata={"rms_level": features.intensity}
            ))

        # High complexity events (textural changes)
        if features.complexity > 3.0:
            events.append(SignalEvent(
                timestamp=timestamp,
                event_type="texture_change",
                intensity=min(features.complexity / 5.0, 1.0),
                metadata={"entropy": features.complexity}
            ))

        # Frequency band emphasis events
        band_names = ["bass", "low_mid", "mid", "high_mid", "treble", "ultra"]
        for i, (band_name, band_energy) in enumerate(zip(band_names, features.frequency_bands)):
            if band_energy > 0.8:  # Strong emphasis in this band
                events.append(SignalEvent(
                    timestamp=timestamp,
                    event_type=f"freq_emphasis_{band_name}",
                    intensity=band_energy,
                    metadata={"band": band_name, "energy": band_energy}
                ))

        return events

    def _audio_callback(self, indata, frames, time, status):
        """Audio input callback - receives real-time audio"""
        if status:
            logger.warning(f"Audio callback status: {status}")

        try:
            # Add audio chunk to queue (mono)
            audio_chunk = indata[:, 0].copy()  # Convert to mono
            if not self.audio_queue.full():
                self.audio_queue.put_nowait(audio_chunk)
        except queue.Full:
            # Drop frames if queue is full
            pass

    def _compute_spectral_centroid(self, spectrum: np.ndarray, freqs: np.ndarray) -> float:
        """Compute spectral centroid (brightness)"""
        if np.sum(spectrum) == 0:
            return 0.0
        return np.sum(freqs * spectrum) / np.sum(spectrum)

    def _compute_spectral_rolloff(self, spectrum: np.ndarray, freqs: np.ndarray, rolloff_percent: float = 0.85) -> float:
        """Compute spectral rolloff (energy distribution)"""
        total_energy = np.sum(spectrum)
        if total_energy == 0:
            return 0.0

        cumulative_energy = np.cumsum(spectrum)
        rolloff_idx = np.where(cumulative_energy >= rolloff_percent * total_energy)[0]
        return freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else freqs[-1]

    def _compute_zcr(self, signal: np.ndarray) -> float:
        """Compute zero crossing rate"""
        return np.mean(0.5 * np.abs(np.diff(np.sign(signal))))

    def _compute_frequency_bands(self, spectrum: np.ndarray, freqs: np.ndarray) -> List[float]:
        """Split spectrum into 6 frequency bands"""
        # Define band boundaries (Hz)
        bands = [
            (0, 250),      # Bass
            (250, 500),    # Low-mid
            (500, 1000),   # Mid
            (1000, 2000),  # High-mid
            (2000, 4000),  # Treble
            (4000, 22050)  # Ultra
        ]

        band_energies = []
        for low, high in bands:
            band_mask = (freqs >= low) & (freqs <= high)
            band_energy = np.sum(spectrum[band_mask])
            band_energies.append(float(band_energy))

        # Normalize to 0-1
        max_energy = max(band_energies) if max(band_energies) > 0 else 1.0
        return [energy / max_energy for energy in band_energies]

    def _compute_spectral_entropy(self, spectrum: np.ndarray) -> float:
        """Compute spectral entropy (complexity measure)"""
        spectrum_norm = spectrum / (np.sum(spectrum) + 1e-10)
        spectrum_norm = spectrum_norm[spectrum_norm > 0]
        return float(-np.sum(spectrum_norm * np.log2(spectrum_norm + 1e-10)))

    def _compute_spectral_flux(self, spectrum: np.ndarray) -> float:
        """Compute spectral flux (change rate)"""
        if len(self.spectrum_history) == 0:
            return 0.0

        prev_spectrum = self.spectrum_history[-1]
        if len(prev_spectrum) != len(spectrum):
            return 0.0

        flux = np.sum((spectrum - prev_spectrum) ** 2)
        return float(flux)

    def _compute_harmonics(self, spectrum: np.ndarray, freqs: np.ndarray, fundamental: float) -> List[float]:
        """Extract harmonic content"""
        harmonics = []
        for h in range(1, 9):  # 8 harmonics
            harmonic_freq = fundamental * h
            # Find closest frequency bin
            freq_idx = np.argmin(np.abs(freqs - harmonic_freq))
            if freq_idx < len(spectrum):
                harmonics.append(float(spectrum[freq_idx]))
            else:
                harmonics.append(0.0)

        # Normalize
        max_harmonic = max(harmonics) if max(harmonics) > 0 else 1.0
        return [h / max_harmonic for h in harmonics]

    def stop(self):
        """Stop audio processing"""
        self.is_running = False
        if self.audio_stream:
            self.audio_stream.stop()
            self.audio_stream.close()
            logger.info("🔇 Audio stream stopped")

# NEXT SESSION TODO LIST:
"""
IMPLEMENTATION CHECKLIST FOR AUDIO PROCESSOR:

[ ] 1. Audio Input Setup
    - Install: pip install sounddevice (or pyaudio)
    - Initialize audio stream with callback
    - Handle audio device selection

[ ] 2. Real-time FFT Analysis
    - Implement windowed FFT (Hanning window)
    - Extract magnitude spectrum
    - Compute frequency bins

[ ] 3. Feature Extraction
    - Intensity: RMS level calculation
    - Frequency: Peak detection in spectrum
    - Spectral centroid/rolloff: Weighted frequency features
    - Zero crossing rate: Time domain analysis

[ ] 4. Beat Detection
    - Onset detection algorithm
    - Rhythm strength from beat regularity
    - Tempo estimation

[ ] 5. Frequency Band Analysis
    - Split spectrum into 6 bands (bass, low-mid, mid, high-mid, treble, ultra)
    - Energy per band calculation
    - Normalize to 0-1 range

[ ] 6. Audio Event Detection
    - Beat onsets
    - Volume peaks (forte events)
    - Frequency peaks (instrument detection)
    - Silence detection

[ ] 7. Integration with MMPA
    - Add AudioSignalProcessor to enhanced_visual_morphing_mmpa.py
    - Test dual MIDI + Audio processing
    - Verify signal-to-form mapping works with audio

[ ] 8. Testing
    - Microphone input test
    - Music playback test
    - Instrument direct input test
    - Verify visual morphing responds to audio

ESTIMATED TIME: 30-45 minutes for complete implementation
"""

if __name__ == "__main__":
    print("🎤 Audio Signal Processor Skeleton Created")
    print("📋 Ready for next session implementation!")
    print("🎯 Goal: Real-time audio → universal SignalFeatures → visual morphing")