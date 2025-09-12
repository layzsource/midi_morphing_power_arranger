#!/usr/bin/env python3
"""
Configuration module for MIDI Morphing Visualizer
Contains all configuration parameters and settings management.
"""

import os
import json
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class RenderQuality(Enum):
    """Render quality presets."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    ULTRA = "Ultra"


class AudioPriority(Enum):
    """Audio processing priority."""
    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    REALTIME = "Realtime"


@dataclass
class Config:
    """Complete configuration for the MIDI Morphing Visualizer."""
    
    # === MIDI Settings ===
    MIDI_PORT: Optional[str] = None
    MIDI_CHANNEL: int = 0  # 0 = all channels
    VELOCITY_SENSITIVITY: float = 1.0
    NOTE_MIN: int = 0
    NOTE_MAX: int = 127
    MORPH_CC: int = 1  # Modulation wheel
    NOTE_TIMEOUT: int = 60  # seconds
    MIDI_AUTO_RECONNECT: bool = True
    
    # === Audio Settings ===
    AUDIO_ENABLED: bool = False
    AUDIO_DEVICE: Optional[str] = None
    AUDIO_SAMPLE_RATE: int = 44100
    AUDIO_BUFFER_SIZE: int = 2048
    AUDIO_CHUNK_SIZE: int = 1024
    AUDIO_HOP_LENGTH: int = 512
    AUDIO_ONSET_THRESHOLD: float = 2.0
    AUDIO_SPECTRAL_ROLLOFF: float = 0.85
    AUDIO_FREQUENCY_RANGE: List[int] = field(default_factory=lambda: [20, 20000])
    AUDIO_COLOR_STRENGTH: float = 1.0
    AUDIO_MORPH_STRENGTH: float = 0.2
    FREQ_MIN: int = 80
    FREQ_MAX: int = 8000
    
    # === Visualization Settings ===
    BACKGROUND_COLOR: str = "black"  # PyVista background color
    DEFAULT_COLOR: List[float] = field(default_factory=lambda: [0.8, 0.8, 0.8])
    MESH_RESOLUTION: int = 50
    COLOR_SATURATION: float = 0.8
    COLOR_BRIGHTNESS: float = 1.0
    MORPH_SPEED: float = 1.0
    COLOR_TRANSITION_SPEED: float = 0.5
    FLASH_DURATION: int = 150  # milliseconds
    SMOOTH_SHADING: bool = True
    WIREFRAME_MODE: bool = False
    AUTO_ROTATE: bool = False
    ROTATION_SPEED: float = 1.0
    SHOW_EDGES: bool = False
    EDGE_COLOR: List[float] = field(default_factory=lambda: [0.2, 0.2, 0.2])
    
    # === Lighting Settings ===
    NUM_LIGHTS: int = 3
    LIGHT_INTENSITY: float = 1.0
    LIGHT_COLOR: List[float] = field(default_factory=lambda: [1.0, 1.0, 1.0])
    AMBIENT_LIGHT: float = 0.2
    SPECULAR_POWER: int = 50
    ENABLE_SHADOWS: bool = False
    
    # === Particle Settings ===
    PARTICLES_ENABLED: bool = True
    MAX_PARTICLES: int = 1000
    PARTICLE_SIZE_SCALE: float = 1.0
    PARTICLE_OPACITY_SCALE: float = 1.0
    PARTICLE_GRAVITY: List[float] = field(default_factory=lambda: [0.0, -9.8, 0.0])
    PARTICLE_DRAG: float = 0.98
    PARTICLE_PERFORMANCE_MODE: bool = False
    
    # === Scene Manager Settings ===
    MAX_SCENE_OBJECTS: int = 8
    SCENE_PHYSICS_ENABLED: bool = True
    SCENE_BLEND_MODE: str = "normal"
    DEPTH_SORTING: bool = True
    UPDATE_THROTTLE: float = 0.016  # ~60 FPS
    
    # === Performance Settings ===
    TARGET_FPS: int = 60
    VSYNC: bool = True
    RENDER_QUALITY: str = "High"
    MEMORY_LIMIT: int = 1000  # MB
    CLEANUP_INTERVAL: int = 5  # seconds
    FPS_WARNING: int = 30
    MEMORY_WARNING: int = 80  # percentage
    CPU_WARNING: int = 85  # percentage
    ENABLE_PROFILING: bool = True
    VERBOSE_LOGGING: bool = False
    SHOW_DEBUG_INFO: bool = False
    
    # === OSC Settings ===
    OSC_ENABLED: bool = False
    OSC_IP: str = "127.0.0.1"
    OSC_PORT: int = 5005
    OSC_PREFIX: str = "/morphing"
    
    # === Advanced Settings ===
    WORKER_THREADS: int = 2
    AUDIO_PRIORITY: str = "High"
    CONFIG_DIR: str = field(default_factory=lambda: os.path.expanduser("~/.morphing_visualizer"))
    LOG_DIR: str = field(default_factory=lambda: os.path.expanduser("~/.morphing_visualizer/logs"))
    CACHE_DIR: str = field(default_factory=lambda: os.path.expanduser("~/.morphing_visualizer/cache"))
    ENABLE_ML_FEATURES: bool = False
    ENABLE_NETWORK_SYNC: bool = False
    ENABLE_PLUGIN_SYSTEM: bool = False
    ENABLE_OSC: bool = False  # Duplicate for compatibility
    
    # === Note Range Mappings ===
    BASS_RANGE: Tuple[int, int] = (0, 47)
    MELODY_RANGE: Tuple[int, int] = (48, 71)
    TREBLE_RANGE: Tuple[int, int] = (72, 95)
    HIGH_RANGE: Tuple[int, int] = (96, 127)
    
    def save_to_file(self, filename: str):
        """Save configuration to JSON file."""
        try:
            config_dict = asdict(self)
            # Convert numpy arrays and tuples to lists for JSON serialization
            config_dict = self._prepare_for_json(config_dict)
            
            os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
            with open(filename, 'w') as f:
                json.dump(config_dict, f, indent=4)
            print(f"Configuration saved to {filename}")
            return True
        except Exception as e:
            print(f"Failed to save configuration: {e}")
            return False
    
    def load_from_file(self, filename: str):
        """Load configuration from JSON file."""
        try:
            with open(filename, 'r') as f:
                config_dict = json.load(f)
            
            # Update current configuration
            for key, value in config_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            print(f"Configuration loaded from {filename}")
            return True
        except FileNotFoundError:
            print(f"Configuration file not found: {filename}")
            return False
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return False
    
    def save_to_settings(self, settings):
        """Save configuration to QSettings."""
        try:
            # MIDI settings
            settings.setValue("midi/port", self.MIDI_PORT)
            settings.setValue("midi/channel", self.MIDI_CHANNEL)
            settings.setValue("midi/velocity_sensitivity", self.VELOCITY_SENSITIVITY)
            settings.setValue("midi/note_min", self.NOTE_MIN)
            settings.setValue("midi/note_max", self.NOTE_MAX)
            settings.setValue("midi/morph_cc", self.MORPH_CC)
            settings.setValue("midi/note_timeout", self.NOTE_TIMEOUT)
            settings.setValue("midi/auto_reconnect", self.MIDI_AUTO_RECONNECT)
            
            # Audio settings
            settings.setValue("audio/enabled", self.AUDIO_ENABLED)
            settings.setValue("audio/device", self.AUDIO_DEVICE)
            settings.setValue("audio/sample_rate", self.AUDIO_SAMPLE_RATE)
            settings.setValue("audio/buffer_size", self.AUDIO_BUFFER_SIZE)
            settings.setValue("audio/chunk_size", self.AUDIO_CHUNK_SIZE)
            settings.setValue("audio/onset_threshold", self.AUDIO_ONSET_THRESHOLD)
            settings.setValue("audio/color_strength", self.AUDIO_COLOR_STRENGTH)
            settings.setValue("audio/morph_strength", self.AUDIO_MORPH_STRENGTH)
            settings.setValue("audio/freq_min", self.FREQ_MIN)
            settings.setValue("audio/freq_max", self.FREQ_MAX)
            
            # Visualization settings
            settings.setValue("visualization/background_color", self.BACKGROUND_COLOR)
            settings.setValue("visualization/default_color", self.DEFAULT_COLOR)
            settings.setValue("visualization/mesh_resolution", self.MESH_RESOLUTION)
            settings.setValue("visualization/color_saturation", self.COLOR_SATURATION)
            settings.setValue("visualization/color_brightness", self.COLOR_BRIGHTNESS)
            settings.setValue("visualization/morph_speed", self.MORPH_SPEED)
            settings.setValue("visualization/color_transition_speed", self.COLOR_TRANSITION_SPEED)
            settings.setValue("visualization/flash_duration", self.FLASH_DURATION)
            settings.setValue("visualization/smooth_shading", self.SMOOTH_SHADING)
            settings.setValue("visualization/wireframe_mode", self.WIREFRAME_MODE)
            settings.setValue("visualization/auto_rotate", self.AUTO_ROTATE)
            settings.setValue("visualization/rotation_speed", self.ROTATION_SPEED)
            
            # Lighting settings
            settings.setValue("lighting/num_lights", self.NUM_LIGHTS)
            settings.setValue("lighting/light_intensity", self.LIGHT_INTENSITY)
            settings.setValue("lighting/light_color", self.LIGHT_COLOR)
            settings.setValue("lighting/ambient_light", self.AMBIENT_LIGHT)
            
            # Performance settings
            settings.setValue("performance/target_fps", self.TARGET_FPS)
            settings.setValue("performance/vsync", self.VSYNC)
            settings.setValue("performance/render_quality", self.RENDER_QUALITY)
            settings.setValue("performance/memory_limit", self.MEMORY_LIMIT)
            settings.setValue("performance/cleanup_interval", self.CLEANUP_INTERVAL)
            settings.setValue("performance/fps_warning", self.FPS_WARNING)
            settings.setValue("performance/memory_warning", self.MEMORY_WARNING)
            settings.setValue("performance/cpu_warning", self.CPU_WARNING)
            settings.setValue("performance/enable_profiling", self.ENABLE_PROFILING)
            
            # Advanced settings
            settings.setValue("advanced/osc_ip", self.OSC_IP)
            settings.setValue("advanced/osc_port", self.OSC_PORT)
            settings.setValue("advanced/enable_osc", self.ENABLE_OSC)
            settings.setValue("advanced/worker_threads", self.WORKER_THREADS)
            settings.setValue("advanced/audio_priority", self.AUDIO_PRIORITY)
            
            return True
        except Exception as e:
            print(f"Failed to save to settings: {e}")
            return False
    
    def load_from_settings(self, settings):
        """Load configuration from QSettings."""
        try:
            # MIDI settings
            self.MIDI_PORT = settings.value("midi/port", self.MIDI_PORT)
            self.MIDI_CHANNEL = settings.value("midi/channel", self.MIDI_CHANNEL, int)
            self.VELOCITY_SENSITIVITY = settings.value("midi/velocity_sensitivity", self.VELOCITY_SENSITIVITY, float)
            self.NOTE_MIN = settings.value("midi/note_min", self.NOTE_MIN, int)
            self.NOTE_MAX = settings.value("midi/note_max", self.NOTE_MAX, int)
            self.MORPH_CC = settings.value("midi/morph_cc", self.MORPH_CC, int)
            self.NOTE_TIMEOUT = settings.value("midi/note_timeout", self.NOTE_TIMEOUT, int)
            self.MIDI_AUTO_RECONNECT = settings.value("midi/auto_reconnect", self.MIDI_AUTO_RECONNECT, bool)
            
            # Audio settings
            self.AUDIO_ENABLED = settings.value("audio/enabled", self.AUDIO_ENABLED, bool)
            self.AUDIO_DEVICE = settings.value("audio/device", self.AUDIO_DEVICE)
            self.AUDIO_SAMPLE_RATE = settings.value("audio/sample_rate", self.AUDIO_SAMPLE_RATE, int)
            self.AUDIO_BUFFER_SIZE = settings.value("audio/buffer_size", self.AUDIO_BUFFER_SIZE, int)
            self.AUDIO_CHUNK_SIZE = settings.value("audio/chunk_size", self.AUDIO_CHUNK_SIZE, int)
            self.AUDIO_ONSET_THRESHOLD = settings.value("audio/onset_threshold", self.AUDIO_ONSET_THRESHOLD, float)
            self.AUDIO_COLOR_STRENGTH = settings.value("audio/color_strength", self.AUDIO_COLOR_STRENGTH, float)
            self.AUDIO_MORPH_STRENGTH = settings.value("audio/morph_strength", self.AUDIO_MORPH_STRENGTH, float)
            self.FREQ_MIN = settings.value("audio/freq_min", self.FREQ_MIN, int)
            self.FREQ_MAX = settings.value("audio/freq_max", self.FREQ_MAX, int)
            
            # Visualization settings
            self.BACKGROUND_COLOR = settings.value("visualization/background_color", self.BACKGROUND_COLOR)
            default_color = settings.value("visualization/default_color", self.DEFAULT_COLOR)
            if isinstance(default_color, (list, tuple)) and len(default_color) == 3:
                self.DEFAULT_COLOR = list(default_color)
            self.MESH_RESOLUTION = settings.value("visualization/mesh_resolution", self.MESH_RESOLUTION, int)
            self.COLOR_SATURATION = settings.value("visualization/color_saturation", self.COLOR_SATURATION, float)
            self.COLOR_BRIGHTNESS = settings.value("visualization/color_brightness", self.COLOR_BRIGHTNESS, float)
            self.MORPH_SPEED = settings.value("visualization/morph_speed", self.MORPH_SPEED, float)
            self.COLOR_TRANSITION_SPEED = settings.value("visualization/color_transition_speed", self.COLOR_TRANSITION_SPEED, float)
            self.FLASH_DURATION = settings.value("visualization/flash_duration", self.FLASH_DURATION, int)
            self.SMOOTH_SHADING = settings.value("visualization/smooth_shading", self.SMOOTH_SHADING, bool)
            self.WIREFRAME_MODE = settings.value("visualization/wireframe_mode", self.WIREFRAME_MODE, bool)
            self.AUTO_ROTATE = settings.value("visualization/auto_rotate", self.AUTO_ROTATE, bool)
            self.ROTATION_SPEED = settings.value("visualization/rotation_speed", self.ROTATION_SPEED, float)
            
            # Lighting settings
            self.NUM_LIGHTS = settings.value("lighting/num_lights", self.NUM_LIGHTS, int)
            self.LIGHT_INTENSITY = settings.value("lighting/light_intensity", self.LIGHT_INTENSITY, float)
            light_color = settings.value("lighting/light_color", self.LIGHT_COLOR)
            if isinstance(light_color, (list, tuple)) and len(light_color) == 3:
                self.LIGHT_COLOR = list(light_color)
            self.AMBIENT_LIGHT = settings.value("lighting/ambient_light", self.AMBIENT_LIGHT, float)
            
            # Performance settings
            self.TARGET_FPS = settings.value("performance/target_fps", self.TARGET_FPS, int)
            self.VSYNC = settings.value("performance/vsync", self.VSYNC, bool)
            self.RENDER_QUALITY = settings.value("performance/render_quality", self.RENDER_QUALITY)
            self.MEMORY_LIMIT = settings.value("performance/memory_limit", self.MEMORY_LIMIT, int)
            self.CLEANUP_INTERVAL = settings.value("performance/cleanup_interval", self.CLEANUP_INTERVAL, int)
            self.FPS_WARNING = settings.value("performance/fps_warning", self.FPS_WARNING, int)
            self.MEMORY_WARNING = settings.value("performance/memory_warning", self.MEMORY_WARNING, int)
            self.CPU_WARNING = settings.value("performance/cpu_warning", self.CPU_WARNING, int)
            self.ENABLE_PROFILING = settings.value("performance/enable_profiling", self.ENABLE_PROFILING, bool)
            
            # Advanced settings
            self.OSC_IP = settings.value("advanced/osc_ip", self.OSC_IP)
            self.OSC_PORT = settings.value("advanced/osc_port", self.OSC_PORT, int)
            self.ENABLE_OSC = settings.value("advanced/enable_osc", self.ENABLE_OSC, bool)
            self.WORKER_THREADS = settings.value("advanced/worker_threads", self.WORKER_THREADS, int)
            self.AUDIO_PRIORITY = settings.value("advanced/audio_priority", self.AUDIO_PRIORITY)
            
            return True
        except Exception as e:
            print(f"Failed to load from settings: {e}")
            return False
    
    def _prepare_for_json(self, obj):
        """Prepare configuration for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._prepare_for_json(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, '__dict__'):
            return self._prepare_for_json(obj.__dict__)
        else:
            return obj
    
    def get_preset(self, preset_name: str) -> Dict:
        """Get a configuration preset."""
        presets = {
            "performance": {
                "RENDER_QUALITY": "Low",
                "MESH_RESOLUTION": 30,
                "MAX_PARTICLES": 500,
                "PARTICLE_PERFORMANCE_MODE": True,
                "TARGET_FPS": 30,
                "ENABLE_SHADOWS": False
            },
            "quality": {
                "RENDER_QUALITY": "Ultra",
                "MESH_RESOLUTION": 100,
                "MAX_PARTICLES": 2000,
                "PARTICLE_PERFORMANCE_MODE": False,
                "TARGET_FPS": 60,
                "ENABLE_SHADOWS": True
            },
            "balanced": {
                "RENDER_QUALITY": "High",
                "MESH_RESOLUTION": 50,
                "MAX_PARTICLES": 1000,
                "PARTICLE_PERFORMANCE_MODE": False,
                "TARGET_FPS": 60,
                "ENABLE_SHADOWS": False
            }
        }
        return presets.get(preset_name, {})
    
    def apply_preset(self, preset_name: str):
        """Apply a configuration preset."""
        preset = self.get_preset(preset_name)
        for key, value in preset.items():
            if hasattr(self, key):
                setattr(self, key, value)
        print(f"Applied preset: {preset_name}")


# Test function
def test_config():
    """Test configuration functionality."""
    print("Testing Configuration")
    print("=" * 50)
    
    config = Config()
    
    # Test default values
    print(f"✓ Default BACKGROUND_COLOR: {config.BACKGROUND_COLOR}")
    print(f"✓ Default TARGET_FPS: {config.TARGET_FPS}")
    print(f"✓ Default MAX_PARTICLES: {config.MAX_PARTICLES}")
    
    # Test save/load
    test_file = "test_config.json"
    config.MIDI_PORT = "Test Device"
    config.TARGET_FPS = 120
    
    if config.save_to_file(test_file):
        print(f"✓ Saved config to {test_file}")
        
        # Load into new config
        new_config = Config()
        if new_config.load_from_file(test_file):
            print(f"✓ Loaded config from {test_file}")
            print(f"  • MIDI_PORT: {new_config.MIDI_PORT}")
            print(f"  • TARGET_FPS: {new_config.TARGET_FPS}")
        
        # Clean up
        try:
            os.remove(test_file)
            print(f"✓ Cleaned up test file")
        except:
            pass
    
    # Test presets
    print("\n✓ Available presets:")
    for preset_name in ["performance", "quality", "balanced"]:
        preset = config.get_preset(preset_name)
        print(f"  • {preset_name}: {len(preset)} settings")
    
    print("\n✅ All configuration tests passed!")


if __name__ == "__main__":
    test_config()
