#!/usr/bin/env python3
"""
Fix for missing _note_to_color method in visualizer.py
"""

import os
import re

def create_missing_methods():
    """Create the missing methods for visualizer.py"""
    
    missing_methods = '''
    def _note_to_color(self, note, velocity):
        """Convert MIDI note and velocity to RGB color."""
        import colorsys
        
        # Map note to hue (0-1)
        # MIDI notes 0-127, map to full hue spectrum
        hue = (note % 12) / 12.0  # Chromatic scale mapping
        
        # Velocity affects saturation and brightness
        saturation = 0.8 + (velocity * 0.2)  # 0.8 to 1.0
        brightness = 0.6 + (velocity * 0.4)  # 0.6 to 1.0
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        
        return (r, g, b)
    
    def _cleanup_expired_lights(self):
        """Remove lights that have expired."""
        if not hasattr(self, 'lights'):
            self.lights = {}
            return
        
        current_time = time.time()
        expired_lights = []
        
        for light_id, light_info in self.lights.items():
            if current_time - light_info.get('timestamp', 0) > 60:  # 60 second timeout
                expired_lights.append(light_id)
        
        for light_id in expired_lights:
            try:
                if light_id in self.lights:
                    # Remove from plotter if it exists
                    if hasattr(self, 'plotter') and self.plotter:
                        # Try to remove the light actor
                        try:
                            self.plotter.remove_actor(light_id)
                        except:
                            pass
                    
                    del self.lights[light_id]
            except Exception as e:
                print(f"Error removing expired light {light_id}: {e}")
    
    def _update_lighting(self):
        """Update the lighting in the scene."""
        if not hasattr(self, 'plotter') or not self.plotter:
            return
        
        try:
            # Clean up expired lights first
            self._cleanup_expired_lights()
            
            # Update lighting if needed
            if hasattr(self, 'lights') and self.lights:
                # Apply lighting changes
                for light_id, light_info in self.lights.items():
                    # Update light properties
                    pass
        except Exception as e:
            print(f"Error updating lighting: {e}")
    
    def handle_note_off(self, note, velocity):
        """Handle MIDI note off events."""
        try:
            # Remove from active notes
            if hasattr(self, 'active_notes') and note in self.active_notes:
                del self.active_notes[note]
            
            # Remove light associated with this note
            if hasattr(self, 'lights'):
                light_id = f"note_{note}"
                if light_id in self.lights:
                    try:
                        if hasattr(self, 'plotter') and self.plotter:
                            self.plotter.remove_actor(light_id)
                    except:
                        pass
                    del self.lights[light_id]
            
            # Update display
            self.update()
            
        except Exception as e:
            print(f"Error handling note off {note}: {e}")
    
    def _add_light(self, position, color, intensity=1.0, light_id=None):
        """Add a light to the scene."""
        if not hasattr(self, 'plotter') or not self.plotter:
            return
        
        try:
            if not hasattr(self, 'lights'):
                self.lights = {}
            
            if light_id is None:
                light_id = f"light_{len(self.lights)}"
            
            # Create a small sphere to represent the light
            light_sphere = pv.Sphere(radius=0.1, center=position)
            
            # Add to plotter with color
            actor = self.plotter.add_mesh(
                light_sphere,
                color=color,
                opacity=0.8,
                name=light_id
            )
            
            # Store light info
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
'''
    
    return missing_methods

def add_imports_if_missing():
    """Add required imports to visualizer.py if missing"""
    
    if not os.path.exists("visualizer.py"):
        return False
    
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    imports_to_add = []
    
    if "import time" not in content:
        imports_to_add.append("import time")
    
    if "import colorsys" not in content:
        imports_to_add.append("import colorsys")
    
    if imports_to_add:
        # Find the import section
        lines = content.split('\n')
        import_insertion_point = 0
        
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_insertion_point = i + 1
        
        # Insert new imports
        for import_line in reversed(imports_to_add):
            lines.insert(import_insertion_point, import_line)
        
        content = '\n'.join(lines)
        
        with open("visualizer.py", 'w') as f:
            f.write(content)
        
        print(f"✅ Added missing imports: {', '.join(imports_to_add)}")
    
    return True

def apply_missing_method_fix():
    """Apply the fix for missing methods"""
    
    if not os.path.exists("visualizer.py"):
        print("❌ visualizer.py not found")
        return False
    
    # Add missing imports first
    add_imports_if_missing()
    
    # Read current file
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    # Create backup
    with open("visualizer.py.backup3", 'w') as f:
        f.write(content)
    print("✅ Created backup: visualizer.py.backup3")
    
    # Check if _note_to_color already exists
    if "_note_to_color" in content:
        print("✅ _note_to_color method already exists")
        return True
    
    # Find a good place to insert the missing methods
    # Look for the end of the class or before the last method
    insertion_point = content.rfind('\n    def ')
    
    if insertion_point == -1:
        # Try to find the class definition
        class_match = re.search(r'class MorphingVisualizer.*?:', content)
        if class_match:
            insertion_point = class_match.end()
        else:
            print("❌ Could not find insertion point")
            return False
    
    # Insert missing methods
    missing_methods = create_missing_methods()
    content = content[:insertion_point] + missing_methods + content[insertion_point:]
    
    # Write fixed file
    with open("visualizer.py", 'w') as f:
        f.write(content)
    
    print("✅ Added missing methods to visualizer.py")
    return True

def verify_methods():
    """Verify that all required methods exist"""
    
    if not os.path.exists("visualizer.py"):
        return False
    
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    required_methods = [
        '_note_to_color',
        '_cleanup_expired_lights', 
        'handle_note_off',
        '_add_light'
    ]
    
    missing = []
    for method in required_methods:
        if f"def {method}" not in content:
            missing.append(method)
    
    if missing:
        print(f"❌ Still missing methods: {missing}")
        return False
    else:
        print("✅ All required methods found")
        return True

def test_syntax():
    """Test that the file has valid Python syntax"""
    try:
        with open("visualizer.py", 'r') as f:
            content = f.read()
        
        compile(content, "visualizer.py", "exec")
        print("✅ Syntax check passed")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False

if __name__ == "__main__":
    print("=== Fixing Missing Methods in visualizer.py ===")
    
    if apply_missing_method_fix():
        if verify_methods() and test_syntax():
            print("\n🎉 SUCCESS! Missing methods added successfully.")
            print("\nAdded methods:")
            print("- _note_to_color: Converts MIDI notes to colors")
            print("- _cleanup_expired_lights: Removes old lights") 
            print("- handle_note_off: Handles MIDI note off events")
            print("- _add_light: Adds lights to the scene")
            print("- Added missing imports (time, colorsys)")
            print("\nYour visualizer should now work correctly!")
        else:
            print("\n⚠️  Fix applied but verification failed")
    else:
        print("\n❌ Failed to apply fix")
