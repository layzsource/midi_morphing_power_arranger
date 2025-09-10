"""
Custom exceptions for the MIDI to OSC Morphing Interface.
"""

class MeshCreationError(Exception):
    """Raised when mesh creation fails."""
    pass

class MidiConnectionError(Exception):
    """Raised when MIDI connection fails."""
    pass

class OSCServerError(Exception):
    """Raised when OSC server fails to start."""
    pass

class AudioAnalysisError(Exception):
    """Raised when audio analysis fails."""
    pass