"""
main_window.py - Compatibility import for the main window class

This module provides compatibility imports for the main window implementation.
The actual implementation is in main_fixed_window.py
"""

# Import the actual implementation
from main_fixed_window import PerformanceAwareMainWindow

# Provide compatibility alias
MainWindow = PerformanceAwareMainWindow

# Export the main window class
__all__ = ['MainWindow', 'PerformanceAwareMainWindow']
