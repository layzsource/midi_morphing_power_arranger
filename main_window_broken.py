"""
Main application window for the MIDI to OSC Morphing Interface.
"""

import sys
import time
import logging
import numpy as np
import pyvista as pv
import colorsys
from typing import Dict, Optional
from pyvistaqt import QtInteractor
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QComboBox,
    QStatusBar, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Slot, QTimer, QSettings

from config import Config
from geometry import create_initial_meshes, blend_meshes
from midi_osc import IntegratedMidiOscThread
from audio import AudioAnalysisThread
from dialogs import ConfigDialog, PerformanceDialog
from profiler import profiler, profile_function
from exceptions import MeshCreationError

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = Config()
        # ... rest of the class
