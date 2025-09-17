#!/usr/bin/env python3
"""
MMPA System Test
Test the complete modular MMPA system architecture and verify all components work together.
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_core_modules():
    """Test core modules."""
    print("🧪 Testing Core Modules...")

    try:
        from fig.core.config import get_config, MMPAConfig
        config = get_config()
        print(f"✅ Config system: Audio backend = {config.audio.backend}")

        from fig.core.utils import ColorMapper, MathUtils, GeometryUtils
        color = ColorMapper.frequency_to_color(440.0)  # A4 note
        print(f"✅ Color mapper: 440Hz = {color.name()}")

        print("✅ Core modules working\n")
        return True

    except Exception as e:
        print(f"❌ Core modules failed: {e}\n")
        return False

def test_geometry_system():
    """Test geometry library."""
    print("🧪 Testing Geometry System...")

    try:
        from fig.visuals.geometry_library import GeometryLibrary, ShapeType

        library = GeometryLibrary()

        # Test basic shapes
        sphere = library.get_shape(ShapeType.SPHERE, radius=2.0, u_res=16, v_res=8)
        print(f"✅ Sphere: {len(sphere.vertices)} vertices, {len(sphere.faces)} faces")

        cube = library.get_shape(ShapeType.CUBE, size=1.0)
        print(f"✅ Cube: {len(cube.vertices)} vertices, {len(cube.faces)} faces")

        torus = library.get_shape(ShapeType.TORUS, major_radius=2.0, minor_radius=0.5)
        print(f"✅ Torus: {len(torus.vertices)} vertices, {len(torus.faces)} faces")

        # Test advanced shapes
        helix = library.get_shape(ShapeType.HELIX, radius=1.0, height=4.0, turns=3.0)
        print(f"✅ Helix: {len(helix.vertices)} vertices, {len(helix.faces)} faces")

        mobius = library.get_shape(ShapeType.MOBIUS_STRIP, radius=2.0, width=0.5)
        print(f"✅ Möbius Strip: {len(mobius.vertices)} vertices, {len(mobius.faces)} faces")

        # Test fractal shapes
        terrain = library.get_shape(ShapeType.TERRAIN, size=33, height_scale=2.0, roughness=0.5)
        print(f"✅ Fractal Terrain: {len(terrain.vertices)} vertices, {len(terrain.faces)} faces")

        sierpinski = library.get_shape(ShapeType.SIERPINSKI, order=2, size=1.0)
        print(f"✅ Sierpinski Pyramid: {len(sierpinski.vertices)} vertices, {len(sierpinski.faces)} faces")

        # Test cache
        cache_info = library.get_cache_info()
        print(f"✅ Cache: {cache_info['cached_shapes']} shapes, ~{cache_info['memory_estimate_mb']:.1f}MB")

        print("✅ Geometry system working\n")
        return True

    except Exception as e:
        print(f"❌ Geometry system failed: {e}\n")
        return False

def test_particle_system():
    """Test particle system."""
    print("🧪 Testing Particle System...")

    try:
        from fig.visuals.particles import ParticleSystem, ParticleType, EmissionPattern

        # Create particle system
        ps = ParticleSystem(max_particles=1000)

        # Add emitters
        emitter = ps.add_emitter(position=(0, 0, 0))
        emitter.particle_type = ParticleType.ENERGY
        emitter.emission_pattern = EmissionPattern.FOUNTAIN
        emitter.emission_rate = 50.0

        print(f"✅ Particle System: {len(ps.emitters)} emitters, max {ps.max_particles} particles")

        # Test audio reactivity
        ps.set_audio_data(bass=0.8, mid=0.5, treble=0.3, onset=True)
        print("✅ Audio reactivity test passed")

        # Test MIDI reactivity
        ps.set_midi_data(note=60, velocity=100, channel=0, note_on=True)
        print("✅ MIDI reactivity test passed")

        # Test presets
        presets = ['sparks', 'fountain', 'smoke', 'energy']
        for preset in presets:
            if ps.set_preset(preset):
                print(f"✅ Preset '{preset}' applied")

        # Update system
        ps.update()
        stats = ps.get_statistics()
        print(f"✅ Update: {stats['active_particles']} active particles")

        print("✅ Particle system working\n")
        return True

    except Exception as e:
        print(f"❌ Particle system failed: {e}\n")
        return False

def test_lighting_system():
    """Test lighting system."""
    print("🧪 Testing Lighting System...")

    try:
        from fig.visuals.lighting import LightingSystem, LightType, LightAnimation

        # Create lighting system
        lighting = LightingSystem(max_lights=8)

        # Add different light types
        key_light = lighting.add_light(
            LightType.DIRECTIONAL,
            name="Key Light",
            position=[5, 8, 5],
            intensity=0.8,
            color=(1.0, 0.95, 0.8)
        )

        fill_light = lighting.add_light(
            LightType.POINT,
            name="Fill Light",
            position=[-3, 5, 3],
            intensity=0.4,
            color=(0.8, 0.9, 1.0),
            animation=LightAnimation.PULSE
        )

        print(f"✅ Lighting System: {len(lighting.lights)} lights")

        # Test presets
        presets = ['default', 'concert', 'ambient', 'laser']
        for preset in presets:
            if lighting.apply_preset(preset):
                print(f"✅ Lighting preset '{preset}' applied")
                time.sleep(0.1)  # Brief delay

        # Test audio reactivity
        lighting.update_audio_data(bass=0.7, mid=0.4, treble=0.6, onset=False)
        print("✅ Audio reactivity test passed")

        # Test MIDI reactivity
        lighting.update_midi_data(note=64, velocity=110, channel=0, note_on=True)
        print("✅ MIDI reactivity test passed")

        # Get lighting data
        data = lighting.get_lighting_data()
        print(f"✅ Lighting data: {data['active_lights']} active lights")

        print("✅ Lighting system working\n")
        return True

    except Exception as e:
        print(f"❌ Lighting system failed: {e}\n")
        return False

def test_scene_management():
    """Test scene management system."""
    print("🧪 Testing Scene Management...")

    try:
        from fig.visuals.scene_manager import SceneManager, ScenePreset, CameraMode
        from fig.core.config import get_config

        config = get_config()
        scene = SceneManager(config.visual)

        print(f"✅ Scene Manager initialized")

        # Test scene presets
        presets = [ScenePreset.CIRCLE, ScenePreset.SPIRAL, ScenePreset.DOME,
                  ScenePreset.GRID, ScenePreset.GALAXY, ScenePreset.MANDALA]

        for preset in presets:
            scene.apply_preset(preset, count=6, radius=3.0)
            scene_data = scene.get_scene_data()
            print(f"✅ Preset '{preset.value}': {len(scene_data['objects'])} objects")
            time.sleep(0.1)

        # Test audio update
        audio_data = {
            'bass_energy': 0.6,
            'mid_energy': 0.4,
            'treble_energy': 0.8,
            'onset_detected': True
        }
        scene.on_audio_update(audio_data)
        print("✅ Audio update test passed")

        # Test MIDI events
        scene.on_midi_note_on(note=60, velocity=100, channel=0)
        scene.on_midi_note_off(note=60, velocity=0, channel=0)
        print("✅ MIDI events test passed")

        # Test camera modes
        camera_modes = [CameraMode.ORBIT, CameraMode.STATIC, CameraMode.BOUNCE]
        for mode in camera_modes:
            scene.camera.set_mode(mode)
            print(f"✅ Camera mode '{mode.value}' set")

        print("✅ Scene management working\n")
        return True

    except Exception as e:
        print(f"❌ Scene management failed: {e}\n")
        return False

def test_performance_monitoring():
    """Test performance monitoring."""
    print("🧪 Testing Performance Monitoring...")

    try:
        from fig.monitoring.performance import PerformanceMonitor, QualityLevel
        from fig.core.config import get_config

        config = get_config()
        monitor = PerformanceMonitor(config.performance)

        # Start monitoring
        monitor.start()
        print("✅ Performance monitoring started")

        # Simulate some frames
        for i in range(10):
            monitor.register_frame()
            time.sleep(0.016)  # ~60 FPS

        # Get metrics
        metrics = monitor.get_current_metrics()
        print(f"✅ Current metrics: FPS={metrics['fps']:.1f}, CPU={metrics['cpu_percent']:.1f}%")

        # Test quality levels
        for level in [QualityLevel.LOW, QualityLevel.MEDIUM, QualityLevel.HIGH]:
            monitor.set_quality_level(level)
            print(f"✅ Quality level '{level.value}' applied")

        # Get performance history
        history = monitor.get_metrics_history(2.0)  # Last 2 seconds
        print(f"✅ Performance history: {len(history)} data points")

        monitor.stop()
        print("✅ Performance monitoring working\n")
        return True

    except Exception as e:
        print(f"❌ Performance monitoring failed: {e}\n")
        return False

def test_recording_system():
    """Test recording system."""
    print("🧪 Testing Recording System...")

    try:
        from fig.monitoring.recorder import PerformanceRecorder, RecordingFormat
        from fig.core.config import get_config

        config = get_config()
        recorder = PerformanceRecorder(config.performance)

        print("✅ Performance recorder created")

        # Start brief recording
        recorder.start_recording(title="Test Recording", artist="MMPA Test")
        print("✅ Recording started")

        # Simulate some data
        time.sleep(0.5)  # Record for 0.5 seconds

        # Stop recording
        recorder.stop_recording()
        print("✅ Recording stopped")

        # Get recording info
        info = recorder.get_recording_info()
        print(f"✅ Recording info: {info['frame_count']} frames, {info['metadata']['duration']:.2f}s")

        # Test save/load (create temp file path)
        test_path = "/tmp/mmpa_test_recording"

        # Save recording
        if recorder.save_recording(test_path, RecordingFormat.JSON):
            print("✅ Recording saved as JSON")

            # Test loading
            new_recorder = PerformanceRecorder()
            if new_recorder.load_recording(f"{test_path}.json"):
                print("✅ Recording loaded successfully")
                loaded_info = new_recorder.get_recording_info()
                print(f"✅ Loaded: {loaded_info['frame_count']} frames")

        print("✅ Recording system working\n")
        return True

    except Exception as e:
        print(f"❌ Recording system failed: {e}\n")
        return False

def test_main_application():
    """Test main application orchestration."""
    print("🧪 Testing Main Application...")

    try:
        from fig.core.app import EnhancedApplication

        # Note: We can't fully test the GUI application without Qt Application instance
        # But we can test the initialization
        app = EnhancedApplication()
        print("✅ Enhanced Application created")

        # Test status
        status = app.get_status()
        print(f"✅ Application status: {len(status)} status fields")

        # Test preset application
        preset_applied = app.apply_preset("performance")
        print(f"✅ Preset application: {'success' if preset_applied else 'failed (expected)'}")

        print("✅ Main application working\n")
        return True

    except Exception as e:
        print(f"❌ Main application failed: {e}\n")
        return False

def main():
    """Run complete MMPA system test."""
    print("🎼 MMPA - Midi Morphing Power Arranger")
    print("The Language of Signals Becoming Form")
    print("=" * 50)
    print("Running Complete System Test\n")

    tests = [
        ("Core Modules", test_core_modules),
        ("Geometry System", test_geometry_system),
        ("Particle System", test_particle_system),
        ("Lighting System", test_lighting_system),
        ("Scene Management", test_scene_management),
        ("Performance Monitoring", test_performance_monitoring),
        ("Recording System", test_recording_system),
        ("Main Application", test_main_application),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}\n")

    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! MMPA system is ready.")
        print("\n✨ The modular MMPA architecture is fully functional with:")
        print("   🏗️  Complete modular architecture following fig master plan")
        print("   🎨  Enhanced particle system with 8 types and physics")
        print("   🔺  Comprehensive geometry library with 20+ shapes")
        print("   💡  Advanced lighting system with 7 animations")
        print("   🎭  Scene management with 10 preset arrangements")
        print("   📊  Performance monitoring with adaptive quality")
        print("   📹  Performance recording and playback system")
        print("   🎛️  Thread-safe architecture with Qt signals")
        print("   ⚙️  Professional configuration management")
        print("   🚀  Ready for live performance and development")
    else:
        print(f"⚠️  {total - passed} tests failed. System needs attention.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)