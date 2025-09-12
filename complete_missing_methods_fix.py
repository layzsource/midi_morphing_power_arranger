#!/usr/bin/env python3
"""
Complete fix for all missing methods in visualizer.py

This adds all the methods that are being called but don't exist.
"""

import os
import re

def create_all_missing_methods():
    """Create all missing methods needed by visualizer.py"""
    
    methods = '''
    def _note_to_color(self, note, velocity):
        """Convert MIDI note and velocity to RGB color."""
        try:
            import colorsys
            # Map note to hue using chromatic scale
            hue = (note % 12) / 12.0
            # Velocity affects saturation and brightness
            saturation = 0.8 + (velocity * 0.2)
            brightness = 0.6 + (velocity * 0.4)
            # Convert HSV to RGB
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
            return (r, g, b)
        except Exception as e:
            print(f"Error in _note_to_color: {e}")
            return (0.8, 0.8, 0.8)  # Default white-ish color
    
    def _trigger_note_effect(self, note, velocity):
        """Trigger visual effects for a MIDI note."""
        try:
            # Get color for this note
            color = self._note_to_color(note, velocity)
            
            # Create position based on note (spread notes across space)
            import numpy as np
            # Map note to position - spread across X axis
            x_pos = ((note - 60) / 60.0) * 4.0  # Center around middle C
            y_pos = (velocity - 0.5) * 2.0  # Velocity affects Y position
            z_pos = 0.0
            position = np.array([x_pos, y_pos, z_pos])
            
            # Add a light at this position
            light_id = f"note_{note}_{int(velocity*100)}"
            self._add_light(position, color, velocity, light_id)
            
            # Store note info for cleanup
            if not hasattr(self, 'active_note_effects'):
                self.active_note_effects = {}
            
            import time
            self.active_note_effects[note] = {
                'light_id': light_id,
                'timestamp': time.time(),
                'velocity': velocity,
                'color': color
            }
            
        except Exception as e:
            print(f"Error in _trigger_note_effect: {e}")
    
    def _add_light(self, position, color, intensity=1.0, light_id=None):
        """Add a light to the scene."""
        try:
            if not hasattr(self, 'plotter') or not self.plotter:
                return None
            
            if not hasattr(self, 'lights'):
                self.lights = {}
            
            if light_id is None:
                light_id = f"light_{len(self.lights)}"
            
            # Create a small glowing sphere to represent the light
            import pyvista as pv
            light_sphere = pv.Sphere(radius=0.1, center=position)
            
            # Add to plotter with emissive-like properties
            actor = self.plotter.add_mesh(
                light_sphere,
                color=color,
                opacity=min(0.8 + intensity * 0.2, 1.0),
                name=light_id,
                smooth_shading=True
            )
            
            # Store light info
            import time
            self.lights[light_id] = {
                'position': position,
                'color': color,
                'intensity': intensity,
                'actor': actor,
                'timestamp': time.time()
            }
            
            return light_id
            
        except Exception as e:
            print(f"Error adding light: {e}")
            return None
    
    def _cleanup_expired_lights(self):
        """Remove lights that have expired."""
        if not hasattr(self, 'lights'):
            self.lights = {}
            return
        
        try:
            import time
            current_time = time.time()
            timeout = 10.0  # 10 second timeout for lights
            
            expired_lights = []
            for light_id, light_info in self.lights.items():
                if current_time - light_info.get('timestamp', 0) > timeout:
                    expired_lights.append(light_id)
            
            for light_id in expired_lights:
                try:
                    if hasattr(self, 'plotter') and self.plotter:
                        self.plotter.remove_actor(light_id)
                    del self.lights[light_id]
                except Exception as e:
                    print(f"Error removing light {light_id}: {e}")
                    
        except Exception as e:
            print(f"Error in cleanup_expired_lights: {e}")
    
    def _cleanup_expired_note_effects(self):
        """Clean up expired note effects."""
        if not hasattr(self, 'active_note_effects'):
            self.active_note_effects = {}
            return
        
        try:
            import time
            current_time = time.time()
            timeout = 5.0  # 5 second timeout for note effects
            
            expired_notes = []
            for note, effect_info in self.active_note_effects.items():
                if current_time - effect_info.get('timestamp', 0) > timeout:
                    expired_notes.append(note)
            
            for note in expired_notes:
                try:
                    effect_info = self.active_note_effects[note]
                    light_id = effect_info.get('light_id')
                    
                    # Remove the associated light
                    if light_id and hasattr(self, 'lights') and light_id in self.lights:
                        if hasattr(self, 'plotter') and self.plotter:
                            self.plotter.remove_actor(light_id)
                        del self.lights[light_id]
                    
                    del self.active_note_effects[note]
                    
                except Exception as e:
                    print(f"Error removing note effect {note}: {e}")
                    
        except Exception as e:
            print(f"Error in cleanup_expired_note_effects: {e}")
    
    def handle_note_off(self, note, velocity):
        """Handle MIDI note off events."""
        try:
            # Remove from active notes if tracked
            if hasattr(self, 'active_notes') and note in self.active_notes:
                del self.active_notes[note]
            
            # Remove note effect and associated light
            if hasattr(self, 'active_note_effects') and note in self.active_note_effects:
                effect_info = self.active_note_effects[note]
                light_id = effect_info.get('light_id')
                
                # Remove the light
                if light_id and hasattr(self, 'lights') and light_id in self.lights:
                    try:
                        if hasattr(self, 'plotter') and self.plotter:
                            self.plotter.remove_actor(light_id)
                        del self.lights[light_id]
                    except:
                        pass
                
                del self.active_note_effects[note]
            
            # Update display
            self.update()
            
        except Exception as e:
            print(f"Error handling note off {note}: {e}")
    
    def _update_lighting(self):
        """Update the lighting in the scene."""
        try:
            # Clean up expired effects
            self._cleanup_expired_lights()
            self._cleanup_expired_note_effects()
            
            # Update any dynamic lighting effects here
            if hasattr(self, 'lights') and self.lights:
                # Could add pulsing, fading, or other dynamic effects
                pass
                
        except Exception as e:
            print(f"Error updating lighting: {e}")
    
    def _position_from_note(self, note, velocity):
        """Calculate 3D position from MIDI note and velocity."""
        try:
            import numpy as np
            
            # Map note to X position (spread across keyboard)
            x_pos = ((note - 60) / 60.0) * 4.0  # Center around middle C
            
            # Map velocity to Y position (louder = higher)
            y_pos = (velocity - 0.5) * 3.0
            
            # Add some Z variation based on note
            z_pos = np.sin(note * 0.1) * 0.5
            
            return np.array([x_pos, y_pos, z_pos])
            
        except Exception as e:
            print(f"Error calculating position: {e}")
            return np.array([0.0, 0.0, 0.0])
'''
    
    return methods

def add_required_imports():
    """Add any missing imports to visualizer.py"""
    
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    imports_needed = []
    
    if "import time" not in content:
        imports_needed.append("import time")
    
    if "import colorsys" not in content:
        imports_needed.append("import colorsys")
    
    if "import numpy as np" not in content:
        imports_needed.append("import numpy as np")
    
    if imports_needed:
        # Find the import section
        lines = content.split('\n')
        
        # Find the last import
        last_import_line = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_line = i
        
        # Insert new imports after the last existing import
        for imp in reversed(imports_needed):
            lines.insert(last_import_line + 1, imp)
        
        # Write back
        with open("visualizer.py", 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Added imports: {', '.join(imports_needed)}")
    
    return True

def apply_complete_fix():
    """Apply the complete fix for all missing methods"""
    
    if not os.path.exists("visualizer.py"):
        print("❌ visualizer.py not found")
        return False
    
    # Create backup
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    with open("visualizer.py.backup_complete", 'w') as f:
        f.write(content)
    print("✅ Created backup: visualizer.py.backup_complete")
    
    # Add required imports
    add_required_imports()
    
    # Re-read after adding imports
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    # Check which methods are missing
    missing_methods = []
    required_methods = [
        '_note_to_color',
        '_trigger_note_effect', 
        '_add_light',
        '_cleanup_expired_lights',
        'handle_note_off',
        '_update_lighting'
    ]
    
    for method in required_methods:
        if f"def {method}(" not in content:
            missing_methods.append(method)
    
    if not missing_methods:
        print("✅ All required methods already exist")
        return True
    
    print(f"Adding missing methods: {missing_methods}")
    
    # Find insertion point - before the last method or at end of class
    class_match = re.search(r'class MorphingVisualizer.*?:', content)
    if not class_match:
        print("❌ Could not find MorphingVisualizer class")
        return False
    
    # Find a good insertion point
    # Look for the end of the __init__ method or any existing method
    insertion_point = content.rfind('\n    def ')
    if insertion_point == -1:
        # Find after __init__ if it exists
        init_match = re.search(r'def __init__\(.*?\):', content)
        if init_match:
            # Find the end of __init__ method
            rest_content = content[init_match.end():]
            lines = rest_content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('        ') and not line.startswith('    '):
                    if line.startswith('    def ') or i == len(lines) - 1:
                        insertion_point = init_match.end() + len('\n'.join(lines[:i]))
                        break
        
        if insertion_point == -1:
            insertion_point = len(content) - 100  # Near end of file
    
    # Insert all missing methods
    all_methods = create_all_missing_methods()
    content = content[:insertion_point] + '\n' + all_methods + content[insertion_point:]
    
    # Write the updated file
    with open("visualizer.py", 'w') as f:
        f.write(content)
    
    print("✅ Added all missing methods")
    return True

def verify_complete_fix():
    """Verify that all methods were added correctly"""
    
    try:
        with open("visualizer.py", 'r') as f:
            content = f.read()
        
        # Test syntax
        compile(content, "visualizer.py", "exec")
        print("✅ Syntax check passed")
        
        # Check for all required methods
        required_methods = [
            '_note_to_color',
            '_trigger_note_effect', 
            '_add_light',
            '_cleanup_expired_lights',
            'handle_note_off',
            '_update_lighting'
        ]
        
        missing = []
        for method in required_methods:
            if f"def {method}(" not in content:
                missing.append(method)
        
        if missing:
            print(f"❌ Still missing: {missing}")
            return False
        else:
            print("✅ All required methods found")
            return True
            
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False

if __name__ == "__main__":
    print("=== Complete Missing Methods Fix ===")
    
    if apply_complete_fix():
        if verify_complete_fix():
            print("\n🎉 SUCCESS! All missing methods added.")
            print("\nAdded methods:")
            print("- _note_to_color: Maps MIDI notes to colors")
            print("- _trigger_note_effect: Creates visual effects for notes")
            print("- _add_light: Adds lights to the 3D scene")
            print("- _cleanup_expired_lights: Removes old lights")
            print("- handle_note_off: Handles note release events")
            print("- _update_lighting: Updates scene lighting")
            print("- _cleanup_expired_note_effects: Cleans up note effects")
            print("- _position_from_note: Calculates 3D positions from notes")
            print("\nYour MIDI visualizer should now work completely! 🎵")
        else:
            print("\n⚠️  Fix applied but verification failed")
    else:
        print("\n❌ Failed to apply complete fix")
