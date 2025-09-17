#!/usr/bin/env python3
"""
Test MMPA AudioSignalProcessor with synthetic audio
Demonstrates feature extraction without needing real audio input
"""

import numpy as np
import time
from mmpa_audio_processor import AudioSignalProcessor

def generate_test_signals():
    """Generate different types of test audio signals"""
    sample_rate = 44100
    duration = 0.05  # 50ms chunks
    samples = int(sample_rate * duration)

    # Test signal 1: Pure tone (440Hz)
    t = np.linspace(0, duration, samples)
    tone_440 = 0.5 * np.sin(2 * np.pi * 440 * t)

    # Test signal 2: Complex harmonic (multiple frequencies)
    harmonic = (0.3 * np.sin(2 * np.pi * 220 * t) +  # Fundamental
                0.2 * np.sin(2 * np.pi * 440 * t) +  # 2nd harmonic
                0.1 * np.sin(2 * np.pi * 660 * t))   # 3rd harmonic

    # Test signal 3: Noise (complex spectrum)
    noise = 0.2 * np.random.randn(samples)

    # Test signal 4: Beat pattern (amplitude modulation)
    beat_freq = 5  # 5 Hz beat
    beat = 0.4 * (1 + 0.5 * np.sin(2 * np.pi * beat_freq * t)) * np.sin(2 * np.pi * 440 * t)

    return [
        ("Pure Tone 440Hz", tone_440),
        ("Harmonic Complex", harmonic),
        ("White Noise", noise),
        ("Beat Pattern", beat)
    ]

def test_synthetic_audio():
    """Test audio processor with synthetic signals"""

    print("🎵 MMPA Audio Processor - Synthetic Test")
    print("=" * 50)

    # Create processor (no device needed for synthetic test)
    processor = AudioSignalProcessor()
    processor.sample_rate = 44100
    processor.fft_size = 2048
    processor.window = np.hanning(processor.fft_size)

    # Generate test signals
    test_signals = generate_test_signals()

    print("Testing feature extraction on synthetic audio...\n")

    for signal_name, signal_data in test_signals:
        print(f"📊 {signal_name}")
        print("-" * 30)

        # Pad signal to FFT size
        if len(signal_data) < processor.fft_size:
            padded_signal = np.zeros(processor.fft_size)
            padded_signal[:len(signal_data)] = signal_data
        else:
            padded_signal = signal_data[:processor.fft_size]

        # Process signal
        features = processor.process_signal(padded_signal)
        events = processor.detect_events(features)

        # Display results
        print(f"  Intensity: {features.intensity:.4f}")
        print(f"  Dominant Frequency: {features.frequency:.1f} Hz")
        print(f"  Spectral Centroid: {features.spectral_centroid:.1f} Hz")
        print(f"  Spectral Rolloff: {features.spectral_rolloff:.1f} Hz")
        print(f"  Zero Crossing Rate: {features.zero_crossing_rate:.4f}")
        print(f"  Complexity (Entropy): {features.complexity:.2f}")
        print(f"  Rhythm Strength: {features.rhythm_strength:.3f}")

        # Frequency bands
        band_names = ["Bass", "L-Mid", "Mid", "H-Mid", "Treble", "Ultra"]
        print("  Frequency Bands:")
        for name, energy in zip(band_names, features.frequency_bands):
            print(f"    {name:>7}: {energy:.3f}")

        # Events
        if events:
            print("  Events Detected:")
            for event in events:
                print(f"    🎵 {event.event_type}: {event.intensity:.3f}")
        else:
            print("  Events Detected: None")

        print()

    print("✅ Synthetic audio test completed!")
    print("\n🎯 AudioSignalProcessor successfully extracts:")
    print("   • Spectral features (centroid, rolloff, entropy)")
    print("   • Frequency analysis (6-band spectrum)")
    print("   • Time-domain features (intensity, ZCR)")
    print("   • Event detection (beats, peaks, notes)")

if __name__ == "__main__":
    test_synthetic_audio()