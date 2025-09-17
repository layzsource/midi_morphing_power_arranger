#!/usr/bin/env python3
"""
Live test script to generate audio signals and test Musical Intelligence
"""

import numpy as np
import sounddevice as sd
import time
import threading

def generate_test_audio(frequency=440, duration=5, device="BlackHole 64ch"):
    """Generate test tones to verify Musical Intelligence detection"""

    print(f"🎵 Generating {frequency}Hz test tone for {duration} seconds...")

    # Generate sine wave
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.3 * np.sin(2 * np.pi * frequency * t)

    # Find BlackHole device
    devices = sd.query_devices()
    blackhole_idx = None

    for i, device_info in enumerate(devices):
        if "BlackHole" in device_info['name']:
            blackhole_idx = i
            print(f"✅ Found BlackHole device at index {i}")
            break

    if blackhole_idx is not None:
        try:
            # Play to BlackHole so the MMPA system can capture it
            sd.play(wave, sample_rate, device=blackhole_idx)
            print(f"🔊 Playing {frequency}Hz tone to BlackHole...")
            sd.wait()  # Wait until playback is finished
            print("✅ Test tone completed")
        except Exception as e:
            print(f"❌ Error playing audio: {e}")
    else:
        print("❌ BlackHole device not found")

def test_musical_intelligence():
    """Test various frequencies and musical elements"""

    print("🎼 Musical Intelligence Test Sequence Starting...")
    print("Make sure the MMPA system is running to see the effects!")

    # Test different frequencies for key detection
    test_frequencies = [
        (261.63, "C4", 3),   # C major
        (293.66, "D4", 3),   # D major
        (329.63, "E4", 3),   # E major
        (440.00, "A4", 3),   # A major
        (523.25, "C5", 3),   # C major octave
    ]

    for freq, note, duration in test_frequencies:
        print(f"\n🎵 Testing {note} ({freq:.2f}Hz)")
        generate_test_audio(freq, duration)
        time.sleep(1)  # Brief pause between notes

    print("\n🎼 Musical Intelligence test completed!")
    print("Check the MMPA system for:")
    print("  • Key signature detection changes")
    print("  • Audio level indicators")
    print("  • Musical Intelligence Window updates")
    print("  • Visual morphing responses")

if __name__ == "__main__":
    test_musical_intelligence()