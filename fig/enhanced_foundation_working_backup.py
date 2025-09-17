#!/usr/bin/env python3
"""
Enhanced MIDI Morphing Visualizer - Complete Integration
A comprehensive, professional-grade audio-visual performance system that combines 
advanced 3D morphing, real-time audio analysis, MIDI integration, particle physics, 
and dynamic lighting for interactive performances and live shows.

This version integrates the best of both main.py and the complete implementation,
providing a robust, feature-complete application with all advanced capabilities.
"""

import sys
import os
import logging
import time
import threading
import colorsys
import numpy as np
import ctypes
import queue
import json
import traceback
import math
import psutil
import weakref
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from enum import Enum, IntEnum
from collections import defaultdict, deque

try:
    import pyaudio
    HAS_PYAUDIO = True
except ImportError:
    HAS_PYAUDIO = False

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('midi_visualizer.log')
    ]
)
logger = logging.getLogger(__name__)

# Core dependencies with comprehensive error handling
try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider,
        QLabel, QComboBox, QStatusBar, QPushButton, QCheckBox, QMessageBox,
        QMenuBar, QMenu, QHBoxLayout, QGroupBox, QGridLayout, QTabWidget,
        QSpinBox, QDoubleSpinBox, QTextEdit, QProgressBar, QFrame,
        QDial, QButtonGroup, QRadioButton, QSpacerItem, QSizePolicy,
        QScrollArea, QSplitter, QTreeWidget, QTreeWidgetItem, QFileDialog,
        QColorDialog
    )
    from PySide6.QtOpenGLWidgets import QOpenGLWidget
    from PySide6.QtCore import Qt, QSettings, QTimer, Signal, QObject, QThread, QPropertyAnimation, QEasingCurve, QMutex, QMutexLocker
    from PySide6.QtGui import QAction, QActionGroup, QFont, QKeySequence, QShortcut, QColor, QPalette, QPainter, QPixmap
    QT_AVAILABLE = True
    logger.info("✅ PySide6 successfully imported")
except ImportError as e:
    logger.error(f"❌ PySide6 import error: {e}")
    print("Please install PySide6: pip install PySide6")
    QT_AVAILABLE = False

# OpenGL for 3D rendering
try:
    from OpenGL.GL import *
    from OpenGL.GLU import gluPerspective
    OPENGL_AVAILABLE = True
    logger.info("✅ OpenGL successfully imported")
except ImportError as e:
    logger.warning(f"⚠️ OpenGL not available: {e}")
    OPENGL_AVAILABLE = False

# PyVista for advanced 3D features
try:
    import pyvista as pv
    from pyvistaqt import QtInteractor
    HAS_PYVISTA = True
    logger.info("✅ PyVista available for advanced 3D features")
except ImportError:
    logger.warning("⚠️ PyVista not available - advanced 3D features disabled")
    HAS_PYVISTA = False

# Audio processing libraries
try:
    import sounddevice as sd
    import soundfile as sf
    HAS_SOUNDDEVICE = True
    logger.info("✅ SoundDevice available")
except ImportError:
    logger.warning("⚠️ SoundDevice not available")
    HAS_SOUNDDEVICE = False
    try:
        import pyaudio
        HAS_PYAUDIO = True
        logger.info("✅ PyAudio fallback available")
    except ImportError:
        logger.warning("⚠️ PyAudio also not available")
        HAS_PYAUDIO = False

HAS_AUDIO = HAS_SOUNDDEVICE or HAS_PYAUDIO

# Advanced audio analysis
try:
    import librosa
    import librosa.display
    HAS_LIBROSA = True
    logger.info("✅ Librosa available for advanced audio analysis")
except ImportError:
    logger.warning("⚠️ Librosa not available - basic audio analysis only")
    HAS_LIBROSA = False

# MIDI support
try:
    import rtmidi
    HAS_MIDI = True
    logger.info("✅ RTMIDI available")
except ImportError:
    logger.warning("⚠️ MIDI support not available - install python-rtmidi")
    HAS_MIDI = False

# Note names and frequency conversion
NOTE_NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def hz_to_note_name(hz: float) -> str:
    """Convert frequency in Hz to note name with octave"""
    if hz <= 0:
        return '--'
    try:
        midi = round(69 + 12 * math.log2(hz / 440.0))
        note = NOTE_NAMES_SHARP[midi % 12]
        octave = midi // 12 - 1
        return f"{note}{octave} ({int(hz)} Hz)"
    except (ValueError, OverflowError):
        return f"({int(hz)} Hz)"

# Constants and Enums
class MorphShapes(Enum):
    """Available shapes for morphing"""
    SPHERE = "sphere"
    CUBE = "cube"
    CYLINDER = "cylinder"
    CONE = "cone"
    TORUS = "torus"
    ICOSAHEDRON = "icosahedron"
    OCTAHEDRON = "octahedron"
    DODECAHEDRON = "dodecahedron"
    TETRAHEDRON = "tetrahedron"
    PLANE = "plane"
    PYRAMID = "pyramid"
    HELIX = "helix"
    MOBIUS = "mobius"
    KLEIN_BOTTLE = "klein_bottle"
    STAR = "star"
    HEART = "heart"
    SPIRAL = "spiral"
    CRYSTAL = "crystal"
    FRACTAL = "fractal"
    TERRAIN = "terrain"

class ParticleType(Enum):
    """Particle types for the particle system"""
    SPARK = "spark"
    BURST = "burst"
    TRAIL = "trail"
    BLOOM = "bloom"
    EXPLOSION = "explosion"
    SMOKE = "smoke"
    FIRE = "fire"
    SNOW = "snow"

class LightType(Enum):
    """Lighting system types"""
    POINT = "point"
    DIRECTIONAL = "directional"
    SPOT = "spot"
    AMBIENT = "ambient"
    AREA = "area"

class LightAnimation(Enum):
    """Light animation modes"""
    STATIC = "static"
    PULSE = "pulse"
    ROTATE = "rotate"
    BREATHE = "breathe"
    STROBE = "strobe"
    WAVE = "wave"
    RAINBOW = "rainbow"

class RenderMode(Enum):
    """Rendering modes"""
    DOTS = "dots"
    WIREFRAME = "wireframe"
    SOLID = "solid"
    SHADED = "shaded"

# Global state for audio analysis
class AudioState:
    def __init__(self):
        self.centroid_hz = 0.0
        self.amplitude = 0.0
        self.source_status = "Audio: Off"
        self.running = True
        self.audio_enabled = False  # Audio processing disabled by default
        self.midi_note_freq = 440.0
        self.onset_detected = False
        self.beat_detected = False
        self.tempo = 120.0
        self.lock = threading.Lock()

audio_state = AudioState()

class CircularBuffer:
    """High-performance circular buffer for particles and lights"""

    def __init__(self, max_size):
        self.max_size = max_size
        self.buffer = [None] * max_size
        self.head = 0  # Points to next insertion position
        self.size = 0  # Current number of elements

    def add(self, item):
        """Add item to buffer (O(1) operation)"""
        self.buffer[self.head] = item
        self.head = (self.head + 1) % self.max_size
        if self.size < self.max_size:
            self.size += 1

    def add_multiple(self, items):
        """Add multiple items efficiently"""
        for item in items:
            self.add(item)

    def get_active_items(self):
        """Get all active items as a list (only when needed for rendering)"""
        if self.size == 0:
            return []

        if self.size < self.max_size:
            # Buffer not full yet, return items from start
            return [item for item in self.buffer[:self.size] if item is not None]
        else:
            # Buffer is full, construct proper order
            result = []
            for i in range(self.max_size):
                idx = (self.head + i) % self.max_size
                if self.buffer[idx] is not None:
                    result.append(self.buffer[idx])
            return result

    def remove_expired(self, current_time, life_attr='max_life', created_attr='created_time'):
        """Remove expired items efficiently (in-place filtering)"""
        if self.size == 0:
            return 0

        removed_count = 0
        for i in range(self.max_size):
            if self.buffer[i] is not None:
                item = self.buffer[i]

                # Check if item has the required attributes
                if hasattr(item, life_attr) and hasattr(item, created_attr):
                    age = current_time - getattr(item, created_attr)
                    max_life = getattr(item, life_attr)
                    if age > max_life:
                        self.buffer[i] = None
                        removed_count += 1
                        self.size -= 1
                # For particles, check life attribute
                elif hasattr(item, 'life') and item.life <= 0:
                    self.buffer[i] = None
                    removed_count += 1
                    self.size -= 1

        return removed_count

    def clear(self):
        """Clear all items"""
        for i in range(self.max_size):
            self.buffer[i] = None
        self.size = 0
        self.head = 0

    def __len__(self):
        return self.size

class ObjectPool:
    """Generic object pool for efficient memory allocation"""

    def __init__(self, object_class, max_size=1000):
        self.object_class = object_class
        self.max_size = max_size
        self.available = []
        self.in_use = set()
        self.total_created = 0

    def acquire(self, *args, **kwargs):
        """Get an object from the pool"""
        if self.available:
            obj = self.available.pop()
            self.in_use.add(id(obj))
            # Reset object state if it has a reset method
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
            return obj
        else:
            # Create new object if pool is empty
            obj = self.object_class(*args, **kwargs)
            self.in_use.add(id(obj))
            self.total_created += 1
            return obj

    def release(self, obj):
        """Return an object to the pool"""
        obj_id = id(obj)
        if obj_id in self.in_use:
            self.in_use.remove(obj_id)
            if len(self.available) < self.max_size:
                self.available.append(obj)

    def get_stats(self):
        """Get pool statistics"""
        return {
            'available': len(self.available),
            'in_use': len(self.in_use),
            'total_created': self.total_created,
            'pool_efficiency': len(self.available) / max(1, self.total_created)
        }

class VertexBufferPool:
    """Pool for managing vertex buffer allocations"""

    def __init__(self):
        self.buffers = {}  # size -> list of available buffers
        self.allocated_buffers = set()

    def get_buffer(self, size):
        """Get a vertex buffer of specified size"""
        # Round up to nearest power of 2 for efficient pooling
        pooled_size = self._round_to_power_of_2(size)

        if pooled_size in self.buffers and self.buffers[pooled_size]:
            buffer = self.buffers[pooled_size].pop()
            self.allocated_buffers.add(id(buffer))
            return buffer
        else:
            # Create new buffer
            buffer = np.zeros((pooled_size, 3), dtype=np.float32)
            self.allocated_buffers.add(id(buffer))
            return buffer

    def return_buffer(self, buffer):
        """Return a buffer to the pool"""
        buffer_id = id(buffer)
        if buffer_id in self.allocated_buffers:
            self.allocated_buffers.remove(buffer_id)
            size = len(buffer)

            if size not in self.buffers:
                self.buffers[size] = []

            # Limit pool size to prevent excessive memory usage
            if len(self.buffers[size]) < 10:
                # Clear buffer data for reuse
                buffer.fill(0)
                self.buffers[size].append(buffer)

    def _round_to_power_of_2(self, n):
        """Round up to nearest power of 2"""
        if n <= 0:
            return 1
        return 2 ** (n - 1).bit_length()

class GPUMemoryTracker:
    """Track and manage GPU memory usage"""

    def __init__(self):
        self.allocated_textures = {}
        self.allocated_buffers = {}
        self.estimated_gpu_usage = 0  # Bytes

    def register_texture(self, texture_id, width, height, format_bytes=4):
        """Register a texture allocation"""
        size = width * height * format_bytes
        self.allocated_textures[texture_id] = size
        self.estimated_gpu_usage += size

    def unregister_texture(self, texture_id):
        """Unregister a texture allocation"""
        if texture_id in self.allocated_textures:
            size = self.allocated_textures.pop(texture_id)
            self.estimated_gpu_usage -= size

    def register_buffer(self, buffer_id, size_bytes):
        """Register a GPU buffer allocation"""
        self.allocated_buffers[buffer_id] = size_bytes
        self.estimated_gpu_usage += size_bytes

    def unregister_buffer(self, buffer_id):
        """Unregister a GPU buffer allocation"""
        if buffer_id in self.allocated_buffers:
            size = self.allocated_buffers.pop(buffer_id)
            self.estimated_gpu_usage -= size

    def get_gpu_usage_mb(self):
        """Get estimated GPU memory usage in MB"""
        return self.estimated_gpu_usage / (1024 * 1024)

    def get_allocation_summary(self):
        """Get detailed allocation summary"""
        return {
            'textures': len(self.allocated_textures),
            'buffers': len(self.allocated_buffers),
            'total_mb': self.get_gpu_usage_mb(),
            'texture_mb': sum(self.allocated_textures.values()) / (1024 * 1024),
            'buffer_mb': sum(self.allocated_buffers.values()) / (1024 * 1024)
        }

class TextureCache:
    """LRU cache for texture resources"""

    def __init__(self, max_size_mb=256):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache = {}  # key -> (texture_data, size, access_time)
        self.current_size = 0
        self.access_order = deque()

    def get(self, key):
        """Get texture from cache"""
        if key in self.cache:
            texture_data, size, _ = self.cache[key]
            # Update access time
            current_time = time.time()
            self.cache[key] = (texture_data, size, current_time)
            # Move to end of access order
            self.access_order.remove(key)
            self.access_order.append(key)
            return texture_data
        return None

    def put(self, key, texture_data, size):
        """Store texture in cache"""
        # Remove existing entry if present
        if key in self.cache:
            self._remove_entry(key)

        # Make space if needed
        while self.current_size + size > self.max_size_bytes and self.access_order:
            oldest_key = self.access_order.popleft()
            self._remove_entry(oldest_key)

        # Add new entry
        if self.current_size + size <= self.max_size_bytes:
            self.cache[key] = (texture_data, size, time.time())
            self.current_size += size
            self.access_order.append(key)

    def _remove_entry(self, key):
        """Remove entry from cache"""
        if key in self.cache:
            _, size, _ = self.cache.pop(key)
            self.current_size -= size

    def get_stats(self):
        """Get cache statistics"""
        return {
            'entries': len(self.cache),
            'size_mb': self.current_size / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'utilization': self.current_size / self.max_size_bytes
        }

class MemoryUsagePredictor:
    """Predict future memory usage based on patterns"""

    def __init__(self):
        self.usage_history = deque(maxlen=60)  # Last 60 measurements
        self.allocation_rate = 0.0  # MB/second
        self.peak_prediction = 0.0

    def record_usage(self, current_usage_mb):
        """Record current memory usage"""
        current_time = time.time()
        self.usage_history.append((current_time, current_usage_mb))

        if len(self.usage_history) >= 2:
            self._update_predictions()

    def _update_predictions(self):
        """Update allocation rate and peak predictions"""
        if len(self.usage_history) < 2:
            return

        # Calculate allocation rate (trend)
        recent_points = list(self.usage_history)[-10:]  # Last 10 measurements
        if len(recent_points) >= 2:
            time_diff = recent_points[-1][0] - recent_points[0][0]
            usage_diff = recent_points[-1][1] - recent_points[0][1]

            if time_diff > 0:
                self.allocation_rate = usage_diff / time_diff

        # Predict peak usage in next 30 seconds
        current_usage = self.usage_history[-1][1]
        predicted_increase = self.allocation_rate * 30  # 30 seconds ahead
        self.peak_prediction = max(current_usage, current_usage + predicted_increase)

    def should_preemptive_cleanup(self, threshold_mb=800):
        """Determine if preemptive cleanup should be triggered"""
        return self.peak_prediction > threshold_mb

    def get_prediction_info(self):
        """Get prediction information"""
        return {
            'allocation_rate_mb_per_sec': self.allocation_rate,
            'predicted_peak_mb': self.peak_prediction,
            'samples': len(self.usage_history)
        }

class AdvancedMemoryManager:
    """Intelligent memory management with object pooling and GPU optimization"""

    def __init__(self):
        self.memory_threshold_mb = 500  # MB threshold for cleanup
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 30.0  # seconds between checks
        self.force_cleanup_threshold_mb = 1000  # MB for aggressive cleanup

        # Object pools for efficient allocation/deallocation
        self.particle_pool = ObjectPool(Particle, max_size=2000)
        self.light_pool = ObjectPool(Light, max_size=100)
        self.vertex_buffer_pool = VertexBufferPool()

        # GPU memory management
        self.gpu_memory_tracker = GPUMemoryTracker()
        self.texture_cache = TextureCache(max_size_mb=256)

        # Predictive cleanup
        self.usage_predictor = MemoryUsagePredictor()
        self.allocation_patterns = deque(maxlen=100)

        # Performance monitoring
        self.allocation_count = 0
        self.deallocation_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def acquire_particle(self, **kwargs):
        """Get a particle from the object pool"""
        self.allocation_count += 1
        return self.particle_pool.acquire(**kwargs)

    def release_particle(self, particle):
        """Return a particle to the object pool"""
        self.deallocation_count += 1
        self.particle_pool.release(particle)

    def acquire_light(self, **kwargs):
        """Get a light from the object pool"""
        self.allocation_count += 1
        return self.light_pool.acquire(**kwargs)

    def release_light(self, light):
        """Return a light to the object pool"""
        self.deallocation_count += 1
        self.light_pool.release(light)

    def get_vertex_buffer(self, size):
        """Get a vertex buffer from the pool"""
        return self.vertex_buffer_pool.get_buffer(size)

    def return_vertex_buffer(self, buffer):
        """Return a vertex buffer to the pool"""
        self.vertex_buffer_pool.return_buffer(buffer)

    def get_cached_texture(self, key):
        """Get texture from cache"""
        texture = self.texture_cache.get(key)
        if texture is not None:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        return texture

    def cache_texture(self, key, texture_data, size):
        """Store texture in cache"""
        self.texture_cache.put(key, texture_data, size)

    def check_memory_usage(self):
        """Check current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)  # MB
        except ImportError:
            return 0  # Fallback if psutil not available

    def should_cleanup(self, force_check=False):
        """Intelligent cleanup decision with predictive analysis"""
        current_time = time.time()

        if force_check or (current_time - self.last_cleanup_time) > self.cleanup_interval:
            memory_usage = self.check_memory_usage()
            self.last_cleanup_time = current_time

            # Record usage for prediction
            self.usage_predictor.record_usage(memory_usage)

            # Check for immediate cleanup needs
            if memory_usage > self.force_cleanup_threshold_mb:
                return 'aggressive'
            elif memory_usage > self.memory_threshold_mb:
                return 'normal'

            # Check predictive cleanup
            if self.usage_predictor.should_preemptive_cleanup():
                logger.info(f"🔮 Preemptive cleanup triggered: predicted peak {self.usage_predictor.peak_prediction:.1f}MB")
                return 'preemptive'

        return 'none'

    def perform_cleanup(self, particle_system, lighting_system, session_data=None, level='normal'):
        """Intelligent memory cleanup with object pool optimization"""
        cleaned_items = 0
        start_time = time.time()

        if level == 'aggressive':
            # Aggressive cleanup: reduce limits and clear more data
            if hasattr(particle_system, 'particles'):
                old_max = particle_system.max_particles
                particle_system.max_particles = min(500, old_max)
                cleaned_items += self._cleanup_particles(particle_system, aggressive=True)

            if hasattr(lighting_system, 'lights'):
                old_max = lighting_system.max_lights
                lighting_system.max_lights = min(25, old_max)
                cleaned_items += self._cleanup_lights(lighting_system, aggressive=True)

            # Trim session data more aggressively
            if session_data and len(session_data) > 100:
                removed = len(session_data) - 100
                session_data[:] = session_data[-100:]
                cleaned_items += removed

            # Aggressive cache cleanup
            self._cleanup_caches(aggressive=True)

        elif level == 'preemptive':
            # Preemptive cleanup: moderate but proactive
            if hasattr(particle_system, 'particles'):
                cleaned_items += self._cleanup_particles(particle_system, aggressive=False)

            if hasattr(lighting_system, 'lights'):
                cleaned_items += self._cleanup_lights(lighting_system, aggressive=False)

            # Optimize object pools
            self._optimize_object_pools()

            # Moderate cache cleanup
            self._cleanup_caches(aggressive=False)

        elif level == 'normal':
            # Normal cleanup: remove expired items and trim data
            if hasattr(particle_system, 'particles'):
                cleaned_items += self._cleanup_particles(particle_system, aggressive=False)

            if hasattr(lighting_system, 'lights'):
                cleaned_items += self._cleanup_lights(lighting_system, aggressive=False)

            # Trim session data
            if session_data and len(session_data) > 500:
                removed = len(session_data) - 500
                session_data[:] = session_data[-500:]
                cleaned_items += removed

        # Force garbage collection
        import gc
        collected = gc.collect()

        cleanup_time = time.time() - start_time
        logger.debug(f"🧹 Memory cleanup ({level}): {cleaned_items} items, {collected} collected, {cleanup_time:.3f}s")

        return cleaned_items, collected

    def _cleanup_caches(self, aggressive=False):
        """Clean up texture and vertex buffer caches"""
        if aggressive:
            # Clear significant portion of texture cache
            cache_stats = self.texture_cache.get_stats()
            if cache_stats['utilization'] > 0.7:
                # Remove 50% of cache entries
                entries_to_remove = cache_stats['entries'] // 2
                for _ in range(entries_to_remove):
                    if self.texture_cache.access_order:
                        oldest_key = self.texture_cache.access_order.popleft()
                        self.texture_cache._remove_entry(oldest_key)

        # Clean up vertex buffer pool (remove excessive buffers)
        for size, buffers in self.vertex_buffer_pool.buffers.items():
            if len(buffers) > 5:  # Keep max 5 buffers per size
                excess = len(buffers) - 5
                for _ in range(excess):
                    buffers.pop()

    def _optimize_object_pools(self):
        """Optimize object pool sizes based on usage patterns"""
        # Analyze particle pool efficiency
        particle_stats = self.particle_pool.get_stats()
        if particle_stats['pool_efficiency'] < 0.3:  # Low efficiency
            # Reduce pool size to prevent memory waste
            self.particle_pool.max_size = max(500, self.particle_pool.max_size // 2)

        # Analyze light pool efficiency
        light_stats = self.light_pool.get_stats()
        if light_stats['pool_efficiency'] < 0.3:
            self.light_pool.max_size = max(50, self.light_pool.max_size // 2)

    def get_comprehensive_memory_stats(self):
        """Get detailed memory usage statistics"""
        cpu_memory = self.check_memory_usage()
        gpu_summary = self.gpu_memory_tracker.get_allocation_summary()

        return {
            'cpu_memory_mb': cpu_memory,
            'gpu_memory_mb': gpu_summary['total_mb'],
            'particle_pool': self.particle_pool.get_stats(),
            'light_pool': self.light_pool.get_stats(),
            'texture_cache': self.texture_cache.get_stats(),
            'prediction': self.usage_predictor.get_prediction_info(),
            'allocations': self.allocation_count,
            'deallocations': self.deallocation_count,
            'cache_hit_rate': self.cache_hits / max(1, self.cache_hits + self.cache_misses),
            'pool_efficiency': {
                'particles': self.particle_pool.get_stats()['pool_efficiency'],
                'lights': self.light_pool.get_stats()['pool_efficiency']
            }
        }

    def _cleanup_particles(self, particle_system, aggressive=False):
        """Clean up particle system"""
        if not hasattr(particle_system, 'particles'):
            return 0

        initial_count = len(particle_system.particles)

        if aggressive:
            # Remove particles more aggressively
            current_time = time.time()
            # Force cleanup of particles older than 1 second
            particle_system.particles.remove_expired(current_time - 1.0)
        else:
            # Normal cleanup of expired particles
            current_time = time.time()
            particle_system.particles.remove_expired(current_time)

        return initial_count - len(particle_system.particles)

    def _cleanup_lights(self, lighting_system, aggressive=False):
        """Clean up lighting system"""
        if not hasattr(lighting_system, 'lights'):
            return 0

        initial_count = len(lighting_system.lights)

        if aggressive:
            # Remove lights more aggressively
            current_time = time.time()
            # Force cleanup of lights older than 5 seconds
            lighting_system.lights.remove_expired(current_time - 5.0, 'life_time', 'created_time')
        else:
            # Normal cleanup of expired lights
            current_time = time.time()
            lighting_system.lights.remove_expired(current_time, 'life_time', 'created_time')

        return initial_count - len(lighting_system.lights)

# Backward compatibility alias
MemoryManager = AdvancedMemoryManager

class AdaptiveFrameRateManager:
    """Dynamic frame rate management for optimal performance"""

    def __init__(self):
        self.target_fps = 30.0  # Target FPS for good performance
        self.min_fps = 15.0     # Minimum acceptable FPS
        self.max_fps = 60.0     # Maximum FPS to prevent excessive CPU usage

        # Current settings
        self.current_ui_interval = 50   # milliseconds (20 FPS)
        self.current_particle_interval = 16  # milliseconds (60 FPS)
        self.current_lighting_interval = 32  # milliseconds (30 FPS)

        # Performance tracking
        self.fps_history = []
        self.frame_time_history = []
        self.max_history = 30  # Keep 30 samples for averaging
        self.last_adjustment_time = time.time()
        self.adjustment_interval = 2.0  # seconds between adjustments

        # Quality scaling
        self.quality_level = 1.0  # 0.5 = half quality, 1.0 = full quality, 2.0 = high quality
        self.auto_quality_scaling = True

    def update_performance_metrics(self, fps, frame_time_ms):
        """Update performance tracking with current metrics"""
        self.fps_history.append(fps)
        self.frame_time_history.append(frame_time_ms)

        # Keep history within limits
        if len(self.fps_history) > self.max_history:
            self.fps_history.pop(0)
        if len(self.frame_time_history) > self.max_history:
            self.frame_time_history.pop(0)

    def get_average_fps(self):
        """Get average FPS from recent history"""
        if not self.fps_history:
            return self.target_fps
        return sum(self.fps_history) / len(self.fps_history)

    def get_average_frame_time(self):
        """Get average frame time from recent history"""
        if not self.frame_time_history:
            return 1000.0 / self.target_fps
        return sum(self.frame_time_history) / len(self.frame_time_history)

    def should_adjust_frame_rates(self):
        """Check if frame rates should be adjusted"""
        current_time = time.time()
        if (current_time - self.last_adjustment_time) < self.adjustment_interval:
            return False

        if len(self.fps_history) < 5:  # Need enough samples
            return False

        return True

    def adjust_frame_rates(self, ui_timer, particle_timer, lighting_timer):
        """Adjust frame rates based on performance"""
        if not self.should_adjust_frame_rates():
            return False

        avg_fps = self.get_average_fps()
        self.last_adjustment_time = time.time()

        # Determine performance level
        if avg_fps < self.min_fps:
            # Poor performance - reduce frame rates and quality
            performance_level = 'poor'
            self._adjust_for_poor_performance(ui_timer, particle_timer, lighting_timer)
        elif avg_fps < self.target_fps:
            # Below target - moderate adjustments
            performance_level = 'below_target'
            self._adjust_for_below_target(ui_timer, particle_timer, lighting_timer)
        elif avg_fps > self.max_fps:
            # Excessive FPS - can reduce to save CPU
            performance_level = 'excessive'
            self._adjust_for_excessive_fps(ui_timer, particle_timer, lighting_timer)
        else:
            # Good performance - can try to improve quality
            performance_level = 'good'
            self._adjust_for_good_performance(ui_timer, particle_timer, lighting_timer)

        logger.debug(f"🎯 Frame rate adjustment: {performance_level}, avg FPS: {avg_fps:.1f}")
        return True

    def _adjust_for_poor_performance(self, ui_timer, particle_timer, lighting_timer):
        """Aggressive adjustments for poor performance"""
        # Reduce UI update rate
        self.current_ui_interval = min(100, self.current_ui_interval + 10)  # Down to 10 FPS
        ui_timer.setInterval(self.current_ui_interval)

        # Reduce particle update rate
        self.current_particle_interval = min(50, self.current_particle_interval + 8)  # Down to 20 FPS
        particle_timer.setInterval(self.current_particle_interval)

        # Reduce lighting update rate
        self.current_lighting_interval = min(100, self.current_lighting_interval + 15)  # Down to 10 FPS
        lighting_timer.setInterval(self.current_lighting_interval)

        # Reduce quality
        if self.auto_quality_scaling:
            self.quality_level = max(0.5, self.quality_level - 0.1)

    def _adjust_for_below_target(self, ui_timer, particle_timer, lighting_timer):
        """Moderate adjustments for below-target performance"""
        # Slightly reduce update rates
        self.current_ui_interval = min(80, self.current_ui_interval + 5)  # Down to ~12 FPS
        ui_timer.setInterval(self.current_ui_interval)

        self.current_particle_interval = min(40, self.current_particle_interval + 4)  # Down to 25 FPS
        particle_timer.setInterval(self.current_particle_interval)

        # Slightly reduce quality
        if self.auto_quality_scaling:
            self.quality_level = max(0.7, self.quality_level - 0.05)

    def _adjust_for_excessive_fps(self, ui_timer, particle_timer, lighting_timer):
        """Adjustments for excessive FPS (save CPU)"""
        # Increase intervals to reduce CPU usage
        self.current_ui_interval = min(80, self.current_ui_interval + 5)
        ui_timer.setInterval(self.current_ui_interval)

        self.current_particle_interval = min(25, self.current_particle_interval + 2)
        particle_timer.setInterval(self.current_particle_interval)

    def _adjust_for_good_performance(self, ui_timer, particle_timer, lighting_timer):
        """Try to improve quality when performance is good"""
        # Can try to improve frame rates if not at maximum
        if self.current_ui_interval > 50:  # Not at 20 FPS yet
            self.current_ui_interval = max(50, self.current_ui_interval - 5)
            ui_timer.setInterval(self.current_ui_interval)

        if self.current_particle_interval > 16:  # Not at 60 FPS yet
            self.current_particle_interval = max(16, self.current_particle_interval - 2)
            particle_timer.setInterval(self.current_particle_interval)

        if self.current_lighting_interval > 32:  # Not at 30 FPS yet
            self.current_lighting_interval = max(32, self.current_lighting_interval - 5)
            lighting_timer.setInterval(self.current_lighting_interval)

        # Increase quality
        if self.auto_quality_scaling:
            self.quality_level = min(1.5, self.quality_level + 0.05)

    def get_current_intervals(self):
        """Get current timer intervals"""
        return {
            'ui': self.current_ui_interval,
            'particles': self.current_particle_interval,
            'lighting': self.current_lighting_interval,
            'quality': self.quality_level
        }

    def reset_to_defaults(self):
        """Reset all timers to default values"""
        self.current_ui_interval = 50
        self.current_particle_interval = 16
        self.current_lighting_interval = 32
        self.quality_level = 1.0
        self.fps_history.clear()
        self.frame_time_history.clear()

class QualityController:
    """Dynamic quality scaling system for real-time performance optimization"""

    def __init__(self):
        self.quality_presets = {
            'ultra_low': {
                'particle_quality': 0.7,  # Improved from 0.3 for better visibility
                'resolution_scale': 0.8,  # Improved from 0.5 for better clarity
                'post_processing': False,
                'bloom_enabled': False,
                'color_grading_enabled': False,
                'max_particles': 200,  # Improved from 100
                'update_interval_multiplier': 1.5  # Improved from 2.0
            },
            'low': {
                'particle_quality': 0.5,
                'resolution_scale': 0.7,
                'post_processing': True,
                'bloom_enabled': False,
                'color_grading_enabled': True,
                'max_particles': 300,
                'update_interval_multiplier': 1.5
            },
            'medium': {
                'particle_quality': 0.8,
                'resolution_scale': 0.85,
                'post_processing': True,
                'bloom_enabled': True,
                'color_grading_enabled': True,
                'max_particles': 500,
                'update_interval_multiplier': 1.0
            },
            'high': {
                'particle_quality': 1.0,
                'resolution_scale': 1.0,
                'post_processing': True,
                'bloom_enabled': True,
                'color_grading_enabled': True,
                'max_particles': 1000,
                'update_interval_multiplier': 1.0
            },
            'ultra': {
                'particle_quality': 1.5,
                'resolution_scale': 1.0,
                'post_processing': True,
                'bloom_enabled': True,
                'color_grading_enabled': True,
                'max_particles': 2000,
                'update_interval_multiplier': 0.8
            }
        }

        self.current_preset = 'medium'
        self.custom_settings = None
        self.auto_scaling = True
        self.performance_history = []

    def get_current_settings(self):
        """Get current quality settings"""
        if self.custom_settings:
            return self.custom_settings
        return self.quality_presets.get(self.current_preset, self.quality_presets['medium'])

    def set_preset(self, preset_name):
        """Set quality preset by name"""
        if preset_name in self.quality_presets:
            self.current_preset = preset_name
            self.custom_settings = None
            logger.info(f"🎨 Quality preset set to: {preset_name}")
            return True
        return False

    def set_custom_quality(self, **settings):
        """Set custom quality settings"""
        default_settings = self.quality_presets['medium'].copy()
        default_settings.update(settings)
        self.custom_settings = default_settings
        logger.info("🎨 Custom quality settings applied")

    def auto_adjust_quality(self, fps, target_fps=30.0, adjustment_factor=0.8):
        """Automatically adjust quality based on performance"""
        if not self.auto_scaling:
            return False

        self.performance_history.append(fps)
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)

        avg_fps = sum(self.performance_history) / len(self.performance_history)
        performance_ratio = avg_fps / target_fps

        # Determine quality adjustment
        if performance_ratio < 0.7:  # Poor performance
            if self.current_preset != 'ultra_low':
                presets = list(self.quality_presets.keys())
                current_index = presets.index(self.current_preset)
                if current_index > 0:
                    self.set_preset(presets[current_index - 1])
                    return True
        elif performance_ratio > 1.3:  # Excellent performance
            if self.current_preset != 'ultra':
                presets = list(self.quality_presets.keys())
                current_index = presets.index(self.current_preset)
                if current_index < len(presets) - 1:
                    self.set_preset(presets[current_index + 1])
                    return True

        return False

    def get_recommended_settings_for_fps(self, current_fps, target_fps=30.0):
        """Get recommended settings based on current FPS"""
        performance_ratio = current_fps / target_fps

        if performance_ratio < 0.5:
            return self.quality_presets['ultra_low']
        elif performance_ratio < 0.8:
            return self.quality_presets['low']
        elif performance_ratio < 1.2:
            return self.quality_presets['medium']
        elif performance_ratio < 1.8:
            return self.quality_presets['high']
        else:
            return self.quality_presets['ultra']

    def apply_settings_to_renderer(self, gl_widget):
        """Apply current quality settings to the OpenGL renderer"""
        settings = self.get_current_settings()

        # Apply particle quality
        if hasattr(gl_widget, 'set_particle_quality'):
            gl_widget.set_particle_quality(settings['particle_quality'])

        # Apply post-processing settings
        if hasattr(gl_widget, 'set_post_processing_quality'):
            gl_widget.set_post_processing_quality(
                enable_bloom=settings['bloom_enabled'],
                enable_color_grading=settings['color_grading_enabled']
            )

        # Log current quality level
        logger.debug(f"🎨 Applied quality settings: {self.current_preset}")

    def get_quality_info(self):
        """Get current quality information for display"""
        settings = self.get_current_settings()
        return {
            'preset': self.current_preset if not self.custom_settings else 'custom',
            'particle_quality': settings['particle_quality'],
            'resolution_scale': settings['resolution_scale'],
            'post_processing': settings['post_processing'],
            'auto_scaling': self.auto_scaling,
            'estimated_performance': self._estimate_performance_impact(settings)
        }

    def _estimate_performance_impact(self, settings):
        """Estimate relative performance impact of current settings"""
        base_score = 1.0
        base_score *= settings['particle_quality']
        base_score *= settings['resolution_scale']
        if settings['post_processing']:
            base_score *= 1.2
        if settings['bloom_enabled']:
            base_score *= 1.1
        return base_score

class AudioRingBuffer:
    """Non-blocking ring buffer for audio data"""

    def __init__(self, max_size_seconds=2.0, sample_rate=44100, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.max_size = int(max_size_seconds * sample_rate * channels)
        self.buffer = np.zeros(self.max_size, dtype=np.float32)
        self.write_index = 0
        self.read_index = 0
        self.size = 0
        self.lock = threading.Lock()
        self.stream = None
        self.is_running = False

    def _audio_callback(self, indata, frames, time, status):
        """Audio input callback (non-blocking)"""
        if status:
            logger.warning(f"Audio callback status: {status}")

        with self.lock:
            # Convert to flat array
            audio_data = indata[:, 0] if len(indata.shape) > 1 else indata
            frames_to_write = len(audio_data)

            # Write to ring buffer
            for i in range(frames_to_write):
                self.buffer[self.write_index] = audio_data[i]
                self.write_index = (self.write_index + 1) % self.max_size
                if self.size < self.max_size:
                    self.size += 1
                else:
                    # Buffer full, advance read index
                    self.read_index = (self.read_index + 1) % self.max_size

    def start_input(self, device=None):
        """Start non-blocking audio input"""
        try:
            if HAS_SOUNDDEVICE:
                self.stream = sd.InputStream(
                    device=device,
                    channels=self.channels,
                    samplerate=self.sample_rate,
                    callback=self._audio_callback,
                    blocksize=512,  # Small block size for low latency
                    dtype=np.float32
                )
                self.stream.start()
                self.is_running = True
                logger.info(f"🎤 Non-blocking audio input started: {self.sample_rate}Hz")
                return True
        except Exception as e:
            logger.error(f"Failed to start audio input: {e}")
            return False

    def stop(self):
        """Stop audio input"""
        self.is_running = False
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
                self.stream = None
                logger.info("🎤 Audio input stopped")
            except Exception as e:
                logger.error(f"Error stopping audio input: {e}")

    def read_frames(self, frame_count):
        """Read frames from ring buffer (non-blocking)"""
        with self.lock:
            if self.size < frame_count:
                # Not enough data available
                return None

            # Read from ring buffer
            frames = np.zeros(frame_count, dtype=np.float32)
            for i in range(frame_count):
                frames[i] = self.buffer[self.read_index]
                self.read_index = (self.read_index + 1) % self.max_size
                self.size -= 1

            return frames

    def get_latest_frames(self, frame_count):
        """Get the most recent frames without removing them from buffer"""
        with self.lock:
            if self.size < frame_count:
                return None

            # Get latest frames without advancing read pointer
            frames = np.zeros(frame_count, dtype=np.float32)
            latest_index = (self.write_index - 1) % self.max_size

            for i in range(frame_count):
                idx = (latest_index - frame_count + 1 + i) % self.max_size
                frames[i] = self.buffer[idx]

            return frames

    def get_buffer_level(self):
        """Get current buffer level as percentage"""
        with self.lock:
            return (self.size / self.max_size) * 100.0

class ShaderManager:
    """Modern OpenGL shader management system"""

    def __init__(self):
        self.shaders = {}
        self.programs = {}

    def create_shader(self, shader_type, source):
        """Create and compile a shader"""
        try:
            from OpenGL.GL import shaders

            shader = shaders.compileShader(source, shader_type)
            return shader
        except Exception as e:
            logger.error(f"Shader compilation failed: {e}")
            return None

    def create_program(self, name, vertex_source, fragment_source):
        """Create a shader program from vertex and fragment shaders"""
        try:
            from OpenGL.GL import shaders
            from OpenGL.GL import GL_VERTEX_SHADER, GL_FRAGMENT_SHADER

            vertex_shader = self.create_shader(GL_VERTEX_SHADER, vertex_source)
            fragment_shader = self.create_shader(GL_FRAGMENT_SHADER, fragment_source)

            if vertex_shader and fragment_shader:
                program = shaders.compileProgram(vertex_shader, fragment_shader)
                self.programs[name] = program
                logger.info(f"✅ Shader program '{name}' compiled successfully")
                return program
            else:
                logger.error(f"Failed to create shaders for program '{name}'")
                return None

        except Exception as e:
            logger.error(f"Shader program creation failed for '{name}': {e}")
            return None

    def use_program(self, name):
        """Use a shader program"""
        if name in self.programs:
            from OpenGL.GL import glUseProgram
            glUseProgram(self.programs[name])
            return self.programs[name]
        return None

    def get_uniform_location(self, program_name, uniform_name):
        """Get uniform location in shader program"""
        if program_name in self.programs:
            from OpenGL.GL import glGetUniformLocation
            return glGetUniformLocation(self.programs[program_name], uniform_name)
        return -1

    def set_uniform_matrix4fv(self, location, matrix):
        """Set a 4x4 matrix uniform"""
        if location >= 0:
            from OpenGL.GL import glUniformMatrix4fv, GL_FALSE
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix)

    def set_uniform_3f(self, location, x, y, z):
        """Set a 3-component float uniform"""
        if location >= 0:
            from OpenGL.GL import glUniform3f
            glUniform3f(location, x, y, z)

    def set_uniform_1f(self, location, value):
        """Set a float uniform"""
        if location >= 0:
            from OpenGL.GL import glUniform1f
            glUniform1f(location, value)

class ModernRenderer:
    """Modern OpenGL rendering system with shaders and VBOs"""

    def __init__(self):
        self.shader_manager = ShaderManager()
        self.vbos = {}
        self.vaos = {}
        self.modern_gl_available = False
        self.fallback_to_legacy = False

        # Shader sources
        self.vertex_shaders = {
            'basic': """
                #version 330 core
                layout (location = 0) in vec3 aPos;
                layout (location = 1) in vec3 aNormal;
                layout (location = 2) in vec3 aColor;

                uniform mat4 model;
                uniform mat4 view;
                uniform mat4 projection;
                uniform mat3 normalMatrix;

                out vec3 FragPos;
                out vec3 Normal;
                out vec3 Color;

                void main() {
                    FragPos = vec3(model * vec4(aPos, 1.0));
                    Normal = normalMatrix * aNormal;
                    Color = aColor;

                    gl_Position = projection * view * vec4(FragPos, 1.0);
                }
            """,

            'particle': """
                #version 330 core
                layout (location = 0) in vec3 aPos;
                layout (location = 1) in vec4 aColor;
                layout (location = 2) in float aSize;

                uniform mat4 view;
                uniform mat4 projection;

                out vec4 Color;

                void main() {
                    gl_Position = projection * view * vec4(aPos, 1.0);
                    gl_PointSize = aSize;
                    Color = aColor;
                }
            """
        }

        self.fragment_shaders = {
            'pbr': """
                #version 330 core
                out vec4 FragColor;

                in vec3 FragPos;
                in vec3 Normal;
                in vec3 Color;

                struct Light {
                    vec3 position;
                    vec3 color;
                    float intensity;
                };

                uniform Light lights[8];
                uniform int numLights;
                uniform vec3 viewPos;
                uniform float metallic;
                uniform float roughness;
                uniform float ao;

                vec3 calculatePBR(Light light, vec3 normal, vec3 viewDir, vec3 fragPos, vec3 albedo) {
                    vec3 lightColor = light.color * light.intensity;
                    vec3 lightDir = normalize(light.position - fragPos);

                    // Calculate distance and attenuation
                    float distance = length(light.position - fragPos);
                    float attenuation = 1.0 / (1.0 + 0.09 * distance + 0.032 * distance * distance);
                    lightColor *= attenuation;

                    // Cook-Torrance BRDF
                    vec3 halfwayDir = normalize(lightDir + viewDir);

                    float NdotV = max(dot(normal, viewDir), 0.0);
                    float NdotL = max(dot(normal, lightDir), 0.0);
                    float HdotV = max(dot(halfwayDir, viewDir), 0.0);
                    float NdotH = max(dot(normal, halfwayDir), 0.0);

                    // Fresnel reflectance
                    vec3 F0 = mix(vec3(0.04), albedo, metallic);
                    vec3 F = F0 + (1.0 - F0) * pow(clamp(1.0 - HdotV, 0.0, 1.0), 5.0);

                    // Normal distribution (GGX/Trowbridge-Reitz)
                    float alpha = roughness * roughness;
                    float alpha2 = alpha * alpha;
                    float denom = NdotH * NdotH * (alpha2 - 1.0) + 1.0;
                    float D = alpha2 / (3.14159265 * denom * denom);

                    // Geometric shadowing
                    float k = (roughness + 1.0) * (roughness + 1.0) / 8.0;
                    float G_L = NdotL / (NdotL * (1.0 - k) + k);
                    float G_V = NdotV / (NdotV * (1.0 - k) + k);
                    float G = G_L * G_V;

                    // BRDF
                    vec3 numerator = D * G * F;
                    float denominator = 4.0 * NdotV * NdotL + 0.0001;
                    vec3 specular = numerator / denominator;

                    // Energy conservation
                    vec3 kS = F;
                    vec3 kD = vec3(1.0) - kS;
                    kD *= 1.0 - metallic;

                    // Add to outgoing radiance
                    return (kD * albedo / 3.14159265 + specular) * lightColor * NdotL;
                }

                void main() {
                    vec3 norm = normalize(Normal);
                    vec3 viewDir = normalize(viewPos - FragPos);
                    vec3 albedo = pow(Color, vec3(2.2)); // Convert to linear space

                    vec3 result = vec3(0.0);

                    // Ambient lighting (IBL approximation)
                    vec3 ambient = 0.03 * albedo * ao;
                    result += ambient;

                    // Calculate lighting for each light
                    for(int i = 0; i < numLights && i < 8; i++) {
                        result += calculatePBR(lights[i], norm, viewDir, FragPos, albedo);
                    }

                    // HDR tone mapping (ACES approximation)
                    result = (result * (2.51 * result + 0.03)) / (result * (2.43 * result + 0.59) + 0.14);

                    // Gamma correction
                    result = pow(result, vec3(1.0/2.2));

                    FragColor = vec4(result, 1.0);
                }
            """,

            'particle': """
                #version 330 core
                out vec4 FragColor;

                in vec4 Color;

                void main() {
                    // Create circular particle shape
                    vec2 coord = gl_PointCoord - vec2(0.5);
                    float distance = length(coord);

                    if(distance > 0.5)
                        discard;

                    // Smooth edge falloff
                    float alpha = 1.0 - smoothstep(0.3, 0.5, distance);

                    FragColor = vec4(Color.rgb, Color.a * alpha);
                }
            """
        }

    def initialize(self):
        """Initialize modern OpenGL rendering"""
        try:
            # Check if modern OpenGL is available
            from OpenGL.GL import glGenVertexArrays, glGenBuffers
            from OpenGL.GL import GL_VERSION
            import OpenGL.GL as gl

            version = gl.glGetString(GL_VERSION).decode()
            logger.info(f"OpenGL Version: {version}")

            # Try to create a VAO to test modern OpenGL support
            test_vao = glGenVertexArrays(1)
            if test_vao:
                self.modern_gl_available = True
                logger.info("✅ Modern OpenGL (3.3+) available")

                # Compile shader programs
                self._compile_shaders()
                return True
            else:
                raise Exception("VAO creation failed")

        except Exception as e:
            logger.warning(f"⚠️ Modern OpenGL not available, falling back to legacy: {e}")
            self.fallback_to_legacy = True
            return False

    def _compile_shaders(self):
        """Compile all shader programs"""
        # Basic PBR shader
        self.shader_manager.create_program(
            'pbr_basic',
            self.vertex_shaders['basic'],
            self.fragment_shaders['pbr']
        )

        # Particle shader
        self.shader_manager.create_program(
            'particle',
            self.vertex_shaders['particle'],
            self.fragment_shaders['particle']
        )

    def create_mesh_vbo(self, name, vertices, normals=None, colors=None, indices=None):
        """Create VBO for mesh data"""
        if not self.modern_gl_available:
            return None

        try:
            from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray
            from OpenGL.GL import glBindBuffer, glBufferData, glEnableVertexAttribArray
            from OpenGL.GL import glVertexAttribPointer, GL_ARRAY_BUFFER, GL_STATIC_DRAW
            from OpenGL.GL import GL_FLOAT, GL_FALSE
            import numpy as np

            # Generate VAO and VBO
            vao = glGenVertexArrays(1)
            vbo = glGenBuffers(1)

            glBindVertexArray(vao)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)

            # Prepare vertex data
            vertex_data = []

            # Add positions
            for vertex in vertices:
                vertex_data.extend(vertex)

            # Add normals (or generate if not provided)
            if normals is None:
                normals = self._generate_normals(vertices)
            for normal in normals:
                vertex_data.extend(normal)

            # Add colors (or default if not provided)
            if colors is None:
                colors = [[1.0, 1.0, 1.0] for _ in vertices]
            for color in colors:
                vertex_data.extend(color)

            # Upload data
            vertex_array = np.array(vertex_data, dtype=np.float32)
            glBufferData(GL_ARRAY_BUFFER, vertex_array.nbytes, vertex_array, GL_STATIC_DRAW)

            # Set vertex attributes
            stride = 9 * 4  # 3 pos + 3 normal + 3 color, 4 bytes per float

            # Position attribute
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, None)
            glEnableVertexAttribArray(0)

            # Normal attribute
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
            glEnableVertexAttribArray(1)

            # Color attribute
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))
            glEnableVertexAttribArray(2)

            # Store VAO and vertex count
            self.vaos[name] = {
                'vao': vao,
                'vbo': vbo,
                'count': len(vertices)
            }

            logger.debug(f"Created VBO for '{name}' with {len(vertices)} vertices")
            return vao

        except Exception as e:
            logger.error(f"Failed to create VBO for '{name}': {e}")
            return None

    def _generate_normals(self, vertices):
        """Generate simple normals for vertices"""
        import numpy as np
        normals = []

        # Simple approach: use vertex position as normal (for spherical objects)
        for vertex in vertices:
            normal = np.array(vertex)
            length = np.linalg.norm(normal)
            if length > 0:
                normal = normal / length
            else:
                normal = np.array([0.0, 0.0, 1.0])
            normals.append(normal.tolist())

        return normals

    def render_mesh(self, name, model_matrix, view_matrix, projection_matrix, lights=None):
        """Render a mesh using modern OpenGL"""
        if not self.modern_gl_available or name not in self.vaos:
            return False

        try:
            from OpenGL.GL import glBindVertexArray, glDrawArrays, GL_TRIANGLES
            import numpy as np

            # Use PBR shader
            program = self.shader_manager.use_program('pbr_basic')
            if not program:
                return False

            # Set matrices
            model_loc = self.shader_manager.get_uniform_location('pbr_basic', 'model')
            view_loc = self.shader_manager.get_uniform_location('pbr_basic', 'view')
            proj_loc = self.shader_manager.get_uniform_location('pbr_basic', 'projection')

            self.shader_manager.set_uniform_matrix4fv(model_loc, model_matrix)
            self.shader_manager.set_uniform_matrix4fv(view_loc, view_matrix)
            self.shader_manager.set_uniform_matrix4fv(proj_loc, projection_matrix)

            # Set view position for PBR calculations
            view_pos_loc = self.shader_manager.get_uniform_location('pbr_basic', 'viewPos')
            self.shader_manager.set_uniform_3f(view_pos_loc, 0.0, 0.0, 5.0)  # Camera position

            # Set material properties (could be made dynamic based on audio)
            metallic_loc = self.shader_manager.get_uniform_location('pbr_basic', 'metallic')
            roughness_loc = self.shader_manager.get_uniform_location('pbr_basic', 'roughness')
            ao_loc = self.shader_manager.get_uniform_location('pbr_basic', 'ao')

            self.shader_manager.set_uniform_1f(metallic_loc, 0.2)  # Slightly metallic
            self.shader_manager.set_uniform_1f(roughness_loc, 0.4)  # Medium roughness
            self.shader_manager.set_uniform_1f(ao_loc, 1.0)

            # Set lights (simplified for now)
            if lights:
                num_lights = min(len(lights), 8)
                num_lights_loc = self.shader_manager.get_uniform_location('pbr_basic', 'numLights')
                from OpenGL.GL import glUniform1i
                glUniform1i(num_lights_loc, num_lights)

                for i, light in enumerate(lights[:8]):
                    pos_loc = self.shader_manager.get_uniform_location('pbr_basic', f'lights[{i}].position')
                    color_loc = self.shader_manager.get_uniform_location('pbr_basic', f'lights[{i}].color')
                    intensity_loc = self.shader_manager.get_uniform_location('pbr_basic', f'lights[{i}].intensity')

                    pos = light.position if hasattr(light, 'position') else [0, 0, 5]
                    color = light.color[:3] if hasattr(light, 'color') else [1, 1, 1]
                    intensity = light.intensity if hasattr(light, 'intensity') else 1.0

                    self.shader_manager.set_uniform_3f(pos_loc, pos[0], pos[1], pos[2])
                    self.shader_manager.set_uniform_3f(color_loc, color[0], color[1], color[2])
                    self.shader_manager.set_uniform_1f(intensity_loc, intensity)

            # Render
            vao_data = self.vaos[name]
            glBindVertexArray(vao_data['vao'])
            glDrawArrays(GL_TRIANGLES, 0, vao_data['count'])

            return True

        except Exception as e:
            logger.error(f"Failed to render mesh '{name}': {e}")
            return False

class PostProcessingManager:
    """Legacy-compatible post-processing effects system"""

    def __init__(self):
        self.bloom_enabled = True
        self.bloom_intensity = 0.3
        self.bloom_threshold = 0.7
        self.color_grading_enabled = True
        self.contrast = 1.2
        self.brightness = 0.1
        self.saturation = 1.1
        self.vignette_enabled = True
        self.vignette_strength = 0.3

        # Frame buffer for multi-pass rendering
        self.previous_frame = None
        self.bloom_buffer = None
        self.use_post_processing = True

    def initialize(self, width, height):
        """Initialize post-processing buffers"""
        try:
            import numpy as np

            # Create frame buffers for post-processing
            self.frame_width = width
            self.frame_height = height

            # RGB frame buffer
            self.previous_frame = np.zeros((height, width, 3), dtype=np.float32)
            self.bloom_buffer = np.zeros((height, width, 3), dtype=np.float32)

            logger.info(f"✅ Post-processing initialized for {width}x{height}")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize post-processing: {e}")
            self.use_post_processing = False
            return False

    def capture_frame(self):
        """Capture current frame for post-processing"""
        if not self.use_post_processing:
            return None

        try:
            from OpenGL.GL import glReadPixels, GL_RGB, GL_FLOAT
            import numpy as np

            # Read pixels from framebuffer
            pixels = glReadPixels(0, 0, self.frame_width, self.frame_height, GL_RGB, GL_FLOAT)
            frame = np.frombuffer(pixels, dtype=np.float32)
            frame = frame.reshape((self.frame_height, self.frame_width, 3))

            # Flip vertically (OpenGL coordinates)
            frame = np.flipud(frame)

            return frame

        except Exception as e:
            logger.debug(f"Frame capture failed: {e}")
            return None

    def apply_bloom(self, frame):
        """Apply bloom effect using CPU processing"""
        if not self.bloom_enabled or frame is None:
            return frame

        try:
            import numpy as np
            from scipy import ndimage

            # Extract bright areas (threshold)
            bright_mask = np.mean(frame, axis=2) > self.bloom_threshold
            bloom_source = frame.copy()
            bloom_source[~bright_mask] = 0

            # Gaussian blur for bloom effect
            for channel in range(3):
                bloom_source[:, :, channel] = ndimage.gaussian_filter(
                    bloom_source[:, :, channel], sigma=8.0
                )

            # Combine with original
            result = frame + bloom_source * self.bloom_intensity
            return np.clip(result, 0.0, 1.0)

        except ImportError:
            # Fallback without scipy
            return self._simple_bloom(frame)
        except Exception as e:
            logger.debug(f"Bloom effect failed: {e}")
            return frame

    def _simple_bloom(self, frame):
        """Simple bloom without scipy"""
        import numpy as np

        # Simple box blur approximation
        kernel_size = 15
        half_kernel = kernel_size // 2

        # Extract bright areas
        bright_mask = np.mean(frame, axis=2) > self.bloom_threshold
        bloom_source = frame.copy()
        bloom_source[~bright_mask] = 0

        # Simple averaging for blur effect
        h, w, c = frame.shape
        blurred = np.zeros_like(bloom_source)

        for y in range(half_kernel, h - half_kernel):
            for x in range(half_kernel, w - half_kernel):
                region = bloom_source[y-half_kernel:y+half_kernel+1,
                                    x-half_kernel:x+half_kernel+1]
                blurred[y, x] = np.mean(region, axis=(0, 1))

        # Combine with original
        result = frame + blurred * self.bloom_intensity
        return np.clip(result, 0.0, 1.0)

    def apply_color_grading(self, frame):
        """Apply color grading effects"""
        if not self.color_grading_enabled or frame is None:
            return frame

        try:
            import numpy as np

            result = frame.copy()

            # Brightness adjustment
            result = result + self.brightness

            # Contrast adjustment
            result = (result - 0.5) * self.contrast + 0.5

            # Saturation adjustment
            if self.saturation != 1.0:
                # Convert to grayscale for desaturation
                gray = np.mean(result, axis=2, keepdims=True)
                result = gray + (result - gray) * self.saturation

            return np.clip(result, 0.0, 1.0)

        except Exception as e:
            logger.debug(f"Color grading failed: {e}")
            return frame

    def apply_vignette(self, frame):
        """Apply vignette effect"""
        if not self.vignette_enabled or frame is None:
            return frame

        try:
            import numpy as np

            h, w = frame.shape[:2]

            # Create vignette mask
            y, x = np.ogrid[:h, :w]
            center_y, center_x = h // 2, w // 2

            # Distance from center
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_distance = np.sqrt(center_x**2 + center_y**2)

            # Normalize distance
            normalized_distance = distance / max_distance

            # Create vignette
            vignette = 1.0 - (normalized_distance * self.vignette_strength)
            vignette = np.clip(vignette, 0.0, 1.0)

            # Apply to frame
            result = frame * vignette[:, :, np.newaxis]
            return result

        except Exception as e:
            logger.debug(f"Vignette effect failed: {e}")
            return frame

    def process_frame(self, frame):
        """Apply all post-processing effects"""
        if frame is None:
            return None

        result = frame

        # Apply effects in order
        result = self.apply_bloom(result)
        result = self.apply_color_grading(result)
        result = self.apply_vignette(result)

        return result

    def display_processed_frame(self, frame):
        """Display processed frame back to OpenGL"""
        if frame is None:
            return

        try:
            from OpenGL.GL import glDrawPixels, GL_RGB, GL_FLOAT
            import numpy as np

            # Flip frame back for OpenGL
            flipped_frame = np.flipud(frame)

            # Convert to proper format
            frame_data = flipped_frame.astype(np.float32)

            # Draw pixels to screen
            glDrawPixels(self.frame_width, self.frame_height, GL_RGB, GL_FLOAT, frame_data)

        except Exception as e:
            logger.debug(f"Frame display failed: {e}")

    def adjust_bloom(self, intensity, threshold):
        """Adjust bloom parameters"""
        self.bloom_intensity = max(0.0, min(1.0, intensity))
        self.bloom_threshold = max(0.0, min(1.0, threshold))

    def adjust_color_grading(self, brightness, contrast, saturation):
        """Adjust color grading parameters"""
        self.brightness = max(-0.5, min(0.5, brightness))
        self.contrast = max(0.1, min(3.0, contrast))
        self.saturation = max(0.0, min(2.0, saturation))

    def toggle_effect(self, effect_name, enabled):
        """Toggle specific effects on/off"""
        if effect_name == "bloom":
            self.bloom_enabled = enabled
        elif effect_name == "color_grading":
            self.color_grading_enabled = enabled
        elif effect_name == "vignette":
            self.vignette_enabled = enabled

class OptimizedParticleRenderer:
    """Optimized particle rendering system for legacy OpenGL"""

    def __init__(self):
        self.particle_batches = {}
        self.texture_id = None
        self.use_textures = True
        self.batch_size = 1000
        self.quality_level = 1.0  # 0.5 = half particles, 2.0 = double particles

        # Pre-allocated arrays for batching
        self.positions = []
        self.colors = []
        self.sizes = []

    def initialize(self):
        """Initialize particle rendering resources"""
        try:
            if self.use_textures:
                self._create_particle_texture()

            logger.info("✅ Optimized particle renderer initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize particle renderer: {e}")
            return False

    def _create_particle_texture(self):
        """Create a simple particle texture"""
        try:
            from OpenGL.GL import glGenTextures, glBindTexture, glTexImage2D
            from OpenGL.GL import GL_TEXTURE_2D, GL_RGBA, GL_UNSIGNED_BYTE
            from OpenGL.GL import glTexParameteri, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER
            from OpenGL.GL import GL_LINEAR
            import numpy as np

            # Create simple circular particle texture
            size = 32
            texture_data = np.zeros((size, size, 4), dtype=np.uint8)

            center = size // 2
            for y in range(size):
                for x in range(size):
                    # Distance from center
                    dx = x - center
                    dy = y - center
                    distance = np.sqrt(dx*dx + dy*dy)
                    normalized_distance = distance / center

                    if normalized_distance <= 1.0:
                        # Smooth circular falloff
                        alpha = int(255 * (1.0 - normalized_distance) ** 2)
                        texture_data[y, x] = [255, 255, 255, alpha]

            # Upload texture to OpenGL
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, size, size, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            logger.debug("✅ Particle texture created")

        except Exception as e:
            logger.warning(f"Failed to create particle texture: {e}")
            self.use_textures = False

    def batch_particles(self, particles):
        """Batch particles by type for efficient rendering"""
        batches = {}

        # Apply quality scaling
        particle_count = max(1, int(len(particles) * self.quality_level))
        particles_to_render = particles[:particle_count]

        for particle in particles_to_render:
            particle_type = particle.particle_type if hasattr(particle, 'particle_type') else 'default'

            if particle_type not in batches:
                batches[particle_type] = {
                    'positions': [],
                    'colors': [],
                    'sizes': []
                }

            # Add particle data to batch
            batches[particle_type]['positions'].append(particle.position)
            batches[particle_type]['colors'].append(particle.color)
            batches[particle_type]['sizes'].append(particle.size)

        return batches

    def render_particles(self, particles):
        """Render particles using optimized batching"""
        if not particles:
            return

        try:
            from OpenGL.GL import glEnable, glDisable, glBlendFunc
            from OpenGL.GL import GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
            from OpenGL.GL import GL_TEXTURE_2D, glBindTexture
            from OpenGL.GL import glBegin, glEnd, GL_QUADS
            from OpenGL.GL import glColor4f, glTexCoord2f, glVertex3f
            import numpy as np

            # Enable blending for transparency
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            if self.use_textures and self.texture_id:
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, self.texture_id)

            # Batch particles by type
            batches = self.batch_particles(particles)

            # Render each batch
            for particle_type, batch_data in batches.items():
                positions = batch_data['positions']
                colors = batch_data['colors']
                sizes = batch_data['sizes']

                # Render particles as textured quads
                if self.use_textures:
                    self._render_textured_particles(positions, colors, sizes)
                else:
                    self._render_point_particles(positions, colors, sizes)

            if self.use_textures:
                glDisable(GL_TEXTURE_2D)

            glDisable(GL_BLEND)

        except Exception as e:
            logger.debug(f"Particle rendering failed: {e}")

    def _render_textured_particles(self, positions, colors, sizes):
        """Render particles as textured quads"""
        from OpenGL.GL import glBegin, glEnd, GL_QUADS
        from OpenGL.GL import glColor4f, glTexCoord2f, glVertex3f

        glBegin(GL_QUADS)

        for i, position in enumerate(positions):
            if i >= len(colors) or i >= len(sizes):
                break

            color = colors[i]
            size = sizes[i] * 0.5  # Scale down for quad rendering

            # Set particle color
            glColor4f(color[0], color[1], color[2], color[3] if len(color) > 3 else 1.0)

            # Create billboard quad facing camera
            x, y, z = position[0], position[1], position[2]

            # Quad vertices with texture coordinates
            glTexCoord2f(0.0, 0.0)
            glVertex3f(x - size, y - size, z)

            glTexCoord2f(1.0, 0.0)
            glVertex3f(x + size, y - size, z)

            glTexCoord2f(1.0, 1.0)
            glVertex3f(x + size, y + size, z)

            glTexCoord2f(0.0, 1.0)
            glVertex3f(x - size, y + size, z)

        glEnd()

    def _render_point_particles(self, positions, colors, sizes):
        """Fallback: render particles as point sprites"""
        from OpenGL.GL import glBegin, glEnd, GL_POINTS
        from OpenGL.GL import glColor4f, glVertex3f, glPointSize

        for i, position in enumerate(positions):
            if i >= len(colors) or i >= len(sizes):
                break

            color = colors[i]
            size = sizes[i]

            # Set point size
            glPointSize(max(5.0, size * 10.0))  # Much larger point size

            glBegin(GL_POINTS)
            glColor4f(color[0], color[1], color[2], color[3] if len(color) > 3 else 1.0)
            glVertex3f(position[0], position[1], position[2])
            glEnd()

    def set_quality_level(self, quality):
        """Set particle quality level (0.1 to 2.0)"""
        self.quality_level = max(0.1, min(2.0, quality))

    def get_particle_count_for_quality(self, base_count):
        """Get actual particle count based on quality level"""
        return max(1, int(base_count * self.quality_level))

# Data Classes
@dataclass(eq=False)
class AudioFeatures:
    """Advanced audio analysis features with psychoacoustic modeling"""

    def __eq__(self, other):
        if not isinstance(other, AudioFeatures):
            return NotImplemented
        return (self.amplitude == other.amplitude and
                self.pitch == other.pitch and
                self.spectral_centroid == other.spectral_centroid)

    # Basic features
    amplitude: float = 0.0
    pitch: float = 440.0
    fundamental_frequency: float = 440.0
    confidence: float = 0.0

    # Spectral features
    spectral_centroid: float = 0.0
    spectral_rolloff: float = 0.0
    spectral_bandwidth: float = 0.0
    spectral_flux: float = 0.0
    spectral_spread: float = 0.0
    spectral_skewness: float = 0.0
    spectral_kurtosis: float = 0.0
    spectral_slope: float = 0.0

    # Advanced spectral analysis
    spectral_envelope: Optional[np.ndarray] = None
    harmonic_energy: float = 0.0
    noise_energy: float = 0.0
    harmonicity: float = 0.0
    inharmonicity: float = 0.0

    # Formant analysis
    formants: Optional[np.ndarray] = None  # F1, F2, F3, F4
    formant_bandwidths: Optional[np.ndarray] = None
    vocal_tract_length: float = 0.0

    # Psychoacoustic features
    loudness_sones: float = 0.0
    sharpness_acum: float = 0.0
    roughness_asper: float = 0.0
    fluctuation_strength: float = 0.0
    critical_band_energies: Optional[np.ndarray] = None
    bark_spectrum: Optional[np.ndarray] = None

    # Temporal features
    zero_crossing_rate: float = 0.0
    onset_detected: bool = False
    beat_detected: bool = False
    tempo: float = 120.0
    rhythm_strength: float = 0.0
    pulse_clarity: float = 0.0

    # Machine learning features
    mfcc: Optional[np.ndarray] = None
    mel_spectrogram: Optional[np.ndarray] = None
    chroma: Optional[np.ndarray] = None
    tonnetz: Optional[np.ndarray] = None
    spectral_contrast: Optional[np.ndarray] = None

    # Energy and dynamics
    rms_energy: float = 0.0
    peak_energy: float = 0.0
    crest_factor: float = 0.0
    dynamic_range: float = 0.0

    # Musical features
    key_signature: str = "C"
    mode: str = "major"  # major, minor, dorian, etc.
    chord_progression: Optional[List[str]] = None
    tension: float = 0.0
    consonance: float = 0.0

class PsychoacousticAnalyzer:
    """Advanced psychoacoustic analysis engine for perceptual audio features"""

    def __init__(self, sample_rate=44100, frame_size=4096):
        self.sr = sample_rate
        self.frame_size = frame_size
        self.nyquist = sample_rate / 2

        # Bark scale critical bands (24 bands)
        self.bark_bands = self._create_bark_bands()
        self.mel_filters = self._create_mel_filterbank()

        # Psychoacoustic model parameters
        self.absolute_threshold = self._create_absolute_threshold()
        self.masking_threshold = np.zeros(self.frame_size // 2 + 1)

        # Formant detection parameters
        self.formant_tracker = FormantTracker()

        # Harmonic analysis
        self.harmonic_analyzer = HarmonicAnalyzer()

    def _create_bark_bands(self):
        """Create Bark scale frequency bands"""
        # Bark scale: critical band boundaries
        bark_edges = [0, 100, 200, 300, 400, 510, 630, 770, 920, 1080, 1270,
                     1480, 1720, 2000, 2320, 2700, 3150, 3700, 4400, 5300,
                     6400, 7700, 9500, 12000, 15500, self.nyquist]

        bands = []
        freqs = np.fft.rfftfreq(self.frame_size, 1/self.sr)

        for i in range(len(bark_edges) - 1):
            low_freq = bark_edges[i]
            high_freq = bark_edges[i + 1]

            # Find frequency bin indices
            low_bin = np.argmin(np.abs(freqs - low_freq))
            high_bin = np.argmin(np.abs(freqs - high_freq))

            bands.append((low_bin, high_bin))

        return bands

    def _create_mel_filterbank(self, n_mels=128):
        """Create mel-scale filterbank"""
        # Convert to mel scale
        mel_low = 2595 * np.log10(1 + 80 / 700)  # 80 Hz low end
        mel_high = 2595 * np.log10(1 + self.nyquist / 700)

        # Create mel points
        mel_points = np.linspace(mel_low, mel_high, n_mels + 2)
        hz_points = 700 * (10**(mel_points / 2595) - 1)

        # Convert to FFT bin numbers
        freqs = np.fft.rfftfreq(self.frame_size, 1/self.sr)
        bin_points = np.floor((self.frame_size + 1) * hz_points / self.sr).astype(int)

        # Create filterbank
        filters = np.zeros((n_mels, len(freqs)))
        for i in range(1, n_mels + 1):
            left = bin_points[i - 1]
            center = bin_points[i]
            right = bin_points[i + 1]

            # Left slope
            for j in range(left, center):
                filters[i - 1, j] = (j - left) / (center - left)

            # Right slope
            for j in range(center, right):
                filters[i - 1, j] = (right - j) / (right - center)

        return filters

    def _create_absolute_threshold(self):
        """Create absolute threshold of hearing"""
        freqs = np.fft.rfftfreq(self.frame_size, 1/self.sr)
        freqs = np.maximum(freqs, 1.0)  # Avoid division by zero

        # Absolute threshold in quiet (dB SPL)
        threshold = (3.64 * (freqs / 1000) ** -0.8 -
                    6.5 * np.exp(-0.6 * (freqs / 1000 - 3.3) ** 2) +
                    1e-3 * (freqs / 1000) ** 4)

        # Convert from dB SPL to magnitude
        return 10 ** (threshold / 20)

    def analyze_psychoacoustic_features(self, audio_data, features):
        """Comprehensive psychoacoustic analysis"""
        if len(audio_data) < self.frame_size:
            return features

        # FFT analysis
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        power = magnitude ** 2
        freqs = np.fft.rfftfreq(len(audio_data), 1/self.sr)

        # Critical band analysis
        features.critical_band_energies = self._compute_critical_band_energies(power)
        features.bark_spectrum = self._compute_bark_spectrum(power)

        # Psychoacoustic metrics
        features.loudness_sones = self._compute_loudness(power)
        features.sharpness_acum = self._compute_sharpness(power)
        features.roughness_asper = self._compute_roughness(power)

        # Advanced spectral features
        features.spectral_spread = self._compute_spectral_spread(power, freqs)
        features.spectral_skewness = self._compute_spectral_skewness(power, freqs)
        features.spectral_kurtosis = self._compute_spectral_kurtosis(power, freqs)
        features.spectral_slope = self._compute_spectral_slope(power, freqs)

        # Harmonic analysis
        harmonics = self.harmonic_analyzer.analyze(audio_data, self.sr)
        features.harmonic_energy = harmonics['harmonic_energy']
        features.noise_energy = harmonics['noise_energy']
        features.harmonicity = harmonics['harmonicity']
        features.inharmonicity = harmonics['inharmonicity']

        # Formant analysis
        if len(audio_data) >= 1024:  # Need sufficient data for formants
            formant_data = self.formant_tracker.detect_formants(audio_data, self.sr)
            features.formants = formant_data['frequencies']
            features.formant_bandwidths = formant_data['bandwidths']
            features.vocal_tract_length = formant_data['vocal_tract_length']

        return features

    def _compute_critical_band_energies(self, power_spectrum):
        """Compute energy in critical bands"""
        band_energies = np.zeros(len(self.bark_bands))

        for i, (low_bin, high_bin) in enumerate(self.bark_bands):
            if high_bin < len(power_spectrum):
                band_energies[i] = np.sum(power_spectrum[low_bin:high_bin])

        return band_energies

    def _compute_bark_spectrum(self, power_spectrum):
        """Compute Bark-scale spectrum"""
        band_energies = self._compute_critical_band_energies(power_spectrum)
        # Convert to dB
        bark_spectrum = 10 * np.log10(np.maximum(band_energies, 1e-10))
        return bark_spectrum

    def _compute_loudness(self, power_spectrum):
        """Compute loudness in sones using Zwicker's model"""
        band_energies = self._compute_critical_band_energies(power_spectrum)

        # Convert to specific loudness
        specific_loudness = np.zeros_like(band_energies)
        for i, energy in enumerate(band_energies):
            if energy > self.absolute_threshold[min(i, len(self.absolute_threshold) - 1)]:
                # Simplified loudness calculation
                specific_loudness[i] = energy ** 0.23

        # Total loudness (sum across critical bands)
        return np.sum(specific_loudness)

    def _compute_sharpness(self, power_spectrum):
        """Compute sharpness in acum"""
        band_energies = self._compute_critical_band_energies(power_spectrum)
        total_loudness = np.sum(band_energies)

        if total_loudness == 0:
            return 0.0

        # Weight higher frequencies more heavily
        weights = np.logspace(0, 1, len(band_energies))
        weighted_loudness = np.sum(band_energies * weights)

        return weighted_loudness / total_loudness

    def _compute_roughness(self, power_spectrum):
        """Compute roughness in asper"""
        band_energies = self._compute_critical_band_energies(power_spectrum)

        # Roughness from adjacent band interactions
        roughness = 0.0
        for i in range(len(band_energies) - 1):
            # Simplified roughness model
            energy_product = band_energies[i] * band_energies[i + 1]
            roughness += energy_product ** 0.5

        return roughness

    def _compute_spectral_spread(self, power_spectrum, freqs):
        """Compute spectral spread (variance around centroid)"""
        if np.sum(power_spectrum) == 0:
            return 0.0

        centroid = np.sum(freqs * power_spectrum) / np.sum(power_spectrum)
        spread = np.sum(((freqs - centroid) ** 2) * power_spectrum) / np.sum(power_spectrum)
        return np.sqrt(spread)

    def _compute_spectral_skewness(self, power_spectrum, freqs):
        """Compute spectral skewness (asymmetry)"""
        if np.sum(power_spectrum) == 0:
            return 0.0

        centroid = np.sum(freqs * power_spectrum) / np.sum(power_spectrum)
        spread = self._compute_spectral_spread(power_spectrum, freqs)

        if spread == 0:
            return 0.0

        skewness = np.sum(((freqs - centroid) ** 3) * power_spectrum)
        skewness /= np.sum(power_spectrum) * (spread ** 3)
        return skewness

    def _compute_spectral_kurtosis(self, power_spectrum, freqs):
        """Compute spectral kurtosis (peakedness)"""
        if np.sum(power_spectrum) == 0:
            return 0.0

        centroid = np.sum(freqs * power_spectrum) / np.sum(power_spectrum)
        spread = self._compute_spectral_spread(power_spectrum, freqs)

        if spread == 0:
            return 0.0

        kurtosis = np.sum(((freqs - centroid) ** 4) * power_spectrum)
        kurtosis /= np.sum(power_spectrum) * (spread ** 4)
        return kurtosis - 3  # Excess kurtosis

    def _compute_spectral_slope(self, power_spectrum, freqs):
        """Compute spectral slope (linear regression)"""
        if len(power_spectrum) < 2:
            return 0.0

        # Log-frequency, log-magnitude
        log_freqs = np.log(np.maximum(freqs[1:], 1.0))
        log_magnitudes = np.log(np.maximum(power_spectrum[1:], 1e-10))

        # Linear regression
        slope, _ = np.polyfit(log_freqs, log_magnitudes, 1)
        return slope

class FormantTracker:
    """Real-time formant detection and tracking"""

    def __init__(self):
        self.formant_history = deque(maxlen=10)

    def detect_formants(self, audio_data, sample_rate):
        """Detect formant frequencies using LPC analysis"""
        # Linear Predictive Coding for formant estimation
        lpc_order = min(16, len(audio_data) // 4)

        try:
            # Autocorrelation method for LPC
            autocorr = np.correlate(audio_data, audio_data, mode='full')
            autocorr = autocorr[len(autocorr) // 2:]

            # Levinson-Durbin algorithm
            lpc_coeffs = self._levinson_durbin(autocorr[:lpc_order + 1])

            # Find roots of LPC polynomial
            roots = np.roots(lpc_coeffs)

            # Extract formant frequencies
            formants = self._roots_to_formants(roots, sample_rate)

            # Estimate vocal tract length
            vocal_tract_length = self._estimate_vocal_tract_length(formants)

            return {
                'frequencies': formants,
                'bandwidths': self._estimate_bandwidths(formants),
                'vocal_tract_length': vocal_tract_length
            }

        except Exception as e:
            logger.debug(f"Formant detection failed: {e}")
            return {
                'frequencies': np.array([800, 1200, 2500, 3500]),  # Default formants
                'bandwidths': np.array([80, 120, 250, 350]),
                'vocal_tract_length': 17.5  # Average adult vocal tract
            }

    def _levinson_durbin(self, autocorr):
        """Levinson-Durbin recursion for LPC coefficients"""
        n = len(autocorr) - 1
        lpc = np.zeros(n + 1)
        lpc[0] = 1.0

        error = autocorr[0]

        for i in range(1, n + 1):
            reflection = -np.sum(lpc[:i] * autocorr[i:0:-1]) / error

            lpc[1:i] += reflection * lpc[i-1:0:-1]
            lpc[i] = reflection

            error *= (1 - reflection ** 2)

        return lpc

    def _roots_to_formants(self, roots, sample_rate):
        """Convert LPC roots to formant frequencies"""
        # Keep only roots inside unit circle with positive frequencies
        formant_frequencies = []

        for root in roots:
            if np.abs(root) < 1.0 and np.imag(root) > 0:
                freq = np.angle(root) * sample_rate / (2 * np.pi)
                if 200 < freq < sample_rate / 2:  # Reasonable formant range
                    formant_frequencies.append(freq)

        # Sort and take first 4 formants
        formant_frequencies = sorted(formant_frequencies)[:4]

        # Pad to 4 formants if needed
        while len(formant_frequencies) < 4:
            if len(formant_frequencies) == 0:
                formant_frequencies.append(800)
            else:
                formant_frequencies.append(formant_frequencies[-1] * 1.3)

        return np.array(formant_frequencies)

    def _estimate_bandwidths(self, formants):
        """Estimate formant bandwidths"""
        # Empirical bandwidth estimation
        bandwidths = []
        for f in formants:
            # Bandwidth increases with frequency
            bw = 50 + f * 0.05
            bandwidths.append(bw)

        return np.array(bandwidths)

    def _estimate_vocal_tract_length(self, formants):
        """Estimate vocal tract length from formant frequencies"""
        if len(formants) < 2:
            return 17.5  # Default average

        # Use first two formants for estimation
        f1, f2 = formants[0], formants[1]

        # Simplified acoustic tube model
        # VTL ≈ c / (4 * F1) where c is speed of sound
        c = 34300  # cm/s
        vtl = c / (4 * f1) if f1 > 0 else 17.5

        return np.clip(vtl, 10, 25)  # Reasonable range

class HarmonicAnalyzer:
    """Advanced harmonic and noise analysis"""

    def __init__(self):
        self.harmonic_threshold = 0.1

    def analyze(self, audio_data, sample_rate):
        """Comprehensive harmonic analysis"""
        # Find fundamental frequency
        fundamental = self._estimate_fundamental(audio_data, sample_rate)

        if fundamental == 0:
            return {
                'harmonic_energy': 0.0,
                'noise_energy': 1.0,
                'harmonicity': 0.0,
                'inharmonicity': 1.0
            }

        # Separate harmonic and noise components
        harmonic_energy, noise_energy = self._separate_harmonic_noise(
            audio_data, sample_rate, fundamental
        )

        total_energy = harmonic_energy + noise_energy
        if total_energy == 0:
            return {
                'harmonic_energy': 0.0,
                'noise_energy': 0.0,
                'harmonicity': 0.0,
                'inharmonicity': 0.0
            }

        harmonicity = harmonic_energy / total_energy
        inharmonicity = noise_energy / total_energy

        return {
            'harmonic_energy': harmonic_energy,
            'noise_energy': noise_energy,
            'harmonicity': harmonicity,
            'inharmonicity': inharmonicity
        }

    def _estimate_fundamental(self, audio_data, sample_rate):
        """Estimate fundamental frequency using autocorrelation"""
        # Autocorrelation method
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]

        # Find peak in reasonable frequency range
        min_period = int(sample_rate / 800)  # 800 Hz max
        max_period = int(sample_rate / 80)   # 80 Hz min

        if max_period >= len(autocorr):
            return 0.0

        search_range = autocorr[min_period:max_period]
        if len(search_range) == 0:
            return 0.0

        peak_idx = np.argmax(search_range) + min_period
        fundamental = sample_rate / peak_idx if peak_idx > 0 else 0.0

        return fundamental

    def _separate_harmonic_noise(self, audio_data, sample_rate, fundamental):
        """Separate harmonic and noise components using spectral analysis"""
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)
        freqs = np.fft.rfftfreq(len(audio_data), 1/sample_rate)

        harmonic_energy = 0.0
        noise_energy = 0.0

        # Define harmonic bins
        harmonic_bins = set()
        for harmonic in range(1, 20):  # Up to 20th harmonic
            target_freq = fundamental * harmonic
            if target_freq > sample_rate / 2:
                break

            # Find closest frequency bin
            bin_idx = np.argmin(np.abs(freqs - target_freq))
            # Include neighboring bins for tolerance
            for offset in range(-2, 3):
                if 0 <= bin_idx + offset < len(magnitude):
                    harmonic_bins.add(bin_idx + offset)

        # Sum energies
        for i, mag in enumerate(magnitude):
            energy = mag ** 2
            if i in harmonic_bins:
                harmonic_energy += energy
            else:
                noise_energy += energy

        return harmonic_energy, noise_energy

@dataclass(eq=False)
class Particle:
    """Individual particle for the particle system"""

    def __eq__(self, other):
        if not isinstance(other, Particle):
            return NotImplemented
        return (
            np.array_equal(self.position, other.position) and
            np.array_equal(self.velocity, other.velocity) and
            self.id == other.id
        )
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    velocity: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    acceleration: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0, 1.0]))
    size: float = 1.0
    life: float = 1.0
    max_life: float = 1.0
    mass: float = 1.0
    particle_type: ParticleType = ParticleType.SPARK

@dataclass(eq=False)
class Light:
    """Light object for the lighting system"""

    def __eq__(self, other):
        if not isinstance(other, Light):
            return NotImplemented
        return (
            np.array_equal(self.position, other.position) and
            np.array_equal(self.color, other.color) and
            self.intensity == other.intensity
        )
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    intensity: float = 1.0
    light_type: LightType = LightType.POINT
    animation: LightAnimation = LightAnimation.STATIC
    direction: np.ndarray = field(default_factory=lambda: np.array([0.0, -1.0, 0.0]))
    cone_angle: float = 30.0
    attenuation: float = 1.0
    created_time: float = field(default_factory=time.time)
    life_time: float = 10.0

@dataclass(eq=False)
class SceneObject:
    """Scene object with comprehensive morphing capabilities"""

    def __eq__(self, other):
        if not isinstance(other, SceneObject):
            return NotImplemented
        return self.id == other.id  # simplify: objects are equal if IDs match
    name: str = "Object"
    position: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    scale: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    current_shape: MorphShapes = MorphShapes.SPHERE
    target_shape: MorphShapes = MorphShapes.SPHERE
    morph_factor: float = 0.0
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0, 1.0]))
    note_range: Tuple[int, int] = (60, 72)
    velocity_sensitivity: float = 1.0
    vertices: Optional[np.ndarray] = None
    active: bool = True

@dataclass
class PerformanceMetrics:
    """Performance monitoring data"""
    fps: float = 0.0
    frame_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    gpu_memory: float = 0.0
    particle_count: int = 0
    light_count: int = 0
    mesh_vertices: int = 0
    render_time: float = 0.0
    audio_latency: float = 0.0

class AudioEngine:
    """Enhanced audio engine with multiple sources and analysis"""
    
    def __init__(self, samplerate=44100, buffer_size=4096):
        self.sr = samplerate
        self.buffer_size = buffer_size
        self.frequency = 440.0
        self.amplitude = 0.18
        self.stream = None
        self.lock = threading.Lock()
        self.time_index = 0
        self.is_running = False
        self.source_mode = "Sine"  # "Sine", "Microphone", "MPK Mini"
        
        # Audio analysis buffers
        self.audio_buffer = deque(maxlen=buffer_size * 2)
        self.features = AudioFeatures()

        # Advanced psychoacoustic analyzer
        self.psychoacoustic_analyzer = PsychoacousticAnalyzer(samplerate, buffer_size)

        # Onset detection parameters
        self.onset_threshold = 0.3
        self.last_onset_time = 0.0
        self.onset_cooldown = 0.1

        # Beat tracking
        self.beat_tracker = deque(maxlen=100)
        self.last_beat_time = 0.0

        # Advanced analysis history for smoothing
        self.feature_history = deque(maxlen=10)
        self.enable_advanced_analysis = True

    def _audio_callback(self, outdata, frames, time, status):
        """Audio output callback for sine wave generation"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        t = (np.arange(frames) + self.time_index) / float(self.sr)
        with self.lock:
            freq = self.frequency
            amp = self.amplitude
        
        wave = amp * np.sin(2 * math.pi * freq * t)
        outdata[:] = wave.reshape(-1, 1)
        self.time_index += frames

    def _input_callback(self, indata, frames, time, status):
        """Audio input callback for microphone analysis"""
        if status:
            logger.warning(f"Audio input callback status: {status}")
        
        audio_data = indata[:, 0] if len(indata.shape) > 1 else indata
        self.audio_buffer.extend(audio_data.flatten())
        self._analyze_audio()

    def start_output(self):
        """Start audio output (sine wave)"""
        if self.is_running or not HAS_SOUNDDEVICE:
            return False
        
        try:
            self.time_index = 0
            self.stream = sd.OutputStream(
                channels=1, 
                callback=self._audio_callback, 
                samplerate=self.sr,
                blocksize=self.buffer_size
            )
            self.stream.start()
            self.is_running = True
            logger.info("✅ Audio output started")
            return True
        except Exception as e:
            logger.error(f'❌ Audio output start failed: {e}')
            return False

    def start_input(self):
        """Start audio input (microphone)"""
        if self.is_running or not HAS_SOUNDDEVICE:
            return False
        
        try:
            self.stream = sd.InputStream(
                channels=1,
                callback=self._input_callback,
                samplerate=self.sr,
                blocksize=self.buffer_size
            )
            self.stream.start()
            self.is_running = True
            logger.info("✅ Audio input started")
            return True
        except Exception as e:
            logger.error(f'❌ Audio input start failed: {e}')
            return False

    def stop(self):
        """Stop audio stream"""
        if not self.is_running or not self.stream:
            return
        
        try:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            self.is_running = False
            logger.info("✅ Audio stream stopped")
        except Exception as e:
            logger.error(f'⚠️ Error stopping audio: {e}')

    def set_frequency(self, freq_hz: float):
        """Set sine wave frequency"""
        with self.lock:
            self.frequency = max(20.0, min(20000.0, float(freq_hz)))

    def set_source_mode(self, mode: str):
        """Set audio source mode"""
        self.source_mode = mode
        with audio_state.lock:
            audio_state.source_status = mode

    def _analyze_audio(self):
        """Analyze audio buffer and extract features"""
        if len(self.audio_buffer) < self.buffer_size:
            return
        
        # Get recent audio data
        audio_data = np.array(list(self.audio_buffer)[-self.buffer_size:])
        
        try:
            # Basic features
            self.features.amplitude = float(np.sqrt(np.mean(audio_data**2)))
            self.features.rms_energy = float(np.sqrt(np.mean(audio_data**2)))
            
            # Spectral analysis
            if len(audio_data) > 0:
                # FFT analysis
                fft = np.fft.rfft(audio_data)
                magnitude = np.abs(fft)
                freqs = np.fft.rfftfreq(len(audio_data), 1/self.sr)
                
                if len(magnitude) > 0 and np.sum(magnitude) > 0:
                    # Spectral centroid
                    self.features.spectral_centroid = float(
                        np.sum(freqs * magnitude) / np.sum(magnitude)
                    )
                    
                    # Spectral rolloff (85% of energy)
                    cumsum = np.cumsum(magnitude)
                    total_energy = cumsum[-1]
                    if total_energy > 0:
                        rolloff_idx = np.where(cumsum >= 0.85 * total_energy)[0]
                        if len(rolloff_idx) > 0:
                            self.features.spectral_rolloff = float(freqs[rolloff_idx[0]])
                    
                    # Zero crossing rate
                    zero_crossings = np.where(np.diff(np.sign(audio_data)))[0]
                    self.features.zero_crossing_rate = float(len(zero_crossings) / len(audio_data))
            
            # Onset detection
            current_time = time.time()
            if (self.features.amplitude > self.onset_threshold and 
                (current_time - self.last_onset_time) > self.onset_cooldown):
                self.features.onset_detected = True
                self.last_onset_time = current_time
            else:
                self.features.onset_detected = False
            
            # Advanced analysis with librosa
            if HAS_LIBROSA and len(audio_data) >= 512:
                try:
                    # MFCC features
                    mfccs = librosa.feature.mfcc(y=audio_data.astype(np.float32), 
                                               sr=self.sr, n_mfcc=13)
                    self.features.mfcc = np.mean(mfccs, axis=1)
                    
                    # Mel spectrogram
                    mel_spec = librosa.feature.melspectrogram(y=audio_data.astype(np.float32), 
                                                            sr=self.sr, n_mels=128)
                    self.features.mel_spectrogram = np.mean(mel_spec, axis=1)
                    
                    # Chromagram
                    chroma = librosa.feature.chroma_stft(y=audio_data.astype(np.float32), 
                                                       sr=self.sr)
                    self.features.chroma = np.mean(chroma, axis=1)
                    
                    # Beat tracking
                    tempo, beats = librosa.beat.beat_track(y=audio_data.astype(np.float32), 
                                                         sr=self.sr, hop_length=512)
                    if tempo and tempo > 0:
                        self.features.tempo = float(tempo)
                        if len(beats) > 0:
                            self.features.beat_detected = True
                            self.last_beat_time = current_time
                    
                    # Spectral contrast
                    contrast = librosa.feature.spectral_contrast(y=audio_data.astype(np.float32),
                                                               sr=self.sr)
                    self.features.spectral_contrast = np.mean(contrast, axis=1)

                    # Tonnetz (harmonic network)
                    tonnetz = librosa.feature.tonnetz(y=audio_data.astype(np.float32), sr=self.sr)
                    self.features.tonnetz = np.mean(tonnetz, axis=1)

                except Exception as e:
                    logger.debug(f"Advanced audio analysis failed: {e}")

            # Advanced psychoacoustic analysis
            if self.enable_advanced_analysis:
                try:
                    self.features = self.psychoacoustic_analyzer.analyze_psychoacoustic_features(
                        audio_data, self.features
                    )

                    # Add dynamic range analysis
                    if len(audio_data) > 0:
                        peak = np.max(np.abs(audio_data))
                        rms = np.sqrt(np.mean(audio_data**2))
                        self.features.peak_energy = float(peak)
                        self.features.crest_factor = float(peak / rms) if rms > 0 else 0.0
                        self.features.dynamic_range = float(peak - rms)

                    # Fundamental frequency estimation (improved)
                    if len(audio_data) >= 1024:
                        fund_freq = self._estimate_fundamental_improved(audio_data)
                        self.features.fundamental_frequency = fund_freq
                        self.features.pitch = fund_freq

                    # Add feature smoothing
                    self.feature_history.append(self.features)
                    self._smooth_features()

                except Exception as e:
                    logger.debug(f"Psychoacoustic analysis failed: {e}")

            # Update global state
            with audio_state.lock:
                audio_state.centroid_hz = self.features.spectral_centroid
                audio_state.amplitude = self.features.amplitude
                audio_state.onset_detected = self.features.onset_detected
                audio_state.beat_detected = self.features.beat_detected
                audio_state.tempo = self.features.tempo
                
        except Exception as e:
            logger.error(f"Audio analysis error: {e}")

    def _estimate_fundamental_improved(self, audio_data):
        """Improved fundamental frequency estimation using multiple methods"""
        # Method 1: Autocorrelation
        autocorr_f0 = self._autocorr_fundamental(audio_data)

        # Method 2: Cepstral analysis
        cepstral_f0 = self._cepstral_fundamental(audio_data)

        # Method 3: Harmonic product spectrum
        hps_f0 = self._harmonic_product_spectrum(audio_data)

        # Combine estimates with confidence weighting
        estimates = [f for f in [autocorr_f0, cepstral_f0, hps_f0] if f > 80 and f < 800]

        if not estimates:
            return 440.0  # Default

        # Use median for robustness
        return float(np.median(estimates))

    def _autocorr_fundamental(self, audio_data):
        """Autocorrelation-based F0 estimation"""
        autocorr = np.correlate(audio_data, audio_data, mode='full')
        autocorr = autocorr[len(autocorr) // 2:]

        # Find peak in reasonable range
        min_period = int(self.sr / 800)  # 800 Hz max
        max_period = int(self.sr / 80)   # 80 Hz min

        if max_period >= len(autocorr):
            return 440.0

        search_range = autocorr[min_period:max_period]
        if len(search_range) == 0:
            return 440.0

        peak_idx = np.argmax(search_range) + min_period
        return self.sr / peak_idx if peak_idx > 0 else 440.0

    def _cepstral_fundamental(self, audio_data):
        """Cepstral analysis for F0 estimation"""
        # Real cepstrum
        fft = np.fft.rfft(audio_data)
        log_magnitude = np.log(np.maximum(np.abs(fft), 1e-10))
        cepstrum = np.fft.irfft(log_magnitude)

        # Find peak in quefrency domain
        min_quefrency = int(self.sr / 800)
        max_quefrency = int(self.sr / 80)

        if max_quefrency >= len(cepstrum):
            return 440.0

        search_range = cepstrum[min_quefrency:max_quefrency]
        if len(search_range) == 0:
            return 440.0

        peak_idx = np.argmax(search_range) + min_quefrency
        return self.sr / peak_idx if peak_idx > 0 else 440.0

    def _harmonic_product_spectrum(self, audio_data):
        """Harmonic Product Spectrum for F0 estimation"""
        fft = np.fft.rfft(audio_data)
        magnitude = np.abs(fft)

        # Downsample for harmonics
        hps = magnitude.copy()
        for harmonic in range(2, 6):  # Up to 5th harmonic
            downsampled = magnitude[::harmonic]
            # Pad or trim to match length
            if len(downsampled) < len(hps):
                hps = hps[:len(downsampled)]
            hps *= downsampled[:len(hps)]

        # Find peak
        freqs = np.fft.rfftfreq(len(audio_data), 1/self.sr)[:len(hps)]
        valid_range = (freqs >= 80) & (freqs <= 800)

        if not np.any(valid_range):
            return 440.0

        valid_hps = hps[valid_range]
        valid_freqs = freqs[valid_range]

        if len(valid_hps) == 0:
            return 440.0

        peak_idx = np.argmax(valid_hps)
        return float(valid_freqs[peak_idx])

    def _smooth_features(self):
        """Apply temporal smoothing to features"""
        if len(self.feature_history) < 2:
            return

        # Smooth numeric features
        numeric_features = [
            'amplitude', 'spectral_centroid', 'spectral_rolloff',
            'loudness_sones', 'sharpness_acum', 'roughness_asper',
            'harmonicity', 'fundamental_frequency'
        ]

        alpha = 0.3  # Smoothing factor
        current = self.feature_history[-1]
        previous = self.feature_history[-2]

        for feature_name in numeric_features:
            if hasattr(current, feature_name) and hasattr(previous, feature_name):
                current_val = getattr(current, feature_name)
                previous_val = getattr(previous, feature_name)

                if isinstance(current_val, (int, float)) and isinstance(previous_val, (int, float)):
                    smoothed_val = alpha * current_val + (1 - alpha) * previous_val
                    setattr(current, feature_name, smoothed_val)

class PhysicsBasedMorphing:
    """Spring-mass system for organic morphing transitions"""

    def __init__(self, resolution=24):
        self.resolution = resolution
        self.vertices = None
        self.velocities = None
        self.springs = []

        # Physics parameters
        self.spring_constant = 0.8
        self.damping = 0.95
        self.mass = 1.0
        self.time_step = 0.016  # ~60 FPS

        # Force field parameters
        self.gravity = np.array([0.0, -0.1, 0.0])
        self.wind = np.array([0.0, 0.0, 0.0])

    def initialize_mesh(self, initial_vertices):
        """Initialize spring-mass mesh from vertices"""
        self.vertices = initial_vertices.copy()
        self.velocities = np.zeros_like(self.vertices)
        self._create_spring_network()

    def _create_spring_network(self):
        """Create spring connections between nearby vertices"""
        self.springs = []
        n_vertices = len(self.vertices)

        # Connect each vertex to its nearest neighbors
        for i in range(n_vertices):
            for j in range(i + 1, n_vertices):
                distance = np.linalg.norm(self.vertices[i] - self.vertices[j])

                # Connect vertices within threshold distance
                if distance < 0.5:  # Adjust threshold as needed
                    rest_length = distance
                    self.springs.append({
                        'vertex_a': i,
                        'vertex_b': j,
                        'rest_length': rest_length,
                        'strength': self.spring_constant
                    })

    def apply_morph_target(self, target_vertices, morph_factor):
        """Apply target shape as force field"""
        if self.vertices is None:
            self.initialize_mesh(target_vertices)
            return self.vertices

        # Calculate forces toward target positions
        target_forces = np.zeros_like(self.vertices)
        for i, (current_pos, target_pos) in enumerate(zip(self.vertices, target_vertices)):
            displacement = target_pos - current_pos
            force_magnitude = morph_factor * 2.0  # Adjust for responsiveness
            target_forces[i] = displacement * force_magnitude

        # Update physics simulation
        return self._update_physics(target_forces)

    def _update_physics(self, external_forces):
        """Update spring-mass physics simulation"""
        forces = external_forces.copy()

        # Add spring forces
        for spring in self.springs:
            i, j = spring['vertex_a'], spring['vertex_b']

            # Current spring vector
            spring_vector = self.vertices[j] - self.vertices[i]
            current_length = np.linalg.norm(spring_vector)

            if current_length > 0:
                # Normalized direction
                direction = spring_vector / current_length

                # Spring force (Hooke's law)
                extension = current_length - spring['rest_length']
                spring_force = direction * extension * spring['strength']

                forces[i] += spring_force
                forces[j] -= spring_force

        # Add gravity and other global forces
        forces += self.gravity
        forces += self.wind

        # Update velocities (F = ma, assume mass = 1)
        self.velocities += forces * self.time_step

        # Apply damping
        self.velocities *= self.damping

        # Update positions
        self.vertices += self.velocities * self.time_step

        return self.vertices.copy()

class FluidDynamicsMorphing:
    """Fluid-like morphing simulation using simplified Navier-Stokes"""

    def __init__(self):
        self.viscosity = 0.1
        self.density = 1.0
        self.pressure_field = None
        self.velocity_field = None

    def apply_fluid_morph(self, source_vertices, target_vertices, morph_factor):
        """Apply fluid dynamics to morphing process"""
        # Simplified fluid simulation
        # Calculate velocity field based on target displacement
        displacement = target_vertices - source_vertices

        # Apply viscous forces
        fluid_velocity = displacement * morph_factor * self.viscosity

        # Add turbulence for organic feel
        turbulence = self._generate_turbulence(source_vertices.shape[0])
        fluid_velocity += turbulence * 0.1

        # Apply fluid motion
        result_vertices = source_vertices + fluid_velocity

        return result_vertices

    def _generate_turbulence(self, n_vertices):
        """Generate turbulent velocity field"""
        # Simple noise-based turbulence
        turbulence = np.random.normal(0, 0.02, (n_vertices, 3))
        return turbulence.astype(np.float32)

class OrganicNoiseGenerator:
    """Procedural noise for organic shape variations"""

    def __init__(self):
        self.time = 0.0
        self.noise_scale = 1.0
        self.octaves = 4

    def apply_organic_noise(self, vertices, strength=0.1):
        """Apply Perlin-like noise for organic variation"""
        noisy_vertices = vertices.copy()

        # Generate noise for each vertex
        for i, vertex in enumerate(vertices):
            # Multi-octave noise
            noise_value = 0.0
            amplitude = 1.0
            frequency = self.noise_scale

            for octave in range(self.octaves):
                # Simple noise approximation
                seed = (vertex[0] * 1000 + vertex[1] * 100 + vertex[2] * 10 +
                       self.time * 0.1 + octave * 1000)
                noise = (np.sin(seed) + np.sin(seed * 1.1) + np.sin(seed * 1.3)) / 3.0

                noise_value += noise * amplitude
                amplitude *= 0.5
                frequency *= 2.0

            # Apply noise as displacement
            normal = vertex / (np.linalg.norm(vertex) + 1e-6)  # Approximate normal
            displacement = normal * noise_value * strength
            noisy_vertices[i] += displacement

        self.time += 0.016  # Advance time for animation
        return noisy_vertices

class SubdivisionSurface:
    """Catmull-Clark subdivision for smooth surfaces"""

    def __init__(self):
        self.topology = None  # Will store mesh connectivity

    def subdivide(self, vertices, level=1):
        """Apply Catmull-Clark subdivision"""
        if level == 0:
            return vertices

        # For simplicity, implement a basic subdivision
        # In a full implementation, this would use proper mesh topology
        subdivided = self._simple_subdivision(vertices)

        # Recursively apply subdivision
        if level > 1:
            return self.subdivide(subdivided, level - 1)
        else:
            return subdivided

    def _simple_subdivision(self, vertices):
        """Simplified subdivision - increases vertex density"""
        # This is a simplified version that interpolates between existing vertices
        # A full implementation would require proper mesh topology and edge/face data

        n = len(vertices)
        new_vertices = []

        # Keep original vertices (smoothed)
        for i, vertex in enumerate(vertices):
            # Simple smoothing by averaging with neighbors
            neighbors = self._find_neighbors(vertices, i, threshold=0.6)
            if len(neighbors) > 0:
                smoothed = vertex * 0.6 + np.mean(neighbors, axis=0) * 0.4
                new_vertices.append(smoothed)
            else:
                new_vertices.append(vertex)

        # Add edge vertices (midpoints)
        for i in range(n):
            for j in range(i + 1, n):
                distance = np.linalg.norm(vertices[i] - vertices[j])
                if distance < 0.5:  # Adjacent vertices
                    midpoint = (vertices[i] + vertices[j]) / 2.0
                    new_vertices.append(midpoint)

        return np.array(new_vertices, dtype=np.float32)

    def _find_neighbors(self, vertices, index, threshold=0.5):
        """Find neighboring vertices within threshold distance"""
        neighbors = []
        current = vertices[index]

        for i, vertex in enumerate(vertices):
            if i != index:
                distance = np.linalg.norm(vertex - current)
                if distance < threshold:
                    neighbors.append(vertex)

        return np.array(neighbors) if neighbors else np.array([])

class MorphingEngine:
    """Advanced morphing engine with physics-based deformation and spring-mass systems"""

    def __init__(self, resolution=24):
        self.resolution = resolution
        self.morph = 0.0  # 0..1 base morph factor
        self.rotation_enabled = True
        self.render_modes = ['dots', 'wireframe', 'solid', 'shaded']
        self.render_idx = 2  # Default to 'solid' instead of 'dots'

        # Pre-generate base shapes
        self.shapes_cache = {}
        self._generate_base_shapes()

        # Current shape pair for morphing
        self.shape_a = MorphShapes.SPHERE
        self.shape_b = MorphShapes.CUBE

        # Physics-based morphing system
        self.physics_system = PhysicsBasedMorphing(resolution)
        self.enable_physics = False  # DISABLED to prevent geometry corruption
        self.physics_strength = 0.5  # 0-1 blend between linear and physics morphing

        # Fluid dynamics simulation
        self.fluid_sim = FluidDynamicsMorphing()
        self.enable_fluid = False

        # Noise-based organic morphing
        self.noise_generator = OrganicNoiseGenerator()
        self.noise_strength = 0.0  # DISABLED to prevent blob mess

        # Subdivision surface system
        self.subdivision_system = SubdivisionSurface()
        self.subdivision_level = 0  # 0 = off, 1-3 = increasing detail
        
    def _generate_base_shapes(self):
        """Generate and cache base shapes with consistent vertex counts"""
        # Generate sphere first to establish target vertex count
        sphere_vertices = self._generate_sphere()
        self.shapes_cache[MorphShapes.SPHERE] = sphere_vertices
        self._target_vertex_count = len(sphere_vertices)

        # Generate all other shapes with consistent vertex count
        self.shapes_cache[MorphShapes.CUBE] = self._sphere_to_cube(sphere_vertices)
        self.shapes_cache[MorphShapes.CYLINDER] = self._generate_cylinder()
        self.shapes_cache[MorphShapes.CONE] = self._generate_cone()
        self.shapes_cache[MorphShapes.TORUS] = self._generate_torus()
        self.shapes_cache[MorphShapes.ICOSAHEDRON] = self._generate_icosahedron()
        self.shapes_cache[MorphShapes.OCTAHEDRON] = self._generate_octahedron()
        self.shapes_cache[MorphShapes.DODECAHEDRON] = self._generate_dodecahedron()
        self.shapes_cache[MorphShapes.TETRAHEDRON] = self._generate_tetrahedron()
        self.shapes_cache[MorphShapes.PLANE] = self._generate_plane()
        self.shapes_cache[MorphShapes.PYRAMID] = self._generate_pyramid()
        self.shapes_cache[MorphShapes.HELIX] = self._generate_helix()
        self.shapes_cache[MorphShapes.MOBIUS] = self._generate_mobius()
        self.shapes_cache[MorphShapes.KLEIN_BOTTLE] = self._generate_klein_bottle()
        self.shapes_cache[MorphShapes.STAR] = self._generate_star()
        self.shapes_cache[MorphShapes.HEART] = self._generate_heart()
        self.shapes_cache[MorphShapes.SPIRAL] = self._generate_spiral()
        self.shapes_cache[MorphShapes.CRYSTAL] = self._generate_crystal()
        self.shapes_cache[MorphShapes.FRACTAL] = self._generate_fractal()
        self.shapes_cache[MorphShapes.TERRAIN] = self._generate_terrain()
        
    def _generate_sphere(self):
        """Generate sphere vertices with exact vertex count"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        # Generate points directly to target count
        for i in range(target_count):
            # Distribute points evenly on sphere surface
            theta = math.pi * (i % int(math.sqrt(target_count))) / (math.sqrt(target_count) - 1)
            phi = 2 * math.pi * (i // int(math.sqrt(target_count))) / (target_count // int(math.sqrt(target_count)))
            x = math.sin(theta) * math.cos(phi)
            y = math.cos(theta)
            z = math.sin(theta) * math.sin(phi)
            pts.append([x, y, z])

        return np.array(pts[:target_count], dtype=np.float32)
    
    def _sphere_to_cube(self, sphere_pts):
        """Convert sphere points to cube points with exact count"""
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        cube = []

        for i, (x, y, z) in enumerate(sphere_pts):
            if i >= target_count:
                break
            m = max(abs(x), abs(y), abs(z))
            if m == 0:
                cube.append([0.0, 0.0, 0.0])
            else:
                cube.append([x / m, y / m, z / m])

        # Ensure exact count
        while len(cube) < target_count:
            cube.append(cube[-1] if cube else [0.0, 0.0, 0.0])

        return np.array(cube[:target_count], dtype=np.float32)
    
    def _generate_cylinder(self):
        """Generate cylinder vertices"""
        pts = []
        res = self.resolution
        for i in range(res):
            # Top and bottom circles
            angle = 2 * math.pi * i / res
            x = math.cos(angle)
            z = math.sin(angle)
            pts.append([x, 1.0, z])  # Top circle
            pts.append([x, -1.0, z])  # Bottom circle
            
            # Side lines
            for j in range(res // 2):
                y = -1.0 + 2.0 * j / (res // 2 - 1)
                pts.append([x, y, z])
        
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        return np.array(pts[:target_count], dtype=np.float32)
    
    def _generate_cone(self):
        """Generate cone vertices"""
        pts = []
        res = self.resolution
        
        # Tip of cone
        pts.append([0.0, 1.0, 0.0])
        
        # Base circle and sides
        for i in range(res - 1):
            angle = 2 * math.pi * i / (res - 1)
            x = math.cos(angle)
            z = math.sin(angle)
            pts.append([x, -1.0, z])  # Base circle
            
            # Add points along the side
            for j in range(2):
                y = -1.0 + 2.0 * (j + 1) / 3
                scale = 1.0 - (j + 1) / 3
                pts.append([x * scale, y, z * scale])
        
        # Pad to match sphere point count
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        while len(pts) < target_count:
            pts.append(pts[-1])
        
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        return np.array(pts[:target_count], dtype=np.float32)
    
    def _generate_torus(self):
        """Generate torus vertices with exact vertex count"""
        pts = []
        R = 1.0  # Major radius
        r = 0.3  # Minor radius
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        # Generate vertices directly to target count
        generated = 0
        res = max(32, int(math.sqrt(target_count * 1.2)))  # Generate extra to ensure coverage

        for i in range(res):
            if generated >= target_count:
                break
            theta = 2 * math.pi * i / res
            for j in range(res):
                if generated >= target_count:
                    break
                phi = 2 * math.pi * j / res
                x = (R + r * math.cos(phi)) * math.cos(theta)
                y = r * math.sin(phi)
                z = (R + r * math.cos(phi)) * math.sin(theta)
                pts.append([x, y, z])
                generated += 1

        # Ensure exact vertex count
        while len(pts) < target_count:
            pts.append(pts[-1])

        return np.array(pts[:target_count], dtype=np.float32)

    def _generate_icosahedron(self):
        """Generate icosahedron vertices"""
        pts = []
        t = (1.0 + math.sqrt(5.0)) / 2.0  # Golden ratio

        # Icosahedron vertices
        vertices = [
            [-1,  t,  0], [ 1,  t,  0], [-1, -t,  0], [ 1, -t,  0],
            [ 0, -1,  t], [ 0,  1,  t], [ 0, -1, -t], [ 0,  1, -t],
            [ t,  0, -1], [ t,  0,  1], [-t,  0, -1], [-t,  0,  1]
        ]

        # Normalize and tessellate for more points
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        for i in range(target_count):
            v = vertices[i % len(vertices)]
            length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            pts.append([v[0]/length, v[1]/length, v[2]/length])

        return np.array(pts[:target_count], dtype=np.float32)

    def _generate_octahedron(self):
        """Generate octahedron vertices"""
        pts = []
        vertices = [[1,0,0], [-1,0,0], [0,1,0], [0,-1,0], [0,0,1], [0,0,-1]]

        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        for i in range(target_count):
            pts.append(vertices[i % len(vertices)])

        return np.array(pts[:target_count], dtype=np.float32)

    def _generate_dodecahedron(self):
        """Generate dodecahedron vertices"""
        pts = []
        t = (1.0 + math.sqrt(5.0)) / 2.0  # Golden ratio

        vertices = [
            [1,1,1], [1,1,-1], [1,-1,1], [1,-1,-1], [-1,1,1], [-1,1,-1], [-1,-1,1], [-1,-1,-1],
            [0,1/t,t], [0,-1/t,t], [0,1/t,-t], [0,-1/t,-t],
            [1/t,t,0], [-1/t,t,0], [1/t,-t,0], [-1/t,-t,0],
            [t,0,1/t], [t,0,-1/t], [-t,0,1/t], [-t,0,-1/t]
        ]

        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        for i in range(target_count):
            v = vertices[i % len(vertices)]
            length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            pts.append([v[0]/length, v[1]/length, v[2]/length])

        return np.array(pts[:target_count], dtype=np.float32)

    def _generate_tetrahedron(self):
        """Generate tetrahedron vertices"""
        pts = []
        vertices = [[1,1,1], [1,-1,-1], [-1,1,-1], [-1,-1,1]]

        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        for i in range(target_count):
            v = vertices[i % len(vertices)]
            length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
            pts.append([v[0]/length, v[1]/length, v[2]/length])

        return np.array(pts[:target_count], dtype=np.float32)

    def _generate_plane(self):
        """Generate plane vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        # Generate vertices directly to target count
        generated = 0
        res = max(32, int(math.sqrt(target_count * 1.2)))  # Generate extra

        for i in range(res):
            if generated >= target_count:
                break
            for j in range(res):
                if generated >= target_count:
                    break
                x = (i / (res - 1)) * 2 - 1
                z = (j / (res - 1)) * 2 - 1
                pts.append([x, 0, z])
                generated += 1

        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        while len(pts) < target_count:
            pts.append(pts[-1])

        return np.array(pts[:target_count], dtype=np.float32)

    def _generate_pyramid(self):
        """Generate pyramid vertices"""
        pts = []
        base_vertices = [[1,0,1], [1,0,-1], [-1,0,-1], [-1,0,1]]
        apex = [0, 1, 0]

        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        for i in range(target_count):
            if i % 5 == 0:
                pts.append(apex)
            else:
                pts.append(base_vertices[(i-1) % len(base_vertices)])

        return np.array(pts[:target_count], dtype=np.float32)

    def _generate_helix(self):
        """Generate helix vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        for i in range(target_count):
            t = i / target_count * 4 * math.pi
            x = math.cos(t)
            y = (i / target_count) * 2 - 1
            z = math.sin(t)
            pts.append([x, y, z])

        return np.array(pts, dtype=np.float32)

    def _generate_mobius(self):
        """Generate Möbius strip vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        for i in range(target_count):
            u = i / target_count * 2 * math.pi
            v = (i % 20) / 20 * 2 - 1  # Width parameter

            x = (1 + v/2 * math.cos(u/2)) * math.cos(u)
            y = (1 + v/2 * math.cos(u/2)) * math.sin(u)
            z = v/2 * math.sin(u/2)
            pts.append([x, y, z])

        return np.array(pts, dtype=np.float32)

    def _generate_klein_bottle(self):
        """Generate Klein bottle vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        for i in range(target_count):
            u = i / target_count * 2 * math.pi
            v = (i % 20) / 20 * 2 * math.pi

            x = (2 + math.cos(v/2) * math.sin(u) - math.sin(v/2) * math.sin(2*u)) * math.cos(v)
            y = (2 + math.cos(v/2) * math.sin(u) - math.sin(v/2) * math.sin(2*u)) * math.sin(v)
            z = math.sin(v/2) * math.sin(u) + math.cos(v/2) * math.sin(2*u)
            pts.append([x/3, y/3, z/3])  # Scale down

        return np.array(pts, dtype=np.float32)

    def _generate_star(self):
        """Generate star vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        # 5-pointed star
        for i in range(target_count):
            angle = i / target_count * 2 * math.pi * 5  # 5 points
            r = 1.0 if (i // (target_count // 10)) % 2 == 0 else 0.5  # Alternate radius
            x = r * math.cos(angle)
            y = 0
            z = r * math.sin(angle)
            pts.append([x, y, z])

        return np.array(pts, dtype=np.float32)

    def _generate_heart(self):
        """Generate heart shape vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        for i in range(target_count):
            t = i / target_count * 2 * math.pi
            x = 16 * math.sin(t)**3
            y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            z = 0
            pts.append([x/20, y/20, z])  # Scale down

        return np.array(pts, dtype=np.float32)

    def _generate_spiral(self):
        """Generate spiral vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        for i in range(target_count):
            t = i / target_count * 6 * math.pi
            r = i / target_count
            x = r * math.cos(t)
            y = (i / target_count) * 2 - 1
            z = r * math.sin(t)
            pts.append([x, y, z])

        return np.array(pts, dtype=np.float32)

    def _generate_crystal(self):
        """Generate crystal vertices"""
        pts = []
        # Crystal is like a diamond/gem shape
        vertices = [
            [0, 1, 0],     # Top apex
            [0.5, 0.5, 0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, 0.5], [-0.5, 0.5, -0.5],  # Upper ring
            [0.8, 0, 0.8], [0.8, 0, -0.8], [-0.8, 0, 0.8], [-0.8, 0, -0.8],         # Middle ring
            [0.5, -0.5, 0.5], [0.5, -0.5, -0.5], [-0.5, -0.5, 0.5], [-0.5, -0.5, -0.5], # Lower ring
            [0, -1, 0]     # Bottom apex
        ]

        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        for i in range(target_count):
            pts.append(vertices[i % len(vertices)])

        return np.array(pts, dtype=np.float32)

    def _generate_fractal(self):
        """Generate fractal vertices (Sierpinski tetrahedron approximation)"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        # Base tetrahedron vertices
        base = [[1,1,1], [1,-1,-1], [-1,1,-1], [-1,-1,1]]

        for i in range(target_count):
            # Create fractal pattern by scaling and positioning
            level = i % 4
            scale = 0.5 ** (level + 1)
            base_pt = base[i % len(base)]
            offset = [scale * base_pt[0], scale * base_pt[1], scale * base_pt[2]]
            pts.append(offset)

        return np.array(pts, dtype=np.float32)

    def _generate_terrain(self):
        """Generate terrain vertices"""
        pts = []
        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)

        # Generate vertices directly to target count
        generated = 0
        res = max(32, int(math.sqrt(target_count * 1.2)))  # Generate extra

        for i in range(res):
            if generated >= target_count:
                break
            for j in range(res):
                if generated >= target_count:
                    break
                x = (i / (res - 1)) * 2 - 1
                z = (j / (res - 1)) * 2 - 1
                # Generate height using simple noise
                y = 0.3 * math.sin(x * 3) * math.cos(z * 3) + 0.1 * math.sin(x * 10) * math.cos(z * 10)
                pts.append([x, y, z])
                generated += 1

        target_count = getattr(self, '_target_vertex_count', self.resolution * self.resolution)
        while len(pts) < target_count:
            pts.append(pts[-1])

        return np.array(pts[:target_count], dtype=np.float32)

    def get_morphed_vertices(self, shape_a=None, shape_b=None, morph_factor=None):
        """Get morphed vertices with advanced physics-based deformation"""
        if shape_a is None:
            shape_a = self.shape_a
        if shape_b is None:
            shape_b = self.shape_b
        if morph_factor is None:
            morph_factor = self.morph

        # Get vertex arrays
        verts_a = self.shapes_cache.get(shape_a, self.shapes_cache[MorphShapes.SPHERE])
        verts_b = self.shapes_cache.get(shape_b, self.shapes_cache[MorphShapes.CUBE])

        # Start with linear interpolation
        linear_morph = (1.0 - morph_factor) * verts_a + morph_factor * verts_b

        # Apply physics-based morphing if enabled
        if self.enable_physics:
            physics_morph = self.physics_system.apply_morph_target(verts_b, morph_factor)
            # Blend linear and physics morphing
            result_vertices = (1.0 - self.physics_strength) * linear_morph + self.physics_strength * physics_morph
        else:
            result_vertices = linear_morph

        # Apply fluid dynamics if enabled
        if self.enable_fluid:
            result_vertices = self.fluid_sim.apply_fluid_morph(verts_a, result_vertices, morph_factor)

        # Apply organic noise variation
        if self.noise_strength > 0:
            result_vertices = self.noise_generator.apply_organic_noise(result_vertices, self.noise_strength)

        # Apply subdivision surface if enabled
        if self.subdivision_level > 0:
            result_vertices = self.subdivision_system.subdivide(result_vertices, self.subdivision_level)

        return result_vertices

    def set_physics_parameters(self, **params):
        """Configure physics system parameters"""
        if 'spring_constant' in params:
            self.physics_system.spring_constant = params['spring_constant']
        if 'damping' in params:
            self.physics_system.damping = params['damping']
        if 'gravity' in params:
            self.physics_system.gravity = np.array(params['gravity'])
        if 'wind' in params:
            self.physics_system.wind = np.array(params['wind'])

    def set_fluid_parameters(self, **params):
        """Configure fluid dynamics parameters"""
        if 'viscosity' in params:
            self.fluid_sim.viscosity = params['viscosity']
        if 'density' in params:
            self.fluid_sim.density = params['density']

    def enable_advanced_morphing(self, physics=True, fluid=False, noise_strength=0.1, subdivision=0):
        """Enable/configure advanced morphing features"""
        self.enable_physics = physics
        self.enable_fluid = fluid
        self.noise_strength = noise_strength
        self.subdivision_level = subdivision

        logger.info(f"🌊 Advanced morphing: physics={physics}, fluid={fluid}, "
                   f"noise={noise_strength}, subdivision={subdivision}")

    def reset_physics_state(self):
        """Reset physics simulation state"""
        self.physics_system.vertices = None
        self.physics_system.velocities = None
        self.physics_system.springs = []
    
    def cycle_render_mode(self):
        """Cycle through render modes"""
        self.render_idx = (self.render_idx + 1) % len(self.render_modes)
    
    def get_render_mode(self):
        """Get current render mode"""
        return self.render_modes[self.render_idx]
    
    def set_shapes(self, shape_a: MorphShapes, shape_b: MorphShapes):
        """Set the shapes to morph between"""
        self.shape_a = shape_a
        self.shape_b = shape_b

class MidiHandler:
    """Enhanced MIDI handler with comprehensive CC and note support"""
    
    def __init__(self, morph_engine, audio_engine, midi_note_callback=None,
                 desired_port_substr='MPK', main_window=None):
        self.morph_engine = morph_engine
        self.audio_engine = audio_engine
        self.midi_note_callback = midi_note_callback
        self.desired_port_substr = desired_port_substr
        self.main_window = main_window  # Reference to main window for manual control flag
        self.midi_in = None
        self.connected_device = None
        self.available_ports = []
        
        # MIDI state tracking
        self.active_notes = set()
        self.cc_values = {}
        self.last_note_time = 0.0
        
        # Connect to MIDI device
        self._initialize_midi()
    
    def _initialize_midi(self):
        """Initialize MIDI connection"""
        if not HAS_MIDI:
            logger.warning("⚠️ MIDI not available")
            return
        
        try:
            midi = rtmidi.MidiIn()
            self.available_ports = []
            
            for i in range(midi.get_port_count()):
                port_name = midi.get_port_name(i)
                self.available_ports.append((i, port_name))
                logger.info(f"MIDI port {i}: {port_name}")
            
            if not self.available_ports:
                logger.warning('No MIDI ports found')
                return
            
            # Auto-connect to preferred device or first available
            port_idx = 0
            if self.desired_port_substr:
                for i, (idx, name) in enumerate(self.available_ports):
                    if self.desired_port_substr.lower() in name.lower():
                        port_idx = idx
                        break
            
            midi.open_port(port_idx)
            midi.set_callback(self._midi_callback)
            self.midi_in = midi
            self.connected_device = self.available_ports[port_idx][1]
            
            logger.info(f"✅ Connected to MIDI device: {self.connected_device}")
            
        except Exception as e:
            logger.error(f'❌ MIDI initialization failed: {e}')
            self.midi_in = None
    
    def _midi_callback(self, event, data=None):
        """Enhanced MIDI message callback"""
        try:
            msg, timestamp = event
            if not msg or len(msg) < 2:
                return
            
            status = msg[0]
            channel = (status & 0x0F) + 1
            command = status & 0xF0
            
            # Control Change messages
            if command == 0xB0 and len(msg) >= 3:
                cc = msg[1]
                value = msg[2]
                self.cc_values[cc] = value
                
                # CC1 -> Morph factor (only if not under manual control)
                if cc == 1:
                    manual_control_active = (self.main_window and
                                           hasattr(self.main_window, 'manual_morph_control') and
                                           self.main_window.manual_morph_control)
                    if not manual_control_active:
                        self.morph_engine.morph = value / 127.0
                        # Update slider to reflect MIDI control without triggering manual mode
                        if self.main_window and hasattr(self.main_window, 'morph_slider'):
                            # Block signals to prevent triggering manual control mode
                            self.main_window.morph_slider.blockSignals(True)
                            self.main_window.morph_slider.setValue(int(value / 127.0 * 100))
                            if hasattr(self.main_window, 'morph_value_label'):
                                self.main_window.morph_value_label.setText(f"{int(value / 127.0 * 100)}%")
                            self.main_window.morph_slider.blockSignals(False)
                        logger.debug(f"MIDI CC1: Morph set to {self.morph_engine.morph:.2f}")
                    else:
                        logger.debug(f"MIDI CC1 ignored: Manual control active")
                
                # CC2 -> Audio frequency
                elif cc == 2:
                    freq = 100.0 + (value / 127.0) * 900.0  # 100-1000 Hz range
                    self.audio_engine.set_frequency(freq)
                    logger.debug(f"MIDI CC2: Frequency set to {freq:.1f} Hz")
                
                # CC3 -> Audio amplitude
                elif cc == 3:
                    self.audio_engine.amplitude = (value / 127.0) * 0.5
                    logger.debug(f"MIDI CC3: Amplitude set to {self.audio_engine.amplitude:.2f}")
                
                # CC4-7 -> Shape selection
                elif cc in range(4, 8):
                    shape_index = value // 16  # 8 shapes per CC
                    shapes = list(MorphShapes)
                    if shape_index < len(shapes):
                        if cc == 4:  # Shape A
                            self.morph_engine.shape_a = shapes[shape_index]
                        elif cc == 5:  # Shape B
                            self.morph_engine.shape_b = shapes[shape_index]
                        logger.debug(f"MIDI CC{cc}: Shape set to {shapes[shape_index].value}")
            
            # Note On messages
            elif command == 0x90 and len(msg) >= 3 and msg[2] > 0:
                note = msg[1]
                velocity = msg[2]
                self.active_notes.add(note)
                self.last_note_time = time.time()
                
                # Convert note to frequency
                frequency = 440.0 * (2 ** ((note - 69) / 12.0))
                
                # Update global MIDI note frequency for MPK mode
                with audio_state.lock:
                    audio_state.midi_note_freq = frequency
                
                # Call note callback if provided
                if self.midi_note_callback:
                    try:
                        self.midi_note_callback(frequency, velocity, note)
                    except Exception as e:
                        logger.error(f"MIDI note callback error: {e}")
                
                logger.debug(f"MIDI Note On: Ch{channel} Note{note} Vel{velocity} ({frequency:.1f} Hz)")
            
            # Note Off messages
            elif command == 0x80 or (command == 0x90 and msg[2] == 0):
                note = msg[1]
                if note in self.active_notes:
                    self.active_notes.remove(note)
                logger.debug(f"MIDI Note Off: Ch{channel} Note{note}")
            
            # Program Change
            elif command == 0xC0:
                program = msg[1]
                # Cycle through render modes
                self.morph_engine.render_idx = program % len(self.morph_engine.render_modes)
                logger.debug(f"MIDI Program Change: {program} -> Render mode: {self.morph_engine.get_render_mode()}")
                
        except Exception as e:
            logger.error(f'❌ MIDI callback error: {e}')
    
    def disconnect(self):
        """Disconnect MIDI device"""
        if self.midi_in:
            try:
                self.midi_in.close_port()
                self.midi_in = None
                logger.info("✅ MIDI device disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting MIDI: {e}")

class ParticleSystem(QObject):
    """Advanced particle system with physics simulation"""
    
    particles_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.max_particles = 1000
        self.particles = CircularBuffer(self.max_particles)
        self.gravity = np.array([0.0, 0.0, -9.81])
        self.air_resistance = 0.01
        self.wind = np.array([0.0, 0.0, 0.0])
        
        # Particle emission parameters
        self.emission_rate = 0.0
        self.last_emission_time = 0.0
        
        # Physics update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16)  # ~60 FPS
        
    def emit_particles(self, position: np.ndarray, velocity: np.ndarray, 
                      count: int = 10, particle_type: ParticleType = ParticleType.SPARK,
                      size_range: Tuple[float, float] = (0.5, 2.0),
                      life_range: Tuple[float, float] = (1.0, 3.0)):
        """Emit particles with enhanced parameters"""
        new_particles = []
        for _ in range(count):
            # Add randomness to velocity and properties
            random_velocity = velocity + np.random.normal(0, 0.5, 3)
            random_position = position + np.random.normal(0, 0.1, 3)

            particle = Particle(
                position=random_position.copy(),
                velocity=random_velocity.copy(),
                color=self._get_particle_color(particle_type),
                size=np.random.uniform(*size_range),
                life=1.0,
                max_life=np.random.uniform(*life_range),
                mass=np.random.uniform(0.1, 1.0),
                particle_type=particle_type
            )
            new_particles.append(particle)

        # Add all particles efficiently with circular buffer
        self.particles.add_multiple(new_particles)
    
    def _get_particle_color(self, particle_type: ParticleType) -> np.ndarray:
        """Get color based on particle type with variations"""
        base_colors = {
            ParticleType.SPARK: [1.0, 1.0, 0.0, 1.0],      # Yellow
            ParticleType.BURST: [1.0, 0.5, 0.0, 1.0],      # Orange
            ParticleType.TRAIL: [0.0, 0.5, 1.0, 1.0],      # Blue
            ParticleType.BLOOM: [1.0, 0.0, 1.0, 1.0],      # Magenta
            ParticleType.EXPLOSION: [1.0, 0.0, 0.0, 1.0],  # Red
            ParticleType.SMOKE: [0.5, 0.5, 0.5, 0.8],      # Gray
            ParticleType.FIRE: [1.0, 0.3, 0.0, 1.0],       # Fire
            ParticleType.SNOW: [1.0, 1.0, 1.0, 1.0],       # White
        }
        
        base_color = base_colors.get(particle_type, [1.0, 1.0, 1.0, 1.0])
        
        # Add some color variation
        variation = np.random.uniform(-0.2, 0.2, 3)
        color = np.array(base_color)
        color[:3] = np.clip(color[:3] + variation, 0.0, 1.0)
        
        return color
    
    def update_particles(self):
        """Update particle physics with enhanced forces"""
        if len(self.particles) == 0:
            return

        dt = 1.0 / 60.0  # 60 FPS assumption
        current_time = time.time()

        # Remove expired particles efficiently
        self.particles.remove_expired(current_time)

        # Get active particles for physics update
        active_particles = self.particles.get_active_items()

        for particle in active_particles:
            # Update life
            particle.life -= dt / particle.max_life

            # Skip dead particles (will be cleaned up next frame)
            if particle.life <= 0:
                continue

            # Reset acceleration
            particle.acceleration = np.zeros(3)

            # Apply gravity
            particle.acceleration += self.gravity

            # Apply wind
            particle.acceleration += self.wind

            # Air resistance (drag)
            speed = np.linalg.norm(particle.velocity)
            if speed > 0:
                drag_force = -particle.velocity * speed * self.air_resistance
                particle.acceleration += drag_force / particle.mass

            # Update physics
            particle.velocity += particle.acceleration * dt
            particle.position += particle.velocity * dt

            # Update visual properties
            particle.color[3] = max(0.0, min(1.0, particle.life))  # Alpha fade
            particle.size *= 0.999  # Slight size reduction over time

            # Particle type specific behaviors
            if particle.particle_type == ParticleType.FIRE:
                # Fire particles rise and flicker
                particle.velocity[2] += 2.0 * dt
                particle.color[0] = min(1.0, particle.color[0] + np.random.uniform(-0.1, 0.1))

            elif particle.particle_type == ParticleType.SMOKE:
                # Smoke drifts and expands
                particle.velocity += np.random.normal(0, 0.5, 3) * dt
                particle.size += 0.01 * dt

            elif particle.particle_type == ParticleType.SNOW:
                # Snow falls gently with drift
                particle.velocity[2] = min(particle.velocity[2], -1.0)
                particle.velocity[:2] += np.random.normal(0, 0.2, 2) * dt

        # Emit update signal with active particles only
        if len(self.particles) > 0:
            self.particles_updated.emit(active_particles)

class LightingSystem(QObject):
    """Professional lighting system with animations and presets"""
    
    lights_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.max_lights = 50
        self.lights = CircularBuffer(self.max_lights)
        self.global_intensity = 1.0
        
        # Animation parameters
        self.animation_speed = 1.0
        self.strobe_frequency = 10.0
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_lights)
        self.timer.start(32)  # ~30 FPS for lighting updates
        
    def add_light(self, position: np.ndarray, color: np.ndarray, 
                 intensity: float = 1.0, light_type: LightType = LightType.POINT,
                 animation: LightAnimation = LightAnimation.STATIC, 
                 life_time: float = 10.0):
        """Add a new light with comprehensive parameters"""
        light = Light(
            position=position.copy(),
            color=color.copy(),
            intensity=intensity,
            light_type=light_type,
            animation=animation,
            life_time=life_time
        )

        # Add to circular buffer (automatically handles overflow)
        self.lights.add(light)
        logger.debug(f"Added {light_type.value} light at {position}")
    
    def update_lights(self):
        """Update light animations and lifecycle"""
        current_time = time.time()

        # Remove expired lights efficiently
        self.lights.remove_expired(current_time, 'life_time', 'created_time')

        # Get active lights for animation update
        active_lights = self.lights.get_active_items()

        for light in active_lights:
            # Check if light has expired (double check since we just cleaned)
            age = current_time - light.created_time
            if age > light.life_time:
                continue

            # Apply animations
            base_intensity = light.intensity * self.global_intensity

            if light.animation == LightAnimation.PULSE:
                pulse_factor = 0.5 + 0.5 * math.sin(current_time * 4 * self.animation_speed)
                light.intensity = base_intensity * pulse_factor

            elif light.animation == LightAnimation.BREATHE:
                breathe_factor = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(current_time * 1.5 * self.animation_speed))
                light.intensity = base_intensity * breathe_factor

            elif light.animation == LightAnimation.ROTATE:
                radius = math.sqrt(light.position[0]**2 + light.position[1]**2)
                angle = current_time * self.animation_speed
                light.position[0] = radius * math.cos(angle)
                light.position[1] = radius * math.sin(angle)

            elif light.animation == LightAnimation.STROBE:
                strobe_phase = (current_time * self.strobe_frequency) % 1.0
                light.intensity = base_intensity if strobe_phase < 0.5 else 0.0

            elif light.animation == LightAnimation.WAVE:
                wave_factor = 0.5 + 0.5 * math.sin(
                    current_time * 3 * self.animation_speed + light.position[0]
                )
                light.intensity = base_intensity * wave_factor

            elif light.animation == LightAnimation.RAINBOW:
                hue = (current_time * 0.5 * self.animation_speed) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                light.color[:3] = np.array(rgb)

        # Emit update signal with active lights only
        if len(self.lights) > 0:
            self.lights_updated.emit(active_lights)
    
    def clear_lights(self):
        """Clear all lights"""
        self.lights.clear()
    
    def apply_preset(self, preset_name: str):
        """Apply lighting presets"""
        self.clear_lights()
        
        if preset_name == "stadium":
            # High-intensity overhead lighting
            positions = [
                np.array([-10, -10, 8]), np.array([10, -10, 8]),
                np.array([-10, 10, 8]), np.array([10, 10, 8]),
                np.array([0, -15, 12]), np.array([0, 15, 12])
            ]
            for pos in positions:
                self.add_light(pos, np.array([1.0, 1.0, 1.0]), 
                             intensity=3.0, light_type=LightType.SPOT, life_time=60.0)
        
        elif preset_name == "club":
            # Colorful moving lights
            colors = [
                np.array([1.0, 0.0, 0.0]), np.array([0.0, 1.0, 0.0]),
                np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 1.0]),
                np.array([1.0, 1.0, 0.0]), np.array([0.0, 1.0, 1.0])
            ]
            for i, color in enumerate(colors):
                angle = i * math.pi / 3
                pos = np.array([5 * math.cos(angle), 5 * math.sin(angle), 3])
                self.add_light(pos, color, intensity=2.0, 
                             animation=LightAnimation.ROTATE, life_time=60.0)
        
        elif preset_name == "theater":
            # Warm theater lighting
            self.add_light(np.array([0, -8, 6]), np.array([1.0, 0.9, 0.7]),
                         intensity=2.0, light_type=LightType.SPOT, life_time=60.0)
            self.add_light(np.array([-3, 5, 4]), np.array([0.9, 0.8, 0.6]),
                         intensity=1.5, animation=LightAnimation.BREATHE, life_time=60.0)
            self.add_light(np.array([3, 5, 4]), np.array([0.9, 0.8, 0.6]),
                         intensity=1.5, animation=LightAnimation.BREATHE, life_time=60.0)
        
        elif preset_name == "ambient":
            # Soft ambient lighting
            self.add_light(np.array([0, 0, 10]), np.array([0.8, 0.8, 1.0]),
                         intensity=1.0, light_type=LightType.AMBIENT, life_time=60.0)
            self.add_light(np.array([5, 0, 3]), np.array([1.0, 0.8, 0.6]),
                         intensity=0.5, animation=LightAnimation.WAVE, life_time=60.0)
            self.add_light(np.array([-5, 0, 3]), np.array([0.6, 1.0, 0.8]),
                         intensity=0.5, animation=LightAnimation.WAVE, life_time=60.0)

def audio_analysis_thread(audio_engine, source_getter, frame_count=2048, sr=44100):
    """Enhanced audio analysis thread with multiple source support"""
    global audio_state
    
    logger.info("🎵 Audio analysis thread started")
    
    while audio_state.running:
        try:
            source = source_getter()
            y = None
            
            with audio_state.lock:
                audio_state.source_status = source
            
            # Generate or capture audio based on source
            if source == "Microphone" and HAS_SOUNDDEVICE:
                try:
                    # Record from microphone
                    data = sd.rec(int(frame_count), samplerate=sr, channels=1, blocking=True)
                    y = np.squeeze(data).astype(np.float32)
                    with audio_state.lock:
                        audio_state.source_status = "Microphone"
                except Exception as e:
                    logger.warning(f"Microphone capture failed: {e}")
                    source = "Sine"
                    with audio_state.lock:
                        audio_state.source_status = "Mic failed → Sine"
            
            elif source == "MPK Mini":
                # Generate sine wave from MIDI note
                with audio_state.lock:
                    freq = audio_state.midi_note_freq
                t = np.arange(frame_count) / float(sr)
                y = np.sin(2 * np.pi * freq * t).astype(np.float32)
                with audio_state.lock:
                    audio_state.source_status = "MPK Mini"
            
            else:  # Sine wave from audio engine
                freq = audio_engine.frequency
                t = np.arange(frame_count) / float(sr)
                y = np.sin(2 * np.pi * freq * t).astype(np.float32)
                with audio_state.lock:
                    audio_state.source_status = "Sine"
            
            # Analyze audio if we have data
            if y is not None and len(y) > 0:
                # Update audio engine buffer for analysis
                audio_engine.audio_buffer.extend(y)
                audio_engine._analyze_audio()
            
            # Sleep based on frame rate
            time.sleep(frame_count / float(sr))
            
        except Exception as e:
            logger.error(f"Audio analysis thread error: {e}")
            time.sleep(0.1)  # Brief pause before retry
    
    logger.info("🎵 Audio analysis thread stopped")

def non_blocking_audio_analysis_thread(audio_engine, source_getter, frame_count=2048, sr=44100):
    """Non-blocking audio analysis thread with ring buffer"""
    global audio_state

    logger.info("🎵 Non-blocking audio analysis thread started")

    # Create ring buffer for microphone input
    audio_buffer = AudioRingBuffer(max_size_seconds=2.0, sample_rate=sr, channels=1)

    while audio_state.running:
        try:
            # Check if audio processing is enabled
            with audio_state.lock:
                if not audio_state.audio_enabled:
                    audio_state.source_status = "Audio: Off - MIDI Active"
                    # Reset audio features to prevent stale data affecting visuals
                    audio_state.centroid_hz = 0.0
                    audio_state.amplitude = 0.0
                    time.sleep(0.1)  # Sleep when disabled
                    continue

            source = source_getter()
            y = None

            with audio_state.lock:
                audio_state.source_status = source

            # Generate or capture audio based on source
            if source == "Microphone" and HAS_SOUNDDEVICE:
                if not audio_buffer.is_running:
                    # Start non-blocking audio input
                    if audio_buffer.start_input():
                        with audio_state.lock:
                            audio_state.source_status = "Microphone (starting...)"
                    else:
                        # Fallback to sine wave
                        source = "Sine"
                        with audio_state.lock:
                            audio_state.source_status = "Mic failed → Sine"

                if audio_buffer.is_running:
                    # Try to get audio data from ring buffer (non-blocking)
                    y = audio_buffer.get_latest_frames(frame_count)
                    if y is not None:
                        with audio_state.lock:
                            audio_state.source_status = f"Microphone ({audio_buffer.get_buffer_level():.0f}% buffer)"
                    else:
                        # No data available yet, skip this iteration
                        time.sleep(0.01)  # Short sleep to prevent busy waiting
                        continue

            # If not microphone or microphone failed, stop audio buffer
            if source != "Microphone" and audio_buffer.is_running:
                audio_buffer.stop()

            if source == "MPK Mini":
                # Generate sine wave from MIDI note
                with audio_state.lock:
                    freq = audio_state.midi_note_freq
                t = np.arange(frame_count) / float(sr)
                y = np.sin(2 * np.pi * freq * t).astype(np.float32)
                with audio_state.lock:
                    audio_state.source_status = "MPK Mini"

            elif source != "Microphone":  # Sine wave from audio engine
                freq = audio_engine.frequency
                t = np.arange(frame_count) / float(sr)
                y = np.sin(2 * np.pi * freq * t).astype(np.float32)
                with audio_state.lock:
                    audio_state.source_status = "Sine"

            # Analyze audio if we have data
            if y is not None and len(y) > 0:
                # Basic amplitude analysis
                amplitude = np.sqrt(np.mean(y**2))

                # Advanced analysis (only if librosa available)
                if HAS_LIBROSA:
                    try:
                        # Spectral centroid (brightness)
                        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                        centroid_hz = np.mean(spectral_centroid)

                        # Spectral rolloff (brightness/harshness)
                        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
                        rolloff_hz = np.mean(spectral_rolloff)

                        # Zero crossing rate (texture)
                        zcr = librosa.feature.zero_crossing_rate(y)[0]
                        zcr_mean = np.mean(zcr)

                        # Onset detection
                        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
                        onset_detected = len(onset_frames) > 0

                        # Tempo estimation
                        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
                        tempo = float(tempo)

                        # Beat tracking
                        _, beat_frames = librosa.beat.beat_track(y=y, sr=sr, units='frames')
                        beat_detected = len(beat_frames) > 0

                    except Exception as e:
                        # Fallback to basic analysis
                        logger.debug(f"Advanced audio analysis failed: {e}")
                        centroid_hz = 1000.0
                        rolloff_hz = 2000.0
                        zcr_mean = 0.1
                        onset_detected = amplitude > 0.3
                        beat_detected = amplitude > 0.2
                        tempo = 120.0
                else:
                    # Basic analysis when librosa not available
                    centroid_hz = 1000.0
                    rolloff_hz = 2000.0
                    zcr_mean = 0.1
                    onset_detected = amplitude > 0.3
                    beat_detected = amplitude > 0.2
                    tempo = 120.0

                # Update global state
                with audio_state.lock:
                    audio_state.centroid_hz = centroid_hz
                    audio_state.amplitude = amplitude
                    audio_state.onset_detected = onset_detected
                    audio_state.beat_detected = beat_detected
                    audio_state.tempo = tempo

            # Small sleep to prevent excessive CPU usage
            time.sleep(0.005)  # 5ms sleep for ~200 FPS analysis rate

        except Exception as e:
            logger.error(f"Non-blocking audio analysis error: {e}")
            time.sleep(0.1)  # Brief pause before retry

    # Cleanup
    if audio_buffer.is_running:
        audio_buffer.stop()

    logger.info("🎵 Non-blocking audio analysis thread stopped")

class EnhancedGLWidget(QOpenGLWidget):
    """Enhanced OpenGL widget with advanced rendering capabilities"""
    
    def __init__(self, morph_engine: MorphingEngine, particle_system: ParticleSystem, 
                 lighting_system: LightingSystem):
        super().__init__()
        self.morph_engine = morph_engine
        self.particle_system = particle_system
        self.lighting_system = lighting_system

        # Modern rendering system
        self.modern_renderer = ModernRenderer()
        self.use_modern_rendering = False

        # Post-processing system
        self.post_processor = PostProcessingManager()
        self.use_post_processing = True

        # Optimized particle renderer
        self.particle_renderer = OptimizedParticleRenderer()
        self.use_optimized_particles = True

        # Quality controller for dynamic scaling
        self.quality_controller = QualityController()

        # Rendering state
        self.angle = 0.0
        self.zoom = 3.5
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        
        # Performance tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # ~60 FPS
        
        # Connect signals
        self.particle_system.particles_updated.connect(self._on_particles_updated)
        self.lighting_system.lights_updated.connect(self._on_lights_updated)
        
        # Cached data
        self.cached_particles = []
        self.cached_lights = []
    
    def initializeGL(self):
        """Initialize OpenGL settings"""
        if not OPENGL_AVAILABLE:
            return
            
        # Basic OpenGL setup
        glClearColor(0.05, 0.05, 0.1, 1.0)  # Dark blue background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        # Point and line sizes
        glPointSize(2.0)
        glLineWidth(1.5)
        
        # Try to initialize modern OpenGL rendering
        if self.modern_renderer.initialize():
            self.use_modern_rendering = True
            logger.info("✅ Modern OpenGL rendering enabled")

            # Create VBOs for morphing geometry
            self._create_modern_geometry()
        else:
            # Fall back to legacy OpenGL
            self.use_modern_rendering = False
            logger.info("⚠️ Using legacy OpenGL rendering")

            # Enable legacy lighting
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Initialize optimized particle renderer
        if self.use_optimized_particles:
            if self.particle_renderer.initialize():
                logger.info("✅ Optimized particle renderer initialized")
            else:
                self.use_optimized_particles = False
                logger.warning("⚠️ Falling back to basic particle rendering")

        # Initialize post-processing manager
        if self.use_post_processing:
            try:
                self.post_processor.initialize()
                logger.info("✅ Post-processing manager initialized")
            except Exception as e:
                self.use_post_processing = False
                logger.warning(f"⚠️ Post-processing disabled: {e}")

        logger.info("✅ OpenGL initialized")
    
    def resizeGL(self, w, h):
        """Handle window resize"""
        if not OPENGL_AVAILABLE:
            return
            
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect_ratio = w / h if h != 0 else 1.0
        gluPerspective(45.0, aspect_ratio, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)

        # Initialize post-processing for new size
        if self.use_post_processing:
            self.post_processor.initialize(w, h)

    def _create_modern_geometry(self):
        """Create VBOs for morphing geometry using modern OpenGL"""
        try:
            # Generate high-resolution sphere geometry for morphing
            vertices, normals, colors = self._generate_sphere_geometry(64)  # Higher resolution

            # Create VBO for morphing object
            self.modern_renderer.create_mesh_vbo('morph_object', vertices, normals, colors)

            logger.info(f"✅ Created modern geometry VBOs with {len(vertices)} vertices")

        except Exception as e:
            logger.error(f"Failed to create modern geometry: {e}")
            self.use_modern_rendering = False

    def _generate_sphere_geometry(self, resolution):
        """Generate sphere geometry with proper triangulation"""
        import numpy as np

        vertices = []
        normals = []
        colors = []

        # Generate sphere vertices using spherical coordinates
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                # Spherical coordinates
                theta = (i / resolution) * np.pi  # 0 to pi
                phi = (j / resolution) * 2 * np.pi  # 0 to 2pi

                # Convert to Cartesian coordinates
                x = np.sin(theta) * np.cos(phi)
                y = np.sin(theta) * np.sin(phi)
                z = np.cos(theta)

                vertices.append([x, y, z])
                normals.append([x, y, z])  # For a sphere, normal = position
                colors.append([1.0, 1.0, 1.0])  # Will be set dynamically

        # Generate triangulated mesh
        triangulated_vertices = []
        triangulated_normals = []
        triangulated_colors = []

        for i in range(resolution):
            for j in range(resolution):
                # Current quad vertices
                v1 = i * (resolution + 1) + j
                v2 = v1 + 1
                v3 = (i + 1) * (resolution + 1) + j
                v4 = v3 + 1

                # Triangle 1: v1, v2, v3
                triangulated_vertices.extend([vertices[v1], vertices[v2], vertices[v3]])
                triangulated_normals.extend([normals[v1], normals[v2], normals[v3]])
                triangulated_colors.extend([colors[v1], colors[v2], colors[v3]])

                # Triangle 2: v2, v4, v3
                triangulated_vertices.extend([vertices[v2], vertices[v4], vertices[v3]])
                triangulated_normals.extend([normals[v2], normals[v4], normals[v3]])
                triangulated_colors.extend([colors[v2], colors[v4], colors[v3]])

        return triangulated_vertices, triangulated_normals, triangulated_colors

    def _get_model_matrix(self):
        """Get model transformation matrix"""
        import numpy as np

        # Create identity matrix
        model = np.eye(4, dtype=np.float32)

        # Apply rotations (simplified for now)
        if self.morph_engine.rotation_enabled:
            angle_rad = np.radians(self.angle)
            # Simple rotation around Y axis for now
            cos_a = np.cos(angle_rad)
            sin_a = np.sin(angle_rad)
            model[0, 0] = cos_a
            model[0, 2] = sin_a
            model[2, 0] = -sin_a
            model[2, 2] = cos_a

        return model.flatten()

    def _get_view_matrix(self):
        """Get view transformation matrix"""
        import numpy as np

        # Create basic view matrix
        view = np.eye(4, dtype=np.float32)

        # Apply camera transformations
        # Translate by zoom
        view[3, 2] = -self.zoom

        # Apply rotations
        rx_rad = np.radians(self.rotation_x)
        ry_rad = np.radians(self.rotation_y)

        # Simple rotation matrices (could be improved)
        cos_x, sin_x = np.cos(rx_rad), np.sin(rx_rad)
        cos_y, sin_y = np.cos(ry_rad), np.sin(ry_rad)

        # Apply Y rotation
        view[0, 0] = cos_y
        view[0, 2] = sin_y
        view[2, 0] = -sin_y
        view[2, 2] = cos_y

        return view.flatten()

    def _get_projection_matrix(self):
        """Get projection transformation matrix"""
        import numpy as np

        # Create perspective projection matrix
        fov = np.radians(45.0)
        aspect = self.width() / self.height() if self.height() != 0 else 1.0
        near = 0.1
        far = 100.0

        f = 1.0 / np.tan(fov / 2.0)

        projection = np.zeros((4, 4), dtype=np.float32)
        projection[0, 0] = f / aspect
        projection[1, 1] = f
        projection[2, 2] = (far + near) / (near - far)
        projection[2, 3] = (2 * far * near) / (near - far)
        projection[3, 2] = -1.0

        return projection.flatten()

    def paintGL(self):
        """Main rendering function"""
        if not OPENGL_AVAILABLE:
            return
        
        start_time = time.time()
        
        # Clear buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Set up camera
        glTranslatef(0.0, 0.0, -self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        if self.morph_engine.rotation_enabled:
            self.angle = (self.angle + 0.5) % 360.0
            glRotatef(self.angle, 1.0, 1.0, 0.3)
        
        # Render main morphing object
        self._render_morph_object()
        
        # Render particles
        self._render_particles()
        
        # Render lights as small spheres
        self._render_lights()
        
        # Apply post-processing effects
        if self.use_post_processing and self.post_processor.use_post_processing:
            # Capture the rendered frame
            frame = self.post_processor.capture_frame()

            if frame is not None:
                # Process frame with effects
                processed_frame = self.post_processor.process_frame(frame)

                if processed_frame is not None:
                    # Clear and display processed frame
                    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
                    self.post_processor.display_processed_frame(processed_frame)

        # Update FPS counter
        self._update_fps()

        # Track render time
        render_time = time.time() - start_time
        
    def _render_morph_object(self):
        """Render the main morphing object"""
        if self.use_modern_rendering:
            self._render_morph_object_modern()
        else:
            self._render_morph_object_legacy()

    def _render_morph_object_modern(self):
        """Render using modern OpenGL pipeline"""
        try:
            import numpy as np

            # Create transformation matrices
            model_matrix = self._get_model_matrix()
            view_matrix = self._get_view_matrix()
            projection_matrix = self._get_projection_matrix()

            # Get current lights for rendering
            lights = self.cached_lights if self.cached_lights else []

            # Render the mesh
            self.modern_renderer.render_mesh(
                'morph_object',
                model_matrix,
                view_matrix,
                projection_matrix,
                lights
            )

        except Exception as e:
            logger.debug(f"Modern rendering failed, falling back to legacy: {e}")
            self.use_modern_rendering = False
            self._render_morph_object_legacy()

    def _render_morph_object_legacy(self):
        """Render using legacy OpenGL (original implementation)"""
        # Get morphed vertices
        vertices = self.morph_engine.get_morphed_vertices()
        
        # Apply spectral centroid to color mapping
        with audio_state.lock:
            centroid = audio_state.centroid_hz
            amplitude = audio_state.amplitude
        
        # Map centroid to color (0-4000 Hz -> blue to red)
        hue = min(max(centroid / 4000.0, 0.0), 1.0)
        r = hue
        g = 0.5 * (1 - hue) + 0.5 * hue
        b = 1.0 - hue
        
        # Add amplitude-based brightness
        brightness = 0.5 + 0.5 * min(amplitude * 10, 1.0)
        r *= brightness
        g *= brightness
        b *= brightness
        
        glColor4f(r, g, b, 0.8)
        
        # Render based on current mode
        render_mode = self.morph_engine.get_render_mode()
        
        if render_mode == 'dots':
            glBegin(GL_POINTS)
            for vertex in vertices:
                glVertex3f(vertex[0], vertex[1], vertex[2])
            glEnd()
        
        elif render_mode == 'wireframe':
            # Simple wireframe approximation
            glBegin(GL_LINES)
            res = self.morph_engine.resolution
            for i in range(len(vertices) - 1):
                if i % res != res - 1:  # Don't connect end of row to start of next
                    glVertex3f(vertices[i][0], vertices[i][1], vertices[i][2])
                    glVertex3f(vertices[i+1][0], vertices[i+1][1], vertices[i+1][2])
                if i < len(vertices) - res:  # Connect to vertex below
                    glVertex3f(vertices[i][0], vertices[i][1], vertices[i][2])
                    glVertex3f(vertices[i+res][0], vertices[i+res][1], vertices[i+res][2])
            glEnd()
        
        elif render_mode == 'solid' or render_mode == 'shaded':
            # Render as triangulated surface (simplified)
            glBegin(GL_TRIANGLES)
            res = self.morph_engine.resolution
            for i in range(res - 1):
                for j in range(res - 1):
                    idx = i * res + j
                    if idx + res + 1 < len(vertices):
                        # Triangle 1
                        glVertex3f(vertices[idx][0], vertices[idx][1], vertices[idx][2])
                        glVertex3f(vertices[idx + 1][0], vertices[idx + 1][1], vertices[idx + 1][2])
                        glVertex3f(vertices[idx + res][0], vertices[idx + res][1], vertices[idx + res][2])
                        
                        # Triangle 2
                        glVertex3f(vertices[idx + 1][0], vertices[idx + 1][1], vertices[idx + 1][2])
                        glVertex3f(vertices[idx + res + 1][0], vertices[idx + res + 1][1], vertices[idx + res + 1][2])
                        glVertex3f(vertices[idx + res][0], vertices[idx + res][1], vertices[idx + res][2])
            glEnd()
    
    def _render_particles(self):
        """Render particle system with optimized renderer"""
        if not self.cached_particles:
            return

        if self.use_optimized_particles:
            # Use optimized batched particle rendering
            self.particle_renderer.render_particles(self.cached_particles)
        else:
            # Fallback to basic point rendering
            glPointSize(8.0)  # Larger particles
            glBegin(GL_POINTS)

            for particle in self.cached_particles:
                # Set particle color
                color = particle.color
                glColor4f(color[0], color[1], color[2], color[3])

                # Render particle
                pos = particle.position
                glVertex3f(pos[0], pos[1], pos[2])

            glEnd()
            glPointSize(2.0)  # Reset
    
    def _render_lights(self):
        """Render lights as small colored spheres"""
        if not self.cached_lights:
            return
        
        for light in self.cached_lights:
            glPushMatrix()
            glTranslatef(light.position[0], light.position[1], light.position[2])
            
            # Set light color and intensity
            color = light.color * light.intensity
            glColor4f(color[0], color[1], color[2], 0.8)
            
            # Simple sphere approximation
            glPointSize(6.0)
            glBegin(GL_POINTS)
            glVertex3f(0.0, 0.0, 0.0)
            glEnd()
            
            glPopMatrix()
        
        glPointSize(2.0)  # Reset
    
    def update_scene(self):
        """Update scene and trigger repaint"""
        self.update()  # Trigger paintGL
    
    def _update_fps(self):
        """Update FPS counter and auto-adjust quality"""
        self.frame_count += 1
        current_time = time.time()

        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time

            # Auto-adjust quality based on performance
            if self.quality_controller.auto_adjust_quality(self.fps):
                self.quality_controller.apply_settings_to_renderer(self)
    
    def _on_particles_updated(self, particles):
        """Handle particle system updates"""
        self.cached_particles = particles
    
    def _on_lights_updated(self, lights):
        """Handle lighting system updates"""
        self.cached_lights = lights
    
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming"""
        delta = event.angleDelta().y()
        self.zoom -= delta / 1200.0
        self.zoom = max(1.0, min(20.0, self.zoom))
        self.update()
    
    def mousePressEvent(self, event):
        """Handle mouse press for rotation"""
        self.last_mouse_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement for rotation"""
        if hasattr(self, 'last_mouse_pos'):
            dx = event.pos().x() - self.last_mouse_pos.x()
            dy = event.pos().y() - self.last_mouse_pos.y()

            self.rotation_y += dx * 0.5
            self.rotation_x += dy * 0.5

            self.last_mouse_pos = event.pos()
            self.update()

    def set_particle_quality(self, quality_level):
        """Set particle rendering quality level"""
        if self.use_optimized_particles:
            self.particle_renderer.set_quality_level(quality_level)
            logger.debug(f"Particle quality set to {quality_level}")

    def set_post_processing_quality(self, enable_bloom=True, enable_color_grading=True):
        """Configure post-processing quality"""
        if self.use_post_processing:
            self.post_processor.enable_bloom = enable_bloom
            self.post_processor.enable_color_grading = enable_color_grading
            logger.debug(f"Post-processing: bloom={enable_bloom}, color_grading={enable_color_grading}")

    def get_rendering_stats(self):
        """Get current rendering performance statistics"""
        particle_count = len(self.cached_particles) if self.cached_particles else 0
        effective_particle_count = particle_count

        if self.use_optimized_particles:
            effective_particle_count = self.particle_renderer.get_particle_count_for_quality(particle_count)

        return {
            'fps': self.fps,
            'total_particles': particle_count,
            'rendered_particles': effective_particle_count,
            'lights': len(self.cached_lights) if self.cached_lights else 0,
            'modern_rendering': self.use_modern_rendering,
            'optimized_particles': self.use_optimized_particles,
            'post_processing': self.use_post_processing,
            'quality_info': self.quality_controller.get_quality_info()
        }

    def set_quality_preset(self, preset_name):
        """Set quality preset and apply to renderer"""
        if self.quality_controller.set_preset(preset_name):
            self.quality_controller.apply_settings_to_renderer(self)
            return True
        return False

    def toggle_auto_quality_scaling(self, enabled=None):
        """Toggle automatic quality scaling"""
        if enabled is None:
            self.quality_controller.auto_scaling = not self.quality_controller.auto_scaling
        else:
            self.quality_controller.auto_scaling = enabled
        logger.info(f"🎨 Auto quality scaling: {'enabled' if self.quality_controller.auto_scaling else 'disabled'}")

    def get_quality_presets(self):
        """Get available quality presets"""
        return list(self.quality_controller.quality_presets.keys())

    def integrate_with_frame_rate_manager(self, frame_rate_manager):
        """Integrate quality controller with adaptive frame rate manager"""
        self.frame_rate_manager = frame_rate_manager

        # Apply quality settings that affect frame rates
        settings = self.quality_controller.get_current_settings()
        multiplier = settings.get('update_interval_multiplier', 1.0)

        # Adjust frame rate manager based on quality settings
        if hasattr(frame_rate_manager, 'quality_level'):
            frame_rate_manager.quality_level = settings['particle_quality']

        logger.info(f"🔗 Quality controller integrated with frame rate manager (multiplier: {multiplier})")

    def apply_dynamic_quality_scaling(self):
        """Apply dynamic quality scaling based on current performance"""
        settings = self.quality_controller.get_recommended_settings_for_fps(self.fps)

        # Apply particle quality
        if hasattr(self.particle_renderer, 'set_quality_level'):
            self.particle_renderer.set_quality_level(settings['particle_quality'])

        # Apply post-processing settings
        if self.use_post_processing:
            self.post_processor.enable_bloom = settings['bloom_enabled']
            self.post_processor.enable_color_grading = settings['color_grading_enabled']

        logger.debug(f"🎨 Dynamic quality applied for {self.fps:.1f} FPS")

class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with comprehensive UI and features"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Enhanced MIDI Morphing Visualizer - Complete')
        self.setGeometry(100, 100, 1400, 1000)
        
        # Initialize core systems
        self.audio_engine = AudioEngine()
        self.morph_engine = MorphingEngine(resolution=32)
        self.particle_system = ParticleSystem()
        self.lighting_system = LightingSystem()
        self.memory_manager = MemoryManager()
        self.frame_rate_manager = AdaptiveFrameRateManager()

        # Manual control state
        self.manual_morph_control = False

        # Initialize OpenGL widget
        self.gl_widget = EnhancedGLWidget(self.morph_engine, self.particle_system, self.lighting_system)

        # Integrate quality controls with frame rate manager
        self.gl_widget.integrate_with_frame_rate_manager(self.frame_rate_manager)

        # Initialize MIDI handler with callbacks
        self.midi_handler = MidiHandler(
            self.morph_engine,
            self.audio_engine,
            midi_note_callback=self._on_midi_note,
            desired_port_substr='MPK',
            main_window=self
        )
        
        # Performance monitoring
        self.performance_metrics = PerformanceMetrics()
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self._update_performance_metrics)
        self.performance_timer.start(1000)  # Update every second
        
        # UI state
        self.current_scene_objects = []
        self.recording_session = False
        self.session_data = []
        
        # Setup UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._connect_signals()
        
        # Start audio analysis thread
        def get_audio_source():
            try:
                if hasattr(self, 'source_combo') and self.source_combo:
                    return self.source_combo.currentText().split()[0]  # Extract first word
                else:
                    return "Sine"  # Default fallback
            except RuntimeError:
                return "Sine"  # UI object deleted, return safe default
        
        self.analysis_thread = threading.Thread(
            target=non_blocking_audio_analysis_thread,
            args=(self.audio_engine, get_audio_source),
            daemon=True
        )
        self.analysis_thread.start()
        
        # UI update timer
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._update_ui)
        self.ui_timer.start(50)  # 20 FPS for UI updates
        
        # Initialize scene objects
        self._initialize_scene_objects()
        
        logger.info("🎉 Enhanced MIDI Morphing Visualizer initialized successfully!")
    
    def _setup_ui(self):
        """Setup the comprehensive user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - 3D visualization
        left_panel = QVBoxLayout()
        
        # Control bar
        control_bar = self._create_control_bar()
        left_panel.addWidget(control_bar)
        
        # 3D visualization
        self.gl_widget.setMinimumSize(800, 600)
        left_panel.addWidget(self.gl_widget)
        
        # Right panel - controls and monitoring
        right_panel = self._create_control_panel()
        
        # Add panels to main layout
        left_container = QWidget()
        left_container.setLayout(left_panel)
        
        main_layout.addWidget(left_container, 2)  # 2/3 of space
        main_layout.addWidget(right_panel, 1)     # 1/3 of space
    
    def _create_control_bar(self):
        """Create the top control bar"""
        control_widget = QWidget()
        control_widget.setMaximumHeight(80)
        layout = QHBoxLayout(control_widget)
        
        # Audio source selection
        audio_group = QGroupBox("Audio Source")
        audio_layout = QHBoxLayout(audio_group)
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(['Sine (Knob 2)', 'Microphone', 'MPK Mini'])
        self.source_combo.setCurrentIndex(0)
        audio_layout.addWidget(self.source_combo)
        
        self.audio_btn = QPushButton('Audio: Off')
        self.audio_btn.clicked.connect(self.toggle_audio)
        audio_layout.addWidget(self.audio_btn)
        
        layout.addWidget(audio_group)
        
        # Rendering controls
        render_group = QGroupBox("Rendering")
        render_layout = QHBoxLayout(render_group)
        
        self.render_btn = QPushButton('Render: Dots')
        self.render_btn.clicked.connect(self.cycle_render_mode)
        render_layout.addWidget(self.render_btn)
        
        self.rotation_btn = QPushButton('Rotation: On')
        self.rotation_btn.clicked.connect(self.toggle_rotation)
        render_layout.addWidget(self.rotation_btn)
        
        layout.addWidget(render_group)
        
        # Shape morphing controls
        morph_group = QGroupBox("Morphing")
        morph_layout = QHBoxLayout(morph_group)
        
        self.shape_a_combo = QComboBox()
        self.shape_a_combo.addItems([shape.value for shape in MorphShapes])
        self.shape_a_combo.setCurrentText('sphere')
        self.shape_a_combo.currentTextChanged.connect(self._on_shape_a_changed)
        
        self.shape_b_combo = QComboBox()
        self.shape_b_combo.addItems([shape.value for shape in MorphShapes])
        self.shape_b_combo.setCurrentText('cube')
        self.shape_b_combo.currentTextChanged.connect(self._on_shape_b_changed)
        
        morph_layout.addWidget(QLabel("A:"))
        morph_layout.addWidget(self.shape_a_combo)
        morph_layout.addWidget(QLabel("→"))
        morph_layout.addWidget(self.shape_b_combo)
        
        layout.addWidget(morph_group)
        
        # Status display
        self.status_display = QLabel('Ready')
        self.status_display.setMinimumWidth(200)
        self.status_display.setStyleSheet("QLabel { background-color: #2b2b2b; color: white; padding: 5px; border-radius: 3px; }")
        layout.addWidget(self.status_display)
        
        return control_widget
    
    def _create_control_panel(self):
        """Create the comprehensive control panel"""
        panel = QWidget()
        panel.setMaximumWidth(400)
        layout = QVBoxLayout(panel)
        
        # Tabbed interface
        tab_widget = QTabWidget()
        
        # Audio Analysis Tab
        audio_tab = self._create_audio_tab()
        tab_widget.addTab(audio_tab, "Audio")
        
        # MIDI Control Tab
        midi_tab = self._create_midi_tab()
        tab_widget.addTab(midi_tab, "MIDI")
        
        # Scene Management Tab
        scene_tab = self._create_scene_tab()
        tab_widget.addTab(scene_tab, "Scene")
        
        # Particles Tab
        particles_tab = self._create_particles_tab()
        tab_widget.addTab(particles_tab, "Particles")
        
        # Lighting Tab
        lighting_tab = self._create_lighting_tab()
        tab_widget.addTab(lighting_tab, "Lighting")
        
        # Performance Tab
        performance_tab = self._create_performance_tab()
        tab_widget.addTab(performance_tab, "Performance")
        
        layout.addWidget(tab_widget)
        return panel
    
    def _create_audio_tab(self):
        """Create audio analysis and control tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Audio parameters
        params_group = QGroupBox("Audio Parameters")
        params_layout = QGridLayout(params_group)
        
        # Sample rate
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(8000, 96000)
        self.sample_rate_spin.setValue(44100)
        self.sample_rate_spin.setSuffix(" Hz")
        params_layout.addWidget(QLabel("Sample Rate:"), 0, 0)
        params_layout.addWidget(self.sample_rate_spin, 0, 1)
        
        # Buffer size
        self.buffer_size_spin = QSpinBox()
        self.buffer_size_spin.setRange(256, 8192)
        self.buffer_size_spin.setValue(4096)
        self.buffer_size_spin.setSuffix(" samples")
        params_layout.addWidget(QLabel("Buffer Size:"), 1, 0)
        params_layout.addWidget(self.buffer_size_spin, 1, 1)
        
        # Frequency control (for sine mode)
        self.frequency_spin = QDoubleSpinBox()
        self.frequency_spin.setRange(20.0, 20000.0)
        self.frequency_spin.setValue(440.0)
        self.frequency_spin.setSuffix(" Hz")
        self.frequency_spin.valueChanged.connect(self._on_frequency_changed)
        params_layout.addWidget(QLabel("Frequency:"), 2, 0)
        params_layout.addWidget(self.frequency_spin, 2, 1)
        
        layout.addWidget(params_group)
        
        # Audio analysis display
        analysis_group = QGroupBox("Real-time Analysis")
        analysis_layout = QGridLayout(analysis_group)
        
        self.amplitude_label = QLabel("Amplitude: 0.00")
        self.centroid_label = QLabel("Spectral Centroid: 0.0 Hz")
        self.rolloff_label = QLabel("Spectral Rolloff: 0.0 Hz")
        self.zcr_label = QLabel("Zero Crossing Rate: 0.00")
        self.onset_label = QLabel("Onset: No")
        self.tempo_label = QLabel("Tempo: 120.0 BPM")
        
        analysis_layout.addWidget(self.amplitude_label, 0, 0)
        analysis_layout.addWidget(self.centroid_label, 0, 1)
        analysis_layout.addWidget(self.rolloff_label, 1, 0)
        analysis_layout.addWidget(self.zcr_label, 1, 1)
        analysis_layout.addWidget(self.onset_label, 2, 0)
        analysis_layout.addWidget(self.tempo_label, 2, 1)
        
        layout.addWidget(analysis_group)
        
        # Audio effects
        effects_group = QGroupBox("Audio Effects")
        effects_layout = QVBoxLayout(effects_group)
        
        self.onset_threshold_spin = QDoubleSpinBox()
        self.onset_threshold_spin.setRange(0.01, 2.0)
        self.onset_threshold_spin.setValue(0.3)
        self.onset_threshold_spin.setSingleStep(0.05)
        self.onset_threshold_spin.valueChanged.connect(self._on_onset_threshold_changed)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Onset Threshold:"))
        threshold_layout.addWidget(self.onset_threshold_spin)
        effects_layout.addLayout(threshold_layout)
        
        self.auto_particles_cb = QCheckBox("Auto Particle Emission on Onset")
        self.auto_particles_cb.setChecked(True)
        effects_layout.addWidget(self.auto_particles_cb)
        
        self.auto_lights_cb = QCheckBox("Auto Lighting on Beat")
        self.auto_lights_cb.setChecked(True)
        effects_layout.addWidget(self.auto_lights_cb)
        
        layout.addWidget(effects_group)
        
        tab.setWidget(content)
        return tab
    
    def _create_midi_tab(self):
        """Create MIDI control and monitoring tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # MIDI device info
        device_group = QGroupBox("MIDI Device")
        device_layout = QVBoxLayout(device_group)
        
        if self.midi_handler.connected_device:
            device_label = QLabel(f"Connected: {self.midi_handler.connected_device}")
            device_label.setStyleSheet("QLabel { color: green; }")
        else:
            device_label = QLabel("No MIDI device connected")
            device_label.setStyleSheet("QLabel { color: red; }")
        
        device_layout.addWidget(device_label)
        
        # Available ports
        if self.midi_handler.available_ports:
            ports_label = QLabel("Available ports:")
            device_layout.addWidget(ports_label)
            for idx, name in self.midi_handler.available_ports:
                port_label = QLabel(f"  {idx}: {name}")
                device_layout.addWidget(port_label)
        
        layout.addWidget(device_group)
        
        # MIDI mapping
        mapping_group = QGroupBox("Control Mapping")
        mapping_layout = QVBoxLayout(mapping_group)
        
        mappings = [
            "CC1: Morph Factor (0-127 → 0.0-1.0)",
            "CC2: Audio Frequency (0-127 → 100-1000 Hz)",
            "CC3: Audio Amplitude (0-127 → 0.0-0.5)",
            "CC4: Shape A Selection",
            "CC5: Shape B Selection",
            "Notes: Trigger particles & frequency",
            "Program Change: Render mode cycle"
        ]
        
        for mapping in mappings:
            label = QLabel(f"• {mapping}")
            label.setWordWrap(True)
            mapping_layout.addWidget(label)
        
        layout.addWidget(mapping_group)
        
        # MIDI monitor
        monitor_group = QGroupBox("MIDI Monitor")
        monitor_layout = QVBoxLayout(monitor_group)
        
        self.midi_log = QTextEdit()
        self.midi_log.setMaximumHeight(150)
        self.midi_log.setReadOnly(True)
        self.midi_log.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #00ff00; font-family: monospace; }")
        monitor_layout.addWidget(self.midi_log)
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.midi_log.clear)
        monitor_layout.addWidget(clear_btn)
        
        layout.addWidget(monitor_group)
        
        # Test controls
        test_group = QGroupBox("Test Controls")
        test_layout = QVBoxLayout(test_group)
        
        test_note_btn = QPushButton("Test MIDI Note Sequence")
        test_note_btn.clicked.connect(self._test_midi_sequence)
        test_layout.addWidget(test_note_btn)
        
        test_cc_btn = QPushButton("Test CC Controls")
        test_cc_btn.clicked.connect(self._test_cc_controls)
        test_layout.addWidget(test_cc_btn)
        
        layout.addWidget(test_group)
        
        tab.setWidget(content)
        return tab
    
    def _create_scene_tab(self):
        """Create scene management tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Scene presets
        presets_group = QGroupBox("Scene Presets")
        presets_layout = QGridLayout(presets_group)
        
        preset_buttons = [
            ("Default", self._load_default_scene),
            ("Piano", self._load_piano_scene),
            ("Drums", self._load_drums_scene),
            ("Orchestral", self._load_orchestral_scene)
        ]
        
        for i, (name, callback) in enumerate(preset_buttons):
            btn = QPushButton(name)
            btn.clicked.connect(callback)
            presets_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(presets_group)
        
        # Morph control
        morph_group = QGroupBox("Morph Control")
        morph_layout = QVBoxLayout(morph_group)
        
        # Manual morph slider
        self.morph_slider = QSlider(Qt.Horizontal)
        self.morph_slider.setRange(0, 100)
        self.morph_slider.setValue(0)
        self.morph_slider.valueChanged.connect(self._on_morph_slider_changed)
        
        morph_layout.addWidget(QLabel("Manual Morph Factor:"))
        morph_layout.addWidget(self.morph_slider)
        
        # Morph boost from audio
        self.morph_boost_label = QLabel("Audio Boost: 0.00")
        morph_layout.addWidget(self.morph_boost_label)
        
        # Auto-morph options
        self.auto_morph_cb = QCheckBox("Auto-morph from spectral centroid")
        self.auto_morph_cb.setChecked(False)  # DISABLED by default for manual control
        self.auto_morph_cb.stateChanged.connect(self._on_auto_morph_changed)
        morph_layout.addWidget(self.auto_morph_cb)

        # Manual control reset button
        reset_manual_btn = QPushButton("Enable MIDI Control")
        reset_manual_btn.setToolTip("Allow MIDI CC1 to control morphing")
        reset_manual_btn.clicked.connect(self._reset_manual_control)
        morph_layout.addWidget(reset_manual_btn)
        
        layout.addWidget(morph_group)
        
        # Scene objects list
        objects_group = QGroupBox("Scene Objects")
        objects_layout = QVBoxLayout(objects_group)
        
        self.objects_list = QTreeWidget()
        self.objects_list.setHeaderLabels(["Name", "Shape", "Note Range", "Active"])
        self.objects_list.setMaximumHeight(200)
        objects_layout.addWidget(self.objects_list)
        
        # Object controls
        obj_controls = QHBoxLayout()
        add_obj_btn = QPushButton("Add Object")
        remove_obj_btn = QPushButton("Remove Selected")
        obj_controls.addWidget(add_obj_btn)
        obj_controls.addWidget(remove_obj_btn)
        objects_layout.addLayout(obj_controls)
        
        layout.addWidget(objects_group)
        
        tab.setWidget(content)
        return tab
    
    def _create_particles_tab(self):
        """Create particle system control tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Particle parameters
        params_group = QGroupBox("Particle Parameters")
        params_layout = QGridLayout(params_group)
        
        self.max_particles_spin = QSpinBox()
        self.max_particles_spin.setRange(100, 10000)
        self.max_particles_spin.setValue(1000)
        self.max_particles_spin.valueChanged.connect(self._on_max_particles_changed)
        params_layout.addWidget(QLabel("Max Particles:"), 0, 0)
        params_layout.addWidget(self.max_particles_spin, 0, 1)
        
        self.gravity_spin = QDoubleSpinBox()
        self.gravity_spin.setRange(-50.0, 50.0)
        self.gravity_spin.setValue(-9.81)
        self.gravity_spin.setSingleStep(1.0)
        self.gravity_spin.valueChanged.connect(self._on_gravity_changed)
        params_layout.addWidget(QLabel("Gravity:"), 1, 0)
        params_layout.addWidget(self.gravity_spin, 1, 1)
        
        self.air_resistance_spin = QDoubleSpinBox()
        self.air_resistance_spin.setRange(0.0, 1.0)
        self.air_resistance_spin.setValue(0.01)
        self.air_resistance_spin.setSingleStep(0.01)
        self.air_resistance_spin.valueChanged.connect(self._on_air_resistance_changed)
        params_layout.addWidget(QLabel("Air Resistance:"), 2, 0)
        params_layout.addWidget(self.air_resistance_spin, 2, 1)
        
        layout.addWidget(params_group)
        
        # Particle emission
        emission_group = QGroupBox("Particle Emission")
        emission_layout = QGridLayout(emission_group)
        
        particle_types = list(ParticleType)
        for i, ptype in enumerate(particle_types):
            btn = QPushButton(f"Emit {ptype.value.title()}")
            btn.clicked.connect(lambda checked, pt=ptype: self._emit_test_particles(pt))
            emission_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addWidget(emission_group)
        
        # Particle statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.particle_count_label = QLabel("Active Particles: 0")
        self.emission_rate_label = QLabel("Emission Rate: 0/s")
        
        stats_layout.addWidget(self.particle_count_label)
        stats_layout.addWidget(self.emission_rate_label)
        
        layout.addWidget(stats_group)
        
        tab.setWidget(content)
        return tab
    
    def _create_lighting_tab(self):
        """Create lighting system control tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Lighting parameters
        params_group = QGroupBox("Lighting Parameters")
        params_layout = QGridLayout(params_group)
        
        self.max_lights_spin = QSpinBox()
        self.max_lights_spin.setRange(10, 200)
        self.max_lights_spin.setValue(50)
        self.max_lights_spin.valueChanged.connect(self._on_max_lights_changed)
        params_layout.addWidget(QLabel("Max Lights:"), 0, 0)
        params_layout.addWidget(self.max_lights_spin, 0, 1)
        
        self.global_intensity_spin = QDoubleSpinBox()
        self.global_intensity_spin.setRange(0.0, 5.0)
        self.global_intensity_spin.setValue(1.0)
        self.global_intensity_spin.setSingleStep(0.1)
        self.global_intensity_spin.valueChanged.connect(self._on_global_intensity_changed)
        params_layout.addWidget(QLabel("Global Intensity:"), 1, 0)
        params_layout.addWidget(self.global_intensity_spin, 1, 1)
        
        layout.addWidget(params_group)
        
        # Light presets
        presets_group = QGroupBox("Lighting Presets")
        presets_layout = QGridLayout(presets_group)
        
        preset_buttons = [
            ("Stadium", lambda: self.lighting_system.apply_preset("stadium")),
            ("Club", lambda: self.lighting_system.apply_preset("club")),
            ("Theater", lambda: self.lighting_system.apply_preset("theater")),
            ("Ambient", lambda: self.lighting_system.apply_preset("ambient")),
            ("Clear All", self.lighting_system.clear_lights)
        ]
        
        for i, (name, callback) in enumerate(preset_buttons):
            btn = QPushButton(name)
            btn.clicked.connect(callback)
            presets_layout.addWidget(btn, i // 3, i % 3)
        
        layout.addWidget(presets_group)
        
        # Manual light controls
        manual_group = QGroupBox("Manual Light Control")
        manual_layout = QGridLayout(manual_group)
        
        light_types = list(LightType)
        for i, ltype in enumerate(light_types):
            btn = QPushButton(f"Add {ltype.value.title()}")
            btn.clicked.connect(lambda checked, lt=ltype: self._add_manual_light(lt))
            manual_layout.addWidget(btn, i // 3, i % 3)
        
        layout.addWidget(manual_group)
        
        # Animation controls
        animation_group = QGroupBox("Animation Controls")
        animation_layout = QGridLayout(animation_group)
        
        self.animation_speed_spin = QDoubleSpinBox()
        self.animation_speed_spin.setRange(0.1, 5.0)
        self.animation_speed_spin.setValue(1.0)
        self.animation_speed_spin.setSingleStep(0.1)
        self.animation_speed_spin.valueChanged.connect(self._on_animation_speed_changed)
        animation_layout.addWidget(QLabel("Animation Speed:"), 0, 0)
        animation_layout.addWidget(self.animation_speed_spin, 0, 1)
        
        layout.addWidget(animation_group)
        
        # Lighting statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.light_count_label = QLabel("Active Lights: 0")
        stats_layout.addWidget(self.light_count_label)
        
        layout.addWidget(stats_group)
        
        tab.setWidget(content)
        return tab
    
    def _create_performance_tab(self):
        """Create performance monitoring tab"""
        tab = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)
        
        # Performance metrics
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QGridLayout(metrics_group)
        
        self.fps_label = QLabel("FPS: 0.0")
        self.frame_time_label = QLabel("Frame Time: 0.0 ms")
        self.memory_label = QLabel("Memory: 0 MB")
        self.cpu_label = QLabel("CPU: 0.0%")
        
        metrics_layout.addWidget(self.fps_label, 0, 0)
        metrics_layout.addWidget(self.frame_time_label, 0, 1)
        metrics_layout.addWidget(self.memory_label, 1, 0)
        metrics_layout.addWidget(self.cpu_label, 1, 1)
        
        layout.addWidget(metrics_group)
        
        # System information
        system_group = QGroupBox("System Information")
        system_layout = QVBoxLayout(system_group)
        
        system_info = [
            f"Qt Available: {'✅ Yes' if QT_AVAILABLE else '❌ No'}",
            f"OpenGL Available: {'✅ Yes' if OPENGL_AVAILABLE else '❌ No'}",
            f"PyVista Available: {'✅ Yes' if HAS_PYVISTA else '❌ No'}",
            f"Audio Available: {'✅ Yes' if HAS_AUDIO else '❌ No'}",
            f"Librosa Available: {'✅ Yes' if HAS_LIBROSA else '❌ No'}",
            f"MIDI Available: {'✅ Yes' if HAS_MIDI else '❌ No'}"
        ]
        
        for info in system_info:
            label = QLabel(info)
            if "✅" in info:
                label.setStyleSheet("QLabel { color: green; }")
            elif "❌" in info:
                label.setStyleSheet("QLabel { color: red; }")
            system_layout.addWidget(label)
        
        layout.addWidget(system_group)
        
        # Performance controls
        controls_group = QGroupBox("Performance Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        self.vsync_cb = QCheckBox("Enable V-Sync")
        self.vsync_cb.setChecked(True)
        controls_layout.addWidget(self.vsync_cb)
        
        self.high_quality_cb = QCheckBox("High Quality Rendering")
        self.high_quality_cb.setChecked(True)
        controls_layout.addWidget(self.high_quality_cb)
        
        # Performance actions
        gc_btn = QPushButton("Force Garbage Collection")
        gc_btn.clicked.connect(self._force_garbage_collection)
        controls_layout.addWidget(gc_btn)
        
        layout.addWidget(controls_group)
        
        tab.setWidget(content)
        return tab
    
    def _setup_menu_bar(self):
        """Setup the application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New Session', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self._new_session)
        file_menu.addAction(new_action)
        
        load_action = QAction('&Load Session...', self)
        load_action.setShortcut('Ctrl+O')
        load_action.triggered.connect(self._load_session)
        file_menu.addAction(load_action)
        
        save_action = QAction('&Save Session...', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self._save_session)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        fullscreen_action = QAction('Toggle &Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        record_action = QAction('Start &Recording', self)
        record_action.setShortcut('Ctrl+R')
        record_action.triggered.connect(self._toggle_recording)
        tools_menu.addAction(record_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """Setup the application status bar"""
        self.statusbar = self.statusBar()
        
        # Status indicators
        self.audio_status = QLabel("Audio: ⏸️ Stopped")
        self.midi_status = QLabel("MIDI: ⏸️ Disconnected")
        self.performance_status = QLabel("FPS: 0.0")
        
        self.statusbar.addPermanentWidget(self.audio_status)
        self.statusbar.addPermanentWidget(self.midi_status)
        self.statusbar.addPermanentWidget(self.performance_status)
        
        self.statusbar.showMessage("Enhanced MIDI Morphing Visualizer Ready")
    
    def _connect_signals(self):
        """Connect all signal-slot connections"""
        # Particle system signals
        self.particle_system.particles_updated.connect(self._on_particles_updated)
        
        # Lighting system signals
        self.lighting_system.lights_updated.connect(self._on_lights_updated)
    
    def _initialize_scene_objects(self):
        """Initialize default scene objects"""
        default_objects = [
            {
                'name': 'Bass',
                'position': np.array([-2.0, -1.0, 0.0]),
                'note_range': (24, 47),  # C1-B2
                'color': np.array([0.2, 0.2, 1.0, 1.0]),  # Blue
                'shape': MorphShapes.SPHERE
            },
            {
                'name': 'Melody', 
                'position': np.array([0.0, 1.0, 0.0]),
                'note_range': (48, 71),  # C3-B4
                'color': np.array([0.2, 1.0, 0.2, 1.0]),  # Green
                'shape': MorphShapes.CUBE
            },
            {
                'name': 'Treble',
                'position': np.array([2.0, -1.0, 0.0]),
                'note_range': (72, 95),  # C5-B6
                'color': np.array([1.0, 0.6, 0.2, 1.0]),  # Orange
                'shape': MorphShapes.CYLINDER
            },
            {
                'name': 'High',
                'position': np.array([0.0, 0.0, 2.0]),
                'note_range': (96, 127),  # C7-G9
                'color': np.array([1.0, 0.2, 1.0, 1.0]),  # Magenta
                'shape': MorphShapes.TORUS
            }
        ]
        
        for obj_data in default_objects:
            obj = SceneObject(
                name=obj_data['name'],
                position=obj_data['position'],
                color=obj_data['color'],
                note_range=obj_data['note_range'],
                current_shape=obj_data['shape'],
                target_shape=obj_data['shape']
            )
            self.current_scene_objects.append(obj)
        
        self._update_objects_list()
    
    def _update_objects_list(self):
        """Update the scene objects list display"""
        self.objects_list.clear()
        
        for obj in self.current_scene_objects:
            item = QTreeWidgetItem([
                obj.name,
                obj.current_shape.value,
                f"{obj.note_range[0]}-{obj.note_range[1]}",
                "Yes" if obj.active else "No"
            ])
            self.objects_list.addTopLevelItem(item)
    
    # Event handlers and callbacks
    def _on_midi_note(self, frequency, velocity, note):
        """Handle MIDI note events"""
        # Find corresponding scene object
        for obj in self.current_scene_objects:
            if obj.note_range[0] <= note <= obj.note_range[1] and obj.active:
                # Trigger particle emission
                if self.auto_particles_cb.isChecked():
                    particle_count = max(5, velocity // 8)
                    self.particle_system.emit_particles(
                        obj.position,
                        np.array([0, 0, 3]) * (velocity / 127.0),
                        count=particle_count,
                        particle_type=ParticleType.SPARK
                    )
                
                # Add lighting effect
                if self.auto_lights_cb.isChecked():
                    # Note-based color
                    hue = (note % 12) / 12.0
                    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    
                    self.lighting_system.add_light(
                        obj.position + np.array([0, 0, 1]),
                        np.array(rgb),
                        intensity=velocity / 127.0 * 2.0,
                        animation=LightAnimation.PULSE,
                        life_time=3.0
                    )
                
                # Update object color
                hue = (note % 12) / 12.0
                rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                obj.color[:3] = rgb
                
                # Scale based on velocity
                scale_factor = 1.0 + (velocity / 127.0) * 0.5
                obj.scale = np.array([scale_factor, scale_factor, scale_factor])
                
                break
        
        # Log MIDI message
        self.midi_log.append(f"Note: {note} ({hz_to_note_name(frequency)}) Vel: {velocity}")
        self._trim_midi_log()
    
    def _trim_midi_log(self):
        """Keep MIDI log to reasonable size"""
        text = self.midi_log.toPlainText().split('\n')
        if len(text) > 50:
            self.midi_log.clear()
            self.midi_log.append('\n'.join(text[-30:]))  # Keep last 30 lines
    
    def _on_particles_updated(self, particles):
        """Handle particle system updates"""
        self.particle_count_label.setText(f"Active Particles: {len(particles)}")
        self.performance_metrics.particle_count = len(particles)
    
    def _on_lights_updated(self, lights):
        """Handle lighting system updates"""
        self.light_count_label.setText(f"Active Lights: {len(lights)}")
        self.performance_metrics.light_count = len(lights)
    
    # UI Control Handlers
    def toggle_audio(self):
        """Toggle audio output"""
        if self.audio_engine.is_running:
            self.audio_engine.stop()
            self.audio_btn.setText('Audio: Off')
            self.audio_status.setText("Audio: ⏸️ Stopped")
            # Disable audio analysis processing
            with audio_state.lock:
                audio_state.audio_enabled = False
        else:
            source = self.source_combo.currentText().split()[0]
            if source == "Sine":
                success = self.audio_engine.start_output()
            else:
                success = self.audio_engine.start_input()

            if success:
                self.audio_btn.setText('Audio: On')
                self.audio_status.setText("Audio: 🎵 Active")
                # Enable audio analysis processing
                with audio_state.lock:
                    audio_state.audio_enabled = True
            else:
                QMessageBox.warning(self, "Audio Error", "Failed to start audio system")
    
    def cycle_render_mode(self):
        """Cycle through render modes"""
        self.morph_engine.cycle_render_mode()
        mode = self.morph_engine.get_render_mode().title()
        self.render_btn.setText(f'Render: {mode}')
    
    def toggle_rotation(self):
        """Toggle rotation"""
        self.morph_engine.rotation_enabled = not self.morph_engine.rotation_enabled
        state = 'On' if self.morph_engine.rotation_enabled else 'Off'
        self.rotation_btn.setText(f'Rotation: {state}')
    
    def _on_shape_a_changed(self, shape_name):
        """Handle shape A selection change"""
        try:
            shape = MorphShapes(shape_name)
            self.morph_engine.shape_a = shape
        except ValueError:
            pass
    
    def _on_shape_b_changed(self, shape_name):
        """Handle shape B selection change"""
        try:
            shape = MorphShapes(shape_name)
            self.morph_engine.shape_b = shape
        except ValueError:
            pass
    
    def _on_frequency_changed(self, value):
        """Handle frequency change"""
        self.audio_engine.set_frequency(value)
    
    def _on_morph_slider_changed(self, value):
        """Handle manual morph slider change"""
        manual_morph = value / 100.0
        # Set manual control flag to prevent MIDI override
        self.manual_morph_control = True
        # Immediately apply morph if auto-morph is disabled
        if not self.auto_morph_cb.isChecked():
            self.morph_engine.morph = manual_morph
            logger.debug(f"Manual morph slider: {manual_morph:.2f}")

    def _on_auto_morph_changed(self, state):
        """Handle auto-morph checkbox change"""
        if state == Qt.Checked:
            # When enabling auto-morph, reset manual control
            self.manual_morph_control = False
            logger.debug("Auto-morph enabled: MIDI control restored")

    def _reset_manual_control(self):
        """Reset manual control flag to allow MIDI control"""
        self.manual_morph_control = False
        logger.debug("Manual control reset: MIDI control restored")
        
    def _on_onset_threshold_changed(self, value):
        """Handle onset threshold change"""
        self.audio_engine.onset_threshold = value
    
    def _on_max_particles_changed(self, value):
        """Handle max particles change"""
        self.particle_system.max_particles = value
    
    def _on_gravity_changed(self, value):
        """Handle gravity change"""
        self.particle_system.gravity[2] = value
    
    def _on_air_resistance_changed(self, value):
        """Handle air resistance change"""
        self.particle_system.air_resistance = value
    
    def _on_max_lights_changed(self, value):
        """Handle max lights change"""
        self.lighting_system.max_lights = value
    
    def _on_global_intensity_changed(self, value):
        """Handle global intensity change"""
        self.lighting_system.global_intensity = value
    
    def _on_animation_speed_changed(self, value):
        """Handle animation speed change"""
        self.lighting_system.animation_speed = value
    
    # Test functions
    def _test_midi_sequence(self):
        """Test MIDI note sequence"""
        test_notes = [36, 48, 60, 72, 84, 96]  # Different octaves
        for i, note in enumerate(test_notes):
            QTimer.singleShot(i * 300, lambda n=note: self._on_midi_note(
                440.0 * (2 ** ((n - 69) / 12.0)), 100, n))
    
    def _test_cc_controls(self):
        """Test CC controls"""
        # Animate morph factor
        for i in range(0, 128, 8):
            QTimer.singleShot(i * 50, lambda v=i: setattr(self.morph_engine, 'morph', v/127.0))
    
    def _emit_test_particles(self, particle_type):
        """Emit test particles"""
        center_pos = np.array([0, 0, 1])
        velocity = np.array([
            np.random.uniform(-3, 3),
            np.random.uniform(-3, 3),
            np.random.uniform(0, 8)
        ])
        self.particle_system.emit_particles(
            center_pos, velocity, count=30, particle_type=particle_type
        )
    
    def _add_manual_light(self, light_type):
        """Add manual light"""
        position = np.array([
            np.random.uniform(-3, 3),
            np.random.uniform(-3, 3),
            np.random.uniform(0, 4)
        ])
        color = np.array([np.random.random(), np.random.random(), np.random.random()])
        
        self.lighting_system.add_light(
            position, color, intensity=1.5, light_type=light_type, life_time=10.0
        )
    
    # Scene management
    def _load_default_scene(self):
        """Load default scene"""
        self.current_scene_objects.clear()
        self._initialize_scene_objects()
    
    def _load_piano_scene(self):
        """Load piano-optimized scene"""
        self.current_scene_objects.clear()
        # Add piano-specific objects with appropriate ranges
        piano_objects = [
            {'name': 'Bass Keys', 'range': (21, 35), 'shape': MorphShapes.CUBE, 'color': [0.8, 0.2, 0.2, 1.0]},
            {'name': 'Low Mid', 'range': (36, 50), 'shape': MorphShapes.CYLINDER, 'color': [0.2, 0.8, 0.2, 1.0]},
            {'name': 'High Mid', 'range': (51, 65), 'shape': MorphShapes.SPHERE, 'color': [0.2, 0.2, 0.8, 1.0]},
            {'name': 'Treble', 'range': (66, 88), 'shape': MorphShapes.TORUS, 'color': [0.8, 0.8, 0.2, 1.0]},
        ]
        
        for i, obj_data in enumerate(piano_objects):
            angle = i * math.pi / 2
            position = np.array([2 * math.cos(angle), 2 * math.sin(angle), 0])
            
            obj = SceneObject(
                name=obj_data['name'],
                position=position,
                color=np.array(obj_data['color']),
                note_range=obj_data['range'],
                current_shape=obj_data['shape'],
                target_shape=obj_data['shape']
            )
            self.current_scene_objects.append(obj)
        
        self._update_objects_list()
        self.lighting_system.apply_preset("theater")
    
    def _load_drums_scene(self):
        """Load drums-optimized scene"""
        self.current_scene_objects.clear()
        # Typical drum kit MIDI mapping
        drum_objects = [
            {'name': 'Kick', 'range': (35, 36), 'shape': MorphShapes.SPHERE, 'color': [1.0, 0.3, 0.3, 1.0]},
            {'name': 'Snare', 'range': (37, 40), 'shape': MorphShapes.CYLINDER, 'color': [0.3, 1.0, 0.3, 1.0]},
            {'name': 'Hi-Hat', 'range': (42, 44), 'shape': MorphShapes.CONE, 'color': [0.3, 0.3, 1.0, 1.0]},
            {'name': 'Toms', 'range': (45, 50), 'shape': MorphShapes.TORUS, 'color': [1.0, 1.0, 0.3, 1.0]},
            {'name': 'Cymbals', 'range': (51, 59), 'shape': MorphShapes.PLANE, 'color': [1.0, 0.3, 1.0, 1.0]},
        ]
        
        for i, obj_data in enumerate(drum_objects):
            angle = i * 2 * math.pi / 5
            radius = 1.5 + 0.5 * (i % 2)
            position = np.array([radius * math.cos(angle), radius * math.sin(angle), 0])
            
            obj = SceneObject(
                name=obj_data['name'],
                position=position,
                color=np.array(obj_data['color']),
                note_range=obj_data['range'],
                current_shape=obj_data['shape'],
                target_shape=obj_data['shape']
            )
            self.current_scene_objects.append(obj)
        
        self._update_objects_list()
        self.lighting_system.apply_preset("club")
    
    def _load_orchestral_scene(self):
        """Load orchestral scene"""
        self.current_scene_objects.clear()
        # Orchestral instrument ranges
        orch_objects = [
            {'name': 'Double Bass', 'range': (28, 43), 'shape': MorphShapes.CYLINDER, 'color': [0.6, 0.3, 0.1, 1.0]},
            {'name': 'Cello', 'range': (36, 72), 'shape': MorphShapes.HEART, 'color': [0.8, 0.4, 0.2, 1.0]},
            {'name': 'Violin', 'range': (55, 103), 'shape': MorphShapes.SPIRAL, 'color': [1.0, 0.8, 0.4, 1.0]},
            {'name': 'Flute', 'range': (60, 96), 'shape': MorphShapes.HELIX, 'color': [0.7, 0.9, 1.0, 1.0]},
            {'name': 'Trumpet', 'range': (55, 82), 'shape': MorphShapes.CONE, 'color': [1.0, 0.8, 0.2, 1.0]},
        ]
        
        positions = [
            np.array([-3, -2, 0]), np.array([-1, -1, 0]), np.array([1, 1, 0]),
            np.array([0, 3, 1]), np.array([2, 0, 1])
        ]
        
        for obj_data, position in zip(orch_objects, positions):
            obj = SceneObject(
                name=obj_data['name'],
                position=position,
                color=np.array(obj_data['color']),
                note_range=obj_data['range'],
                current_shape=obj_data['shape'],
                target_shape=obj_data['shape']
            )
            self.current_scene_objects.append(obj)
        
        self._update_objects_list()
        self.lighting_system.apply_preset("theater")
    
    # Menu actions
    def _new_session(self):
        """Create new session"""
        reply = QMessageBox.question(self, 'New Session', 
                                   'This will clear the current session. Continue?',
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.particle_system.particles.clear()
            self.lighting_system.clear_lights()
            self._load_default_scene()
            self.session_data.clear()
            self.statusbar.showMessage("New session created", 3000)
    
    def _load_session(self):
        """Load session from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Load Session', '', 'JSON Files (*.json)')
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    session_data = json.load(f)
                
                # Load session parameters
                if 'morph_factor' in session_data:
                    self.morph_slider.setValue(int(session_data['morph_factor'] * 100))
                
                if 'audio_frequency' in session_data:
                    self.frequency_spin.setValue(session_data['audio_frequency'])
                    self.audio_engine.set_frequency(session_data['audio_frequency'])
                
                if 'shapes' in session_data:
                    self.shape_a_combo.setCurrentText(session_data['shapes']['shape_a'])
                    self.shape_b_combo.setCurrentText(session_data['shapes']['shape_b'])
                
                self.statusbar.showMessage(f"Session loaded from {file_path}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load session:\n{e}')
    
    def _save_session(self):
        """Save current session to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save Session', '', 'JSON Files (*.json)')
        
        if file_path:
            try:
                session_data = {
                    'timestamp': time.time(),
                    'version': '5.0 Complete',
                    'morph_factor': self.morph_engine.morph,
                    'audio_frequency': self.audio_engine.frequency,
                    'shapes': {
                        'shape_a': self.morph_engine.shape_a.value,
                        'shape_b': self.morph_engine.shape_b.value
                    },
                    'render_mode': self.morph_engine.get_render_mode(),
                    'scene_objects': [
                        {
                            'name': obj.name,
                            'position': obj.position.tolist(),
                            'note_range': obj.note_range,
                            'color': obj.color.tolist(),
                            'shape': obj.current_shape.value
                        }
                        for obj in self.current_scene_objects
                    ],
                    'performance_data': self.session_data[-100:] if self.recording_session else [],
                    'particle_settings': {
                        'max_particles': self.particle_system.max_particles,
                        'gravity': self.particle_system.gravity[2],
                        'air_resistance': self.particle_system.air_resistance
                    },
                    'lighting_settings': {
                        'max_lights': self.lighting_system.max_lights,
                        'global_intensity': self.lighting_system.global_intensity,
                        'animation_speed': self.lighting_system.animation_speed
                    }
                }
                
                with open(file_path, 'w') as f:
                    json.dump(session_data, f, indent=2)
                
                self.statusbar.showMessage(f"Session saved to {file_path}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save session:\n{e}')
    
    def _toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def _toggle_recording(self):
        """Toggle session recording"""
        self.recording_session = not self.recording_session
        
        if self.recording_session:
            self.statusbar.showMessage("Recording started", 3000)
        else:
            self.statusbar.showMessage(f"Recording stopped - {len(self.session_data)} data points", 3000)
    
    def _show_about(self):
        """Show about dialog"""
        about_text = """
        Enhanced MIDI Morphing Visualizer - Complete Implementation
        Version 5.0 Complete
        
        🎵 Advanced Audio Analysis with Spectral Features
        🎹 Comprehensive MIDI Integration & Device Management  
        ✨ Physics-Based Particle System (8 Particle Types)
        💡 Professional Lighting System (5 Light Types, 7 Animations)
        🎭 20+ Geometric Shapes for Real-time Morphing
        📊 Real-time Performance Monitoring & Optimization
        🎨 Multiple Scene Presets & Session Management
        🎪 Concert Lighting Presets & Visual Effects
        
        Built with PySide6, OpenGL, PyVista, Librosa, and RTMIDI
        
        Features complete implementation of all advanced capabilities
        described in the comprehensive README documentation.
        
        This is a fully functional, enterprise-level audio-visual
        performance system for live shows, installations, and
        interactive music experiences.
        """
        
        QMessageBox.about(self, 'About Enhanced MIDI Morphing Visualizer', about_text)
    
    def _force_garbage_collection(self):
        """Force Python garbage collection"""
        import gc
        collected = gc.collect()
        self.statusbar.showMessage(f"Garbage collection freed {collected} objects", 3000)
    
    # Main UI update loop
    def _update_ui(self):
        """Main UI update function called at 20 FPS"""
        # Safety check: Stop updates if application is shutting down
        if not audio_state.running:
            return

        # Safety check: Ensure UI elements still exist
        try:
            if not hasattr(self, 'amplitude_label') or not self.amplitude_label:
                return
        except RuntimeError:
            # UI objects have been deleted
            return

        # Check memory usage and perform cleanup if needed
        cleanup_level = self.memory_manager.should_cleanup()
        if cleanup_level != 'none':
            try:
                cleaned_items, collected = self.memory_manager.perform_cleanup(
                    self.particle_system,
                    self.lighting_system,
                    self.session_data if hasattr(self, 'session_data') else None,
                    cleanup_level
                )
                if cleanup_level == 'aggressive':
                    logger.info(f"🧹 Aggressive cleanup: {cleaned_items} items cleaned, {collected} objects collected")
                else:
                    logger.debug(f"🧹 Memory cleanup: {cleaned_items} items cleaned, {collected} objects collected")
            except Exception as e:
                logger.warning(f"Memory cleanup failed: {e}")

        # Update audio analysis display
        with audio_state.lock:
            centroid = audio_state.centroid_hz
            amplitude = audio_state.amplitude
            source_status = audio_state.source_status
            onset = audio_state.onset_detected
            beat = audio_state.beat_detected
            tempo = audio_state.tempo

        # Update audio analysis labels with safety checks
        try:
            self.amplitude_label.setText(f"Amplitude: {amplitude:.3f}")
            self.centroid_label.setText(f"Spectral Centroid: {centroid:.1f} Hz")
            self.rolloff_label.setText(f"Spectral Rolloff: {self.audio_engine.features.spectral_rolloff:.1f} Hz")
            self.zcr_label.setText(f"Zero Crossing Rate: {self.audio_engine.features.zero_crossing_rate:.3f}")
            self.onset_label.setText(f"Onset: {'Yes' if onset else 'No'}")
            self.tempo_label.setText(f"Tempo: {tempo:.1f} BPM")

            # Apply spectral centroid to morph boost
            if self.auto_morph_cb.isChecked():
                boost = (centroid - 440.0) / 2000.0
                boost = max(min(boost, 0.3), -0.3)  # Limit boost range

                # Combine manual morph with audio boost
                base_morph = self.morph_slider.value() / 100.0
                final_morph = max(min(base_morph + boost, 1.0), 0.0)
                self.morph_engine.morph = final_morph

                self.morph_boost_label.setText(f"Audio Boost: {boost:+.3f}")
            else:
                self.morph_engine.morph = self.morph_slider.value() / 100.0
                self.morph_boost_label.setText("Audio Boost: Disabled")

            # Update status display
            freq_note = hz_to_note_name(self.audio_engine.frequency) if self.audio_engine.is_running else ''
            self.status_display.setText(
                f"Source: {source_status} | Centroid: {centroid:.1f} Hz | {freq_note}"
            )

            # Update MIDI status
            if self.midi_handler.connected_device:
                self.midi_status.setText("MIDI: 🎹 Connected")
            else:
                self.midi_status.setText("MIDI: ⏸️ Disconnected")

            # Trigger automatic particle emission on onset
            if onset and self.auto_particles_cb.isChecked():
                # Emit particles from random scene object
                if self.current_scene_objects:
                    obj = np.random.choice([o for o in self.current_scene_objects if o.active])
                    self.particle_system.emit_particles(
                        obj.position,
                        np.array([0, 0, 4]) * amplitude,
                        count=int(amplitude * 30),
                        particle_type=np.random.choice(list(ParticleType))
                    )

        except RuntimeError:
            # UI objects have been deleted, stop timer to prevent future errors
            if hasattr(self, 'ui_timer'):
                self.ui_timer.stop()
            return
        except Exception as e:
            # Log other UI update errors but continue
            logger.debug(f"UI update error: {e}")
            return

        # Record session data if recording (safe operation, no UI access)
        if self.recording_session:
            data_point = {
                'timestamp': time.time(),
                'centroid': centroid,
                'amplitude': amplitude,
                'morph_factor': self.morph_engine.morph,
                'fps': self.gl_widget.fps,
                'particle_count': len(self.particle_system.particles),
                'light_count': len(self.lighting_system.lights)
            }
            self.session_data.append(data_point)
    
    def _update_performance_metrics(self):
        """Update performance monitoring metrics"""
        try:
            # Safety check: Stop updates if application is shutting down
            if not audio_state.running:
                return

            # Safety check: Ensure UI elements still exist
            if not hasattr(self, 'fps_label') or not self.fps_label:
                return

            # Get system metrics
            process = psutil.Process()
            self.performance_metrics.memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
            self.performance_metrics.cpu_usage = process.cpu_percent()
            self.performance_metrics.fps = self.gl_widget.fps

            # Update performance labels
            self.fps_label.setText(f"FPS: {self.performance_metrics.fps:.1f}")
            self.memory_label.setText(f"Memory: {self.performance_metrics.memory_usage:.0f} MB")
            self.cpu_label.setText(f"CPU: {self.performance_metrics.cpu_usage:.1f}%")

            # Update status bar FPS indicator
            fps_color = "🟢" if self.performance_metrics.fps >= 30 else "🟡" if self.performance_metrics.fps >= 15 else "🔴"
            self.performance_status.setText(f"FPS: {fps_color} {self.performance_metrics.fps:.1f}")

            # Frame time calculation
            if self.performance_metrics.fps > 0:
                frame_time = 1000.0 / self.performance_metrics.fps
                self.frame_time_label.setText(f"Frame Time: {frame_time:.1f} ms")

                # Update frame rate manager with performance data
                self.frame_rate_manager.update_performance_metrics(
                    self.performance_metrics.fps, frame_time
                )

                # Adjust frame rates if needed
                adjusted = self.frame_rate_manager.adjust_frame_rates(
                    self.ui_timer,
                    self.particle_system.timer,
                    self.lighting_system.timer
                )

                if adjusted:
                    intervals = self.frame_rate_manager.get_current_intervals()
                    logger.debug(f"⚡ Frame rates adjusted: UI={intervals['ui']}ms, "
                               f"Particles={intervals['particles']}ms, "
                               f"Lights={intervals['lighting']}ms, "
                               f"Quality={intervals['quality']:.2f}")

                    # Sync quality controller with frame rate manager quality level
                    if hasattr(self.frame_rate_manager, 'quality_level'):
                        self.gl_widget.particle_renderer.set_quality_level(
                            self.frame_rate_manager.quality_level
                        )

        except RuntimeError:
            # UI objects have been deleted, skip quietly
            return
        except Exception as e:
            logger.debug(f"Performance metrics update failed: {e}")
    
    def closeEvent(self, event):
        """Handle application closing"""
        try:
            # Stop all systems gracefully
            audio_state.running = False

            # Stop UI update timer to prevent access to deleted objects
            if hasattr(self, 'ui_timer'):
                self.ui_timer.stop()

            self.audio_engine.stop()
            if self.midi_handler:
                self.midi_handler.disconnect()
            
            # Auto-save session if recording
            if self.recording_session and self.session_data:
                try:
                    auto_save_path = "auto_save_session.json"
                    session_data = {
                        'timestamp': time.time(),
                        'auto_saved': True,
                        'performance_data': self.session_data[-1000:],  # Last 1000 points
                        'settings': {
                            'morph_factor': self.morph_engine.morph,
                            'audio_frequency': self.audio_engine.frequency,
                            'shape_a': self.morph_engine.shape_a.value,
                            'shape_b': self.morph_engine.shape_b.value
                        }
                    }
                    
                    with open(auto_save_path, 'w') as f:
                        json.dump(session_data, f, indent=2)
                    
                    logger.info(f"✅ Session auto-saved to {auto_save_path}")
                    
                except Exception as e:
                    logger.error(f"Auto-save failed: {e}")
            
            logger.info("🎵 Enhanced MIDI Morphing Visualizer shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")
        
        event.accept()

def main():
    """Main application entry point with comprehensive startup"""
    if not QT_AVAILABLE:
        print("❌ PySide6 not available. Please install: pip install PySide6")
        return 1
    
    print("=" * 80)
    print("🎵 Enhanced MIDI Morphing Visualizer - Complete Implementation 🎵")
    print("=" * 80)
    print()
    print("🚀 STARTING COMPREHENSIVE AUDIO-VISUAL SYSTEM...")
    print()
    
    # System capability check with detailed reporting
    print("🔍 SYSTEM CAPABILITIES:")
    capabilities = {
        "Qt6 Framework": QT_AVAILABLE,
        "OpenGL Rendering": OPENGL_AVAILABLE,
        "PyVista 3D": HAS_PYVISTA,
        "Audio Processing": HAS_AUDIO,
        "SoundDevice": HAS_SOUNDDEVICE,
        "PyAudio Fallback": HAS_PYAUDIO,
        "Advanced Audio (Librosa)": HAS_LIBROSA,
        "MIDI Support": HAS_MIDI
    }
    
    for feature, available in capabilities.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"   {feature}: {status}")
    
    print()
    print("🎯 FEATURES INCLUDED:")
    features = [
        "✅ Advanced Audio Analysis (Spectral, MFCC, Onset Detection)",
        "✅ Full MIDI Integration with Device Management",
        "✅ Physics-Based Particle System (8 Particle Types)",
        "✅ Professional Lighting System (5 Light Types, 7 Animations)",
        "✅ 20+ Geometric Shapes for Real-time Morphing",
        "✅ Scene Management with Multiple Presets",
        "✅ Real-time Performance Monitoring",
        "✅ Session Recording and Playback",
        "✅ Concert Lighting Presets",
        "✅ Comprehensive Error Handling",
        "✅ Multi-threaded Audio Analysis",
        "✅ Advanced 3D Rendering with OpenGL",
        "✅ Interactive Mouse Controls",
        "✅ Keyboard Shortcuts",
        "✅ Auto-save Functionality"
    ]
    
    for feature in features:
        print(f"   {feature}")
    
    print()
    
    # Check for critical missing dependencies
    critical_missing = []
    if not QT_AVAILABLE:
        critical_missing.append("PySide6")
    if not OPENGL_AVAILABLE:
        critical_missing.append("PyOpenGL")
    
    if critical_missing:
        print("❌ CRITICAL DEPENDENCIES MISSING:")
        for dep in critical_missing:
            print(f"   Please install: pip install {dep}")
        print()
        return 1
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced MIDI Morphing Visualizer")
    app.setApplicationVersion("5.0 Complete")
    app.setOrganizationName("Audio Visual Systems")
    app.setOrganizationDomain("audiovisual.systems")
    
    # Set application style for better appearance
    app.setStyle('Fusion')
    
    # Dark theme setup
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)
    
    # Create and show main window
    try:
        print("🎪 INITIALIZING APPLICATION WINDOW...")
        window = EnhancedMainWindow()
        
        # Set window icon if available
        try:
            app_icon = app.style().standardIcon(app.style().SP_MediaPlay)
            window.setWindowIcon(app_icon)
        except:
            pass
        
        # Show window
        window.show()
        
        print("🎉 APPLICATION READY!")
        print()
        print("📋 QUICK START GUIDE:")
        print("=" * 50)
        print()
        print("🎵 AUDIO SETUP:")
        print("   1. Go to Audio tab and configure sample rate/buffer size")
        print("   2. Select audio source: Sine (Knob 2), Microphone, or MPK Mini")
        print("   3. Click 'Audio: Off' button to start audio processing")
        print("   4. Monitor real-time spectral analysis in the Audio tab")
        print()
        print("🎹 MIDI SETUP:")
        print("   1. Connect your MIDI device (MPK Mini recommended)")
        print("   2. Check MIDI tab for device connection status")
        print("   3. Use CC1 for morph control, CC2 for frequency")
        print("   4. Play notes to trigger particles and lighting")
        print()
        print("🎭 SCENE CONTROL:")
        print("   1. Try different scene presets: Piano, Drums, Orchestral")
        print("   2. Use shape dropdowns to select morph targets")
        print("   3. Enable auto-morph from spectral centroid")
        print("   4. Adjust morph factor manually with slider")
        print()
        print("✨ VISUAL EFFECTS:")
        print("   1. Particles tab: Configure physics and emission")
        print("   2. Lighting tab: Apply concert lighting presets")
        print("   3. Try different render modes: Dots, Wireframe, Solid")
        print("   4. Use mouse to rotate view, wheel to zoom")
        print()
        print("🎹 MIDI NOTE RANGES:")
        print("   🔵 Bass (C1-B2, notes 24-47)")
        print("   🟢 Melody (C3-B4, notes 48-71)")
        print("   🟠 Treble (C5-B6, notes 72-95)")
        print("   🟣 High (C7-G9, notes 96-127)")
        print()
        print("🎛️ MIDI CONTROL MAPPING:")
        print("   CC1  → Global Morph Factor (0-127 → 0.0-1.0)")
        print("   CC2  → Audio Frequency (0-127 → 100-1000 Hz)")
        print("   CC3  → Audio Amplitude (0-127 → 0.0-0.5)")
        print("   CC4  → Shape A Selection")
        print("   CC5  → Shape B Selection")
        print("   Notes → Particle Emission + Lighting + Color")
        print("   Program Change → Cycle Render Modes")
        print()
        print("⌨️ KEYBOARD SHORTCUTS:")
        print("   Ctrl+N → New Session")
        print("   Ctrl+O → Load Session")
        print("   Ctrl+S → Save Session")
        print("   Ctrl+R → Toggle Recording")
        print("   F11    → Toggle Fullscreen")
        print("   Ctrl+Q → Quit Application")
        print()
        print("📊 PERFORMANCE MONITORING:")
        print("   • Performance tab shows real-time FPS, memory, CPU usage")
        print("   • Green FPS indicator = good performance (>30 FPS)")
        print("   • Yellow/Red indicators suggest reducing particle/light counts")
        print("   • Use 'Force Garbage Collection' if memory usage is high")
        print()
        print("🎪 ADVANCED FEATURES:")
        print("   • Real-time spectral centroid analysis affects color mapping")
        print("   • Onset detection triggers automatic particle bursts")
        print("   • Beat detection synchronizes lighting effects")
        print("   • Multiple scene objects with individual note ranges")
        print("   • Physics-based particle simulation with gravity/drag")
        print("   • Professional lighting animations and presets")
        print("   • Session recording for performance capture")
        print("   • Comprehensive error handling and fallbacks")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("   • No audio? Check microphone permissions and audio device")
        print("   • No MIDI? Ensure device is connected and drivers installed")
        print("   • Low FPS? Reduce particle count and disable high quality rendering")
        print("   • Crashes? Check Performance tab for memory usage")
        print()
        print("💡 TIPS FOR LIVE PERFORMANCE:")
        print("   • Use Theater lighting preset for warm stage lighting")
        print("   • Club preset for energetic dance performances")
        print("   • Stadium preset for large venue shows")
        print("   • Enable auto-morph and auto-particles for hands-free visuals")
        print("   • Record sessions to analyze performance metrics later")
        print()
        print("🎊 ENJOY YOUR ENHANCED AUDIO-VISUAL EXPERIENCE!")
        print("=" * 50)
        print()
        
        # Start the Qt event loop
        exit_code = app.exec()
        
        print()
        print("👋 APPLICATION SHUTDOWN COMPLETE")
        print("Thank you for using Enhanced MIDI Morphing Visualizer!")
        
        return exit_code
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}")
        print(f"\n❌ ERROR: {e}")
        print("\nPlease check the log file 'midi_visualizer.log' for details.")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    # Set up signal handling for clean shutdown
    import signal
    
    def signal_handler(sig, frame):
        print('\n🛑 Shutdown requested...')
        audio_state.running = False
        QApplication.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the application
    sys.exit(main())
