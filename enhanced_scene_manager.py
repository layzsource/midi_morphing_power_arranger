"""
Enhanced Scene Manager with Instrument Presets, Performance Recording, and Advanced Transitions
"""

import time
import json
import threading
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import colorsys

from scene_manager import SceneManager, VisualObject, NoteRange, CompositionRule, LayerBlendMode


class InstrumentType(Enum):
    """Predefined instrument types with specific visual characteristics."""
    PIANO = "piano"
    DRUMS = "drums"
    SYNTHESIZER = "synthesizer"
    VIOLIN = "violin"
    GUITAR = "guitar"
    ORGAN = "organ"
    AMBIENT = "ambient"
    ORCHESTRAL = "orchestral"


@dataclass
class PerformanceEvent:
    """Represents a single event in a performance recording."""
    timestamp: float
    event_type: str  # 'note_on', 'note_off', 'control_change', 'scene_change'
    data: Dict[str, Any]
    scene_state: Optional[Dict] = None


@dataclass
class SceneTransition:
    """Defines a transition between scene states."""
    duration: float
    easing_function: str  # 'linear', 'ease_in', 'ease_out', 'ease_in_out'
    properties: List[str]  # Which properties to transition
    start_values: Dict[str, Any]
    end_values: Dict[str, Any]


class PresetManager:
    """Manages instrument-specific scene presets."""
    
    def __init__(self):
        self.presets = self._create_default_presets()
        self.custom_presets = {}
    
    def _create_default_presets(self) -> Dict[InstrumentType, Dict]:
        """Create default instrument presets."""
        return {
            InstrumentType.PIANO: {
                'name': 'Piano (4 Octaves)',
                'description': 'Classic piano layout with 4 octave ranges',
                'objects': [
                    {
                        'id': 'bass_keys',
                        'shape_type': 'cube',
                        'note_range': {'min_note': 36, 'max_note': 59, 'name': 'Bass Keys'},
                        'position': [-2.0, 0.0, 0.0],
                        'scale': 1.2,
                        'color_scheme': 'warm',
                        'depth_layer': 1
                    },
                    {
                        'id': 'mid_keys',
                        'shape_type': 'sphere',
                        'note_range': {'min_note': 60, 'max_note': 83, 'name': 'Mid Keys'},
                        'position': [0.0, 0.0, 0.0],
                        'scale': 1.0,
                        'color_scheme': 'bright',
                        'depth_layer': 2
                    },
                    {
                        'id': 'treble_keys',
                        'shape_type': 'icosahedron',
                        'note_range': {'min_note': 84, 'max_note': 107, 'name': 'Treble Keys'},
                        'position': [2.0, 0.0, 0.0],
                        'scale': 0.8,
                        'color_scheme': 'bright',
                        'depth_layer': 3
                    }
                ],
                'composition_rules': ['HARMONIC', 'SPATIAL'],
                'physics_enabled': False,
                'transition_speed': 1.0
            },
            
            InstrumentType.DRUMS: {
                'name': 'Drum Kit',
                'description': 'Percussive elements with impact-based visuals',
                'objects': [
                    {
                        'id': 'kick',
                        'shape_type': 'sphere',
                        'note_range': {'min_note': 35, 'max_note': 36, 'name': 'Kick Drum'},
                        'position': [0.0, -1.5, 0.0],
                        'scale': 2.0,
                        'color_scheme': 'deep',
                        'depth_layer': 1
                    },
                    {
                        'id': 'snare',
                        'shape_type': 'cylinder',
                        'note_range': {'min_note': 38, 'max_note': 40, 'name': 'Snare'},
                        'position': [0.0, 0.0, 0.0],
                        'scale': 1.2,
                        'color_scheme': 'sharp',
                        'depth_layer': 2
                    },
                    {
                        'id': 'hi_hat',
                        'shape_type': 'torus',
                        'note_range': {'min_note': 42, 'max_note': 46, 'name': 'Hi-Hat'},
                        'position': [1.5, 1.0, 0.0],
                        'scale': 0.6,
                        'color_scheme': 'metallic',
                        'depth_layer': 3
                    },
                    {
                        'id': 'toms',
                        'shape_type': 'cone',
                        'note_range': {'min_note': 47, 'max_note': 50, 'name': 'Toms'},
                        'position': [-1.5, 0.5, 0.0],
                        'scale': 1.0,
                        'color_scheme': 'warm',
                        'depth_layer': 2
                    }
                ],
                'composition_rules': ['RHYTHMIC', 'INDEPENDENT'],
                'physics_enabled': True,
                'transition_speed': 2.0
            },
            
            InstrumentType.SYNTHESIZER: {
                'name': 'Synthesizer (3 Layers)',
                'description': 'Layered synthesis with morphing capabilities',
                'objects': [
                    {
                        'id': 'bass_synth',
                        'shape_type': 'cube',
                        'note_range': {'min_note': 24, 'max_note': 47, 'name': 'Bass Synth'},
                        'position': [0.0, -1.0, 0.0],
                        'scale': 1.5,
                        'color_scheme': 'deep',
                        'depth_layer': 1
                    },
                    {
                        'id': 'lead_synth',
                        'shape_type': 'icosahedron',
                        'note_range': {'min_note': 48, 'max_note': 84, 'name': 'Lead Synth'},
                        'position': [0.0, 0.5, 0.0],
                        'scale': 1.0,
                        'color_scheme': 'electric',
                        'depth_layer': 2
                    },
                    {
                        'id': 'pad_synth',
                        'shape_type': 'sphere',
                        'note_range': {'min_note': 36, 'max_note': 96, 'name': 'Pad Synth'},
                        'position': [0.0, 0.0, -1.0],
                        'scale': 2.5,
                        'color_scheme': 'ambient',
                        'depth_layer': 0
                    }
                ],
                'composition_rules': ['HARMONIC', 'SPATIAL', 'RHYTHMIC'],
                'physics_enabled': False,
                'transition_speed': 1.5
            },
            
            InstrumentType.AMBIENT: {
                'name': 'Ambient (Sparse)',
                'description': 'Minimal, atmospheric visualization',
                'objects': [
                    {
                        'id': 'ambient_low',
                        'shape_type': 'sphere',
                        'note_range': {'min_note': 24, 'max_note': 60, 'name': 'Low Ambient'},
                        'position': [-1.0, 0.0, 0.0],
                        'scale': 3.0,
                        'color_scheme': 'muted',
                        'depth_layer': 0
                    },
                    {
                        'id': 'ambient_high',
                        'shape_type': 'icosahedron',
                        'note_range': {'min_note': 60, 'max_note': 108, 'name': 'High Ambient'},
                        'position': [1.0, 0.0, 0.0],
                        'scale': 2.0,
                        'color_scheme': 'ethereal',
                        'depth_layer': 1
                    }
                ],
                'composition_rules': ['SPATIAL'],
                'physics_enabled': False,
                'transition_speed': 0.5
            }
        }
    
    def get_color_scheme(self, scheme_name: str) -> Dict[str, np.ndarray]:
        """Get color scheme configuration."""
        schemes = {
            'warm': {
                'base': np.array([0.9, 0.6, 0.3]),
                'accent': np.array([1.0, 0.4, 0.2]),
                'highlight': np.array([1.0, 0.8, 0.4])
            },
            'bright': {
                'base': np.array([0.3, 0.7, 0.9]),
                'accent': np.array([0.1, 0.9, 0.7]),
                'highlight': np.array([0.8, 0.9, 0.3])
            },
            'deep': {
                'base': np.array([0.2, 0.1, 0.4]),
                'accent': np.array([0.4, 0.2, 0.6]),
                'highlight': np.array([0.6, 0.3, 0.8])
            },
            'sharp': {
                'base': np.array([0.9, 0.9, 0.9]),
                'accent': np.array([1.0, 0.0, 0.0]),
                'highlight': np.array([1.0, 1.0, 0.0])
            },
            'metallic': {
                'base': np.array([0.7, 0.7, 0.8]),
                'accent': np.array([0.9, 0.9, 1.0]),
                'highlight': np.array([1.0, 1.0, 1.0])
            },
            'electric': {
                'base': np.array([0.0, 0.5, 1.0]),
                'accent': np.array([0.5, 0.0, 1.0]),
                'highlight': np.array([1.0, 0.0, 0.5])
            },
            'ambient': {
                'base': np.array([0.2, 0.3, 0.4]),
                'accent': np.array([0.3, 0.4, 0.5]),
                'highlight': np.array([0.4, 0.5, 0.6])
            },
            'muted': {
                'base': np.array([0.3, 0.3, 0.3]),
                'accent': np.array([0.4, 0.4, 0.4]),
                'highlight': np.array([0.6, 0.6, 0.6])
            },
            'ethereal': {
                'base': np.array([0.8, 0.9, 1.0]),
                'accent': np.array([0.9, 0.8, 1.0]),
                'highlight': np.array([1.0, 0.9, 0.9])
            }
        }
        return schemes.get(scheme_name, schemes['bright'])


class PerformanceRecorder:
    """Records and plays back performance data."""
    
    def __init__(self):
        self.events: List[PerformanceEvent] = []
        self.is_recording = False
        self.is_playing = False
        self.recording_start_time = 0.0
        self.playback_start_time = 0.0
        self.playback_thread = None
        self.playback_callbacks = []
    
    def start_recording(self):
        """Start recording performance events."""
        self.events.clear()
        self.is_recording = True
        self.recording_start_time = time.time()
        print("Performance recording started")
    
    def stop_recording(self):
        """Stop recording performance events."""
        self.is_recording = False
        print(f"Performance recording stopped. Captured {len(self.events)} events")
    
    def record_event(self, event_type: str, data: Dict[str, Any], scene_state: Optional[Dict] = None):
        """Record a performance event."""
        if not self.is_recording:
            return
        
        timestamp = time.time() - self.recording_start_time
        event = PerformanceEvent(timestamp, event_type, data, scene_state)
        self.events.append(event)
    
    def play_recording(self, callback: Callable[[PerformanceEvent], None]):
        """Play back recorded performance."""
        if self.is_playing or not self.events:
            return
        
        self.is_playing = True
        self.playback_start_time = time.time()
        self.playback_callbacks = [callback]
        
        self.playback_thread = threading.Thread(target=self._playback_worker)
        self.playback_thread.daemon = True
        self.playback_thread.start()
    
    def _playback_worker(self):
        """Worker thread for playback."""
        event_index = 0
        
        while self.is_playing and event_index < len(self.events):
            current_time = time.time() - self.playback_start_time
            event = self.events[event_index]
            
            if current_time >= event.timestamp:
                # Trigger event
                for callback in self.playback_callbacks:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"Playback callback error: {e}")
                
                event_index += 1
            else:
                # Wait for next event
                time.sleep(0.001)  # 1ms resolution
        
        self.is_playing = False
        print("Playback completed")
    
    def stop_playback(self):
        """Stop playback."""
        self.is_playing = False
        if self.playback_thread:
            self.playback_thread.join(timeout=1.0)
    
    def save_recording(self, filename: str):
        """Save recording to file."""
        data = {
            'events': [asdict(event) for event in self.events],
            'duration': self.events[-1].timestamp if self.events else 0.0,
            'event_count': len(self.events)
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Recording saved to {filename}")
    
    def load_recording(self, filename: str):
        """Load recording from file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.events = [
            PerformanceEvent(**event_data) 
            for event_data in data['events']
        ]
        
        print(f"Recording loaded from {filename}. {len(self.events)} events")


class TransitionManager:
    """Manages smooth transitions between scene states."""
    
    def __init__(self):
        self.active_transitions: Dict[str, SceneTransition] = {}
        self.transition_start_times: Dict[str, float] = {}
        self.easing_functions = {
            'linear': self._linear,
            'ease_in': self._ease_in,
            'ease_out': self._ease_out,
            'ease_in_out': self._ease_in_out,
            'bounce': self._bounce,
            'elastic': self._elastic
        }
    
    def start_transition(self, object_id: str, transition: SceneTransition):
        """Start a transition for an object."""
        self.active_transitions[object_id] = transition
        self.transition_start_times[object_id] = time.time()
    
    def update_transitions(self, scene_manager):
        """Update all active transitions."""
        current_time = time.time()
        completed_transitions = []
        
        for object_id, transition in self.active_transitions.items():
            start_time = self.transition_start_times[object_id]
            elapsed = current_time - start_time
            progress = min(elapsed / transition.duration, 1.0)
            
            # Apply easing
            eased_progress = self.easing_functions[transition.easing_function](progress)
            
            # Update object properties
            if object_id in scene_manager.objects:
                visual_obj = scene_manager.objects[object_id]
                self._apply_transition_values(visual_obj, transition, eased_progress)
                scene_manager._update_object_visual(object_id)
            
            # Check if transition is complete
            if progress >= 1.0:
                completed_transitions.append(object_id)
        
        # Remove completed transitions
        for object_id in completed_transitions:
            del self.active_transitions[object_id]
            del self.transition_start_times[object_id]
    
    def _apply_transition_values(self, visual_obj, transition, progress):
        """Apply interpolated values to visual object."""
        for prop in transition.properties:
            if prop in transition.start_values and prop in transition.end_values:
                start_val = transition.start_values[prop]
                end_val = transition.end_values[prop]
                
                if isinstance(start_val, (list, np.ndarray)):
                    # Interpolate arrays/vectors
                    start_arr = np.array(start_val)
                    end_arr = np.array(end_val)
                    interpolated = start_arr + (end_arr - start_arr) * progress
                    setattr(visual_obj, prop, interpolated)
                else:
                    # Interpolate scalars
                    interpolated = start_val + (end_val - start_val) * progress
                    setattr(visual_obj, prop, interpolated)
    
    # Easing functions
    def _linear(self, t):
        return t
    
    def _ease_in(self, t):
        return t * t
    
    def _ease_out(self, t):
        return 1 - (1 - t) * (1 - t)
    
    def _ease_in_out(self, t):
        if t < 0.5:
            return 2 * t * t
        return 1 - 2 * (1 - t) * (1 - t)
    
    def _bounce(self, t):
        if t < 0.5:
            return 8 * t * t
        return 1 - 8 * (1 - t) * (1 - t)
    
    def _elastic(self, t):
        return np.sin(13 * np.pi / 2 * t) * (2 ** (10 * (t - 1)))


class SceneTemplate:
    """Template system for creating reusable scene configurations."""
    
    def __init__(self, name: str, description: str, template_data: Dict):
        self.name = name
        self.description = description
        self.template_data = template_data
    
    def instantiate(self, **kwargs) -> Dict:
        """Create a scene configuration from this template with parameters."""
        instance = json.loads(json.dumps(self.template_data))  # Deep copy
        
        # Apply parameter substitutions
        self._substitute_parameters(instance, kwargs)
        
        return instance
    
    def _substitute_parameters(self, data, params):
        """Recursively substitute template parameters."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    param_name = value[2:-1]
                    if param_name in params:
                        data[key] = params[param_name]
                else:
                    self._substitute_parameters(value, params)
        elif isinstance(data, list):
            for item in data:
                self._substitute_parameters(item, params)


class EnhancedSceneManager(SceneManager):
    """Enhanced scene manager with presets, recording, and advanced transitions."""
    
    def __init__(self, initial_meshes, plotter_widget):
        super().__init__(initial_meshes, plotter_widget)
        self.preset_manager = PresetManager()
        self.performance_recorder = PerformanceRecorder()
        self.transition_manager = TransitionManager()
        self.scene_templates = self._create_scene_templates()
        
        # Real-time switching
        self.switching_enabled = True
        self.switch_queue = deque()
        
        # Performance optimization
        self.update_throttle = 0.016  # ~60 FPS
        self.last_update_time = 0.0
    
    def _create_scene_templates(self) -> Dict[str, SceneTemplate]:
        """Create built-in scene templates."""
        templates = {}
        
        # Scalable instrument template
        scalable_template = SceneTemplate(
            "Scalable Instrument",
            "Template for creating instruments with variable range and position",
            {
                "objects": [
                    {
                        "id": "${id}",
                        "shape_type": "${shape}",
                        "note_range": {
                            "min_note": "${min_note}",
                            "max_note": "${max_note}",
                            "name": "${name}"
                        },
                        "position": "${position}",
                        "scale": "${scale}",
                        "color_scheme": "${color_scheme}"
                    }
                ],
                "composition_rules": "${rules}",
                "physics_enabled": "${physics}"
            }
        )
        templates["scalable_instrument"] = scalable_template
        
        return templates
    
    def load_instrument_preset(self, instrument_type: InstrumentType) -> bool:
        """Load optimized presets for different instruments."""
        if instrument_type not in self.preset_manager.presets:
            print(f"Unknown instrument type: {instrument_type}")
            return False
        
        preset = self.preset_manager.presets[instrument_type]
        
        # Record scene change if recording
        if self.performance_recorder.is_recording:
            self.performance_recorder.record_event(
                'scene_change',
                {'preset': instrument_type.value},
                self.get_scene_summary()
            )
        
        # Create transition for smooth switching
        if self.switching_enabled and self.objects:
            self._transition_to_preset(preset)
        else:
            self._apply_preset_immediately(preset)
        
        return True
    
    def _transition_to_preset(self, preset: Dict):
        """Smoothly transition to a new preset."""
        # Clear existing objects with fade-out transitions
        for obj_id in list(self.objects.keys()):
            transition = SceneTransition(
                duration=0.5,
                easing_function='ease_out',
                properties=['scale', 'opacity'],
                start_values={'scale': self.objects[obj_id].scale, 'opacity': 1.0},
                end_values={'scale': 0.0, 'opacity': 0.0}
            )
            self.transition_manager.start_transition(obj_id, transition)
        
        # Schedule new objects to appear after fade-out
        def create_new_objects():
            time.sleep(0.6)  # Wait for fade-out
            self._apply_preset_immediately(preset)
            
            # Fade in new objects
            for obj_id in self.objects.keys():
                transition = SceneTransition(
                    duration=0.5,
                    easing_function='ease_in',
                    properties=['scale', 'opacity'],
                    start_values={'scale': 0.0, 'opacity': 0.0},
                    end_values={'scale': self.objects[obj_id].scale, 'opacity': 1.0}
                )
                self.transition_manager.start_transition(obj_id, transition)
        
        thread = threading.Thread(target=create_new_objects)
        thread.daemon = True
        thread.start()
    
    def _apply_preset_immediately(self, preset: Dict):
        """Apply preset configuration immediately."""
        # Clear current scene
        for obj_id in list(self.objects.keys()):
            self.remove_object(obj_id)
        
        # Apply global settings
        if 'composition_rules' in preset:
            rule_names = preset['composition_rules']
            self.composition_rules = [CompositionRule[rule] for rule in rule_names]
        
        if 'physics_enabled' in preset:
            self.physics_enabled = preset['physics_enabled']
        
        # Create objects
        for obj_config in preset['objects']:
            note_range_config = obj_config['note_range']
            note_range = NoteRange(
                min_note=note_range_config['min_note'],
                max_note=note_range_config['max_note'],
                name=note_range_config['name']
            )
            
            # Get color scheme
            color_scheme_name = obj_config.get('color_scheme', 'bright')
            color_scheme = self.preset_manager.get_color_scheme(color_scheme_name)
            
            self.add_object(
                id=obj_config['id'],
                note_range=note_range,
                shape_type=obj_config['shape_type'],
                position=np.array(obj_config['position']),
                scale=obj_config['scale'],
                depth_layer=obj_config.get('depth_layer', 1)
            )
            
            # Apply color scheme
            if obj_config['id'] in self.objects:
                visual_obj = self.objects[obj_config['id']]
                visual_obj.color = color_scheme['base']
        
        print(f"Applied preset: {preset['name']}")
    
    def record_performance(self, duration_seconds: float):
        """Record a performance for the specified duration."""
        if self.performance_recorder.is_recording:
            print("Already recording!")
            return False
        
        self.performance_recorder.start_recording()
        
        # Auto-stop after duration
        def stop_after_duration():
            time.sleep(duration_seconds)
            if self.performance_recorder.is_recording:
                self.performance_recorder.stop_recording()
        
        thread = threading.Thread(target=stop_after_duration)
        thread.daemon = True
        thread.start()
        
        return True
    
    def stop_recording(self):
        """Stop current recording."""
        self.performance_recorder.stop_recording()
    
    def play_recording(self):
        """Play back the last recording."""
        def playback_callback(event: PerformanceEvent):
            if event.event_type == 'note_on':
                data = event.data
                self.handle_midi_note(data['note'], data['velocity'], True)
            elif event.event_type == 'note_off':
                data = event.data
                self.handle_midi_note(data['note'], 0, False)
            elif event.event_type == 'scene_change':
                data = event.data
                instrument_type = InstrumentType(data['preset'])
                self.load_instrument_preset(instrument_type)
        
        self.performance_recorder.play_recording(playback_callback)
    
    def save_recording(self, filename: str):
        """Save current recording to file."""
        self.performance_recorder.save_recording(filename)
    
    def load_recording(self, filename: str):
        """Load recording from file."""
        self.performance_recorder.load_recording(filename)
    
    def switch_scene_realtime(self, instrument_type: InstrumentType):
        """Queue a real-time scene switch."""
        if self.switching_enabled:
            self.switch_queue.append(instrument_type)
    
    def create_scene_from_template(self, template_name: str, **params) -> bool:
        """Create a scene from a template with parameters."""
        if template_name not in self.scene_templates:
            print(f"Unknown template: {template_name}")
            return False
        
        template = self.scene_templates[template_name]
        scene_config = template.instantiate(**params)
        
        # Apply the generated configuration
        self._apply_preset_immediately({'objects': scene_config['objects']})
        
        return True
    
    def handle_midi_note(self, note: int, velocity: int, is_note_on: bool) -> List[str]:
        """Enhanced MIDI note handling with recording."""
        # Record the event
        if self.performance_recorder.is_recording:
            event_type = 'note_on' if is_note_on else 'note_off'
            self.performance_recorder.record_event(
                event_type,
                {'note': note, 'velocity': velocity}
            )
        
        # Call parent implementation
        return super().handle_midi_note(note, velocity, is_note_on)
    
    def update_frame(self):
        """Update frame with throttling and transition management."""
        current_time = time.time()
        
        # Throttle updates for performance
        if current_time - self.last_update_time < self.update_throttle:
            return
        
        self.last_update_time = current_time
        
        # Process queued scene switches
        if self.switch_queue:
            instrument_type = self.switch_queue.popleft()
            self.load_instrument_preset(instrument_type)
        
        # Update transitions
        self.transition_manager.update_transitions(self)
        
        # Update physics
        if self.physics_enabled:
            self.update_physics()
        
        # Call parent frame update
        if hasattr(super(), 'render_frame'):
            super().render_frame()
    
    def get_performance_stats(self) -> Dict:
        """Get performance recording statistics."""
        return {
            'is_recording': self.performance_recorder.is_recording,
            'is_playing': self.performance_recorder.is_playing,
            'recorded_events': len(self.performance_recorder.events),
            'recording_duration': (
                time.time() - self.performance_recorder.recording_start_time
                if self.performance_recorder.is_recording else 0.0
            ),
            'active_transitions': len(self.transition_manager.active_transitions),
            'current_preset': self._get_current_preset_name(),
            'scene_summary': self.get_scene_summary()
        }
    
    def _get_current_preset_name(self) -> str:
        """Determine the current preset name based on scene configuration."""
        # Simple heuristic based on object count and types
        object_count = len(self.objects)
        shape_types = [obj.shape_type for obj in self.objects.values()]
        
        if object_count == 3 and 'cube' in shape_types and 'sphere' in shape_types:
            return "Piano-like"
        elif object_count >= 4 and 'torus' in shape_types:
            return "Drum-like"
        elif 'icosahedron' in shape_types and object_count == 3:
            return "Synthesizer-like"
        elif object_count <= 2:
            return "Ambient-like"
        else:
            return "Custom"
    
    def create_custom_preset(self, name: str, description: str = "") -> bool:
        """Create a custom preset from current scene state."""
        if not self.objects:
            print("No objects in scene to save as preset")
            return False
        
        preset_data = {
            'name': name,
            'description': description,
            'objects': [],
            'composition_rules': [rule.value for rule in self.composition_rules],
            'physics_enabled': self.physics_enabled,
            'transition_speed': 1.0
        }
        
        for obj_id, visual_obj in self.objects.items():
            obj_config = {
                'id': obj_id,
                'shape_type': visual_obj.shape_type,
                'note_range': {
                    'min_note': visual_obj.note_range.min_note,
                    'max_note': visual_obj.note_range.max_note,
                    'name': visual_obj.note_range.name or obj_id
                },
                'position': visual_obj.position.tolist(),
                'scale': visual_obj.scale,
                'color_scheme': 'bright',  # Default, could be enhanced
                'depth_layer': visual_obj.depth_layer
            }
            preset_data['objects'].append(obj_config)
        
        self.preset_manager.custom_presets[name] = preset_data
        print(f"Custom preset '{name}' created with {len(preset_data['objects'])} objects")
        return True
    
    def load_custom_preset(self, name: str) -> bool:
        """Load a custom preset by name."""
        if name not in self.preset_manager.custom_presets:
            print(f"Custom preset '{name}' not found")
            return False
        
        preset = self.preset_manager.custom_presets[name]
        
        # Record scene change if recording
        if self.performance_recorder.is_recording:
            self.performance_recorder.record_event(
                'scene_change',
                {'preset': f"custom_{name}"},
                self.get_scene_summary()
            )
        
        # Apply the preset
        if self.switching_enabled and self.objects:
            self._transition_to_preset(preset)
        else:
            self._apply_preset_immediately(preset)
        
        return True
    
    def list_available_presets(self) -> Dict[str, List[str]]:
        """List all available presets (built-in and custom)."""
        return {
            'built_in': [preset.value for preset in InstrumentType],
            'custom': list(self.preset_manager.custom_presets.keys()),
            'templates': list(self.scene_templates.keys())
        }
    
    def save_custom_presets(self, filename: str):
        """Save all custom presets to file."""
        with open(filename, 'w') as f:
            json.dump(self.preset_manager.custom_presets, f, indent=2)
        print(f"Custom presets saved to {filename}")
    
    def load_custom_presets(self, filename: str):
        """Load custom presets from file."""
        try:
            with open(filename, 'r') as f:
                self.preset_manager.custom_presets = json.load(f)
            print(f"Custom presets loaded from {filename}")
        except Exception as e:
            print(f"Error loading custom presets: {e}")
    
    def set_transition_style(self, style: str, duration: float = 1.0):
        """Set the transition style for scene changes."""
        valid_styles = ['linear', 'ease_in', 'ease_out', 'ease_in_out', 'bounce', 'elastic']
        if style not in valid_styles:
            print(f"Invalid transition style. Valid options: {valid_styles}")
            return False
        
        self.default_transition_style = style
        self.default_transition_duration = duration
        return True
    
    def enable_realtime_switching(self, enabled: bool = True):
        """Enable or disable real-time scene switching."""
        self.switching_enabled = enabled
        print(f"Real-time switching {'enabled' if enabled else 'disabled'}")
    
    def add_transition_effect(self, object_id: str, effect_type: str, **params):
        """Add a special transition effect to an object."""
        if object_id not in self.objects:
            print(f"Object '{object_id}' not found")
            return
        
        visual_obj = self.objects[object_id]
        
        if effect_type == 'pulse':
            # Pulsing scale effect
            duration = params.get('duration', 0.5)
            intensity = params.get('intensity', 1.5)
            
            transition = SceneTransition(
                duration=duration,
                easing_function='ease_in_out',
                properties=['scale'],
                start_values={'scale': visual_obj.scale},
                end_values={'scale': visual_obj.scale * intensity}
            )
            self.transition_manager.start_transition(object_id, transition)
            
            # Return to original scale
            def return_to_normal():
                time.sleep(duration)
                return_transition = SceneTransition(
                    duration=duration,
                    easing_function='ease_in_out',
                    properties=['scale'],
                    start_values={'scale': visual_obj.scale * intensity},
                    end_values={'scale': visual_obj.scale}
                )
                self.transition_manager.start_transition(object_id, return_transition)
            
            thread = threading.Thread(target=return_to_normal)
            thread.daemon = True
            thread.start()
        
        elif effect_type == 'color_shift':
            # Color shifting effect
            target_color = params.get('target_color', np.array([1.0, 0.0, 0.0]))
            duration = params.get('duration', 1.0)
            
            transition = SceneTransition(
                duration=duration,
                easing_function='ease_in_out',
                properties=['color'],
                start_values={'color': visual_obj.color.copy()},
                end_values={'color': target_color}
            )
            self.transition_manager.start_transition(object_id, transition)
        
        elif effect_type == 'spiral':
            # Spiral movement effect
            center = params.get('center', np.array([0.0, 0.0, 0.0]))
            radius = params.get('radius', 2.0)
            duration = params.get('duration', 2.0)
            
            # Calculate spiral positions
            original_pos = visual_obj.position.copy()
            
            def spiral_movement():
                start_time = time.time()
                while time.time() - start_time < duration:
                    t = (time.time() - start_time) / duration
                    angle = t * 4 * np.pi  # Two full rotations
                    
                    spiral_pos = center + np.array([
                        radius * np.cos(angle) * (1 - t),
                        original_pos[1] + np.sin(t * np.pi) * 0.5,
                        radius * np.sin(angle) * (1 - t)
                    ])
                    
                    visual_obj.position = spiral_pos
                    self._update_object_visual(object_id)
                    time.sleep(0.016)  # ~60 FPS
                
                # Return to original position
                visual_obj.position = original_pos
                self._update_object_visual(object_id)
            
            thread = threading.Thread(target=spiral_movement)
            thread.daemon = True
            thread.start()
    
    def create_performance_visualization(self, recording_filename: str, output_filename: str):
        """Create a visual timeline of a recorded performance."""
        # This would generate a visual representation of the performance
        # Could be implemented with matplotlib or other visualization library
        pass
    
    def optimize_scene_for_performance(self):
        """Optimize current scene for better performance."""
        optimizations_applied = []
        
        # Reduce object count if too high
        if len(self.objects) > 8:
            # Keep only the most active objects
            activity_scores = {}
            for obj_id, visual_obj in self.objects.items():
                activity_scores[obj_id] = len(visual_obj.active_notes)
            
            # Sort by activity and keep top 8
            sorted_objects = sorted(activity_scores.items(), key=lambda x: x[1], reverse=True)
            objects_to_remove = [obj_id for obj_id, _ in sorted_objects[8:]]
            
            for obj_id in objects_to_remove:
                self.remove_object(obj_id)
            
            optimizations_applied.append(f"Reduced object count by {len(objects_to_remove)}")
        
        # Disable physics if not needed
        if self.physics_enabled and not any(
            hasattr(obj, 'velocity') and np.linalg.norm(obj.velocity) > 0.01
            for obj in self.objects.values()
        ):
            self.physics_enabled = False
            optimizations_applied.append("Disabled unused physics simulation")
        
        # Increase update throttle if performance is poor
        if len(self.objects) > 5:
            self.update_throttle = max(0.033, self.update_throttle)  # Limit to 30 FPS
            optimizations_applied.append("Increased update throttle")
        
        print(f"Performance optimizations applied: {optimizations_applied}")
        return optimizations_applied


# Example usage and integration
def create_enhanced_scene_manager_example():
    """Example of how to use the enhanced scene manager."""
    
    # This would typically be called from your main application
    # where you have access to initial_meshes and plotter_widget
    
    # enhanced_scene = EnhancedSceneManager(initial_meshes, plotter_widget)
    
    # Load a piano preset
    # enhanced_scene.load_instrument_preset(InstrumentType.PIANO)
    
    # Start recording a performance
    # enhanced_scene.record_performance(60.0)  # Record for 60 seconds
    
    # Handle MIDI notes (this would be called from your MIDI handler)
    # enhanced_scene.handle_midi_note(60, 100, True)  # Note on
    # enhanced_scene.handle_midi_note(64, 80, True)   # Another note
    # enhanced_scene.handle_midi_note(60, 0, False)   # Note off
    
    # Switch to drums in real-time
    # enhanced_scene.switch_scene_realtime(InstrumentType.DRUMS)
    
    # Create a custom preset
    # enhanced_scene.create_custom_preset("My Custom Setup", "Personal performance setup")
    
    # Save recording
    # enhanced_scene.save_recording("my_performance.json")
    
    # Play back recording
    # enhanced_scene.load_recording("my_performance.json")
    # enhanced_scene.play_recording()
    
    return True


if __name__ == "__main__":
    # Example usage
    print("Enhanced Scene Manager with Advanced Features")
    print("Features implemented:")
    print("✅ Instrument-specific scene presets")
    print("✅ Performance recording and playback")
    print("✅ Scene template system")
    print("✅ Real-time scene switching")
    print("✅ Advanced visual transitions")
    print("✅ Custom preset creation")
    print("✅ Transition effects (pulse, color shift, spiral)")
    print("✅ Performance optimization")
    
    # Display available instrument presets
    preset_manager = PresetManager()
    print(f"\nAvailable instrument presets:")
    for instrument_type in InstrumentType:
        preset = preset_manager.presets[instrument_type]
        print(f"  • {instrument_type.value}: {preset['description']}")
    
    print(f"\nTransition effects available:")
    print("  • pulse: Pulsing scale animation")
    print("  • color_shift: Smooth color transitions")
    print("  • spiral: Spiral movement patterns")
    
    print(f"\nEasing functions available:")
    print("  • linear, ease_in, ease_out, ease_in_out")
    print("  • bounce, elastic")
    
    create_enhanced_scene_manager_example()
