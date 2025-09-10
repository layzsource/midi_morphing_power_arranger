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
from config import Config
from midi_constants import MidiConstants
from exceptions import (
    MeshCreationError, 
    MidiConnectionError, 
    OSCServerError, 
    AudioAnalysisError
)
from profiler import PerformanceProfiler, profiler, profile_function
from geometry import create_initial_meshes, blend_meshes

# Import thread components with correct names
from audio import AudioAnalysisThread
from midi_osc import IntegratedMidiOscThread

# Import dialog components - handle name conflicts
from dialogs import ConfigDialog, PerformanceDialog
from config_dialog import ConfigurationDialog
from performance_monitoring import PerformanceDialog as AdvancedPerformanceDialog

# Import main window
from main_window import MainWindow

# Import scene management
from scene_manager import SceneManager, NoteRange, LayerBlendMode, CompositionRule
from scene_config_dialog import SceneConfigurationDialog

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
    'ConfigurationDialog',
    'AdvancedPerformanceDialog',
    'MainWindow',
    
    # Scene Management
    'SceneManager',
    'NoteRange',
    'LayerBlendMode',
    'CompositionRule',
    'SceneConfigurationDialog',
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

def check_dependencies():
    """Check if all dependencies are available."""
    dependencies = {
        'required': [],
        'optional': [],
        'missing_required': [],
        'missing_optional': []
    }
    
    # Required dependencies
    required_modules = [
        ('PySide6', 'PySide6.QtWidgets'),
        ('pyvista', 'pyvista'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('psutil', 'psutil')
    ]
    
    # Optional dependencies
    optional_modules = [
        ('pygame', 'pygame.midi'),
        ('pyaudio', 'pyaudio'),
        ('librosa', 'librosa'),
        ('rtmidi', 'rtmidi'),
        ('python-osc', 'pythonosc'),
        ('matplotlib', 'matplotlib.pyplot')
    ]
    
    # Check required
    for name, module in required_modules:
        try:
            __import__(module)
            dependencies['required'].append(name)
        except ImportError:
            dependencies['missing_required'].append(name)
    
    # Check optional
    for name, module in optional_modules:
        try:
            __import__(module)
            dependencies['optional'].append(name)
        except ImportError:
            dependencies['missing_optional'].append(name)
    
    return dependencies

def get_system_info():
    """Get system information for debugging."""
    import sys
    import platform
    
    info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
        'python_executable': sys.executable,
        'package_version': __version__
    }
    
    # Add dependency information
    deps = check_dependencies()
    info['dependencies'] = deps
    
    return info

def print_system_info():
    """Print system information."""
    info = get_system_info()
    
    print("=" * 50)
    print("MIDI to OSC Morphing Interface System Information")
    print("=" * 50)
    print(f"Package Version: {info['package_version']}")
    print(f"Python Version: {info['python_version']}")
    print(f"Platform: {info['platform']}")
    print(f"Architecture: {info['architecture']}")
    print(f"Processor: {info['processor']}")
    print()
    
    deps = info['dependencies']
    print("Required Dependencies:")
    for dep in deps['required']:
        print(f"  ✓ {dep}")
    
    if deps['missing_required']:
        print("Missing Required Dependencies:")
        for dep in deps['missing_required']:
            print(f"  ✗ {dep}")
    
    print()
    print("Optional Dependencies:")
    for dep in deps['optional']:
        print(f"  ✓ {dep}")
    
    if deps['missing_optional']:
        print("Missing Optional Dependencies:")
        for dep in deps['missing_optional']:
            print(f"  ✗ {dep}")
    
    print("=" * 50)

# Compatibility aliases for older code
AudioAnalyzer = AudioAnalysisThread  # In case old code uses this name
MidiOscBridge = IntegratedMidiOscThread  # Alternative name

# Package metadata
__package_name__ = "morphing_interface"
__license__ = "MIT"
__url__ = "https://github.com/user/morphing-interface"
__maintainer__ = __author__
__maintainer_email__ = __email__
