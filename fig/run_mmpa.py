#!/usr/bin/env python3
"""
MMPA - Minimal Runnable Version
A working demonstration of the MMPA core systems without full Qt application.
"""

import sys
import time
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Configure logging for MMPA."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def demonstrate_mmpa_systems():
    """Demonstrate MMPA systems working."""
    print("🎼 MMPA - Midi Morphing Power Arranger")
    print("The Language of Signals Becoming Form")
    print("=" * 50)

    try:
        # Test configuration system
        print("🔧 Testing Configuration System...")
        from fig.core.config import get_config
        config = get_config()
        print(f"   ✅ Audio backend: {config.audio.backend}")
        print(f"   ✅ Target FPS: {config.visual.target_fps}")
        print(f"   ✅ Max particles: {config.visual.particle_count_max}")

        # Test utilities
        print("\n🛠️  Testing Utilities...")
        from fig.core.utils import ColorMapper, MathUtils

        # Test color mapping
        freq_color = ColorMapper.frequency_to_color(440.0)  # A4
        note_color = ColorMapper.note_to_color(60)  # Middle C
        print(f"   ✅ 440Hz maps to color: {freq_color.name()}")
        print(f"   ✅ MIDI note 60 maps to color: {note_color.name()}")

        # Test math utilities
        smoothed = MathUtils.smooth_value(0.0, 1.0, 0.1)
        mapped = MathUtils.map_range(0.5, 0, 1, -10, 10)
        print(f"   ✅ Smoothing: {smoothed:.2f}")
        print(f"   ✅ Range mapping: {mapped:.2f}")

        # Test geometry library
        print("\n🔺 Testing Geometry Library...")
        from fig.visuals.geometry_library import GeometryLibrary, ShapeType

        library = GeometryLibrary()
        sphere = library.get_shape(ShapeType.SPHERE, radius=1.0)
        cube = library.get_shape(ShapeType.CUBE, size=1.0)
        torus = library.get_shape(ShapeType.TORUS, major_radius=1.0, minor_radius=0.3)

        print(f"   ✅ Sphere: {len(sphere.vertices)} vertices, {len(sphere.faces)} faces")
        print(f"   ✅ Cube: {len(cube.vertices)} vertices, {len(cube.faces)} faces")
        print(f"   ✅ Torus: {len(torus.vertices)} vertices, {len(torus.faces)} faces")

        # Test advanced shapes
        helix = library.get_shape(ShapeType.HELIX, radius=1.0, height=3.0, turns=2.0)
        print(f"   ✅ Helix: {len(helix.vertices)} vertices")

        # Test fractals
        terrain = library.get_shape(ShapeType.TERRAIN, size=17, height_scale=1.0)
        sierpinski = library.get_shape(ShapeType.SIERPINSKI, order=2)
        print(f"   ✅ Terrain: {len(terrain.vertices)} vertices")
        print(f"   ✅ Sierpinski: {len(sierpinski.vertices)} vertices")

        cache_info = library.get_cache_info()
        print(f"   ✅ Cache: {cache_info['cached_shapes']} shapes, ~{cache_info['memory_estimate_mb']:.1f}MB")

        # Test particle system (without Qt timers)
        print("\n🎨 Testing Particle System...")
        from fig.visuals.particles import ParticleSystem, ParticleType, EmissionPattern

        # Create particle system without starting timers
        ps = ParticleSystem(max_particles=100)

        # Add emitter
        emitter = ps.add_emitter(position=(0, 0, 0))
        emitter.particle_type = ParticleType.ENERGY
        emitter.emission_pattern = EmissionPattern.FOUNTAIN
        emitter.emission_rate = 10.0

        print(f"   ✅ Particle system: {len(ps.emitters)} emitters")

        # Test audio reactivity
        ps.set_audio_data(bass=0.8, mid=0.5, treble=0.3, onset=True)
        print("   ✅ Audio reactivity configured")

        # Test MIDI reactivity
        ps.set_midi_data(note=60, velocity=100, channel=0, note_on=True)
        print("   ✅ MIDI reactivity configured")

        # Manually emit some particles
        new_particles = emitter.emit_particles(0.1)  # 0.1 second delta
        ps.particles.extend(new_particles[:10])  # Add up to 10 particles

        stats = ps.get_statistics()
        print(f"   ✅ Statistics: {stats['active_particles']} active particles")

        # Test lighting system (without Qt)
        print("\n💡 Testing Lighting System...")
        from fig.visuals.lighting import LightingSystem, LightType, LightAnimation

        # Create lighting system without starting timers
        lighting = LightingSystem(max_lights=4)

        # Add lights manually
        key_light = lighting.add_light(
            LightType.DIRECTIONAL,
            name="Key Light",
            position=[5, 8, 5],
            intensity=0.8
        )

        fill_light = lighting.add_light(
            LightType.POINT,
            name="Fill Light",
            position=[-3, 5, 3],
            intensity=0.4
        )

        print(f"   ✅ Lighting: {len(lighting.lights)} lights created")

        # Test presets
        if lighting.apply_preset("concert"):
            print("   ✅ Concert preset applied")

        # Test audio reactivity
        lighting.update_audio_data(bass=0.7, mid=0.4, treble=0.6)
        print("   ✅ Audio reactivity working")

        # Test scene management
        print("\n🎭 Testing Scene Management...")
        from fig.visuals.scene_manager import SceneManager, ScenePreset

        # Create scene manager without Qt parent
        scene = SceneManager(visual_config=config.visual, parent=None)

        # Apply preset
        scene.apply_preset(ScenePreset.CIRCLE, count=6, radius=3.0)
        scene_data = scene.get_scene_data()
        print(f"   ✅ Circle preset: {len(scene_data['objects'])} objects")

        # Test audio update
        audio_data = {
            'bass_energy': 0.6,
            'mid_energy': 0.4,
            'treble_energy': 0.8,
            'onset_detected': True
        }
        scene.on_audio_update(audio_data)
        print("   ✅ Audio update processed")

        # Test performance monitoring (without Qt)
        print("\n📊 Testing Performance Monitoring...")
        from fig.monitoring.performance import PerformanceMonitor, QualityLevel

        # Create monitor without starting
        monitor = PerformanceMonitor(config.performance, parent=None)

        # Simulate frame registration
        for i in range(5):
            monitor.register_frame()
            time.sleep(0.016)  # ~60 FPS

        # Update metrics manually
        monitor._update_metrics()
        metrics = monitor.get_current_metrics()
        print(f"   ✅ Performance: FPS={metrics['fps']:.1f}")

        # Test quality levels
        monitor.set_quality_level(QualityLevel.HIGH)
        print(f"   ✅ Quality level: {monitor.current_quality.value}")

        # Test recording system
        print("\n📹 Testing Recording System...")
        from fig.monitoring.recorder import PerformanceRecorder, RecordingFormat

        # Create recorder
        recorder = PerformanceRecorder(config.performance, parent=None)
        print("   ✅ Recorder created")

        # Test recording info
        info = recorder.get_recording_info()
        print(f"   ✅ Recording state: {info['state']}")

        print("\n" + "=" * 50)
        print("🎉 SUCCESS! All MMPA core systems are working!")
        print("\n✨ What's working:")
        print("   🏗️  Modular architecture with proper imports")
        print("   ⚙️  Configuration management system")
        print("   🔺  Comprehensive geometry library (20+ shapes)")
        print("   🎨  Enhanced particle system with physics")
        print("   💡  Advanced lighting system with presets")
        print("   🎭  Scene management with coordinated control")
        print("   📊  Performance monitoring system")
        print("   📹  Performance recording system")
        print("   🛠️  Professional utilities and helpers")

        print(f"\n🚀 Ready for next steps:")
        print("   1. Audio/MIDI module implementation")
        print("   2. Qt GUI development")
        print("   3. OpenGL/3D rendering backend")
        print("   4. Live performance integration")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_logging()
    success = demonstrate_mmpa_systems()

    if success:
        print("\n🎼 MMPA foundation is ready! The Language of Signals Becoming Form awaits...")
    else:
        print("\n⚠️ Some issues found. Check the error messages above.")

    sys.exit(0 if success else 1)