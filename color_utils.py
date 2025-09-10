# color_utils.py - Add this as a new file to your project
"""
Color utility functions with proper clamping to prevent invalid RGB values.
"""

import numpy as np
import colorsys

def safe_hsv_to_rgb(hue, saturation, brightness):
    """
    Safely convert HSV to RGB with proper clamping to avoid invalid color values.
    
    Args:
        hue: Hue value (will be wrapped to 0-1 range)
        saturation: Saturation value (will be clamped to 0-1 range)  
        brightness: Brightness/Value (will be clamped to 0-1 range)
    
    Returns:
        tuple: RGB values guaranteed to be in 0-1 range
    """
    # Ensure hue wraps around (0-1 range, can exceed)
    hue = hue % 1.0
    
    # Clamp saturation and brightness to valid range
    saturation = np.clip(saturation, 0.0, 1.0)
    brightness = np.clip(brightness, 0.0, 1.0)
    
    # Convert to RGB
    rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
    
    # Extra safety: clamp RGB values (shouldn't be needed but good practice)
    return tuple(np.clip(rgb, 0.0, 1.0))

def safe_color_array(color):
    """
    Ensure a color array/tuple has valid RGB values.
    
    Args:
        color: Color as array, tuple, or list
    
    Returns:
        numpy.ndarray: RGB color array with values clamped to 0-1 range
    """
    color_array = np.array(color)
    return np.clip(color_array, 0.0, 1.0)

def safe_rgb_to_hsv(r, g, b):
    """
    Safely convert RGB to HSV with input validation.
    
    Args:
        r, g, b: RGB values (will be clamped to 0-1 range)
    
    Returns:
        tuple: HSV values
    """
    r = np.clip(r, 0.0, 1.0)
    g = np.clip(g, 0.0, 1.0)
    b = np.clip(b, 0.0, 1.0)
    
    return colorsys.rgb_to_hsv(r, g, b)

def blend_colors_safe(colors, weights=None):
    """
    Safely blend multiple colors with optional weights.
    
    Args:
        colors: List of color arrays/tuples
        weights: Optional list of weights (same length as colors)
    
    Returns:
        numpy.ndarray: Blended color with valid RGB values
    """
    if not colors:
        return np.array([0.5, 0.5, 0.5])  # Default gray
    
    colors = [safe_color_array(color) for color in colors]
    
    if weights is None:
        weights = [1.0] * len(colors)
    
    weights = np.array(weights)
    total_weight = np.sum(weights)
    
    if total_weight == 0:
        return np.array([0.5, 0.5, 0.5])
    
    # Weighted average
    blended = np.zeros(3)
    for color, weight in zip(colors, weights):
        blended += color * weight
    
    blended = blended / total_weight
    return safe_color_array(blended)
