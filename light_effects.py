#!/usr/bin/env python3
"""
Advanced Light Effects System for MIDI Visualization
Provides dynamic lighting, color effects, and atmospheric rendering.
"""

import numpy as np
import pyvista as pv
import colorsys
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from enum import Enum


class LightType(Enum):
    """Types of lights available."""
    POINT = "point"
    DIRECTIONAL = "directional"
    SPOT = "spot"
    AMBIENT = "ambient"


class LightAnimationType(Enum):
    """Light animation types."""
    STATIC = "static"
    PULSE = "pulse"
    ROTATE = "rotate"
    BREATHE = "breathe"
    STROBE = "strobe"
    WAVE = "wave"


@dataclass
class LightSource:
    """Advanced light source with animation capabilities."""
    position: np.ndarray
    intensity: float = 1.0
    color: np.ndarray = None
    light_type: LightType = LightType.POINT
    animation_type: LightAnimationType = LightAnimationType.STATIC
    
    # Animation parameters
    animation_speed: float = 1.0
    animation_phase: float = 0.0
    animation_amplitude: float = 0.5
    
    # Spot light parameters
    focal_point: np.ndarray = None
    cone_angle: float = 30.0
    
    # State tracking
    base_intensity: float = None
    base_position: np.ndarray = None
    creation_time: float = None
    
    # MIDI response
    responds_to_midi: bool = True
    note_response_range: Tuple[int, int] = (0, 127)
    velocity_influence: float = 1.0
    
    def __post_init__(self):
        if self.color is None:
            self.color = np.array([1.0, 1.0, 1.0])
        if self.focal_point is None:
            self.focal_point = np.array([0.0, 0.0, 0.0])
        if self.base_intensity is None:
            self.base_intensity = self.intensity
        if self.base_position is None:
            self.base_position = self.position.copy()
        if self.creation_time is None:
            self.creation_time = time.time()
    
    def update(self, delta_time: float, active_notes: Dict = None):
        """Update light animation and MIDI response."""
        elapsed = time.time() - self.creation_time
        
        # Update based on animation type
        if self.animation_type == LightAnimationType.PULSE:
            self._update_pulse(elapsed)
        elif self.animation_type == LightAnimationType.ROTATE:
            self._update_rotate(elapsed)
        elif self.animation_type == LightAnimationType.BREATHE:
            self._update_breathe(elapsed)
        elif self.animation_type == LightAnimationType.STROBE:
            self._update_strobe(elapsed)
        elif self.animation_type == LightAnimationType.WAVE:
            self._update_wave(elapsed)
        
        # MIDI response
        if self.responds_to_midi and active_notes:
            self._update_midi_response(active_notes)
    
    def _update_pulse(self, elapsed: float):
        """Pulse animation."""
        pulse = np.sin(elapsed * self.animation_speed * 2 * np.pi) * self.animation_amplitude
        self.intensity = self.base_intensity * (1.0 + pulse)
    
    def _update_rotate(self, elapsed: float):
        """Rotation animation."""
        angle = elapsed * self.animation_speed
        radius = np.linalg.norm(self.base_position[:2])
        if radius > 0:
            self.position[0] = radius * np.cos(angle + self.animation_phase)
            self.position[1] = radius * np.sin(angle + self.animation_phase)
    
    def _update_breathe(self, elapsed: float):
        """Breathing animation."""
        breathe = (np.sin(elapsed * self.animation_speed * 0.5) + 1.0) * 0.5
        self.intensity = self.base_intensity * (0.3 + breathe * 0.7)
    
    def _update_strobe(self, elapsed: float):
        """Strobe effect."""
        strobe = int(elapsed * self.animation_speed * 10) % 2
        self.intensity = self.base_intensity * strobe
    
    def _update_wave(self, elapsed: float):
        """Wave animation."""
        wave = np.sin(elapsed * self.animation_speed + self.animation_phase)
        self.position[2] = self.base_position[2] + wave * self.animation_amplitude
        self.intensity = self.base_intensity * (0.7 + wave * 0.3)
    
    def _update_midi_response(self, active_notes: Dict):
        """Update light based on MIDI activity."""
        # Check if any active notes are in our response range
        responding_notes = [
            note for note in active_notes.keys()
            if self.note_response_range[0] <= note <= self.note_response_range[1]
        ]
        
        if responding_notes:
            # Calculate average velocity of responding notes
            avg_velocity = np.mean([
                active_notes[note].get('velocity', 1.0) 
                for note in responding_notes
            ])
            
            # Modulate intensity based on velocity
            velocity_mod = 0.5 + avg_velocity * 0.5 * self.velocity_influence
            self.intensity = self.base_intensity * velocity_mod
            
            # Color shift based on note pitch
            avg_note = np.mean(responding_notes)
            hue = (avg_note - self.note_response_range[0]) / (
                self.note_response_range[1] - self.note_response_range[0]
            )
            self.color = np.array(colorsys.hsv_to_rgb(hue, 0.8, 1.0))
    
    def to_pyvista_light(self):
        """Convert to PyVista light object."""
        light = pv.Light()
        light.position = self.position
        light.intensity = self.intensity
        
        # Set color using the correct method
        # PyVista light uses SetColor method or ambient/diffuse/specular color properties
        try:
            # Try setting diffuse color (main light color)
            light.diffuse_color = self.color
        except AttributeError:
            try:
                # Alternative: use SetColor if available
                light.SetColor(self.color)
            except AttributeError:
                # If neither works, set the light color properties individually
                pass
        
        if self.light_type == LightType.DIRECTIONAL:
            light.positional = False
            light.focal_point = self.focal_point
        elif self.light_type == LightType.SPOT:
            light.positional = True
            light.focal_point = self.focal_point
            light.cone_angle = self.cone_angle
        else:  # POINT
            light.positional = True
        
        return light


class LightingSystem:
    """Advanced lighting system manager."""
    
    def __init__(self, plotter):
        self.plotter = plotter
        self.lights: Dict[str, LightSource] = {}
        self.pv_lights: Dict[str, pv.Light] = {}
        
        # Global lighting parameters
        self.ambient_intensity = 0.2
        self.global_intensity_multiplier = 1.0
        self.shadows_enabled = False
        
        # Effects
        self.color_cycle_enabled = False
        self.color_cycle_speed = 0.1
        self.lightning_effect_enabled = False
        
        # Performance
        self.max_dynamic_lights = 8
        self.update_frequency = 30  # Hz
        self.last_update = time.time()
    
    def add_light(self, name: str, light: LightSource):
        """Add a light to the system."""
        if len(self.lights) >= self.max_dynamic_lights:
            # Remove oldest light
            oldest = min(self.lights.items(), key=lambda x: x[1].creation_time)
            self.remove_light(oldest[0])
        
        self.lights[name] = light
        pv_light = light.to_pyvista_light()
        self.pv_lights[name] = pv_light
        self.plotter.add_light(pv_light)
    
    def remove_light(self, name: str):
        """Remove a light from the system."""
        if name in self.lights:
            del self.lights[name]
        if name in self.pv_lights:
            self.plotter.remove_light(self.pv_lights[name])
            del self.pv_lights[name]
    
    def update(self, active_notes: Dict = None):
        """Update all lights."""
        current_time = time.time()
        delta_time = current_time - self.last_update
        
        # Throttle updates
        if delta_time < 1.0 / self.update_frequency:
            return
        
        # Update each light
        for name, light in self.lights.items():
            light.update(delta_time, active_notes)
            
            # Update PyVista light
            if name in self.pv_lights:
                pv_light = self.pv_lights[name]
                pv_light.position = light.position
                pv_light.intensity = light.intensity * self.global_intensity_multiplier
                pv_light.color = light.color
        
        # Global effects
        if self.color_cycle_enabled:
            self._update_color_cycle(current_time)
        
        if self.lightning_effect_enabled:
            self._update_lightning(current_time)
        
        self.last_update = current_time
    
    def _update_color_cycle(self, current_time: float):
        """Update global color cycling."""
        hue = (current_time * self.color_cycle_speed) % 1.0
        color = np.array(colorsys.hsv_to_rgb(hue, 0.5, 1.0))
        
        for light in self.lights.values():
            if light.animation_type == LightAnimationType.STATIC:
                light.color = color
    
    def _update_lightning(self, current_time: float):
        """Create lightning flash effects."""
        if np.random.random() < 0.01:  # 1% chance per update
            # Flash all lights
            for light in self.lights.values():
                light.intensity = light.base_intensity * 3.0
    
    def create_note_light(self, note: int, velocity: float, position: Optional[np.ndarray] = None):
        """Create a light triggered by a MIDI note."""
        if position is None:
            # Generate position based on note
            angle = (note / 127.0) * 2 * np.pi
            radius = 2.0 + velocity
            position = np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                1.0 + velocity * 2.0
            ])
        
        # Color based on note octave
        octave = note // 12
        hue = (octave / 10.0) % 1.0
        color = np.array(colorsys.hsv_to_rgb(hue, 0.7, 1.0))
        
        light = LightSource(
            position=position,
            intensity=0.5 + velocity * 1.5,
            color=color,
            animation_type=LightAnimationType.PULSE,
            animation_speed=1.0 + velocity,
            responds_to_midi=True,
            note_response_range=(note - 6, note + 6)
        )
        
        self.add_light(f"note_{note}_{time.time()}", light)
        return light
    
    def create_ambient_setup(self):
        """Create a standard ambient lighting setup."""
        # Key light
        self.add_light("key", LightSource(
            position=np.array([5.0, 5.0, 5.0]),
            intensity=1.0,
            color=np.array([1.0, 0.95, 0.9]),
            light_type=LightType.DIRECTIONAL,
            animation_type=LightAnimationType.STATIC
        ))
        
        # Fill light
        self.add_light("fill", LightSource(
            position=np.array([-3.0, 2.0, 3.0]),
            intensity=0.5,
            color=np.array([0.9, 0.9, 1.0]),
            light_type=LightType.POINT,
            animation_type=LightAnimationType.BREATHE
        ))
        
        # Rim light
        self.add_light("rim", LightSource(
            position=np.array([0.0, -5.0, 2.0]),
            intensity=0.7,
            color=np.array([1.0, 1.0, 1.0]),
            light_type=LightType.SPOT,
            animation_type=LightAnimationType.STATIC
        ))
    
    def clear_all(self):
        """Remove all lights."""
        light_names = list(self.lights.keys())
        for name in light_names:
            self.remove_light(name)


def generate_lighting_positions(num_lights: int, pattern: str = "circle") -> List[np.ndarray]:
    """Generate positions for multiple lights in various patterns."""
    positions = []
    
    if pattern == "circle":
        for i in range(num_lights):
            angle = (i / num_lights) * 2 * np.pi
            radius = 3.0
            positions.append(np.array([
                radius * np.cos(angle),
                radius * np.sin(angle),
                2.0
            ]))
    
    elif pattern == "spiral":
        for i in range(num_lights):
            t = i / num_lights * 4 * np.pi
            radius = 1.0 + t / (2 * np.pi)
            positions.append(np.array([
                radius * np.cos(t),
                radius * np.sin(t),
                0.5 + i * 0.5
            ]))
    
    elif pattern == "grid":
        grid_size = int(np.ceil(np.sqrt(num_lights)))
        for i in range(num_lights):
            x = (i % grid_size - grid_size/2) * 2
            y = (i // grid_size - grid_size/2) * 2
            positions.append(np.array([x, y, 3.0]))
    
    elif pattern == "random":
        for i in range(num_lights):
            positions.append(np.random.uniform(-3, 3, 3))
    
    elif pattern == "dome":
        for i in range(num_lights):
            # Fibonacci sphere distribution
            golden_ratio = (1 + 5**0.5) / 2
            theta = 2 * np.pi * i / golden_ratio
            phi = np.arccos(1 - 2 * (i + 0.5) / num_lights)
            
            positions.append(np.array([
                3 * np.sin(phi) * np.cos(theta),
                3 * np.sin(phi) * np.sin(theta),
                3 * np.cos(phi)
            ]))
    
    else:  # Default to line
        for i in range(num_lights):
            x = (i / max(num_lights - 1, 1) - 0.5) * 6
            positions.append(np.array([x, 0.0, 3.0]))
    
    return positions


def create_concert_lighting(plotter, num_lights: int = 6):
    """Create a concert-style lighting setup."""
    system = LightingSystem(plotter)
    
    # Stage lights
    positions = generate_lighting_positions(num_lights, "circle")
    colors = [
        [1.0, 0.0, 0.0],  # Red
        [0.0, 1.0, 0.0],  # Green
        [0.0, 0.0, 1.0],  # Blue
        [1.0, 1.0, 0.0],  # Yellow
        [1.0, 0.0, 1.0],  # Magenta
        [0.0, 1.0, 1.0],  # Cyan
    ]
    
    for i, pos in enumerate(positions):
        light = LightSource(
            position=pos,
            intensity=1.5,
            color=np.array(colors[i % len(colors)]),
            light_type=LightType.SPOT,
            animation_type=LightAnimationType.ROTATE,
            animation_speed=0.5,
            animation_phase=i * np.pi / 3
        )
        system.add_light(f"stage_{i}", light)
    
    # Add moving head lights
    for i in range(2):
        light = LightSource(
            position=np.array([(-1)**i * 4, 0, 4]),
            intensity=2.0,
            color=np.array([1.0, 1.0, 1.0]),
            light_type=LightType.SPOT,
            animation_type=LightAnimationType.WAVE,
            animation_speed=0.3,
            animation_phase=i * np.pi
        )
        system.add_light(f"moving_{i}", light)
    
    return system


# Test function
def test_light_effects():
    """Test light effects system."""
    import pyvista as pv
    
    # Create plotter
    plotter = pv.Plotter()
    plotter.set_background("black")
    
    # Add a test mesh
    mesh = pv.Sphere()
    plotter.add_mesh(mesh, color="white", smooth_shading=True)
    
    # Create lighting system
    system = LightingSystem(plotter)
    
    # Test different light setups
    print("Testing Light Effects System")
    print("=" * 50)
    
    # Create ambient setup
    system.create_ambient_setup()
    print("✓ Created ambient lighting setup")
    
    # Test concert lighting
    concert_system = create_concert_lighting(plotter, 8)
    print("✓ Created concert lighting with 8 lights")
    
    # Test light positions
    positions = generate_lighting_positions(6, "dome")
    print(f"✓ Generated {len(positions)} dome positions")
    
    # Show the scene
    plotter.show()


if __name__ == "__main__":
    test_light_effects()
