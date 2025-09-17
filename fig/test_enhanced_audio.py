#!/usr/bin/env python3
"""
Test Enhanced MMPA AudioSignalProcessor
Tests advanced features: tempo estimation, pattern detection, melody tracking
"""

import numpy as np
import time
from mmpa_audio_processor import AudioSignalProcessor

def generate_complex_test_signals():
    """Generate complex musical test signals"""
    sample_rate = 44100
    duration = 0.1  # 100ms chunks for better analysis
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples)

    # Test 1: Steady beat pattern (120 BPM)
    beat_interval = 60.0 / 120.0  # 0.5 seconds
    beats_per_chunk = duration / beat_interval
    steady_beat = np.zeros(samples)
    for i in range(int(beats_per_chunk) + 1):
        beat_time = i * beat_interval
        if beat_time < duration:
            beat_idx = int(beat_time * sample_rate)
            if beat_idx < samples:
                # Kick drum simulation (low freq burst)
                kick_duration = int(0.05 * sample_rate)  # 50ms kick
                end_idx = min(beat_idx + kick_duration, samples)
                kick = 0.8 * np.sin(2 * np.pi * 60 * t[beat_idx:end_idx]) * np.exp(-10 * t[beat_idx:end_idx])
                steady_beat[beat_idx:end_idx] += kick

    # Test 2: Complex harmonic (C major chord)
    c_major = (0.4 * np.sin(2 * np.pi * 261.63 * t) +  # C4
               0.3 * np.sin(2 * np.pi * 329.63 * t) +  # E4
               0.2 * np.sin(2 * np.pi * 392.00 * t))   # G4

    # Test 3: Syncopated rhythm
    syncopated = np.zeros(samples)
    syncopated_pattern = [0, 0.3, 0, 0.7, 0.1, 0.8, 0, 0.4]  # Off-beat emphasis
    for i, intensity in enumerate(syncopated_pattern):
        beat_time = i * duration / len(syncopated_pattern)
        if beat_time < duration:
            beat_idx = int(beat_time * sample_rate)
            if beat_idx < samples:
                note_freq = 440 + i * 20  # Rising melody
                note_duration = int(0.02 * sample_rate)  # 20ms note
                end_idx = min(beat_idx + note_duration, samples)
                note = intensity * np.sin(2 * np.pi * note_freq * t[beat_idx:end_idx])
                syncopated[beat_idx:end_idx] += note

    # Test 4: Melody line (simple scale)
    melody_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C major scale
    melody = np.zeros(samples)
    note_duration = duration / len(melody_freqs)
    for i, freq in enumerate(melody_freqs):
        start_idx = int(i * note_duration * sample_rate)
        end_idx = int((i + 1) * note_duration * sample_rate)
        if end_idx <= samples:
            note_t = t[start_idx:end_idx]
            note = 0.5 * np.sin(2 * np.pi * freq * note_t)
            melody[start_idx:end_idx] = note

    return [
        ("Steady Beat (120 BPM)", steady_beat),
        ("C Major Chord", c_major),
        ("Syncopated Rhythm", syncopated),
        ("Melody Scale", melody)
    ]

def test_enhanced_features():
    """Test enhanced audio processing features"""

    print("🎵 Enhanced MMPA Audio Processor Test")
    print("=" * 60)

    # Create enhanced processor
    processor = AudioSignalProcessor()
    processor.sample_rate = 44100
    processor.fft_size = 2048
    processor.window = np.hanning(processor.fft_size)

    # Generate complex test signals
    test_signals = generate_complex_test_signals()

    print("Testing enhanced features on complex musical signals...\n")

    for signal_name, signal_data in test_signals:
        print(f"🎼 {signal_name}")
        print("-" * 40)

        # Process multiple chunks to build up pattern history
        for chunk_num in range(5):  # Process 5 chunks
            # Pad signal to FFT size
            if len(signal_data) < processor.fft_size:
                padded_signal = np.zeros(processor.fft_size)
                padded_signal[:len(signal_data)] = signal_data
            else:
                padded_signal = signal_data[:processor.fft_size]

            # Add some variation for chunk processing
            padded_signal += 0.05 * np.random.randn(len(padded_signal))

            # Process signal
            features = processor.process_signal(padded_signal)
            events = processor.detect_events(features)

            # Only print results for last chunk (after pattern builds up)
            if chunk_num == 4:
                # Basic features
                print(f"  Intensity: {features.intensity:.4f}")
                print(f"  Frequency: {features.frequency:.1f} Hz")
                print(f"  Rhythm Strength: {features.rhythm_strength:.3f}")
                print(f"  Complexity: {features.complexity:.2f}")

                # Enhanced features from raw_data
                raw_data = features.raw_data
                print(f"  BPM: {raw_data.get('bpm', 0):.1f}")
                print(f"  Melody Note: {raw_data.get('melody_note', 'N/A')}")
                print(f"  Rhythm Pattern: {raw_data.get('rhythm_pattern', 'unknown')}")
                print(f"  Pattern Confidence: {raw_data.get('pattern_confidence', 0):.2f}")

                # Pattern analysis
                patterns = features.patterns
                if len(patterns) >= 4:
                    print(f"  Rhythmic Complexity: {patterns[0]:.3f}")
                    print(f"  Groove Factor: {patterns[1]:.3f}")
                    print(f"  Melody Stability: {patterns[2]:.3f}")
                    print(f"  Harmonic Complexity: {patterns[3]:.3f}")

                # Peak information
                peaks = raw_data.get('peaks', [])
                if peaks:
                    print(f"  Top Peaks:")
                    for i, peak in enumerate(peaks[:3]):
                        print(f"    {i+1}. {peak['frequency']:.1f}Hz ({peak['note']}) - {peak['magnitude']:.3f}")

                # Events
                if events:
                    print(f"  Events Detected ({len(events)}):")
                    for event in events:
                        metadata_str = ", ".join([f"{k}: {v}" for k, v in list(event.metadata.items())[:2]])
                        print(f"    🎵 {event.event_type}: {event.intensity:.3f} ({metadata_str})")
                else:
                    print("  Events Detected: None")

                print()

    print("✅ Enhanced audio processor test completed!")
    print("\n🎯 New Features Demonstrated:")
    print("   • Advanced beat detection with adaptive thresholds")
    print("   • Real-time BPM estimation and tempo tracking")
    print("   • Spectral peak tracking and melody detection")
    print("   • Musical note identification (frequency → note name)")
    print("   • Rhythmic pattern classification (steady, syncopated, etc.)")
    print("   • Enhanced event detection (harmony, tempo, patterns)")
    print("   • Multi-dimensional pattern analysis (groove, complexity)")

if __name__ == "__main__":
    test_enhanced_features()