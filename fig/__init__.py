"""
MMPA - Midi Morphing Power Arranger
The Language of Signals Becoming Form

A comprehensive audiovisual synthesis engine for live performance,
education, and creative exploration.
"""

__version__ = "1.0.0"
__author__ = "MMPA Project"
__description__ = "Midi Morphing Power Arranger - The Language of Signals Becoming Form"

from .core.app import EnhancedApplication
from .core.config import get_config, MMPAConfig

__all__ = [
    'EnhancedApplication',
    'get_config',
    'MMPAConfig',
]