"""
MIDI to OSC Morphing Interface Package

A real-time audio-visual morphing system that combines MIDI input, OSC messaging,
3D mesh visualization, and audio analysis for interactive performance art.

Author: Assistant
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Assistant"
__email__ = "assistant@example.com"
__description__ = "MIDI to OSC Morphing Interface"

# Import main components for convenience
from config import Config, MidiConstants
from exceptions import (
    MeshCreationError, 
    MidiConnectionError, 
    OSCServerError, 
    AudioAnalysisError
)
from profiler import PerformanceProfiler, profiler, profile_function
from geometry import create_initial_meshes, blend_meshes
from audio import AudioAnalysisThread
from midi_osc import IntegratedMidiOscThread
from dialogs import ConfigDialog, PerformanceDialog
from main_window import MainWindow

__all__ = [
    # Configuration
    'Config',
    'MidiConstants',
    
    # Exceptions
    'MeshCreationError',
    'MidiConnectionError', 
    'OSCServerError',
    'AudioAnalysisError',
    
    # Performance
    'PerformanceProfiler',
    'profiler',
    'profile_function',
    
    # Geometry
    'create_initial_meshes',
    'blend_meshes',
    
    # Threads
    'AudioAnalysisThread',
    'IntegratedMidiOscThread',
    
    # UI Components
    'ConfigDialog',
    'PerformanceDialog',
    'MainWindow',
]

def get_version():
    """Return the current version."""
    return __version__

def get_info():
    """Return package information."""
    return {
        'name': 'MIDI to OSC Morphing Interface',
        'version': __version__,
        'author': __author__,
        'description': __description__,
    }