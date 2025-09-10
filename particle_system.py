"""
Particle Effects System for MIDI Visualization
Provides note-triggered particle effects with physics simulation and performance optimization.
"""

import numpy as np
import time
import colorsys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import pyvista as pv
import threading


class ParticleType(Enum):
    """Different types of particles for different effects."""
    SPARK = "spark"
    BURST = "burst"
    TRAIL = "trail"
    BLOOM = "bloom"
    SHOCKWAVE = "shockwave"


class ParticleBlendMode(Enum):
    """Particle rendering blend modes."""
    NORMAL = "normal"
    ADDITIVE = "additive"
    MULTIPLY = "multiply"
    SCREEN = "screen"


@dataclass
class Particle:
    """Individual particle with physics properties."""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(3))
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    size: float = 1.0
    opacity: float = 1.0
    life_remaining: float = 1.0
    max_life: float = 1.0
    mass: float = 1.0
    drag: float = 0.98
    note: int = 60
    velocity_midi: float = 1.0
    spawn_time: float = field(default_factory=time.time)
    
    def update(self, delta_time: float, gravity: np.ndarray = None) -> bool:
        """Update particle physics and return False if particle should be removed."""
        if self.life_remaining <= 0:
            return False
        
        # Apply gravity if provided
        if gravity is not None:
            self.acceleration += gravity * self.mass
        
        # Update physics
        self.velocity += self.acceleration * delta_time
        self.velocity *= self.drag  # Apply drag
        self.position += self.velocity * delta_time
        
        # Update life and derived properties
        self.life_remaining -= delta_time
        life_ratio = self.life_remaining / self.max_life
        
        # Fade out as particle dies
        self.opacity = life_ratio * 0.8 + 0.2  # Keep some minimum opacity
        
        # Size can evolve over lifetime
        self.size = max(0.1, self.size * life_ratio * 1.2)
        
        # Reset acceleration for next frame
        self.acceleration = np.zeros(3)
        
        return self.life_remaining > 0


@dataclass
class ParticleEmitter:
    """Emitter configuration for creating particles."""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    direction: np.ndarray = field(default_factory=lambda: np.array([0, 1, 0]))
    spread_angle: float = 30.0  # degrees
    particle_type: ParticleType = ParticleType.SPARK
    emission_rate: float = 50.0  # particles per second
    particle_life: float = 2.0
    initial_speed: float = 5.0
    speed_variation: float = 0.3
    size_range: Tuple[float, float] = (0.5, 2.0)
    color_base: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0]))
    color_variation: float = 0.2
    gravity_scale: float = 1.0
    drag_coefficient: float = 0.98
    enabled: bool = True
    last_emission: float = field(default_factory=time.time)


class ParticleSystem:
    """
    Main particle system managing all particle effects.
    Integrates with existing scene manager and provides MIDI-triggered effects.
    """
    
    def __init__(self, plotter_widget=None, scene_manager=None):
        self.plotter_widget = plotter_widget
        self.scene_manager = scene_manager
        
        # Particle storage
        self.active_particles: List[Particle] = []
        self.particle_pools: Dict[ParticleType, List[Particle]] = defaultdict(list)
        self.particle_actors: List[Any] = []  # PyVista actors for rendering
        
        # Emitters
        self.active_emitters: Dict[str, ParticleEmitter] = {}
        self.note_emitters: Dict[int, str] = {}  # Note to emitter ID mapping
        
        # Physics and performance settings
        self.gravity = np.array([0.0, -9.81, 0.0])
        self.max_particles = 1000
        self.particle_update_rate = 60.0  # Hz
        self.last_update_time = time.time()
        self.performance_mode = False
        
        # Rendering settings
        self.render_particles = True
        self.particle_size_scale = 1.0
        self.opacity_scale = 1.0
        self.blend_mode = ParticleBlendMode.ADDITIVE
        
        # Performance monitoring
        self.update_times = deque(maxlen=60)
        self.particle_count_history = deque(maxlen=300)  # 5 seconds at 60fps
        
        # Thread safety
        self._update_lock = threading.Lock()
        
        print("Particle system initialized")
    
    def emit_note_particles(self, note: int, velocity: float, position: np.ndarray = None, 
                          particle_type: ParticleType = ParticleType.SPARK) -> str:
        """
        Emit particles when MIDI note is triggered.
        Returns emitter ID for tracking.
        """
        if not self.render_particles:
            return ""
        
        if position is None:
            position = self._get_note_position(note)
        
        # Create emitter configuration based on note and velocity
        emitter_id = f"note_{note}_{time.time()}"
        color = self._note_to_color(note)
        
        # Scale particle count and properties by velocity
        particle_count = int(velocity * 30)  # 0-30 particles based on velocity
        speed = 2.0 + velocity * 8.0  # Speed scales with velocity
        life = 1.0 + velocity * 2.0  # Life scales with velocity
        
        emitter = ParticleEmitter(
            position=position.copy(),
            direction=self._get_emission_direction(particle_type),
            spread_angle=self._get_spread_angle(particle_type),
            particle_type=particle_type,
            emission_rate=particle_count / 0.1,  # Burst over 0.1 seconds
            particle_life=life,
            initial_speed=speed,
            speed_variation=0.4,
            color_base=color,
            color_variation=0.3,
            gravity_scale=self._get_gravity_scale(particle_type)
        )
        
        self.active_emitters[emitter_id] = emitter
        self.note_emitters[note] = emitter_id
        
        # Emit initial burst
        self._emit_particles_from_emitter(emitter, particle_count)
        
        # Schedule emitter removal
        removal_time = time.time() + 0.2  # Short burst
        self._schedule_emitter_removal(emitter_id, removal_time)
        
        return emitter_id
    
    def emit_special_effect(self, effect_type: str, position: np.ndarray, 
                          intensity: float = 1.0) -> str:
        """Emit special particle effects for dramatic moments."""
        if effect_type == "explosion":
            return self._create_explosion_effect(position, intensity)
        elif effect_type == "shockwave":
            return self._create_shockwave_effect(position, intensity)
        elif effect_type == "bloom":
            return self._create_bloom_effect(position, intensity)
        else:
            # Default to spark burst
            return self.emit_note_particles(60, intensity, position, ParticleType.BURST)
    
    def update_particles(self, delta_time: float = None):
        """Update all active particles with physics simulation."""
        if not self.render_particles or len(self.active_particles) == 0:
            return
        
        update_start = time.time()
        
        if delta_time is None:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time
        
        # Limit delta time to prevent large jumps
        delta_time = min(delta_time, 1.0 / 30.0)  # Cap at 30fps minimum
        
        with self._update_lock:
            # Update existing particles
            surviving_particles = []
            for particle in self.active_particles:
                if particle.update(delta_time, self.gravity):
                    surviving_particles.append(particle)
                else:
                    # Return dead particle to pool for reuse
                    self.particle_pools[ParticleType.SPARK].append(particle)
            
            self.active_particles = surviving_particles
            
            # Update emitters and emit new particles
            self._update_emitters(delta_time)
            
            # Enforce particle limit
            if len(self.active_particles) > self.max_particles:
                # Remove oldest particles
                excess = len(self.active_particles) - self.max_particles
                for i in range(excess):
                    old_particle = self.active_particles.pop(0)
                    self.particle_pools[ParticleType.SPARK].append(old_particle)
        
        # Update visual representation
        if self.plotter_widget is not None:
            self._update_particle_rendering()
        
        # Performance tracking
        update_time = time.time() - update_start
        self.update_times.append(update_time)
        self.particle_count_history.append(len(self.active_particles))
    
    def _update_emitters(self, delta_time: float):
        """Update all active emitters."""
        expired_emitters = []
        current_time = time.time()
        
        for emitter_id, emitter in self.active_emitters.items():
            if not emitter.enabled:
                continue
            
            # Check if enough time has passed for emission
            time_since_last = current_time - emitter.last_emission
            emission_interval = 1.0 / emitter.emission_rate
            
            if time_since_last >= emission_interval:
                particles_to_emit = int(time_since_last * emitter.emission_rate)
                self._emit_particles_from_emitter(emitter, particles_to_emit)
                emitter.last_emission = current_time
    
    def _emit_particles_from_emitter(self, emitter: ParticleEmitter, count: int):
        """Emit a specified number of particles from an emitter."""
        for _ in range(min(count, 50)):  # Limit burst size
            particle = self._create_particle_from_emitter(emitter)
            if particle:
                self.active_particles.append(particle)
    
    def _create_particle_from_emitter(self, emitter: ParticleEmitter) -> Optional[Particle]:
        """Create a single particle from emitter configuration."""
        # Try to reuse particle from pool
        pool = self.particle_pools[emitter.particle_type]
        if pool:
            particle = pool.pop()
        else:
            particle = Particle()
        
        # Configure particle
        particle.position = emitter.position.copy()
        particle.life_remaining = emitter.particle_life
        particle.max_life = emitter.particle_life
        particle.spawn_time = time.time()
        
        # Random velocity within spread cone
        velocity_dir = self._random_cone_direction(emitter.direction, emitter.spread_angle)
        speed = emitter.initial_speed * (1.0 + np.random.uniform(-emitter.speed_variation, 
                                                                 emitter.speed_variation))
        particle.velocity = velocity_dir * speed
        
        # Random size within range
        particle.size = np.random.uniform(*emitter.size_range)
        
        # Color with variation
        base_color = emitter.color_base
        if emitter.color_variation > 0:
            # Add color variation in HSV space for more natural results
            hsv = colorsys.rgb_to_hsv(*base_color)
            h_var = emitter.color_variation * np.random.uniform(-1, 1)
            s_var = emitter.color_variation * 0.5 * np.random.uniform(-1, 1)
            v_var = emitter.color_variation * 0.3 * np.random.uniform(-1, 1)
            
            new_h = (hsv[0] + h_var) % 1.0
            new_s = np.clip(hsv[1] + s_var, 0, 1)
            new_v = np.clip(hsv[2] + v_var, 0, 1)
            
            particle.color = np.array(colorsys.hsv_to_rgb(new_h, new_s, new_v))
        else:
            particle.color = base_color.copy()
        
        particle.opacity = 1.0
        particle.drag = emitter.drag_coefficient
        particle.mass = emitter.gravity_scale
        
        return particle
    
    def _update_particle_rendering(self):
        """Update the visual representation of particles in the 3D scene."""
        try:
            # Remove old particle actors
            for actor in self.particle_actors:
                self.plotter_widget.remove_actor(actor)
            self.particle_actors.clear()
            
            if not self.active_particles:
                return
            
            # Performance optimization: batch particles by type/color
            if self.performance_mode and len(self.active_particles) > 200:
                self._render_particles_batched()
            else:
                self._render_particles_individual()
                
        except Exception as e:
            print(f"Error updating particle rendering: {e}")
    
    def _render_particles_individual(self):
        """Render each particle as individual mesh (high quality, lower performance)."""
        for particle in self.active_particles:
            if particle.opacity < 0.01:  # Skip nearly invisible particles
                continue
            
            # Create sphere for particle
            sphere = pv.Sphere(radius=particle.size * self.particle_size_scale, center=particle.position)
            
            # Configure appearance
            opacity = particle.opacity * self.opacity_scale
            color = particle.color
            
            # Apply blend mode effects
            if self.blend_mode == ParticleBlendMode.ADDITIVE:
                opacity *= 0.6
                color = color * 1.2  # Brighten for additive effect
            
            actor = self.plotter_widget.add_mesh(
                sphere,
                color=color,
                opacity=opacity,
                smooth_shading=True
            )
            
            self.particle_actors.append(actor)
    
    def _render_particles_batched(self):
        """Render particles in batches for better performance."""
        # Group particles by color (quantized)
        color_groups = defaultdict(list)
        
        for particle in self.active_particles:
            if particle.opacity < 0.01:
                continue
            
            # Quantize color to reduce groups
            quantized_color = tuple(np.round(particle.color * 4) / 4)
            color_groups[quantized_color].append(particle)
        
        # Render each color group as a single point cloud
        for color, particles in color_groups.items():
            if not particles:
                continue
            
            positions = np.array([p.position for p in particles])
            sizes = np.array([p.size * self.particle_size_scale for p in particles])
            opacities = np.array([p.opacity * self.opacity_scale for p in particles])
            
            # Create point cloud
            point_cloud = pv.PolyData(positions)
            point_cloud.point_data['sizes'] = sizes
            point_cloud.point_data['opacities'] = opacities
            
            avg_opacity = np.mean(opacities)
            actor = self.plotter_widget.add_points(
                point_cloud,
                color=np.array(color),
                opacity=avg_opacity,
                point_size=np.mean(sizes) * 10
            )
            
            self.particle_actors.append(actor)
    
    def _note_to_color(self, note: int) -> np.ndarray:
        """Convert MIDI note to color using HSV color wheel."""
        # Map note to hue (chromatic circle)
        hue = (note % 12) / 12.0
        
        # Adjust saturation and value based on octave
        octave = note // 12
        saturation = 0.7 + (octave % 4) * 0.075  # Vary saturation by octave
        value = 0.8 + (note % 24) / 48.0  # Brighter for higher notes
        
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return np.array(rgb)
    
    def _get_note_position(self, note: int) -> np.ndarray:
        """Get 3D position for a note based on scene layout."""
        if self.scene_manager:
            # Find objects that handle this note
            for obj_id, visual_obj in self.scene_manager.objects.items():
                if visual_obj.note_range.contains(note, 0):
                    return visual_obj.position.copy()
        
        # Default positioning based on note value
        x = (note % 12 - 6) * 0.5  # Spread chromatically
        y = ((note // 12) - 5) * 0.3  # Stack octaves vertically
        z = np.random.uniform(-1, 1)  # Random depth
        
        return np.array([x, y, z])
    
    def _get_emission_direction(self, particle_type: ParticleType) -> np.ndarray:
        """Get emission direction based on particle type."""
        if particle_type == ParticleType.BURST:
            return np.array([0, 1, 0])  # Upward burst
        elif particle_type == ParticleType.SHOCKWAVE:
            return np.array([1, 0, 0])  # Horizontal spread
        elif particle_type == ParticleType.TRAIL:
            return np.array([0, 0, 1])  # Forward trail
        else:  # SPARK, BLOOM
            return np.array([0, 1, 0])  # Default upward
    
    def _get_spread_angle(self, particle_type: ParticleType) -> float:
        """Get spread angle based on particle type."""
        spread_angles = {
            ParticleType.SPARK: 15.0,
            ParticleType.BURST: 45.0,
            ParticleType.TRAIL: 5.0,
            ParticleType.BLOOM: 30.0,
            ParticleType.SHOCKWAVE: 90.0
        }
        return spread_angles.get(particle_type, 30.0)
    
    def _get_gravity_scale(self, particle_type: ParticleType) -> float:
        """Get gravity scale based on particle type."""
        gravity_scales = {
            ParticleType.SPARK: 1.0,
            ParticleType.BURST: 0.5,
            ParticleType.TRAIL: 0.1,
            ParticleType.BLOOM: 0.3,
            ParticleType.SHOCKWAVE: 0.0
        }
        return gravity_scales.get(particle_type, 1.0)
    
    def _random_cone_direction(self, center_dir: np.ndarray, angle_degrees: float) -> np.ndarray:
        """Generate random direction within a cone."""
        # Convert to radians
        angle_rad = np.radians(angle_degrees)
        
        # Generate random direction in cone
        # First, create a random direction in a circle
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, angle_rad)
        
        # Convert to cartesian coordinates relative to center direction
        # This is a simplified cone generation - could be more sophisticated
        offset = np.array([
            np.sin(phi) * np.cos(theta),
            np.sin(phi) * np.sin(theta),
            np.cos(phi) - 1
        ]) * 0.5
        
        direction = center_dir + offset
        return direction / np.linalg.norm(direction)
    
    def _create_explosion_effect(self, position: np.ndarray, intensity: float) -> str:
        """Create dramatic explosion effect."""
        emitter_id = f"explosion_{time.time()}"
        particle_count = int(intensity * 100)
        
        emitter = ParticleEmitter(
            position=position.copy(),
            direction=np.array([0, 1, 0]),
            spread_angle=180.0,  # Full sphere
            particle_type=ParticleType.BURST,
            emission_rate=particle_count / 0.05,  # Very fast burst
            particle_life=3.0,
            initial_speed=15.0 * intensity,
            speed_variation=0.6,
            color_base=np.array([1.0, 0.5, 0.1]),  # Orange explosion
            color_variation=0.4,
            gravity_scale=0.8
        )
        
        self.active_emitters[emitter_id] = emitter
        self._emit_particles_from_emitter(emitter, particle_count)
        self._schedule_emitter_removal(emitter_id, time.time() + 0.1)
        
        return emitter_id
    
    def _create_shockwave_effect(self, position: np.ndarray, intensity: float) -> str:
        """Create expanding shockwave effect."""
        emitter_id = f"shockwave_{time.time()}"
        
        emitter = ParticleEmitter(
            position=position.copy(),
            direction=np.array([1, 0, 0]),
            spread_angle=360.0,  # Full horizontal circle
            particle_type=ParticleType.SHOCKWAVE,
            emission_rate=200.0,
            particle_life=2.0,
            initial_speed=10.0 * intensity,
            speed_variation=0.2,
            color_base=np.array([0.3, 0.7, 1.0]),  # Blue shockwave
            color_variation=0.3,
            gravity_scale=0.0  # No gravity for shockwave
        )
        
        self.active_emitters[emitter_id] = emitter
        self._emit_particles_from_emitter(emitter, int(intensity * 50))
        self._schedule_emitter_removal(emitter_id, time.time() + 0.3)
        
        return emitter_id
    
    def _create_bloom_effect(self, position: np.ndarray, intensity: float) -> str:
        """Create gentle blooming effect."""
        emitter_id = f"bloom_{time.time()}"
        
        emitter = ParticleEmitter(
            position=position.copy(),
            direction=np.array([0, 1, 0]),
            spread_angle=60.0,
            particle_type=ParticleType.BLOOM,
            emission_rate=30.0,
            particle_life=4.0,
            initial_speed=3.0 * intensity,
            speed_variation=0.4,
            color_base=np.array([1.0, 0.8, 1.0]),  # Soft pink
            color_variation=0.2,
            gravity_scale=0.2
        )
        
        self.active_emitters[emitter_id] = emitter
        self._emit_particles_from_emitter(emitter, int(intensity * 20))
        self._schedule_emitter_removal(emitter_id, time.time() + 1.0)
        
        return emitter_id
    
    def _schedule_emitter_removal(self, emitter_id: str, removal_time: float):
        """Schedule an emitter for removal at a specific time."""
        # In a more complete implementation, this would use a timer or queue
        # For now, we'll disable the emitter and rely on cleanup
        def disable_emitter():
            if emitter_id in self.active_emitters:
                self.active_emitters[emitter_id].enabled = False
        
        # Schedule removal (simplified - in real app use QTimer or similar)
        threading.Timer(removal_time - time.time(), disable_emitter).start()
    
    def cleanup_expired_emitters(self):
        """Remove expired emitters to free memory."""
        current_time = time.time()
        expired_emitters = []
        
        for emitter_id, emitter in self.active_emitters.items():
            # Remove emitters that haven't emitted recently and are disabled
            if (not emitter.enabled and 
                current_time - emitter.last_emission > 5.0):
                expired_emitters.append(emitter_id)
        
        for emitter_id in expired_emitters:
            del self.active_emitters[emitter_id]
            # Remove from note mapping if present
            note_to_remove = None
            for note, mapped_id in self.note_emitters.items():
                if mapped_id == emitter_id:
                    note_to_remove = note
                    break
            if note_to_remove is not None:
                del self.note_emitters[note_to_remove]
    
    def clear_all_particles(self):
        """Clear all particles and emitters."""
        with self._update_lock:
            # Return all particles to pools
            for particle in self.active_particles:
                self.particle_pools[ParticleType.SPARK].append(particle)
            
            self.active_particles.clear()
            self.active_emitters.clear()
            self.note_emitters.clear()
            
            # Clear visual actors
            if self.plotter_widget:
                for actor in self.particle_actors:
                    self.plotter_widget.remove_actor(actor)
                self.particle_actors.clear()
    
    def set_performance_mode(self, enabled: bool):
        """Enable/disable performance optimizations."""
        self.performance_mode = enabled
        if enabled:
            self.max_particles = 500
            self.particle_update_rate = 30.0
        else:
            self.max_particles = 1000
            self.particle_update_rate = 60.0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        if not self.update_times:
            return {}
        
        avg_update_time = np.mean(self.update_times)
        max_update_time = np.max(self.update_times)
        avg_particle_count = np.mean(self.particle_count_history) if self.particle_count_history else 0
        
        return {
            'active_particles': len(self.active_particles),
            'active_emitters': len(self.active_emitters),
            'avg_update_time_ms': avg_update_time * 1000,
            'max_update_time_ms': max_update_time * 1000,
            'avg_particle_count': avg_particle_count,
            'performance_mode': self.performance_mode,
            'total_particle_actors': len(self.particle_actors)
        }


class ParticleSystemIntegration:
    """
    Integration helper to connect particle system with existing scene manager.
    """
    
    def __init__(self, scene_manager, plotter_widget):
        self.scene_manager = scene_manager
        self.particle_system = ParticleSystem(plotter_widget, scene_manager)
        
        # Store original handle_midi_note method
        self.original_handle_midi_note = scene_manager.handle_midi_note
        
        # Replace with enhanced version
        scene_manager.handle_midi_note = self._enhanced_handle_midi_note
        
        print("Particle system integrated with scene manager")
    
    def _enhanced_handle_midi_note(self, note: int, velocity: float, note_on: bool = True, channel: int = 0):
        """Enhanced MIDI note handler that triggers particles."""
        # Call original handler
        affected_objects = self.original_handle_midi_note(note, velocity, note_on, channel)
        
        # Add particle effects for note events
        if note_on and velocity > 0:
            # Determine particle type based on velocity and note
            if velocity > 0.8:
                particle_type = ParticleType.BURST
            elif velocity > 0.5:
                particle_type = ParticleType.SPARK
            else:
                particle_type = ParticleType.BLOOM
            
            # Get position from affected objects or use default
            position = None
            if affected_objects:
                obj_id = affected_objects[0]
                if obj_id in self.scene_manager.objects:
                    position = self.scene_manager.objects[obj_id].position
            
            # Emit particles
            self.particle_system.emit_note_particles(note, velocity, position, particle_type)
        
        return affected_objects
    
    def update(self, delta_time: float = None):
        """Update particle system (call this from main update loop)."""
        self.particle_system.update_particles(delta_time)
        self.particle_system.cleanup_expired_emitters()
    
    def set_enabled(self, enabled: bool):
        """Enable/disable particle effects."""
        self.particle_system.render_particles = enabled
        if not enabled:
            self.particle_system.clear_all_particles()


# Example usage and integration
def integrate_particles_with_existing_system(main_window):
    """
    Example of how to integrate particle system with existing application.
    Call this from your main application initialization.
    """
    if hasattr(main_window, 'scene_manager') and hasattr(main_window, 'plotter_widget'):
        # Create particle integration
        particle_integration = ParticleSystemIntegration(
            main_window.scene_manager, 
            main_window.plotter_widget
        )
        
        # Store reference for updates
        main_window.particle_integration = particle_integration
        
        # Add particle update to existing update timer
        if hasattr(main_window, 'update_timer'):
            original_timeout = main_window.update_timer.timeout
            
            def enhanced_update():
                # Call original update
                if hasattr(original_timeout, 'connect'):
                    for slot in original_timeout.receivers():
                        slot()
                
                # Update particles
                particle_integration.update()
            
            # Replace timer connection
            main_window.update_timer.timeout.disconnect()
            main_window.update_timer.timeout.connect(enhanced_update)
        
        print("Particle system fully integrated")
        return particle_integration
    else:
        print("Cannot integrate particles - missing scene_manager or plotter_widget")
        return None


if __name__ == "__main__":
    # Example standalone test
    import pyvista as pv
    from pyvistaqt import QtInteractor
    
    # Create test scene
    plotter = QtInteractor()
    
    # Create particle system
    particle_system = ParticleSystem(plotter)
    
    # Emit some test particles
    test_position = np.array([0, 0, 0])
    particle_system.emit_note_particles(60, 0.8, test_position, ParticleType.BURST)
    particle_system.emit_note_particles(64, 0.6, test_position + np.array([2, 0, 0]), ParticleType.SPARK)
    particle_system.emit_note_particles(67, 0.9, test_position + np.array([-2, 0, 0]), ParticleType.BLOOM)
    
    # Animation loop
    def update_animation():
        particle_system.update_particles()
        plotter.render()
    
    # Note: In real application, this would be connected to a QTimer
    print("Particle system test complete")
    print(f"Performance stats: {particle_system.get_performance_stats()}")
