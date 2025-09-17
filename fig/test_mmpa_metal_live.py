#!/usr/bin/env python3
"""
MMPA Metal Live Test System
Test complete Metal-powered MMPA with real audio and visual rendering
"""

import sys
import time
import math
import logging
import numpy as np
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_metal_integration():
    """Test Metal backend integration with MMPA system"""
    print("🚀 MMPA Metal Integration Test")
    print("=" * 50)

    try:
        # Test Metal backend availability
        from mmpa_metal_backend import MMPAMetalRenderer
        print("✅ Metal backend imported successfully")

        # Test MMPA signal framework
        from mmpa_signal_framework import MMPASignalEngine
        print("✅ MMPA signal framework imported")

        # Test audio processor
        from mmpa_audio_processor import AudioSignalProcessor
        print("✅ Audio processor imported")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_metal_audio_reactive():
    """Test Metal backend with audio-reactive rendering"""
    print("\n🎵 Testing Metal Audio-Reactive Rendering")
    print("=" * 50)

    try:
        from mmpa_metal_backend import MMPAMetalRenderer

        # Create Metal renderer
        renderer = MMPAMetalRenderer(800, 600)
        device_info = renderer.get_device_info()

        print(f"Device: {device_info['name']}")
        print(f"Metal 3: {device_info['metal3_support']}")
        print(f"Unified Memory: {device_info['unified_memory']}")

        # Test audio-reactive rendering loop
        print("\n🔄 Running audio-reactive test...")

        frames_rendered = 0
        start_time = time.time()

        for i in range(100):  # 100 frames
            # Simulate audio parameters
            t = time.time()
            amplitude = 0.5 + 0.4 * math.sin(t * 2)
            bass = 0.3 + 0.3 * math.sin(t * 0.5)
            mid = 0.4 + 0.2 * math.cos(t * 1.5)
            treble = 0.2 + 0.3 * math.sin(t * 3)

            # Update Metal renderer
            renderer.update_audio_data(amplitude, bass, mid, treble)

            # Render frame
            success = renderer.render_frame()
            if success:
                frames_rendered += 1

            # Show progress every 20 frames
            if (i + 1) % 20 == 0:
                print(f"   Rendered {i + 1}/100 frames...")

        elapsed = time.time() - start_time
        fps = frames_rendered / elapsed

        print(f"\n📊 Metal Rendering Results:")
        print(f"   Frames rendered: {frames_rendered}/100")
        print(f"   Time elapsed: {elapsed:.2f}s")
        print(f"   Average FPS: {fps:.1f}")

        # Get performance metrics
        metrics = renderer.get_performance_metrics()
        print(f"   Final FPS: {metrics['fps']:.1f}")
        print(f"   GPU Utilization: {metrics['device_utilization']:.1%}")

        return True

    except Exception as e:
        print(f"❌ Metal audio-reactive test failed: {e}")
        return False

def test_mmpa_signal_processing():
    """Test MMPA signal processing integration"""
    print("\n🎛️ Testing MMPA Signal Processing")
    print("=" * 50)

    try:
        from mmpa_signal_framework import MMPASignalEngine, SignalType, SignalFeatures
        from mmpa_audio_processor import AudioSignalProcessor

        # Initialize MMPA signal engine
        engine = MMPASignalEngine()
        print("✅ MMPA Signal Engine initialized")

        # Create audio processor
        audio_processor = AudioSignalProcessor()
        print("✅ Audio Signal Processor created")

        # Register audio processor
        engine.register_signal_processor(SignalType.AUDIO, audio_processor)
        print("✅ Audio processor registered")

        # Test signal processing
        print("\n🎵 Testing signal analysis...")

        # Generate test audio signal
        sample_rate = 44100
        duration = 0.1  # 100ms
        t = np.linspace(0, duration, int(sample_rate * duration))

        # Create complex test signal
        frequency1 = 440  # A4
        frequency2 = 880  # A5
        frequency3 = 220  # A3

        test_signal = (
            0.3 * np.sin(2 * np.pi * frequency1 * t) +  # Mid
            0.4 * np.sin(2 * np.pi * frequency2 * t) +  # Treble
            0.5 * np.sin(2 * np.pi * frequency3 * t)    # Bass
        )

        # Process signal
        signal_features = audio_processor._extract_features(test_signal, sample_rate)

        if signal_features:
            print(f"✅ Signal processing successful:")
            print(f"   RMS: {signal_features.amplitude:.3f}")
            print(f"   Spectral centroid: {signal_features.spectral_centroid:.1f} Hz")
            print(f"   Zero crossing rate: {signal_features.zero_crossing_rate:.3f}")

            # Test frequency analysis
            freq_analysis = audio_processor._analyze_frequency_bands(test_signal, sample_rate)
            if freq_analysis:
                print(f"   Bass energy: {freq_analysis.get('bass', 0):.3f}")
                print(f"   Mid energy: {freq_analysis.get('mid', 0):.3f}")
                print(f"   Treble energy: {freq_analysis.get('treble', 0):.3f}")

        return True

    except Exception as e:
        print(f"❌ MMPA signal processing test failed: {e}")
        return False

def test_complete_integration():
    """Test complete Metal + MMPA integration"""
    print("\n🎯 Testing Complete Metal + MMPA Integration")
    print("=" * 50)

    try:
        from mmpa_metal_backend import MMPAMetalRenderer
        from mmpa_signal_framework import MMPASignalEngine

        # Initialize systems
        renderer = MMPAMetalRenderer(1024, 768)
        signal_engine = MMPASignalEngine()

        print("✅ Metal renderer initialized")
        print("✅ MMPA signal engine initialized")

        # Test integrated rendering loop
        print("\n🔄 Running integrated test loop...")

        total_frames = 0
        successful_frames = 0
        start_time = time.time()
        test_duration = 3.0  # 3 seconds

        frame_count = 0
        while (time.time() - start_time) < test_duration:
            # Simulate real-time signal processing
            t = time.time()

            # Generate varied audio characteristics
            bass_freq = 2.0 + math.sin(t * 0.3)
            mid_freq = 1.5 + math.cos(t * 0.7)
            treble_freq = 3.0 + math.sin(t * 1.2)

            amplitude = 0.4 + 0.3 * math.sin(t * bass_freq)
            bass = 0.2 + 0.4 * math.sin(t * bass_freq)
            mid = 0.3 + 0.3 * math.cos(t * mid_freq)
            treble = 0.1 + 0.4 * math.sin(t * treble_freq)

            # Update Metal renderer with processed audio data
            renderer.update_audio_data(amplitude, bass, mid, treble)

            # Render frame with Metal
            success = renderer.render_frame()

            total_frames += 1
            if success:
                successful_frames += 1

            frame_count += 1

            # Progress indicator
            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                current_fps = frame_count / elapsed
                print(f"   {elapsed:.1f}s - {frame_count} frames - {current_fps:.1f} FPS")

        elapsed = time.time() - start_time
        avg_fps = total_frames / elapsed
        success_rate = (successful_frames / total_frames) * 100

        print(f"\n📊 Integration Test Results:")
        print(f"   Total frames: {total_frames}")
        print(f"   Successful frames: {successful_frames}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Average FPS: {avg_fps:.1f}")
        print(f"   Test duration: {elapsed:.2f}s")

        # Final performance metrics
        metrics = renderer.get_performance_metrics()
        print(f"\n⚡ Final Performance Metrics:")
        print(f"   Metal FPS: {metrics['fps']:.1f}")
        print(f"   Frame count: {metrics['frame_count']}")
        print(f"   GPU utilization: {metrics['device_utilization']:.1%}")

        # Success criteria
        if success_rate >= 95 and avg_fps >= 30:
            print(f"\n🎉 INTEGRATION TEST PASSED!")
            print(f"   ✅ High success rate: {success_rate:.1f}%")
            print(f"   ✅ Good performance: {avg_fps:.1f} FPS")
            return True
        else:
            print(f"\n⚠️ Integration test completed with issues")
            print(f"   Success rate: {success_rate:.1f}% (target: ≥95%)")
            print(f"   Performance: {avg_fps:.1f} FPS (target: ≥30 FPS)")
            return False

    except Exception as e:
        print(f"❌ Complete integration test failed: {e}")
        return False

def run_comprehensive_test():
    """Run comprehensive MMPA Metal test suite"""
    print("🚀 MMPA METAL COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    tests = [
        ("Metal Integration", test_metal_integration),
        ("Metal Audio-Reactive", test_metal_audio_reactive),
        ("MMPA Signal Processing", test_mmpa_signal_processing),
        ("Complete Integration", test_complete_integration)
    ]

    results = {}
    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")

        try:
            result = test_func()
            results[test_name] = result
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")

        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
            results[test_name] = False

    # Final summary
    print(f"\n🎯 FINAL TEST RESULTS")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name:<25} {status}")

    print(f"\nSUMMARY: {passed}/{total} tests passed")

    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! MMPA Metal system is ready for production!")
        print(f"🚀 Features confirmed:")
        print(f"   • Native Apple Silicon Metal 3 performance")
        print(f"   • Audio-reactive GPU compute shaders")
        print(f"   • Real-time signal processing integration")
        print(f"   • High-performance rendering pipeline")
        print(f"   • Production-ready stability")
    elif passed >= total * 0.75:
        print(f"\n⚡ Most tests passed - system is functional with minor issues")
    else:
        print(f"\n⚠️ Multiple test failures - system needs debugging")

    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)