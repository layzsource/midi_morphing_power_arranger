#!/usr/bin/env python3
"""
Test Advanced Musical Intelligence Features
Tests chord detection, key signature, genre classification, and harmonic analysis
"""

import numpy as np
import time
from mmpa_audio_processor import AudioSignalProcessor

def generate_musical_test_signals():
    """Generate sophisticated musical test signals"""
    sample_rate = 44100
    duration = 0.2  # 200ms chunks for better harmonic analysis
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples)

    # Test 1: C Major Chord (C-E-G)
    c_major_chord = (0.5 * np.sin(2 * np.pi * 261.63 * t) +  # C4
                     0.4 * np.sin(2 * np.pi * 329.63 * t) +  # E4
                     0.3 * np.sin(2 * np.pi * 392.00 * t))   # G4

    # Test 2: Jazz Chord (Cmaj7 - C-E-G-B)
    cmaj7_chord = (0.4 * np.sin(2 * np.pi * 261.63 * t) +   # C4
                   0.3 * np.sin(2 * np.pi * 329.63 * t) +   # E4
                   0.3 * np.sin(2 * np.pi * 392.00 * t) +   # G4
                   0.2 * np.sin(2 * np.pi * 493.88 * t))    # B4

    # Test 3: Rock Power Chord (E5 - E-B)
    e5_power_chord = (0.7 * np.sin(2 * np.pi * 82.41 * t) +   # E2
                      0.5 * np.sin(2 * np.pi * 123.47 * t))    # B2

    # Test 4: Classical Scale Passage (C Major Scale)
    scale_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    classical_scale = np.zeros(samples)
    note_duration = samples // len(scale_freqs)
    for i, freq in enumerate(scale_freqs):
        start_idx = i * note_duration
        end_idx = min((i + 1) * note_duration, samples)
        note_t = t[start_idx:end_idx]
        # Add harmonics for more realistic sound
        note = (0.6 * np.sin(2 * np.pi * freq * note_t) +
                0.3 * np.sin(2 * np.pi * freq * 2 * note_t) +  # Octave
                0.1 * np.sin(2 * np.pi * freq * 3 * note_t))   # Fifth
        classical_scale[start_idx:end_idx] = note

    # Test 5: Electronic Beat (Strong 4/4 with synth bass)
    electronic_beat = np.zeros(samples)
    beat_freq = 60  # 60 Hz bass
    beats_per_chunk = 4
    for beat in range(beats_per_chunk):
        beat_time = beat * duration / beats_per_chunk
        beat_idx = int(beat_time * sample_rate)
        beat_duration = int(0.1 * sample_rate)  # 100ms beat
        end_idx = min(beat_idx + beat_duration, samples)
        # Synthetic bass with harmonics
        bass_burst = (0.8 * np.sin(2 * np.pi * beat_freq * t[beat_idx:end_idx]) +
                      0.4 * np.sin(2 * np.pi * beat_freq * 2 * t[beat_idx:end_idx]) +
                      0.2 * np.sin(2 * np.pi * beat_freq * 4 * t[beat_idx:end_idx]))
        electronic_beat[beat_idx:end_idx] += bass_burst

    # Test 6: Blues Progression (Dm - G - C with bends)
    blues_progression = np.zeros(samples)
    # Add slight detuning and vibrato for blues character
    chord_duration = samples // 3

    # Dm chord (D-F-A)
    dm_section = t[:chord_duration]
    vibrato = 1 + 0.02 * np.sin(2 * np.pi * 6 * dm_section)  # 6Hz vibrato
    dm_chord = (0.4 * np.sin(2 * np.pi * 146.83 * dm_section * vibrato) +  # D3
                0.3 * np.sin(2 * np.pi * 174.61 * dm_section * vibrato) +  # F3
                0.3 * np.sin(2 * np.pi * 220.00 * dm_section * vibrato))   # A3
    blues_progression[:chord_duration] = dm_chord

    # G chord
    g_section = t[chord_duration:2*chord_duration]
    g_chord = (0.4 * np.sin(2 * np.pi * 196.00 * g_section) +  # G3
               0.3 * np.sin(2 * np.pi * 246.94 * g_section) +  # B3
               0.3 * np.sin(2 * np.pi * 293.66 * g_section))   # D4
    blues_progression[chord_duration:2*chord_duration] = g_chord

    # C chord
    c_section = t[2*chord_duration:]
    c_chord = (0.4 * np.sin(2 * np.pi * 261.63 * c_section) +  # C4
               0.3 * np.sin(2 * np.pi * 329.63 * c_section) +  # E4
               0.3 * np.sin(2 * np.pi * 392.00 * c_section))   # G4
    blues_progression[2*chord_duration:] = c_chord

    return [
        ("C Major Chord", c_major_chord),
        ("Jazz Cmaj7 Chord", cmaj7_chord),
        ("Rock E5 Power Chord", e5_power_chord),
        ("Classical Scale Passage", classical_scale),
        ("Electronic Beat", electronic_beat),
        ("Blues Progression", blues_progression)
    ]

def test_musical_intelligence():
    """Test advanced musical intelligence features"""

    print("🎼 Advanced Musical Intelligence Test")
    print("=" * 70)

    # Create advanced processor
    processor = AudioSignalProcessor()
    processor.sample_rate = 44100
    processor.fft_size = 4096  # Larger FFT for better frequency resolution
    processor.window = np.hanning(processor.fft_size)

    # Generate musical test signals
    test_signals = generate_musical_test_signals()

    print("Testing advanced musical intelligence on complex signals...\n")

    for signal_name, signal_data in test_signals:
        print(f"🎹 {signal_name}")
        print("=" * 50)

        # Process multiple chunks to build up musical context
        for chunk_num in range(8):  # Process 8 chunks to build history
            # Pad signal to FFT size
            if len(signal_data) < processor.fft_size:
                padded_signal = np.zeros(processor.fft_size)
                padded_signal[:len(signal_data)] = signal_data
            else:
                padded_signal = signal_data[:processor.fft_size]

            # Add slight variations for each chunk
            padded_signal += 0.02 * np.random.randn(len(padded_signal))

            # Process signal
            features = processor.process_signal(padded_signal)
            events = processor.detect_events(features)

            # Only print results for last chunk (after analysis builds up)
            if chunk_num == 7:
                # Basic features
                print(f"  🎵 Basic Analysis:")
                print(f"    Intensity: {features.intensity:.4f}")
                print(f"    Frequency: {features.frequency:.1f} Hz")
                print(f"    Rhythm Strength: {features.rhythm_strength:.3f}")
                print(f"    Spectral Complexity: {features.complexity:.2f}")

                # Advanced musical features from raw_data
                raw_data = features.raw_data
                print(f"\n  🎼 Musical Intelligence:")
                print(f"    BPM: {raw_data.get('bpm', 0):.1f}")
                print(f"    Melody Note: {raw_data.get('melody_note', 'N/A')}")
                print(f"    Key Signature: {raw_data.get('key_signature', 'unknown')}")
                print(f"    Key Confidence: {raw_data.get('key_confidence', 0):.2f}")

                # Harmonic analysis
                print(f"\n  🎸 Harmonic Analysis:")
                print(f"    Chord: {raw_data.get('chord', 'unknown')}")
                print(f"    Chord Quality: {raw_data.get('chord_quality', 'unknown')}")
                print(f"    Progression: {raw_data.get('chord_progression', 'unknown')}")
                print(f"    Harmonic Tension: {raw_data.get('harmonic_tension', 0):.3f}")

                # Genre classification
                print(f"\n  🎭 Genre Classification:")
                print(f"    Genre: {raw_data.get('genre', 'unknown')}")
                print(f"    Confidence: {raw_data.get('genre_confidence', 0):.2f}")

                # Style indicators
                style_indicators = raw_data.get('style_indicators', {})
                if style_indicators:
                    print(f"    Style: {style_indicators.get('tempo', 'unknown')} tempo, "
                          f"{style_indicators.get('rhythm', 'unknown')}, "
                          f"{style_indicators.get('frequency', 'unknown')}, "
                          f"{style_indicators.get('harmony', 'unknown')}")

                # Top genre scores
                genre_scores = raw_data.get('genre_scores', {})
                if genre_scores:
                    sorted_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
                    print(f"    Top Genres:")
                    for genre, score in sorted_genres[:3]:
                        print(f"      {genre}: {score:.3f}")

                # Peak analysis
                peaks = raw_data.get('peaks', [])
                if peaks:
                    print(f"\n  🎯 Spectral Peaks:")
                    for i, peak in enumerate(peaks[:3]):
                        print(f"    {i+1}. {peak['frequency']:.1f}Hz ({peak['note']}) - {peak['magnitude']:.2f}")

                # Advanced patterns
                patterns = features.patterns
                if len(patterns) >= 8:
                    print(f"\n  📊 Advanced Patterns:")
                    print(f"    Rhythmic Complexity: {patterns[0]:.3f}")
                    print(f"    Groove Factor: {patterns[1]:.3f}")
                    print(f"    Melody Stability: {patterns[2]:.3f}")
                    print(f"    Harmonic Tension: {patterns[3]:.3f}")
                    print(f"    Chord Stability: {patterns[4]:.3f}")
                    print(f"    Key Confidence: {patterns[5]:.3f}")
                    print(f"    Key Stability: {patterns[6]:.3f}")
                    print(f"    Harmonic Richness: {patterns[7]:.3f}")

                # Musical complexity
                musical_complexity = raw_data.get('musical_complexity', 0)
                print(f"    Overall Musical Complexity: {musical_complexity:.3f}")

                # Events
                if events:
                    print(f"\n  🎪 Events Detected ({len(events)}):")
                    for event in events[:5]:  # Show first 5 events
                        metadata_items = list(event.metadata.items())[:2]
                        metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata_items])
                        print(f"    🎵 {event.event_type}: {event.intensity:.3f} ({metadata_str})")
                else:
                    print(f"\n  🎪 Events Detected: None")

                print()

    print("✅ Advanced musical intelligence test completed!")
    print("\n🎯 Musical Intelligence Features Demonstrated:")
    print("   • Chord detection and harmonic analysis")
    print("   • Key signature recognition with confidence scoring")
    print("   • Genre classification (rock, jazz, classical, electronic, etc.)")
    print("   • Advanced harmonic tension and dissonance analysis")
    print("   • Musical complexity and pattern recognition")
    print("   • Real-time music theory analysis")
    print("   • Multi-dimensional musical feature extraction")
    print("   • Style indicators and musical character analysis")

if __name__ == "__main__":
    test_musical_intelligence()