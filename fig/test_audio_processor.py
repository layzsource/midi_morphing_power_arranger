#!/usr/bin/env python3
"""
Test script for MMPA AudioSignalProcessor
Tests real-time audio processing with BlackHole
"""

import time
import logging
from mmpa_audio_processor import AudioSignalProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_audio_processor():
    """Test the AudioSignalProcessor with real audio input"""

    print("🎤 MMPA Audio Processor Test")
    print("=" * 50)

    # Create processor (will auto-detect BlackHole if available)
    processor = AudioSignalProcessor(device_name="BlackHole")

    # Initialize audio
    if not processor.initialize():
        print("❌ Audio initialization failed")
        return False

    print("✅ Audio processor initialized")
    print("🎧 Listening for audio... (Press Ctrl+C to stop)")
    print()

    try:
        # Test for 30 seconds
        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < 30:
            # Get raw audio signal
            raw_signal = processor._get_raw_signal()

            if raw_signal is not None:
                frame_count += 1

                # Process signal
                features = processor.process_signal(raw_signal)
                events = processor.detect_events(features)

                # Print interesting features every 10th frame
                if frame_count % 10 == 0:
                    print(f"Frame {frame_count:4d} | "
                          f"Intensity: {features.intensity:.3f} | "
                          f"Freq: {features.frequency:6.1f}Hz | "
                          f"Rhythm: {features.rhythm_strength:.3f} | "
                          f"Events: {len(events)}")

                    # Print frequency bands
                    bands = features.frequency_bands
                    band_names = ["Bass", "L-Mid", "Mid", "H-Mid", "Treble", "Ultra"]
                    band_str = " | ".join([f"{name}: {val:.2f}" for name, val in zip(band_names, bands)])
                    print(f"         Bands: {band_str}")

                    # Print events
                    for event in events:
                        print(f"         🎵 {event.event_type}: {event.intensity:.3f}")

                    print()

            time.sleep(0.1)  # 100ms processing interval

    except KeyboardInterrupt:
        print("\n🛑 Stopping audio processor...")

    finally:
        processor.stop()
        print("✅ Audio processor stopped")
        print(f"📊 Processed {frame_count} audio frames")

    return True

if __name__ == "__main__":
    success = test_audio_processor()
    if success:
        print("\n🎉 Audio processor test completed successfully!")
    else:
        print("\n❌ Audio processor test failed")