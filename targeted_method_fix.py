#!/usr/bin/env python3
"""
Targeted fix for the specific missing _note_to_color method
"""

import os
import re

def analyze_visualizer_file():
    """Analyze what's actually in the visualizer.py file"""
    
    if not os.path.exists("visualizer.py"):
        print("❌ visualizer.py not found")
        return None
    
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    # Find all method definitions
    method_pattern = r'def\s+(\w+)\s*\('
    methods = re.findall(method_pattern, content)
    
    print("Found methods in visualizer.py:")
    for method in sorted(methods):
        print(f"  - {method}")
    
    # Check specifically for color-related methods
    color_methods = [m for m in methods if 'color' in m.lower()]
    note_methods = [m for m in methods if 'note' in m.lower()]
    
    print(f"\nColor-related methods: {color_methods}")
    print(f"Note-related methods: {note_methods}")
    
    return content, methods

def find_error_location():
    """Find where the _note_to_color method is being called"""
    
    with open("visualizer.py", 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines, 1):
        if "_note_to_color" in line:
            print(f"Line {i}: {line.strip()}")
    
    return lines

def create_minimal_fix():
    """Create the minimal fix needed"""
    
    return '''    def _note_to_color(self, note, velocity):
        """Convert MIDI note and velocity to RGB color."""
        try:
            import colorsys
            
            # Map note to hue (0-1) using chromatic scale
            hue = (note % 12) / 12.0
            
            # Velocity affects saturation and brightness
            saturation = 0.8 + (velocity * 0.2)
            brightness = 0.6 + (velocity * 0.4)
            
            # Convert HSV to RGB
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
            
            return (r, g, b)
            
        except Exception as e:
            print(f"Error in _note_to_color: {e}")
            # Return a default color
            return (0.8, 0.8, 0.8)
'''

def apply_targeted_fix():
    """Apply a very targeted fix"""
    
    print("=== Analyzing visualizer.py ===")
    result = analyze_visualizer_file()
    if not result:
        return False
    
    content, methods = result
    
    print("\n=== Finding error location ===")
    lines = find_error_location()
    
    # Check if _note_to_color actually exists (case sensitive)
    if "_note_to_color" in methods:
        print("✅ _note_to_color method found - error might be elsewhere")
        
        # Check for syntax issues around the method
        method_start = content.find("def _note_to_color")
        if method_start != -1:
            # Extract the method
            method_section = content[method_start:method_start+500]
            print("Current _note_to_color method preview:")
            print(method_section[:200] + "...")
        
        return True
    
    else:
        print("❌ _note_to_color method not found, adding it...")
        
        # Create backup
        with open("visualizer.py.backup4", 'w') as f:
            f.write(content)
        print("✅ Created backup: visualizer.py.backup4")
        
        # Find insertion point (before the last method)
        last_method = content.rfind('\n    def ')
        if last_method == -1:
            print("❌ Could not find insertion point")
            return False
        
        # Insert the method
        new_method = create_minimal_fix()
        new_content = content[:last_method] + '\n' + new_method + content[last_method:]
        
        # Write the file
        with open("visualizer.py", 'w') as f:
            f.write(new_content)
        
        print("✅ Added _note_to_color method")
        return True

def test_import():
    """Test if we can import the visualizer module"""
    try:
        import sys
        sys.path.insert(0, '.')
        
        # Try to compile the file
        with open("visualizer.py", 'r') as f:
            content = f.read()
        
        compile(content, "visualizer.py", "exec")
        print("✅ File compiles successfully")
        
        # Try to find the specific issue
        if "self._note_to_color(note, velocity_norm)" in content:
            if "def _note_to_color(self" in content:
                print("✅ Method definition and call both found")
                return True
            else:
                print("❌ Method call found but definition missing")
                return False
        else:
            print("⚠️  Method call not found in expected format")
            return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def quick_fix_approach():
    """Quick approach - just add the method at the end of the class"""
    
    with open("visualizer.py", 'r') as f:
        content = f.read()
    
    # Find the MorphingVisualizer class
    class_match = re.search(r'class MorphingVisualizer.*?:', content)
    if not class_match:
        print("❌ Could not find MorphingVisualizer class")
        return False
    
    # Simple approach: add method before any potential __init__ or at end
    if "def _note_to_color" not in content:
        method = '''
    def _note_to_color(self, note, velocity):
        """Convert MIDI note and velocity to RGB color."""
        import colorsys
        hue = (note % 12) / 12.0
        saturation = 0.8 + (velocity * 0.2)
        brightness = 0.6 + (velocity * 0.4)
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, brightness)
        return (r, g, b)
'''
        
        # Find the end of the class (before next class or end of file)
        class_end = len(content)
        next_class = content.find('\nclass ', class_match.end())
        if next_class != -1:
            class_end = next_class
        
        # Insert method near the end of the class
        content = content[:class_end] + method + content[class_end:]
        
        with open("visualizer.py", 'w') as f:
            f.write(content)
        
        print("✅ Added _note_to_color method using quick fix")
        return True
    
    return True

if __name__ == "__main__":
    print("=== Targeted Fix for _note_to_color ===")
    
    if apply_targeted_fix():
        if test_import():
            print("\n🎉 SUCCESS! The method should now work.")
        else:
            print("\n⚠️  Trying quick fix approach...")
            if quick_fix_approach() and test_import():
                print("🎉 Quick fix successful!")
            else:
                print("❌ Quick fix failed")
    else:
        print("\n❌ Targeted fix failed")
        print("\nTrying quick fix approach...")
        if quick_fix_approach():
            print("✅ Quick fix applied")
        else:
            print("❌ All fixes failed")
